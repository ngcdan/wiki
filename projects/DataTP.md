---
title: DataTP_Document
description:
published: true
date: 2026-02-08T03:39:53.246Z
tags:
editor: markdown
dateCreated: 2026-01-28T07:52:42.641Z
---

# Hướng Dẫn

Trang này đóng vai trò như menu tổng quan, giúp bạn điều hướng nhanh đến các mục hướng dẫn chi tiết.

---

## 📌 Mục Lục
- [S3](/OF1/Developer_Guides/MSA/S3)
- [February Plan](/OF1/Developer_Guides/Developers/DataTP_Document/February.md)


# Changelog

All notable changes to this project will be documented in this file.

### [Unreleased]
#### Hướng dẫn cập nhật
- Update schema - yêu cầu chạy instance.sh với run:update:
[Document-set] Thêm 2 cột :
***category(house-bills, tms-fcl-inv, tms-lcl-inv, receipt,...)***
Sử dụng tạo key lưu trữ trên s3 với cấu trúc {document-category}/{docSetId} - vd: tms-fcl-inv/doc-set-01.
***upload_app(tms, document,crm,...)***
Sử dụng phân loại document đc upload từ đâu

- Yêu câu máy chủ platform cập nhật config/application-env.yaml
```
s3:
  endpoint: http://rook-ceph-rgw-bee-vietnam-hn-prod-store.rook-ceph.svc.cluster.local
  access-key: U7IZNLULT4U5WECC29ZP
  secret-key: Gufj2fk7S2pnKuB5X3evzCsTM5kiALLzsmaPM9cM
  region: bee-vietnam
```
Thêm trong datatp
```
datatp:
  msa:
    identity:
      queue:
        event-producer-enable: false
        event-consumer-enable: false
        topic:
          events: "datatp.${env.name}.identity.events"
          retry-events: "datatp.${env.name}.identity.retry-events"
          event-acks: "datatp.${env.name}.identity.event-acks"
```
#### Thông tin cập nhập
- Cập nhật giao diện S3 Manager
- Viết document-set-plugin hỗ trợ xử lý các việc như move file với các loại doc-set khác nhau

- Lưu trữ vào document-upload theo cấu trúc mới
```
{companyCode}-doc-upload
    {document-category}/{docSetId}:  // vd: tms-fcl-inv/doc-set-01
        __info__
        hb-1-invoice-01.pdf
        hb-2-invoice-01.pdf
        hb-1-receipt-01.pdf
        hb-1-other-01.pdf
```

- Rename các file upload trong bộ doc-set theo bảng kê với cấu trúc {hbl-no}-{invoice-no}.ext
b1: Thực hiện đổi key và save lại trên document-db
b2: Lưu file với key mới trên S3
b3: Xóa các file với key cũ
- Move file to hbl
b1: Tạo các bộ doc-set loại doc-accounting với name là hblNo tương ứng
b2: Sao chép file từ bucket: {companyCode}-doc-upload sang {companyCode}-doc-accounting với cấu trúc
```
{companyCode}-doc-accounting
    house-bills
        {house-bill-code}
            __info__
            invoices
                invoice-01.pdf
                invoice-01.pdfie
            receipts
                receipt-01.pdf
                receipt-01.pdfie
            others
                other-01.pdf
```
b3: S3 các file origin xóa nội dung và lưu metadata link tới vị trí file ở bucket mới
datatp-storage-move-to: bucket:/key

### [R20250820]

    - Thêm chức năng in cho document dạng ảnh
    - Thêm chức năng cache lại dữ liệu taxcode

### [R20250818]

1. Tasks:

- [Dat]:
    - Thêm bổ sung xử lý các document dạng ảnh, thêm type "image" và plugin
- [Dat]:
  - Cập nhập bổ sung phần tạo bảng kê cho hóa đơn nâng hạ
- [Dat]:
  - Bổ sung phần download bộ chứng từ theo format chuẩn BFSOne

### [R20250721]


