### navigate
cd /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server-env       # cd OF1 platform start
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-build                                 # cd OF1 root (build) project.
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile                    # cd OF1 mobile project.
cd /Users/nqcdan/OF1/forgejo/of1-platform/datatp-python && source venv/bin/activate # cd OF1 python
cd /Users/nqcdan/OF1/forgejo/of1-cloud/of1-cloud-dev/namespaces/of1/beta/platform   # cd OF1 beta namespace
cd /Users/nqcdan/OF1/forgejo/of1-cloud/of1-cloud-dev/namespaces/of1/dev/crm         # cd OF1 crm namespace

### open vs code workspace
code_ws ~/OF1/ws/mobile.code-workspace
code_ws ~/OF1/ws/crm.code-workspace
code_ws ~/OF1/ws/datatp-python.code-workspace

vi ~/dev/wiki/cheatsheets/cli.md                 # Edit cheatsheet

### Build code
./tools.sh build -clean -code -ui
gradle clean build --refresh-dependencies
gradle publishToMaven

### k8s, server, cloud
tar -xvf server.tar
<!-- Copy file local to remote server  -->
kns-ctl of1-prod-platform cp-to server.tar server:/home/datatp/release-platform
<!-- Lệnh copy from (từ remote server to local) -->
kns-ctl of1-beta-platform cp-from server:home/datatp/release-platform/server.tar ./server.tar
kns-ctl of1-prod-platform get services,pods
kns-ctl of1-dev-crm get services,pods
<!-- Sync prod to beta, dev image -->
./k-ctl.sh ns status
./k-ctl.sh admin undeploy
./k-ctl.sh admin sync-pv
./k-ctl.sh admin deploy
<!-- Vào máy chủ/ máy pod bằng command: pod name: python-msa, su - datatp: switch to datatp user -->
kns-ctl of1-prod-platform exec -it python-msa -- su - datatp
kns-ctl of1-prod-platform exec -it server -- su - datatp
kns-ctl of1-dev-crm exec -it server -- su - datatp

ssh of1@nginx-waf.of1-apps.svc.cluster.local  # nginx server (prod)
<!-- access prod platform server (datatp user) -->
ssh datatp@server.of1-prod-platform.svc.cluster.local # pass server@prod

<!-- Copy server.tar lên prod platform server (scp/rsync) -->
scp /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server.tar \
  datatp@server.of1-prod-platform.svc.cluster.local:/home/datatp/release-platform/

rsync -avh --progress \
  /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server.tar \
  datatp@server.of1-prod-platform.svc.cluster.local:/home/datatp/release-platform/

# Check file trên server
ssh datatp@server.of1-prod-platform.svc.cluster.local "ls -lh /home/datatp/release-platform/server.tar"

### Git
git config user.name "nqcdan" && git config user.email "linuss1908@gmail.com"                   # github mail config
git config -g user.name "jesse.vnhph" && git config -g user.email "jesse.vnhph@openfreightone"  # config forgejo

./git.sh working:set crm            # switch branch crm
./git.sh working:set develop        # switch branch develop
./git.sh working:merge crm          # merge crm to current branch
./git.sh status && ./git.sh working:commit "update code" && ./git.sh working:push              # git commit

git config --global pull.ff only
git config --global core.autocrlf input    # Line ending (multi OS)

### Mobile - Flutter
flutter doctor
flutter clean && flutter pub get
flutter build apk --release         # mobile android apk
flutter build appbundle --release   # mobile android bundle
flutter build ios --release         # mobile ios release

### Cách clone database trên cloud.
<!-- 1. Vào máy postgres trên cloud bằng command **kns-ctl** *of1-dev-crm*: thay tên config tương ứng với từng cụm máy (beta, dev, crm, tms, …) -->
kns-ctl of1-dev-crm exec -it postgres -- su - datatp
<!-- 2. Vào server postgres bằng command **psql**.  Note: có thể chạy lệnh \list hoặc \l trước và sau để kiểm tra.  -->
psql -U datatp-crm datatp_crm_db;
CREATE DATABASE new_datatp_crm_db TEMPLATE datatp_crm_db;

### CDC + Postgres

PGPASSWORD="postgres" psql -h "postgres.of1-dev-crm.svc.cluster.local" -p "5432" -U "postgres" -d "datatp_crm_db"
show wal_level;
ALTER SYSTEM SET wal_level=logical;
select pg_reload_conf(); # show t

SELECT count(*) FROM pg_replication_slots WHERE slot_name = 'debezium_slot';
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');

kns-ctl of1-dev-crm exec -it postgres -- su - datatp

### tmux
# Show current tmux session name (run inside tmux)
tmux display-message -p '#S'

# Show full info: session/window/pane (run inside tmux)
tmux display-message -p 'session=#S window=#I:#W pane=#P'

# List all tmux sessions
tmux ls

