#!/usr/bin/env python3
"""Forgejo Issue Collector (Markdown Summary)

Quick run

1) Ensure venv is ready (one-time):

    cd /Users/nqcdan/dev/wiki/automation
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

2) Configure env (do NOT commit):

    # file: /Users/nqcdan/dev/wiki/automation/.env
    FORGEJO_URL=https://git.datatp.cloud
    FORGEJO_TOKEN=***
    FORGEJO_OWNER=of1-crm
    FORGEJO_REPOS=of1-crm

    # Optional:
    ISSUE_STATE=all          # open|closed|all (default: all)
    DAYS_BACK=3              # only include issues updated within N days (default: 3; set None for all)
    OUTPUT_ISSUES_FILE=/Users/nqcdan/dev/wiki/automation/team_issues_summary.md

3) Run:

    cd /Users/nqcdan/dev/wiki/automation
    set -a && source .env && set +a
    ./.venv/bin/python forgejo_issue_collector.py

Purpose
- Fetch issues from Forgejo (Gitea-compatible API) using a token.
- Write a markdown summary file (no backlog mutation by default).

Notes
- Uses /api/v1/repos/{owner}/{repo}/issues?type=issues so PRs are excluded.
- If DAYS_BACK is set, filters by updated_at >= now - DAYS_BACK.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    token: str
    owner: str
    repos: List[str]
    state: str
    days_back: Optional[int]

    # Outputs
    output_file: Path
    personal_backlog_file: Path
    crm_backlog_file: Optional[Path]


class ConfigBuilder:
    @staticmethod
    def maybe_load_dotenv(dotenv_path: Path) -> None:
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv(dotenv_path=dotenv_path, override=False)
        except Exception:
            return

    @staticmethod
    def _csv(values: Optional[str]) -> List[str]:
        if not values:
            return []
        return [v.strip() for v in values.split(",") if v.strip()]

    @staticmethod
    def build(argv: Optional[List[str]] = None) -> CollectorConfig:
        script_dir = Path(__file__).resolve().parent
        ConfigBuilder.maybe_load_dotenv(script_dir / ".env")

        parser = argparse.ArgumentParser(description="Forgejo Issue Collector")
        parser.add_argument("--url", default=os.getenv("FORGEJO_URL"), help="Forgejo base URL")
        parser.add_argument("--token", default=os.getenv("FORGEJO_TOKEN"), help="Forgejo access token")
        parser.add_argument("--owner", default=os.getenv("FORGEJO_OWNER"), help="Repo owner/org")
        parser.add_argument(
            "--repos",
            default=os.getenv("FORGEJO_REPOS"),
            help="Comma-separated repo list (e.g. of1-crm,of1-tms)",
        )
        parser.add_argument(
            "--state",
            default=os.getenv("ISSUE_STATE", "closed"),
            choices=["open", "closed", "all"],
            help="Issue state to fetch",
        )
        parser.add_argument(
            "--days-back",
            default=os.getenv("DAYS_BACK", "3"),
            help="Only include issues updated within N days (omit/None for all)",
        )
        parser.add_argument(
            "--output-file",
            default=os.getenv("OUTPUT_ISSUES_FILE") or str(script_dir / "team_issues_summary.md"),
            help="Markdown file to write summary to",
        )
        parser.add_argument(
            "--backlog-file",
            default=os.getenv("BACKLOG_FILE") or str((script_dir.parent / "BACKLOG.md")),
            help="Personal wiki backlog markdown file to update (Issues section)",
        )
        parser.add_argument(
            "--crm-backlog-file",
            default=os.getenv("CRM_BACKLOG_FILE") or str((script_dir.parent / "work" / "OF1_Crm" / "BACKLOG.md")),
            help="OF1_Crm backlog markdown file to update (Features + Bugs/Enhancements/Maintenance sections). Use None to disable.",
        )

        args = parser.parse_args(argv)

        if not args.url:
            raise SystemExit("❌ Missing Forgejo URL. Provide --url or set FORGEJO_URL")
        if not args.token:
            raise SystemExit("❌ Missing token. Provide --token or set FORGEJO_TOKEN")
        if not args.owner:
            raise SystemExit("❌ Missing owner. Provide --owner or set FORGEJO_OWNER")

        repos = ConfigBuilder._csv(args.repos)
        if not repos:
            raise SystemExit("❌ Missing repos. Provide --repos or set FORGEJO_REPOS")

        if args.days_back in (None, "", "None"):
            days_back: Optional[int] = None
        else:
            days_back = int(args.days_back)

        crm_file: Optional[Path] = None
        if args.crm_backlog_file not in (None, "", "None"):
            crm_file = Path(args.crm_backlog_file).expanduser().resolve()

        return CollectorConfig(
            base_url=str(args.url),
            token=str(args.token),
            owner=str(args.owner),
            repos=repos,
            state=str(args.state),
            days_back=days_back,
            output_file=Path(args.output_file).expanduser().resolve(),
            personal_backlog_file=Path(args.backlog_file).expanduser().resolve(),
            crm_backlog_file=crm_file,
        )


# -----------------------------------------------------------------------------
# Forgejo API
# -----------------------------------------------------------------------------


class ForgejoClient:
    def __init__(self, base_url: str, token: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        }

    def iter_issues(
        self,
        owner: str,
        repo: str,
        state: str,
        *,
        limit: int = 100,
    ) -> Iterable[Dict]:
        url = f"{self._base_url}/api/v1/repos/{owner}/{repo}/issues"

        page = 1
        while True:
            params = {
                "state": state,
                "type": "issues",  # important: exclude PRs
                "sort": "updated",
                "direction": "desc",
                "limit": limit,
                "page": page,
            }

            resp = requests.get(url, headers=self._headers, params=params, timeout=30)
            resp.raise_for_status()

            data = resp.json() or []
            if not data:
                break

            for issue in data:
                yield issue

            if len(data) < limit:
                break
            page += 1


# -----------------------------------------------------------------------------
# Domain helpers
# -----------------------------------------------------------------------------


class Iso:
    @staticmethod
    def parse(dt: str) -> datetime:
        # Example: 2026-02-11T03:41:08Z
        if dt.endswith("Z"):
            return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        # Fallback: try fromisoformat
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))

    @staticmethod
    def date(dt: str) -> str:
        try:
            return Iso.parse(dt).astimezone(timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            return str(dt)[:10]


class Issue:
    IGNORE_TITLES = {
        "Excel Jobs (BEE HPH)",
        "BF1 References",
        "DB CHANGELOG",
        "TECHNICAL DEBT",
    }

    @staticmethod
    def id(issue: Dict) -> Optional[int]:
        v = issue.get("number")
        try:
            return int(v)
        except Exception:
            return None

    @staticmethod
    def title(issue: Dict) -> str:
        return str(issue.get("title") or "").strip()

    @staticmethod
    def should_ignore(issue: Dict) -> bool:
        return Issue.title(issue) in Issue.IGNORE_TITLES

    @staticmethod
    def body(issue: Dict) -> str:
        return str(issue.get("body") or "").strip()

    @staticmethod
    def body_without_images(issue: Dict) -> str:
        """Return issue body with image-only markdown lines removed.

        Remove lines that look like: ![alt](url)
        (We treat any line starting with '![' after trim as an image line.)
        """
        body = Issue.body(issue)
        if not body:
            return ""

        kept: List[str] = []
        for raw in body.splitlines():
            line = raw.rstrip()
            if line.strip().startswith("!["):
                continue
            kept.append(line)

        # Trim leading/trailing blank lines after removals
        out = "\n".join(kept).strip("\n").rstrip()
        return out

    @staticmethod
    def desc_full(issue: Dict) -> str:
        """Full description (body) excluding image lines."""
        txt = Issue.body_without_images(issue)
        return txt if txt else ""  # omit when empty

    @staticmethod
    def html_url(issue: Dict) -> str:
        return str(issue.get("html_url") or "").strip()

    @staticmethod
    def state(issue: Dict) -> str:
        return str(issue.get("state") or "").strip()

    @staticmethod
    def updated_at(issue: Dict) -> str:
        return str(issue.get("updated_at") or "").strip()

    @staticmethod
    def created_at(issue: Dict) -> str:
        return str(issue.get("created_at") or "").strip()

    @staticmethod
    def closed_at(issue: Dict) -> str:
        return str(issue.get("closed_at") or "").strip()

    @staticmethod
    def user_login(issue: Dict) -> str:
        user = issue.get("user") or {}
        return str(user.get("login") or "").strip()

    @staticmethod
    def labels(issue: Dict) -> List[str]:
        labels = issue.get("labels") or []
        out: List[str] = []
        for lb in labels:
            name = str((lb or {}).get("name") or "").strip()
            if name:
                out.append(name)
        return out

    @staticmethod
    def assignees(issue: Dict) -> List[str]:
        assignees = issue.get("assignees") or []
        out: List[str] = []
        for a in assignees:
            login = str((a or {}).get("login") or "").strip()
            if login:
                out.append(login)
        return out


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------


class MarkdownRenderer:
    @staticmethod
    def render_snapshot(cfg: CollectorConfig, by_repo: Dict[str, List[Dict]]) -> str:
        now_local = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        lines: List[str] = []
        lines.append("# Forgejo Issues Snapshot")
        lines.append("")
        lines.append(f"- Generated: {now_local}")
        lines.append(f"- Owner: `{cfg.owner}`")
        lines.append(f"- Repos: {', '.join([f'`{r}`' for r in cfg.repos])}")
        lines.append(f"- State: `{cfg.state}`")
        lines.append(f"- Days back: `{cfg.days_back}`")
        lines.append("")

        total = sum(len(v) for v in by_repo.values())
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total issues: **{total}**")
        for repo, issues in by_repo.items():
            lines.append(f"- `{repo}`: **{len(issues)}**")
        lines.append("")

        for repo, issues in by_repo.items():
            lines.append(f"## {repo}")
            lines.append("")
            if not issues:
                lines.append("- (none)")
                lines.append("")
                continue

            for it in issues:
                iid = Issue.id(it)
                title = Issue.title(it)
                url = Issue.html_url(it)
                state = Issue.state(it)
                updated = Issue.updated_at(it)
                created = Issue.created_at(it)
                author = Issue.user_login(it)
                labels = Issue.labels(it)
                assignees = Issue.assignees(it)

                tags: List[str] = []
                if labels:
                    tags.append("labels=" + ", ".join(labels))
                if assignees:
                    tags.append("assignees=" + ", ".join(assignees))
                tag_text = f" ({'; '.join(tags)})" if tags else ""

                updated_d = Iso.date(updated) if updated else ""
                created_d = Iso.date(created) if created else ""

                prefix = f"- #{iid}" if iid is not None else "-"
                lines.append(
                    f"{prefix} **{title}** — {state} | created {created_d} | updated {updated_d} | by {author}{tag_text}\n  - {url}"
                )

            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


class BacklogUpdater:
    """Update BACKLOG.md by upserting an Issues section."""

    _SECTION_HEADER = "## BACKLOG - Issues"

    @staticmethod
    def _find_section_range(md: str, header: str) -> Optional[tuple[int, int]]:
        """Return (start_idx, end_idx) slice for the whole section, or None."""
        lines = md.splitlines(keepends=True)

        start_line = None
        for i, line in enumerate(lines):
            if line.strip() == header:
                start_line = i
                break

        if start_line is None:
            return None

        end_line = len(lines)
        for j in range(start_line + 1, len(lines)):
            if lines[j].startswith("## "):
                end_line = j
                break

        start_idx = sum(len(l) for l in lines[:start_line])
        end_idx = sum(len(l) for l in lines[:end_line])
        return start_idx, end_idx

    @staticmethod
    def _insert_pos(md: str) -> int:
        """Insert before '## Automation' if present, else append."""
        needle = "\n## Automation"
        idx = md.find(needle)
        if idx >= 0:
            return idx + 1  # keep leading newline
        return len(md)

    @staticmethod
    def _render_issue_block(repo: str, issue: Dict) -> str:
        iid = Issue.id(issue)
        title = Issue.title(issue)
        url = Issue.html_url(issue)
        state = Issue.state(issue)
        labels = Issue.labels(issue)
        assignees = Issue.assignees(issue)
        updated = Iso.date(Issue.updated_at(issue)) if Issue.updated_at(issue) else ""

        out: List[str] = []
        if iid is not None:
            out.append(f"#### #{iid} {title}")
        else:
            out.append(f"#### {title}")

        out.append(f"- **Repo:** {repo}")
        out.append(f"- **Link:** {url}")
        if labels:
            out.append(f"- **Labels:** {', '.join(labels)}")
        if assignees:
            out.append(f"- **Assignee:** {', '.join([f'@{a}' for a in assignees])}")
        else:
            out.append("- **Assignee:** (unassigned)")
        out.append(f"- **Status:** {state}")
        if updated:
            out.append(f"- **Updated at:** {updated}")
        return "\n".join(out) + "\n\n"

    @staticmethod
    def _sort_key(issue: Dict) -> tuple:
        # open first, then closed; then updated_at desc; then id desc
        state = Issue.state(issue)
        state_rank = 0 if state == "open" else 1

        updated = Issue.updated_at(issue)
        try:
            updated_ts = Iso.parse(updated).timestamp() if updated else 0
        except Exception:
            updated_ts = 0

        iid = Issue.id(issue) or 0
        return (state_rank, -updated_ts, -iid)

    @staticmethod
    def update_backlog(cfg: CollectorConfig, by_repo: Dict[str, List[Dict]]) -> None:
        backlog_path = cfg.personal_backlog_file
        md = backlog_path.read_text(encoding="utf-8") if backlog_path.exists() else ""

        blocks: List[str] = []
        blocks.append(BacklogUpdater._SECTION_HEADER + "\n")
        blocks.append("\n")

        all_items: List[tuple[str, Dict]] = []
        for repo, items in by_repo.items():
            for it in items:
                all_items.append((repo, it))

        all_items.sort(key=lambda x: BacklogUpdater._sort_key(x[1]))

        if not all_items:
            blocks.append("- (none)\n")
        else:
            for repo, it in all_items:
                blocks.append(BacklogUpdater._render_issue_block(repo, it))

        new_section = "".join(blocks).rstrip() + "\n\n"

        rng = BacklogUpdater._find_section_range(md, BacklogUpdater._SECTION_HEADER)
        if rng:
            start, end = rng
            md2 = md[:start] + new_section + md[end:]
        else:
            pos = BacklogUpdater._insert_pos(md)
            sep = "\n" if md and not md.endswith("\n") else ""
            md2 = md[:pos] + sep + new_section + md[pos:]

        backlog_path.write_text(md2, encoding="utf-8")


# -----------------------------------------------------------------------------
# CRM backlog updater (OF1_Crm/BACKLOG.md)
# -----------------------------------------------------------------------------


class CrmIssueBacklogRenderer:
    """Render an Issue block template for OF1_Crm backlog (numbering applied later)."""

    def render_template(self, repo: str, issue: Dict) -> str:
        state = Issue.state(issue)
        if state == "open":
            tag = "In Progress"
        else:
            closed_at = Issue.closed_at(issue)
            tag = Iso.date(closed_at) if closed_at else Iso.date(Issue.updated_at(issue))

        title = Issue.title(issue) or "(no title)"
        desc = Issue.desc_full(issue)
        url = Issue.html_url(issue)
        assignees = Issue.assignees(issue)
        ass = ", ".join([f"@{a}" for a in assignees]) if assignees else "(unassigned)"

        body_block = ""
        if str(desc).strip():
            body_lines = str(desc).splitlines()
            indented_body: List[str] = []
            for line in body_lines:
                # Keep markdown as-is (no '>'), just indent to match existing PR style
                indented_body.append(f"    {line}" if line.strip() else "")
            body_block = "\n".join(indented_body).rstrip() + "\n"

        return (
            f"#### {{n}}. [{tag}] - {title}\n"
            f"{body_block}\n"
            f"   **Link:** {url}\n"
            f"   **Assignee:** {ass}\n"
        )


class CrmIssueBacklogUpdater:
    """Update OF1_Crm backlog by syncing issues into a *safe auto-managed block*.

    Why:
    - The CRM wiki backlog under `## [Unreleased]` contains long-form notes (often generated by PR collector).
    - We must never replace the entire `[Unreleased]` section, otherwise we risk wiping that content.

    Approach:
    - Ensure `## [Unreleased]` exists.
    - Ensure an `### Issues` heading exists.
    - Manage ONLY the content between markers:

        <!-- AUTO:ISSUES:BEGIN -->
        ... generated ...
        <!-- AUTO:ISSUES:END -->

    This is robust even if the rest of the file uses `#### ...` entries.
    """

    UNRELEASED_HEADER = "## [Unreleased]"
    ISSUES_HEADING = "### Issues"
    MARK_BEGIN = "<!-- AUTO:ISSUES:BEGIN -->"
    MARK_END = "<!-- AUTO:ISSUES:END -->"

    def __init__(self, path: Path, renderer: CrmIssueBacklogRenderer):
        self._path = path
        self._renderer = renderer

    def sync(self, by_repo: Dict[str, List[Dict]]) -> None:
        text = self._path.read_text(encoding="utf-8")

        text = self._ensure_section(text, self.UNRELEASED_HEADER)
        text = self._ensure_issues_block(text)

        items: List[Tuple[str, Dict]] = []
        for repo, issues in by_repo.items():
            for it in issues:
                items.append((repo, it))

        body = self._build_block_body(text, items)
        text = self._replace_between_markers(text, body)

        self._path.write_text(text, encoding="utf-8")
        print(f"✅ CRM backlog updated: {self._path}")

    @staticmethod
    def _ensure_section(text: str, header: str) -> str:
        if header in text:
            return text

        # Insert after first H1 if possible, else append
        import re

        m = re.search(r"^#\s+.*$", text, flags=re.M)
        insert_at = m.end(0) + 1 if m else len(text)
        return text[:insert_at] + f"\n\n{header}\n\n" + text[insert_at:]

    def _ensure_issues_block(self, text: str) -> str:
        # If markers already exist, we're good.
        if self.MARK_BEGIN in text and self.MARK_END in text:
            return text

        # Ensure heading exists.
        if self.ISSUES_HEADING not in text:
            # Insert heading right after `## [Unreleased]` line.
            start = text.find(self.UNRELEASED_HEADER)
            line_end = text.find("\n", start) if start != -1 else -1
            insert_at = line_end + 1 if line_end != -1 else len(text)
            text = text[:insert_at] + f"\n{self.ISSUES_HEADING}\n\n" + text[insert_at:]

        # Insert markers right after the Issues heading line.
        h_start = text.find(self.ISSUES_HEADING)
        h_line_end = text.find("\n", h_start)
        insert_at = h_line_end + 1 if h_line_end != -1 else len(text)

        block = (
            f"\n{self.MARK_BEGIN}\n"
            f"- (none)\n"
            f"{self.MARK_END}\n"
        )

        return text[:insert_at] + block + text[insert_at:]

    def _replace_between_markers(self, text: str, new_body: str) -> str:
        start = text.find(self.MARK_BEGIN)
        end = text.find(self.MARK_END)
        if start == -1 or end == -1 or end < start:
            return text

        start_line_end = text.find("\n", start)
        body_start = start_line_end + 1 if start_line_end != -1 else start + len(self.MARK_BEGIN)

        body_end = end

        nb = new_body.rstrip() + "\n"
        return text[:body_start] + nb + text[body_end:]

    @staticmethod
    def _extract_blocks_by_id(body: str) -> Dict[int, str]:
        """Map ISSUE_ID -> template block (normalize numbering to #### {n}.)"""
        import re

        block_re = re.compile(r"(?ms)^####\s+\d+\.\s+\[[^\]]+\]\s+-\s+.*?(?=^####\s+\d+\.\s+\[|\Z)")

        out: Dict[int, str] = {}
        for m in block_re.finditer(body):
            blk = m.group(0)
            blk = re.sub(r"^####\s+\d+\.", "#### {n}.", blk, flags=re.M)
            m_id = re.search(r"/issues/(\d+)\b", blk)
            if not m_id:
                continue
            iid = int(m_id.group(1))
            out[iid] = blk.strip()
        return out

    def _build_block_body(self, full_text: str, items: List[Tuple[str, Dict]]) -> str:
        # Only look at the current auto block content for incremental updates.
        start = full_text.find(self.MARK_BEGIN)
        end = full_text.find(self.MARK_END)
        existing_body = ""
        if start != -1 and end != -1 and end > start:
            start_line_end = full_text.find("\n", start)
            body_start = start_line_end + 1 if start_line_end != -1 else start + len(self.MARK_BEGIN)
            existing_body = full_text[body_start:end]

        by_id = self._extract_blocks_by_id(existing_body)

        fetched_ids: set[int] = set()
        for repo, issue in items:
            iid = Issue.id(issue)
            if iid is None:
                continue
            fetched_ids.add(iid)

            tmpl = self._renderer.render_template(repo, issue).strip()
            if by_id.get(iid, "").strip() != tmpl:
                by_id[iid] = tmpl

        for existing_id in list(by_id.keys()):
            if existing_id not in fetched_ids:
                by_id.pop(existing_id, None)

        sorted_items = sorted(by_id.items(), key=self._crm_sort_key, reverse=True)

        rebuilt: List[str] = []
        for i, (_, tmpl) in enumerate(sorted_items, start=1):
            rebuilt.append(tmpl.replace("{n}", str(i)).rstrip())

        if not rebuilt:
            return "- (none)"

        return "\n\n".join(rebuilt).rstrip()

    @staticmethod
    def _crm_sort_key(item: Tuple[int, str]) -> Tuple[str, int]:
        import re

        iid, blk = item
        m = re.search(r"\[(\d{4}-\d{2}-\d{2}|In Progress)\]", blk)
        tag = m.group(1) if m else "In Progress"

        tag_key = "9999-99-99" if tag == "In Progress" else tag
        return (tag_key, iid)


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------


class App:
    def __init__(self, cfg: CollectorConfig):
        self._cfg = cfg
        self._client = ForgejoClient(cfg.base_url, cfg.token)

    def _cutoff(self) -> Optional[datetime]:
        if self._cfg.days_back is None:
            return None
        return datetime.now(timezone.utc) - timedelta(days=int(self._cfg.days_back))

    def run(self) -> None:
        print("🚀 Forgejo Issue Collector")
        print("=" * 50)

        cutoff = self._cutoff()
        if cutoff:
            print(f"🕒 Filtering: updated_at >= {cutoff.isoformat()}")

        by_repo: Dict[str, List[Dict]] = {}

        for repo in self._cfg.repos:
            print(f"📥 Fetching issues from {repo}...")
            items: List[Dict] = []
            for issue in self._client.iter_issues(self._cfg.owner, repo, self._cfg.state):
                # Safety: ensure PRs are excluded even if server ignores type param
                if issue.get("pull_request") is not None:
                    continue

                # Ignore internal tracking/meta tasks by title
                if Issue.should_ignore(issue):
                    continue

                if cutoff:
                    updated_at = Issue.updated_at(issue)
                    if updated_at:
                        try:
                            if Iso.parse(updated_at) < cutoff:
                                continue
                        except Exception:
                            pass
                items.append(issue)

            print(f"   ✓ Found {len(items)} issues")
            by_repo[repo] = items

        content = MarkdownRenderer.render_snapshot(self._cfg, by_repo)
        self._cfg.output_file.parent.mkdir(parents=True, exist_ok=True)
        self._cfg.output_file.write_text(content, encoding="utf-8")
        print(f"✅ Wrote snapshot: {self._cfg.output_file}")

        BacklogUpdater.update_backlog(self._cfg, by_repo)
        print(f"✅ Backlog updated: {self._cfg.personal_backlog_file}")

        if self._cfg.crm_backlog_file:
            CrmIssueBacklogUpdater(self._cfg.crm_backlog_file, CrmIssueBacklogRenderer()).sync(by_repo)

        print("✨ Done!")


def main() -> None:
    cfg = ConfigBuilder.build()
    App(cfg).run()


if __name__ == "__main__":
    main()
