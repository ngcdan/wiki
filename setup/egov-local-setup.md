# Local Setup

First-time setup guide. For daily build commands, see [testing.md](./testing.md).

## Step 0: Git & SSH Access (Egov Project)

Because EGOV projects require access via a specific account (e.g., `hieuht2910`), you must configure Git and SSH locally to use the correct SSH key instead of your default one.

### 1. SSH Key & Config Setup
Ensure you have the private key (e.g., `~/.ssh/id_rsa_hieuht`). Check the SSH connection explicitly:
```bash
ssh -T -i ~/.ssh/id_rsa_hieuht -p 52222 git@git.datatp.cloud
```
*Expected output: `Hi there, hieuht2910! You've successfully authenticated...`*

### 2. Configure Local Repo to use the Key
Inside the `of1-egov` repository (or any egov repo), override the `core.sshCommand` to force using the specific key:
```bash
cd /path/to/of1-egov-repo
git config --local core.sshCommand "ssh -i ~/.ssh/id_rsa_hieuht"
```

### 3. Setup Git User & Email
Create a specific `.gitconfig` for the egov profile (e.g., `~/.gitconfig-egov-hieu`):
```ini
[user]
  name = hieuht2901
  email = hieuht2910@gmail.com
```

Then, include this config locally in your egov repos:
```bash
git config --local include.path ~/.gitconfig-egov-hieu
```

Verify your setup:
```bash
git config user.email
# Should return hieuht2910@gmail.com
```

---

## Prerequisites

- Java 21, Gradle 8.5, Node.js 20, pnpm
- PostgreSQL client (psql)
- Git Bash (Windows)

## Project Structure

```
forgejo/
├── of1-build          # Build scripts, phoenix host app
├── of1-core           # Base framework
├── of1-platform       # ERP platform
├── of1-crm            # CRM module
├── of1-document       # Document module
├── of1-tms            # TMS module
├── of1-egov           # Customs module (our target)
└── working/           # Release output
```

**Build order:** of1-core → of1-platform → of1-document, of1-tms, of1-crm → of1-egov

## Step 1: Setup Gradle Properties

Create `~/.gradle/gradle.properties`:

```properties
org.gradle.daemon=true

prodReleaseDir=C:/Users/ADMIN/Documents/projects/forgejo/working/release-prod
baseReleaseDir=C:/Users/ADMIN/Documents/projects/forgejo/working

ahaysoftUsername=automation
ahaysoftPassword=Auto!@#

#Lib Versions
slf4jVersion             = 2.0.12
log4jVersion             = 2.23.1
jacksonVersion           = 2.17.0
springfoxVersion         = 3.0.0
springBootVersion        = 3.3.3
springFrameworkVersion   = 6.2.0
springSecurityVersion    = 6.3.3
springIntegrationVersion = 6.3.3
springDataVersion        = 3.2.4
springDataJpaVersion     = 3.2.4
springBatchVersion       = 5.1.1
hibernateVersion          = 6.4.4.Final
hibernateValidatorVersion = 7.0.5.Final
jettyVersion             = 12.0.15
dataTPCore               = 1.0.0
dataTPErpVersion         = 1.0.0
```

## Step 2: Checkout to Egov Branch

```bash
cd of1-build
./git.sh status           # Check status
./git.sh working:env      # Checkout to 'egov' branch
```

## Step 3: Build Platform

```bash
cd of1-build
./tools.sh build -code -ui
```

### Clean Document Addon Libs (IMPORTANT - after every platform build)

Delete ALL files in `working/release-platform/server/addons/document/lib/` **EXCEPT** `of1-document-document-1.0.0.jar`. Duplicate libs cause classpath conflicts.

```bash
cd working/release-platform/server/addons/document/lib
ls | grep -v "of1-document-document-1.0.0.jar" | xargs rm -f
```

### Verify

These folders must exist:
- `working/release-platform/server-env/`
- `working/release-platform/server/`

## Step 4: Setup Platform Server Environment

Copy to `working/release-platform/server-env/`:

**a) `env.sh`:**
```bash
#!/usr/bin/env bash

window=false
bin=`dirname "$0"`
if [ "$OSTYPE" = "msys" ] ; then window=true;
elif [[ "$OSTYPE" == "cygwin" ]]; then window=true;
elif [[ "$OSTYPE" == "win32" ]]; then window=true;
elif [[ "$OSTYPE" == "darwin20.0" ]]; then window=true;
fi

SERVER_ENV_DIR=`cd "$bin"; pwd`
BASE_DIR="$SERVER_ENV_DIR/.."
ROOT_DIR="$BASE_DIR"
RELEASE_DIR="$BASE_DIR"
echo "BASE_DIR = $BASE_DIR"
if $window; then
  RELEASE_DIR=`cygpath --absolute --windows "$RELEASE_DIR"`
fi

SERVER_ENV="prod"
SERVER_JAVA_OPTS="-Xmx2048m"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.datasource.server.host=postgres.of1-dev-egov.svc.cluster.local"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.datasource.server.port=5432"
export SERVER_JAVA_OPTS
```

**b) Copy `config/` folder** (application properties files)

## Step 5: Run Platform

```bash
cd working/release-platform/server-env
./instances.sh run
```

Platform runs at http://localhost:7080

## Step 6: Build Egov

```bash
cd of1-egov
./tools.sh build -code -ui
```

### Verify

- `working/release-egov/server-env/`
- `working/release-egov/server/`

## Step 7: Setup Egov Server Environment

Copy to `working/release-egov/server-env/`:

**a) `env.sh`** — same as platform's

**b) `config/` folder**

**c) Change port** in `config/application-prod.yaml`:
```yaml
server:
  port: 7082
```

### Database Connection

Configured in TWO places (env.sh takes precedence):

**env.sh** (JVM args):
```bash
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.datasource.server.host=java-server.of1-dev-egov.svc.cluster.local"
SERVER_JAVA_OPTS="$SERVER_JAVA_OPTS -Dspring.datasource.server.port=5432"
```

**application-prod.yaml:**
```yaml
spring:
  datasource:
    jdbc:
      jdbcUrl: jdbc:postgresql://${spring.datasource.server.host}:${spring.datasource.server.port}/egov-dev-full-12
      username: postgres
      password: postgres
```

## Step 8: Run Egov

```bash
# Backend
cd working/release-egov/server-env
./instances.sh run

# Frontend dev server (REQUIRED for EGov menu in "My Apps")
cd of1-egov/webui/egov
pnpm run dev-server
```

EGov BE at http://localhost:7082, FE dev server at http://localhost:3002
