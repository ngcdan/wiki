# Build & Release Updates — 2026-05-06

## 1. BFSOne API: Fix dynamic ToDate

**Repo:** of1-crm

- `BFSOneApi.java` — Thay hardcoded `"20260301"` bang `DateUtil.asCompactDateId(new Date())` (format `yyyyMMdd`)
- `BFSOneCRMLogic.java` — Them log error thay vi swallow exception + log so luong records tra ve
- Them log authentication success/failure trong `BFSOneApi.authenticate()`

## 2. Nexus Registry Migration

**Repo:** of1-crm, of1-fms, of1-egov

### Maven (Java JARs)

- `build.gradle` — Them nexus vao `repositories` block:
  ```groovy
  maven {
    url "${nexusUrl}/repository/maven-public/"
    allowInsecureProtocol = true
  }
  ```
- `build.gradle` — Chuyen `publishing.repositories` tu ahaysoft (`nexus.dev.datatp.net`) sang OF1 nexus (`${nexusUrl}/repository/maven-releases/`)
- `NEXUS_PASSWORD` secret da update tren Forgejo cho ca 3 repo

### npm (WebUI packages)

- `webui/crm/package.json` — Chuyen `@of1-webui/lib` va `@of1-webui/platform` tu `file:` sang version `"1.0.0"` (resolve tu Nexus npm)
- Them `publishConfig.registry` tro vao Nexus npm-hosted
- Them `pnpm.overrides` de force resolve `@of1-webui/lib: "1.0.0"` (workaround cho platform package van chua `file:` reference)

### of1-egov Pipeline Refactor

- Chuyen hardcoded version pins tu pipeline YAML sang `gradle.properties` (giong CRM/FMS)
- Them step `Install shared gradle.properties` trong ca `deploy.yaml` va `test.yaml`
- Fix: `test.yaml` truoc do dung versions cu hon `deploy.yaml` — gio ca 2 dung chung `gradle.properties`

## 3. LOCAL_LIBS Webpack Alias

**Repo:** of1-crm, of1-fms

- `webpack.config.ts` — Them `resolve.alias` khi `LOCAL_LIBS=true`:
  ```
  @of1-webui/lib     → ../../../of1-core/webui/lib
  @of1-webui/platform → ../../../of1-platform/webui/platform
  ```
- Dev local: `LOCAL_LIBS=true pnpm dev-watch`
- Build/CI: `pnpm build` (binh thuong, lay tu Nexus)
- Khong thay doi `package.json` — khong so commit nham

## 4. Publish Script Fix

**Repo:** of1-build

- `tools.sh` — Khi publish `@of1-webui/platform` len Nexus, tu dong swap `file:../../../of1-core/webui/lib` thanh `"1.0.0"` truoc `pnpm publish`, revert sau
- Dam bao consumer (CRM, FMS) install khong gap loi `file:` reference

## 5. Server Script Fixes

### Fix cygpath bug (of1-core)

- `env-sample.sh` — Bo window detection sai (`darwin20.0` bi nhan la Windows) va `cygpath --absolute --windows` convert lam hong path tren Git Bash
- Root cause: `cygpath` tao `C:\Users\...` mix voi Unix `/server/bin/server.sh` → path khong hop le

### CRM tools.sh

- Bo `of1-platform` khoi build steps — Java JARs va npm packages da co tren Nexus, khong can clone of1-platform repo
- Build chi can: `of1-core/` (build scripts + release) + `of1-crm/`

## Tong ket Dependency Flow

```
of1-core   → publish → Nexus Maven (JARs) + Nexus npm (@of1-webui/lib)
of1-platform → publish → Nexus Maven (JARs) + Nexus npm (@of1-webui/platform)

of1-crm    → download tu Nexus (standalone, chi can of1-core repo cho build scripts + release)
of1-fms    → download tu Nexus (tuong tu)
of1-egov   → download tu Nexus (tuong tu)
```
