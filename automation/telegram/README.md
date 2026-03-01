# Telegram automation — get group chat_id

Mục tiêu: lấy **Telegram group chat_id** để cấu hình routing/bindings/crons.

## Cách dùng (Bot API)

1) Chuẩn bị bot token (từ BotFather)

2) Add bot vào group cần lấy id

3) Gửi 1 tin nhắn bất kỳ trong group (để bot nhận update)

4) Chạy script:

```bash
cd /Users/nqcdan/dev/wiki/automation/telegram
export TELEGRAM_BOT_TOKEN='123:abc...'
python3 get_group_chat_id.py
```

Nếu gặp lỗi **409 Conflict** (do bot đang set webhook), chạy:

```bash
python3 get_group_chat_id.py --delete-webhook
```
Rồi chạy lại `get_group_chat_id.py`.

Tuỳ chọn:
- Lấy nhiều update hơn:
  ```bash
  python3 get_group_chat_id.py --tail 500
  ```
- Filter theo title:
  ```bash
  python3 get_group_chat_id.py --title "OF1"
  ```

Output mẫu:

```
type    title           username   chat_id
supergroup  My Group              -1001234567890
```

## Notes
- Group chat_id thường là số âm; supergroup thường dạng `-100...`.
- Không hardcode token trong repo; dùng env var `TELEGRAM_BOT_TOKEN`.
