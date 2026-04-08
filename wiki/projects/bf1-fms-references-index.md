---
title: "FMS References Index"
tags: [bf1, fms, index]
---

# References

Index of reference documents for the OF1 Freight Management System.

---

## BFS — Business Functional Specs

Original business requirements and functional specifications from the legacy BF1 system.

| File | Description |
|------|-------------|
| [feature-spec.md](bfs/feature-spec.md) | OF1 FMS — Project analysis and full feature specification |
| [catalogue.md](bfs/catalogue.md) | Catalogue module — Master data screens and flows |
| [saleExcutive.md](bfs/saleExcutive.md) | Sales Executive module — Quotation, booking, pricing |
| [documentation.md](bfs/documentation.md) | Documentations module — Chứng từ, vận đơn, rates |
| [accounting.md](bfs/accounting.md) | Accounting module — Invoice, công nợ, tạm ứng |

---

## FMS — Core Documentation (reading order)

| # | File | Description |
|---|------|-------------|
| 1 | [[bf1-fms-01-overview]] | Project goals, business modules, implementation phases |
| 2 | [[bf1-fms-02-features]] | Business processes, core features, entity relationships |
| 3 | [[bf1-fms-03-data-model]] | Entities, enums, master data, legacy BF1 schema |
| 4 | [[bf1-fms-04-integration]] | CDC + Batch Sync pipeline architecture |

---

## FMS — CDC Field Mappings (by target entity)

| Target | File | Notes |
|--------|------|-------|
| Index | [[bf1-fms-mapping-readme]] | Mapping coverage legend and overview |
| Transaction | [[bf1-fms-mapping-transaction]] | Master bill + ContainerSize parse + TransportPlan rebuild |
| House Bill + Rates | [[bf1-fms-mapping-house-bill]] | Skeleton + details + selling/buying/OBH rates |
| Cargo | [[bf1-fms-mapping-cargo]] | Auto-upsert from HAWB CDC |
| Container | [[bf1-fms-mapping-container]] | Dual source: parsed text + CDC line items |
| Transport Plan | [[bf1-fms-mapping-transport-plan]] | Delete + recreate per Transaction event |
| Purchase Order | [[bf1-fms-mapping-purchase-order]] | FMS-only (no CDC) |

---

## FMS — DB Schema

| File | Description |
|------|-------------|
| [[bf1-fms-schema-db-schema]] | BEE_DB Schema Survey |
| [[bf1-fms-schema-db-schema-cloud]] | DB Schema Cloud |
