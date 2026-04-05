---
title: "BF1 Folder Reorganization Design"
tags:
  - bf1
  - design
---

# BF1 Folder Reorganization — Design Spec

- **Date:** 2026-03-29
- **Author:** nqcdan
- **Status:** Approved

## Mục tiêu

Tổ chức lại `projects/bf1/` để team có thể cùng làm việc, navigate dễ dàng, và phân tách rõ ràng giữa phân tích hệ thống cũ (BFS One) và thiết kế hệ thống mới (OF1 FMS).

---

## Cấu trúc mới

```
projects/bf1/
  README.md                     ← Index, navigation toàn bộ folder
  project-overview.md           ← Tổng quan dự án (đổi từ BF1.md)
  bfs/                ← Phân tích hệ thống cũ BFS One
  fms/                       ← Thiết kế hệ thống mới OF1 FMS
  dev/                          ← Tài liệu kỹ thuật dùng khi code
  sandbox/                      ← Môi trường thử nghiệm (giữ nguyên)
```

---

## Chi tiết từng thư mục

### `bfs/` — Hệ thống cũ BFS One

Chứa toàn bộ tài liệu phân tích từ hệ thống nguồn để migrate.

```
bfs/
  of1-project-analysis.md       ← (từ references/of1-project-analysis.md)
  erp-analysis.md               ← (từ references/erp-analysis.md)
  overview-report.pdf           ← (từ Overview_Report.pdf)
  references/
    accounting.md
    catalogue.md
    system-documentation.md     ← (đổi từ documentation.md)
    sale-executive.md           ← (đổi từ references/saleExcutive.md, sửa typo)
    images/                     ← giữ nguyên cấu trúc
```

### `fms/` — Hệ thống mới OF1 FMS

Chứa thiết kế kỹ thuật và mô hình nghiệp vụ của hệ thống mới.

```
fms/
  erd.md                        ← (đổi từ ERD.md)
  master-data.md                ← (đổi từ Master_Data.md; bỏ master-data.md trùng lặp)
  cdc-architecture.md           ← (đổi từ CDC_Architecture.md)
  domain-model.drawio           ← (đổi từ DDD.drawio)
  schema/
    db-schema.md                ← (đổi từ BF1_DB_Schema.md)
    db-schema-core.md           ← (đổi từ BF1_DB_Schema_Core.md)
    db-schema-cloud.md          ← (đổi từ Cloud_DB_Schema.md)
  img/
    domain-model.png            ← (đổi từ DDD.png)
    erd.png                     ← (đổi từ ERD.png)
    erd.excalidraw              ← (đổi từ ERD.excalidraw)
    master-data.png
```

### `dev/` — Tài liệu kỹ thuật

Tài liệu dùng trực tiếp khi code: query reference, dev notes.

```
dev/
  query-reference.md            ← (đổi từ Query_Reference.md)
  devlog.md                     ← (đổi từ DEVLOG.md)
```

### `sandbox/` — Môi trường thử nghiệm

Giữ nguyên toàn bộ, không thay đổi.

---

## Xử lý file đặc biệt

| File | Hành động |
|---|---|
| `env.sh` | Thêm vào `.gitignore`, xóa khỏi repo |
| `master-data.md` | Xóa (trùng lặp với `Master_Data.md`) |
| `img/` (root) | Xóa sau khi chuyển nội dung vào `fms/img/` |
| `references/` (root) | Xóa sau khi chuyển nội dung vào `bfs/references/` |
| `ai/` | Đã xóa |
| `superpowers/` | Đã xóa |
| `2026-03-29-bf1-reorganization-design.md` | Xóa sau khi hoàn thành reorganization |

---

## Naming convention

- Toàn bộ **file Markdown và text**: **kebab-case** (lowercase, phân cách bằng dấu `-`)
- Tên mô tả nội dung, không dùng project code (`BF1`, `DDD`, `ERD` viết hoa → lowercase hoặc tên đầy đủ)
- Không dùng underscore trong tên file Markdown
- **Image files** (`references/images/`): giữ nguyên tên hiện tại (đổi tên 400+ ảnh không có giá trị thực tế)

---

## README.md — Index

File `README.md` ở root `bf1/` cần có:
- Mô tả ngắn dự án migrate BFS One → OF1 FMS
- Links đến từng section: legacy, design, dev, sandbox
- Ghi chú tech stack cũ vs mới
- Hướng dẫn "start here" cho người mới vào team

> Scope README có thể mở rộng thêm (owner từng section, trạng thái dự án) khi team bắt đầu sử dụng.
