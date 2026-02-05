# Forgejo PR Management Solution

## Yêu cầu
Tôi là leader team dev, tôi muốn quản lý các công việc của team thông qua pull request của họ.

Tôi muốn có tool, hook để thu thập và tự động tổng hợp thông tin title, description pull request của họ về file markdown ở local hoặc tương tự vậy.

Tool sẽ tự động gọi hook khi nhận được event tạo pull request.

Sau đó review title, để đảm bảo có prefix bắt đầu dạng
Closes #123 / Fixes #123 / Resolves #123 / Refs #123

Sau đó, check labels, projects, descriptions, assignee


---

## Giải pháp

### Phương án 1: Script định kỳ với Forgejo API ⭐ (Khuyên dùng)

**Ưu điểm:**
- Đơn giản, dễ triển khai
- Không cần server luôn chạy
- Kiểm soát được thời điểm cập nhật
- Phù hợp cho báo cáo hàng ngày/tuần

**Cách sử dụng:**

1. **Tạo Access Token trên Forgejo:**
   ```
   Settings → Applications → Generate New Token
   Chọn quyền: read:repository, read:organization
   ```

2. **Setup script:**
   ```bash
   cd /Users/nqcdan/dev/tools/setup/setup
   chmod +x setup_pr_collector.sh
   ./setup_pr_collector.sh
   ```

3. **Cấu hình (không hardcode token trong code):**

   Tạo file `.env` cạnh script (hoặc export env vars):

   ```bash
   # automation/.env (KHÔNG commit)
   FORGEJO_URL=http://forgejo.of1-apps.svc.cluster.local
   FORGEJO_TOKEN=xxx
   FORGEJO_OWNER=of1-crm
   FORGEJO_REPOS=of1-crm
   PR_STATE=all
   DAYS_BACK=30
   # OUTPUT_FILE=/path/to/team_prs_summary.md (optional)
   ```

4. **Chạy thủ công:**
   ```bash
   cd automation
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # chạy bằng env/.env
   python3 forgejo_pr_collector.py

   # hoặc override bằng CLI
   python3 forgejo_pr_collector.py --owner of1-crm --repos of1-crm --days-back 30
   ```

5. **Tự động hóa với cron (tùy chọn):**
   ```bash
   crontab -e
   # Chạy mỗi sáng 9h
   0 9 * * * cd /Users/nqcdan/dev/tools/setup/setup && ./venv/bin/python forgejo_pr_collector.py

   # Hoặc chạy mỗi 4 tiếng
   0 */4 * * * cd /Users/nqcdan/dev/tools/setup/setup && ./venv/bin/python forgejo_pr_collector.py
   ```

**Output:**
- Chỉ update file backlog (mặc định): `work/OF1_Crm/BACKLOG.md` sẽ được update *giữa 2 marker*:
  - `<!-- AUTO:FORGEJO_PRS_START -->`
  - `<!-- AUTO:FORGEJO_PRS_END -->`

Format backlog entry (auto):
```md
#### #284 [Enhancement] ...
> 1 dòng mô tả ngắn từ PR description

- **Link:** ...
- **Author:** @...
```

---

### Phương án 2: Webhook Real-time ⭐ (đang dùng)

**Ưu điểm:**
- Cập nhật ngay lập tức khi có PR mới
- Không cần chạy định kỳ

**Nhược điểm:**
- Cần server/service luôn chạy
- Phức tạp hơn để setup

**Cách triển khai:**

1. **Webhook service (FastAPI) đã có sẵn trong repo:**

   - File: `automation/forgejo_webhook_service.py`
   - Endpoint: `POST /webhook/forgejo`
   - Healthcheck: `GET /health`

2. **Cấu hình webhook trên Forgejo (repo `of1-crm/of1-crm`):**
   - Settings → Webhooks → Add Webhook
   - URL: `http://<macmini-ip>:9009/webhook/forgejo` (hoặc Tailscale IP)
   - Trigger events: **Pull Requests**
   - Content type: `application/json`
   - Secret: đặt giống `WEBHOOK_SECRET`

3. **Chạy local test:**
   ```bash
   cd automation
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-webhook.txt

   export WEBHOOK_SECRET='...'
   uvicorn forgejo_webhook_service:app --host 0.0.0.0 --port 9009
   ```

4. **Chạy 24/7 bằng launchd (macOS):**

   - Template plist: `automation/com.tommy.forgejo-webhook.plist`
   - Copy vào LaunchAgents và sửa `WEBHOOK_SECRET`:

   ```bash
   cp automation/com.tommy.forgejo-webhook.plist ~/Library/LaunchAgents/
   nano ~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist

   launchctl unload ~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist 2>/dev/null || true
   launchctl load ~/Library/LaunchAgents/com.tommy.forgejo-webhook.plist

   # logs
   tail -f /Users/nqcdan/dev/wiki/automation/forgejo-webhook.log
   tail -f /Users/nqcdan/dev/wiki/automation/forgejo-webhook.err
   ```

**Behavior:** mỗi event PR sẽ trigger sync và:
- update `work/OF1_Crm/BACKLOG.md` (giữa AUTO markers)
- auto `git commit` + `git push origin main`

---

## So sánh 2 phương án

| Tiêu chí | Script định kỳ | Webhook |
|----------|----------------|---------|
| Độ phức tạp | ⭐ Đơn giản | ⭐⭐⭐ Phức tạp |
| Real-time | ❌ Không | ✅ Có |
| Infrastructure | ✅ Không cần | ❌ Cần server |
| Báo cáo tổng hợp | ✅ Tốt | ⭐ Trung bình |
| Dễ maintenance | ✅ Dễ | ⭐ Khó hơn |

---

## Khuyến nghị

**Bắt đầu với Phương án 1** (Script định kỳ):
- Đơn giản, nhanh chóng triển khai
- Đủ cho hầu hết use case quản lý team
- Chạy sáng/chiều mỗi ngày là đủ
- Dễ customize và maintain

**Nâng cấp lên Phương án 2** khi:
- Cần theo dõi real-time
- Team lớn, nhiều PRs
- Cần tích hợp với hệ thống khác

---

## Files đã tạo

### Scripts & Tools:
- `forgejo_pr_collector.py`: Script chính thu thập PRs
- `requirements.txt`: Dependencies
- `setup_pr_collector.sh`: Script setup tự động

### Documentation & Conventions:
- `PR_CONVENTIONS.md`: ⭐ Quy ước đặt tên và format Pull Requests
- `FEATURE_TRACKING_TEMPLATE.md`: Template theo dõi features lớn

## Next Steps

### 1. Setup & Test Tool:
- [x] Chạy setup script
- [x] Cấu hình thông tin Forgejo
- [x] Test chạy thủ công thành công
- [ ] Setup cron job nếu muốn tự động hóa


