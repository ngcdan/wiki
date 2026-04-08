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

### CDC Field Mappings (by target entity)
- [[bf1-fms-mapping-readme|Mapping Index]]
- [[bf1-fms-mapping-transaction|Transaction]]
- [[bf1-fms-mapping-house-bill|House Bill + Rates]]
- [[bf1-fms-mapping-cargo|Cargo (auto-upsert from HAWB CDC)]]
- [[bf1-fms-mapping-container|Container (dual source: parse text + CDC line items)]]
- [[bf1-fms-mapping-transport-plan|Transport Plan (rebuild per event)]]
- [[bf1-fms-mapping-purchase-order|Purchase Order (FMS-only)]]

### DB Schema
- [[bf1-fms-schema-db-schema|BEE_DB Schema Survey]]
- [[bf1-fms-schema-db-schema-cloud|DB Schema Cloud]]

## Kỹ thuật — `dev/`

- [[bf1-dev-query-reference|Query Reference]]
- [[bf1-dev-devlog|Developer Log]]
- [[bf1-dev-mssql-windows-setup|MSSQL Windows Setup]]

## Sandbox — `sandbox/`

Docker-compose + scripts để chạy môi trường thử nghiệm local.

## Liên quan

- [[datatp-datatp-overview|DataTP - Tổng quan dự án]]
- [[datatp-cdc-debezium|CDC với Debezium (DataTP)]]
