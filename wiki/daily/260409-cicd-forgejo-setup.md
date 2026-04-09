# 2026-04-09 — Forgejo CI/CD Setup (fms, crm, build)

## Context

Triển khai CI/CD trên Forgejo Actions cho 3 dự án OF1 theo pattern có sẵn từ `of1-egov`:
- `of1-fms` (chính, setup đầu tiên + tối ưu)
- `of1-crm` (clone từ fms với substitution)
- `of1-build` (chỉ port block `-nexus` publish từ branch egov)

## Branch strategy

- `develop` — dev work, **không** trigger workflow
- `release` — mỗi push = auto deploy lên prod
- Flow: feature → `develop` → PR vào `release` (trigger `test.yaml`) → merge (trigger `deploy.yaml`)
- `workflow_dispatch` vẫn bật để trigger manual khi cần

## Files tạo cho mỗi repo (fms/crm)

```
.forgejo/workflows/test.yaml       # Build & Test - PR vào release
.forgejo/workflows/deploy.yaml     # Build & Deploy - push vào release
scripts/deploy/deploy.sh           # Adapt từ of1-egov
scripts/deploy/env/dev.env         # Host/user/password dev (committed)
scripts/deploy/env/prod.env        # Host/user (no password)
gradle.properties                  # Version pins (nguồn duy nhất)
.gitignore                         # Exception cho .forgejo/ và env files
```

## Version pins & DRY env

- Version Spring/Hibernate/Jetty/... pin trong `gradle.properties` tại root mỗi repo
- Workflow step **"Install shared gradle.properties (user-level)"** copy file này vào `~/.gradle/gradle.properties` → mọi project (of1-core, of1-platform, of1-fms/crm) đọc cùng 1 nguồn
- Bump version → sửa 1 file `gradle.properties`, không động workflow

## Secrets cần có trong mỗi repo Forgejo

| Secret | Mục đích |
|---|---|
| `FORGEJO_TOKEN` | Checkout cross-repo (of1-core@develop, of1-platform@develop) |
| `NEXUS_PASSWORD` | Gradle dependency resolution |
| `AHAYSOFT_PASSWORD` | Internal artifact repo |
| `{FMS|CRM}_PROD_SSH_PASSWORD` | SSH deploy prod (`prod.env` không commit password) |

## Cache (actions/cache@v4)

Không có quyền setup persistent dir trên runner VM → dùng `actions/cache@v4`:
- `~/.gradle/caches`, `~/.gradle/wrapper` — key theo hash `gradle.properties`, `*.gradle`
- `~/.pnpm-store` — key theo hash `pnpm-lock.yaml`

## Runner requirements (tag `prod`)

- Java 21 Temurin
- Gradle tại `/opt/gradle/bin` (workflow prepend vào PATH)
- Node.js 20, pnpm
- Docker socket
- Truy cập internal Nexus: `http://nexus.of1-dev-egov.svc.cluster.local`

## Deploy script — điểm quan trọng

`scripts/deploy/deploy.sh`:
1. Tar **chỉ** `release-{fms,crm}/server/` (KHÔNG tar `server-env/`)
2. scp → ssh stop → backup `server/` → extract → start → cleanup tar (local + remote)
3. `server-env/` trên remote **được giữ nguyên** — chứa `env.sh`, `instances.sh` được cấu hình thủ công

**Lý do:** CI build không tạo đầy đủ `env.sh`, và `env.sh` chứa config server-specific mà ops quản lý thủ công. Nếu tar cả `release-{fms,crm}/` thì extract sẽ ghi đè → service fail do thiếu/sai config.

**Prerequisite trước deploy đầu tiên:** scp thủ công `env.sh` lên server vào `/home/datatp/release-{fms,crm}/server-env/env.sh`.

## Issues gặp phải khi test E2E

| # | Lỗi | Root cause | Fix |
|---|---|---|---|
| 1 | `has_actions: False` | Actions chưa bật trong repo settings | User bật qua UI |
| 2 | `403 User permission denied` khi checkout of1-core | `FORGEJO_TOKEN` scope/owner sai | User update token có quyền org `of1-platform` |
| 3 | `gradle: command not found` | Runner không tự có gradle trên PATH | Thêm `/opt/gradle/bin` vào `PATH` env workflow |
| 4 | `Could not get unknown property 'slf4jVersion'` khi build of1-core/of1-platform | Các sub-project không đọc `gradle.properties` của of1-fms | Copy file vào `~/.gradle/gradle.properties` (user-level) |
| 5 | `find: 'release-fms': No such file` khi deploy | `tools.sh build -code -ui` không tạo đầy đủ cấu trúc package | Chuyển sang tar chỉ `server/` |
| 6 | `instances.sh: env.sh: No such file or directory` | Tar cũ không có `env.sh`, extract ghi đè folder cũ | scp `env.sh` thủ công + chỉ tar `server/` (không động `server-env/`) |
| 7 | `dev.env` có `ENV_NAME="prod"` | User paste nhầm nội dung prod sang dev | Sửa `ENV_NAME="dev"` |

## Tối ưu đã áp dụng

- **Cache** Gradle + pnpm qua `actions/cache@v4`
- **DRY** — bỏ ~18 dòng `ORG_GRADLE_PROJECT_*` duplicate; version tập trung ở `gradle.properties`
- **Cleanup tar** sau deploy — xóa cả local + remote
- **Deploy scope hẹp** — chỉ `server/`, không đụng `server-env/`

## of1-build — `-nexus` option

Port từ branch `egov` vào `develop`:
- `./tools.sh build -nexus` sau build thường sẽ publish:
  - JAR `of1-core`, `of1-platform` lên Nexus Maven
  - npm `@of1-webui/lib`, `@of1-webui/platform` lên Nexus npm (`http://nexus.of1-dev-egov.svc.cluster.local/repository/npm-hosted/`)
- Các project khác (tms, crm, fms) chưa enable trong develop — có thể uncomment trong `tools.sh` khi cần

## Documentation updated

- `of1-fms/docs/ai/devops-rules.md` — thêm section "CI/CD Pipeline"
- `of1-crm/docs/ai/devops-rules.md` — thêm section "CI/CD Pipeline"
- `of1-build/docs/ai/devops-rules.md` — tạo mới, document `-nexus` option

## TODO

- [ ] Rotate `FORGEJO_TOKEN` đã lộ trong chat
- [ ] Bật Actions + add secrets cho `of1-crm`
- [ ] scp `env.sh` thủ công lên server prod fms + dev/prod crm
- [ ] Update `dev.env`/`prod.env` của crm với host/password thật
- [ ] Test E2E merge `develop → release` cho crm
