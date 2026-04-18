# eGov Document Upload to S3 — Design Spec

**Date:** 2026-04-14
**Status:** Draft
**Author:** Claude + Dan
**Project:** of1-egov
**Branch:** egov_local_1

---

## 1. Overview

Implement file upload/download for eGov declaration documents. Files are stored on S3 (Rook-Ceph) using AWS S3 SDK directly. Each declaration has its own set of attached documents that users can upload, download individually, or download as a zip bundle.

### Goals
- User uploads document files per declaration to S3
- User downloads individual files or entire declaration document set (zip)
- Folder structure: company > vendor > partner > yyMM > declaration code
- Single shared bucket `egov-documents`, path-based isolation
- Remove legacy `AttachedDocumentItem` table
- Phase 3 (future): sync uploaded files back to eCUS legacy MSSQL

### Out of Scope (Phase 1-2)
- eCUS MSSQL sync
- File preview in browser
- File versioning
- Access control per file (inherits declaration-level permissions)

---

## 2. Architecture

```
+--------------+     multipart      +------------------+     S3 SDK      +-------------------+
|   Frontend   | -----------------> |   eGov Backend   | -------------> |  S3 (Ceph)        |
|  (React/TS)  | <----------------- |  (Spring Boot)   | <------------- |                   |
|              |   file stream/zip  |                  |   getObject    |  Bucket:          |
|              |                    |  DeclarationFile |                |  egov-documents   |
|              |   GET /files       |  Service         |                |                   |
|              |   POST /files      |                  |   putObject    |  Key:             |
|              |   DELETE /files    |  DeclarationFile |                |  {company}/       |
|              |   GET /files/zip   |  Attachment (DB) |   deleteObject |  {vendor}/        |
+--------------+                    +------------------+                |  {partner}/       |
                                           |                           |  {yyMM}/          |
                                           v                           |  {declCode}/      |
                                   +------------------+                |  {fileName}       |
                                   |   PostgreSQL     |                +-------------------+
                                   |                  |
                                   |  egov_declaration |
                                   |  _file_attachment |
                                   +------------------+

                                   +- - - - - - - - - +
                                   | Phase 3 (Future) |
                                   |                  |
                                   | eCUS MSSQL Sync  |
                                   +- - - - - - - - - +
```

### Tech Stack
- **Storage:** S3 (Rook-Ceph) via AWS S3 SDK 2.26.0 (already in release/build.gradle)
- **Backend:** Spring Boot 3.3.3, Java 21
- **Database:** PostgreSQL (metadata tracking)
- **Frontend:** React/TypeScript (existing eGov webui)

---

## 3. S3 Storage Structure

### Bucket
```
egov-documents
```
Single shared bucket. Auto-created on first upload if not exists.

### Key (Path) Structure
```
{companyCode}/{vendor}/{partnerCode}/{yyMM}/{declarationCode}/{fileName}
```

- **companyCode**: Logistics company code (e.g., `beehph`, `beesgn`)
- **vendor**: eCUS software vendor, from `SyncSourceConfiguration.vendor` (e.g., `ecus`)
- **partnerCode**: Trading partner/client code (e.g., `abc-trading`, `thaison`)
- **yyMM**: Year-month compact format (e.g., `2604` = April 2026)
- **declarationCode**: Declaration number (e.g., `301-2026-00123`)
- **fileName**: Sanitized original file name

### Examples
```
egov-documents/beehph/ecus/abc-trading/2604/301-2026-00123/invoice.pdf
egov-documents/beehph/ecus/abc-trading/2604/301-2026-00123/co-form-d.pdf
egov-documents/beehph/ecus/abc-trading/2604/301-2026-00123/bill-of-lading.pdf
egov-documents/beesgn/ecus/xyz-corp/2604/302-2026-00456/packing-list.pdf
```

### Rationale
- **Single bucket**: Simpler management, path-based isolation via prefix
- **company > vendor > partner hierarchy**: Natural data partitioning, easy to list/filter by any level
- **yyMM compact**: Shorter path, good S3 partitioning, enables lifecycle policies
- **declarationCode folder**: 1 folder = 1 complete document set, simple zip download

---

## 4. Data Model

### New Entity: `DeclarationFileAttachment`

Separate table. Existing `AttachedDocumentItem` table will be **removed** as part of this work (it was eCUS-synced metadata, no longer needed).

```
Table: egov_declaration_file_attachment
+---------------------+---------------+------------------------------------------------------+
| Column              | Type          | Description                                          |
+---------------------+---------------+------------------------------------------------------+
| id                  | BIGINT (PK)   | Auto-generated ID                                    |
| company_id          | BIGINT (FK)   | Company scope                                        |
| partner_company_id  | BIGINT (FK)   | Partner company scope                                |
| declaration_id      | BIGINT (FK)   | FK to Declaration                                    |
| declaration_code    | VARCHAR(64)   | Redundant for S3 path lookup                         |
| vendor              | VARCHAR(50)   | eCUS vendor (from SyncSourceConfiguration)           |
| s3_key              | VARCHAR(512)  | Full key: {co}/{vendor}/{partner}/{yyMM}/{decl}/{f}  |
| file_name           | VARCHAR(255)  | Original file name                                   |
| file_size           | BIGINT        | File size in bytes                                   |
| content_type        | VARCHAR(128)  | MIME type                                            |
| uploaded_by         | VARCHAR(64)   | User login who uploaded                              |
| uploaded_at         | TIMESTAMP     | Upload timestamp                                     |
| metadata            | JSONB         | Extensible metadata (optional)                       |
+---------------------+---------------+------------------------------------------------------+

Indexes:
- (company_id, declaration_code)
- (company_id, partner_company_id)
```

Note: Bucket is always `egov-documents` (constant, not stored per row).

### Aggregate Relationship
```java
// Declaration (Aggregate Root)
@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
@JoinColumn(name = "declaration_id")
private List<DeclarationFileAttachment> fileAttachments;
```

Add/remove attachments MUST go through Declaration root (Aggregate pattern).

---

## 5. API Design

### 5.1 Upload Files

```
POST /declaration/{declarationId}/files
Content-Type: multipart/form-data

Body: file[] (one or more files)

Response 200:
[
  {
    "id": 1,
    "fileName": "invoice.pdf",
    "fileSize": 204800,
    "contentType": "application/pdf",
    "uploadedBy": "dan",
    "uploadedAt": "2026-04-14T10:30:00"
  }
]
```

**Flow:**
1. Validate file size (configurable max)
2. Load Declaration from DB (get declarationCode, companyCode, partnerCode, vendor)
3. Bucket: `egov-documents` (constant)
4. Build S3 key: `{companyCode}/{vendor}/{partnerCode}/{yyMM}/{declarationCode}/{sanitizedFileName}`
5. `S3Client.putObject(bucket, key, fileBytes, contentType)`
6. Create `DeclarationFileAttachment` entity, add to Declaration aggregate
7. Save Declaration (cascade saves attachment)
8. Return attachment DTOs

### 5.2 List Files

```
GET /declaration/{declarationId}/files

Response 200:
[
  {
    "id": 1,
    "fileName": "invoice.pdf",
    "fileSize": 204800,
    "contentType": "application/pdf",
    "uploadedBy": "dan",
    "uploadedAt": "2026-04-14T10:30:00"
  }
]
```

### 5.3 Download Single File

```
GET /declaration/{declarationId}/files/{attachmentId}

Response 200:
Content-Type: application/pdf
Content-Disposition: attachment; filename="invoice.pdf"
Body: binary file stream
```

**Flow:**
1. Load attachment from DB
2. `S3Client.getObject(bucket, s3Key)`
3. Stream response with proper Content-Type and Content-Disposition

### 5.4 Download Zip (All Files)

```
GET /declaration/{declarationId}/files/zip

Response 200:
Content-Type: application/zip
Content-Disposition: attachment; filename="301-2026-00123-documents.zip"
Body: zip stream
```

**Flow:**
1. Load all attachments for declaration from DB
2. For each attachment: `S3Client.getObject` -> write to `ZipOutputStream`
3. Stream zip response
4. Zip file name: `{declarationCode}-documents.zip`

### 5.5 Delete File

```
DELETE /declaration/{declarationId}/files/{attachmentId}

Response 200: OK
```

**Flow:**
1. Load attachment from DB
2. `S3Client.deleteObject(bucket, s3Key)`
3. Remove from Declaration aggregate (orphanRemoval handles DB delete)
4. Save Declaration

---

## 6. S3 Configuration

Add to `addon-egov-config.yaml`:

```yaml
egov:
  s3:
    endpoint: http://rook-ceph-rgw-bee-vietnam-dev-store-hn.rook-ceph.svc.cluster.local
    access-key: ${S3_ACCESS_KEY}
    secret-key: ${S3_SECRET_KEY}
    region: bee-vietnam-dev
    max-file-size: 50MB
```

Spring config class:

```java
@ConfigurationProperties(prefix = "egov.s3")
public class EgovS3Properties {
  private String endpoint;
  private String accessKey;
  private String secretKey;
  private String region;
  private String maxFileSize;
}
```

S3Client bean:

```java
@Bean
public S3Client s3Client(EgovS3Properties props) {
  return S3Client.builder()
    .endpointOverride(URI.create(props.getEndpoint()))
    .credentialsProvider(StaticCredentialsProvider.create(
      AwsBasicCredentials.create(props.getAccessKey(), props.getSecretKey())))
    .region(Region.of(props.getRegion()))
    .forcePathStyle(true) // required for Ceph
    .build();
}
```

---

## 7. Frontend Integration

### Location
Add "Chung tu dinh kem" (Attached Documents) tab/section in:
- `UIImportEditor.tsx` (import declarations)
- `UIExportEditor.tsx` (export declarations)

### Component Structure
```
DeclarationFileUpload
+-- Drag & drop zone + file picker button
+-- File list table
|   +-- fileName | size | type | uploadedAt | actions (download, delete)
+-- Upload progress bar per file
+-- "Download tat ca" button -> zip download
```

### Interaction Flow
1. User opens declaration -> load file list (`GET /declaration/{id}/files`)
2. User drag-drop/select files -> upload each file (`POST` multipart)
3. Upload complete -> refresh list, show new file
4. User clicks file -> download single (`GET .../files/{attachmentId}`)
5. User clicks "Download tat ca" -> download zip (`GET .../files/zip`)
6. User clicks delete -> confirm dialog -> delete (`DELETE .../files/{attachmentId}`)

### Key Behaviors
- Upload is **independent** from Save Declaration — no need to save declaration first
- File list loads separately, NOT part of Declaration entity JSON response (avoid heavy payload)
- Max file size validated on frontend before sending (read from backend config)
- Duplicate file name handling: append suffix `(1)`, `(2)` etc.

---

## 8. Phase Plan

### Phase 1 — Core Upload/Download (MVP)
- [ ] Remove `AttachedDocumentItem` entity + Liquibase migration (drop table)
- [ ] S3Client config + `@ConfigurationProperties`
- [ ] Entity `DeclarationFileAttachment` + Liquibase migration (create table)
- [ ] `DeclarationFileService`: upload, download single, delete, list
- [ ] REST controller endpoints
- [ ] Frontend: file list table + upload + download single + delete
- [ ] File name sanitization
- [ ] File size validation

### Phase 2 — Batch Download
- [ ] Zip download endpoint (stream ZipOutputStream)
- [ ] Frontend: "Download tat ca" button
- [ ] Configurable max zip size limit
- [ ] Error handling for large zip (too many files / total size exceeded)

### Phase 3 — eCUS Sync (Future)
- [ ] Research eCUS MSSQL schema for file attachments
- [ ] Design upload flow: S3 -> eCUS (stored procedure or direct insert binary)
- [ ] Mapping metadata between eGov attachment and eCUS format
- [ ] Sync status tracking (pending, synced, failed)
- [ ] Retry mechanism for failed syncs

---

## 9. Reference

### Existing Patterns
- **of1-crm InquiryRequest**: PlatformCallGateway + S3ApiService pattern
  - Entity: `InquiryRequestAttachment` (bucket, key, storeId, filePath, b64Data)
  - Bucket: `{companyCode}-quote`
  - Key: `{referenceCode}/{fileName}`
- **BFS Storage API** (of1-fms): RPC endpoint for S3 operations
  - `POST /platform/plugin/fms/rest/v1.0.0/rpc/internal/call`
  - Methods: readFile, writeFile, deleteFile, listFolder

### Key Differences from of1-crm Pattern
| Aspect | of1-crm | eGov (this design) |
|--------|---------|-------------------|
| S3 access | RPC via PlatformCallGateway | Direct AWS S3 SDK |
| Upload encoding | Base64 in JSON body | Multipart binary stream |
| Bucket scope | Per company | Single shared bucket |
| Path structure | {refCode}/{file} | {co}/{vendor}/{partner}/{yyMM}/{declCode}/{file} |
| Batch download | Not supported | Zip download |

### AWS S3 SDK (already in project)
- `software.amazon.awssdk:s3:2.26.0` in `release/build.gradle`
- Using `S3Client` (sync) — sufficient for document-sized files
- `forcePathStyle(true)` required for Rook-Ceph compatibility

---

## 10. Pseudocode

### Constants
```
BUCKET = "egov-documents"
```

### Upload Service
```
function upload(declarationId, files[]):
  declaration = declarationRepository.findById(declarationId)
  companyCode = declaration.companyCode.toLowerCase()
  vendor = declaration.syncSource.vendor.toLowerCase()  // e.g. "ecus"
  partnerCode = declaration.partnerCompanyCode.toLowerCase()
  yyMM = now().format("yyMM")  // e.g. "2604"

  ensureBucketExists(BUCKET)

  results = []
  for file in files:
    sanitizedName = sanitizeFileName(file.originalName)
    s3Key = "{companyCode}/{vendor}/{partnerCode}/{yyMM}/{declaration.code}/{sanitizedName}"

    s3Client.putObject(
      PutObjectRequest.builder()
        .bucket(BUCKET).key(s3Key)
        .contentType(file.contentType)
        .build(),
      RequestBody.fromBytes(file.bytes)
    )

    attachment = new DeclarationFileAttachment(
      companyId = declaration.companyId,
      partnerCompanyId = declaration.partnerCompanyId,
      declarationId = declaration.id,
      declarationCode = declaration.code,
      vendor = vendor,
      s3Key = s3Key,
      fileName = sanitizedName,
      fileSize = file.size,
      contentType = file.contentType,
      uploadedBy = currentUser.login,
      uploadedAt = now()
    )
    declaration.addFileAttachment(attachment)
    results.add(attachment)

  declarationRepository.save(declaration)
  return results.map(toDTO)
```

### Download Zip Service
```
function downloadZip(declarationId, outputStream):
  attachments = attachmentRepository.findByDeclarationId(declarationId)

  zipOut = new ZipOutputStream(outputStream)
  for att in attachments:
    s3Response = s3Client.getObject(
      GetObjectRequest.builder().bucket(BUCKET).key(att.s3Key).build()
    )
    zipOut.putNextEntry(new ZipEntry(att.fileName))
    s3Response.transferTo(zipOut)
    zipOut.closeEntry()

  zipOut.finish()
```

### Ensure Bucket Exists
```
function ensureBucketExists(bucket):
  try:
    s3Client.headBucket(HeadBucketRequest.builder().bucket(bucket).build())
  catch NoSuchBucketException:
    s3Client.createBucket(CreateBucketRequest.builder().bucket(bucket).build())
```
