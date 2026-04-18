cd /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server-env       # cd OF1 platform start
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-build                                 # cd OF1 root (build) project.
cd /Users/nqcdan/OF1/forgejo/of1-platform/of1-mobile/apps/mobile                    # cd OF1 mobile project.
cd /Users/nqcdan/OF1/forgejo/of1-platform/datatp-python && source venv/bin/activate # cd OF1 python
cd /Users/nqcdan/OF1/forgejo/of1-cloud/of1-cloud-dev/namespaces/of1/beta/platform   # cd OF1 beta namespace
cd /Users/nqcdan/OF1/forgejo/of1-cloud/of1-cloud-dev/namespaces/of1/dev/crm         # cd OF1 crm namespace

code_ws ~/OF1/ws/mobile.code-workspace
code_ws ~/OF1/ws/crm.code-workspace
code_ws ~/OF1/ws/datatp-python.code-workspace

vi ~/dev/wiki/cheatsheets/cli.md                 # Edit cheatsheet

./tools.sh build -clean -code -ui
gradle clean build --refresh-dependencies
gradle publishToMaven

### k8s, server, cloud
tar -xvf server.tar
kns-ctl of1-prod-platform cp-to server.tar server:/home/datatp/release-platform
kns-ctl of1-beta-platform cp-from server:home/datatp/release-platform/server.tar ./server.tar
kns-ctl of1-prod-platform get services,pods
kns-ctl of1-dev-crm get services,pods

./k-ctl.sh ns status
./k-ctl.sh admin undeploy
./k-ctl.sh admin sync-pv
./k-ctl.sh admin deploy

kns-ctl of1-prod-platform exec -it python-msa -- su - datatp
kns-ctl of1-prod-platform exec -it server -- su - datatp
kns-ctl of1-dev-crm exec -it server -- su - datatp

ssh of1@nginx-waf.of1-apps.svc.cluster.local  # nginx server (prod)
ssh datatp@server.of1-prod-platform.svc.cluster.local       #server@prod
ssh datatp@crm-server.of1-prod-platform.svc.cluster.local   #crm@prod

scp /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server.tar datatp@server.of1-prod-platform.svc.cluster.local:/home/datatp/release-platform/

rsync -avh --progress /Users/nqcdan/OF1/forgejo/of1-platform/working/release-platform/server.tar datatp@server.of1-prod-platform.svc.cluster.local:/home/datatp/release-platform/

ssh datatp@server.of1-prod-platform.svc.cluster.local "ls -lh /home/datatp/release-platform/server.tar"


git config user.name "nqcdan" && git config user.email "linuss1908@gmail.com"                   # github mail config
git config -g user.name "jesse.vnhph" && git config -g user.email "jesse.vnhph@openfreightone"  # config forgejo

./git.sh working:set crm            # switch branch crm
./git.sh working:set develop        # switch branch develop
./git.sh working:merge crm          # merge crm to current branch
./git.sh status && ./git.sh working:commit "update code" && ./git.sh working:push              # git commit

git config --global pull.ff only
git config --global core.autocrlf input    # Line ending (multi OS)

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
# Manage Sessions (CLI)
tmux new -s <name>      # Create new session (e.g. tmux new -s backend)
tmux a -t <name>        # Attach to session (e.g. tmux a -t backend)
tmux a -t of1           # Attach to OF1 session
tmux a -t egov          # Attach to E-Gov session
tmux ls                 # List running sessions
tmux kill-session -t <name> # Kill a session

# Inside Tmux (Prefix = Ctrl+a)
# Ctrl+a d              # Detach (leave running in background)
# Ctrl+a s              # Switch session (interactive list)
# Ctrl+a $              # Rename session
# Ctrl+a c              # New window (tab)
# Ctrl+a ,              # Rename window
# Ctrl+a | / -          # Split vertical / horizontal
# Ctrl+a z              # Zoom pane (maximize/restore)

# Show current info
tmux display-message -p '#S'

### AI Agents / Coding CLI (Context & Files)

# Claude CLI - Attach Files
claude -f file.txt "explain this"       # Single file
claude -f a.js -f b.js "diff these"     # Multiple files
cat file.txt | claude "explain"         # Pipe stdin

# Codex CLI - Context
codex "Refactor utils.js"               # Auto-scans named files
cat config.json | codex "validate"      # Pipe stdin

# Heredoc / Multiline (Bash)
claude "Analyze:
$(cat error.log)"

http://k8s-prometheus-stack-grafana.monitoring.svc.cluster.local Username/pass = of1/Of1!!!
http://filestash.of1-dev-kafka.svc.cluster.local/files/

# SSH Authentication Check
ssh -T -i ~/.ssh/id_rsa_hieuht -p 52222 git@git.datatp.cloud # Test kết nối SSH đến Git server và in ra lời chào (kèm username) để xác nhận hệ thống đã nhận đúng key SSH.

### Git Merge & Status
- `git merge --autostash -X ours origin/crm`: Thực hiện merge từ nhánh khác vào nhánh hiện tại. Tự động cất (stash) các thay đổi đang làm dở, ưu tiên giữ code của nhánh hiện tại (`-X ours`) nếu xảy ra xung đột, sau đó tự động apply lại phần stash ban đầu.
- `git status --short`: Xem trạng thái working tree dạng rút gọn (dễ nhìn hơn status thường).
- `git log --oneline -1`: Xem commit gần nhất một cách ngắn gọn trên 1 dòng.

### SSH Authentication Check
- `ssh -T -i ~/.ssh/id_rsa_hieuht -p 52222 git@git.datatp.cloud`: Test kết nối SSH đến Git server và in ra lời chào (kèm username) để xác nhận hệ thống đã nhận đúng key SSH.




http://tools-server.of1-prod-platform.svc.cluster.local/admin

ssh -p 30222 clouddev@14.225.17.105       # Of1Clo!@#
ssh of1@nginx-waf.of1-apps.svc.cluster.local # of1/of1@

