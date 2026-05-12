# CRM Sales Module Code Review & Fix

**Date:** 2026-04-12
**Project:** of1-crm
**Module:** module/sales
**Branch:** dan

---

## Scope

Review backend module sales (115 files, ~12,600 LOC), focus vao booking pipeline (UI -> Backend).

## Files Modified

- `module/sales/src/main/java/cloud/datatp/sales/booking/BookingLogic.java`
- `module/sales/src/main/java/cloud/datatp/sales/project/TaskCalendarLogic.java`
- `module/sales/src/main/java/cloud/datatp/sales/project/plugin/AMNTaskCalendarServicePlugin.java`
- `module/sales/src/main/java/cloud/datatp/sales/report/PerformanceReportLogic.java`
- `webui/crm/src/app/crm/sales/booking/UIBooking.tsx`

---

## Fixes Applied

### CRITICAL

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `BookingLogic.java:116` | Empty catch block — BFSOne booking created nhung local save fail bi nuot | Log error + re-throw RuntimeError |
| 2 | `BookingLogic.java:188` | `.get()` on empty Optional | `.orElseThrow()` |
| 3 | `TaskCalendarLogic.java:80` | `.get()` + dead null check | `.orElse(null)` |
| 4 | `PerformanceReportLogic.java:1087` | `.get()` without guard | `.orElseThrow()` with ErrorType |

### HIGH — Connection Leak & Transaction Consistency

| # | File | Issue | Fix |
|---|------|-------|-----|
| 5 | `BookingLogic` deleteBookings | `DBConnectionUtil` tao connection rieng, ngoai Spring TX | Dung `DataSourceUtils.getConnection(dataSource)` — cung TX voi JPA |
| 6 | `BookingLogic` deleteTruckCharges | Connection leak (no try-finally) + TX isolation | Same fix — Spring-managed connection, no commit/close |
| 7 | `BookingLogic` deleteCustomClearances | Same as above | Same fix |

**Giai thich:** `DataSourceUtils.getConnection(dataSource)` tra ve connection dang tham gia Spring `@Transactional` hien tai (tu `BookingService`). Raw JDBC qua `DeleteGraphBuilder` chay tren cung connection/transaction voi JPA. Spring commit khi method return thanh cong, rollback neu exception. Khong can manual commit/close.

### HIGH — Frontend & Backend Bugs

| # | File | Issue | Fix |
|---|------|-------|-----|
| 8 | `UIBooking.tsx:305` | UI text "1000 characters" nhung MAX = 500 | Fix text "500 characters" |
| 9 | `UIBooking.tsx:407-424` | `onPreCommit` return thay vi throw — form van submit | Doi thanh `throw new Error(...)` |
| 10 | `BookingLogic.java:215` | Error message log `payer` (null) thay vi ID | Log `sellingRate.getPayerPartnerId()` |
| 11 | `AMNTaskCalendarServicePlugin:337-338` | Ternary operator precedence bug — email hien thi "TBD - true/false" | Them parentheses cho ca 2 ternary |
| 12 | `TaskCalendarLogic:138` | Pass `null` context vao `plugin.onPreSave()` | Pass `context` object |

### TODO (noted in code)

| # | File | Note |
|---|------|------|
| 1 | `TaskCalendarLogic:223` | `// TODO: Move email config` — hardcoded `dcenter@beelogistics.com` |
| 2 | `AMNTaskCalendarServicePlugin:87` | `// TODO: Move email config` — same |

---

## Architecture Notes

### Booking Pipeline Flow

```
UIBookingList (list) -> click -> BookingService.getBooking() -> UIBooking popup
UIBookingUtils.onNewBooking (from Quotation) -> BookingService.newBooking() -> UIBooking popup
UIBooking (editor):
  - "Draft IB" -> BookingService.saveBooking()
  - "Push to BFSOne" -> BookingService.sendBFSOneIBooking()
  - "Push as New IB" -> BookingService.resendBFSOneIBooking()

BookingService (@Transactional) -> BookingLogic -> Repositories + BFSOneCRMLogic (external)
```

### Key Design Decision: DataSourceUtils vs DBConnectionUtil

- `getDBConnectionUtil()` tao connection moi tu DataSource — NGOAI Spring TX
- `DataSourceUtils.getConnection(dataSource)` lay connection TU Spring TX hien tai
- Khi dung trong `@Transactional` context: tat ca JPA + raw JDBC cung 1 transaction
- KHONG commit/close manual — Spring quan ly lifecycle

---

## Remaining Backlog

| # | Issue | Effort |
|---|-------|--------|
| 1 | Merge 2 plugin duplicate (SalesAgent + SalesFreehand) thanh abstract base | 2h |
| 2 | Extract business logic tu Booking.java entity ra BookingChargeService | 4h |
| 3 | Refactor PerformanceReportLogic (1090 LOC) thanh nhieu class | 4h |
| 4 | Compensation pattern cho sendBFSOneIBooking (external call risk) | 3h |
| 5 | Constructor injection thay field injection toan bo module | 2h |
| 6 | Hardcoded currency "VND" ra config | 1h |
