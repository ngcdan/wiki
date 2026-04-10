---
title: "BF1 AI — Backend Rules"
tags: [bf1, ai, rules, backend, java]
---

# Backend Conventions & Formatting (Java / Spring Boot)

## 1. Code Style & Formatting
- **Imports**: Prefer wildcard imports (`import ...;`) or block imports. Do not use fully qualified class names inline unless resolving a naming collision.
- **Comments**: Keep them concise. Explain the *why* and the *flow*, not the *what*.
- **Formatting**: Use 2 spaces for indentation. Keep lines at a readable length (typically under 100-120 characters) to avoid horizontal scrolling.
- **Naming**: Use strict `camelCase` for variables/methods. Use `PascalCase` for classes.
  - Logic layer: `*Logic` (e.g., `PartnerLogic`)
  - Service layer: `*Service` (e.g., `PartnerService`)
  - Plugins: `*Plugin`
- **Interfaces**: Do not use the `I` prefix for interfaces unless matching an existing pattern.
- **Constants**: Use `UPPER_SNAKE_CASE` for `static final` fields.

## 2. Component & Layer Rules
### Service & Logic Layers
- **Service Naming**: Explicitly name your services, e.g., `@Service("MyEntityService")`.
- **Inheritance**: Services must extend `BaseComponent`.
- **Logic Delegation**: Services act as a facade and transaction boundary. Complex business rules should be delegated to `*Logic` classes.
- **Transactions**: Explicitly use `@Transactional(readOnly = true)` for search/get methods. For write operations, explicitly define the transaction manager: `@Transactional(transactionManager = "crmTransactionManager")`. Never use raw `@Transactional`.
- **Dependency Injection**: Field injection (`@Autowired`) is the standard pattern.
- **ClientContext**: Every business method (Logic, Service, Plugin) MUST accept `ClientContext client` as its first parameter.
- **Spring Bean Registration**: Do not use `@Component` for infrastructure classes that might conflict with platform beans. Use `@Bean` + `@ConditionalOnMissingBean` in config files. Bean injection for multi-instance (DataSource): `@Autowired` + `@Qualifier`. Framework beans (AppEnv): `@Resource(name = "...")`.

### Entities & DTOs
- **Lombok**: Use `@Getter`, `@Setter`, `@NoArgsConstructor`. Avoid `@Data` to prevent unintended `equals`/`hashCode` issues.
- **Fields (Data Types)**: Always use wrapper types (`Long`, `Double`, `Integer`, `Boolean`) instead of primitives.
- **Mapping Logic Pattern**: Place mapping logic in static factory/helper methods directly inside the DTO. Often maps from `SqlMapRecord`.
  ```java
  public static List<MyReport> computeFromMapRecords(List<SqlMapRecord> records) { ... }
  ```

## 3. Database & Entity Design (Domain-Driven Design)
Thống nhất nguyên tắc thiết kế Data Model theo chuẩn Aggregate:
1. **Tách biệt Sứ Mệnh Database & Model**: Database lưu trữ an toàn, Model phản ánh business logic.
2. **Aggregate & Aggregate Root**: Không có khái niệm nghiệp vụ thao tác độc lập với child mà không đi qua gốc. Mọi thao tác bắt buộc qua Aggregate Root.
3. **Hướng Mapping Unidirectional**: Các Entity con **không nên** chứa tham chiếu đối tượng Entity cha (nếu cần chỉ để virtual property `updatable=false, insertable=false`). Root map bằng `@JoinColumn`.
4. **Repository Độc Tài**: Tuyệt đối **không** tạo hoặc gọi `save()` tại Service/Repository của Entity con. Thêm sửa xóa con thông qua Root (nhờ *Cascading*).
5. **Toàn Vẹn Transaction**: Mọi thay đổi trong Aggregate phải diễn ra trong 1 Transaction cùng Aggregate Root.
6. **Thứ Tự Khai Báo Class**: Fields -> Override methods -> Helper methods (`addXxx()`).
7. **Propagate Context (Override `set`)**: Khi Root có cascade đến child (extends `CompanyEntity`), **bắt buộc** override `set(ClientContext, ICompany)` tại Root để truyền data xuống child.
8. **Database Index & Constraints**: Keep index and unique constraint names ≤ 63 characters (PostgreSQL limit).

## 4. Architecture & MSA Rules
- **Layered MSA**: `of1-core` -> `of1-platform` -> standalone apps (`of1-crm`).
- **Standalone Rule**: No platform bean injection (use `PlatformCallGateway`). Không dùng `*RPCService` trực tiếp.
- **Entity Imports**: Import platform entities strictly from `*.api.*` packages.
- **Dependency**: Chỉ dùng `*-api` artifact; thêm mới phải cập nhật cả `module/*/build.gradle` VÀ `release/build.gradle` (dùng `$dataTPErpVersion`). Compile dependency chưa đủ đối với `transitive=false`, phải khai báo runtime jars explicit.
- **Không query platform DB**: Tuyệt đối không dùng `SqlQueryUnitManager` để query trực tiếp vào DB của platform.
- **Multi-Datasource**: `of1-crm` uses `@Primary`, `bf1-legacy` uses `@Qualifier(BF1_LEGACY)`. Phải luôn có `@Primary` trên datasource mặc định, nếu không Spring Boot fail startup.
- **Checklist Khi Thêm Feature Mới**:
  - [ ] Không inject logic/service/repo từ `net.datatp.module.*` platform.
  - [ ] Gọi platform qua `platformCallGateway`.
  - [ ] `ClientContext client` luôn là tham số đầu tiên.
  - [ ] Import entity từ `*.api.*` package.

## 5. Platform Call Pattern (`PlatformCallGateway`)
All platform API communication goes through `PlatformCallGateway` (`cloud.datatp.core.integration`).
If extending `CRMDaoService`, use the inherited `platformCallGateway`:
```java
public class MyLogic extends CRMDaoService {
  public void doSomething(ClientContext client) {
    Long seq = platformCallGateway.nextSequence(client, "MY_SEQ");
    CompanyConfig config = platformCallGateway.getCompanyConfig(client, companyId);
  }
}
```

**Generic Call Pattern:**
```java
// Generic Call with Type Conversion
MyType obj = platformCallGateway.call(client, "ServiceName", "methodName",
    platformCallGateway.params("key", value), MyType.class);

// Generic Call with TypeReference
List<MyType> list = platformCallGateway.call(client, "ServiceName", "methodName",
    platformCallGateway.params(), new TypeReference<List<MyType>>() {});
```

## 6. Dependencies Reference
**of1-core** (Hạ tầng cơ sở):
- `datatp-core-module-data`: Kafka, `SqlQueryUnitManager`, `PersistableEntity`
- `datatp-core-module-security`: Auth, AES, `SessionData`
- `datatp-core-module-http`: REST/RPC controllers, `UploadService`
- `datatp-core-module-app`: `ServerApp`, Spring Security, `ClientContext` filter

**of1-platform** (Nền tảng ERP):
- `datatp-platform-app-api`: `PlatformClient`, `PlatformApiConfig`
- `datatp-platform-module-company-api`: `Company`, `CompanyConfig`
- `datatp-platform-module-account-api`: `Account`, `UserProfile`
- `datatp-platform-module-storage-api`: `EntityAttachment`
- `datatp-platform-module-communication-api`: Communication entities---
name: backend-implementation-template
description: Template chuẩn để implement Backend OF1 (Entity, Repository, Logic, Service). Tuân thủ kiến trúc RPC-like, DDD, và Transaction boundaries.
---

# Template Backend OF1 (Service/Logic/Repository)

Dự án OF1 triển khai kiến trúc BE đặc thù không sử dụng REST Controller truyền thống cho các API gọi từ WebUI, thay vào đó WebUI sử dụng `createHttpBackendCall` mapping trực tiếp tới các `@Service` / `@Transactional` Bean.
Theo pattern đó, Backend sẽ chia làm 3 lớp:
1. **Service Layer**: Nơi định nghĩa các function entry-point (nhận request từ WebUI qua HTTP RPC), quản lý Transaction boundaries (`@Transactional`), và check permission/ClientContext.
2. **Logic Layer**: Chứa pure business logic, xử lý data validation, call external service (thường kế thừa `CRMDaoService` để gọi `platformCallGateway`).
3. **Repository Layer**: Kế thừa `JpaRepository`, thực hiện query Database (`@Query`).
4. **Entity Layer**: Kế thừa `PersistableEntity<Long>` hoặc `CompanyEntity` cho JPA Model.

Sử dụng template này khi bạn cần làm tính năng mới ở Backend để đảm bảo tuân thủ thiết kế kiến trúc chuẩn.

## 1. Entity (`YourEntity.java`)
```java
package [your.package.entity];

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.module.data.db.entity.PersistableEntity;
import net.datatp.util.text.DateUtil;
import java.util.Date;

/**
 * Model ánh xạ DB table.
 * Chú ý: Tên Index và Unique Constraint phải <= 63 ký tự.
 */
@Entity
@Table(
    name = YourEntity.TABLE_NAME,
    indexes = {
        @Index(name = YourEntity.TABLE_NAME + "_code_idx", columnList = "code")
    }
)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@Getter
@Setter
public class YourEntity extends PersistableEntity<Long> { // Hoặc extends CompanyEntity
    public static final String TABLE_NAME = "your_project_table_name";

    // TODO: Add thêm properties mapping ở đây (Luôn dùng Wrapper class như Long, Double)
    
    // Nếu có Child Entities (Aggregate Pattern):
    // Phía Aggregate Root chủ động map List con bằng @JoinColumn thay vì mappedBy.
    // Thêm các Helper methods (addXxx, removeXxx) ở cuối class.
}
```

## 2. Repository (`YourEntityRepository.java`)
```java
package [your.package.repository];

import java.io.Serializable;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import [your.package.entity].YourEntity;

/**
 * JPA Repository Interface
 */
@Repository
public interface YourEntityRepository extends JpaRepository<YourEntity, Serializable> {

    @Query("SELECT e FROM YourEntity e WHERE e.id = :id")
    YourEntity getById(@Param("id") Long id);

    @Query("SELECT e FROM YourEntity e WHERE e.code = :code")
    List<YourEntity> findByCode(@Param("code") String code);

    // TODO: Add các Native Query hoặc JPA Query khác
    // Tuyệt đối KHÔNG tạo hàm save() cho Child Entity. Thêm/sửa/xóa con thông qua Parent.
}
```

## 3. Logic Layer (`YourEntityLogic.java`)
```java
package [your.package];

import java.util.Date;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import net.datatp.module.service.BaseComponent;
import net.datatp.security.client.ClientContext;
import net.datatp.util.error.ErrorType;
import net.datatp.util.error.RuntimeError;
import [your.package.entity].YourEntity;
import [your.package.repository].YourEntityRepository;

// Nếu là CRM: Kế thừa CRMDaoService để có sẵn platformCallGateway
// Nếu là EGOV/Khác: Kế thừa BaseComponent
/**
 * Logic Component chứa strict business rules, không mở transaction ở đây để tái sử dụng.
 */
@Component
public class YourEntityLogic extends BaseComponent { 

    @Autowired
    private YourEntityRepository repository;

    public YourEntity getById(ClientContext ctx, Long id) {
        if (id == null) return null;
        return repository.getById(id);
    }

    public YourEntity saveEntity(ClientContext ctx, YourEntity entity) {
        // 1. Validation
        if (entity.getCode() == null || entity.getCode().isEmpty()) {
            throw new RuntimeError(ErrorType.IllegalArgument, "Code is required!");
        }

        // 2. Audit Tracking
        if (entity.getId() == null) {
            entity.setDateCreated(new Date());
            // VD Platform Call (nếu extends CRMDaoService):
            // Long seq = platformCallGateway.nextSequence(ctx, "YOUR_SEQ");
            // entity.setCode("CODE" + seq);
        }
        entity.setDateModified(new Date());

        // 3. TODO: Business rules (check trùng code, tính toán trường phụ, ...)
        
        // 4. Persist
        return repository.save(entity);
    }

    public int deleteEntities(ClientContext ctx, List<Long> targetIds) {
        // TODO: Add logic để check liên kết trước khi xóa (VD: không cho xóa nếu record đang active)
        repository.deleteAllById(targetIds);
        return targetIds.size();
    }
}
```

## 4. Service Layer (`YourEntityService.java` -> Cổng giao tiếp với WebUI)
```java
package [your.package];

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import net.datatp.module.service.BaseComponent;
import net.datatp.security.client.ClientContext;
import [your.package.entity].YourEntity;

/**
 * Boundary Service nhận calls từ WebUI (Framework sẽ auto map `appContext.createHttpBackendCall`).
 * QUAN TRỌNG: Must specify proper `transactionManager`.
 */
@Service("YourEntityService") // <- Tên Bean này sẽ được gọi từ FE: appContext.createHttpBackendCall("YourEntityService", ...)
@Transactional(transactionManager = "crmTransactionManager") // Đổi tên manager tùy module (vd: egovTransactionManager)
public class YourEntityService extends BaseComponent {

    @Autowired
    private YourEntityLogic logic;

    // READ methods
    @Transactional(readOnly = true, transactionManager = "crmTransactionManager")
    public YourEntity getEntity(ClientContext client, Long id) {
        return logic.getById(client, id);
    }

    // WRITE methods
    // Framework tự động mở Transaction với write capability
    public YourEntity saveEntity(ClientContext client, YourEntity entity) {
        return logic.saveEntity(client, entity);
    }

    public int deleteEntities(ClientContext client, List<Long> targetIds) {
        return logic.deleteEntities(client, targetIds);
    }

    // TODO: Add custom methods ví dụ fetchList, search... 
    // Object trả về hoặc nhận vào có thể dùng SqlMapRecord hoặc POJO
}
```
