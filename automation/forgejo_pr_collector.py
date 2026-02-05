#!/usr/bin/env python3
"""forgejo_pr_collector.py

Collect Pull Requests from Forgejo (Gitea-compatible API) and generate a Markdown summary.

Key features:
- No hardcoded secrets (token via env/.env/CLI)
- Pagination (fetches all PRs, not only first 100)
- Optional updated-at filtering (days-back)
- Summary by author + per-repo breakdown

Env vars (optional):
- FORGEJO_URL
- FORGEJO_TOKEN
- FORGEJO_OWNER
- FORGEJO_REPOS (comma-separated)
- PR_STATE (open|closed|all)
- DAYS_BACK (int)
- OUTPUT_FILE

Examples:
  export FORGEJO_URL="https://forgejo.example.com"
  export FORGEJO_TOKEN="..."
  python3 forgejo_pr_collector.py --owner of1-crm --repos of1-crm --days-back 30
"""

from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests


def _maybe_load_dotenv(dotenv_path: Path) -> None:
    """Load .env (best-effort) if python-dotenv is installed.

    We explicitly point to the script-local .env so it works no matter where you run the script from.
    """
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=dotenv_path, override=False)
    except Exception:
        return


def _parse_iso_z(dt: str) -> datetime:
    # Forgejo/Gitea timestamps typically look like: 2026-02-05T09:04:24Z
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")


def _csv(values: Optional[str]) -> List[str]:
    if not values:
        return []
    return [v.strip() for v in values.split(",") if v.strip()]


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    token: str
    owner: str
    repos: List[str]
    state: str
    days_back: Optional[int]
    output_file: Path


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

            # Heuristic: if we got less than 'limit', no more pages.
            if len(data) < limit:
                break
            page += 1


class MarkdownGenerator:
    @staticmethod
    def generate(all_prs: Dict[str, List[Dict]], output_file: Path, *, days_back: Optional[int]) -> None:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        total_prs = sum(len(prs) for prs in all_prs.values())

        # Summary by author across all repos
        author_stats = defaultdict(lambda: Counter({"open": 0, "closed": 0, "merged": 0}))
        for prs in all_prs.values():
            for pr in prs:
                author = pr.get("user", {}).get("login") or "unknown"
                state = pr.get("state") or "unknown"
                author_stats[author][state] += 1
                if MarkdownGenerator._is_merged(pr):
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
                    f.write(
                        f"- @{author}: open **{s['open']}**, closed **{s['closed']}**, merged **{s['merged']}**\n"
                    )
            else:
                f.write("(no data)\n")

            f.write("\n---\n\n")

            for repo, prs in all_prs.items():
                f.write(f"## 📦 Repository: `{repo}`\n\n")
                f.write(f"**Total PRs:** {len(prs)}\n\n")

                open_prs = [pr for pr in prs if pr.get("state") == "open"]
                closed_prs = [pr for pr in prs if pr.get("state") == "closed"]
                merged_prs = [pr for pr in prs if MarkdownGenerator._is_merged(pr)]

                f.write("### 🧾 Breakdown\n\n")
                f.write(f"- Open: **{len(open_prs)}**\n")
                f.write(f"- Closed: **{len(closed_prs)}**\n")
                f.write(f"- Merged: **{len(merged_prs)}**\n\n")

                if open_prs:
                    f.write(f"### 🟢 Open PRs ({len(open_prs)})\n\n")
                    MarkdownGenerator._write_pr_list(f, open_prs)

                if closed_prs:
                    f.write(f"### 🔴 Closed PRs ({len(closed_prs)})\n\n")
                    MarkdownGenerator._write_pr_list(f, closed_prs)

                f.write("\n---\n\n")

        print(f"✅ Summary saved to: {output_file}")

    @staticmethod
    def _is_merged(pr: Dict) -> bool:
        # Depending on Forgejo version, fields may differ.
        if pr.get("merged") is True:
            return True
        if pr.get("merged_at"):
            return True
        return False

    @staticmethod
    def _write_pr_list(f, prs: List[Dict]) -> None:
        for pr in prs:
            number = pr.get("number")
            title = pr.get("title") or "(no title)"
            author = pr.get("user", {}).get("login") or "unknown"

            created_at = (pr.get("created_at") or "")[:10]
            updated_at = (pr.get("updated_at") or "")[:10]
            state = pr.get("state") or "unknown"

            f.write(f"#### #{number} - {title}\n\n")
            f.write(f"- **Author:** @{author}\n")
            f.write(f"- **Created:** {created_at}\n")
            f.write(f"- **Updated:** {updated_at}\n")
            f.write(f"- **Status:** {state}")
            if MarkdownGenerator._is_merged(pr):
                f.write(" (merged)")
            f.write("\n")

            labels = pr.get("labels") or []
            if labels:
                label_names = ", ".join([f"`{lb.get('name')}`" for lb in labels if lb.get("name")])
                if label_names:
                    f.write(f"- **Labels:** {label_names}\n")

            if pr.get("html_url"):
                f.write(f"- **Link:** {pr['html_url']}\n")

            body = (pr.get("body") or "").strip()
            if body:
                f.write("\n**Description:**\n\n")
                snippet = body[:800]
                # Markdown quote, keep single paragraph-ish
                snippet = snippet.replace("\n", "\n> ")
                f.write(f"> {snippet}")
                if len(body) > 800:
                    f.write("...\n")
                else:
                    f.write("\n")

            f.write("\n")


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
        default=os.getenv("DAYS_BACK"),
        help="Only include PRs updated within N days (omit for all)",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("OUTPUT_FILE") or str(script_dir / "team_prs_summary.md"),
        help="Output markdown file path",
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

    days_back: Optional[int]
    if args.days_back in (None, "", "None"):
        days_back = None
    else:
        days_back = int(args.days_back)

    return CollectorConfig(
        base_url=str(args.url),
        token=str(args.token),
        owner=str(args.owner),
        repos=repos,
        state=str(args.state),
        days_back=days_back,
        output_file=Path(args.output).expanduser().resolve(),
    )


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

    MarkdownGenerator.generate(all_prs, cfg.output_file, days_back=cfg.days_back)
    print("✨ Done!")


if __name__ == "__main__":
    main()
