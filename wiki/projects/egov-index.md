---
title: "Egov — README"
tags: [bf1, egov, index]
---

> Nhánh của [[bf1-index|BF1 — Migration BFS One → OF1 FMS]]

# DataTP eGov - Customs Clearance

## Project Overview

This project implements a customs declaration management system that integrates with the eCUS platform. The system provides form display, data submission, and declaration management capabilities.

## Project Timeline

## Milestones & Acceptance Criteria

| Milestone | Phase | Target Start Date | Target End Date | Actual Start Date | Actual End Date | Acceptance Criteria |
|-----------|-------|-------------------|-----------------|-------------------|-----------------|---------------------|
| M0: Analysis & Preparation | 0 | 2025-07-15 | 2025-07-25      | 2025-07-15 | TBD | Requirements documented, architecture designed, development environment ready |
| M1: Form & List Display | 1.1 | 2025-07-28 | 2025-10-03      | 2025-07-28 | TBD | Display data of export and import form with Ecus data |
| M2: BF1 Data Submition | 1.2 | 2025-10-06 | 2025-10-31      | TBD | TBD | Submit necessary data from Ecus to BF1 |
| M3: Declaration Form Input & eCUS Viewing | 1.3 | 2025-11-03 | 2025-12-26      | TBD | TBD | Complete the forms with eCUS integration. Data is displayed on eCus |
| M4: Common Funtionalities Integration | 1.3 | TBD | TBD             | TBD | TBD | Implement common components such as authentication, authentication, company structure... |
| M5: Phase 2 Planning | - | TBD | TBD             | TBD | TBD | Integrating with Gov Custom Clearance - Requirements gathered and roadmap defined |

---

### Phase 0: Analysis and Preparation

**Project Setup**
- [X] Initialize project repository and structure
- [ ] Set up development environment
- [ ] Establish coding standards and conventions

**eCUS Integration Setup**
- [X] Set up eCUS test environment
- [X] Establish secure connection protocols

**eCUS Analysis**
- [ ] Analyze current import/export declaration from CC team
- [ ] Analyze eCUS current screens usage
- [ ] Map import/export declaration to eCus screens
- [ ] Create basic mapping between screens and fields

**Project Planning**
- [X] Define project scope and boundaries
- [ ] Create detailed technical specifications
- [X] Establish development milestones
- [ ] Set up project tracking and reporting

**Technical Foundation**
- [X] Integrate common backend libraries from existing DataTP projects
- [ ] Integrate common frontend libraries and components
- [ ] Set up shared authentication mechanisms
- [ ] Configure logging and monitoring infrastructure

**Deliverables:**
- Complete development environment
- eCUS test environment setup
- Technical architecture document
- Project roadmap and timeline

---

### Phase 1: Core Declaration Management System

#### 1.0 Scope boundaries
- Tờ khai hải quan > Đăng ký mới tờ khai nhập khẩu IDA
- Tờ khai hải quan > Danh sách tờ khải nhập khẩu
- Tờ khai hải quan > Đăng ký mới tờ khai xuất khẩu EDA
- Tờ khai hải quan > Danh sách tờ khải xuất khẩu

#### 1.1 Declaration List and Form Display

**Setup & Infrastructure**
- [ ] Project initialization and development environment setup
- [ ] Database schema design for declaration forms
- [ ] API architecture planning

**Database Design**
- [ ] Set up database infrastructure
- [ ] Create initial migration scripts
- [ ] Implement database schema (incrementally)

**Form and List Display Implementation**
- [ ] Implement list view for import/export declaration forms
- [ ] Create form rendering engine for various declaration types
- [ ] Develop UI components for form display
- [ ] Collect and categorize different declaration form types

**Deliverables:**
- Display list and form of import/export declaration (for the most frequently used types of declarations - need clarify) based on data from eCus

---

#### 1.2 eCUS to BF1 Data Submission

**BF1 Submission Module**
- [ ] Open BF1 database connection
- [ ] Mapping EGov table/columns to BF1 schema 
- [ ] Implement data validation before submission
- [ ] Create submission service to insert data to BF1
- [ ] Build submission status tracking

**Deliverables:**
- Reliable submission pipeline to BF1
- Status monitoring submission
- Able to view submitted data in BF1

---

#### 1.3 Declaration Form Input & eCUS Viewing

**Form Input Development**
- [ ] Create dynamic form builder for declarations
- [ ] Implement form validation rules
- [ ] Develop save/draft functionality
- [ ] Build form submission workflow

**eCUS Integration & Testing**
- [ ] Implement submission to eCUS system
- [ ] Create view synchronization with eCUS
- [ ] Develop error handling and recovery
- [ ] Conduct end-to-end testing

**Deliverables:**
- Complete form input system for all declaration types
- Seamless submission to internal system
- Real-time viewing capability on eCUS
- (Note: Excluding customs synchronization features)

---

### Phase 2: Integrating with Gov Custom Clearance system (TBD)

*Phase 2 specifications and features to be defined based on Phase 1 outcomes and business requirements.*

---

## Technical Requirements

### Backend
- RESTful API architecture
- Database: PostgreSQL
- Integration: eCUS Database, BF1 Database
- Common parts use the same with datatp: Authentication, Authorization ...

### Frontend
- React-based web application
- Responsive design for various devices
- Real-time form validation
- Common parts use the same with datatp: Authentication, Authorization, Form, List style...

### Security
- Authentication & authorization using datatp SSO
- Audit logging

## Design & Specs

- [[egov-declaration-entity-design|Declaration Entity Design]]
- [[egov-ecus-batch-sync|eCUS Batch Sync]]
- [[egov-first-setup-accounts|First Setup Accounts]]

### Plans
- [[egov-plans-2026-03-29-company-mapper-batch-single-split|Company Mapper Batch/Single Split]]
- [[egov-plans-2026-03-29-ecus-entity-mapping-refactor|eCUS Entity Mapping Refactor]]
- [[egov-plans-2026-03-29-ecus-thaison-gaps|eCUS Thaison Gaps]]
- [[egov-plans-2026-03-29-remove-getSyncSourceConfigurationId|Remove getSyncSourceConfigurationId]]
- [[egov-plans-2026-03-30-move-mapping-back-to-mapper|Move Mapping Back to Mapper]]

### Specs
- [[egov-specs#company-mapper-batchsingle-split-design-2026-03-29|Company Mapper Design]]
- [[egov-specs#ecus-entity-mapping-design-2026-03-29|eCUS Entity Mapping Design]]
- [[egov-specs#ecus-thaison-architecture-design-2026-03-29|eCUS Thaison Architecture Design]]
- [[egov-specs#remove-getsyncsourceconfigurationid-design-2026-03-29|Remove getSyncSourceConfigurationId Design]]

### Developer
- [[egov-devlog|Developer Log]]

## Risk Management

### Technical Risks
- eCUS integration complexity
- BF1 integration complexity
- Data format compatibility issues

## Team & Resources

### Development Team Members
- Hieu
- Son

## Getting Started

### Prerequisites
```bash
Node.js >= 14.x
npm >= 6.x
Database (PostgreSQL/MySQL)
```

### Installation
```bash
# Clone the repository
git clone http://gitlab/tuan/datatp-egov.git

## Liên quan

- [[bf1-index|BF1 - Migration BFS One → OF1 FMS]]
- [[datatp-index|DataTP - Tổng quan]]
- [[datatp-cdc-debezium|CDC với Debezium]]

## License

This project is proprietary and confidential.