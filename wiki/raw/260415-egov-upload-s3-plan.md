# eGov S3 File Upload — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement file upload/download for eGov declarations using AWS S3 SDK with Rook-Ceph storage.

**Architecture:** Backend Spring Boot service with direct S3Client, multipart upload from React frontend, metadata tracked in PostgreSQL. Single bucket `egov-documents` with hierarchical key: `{company}/{vendor}/{partner}/{yyMM}/{declCode}/{file}`.

**Tech Stack:** Java 21, Spring Boot 3.3.3, AWS S3 SDK 2.26.0, PostgreSQL + Liquibase, React 18 + Bootstrap 5 + @of1-webui/lib

**Spec:** `/Users/nqcdan/dev/wiki/wiki/raw/260414-egov-upload-s3.md`

---

## File Map

### Backend — New Files
| File | Purpose |
|------|---------|
| `module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeclarationFileAttachment.java` | JPA entity for file metadata |
| `module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeclarationFileAttachmentRepository.java` | JPA repository |
| `module/ecutoms/src/main/java/com/egov/ecutoms/service/DeclarationFileService.java` | Upload/download/delete/list/zip logic |
| `module/ecutoms/src/main/java/com/egov/ecutoms/controller/DeclarationFileController.java` | REST endpoints |
| `module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Properties.java` | S3 config properties |
| `module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Config.java` | S3Client bean |
| `module/ecutoms/src/main/resources/db/changelog/changes/004-file-attachment.sql` | Liquibase: create table + drop old |

### Backend — Modified Files
| File | Change |
|------|--------|
| `module/ecutoms/src/main/resources/db/changelog/db.changelog-master.yaml` | Add include for 004 |
| `release/src/app/server/addons/egov/config/addon-egov-config.yaml` | Add S3 config section |

### Frontend — New Files
| File | Purpose |
|------|---------|
| `webui/egov/src/module/egov/declaration/detail-screens/FileAttachmentEntity.tsx` | File upload/download UI section |

### Frontend — Modified Files
| File | Change |
|------|--------|
| `webui/egov/src/module/egov/declaration/detail-screens/index.tsx` | Export new section |
| `webui/egov/src/module/egov/declaration/UIImportEditor.tsx` | Add file attachment section to tab |
| `webui/egov/src/module/egov/declaration/UIExportEditor.tsx` | Add file attachment section to tab |

### Files to Remove (Phase 1)
| File | Reason |
|------|--------|
| `module/ecutoms/src/main/java/com/egov/ecutoms/entity/AttachedDocumentItem.java` | Replaced by DeclarationFileAttachment |
| `module/ecutoms/src/main/java/com/egov/ecutoms/repository/AttachedDocumentItemRepository.java` | No longer needed |

---

## Task 1: Liquibase Migration

**Files:**
- Create: `module/ecutoms/src/main/resources/db/changelog/changes/004-file-attachment.sql`
- Modify: `module/ecutoms/src/main/resources/db/changelog/db.changelog-master.yaml`

- [ ] **Step 1: Create migration SQL file**

```sql
--liquibase formatted sql

--changeset dan:4-1 labels:file-attachment context:dev,beta,prod
--comment: Create declaration file attachment table for S3 uploads
CREATE TABLE IF NOT EXISTS egov_declaration_file_attachment (
    id BIGSERIAL PRIMARY KEY,
    created_by VARCHAR(255),
    created_time TIMESTAMP(6),
    modified_by VARCHAR(255),
    modified_time TIMESTAMP(6),
    storage_state VARCHAR(255),
    version BIGINT,
    company_id BIGINT NOT NULL,
    partner_company_id BIGINT,
    declaration_id BIGINT NOT NULL REFERENCES declaration(id),
    declaration_code VARCHAR(64),
    vendor VARCHAR(50),
    s3_key VARCHAR(512) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    content_type VARCHAR(128),
    uploaded_by VARCHAR(64),
    uploaded_at TIMESTAMP(6),
    metadata JSONB
);

CREATE INDEX idx_file_att_company_decl ON egov_declaration_file_attachment(company_id, declaration_code);
CREATE INDEX idx_file_att_company_partner ON egov_declaration_file_attachment(company_id, partner_company_id);
CREATE INDEX idx_file_att_declaration ON egov_declaration_file_attachment(declaration_id);

--changeset dan:4-2 labels:file-attachment context:dev,beta,prod
--comment: Drop legacy attached_document_items table (replaced by file attachment)
DROP TABLE IF EXISTS attached_document_items CASCADE;
```

- [ ] **Step 2: Add include to changelog master**

Add to `db.changelog-master.yaml` after the 003 entry:
```yaml
  # 004: File attachment table + drop legacy attached_document_items
  - include:
      file: changes/004-file-attachment.sql
      relativeToChangelogFile: true
```

- [ ] **Step 3: Commit**

```bash
git add module/ecutoms/src/main/resources/db/changelog/
git commit -m "feat: add liquibase migration for declaration file attachment"
```

---

## Task 2: S3 Configuration

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Properties.java`
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Config.java`
- Modify: `release/src/app/server/addons/egov/config/addon-egov-config.yaml`

- [ ] **Step 1: Create EgovS3Properties**

```java
package com.egov.ecutoms.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

@Getter
@Setter
@ConfigurationProperties(prefix = "egov.s3")
public class EgovS3Properties {
    private String endpoint;
    private String accessKey;
    private String secretKey;
    private String region;
    private long maxFileSize = 52428800; // 50MB default
}
```

- [ ] **Step 2: Create EgovS3Config**

```java
package com.egov.ecutoms.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

import java.net.URI;

@Configuration
@EnableConfigurationProperties(EgovS3Properties.class)
public class EgovS3Config {

    @Bean
    public S3Client s3Client(EgovS3Properties props) {
        return S3Client.builder()
            .endpointOverride(URI.create(props.getEndpoint()))
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create(props.getAccessKey(), props.getSecretKey())))
            .region(Region.of(props.getRegion()))
            .forcePathStyle(true)
            .build();
    }
}
```

- [ ] **Step 3: Add S3 config to addon-egov-config.yaml**

Add at root level of the yaml:
```yaml
egov:
  s3:
    endpoint: ${env.s3.endpoint:http://rook-ceph-rgw-bee-vietnam-dev-store-hn.rook-ceph.svc.cluster.local}
    access-key: ${env.s3.access-key}
    secret-key: ${env.s3.secret-key}
    region: ${env.s3.region:bee-vietnam-dev}
    max-file-size: 52428800
```

- [ ] **Step 4: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Properties.java
git add module/ecutoms/src/main/java/com/egov/ecutoms/config/EgovS3Config.java
git add release/src/app/server/addons/egov/config/addon-egov-config.yaml
git commit -m "feat: add S3 client configuration for file uploads"
```

---

## Task 3: Entity + Repository

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeclarationFileAttachment.java`
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeclarationFileAttachmentRepository.java`
- Remove: `module/ecutoms/src/main/java/com/egov/ecutoms/entity/AttachedDocumentItem.java`
- Remove: `module/ecutoms/src/main/java/com/egov/ecutoms/repository/AttachedDocumentItemRepository.java`

- [ ] **Step 1: Create DeclarationFileAttachment entity**

```java
package com.egov.ecutoms.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import io.hypersistence.utils.hibernate.type.json.JsonType;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import net.datatp.util.text.DateUtil;
import org.hibernate.annotations.Type;

import java.util.Date;
import java.util.Map;

@Entity
@Table(name = "egov_declaration_file_attachment", indexes = {
    @Index(name = "idx_file_att_company_decl", columnList = "company_id, declaration_code"),
    @Index(name = "idx_file_att_company_partner", columnList = "company_id, partner_company_id"),
    @Index(name = "idx_file_att_declaration", columnList = "declaration_id")
})
@JsonInclude(Include.NON_NULL)
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
@NoArgsConstructor
@Getter
@Setter
public class DeclarationFileAttachment extends PersistableEntity<Long> {

    @Column(name = "company_id", nullable = false)
    private Long companyId;

    @Column(name = "partner_company_id")
    private Long partnerCompanyId;

    @Column(name = "declaration_id", nullable = false, insertable = false, updatable = false)
    private Long declarationId;

    @Column(name = "declaration_code", length = 64)
    private String declarationCode;

    @Column(name = "vendor", length = 50)
    private String vendor;

    @Column(name = "s3_key", nullable = false, length = 512)
    private String s3Key;

    @Column(name = "file_name", nullable = false, length = 255)
    private String fileName;

    @Column(name = "file_size")
    private Long fileSize;

    @Column(name = "content_type", length = 128)
    private String contentType;

    @Column(name = "uploaded_by", length = 64)
    private String uploadedBy;

    @JsonFormat(pattern = DateUtil.COMPACT_DATETIME_FORMAT)
    @Column(name = "uploaded_at")
    private Date uploadedAt;

    @Type(JsonType.class)
    @Column(name = "metadata", columnDefinition = "jsonb")
    private Map<String, Object> metadata;
}
```

- [ ] **Step 2: Create DeclarationFileAttachmentRepository**

```java
package com.egov.ecutoms.repository;

import com.egov.ecutoms.entity.DeclarationFileAttachment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DeclarationFileAttachmentRepository extends JpaRepository<DeclarationFileAttachment, Long> {
    List<DeclarationFileAttachment> findByDeclarationIdOrderByUploadedAtDesc(Long declarationId);
}
```

- [ ] **Step 3: Remove AttachedDocumentItem entity and repository**

Delete:
- `module/ecutoms/src/main/java/com/egov/ecutoms/entity/AttachedDocumentItem.java`
- `module/ecutoms/src/main/java/com/egov/ecutoms/repository/AttachedDocumentItemRepository.java`

Then grep for any remaining references to `AttachedDocumentItem` or `AttachedDocumentItemRepository` in the codebase and remove/update them. Key places to check:
- `DeclarationAttachedDocument.java` — has `@OneToMany` to `AttachedDocumentItem`. Remove that field.
- `detail-screens/AttachmentEntity.tsx` — references `attachedDocumentItems`. Will be replaced in Task 6.
- Any test files referencing these classes.
- Any imports in service/logic files.

- [ ] **Step 4: Add OneToMany to Declaration for file attachments**

In `Declaration.java`, add after the existing `declarationAttachedDocument` field:

```java
@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
@JoinColumn(name = "declaration_id")
private List<DeclarationFileAttachment> fileAttachments = new ArrayList<>();

public void addFileAttachment(DeclarationFileAttachment attachment) {
    fileAttachments.add(attachment);
}

public void removeFileAttachment(DeclarationFileAttachment attachment) {
    fileAttachments.remove(attachment);
}
```

Add import: `import java.util.ArrayList;` and `import java.util.List;`

- [ ] **Step 5: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/entity/DeclarationFileAttachment.java
git add module/ecutoms/src/main/java/com/egov/ecutoms/repository/DeclarationFileAttachmentRepository.java
git add module/ecutoms/src/main/java/com/egov/ecutoms/entity/Declaration.java
git rm module/ecutoms/src/main/java/com/egov/ecutoms/entity/AttachedDocumentItem.java
git rm module/ecutoms/src/main/java/com/egov/ecutoms/repository/AttachedDocumentItemRepository.java
git commit -m "feat: add DeclarationFileAttachment entity, remove legacy AttachedDocumentItem"
```

---

## Task 4: Backend Service

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/service/DeclarationFileService.java`

- [ ] **Step 1: Create DeclarationFileService**

```java
package com.egov.ecutoms.service;

import com.egov.ecutoms.config.EgovS3Properties;
import com.egov.ecutoms.entity.Declaration;
import com.egov.ecutoms.entity.DeclarationFileAttachment;
import com.egov.ecutoms.entity.PartnerCompany;
import com.egov.ecutoms.entity.SyncSourceConfiguration;
import com.egov.ecutoms.repository.DeclarationFileAttachmentRepository;
import com.egov.ecutoms.repository.DeclarationRepository;
import jakarta.servlet.http.HttpServletResponse;
import net.datatp.util.text.FileUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.io.IOException;
import java.io.OutputStream;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service("DeclarationFileService")
public class DeclarationFileService {

    private static final String BUCKET = "egov-documents";
    private static final DateTimeFormatter YY_MM = DateTimeFormatter.ofPattern("yyMM");

    @Autowired
    private S3Client s3Client;

    @Autowired
    private EgovS3Properties s3Properties;

    @Autowired
    private DeclarationRepository declarationRepository;

    @Autowired
    private DeclarationFileAttachmentRepository fileAttachmentRepository;

    @Autowired
    private PartnerCompanyService partnerCompanyService;

    @Autowired
    private SyncSourceConfigurationService syncSourceConfigurationService;

    @Transactional
    public List<DeclarationFileAttachment> upload(Long declarationId, MultipartFile[] files, String uploadedBy) throws IOException {
        Declaration declaration = declarationRepository.findById(declarationId)
            .orElseThrow(() -> new IllegalArgumentException("Declaration not found: " + declarationId));

        String companyCode = resolveCompanyCode(declaration);
        String vendor = resolveVendor(declaration);
        String partnerCode = resolvePartnerCode(declaration);
        String yyMM = LocalDate.now().format(YY_MM);
        String declCode = declaration.getDeclarationNo() != null ? declaration.getDeclarationNo() : String.valueOf(declaration.getSequenceNo());

        ensureBucketExists();

        List<DeclarationFileAttachment> results = new ArrayList<>();
        for (MultipartFile file : files) {
            validateFileSize(file);
            String sanitizedName = sanitizeFileName(file.getOriginalFilename());
            String s3Key = String.join("/", companyCode, vendor, partnerCode, yyMM, declCode, sanitizedName);

            s3Client.putObject(
                PutObjectRequest.builder()
                    .bucket(BUCKET)
                    .key(s3Key)
                    .contentType(file.getContentType())
                    .build(),
                RequestBody.fromBytes(file.getBytes())
            );

            DeclarationFileAttachment attachment = new DeclarationFileAttachment();
            attachment.setCompanyId(declaration.getCompanyId());
            attachment.setPartnerCompanyId(declaration.getPartnerCompanyId());
            attachment.setDeclarationCode(declCode);
            attachment.setVendor(vendor);
            attachment.setS3Key(s3Key);
            attachment.setFileName(sanitizedName);
            attachment.setFileSize(file.getSize());
            attachment.setContentType(file.getContentType());
            attachment.setUploadedBy(uploadedBy);
            attachment.setUploadedAt(new Date());

            declaration.addFileAttachment(attachment);
            results.add(attachment);
        }

        declarationRepository.save(declaration);
        return results;
    }

    @Transactional(readOnly = true)
    public List<DeclarationFileAttachment> list(Long declarationId) {
        return fileAttachmentRepository.findByDeclarationIdOrderByUploadedAtDesc(declarationId);
    }

    @Transactional(readOnly = true)
    public void download(Long declarationId, Long attachmentId, HttpServletResponse response) throws IOException {
        DeclarationFileAttachment attachment = fileAttachmentRepository.findById(attachmentId)
            .orElseThrow(() -> new IllegalArgumentException("Attachment not found: " + attachmentId));

        var s3Response = s3Client.getObject(
            GetObjectRequest.builder().bucket(BUCKET).key(attachment.getS3Key()).build()
        );

        response.setContentType(attachment.getContentType());
        response.setHeader("Content-Disposition", "attachment; filename=\"" + attachment.getFileName() + "\"");
        if (attachment.getFileSize() != null) {
            response.setContentLengthLong(attachment.getFileSize());
        }
        s3Response.transferTo(response.getOutputStream());
    }

    @Transactional(readOnly = true)
    public void downloadZip(Long declarationId, HttpServletResponse response) throws IOException {
        List<DeclarationFileAttachment> attachments = fileAttachmentRepository
            .findByDeclarationIdOrderByUploadedAtDesc(declarationId);

        if (attachments.isEmpty()) {
            throw new IllegalArgumentException("No attachments found for declaration: " + declarationId);
        }

        String zipName = attachments.get(0).getDeclarationCode() + "-documents.zip";
        response.setContentType("application/zip");
        response.setHeader("Content-Disposition", "attachment; filename=\"" + zipName + "\"");

        try (ZipOutputStream zipOut = new ZipOutputStream(response.getOutputStream())) {
            for (DeclarationFileAttachment att : attachments) {
                var s3Response = s3Client.getObject(
                    GetObjectRequest.builder().bucket(BUCKET).key(att.getS3Key()).build()
                );
                zipOut.putNextEntry(new ZipEntry(att.getFileName()));
                s3Response.transferTo(zipOut);
                zipOut.closeEntry();
            }
            zipOut.finish();
        }
    }

    @Transactional
    public void delete(Long declarationId, Long attachmentId) {
        Declaration declaration = declarationRepository.findById(declarationId)
            .orElseThrow(() -> new IllegalArgumentException("Declaration not found: " + declarationId));

        DeclarationFileAttachment attachment = declaration.getFileAttachments().stream()
            .filter(a -> a.getId().equals(attachmentId))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException("Attachment not found: " + attachmentId));

        s3Client.deleteObject(
            DeleteObjectRequest.builder().bucket(BUCKET).key(attachment.getS3Key()).build()
        );

        declaration.removeFileAttachment(attachment);
        declarationRepository.save(declaration);
    }

    private void ensureBucketExists() {
        try {
            s3Client.headBucket(HeadBucketRequest.builder().bucket(BUCKET).build());
        } catch (NoSuchBucketException e) {
            s3Client.createBucket(CreateBucketRequest.builder().bucket(BUCKET).build());
        }
    }

    private void validateFileSize(MultipartFile file) {
        if (file.getSize() > s3Properties.getMaxFileSize()) {
            throw new IllegalArgumentException(
                "File size exceeds limit: " + file.getOriginalFilename() +
                " (" + file.getSize() + " > " + s3Properties.getMaxFileSize() + ")");
        }
    }

    private String sanitizeFileName(String fileName) {
        if (fileName == null) return "unnamed";
        return fileName.replaceAll("[^a-zA-Z0-9._-]", "_");
    }

    private String resolveCompanyCode(Declaration declaration) {
        // Company code comes from the platform context
        // For now, derive from companyId via a lookup or use a default
        // TODO: Inject company code resolution from platform
        return "company-" + declaration.getCompanyId();
    }

    private String resolveVendor(Declaration declaration) {
        if (declaration.getSyncSourceConfigurationId() == null) return "ecus";
        // Lookup SyncSourceConfiguration to get vendor
        // TODO: Use SyncSourceConfigurationService to resolve
        return "ecus";
    }

    private String resolvePartnerCode(Declaration declaration) {
        if (declaration.getPartnerCompanyId() == null) return "unknown";
        // TODO: Lookup PartnerCompany.code by partnerCompanyId
        return "partner-" + declaration.getPartnerCompanyId();
    }
}
```

> **Note:** The `resolveCompanyCode`, `resolveVendor`, `resolvePartnerCode` methods contain TODOs. During implementation, check existing services (`PartnerCompanyService`, `SyncSourceConfigurationService`) for actual lookup patterns and wire them properly. The placeholder implementations ensure the code compiles and runs; real resolution is wired when those services are confirmed available.

- [ ] **Step 2: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/service/DeclarationFileService.java
git commit -m "feat: add DeclarationFileService with S3 upload/download/zip/delete"
```

---

## Task 5: REST Controller

**Files:**
- Create: `module/ecutoms/src/main/java/com/egov/ecutoms/controller/DeclarationFileController.java`

- [ ] **Step 1: Create DeclarationFileController**

```java
package com.egov.ecutoms.controller;

import com.egov.ecutoms.entity.DeclarationFileAttachment;
import com.egov.ecutoms.service.DeclarationFileService;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/declaration")
public class DeclarationFileController {

    @Autowired
    private DeclarationFileService fileService;

    @PostMapping("/{declarationId}/files")
    public ResponseEntity<List<DeclarationFileAttachment>> upload(
            @PathVariable Long declarationId,
            @RequestParam("files") MultipartFile[] files) throws IOException {
        // TODO: resolve uploadedBy from security context
        String uploadedBy = "system";
        List<DeclarationFileAttachment> result = fileService.upload(declarationId, files, uploadedBy);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{declarationId}/files")
    public ResponseEntity<List<DeclarationFileAttachment>> list(@PathVariable Long declarationId) {
        return ResponseEntity.ok(fileService.list(declarationId));
    }

    @GetMapping("/{declarationId}/files/{attachmentId}")
    public void download(
            @PathVariable Long declarationId,
            @PathVariable Long attachmentId,
            HttpServletResponse response) throws IOException {
        fileService.download(declarationId, attachmentId, response);
    }

    @GetMapping("/{declarationId}/files/zip")
    public void downloadZip(
            @PathVariable Long declarationId,
            HttpServletResponse response) throws IOException {
        fileService.downloadZip(declarationId, response);
    }

    @DeleteMapping("/{declarationId}/files/{attachmentId}")
    public ResponseEntity<Void> delete(
            @PathVariable Long declarationId,
            @PathVariable Long attachmentId) {
        fileService.delete(declarationId, attachmentId);
        return ResponseEntity.ok().build();
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add module/ecutoms/src/main/java/com/egov/ecutoms/controller/DeclarationFileController.java
git commit -m "feat: add REST controller for declaration file operations"
```

---

## Task 6: Frontend — File Attachment Section

**Files:**
- Create: `webui/egov/src/module/egov/declaration/detail-screens/FileAttachmentEntity.tsx`
- Modify: `webui/egov/src/module/egov/declaration/detail-screens/index.tsx`

- [ ] **Step 1: Create FileAttachmentEntity.tsx**

This component handles file upload, list, download, delete independent of the Declaration save flow. It uses `rest.formSubmit()` for multipart upload (same pattern as `UIProductList.tsx` Excel import) and `createHttpBackendCall()` for list/delete.

```tsx
import React from 'react';
import { bs, app } from '@of1-webui/lib';
import { FeatherIcon } from 'react-feather';
import { T } from '../../Dependency';

interface FileAttachmentProps {
  appContext: app.HostAppContext;
  pageContext: any;
  declarationId: number | null;
}

interface FileAttachmentState {
  attachments: any[];
  uploading: boolean;
}

export class UIFileAttachmentSection extends React.Component<FileAttachmentProps, FileAttachmentState> {
  private fileInputRef = React.createRef<HTMLInputElement>();

  state: FileAttachmentState = {
    attachments: [],
    uploading: false
  };

  componentDidMount() {
    this.loadAttachments();
  }

  componentDidUpdate(prevProps: FileAttachmentProps) {
    if (prevProps.declarationId !== this.props.declarationId) {
      this.loadAttachments();
    }
  }

  loadAttachments = () => {
    const { appContext, declarationId } = this.props;
    if (!declarationId) return;

    const rest = appContext.getBackendConfigs().getBackendConfig('egov').getRestClient();
    rest.get(`api/declaration/${declarationId}/files`, (result: any) => {
      if (result.data) {
        this.setState({ attachments: result.data });
      }
    });
  }

  onUploadClick = () => {
    this.fileInputRef.current?.click();
  }

  onFileSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { appContext, declarationId } = this.props;
    if (!declarationId || !event.target.files || event.target.files.length === 0) return;

    const rest = appContext.getBackendConfigs().getBackendConfig('egov').getRestClient();
    const data = new FormData();
    for (let i = 0; i < event.target.files.length; i++) {
      data.append('files', event.target.files[i]);
    }

    this.setState({ uploading: true });
    rest.formSubmit(`api/declaration/${declarationId}/files`, data, (_result: any) => {
      this.setState({ uploading: false });
      this.loadAttachments();
      // Reset file input
      if (this.fileInputRef.current) this.fileInputRef.current.value = '';
    });
  }

  onDownload = (attachment: any) => {
    const { appContext, declarationId } = this.props;
    const rest = appContext.getBackendConfigs().getBackendConfig('egov').getRestClient();
    const url = rest.getBaseUrl() + `api/declaration/${declarationId}/files/${attachment.id}`;
    window.open(url, '_blank');
  }

  onDownloadZip = () => {
    const { appContext, declarationId } = this.props;
    if (!declarationId) return;
    const rest = appContext.getBackendConfigs().getBackendConfig('egov').getRestClient();
    const url = rest.getBaseUrl() + `api/declaration/${declarationId}/files/zip`;
    window.open(url, '_blank');
  }

  onDelete = (attachment: any) => {
    const { appContext, declarationId } = this.props;
    if (!declarationId) return;
    if (!confirm(T('Xác nhận xóa file') + ': ' + attachment.fileName + '?')) return;

    const rest = appContext.getBackendConfigs().getBackendConfig('egov').getRestClient();
    rest.delete(`api/declaration/${declarationId}/files/${attachment.id}`, (_result: any) => {
      this.loadAttachments();
    });
  }

  formatFileSize = (bytes: number) => {
    if (!bytes) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  render() {
    const { declarationId } = this.props;
    const { attachments, uploading } = this.state;

    if (!declarationId) {
      return (
        <bs.Card header={T("Chứng từ đính kèm (File)")}>
          <div className='p-3 text-center text-muted'>
            {T("Lưu tờ khai trước khi upload file")}
          </div>
        </bs.Card>
      );
    }

    return (
      <bs.Card header={T("Chứng từ đính kèm (File)")}>
        <div className='p-2'>
          <div className='d-flex gap-2 mb-3'>
            <button className='btn btn-sm btn-primary' onClick={this.onUploadClick} disabled={uploading}>
              {uploading ? T('Đang upload...') : T('Upload file')}
            </button>
            {attachments.length > 0 && (
              <button className='btn btn-sm btn-outline-secondary' onClick={this.onDownloadZip}>
                {T('Download tất cả (ZIP)')}
              </button>
            )}
            <input
              ref={this.fileInputRef}
              type='file'
              multiple
              style={{ display: 'none' }}
              onChange={this.onFileSelected}
            />
          </div>

          {attachments.length > 0 && (
            <table className='table table-sm table-hover'>
              <thead>
                <tr>
                  <th>{T('STT')}</th>
                  <th>{T('Tên file')}</th>
                  <th>{T('Kích thước')}</th>
                  <th>{T('Loại')}</th>
                  <th>{T('Người upload')}</th>
                  <th>{T('Ngày upload')}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {attachments.map((att: any, idx: number) => (
                  <tr key={att.id}>
                    <td>{idx + 1}</td>
                    <td>
                      <a href='#' onClick={(e) => { e.preventDefault(); this.onDownload(att); }}>
                        {att.fileName}
                      </a>
                    </td>
                    <td>{this.formatFileSize(att.fileSize)}</td>
                    <td>{att.contentType}</td>
                    <td>{att.uploadedBy}</td>
                    <td>{att.uploadedAt}</td>
                    <td>
                      <button className='btn btn-sm btn-outline-danger' onClick={() => this.onDelete(att)}>
                        {T('Xóa')}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {attachments.length === 0 && (
            <div className='text-center text-muted p-3'>
              {T('Chưa có file đính kèm')}
            </div>
          )}
        </div>
      </bs.Card>
    );
  }
}
```

- [ ] **Step 2: Export from detail-screens/index.tsx**

Add to `webui/egov/src/module/egov/declaration/detail-screens/index.tsx`:
```tsx
export { UIFileAttachmentSection } from './FileAttachmentEntity';
```

- [ ] **Step 3: Commit**

```bash
git add webui/egov/src/module/egov/declaration/detail-screens/FileAttachmentEntity.tsx
git add webui/egov/src/module/egov/declaration/detail-screens/index.tsx
git commit -m "feat: add file attachment upload/download UI component"
```

---

## Task 7: Integrate into Import/Export Editors

**Files:**
- Modify: `webui/egov/src/module/egov/declaration/UIImportEditor.tsx`
- Modify: `webui/egov/src/module/egov/declaration/UIExportEditor.tsx`

- [ ] **Step 1: Add UIFileAttachmentSection to UIImportEditor**

In `UIImportEditor.tsx`:

1. Add import:
```tsx
import { UIFileAttachmentSection } from './detail-screens';
```
(If `UIFileAttachmentSection` is not already in the destructured import, add it)

2. In the tab pane that contains the existing `UIAttachmentSection` (tab `general-info-2`), add below or alongside it:
```tsx
<UIFileAttachmentSection
  appContext={appContext}
  pageContext={pageContext}
  declarationId={declaration?.id || null}
/>
```

- [ ] **Step 2: Add UIFileAttachmentSection to UIExportEditor**

Same pattern as UIImportEditor — add to the appropriate tab pane.

- [ ] **Step 3: Verify build**

```bash
cd webui/egov && pnpm build
```

- [ ] **Step 4: Commit**

```bash
git add webui/egov/src/module/egov/declaration/UIImportEditor.tsx
git add webui/egov/src/module/egov/declaration/UIExportEditor.tsx
git commit -m "feat: integrate file attachment section into declaration editors"
```

---

## Task 8: Cleanup & Verify

- [ ] **Step 1: Remove all references to AttachedDocumentItem**

Grep and fix:
```bash
grep -r "AttachedDocumentItem" module/ webui/ --include="*.java" --include="*.tsx" --include="*.ts"
```

Key files to update:
- `DeclarationAttachedDocument.java` — remove `@OneToMany` to `AttachedDocumentItem`, remove `attachedDocumentItems` field
- `detail-screens/AttachmentEntity.tsx` — remove references to `attachedDocumentItems` array (the `UIAttachmentSection` can remain for document type metadata if still needed, or be removed entirely)
- Any test files

- [ ] **Step 2: Verify Gradle build**

```bash
./gradlew build
```

- [ ] **Step 3: Verify frontend build**

```bash
cd webui/egov && pnpm build
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: cleanup AttachedDocumentItem references, verify builds"
```
