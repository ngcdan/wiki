# Hướng dẫn Setup & Bảo mật moltbot (Clawdbot) 24/7 trên Mac mini

## 1. Mục tiêu
- Chạy moltbot (Clawdbot) 24/7 trên Mac mini, tách biệt hoàn toàn với các user khác.
- Đảm bảo chỉ bạn có quyền điều khiển, không lộ API key, hạn chế tối đa rủi ro bảo mật.

#### Node cho OpenClaw daemon (khuyến nghị)
NÊN: cài Node LTS bằng Homebrew
KHÔNG NÊN: dùng Node qua nvm / fnm / asdf cho daemon
Vì sao dùng brew node?
LaunchAgent (daemon macOS) không load .zshrc → không thấy nvm
Node trong nvm nằm ở ~/.nvm/... → dễ gãy khi upgrade / xoá version
Brew node nằm ở đường dẫn cố định (/opt/homebrew/bin/node)
OpenClaw daemon chạy ổn định 24/7

```
openclaw gateway install
openclaw gateway start
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```


## 2. Cơ chế isolate & bảo mật
### 2.1. Isolate môi trường
- **Tạo user riêng biệt** (ví dụ: `clawdbot`) chỉ dùng để chạy moltbot, không cấp quyền admin, không dùng chung với các tác vụ khác.
- **Virtualenv riêng**: Mỗi user có home, môi trường Python, package, biến môi trường tách biệt hoàn toàn.
- **Không cấp quyền sudo** cho user này, không thể truy cập file hệ thống hoặc user khác.
- **Chạy moltbot dưới user clawdbot**: Nếu moltbot bị tấn công, kẻ tấn công chỉ kiểm soát user này, không ảnh hưởng hệ thống chính.

### 2.2. Bảo mật truy cập
- **Chỉ cho phép SSH từ MacBook của bạn** (xem cấu hình Tailscale ACLs trong remote-macmini.md).
- **Không chia sẻ API key**: Lưu key trong file `.env` chỉ user clawdbot đọc được (`chmod 600 .env`).
- **Giới hạn network** (nâng cao): Dùng firewall (pf, Little Snitch) chỉ cho phép user này truy cập outbound đến domain cần thiết (OpenAI, GitHub).
- **Không mở port public**: Chỉ truy cập qua Tailscale, không NAT, không expose port ra internet.
- **Cập nhật hệ điều hành và package thường xuyên**.

---

## 3. Các bước setup moltbot 24/7 (chi tiết)

### Bước 1: Tạo user isolate
```bash
sudo sysadminctl -addUser clawdbot -fullName "Clawdbot Service" -password "mật_khẩu_mạnh"
# Không cấp quyền admin, không thêm vào sudoers
```

### Bước 2: Đăng nhập user, tạo môi trường Python riêng
```bash
su - clawdbot
python3 -m venv moltbot-env
source moltbot-env/bin/activate
```

### Bước 3: Clone moltbot và cài đặt
```bash
git clone https://github.com/clawdbot/moltbot.git
cd moltbot
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4: Cấu hình API key và biến môi trường
```bash
cp .env.example .env
nano .env
# Thêm OPENAI_API_KEY=sk-xxxxxx
chmod 600 .env
```

### Bước 5: Tạo script khởi động
```bash
echo '#!/bin/bash\ncd ~/moltbot\nsource ~/moltbot-env/bin/activate\npython main.py' > ~/moltbot/start.sh
chmod +x ~/moltbot/start.sh
```

### Bước 6: Thiết lập launchd để chạy 24/7
Tạo file: `/Users/clawdbot/Library/LaunchAgents/com.moltbot.service.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.moltbot.service</string>
	<key>ProgramArguments</key>
	<array>
		<string>/Users/clawdbot/moltbot/start.sh</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>KeepAlive</key>
	<true/>
	<key>StandardOutPath</key>
	<string>/Users/clawdbot/moltbot/moltbot.log</string>
	<key>StandardErrorPath</key>
	<string>/Users/clawdbot/moltbot/moltbot.err</string>
</dict>
</plist>
```
Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.moltbot.service.plist
```

---

## 4. Theo dõi & quản lý
- Xem log: `tail -f ~/moltbot/moltbot.log`
- Restart: `launchctl unload ~/Library/LaunchAgents/com.moltbot.service.plist && launchctl load ~/Library/LaunchAgents/com.moltbot.service.plist`
- Đảm bảo service tự động restart khi lỗi.

---

## 5. Checklist bảo mật cuối cùng
- [x] User riêng biệt, không quyền admin
- [x] Không chia sẻ API key, file .env chỉ user đọc
- [x] Chỉ cho phép SSH từ thiết bị tin cậy (Tailscale ACL)
- [x] Không expose port ra internet
- [x] Cập nhật hệ điều hành, package định kỳ
- [x] (Nâng cao) Giới hạn network outbound của user moltbot

---

## 6. Tham khảo thêm
- [remote-macmini.md](remote-macmini.md) – Hướng dẫn cấu hình Tailscale, SSH, Screen Sharing, ACLs
- [Tailscale ACLs docs](https://tailscale.com/kb/1018/acls/)
- [macOS launchd docs](https://www.launchd.info/)
