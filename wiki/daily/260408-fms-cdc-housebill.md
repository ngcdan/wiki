---
title: "FMS CDC HouseBill"
tags: [daily, fms, cdc, house-bill, hps, mssql, transport-plan, mapping, spec, plan]
created: 2026-04-08
---

# FMS CDC HouseBill

Tổng hợp nghiên cứu, phân tích field MSSQL, implementation, design spec, và plan cho CDC mapping HPS → FMS liên quan đến HouseBill.

## Mục lục

- [Tổng quan](#tổng-quan)
- [A. HPS MSSQL Field Analysis](#a-hps-mssql-field-analysis) — nghiên cứu field chưa/đã map
- [B. CDC Implementation](#b-cdc-implementation) — code đã implement trong ngày
- [C. HouseBill CDC Completeness — Design](#c-housebill-cdc-completeness--design) — spec cho Sub-project 1
- [D. HouseBill CDC Completeness — Plan](#d-housebill-cdc-completeness--plan) — plan 12 tasks TDD
- [Appendix](#appendix) — typo reference, field dễ nhầm lẫn
- [E. Schema Mismatch Analysis & Solutions](#e-schema-mismatch-analysis--solutions) — phân tích field lệch schema MSSQL→PostgreSQL và giải pháp

---

## Tổng quan

| Chủ đề | Status | Section |
|--------|--------|---------|
| ColoaderID / AirLine analysis | Research done | A.1 |
| Status / Notes / Contact fields | Research done | A.2 |
| Lock / Audit / Commercial fields | Research done | A.3 |
| HAWB.CussignedDate | Implemented | A.4 |
| CDC Transaction → TransportPlan | Implemented (sẽ refactor) | B.1 |
| HouseBill CDC Completeness | Design + Plan | C + D |
| Schema Mismatch MSSQL→PostgreSQL | Analysis + 3 Solutions | E |

**Source chung**: `dbo.Transactions`, `dbo.TransactionDetails`, `dbo.HAWB` (HPS BFS One)
**CDC handler**: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/`
**Ref docs**: `docs/references/mapping/ref/sql_query_analysis.md`, `docs/references/bfs/documentation.md`, `docs/references/mapping/mapping-transactions.md`

---

# A. HPS MSSQL Field Analysis

## A.1 ColoaderID / ColoaderID_O / AirLine

Source: `dbo.Transactions`

### Giống nhau

- Cả 3 đều là mã đối tác (partner code) — join ra bảng partner để lookup label
- Cả 3 phản ánh "bên vận chuyển" — thuộc nhóm carrier/coloader

### Khác nhau

| Field | Giai đoạn Save | Ý nghĩa nghiệp vụ | Phạm vi |
|---|---|---|---|
| `ColoaderID` | Inbound + Outbound | Coloader/carrier chính — canonical "carrier hiện tại" | Mọi TypeOfService |
| `ColoaderID_O` | Chỉ Outbound (suffix `_O`) | Coloader thực tế khi xuất — có thể khác ColoaderID (đổi hãng tại khâu handover) | Chỉ outbound |
| `AirLine` | Chỉ Inbound | Hãng hàng không actual — chỉ áp dụng Air | TypeOfService nhóm Air |

### Quan hệ

- **ColoaderID vs ColoaderID_O**: `ColoaderID_O` = snapshot riêng outbound. Nếu khác → đã đổi coloader tại khâu xuất. Ưu tiên `ColoaderID_O` nếu non-null.
- **ColoaderID vs AirLine**: ColoaderID = forwarder/coloader (CASS member). AirLine = carrier thực tế (hãng bay phát MAWB). Trong Air 2 bên **khác nhau** — forwarder bán cước, airline chở hàng.

### Trạng thái mapping FMS

| Field MSSQL | Transaction (FMS) | TransportPlan/Route |
|---|---|---|
| `ColoaderID` | `coloaderPartnerLabel` | `TransportRoute.carrierLabel` |
| `ColoaderID_O` | Chưa map | Chưa map |
| `AirLine` | `transportName` (fallback RefNoSea) | Chưa map |

### Đề xuất

1. Thêm `coloader_partner_label_outbound` hoặc ưu tiên `ColoaderID_O` → fallback `ColoaderID`
2. Tách `carrier_airline_label` riêng cho actual airline
3. `IntegratedTransaction` cần map thêm `ColoaderID` và `AirLine` cho analytics

**Gap**: `ColoaderID_O` chưa map ở bất kỳ entity nào. "Forwarder vs actual airline" là khác biệt quan trọng — đừng merge vào 1 field.

---

## A.2 Status / Notes / Contact Fields

Source: `dbo.Transactions`

### 6 cột phân tích

| Cột | Kiểu | Ý nghĩa | Update stage |
|---|---|---|---|
| `Starus` | varchar | Status (typo gốc HPS) — trạng thái term: CREATE, OPEN, CLOSED, PRE-ALERT, TERMED... | Inbound + Outbound |
| `Delivered` | bit/varchar | Cờ đã giao hàng | Inbound + Outbound |
| `BookingRequestNotes` | nvarchar | Ghi chú Sales/CS khi tạo booking request | Chỉ Inbound |
| `Remark` | nvarchar | Nhận xét chung về shipment | Chỉ Inbound |
| `Attn` | nvarchar | Attention to — tên người chịu trách nhiệm file | Chỉ Inbound |
| `OtherInfo` | nvarchar | M-B/L Type hoặc metadata chứng từ | Inbound + Outbound |

### Nhóm semantics

**Operation state**: `Starus` + `Delivered` → xây state machine: `Booked → In Transit → Delivered → Closed`

**Notes family (3 field RIÊNG — đừng gộp)**:

| Field MSSQL | FMS target | Ý nghĩa |
|---|---|---|
| `BookingRequestNotes` | Chưa map | Yêu cầu từ khách lúc book |
| `Remark` | Chưa map | Ghi chú vận hành của staff |
| `ExpressNotes` | `Transaction.note` | Ghi chú chứng từ in trên bill |

3 field có audience và lifecycle khác nhau, **không nên gộp** thành 1 field `notes`.

**Contact / Metadata**: `Attn` = Sales/CS owner. `OtherInfo` = M-B/L Type.

### Mapping gaps

| Field | Gap |
|---|---|
| `Starus` | Doc nói map → `state`, nhưng CDC handler chưa set |
| `Delivered` | Chưa map — cần thêm field + column + CDC |
| `BookingRequestNotes` | Chưa map — cần field riêng |
| `Remark` | Chưa map — cần field riêng |
| `Attn` | Chưa map — cần `fileOwnerName` |
| `OtherInfo` | Chưa map (có placeholder comment) — map tới `mblType` |

### Đề xuất schema mở rộng Transaction (FMS)

```java
@Column(name = "state")                       private String state;                // ← Starus
@Column(name = "delivered")                    private Boolean delivered;           // ← Delivered
@Column(name = "booking_request_notes")        private String bookingRequestNotes;  // ← BookingRequestNotes
@Column(name = "remark")                       private String remark;               // ← Remark
@Column(name = "file_owner_name")              private String fileOwnerName;        // ← Attn
@Column(name = "mbl_type")                     private String mblType;              // ← OtherInfo
```

### Query sample

```sql
SELECT TOP 10 TransID, TransDate, TpyeofService, Starus, Delivered,
       Attn, OtherInfo, BookingRequestNotes, Remark
FROM dbo.Transactions ORDER BY TransDate DESC;
```

Database: `HPS_DB` @ `hpsvn.openfreightone.com:34541`

### Notes

- `Starus` là typo gốc HPS — khi viết code comment nên nhắc rõ để dev sau không sửa nhầm
- Nếu enum hoá state, cần survey giá trị distinct trên HPS trước khi define `TransactionState` enum
- `Delivered` dùng `Boolean` trong Java (parse từ bit/0/1 string)

---

## A.3 Lock / Audit / Commercial Fields

Source: `dbo.Transactions`
Ref: `docs/references/mapping/ref/sql_query_analysis.md`, `docs/references/mapping/ref/legacy_entity_mapping_review.md`

### Nhóm 1: Lock / Audit nội bộ (KHÔNG sync sang FMS)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `transLock` | bit | Cờ khoá file inbound — HPS auto-set sau save, kiểm tra qua `NoDaysLock` + `DateofPrealert` | **Skip** — cơ chế lock nội bộ HPS |
| `TransLockLog` | bit | Cờ khoá file logistics — tương tự `transLock` cho tab Logistics | **Skip** — cùng lý do |
| `Revision` | int | Số lần sửa đổi file (counter) | **Skip** — dùng JPA `version` + `modified_time` của FMS |
| `ModifyDate` | datetime | Ngày sửa cuối cùng trên HPS | **Skip** — FMS đã có `modified_time` (JPA auditing) |

### Nhóm 2: Notes / Log (append-only text)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `TransactionNotes` | ntext | Log thay đổi — HPS append text mỗi lần save (format: `[date] [user] [action]`) | **Skip** (optional phase sau) — FMS có `modified_by` + `modified_time` |
| `ReportInfor` | ntext | Thông tin báo cáo — arrival/delivery status updates, milestone notes | **Map** → `reportInfo` (text) |

### Nhóm 3: Tham chiếu thương mại (NÊN sync)

| Cột | Kiểu | Ý nghĩa | Quyết định |
|---|---|---|---|
| `OtherInfo` | nvarchar | M-B/L Type (Original / Surrendered / Seaway / Express Release) | **Map** → `mblType` |
| `OMB` | nvarchar | Original Master Bill — số MBL gốc (có thể khác MAWB khi amendment) | **Map** → `originalMasterBillNo` |
| `Destination` | nvarchar | Điểm đến cuối — khác POD (cảng dỡ hàng vs địa chỉ giao cuối) | **Map** → `finalDestination` |
| `Ref` | nvarchar | Số tham chiếu booking / manifest number | **Đã map** → `Transaction.manifestNo` |

### DateofPrealert

| Cột | Ý nghĩa | Quyết định |
|---|---|---|
| `DateofPrealert` | Ngày gửi pre-alert cho đại lý đích. HPS dùng làm điều kiện lock, nhưng bản thân có giá trị nghiệp vụ | **Map** → `preAlertDate` |

Timeline vị trí:
```
Booking → ConsignedDate → LoadingDate (ETD)
       → DateofPrealert (gửi thông báo cho agent đích)
       → ArrivalDate (ETA) → DestinationDate (giao cuối)
```

### Tổng hợp quyết định

| Cột | Quyết định | FMS field |
|---|---|---|
| `transLock` | **Skip** | — |
| `TransLockLog` | **Skip** | — |
| `Revision` | **Skip** | — |
| `ModifyDate` | **Skip** | — |
| `TransactionNotes` | **Skip** (optional) | `changeLog` |
| `DateofPrealert` | **Map** | `preAlertDate` |
| `ReportInfor` | **Map** | `reportInfo` |
| `OtherInfo` | **Map** | `mblType` |
| `OMB` | **Map** | `originalMasterBillNo` |
| `Destination` | **Map** | `finalDestination` |
| `Ref` | **Đã xong** | `manifestNo` |

---

## A.4 HAWB.CussignedDate

Status: **Implemented**
Source: `dbo.HAWB`
Ref: `docs/references/mapping/ref/sql_query_analysis.md:129`, `docs/references/mapping/ref/legacy_entity_mapping_review.md:27`

### Ý nghĩa

`CussignedDate` = typo của `ConsignedDate`. **Consigned Date** = ngày consign/handover lô hàng cho carrier — bắt đầu trách nhiệm vận chuyển. Trên HAWB gọi là "Date of Issue" hoặc "Date of Consignment".

Chỉ update ở **Inbound Save** — mốc khởi đầu shipment.

### Timeline điển hình

```
Booking → CussignedDate (handover) → IssuedDate (phát HAWB) → LoadingDate (ETD) → ArrivalDate (ETA) → DestinationDate (giao cuối)
```

### Implementation

**Entity HouseBill**: `consignedDate` (column `consigned_date`) — sửa typo trong FMS, handler vẫn đọc raw key `"CussignedDate"`.

**CDC mapping** (`HAWBCDCHandler.enrichHouseBill`):
```java
Long consignedDate = CDCMapperUtils.parseLong(data.get("CussignedDate"));
if (consignedDate != null) hb.setConsignedDate(CDCMapperUtils.toTimestamp(consignedDate));
```

**Liquibase**:
```sql
ALTER TABLE of1_fms_house_bill ADD COLUMN IF NOT EXISTS consigned_date TIMESTAMP(6);
```

**Lưu ý**: Đừng gộp với `issuedDate` — 2 khái niệm khác nhau. Nếu FMS cần state machine chi tiết, `consignedDate` xác định `BOOKED → CONSIGNED` trước `IN_TRANSIT`.

---

# B. CDC Implementation

## B.1 CDC Transactions → HouseBill + TransportPlan/Route

Status: **Implemented** — `saveDraftHouseBill` sẽ bị **xoá** trong section C (Completeness spec), ownership chuyển sang `TransactionDetailsCDCHandler`.
File: `TransactionsCDCHandler.java`

### Goal

Khi CDC `dbo.Transactions` flow vào FMS, ngoài upsert `IntegratedTransaction` + `of1_fms_transactions`:
1. Tạo/đảm bảo có **HouseBill draft** gắn với transaction.
2. Build **TransportPlan** + **TransportRoute** theo thông tin transit trên MSSQL.

### MSSQL Columns (4 cột transit)

| Cột | Ý nghĩa |
|---|---|
| `TransitPortFrom` | Cảng transit đầu vào |
| `TransitPortDes` | Cảng transit đầu ra (thường trùng `TransitPortFrom`) |
| `ETDTransit` | Ngày/giờ rời transit port |
| `ETATransit` | Ngày/giờ đến transit port |

### Target Entities

- `of1_fms_house_bill` — neo vào `transaction_id`, unique theo `hawb_no`
- `of1_fms_transport_plan` — neo vào `house_bill_id`, chứa POL/POD + depart/arrival tổng
- `of1_fms_transport_route` — các chặng con, có `sort_order`

### Flow

```
saveFmsTransaction
  → save Transaction (FMS)
  → saveDraftHouseBill(data, fmsTx)        // trả về HouseBill
  → saveTransportPlan(data, hb, fmsTx)     // rebuild plan + routes
```

### saveDraftHouseBill

- Lookup theo `HWBNO` (unique) → fallback `findByTransactionId`
- Nếu không có → tạo draft: `companyId` từ `CDCTenantContext`, `transactionId`, `hawbNo`, `typeOfService`, `shipmentType`, `issuedDate` copy từ `fmsTx`

### buildTransportPlan

**Plan header**: `fromLocation=PortofLading`, `toLocation=PortofUnlading`, `departTime=LoadingDate`, `arrivalTime=ArrivalDate`

**Normalize transit**: nếu chỉ 1 trong 2 cột `TransitPortFrom`/`TransitPortDes` có giá trị → dùng chung cho cả 2.

**Route logic**:

| Case | Routes |
|---|---|
| Không transit | 1 route: `POL → POD` |
| Có transit | Leg1: `POL → Transit` (depart=LoadingDate, arrival=ETATransit), Leg2: `Transit → POD` (depart=ETDTransit, arrival=ArrivalDate) |

**Route fields**: `transportNo=FlghtNo`, `carrierLabel=lookupPartnerName(ColoaderID)`, location codes qua `lookupLocationCode(label)`

### User Decisions (confirmed)

1. Lookup transaction by code → lookup house bill theo transaction id → tạo draft nếu chưa có
2. Transit chỉ 1 port: `fromLocation → transitPort → toLocation`
3. Rebuild routes: mỗi lần CDC update → xoá plan cũ rồi build lại, không merge

### Code Structure

```java
saveFmsTransaction(...)                  // upsert fms_transaction
  └── saveDraftHouseBill(data, fmsTx)    // returns HouseBill (draft nếu cần)
  └── saveTransportPlan(data, hb, fmsTx) // delete old + build + save
        └── buildTransportPlan(...)      // plan header + routes
              └── newRoute(...)          // helper cho từng TransportRoute
```

**Dependencies mới inject**: `HouseBillRepository`, `TransportPlanRepository` (đã có sẵn: `SettingLocationRepository`, `IntegratedPartnerRepository`).

### Notes / TODO

- `saveDraftHouseBill` sẽ bị xoá — xem section C, Task 6. `TransportPlan` logic giữ lại nhưng refactor signature.
- HouseBill chưa có field `status`/`draft` rõ ràng — thêm enum status sau (deferred)
- Chưa xử lý multi-transit (schema MSSQL chỉ expose 1 cặp transit)
- Pipeline (booking_process_id / status update) xử lý ở bước sau

---

# C. HouseBill CDC Completeness — Design

Scope: Sub-project 1 of "HouseBill + HouseBillDetail mapping" decomposition
Status: Draft — pending user review

## Context

Three CDC handlers currently write to `of1_fms_house_bill`:

1. `TransactionsCDCHandler.saveDraftHouseBill()` — creates draft when `Transactions` CDC fires.
2. `TransactionDetailsCDCHandler.upsert()` — writes from `TransactionDetails`.
3. `HAWBCDCHandler.enrichHouseBill()` — writes from `HAWB`.

Problems:
- Overlapping writes cause race conditions; last writer wins non-deterministically (cargo weights written by both #2 and #3).
- Many fields on `HouseBill` entity are unmapped despite MSSQL sources being available.
- Partner code lookups only populate labels, not foreign keys — breaking FK-based queries.
- No single source of truth for shared fields.

This spec fixes data completeness, introduces shared lookup utility, enforces ownership matrix, and removes the draft-creation path.

## Goals

1. Every field on `HouseBill` entity is mapped from an explicit HPS source (or documented as FMS-internal).
2. Each field has exactly one owning CDC handler; no race between handlers.
3. Partner/account codes are resolved to FK ids, not just labels.
4. Shared lookup logic lives in one testable helper.

## Non-goals

- `HouseBillStatus` enum/workflow (deferred).
- `of1_fms_air/sea/truck/logistics_house_bill_detail` mapping (Sub-project 2 & 3).
- UI changes for House Bill editor.
- CDC ordering guarantees / snapshot replay for out-of-order events.
- `bookingProcessId` linking (FMS-internal; set by booking flow).

## Ownership matrix

| Field | Owner | HPS source |
|---|---|---|
| `hawbNo` (PK) | TransactionDetails | `TransactionDetails.HWBNO` |
| `companyId` | TransactionDetails (at create) | `CDCTenantContext` |
| `transactionId` | TransactionDetails | Lookup `of1_fms_transactions.id` by `TRANSID` |
| `typeOfService` | TransactionDetails | Copied from `of1_fms_transactions.type_of_service` via transaction lookup |
| `shipmentType` | TransactionDetails | `TransactionDetails.ShipmentType` |
| `clientPartnerId` / `clientLabel` | TransactionDetails | `TransactionDetails.ContactID` → `IntegratedPartner` lookup |
| `salemanAccountId` / `salemanLabel` | TransactionDetails | `TransactionDetails.SalesManID` → `SettingsUserRole` lookup |
| `handlingAgentPartnerId` / `handlingAgentLabel` | HAWB (primary), fallback Transaction | `HAWB.HBAgentID` → `IntegratedPartner`; fallback `Transaction.handlingAgent*` |
| `assigneeAccountId` / `assigneeLabel` | HAWB | Copy `of1_fms_transactions.createdByAccountId/Name` via `transactionId` |
| `descOfGoods` | TransactionDetails | `TransactionDetails.Description` |
| `packagingType` | TransactionDetails | `TransactionDetails.UnitDetail` |
| `cargoGrossWeightInKgs` | **HAWB** | `HAWB.GrossWeight` |
| `cargoChargeableWeightInKgs` | **HAWB** | `HAWB.ChargeableWeight` |
| `cargoVolumeInCbm` | **HAWB** | `HAWB.Dimension` |
| `containerVol` | **HAWB** | `HAWB.ContainerSize` |
| `packageQuantity` | **HAWB** | `HAWB.Pieces` |
| `consignedDate` | HAWB | `HAWB.CussignedDate` |
| `issuedDate` | TransactionDetails | Copy `of1_fms_transactions.issued_date` via transaction lookup |
| `bookingProcessId` | FMS-only | Null from CDC |

**Key rule**: cargo weights / container / packages are owned exclusively by HAWB.

## Architecture

### Removed code

- `TransactionsCDCHandler.saveDraftHouseBill()` — deleted.
- Call site in `saveFmsTransaction` — removed.

### New component — `HouseBillLookupSupport`

Location: `module/transaction/src/main/java/of1/fms/module/transaction/cdc/HouseBillLookupSupport.java`
Type: Spring `@Component`

```java
public record PartnerRef(Long id, String label) {}
public record AccountRef(Long id, String label) {}
public record TransactionRef(
    Long id, TypeOfService typeOfService, Date issuedDate,
    Long handlingAgentPartnerId, String handlingAgentLabel,
    Long createdByAccountId, String createdByAccountName
) {}

public class HouseBillLookupSupport {
  PartnerRef resolveClient(String contactId);
  AccountRef resolveSaleman(String salesmanUsername);
  PartnerRef resolveHandlingAgent(String hawbAgentId, TransactionRef transactionRef);
  TransactionRef resolveTransaction(String transId);
}
```

Behavior: null-safe, lookup miss returns ref with `id=null, label=rawCode`, logs at `debug`.

### Refactor — `TransactionDetailsCDCHandler`

Inject `HouseBillLookupSupport`. In `upsert(data)`:

```java
String hwbNo = CDCMapperUtils.trimString(data.get("HWBNO"));
if (hwbNo == null) return;

synchronized (lockManager.getLock("housebill:" + hwbNo)) {
  HouseBill hb = houseBillRepo.findByHawbNo(hwbNo);
  if (hb == null) {
    hb = new HouseBill();
    hb.setHawbNo(hwbNo);
    hb.setCompanyId(CDCTenantContext.getCompanyId());
  }

  // Transaction lookup → transactionId, typeOfService, issuedDate
  TransactionRef txRef = lookupSupport.resolveTransaction(transId);
  if (txRef != null) { hb.setTransactionId(txRef.id()); ... }

  // Client (ContactID → IntegratedPartner), Saleman (SalesManID → SettingsUserRole)
  // TransactionDetails-owned plain fields: descOfGoods, packagingType
  // NOTE: cargo weights OWNED BY HAWB — do NOT set here.

  houseBillRepo.save(hb);
}
```

### Refactor — `HAWBCDCHandler.enrichHouseBill`

```java
synchronized (lockManager.getLock("housebill:" + hawbNo)) {
  HouseBill hb = houseBillRepo.findByHawbNo(hawbNo);
  if (hb == null) return; // Wait for TransactionDetails CDC

  // HAWB-owned: cargo weights, container, consigned date
  // Handling agent (HAWB primary, Transaction fallback)
  // Assignee = Transaction.createdBy*

  houseBillRepo.save(hb);
}
```

### Side change — `TransactionsCDCHandler`

Populate `Transaction.handlingAgentPartnerId` (not just label) via `lookupSupport.resolveHandlingAgent`.

## Data flow

```
1. Transactions CDC        → of1_fms_transactions (+ handlingAgent* now with id)
2. TransactionDetails CDC  → of1_fms_house_bill (CREATE skeleton + TD-owned fields)
3. HAWB CDC                → of1_fms_house_bill (UPDATE HAWB-owned fields)
                              Skips if HB not yet created
```

**CDC ordering limitations** (accepted):
- HAWB before TransactionDetails: enrich skips; next HAWB update re-fires.
- TransactionDetails before Transactions: `resolveTransaction` returns null; fields stay null until next update.

**Lock key**: both handlers use `housebill:{hwbNo}`.

## Error handling

| Condition | Handling |
|---|---|
| Lookup miss | Return ref with `id=null, label=rawCode`. Log `debug`. |
| HAWB before TransactionDetails | `enrichHouseBill` returns early. |
| TransactionDetails before Transactions | Dependent fields stay null. Next CDC fills them. |
| DB exception | Bubble → rollback → CDC framework retry. |

## Testing

**Unit — `HouseBillLookupSupportTest`**: Mock repos with Mockito. Test resolveClient/resolveSaleman/resolveHandlingAgent/resolveTransaction (happy / null / not-found).

**Integration — `HouseBillCDCIntegrationIT`**: Testcontainers Postgres. 4 scenarios:
1. Full happy path: all fields populated correctly.
2. HAWB before TransactionDetails: enrich skipped → re-fire succeeds.
3. TransactionDetails before Transactions: transactionId null → re-fire fills.
4. Ownership enforcement: HAWB doesn't overwrite TD-owned fields.

Coverage target: 80%+.

## Migration

**No Liquibase changes**. All columns already exist. Code backward compat: existing draft HB rows updated normally by next CDC event. Weight staleness window until next HAWB CDC fires.

## Limitations / accepted risks

1. CDC ordering: HAWB-before-TransactionDetails loses data until next HAWB update.
2. Partner uniqueness assumption (`partner_code` unique).
3. Missing assignee for non-HAWB shipments.
4. Weight staleness window after deployment.

## Checklist

- [ ] Create `HouseBillLookupSupport` with 4 methods + 3 record types
- [ ] Unit tests for `HouseBillLookupSupport`
- [ ] Refactor `TransactionDetailsCDCHandler.upsert` — add lookups, remove weight writes
- [ ] Refactor `HAWBCDCHandler.enrichHouseBill` — add lock + lookups + assignee + handling agent
- [ ] Remove `TransactionsCDCHandler.saveDraftHouseBill` + call site
- [ ] Update `TransactionsCDCHandler` to populate `handlingAgentPartnerId`
- [ ] Integration tests for 4 scenarios
- [ ] Verify no Liquibase changes needed
- [ ] Update `docs/references/mapping/mapping-transactions.md` with ownership matrix

---

# D. HouseBill CDC Completeness — Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every field on `HouseBill` entity populated correctly from HPS CDC with no race between handlers.

**Architecture:** Introduce `HouseBillLookupSupport` (Spring `@Component`) that centralises partner/user/transaction lookups. Enforce ownership matrix. Remove `saveDraftHouseBill` entirely.

**Tech Stack:** Java 21, Spring Boot, JPA, JUnit 5, Mockito, AssertJ, Testcontainers.

## File structure

**New files:**
- `module/transaction/.../cdc/HouseBillLookupSupport.java`
- `module/transaction/.../cdc/HouseBillLookupSupportTest.java`

**Modified files:**
- `TransactionsCDCHandler.java` — remove `saveDraftHouseBill`; add `handlingAgentPartnerId` lookup
- `TransactionDetailsCDCHandler.java` — inject lookup support, add lookups, remove cargo weight writes
- `HAWBCDCHandler.java` — add lock; inject lookup support; set handling agent + assignee
- `docs/references/mapping/mapping-transactions.md` — update ownership matrix

---

## Task 1: Create HouseBillLookupSupport skeleton + record types

- [ ] **Step 1: Write failing skeleton test**

```java
@ExtendWith(MockitoExtension.class)
class HouseBillLookupSupportTest {
  @Mock IntegratedPartnerRepository partnerRepo;
  @Mock SettingsUserRoleRepository userRoleRepo;
  @Mock TransactionRepository transactionRepo;
  HouseBillLookupSupport support;

  @BeforeEach
  void setUp() {
    support = new HouseBillLookupSupport(partnerRepo, userRoleRepo, transactionRepo);
  }

  @Test void resolveClient_nullInput_returnsNull() {
    assertThat(support.resolveClient(null)).isNull();
  }
}
```

- [ ] **Step 2: Run test → verify FAIL** (`cannot find symbol HouseBillLookupSupport`)
- [ ] **Step 3: Create skeleton class** — `@Component`, 3 records, 4 stub methods returning null
- [ ] **Step 4: Run test → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): add HouseBillLookupSupport skeleton`

---

## Task 2: Implement resolveClient

- [ ] **Step 1: Write failing tests** — `resolveClient_found_returnsPartnerRef`, `resolveClient_notFound_returnsRefWithRawCode`
- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement**

```java
public PartnerRef resolveClient(String contactId) {
  if (contactId == null) return null;
  try {
    IntegratedPartner p = partnerRepo.getByPartnerCode(contactId);
    if (p != null) return new PartnerRef(p.getId(), p.getLabel());
  } catch (Exception e) { log.debug("Client partner lookup failed: {}", contactId); }
  return new PartnerRef(null, contactId);
}
```

- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveClient`

---

## Task 3: Implement resolveSaleman

- [ ] **Step 1: Write failing tests** — found / not-found / null
- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — `userRoleRepo.getByBfsoneUsername(username)` → `AccountRef(accountId, fullName)`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveSaleman`

---

## Task 4: Implement resolveTransaction

- [ ] **Step 1: Write failing tests** — found (full ref) / not-found / null

```java
@Test void resolveTransaction_found_returnsFullRef() {
  Transaction tx = new Transaction();
  tx.setId(10L); tx.setTypeOfService(TypeOfService.AIR_IMPORT);
  tx.setIssuedDate(new Date(1_700_000_000L));
  tx.setHandlingAgentPartnerId(55L); tx.setHandlingAgentLabel("Agent X");
  tx.setCreatedByAccountId(77L); tx.setCreatedByAccountName("Owner");
  when(transactionRepo.findByCode("TR001")).thenReturn(tx);

  TransactionRef ref = support.resolveTransaction("TR001");
  assertThat(ref.id()).isEqualTo(10L);
  assertThat(ref.typeOfService()).isEqualTo(TypeOfService.AIR_IMPORT);
  // ... assert all fields
}
```

- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — `transactionRepo.findByCode(transId)` → build `TransactionRef`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveTransaction`

---

## Task 5: Implement resolveHandlingAgent

- [ ] **Step 1: Write failing tests** — hawb present / hawb null + tx fallback / both null

```java
@Test void resolveHandlingAgent_hawbIdPresent_usesHawb() { ... }
@Test void resolveHandlingAgent_hawbNull_fallbackToTransaction() { ... }
@Test void resolveHandlingAgent_bothNull_returnsNull() { ... }
```

- [ ] **Step 2: Run → verify FAIL**
- [ ] **Step 3: Implement** — if hawbAgentId → `resolvePartnerById(hawbAgentId)`, else fallback `transactionRef.handlingAgent*`
- [ ] **Step 4: Run → verify PASS**
- [ ] **Step 5: Commit** `feat(cdc): implement HouseBillLookupSupport.resolveHandlingAgent`

---

## Task 6: Remove TransactionsCDCHandler.saveDraftHouseBill

- [ ] **Step 1: Remove method + call site** — update `saveTransportPlan` signature to resolve HouseBill inline
- [ ] **Step 2: Run existing tests → verify nothing broken**
- [ ] **Step 3: Commit** `refactor(cdc): remove saveDraftHouseBill from TransactionsCDCHandler`

---

## Task 7: TransactionsCDCHandler — populate handlingAgentPartnerId

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Replace label-only mapping** with `lookupSupport.resolveHandlingAgent` → set both `id` and `label`
- [ ] **Step 3: Build + run tests**
- [ ] **Step 4: Commit** `feat(cdc): populate Transaction.handlingAgentPartnerId via lookup`

---

## Task 8: Refactor TransactionDetailsCDCHandler.upsert

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Rewrite `upsert(data)` body** — add lock, transaction/client/saleman lookup, remove cargo weight writes
- [ ] **Step 3: Build + run tests**
- [ ] **Step 4: Commit** `refactor(cdc): TransactionDetails uses HouseBillLookupSupport + ownership matrix`

---

## Task 9: Refactor HAWBCDCHandler.enrichHouseBill

- [ ] **Step 1: Inject HouseBillLookupSupport**
- [ ] **Step 2: Rewrite `enrichHouseBill`** — add lock, cargo weights, consigned date, handling agent + assignee lookup
- [ ] **Step 3: Build**
- [ ] **Step 4: Commit** `refactor(cdc): HAWB handler enriches HouseBill with lookups + lock`

---

## Task 10: Integration tests (4 scenarios)

Create: `HouseBillCDCIntegrationIT.java` (Testcontainers Postgres)

- [ ] **Step 1: Write 4 test methods**
  1. `fullHappyPath_allFieldsPopulated`
  2. `hawbBeforeTransactionDetails_enrichSkipped`
  3. `transactionDetailsBeforeTransactions_transactionIdNull`
  4. `ownershipEnforced_hawbDoesNotOverwriteTDFields`
- [ ] **Step 2: Run IT**
- [ ] **Step 3: Fix failures iteratively**
- [ ] **Step 4: Commit** `test(cdc): integration tests for HouseBill CDC ownership + ordering`

---

## Task 11: Update mapping doc

- [ ] **Step 1: Update `of1_fms_house_bill` section** in `docs/references/mapping/mapping-transactions.md` with ownership matrix
- [ ] **Step 2: Commit** `docs(mapping): update house_bill ownership matrix`

---

## Task 12: Final verification

- [ ] **Step 1: Full module build + test** — `./gradlew :module-transaction:build`
- [ ] **Step 2: Manual smoke check** (optional)
- [ ] **Step 3: Push branch**
- [ ] **Step 4: Open PR** — `feat(cdc): HouseBill CDC completeness with ownership matrix`

---

## Plan notes

- Task 1–5: build `HouseBillLookupSupport` via strict TDD (one method per task).
- Task 6: remove legacy draft path **before** new handlers use lookup.
- Task 7: fix prerequisite (`handlingAgentPartnerId` must be populated for HAWB fallback).
- Task 8–9: wire lookup into surviving handlers.
- Task 10: single IT file with 4 scenarios (limit test container startup overhead).
- All changes are code-only; no Liquibase migration required.

---

# Appendix

## HPS Typo Reference

| HPS Column | Nghĩa gốc |
|---|---|
| `Starus` | Status |
| `TpyeofService` | TypeOfService |
| `CussignedDate` | ConsignedDate |
| `Noofpieces` | NoOfPieces |
| `FlghtNo` | FlightNo |
| `Pieaces` | Pieces |

## Field dễ nhầm lẫn

### `masterBillNo` vs `originalMasterBillNo` (OMB)
- `masterBillNo` (← MAWB): số MBL/MAWB hiện tại (có thể đã amended).
- `originalMasterBillNo` (← OMB): số MBL gốc ban đầu trước khi amend.
- Thường giống nhau. Khác khi carrier issue correction/amendment.

### `toLocationLabel` (POD) vs `finalDestination` (Destination)
- `toLocationLabel` (← PortofUnlading): cảng dỡ hàng (port/airport level).
- `finalDestination` (← Destination): địa chỉ giao cuối cùng (warehouse, door, ICD).
- Ví dụ: POD = "Cat Lai Port", finalDestination = "KCN Binh Duong, Lot A1-5".

### `mblType` (OtherInfo) — giá trị phổ biến
- "Original" — vận đơn gốc (cần surrender để nhận hàng).
- "Surrendered" — đã surrender (nhận hàng bằng bản copy).
- "Seaway Bill" — vận đơn điện tử (không cần surrender).
- "Express Release" — giải phóng nhanh (telex release).

---

---

# E. Schema Mismatch — CDC MSSQL → PostgreSQL

## E.1 Bối cảnh: Tại sao schema không khớp?

### Hệ thống cũ (HPS BFS One — MSSQL)

Thiết kế **flat**: bảng `Transactions` chứa mọi thứ — cả thông tin master bill lẫn thông tin per-HAWB.

```
dbo.Transactions (MSSQL)
├── TransID, TransDate, MAWB, PortofLading...     ← master-level (đúng)
├── BookingNo, BookingRequestNotes, PaymentTerm    ← per-HAWB (lẫn vào)
├── ExpressNotes, Remark                           ← per-HAWB (lẫn vào)
├── Ref (manifest)                                 ← sea-specific (lẫn vào)
└── GrossWeight, Noofpieces, Description           ← aggregate summary
```

Lý do: HPS không phân biệt master vs house bill. Mỗi transaction thường chỉ có 1 HAWB, nên mọi thứ gom vào 1 bảng cho tiện.

### Hệ thống mới (FMS — PostgreSQL)

Thiết kế **normalized**: tách rõ 3 tầng.

```
of1_fms_transactions          ← Master Bill (1 lô hàng)
    └── of1_fms_house_bill    ← House Bill (1:N HAWB per master)
        └── of1_fms_*_house_bill_detail  ← Chi tiết theo loại dịch vụ (air/sea/truck/logistics)
```

### Vấn đề phát sinh

Khi CDC đồng bộ data từ MSSQL → PostgreSQL:
- Một số field trên `Transactions` **không thuộc về** `of1_fms_transactions` trong schema mới
- Nhưng entity đích (`HouseBill`, `SeaHouseBillDetail`) **chưa tồn tại** tại thời điểm CDC event đến
- Kết quả: field bị ghi vào entity sai, hoặc bị mất

---

## E.2 Ba vấn đề cụ thể

### Vấn đề 1: Field per-HAWB mắc kẹt trên Transaction

**Hiện trạng**: 5 field sau đây nằm trên `Transaction.java` nhưng **không tồn tại trên `HouseBill.java`**:

| Field | MSSQL source | Tại sao thuộc HouseBill? |
|---|---|---|
| `bookingNo` | `Transactions.BookingNo` | Mỗi HAWB có booking riêng với carrier |
| `bookingRequestNote` | `Transactions.BookingRequestNotes` | Ghi chú đặt chỗ là per-customer, per-HAWB |
| `paymentTerm` | `Transactions.PaymentTerm` | HAWB A có thể Prepaid, HAWB B có thể Collect |
| `note` | `Transactions.ExpressNotes` | Ghi chú trên bill — mỗi HAWB khác nhau |
| `remark` | `Transactions.Remark` | Ghi chú nội bộ — mỗi HAWB khác nhau |

**Ví dụ thực tế**:
```
Transaction BIHCM008238/25 (Sea Export)
├── HAWB-001: client ABC, paymentTerm = Prepaid, bookingNo = BK-001
├── HAWB-002: client XYZ, paymentTerm = Collect, bookingNo = BK-002
└── Transaction.paymentTerm = "Prepaid" ← GIÁ TRỊ CỦA AI? Ambiguous!
```

Khi chỉ có 1 HAWB → không thấy vấn đề. Khi có 2+ HAWB → data mâu thuẫn.

**Bằng chứng trong code**: `Transaction.java` line 215, 228 có comment:
```java
// REMIND: Dan - review with a Quy move to House Bill entity
```

**Hậu quả**:
- UI hiển thị paymentTerm/bookingNo ở detail view → đọc từ Transaction → sai khi có nhiều HAWB
- Không thể filter/search theo paymentTerm per-HAWB
- Data integrity: HouseBill entity thiếu thông tin quan trọng

### Vấn đề 2: Field sea-specific mắc kẹt trên Transaction

**Hiện trạng**: `manifestNo` (`Transactions.Ref`) nằm trên `Transaction.java`.

| Field | MSSQL source | Nên thuộc về |
|---|---|---|
| `manifestNo` | `Transactions.Ref` | `SeaHouseBillDetail.manifestNo` |

**Tại sao sai?**
- Manifest number chỉ có ý nghĩa với **sea shipment** (không phải air/truck/logistics)
- Trong schema mới, nó thuộc `SeaHouseBillDetail` — entity con chuyên biệt cho sea
- `HAWBDETAILSCDCHandler` đã set đúng `manifestNo` trên `SeaHouseBillDetail` (từ `HAWBDETAILS`)
- Nhưng `Transaction` cũng giữ 1 bản copy riêng → 2 nguồn, dễ inconsistent

**Hậu quả**: Nhẹ hơn vấn đề 1 vì `SeaHouseBillDetail` đã có field này. Nhưng `Transaction.manifestNo` là bản copy thừa, gây confusion cho developer.

### Vấn đề 3: Field duplicate OK nhưng cần hiểu rõ vai trò

**Hiện trạng**: 6 field tồn tại trên CẢ `Transaction` VÀ `HouseBill`, mỗi bên set bởi handler khác nhau.

| Field | Transaction (aggregate) | HouseBill (per-HAWB) |
|---|---|---|
| `descOfGoods` | `Transactions.Description` | `TransactionDetails.Description` |
| `cargoGrossWeightInKgs` | `Transactions.GrossWeight` | `HAWB.GrossWeight` |
| `cargoVolumeInCbm` | `Transactions.Dimension` | `HAWB.Dimension` |
| `cargoChargeableWeightInKgs` | `Transactions.ChargeableWeight` | `HAWB.ChargeableWeight` |
| `packageQuantity` | `Transactions.Noofpieces` | `HAWB.Pieces` |
| `packagingType` | `Transactions.UnitPieaces` | `TransactionDetails.UnitDetail` |

**Kết luận: KHÔNG phải vấn đề.**
- Transaction giữ tổng số (aggregate of all HAWBs)
- HouseBill giữ chi tiết per-HAWB
- 2 handler set độc lập, mỗi bên có data source riêng
- Mô hình master-detail chuẩn

---

## E.3 Gốc rễ: Timing mismatch trong CDC pipeline

Tại sao Vấn đề 1 & 2 xảy ra? Vì thứ tự CDC events:

```
T0  Transactions INSERT (MSSQL)
    → TransactionsCDCHandler chạy
    → Transaction entity CREATED ✅
    → HouseBill CHƯA TỒN TẠI ❌
    → bookingNo, note, remark... GHI LÊN TRANSACTION (đành vậy)

T1  TransactionDetails INSERT (MSSQL, vài ms sau)
    → TransactionDetailsCDCHandler chạy
    → HouseBill skeleton CREATED ✅
    → NHƯNG KHÔNG KÉO bookingNo/note/remark TỪ TRANSACTION XUỐNG ❌

T2  HAWB INSERT (MSSQL)
    → HAWBCDCHandler chạy
    → HouseBill enriched (weights, consignee, agent...) ✅
    → VẪN KHÔNG KÉO bookingNo/note/remark XUỐNG ❌

T3  HAWBDETAILS INSERT (MSSQL)
    → HAWBDETAILSCDCHandler chạy
    → SeaHouseBillDetail CREATED, manifestNo SET ✅ (từ HAWBDETAILS riêng)
```

**Gap rõ ràng**: Không có bước nào propagate 5 field Loại 1 từ Transaction → HouseBill.

**Tại sao gap này tồn tại?**
- Ban đầu code xử lý đúng thứ tự: Transaction ghi trước, HouseBill ghi sau
- Nhưng 5 field per-HAWB bị "mắc kẹt" trên Transaction vì HouseBill entity ban đầu không có các field này
- Không ai thêm bước propagation vì HouseBill.java chưa có columns để nhận

---

## E.4 Năm giải pháp

### Giải pháp A — Propagation đơn giản (Quick fix)

**Tư tưởng**: Giữ nguyên mọi thứ. Chỉ thêm field vào HouseBill + thêm logic copy data.

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity
        bookingNo, bookingRequestNote, paymentTerm, note, remark

Bước 2: TransactionDetailsCDCHandler (T1) — khi tạo HouseBill:
        → Đọc parent Transaction
        → Copy 5 fields xuống HouseBill (nếu HouseBill chưa có giá trị)

Bước 3: TransactionsCDCHandler (T0) — khi Transaction UPDATE:
        → Tìm HouseBills đã tồn tại
        → Push 5 fields xuống (nếu HouseBill chưa có giá trị)
```

**Transaction entity**: GIỮ NGUYÊN 5 field (backward compatible).

**Ưu điểm**: Effort thấp nhất, risk thấp nhất, backward compatible.
**Nhược điểm**: Data duplicate — 5 fields tồn tại trên CẢ Transaction VÀ HouseBill. Phải đồng bộ khi update. Developer dễ nhầm "đọc từ đâu mới đúng?"

---

### Giải pháp B — Propagation + Ownership documentation

**Tư tưởng**: Giống A, nhưng thêm convention rõ ràng cho developer biết field nào là "bản gốc" vs "bản copy".

**Cách làm**: Giống A, cộng thêm:

```java
// Transaction.java — đánh dấu field là copy
/** @denorm Source of truth: HouseBill.bookingNo. Copy for list/search perf. */
private String bookingNo;

/** @denorm Source of truth: HouseBill.paymentTerm. Copy for list/search perf. */
private FreightTerm paymentTerm;
```

**Quy tắc đọc**:
- **Detail view** (xem chi tiết 1 transaction): đọc từ HouseBill (source of truth)
- **List view** (danh sách): đọc từ Transaction (denormalized, nhanh)

**Ưu điểm**: Developer biết rõ "cái nào là gốc, cái nào là copy". Giảm confusion.
**Nhược điểm**: Convention-based — phụ thuộc vào kỷ luật team. Nếu developer mới không đọc comment → vẫn nhầm.

---

### Giải pháp C — Xóa field sai khỏi Transaction + staging buffer

**Tư tưởng**: "Dọn sạch" Transaction entity. Transaction chỉ chứa đúng master-level data. HAWB-level fields chỉ tồn tại trên HouseBill.

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity

Bước 2: XÓA 5 columns khỏi Transaction entity

Bước 3: Khi Transactions CDC đến (T0) mà HouseBill chưa có:
        → Lưu 5 fields vào bảng staging: of1_fms_cdc_pending_fields
          (transaction_code, field_name, field_value, created_at)

Bước 4: Khi TransactionDetails CDC đến (T1) và tạo HouseBill:
        → Check pending_fields cho transaction này
        → Apply lên HouseBill
        → Xóa pending records

Bước 5: DB migration: chuyển data cũ từ Transaction → HouseBill, drop columns
```

**Ưu điểm**: Schema sạch nhất. Không duplicate. Không ambiguous.
**Nhược điểm**: Effort cao. Cần migration + bảng staging mới. UI/API phải đổi query source. Risk medium.

---

### Giải pháp D — CQRS: Dùng IntegratedTransaction làm Read Model (Recommended long-term)

**Insight quan trọng**: Project ĐÃ CÓ `IntegratedTransaction` — entity denormalized song song, chứa MỌI field (cả master lẫn HAWB-level). Đây chính là **Read Model** trong pattern CQRS, chỉ chưa được commit vào vai trò đó.

**Hiện tại `Transaction` đang đóng 2 vai:**
1. Write Model (domain entity, normalized) — vai trò đúng
2. Read Model (denormalized, cho UI list/search) — vai trò sai, nên là IntegratedTransaction

**Tư tưởng**: Tách rõ 2 vai. Transaction chỉ làm Write Model. IntegratedTransaction làm Read Model.

```
┌─────────────────────────────────────────────────────────────┐
│                    WRITE MODEL (Normalized)                  │
│                                                             │
│  Transaction                    HouseBill                   │
│  ├── code                       ├── hawbNo                  │
│  ├── masterBillNo               ├── bookingNo         NEW   │
│  ├── fromLocationCode           ├── bookingRequestNote NEW  │
│  ├── toLocationCode             ├── paymentTerm        NEW  │
│  ├── loadingDate                ├── note               NEW  │
│  ├── arrivalDate                ├── remark             NEW  │
│  ├── typeOfService              ├── clientPartnerId         │
│  ├── status                     ├── cargoGrossWeight...     │
│  ├── carrierPartnerId           └── ...                     │
│  ├── cargoGrossWeight (agg)                                 │
│  └── ...                        SeaHouseBillDetail          │
│  ❌ KHÔNG CÒN: bookingNo,      ├── manifestNo (SOT)        │
│     paymentTerm, note, remark   └── ...                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    READ MODEL (Denormalized)                 │
│                                                             │
│  IntegratedTransaction (ĐÃ CÓ SẴN)                        │
│  ├── transactionId, transactionDate, etd, eta               │
│  ├── typeOfService, status, manifestNo                      │
│  ├── bookingRequestNote, paymentTerm, remark    ← ĐÃ CÓ    │
│  ├── fromLocationCode, toLocationCode                       │
│  ├── coloaderLabel, handlingAgentLabel                      │
│  └── ... (tất cả field gộp lại cho list/search/report)     │
│                                                             │
│  IntegratedHousebill (ĐÃ CÓ SẴN)                          │
│  ├── hawbNo, transactionId, customerName                    │
│  ├── hawbGw, hawbCw, hawbCbm                                │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Cách làm:**

```
Bước 1: Thêm 5 columns vào HouseBill entity

Bước 2: XÓA 5 columns + manifestNo khỏi Transaction entity

Bước 3: IntegratedTransaction GIỮ NGUYÊN (nó đã có sẵn tất cả field)

Bước 4: CDC handlers:
        TransactionsCDCHandler:
          → Set master fields lên Transaction (không còn HAWB fields)
          → Set TẤT CẢ fields lên IntegratedTransaction (như cũ)
          → Nếu HouseBill đã tồn tại → propagate HAWB fields xuống

        TransactionDetailsCDCHandler:
          → Tạo HouseBill skeleton
          → Pull HAWB fields từ IntegratedTransaction (buffer tự nhiên!)
            IntegratedTransaction đã nhận data từ T0 → không cần staging table

Bước 5: UI/API queries:
        - List/search → IntegratedTransaction (denormalized, nhanh)
        - Detail view → Transaction JOIN HouseBill (normalized, chính xác)
```

**Xử lý timing — IntegratedTransaction là buffer tự nhiên:**

```
T0  Transactions CDC
    → Transaction: chỉ set master fields ✅
    → IntegratedTransaction: set TẤT CẢ fields (kể cả bookingNo, remark...) ✅
    → HouseBill chưa có? OK, không sao — data đã an toàn trong IntegratedTransaction

T1  TransactionDetails CDC
    → HouseBill skeleton CREATED ✅
    → Pull bookingNo, remark... từ IntegratedTransaction → set lên HouseBill ✅
    → Data không bị mất!
```

**Ưu điểm**:
- Schema domain sạch nhất — Transaction chỉ chứa master-level
- Không cần bảng staging mới — IntegratedTransaction đã đóng vai trò buffer
- Tận dụng 100% infra có sẵn
- UI list/search không đổi gì — đã đọc IntegratedTransaction
- Rõ ràng về mặt kiến trúc: Write Model vs Read Model

**Nhược điểm**:
- Cần migration xóa columns trên Transaction
- Detail API phải đổi source (Transaction → Transaction + HouseBill join)
- IntegratedTransaction fail → HouseBill thiếu data (nhưng IntegratedTransaction đã ổn định)

---

### Giải pháp E — CDC Deferred Event Queue (generic infra)

**Tư tưởng**: Giải quyết timing ở tầng infrastructure. Bất kỳ CDC event nào mà target entity chưa sẵn sàng → lưu vào queue → tự động replay khi target có.

**Khi nào cần**: Khi CDC mở rộng thêm nhiều bảng source và timing issues trở nên pattern phổ biến (không chỉ 5 fields hiện tại).

```sql
CREATE TABLE of1_fms_cdc_deferred_event (
    id          BIGSERIAL PRIMARY KEY,
    event_key   VARCHAR(100) NOT NULL,   -- "housebill:BIHCM008238/25"
    handler     VARCHAR(100) NOT NULL,   -- "TransactionsCDCHandler"
    field_group VARCHAR(50)  NOT NULL,   -- "hawb_level_fields"
    payload     JSONB        NOT NULL,   -- subset CDC data
    created_at  TIMESTAMP    DEFAULT NOW(),
    processed   BOOLEAN      DEFAULT FALSE,
    processed_at TIMESTAMP
);
```

**Flow:**

```
T0: Transactions CDC → TransactionsCDCHandler
    ├─ Set master fields lên Transaction ✅
    ├─ HouseBill exists?
    │   ├─ YES → set HAWB fields trực tiếp ✅
    │   └─ NO  → INSERT deferred_event (payload = {bookingNo, remark...}) ⏳
    └─ Set IntegratedTransaction ✅

T1: TransactionDetails CDC → TransactionDetailsCDCHandler
    ├─ Create HouseBill ✅
    ├─ Query deferred_event WHERE event_key matches
    │   └─ Found → apply payload lên HouseBill, mark processed ✅
    └─ Done
```

**Ưu điểm**:
- Generic — giải quyết MỌI timing mismatch, không chỉ 5 fields
- Domain model sạch
- Audit trail: biết event nào bị deferred, bao lâu
- Retry-safe: data không mất

**Nhược điểm**:
- Thêm bảng + logic mới
- HouseBill thiếu data tạm thời (vài giây)
- Cần monitor expired events
- Over-engineering nếu chỉ cần cho 5 fields

---

## E.5 So sánh tổng thể

| Tiêu chí | A | B | C | D | E |
|---|---|---|---|---|---|
| **Tên** | Propagation | + Ownership docs | Xóa + Buffer | CQRS | Deferred Queue |
| **Effort** | Thấp | Thấp-TB | Cao | Trung bình | Trung bình |
| **Risk** | Thấp | Thấp | Cao | TB | Thấp |
| **Schema sạch?** | Không (duplicate) | Không (documented duplicate) | Sạch | **Sạch nhất** | Sạch |
| **Backward compatible?** | 100% | 100% | Không | Phần lớn | 100% |
| **Dùng infra sẵn?** | Dùng | Dùng | Không | **Tốt nhất** | Không |
| **Giải timing generic?** | Chỉ 5 fields | Chỉ 5 fields | Chỉ 5 fields | Phần lớn | **Tất cả** |

**Khi nào dùng?**

| Giải pháp | Giai đoạn phù hợp | Điều kiện |
|---|---|---|
| A | Ngay bây giờ | Cần unblock CDC migration nhanh |
| B | Sau A | Team cần convention rõ ràng |
| C | Refactor lớn | Quyết định xóa technical debt triệt để |
| D | Khi ổn định | Muốn kiến trúc sạch, tận dụng IntegratedTransaction |
| E | Khi scale CDC | Timing issues xuất hiện ở nhiều bảng khác |

## E.6 Lộ trình khuyến nghị

```
Phase 1 (Now)   ─── A: Thêm 5 fields vào HouseBill + propagation logic
                     → Unblock CDC. Effort: 1-2 ngày. Risk: thấp.

Phase 2 (Soon)  ─── D: CQRS cleanup
                     → Xóa 5 fields + manifestNo khỏi Transaction
                     → IntegratedTransaction làm Read Model chính thức
                     → Kết hợp B (ownership docs) cho bất kỳ field nào còn duplicate
                     → Effort: 3-5 ngày. Risk: trung bình.

Phase 3 (If needed) ─ E: Deferred Queue
                     → Chỉ khi CDC thêm 5+ bảng source mới
                     → Timing issues trở thành pattern phổ biến
                     → Effort: 2-3 ngày.
```

**Tại sao D là đích đến tốt nhất?**
1. IntegratedTransaction **ĐÃ TỒN TẠI** — đó chính là Read Model, chỉ cần chính thức hóa vai trò
2. Transaction entity trở về đúng vai domain model — sạch, dễ test, không ambiguous
3. Không cần bảng mới (khác C, E)
4. IntegratedTransaction đã nhận TẤT CẢ data từ T0 → đóng vai buffer tự nhiên cho timing issue
5. UI list/search đã đọc từ IntegratedTransaction → không đổi gì

**Nguyên tắc kiến trúc (áp dụng cho toàn bộ CDC pipeline):**

| Entity | Vai trò | Quy tắc |
|---|---|---|
| `Transaction` | Write Model, aggregate root | Chỉ master-level: code, MBL, ports, dates, carrier, status |
| `HouseBill` | Write Model, source of truth per-HAWB | Tất cả per-HAWB: client, booking, payment, notes, cargo |
| `*HouseBillDetail` | Write Model, service-specific | manifestNo (sea), truckNo (truck), cdsNo (logistics) |
| `IntegratedTransaction` | Read Model, denormalized | Gộp tất cả cho list/search/report. Chấp nhận eventual consistency |
| `IntegratedHousebill` | Read Model, denormalized | Gộp HAWB-level cho report |

---

## Liên quan

- [[260406-cdc-handler-refactor]] — Refactor CDC handler trước đó
- [[260406-cdc-handler-refactor-plan]] — Plan refactor CDC
- [[260407-customs-receipt-bot-v5-design]] — Customs receipt bot
