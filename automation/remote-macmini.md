# Remote Mac mini Setup Guide (Tailscale + Screen Sharing + VS Code)

Hướng dẫn thiết lập môi trường Remote Development từ MacBook M1 về Mac mini M4 đặt tại công ty.
Mục tiêu: **Ổn định - Bảo mật - Hiệu năng cao**.

## 1. Chuẩn bị (Prerequisites)
| Thiết bị | Vai trò | Yêu cầu |
| :--- | :--- | :--- |
| **Mac mini M4** | **Host** (Máy Remote) | macOS mới nhất, quyền Admin, cắm LAN (ưu tiên) hoặc Wi-Fi ổn định. Khuyên dùng UPS. |
| **MacBook M1** | **Client** (Máy làm việc) | Đã cài Tailscale. |

- **Tài khoản Tailnet**: `linuss1908@` (Dùng chung cho cả 2 máy).
- **User máy Mac mini**: `nqcdan`.
- **IP Tailscale Mac mini**: `100.78.159.118` (IP tĩnh trong mạng Tailscale).
- **Hostname**: `mac-mini` (hoặc `mac-mini.ts.net`).

---

## 2. Thiết lập Network (Tailscale)
Thực hiện trên **cả hai máy** để tạo mạng LAN ảo kết nối trực tiếp.

### 2.1 Cài đặt & Đăng nhập
1. **Cài đặt**:
   ```bash
   brew install --cask tailscale
   ```
2. **Đăng nhập**: Mở app Tailscale, log in bằng tài khoản `linuss1908@`.
3. **Cấu hình trên Mac mini**:
   - Đặt tên máy là `mac-mini`.
   - **Quan trọng**: Vào Settings của Tailscale, bật **"Start at Login"**.

### 2.2 Bật MagicDNS (Khuyên dùng)
Giúp truy cập bằng tên (`mac-mini`) thay vì nhớ IP.
1. Truy cập [Tailscale Admin Console](https://login.tailscale.com/admin/dns).
2. Vào mục **DNS** > Bật **MagicDNS**.
3. Kiểm tra từ MacBook:
   ```bash
   # Nếu ping thấy phản hồi là OK
   tailscale ping mac-mini
   ```

---

## 3. Cấu hình Máy Host (Mac mini)
Thực hiện trên Mac mini để cho phép điều khiển từ xa và ngăn máy ngủ.

### 3.1 Bật Remote Access (Screen Sharing & SSH)
Vào **System Settings > General > Sharing**:

1.  **Screen Sharing** (Điều khiển GUI):
    *   Gạt sang **ON**.
    *   Bấm vào chữ **(i)** bên cạnh.
    *   Mục "Allow access for": Chọn "Only these users" và thêm user `nqcdan`.
    *   *(Tắt "Anyone may request permission to control screen" để tránh pop-up phiền phức)*.

2.  **Remote Login** (SSH):
    *   Gạt sang **ON**.
    *   Mục "Allow access for": Chọn "Only these users" và thêm user `nqcdan`.

### 3.2 Cấu hình Năng lượng (Power Management)
Đảm bảo máy luôn chạy kể cả khi không dùng.

1.  **Cài đặt GUI**:
    *   **System Settings > Displays > Advanced**: Bật "Prevent automatic sleeping on power adapter when the display is off".
    *   **Energy**: Bật "Wake for network access".

2.  **Cài đặt Terminal (Mạnh hơn)**:
    ```bash
    # Máy không bao giờ ngủ, màn hình tắt sau 10 phút
    sudo pmset -a sleep 0 displaysleep 10

    # Bật Wake-on-LAN (đánh thức qua mạng)
    sudo pmset -a womp 1
    ```

3.  **Lưu ý về FileVault**:
    *   Nếu bật FileVault: Khi khởi động lại, máy chưa vào mạng cho đến khi có người nhập mật khẩu trực tiếp.
    *   **Khắc phục**: Không tắt máy, chỉ sleep màn hình. Nếu mất điện phải có người bật lại tại chỗ.

---

## 4. Hướng dẫn Kết nối từ MacBook

### 4.1 Remote Desktop (Screen Sharing)
Dùng khi cần thao tác giao diện (Cài app, chỉnh setting hệ thống).

*   **Cách 1 (Nhanh nhất nếu có MagicDNS)**:
    *   Mở Spotlight (`Cmd + Space`).
    *   Gõ: `screensharing://mac-mini.ts.net` và Enter.
*   **Cách 2 (Qua IP)**:
    *   Mở Terminal hoặc Spotlight.
    *   Gõ: `open vnc://100.78.159.118`

### 4.2 VS Code Remote SSH (Code hàng ngày)
Dùng để code, build, chạy lệnh. Nhanh và mượt hơn Screen Sharing rất nhiều.

1.  Cài Extension **Remote - SSH** trên VS Code MacBook.
2.  Thêm config vào file `~/.ssh/config` trên MacBook:
    ```ssh
    Host mac-mini
        HostName 100.78.159.118   # Hoặc mac-mini.ts.net nếu MagicDNS ổn định
        User nqcdan
        IdentityFile ~/.ssh/id_ed25519
        ServerAliveInterval 30
        ServerAliveCountMax 120
    ```
3.  Kết nối:
    *   Mở VS Code.
    *   Bấm vào biểu tượng **><** (xanh lá góc trái dưới) hoặc `Cmd + Shift + P`.
    *   Chọn **Remote-SSH: Connect to Host...** -> Chọn `mac-mini`.

---

## 5. Bảo mật & Tailscale ACLs (Nâng cao)
Giới hạn quyền truy cập để an toàn hơn (chỉ MacBook của bạn mới vào được).

Vào [Tailscale Access Controls](https://login.tailscale.com/admin/acls/file) và cấu hình JSON:

```json
{
  "groups": {
    "group:dev": ["linuss1908@"]
  },
  "hosts": {
    "mac-mini": "100.78.159.118"
  },
  "acls": [
    // Cho phép thiết bị cá nhân truy cập SSH và Screen Sharing (port 5900) vào Mac mini
    {
      "action": "accept",
      "src": ["linuss1908@"],
      "dst": ["mac-mini:22,5900"]
    }
  ],
  "ssh": [
    {
      "action": "accept",
      "src": ["linuss1908@"],
      "dst": ["mac-mini"],
      "users": ["nqcdan"]
    }
  ]
}
```

---

## 6. Khắc phục sự cố (Troubleshooting)

| Vấn đề | Kiểm tra & Khắc phục |
| :--- | :--- |
| **Không ping được `mac-mini`** | 1. Kiểm tra Tailscale trên cả 2 máy đã bật chưa (`tailscale status`). <br> 2. Thử ping bằng IP: `tailscale ping 100.78.159.118`. |
| **Không kết nối được Screen Sharing** | 1. Trên Mac mini, chạy: `sudo lsof -i :5900` xem port có mở không. <br> 2. Vào System Settings tắt đi bật lại Screen Sharing. |
| **VS Code bị đứt kết nối** | Kiểm tra đường truyền internet. Thử `kill` VS Code Server trên Mac mini: <br> `ssh mac-mini "rm -rf .vscode-server"` (sẽ phải cài lại extension remote). |
| **Máy Mac mini offline** | Có thể máy đã bị tắt nguồn hoặc rớt mạng. Cần kiểm tra trực tiếp. |

---

## 7. Các lệnh thường dùng

```bash
# ----- Trên MacBook -----
# Kiểm tra kết nối
tailscale ping mac-mini

# SSH nhanh vào terminal
ssh mac-mini

# Mở GUI remote
open vnc://100.78.159.118

# ----- Trên Mac mini (Debug) -----
# Kiểm tra log Screen Sharing
log show --predicate 'process == "screensharingd"' --last 5m
```
