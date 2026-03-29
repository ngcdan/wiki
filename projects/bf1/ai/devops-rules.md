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
# Full Build: Backend + Package Release
./tools.sh build -clean -code

# Build with profile
./tools.sh build -clean -code --profile=dev
./tools.sh build -clean -code --profile=beta
./tools.sh build -clean -code --profile=prod
```

```bash
# Run FMS server
cd working/release-fms/server-env
./instance.sh run
```

- Check FMS BE: `http://localhost:7084`
- **Open Web**: `http://localhost:8080`

## 4. Local Debugging Notes
- When running locally, you must open `http://localhost:7080` first.
- After `7080` is up and has finished loading, you can then open `http://localhost:8080`.
