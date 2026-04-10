---
title: "BF1 AI — Docs Rules"
tags: [bf1, ai, rules, docs]
---

# Documentation & Formatting Rules

## 1. Pull Requests (PRs)
- **Language**: Vietnamese/English based on audience, but technical terms remain in English.
- **Style**: Use clear, scannable bullet points. No emojis unless specifically requested for flair.
- **Format Template**:
  - **Summary**: Concise explanation of what changed and why.
  - **Changes**: Technical list of file/logic changes.
  - **Configuration Required**: Explicitly mention if new DB migrations, env vars, or crons need to be applied.

## 2. DEVLOG.md Conventions
- **Location**: Top of `DEVLOG.md`.
- **Style**: Start with the Date. Focus on the *why* (decisions, trade-offs) and the *impact*.
- **Code Snippets**: Only include snippets if they demonstrate a new architectural pattern or are critical to understanding the change. Do not dump raw code unnecessarily.
- **Tone**: Keep it direct, objective, and simple.

## 3. General AI Writing Style
- Omit filler words, "Great question", or "Here is the code". Just output the requested content.
- Use Markdown lists and code blocks properly.
- If providing a bash command, wrap it in a `bash` code block. If writing Java, use `java`.