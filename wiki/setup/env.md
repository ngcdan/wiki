---
title: "Dev Environment Setup"
tags: [setup, env, terminal, git, mac-mini]
created: 2026-01-27
updated: 2026-04-05
---

# Dev Environment Setup

Tổng hợp toàn bộ cấu hình môi trường phát triển trên macOS.

---

## 1. Git Identity

Mục tiêu: tránh commit nhầm `user.name/user.email` giữa các project.

| Context | Name | Email | Scope |
|---------|------|-------|-------|
| **Default (global)** | _(không set — mỗi repo tự config)_ | | |
| **Forgejo (OF1)** | `nqcdan.dev` | `jesse.vnhph@openfreightone.com` | `/Users/nqcdan/OF1/forgejo/**` |
| **Egov (a Hiếu)** | `hieuht2901` | `hieuht2910@gmail.com` | `of1-egov*`, `of1-egov-document`, `of1-egov-ai-instruction` |

### Global settings (`~/.gitconfig`)

```ini
[pull]
    ff = only
[advice]
    diverging = false
[merge]
    autoEdit = no

[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/"]
    path = ~/.gitconfig-forgejo
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/**"]
    path = ~/.gitconfig-forgejo

# Override cho eGov repos (account hieuht2901)
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov/"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov/**"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov-**"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov-document/"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov-document/**"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov-ai-instruction/"]
    path = ~/.gitconfig-egov-hieu
[includeIf "gitdir:/Users/nqcdan/OF1/forgejo/of1-platform/of1-egov-ai-instruction/**"]
    path = ~/.gitconfig-egov-hieu
```

### Override files

**`~/.gitconfig-forgejo`:**
```ini
[user]
  name = nqcdan.dev
  email = jesse.vnhph@openfreightone.com
```

**`~/.gitconfig-egov-hieu`:**
```ini
[user]
  name = hieuht2901
  email = hieuht2910@gmail.com
```

---

## 2. Ghostty (Terminal Emulator)

Terminal emulator modern, nhanh, native macOS. File: `~/.config/ghostty/config`

Config hiện tại rất minimal — chỉ set theme:

```ini
theme = "gruvbox-dark"
```

---

## 3. Tmux

Trình quản lý session — terminal workspace tồn tại bền vững qua restart.

### Core Concepts

- **Session = Project** (e.g., `of1-be`, `of1-fe`)
- **Window = Context** (e.g., `code`, `server`, `db`)
- **Pane = View** (e.g., split editor + logs)
- **Golden Rule:** Khi xong, **DETACH** (`Ctrl+a` `d`), đừng exit.

### Config (`~/.tmux.conf`)

- **Prefix:** `Ctrl + a`
- **Splits:** `|` (ngang) và `-` (dọc)
- **Navigation:** `h` `j` `k` `l` (Vim-style)
- **Copy mode:** Vi keys, `y` to copy via pbcopy
- **Theme:** Gruvbox Dark (manual, full powerline-style statusbar)
- **Plugins:** tmux-resurrect (save/restore), tmux-continuum (auto-save 15p)
- **History:** 50,000 lines

```tmux
set -g default-terminal 'tmux-256color'
set -as terminal-overrides ',xterm-kitty:RGB'
set -g mouse on

# --- Prefix ---
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# --- Keybindings ---
bind | split-window -h
bind - split-window -v
unbind '"'
unbind %

# Vim-like navigation
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Resize
bind J resize-pane -D 10
bind K resize-pane -U 10
bind L resize-pane -L 10
bind H resize-pane -R 19

set-option -g allow-rename off

# --- THEME (Gruvbox Dark medium) ---
set-option -g status "on"
set-option -g status-style bg=colour237,fg=colour223
set-window-option -g window-status-style bg=colour214,fg=colour237
set-window-option -g window-status-activity-style bg=colour237,fg=colour248
set-window-option -g window-status-current-style bg=red,fg=colour237
set-option -g pane-active-border-style fg=colour250
set-option -g pane-border-style fg=colour237
set-option -g message-style bg=colour239,fg=colour223
set-option -g message-command-style bg=colour239,fg=colour223
set-option -g display-panes-active-colour colour250
set-option -g display-panes-colour colour237
set-window-option -g clock-mode-colour colour109
set-window-option -g window-status-bell-style bg=colour167,fg=colour235

set-option -g status-justify "left"
set-option -g status-left-style none
set-option -g status-left-length "80"
set-option -g status-right-style none
set-option -g status-right-length "80"
set-window-option -g window-status-separator ""

set-option -g status-left "#[bg=colour241,fg=colour248] #S #[bg=colour237,fg=colour241,nobold,noitalics,nounderscore]"
set-option -g status-right "#[bg=colour237,fg=colour239 nobold, nounderscore, noitalics]#[bg=colour239,fg=colour246] %Y-%m-%d  %H:%M #[bg=colour239,fg=colour248,nobold,noitalics,nounderscore]#[bg=colour248,fg=colour237] #h "
set-window-option -g window-status-current-format "#[bg=colour214,fg=colour237,nobold,noitalics,nounderscore]#[bg=colour214,fg=colour239] #I #[bg=colour214,fg=colour239,bold] #W#{?window_zoomed_flag,*Z,} #[bg=colour237,fg=colour214,nobold,noitalics,nounderscore]"
set-window-option -g window-status-format "#[bg=colour239,fg=colour237,noitalics]#[bg=colour239,fg=colour223] #I #[bg=colour239,fg=colour223] #W #[bg=colour237,fg=colour239,noitalics]"

# --- CLIPBOARD & COPY MODE ---
set -g mode-keys vi
set -g set-clipboard on
set -g history-limit 50000
bind-key -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"
bind-key -T copy-mode-vi MouseDragEnd1Pane send -X copy-pipe-and-cancel "pbcopy"

# --- PLUGINS ---
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'

set -g @continuum-restore 'on'
set -g @resurrect-strategy-vim 'session'
set -g @resurrect-strategy-nvim 'session'

run '~/.tmux/plugins/tpm/tpm'
```

### Installation

```bash
brew install tmux
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
# Tạo ~/.tmux.conf, vào tmux, nhấn Ctrl+a rồi I (Shift+i) để install plugins
```

### Workflow Alias (optional)

```bash
# Thêm vào ~/.zshrc
ide() {
  tmux new-session -A -s workspace -n editor "cd ~/dev/wiki && nvim ."
}
```

### Zsh Integration

- Theme: `powerlevel10k/powerlevel10k`
- Plugins: `git`, `zsh-autosuggestions`, `zsh-syntax-highlighting`

---

## 4. Remote Mac mini (Tailscale + SSH + Screen Sharing)

Remote Development từ MacBook M1 về Mac mini M4 đặt tại công ty.

### Tailnet devices

| Thiết bị | OS | IP |
|----------|----|----|
| Mac mini M4 (host) | macOS | `100.78.159.118` |
| MacBook M1 (client) | macOS | `100.66.189.23` |
| iPhone | iOS | `100.123.23.20` |
| OF1 server | Windows | `100.123.28.7` |
| OF1 server backup | Linux | `100.96.120.47` |

Tailnet account: `linuss1908@`. Chỉ dùng IP để kết nối.

### 4.1 Cài Tailscale (cả 2 máy)

```bash
brew install --cask tailscale
```

Đăng nhập bằng `linuss1908@`. Trên Mac mini bật **"Start at Login"**. Chỉ dùng IP để kết nối (không dùng MagicDNS).

### 4.2 Cấu hình Mac mini

**System Settings > General > Sharing:**
- **Screen Sharing** → ON → "Only these users" → `nqcdan`
- **Remote Login** (SSH) → ON → "Only these users" → `nqcdan`

**Power Management:**

```bash
sudo pmset -a sleep 0 displaysleep 10
sudo pmset -a womp 1
```

> [!warning] FileVault
> Nếu bật FileVault, khi restart máy chưa vào mạng cho đến khi nhập password trực tiếp. Nên chỉ sleep màn hình, không tắt máy.

### 4.3 Kết nối từ MacBook

**Remote Desktop:**

```bash
open vnc://100.78.159.118
```

### 4.4 SSH Config (`~/.ssh/config`)

```ssh
# OF1 Apps
Host nginx.of1-apps.svc.cluster.local
    HostName nginx.of1-apps.svc.cluster.local
    User of1

# GitHub
Host github.com
    Preferredauthentications publickey
    User ngcdan
    IdentityFile ~/.ssh/id_rsa_github

# Forgejo (OF1 CI/CD) — default account
Host forgejo.of1-cicd.svc.cluster.local
    User nqcdan.dev
    Preferredauthentications publickey
    Port 22
    IdentityFile ~/.ssh/id_rsa

# Forgejo — hieuht2901
Host forgejo-hieuht
    HostName forgejo.of1-cicd.svc.cluster.local
    Preferredauthentications publickey
    Port 22
    IdentityFile ~/.ssh/id_rsa_hieuht
    IdentitiesOnly yes
```

### 4.4 Tailscale ACLs (bảo mật)

```json
{
  "groups": { "group:dev": ["linuss1908@"] },
  "hosts": { "mac-mini": "100.78.159.118" },
  "acls": [
    { "action": "accept", "src": ["linuss1908@"], "dst": ["mac-mini:22,5900"] }
  ],
  "ssh": [
    { "action": "accept", "src": ["linuss1908@"], "dst": ["mac-mini"], "users": ["nqcdan"] }
  ]
}
```

### 4.5 Troubleshooting

| Vấn đề | Khắc phục |
|--------|-----------|
| Không ping được | `tailscale status` trên cả 2 máy, thử `tailscale ping 100.78.159.118` |
| Screen Sharing lỗi | `sudo lsof -i :5900`, tắt/bật lại Screen Sharing |
| VS Code đứt | `ssh nqcdan@100.78.159.118 "rm -rf .vscode-server"` |
| Mac mini offline | Kiểm tra trực tiếp (mất điện, rớt mạng) |

### 4.6 Lệnh thường dùng

```bash
tailscale ping 100.78.159.118
ssh nqcdan@100.78.159.118
open vnc://100.78.159.118
# Debug: log show --predicate 'process == "screensharingd"' --last 5m
```

---

## 5. Moltbot (Clawdbot) — Bot 24/7 trên Mac mini

Chạy moltbot 24/7, tách biệt hoàn toàn với user chính.

### Node cho OpenClaw daemon

Dùng **Homebrew Node** (không dùng nvm/fnm cho daemon — LaunchAgent không load `.zshrc`).

```bash
openclaw gateway install
openclaw gateway start
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

### User isolation & bảo mật

```bash
# Tạo user riêng, không admin, không sudo
sudo sysadminctl -addUser clawdbot -fullName "Clawdbot Service" -password "mật_khẩu_mạnh"
```

- API key trong `.env` chỉ user clawdbot đọc (`chmod 600 .env`)
- SSH chỉ từ MacBook qua Tailscale ACL
- Không expose port ra internet

### Setup steps

```bash
# Đăng nhập user
su - clawdbot

# Python env
python3 -m venv moltbot-env
source moltbot-env/bin/activate

# Clone & install
git clone https://github.com/clawdbot/moltbot.git
cd moltbot && pip install -r requirements.txt

# Config
cp .env.example .env && nano .env && chmod 600 .env

# Startup script
echo '#!/bin/bash\ncd ~/moltbot\nsource ~/moltbot-env/bin/activate\npython main.py' > ~/moltbot/start.sh
chmod +x ~/moltbot/start.sh
```

### LaunchAgent (auto-start)

File: `/Users/clawdbot/Library/LaunchAgents/com.moltbot.service.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.moltbot.service</string>
    <key>ProgramArguments</key><array><string>/Users/clawdbot/moltbot/start.sh</string></array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/Users/clawdbot/moltbot/moltbot.log</string>
    <key>StandardErrorPath</key><string>/Users/clawdbot/moltbot/moltbot.err</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.moltbot.service.plist
# Xem log: tail -f ~/moltbot/moltbot.log
# Restart: launchctl unload ... && launchctl load ...
```

### Checklist bảo mật

- [x] User riêng, không admin
- [x] `.env` chỉ user đọc (`chmod 600`)
- [x] SSH chỉ từ thiết bị tin cậy (Tailscale ACL)
- [x] Không expose port ra internet
- [x] Cập nhật OS + package định kỳ

---

## 6. macOS Quick Setup (DataTP)

1. Tắt Spotlight, dùng Alfred: **System Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Install ngrok
3. Install Claude Code: `curl -fsSL https://claude.ai/install.sh | bash`

---

## Liên quan

- [[muscle-shortcuts]] — keyboard shortcuts cheat sheet
- [[projects]] — project-specific setup guides
