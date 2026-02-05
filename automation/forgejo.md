# Forgejo PR Management Solution

## Yêu cầu
Tôi là leader team dev, tôi muốn quản lý các công việc của team thông qua pull request của họ.

Tôi muốn có tool, hook để thu thập và tự động tổng hợp thông tin title, description pull request của họ về file markdown ở local hoặc tương tự vậy.

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
- File `team_prs_summary.md` sẽ chứa tổng hợp tất cả PRs
- Bao gồm: title, description, author, status, labels, links

---

### Phương án 2: Webhook Real-time

**Ưu điểm:**
- Cập nhật ngay lập tức khi có PR mới
- Không cần chạy định kỳ

**Nhược điểm:**
- Cần server/service luôn chạy
- Phức tạp hơn để setup

**Cách triển khai:**

1. **Tạo webhook server đơn giản:**
   ```python
   # webhook_server.py
   from flask import Flask, request
   import json
   from datetime import datetime

   app = Flask(__name__)

   @app.route('/webhook', methods=['POST'])
   def webhook():
       data = request.json

       if 'pull_request' in data:
           pr = data['pull_request']
           action = data['action']

           # Append to markdown file
           with open('team_prs_live.md', 'a', encoding='utf-8') as f:
               f.write(f"\n## [{action.upper()}] PR #{pr['number']}: {pr['title']}\n")
               f.write(f"- **Author:** @{pr['user']['login']}\n")
               f.write(f"- **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
               f.write(f"- **Link:** {pr['html_url']}\n")
               if pr.get('body'):
                   f.write(f"- **Description:** {pr['body'][:200]}...\n")
               f.write("\n")

       return {'status': 'ok'}

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```

2. **Cấu hình webhook trên Forgejo:**
   - Vào Settings → Webhooks → Add Webhook
   - URL: `http://your-server:5000/webhook`
   - Trigger events: Pull Requests
   - Content type: `application/json`

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

### 2. Áp dụng Conventions cho Team:
1. **Đọc và review conventions:**
   - Mở file [PR_CONVENTIONS.md](PR_CONVENTIONS.md)
   - Review format và examples
   - Điều chỉnh nếu cần

2. **Truyền thông với team:**
   - Share file `PR_CONVENTIONS.md` với team
   - Tổ chức meeting giải thích conventions
   - Trả lời questions từ dev

3. **Bắt đầu áp dụng:**
   - PRs mới phải follow conventions
   - Review PRs cũ và suggest improvements
   - Update dần theo format mới

4. **Track features lớn:**
   - Copy `FEATURE_TRACKING_TEMPLATE.md` cho mỗi feature
   - Assign Feature IDs (CRM-001, CRM-002, ...)
   - Update progress thường xuyên

