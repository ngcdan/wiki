---
title: "Muscle shortcuts — VS Code + IntelliJ + Vim (macOS)"
type: note
tags: [setup, work, automation]
created: 2026-02-09
updated: 2026-02-09
---
# Muscle shortcuts — VS Code + IntelliJ + Vim (macOS)
Mục tiêu: **1 bộ muscle memory** dùng được cả VS Code và IntelliJ, ưu tiên **Vim**.

---

## Cheat sheet (bảng mapping)

> Cột **Vim** = bấm trong Vim mode (VS Code Vim / IdeaVim).
> Cột **IDE** = bấm kiểu IDE-level (không phụ thuộc Vim).

### Navigate / Search

| Description | Vim | IDE | Notes |
|---|---|---|---|
| Open file / Go to file | `<leader>p` | `Cmd+P` | Portable nhất. |
| Search in project | `<leader>/` | `Cmd+Shift+F` | Find in Files / Find in Path |
| Command palette / Search actions (Search Everywhere) | — | `Cmd+Shift+P` | VS Code: Command Palette; IntelliJ: Search Everywhere |
| Go to symbol (in file) | — | `Cmd+Shift+O` | VS Code + IntelliJ đều có |
| Find (in file) | — | `Cmd+F` | |
| Replace (in file) | — | `Cmd+Option+F` | Chuẩn VS Code; IntelliJ đã ép theo VS Code (không dùng Cmd+R) |
| Replace in files (project) | — | `Cmd+Shift+H` | Chuẩn VS Code; IntelliJ đã ép theo VS Code |
| Recent files | `<leader>fr` | — | IntelliJ action; VS Code có thể thêm sau nếu muốn |

### Code intelligence

| Description | Vim | IDE | Notes |
|---|---|---|---|
| Go to definition / declaration | `<leader>gd` | `F12` | VS Code: Go to Definition; IntelliJ: **GotoDeclaration** |
| References / usages | `<leader>gr` | `Shift+F12` | VS Code: References; IntelliJ: **FindUsages** |
| Rename symbol | `<leader>rn` | `F2` | |
| Code actions / intentions | `<leader>ca` | `Cmd+.` | VS Code: Quick Fix; IntelliJ: Show Intention Actions |

### Editing (Vim-native)

| Description | Vim | IDE | Notes |
|---|---|---|---|
| Escape insert mode | `jk` | — | Đồng bộ VS Code Vim + IdeaVim |
| Change / inside quotes | `ci"`, `ci'` | — | |
| Change / inside parens/braces | `ci(`, `ci{` | — | |
| Repeat last change | `.` | — | |
| Macro record/play | `qa … q`, `@a`, `@@` | — | |

### Formatting / Imports

| Description | Vim | IDE | Notes |
|---|---|---|---|
| Format / Reformat | `<leader>fm` | `Shift+Option+F` | IntelliJ maps ReformatCode → Shift+Option+F |
| Optimize imports (Java) | `<leader>oi` | — | VS Code tuỳ toolchain (ESLint/TS/Python) |

### Tabs / Windows / Terminal

| Description | Vim | IDE | Notes |
|---|---|---|---|
| Close current tab/editor | `qq` | — | Đã chốt: chỉ giữ `qq` cho close current |
| Close all editors | `<leader>qa` | — | |
| Next tab/editor | `]t` | `Ctrl+Tab` | IDE-level chuẩn VS Code (macOS): next editor/tab |
| Previous tab/editor | `[t` | `Ctrl+Shift+Tab` | |
| Vertical split | `<leader>\\` | — | Portable (đã dùng giống VS Code mapping trước đó) |
| Horizontal split | `<leader>-` | — | |
| Toggle terminal | `<leader>tt` | `Ctrl+`` | Chuẩn hoá theo VS Code macOS (`Cmd+`` dễ conflict macOS) |

---

## Config locations

### VS Code
- `~/Library/Application Support/Code/User/settings.json`
  - section: `vim.*` (leader mappings + `]t/[t`)
- `~/Library/Application Support/Code/User/keybindings.json`
  - đang để default: `[]`

### IntelliJ
- IdeaVim: `~/.ideavimrc`
- Keymap (B-layer):
  - `~/Library/Application Support/JetBrains/IdeaIC2025.2/keymaps/VSCode OSX (Zoe B-layer).xml`

---

## Session log (2026-02-09)

- Reset shortcuts ve default (VS Code keybindings.json trong, IntelliJ don keymaps duplicate)
- Build IntelliJ keymap layer de match VS Code (B-layer)
- Dong bo portable Vim layer (leader = Space) cho VS Code Vim + IdeaVim
- Da patch Ctrl+` terminal, Search Everywhere = Cmd+Shift+P
- Da patch Cmd+Click go-to-definition cho IntelliJ keymap (GotoDeclaration mouse shortcut)
- Backup bundle: `/Users/nqcdan/.openclaw/workspace/backup/shortcuts-reset-20260209-110552`
- Old ideavimrc: `~/.ideavimrc.bak.20260209-120250`

### Quick verify checklist
- VS Code: `Cmd+Click` goto definition OK, `Ctrl+`` toggle terminal OK
- IntelliJ: `Cmd+Shift+P` Search Everywhere, `Cmd+Option+F` Replace, `Cmd+Shift+H` Replace in Path, `Ctrl+`` terminal, `Cmd+Click` goto declaration

---

Xem them: [[ghostty-tmux]], [[config]]
