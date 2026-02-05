# Forgejo Webhook (Real-time) Runbook

> Mục tiêu: mỗi khi có Pull Request event ở repo `of1-crm/of1-crm`, Forgejo bắn webhook tới Mac mini → service update `work/OF1_Crm/BACKLOG.md` (giữa AUTO markers) → auto commit & push `main`.

## 0) Current status (2026-02-05)

✅ **Mac mini webhook service đã chạy OK** (launchd), healthcheck OK.

❌ **Forgejo delivery đang bị chặn** do policy:

> `webhook can only call allowed HTTP servers (check your webhook.ALLOWED_HOST_LIST setting)`

Forgejo đang chạy trên Kubernetes/Helm và user không control config → cần workaround.

---

## 1) Service overview

- Service code: `automation/forgejo_webhook_service.py`
- Endpoint:
  - `POST /webhook/forgejo`
  - `GET /health`
- Shared secret: `WEBHOOK_SECRET=nqcdan1908`
- Behavior on PR event:
  1) Call Forgejo API to fetch PR list (repo `of1-crm`)
  2) Update backlog file between markers:
     - `<!-- AUTO:FORGEJO_PRS_START -->`
     - `<!-- AUTO:FORGEJO_PRS_END -->`
  3) Auto `git commit` + `git push origin main` in the **repo that actually contains** `BACKLOG.md` (important due to symlinked `work/OF1_Crm`).

### Backlog file

- Logical path: `work/OF1_Crm/BACKLOG.md`
- Actual resolved path (symlink target):
  - `/Users/nqcdan/OF1/forgejo/of1-platform/wiki/OF1/Developer_Guides/Developers/OF1_Crm/BACKLOG.md`

---

## 2) Network addresses (Mac mini)

- Tailscale IPv4: `100.78.159.118`
- LAN IPv4: `192.168.0.199`

Health endpoints:
- `http://127.0.0.1:9009/health`
- `http://100.78.159.118:9009/health`

---

## 3) Install / update dependencies

```bash
cd /Users/nqcdan/dev/wiki/automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4) Run locally (manual)

```bash
cd /Users/nqcdan/dev/wiki/automation
source .venv/bin/activate
export WEBHOOK_SECRET='nqcdan1908'
uvicorn forgejo_webhook_service:app --host 0.0.0.0 --port 9009
```

Test:
```bash
curl http://127.0.0.1:9009/health
```

---

## 5) Run 24/7 via launchd (macOS)

Plist:
- `~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist`

Commands:
```bash
launchctl unload ~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist

curl http://127.0.0.1:9009/health
```

Logs:
```bash
tail -f /Users/nqcdan/dev/wiki/automation/forgejo-webhook.log
# errors (only appears if errors exist)
tail -f /Users/nqcdan/dev/wiki/automation/forgejo-webhook.err
```

---

## 6) Forgejo webhook configuration (UI)

Repo: `of1-crm/of1-crm` → Settings → Webhooks

- Target URL: `http://<IP>:9009/webhook/forgejo`
  - tried: `http://100.78.159.118:9009/webhook/forgejo` (Tailscale)
  - tried: `http://192.168.0.199:9009/webhook/forgejo` (LAN)
- Method: POST
- Content-Type: application/json
- Secret: `nqcdan1908`
- Events: Pull request events (Modification/Assignment/Reviews/Review requests...) ✅

### Current blocker

Forgejo blocks deliveries unless host is allowlisted:
- `webhook.ALLOWED_HOST_LIST` denies both LAN and Tailscale IPs.

---

## 7) Next steps / options to unblock delivery

### Option A (recommended): ask Forgejo admin to allowlist
Request to Forgejo admin (app.ini / config):

```ini
[webhook]
ALLOWED_HOST_LIST = 192.168.0.199:9009
# or tailscale
# ALLOWED_HOST_LIST = 100.78.159.118:9009
```

Restart Forgejo.

### Option B: expose a public HTTPS URL (tunnel)
Because Forgejo cannot call private IPs unless allowlisted, use a tunnel to obtain a public URL.

Candidates:
- Cloudflare Tunnel (preferred for long-running)
- ngrok (quick testing)

Flow:
- Tunnel → maps `https://<public>/` to `http://127.0.0.1:9009`
- Set Forgejo Target URL to: `https://<public>/webhook/forgejo`

Note: still protected by webhook secret.

### Option C: in-cluster relay
If you can deploy a small service in Kubernetes, receive webhook in-cluster (allowed), then forward to Mac mini.

---

## 8) Quick commands cheatsheet

```bash
# tailscale ip
/usr/local/bin/tailscale ip -4

# health
curl http://127.0.0.1:9009/health

# logs
tail -n 200 /Users/nqcdan/dev/wiki/automation/forgejo-webhook.log
```
