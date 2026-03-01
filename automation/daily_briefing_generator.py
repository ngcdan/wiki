#!/usr/bin/env python3
"""Daily Briefing Generator

Tự động tạo daily briefing từ multiple sources:
- PRs/Issues từ Forgejo
- Notes từ inbox
- BACKLOG changes
- Calendar events (optional)

Output: Markdown report với top priorities, in progress, blockers.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    from ai_classifier import AIClassifier
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class DailyBriefingGenerator:
    """Generate daily briefing from multiple sources."""

    def __init__(self, wiki_root: Path):
        self.wiki_root = wiki_root
        self.automation_dir = wiki_root / "automation"
        self.notes_dir = wiki_root / "notes"
        self.backlog_file = wiki_root / "BACKLOG.md"
        
        # Initialize AI for summarization
        self.classifier: Optional[AIClassifier] = None
        if AI_AVAILABLE:
            try:
                provider = os.getenv("AI_PROVIDER", "openai")
                self.classifier = AIClassifier(provider=provider)
            except Exception:
                pass

    def generate(self, output_path: Optional[Path] = None) -> str:
        """Generate daily briefing and optionally save to file."""
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        
        if output_path is None:
            output_path = self.notes_dir / "daily" / f"{date_str}_briefing.md"
        
        # Collect data from sources
        prs_summary = self._get_prs_summary()
        issues_summary = self._get_issues_summary()
        backlog_summary = self._get_backlog_summary()
        inbox_items = self._get_inbox_items()
        
        # Generate briefing
        briefing = self._build_briefing(
            date_str=date_str,
            prs=prs_summary,
            issues=issues_summary,
            backlog=backlog_summary,
            inbox=inbox_items,
        )
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(briefing, encoding="utf-8")
        
        return briefing

    def _get_prs_summary(self) -> Dict:
        """Get PR summary from team_prs_summary.md."""
        pr_file = self.automation_dir / "team_prs_summary.md"
        if not pr_file.exists():
            return {"total": 0, "items": []}
        
        content = pr_file.read_text(encoding="utf-8")
        # Simple parsing - count PRs
        pr_count = content.count("- #")
        return {"total": pr_count, "content": content[:500]}

    def _get_issues_summary(self) -> Dict:
        """Get issues summary from data/team_issues_summary.md."""
        issue_file = self.automation_dir / "data" / "team_issues_summary.md"
        if not issue_file.exists():
            return {"total": 0, "items": []}
        
        content = issue_file.read_text(encoding="utf-8")
        issue_count = content.count("- #")
        return {"total": issue_count, "content": content[:500]}

    def _get_backlog_summary(self) -> Dict:
        """Extract top priorities from BACKLOG.md."""
        if not self.backlog_file.exists():
            return {"priorities": [], "in_progress": [], "blocked": []}
        
        content = self.backlog_file.read_text(encoding="utf-8")
        
        # Extract Current focus section
        priorities = []
        if "## Current focus" in content:
            focus_section = content.split("## Current focus")[1].split("##")[0]
            for line in focus_section.split("\n"):
                if line.strip().startswith("- [ ]"):
                    priorities.append(line.strip()[6:])
        
        return {
            "priorities": priorities[:5],  # Top 5
            "total_items": len(priorities),
        }

    def _get_inbox_items(self) -> List[str]:
        """Get items from inbox directory."""
        inbox_dir = self.notes_dir / "00_inbox"
        if not inbox_dir.exists():
            return []
        
        items = []
        for file in inbox_dir.glob("*.md"):
            if file.name != "index.md":
                items.append(file.stem)
        
        return items

    def _build_briefing(
        self,
        date_str: str,
        prs: Dict,
        issues: Dict,
        backlog: Dict,
        inbox: List[str],
    ) -> str:
        """Build the briefing markdown."""
        lines = [
            f"# Daily Briefing - {date_str}",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 📊 Summary",
            "",
            f"- **PRs:** {prs['total']} active",
            f"- **Issues:** {issues['total']} active",
            f"- **Backlog items:** {backlog.get('total_items', 0)}",
            f"- **Inbox items:** {len(inbox)}",
            "",
            "## 🎯 Top Priorities (from BACKLOG)",
            "",
        ]
        
        if backlog.get("priorities"):
            for i, priority in enumerate(backlog["priorities"], 1):
                lines.append(f"{i}. {priority}")
        else:
            lines.append("- (no priorities found)")
        
        lines.extend([
            "",
            "## 📥 Inbox Items",
            "",
        ])
        
        if inbox:
            for item in inbox[:10]:  # Top 10
                lines.append(f"- {item}")
        else:
            lines.append("- (inbox empty)")
        
        lines.extend([
            "",
            "## 📝 Recent Activity",
            "",
            f"**PRs:** {prs['total']} active",
            f"**Issues:** {issues['total']} active",
            "",
            "---",
            "",
            "## 🚀 Next 24h Focus",
            "",
            "1. Review and triage inbox items (11:00 batch)",
            "2. Process top priority tasks",
            "3. Team sync and updates",
            "4. Afternoon inbox batch (16:00)",
            "",
            "## 📌 Notes",
            "",
            "- Remember: Batch inbox processing at 11:00 and 16:00",
            "- Focus on P0/P1 items first",
            "- Update BACKLOG as tasks complete",
            "",
        ])
        
        return "\n".join(lines)


def main():
    """Main entry point."""
    wiki_root = Path("/Users/nqcdan/dev/wiki")
    generator = DailyBriefingGenerator(wiki_root)
    
    briefing = generator.generate()
    print("✅ Daily briefing generated")
    print(f"📄 Location: {wiki_root}/notes/daily/{datetime.now().strftime('%Y-%m-%d')}_briefing.md")
    print()
    print("Preview:")
    print("=" * 60)
    print(briefing[:500])
    print("...")


if __name__ == "__main__":
    main()
