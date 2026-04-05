---
title: "BF1 - Index"
tags:
  - bf1
  - index
---

# BF1 — Migration BFS One → OF1 FMS

Tài liệu phân tích và thiết kế cho dự án migrate từ hệ thống BFS One (MSSQL) sang OF1 FMS (tech stack mới).

**Bắt đầu từ đây:** [[project-overview|BF1 Upgrade - Tổng quan]]

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

- [[of1-project-analysis|Phân tích tổng thể dự án OF1]]
- `bfs/overview-report.pdf` — Báo cáo tổng quan
- Tài liệu chi tiết theo module:
  - [[accounting|Kế toán (Accounting)]]
  - [[catalogue|Catalogue]]
  - [[system-documentation|Documentations]]
  - [[sale-executive|Sales Executive]]

## Hệ thống mới — `fms/`

- [[entity-relationship-diagram|Entity Relationship Diagram]]
- [[fms-feature-spec|Đặc tả tính năng FMS (ERP Analysis)]]
- [[master-data|Master Data]]
- [[cdc-architecture|Kiến trúc CDC (Change Data Capture)]]
- `fms/domain-model.drawio` — Domain Model (DDD)
- DB Schema:
  - [[db-schema|BEE_DB Schema Survey]]
  - [[db-schema-core|DB Schema Core]]
  - [[db-schema-cloud|DB Schema Cloud]]

## Kỹ thuật — `dev/`

- [[query-reference|Query Reference]]
- [[devlog|Developer Log]]
- [[mssql-windows-setup|MSSQL Windows Setup]]

## Sandbox — `sandbox/`

Docker-compose + scripts để chạy môi trường thử nghiệm local.

## Liên quan

- [[datatp-overview|DataTP - Tổng quan dự án]]
- [[cdc-debezium|CDC với Debezium (DataTP)]]
