# Dev Shortcuts (macOS) — VS Code + IntelliJ IDEA (Vim mode)

> Setup của anh:
> - **macOS**
> - **VS Code + Vim extension**
> - **IntelliJ IDEA + IdeaVim**
> - IntelliJ keymap: **VS Code Keymap**
> - Stack: **JS/TS/React + Java/Spring + Python**

Mục tiêu: **1 bộ muscle memory** dùng được ở cả 2 IDE, ưu tiên Vim.

---

## 0) Nguyên tắc dùng hằng ngày (khỏi lo lệch phím)

### “Vim trước, IDE sau”
- 80% thao tác di chuyển/chỉnh sửa: làm bằng **Vim keys** (h/j/k/l, w/b, f/t, /, n, ci", etc.).
- 20% thao tác “semantic” (definition/rename/refactor/run/test): dùng **IDE actions**.

### ESC luôn là phím cứu hộ
- Nếu thấy “kỳ kỳ”: `Esc` để về Normal mode.

---

## 1) Vim essentials (dùng chung cho VS Code Vim + IdeaVim)

### Movement
- Char: `h j k l`
- Word: `w` (next), `b` (prev), `e` (end)
- Line: `0` (start), `^` (first non-blank), `$` (end)
- Paragraph/blocks: `{` / `}`
- Go to line: `gg` (top), `G` (bottom), `:{number}` (đến dòng)

### Search / Replace
- Search: `/{pattern}` (forward), `?{pattern}` (back)
- Next/prev match: `n` / `N`
- Replace in line: `:s/old/new/g`
- Replace whole file: `:%s/old/new/g`

### Editing (cực hay cho code)
- Insert: `i` (before), `a` (after), `I` (bol), `A` (eol)
- Delete:
  - `x` (char), `dd` (line), `dw` (word)
- Change:
  - `cw` (change word), `ci"` (inside quotes), `ci(` (inside parens), `ci{` (inside braces)
- Copy/Paste:
  - `yy` (yank line), `p` (paste after), `P` (paste before)
- Undo/redo: `u` / `Ctrl+r`

### Visual mode
- Enter visual: `v` (char), `V` (line), `Ctrl+v` (block)
- Indent: `>` / `<` (trong Visual)

### Multi-cursor kiểu Vim (thay cho mouse)
- Macro: `qa` … `q` rồi `@a` / `@@`
- Repeat last change: `.`

---

## 2) VS Code (macOS) + Vim extension — IDE actions nên thuộc

> Khi bật Vim extension, các phím trong editor ưu tiên Vim. Các shortcut dưới đây là “IDE level” nên vẫn rất hữu dụng.

### Core
- Quick Open: `Cmd+P`
- Command Palette: `Cmd+Shift+P`
- Search project: `Cmd+Shift+F`
- Toggle Terminal: ``Cmd+` ``
- Toggle Sidebar: `Cmd+B`

### Code intelligence
- Go to Definition: `F12`
- Peek Definition: `Option+F12`
- References: `Shift+F12`
- Rename: `F2`
- Code Actions/Quick Fix: `Cmd+.`

### Formatting (JS/TS/React/Python)
- Format document: `Shift+Option+F`
- Format selection: `Cmd+K Cmd+F`

### Debug
- Breakpoint: `F9`
- Start/Continue: `F5`
- Step over/into/out: `F10 / F11 / Shift+F11`

### Git / UI
- Source Control view: `Ctrl+Shift+G` *(nếu máy anh khác, check Keyboard Shortcuts)*

#### Notes cho Vim extension (để đỡ conflict)
- Nếu `Cmd+F` bị “Vim handled”: vào settings của Vim extension và bật allow VS Code search shortcuts (tuỳ config). Nói em biết anh muốn em viết hẳn snippet settings.json.

---

## 3) IntelliJ IDEA (macOS) + IdeaVim + **VS Code Keymap**

> Vì anh dùng **VS Code Keymap**, nhiều phím IDE sẽ giống VS Code hơn. Tuy nhiên IntelliJ có vài action “đáng tiền” cho Java/Spring.

### VS Code-like core (thường giống VS Code)
- Quick Open / Go to File: `Cmd+P` *(trên VS Code keymap thường map vậy; nếu lệch thì anh nói em chỉnh)*
- Find in Path: `Cmd+Shift+F`
- Toggle Terminal: ``Cmd+` `` (hoặc qua Tool Window)
- Toggle Sidebar/Project: `Cmd+B` *(tuỳ mapping)

### IntelliJ actions (rất nên giữ)
- Search Everywhere: `Double Shift`
- Go to Definition: `Cmd+B`
- Find Usages: `Option+F7`
- Intention/Quick Fix: `Option+Enter`
- Reformat: `Cmd+Option+L`
- Optimize imports: `Ctrl+Option+O`

### Refactor (Java/Spring)
- Refactor This: `Ctrl+T`
- Rename: `Shift+F6`
- Extract Method: `Cmd+Option+M`
- Extract Variable: `Cmd+Option+V`
- Change Signature: `Cmd+F6`

### Git
- Commit: `Cmd+K`
- Push: `Cmd+Shift+K`

---

## 4) Chuẩn hoá “1 bộ thao tác” dùng cho cả hai

### A) Di chuyển + sửa code
- Dùng 100% Vim: `w/b/e`, `f/t`, `ci"/ci(/ci{`, `dd`, `yy`, `p`, `.`

### B) Semantic actions (nhất quán)
- Definition: `F12` (VS Code) / `Cmd+B` (IntelliJ)
- Rename: `F2` (VS Code) / `Shift+F6` (IntelliJ)
- Quick Fix: `Cmd+.` (VS Code) / `Option+Enter` (IntelliJ)
- Format: `Shift+Option+F` (VS Code) / `Cmd+Option+L` (IntelliJ)

Nếu anh muốn **thống nhất 100%** (ví dụ rename cũng là `F2` ở IntelliJ), em có thể đề xuất mapping cụ thể trong IntelliJ keymap + IdeaVim.

---

## 5) Trạng thái thực tế trên máy anh (em đã check)

### VS Code Vim
- Anh **có dùng leader key** và đang set: `vim.leader = "<space>"`.

### IdeaVim
- Anh **đã có** file `~/.ideavimrc`.
- Trong đó anh đang set: `let g:mapleader = "\<space>"`.

---

## 6) Chuẩn hoá sâu (đã tạo file hướng dẫn + mapping)

Em đã tạo thêm 2 file trong cùng folder wiki:
- `vscode-vim-settings.md` — mapping leader + gợi ý handleKeys cho VS Code Vim
- `ideavimrc-template.md` — mapping leader đồng bộ cho IntelliJ IdeaVim (Java/Spring/Python)

Mục tiêu đồng bộ: `gd/gr/rn/ca/fm/tt` theo pattern `<leader>`.
