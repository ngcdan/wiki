# BF1 -> FMS Field Mapping

Tài liệu mapping giữa BF1 legacy schema và FMS entity schema.
Chỉ mapping cho normalized FMS entities. Integrated entities (IntegratedTransaction, IntegratedHousebill, IntegratedHawbProfit) nằm ngoài scope.

## Pipeline Guide

- [PIPELINE-GUIDE.md](PIPELINE-GUIDE.md) - Hướng dẫn kiến trúc, triển khai, và xử lý sự cố cho CDC & Batch Sync pipelines

## CDC-verified (có CDC handler)

| # | FMS Entity | File | CDC Handler(s) | BF1 Table(s) |
|---|---|---|---|---|
| 1 | `of1_fms_transactions`, `of1_fms_house_bill`, `of1_fms_house_bill_detail_base`, `of1_fms_air_house_bill_detail`, `of1_fms_sea_house_bill_detail`, `of1_fms_truck_house_bill_detail`, `of1_fms_logistics_house_bill_detail` | [mapping-transactions.md](mapping-transactions.md) | `FmsTransactionCDCHandler`, `TransactionDetailsCDCHandler`, `HAWBDetailsCDCHandler` | `Transactions`, `TransactionDetails`, `HAWBDETAILS`, `CustomsDeclaration` |
| 6 | `of1_fms_cargo_container`, `of1_fms_commodity` | [mapping-cargo-container.md](mapping-cargo-container.md) | `ContainerListCDCHandler` | `ContainerListOnHBL`, `HAWBDETAILS`, `Commodity` |
| 7 | `of1_fms_hawb_rates` | [mapping-hawb-rates.md](mapping-hawb-rates.md) | `SellingRateCDCHandler`, `BuyingRateCDCHandler`, `OtherChargeCDCHandler` | `SellingRate`, `BuyingRateWithHBL`, `OtherChargeDetail` |

## FMS-only (không có tương đương BF1)

| # | FMS Entity | File |
|---|---|---|
| 4 | `of1_fms_transport_plan`, `of1_fms_transport_route` | [mapping-transport-plan.md](mapping-transport-plan.md) |
| 5 | `of1_fms_purchase_order`, `of1_fms_booking_process` | [mapping-purchase-order.md](mapping-purchase-order.md) |
