---
title: "BF1 - Index"
tags:
  - bf1
  - index
---

# BF1 — Migration BFS One → OF1 FMS

Tài liệu phân tích và thiết kế cho dự án migrate từ hệ thống BFS One (MSSQL) sang OF1 FMS (tech stack mới).

**Bắt đầu từ đây:** [[bf1-fms-01-overview|FMS 01 - Overview]]

---

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `bfs/` | Phân tích hệ thống cũ BFS One — nghiệp vụ, quy trình, tài liệu tham chiếu |
| `fms/` | Thiết kế hệ thống mới OF1 FMS — ERD, schema, master data, kiến trúc |
| `dev/` | Tài liệu kỹ thuật dùng khi code — query reference, dev log |
| `sandbox/` | Môi trường thử nghiệm local — docker-compose, scripts |

---

## Hệ thống cũ — `bfs/`

- [[bf1-bfs-of1-project-analysis|Phân tích tổng thể dự án OF1]]
- `bfs/overview-report.pdf` — Báo cáo tổng quan
- Tài liệu chi tiết theo module:
  - [[bf1-bfs-references-accounting|Kế toán (Accounting)]]
  - [[bf1-bfs-references-catalogue|Catalogue]]
  - [[bf1-bfs-references-system-documentation|Documentations]]
  - [[bf1-bfs-references-sale-executive|Sales Executive]]

## Hệ thống mới — fms/

### Core Documentation (reading order)
1. [[bf1-fms-01-overview|01 - Overview — Goals, modules, phases]]
2. [[bf1-fms-02-features|02 - Features — Business processes, core features]]
3. [[bf1-fms-03-data-model|03 - Data Model — Entities, enums, schema, legacy tables]]
4. [[bf1-fms-04-integration|04 - Integration — CDC + Batch Sync pipeline]]

### CDC Field Mappings

→ [[bf1-fms-mapping|Mapping Index — Source MSSQL → FMS PostgreSQL]]

### DB Schema
- [[bf1-fms-03-data-model#9-bee_db-schema-survey|BEE_DB Schema Survey]]
- [[bf1-fms-03-data-model#10-db-schema-cloud|DB Schema Cloud]]

## Kỹ thuật — `dev/`

- [[bf1-dev-query-reference|Query Reference]]
- [[bf1-dev-devlog|Developer Log]]
- [[bf1-dev-mssql-windows-setup|MSSQL Windows Setup]]
- [[bf1-fms-api-api-bfs-storage|API BFS Storage]]
- [[bf1-reorganization-design|Reorganization Design]]

## eGov — Khai quan

→ [[egov-index|eGov — Customs Clearance]]

Hệ thống khai quan hải quan, tích hợp eCUS + đấu nối dữ liệu BFS One.
- [[egov-devlog|Developer Log]]
- [[egov-declaration-entity-design|Declaration Entity Design]]
- [[egov-ecus-batch-sync|eCUS Batch Sync]]

## AI Rules — Quy tắc cho AI assistants

→ [[bf1-ai-index|BF1 AI — Rules & Guides Index]]

## Liên quan

- [[datatp-index|DataTP - Tổng quan]]
- [[datatp-cdc-debezium|CDC với Debezium (DataTP)]]
- [[of1-identity|OF1 Identity Service]]
- [[namespace-ip-cloud|Namespace & IP Cloud]]
