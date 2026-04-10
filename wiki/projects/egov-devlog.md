---
title: "Egov Devlog"
tags: [egov, devlog, dev]
---

# DEVLOG

## 2026-03-29: Refactor — `syncSourceConfigId` resolve từ context thay vì DB lookup

- **Commit:** `57763472`
- **Files changed:** 34 files, -196 lines

### Vấn đề cũ

`AbstractEcusMapper.getSyncSourceConfigurationId(companyId)` query DB mỗi lần `processSync()` được gọi để resolve `syncSourceConfigId`. Lý do: `SyncController` chỉ set 2 field vào `EcusTenantContext`:

```java
EcusTenantContext.set(ecusDbName, mapping.getCompanyId());
// syncSourceConfigId = null → mapper phải tự query
```

Nhưng thực ra controller đã có `mapping` (là `SyncSourceConfiguration`) — `mapping.getId()` chính là `syncSourceConfigId`. Thông tin bị bỏ qua không cần thiết.

### Thay đổi

**1. `SyncController` — tất cả 10 endpoint multi-ECUS:** thêm `mapping.getId()` vào context:

```java
// Trước:
EcusTenantContext.set(ecusDbName, mapping.getCompanyId());

// Sau:
EcusTenantContext.set(ecusDbName, mapping.getCompanyId(), mapping.getId());
```

**2. `AbstractEcusMapper`:** xóa hoàn toàn `getSyncSourceConfigurationId(Long companyId)` và dependency `SyncSourceConfigurationService`.

**3. Tất cả mapper (30+ files):** thay thế call site:

```java
// Trước:
Long syncSourceConfigId = getSyncSourceConfigurationId(companyId);

// Sau:
Long syncSourceConfigId = EcusTenantContext.getSyncSourceConfigurationId();
```

### Kết quả

`syncSourceConfigId` có sẵn trong `EcusTenantContext` từ đầu request — không cần query DB thêm. CDC flow đã làm điều này từ trước (set đủ 3 field), batch flow giờ nhất quán.

---

## 2026-03-29: Architecture Note — `AbstractEcusMapper`

- **File:** `module/ecus-thaison/.../logic/mapper/AbstractEcusMapper.java`

Base class cho tất cả ECUS mapper, giải quyết 2 vấn đề kỹ thuật chung:

**1. `self()` — Spring proxy workaround cho `@Transactional` trong batch loop**

Batch loop gọi `this.processSync(entity)` → Spring không intercept → `@Transactional(REQUIRES_NEW)` bị bỏ qua → toàn batch chạy trong 1 transaction → 1 record lỗi rollback hết.

`self()` dùng `ApplicationContextProvider.getBean(getClass())` để lấy Spring-managed proxy thay vì `this` → `@Transactional` hoạt động đúng, mỗi record là 1 transaction riêng.

**2. `getSyncSourceConfigurationId(companyId)` — resolve sync source từ ThreadLocal context**

Batch flow chỉ set `EcusTenantContext` với `ecusDbName` + `companyId` (không có `syncSourceConfigId`). Mỗi `processSync()` cần `syncSourceConfigId` để lookup/save đúng record theo tenant. Method này query DB theo `(vendor="ECUS", ecusDbName, companyId)`, tạo mới nếu chưa có. Đưa vào base class để không duplicate ở 30+ mapper.

---

## 2026-03-29: Architecture Note — `IEcusPartnerEntityMapper` / `IEcusCompanyEntityMapper` / `IEcusCoreEntityMapper`

- **Module:** `ecus-thaison`

3 interface này có signature **giống hệt nhau** (`SyncResult syncEntity()`). Mục đích duy nhất là phân nhóm mapper để Spring inject đúng danh sách vào từng endpoint.

```java
// EcusMappingService dùng type để group:
@Autowired List<IEcusPartnerEntityMapper> partnerMappers;   // ~10 mappers
@Autowired List<IEcusCompanyEntityMapper> companyMappers;   // ~18 mappers
@Autowired List<IEcusCoreEntityMapper>    coreMappers;      // vài mappers

// REST endpoint tương ứng:
POST /sync/{ecusDbName}/partner-entities  → chạy partnerMappers
POST /sync/{ecusDbName}/company-entities  → chạy companyMappers
POST /sync/{ecusDbName}/core-entities     → chạy coreMappers
```

Nếu merge thành 1 interface chung, `@Autowired List<ICommonMapper>` sẽ inject tất cả vào mọi endpoint — không phân loại được. 3 interface là **marker phân nhóm**, không có logic riêng.

---

## 2026-03-29: Field Notes — `sync_source_configuration_id` và `original_id`

- **Entity:** `CompanyEntity` (base class của `Declaration` và các entity trong `ecutoms`)
- **DB:** `egov_local` (postgres, java-server.of1-dev-egov.svc.cluster.local)

### `sync_source_configuration_id`

FK trỏ đến bảng `sync_source_configuration`. Xác định record được sync vào từ nguồn ECUS nào.

```
sync_source_configuration hiện có:
id=1  vendor=ECUS  source_name=ECUS5VNACCS  company_id=8
id=2  vendor=ECUS  source_name=BEEOLD       company_id=8
id=3  vendor=ECUS  source_name=BEE          company_id=8
id=4  vendor=ECUS  source_name=lkt          company_id=8
```

**Dùng để:**
- Multi-tenant isolation: cùng `company_id` có thể có nhiều ECUS database, field này phân biệt record đến từ DB nào.
- Unique constraint trên `declaration`: `(company_id, sequence_no, sync_source_configuration_id)` — tránh duplicate khi sync từ nhiều nguồn.
- CDC reverse flow: consumer đọc config này để biết cần write ngược vào ECUS database nào (`EcusTenantContext.set(sourceName, companyId, id)`).

### `original_id`

ID gốc của record trong hệ thống nguồn (ECUS SQL Server). Dùng để map ngược khi cần update thay vì insert duplicate.

Hiện tại **chưa được populate** (tất cả null trong DB). Về thiết kế nên chứa:
- `_DToKhaiMDID` từ ECUS `DTOKHAIMD` table khi source là DTOKHAIMD
- `_D_OLAID` từ ECUS `D_OLA` table khi source là OLA

Tương đương `ecus_id` trên `Declaration` nhưng nằm ở base class nên áp dụng toàn hệ thống.

---

## 2026-03-28: Redesign ECUS→eGov Mapping — Single vs Batch

- **Module:** `ecus-thaison`
- **Goal:** Tách rõ 2 luồng sync (CDC single / Batch API), loại bỏ `getSelf()` anti-pattern trong `SyncExecutor`.

### Changes

**Phase 1 — Fix SyncExecutor transaction anti-pattern:**
- Tạo mới `MigrationJobTracker` service: extract 3 `@Transactional(REQUIRES_NEW)` methods ra khỏi `SyncExecutor` (`createJob`, `trackFailedRecord`, `completeJob`).
- `SyncExecutor` xóa `getSelf()`, field `self`, `ApplicationContext`; inject `MigrationJobTracker` thay thế.

**Phase 2 — Tách interface:**
- Tạo mới `IEcusSingleMapper<TSource>`: interface đánh dấu các mapper thuộc CDC flow. Method duy nhất: `processSync(TSource)`.
- `AbstractEcusMapper` thêm helper `self()` dùng `ApplicationContextProvider.getBean(getClass())` — thay thế pattern `ApplicationContextProvider.getBean(ConcreteMapper.class)` lặp lại ở mỗi mapper.

**Phase 3 — Refactor 5 concrete partner mappers:**

| Mapper | Source type |
|--------|-------------|
| `EcusDTOKHAIMapper` | `DTOKHAIMD` |
| `EcusDHANGMDDKMapper` | `DHANGMDDK` |
| `EcusD_OLAMapper` | `D_OLA` |
| `EcusD_OLA_HangMapper` | `D_OLA_Hang` |
| `EcusD_OLA_ContainerMapper` | `D_OLA_Container` |

- Mỗi mapper: thêm `implements IEcusSingleMapper<T>`, thêm `@Override` trên `processSync()`, dùng `self()` trong `processBatch()` thay local proxy variable.
- `EcusDHANGMDDKMapper`: rename `processDhangmddkToGoodsItems` → `processSync` (đồng nhất tên với interface) — fix luôn bug cũ: method này đang được gọi trực tiếp (không qua proxy) nên `@Transactional(REQUIRES_NEW)` không có tác dụng.
- `DHANGMDDKCDCHandler` + `CDCLoopPreventionUnitTest`: cập nhật theo tên mới.

**Style fix — FQCN imports:**
- Xóa 17 inline fully qualified class names rải rác trong catch blocks, variable declarations, method signatures, lambda bodies, và `@Mock` test fields.
- Thêm các imports thiếu: `LocalDateTime`, `DataIntegrityViolationException`, `BigDecimal`, `Timestamp`, `EntityLockManager`, mapper classes.

### Key decisions
- **Batch = loop gọi Single**: `processSync()` là đơn vị atomic có `@Transactional`. `syncEntity()` chỉ là iterator + tracking wrapper.
- `MigrationJobTracker` tách hẳn ra service riêng để `SyncExecutor` không cần tự inject `ApplicationContext` chỉ để gọi proxy của chính nó.
- `self()` đặt ở `AbstractEcusMapper` (không phải `SyncExecutor`) vì nó phục vụ mapper proxy, không phải executor.

---

## 2026-03-24: Cau hinh uu tien Maven Nexus trong Gradle

### Hien trang

Repository resolution order trong `build.gradle` (ap dung cho tat ca subproject):

```groovy
repositories {
  mavenLocal()     // 1st: ~/.m2/repository — local dev cache
  maven {
    url "${nexusUrl}/repository/maven-public/"  // 2nd: Nexus group repo
    allowInsecureProtocol = true
  }
  mavenCentral()   // 3rd: fallback neu Nexus khong co artifact
}
```

`nexusUrl` duoc dinh nghia trong `~/.gradle/gradle.properties` (global, khong commit):

```properties
nexusUrl=http://nexus.of1-dev-egov.svc.cluster.local
nexusUsername=admin
nexusPassword=admin
```

### Nguyen tac hoat dong

Gradle kiem tra repo theo **thu tu khai bao** — repo dau tien tim thay artifact se duoc dung.
Thu tu hien tai: `mavenLocal` > `Nexus` > `mavenCentral`.

### Cac phuong an cau hinh

**PA1 (hien tai): mavenLocal → Nexus → mavenCentral fallback**
- Uu: linh hoat, Nexus khong co van resolve duoc tu Central
- Nhuoc: phu thuoc internet neu Nexus thieu artifact

**PA2: Nexus lam proxy duy nhat (khuyen nghi cho moi truong corporate/offline)**

Xoa `mavenCentral()`, cau hinh Nexus `maven-public` group de proxy mavenCentral:

```groovy
repositories {
  mavenLocal()
  maven {
    url "${nexusUrl}/repository/maven-public/"
    allowInsecureProtocol = true
  }
  // khong co mavenCentral() — tat ca di qua Nexus
}
```

Nexus phai cau hinh `maven-public` group bao gom proxy repo tro toi `https://repo1.maven.org/maven2/`.
Loi ich: tat ca artifact di qua Nexus (cache, kiem soat, offline).

**PA3: Nexus truoc ca mavenLocal (it gap)**

```groovy
repositories {
  maven { url "${nexusUrl}/repository/maven-public/"; allowInsecureProtocol = true }
  mavenLocal()
  mavenCentral()
}
```

Chi dung khi Nexus giu phien ban moi hon local cache.

**PA4: Centralize bang `dependencyResolutionManagement` (Gradle 7+)**

Trong `settings.gradle`, them:

```groovy
dependencyResolutionManagement {
  repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)  // hoac FAIL_ON_PROJECT_REPOS
  repositories {
    mavenLocal()
    maven {
      url "${nexusUrl}/repository/maven-public/"
      allowInsecureProtocol = true
    }
    mavenCentral()
  }
}
```

`PREFER_SETTINGS`: settings.gradle repo uu tien hon subproject repo.
`FAIL_ON_PROJECT_REPOS`: ep buoc chi dung repo khai bao o settings (strict nhat).

### Plugin Resolution

Plugin (`id 'org.springframework.boot'`) resolve rieng, khong dung `repositories {}`.
Phai khai bao trong `settings.gradle`:

```groovy
pluginManagement {
  repositories {
    maven {
      url "${nexusUrl}/repository/maven-public/"
      allowInsecureProtocol = true
    }
    gradlePluginPortal()
  }
}
```

### Ket luan (repo nay)

Cau hinh hien tai (PA1) hop ly cho moi truong dev. Neu muon bat buoc tat ca download qua Nexus
(CI/CD, offline), chuyen sang PA2 va dam bao Nexus proxy cau hinh day du.

## 2026-03-16: eGov -> ECUS Kafka Event Publishing
- **Module:** `ecutoms` (producer), `ecus-thaison` (consumer)
- **Goal:** Xay dung luong dong bo nguoc: eGov PostgreSQL -> Kafka -> ECUS SQL Server
- **Architecture:**
  - `ecutoms`: Event DTO (`EgovEntityEvent`) + Producer (`EgovEventPublisher`) + Config (`EgovKafkaProducerConfig`)
  - `ecus-thaison`: Consumer listener + Reverse mapper (eGov entity -> ECUS entity)
  - FE khong thay doi
- **3 Topics (match FE save boundaries):**
  - `egov.declaration.events` — Declaration aggregate (thong tin chung 1+2)
  - `egov.goods-declaration.events` — GoodsDeclaration + GoodsItems
  - `egov.container-declaration.events` — ContainerDeclaration
- **Key decisions:**
  - Payload = full entity JSON (entity da co Jackson annotations)
  - Producer inject bang `@Autowired Optional<EgovEventPublisher>` — an toan khi Kafka disabled
  - Config theo YAML, producer bean chi tao khi `egov.kafka.producer.enabled: true`
  - CDC loop prevention: sentinel field `NGUOINHAP="EGOV_SYNC"` khi write nguoc vao ECUS
  - eGov DB la source of truth; Kafka publish failure khong rollback PG transaction
- **Checkpoints:**
  1. Infrastructure + Declaration topic (end-to-end)
  2. GoodsDeclaration topic
  3. ContainerDeclaration topic

## 2026-03-07
- **Module:** `ecutoms`, `ecus-thaison`
- **Changes:**
  - Cập nhật mapping từ `Declaration` sang `DeclarationLicense` thành Unidirectional `OneToOne` (bảng `declaration` giữ khóa ngoại `declaration_license_id`).
  - Cập nhật mapping từ `DeclarationLicense` sang `DeclarationLicenseCustomsCode` và `DeclarationLicenseTradingType` thành Unidirectional `OneToMany`.
  - Thêm Liquibase script vào `002-schema-updates.sql` để cập nhật schema.
  - Sửa kiểu dữ liệu `totalInvoiceAmount` và `totalTaxableAmount` trong `TradingInvoice` từ `BigDecimal` sang `Double`.
  - Đồng bộ format ngày giờ `@JsonFormat` cho `invoiceDate` trong `TradingInvoice`.
  - Cập nhật logic `EcusDTOKHAIMapper` để loại bỏ các phép gán entity con không còn tác dụng (do Hibernate tự động Cascade) và map đúng kiểu `Double`.
  - Sửa các Integration Test để pass toàn bộ assertion theo rule mapping mới và xử lý đúng thứ tự cleanup dữ liệu tránh lỗi cấu trúc Foreign Key constraint. Xóa `precision/scale` attribute không hợp lệ ở các field float/double.
  - Mở comment mapping `@OneToOne` cho `TradingInvoice` trong `Declaration`; fix toàn bộ logic mapper và test dùng `tradingInvoiceId` chuyển sang thao tác trực tiếp với entity.
  - Cập nhật mapping `@OneToOne` cho `TransportDocument` trong `Declaration`; fix toàn bộ logic mapper và test dùng `transportDocumentId` chuyển sang thao tác trực tiếp với entity.
  - Cập nhật mapping `@OneToMany` từ `GoodsDeclaration` tới `GoodsItems` thành Unidirectional; chuyển đổi logic save và map JSON của `GoodsItems` thông qua `GoodsDeclaration`.
  - Cập nhật mapping từ `GoodsItems` tới `GoodsItemsOtherTax`, `GoodsItemsLegalDocument`, `GoodsItemsDamageCode` thành Unidirectional; chuyển đổi logic bulk save thông qua Parent entity.
