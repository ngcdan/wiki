# VS Code + Vim extension (macOS) — profile chuẩn hoá sâu

Mục tiêu: dùng **Space leader** + các mapping “semantic” nhất quán với IntelliJ IdeaVim.

> Thực tế máy anh hiện tại:
> - `vim.leader = "<space>"`
> - Có `vim.handleKeys` và một số leader mappings trong `settings.json`
> - `keybindings.json` đang remap **Rename** sang `Cmd+R` và bỏ `F2`

---

## 1) Checklist extension (đúng stack JS/TS/React + Java + Python)

- Vim: `vscodevim.vim`
- ESLint + Prettier (tuỳ repo)
- Java: `Extension Pack for Java`
- Python: `ms-python.python` + `ms-python.vscode-pylance`

---

## 2) Leader mappings gợi ý (Vim normal mode)

Giữ triết lý: **Space + 1-2 ký tự** → IDE action.

### Gợi ý bộ mapping “portable” (nên dùng)

- `<leader>w` → Save
- `<leader>q` → Close editor
- `<leader>e` → Toggle sidebar
- `<leader>f` → Reveal current file in Explorer
- `<leader>p` → Quick Open (`Cmd+P`)
- `<leader>/` → Search in files (`Cmd+Shift+F`)
- `<leader>rn` → Rename (F2 / cmd binding)
- `<leader>ca` → Code actions (Quick Fix)
- `<leader>gd` → Go to definition
- `<leader>gr` → Find references
- `<leader>tt` → Toggle terminal

### Snippet (settings.json → `vim.normalModeKeyBindingsNonRecursive`)

> **Lưu ý:** VS Code cho phép JSON có comment (JSONC). Anh copy/merge theo nhu cầu.

```jsonc
"vim.normalModeKeyBindingsNonRecursive": [
  { "before": ["<leader>", "w"],  "commands": ["workbench.action.files.save"] },
  { "before": ["<leader>", "q"],  "commands": ["workbench.action.closeActiveEditor"] },
  { "before": ["<leader>", "e"],  "commands": ["workbench.action.toggleSidebarVisibility"] },
  { "before": ["<leader>", "f"],  "commands": ["revealInExplorer"] },

  { "before": ["<leader>", "p"],  "commands": ["workbench.action.quickOpen"] },
  { "before": ["<leader>", "/"],  "commands": ["workbench.action.findInFiles"] },

  { "before": ["<leader>", "r", "n"], "commands": ["editor.action.rename"] },
  { "before": ["<leader>", "c", "a"], "commands": ["editor.action.quickFix"] },

  { "before": ["<leader>", "g", "d"], "commands": ["editor.action.revealDefinition"] },
  { "before": ["<leader>", "g", "r"], "commands": ["references-view.findReferences"] },

  { "before": ["<leader>", "t", "t"], "commands": ["workbench.action.terminal.toggleTerminal"] }
]
```

---

## 3) Chuẩn hoá Rename / Quick Fix / Definition (để khỏi lo IDE nào)

### Option A (đơn giản, em khuyên): giữ mặc định VS Code
- Definition: `F12`
- Rename: `F2`
- Code actions: `Cmd+.`

### Option B (đã thấy trên máy anh): **Rename = Cmd+R**
Trong `keybindings.json` của anh hiện tại đang có:
- `Cmd+R` → `editor.action.rename`
- `F2` bị unbind

Nếu anh muốn đồng bộ với IntelliJ VS Code Keymap, **có thể giữ Cmd+R**, nhưng lưu ý:
- `Cmd+R` là phím hay bị dùng cho "reload" ở app khác; trong VS Code thì không quá chuẩn.

---

## 4) `vim.handleKeys` (giảm conflict với VS Code shortcuts)

Nguyên tắc:
- Cho VS Code xử lý các phím **Cmd+...** (search, palette, quick open).
- Vim giữ các phím trong editor.

Anh đang có (tóm tắt):
- `<C-f>` false (VS Code nhận page down/ find…)
- `<C-a>` false
- `<C-v>` true

Nếu anh muốn em đề xuất tối ưu theo thói quen của anh (đặc biệt Ctrl-f / Ctrl-d / Ctrl-u / Ctrl-b), em sẽ đọc nốt phần còn lại của settings và đưa patch.
