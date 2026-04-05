# BF1 Legacy Sync Pipeline

Sync data from BFS One (MSSQL) to FMS (PostgreSQL) via Kafka event pipeline.

## Architecture

```
BF1 MSSQL (BEE_DB) --> SyncLogic (query) --> SyncEvent --> Kafka Producer --> Kafka Consumer --> FMS PostgreSQL
```

- **BF1 Source**: `of1.beelogistics.com:34541` / `BEE_DB` (credentials in TenantRegistry)
- **FMS Target**: `postgres.of1-dev-crm.svc.cluster.local:5432` / `of1_fms_db`
- **Kafka Config**: `addon-fms-config.yaml` -> `datatp.msa.fms.queue.topic.*`

## Sync API

All endpoints via `POST http://localhost:7085/rest/v1.0.0/rpc/internal/call`

```json
{
  "component": "BFSOneSyncService",
  "endpoint": "<endpoint>",
  "userParams": { "sourceDb": "BEE_VN" }
}
```

## Pipeline Summary

| Endpoint | BF1 Table | BF1 Records | FMS Table | FMS Entity | Cron |
|---|---|---|---|---|---|
| `syncBanks` | `lst_Bank` | ~203 | `settings_bank` | `SettingBank` | 30min |
| `syncIndustries` | `lst_Industries` | ~23 | `settings_industry` | `SettingIndustry` | 30min |
| `syncPartnerSources` | `lst_Source` | ~30 | `settings_partner_source` | `SettingPartnerSource` | 30min |
| `syncCommodities` | `Commodity` | ~96 | `settings_commodity` | `SettingCommodity` | 30min |
| `syncNameFeeDescriptions` | `NameFeeDescription` | ~1138 | `settings_name_fee_desc` | `NameFeeDescription` | 30min |
| `syncCustomLists` | `CustomsList` | varies | `settings_custom_list` | `SettingCustomList` | 30min |
| `syncSettingUnits` | `UnitContents` | varies | `settings_unit` | `SettingUnit` | 30min |
| `syncExchangeRates` | `CurrencyExchangeRate` | varies | `settings_exchange_rate` | `ExchangeRate` | 30min |
| `syncUserRoles` | `UserInfos` | ~1095 | `settings_user_roles` | `SettingsUserRole` | 30min |
| `syncTransactions` | `Transactions` | varies | `of1_fms_integrated_transaction` | `IntegratedTransaction` | 30min |
| `syncHousebills` | `TransactionDetails` + joins | varies | `of1_fms_integrated_housebill` | `IntegratedHousebill` | per txn |
| `syncHawbProfits` | `BuyingRateWithHBL`, `SellingRate`, `ProfitShares` | varies | `of1_fms_integrated_hawb_profit` | `IntegratedHawbProfit` | per txn |

## Field Mapping Details

### Bank (`lst_Bank` -> `settings_bank`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `BankCode` | `code` | `code` |
| `BankName` | `label` | `label` |
| `BankGroup` | `short_label` | `shortLabel` |

### Industry (`lst_Industries` -> `settings_industry`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `IDKey` | `code` | `code` |
| `IndustryName` | `label` | `label` |

### Partner Source (`lst_Source` -> `settings_partner_source`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `SourceName` (uppercase) | `code` | `code` |
| `SourceName` | `label` | `label` |

### Commodity (`Commodity` -> `settings_commodity`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `ID` | `code` | `code` |
| `Commodity` / `Commodity_En` | `label` | `label` (prefer English if available) |
| `HSCode` | `hs_code` | `hsCode` |

### Name Fee Description (`NameFeeDescription` -> `settings_name_fee_desc`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `FeeCode` | `code` | `code` |
| `FeeDescEn` | `label` | `label` |
| `FeeDescLocal` | `localized_label` | `localizedLabel` |
| `GroupName` | `charge_group` | `chargeGroup` (resolved: ORIGIN/FREIGHT/DESTINATION/OTHER) |
| `dbt` | `type` | `type` (0=BUYING, else=SELLING) |

### Custom List (`CustomsList` -> `settings_custom_list`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `CustomsCode` | `code` | `code` |
| `ShortName` | `label` | `label` |
| `CustomsBranch` | `name` | `name` |
| `CustomsDept` | `note` | `note` |
| `TeamCode` | `team_code` | `teamCode` |
| `TeamName` | `team_name` | `teamName` |

### Setting Unit (`UnitContents` -> `settings_unit`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `UnitID` | `code` | `code` |
| `Description` | `label` | `label` |
| `LocalUnit` | `localized_description` | `localizedDescription` |
| `ISOCode` | `iso_code` | `isoCode` |

### Exchange Rate (`CurrencyExchangeRate` -> `settings_exchange_rate`)

| BF1 Column | FMS Column | FMS Field |
|---|---|---|
| `ID` | `code` | `code` |
| `ExtVNDSales` | `exchange_rate_usd` | `exchangeRateUSD` |

### User Role (`UserInfos` -> `settings_user_roles`)

| BF1 Column | FMS Column | FMS Field | Note |
|---|---|---|---|
| `Username` | `bfsone_username` | `bfsoneUsername` | uppercase |
| `UserID` | `bfsone_code` | `bfsoneCode` | e.g. CT0002 |
| `FullName` | `full_name` | `fullName` | stripped " - USERNAME" suffix |
| `Position` | `position` | `position` | |
| `DeptID` | `department_name` | `departmentName` | |
| `DepartmentName` | `department_label` | `departmentLabel` | |
| `CmpID` | `company_branch_code` | `companyBranchCode` | |
| `CmpName` | `company_branch_name` | `companyBranchName` | |
| (fixed) | `data_source` | `dataSource` | "BF1" |
| (fixed) | `type` | `type` | OTHER (default) |

## Code Structure

```
module/integration/src/main/java/of1/fms/module/integration/batch/
  groovy/BFSOneSyncSql.groovy          # All BF1 SQL queries
  config/SyncQueueConfig.java          # Kafka bean registration
  BatchSyncService.java                # RPC endpoints orchestrator
  bank/                                # Bank pipeline
  industry/                            # Industry pipeline
  partnersource/                       # Partner Source pipeline
  commodity/                           # Commodity pipeline
  namefeedesc/                         # Name Fee Description pipeline
  customlist/                          # Custom List pipeline
  settingunit/                         # Setting Unit pipeline
  exchangerate/                        # Exchange Rate pipeline
  userrole/                            # User Role pipeline
  transaction/                         # Transaction + Housebill + HAWB Profit pipelines
```

Each pipeline directory contains:
- `*SyncEvent.java` - Data transfer object
- `*SyncLogic.java` - BF1 query + mapping
- `*SyncEventProducer.java` - Kafka producer
- `*SyncEventConsumer.java` - Kafka consumer + save to FMS DB
- `BFSOneSync*CronJob.java` - Scheduled cron job (30min in prod, disabled in dev)
