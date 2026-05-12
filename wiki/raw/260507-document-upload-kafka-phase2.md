# Document Upload via Kafka - Phase 2 Design Notes

## Context
FMS cần migrate hàng trăm ngàn file attachment từ NAS (Windows VM) lên S3.
File sẽ liên tục có thêm mới từ hệ thống khác.

## Requirements
- Stable, tracking được, retry được, chạy nhanh, dễ scale
- File size: < 1-10MB (PDF, ảnh, docs, spreadsheets)
- Source: File nằm sẵn trên NAS/shared storage, API chỉ truyền path
- Trigger: Hệ thống khác gọi API + CDC + scheduled scan

## Tracking từ Windows VM - 3 phương án

### 1. Agent trên Windows VM (Recommended)
- Service nhỏ (Java/Python/PowerShell) trên Windows
- Watch folder bằng FileSystemWatcher / WatchService
- Detect file mới → gọi FMS API hoặc push Kafka trực tiếp
- Real-time, không cần mount NAS vào FMS server

### 2. FMS poll NAS qua SMB/CIFS mount
- Mount NAS path vào FMS server
- Cron scan folder mỗi 1-5 phút
- So sánh DB để biết file mới
- Đơn giản nhưng có delay

### 3. Windows Task Scheduler + Script
- PowerShell scheduled scan folder
- Gọi HTTP API FMS với danh sách file mới
- Lightweight, native Windows tools

## Architecture (to implement)

```
[Windows VM / External System]
  → Gọi FMS API (file path + metadata)
    → FMS Producer → Kafka topic: of1.{env}.fms.document.upload-events
      → FMS Consumer (concurrent) → Đọc file từ NAS mount → Upload S3
        → Success: update DocumentInfo status=SUCCESS
        → Failure: retry topic → retry lần nữa
          → Max retry exceeded: DLQ + Telegram alert + status=FAILED
```

## Kafka Topics
- `of1.{env}.fms.document.upload-events` — main upload requests
- `of1.{env}.fms.document.upload-retry` — retry failed uploads
- `of1.{env}.fms.document.upload-dlq` — dead letter queue

## Reference Implementation
- of1-crm: `CRMMessage` pattern (MessageEvent → Producer → Consumer → RetryConsumer → DlqAlertConsumer)
- of1-fms: existing CDC/Sync Kafka patterns

## Status: Phase 2 - Chưa implement
- Phase 1 (done): DocumentInfo entity refactor, basic sync uploadDocument
- Phase 2 (next): Kafka async upload pipeline + Windows agent
