# Tenant Registry — Database Migration Design

**Date:** 2026-05-04
**Status:** Approved
**Module:** of1-fms / core

---

## Problem

`TenantRegistry.java` hardcodes all tenant mappings, data source URLs, and credentials. Any change (new tenant, URL switch, test/prod toggle) requires code change + redeploy.

## Goals

- **A**: Add/modify tenants and DB URLs without redeploying
- **C**: Switch DB connections at runtime (e.g., HPS test ↔ prod)

## Design

### Database Schema

#### `tenant_source`

| Column | Type | Constraint |
|--------|------|------------|
| id | BIGSERIAL | PK |
| code | VARCHAR(32) | UNIQUE NOT NULL |
| label | VARCHAR(128) | |
| db_url | VARCHAR(512) | NOT NULL |
| db_username | VARCHAR(128) | |
| db_password | VARCHAR(256) | |

#### `tenant_company`

| Column | Type | Constraint |
|--------|------|------------|
| id | BIGSERIAL | PK |
| code | VARCHAR(32) | UNIQUE NOT NULL |
| label | VARCHAR(128) | |
| work_branch_codes | VARCHAR(512) | |
| source_id | BIGINT | FK → tenant_source.id |
| tenant_group | VARCHAR(32) | |

- `work_branch_codes`: comma-separated (e.g., `"BEEAMD,BEEBLR,BEEBOM"` for `bee-in`)
- `tenant_group`: `BEE_VN`, `BEE_INDIA`, or null — replaces `isBeeVNCompany()` / `isBeeIndiaCompany()` logic

### Service Layer

- `TenantRegistryService` replaces static `TenantRegistry`
- Cache strategy: startup load + TTL 30 min auto-refresh
- Method signatures preserved: `getDatabaseSource()`, `getDbUrl()`, `toInternalCompanyCode()`
- Remove unused methods: `isBeeVNCompany()`, `isThuDoCompany()`, `isBeeIndiaCompany()`

### Migration

- Liquibase changeset `fms:62` appended to `002-schema-updates.sql`
- CREATE tables + INSERT all current hardcoded data as seed
- Delete `TenantRegistry.java` after migration complete

### Callers to Update (6 files)

1. `InternalCallGateway.java` — `getDatabaseSource()`
2. `CDCLookupSupport.java` — `getDatabaseSource()`
3. `UserInfoLogic.java` — `getDatabaseSource()` x2
4. `UserSyncLogic.java` — `toInternalCompanyCode()` x2
5. `FMSDaoService.java` — `getDbUrl()`

### Seed Data

Sources (20): BEE_VN, BEE_INDIA, BEESCS, TDLVN, BEE_PAC, BEE_VN_DIS, BEE_TRAN, BEE_VN_PROJ, BONDS, MARINE, HPS, PROS_JSC, TIENDAT, BEE_ID, BEE_KH, BEE_MM, BEE_CN_CNC, BEE_MY, BEE_LA, BEE_US_OCL

Companies (22): bee, beehan, beehph, beedad, beehcm (group=BEE_VN), bee-in (group=BEE_INDIA), beescs, thudo, bee-pac, bee-vn-dis, beetran, bee-vn-proj, bonds, marine, hps, pros-jsc, tiendat, bee-id, bee-kh, bee-mm, bee-cn-cnc, bee-my, bee-la, bee-us-ocl

### No API Endpoints

Admin operations done via direct DB access for now.
