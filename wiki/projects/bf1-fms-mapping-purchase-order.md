---
title: "FMS Mapping - Purchase Order"
tags: [bf1, fms, mapping]
---

# Mapping — Purchase Order & Booking Process

**Targets:** `of1_fms_purchase_order`, `of1_fms_booking_process`
**Status:** **FMS-only** — no CDC handler, no BF1 equivalent

See also: [[bf1-fms-03-data-model|03-data-model.md §5]]

---

## 1. Why FMS-only?

BF1 doesn't have a Purchase Order concept. The legacy `BookingLocal` table is not a direct equivalent — it lacks the one-PO-to-many-bookings structure and per-POP (Purchase Order Process) lifecycle tracking.

FMS introduces the PO model to handle cases like: one customer request ("5 cartons, door-to-door, 2 early + 3 mid-month") that maps to multiple bookings, each further decomposing into multiple POPs (trucking, ocean freight, customs clearance, etc.).

See [[bf1-fms-03-data-model|03-data-model.md §5.1 Purchase Order Model]] for the full rationale and example walkthrough.

---

## 2. Record Lifecycle

Both tables are created and updated via FMS UI / REST API, not CDC.

- `of1_fms_purchase_order` — created from a customer request (e.g. sales app creates PO on booking confirmation)
- `of1_fms_booking_process` — cloned from a PO; state transitions (`draft` → `confirmed` → `closed`) tracked here
- `of1_fms_house_bill.booking_process_id` — FK link from HouseBill to its owning BookingProcess

---

## 3. Field Reference

### 3.1 `of1_fms_purchase_order`

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar (UNIQUE) | PO code |
| `order_date` | timestamp | Business date |
| `label` | varchar | Display label |
| `client_partner_id` / `client_label` | bigint / varchar | Customer |
| `assignee_account_id` / `assignee_label` | bigint / varchar | Owner |

### 3.2 `of1_fms_booking_process`

| Column | Type | Notes |
|---|---|---|
| `id` | bigserial | PK |
| `code` | varchar (UNIQUE) | Booking code |
| `type_of_service` | enum TypeOfService | Service type |
| `purchase_order_id` | bigint | FK → `of1_fms_purchase_order.id` |
| `state` | varchar | `draft` / `confirmed` / `closed` / ... |
| `close_date` | timestamp | Set when transitioning to closed |

---

## 4. Future Integration

When write-back pipelines (Phase 1) go live, BookingProcess state changes may need to sync back to BF1 `BookingLocal` for operational parity. This is not yet implemented.
