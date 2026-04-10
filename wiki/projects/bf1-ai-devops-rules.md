---
title: "BF1 AI — DevOps Rules"
tags: [bf1, ai, rules, devops]
---

# DevOps & Build Conventions

## 1. Build CLI Rules
- **Gradle**: Always use the system `gradle` command, NOT the wrapper (`./gradlew`). The repository does not commit the Gradle wrapper.
- **Build Script**: Use `./tools.sh` from the repository root for common tasks.
  - Full Build: `./tools.sh build -clean -code -ui`
  - Backend Only: `./tools.sh build -clean -code`

## 2. Configuration & Naming
- **Nginx**: Config file at `/opt/homebrew/etc/nginx/servers/of1-fms.conf`. Routes follow the `/platform/plugin/*/` naming convention.
- **Release Versioning**: Do not hardcode versions in `build.gradle` release tasks. Always use the variable `$dataTPErpVersion`.
- **Passwords/Secrets**: Never hardcode credentials in config files or scripts. Always rely on environment variables (e.g., `${env.db.host}`, `${env.db.port}`).

## 3. Build & Run

### FMS Backend
From the root repo `of1-fms`:

```bash
# Default — full build BE + FE
./tools.sh build -clean -code -ui

# BE only (faster when only backend changed)
./tools.sh build -clean -code
```

```bash
# Run FMS server
cd working/release-fms/server-env
./instance.sh run
```

- Check FMS BE: `http://localhost:7084`
- **Open Web**: `http://localhost:8080`

## 4. CI/CD Pipeline (Forgejo Actions)

### Workflows
Located in `.forgejo/workflows/`:

- **`test.yaml`** — Build & Test
  - Trigger: `pull_request` vào `release`, hoặc `workflow_dispatch`
  - Steps: checkout (of1-fms + of1-core@develop + of1-platform@develop) → install shared `gradle.properties` → cache Gradle/pnpm → `./tools.sh build -code -ui`

- **`deploy.yaml`** — Build & Deploy
  - Trigger: `push` vào `release`, hoặc `workflow_dispatch`
  - Steps: giống `test.yaml` + "Determine Environment" (`release` → `prod`) + `scripts/deploy/deploy.sh <env>`

### Branch strategy
- `develop` — dev work, không trigger deploy
- `release` — mỗi push = auto deploy lên prod
- Merge flow: feature → `develop` → PR vào `release` (trigger `test.yaml`) → merge (trigger `deploy.yaml`)

### Runner requirements
- Tag: `prod` (self-hosted)
- Pre-installed: Java 21 (Temurin), Gradle tại `/opt/gradle/bin`, Node.js 20, pnpm, Docker
- Secrets cần có trong repo: `FORGEJO_TOKEN`, `NEXUS_PASSWORD`, `AHAYSOFT_PASSWORD`, `FMS_PROD_SSH_PASSWORD`

### Version pins
Committed trong `gradle.properties` (root repo). Workflow copy file này vào `~/.gradle/gradle.properties` để **mọi** project (of1-core, of1-platform, of1-fms) đọc cùng version. Khi bump version, chỉ sửa 1 file này.

### Deploy script (`scripts/deploy/deploy.sh`)
- Đọc env từ `scripts/deploy/env/{dev,prod}.env`
- **Chỉ package `release-fms/server/`** — `server-env/` trên remote được giữ nguyên (chứa `env.sh`, `instances.sh` đã cấu hình thủ công sẵn)
- Flow: tar → scp → ssh stop → backup server/ → extract → start → cleanup tar (local + remote)
- `dev.env` có `REMOTE_PASSWORD` committed (dev không nhạy cảm)
- `prod.env` **không** có `REMOTE_PASSWORD` — inject qua secret `FMS_PROD_SSH_PASSWORD` ở step "Deploy to server"

### Lưu ý khi sửa CI/CD
- Mọi thay đổi version dependency → sửa `gradle.properties`, không sửa workflow env
- Không hardcode secret trong workflow hoặc env files commit
- `env.sh` trên server cần tồn tại **trước** lần deploy đầu tiên (scp thủ công 1 lần)
- Workflow không copy `env.sh` hay bất kỳ config prod nào — mọi config server-side do ops quản lý thủ công

## 5. Local Debugging Notes
- When running locally, you must open `http://localhost:7080` first.
- After `7080` is up and has finished loading, you can then open `http://localhost:8080`.
