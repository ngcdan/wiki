---
title: "Ideas (2)"
source: "Notion"
synced_date: "2026-04-05"
---

## Project Tracking Week 43

### Python MSA Sync

ETA/ETD data synchronization from BFSOne:
- Extract shipping data from BFSOne
- Transform to microservice format
- Sync to data warehouse
- Scheduled automation

### Kafka Monitoring

Monitor Kafka cluster health:
- Broker status
- Topic throughput
- Consumer lag tracking
- Message processing rates

### SQL Server → Debezium → Kafka Pipeline

Setup CDC pipeline:
1. Enable SQL Server CDC (Change Data Capture)
2. Configure Debezium SQL Server connector
3. Stream changes to Kafka topics
4. Process changes in downstream systems

## OF1-HRM Project Status

### Testing and Validation

- Chị Trâm conducting user acceptance testing
- Mail functionality testing
- Excel preview feature testing

## OF1-CRM Project Items

### Báo Giá (Quotation) Flow

Implement multiple quote generation scenarios:
- Single shipment quote
- Multiple route quotes
- Bulk quote generation
- Quote templates

### Lịch Sử Báo Giá (Quote History)

Implement quote versioning:
- Clone QuotationCharge with versioning
- Track quote revisions
- Compare quote versions
- Historical quote archive

### Xây Dựng Thông Tin Khách Hàng (Customer Information Building)

Customer data tracking over time:
- 30-day customer profile
- 60-day behavior tracking
- 90-day analysis
- 120-day forecast

### Pricing Trucking

Implement trucking price calculations:
- Distance-based pricing
- Weight-based charges
- Route-specific rates
- Surcharge management

### Api Mail DCenter

Email API integration for DCenter:
- Send transactional emails
- Template management
- Delivery tracking
- Bounce handling

### Api Giá cho Agency

Pricing API for agency partners:
- Real-time rate queries
- Volume discounts
- Contract pricing
- Rate card management

## Task Prioritization Framework

### 4-Part Task Classification

#### Part 1: Chân Tay (Hands-On)
Hands-on development and implementation tasks:
- Coding
- Testing
- Deployment
- Configuration

#### Part 2: Quản Lý & Review (Management & Review)
Oversight and quality assurance tasks:
- Code review
- Team coordination
- Performance monitoring
- Decision making

#### Part 3: Dọn Dẹp (Cleanup)
Technical debt and maintenance:
- Refactoring
- Deprecation removal
- Performance optimization
- Documentation updates

#### Part 4: Freelance
External project work and side tasks:
- Consulting
- Contract work
- Training
- Knowledge transfer

## 3 Main Projects Summary

### OF1-CRM Project

**Vận hành (Operations)**:
- Daily system monitoring
- User support
- Performance tracking
- Issue management

**Kiến Trúc Microservices (Architecture)**:
- Service decomposition
- API design
- Data synchronization
- Service communication

**Dữ Liệu (Data)**:
- Data warehouse design
- ETL pipelines
- Data quality assurance
- Analytics

### OF1 Mobile

Mobile application development:
- iOS app development
- Android app development
- Cross-platform features
- Push notification system

### Egov Project

Government e-services integration:
- Customs declaration submission
- Document processing
- Compliance reporting
- Regulatory integration

## Check Partners Exists Update

Enhancement to partner verification system:
- Query existing partners
- Duplicate detection
- Partner validation
- Data integrity checks

## MSA Architecture Screenshots

Visual documentation of microservice architecture:
- Service diagram
- Data flow visualization
- Component relationships
- Deployment topology

## Egov Kafka Pipeline

Event streaming for government services:
- Declaration events
- Document processing events
- Status update events
- Audit log events

## Thiết Kế Quyền Báo Cáo (Report Permission Design)

Report access control system:
- Role-based report access
- Department-specific reports
- User permission mapping
- Report visibility rules
