---
title: "BFS Storage API"
tags: [bf1, fms, api, storage]
---

# BFS Storage API — Integration Guide

Tài liệu hướng dẫn tích hợp các API thao tác file/folder trên hệ thống lưu trữ S3 (Rook-Ceph).

---

## 1. Tổng quan & Cấu hình

Hệ thống cung cấp **9 RPC endpoints** thao tác file/folder/object trên S3 (Rook-Ceph), gọi qua **một endpoint RPC duy nhất**.

| # | Endpoint | Loại | Mô tả |
|---|----------|------|-------|
| 1 | `readFile` | File | Đọc nội dung file, trả về byte[] (base64 qua RPC) |
| 2 | `writeFile` | File | Upload file lên S3, tự động tạo bucket nếu chưa có |
| 3 | `deleteFile` | File | Xóa file khỏi S3 (check protection) |
| 4 | `listFolder` | Folder | Liệt kê các object theo prefix (bao gồm sub-folder) |
| 5 | `createFolder` | Folder | Tạo folder marker |
| 6 | `deleteFolder` | Folder | Xóa folder + toàn bộ nội dung |
| 7 | `getObject` | Object | Đọc object theo bucket+key |
| 8 | `uploadObjects` | Object | Batch upload, multi-type, multi-bucket, rollback |
| 9 | `deleteObject` | Object | Xóa object theo bucket+key (check protection) |

- **Endpoint:** `POST /rest/v1.0.0/rpc/internal/call`
- **Header:** `Content-Type: application/json`
- **Request body:** `{ "component": "S3ApiService", "endpoint": "<tên method>", "userParams": { ... } }`
- **Path format:** `{bucket}/{key}` — ví dụ: `my-bucket/folder/filename.pdf`
  - Dấu `/` ở đầu path sẽ được tự động loại bỏ
  - S3 là **flat namespace** — không có folder thật, "folder" là prefix của key

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
    "path": "my-bucket/test/photo_chilli.png",
    "data": "iVBORw0KGgoAAAANSUhEUgAAAi4AAAGd...",
    "contentType": "image/png"
  }
}'
```

---

## 2. File Operations (path-based)

Các API thao tác file sử dụng path format `{bucket}/{key}`.

### 2.1 Read File (`readFile`)

Đọc nội dung file từ S3, trả về dữ liệu dạng byte[] (base64-encoded khi trả qua RPC).

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "readFile",
  "userParams": {
    "path": "my-bucket/test/photo_chilli.png"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | Đường dẫn file: `{bucket}/{key}` |

**Response**

Trả về nội dung file (base64-encoded khi qua RPC).

```
JVBERi0xLjQKMSAwIG9iago8PA0K...
```

**Errors**

| Error | Nguyên nhân |
|-------|-------------|
| `NoSuchKeyException` | File không tồn tại trên S3 |

> **Tip:** Nếu cần phân biệt rõ "file không tồn tại" (trả về `EntityNotFoundError` thay vì exception), dùng method `ensureObjectExists` (chỉ available in-process, chưa expose RPC).

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
    "path": "my-bucket/test/photo_chilli.png",
    "data": "iVBORw0KGgoAAAANSUhEUgAAAi4AAAGd...",
    "contentType": "image/png",
    "metadata": {
      "author": "hieu"
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
| `upload-date` | Thời điểm upload (compact datetime) |
| `upload-by` | Login ID của người gọi |
| `upload-by-id` | Account ID của người gọi |

> Nếu caller đã truyền `upload-by-id` trong `metadata`, hệ thống giữ nguyên tất cả giá trị của caller (idempotent).

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
    "path": "my-bucket/test/photo_chilli.png"
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

## 3. Folder Operations (path-based)

### 3.1 List Folder (`listFolder`)

Liệt kê các object trong bucket hoặc theo prefix. **Bao gồm cả sub-folder** — S3 là flat namespace nên prefix match tự động trả về tất cả objects ở mọi cấp bên dưới.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "listFolder",
  "userParams": {
    "path": "my-bucket/test"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | `{bucket}` để liệt kê toàn bộ, hoặc `{bucket}/{prefix}` để lọc |

> **Lưu ý:** Bucket name phải là **lowercase**. `createBucket()` tự động chuyển sang lowercase, nên khi list cũng phải dùng lowercase (ví dụ: `bee-quote`, không phải `Bee-Quote`).

**Response**

```json
[
  { "key": "test/dest-910599418.pdf" },
  { "key": "test/photo_chilli.png" }
]
```

> `key` là đường dẫn object **bên trong bucket**, không bao gồm tên bucket. Kết quả bao gồm objects ở tất cả sub-folder.

---

### 3.2 Create Folder (`createFolder`)

Tạo folder marker (empty object với key kết thúc `/`). Tự động tạo bucket nếu chưa tồn tại.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "createFolder",
  "userParams": {
    "path": "my-bucket/documents/reports"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | `{bucket}/{folder-path}` — `/` cuối sẽ được tự động thêm |

**Response**

```json
true
```

> **Lưu ý:** S3 không có folder thật. Method này tạo một empty object với key kết thúc `/` (ví dụ: `documents/reports/`) để đánh dấu folder tồn tại. Files có thể upload vào "folder" mà không cần tạo folder trước.

---

### 3.3 Delete Folder (`deleteFolder`)

Xóa tất cả objects trong folder (theo prefix). **Dừng lại và throw error nếu gặp file có protection — không xóa gì cả.**

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "deleteFolder",
  "userParams": {
    "path": "my-bucket/documents/reports"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `path` | `string` | Có | `{bucket}/{folder-prefix}` — phải bao gồm bucket và prefix |

**Response**

```json
true
```

**Behavior:**

1. List tất cả objects theo prefix
2. Nếu folder rỗng → trả về `true`
3. Kiểm tra protection cho **từng** object trước khi xóa
4. Nếu bất kỳ file nào có `datatp-storage-protect: true` → **throw error, không xóa gì cả**
5. Xóa tất cả objects

**Errors**

| Error | Nguyên nhân |
|-------|-------------|
| `UnknownError` | Path thiếu prefix (chỉ có bucket) |
| `UnknownError` | Có file trong folder được bảo vệ bởi `datatp-storage-protect: true` |

---

## 4. Object Operations (bucket + key)

Các API thao tác trực tiếp bằng bucket và key riêng biệt.

### 4.1 Get Object (`getObject`)

Đọc object theo bucket + key.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "getObject",
  "userParams": {
    "bucket": "bee-quote",
    "key": "LT26040456580/photo_chilli.png"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `bucket` | `string` | Có | Tên bucket |
| `key` | `string` | Có | Key của object |

**Response**

Trả về nội dung file (base64-encoded khi qua RPC).

> **So sánh với `readFile`:** `getObject` nhận bucket và key riêng biệt, `readFile` nhận path format `{bucket}/{key}`. Nội bộ `readFile` gọi `getObject`.

---

### 4.2 Upload Objects (`uploadObjects`)

Upload nhiều file cùng lúc. Hỗ trợ **multi-type** (mỗi file có contentType riêng) và **multi-bucket** (mỗi file có thể thuộc bucket khác nhau). Rollback nếu bất kỳ file nào fail.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "uploadObjects",
  "userParams": {
    "objects": [
      {
        "bucket": "my-bucket",
        "key": "test/photo_chilli.png",
        "b64Data": "iVBORw0KGgoAAAANSUhEUgAAAi4AAAGd...",
        "contentType": "image/png",
        "metadata": { "source": "bee-quote" }
      },
      {
        "bucket": "my-bucket",
        "key": "test/dest-910599418.pdf",
        "b64Data": "JVBERi0xLjUNJeLjz9MNCjYzMiAwIG9i...",
        "contentType": "application/pdf"
      }
    ]
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `objects` | `List<S3ObjectContent>` | Có | Danh sách objects cần upload |

**S3ObjectContent fields:**

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `bucket` | `string` | Có | Tên bucket |
| `key` | `string` | Có | Key (đường dẫn) trong bucket |
| `b64Data` | `string` | Có | Nội dung file mã hóa base64 |
| `contentType` | `string` | Không | MIME type |
| `metadata` | `object` | Không | Key-value metadata |

**Response**

```json
true
```

**Behavior:**

- Tự động tạo bucket nếu chưa tồn tại (check mỗi bucket unique 1 lần)
- Auto-metadata (`upload-date`, `upload-by`, `upload-by-id`) cho mỗi object
- **Rollback on failure:** Nếu bất kỳ file nào upload fail, xóa tất cả files đã upload thành công

---

### 4.3 Delete Object (`deleteObject`)

Xóa object theo bucket + key.

**Request**

```bash
curl -X POST 'https://beelogistics.cloud/rest/v1.0.0/rpc/internal/call' \
-H 'Content-Type: application/json' \
-d '{
  "component": "S3ApiService",
  "endpoint": "deleteObject",
  "userParams": {
    "bucket": "my-bucket",
    "key": "test/photo_chilli.png"
  }
}'
```

**Parameters**

| Param | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| `bucket` | `string` | Có | Tên bucket |
| `key` | `string` | Có | Key của object cần xóa |

**Response**

```json
true
```

Trả về `true` ngay cả khi object không tồn tại.

**Errors**

| Error | Nguyên nhân |
|-------|-------------|
| `UnknownError` | Object được bảo vệ bởi `datatp-storage-protect: true` |

---

## 5. Kiểm tra file trên S3

### 5.1 Web UI (Filestash)

Truy cập giao diện web để duyệt file trực tiếp:

```
http://filestash.of1-dev-kafka.svc.cluster.local/
```

### 5.2 S3 Connection Info

| Env | Endpoint | Access Key | Secret Key | Region |
|-----|----------|------------|------------|--------|
| Dev | `http://rook-ceph-rgw-bee-vietnam-dev-store-hn.rook-ceph.svc.cluster.local` | `VTFYLGlVK3dRRkdDTWo=` | `K2xEbmR0M0hiZXlvPy5SSkU0XHoxJVw8Wk9zMA==` | `bee-vietnam-dev` |
| Prod | `http://rook-ceph-rgw-bee-vietnam-hn-prod-store.rook-ceph.svc.cluster.local` | `U7IZNLULT4U5WECC29ZP` | `Gufj2fk7S2pnKuB5X3evzCsTM5kiALLzsmaPM9cM` | `bee-vietnam` |

---

## 6. Ghi chú

- **Auto Metadata:** Khi gọi `writeFile` hoặc `uploadObjects`, hệ thống tự động gán `upload-date`, `upload-by`, `upload-by-id` vào metadata nếu caller chưa truyền `upload-by-id`.
- **File Protection:** File có metadata `datatp-storage-protect: true` không thể xóa qua `deleteFile`, `deleteObject`, hoặc `deleteFolder`. Các API xóa sẽ trả về `UnknownError`.
- **S3 Flat Namespace:** S3 không có folder thật. `listFolder("bucket/docs")` trả về tất cả objects có prefix `docs/`, bao gồm cả `docs/sub/file.txt`. Method `createFolder` tạo empty marker object, không bắt buộc phải tạo folder trước khi upload file vào đó.
- **ensureObjectExists:** Method in-process (chưa expose RPC) thay thế cho `readFile` khi cần trả về `EntityNotFoundError` rõ ràng thay vì `NoSuchKeyException`.

### Internal-only Methods (không có RPC)

Các method sau chỉ available khi gọi in-process, không qua RPC:

| Method | Mô tả |
|--------|-------|
| `createBucket(bucket)` | Tạo bucket |
| `listBuckets()` | List tất cả buckets |
| `deleteBucket(bucket, clearObjects)` | Xóa bucket |
| `getObjectMetadata(bucket, key)` | Lấy metadata |
| `searchObjects(params)` | Search với pagination |
| `createStoreInfo(bucket, key)` | Tạo temp download link |
