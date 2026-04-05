---
title: Notion Sync Index
synced: 2026-04-05
source: Notion workspace (1 workspace, no teamspaces)
---

# Notion Sync Index

> Synced: 2026-04-05
> Source: Notion workspace (1 workspace, no teamspaces)

## 💼 Công việc (`01_cong_viec/`)

- [TODO - Bugs](01_cong_viec/TODO_Bugs.md) — Task assignments cho team (Nhật, An, Đức)
- [TODO - Request](01_cong_viec/TODO_REQUEST.md) — Purchase Order model proposal (PO/POP)
- [Has to be discuss](01_cong_viec/Has_to_be_discuss.md) — Logistics operations, Round-Used concept
- [Report Team BD Sale/IST](01_cong_viec/Report_Team_BD_Sale_IST.md) — BD Sales/IST quotation reporting
- [OF1 Dan Report](01_cong_viec/OF1_Dan_Report.md) — 4 project updates: CRM, S3, BF1 Web, Mobile
- [Talk with OF1 Team](01_cong_viec/Talk_with_OF1_Team.md) — Team discussions: S3, Multi-Tier sync, CDC
- [OF1 Strategy](01_cong_viec/OF1_Strategy.md) — 5 strategic proposals + Kickoff 2026 analysis
- [OKRs](01_cong_viec/OKRs.md) — OKR system design: hierarchy, workflow, CFR
- [CRM](01_cong_viec/CRM.md) — CRM dev docs: demo, pricing, quotation workflow
- [Daily Report](01_cong_viec/Daily_Report.md) — Daily report template
- [Review Meeting / Booking Car](01_cong_viec/Review_Meeting_Booking_Car.md) — Placeholder (empty page)

## ⚙️ Kỹ thuật (`02_ky_thuat/`)

- [Server / Config / Release](02_ky_thuat/Server_Config_Release.md) — Server configs, k8s, DB URLs, Grafana, Tailscale
- [Kafka](02_ky_thuat/Kafka.md) — Kafka tutorial: concepts, consumer groups, CDC pipeline
- [Keycloak Development](02_ky_thuat/Keycloak_Development.md) — SSO: dual auth, token management, API CRUD
- [Ideas](02_ky_thuat/Ideas.md) — Personal finance system, automation, English learning
- [Ideas (2)](02_ky_thuat/Ideas_2.md) — Project tracking week 43, CRM/Mobile/Egov summaries
- [Technical Note](02_ky_thuat/Technical_Note.md) — Placeholder (bookmarks only)
- [Technical Database](02_ky_thuat/Technical_Database.md) — Docker SQL Server, PostgreSQL setup, backup/restore
- [References](02_ky_thuat/References.md) — Placeholder (image reference only)

## 🌱 Cá nhân (`03_ca_nhan/`)

- [English](03_ca_nhan/English.md) — Luyện viết tiếng Anh A2–B1, AI prompts, weather vocab, IELTS speaking
- [Interview](03_ca_nhan/Interview.md) — Đánh giá ứng viên phỏng vấn (Duy, Đạt, An)

## 📊 Data TP — Project Hub (`05_data_tp/`)

> Notion Page ID: `e321c961d37a424fa0f5148f4ebea3a5`
> Chứa 2 inline databases dạng Board/Kanban

### Data TP Database (Board View)
- **Collection ID:** `collection://8849b5d8-23ec-4c30-a9ba-6387ed081724`
- **Schema:** Name (title), Assign (person), Language (select), Project start date (date), Status (select: Interview/Meeting/Discuss, Business Domain, Planning/TODO, Technical)

**Child pages:**
- [BF1 Web Upgrade](05_data_tp/BF1_Web_Upgrade.md) — BF1 project setup, SPM reports, CDC architecture, cost estimates
- [Reports](05_data_tp/Reports.md) — OF1 Cloud phases, SSO/Keycloak, CRM roadmap
- [CDC Debezium](05_data_tp/CDC_Debezium.md) — MSSQL CDC setup, Kafka Connect pipeline, PostgreSQL CDC
- [Issue Data Sync Conflict](05_data_tp/Issue_Data_Sync_Conflict.md) — Partner data conflict resolution, PartnerReference, SQL migration
- [Mobile](05_data_tp/Mobile.md) — Flutter build commands, iOS/Android setup, App Store listing
- [HPS Odoo](05_data_tp/HPS_Odoo.md) — Odoo ERP accounting, invoice management, reconciliation
- [Odoo ERP](05_data_tp/Odoo_ERP.md) — Odoo dev setup, k8s deployment, Docker concepts
- [Mail Outlook](05_data_tp/Mail_Outlook.md) — Exchange Online PowerShell, CRM Teams meeting integration

### ☑️ Tasks Database (Board View)
- **Collection ID:** `collection://2c3f924d-5d7b-8188-8865-000b6149e9e1`
- **Schema:** Name (title), Assign (person), Request By (text), Start date (date), Status (select: Backlog 1-2 Week, Doing Current Week, Planning/TODO, Done, Review 2-3 days, Report/Feedback)

**Child pages:**
- [Bugs / Enhance](05_data_tp/Bugs_Enhance.md) — CRM identity sync, role template sync, forgot password
- [IT BD Supports](05_data_tp/IT_BD_Supports.md) — Task Calendar BD, AMN user type, agency agreement
- [Performance Report KA](05_data_tp/Performance_Report_KA.md) — Key Account report customization
- [Nhật Week 1](05_data_tp/Nhat_Week1.md) — Enhance/Fix Bugs tuần 1: filter data, partner name normalize, app features, role review
- [Nhật Week 2](05_data_tp/Nhat_Week2.md) — Enhance/Maintenance tuần 2: Lead/Agent UI, report permissions, HPH asset, CDC pipeline

## 🗄️ Databases (Home page)

### Workspace Database
- **ID:** dd3e8111ea73456487a77f8b351f7395
- **Schema:** Name (title), Danh mục (select: Công việc/Kỹ thuật/Cá nhân/Inbox), Link (url), Mô tả (text)
- **Ghi chú:** Database dạng gallery view trên trang Home, dùng để điều hướng workspace. Không chứa dữ liệu độc lập.

### 📋 Home Database
- **ID:** 8723ca60e10f4e41a84fa36f43065919
- **Schema:** Tên trang (title), Danh mục (select), Link (url), Mô tả (text)
- **Ghi chú:** Database dạng gallery view, tương tự Workspace database. Không chứa dữ liệu độc lập.

### 📝 My Tasks Database
- **ID:** 5fdea32c311841ad9b5aac9201496bae
- **Ghi chú:** System-level database trên Home page, list view filtered by assignee. Không chứa dữ liệu riêng.

## ⚡ Inbox (`04_inbox/`)

- (Trống)
