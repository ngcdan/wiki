# Macos

Update and upgrade
```
brew update && brew upgrade
```

# Nginx On Macos

Install nginx
```
brew install nginx
```

Change the default port 8080 to 80 or any other port

```
vi /opt/homebrew/etc/nginx/nginx.conf
# Search for 8080 and change to 80 or any other 80xx port
```

Start the nginx service

```
brew services start nginx
```

Stop the nginx service

```
brew services stop nginx
```

Check the nginx status

```
brew services info nginx
```

The nginx conf is located in /opt/homebrew/etc/nginx/servers

```
# Server Configuration
upstream platform-server {
  #server server.of1-beta-platform.svc.cluster.local;
  server 127.0.0.1:7080;
}

upstream document-server {
  server 127.0.0.1:7081;
}

upstream document-webui-server {
  server 127.0.0.1:3001;
}

server {
  listen      8080;
  http2       on;
  #server_name dev-server;
  server_name localhost;

  proxy_redirect   off;

  proxy_set_header Host              $http_host;
  proxy_set_header X-Forwarded-Host  $http_host;
  proxy_set_header X-Real-IP         $remote_addr;
  #proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-For   $remote_addr;
  proxy_set_header X-Forwarded-Port  $server_port;
  proxy_set_header X-Forwarded-Proto $scheme;

  proxy_connect_timeout   3600;
  proxy_read_timeout      3600;
  proxy_send_timeout      3600;
  send_timeout            3600;

  client_max_body_size 25M;
  expires 0;

  location /websocket/ {
    proxy_pass http://platform-server/websocket/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
  }

  location /platform/plugin/document/rest/ {
    proxy_pass http://document-server/rest/;
  }

  location /platform/plugin/document/get/ {
    proxy_pass http://document-server/get/;
  }

  location  /platform/plugin/document/ {
    add_header Cache-Control "no-store";
    #proxy_pass http://document-server/;
    proxy_pass http://document-webui-server/platform/plugin/document/ ;
  }

  location / {
    proxy_pass http://platform-server/;
  }
}
```

---

## Hướng Dẫn Setup Chi Tiết

### Bước 1: Cập nhật Homebrew
```bash
brew update && brew upgrade
```
**Giải thích:** Cập nhật Homebrew package manager và các gói đã cài để đảm bảo có phiên bản mới nhất.

### Bước 2: Cài đặt Nginx
```bash
brew install nginx
```
**Giải thích:**
- Nginx sẽ được cài vào `/opt/homebrew/Cellar/nginx/`
- File cấu hình chính: `/opt/homebrew/etc/nginx/nginx.conf`
- Thư mục server configs: `/opt/homebrew/etc/nginx/servers/`
- Document root: `/opt/homebrew/var/www`
- Port mặc định: 8080 (để chạy không cần sudo)

### Bước 3: Tạo File Config Server
Tạo file `/opt/homebrew/etc/nginx/servers/local-dev.conf` với nội dung server configuration ở trên.

**Giải thích các phần config:**

#### Upstream Servers (Load Balancer)
```nginx
upstream platform-server {
  server 127.0.0.1:7080;
}
```
- Định nghĩa các backend servers để proxy requests đến
- `platform-server`: chạy trên port 7080
- `document-server`: chạy trên port 7081
- `document-webui-server`: chạy trên port 3001

#### Server Block
```nginx
server {
  listen 8080;
  http2 on;
  server_name localhost;
```
- Nginx lắng nghe trên port 8080
- Bật HTTP/2 cho hiệu suất tốt hơn
- Server name là localhost

#### Proxy Headers
```nginx
proxy_set_header Host              $http_host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $remote_addr;
```
- Chuyển thông tin client gốc đến backend servers
- Backend sẽ biết được IP thật của client

#### Timeouts
```nginx
proxy_connect_timeout   3600;
proxy_read_timeout      3600;
proxy_send_timeout      3600;
```
- Timeout 3600 giây (1 giờ) để xử lý long-running requests
- Phù hợp cho các tác vụ xử lý lâu, uploads lớn

#### Client Settings
```nginx
client_max_body_size 25M;
```
- Cho phép upload file tối đa 25MB

#### Location Blocks (Route Mapping)

**WebSocket Support:**
```nginx
location /websocket/ {
  proxy_pass http://platform-server/websocket/;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 86400;
}
```
- `/websocket/` → platform-server
- HTTP/1.1 và Upgrade headers cho WebSocket
- Timeout 24 giờ cho WebSocket connections

**Document API:**
```nginx
location /platform/plugin/document/rest/ {
  proxy_pass http://document-server/rest/;
}
```
- `/platform/plugin/document/rest/` → document-server REST API
- `/platform/plugin/document/get/` → document-server GET endpoint

**Document WebUI:**
```nginx
location /platform/plugin/document/ {
  add_header Cache-Control "no-store";
  proxy_pass http://document-webui-server/platform/plugin/document/;
}
```
- Web UI của document plugin
- No cache để đảm bảo luôn có phiên bản mới nhất

**Default Route:**
```nginx
location / {
  proxy_pass http://platform-server/;
}
```
- Tất cả requests khác đều đi đến platform-server

### Bước 4: Test Cấu Hình
```bash
nginx -t
```
**Giải thích:** Kiểm tra syntax của file config có lỗi không trước khi start.

### Bước 5: Khởi động Nginx
```bash
brew services start nginx
```
**Giải thích:** Start nginx và tự động chạy khi boot macOS.

### Bước 6: Kiểm tra Status
```bash
brew services info nginx
```
**Giải thích:** Xem trạng thái nginx đang chạy hay không.

### Các Lệnh Hữu Ích

**Reload config (không downtime):**
```bash
brew services reload nginx
# hoặc
nginx -s reload
```

**Restart nginx:**
```bash
brew services restart nginx
```

**Stop nginx:**
```bash
brew services stop nginx
```

**Xem logs:**
```bash
tail -f /opt/homebrew/var/log/nginx/error.log
tail -f /opt/homebrew/var/log/nginx/access.log
```

**Test từng endpoint:**
```bash
# Test platform
curl http://localhost:8080/

# Test document REST API
curl http://localhost:8080/platform/plugin/document/rest/

# Test WebSocket (cần wscat hoặc tool khác)
```

### Lưu Ý Quan Trọng

1. **Backend servers phải chạy trước**: Đảm bảo các services trên port 7080, 7081, 3001 đang chạy
2. **Port conflicts**: Nếu port 8080 bị chiếm, đổi sang port khác trong config
3. **Permissions**: Với port < 1024 cần sudo, port >= 1024 chạy được không cần sudo
4. **File changes**: Mỗi khi sửa config phải reload nginx để apply changes
5. **Testing**: Luôn chạy `nginx -t` trước khi reload để tránh break service

### Troubleshooting

**Nginx không start:**
```bash
# Kiểm tra port có bị chiếm không
lsof -i :8080

# Xem log lỗi
cat /opt/homebrew/var/log/nginx/error.log
```

**502 Bad Gateway:**
- Backend servers chưa chạy hoặc sai port
- Kiểm tra các services trên 7080, 7081, 3001

**Config không apply:**
```bash
# Force reload
nginx -s stop
brew services start nginx
```
