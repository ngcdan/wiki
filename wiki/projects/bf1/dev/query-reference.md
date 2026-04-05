---
title: "Query Reference"
tags:
  - bf1
  - dev
  - mssql
  - query
---


# DEVLOG.md

## MSSQL Queries từ bee_legacy/

---

### 1. Exchange Rate — CurrencyExchangeRate

**File:** `bee_legacy/service/exchange_rate_service.py` (dòng 111–117)
**Method:** `ExchangeRateService.sync_bfsone_exchange_rate()`
**DB:** MSSQL (BFS One)
**Params:** None (filter cứng)

```sql
SELECT
  ex.ID             AS code,
  ex.ExtVNDSales    AS exchange_rate_usd
FROM CurrencyExchangeRate ex
WHERE ex.Unit = 'USD'
  AND (ex.ID like 'HCMGIANGNTH_%'
  AND (ex.ID like '%2025%' OR ex.ID like '%2024%' OR ex.ID like '%2023%' OR ex.ID like '%2022%'))
```

**Result columns:**
| Column | Source | Mô tả |
|--------|--------|-------|
| `code` | `ex.ID` | Mã tỷ giá (e.g. `HCMGIANGNTH_2024`) |
| `exchange_rate_usd` | `ex.ExtVNDSales` | Tỷ giá bán USD → VND |

**Ghi chú:** Filter theo pattern `HCMGIANGNTH_` và năm 2022–2025. Nếu mở rộng sang năm khác hoặc chi nhánh khác cần sửa WHERE.

---

### 2. Settings Unit — UnitContents

**File:** `bee_legacy/service/settings_unit_service.py` (dòng 101–109)
**Method:** `SettingsUnitService.sync_bfsone_units()`
**DB:** MSSQL (BFS One)
**Params:** None

```sql
SELECT
    u.UnitID        AS unit_code,
    u.UnitID        AS unit_name,
    u.LocalUnit     AS unit_localized_name,
    u.ISOCode       AS alias,
    u.Description   AS description
FROM UnitContents u
```

**Result columns:**
| Column | Source | Mô tả |
|--------|--------|-------|
| `unit_code` | `u.UnitID` | Mã đơn vị |
| `unit_name` | `u.UnitID` | Tên đơn vị (dùng lại UnitID) |
| `unit_localized_name` | `u.LocalUnit` | Tên tiếng Việt |
| `alias` | `u.ISOCode` | Mã ISO |
| `description` | `u.Description` | Mô tả |

---

### 3. Transaction — Min/Max/Count (dùng cho chunking)

**File:** `bee_legacy/service/hawb/integrated_transaction_service.py` (dòng 174–184)
**Method:** `TransactionService._get_transaction_id_chunks()`
**DB:** MSSQL (BFS One)
**Params:** `from_date` (optional), `to_date` (optional) → áp lên `COALESCE(t.LoadingDate, t.ArrivalDate, t.TransDate)`

```sql
SELECT MIN(t.TransID), MAX(t.TransID), COUNT(*)
FROM Transactions t
JOIN UserInfos ui ON ui.Username = t.WhoisMaking
LEFT JOIN Airports fr ON fr.AirPortName = t.PortofLading
LEFT JOIN Airports toLoc ON toLoc.AirPortName = t.PortofUnlading
WHERE 1=1
-- + điều kiện date range nếu có
```

**Result columns:**
| Column | Mô tả |
|--------|-------|
| `MIN(t.TransID)` | TransID nhỏ nhất trong range |
| `MAX(t.TransID)` | TransID lớn nhất trong range |
| `COUNT(*)` | Tổng số records |

**Ghi chú:** Dùng để tính số chunk cần xử lý. Chunk size = 5000, batch size = 50.

---

### 4. Transaction — Main Data (phân trang OFFSET/FETCH)

**File:** `bee_legacy/service/hawb/integrated_transaction_service.py` (dòng 228–272)
**Method:** `TransactionService._process_chunk()`
**DB:** MSSQL (BFS One)
**Params:** `:offset`, `:fetch_size`, `from_date` (optional), `to_date` (optional)

```sql
SELECT
    t.TransID           AS transaction_id,
    t.TransDate         AS transaction_date,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate
        ELSE t.LoadingDate
    END                 AS etd,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate
        ELSE t.ArrivalDate
    END                 AS eta,
    t.TpyeofService     AS type_of_service,
    t.ContainerSize     AS container_size,
    t.PortofLading      AS from_location_label,
    fr.AirPortID        AS from_location_code,
    t.PortofUnlading    AS to_location_label,
    toLoc.AirPortID     AS to_location_code,
    t.WhoisMaking       AS creator_username,
    ui.FullName         AS creator_name
FROM Transactions t
JOIN UserInfos ui ON ui.Username = t.WhoisMaking
LEFT JOIN Airports fr ON fr.AirPortName = t.PortofLading
LEFT JOIN Airports toLoc ON toLoc.AirPortName = t.PortofUnlading
WHERE 1=1
-- + điều kiện date range nếu có
ORDER BY t.TransID
OFFSET :offset ROWS FETCH NEXT :fetch_size ROWS ONLY
```

**Result columns:**
| Column | Source | Mô tả |
|--------|--------|-------|
| `transaction_id` | `t.TransID` | Mã giao dịch |
| `transaction_date` | `t.TransDate` | Ngày tạo giao dịch |
| `etd` | ArrivalDate (Import) / LoadingDate (Export) | Ngày dự kiến khởi hành |
| `eta` | LoadingDate (Import) / ArrivalDate (Export) | Ngày dự kiến đến |
| `type_of_service` | `t.TpyeofService` | Loại dịch vụ (typo trong DB: "Tpye") |
| `container_size` | `t.ContainerSize` | Kích thước container |
| `from_location_label` | `t.PortofLading` | Tên cảng đi |
| `from_location_code` | `fr.AirPortID` | Mã cảng đi |
| `to_location_label` | `t.PortofUnlading` | Tên cảng đến |
| `to_location_code` | `toLoc.AirPortID` | Mã cảng đến |
| `creator_username` | `t.WhoisMaking` | Username người tạo |
| `creator_name` | `ui.FullName` | Tên đầy đủ người tạo |

**Ghi chú:**
- Cột `TpyeofService` là typo trong BFS One (sic), không sửa được.
- ETD/ETA swap giữa Import và Export là logic nghiệp vụ — Import: ArrivalDate = ETD (ngày đến dự kiến).

---

### 5. Transaction — Fetch by IDs (IN clause)

**File:** `bee_legacy/service/hawb/integrated_transaction_service.py` (dòng 523–548)
**Method:** `TransactionService.sync_by_transaction_ids()`
**DB:** MSSQL (BFS One)
**Params:** Danh sách transaction IDs → chuyển thành `:trans_id_0, :trans_id_1, ...`

```sql
SELECT
    t.TransID           AS transaction_id,
    t.TransDate         AS transaction_date,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate
        ELSE t.LoadingDate
    END                 AS etd,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate
        ELSE t.ArrivalDate
    END                 AS eta,
    t.TpyeofService     AS type_of_service,
    t.ContainerSize     AS container_size,
    t.PortofLading      AS from_location_label,
    fr.AirPortID        AS from_location_code,
    t.PortofUnlading    AS to_location_label,
    toLoc.AirPortID     AS to_location_code,
    t.WhoisMaking       AS creator_username,
    ui.FullName         AS creator_name
FROM Transactions t
JOIN UserInfos ui ON ui.Username = t.WhoisMaking
LEFT JOIN Airports fr ON fr.AirPortName = t.PortofLading
LEFT JOIN Airports toLoc ON toLoc.AirPortName = t.PortofUnlading
WHERE t.TransID IN (:trans_id_0, :trans_id_1, ...)
```

**Ghi chú:** Cùng structure với query #4 nhưng không phân trang — dùng cho sync theo danh sách ID cụ thể.

---

### 6. House Bill — BFS One Detail Query

**File:** `bee_legacy/service/hawb/integrated_housebill_service.py` (dòng 135–175)
**Method:** `HouseBillService.sync_bfsone_house_info()`
**DB:** MSSQL (BFS One)
**Params:** `:transaction_id`

```sql
SELECT
    t.TransID           AS transaction_id,
    t.TransDate         AS transaction_date,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.ArrivalDate
        ELSE t.LoadingDate
    END                 AS etd,
    CASE
        WHEN t.TpyeofService LIKE '%Imp%' THEN t.LoadingDate
        ELSE t.ArrivalDate
    END                 AS eta,
    t.TpyeofService     AS type_of_service,
    td.HWBNO            AS hawb_no,
    t.ContainerSize     AS container_size,
    h.TotalPackages     AS total_packages,
    h2.GrossWeight      AS hawb_gw,
    h2.WChargeable      AS hawb_cw,
    h2.CBM              AS hawb_cbm,
    td.ShipperID        AS customer_code,
    p.PartnerName       AS customer_name,
    COALESCE(
        NULLIF(t.AgentID, ''),
        NULLIF(h.HBAgentID, '')
    )                   AS agent_code,
    agent.PartnerName   AS agent_name,
    td.ContactID        AS saleman_contact_id,
    td.ShipmentType     AS shipment_type,
    cs.TKSo             AS customs_no_summary
FROM Transactions t
INNER JOIN TransactionDetails td ON td.TransID = t.TransID
INNER JOIN Partners p ON td.ShipperID = p.PartnerID
INNER JOIN HAWB h ON h.HWBNO = td.HWBNO
LEFT JOIN HAWBDETAILS h2 ON h.HWBNO = h2.HWBNO
LEFT JOIN Partners agent ON COALESCE(
    NULLIF(t.AgentID, ''),
    NULLIF(h.HBAgentID, '')
) = agent.PartnerID
LEFT JOIN CustomsDeclaration cs ON cs.MasoTK = td.CustomsID
WHERE t.TransID = :transaction_id
```

**Result columns:**
| Column | Source | Mô tả |
|--------|--------|-------|
| `transaction_id` | `t.TransID` | Mã giao dịch |
| `transaction_date` | `t.TransDate` | Ngày giao dịch |
| `etd` / `eta` | CASE logic | (giống query #4) |
| `hawb_no` | `td.HWBNO` | Số House Waybill |
| `container_size` | `t.ContainerSize` | Kích thước container |
| `total_packages` | `h.TotalPackages` | Số kiện hàng |
| `hawb_gw` | `h2.GrossWeight` | Trọng lượng thô (kg) |
| `hawb_cw` | `h2.WChargeable` | Trọng lượng tính cước |
| `hawb_cbm` | `h2.CBM` | Thể tích (m³) |
| `customer_code` | `td.ShipperID` | Mã khách hàng |
| `customer_name` | `p.PartnerName` | Tên khách hàng |
| `agent_code` | COALESCE(t.AgentID, h.HBAgentID) | Mã đại lý (ưu tiên transaction level) |
| `agent_name` | `agent.PartnerName` | Tên đại lý |
| `saleman_contact_id` | `td.ContactID` | ID nhân viên kinh doanh |
| `shipment_type` | `td.ShipmentType` | Loại lô hàng |
| `customs_no_summary` | `cs.TKSo` | Số tờ khai hải quan |

**Ghi chú:**
- Agent được lấy từ `t.AgentID` trước, fallback sang `h.HBAgentID` nếu rỗng.
- `h2.HWBNO` từ HAWBDETAILS — LEFT JOIN nên có thể NULL nếu chưa có chi tiết.

---

### 7. HAWB Profit — CTE Aggregation Query

**File:** `bee_legacy/service/hawb/integrated_hawb_profit_service.py` (dòng 79–132)
**Method:** `HawbProfitService._query_profit_data()`
**DB:** MSSQL (BFS One)
**Params:** Danh sách HAWB numbers → insert vào VALUES clause

```sql
WITH HawbList AS (
    SELECT hawb_no FROM (VALUES ('HWB001'), ('HWB002'), ...) AS t(hawb_no)
),
BuyData AS (
    SELECT
        HAWBNO AS hawb_no,
        SUM(COALESCE(Quantity * UnitPrice * ExtVND, 0)) AS subtotal_buy,
        SUM(COALESCE(TotalValue * ExtVND, 0))           AS total_buy
    FROM BuyingRateWithHBL
    GROUP BY HAWBNO
),
SellData AS (
    SELECT
        HAWBNO AS hawb_no,
        SUM(COALESCE(Quantity * UnitPrice * ExtVND, 0)) AS subtotal_sell,
        SUM(COALESCE(TotalValue * ExtVND, 0))           AS total_sell
    FROM SellingRate
    GROUP BY HAWBNO
),
DebitData AS (
    SELECT
        HAWBNO AS hawb_no,
        SUM(COALESCE(Quantity * UnitPrice * ExtVND, 0)) AS subtotal_debit,
        SUM(COALESCE(TotalValue * ExtVND, 0))           AS total_debit
    FROM ProfitShares
    WHERE Obh != 1 AND SortDes LIKE 'S%'
    GROUP BY HAWBNO
),
CreditData AS (
    SELECT
        HAWBNO AS hawb_no,
        SUM(COALESCE(Quantity * UnitPrice * ExtVND, 0)) AS subtotal_credit,
        SUM(COALESCE(TotalValue * ExtVND, 0))           AS total_credit
    FROM ProfitShares
    WHERE Obh != 1 AND SortDes LIKE 'B%'
    GROUP BY HAWBNO
)
SELECT
    hl.hawb_no,
    COALESCE(b.subtotal_buy, 0)    AS subtotal_buy,
    COALESCE(b.total_buy, 0)       AS total_buy,
    COALESCE(c.subtotal_credit, 0) AS subtotal_credit,
    COALESCE(c.total_credit, 0)    AS total_credit,
    COALESCE(s.subtotal_sell, 0)   AS subtotal_sell,
    COALESCE(s.total_sell, 0)      AS total_sell,
    COALESCE(d.subtotal_debit, 0)  AS subtotal_debit,
    COALESCE(d.total_debit, 0)     AS total_debit
FROM HawbList hl
LEFT JOIN BuyData b ON hl.hawb_no = b.hawb_no
LEFT JOIN SellData s ON hl.hawb_no = s.hawb_no
LEFT JOIN DebitData d ON hl.hawb_no = d.hawb_no
LEFT JOIN CreditData c ON hl.hawb_no = c.hawb_no
```

**Result columns:**
| Column | Source table | Mô tả |
|--------|-------------|-------|
| `hawb_no` | HawbList | Số House Waybill |
| `subtotal_buy` | BuyingRateWithHBL | Subtotal mua (Qty × UnitPrice × ExtVND) |
| `total_buy` | BuyingRateWithHBL | Total mua (TotalValue × ExtVND) |
| `subtotal_sell` | SellingRate | Subtotal bán |
| `total_sell` | SellingRate | Total bán |
| `subtotal_debit` | ProfitShares (SortDes LIKE 'S%') | Subtotal debit |
| `total_debit` | ProfitShares (SortDes LIKE 'S%') | Total debit |
| `subtotal_credit` | ProfitShares (SortDes LIKE 'B%') | Subtotal credit |
| `total_credit` | ProfitShares (SortDes LIKE 'B%') | Total credit |

**Ghi chú:**
- `ExtVND` là tỷ giá quy đổi sang VND được nhúng trong từng bảng.
- `ProfitShares` lọc `Obh != 1` (loại bỏ OBH entries) và phân chia Debit/Credit theo `SortDes` prefix:
  - `SortDes LIKE 'S%'` → Sell side (Debit)
  - `SortDes LIKE 'B%'` → Buy side (Credit)
- HAWB values được inject trực tiếp vào VALUES clause (không dùng bind params) — cần chú ý sanitize nếu mở rộng input source.

---

### 8. House Bill Info — PostgreSQL (integrated tables)

**File:** `bee_legacy/service/hawb/integrated_housebill_service.py` (dòng 81–91)
**Method:** `HouseBillService.getHawbInfoByTransactionIds()`
**DB:** PostgreSQL (DataTP)
**Params:** Danh sách transaction_ids (dạng string `'id1','id2',...`)

```sql
SELECT
    h.transaction_id,
    h.hawb_no,
    h.customer_name,
    it.creator_name
FROM integrated_housebill h
JOIN integrated_transaction it ON it.transaction_id = h.transaction_id
WHERE h.transaction_id IN ('1001', '1002', ...)
ORDER BY h.transaction_id, h.hawb_no
```

**Result columns:**
| Column | Mô tả |
|--------|-------|
| `transaction_id` | Mã giao dịch |
| `hawb_no` | Số HAWB |
| `customer_name` | Tên khách hàng |
| `creator_name` | Tên nhân viên tạo giao dịch |

---

## Bảng MSSQL liên quan

| Bảng BFS One | Dùng trong query | Mô tả |
|-------------|-----------------|-------|
| `Transactions` | #3, #4, #5, #6 | Giao dịch chính |
| `TransactionDetails` | #6 | Chi tiết giao dịch (HAWB, ShipperID, ...) |
| `UserInfos` | #3, #4, #5, #6 | Thông tin người dùng |
| `Airports` | #3, #4, #5, #6 | Danh mục sân bay/cảng |
| `HAWB` | #6 | Thông tin House Waybill |
| `HAWBDETAILS` | #6 | Chi tiết HAWB (trọng lượng, CBM) |
| `Partners` | #6 | Danh mục đối tác (khách hàng, đại lý) |
| `CustomsDeclaration` | #6 | Tờ khai hải quan |
| `BuyingRateWithHBL` | #7 | Bảng giá mua |
| `SellingRate` | #7 | Bảng giá bán |
| `ProfitShares` | #7 | Phân chia lợi nhuận |
| `CurrencyExchangeRate` | #1 | Tỷ giá hối đoái |
| `UnitContents` | #2 | Đơn vị đo lường |



