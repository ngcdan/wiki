# Ghostty + Tmux Setup Guide (Current Machine Config)

Hướng dẫn cài đặt và cấu hình dựa trên setup thực tế đang chạy trên máy (Mac mini M4).

## 1. Ghostty
*Terminal emulator modern, nhanh, native macOS.*

### Config
File: `~/.config/ghostty/config`

Style hiện tại đang dùng **Gruvbox Dark** để đồng bộ với Tmux/Neovim.

```ini
font-family = "JetBrainsMono Nerd Font Mono"
font-size = 13
theme = Gruvbox Dark

# --- Window & Layout ---
window-padding-x = 4
window-padding-y = 4
window-inherit-working-directory = true
macos-option-as-alt = true

# --- Cursor & Selection (Matching Kitty/Neovim) ---
cursor-color = #928374
cursor-text = #282828
selection-background = #ebdbb2
selection-foreground = #928374

# --- Shell Integration ---
shell-integration = zsh
```

## 2. Tmux
Trình quản lý session, giúp terminal workspace tồn tại bền vững qua các lần restart máy/terminal.

### Config
File: `~/.tmux.conf`

**Key Highlights:**
- **Prefix:** `Ctrl + a` (thay vì default `Ctrl + b`).
- **Splits:** `|` (ngang) và `-` (dọc).
- **Navigation:** `h` `j` `k` `l` (như Vim).
- **Theme:** Custom **Gruvbox** (manual config, không dùng plugin theme).
- **Plugins:**
    - `tmux-resurrect`: Save/Restore sessions (Prefix + `Ctrl-s` save, `Ctrl-r` restore).
    - `tmux-continuum`: Auto-save session mỗi 15p.

```tmux
# Prefer modern terminfo
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

# --- THEME (Gruvbox Manual) ---
set-option -g status "on"
set-option -g status-style bg=colour237,fg=colour223
set-window-option -g window-status-current-style bg=red,fg=colour237
set-option -g status-left "#[bg=colour241,fg=colour248] #S #[bg=colour237,fg=colour241,nobold,noitalics,nounderscore]"
set-option -g status-right "#[bg=colour237,fg=colour239]#[bg=colour239,fg=colour246] %Y-%m-%d  %H:%M #[bg=colour239,fg=colour248]#[bg=colour248,fg=colour237] #h "

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
1. Install Tmux: `brew install tmux`
2. Install TPM: `git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm`
3. Apply Config: Tạo file `~/.tmux.conf` như trên.
4. Install Plugins: Vào tmux, nhấn `Ctrl+a` rồi `I` (Shift+i).

## 3. Automation (Workflow)

Hiện tại chưa có script automation dedicated (như `tmuxp` hay shell script riêng) trong dotfiles quét được. Workflow chủ yếu dựa vào **tmux-continuum** để tự động restore lại trạng thái cũ (session, window, running processes) khi bật máy lại.

### Khuyến nghị (Optional)
Nếu muốn tạo nhanh session mẫu, có thể thêm alias vào `.zshrc`:

```bash
# Thêm vào cuối ~/.zshrc
ide() {
  tmux new-session -A -s workspace -n editor "cd ~/dev/wiki && nvim ."
}
```
*Chạy `ide` sẽ tự vào session "workspace", mở sẵn nvim tại wiki.*

## 4. Zsh Integration
Trong `~/.zshrc` hiện tại:
- `ZSH_THEME="powerlevel10k/powerlevel10k"`
- Plugins: `git`, `zsh-autosuggestions`, `zsh-syntax-highlighting`.
- Aliases hữu ích khác: `fzf` binding, `tm`/`tmx` (đang comment out).

---
*Note: Config này tối ưu cho flow Vim/Neovim + Tmux + Ghostty với màu Gruvbox đồng bộ.*
