---
title: "FMS Mapping - Transaction"
tags: [bf1, fms, mapping]
---

# Mapping — Transaction

**Target:** `of1_fms_transactions`
**Source:** `dbo.Transactions` (MSSQL)
**CDC Handler:** `TransactionsCDCHandler` (also writes `integrated_transaction`, parses `ContainerSize` → Container, rebuilds TransportPlan)

See also: [[bf1-fms-mapping-container]] · [[bf1-fms-mapping-transport-plan]] · [[bf1-fms-mapping-house-bill]]

---

## 1. Field Mapping — Common

| FMS Column | Type | Source Column | Notes |
|---|---|---|---|
| `id` | bigserial | — | PK |
| `code` | varchar (UNIQUE) | `TransID` | Mã lô hàng |
| `company_id` | bigint | `CDCTenantContext` | From Kafka topic |
| `transaction_date` | timestamp | `TransDate` | Ngày tạo lô |
| `issued_date` | date | `IssuedDate` | |
| `loading_date` | timestamp | `LoadingDate` | ETD equivalent |
| `arrival_date` | timestamp | `ArrivalDate` | ETA equivalent |
| `type_of_service` | enum TypeOfService | `TpyeofService` | `TypeOfService.resolve()` |
| `shipment_type` | enum ShipmentType | `ModeSea` | `ShipmentType.parse()` |
| `status` | enum TransactionStatus | `Starus` + `Delivered` | Computed — see §3 |
| `master_bill_no` | varchar | `MAWB` | |
| `from_location_code` | varchar | `PortofLading` → lookup | `SettingLocationRepository.findByLabel` |
| `from_location_label` | varchar | `PortofLading` | Raw label |
| `to_location_code` | varchar | `PortofUnlading` → lookup | |
| `to_location_label` | varchar | `PortofUnlading` | |
| `transport_name` | varchar | `AirLine` (lookup partner) / `RefNoSea` | Air: partner name; Sea: vessel name |
| `transport_no` | varchar | `FlghtNo` | Flight/voyage/license plate |
| `manifest_no` | varchar | `Ref` | |
| `coloader_partner_label` | varchar | `ColoaderID` → lookup | Inbound coloader |
| `coloader_outbound_partner_label` | varchar | `ColoaderID_O` → lookup | Outbound coloader |
| `handling_agent_partner_id` | bigint | `AgentID` → lookup | Via `HouseBillLookupSupport.resolveHandlingAgent` |
| `handling_agent_label` | varchar | `AgentID` → lookup | |
| `created_by_account_name` | varchar | `Attn` → fallback `WhoisMaking` → lookup fullname | Priority: `Attn` > FMS user fullname > raw username |
| `cargo_gross_weight_in_kgs` | double | `GrossWeight` | |
| `cargo_chargeable_weight_in_kgs` | double | `ChargeableWeight` | |
| `cargo_volume_in_cbm` | double | `Dimension` (overridden by `SeaCBM` if present) | Sea uses `SeaCBM` |
| `package_quantity` | int | `Noofpieces` | |
| `packaging_type` | varchar | `UnitPieaces` | |
| `container_vol` | varchar | `ContainerSize` | Text — parsed into Container records |
| `desc_of_goods` | varchar | `Description` | |
| `note` | varchar | `ExpressNotes` | On-bill notes |
| `remark` | varchar | `Remark` | Internal staff notes |
| `booking_request_note` | varchar | `BookingRequestNotes` | Customer booking notes |
| `mbl_type` | varchar | `OtherInfo` | M-B/L Type |
| `original_master_bill_no` | varchar | `OMB` | |
| `final_destination` | varchar | `Destination` | |
| `report_info` | varchar | `ReportInfor` | |
| `pre_alert_date` | timestamp | `DateofPrealert` | |

## 2. Service-specific Additional Fields

### 2.1 Outbound Air

| FMS Column | BF1 Column | BF1 UI Label |
|---|---|---|
| `commodity` | `Description` | `Commodity` |
| `ref` | `Ref` | `B/K No` |
| `package_unit` | `UnitPieaces` | `Unit` |
| `term` | `PaymentTerm` | `Term / D.Date` |
| `note` | `ExpressNotes` | `Notes` |

### 2.2 Inbound Air

| FMS Column | BF1 Column | BF1 UI Label |
|---|---|---|
| `etd_transit` | `ETDTransit` | `Etd / T.S` |
| `eta_transit` | `ETATransit` | `Eta / T.S` |
| `commodity` | `Description` | `Commodity` |
| `package_unit` | `UnitPieaces` | `Unit` |
| `transit_port_des` | `TransitPortDes` | `Delivery` |
| `note` | `ExpressNotes` | `Notes` |

---

## 3. Status Computation

HPS has no standard status column. Two related columns:

- **`Starus`** (typo of "Status") — free-text lifecycle (`CREATE`, `OPEN`, `TERM`, `CLOSED`, `CANCEL`, ...). Updated on both Inbound and Outbound Save.
- **`Delivered`** — bit/varchar flag. True when shipment handed over to consignee. Updated on both Inbound and Outbound Save.

**Resolution order** in `TransactionsCDCHandler.computeStatus()`:

1. If `Starus` maps to `CLOSED` or `CANCELED` → keep as-is (terminal state, `Delivered` cannot override)
2. Else if `Delivered = true` → `DELIVERED`
3. Else → map `Starus` via `TransactionStatus.resolve()` (may be null)
4. If null → don't overwrite existing FMS status

`parseBoolFlag()` accepts: Boolean, Number (0/1), String (`"1"` / `"0"` / `"true"` / `"false"` / `"Y"` / `"N"`).

---

## 4. Side Effects (during upsert)

In addition to saving `of1_fms_transactions`, `TransactionsCDCHandler.saveFmsTransaction()` triggers:

1. **Container upsert** — parses `ContainerSize` text (e.g. `"2x40HC & 1x20"`) and upserts Container records by type. See [[bf1-fms-mapping-container]].
2. **Transport Plan rebuild** — deletes existing `TransportPlan` + `TransportRoute` for the HouseBill and recreates based on `PortofLading`/`PortofUnlading`/`TransitPortFrom`/`TransitPortDes`/dates. See [[bf1-fms-mapping-transport-plan]].
3. **IntegratedTransaction mirror** — parallel write to `integrated_transaction` for denormalized reporting.
