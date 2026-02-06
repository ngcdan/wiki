# IntelliJ IDEA + IdeaVim (macOS) + VS Code Keymap — chuẩn hoá sâu

Mục tiêu: giữ **Vim editing** nhưng map thêm **semantic actions** sao cho giống VS Code (và giống leader mappings bên VS Code Vim).

> Thực tế máy anh:
> - Có `~/.ideavimrc`
> - Leader đang là Space: `let g:mapleader = "\<space>"`

---

## 1) Bộ leader mapping đề xuất (đồng bộ với VS Code)

### Navigation / Files
```vim
" Toggle Project tool window (sidebar)
nnoremap <leader>e :action ActivateProjectToolWindow<CR>

" Go to File (tương đương Quick Open)
nnoremap <leader>p :action GotoFile<CR>

" Find in Path
nnoremap <leader>/ :action FindInPath<CR>

" Recent files
nnoremap <leader>fr :action RecentFiles<CR>
```

### Code intelligence
```vim
" Go to definition / declaration
nnoremap <leader>gd :action GotoDeclaration<CR>

" Find usages / references
nnoremap <leader>gr :action FindUsages<CR>

" Rename
nnoremap <leader>rn :action RenameElement<CR>

" Quick fix / intention (giống Cmd+.)
nnoremap <leader>ca :action ShowIntentionActions<CR>
```

### Formatting / Imports (Java/Spring cực ăn tiền)
```vim
" Reformat code
nnoremap <leader>fm :action ReformatCode<CR>

" Optimize imports
nnoremap <leader>oi :action OptimizeImports<CR>
```

### Terminal
```vim
" Toggle terminal tool window
nnoremap <leader>tt :action ActivateTerminalToolWindow<CR>
```

---

## 2) Chuẩn hoá phím “cốt lõi” giữa 2 IDE (recommended)

Nếu anh muốn 1 pattern thống nhất:
- `<leader>gd` = go to definition
- `<leader>gr` = references/usages
- `<leader>rn` = rename
- `<leader>ca` = code actions/intentions
- `<leader>fm` = format

Thì VS Code Vim chỉ cần map cùng pattern (xem file `vscode-vim-settings.md`).

---

## 3) Gợi ý merge vào ~/.ideavimrc hiện tại (an toàn)

Anh có thể:
- Copy block mapping ở mục (1) và dán vào cuối `~/.ideavimrc`.
- Nếu bị trùng mapping với cái anh đang có, ưu tiên giữ cái nào anh quen tay.

> Nếu anh muốn em làm luôn patch tự động vào `~/.ideavimrc` (giữ backup), nói em 1 câu là em làm.
