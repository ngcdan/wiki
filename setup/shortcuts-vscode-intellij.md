# Dev Shortcuts (macOS) — VS Code + IntelliJ IDEA

> Target của anh: **macOS** + stack **JS/TS/React + Java/Spring + Python**.
>
> Em viết theo kiểu **macOS-first**. Nếu anh dùng keyboard layout khác (VN/US) hoặc remap OS (Karabiner), một vài phím có thể lệch.

**Notation:** `macOS` (kèm `Win/Linux` trong ngoặc khi hay gặp).

---

## 0) Core muscle memory (nên thuộc trước)

### VS Code (macOS)
- Quick Open (mở file nhanh): `Cmd+P` *(Win: Ctrl+P)*
- Command Palette: `Cmd+Shift+P` *(Win: Ctrl+Shift+P)*
- Search toàn project: `Cmd+Shift+F` *(Win: Ctrl+Shift+F)*
- Go to Definition: `F12`
- Rename symbol: `F2`
- Code Actions / Quick Fix: `Cmd+.` *(Win: Ctrl+.)*
- Toggle Terminal: ``Cmd+` `` *(Win: Ctrl+`)*

### IntelliJ IDEA (macOS)
- Search Everywhere: `Double Shift`
- Go to File: `Cmd+Shift+O` *(Win: Ctrl+Shift+N)*
- Find in Path: `Cmd+Shift+F` *(Win: Ctrl+Shift+F)*
- Go to Declaration/Definition: `Cmd+B`
- Intention / Quick Fix: `Option+Enter`
- Rename: `Shift+F6`
- Reformat code: `Cmd+Option+L`

---

## 1) Navigation / Search (đi nhanh trong codebase)

### VS Code (macOS)
- Quick Open file: `Cmd+P`
- Search toàn project: `Cmd+Shift+F`
- Search trong file: `Cmd+F`
- Replace trong file: `Cmd+Option+F`
- Go to line: `Ctrl+G` *(VS Code trên mac vẫn dùng Ctrl+G)*
- Go to symbol (trong file): `Cmd+Shift+O`
- Go to symbol (toàn workspace): `Cmd+T`
- Editor: Back/Forward (quay lại/về tới vị trí trước): thường là `Ctrl+-` / `Ctrl+Shift+-` *(tuỳ keybinding)*

### IntelliJ IDEA (macOS)
- Search Everywhere: `Double Shift`
- Go to File: `Cmd+Shift+O`
- Go to Class: `Cmd+O` *(Java/Spring)*
- Go to Symbol: `Cmd+Option+O`
- Recent Files: `Cmd+E`
- Recent Locations: `Cmd+Shift+E`
- Navigate Back / Forward: `Cmd+Option+Left` / `Cmd+Option+Right`

---

## 2) Code intelligence (definition / references / docs)

### VS Code (macOS)
- Go to Definition: `F12`
- Peek Definition: `Option+F12`
- Go to References: `Shift+F12`
- Rename: `F2`
- Code Actions / Quick Fix: `Cmd+.`
- Trigger Suggest: `Ctrl+Space`
- Hover docs (focus): `Cmd+K Cmd+I`

**TS/JS/React note (rất hay dùng):**
- **Auto import / Fix import**: thường đi qua `Cmd+.` → chọn action phù hợp.
- **Organize Imports (TS/JS)**: `Cmd+Shift+P` → gõ `Organize Imports`.

### IntelliJ IDEA (macOS)
- Go to Declaration/Definition: `Cmd+B` (hoặc `Cmd+Click`)
- Go to Implementation: `Cmd+Option+B`
- Find Usages: `Option+F7`
- Quick Documentation: `F1`
- Type info: `Cmd+Shift+P`
- Intention / Quick Fix: `Option+Enter`
- Basic completion: `Ctrl+Space`
- Smart completion: `Cmd+Shift+Space`

---

## 3) Editing (multi-cursor, line ops, format)

### VS Code (macOS)
- Multi-cursor: `Option+Click`
- Add cursor above/below: `Option+Cmd+Up/Down`
- Select next occurrence: `Cmd+D`
- Select all occurrences: `Cmd+Shift+L`
- Move line up/down: `Option+Up/Down`
- Copy line up/down: `Shift+Option+Up/Down`
- Delete line: `Cmd+Shift+K`
- Comment line: `Cmd+/`
- Block comment: `Shift+Option+A`
- Format document: `Shift+Option+F`
- Format selection: `Cmd+K Cmd+F`

### IntelliJ IDEA (macOS)
- Duplicate line/selection: `Cmd+D`
- Delete line: `Cmd+Backspace`
- Move line up/down: `Shift+Option+Up/Down`
- Comment line: `Cmd+/`
- Block comment: `Cmd+Option+/`
- Reformat code: `Cmd+Option+L`
- Optimize imports: `Ctrl+Option+O`
- Extend/Shrink selection: `Option+Up` / `Option+Down`

---

## 4) Refactor (đặc biệt mạnh cho Java/Spring trong IntelliJ)

### VS Code (macOS) — thực dụng cho JS/TS/React
- Rename: `F2`
- Quick Fix / Refactor actions: `Cmd+.`
- Extract / inline / fix import…: thường nằm trong `Cmd+.` (tuỳ TypeScript Server)

**Gợi ý set up cho stack của anh (VS Code):**
- JS/TS/React: built-in TypeScript + ESLint/Prettier (tuỳ repo).
- Java: **Extension Pack for Java** (để có refactor/definition tốt hơn).
- Python: **Python** + **Pylance**.

### IntelliJ IDEA (macOS) — refactor chuẩn bài
- Refactor This: `Ctrl+T`
- Rename: `Shift+F6`
- Extract Method: `Cmd+Option+M`
- Extract Variable: `Cmd+Option+V`
- Extract Constant: `Cmd+Option+C`
- Inline: `Cmd+Option+N`
- Change Signature: `Cmd+F6`

---

## 5) Run / Debug

### VS Code (macOS)
- Toggle breakpoint: `F9`
- Start/Continue: `F5`
- Step Over / Into / Out: `F10` / `F11` / `Shift+F11`
- Stop: `Shift+F5`
- Run/Debug view: `Cmd+Shift+D`

**Node/React note:**
- Hay dùng `Cmd+Shift+P` → `Debug: Select and Start Debugging` để setup nhanh.

### IntelliJ IDEA (macOS)
- Run: `Ctrl+R` *(và/hoặc `Shift+F10` tuỳ máy)*
- Debug: `Ctrl+D` *(và/hoặc `Shift+F9` tuỳ máy)*
- Toggle breakpoint: `Cmd+F8`
- Step Over / Into / Out: `F8 / F7 / Shift+F8`
- Resume: `F9`
- Evaluate expression: `Option+F8`

---

## 6) Git / UI

### VS Code (macOS)
- Source Control view: `Ctrl+Shift+G` *(thường vậy; nếu khác thì xem Keyboard Shortcuts)*
- Toggle sidebar: `Cmd+B`

### IntelliJ IDEA (macOS)
- Commit: `Cmd+K`
- Push: `Cmd+Shift+K`

---

## 7) Chuẩn hoá thói quen giữa VS Code và IntelliJ (khuyến nghị)

### Option A (em khuyên): **Giữ keymap mặc định**, học “core 15 phím”
- Lý do: IntelliJ default tối ưu cho refactor Java; VS Code default tối ưu cho command palette + multi-cursor.
- Anh chỉ cần thuộc nhóm **0)** + **Navigation/Definition/Rename/QuickFix/Format/RunDebug**.

### Option B: Dùng **VS Code Keymap** trong IntelliJ
- Nếu anh muốn muscle memory giống VS Code hơn khi code Java/Spring.

---

## TODO (nếu anh muốn em tối ưu thêm)
- Anh cho em biết anh đang dùng **IntelliJ keymap nào** (Default / Mac OS / VS Code Keymap / Custom). Em sẽ chỉnh lại mục IntelliJ cho khớp 100%.
- Với VS Code: anh có dùng Vim keybindings không? Nếu có em sẽ làm một section riêng.
