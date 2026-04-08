---
title: "BF1 FMS — README"
tags: [bf1, fms, index, setup]
---

# OF1 FMS — Freight Forwarder Management platform.

---

## Project Overview

### Goals

1. **Build BF1 on the new platform as a productized solution** — standardized, packagable, and ready for external customer deployment.
2. **Design as independent modules focused on Freight Forwarder Management** — each module group is independently developed, deployed, and scalable.
3. **Standardize the platform for long-term integration and operations** — consistent architecture, data model, and connectivity for stable growth.

### Core Business Modules

| Module                       | Description                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------------- |
| **Master Data**              | Shared reference data: location, country, currency, unit, and standard categories              |
| **Partner & Customer**       | Partners, customers, agents, carriers; sync with CRM                                           |
| **Job File (Master Bill)**   | Job file tracking, master bill linked to house bills, shipment structure                       |
| **House Bill**               | House bill lifecycle: status tracking, document management                                     |
| **Purchase Order & Process** | Customer service requests via PO; each PO has one or more bookings and independent POPs        |
| **Tracking & Tracing**       | Shipment/container status tracking, tracing by house bill/master bill/PO/booking, delay alerts |

### Project Milestones

| Milestone                                       | Phase | Key Deliverables                                                                                                                            | Acceptance Criteria                                                                                          |
| ----------------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| M0: Analysis & Rollout Design                   | 0.0   | Assess BF1 current state (.NET/MSSQL), define priority modules, design Java/ReactJS/PostgreSQL/Kafka architecture and parallel rollout plan | Deployment scope, data flow, target architecture, module order and pilot plan agreed                         |
| M1: PostgreSQL Foundation & Schema Design       | 0.1   | Set up PostgreSQL, standardize schema, entities, mappings and validation for core data groups                                               | Target schema finalized, new database ready, data mapping rules agreed                                       |
| M2: Read APIs & Business Screens with Test Data | 0.2   | Build read APIs, lookup screens, reports, dashboards and display forms using test data for priority modules                                 | Users can verify display flows, business data and confirm screen/API correctness on test data                |
| M3: Realtime Sync Pipeline                      | 0.3   | Build realtime pipeline `MSSQL CDC → Kafka → PostgreSQL` with retry, logging, offset tracking and checksum                                  | Data synced stably to new DB with realtime reconciliation capability                                         |
| M4: Module Pilot — Read-First Rollout           | 0.4   | Pilot by feature group and user group for read-first modules: Master Data, Partner & Customer, Job File, House Bill                         | Each pilot group has test checklist, reconciliation results vs legacy system and readiness sign-off          |
| M5: Write Functions & Write-Back Pipeline       | 1.0   | Implement write functions on new system, persist to PostgreSQL and build Kafka publish pipeline to write back to legacy system              | Write flows stable, new data synced back correctly without impacting current operations                      |
| M6: Parallel Run by User Group                  | 1.1   | Expand write pilot by feature group and user group, monitor both systems in parallel                                                        | Each rollout round has test results, reconciliation, error handling and acceptance sign-off before expanding |
| M7: Operational Hardening & Expansion           | 1.2   | Optimize performance, logging, monitoring, alerting, data quality tracking and plan expansion for remaining modules                         | New BF1 ready for long-term operations, scalable, fully monitored and expandable                             |
| M8: Full Data Migration Readiness               | 2.0   | Prepare full data migration plan, cut-over strategy, backup/rollback, reconciliation checklist and go-live criteria                         | Migration plan finalized, data validated and go-live risks controlled                                        |
| M9: Full Data Migration & Production Go-Live    | 2.1   | Migrate all required data to new system, deploy to production and monitor go-live                                                           | Data fully migrated, new system operating stably in production and accepted post go-live                     |
| M10: Post Go-Live Stabilization                 | 2.2   | Monitor live operations, handle issues, reconcile post-migration data and optimize post-deployment                                          | System stable after production rollout, critical issues resolved and operations handed over clearly          |

---

## Tech Stack

| Layer     | Technology                            |
| --------- | ------------------------------------- |
| Backend   | Java 21 / Spring Boot                 |
| Frontend  | ReactJS / Node 22.21.1 / pnpm 10.28.0 |
| Database  | PostgreSQL                            |
| Messaging | Kafka                                 |
| Build     | Gradle 9.1.0 (multi-project)          |
| Admin UI  | Spring Boot Admin                     |

---

## Module Structure

```
of1-fms/
├── module/
│   ├── core/          # Core DB infrastructure (DAOTemplate, DaoService, SqlQueryUnit)
│   ├── common/        # Shared datasource & component scan config
│   ├── settings/      # Settings: exchange rates, setting units
│   ├── reports/       # Reports
│   ├── integration/   # Batch jobs, sync, external & legacy system integration
│   ├── partner/       # Integrated partners
│   └── transaction/   # IntegratedTransaction, Housebill, HawbProfit
├── app/
│   └── server/        # Spring Boot app entry point (port 7084)
└── release/           # Build & release scripts
```

### Module Dependency Hierarchy

```
[datatp-core / datatp-platform]   ← external libraries
        │
    core                          ← core DB infrastructure
        │
    common                        ← shared datasource config, component scan
        │
   ┌────────┼────────┬───────────┬──────────────┐
settings reports integration partner  transaction
                                      │
                              app/server         ← Spring Boot entry point
```

---

## SSH Setup

### 1. Generate SSH key

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Key được lưu mặc định tại `~/.ssh/id_ed25519` (public key: `~/.ssh/id_ed25519.pub`).

### 2. Add public key to Forgejo

Copy nội dung public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Vào **Forgejo → Settings → SSH / GPG Keys → Add Key** và paste vào.

### 3. Configure ~/.ssh/config

```
Host git.datatp.cloud
  PreferredAuthentications publickey
  HostName git.datatp.cloud
  User <forgejo-username>
  Port 52222
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

> Thay `<forgejo-username>` bằng username Forgejo của bạn.
> Thay `id_ed25519` bằng tên key đã tạo nếu khác.

### 4. Verify connection

```bash
ssh -T git@git.datatp.cloud -p 52222
```

---

## Build & Run

### Build

```bash
# Backend only
./tools.sh build -clean -code

# With Web UI
./tools.sh build -clean -code -ui
```

### Run

Before running, set up and configure `env.sh`:

```bash
cd working/release-fms/server-env

# Create env.sh from sample
mv env-sample.sh env.sh
```

Edit `env.sh` and update the following variables:

```bash
# JVM Config
REMOTE_DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,address=*:5004,suspend=n"
SERVER_JAVA_OPTS="-Xmx2048m"

# Env name: local, beta, prod
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.name=local"

# Database
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.db.platform-host=postgres.of1-dev-fms.svc.cluster.local"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.db.platform-port=5432"

# Kafka
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Denv.kafka.env=dev"

# Spring Boot Admin
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.boot.admin.client.url=http://localhost:7070/admin"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.boot.admin.client.enabled=false"

export SERVER_JAVA_OPTS
```

Then start the server:

```bash
./instance.sh run
```

- FMS server: `http://localhost:7084`
- Open web: `http://localhost:8080`

> Start `http://localhost:7080` (platform) first before opening `http://localhost:8080`.

### Gradle tasks

```bash
# Build all modules
gradle build

# Build specific module
gradle :of1-fms-module-core:build
gradle :of1-fms-module-settings:build
gradle :of1-fms-module-reports:build
gradle :of1-fms-module-integration:build
gradle :of1-fms-module-partner:build
gradle :of1-fms-module-transaction:build
gradle :of1-fms-app-server:build

# Release
gradle :of1-fms-release:releaseServer
```

---

## Nginx Setup (macOS)

### Install & manage

```bash
# Update Homebrew packages
brew update && brew upgrade

# Install nginx
brew install nginx

# Start / Stop / Status
brew services start nginx
brew services stop nginx
brew services info nginx

# Test config and reload (after editing config files)
nginx -t && nginx -s reload
```

### Change default port

```bash
vi /opt/homebrew/etc/nginx/nginx.conf
# Tìm 8080 và đổi sang 80 hoặc port khác
```

### Server config

Tạo file config tại `/opt/homebrew/etc/nginx/servers/of1-fms.conf`:

```nginx
upstream platform {
  server server.of1-beta-platform.svc.cluster.local;
}

upstream platform-webui {
  server server.of1-beta-platform.svc.cluster.local;
}

server {
  listen      8080;
  http2       on;
  #server_name dev-server; 
  server_name localhost;

  proxy_redirect   off;

  proxy_set_header Host              $http_host;
  proxy_set_header X-Forwarded-Host  $http_host;
  proxy_set_header X-Real-IP         $remote_addr;
  #proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-For   $remote_addr;
  proxy_set_header X-Forwarded-Port  $server_port;
  proxy_set_header X-Forwarded-Proto $scheme;

  proxy_connect_timeout   3600;
  proxy_read_timeout      3600;
  proxy_send_timeout      3600;
  send_timeout            3600;

  client_max_body_size 25M;

  #Disable Cache
  proxy_no_cache 1;
  proxy_cache_bypass 1;
  proxy_cache off;
  add_header Cache-Control 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
  expires -1;

  location /websocket/ {
    proxy_pass http://platform/websocket/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
  }

  location / {
    #proxy_pass http://platform-webui/;
    proxy_pass http://platform/;
  }

  location /rest/ {
    proxy_pass http://platform/rest/;
  }

  location /get/ {
    proxy_pass http://platform/get/;
  }
}
```

### Service ports

| Service  | Backend port |
| -------- | ------------ |
| platform | 7080         |
| **fms**  | **7084**     |

---

## Package Structure

```
of1.fms.core                  # Core DB infrastructure, shared utilities, CDC
of1.fms.settings              # Settings: ExchangeRate, SettingUnit
of1.fms.module.reports        # Reports
of1.fms.module.integration    # Batch jobs, sync, external & legacy system integration
of1.fms.module.partner        # Integrated partners
of1.fms.module.transaction    # IntegratedTransaction, Housebill, HawbProfit
datatp.config.auto            # App server bootstrap config
```

---

## References

### Project Plan

- [BF1 Web Upgrade Plan](https://wiki.beelogistics.cloud/vi/OF1/IT_Plans/BF1_Web_Upgrade_Plan)

### Google Drive

Project documentation, guidelines, and resources:
https://drive.google.com/drive/folders/1-sBVcPbf-EAcsQ1YNrcHfndLrAojCaDF?usp=sharing

### Kafka

| Service     | Environment | URL                                                  |
| ----------- | ----------- | ---------------------------------------------------- |
| Kafka UI    | dev         | http://webui.of1-dev-kafka.svc.cluster.local/        |
| Kafka UI    | prod        | http://webui.of1-prod-kafka.svc.cluster.local/       |
| Debezium UI | dev         | http://debezium-ui.of1-dev-kafka.svc.cluster.local/  |
| Debezium UI | prod        | http://debezium-ui.of1-prod-kafka.svc.cluster.local/ |
