# BF1 — Migration BFS One → OF1 FMS

Tài liệu phân tích và thiết kế cho dự án migrate từ hệ thống BFS One (MSSQL) sang OF1 FMS (tech stack mới).

**Bắt đầu từ đây:** [`project-overview.md`](project-overview.md)

---

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| [`bfs/`](bfs/) | Phân tích hệ thống cũ BFS One — nghiệp vụ, quy trình, tài liệu tham chiếu |
| [`fms/`](fms/) | Thiết kế hệ thống mới OF1 FMS — ERD, schema, master data, kiến trúc |
| [`dev/`](dev/) | Tài liệu kỹ thuật dùng khi code — query reference, dev log |
| [`sandbox/`](sandbox/) | Môi trường thử nghiệm local — docker-compose, scripts |

---

## Hệ thống cũ — `bfs/`

- [`bfs/of1-project-analysis.md`](bfs/of1-project-analysis.md) — Phân tích tổng thể dự án OF1
- [`bfs/erp-analysis.md`](bfs/erp-analysis.md) — Phân tích ERP
- [`bfs/overview-report.pdf`](bfs/overview-report.pdf) — Báo cáo tổng quan
- [`bfs/references/`](bfs/references/) — Tài liệu chi tiết theo module: accounting, catalogue, documentation, sale-executive

## Hệ thống mới — `fms/`

- [`fms/erd.md`](fms/erd.md) — Entity Relationship Diagram
- [`fms/master-data.md`](fms/master-data.md) — Master Data
- [`fms/cdc-architecture.md`](fms/cdc-architecture.md) — Kiến trúc CDC (Change Data Capture)
- [`fms/domain-model.drawio`](fms/domain-model.drawio) — Domain Model (DDD)
- [`fms/schema/`](fms/schema/) — DB Schema: db-schema, db-schema-core, db-schema-cloud

## Kỹ thuật — `dev/`

- [`dev/query-reference.md`](dev/query-reference.md) — Query reference
- [`dev/devlog.md`](dev/devlog.md) — Dev log, sandbox setup notes

## Sandbox — `sandbox/`

Docker-compose + scripts để chạy môi trường thử nghiệm local.
Xem [`sandbox/`](sandbox/) để biết cách khởi động.
