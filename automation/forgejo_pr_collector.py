#!/usr/bin/env python3
"""Forgejo PR Collector (Backlog Sync)

Quick run

1) Ensure venv is ready (one-time):

    cd /Users/nqcdan/dev/wiki/automation
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

2) Configure env (do NOT commit):

    # file: /Users/nqcdan/dev/wiki/automation/.env
    FORGEJO_URL=http://forgejo.of1-apps.svc.cluster.local
    FORGEJO_TOKEN=***
    FORGEJO_OWNER=of1-crm
    FORGEJO_REPOS=of1-crm
    PR_STATE=all
    DAYS_BACK=3

3) Run (common):

    cd /Users/nqcdan/dev/wiki/automation
    source .venv/bin/activate
    set -a && source .env && set +a

    # update both backlogs (default paths)
    python forgejo_pr_collector.py --state all --days-back 7

    # update only personal backlog
    python forgejo_pr_collector.py --crm-backlog-file None

    # update only OF1_Crm backlog
    python forgejo_pr_collector.py --backlog-file /dev/null --crm-backlog-file /Users/nqcdan/dev/wiki/work/OF1_Crm/BACKLOG.md

Purpose
- Fetch pull requests from Forgejo (Gitea-compatible API) using a token.
- Sync summaries into markdown backlogs.

Outputs
1) Personal wiki backlog: /Users/nqcdan/dev/wiki/BACKLOG.md
   - Updates only section: "## BACKLOG - Team"
   - Detects blocks by PR id: "#### #<id> ..."

2) OF1 CRM backlog: /Users/nqcdan/dev/wiki/work/OF1_Crm/BACKLOG.md (symlink)
   - Updates sections:
     - "## Features"
     - "## Bugs / Enhancements / Maintenance"
   - Detects blocks by PR id from link: /pulls/<id>

Rules (as requested)
- Only include PRs that have non-empty description (body).
- Keep PRs that are OPEN or MERGED; drop CLOSED-but-not-merged.
- Idempotent: detect PR by id and replace existing entry, else append.
- CRM backlog ordering: In Progress (not merged) first, then merged by date desc, then id desc.
- CRM backlog tag: "[In Progress]" for open PRs, otherwise "[YYYY-MM-DD]" from merged_at.

Style
- Prefer OO/class style (Java-ish organization): small cohesive classes, explicit responsibilities.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CollectorConfig:
    """CollectorConfig: helper class. See top docstring for overall flow."""
    base_url: str
    token: str
    owner: str
    repos: List[str]
    state: str
    days_back: Optional[int]

    # Output paths
    personal_backlog_file: Path
    crm_backlog_file: Optional[Path]


class ConfigBuilder:
    """Parse CLI + .env into a CollectorConfig."""

    @staticmethod
    def maybe_load_dotenv(dotenv_path: Path) -> None:
        """Load .env best-effort if python-dotenv is installed."""

        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv(dotenv_path=dotenv_path, override=False)
        except Exception:
            return

    @staticmethod
    def _csv(values: Optional[str]) -> List[str]:
        """Internal helper: _csv."""
        if not values:
            return []
        return [v.strip() for v in values.split(",") if v.strip()]

    @staticmethod
    def build(argv: Optional[List[str]] = None) -> CollectorConfig:
        """build: function helper. See module docstring for behavior."""
        script_dir = Path(__file__).resolve().parent
        ConfigBuilder.maybe_load_dotenv(script_dir / ".env")

        parser = argparse.ArgumentParser(description="Forgejo PR Collector")
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
            default=os.getenv("PR_STATE", "all"),
            choices=["open", "closed", "all"],
            help="PR state to fetch",
        )
        parser.add_argument(
            "--days-back",
            default=os.getenv("DAYS_BACK", "3"),
            help="Only include PRs updated within N days (omit/None for all)",
        )
        parser.add_argument(
            "--backlog-file",
            default=os.getenv("BACKLOG_FILE") or str((script_dir.parent / "BACKLOG.md")),
            help="Personal wiki backlog markdown file to update (Team section)",
        )
        parser.add_argument(
            "--crm-backlog-file",
            default=os.getenv("CRM_BACKLOG_FILE")
            or str((script_dir.parent / "work" / "OF1_Crm" / "BACKLOG.md")),
            help="OF1_Crm backlog markdown file to update (Features + Bugs/Enhancements/Maintenance sections)",
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
            personal_backlog_file=Path(args.backlog_file).expanduser().resolve(),
            crm_backlog_file=crm_file,
        )


# -----------------------------------------------------------------------------
# Forgejo API
# -----------------------------------------------------------------------------


class ForgejoClient:
    """Minimal Forgejo API client for pull requests."""

    def __init__(self, base_url: str, token: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        }

    def iter_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str,
        *,
        limit: int = 100,
    ) -> Iterable[Dict]:
        url = f"{self._base_url}/api/v1/repos/{owner}/{repo}/pulls"

        page = 1
        while True:
            params = {
                "state": state,
                "sort": "recentupdate",
                "limit": limit,
                "page": page,
            }

            resp = requests.get(url, headers=self._headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json() or []
            if not data:
                break

            for pr in data:
                yield pr

            if len(data) < limit:
                break
            page += 1


# -----------------------------------------------------------------------------
# PR domain helpers ("service" style)
# -----------------------------------------------------------------------------


class Pr:
    """Static helpers to read Forgejo PR dicts safely."""

    @staticmethod
    def parse_iso_z(dt: str) -> datetime:
        """parse_iso_z: function helper. See module docstring for behavior."""
        return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def iso_date(iso_z: str) -> str:
        """iso_date: function helper. See module docstring for behavior."""
        try:
            return Pr.parse_iso_z(str(iso_z)).strftime("%Y-%m-%d")
        except Exception:
            return str(iso_z)[:10]

    @staticmethod
    def id(pr: Dict) -> Optional[int]:
        """id: function helper. See module docstring for behavior."""
        n = pr.get("number")
        return int(n) if isinstance(n, int) else None

    @staticmethod
    def is_merged(pr: Dict) -> bool:
        """is_merged: function helper. See module docstring for behavior."""
        return pr.get("merged") is True or bool(pr.get("merged_at"))

    @staticmethod
    def has_description(pr: Dict) -> bool:
        """has_description: function helper. See module docstring for behavior."""
        body = pr.get("body")
        return isinstance(body, str) and body.strip() != ""

    @staticmethod
    def should_include(pr: Dict) -> bool:
        """should_include: function helper. See module docstring for behavior."""
        # Keep: open + merged. Drop: closed-but-not-merged.
        return pr.get("state") == "open" or Pr.is_merged(pr)

    @staticmethod
    def labels(pr: Dict) -> List[str]:
        """labels: function helper. See module docstring for behavior."""
        labels = pr.get("labels")
        if not isinstance(labels, list):
            return []
        out: List[str] = []
        for lb in labels:
            if isinstance(lb, dict) and lb.get("name"):
                out.append(str(lb["name"]))
        return out

    @staticmethod
    def assignees(pr: Dict) -> str:
        """assignees: function helper. See module docstring for behavior."""
        def fmt_user(u: Dict) -> str:
            """fmt_user: function helper. See module docstring for behavior."""
            login = u.get("login") or "unknown"
            name = u.get("full_name") or u.get("name") or ""
            return f"@{login}" + (f" ({name})" if name and name != login else "")

        assignees = pr.get("assignees")
        if isinstance(assignees, list) and assignees:
            return ", ".join(fmt_user(a or {}) for a in assignees)

        assignee = pr.get("assignee")
        if isinstance(assignee, dict) and assignee:
            return fmt_user(assignee)

        return "(unassigned)"

    @staticmethod
    def first_line_desc(pr: Dict) -> str:
        """first_line_desc: function helper. See module docstring for behavior."""
        body = (pr.get("body") or "").strip()
        for ln in body.splitlines():
            if ln.strip():
                return ln.strip()
        return ""

    @staticmethod
    def clean_title_title_only(title: str) -> str:
        """Remove tags/issue refs so backlog is 'Title only'."""

        t = (title or "").strip()

        # Remove any [Tag] anywhere (e.g. [Enhancement])
        t = re.sub(r"\[[^\]]+\]", "", t)

        # Remove leading verbs like Fixes/Closes/Refs/Issues with refs
        t = re.sub(
            r"^(Closes|Fixes|Resolves|Refs?|Issues?)\s+(#\d+)(\s*[+,/]\s*#\d+)*\s*[-:]*\s*",
            "",
            t,
            flags=re.I,
        )

        # Remove any remaining '#123'
        t = re.sub(r"#\d+", "", t)

        # Normalize whitespace/punctuation
        t = re.sub(r"\s+", " ", t).strip()
        t = t.strip("-:–— ").rstrip(".")
        return t


# -----------------------------------------------------------------------------
# Renderers
# -----------------------------------------------------------------------------


class PersonalBacklogRenderer:
    """Render one PR block for personal wiki BACKLOG - Team."""

    def render(self, pr: Dict) -> str:
        """render: function helper. See module docstring for behavior."""
        pid = Pr.id(pr)
        title = pr.get("title") or "(no title)"
        title = re.sub(r"^\s*#\d+\s*[-:]*\s*", "", title).strip()

        url = pr.get("html_url") or ""

        state = pr.get("state") or "unknown"
        merged_at = pr.get("merged_at")
        status = "merged" if Pr.is_merged(pr) else ("open" if state == "open" else state)

        summary = Pr.first_line_desc(pr) or "(no description)"

        lines: List[str] = []
        lines.append(f"#### #{pid} {title}")
        lines.append(f"> {summary}")
        lines.append("")

        if url:
            lines.append(f"- **Link:** {url}")

        lbs = Pr.labels(pr)
        if lbs:
            lines.append(f"- **Labels:** {', '.join(lbs)}")

        lines.append(f"- **Assignee:** {Pr.assignees(pr)}")
        lines.append(f"- **Status:** {status}")
        if merged_at:
            lines.append(f"- **Merged at:** {Pr.iso_date(str(merged_at))}")

        return "\n".join(lines).rstrip() + "\n"


class CrmBacklogRenderer:
    """Render a PR block template for OF1_Crm backlog (numbering applied later)."""

    def render_template(self, pr: Dict) -> str:
        """render_template: function helper. See module docstring for behavior."""
        merged_at = pr.get("merged_at")
        tag = Pr.iso_date(str(merged_at)) if merged_at else "In Progress"

        title = Pr.clean_title_title_only(pr.get("title") or "(no title)")
        desc = Pr.first_line_desc(pr)
        url = pr.get("html_url") or ""
        ass = Pr.assignees(pr)

        return (
            f"#### {{n}}. [{tag}] - {title}\n"
            f"    > {desc}\n\n"
            f"   **Link:** {url}\n"
            f"   **Assignee:** {ass}\n"
        )


# -----------------------------------------------------------------------------
# Markdown file updater base class
# -----------------------------------------------------------------------------


class MarkdownFile:
    """MarkdownFile: helper class. See top docstring for overall flow."""
    def __init__(self, path: Path):
        self._path = path

    def read(self) -> str:
        """read: function helper. See module docstring for behavior."""
        if not self._path.exists():
            raise SystemExit(f"❌ File not found: {self._path}")
        return self._path.read_text(encoding="utf-8")

    def write(self, text: str) -> None:
        """write: function helper. See module docstring for behavior."""
        self._path.write_text(text, encoding="utf-8")

    @property
    def path(self) -> Path:
        """path: function helper. See module docstring for behavior."""
        return self._path


# -----------------------------------------------------------------------------
# Personal backlog updater
# -----------------------------------------------------------------------------


class PersonalBacklogUpdater:
    """Update section '## BACKLOG - Team' in personal wiki backlog."""

    SECTION_HEADER = "## BACKLOG - Team"

    def __init__(self, file: MarkdownFile, renderer: PersonalBacklogRenderer):
        self._file = file
        self._renderer = renderer

    def sync(self, prs: List[Dict]) -> None:
        """sync: function helper. See module docstring for behavior."""
        text = self._file.read()

        idx = text.find(self.SECTION_HEADER)
        if idx == -1:
            raise SystemExit(f"❌ Missing section header: {self.SECTION_HEADER}")

        header_line_end = text.find("\n", idx)
        if header_line_end == -1:
            header_line_end = len(text)

        section_start = header_line_end + 1
        m_next = re.search(r"^##\s+", text[section_start:], flags=re.M)
        section_end = section_start + m_next.start(0) if m_next else len(text)

        before = text[:section_start]
        section = text[section_start:section_end]
        after = text[section_end:]

        # Strip legacy AUTO markers if they exist
        section = re.sub(r"^<!--\s*AUTO:FORGEJO_PRS_START\s*-->\s*\n?", "", section, flags=re.M)
        section = re.sub(r"^<!--\s*AUTO:FORGEJO_PRS_END\s*-->\s*\n?", "", section, flags=re.M)

        pr_block_re = re.compile(r"(?ms)^####\s+#(?P<num>\d+)\b.*?(?=^####\s+#\d+\b|\Z)")

        existing: Dict[int, str] = {}
        first_block_start: Optional[int] = None
        for m in pr_block_re.finditer(section):
            pid = int(m.group("num"))
            existing[pid] = m.group(0).rstrip()
            if first_block_start is None:
                first_block_start = m.start(0)

        prefix = section if first_block_start is None else section[:first_block_start]

        updated = appended = removed = 0

        for pr in prs:
            pid = Pr.id(pr)
            if pid is None:
                continue

            qualifies = Pr.has_description(pr) and Pr.should_include(pr)
            if not qualifies:
                if pid in existing:
                    existing.pop(pid, None)
                    removed += 1
                continue

            new_block = self._renderer.render(pr).rstrip()
            if pid in existing:
                if existing[pid].rstrip() != new_block:
                    existing[pid] = new_block
                    updated += 1
            else:
                existing[pid] = new_block
                appended += 1

        nums_sorted = sorted(existing.keys(), reverse=True)
        rebuilt = "\n\n".join(existing[n].rstrip() for n in nums_sorted).rstrip()

        out_section = prefix.rstrip()
        if out_section.strip() and rebuilt:
            out_section += "\n\n"
        elif out_section.strip() and not rebuilt:
            out_section += "\n"

        out_section += rebuilt
        out_section = out_section.rstrip() + "\n"

        self._file.write(before + out_section + after)

        if updated or appended or removed:
            print(
                f"✅ Backlog updated: {self._file.path} (updated={updated}, appended={appended}, removed={removed})"
            )
        else:
            print(f"✅ Backlog unchanged: {self._file.path}")


# -----------------------------------------------------------------------------
# CRM backlog updater
# -----------------------------------------------------------------------------


class CrmBacklogUpdater:
    """Update OF1_Crm backlog sections (Features + Bugs/Enhancements/Maintenance)."""

    SECTION_FEATURES = "## Features"
    SECTION_BEM = "## Bugs / Enhancements / Maintenance"

    def __init__(self, file: MarkdownFile, renderer: CrmBacklogRenderer):
        self._file = file
        self._renderer = renderer

    def sync(self, prs: List[Dict]) -> None:
        """sync: function helper. See module docstring for behavior."""
        text = self._file.read()

        text = self._ensure_section(text, self.SECTION_FEATURES)
        text = self._ensure_section(text, self.SECTION_BEM)

        features: List[Dict] = []
        bem: List[Dict] = []

        for pr in prs:
            if self._bucket(pr) == self.SECTION_FEATURES:
                features.append(pr)
            else:
                bem.append(pr)

        features_body = self._build_section_body(text, self.SECTION_FEATURES, features)
        bem_body = self._build_section_body(text, self.SECTION_BEM, bem)

        text = self._replace_section_body(text, self.SECTION_FEATURES, features_body)
        text = self._replace_section_body(text, self.SECTION_BEM, bem_body)

        self._file.write(text)
        print(f"✅ CRM backlog updated: {self._file.path}")

    def _bucket(self, pr: Dict) -> str:
        """Internal helper: _bucket."""
        names = [n.lower() for n in Pr.labels(pr)]
        if any("feature" in n for n in names):
            return self.SECTION_FEATURES
        return self.SECTION_BEM

    def _ensure_section(self, text: str, header: str) -> str:
        """Internal helper: _ensure_section."""
        if header in text:
            return text

        # Insert after first H1 if possible, else append
        m = re.search(r"^#\s+.*$", text, flags=re.M)
        insert_at = m.end(0) + 1 if m else len(text)
        return text[:insert_at] + f"\n\n{header}\n\n" + text[insert_at:]

    def _extract_blocks_by_id(self, body: str) -> Dict[int, str]:
        """Map PR_ID -> template block (normalize numbering to #### {n}.)"""

        block_re = re.compile(r"(?ms)^####\s+\d+\.\s+\[[^\]]+\]\s+-\s+.*?(?=^####\s+\d+\.\s+\[|^##\s+|\Z)")

        out: Dict[int, str] = {}
        for m in block_re.finditer(body):
            blk = m.group(0)
            blk = re.sub(r"^####\s+\d+\.", "#### {n}.", blk, flags=re.M)
            m_id = re.search(r"/pulls/(\d+)\b", blk)
            if not m_id:
                continue
            pid = int(m_id.group(1))
            out[pid] = blk.strip()

        return out

    def _build_section_body(self, full_text: str, header: str, prs: List[Dict]) -> str:
        """Internal helper: _build_section_body."""
        section_body = self._get_section_body(full_text, header)
        by_id = self._extract_blocks_by_id(section_body)

        for pr in prs:
            pid = Pr.id(pr)
            if pid is None:
                continue

            qualifies = Pr.has_description(pr) and Pr.should_include(pr)
            if not qualifies:
                by_id.pop(pid, None)
                continue

            tmpl = self._renderer.render_template(pr).strip()
            if by_id.get(pid, "").strip() != tmpl:
                by_id[pid] = tmpl

        # Sort: In Progress first, then merged date desc, then id desc
        items = sorted(by_id.items(), key=self._crm_sort_key, reverse=True)

        rebuilt: List[str] = []
        for i, (_, tmpl) in enumerate(items, start=1):
            rebuilt.append(tmpl.format(n=i).rstrip())

        return "\n\n".join(rebuilt).rstrip()

    @staticmethod
    def _crm_sort_key(item: Tuple[int, str]) -> Tuple[str, int]:
        """Internal helper: _crm_sort_key."""
        pid, blk = item
        m = re.search(r"\[(\d{4}-\d{2}-\d{2}|In Progress)\]", blk)
        tag = m.group(1) if m else "In Progress"

        # In Progress should come first
        tag_key = "9999-99-99" if tag == "In Progress" else tag
        return (tag_key, pid)

    @staticmethod
    def _get_section_body(text: str, header: str) -> str:
        """Internal helper: _get_section_body."""
        start = text.find(header)
        if start == -1:
            return ""

        start_line_end = text.find("\n", start)
        body_start = start_line_end + 1 if start_line_end != -1 else len(text)

        m_next = re.search(r"^##\s+", text[body_start:], flags=re.M)
        body_end = body_start + m_next.start(0) if m_next else len(text)

        return text[body_start:body_end]

    @staticmethod
    def _replace_section_body(text: str, header: str, new_body: str) -> str:
        """Internal helper: _replace_section_body."""
        start = text.find(header)
        if start == -1:
            return text

        start_line_end = text.find("\n", start)
        body_start = start_line_end + 1 if start_line_end != -1 else len(text)

        m_next = re.search(r"^##\s+", text[body_start:], flags=re.M)
        body_end = body_start + m_next.start(0) if m_next else len(text)

        before = text[:body_start]
        after = text[body_end:]

        # Ensure a blank line between header and first PR entry.
        nb = new_body.rstrip() + "\n"
        if nb.strip():
            nb = "\n" + nb

        prefix = before if before.endswith("\n") else before + "\n"
        return prefix + nb + after


# -----------------------------------------------------------------------------
# Application
# -----------------------------------------------------------------------------


class App:
    """App: helper class. See top docstring for overall flow."""
    def __init__(self, cfg: CollectorConfig):
        self._cfg = cfg
        self._client = ForgejoClient(cfg.base_url, cfg.token)

        self._personal_updater = PersonalBacklogUpdater(
            MarkdownFile(cfg.personal_backlog_file), PersonalBacklogRenderer()
        )

        self._crm_updater: Optional[CrmBacklogUpdater] = None
        if cfg.crm_backlog_file:
            self._crm_updater = CrmBacklogUpdater(MarkdownFile(cfg.crm_backlog_file), CrmBacklogRenderer())

    def run(self) -> None:
        """run: function helper. See module docstring for behavior."""
        print("🚀 Forgejo PR Collector")
        print("=" * 50)

        # Cutoff is based on PR.updated_at (not created_at).
        cutoff: Optional[datetime] = None
        if self._cfg.days_back is not None:
            cutoff = datetime.now() - timedelta(days=self._cfg.days_back)

        # Fetch PRs for each repo.
        # Note: we currently *sync outputs using the first repo only* (cfg.repos[0]).
        all_prs: Dict[str, List[Dict]] = {}
        for repo in self._cfg.repos:
            print(f"📥 Fetching PRs from {repo}...")
            prs = list(self._client.iter_pull_requests(self._cfg.owner, repo, self._cfg.state))

            if cutoff is not None:
                prs = [pr for pr in prs if pr.get("updated_at") and Pr.parse_iso_z(pr["updated_at"]) >= cutoff]

            all_prs[repo] = prs
            print(f"   ✓ Found {len(prs)} PRs")

        repo_prs = all_prs.get(self._cfg.repos[0], [])

        # Sync outputs:
        # - Personal wiki BACKLOG.md (section "BACKLOG - Team")
        # - OF1_Crm backlog (Features + Bugs/Enhancements/Maintenance)
        self._personal_updater.sync(repo_prs)
        if self._crm_updater:
            self._crm_updater.sync(repo_prs)

        print("✨ Done!")


def main() -> None:
    """main: function helper. See module docstring for behavior."""
    cfg = ConfigBuilder.build()
    App(cfg).run()


if __name__ == "__main__":
    main()
