# Tmux Guide - Workflow & Concepts

> **Why Tmux?**
> 1. **Persistence:** Never lose your terminal state. Detach, close Kitty, come back later -> everything is still running.
> 2. **Context Switching:** Jump between projects (`backend`, `frontend`, `ops`) instantly without `cd`-ing around.
> 3. **Layout:** Split panes and windows exactly how you like them.

## 1. Core Workflow (The "Session" Mindset)

Instead of opening random tabs, organize work into **Sessions**:
- **Session = Project** (e.g., `of1-be`, `of1-fe`).
- **Window = Context** (e.g., `code`, `server`, `db`).
- **Pane = View** (e.g., split editor + logs).

**Golden Rule:** When done, **DETACH** (`Ctrl+a` `d`), don't exit.

## 2. Key Bindings (Custom Config: Prefix = `Ctrl+a`)

### Session Management
| Action | Key Binding | Command Equivalent |
| :--- | :--- | :--- |
| **Detach** (Leave running) | `Ctrl+a` `d` | `tmux detach` |
| **List/Switch Sessions** | `Ctrl+a` `s` | `tmux ls` |
| **Rename Session** | `Ctrl+a` `$` | `tmux rename-session` |
| **New Session** | (Terminal) | `tmux new -s <name>` |
| **Attach Session** | (Terminal) | `tmux a -t <name>` |

### Window (Tab) Management
| Action | Key Binding |
| :--- | :--- |
| **New Window** | `Ctrl+a` `c` |
| **Rename Window** | `Ctrl+a` `,` |
| **Go to Window 1..9** | `Ctrl+a` `1`..`9` |
| **Next/Prev Window** | `Ctrl+a` `n` / `p` |

### Pane (Split) Management
| Action | Key Binding |
| :--- | :--- |
| **Split Vertical** | `Ctrl+a` `|` |
| **Split Horizontal** | `Ctrl+a` `-` |
| **Move Focus** | `Ctrl+a` `h` `j` `k` `l` (Vim style) |
| **Zoom Pane** | `Ctrl+a` `z` (Maximize/Restore) |
| **Kill Pane** | `Ctrl+a` `x` |

## 3. Common Scenarios

### Scenario A: Starting Work
1. Open Kitty.
2. `tmux ls` (Check existing sessions).
3. `tmux a -t of1` (Resume work) OR `tmux new -s of1` (Start fresh).

### Scenario B: Context Switch
1. Working on Backend (`of1-be`).
2. Need to check Frontend logs?
3. `Ctrl+a` `s` -> Select `of1-fe` -> Enter.
4. Done? `Ctrl+a` `s` -> Back to `of1-be`.

### Scenario C: Emergency Exit
1. Computer freezing? Kitty crashing?
2. Just close the window.
3. Reopen -> `tmux a` -> Everything is saved.
