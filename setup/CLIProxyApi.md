# CLI Proxy API

Tài liệu này tổng hợp hướng dẫn cài đặt và sử dụng CLIProxyAPI, kèm gợi ý thiết lập một số công cụ coding khác.

## Mục đích của CLIProxyAPI
- Làm lớp "proxy" cung cấp API tương thích OpenAI cho nhiều tool/SDK khác nhau.
- Cho phép đổi nhà cung cấp model mà không phải đổi cấu hình trong từng tool (chỉ cần trỏ về CLIProxyAPI).
- Hỗ trợ đăng nhập Codex qua OAuth nếu bạn dùng tài khoản OpenAI/ChatGPT.

## Mục đích của các tool phổ biến (gợi ý)
- Antigravity (IDE): IDE agent-first, có Agent Manager, Artifacts System, multi-surface (browser/terminal/editor) và multi-model (Gemini/Claude/GPT-OSS).
- Continue (VS Code/JetBrains): chat + agent trong IDE, tùy biến config theo project hoặc theo user.
- Cline (VS Code/Cursor/JetBrains): tác vụ agentic có thể tạo/sửa file theo kế hoạch.
- Aider (CLI): pair programming trong terminal, mạnh cho refactor và làm việc theo git diff.

## Cài đặt (macOS)
Theo Quick Start:
```bash
brew install cliproxyapi
brew services start cliproxyapi
```

## Tạo config tối thiểu
CLIProxyAPI đọc `config.yaml` ở project root theo mặc định; có thể chỉ định bằng `--config`.
Ví dụ config tối thiểu:
```yaml
host: "127.0.0.1"
port: 8317
auth-dir: "~/.cli-proxy-api"
api-keys:
  - "your-client-key"
debug: false
logging-to-file: false
```

Chạy foreground với config:
```bash
cli-proxy-api --config ~/.cli-proxy-api/config.yaml
```

## Đăng nhập Codex (OAuth)
Lệnh đăng nhập:
```bash
cli-proxy-api --codex-login
```
Tùy chọn:
- `--no-browser`: in URL login thay vì mở trình duyệt
- Callback OAuth dùng cổng 1455

Dữ liệu credential/auth được lưu trong `auth-dir`.

## Dùng với Codex CLI (tùy chọn)
Chỉnh `~/.codex/config.toml` và `~/.codex/auth.json` như hướng dẫn:
```toml
model_provider = "cliproxyapi"
model = "gpt-5-codex"
model_reasoning_effort = "high"

[model_providers.cliproxyapi]
name = "cliproxyapi"
base_url = "http://127.0.0.1:8317/v1"
wire_api = "responses"
```
```json
{
  "OPENAI_API_KEY": "sk-dummy"
}
```

## Dùng với client OpenAI-compatible
Nếu tool/SDK hỗ trợ "OpenAI-compatible base URL", đặt:
- Base URL: `http://127.0.0.1:8317/v1`
- API key: giá trị trong `api-keys` của config

## GitHub Copilot trên VS Code
Lưu ý (theo docs GitHub): Copilot chỉ hỗ trợ HTTP proxy và chứng chỉ; không có tùy chọn đổi "model endpoint" sang CLIProxyAPI. Nghĩa là bạn không thể dùng CLIProxyAPI làm backend cho Copilot.

Nếu bạn cần Copilot đi qua HTTP proxy (mạng công ty, firewall):
1) VS Code > Settings > Application > Proxy
2) Đặt `http.proxy` = `http://<proxy-host>:<port>`
3) Nếu cần, tắt/bật `Proxy Strict SSL`

Hoặc dùng biến môi trường (ưu tiên cao nhất):
```bash
export HTTPS_PROXY="http://<proxy-host>:<port>"
export HTTP_PROXY="http://<proxy-host>:<port>"
```
Ghi chú:
- Copilot không hỗ trợ URL proxy bắt đầu bằng `https://`.
- Copilot đọc chứng chỉ từ OS trust store và `NODE_EXTRA_CA_CERTS` (nếu cần proxy có SSL inspection).

## Thiết lập theo môi trường của bạn (Mac mini M4 + VS Code Copilot + Antigravity)
### 1) Antigravity (IDE)
Cài đặt:
1) Trang download chính thức yêu cầu bạn đăng nhập Google; việc đăng nhập cũng dùng để truy cập Gemini 3 và các tính năng AI.
2) Trình cài đặt sẽ tự nhận nền tảng và cung cấp bản phù hợp cho macOS.
3) Antigravity đang miễn phí trong giai đoạn Public Preview.

### 2) VS Code + GitHub Copilot
Bạn tiếp tục dùng Copilot như hiện tại. Copilot hoạt động độc lập với CLIProxyAPI, nên hãy xem CLIProxyAPI như một kênh riêng cho các tool OpenAI-compatible khác.

### 3) Dùng CLIProxyAPI song song với Antigravity
Nếu bạn muốn tận dụng model khác hoặc quy trình agentic ngoài IDE, hãy dùng Continue/Cline/Aider trỏ về CLIProxyAPI như các mục ở trên.

## Gợi ý setup và dùng các công cụ khác
Mục tiêu là để các tool trỏ về CLIProxyAPI thông qua OpenAI-compatible base URL.

### 1) Continue (VS Code/JetBrains)
Continue cho phép tự host model hoặc dùng endpoint OpenAI-compatible bằng cách cấu hình provider `openai` và đổi `baseUrl`.

Ví dụ `~/.continue/config.yaml`:
```yaml
name: local-proxy
version: 0.0.1
schema: v1

models:
  - name: CLIProxyAPI
    provider: openai
    model: gpt-4o
    baseUrl: http://127.0.0.1:8317/v1
    apiKey: your-client-key
```
### 2) Cline (VS Code/Cursor/JetBrains)
Trong Cline settings (⚙):
- API Provider: OpenAI Compatible
- Base URL: `http://127.0.0.1:8317/v1`
- API Key: `your-client-key`
- Model ID: ví dụ `gpt-4o` (hoặc model bạn muốn)

### 3) Aider (CLI)
Aider hỗ trợ OpenAI-compatible endpoint qua biến môi trường:
```bash
export OPENAI_API_BASE="http://127.0.0.1:8317/v1"
export OPENAI_API_KEY="your-client-key"
aider --model openai/gpt-4o
```

## Cách chọn công cụ phù hợp (gợi ý nhanh)
- Muốn làm việc ngay trong IDE, chat + chỉnh code: ưu tiên Continue hoặc Cline.
- Muốn thao tác nhanh trong terminal, theo luồng git: Aider.
- Nếu chỉ dùng Copilot, giữ nguyên Copilot và dùng CLIProxyAPI cho tool khác chạy song song.

## Tham khảo
- CLIProxyAPI Quick Start: https://help.router-for.me/introduction/quick-start
- CLIProxyAPI Basic Configuration: https://help.router-for.me/configuration/basic
- CLIProxyAPI Codex OAuth: https://help.router-for.me/configuration/provider/codex
- CLIProxyAPI Codex client config: https://help.router-for.me/agent-client/codex
- GitHub Copilot network/proxy settings: https://docs.github.com/copilot/how-tos/personal-settings/configuring-network-settings-for-github-copilot
- Continue config & self-host: https://docs.continue.dev/customize/deep-dives/configuration
- Continue OpenAI baseUrl: https://docs.continue.dev/guides/how-to-self-host-a-model
- Cline OpenAI-compatible provider: https://docs.cline.bot/provider-config/openai-compatible
- Aider OpenAI-compatible APIs: https://aider.chat/docs/llms/openai-compat.html
- Antigravity home: https://www.antigravityide.app/
- Antigravity download (chính thức): https://www.antigravityide.app/download
- Antigravity features (chính thức): https://www.antigravityide.app/features
