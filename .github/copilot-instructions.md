# Copilot instructions for this notes repo

## Big picture
- This repo is a personal knowledge base of Markdown notes (no application code). Treat it as documentation-first: collect raw notes, then help summarize/clean them.
- README.md is the source of truth for how notes should be structured and used.
- Use Vietnamese by default unless the note’s language is clearly different.

## Content patterns to follow
- Each file is a single topic; avoid mixing unrelated content. See ideas.md and weekly.md for typical structure.
- When adding time-based entries, use date headers in `YYYY-MM-DD` format (e.g., in weekly.md).
- Suggested note skeleton (from README.md):
  - `# Tiêu đề` → `## Bối cảnh` → `## Vấn đề` → `## Giải pháp/Quyết định` → `## Việc cần làm tiếp theo` → `## Lưu ý/Tham khảo`
- Short, scannable bullets are preferred; remove duplication and group by theme.
- Optional tags are plain bracketed words like `[backend]`, `[infra]`.

## Workflows and safety
- There are no build/test commands in this repo; edits are direct Markdown updates.
- Avoid destructive shell commands (e.g., `rm -rf`, `git reset --hard`) unless explicitly requested.

## Examples to anchor edits
- Date-indexed work log entries: weekly.md
- Raw ideation that may need cleanup: ideas.md
- Reference/cheatsheet style content: cheatsheets/cli.md

## When asked to “clean up” notes
- First standardize headings and terminology, then summarize into 3–7 bullets (context, decision, actions, risks).
- If details are missing, ask only for the specific missing facts instead of guessing.
