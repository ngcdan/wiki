---
title: "Quick Notes — Ghi chú thô"
tags: [notes, raw, inbox]
---

# Quick Notes

Inbox cho ghi chú thô chưa phân loại. Định kỳ review và phân bổ vào notes phù hợp.

> [!info] Archive
> Phiên bản quick-notes trước đây (1321 dòng) đã được archive thành `[[quick-notes-archive-260407]]` để review từng block và phân bổ vào notes phù hợp:
>
> - Flutter/DDD/SQL → `[[skills]]`
> - Mindset/redpill/frame/life lessons → `[[mindset]]` hoặc `[[rulebooks]]`
> - Caffeine/health → `[[life]]`
> - Expense tracking → `[[finance]]`
> - English vocab → `[[english]]`
> - DataTP ideas → `[[datatp-datatp-overview]]`
> - Sea Port Map tool → `research/`

## Inbox mới

### 2026-04-16 — ECC (everything-claude-code) cleanup/repair

Đã cài [[setup-env|ECC]] từ `forrestchang/andrej-karpathy-skills` + `affaan-m/everything-claude-code` vào `~/.claude/`.

Cleanup/repair sau này:

```bash
cd ~/tools/everything-claude-code
node scripts/install-apply.js --doctor   # diagnose
node scripts/install-apply.js --repair   # restore managed files
```

Backup settings.json: `~/.claude/settings.json.bak.20260416-212423`
Global CLAUDE.md (Karpathy skills): `~/.claude/CLAUDE.md`
