---
title: "BFS Storage API"
tags: [bf1, fms, api, storage]
---

# BFS Storage API — Integration Guide

Tài liệu hướng dẫn tích hợp các API thao tác file/folder trên hệ thống lưu trữ S3 (Rook-Ceph).

---

## 1. Tổng quan & Cấu hình

Hệ thống cung cấp 4 thao tác cơ bản với file trên S3 (Rook-Ceph), gọi qua **một endpoint RPC duy nhất**. Không yêu cầu authentication.

| Thao tác | Endpoint | Mô tả |
|----------|----------|-------|
| Đọc file | `readFile` | Đọc nội dung file, trả về base64 |
| Ghi file | `writeFile` | Upload file lên S3, tự động tạo bucket nếu chưa có |
| Xóa file | `deleteFile` | Xóa file khỏi S3 |
| Liệt kê folder | `listFolder` | Liệt kê các object theo bucket hoặc prefix |

- **Endpoint:** `POST /rest/v1.0.0/rpc/internal/call`
- **Header:** `Content-Type: application/json`
- **Request body:** `{ "component": "S3ApiService", "endpoint": "<tên method>", "userParams": { ... } }`
- **Path format:** `{bucket}/{key}` — ví dụ: `my-bucket/folder/filename.pdf`
  - Dấu `/` ở đầu path sẽ được tự động loại bỏ
  - Path thiếu `key` (chỉ có bucket hoặc rỗng) sẽ trả về lỗi

**Lỗi chung** (áp dụng cho tất cả endpoint):

| Error | Nguyên nhân |
|-------|-------------|
| `UnknownError` | Path không hợp lệ (rỗng hoặc thiếu key) |
| `S3Exception` | Lỗi S3 (quyền truy cập, kết nối, bucket không tồn tại) |

**Ví dụ:** Upload một file PDF lên S3:

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "writeFile",
  "userParams": {
    "path": "my-bucket/documents/invoice.pdf",
    "data": "JVBERi0xLjQKMSAwIG9iago8PA0K...",
    "contentType": "application/pdf"
  }
}'
```

---

## 2. API Reference

### 2.1 Read File (`readFile`)

Đọc nội dung file từ S3, trả về dữ liệu dạng base64.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "readFile",
  "userParams": {
    "path": "my-bucket/documents/invoice.pdf"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | Đường dẫn file: `{bucket}/{key}` |

**Response**

Trả về nội dung file dạng **base64-encoded string**.

```
JVBERi0xLjQKMSAwIG9iago8PA0K...
```

**Errors**

| Error | Nguyên nhân |
|-------|-------------|
| `NoSuchKeyException` | File không tồn tại trên S3 |

> **Tip:** Nếu cần phân biệt rõ "file không tồn tại" (trả về `EntityNotFoundError` thay vì exception), dùng endpoint `ensureObjectExists`.

---

### 2.2 Write File (`writeFile`)

Upload file lên S3. Tự động tạo bucket nếu chưa tồn tại.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "writeFile",
  "userParams": {
    "path": "my-bucket/documents/invoice.pdf",
    "data": "JVBERi0xLjQKMSAwIG9iago8PA0K...",
    "contentType": "application/pdf",
    "metadata": {
      "author": "duc"
    }
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | Đường dẫn lưu file: `{bucket}/{key}` |
| `data` | `string` | Có | Nội dung file mã hóa base64 |
| `contentType` | `string` | Không | MIME type (vd: `application/pdf`, `image/png`) |
| `metadata` | `object` | Không | Key-value metadata đính kèm với file |

**Response**

```json
true
```

**Auto Metadata**

Hệ thống tự động gán các metadata sau nếu chưa tồn tại `upload-by-id` trong metadata truyền vào:

| Key | Giá trị |
|-----|---------|
| `upload-date` | Thời điểm upload |
| `upload-by` | Login ID của người gọi |
| `upload-by-id` | Account ID của người gọi |

> Nếu caller đã truyền `upload-by-id` trong `metadata`, hệ thống giữ nguyên giá trị của caller.

---

### 2.3 Delete File (`deleteFile`)

Xóa file khỏi S3.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "deleteFile",
  "userParams": {
    "path": "my-bucket/documents/invoice.pdf"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | Đường dẫn file cần xóa: `{bucket}/{key}` |

**Response**

```json
true
```

Trả về `true` ngay cả khi file không tồn tại.

**Errors**

| Error | Nguyên nhân |
|-------|-------------|
| `UnknownError` | File được bảo vệ bởi metadata `datatp-storage-protect: true` |

> File có metadata `datatp-storage-protect: true` **không thể xóa** qua API.

---

### 2.4 List Folder (`listFolder`)

Liệt kê các object trong bucket hoặc theo prefix.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "listFolder",
  "userParams": {
    "path": "my-bucket/documents"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | `{bucket}` để liệt kê toàn bộ, hoặc `{bucket}/{prefix}` để lọc theo prefix |

**Response**

```json
[
  { "key": "documents/invoice.pdf" },
  { "key": "documents/contract.docx" }
]
```

> `key` là đường dẫn object **bên trong bucket**, không bao gồm tên bucket.

---

## 3. Kiểm tra file trên S3

### 3.1 Web UI (Filestash)

Truy cập giao diện web để duyệt file trực tiếp:

```
http://filestash.of1-dev-kafka.svc.cluster.local/
```

### 3.2 S3 Connection Info

| Env | Endpoint | Access Key | Secret Key | Region |
|-----|----------|------------|------------|--------|
| Dev | `http://rook-ceph-rgw-bee-vietnam-dev-store-hn.rook-ceph.svc.cluster.local` | `VTFYLGlVK3dRRkdDTWo=` | `K2xEbmR0M0hiZXlvPy5SSkU0XHoxJVw8Wk9zMA==` | `bee-vietnam-dev` |
| Prod | `http://rook-ceph-rgw-bee-vietnam-hn-prod-store.rook-ceph.svc.cluster.local` | `U7IZNLULT4U5WECC29ZP` | `Gufj2fk7S2pnKuB5X3evzCsTM5kiALLzsmaPM9cM` | `bee-vietnam` |

---

## 4. Ghi chú

- **Auto Metadata:** Khi gọi `writeFile`, hệ thống tự động gán `upload-date`, `upload-by`, `upload-by-id` vào metadata nếu caller chưa truyền `upload-by-id`.
- **File Protection:** File có metadata `datatp-storage-protect: true` không thể xóa qua API `deleteFile`. API sẽ trả về `UnknownError`.
- **ensureObjectExists:** Endpoint thay thế cho `readFile` khi cần trả về `EntityNotFoundError` rõ ràng thay vì `NoSuchKeyException`.
