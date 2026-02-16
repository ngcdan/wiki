---
title: "Shortcut unification session (VS Code + IntelliJ) — 2026-02-09"
type: note
tags: [setup]
created: 2026-02-09
updated: 2026-02-09
---
# Shortcut unification session (VS Code + IntelliJ) — 2026-02-09

Mục tiêu: 1 bộ muscle memory shortcuts dùng được cho VS Code + IntelliJ, ưu tiên Vim.

## Status
- Reset shortcuts về default (VS Code keybindings.json trống, IntelliJ dọn keymaps duplicate)
- Build IntelliJ keymap layer để match VS Code (B-layer)
- Đồng bộ portable Vim layer (leader = Space) cho VS Code Vim + IdeaVim
- Đã patch Ctrl+` terminal, Search Everywhere = Cmd+Shift+P
- Đã patch Cmd+Click go-to-definition cho IntelliJ keymap (GotoDeclaration mouse shortcut)

## Canonical doc
- Muscle shortcuts table: `setup/muscle-shortcuts.md`

## Key files changed
### VS Code
- Settings (Vim mappings):
  - `~/Library/Application Support/Code/User/settings.json`
- Keybindings (reset default):
  - `~/Library/Application Support/Code/User/keybindings.json` = `[]`

### IntelliJ
- Active keymap:
  - `~/Library/Application Support/JetBrains/IdeaIC2025.2/options/mac/keymap.xml`
- Keymap B-layer:
  - `~/Library/Application Support/JetBrains/IdeaIC2025.2/keymaps/VSCode OSX (Zoe B-layer).xml`
  - `~/Library/Application Support/JetBrains/IdeaIC2025.2/settingsSync/keymaps/VSCode OSX (Zoe B-layer).xml`
- IdeaVim:
  - `~/.ideavimrc`

## Backups / rollback
- Backup bundle (vscode settings/keybindings + intellij keymaps/options) created at:
  - `/Users/nqcdan/.openclaw/workspace/backup/shortcuts-reset-20260209-110552`
- Old ideavimrc:
  - `~/.ideavimrc.bak.20260209-120250`

## Quick verify checklist
- VS Code:
  - `Cmd+Click` goto definition OK
  - `Ctrl+`` toggle terminal OK
- IntelliJ:
  - `Cmd+Shift+P` Search Everywhere
  - `Cmd+Option+F` Replace, `Cmd+Shift+H` Replace in Path
  - `Ctrl+`` terminal
  - `Cmd+Click` goto declaration (requires restart if just patched)

