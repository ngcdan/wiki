# Mapping: Container & Commodity

> BF1 -> FMS field mapping cho nhóm Container & Commodity

---

## of1_fms_cargo_container

> CDC Handler: `ContainerListCDCHandler`
> Coverage: CDC-verified

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | | FK → of1_fms_house_bill.id | | | |
| `container_no` | varchar | | Số container | `ContainerListOnHBL` | `ContainerNo` | |
| `container_type` | varchar | | Loại container | `ContainerListOnHBL` | `ContainerType` | |
| `seal_no` | varchar | | Số chì seal | `ContainerListOnHBL` | `SealNo` | |
| `quantity` | double | | Số lượng | `ContainerListOnHBL` | `Qty` | |
| `gross_weight_in_kg` | double | | Trọng lượng (kg) | `ContainerListOnHBL` | `GW` | |
| `volume_in_cbm` | double | | Thể tích (CBM) | `ContainerListOnHBL` | `CBM` | |
| `packaging_type` | varchar | | Loại bao bì | | | |

---

## of1_fms_commodity

> CDC Handler: Chưa có
> Coverage: Schema match — chưa CDC-verified

| FMS Column | Type | Bắt buộc | Mô tả | BF1 Table | BF1 Column | BF1 UI Label |
|---|---|---|---|---|---|---|
| `id` | bigserial | | PK | | | |
| `house_bill_id` | bigint | | FK → of1_fms_house_bill.id | | | |
| `container_id` | bigint | | FK → of1_fms_cargo_container.id | | | |
| `commodity_code` | varchar | | Mã hàng hóa | `Commodity` | `CommodityCode` | |
| `commodity_desc` | varchar | | Mô tả hàng hóa | `Commodity` | `Description` | |
| `desc_of_goods` | varchar | | Mô tả chi tiết hàng hóa | `HAWBDETAILS` | `Description` | |
| `hs_code` | varchar | | Mã HS code | | | |
| `quantity` | double | | Số lượng | `HAWBDETAILS` | `Quantity` | |
| `gross_weight_in_kg` | double | | Trọng lượng (kg) | `HAWBDETAILS` | `Weight` | |
| `volume_in_cbm` | double | | Thể tích (CBM) | `HAWBDETAILS` | `Volume` | |
| `packaging_type` | varchar | | Loại bao bì | | | |
| `package_quantity` | int | | Số kiện | | | |
