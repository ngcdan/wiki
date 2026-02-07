#!/usr/bin/env python3
"""forgejo_pr_collector.py

Collect Pull Requests from Forgejo (Gitea-compatible API) and sync summaries into markdown backlogs.

Current outputs:
- Personal wiki backlog: /Users/nqcdan/dev/wiki/BACKLOG.md
  - Updates the section: "## BACKLOG - Team" (detect PR blocks by "#### #<id>")
- OF1 CRM backlog: /Users/nqcdan/dev/wiki/work/OF1_Crm/BACKLOG.md (symlink)
  - Updates sections: "## Features" and "## Bugs / Enhancements / Maintenance"
  - Buckets PRs by label

Key constraints (as requested):
- Only include PRs that have non-empty description (body)
- Keep PRs that are OPEN or MERGED; drop CLOSED-but-not-merged
- Dedup/replace by PR id so reruns are idempotent
"""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests


# ----------------------------
# Small utilities
# ----------------------------

def _maybe_load_dotenv(dotenv_path: Path) -> None:
    """Load .env (best-effort) if python-dotenv is installed."""

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=dotenv_path, override=False)
    except Exception:
        return


def _parse_iso_z(dt: str) -> datetime:
    # Forgejo/Gitea timestamps typically look like: 2026-02-05T09:04:24Z
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")


def _iso_date(iso_z: str) -> str:
    """Return YYYY-MM-DD from Forgejo's Z timestamps."""

    try:
        return _parse_iso_z(str(iso_z)).strftime("%Y-%m-%d")
    except Exception:
        return str(iso_z)[:10]


def _csv(values: Optional[str]) -> List[str]:
    if not values:
        return []
    return [v.strip() for v in values.split(",") if v.strip()]


def pr_has_description(pr: Dict) -> bool:
    body = pr.get("body")
    return isinstance(body, str) and body.strip() != ""


def pr_is_merged(pr: Dict) -> bool:
    return pr.get("merged") is True or bool(pr.get("merged_at"))


def pr_should_include(pr: Dict) -> bool:
    """Keep open + merged. Drop closed-but-not-merged."""

    return pr.get("state") == "open" or pr_is_merged(pr)


def pr_labels(pr: Dict) -> List[str]:
    labels = pr.get("labels")
    if not isinstance(labels, list):
        return []
    out: List[str] = []
    for lb in labels:
        if isinstance(lb, dict) and lb.get("name"):
            out.append(str(lb["name"]))
    return out


def fmt_user(u: Dict) -> str:
    login = u.get("login") or "unknown"
    name = u.get("full_name") or u.get("name") or ""
    return f"@{login}" + (f" ({name})" if name and name != login else "")


def pr_assignees(pr: Dict) -> str:
    assignees = pr.get("assignees")
    if isinstance(assignees, list) and assignees:
        return ", ".join(fmt_user(a or {}) for a in assignees)

    assignee = pr.get("assignee")
    if isinstance(assignee, dict) and assignee:
        return fmt_user(assignee)

    return "(unassigned)"


def pr_first_line_desc(pr: Dict) -> str:
    body = (pr.get("body") or "").strip()
    for ln in body.splitlines():
        if ln.strip():
            return ln.strip()
    return ""


def clean_title_title_only(title: str) -> str:
    """Remove ids/refs/tags so backlog stays 'Title only'."""

    t = (title or "").strip()

    # Remove any [Tag] anywhere (e.g. [Enhancement])
    t = re.sub(r"\[[^\]]+\]", "", t)

    # Remove leading verbs like Fixes/Closes/Refs/Issues with issue refs
    t = re.sub(
        r"^(Closes|Fixes|Resolves|Refs?|Issues?)\s+(#\d+)(\s*[+,/]\s*#\d+)*\s*[-:]*\s*",
        "",
        t,
        flags=re.I,
    )

    # Remove any remaining issue references like '#123'
    t = re.sub(r"#\d+", "", t)

    # Remove leftover punctuation/double spaces
    t = re.sub(r"\s+", " ", t).strip()
    t = t.strip("-:–— ").rstrip(".")

    return t


# ----------------------------
# Config + API client
# ----------------------------


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    token: str
    owner: str
    repos: List[str]
    state: str
    days_back: Optional[int]
    backlog_file: Path
    crm_backlog_file: Optional[Path]


class ForgejoCollector:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        }

    def iter_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 100,
    ) -> Iterable[Dict]:
        """Iterate PRs with pagination."""

        url = f"{self.base_url}/api/v1/repos/{owner}/{repo}/pulls"

        page = 1
        while True:
            params = {
                "state": state,
                "sort": "recentupdate",
                "limit": limit,
                "page": page,
            }

            resp = requests.get(url, headers=self.headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json() or []
            if not data:
                break

            for pr in data:
                yield pr

            if len(data) < limit:
                break
            page += 1


def build_config(argv: Optional[List[str]] = None) -> CollectorConfig:
    script_dir = Path(__file__).resolve().parent
    _maybe_load_dotenv(script_dir / ".env")

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
        help="Only include PRs updated within N days (omit for all)",
    )
    parser.add_argument(
        "--backlog-file",
        default=os.getenv("BACKLOG_FILE") or str((script_dir.parent / "BACKLOG.md")),
        help="Personal wiki backlog markdown file to update (Team section)",
    )
    parser.add_argument(
        "--crm-backlog-file",
        default=os.getenv("CRM_BACKLOG_FILE") or str((script_dir.parent / "work" / "OF1_Crm" / "BACKLOG.md")),
        help="OF1_Crm backlog markdown file to update (Features + Bugs/Enhancements/Maintenance sections)",
    )

    args = parser.parse_args(argv)

    if not args.url:
        raise SystemExit("❌ Missing Forgejo URL. Provide --url or set FORGEJO_URL")
    if not args.token:
        raise SystemExit("❌ Missing token. Provide --token or set FORGEJO_TOKEN")
    if not args.owner:
        raise SystemExit("❌ Missing owner. Provide --owner or set FORGEJO_OWNER")

    repos = _csv(args.repos)
    if not repos:
        raise SystemExit("❌ Missing repos. Provide --repos or set FORGEJO_REPOS")

    if args.days_back in (None, "", "None"):
        days_back: Optional[int] = None
    else:
        days_back = int(args.days_back)

    crm_backlog_file: Optional[Path] = None
    if args.crm_backlog_file not in (None, "", "None"):
        crm_backlog_file = Path(args.crm_backlog_file).expanduser().resolve()

    return CollectorConfig(
        base_url=str(args.url),
        token=str(args.token),
        owner=str(args.owner),
        repos=repos,
        state=str(args.state),
        days_back=days_back,
        backlog_file=Path(args.backlog_file).expanduser().resolve(),
        crm_backlog_file=crm_backlog_file,
    )


# ----------------------------
# Renderers
# ----------------------------


def render_personal_pr_block(pr: Dict) -> str:
    """Block format for personal wiki BACKLOG - Team (keyed by PR number)."""

    number = pr.get("number")
    title = pr.get("title") or "(no title)"
    title = re.sub(r"^\s*#\d+\s*[-:]*\s*", "", title).strip()

    url = pr.get("html_url") or ""

    state = pr.get("state") or "unknown"
    merged_at = pr.get("merged_at")
    status = "merged" if pr_is_merged(pr) else ("open" if state == "open" else state)

    summary = pr_first_line_desc(pr) or "(no description)"

    lines: List[str] = []
    lines.append(f"#### #{number} {title}")
    lines.append(f"> {summary}")
    lines.append("")

    if url:
        lines.append(f"- **Link:** {url}")

    lbs = pr_labels(pr)
    if lbs:
        lines.append(f"- **Labels:** {', '.join(lbs)}")

    lines.append(f"- **Assignee:** {pr_assignees(pr)}")
    lines.append(f"- **Status:** {status}")
    if merged_at:
        lines.append(f"- **Merged at:** {_iso_date(str(merged_at))}")

    return "\n".join(lines).rstrip() + "\n"


def render_crm_pr_template(pr: Dict) -> str:
    """Template block for OF1_Crm backlog (numbering applied later)."""

    merged_at = pr.get("merged_at")
    merged_tag = _iso_date(str(merged_at)) if merged_at else "In Progress"

    title = clean_title_title_only(pr.get("title") or "(no title)")
    desc = pr_first_line_desc(pr)
    url = pr.get("html_url") or ""
    ass = pr_assignees(pr)

    return (
        f"#### {{n}}. [{merged_tag}] - {title}\n"
        f"    > {desc}\n\n"
        f"   **Link:** {url}\n"
        f"   **Assignee:** {ass}\n"
    )


# ----------------------------
# Personal wiki backlog updater
# ----------------------------


def update_personal_team_section(backlog_file: Path, prs: List[Dict]) -> None:
    """Update `## BACKLOG - Team` section in-place.

    - No AUTO markers.
    - Detect blocks by PR number (`#### #<id> ...`).
    - Replace blocks by id, append new ones.
    - Remove blocks for PRs that don't qualify (no description OR closed-not-merged).
    """

    if not backlog_file.exists():
        raise SystemExit(f"❌ Backlog file not found: {backlog_file}")

    text = backlog_file.read_text(encoding="utf-8")

    header = "## BACKLOG - Team"
    idx = text.find(header)
    if idx == -1:
        raise SystemExit(f"❌ Missing section header: {header}")

    header_line_end = text.find("\n", idx)
    if header_line_end == -1:
        header_line_end = len(text)

    section_start = header_line_end + 1
    m_next = re.search(r"^##\s+", text[section_start:], flags=re.M)
    section_end = section_start + m_next.start(0) if m_next else len(text)

    before = text[:section_start]
    section = text[section_start:section_end]
    after = text[section_end:]

    # Remove any legacy markers if present
    section = re.sub(r"^<!--\s*AUTO:FORGEJO_PRS_START\s*-->\s*\n?", "", section, flags=re.M)
    section = re.sub(r"^<!--\s*AUTO:FORGEJO_PRS_END\s*-->\s*\n?", "", section, flags=re.M)

    # Parse existing blocks in the section
    pr_block_re = re.compile(r"(?ms)^####\s+#(?P<num>\d+)\b.*?(?=^####\s+#\d+\b|\Z)")

    existing_blocks: Dict[int, str] = {}
    first_block_start: Optional[int] = None
    for m in pr_block_re.finditer(section):
        num = int(m.group("num"))
        existing_blocks[num] = m.group(0).rstrip()
        if first_block_start is None:
            first_block_start = m.start(0)

    prefix = section if first_block_start is None else section[:first_block_start]

    updated = appended = removed = 0

    # Apply changes from fetched PR list
    for pr in prs:
        if not isinstance(pr.get("number"), int):
            continue
        pid = pr["number"]

        qualifies = pr_has_description(pr) and pr_should_include(pr)

        if not qualifies:
            if pid in existing_blocks:
                existing_blocks.pop(pid, None)
                removed += 1
            continue

        new_block = render_personal_pr_block(pr).rstrip()
        if pid in existing_blocks:
            if existing_blocks[pid].rstrip() != new_block:
                existing_blocks[pid] = new_block
                updated += 1
        else:
            existing_blocks[pid] = new_block
            appended += 1

    # Rebuild: simple sort by PR id desc
    nums_sorted = sorted(existing_blocks.keys(), reverse=True)
    rebuilt = "\n\n".join(existing_blocks[n].rstrip() for n in nums_sorted).rstrip()

    out_section = prefix.rstrip()
    if out_section.strip() and rebuilt:
        out_section += "\n\n"
    elif out_section.strip() and not rebuilt:
        out_section += "\n"

    out_section += rebuilt
    out_section = out_section.rstrip() + "\n"

    backlog_file.write_text(before + out_section + after, encoding="utf-8")

    if updated or appended or removed:
        print(f"✅ Backlog updated: {backlog_file} (updated={updated}, appended={appended}, removed={removed})")
    else:
        print(f"✅ Backlog unchanged: {backlog_file}")


# ----------------------------
# OF1_Crm backlog updater
# ----------------------------


def _ensure_section_exists(text: str, header: str) -> str:
    if header in text:
        return text

    # Insert after first H1 if possible, else append
    m = re.search(r"^#\s+.*$", text, flags=re.M)
    insert_at = m.end(0) + 1 if m else len(text)
    return text[:insert_at] + f"\n\n{header}\n\n" + text[insert_at:]


def _bucket_for_crm(pr: Dict) -> str:
    names = [n.lower() for n in pr_labels(pr)]
    if any("feature" in n for n in names):
        return "## Features"
    return "## Bugs / Enhancements / Maintenance"


def _extract_crm_blocks_by_id(body: str) -> Dict[int, str]:
    """Return mapping PR_ID -> template block (numbering normalized)."""

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


def _replace_section_body(text: str, section_header: str, new_body: str) -> str:
    start = text.find(section_header)
    if start == -1:
        return text

    start_line_end = text.find("\n", start)
    body_start = start_line_end + 1 if start_line_end != -1 else len(text)

    m_next = re.search(r"^##\s+", text[body_start:], flags=re.M)
    body_end = body_start + m_next.start(0) if m_next else len(text)

    before = text[:body_start]
    after = text[body_end:]

    # Ensure a blank line between header and first PR
    nb = new_body.rstrip() + "\n"
    if nb.strip():
        nb = "\n" + nb

    # Ensure the prefix ends with exactly one newline
    prefix = before if before.endswith("\n") else before + "\n"

    return prefix + nb + after


def update_of1_crm_backlog(backlog_file: Path, prs: List[Dict]) -> None:
    """Update `work/OF1_Crm/BACKLOG.md` with bucketed PR summaries."""

    if not backlog_file.exists():
        raise SystemExit(f"❌ CRM backlog file not found: {backlog_file}")

    text = backlog_file.read_text(encoding="utf-8")

    text = _ensure_section_exists(text, "## Features")
    text = _ensure_section_exists(text, "## Bugs / Enhancements / Maintenance")

    # Split PRs into buckets
    features: List[Dict] = []
    bem: List[Dict] = []
    for pr in prs:
        if _bucket_for_crm(pr) == "## Features":
            features.append(pr)
        else:
            bem.append(pr)

    def build_section(section_header: str, prs_for_section: List[Dict]) -> str:
        # Extract current body
        start = text.find(section_header)
        if start == -1:
            return ""

        start_line_end = text.find("\n", start)
        body_start = start_line_end + 1 if start_line_end != -1 else len(text)

        m_next = re.search(r"^##\s+", text[body_start:], flags=re.M)
        body_end = body_start + m_next.start(0) if m_next else len(text)

        body = text[body_start:body_end]

        by_id = _extract_crm_blocks_by_id(body)

        # Apply fetched PRs (replace/add/remove)
        for pr in prs_for_section:
            if not isinstance(pr.get("number"), int):
                continue
            pid = pr["number"]

            qualifies = pr_has_description(pr) and pr_should_include(pr)
            if not qualifies:
                by_id.pop(pid, None)
                continue

            tmpl = render_crm_pr_template(pr).strip()
            if by_id.get(pid, "").strip() != tmpl:
                by_id[pid] = tmpl

        # Sort: In Progress first, then merged date desc, then id desc
        def sort_key(item: tuple[int, str]) -> tuple[str, int]:
            pid, blk = item
            m = re.search(r"\[(\d{4}-\d{2}-\d{2}|In Progress)\]", blk)
            tag = m.group(1) if m else "In Progress"
            # In Progress first
            tag_key = "9999-99-99" if tag == "In Progress" else tag
            return (tag_key, pid)

        items = sorted(by_id.items(), key=sort_key, reverse=True)

        rebuilt: List[str] = []
        for i, (_, tmpl) in enumerate(items, start=1):
            rebuilt.append(tmpl.format(n=i).rstrip())

        return "\n\n".join(rebuilt).rstrip()

    features_body = build_section("## Features", features)
    bem_body = build_section("## Bugs / Enhancements / Maintenance", bem)

    text = _replace_section_body(text, "## Features", features_body)
    text = _replace_section_body(text, "## Bugs / Enhancements / Maintenance", bem_body)

    backlog_file.write_text(text, encoding="utf-8")
    print(f"✅ CRM backlog updated: {backlog_file}")


# ----------------------------
# Optional: older summary generator (kept for reuse)
# ----------------------------


class MarkdownGenerator:
    @staticmethod
    def generate_team_summary(all_prs: Dict[str, List[Dict]], output_file: Path, *, days_back: Optional[int]) -> None:
        """Generate standalone markdown report (team summary)."""

        output_file.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        total_prs = sum(len(prs) for prs in all_prs.values())

        author_stats = defaultdict(lambda: Counter({"open": 0, "closed": 0, "merged": 0}))
        for prs in all_prs.values():
            for pr in prs:
                author = pr.get("user", {}).get("login") or "unknown"
                state = pr.get("state") or "unknown"
                author_stats[author][state] += 1
                if pr_is_merged(pr):
                    author_stats[author]["merged"] += 1

        def fmt_days_back() -> str:
            return "all time" if days_back is None else f"last {days_back} days"

        with output_file.open("w", encoding="utf-8") as f:
            f.write("# Team Pull Requests Summary\n\n")
            f.write(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Scope:** {fmt_days_back()}\n\n")
            f.write("---\n\n")

            f.write("## 📊 Statistics\n\n")
            f.write(f"- **Total PRs:** {total_prs}\n")
            f.write(f"- **Repositories:** {len(all_prs)}\n\n")

            f.write("## 👤 Summary by author\n\n")
            if author_stats:
                for author in sorted(author_stats.keys(), key=lambda a: (-author_stats[a]["open"], a)):
                    s = author_stats[author]
                    f.write(f"- @{author}: open **{s['open']}**, closed **{s['closed']}**, merged **{s['merged']}**\n")
            else:
                f.write("(no data)\n")


# ----------------------------
# Main
# ----------------------------


def main() -> None:
    print("🚀 Forgejo PR Collector")
    print("=" * 50)

    cfg = build_config()
    collector = ForgejoCollector(cfg.base_url, cfg.token)

    cutoff: Optional[datetime] = None
    if cfg.days_back is not None:
        cutoff = datetime.now() - timedelta(days=cfg.days_back)

    all_prs: Dict[str, List[Dict]] = {}

    for repo in cfg.repos:
        print(f"📥 Fetching PRs from {repo}...")
        prs = list(collector.iter_pull_requests(cfg.owner, repo, cfg.state))

        if cutoff is not None:
            prs = [pr for pr in prs if pr.get("updated_at") and _parse_iso_z(pr["updated_at"]) >= cutoff]

        all_prs[repo] = prs
        print(f"   ✓ Found {len(prs)} PRs")

    first_repo = cfg.repos[0]
    repo_prs = all_prs.get(first_repo, [])

    update_personal_team_section(cfg.backlog_file, repo_prs)

    if cfg.crm_backlog_file:
        update_of1_crm_backlog(cfg.crm_backlog_file, repo_prs)

    print("✨ Done!")


if __name__ == "__main__":
    main()
