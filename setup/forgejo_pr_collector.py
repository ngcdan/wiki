#!/usr/bin/env python3
"""
Forgejo PR Collector - Thu thập thông tin Pull Requests và tổng hợp vào file markdown
"""

import requests
import os
from datetime import datetime
from typing import List, Dict

# ===== CONFIGURATION =====
FORGEJO_URL = "http://forgejo.of1-apps.svc.cluster.local"  # Forgejo URL
ACCESS_TOKEN = "14f78e612428a07d57f3209b662ace2880e54703"  # Access token
OWNER = "of1-crm"  # Organization/user name
REPOS = ["of1-crm"]  # Danh sách repos cần theo dõi
OUTPUT_FILE = "team_prs_summary.md"  # File output

# Trạng thái PR cần lấy: "open", "closed", "all"
PR_STATE = "all"

# Số ngày gần đây cần lấy (None = lấy tất cả)
DAYS_BACK = 30


class ForgejoCollector:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }

    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Lấy danh sách Pull Requests từ một repo"""
        url = f"{self.base_url}/api/v1/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "sort": "recentupdate",
            "limit": 100
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching PRs from {repo}: {e}")
            return []

    def filter_by_date(self, prs: List[Dict], days_back: int = None) -> List[Dict]:
        """Lọc PRs theo ngày"""
        if days_back is None:
            return prs

        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)

        filtered = []
        for pr in prs:
            updated_at = datetime.strptime(pr['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
            if updated_at >= cutoff_date:
                filtered.append(pr)

        return filtered

    def collect_all_prs(self, owner: str, repos: List[str], state: str = "open", days_back: int = None) -> Dict[str, List[Dict]]:
        """Thu thập PRs từ nhiều repos"""
        all_prs = {}

        for repo in repos:
            print(f"📥 Fetching PRs from {repo}...")
            prs = self.get_pull_requests(owner, repo, state)
            prs = self.filter_by_date(prs, days_back)
            all_prs[repo] = prs
            print(f"   ✓ Found {len(prs)} PRs")

        return all_prs


class MarkdownGenerator:
    @staticmethod
    def generate_summary(all_prs: Dict[str, List[Dict]], output_file: str):
        """Tạo file markdown tổng hợp"""

        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Team Pull Requests Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Statistics
            total_prs = sum(len(prs) for prs in all_prs.values())
            f.write(f"## 📊 Statistics\n\n")
            f.write(f"- **Total PRs:** {total_prs}\n")
            f.write(f"- **Repositories:** {len(all_prs)}\n\n")

            # PRs by repo
            for repo, prs in all_prs.items():
                if not prs:
                    continue

                f.write(f"## 📦 Repository: `{repo}`\n\n")
                f.write(f"**Total PRs:** {len(prs)}\n\n")

                # Group by status
                open_prs = [pr for pr in prs if pr['state'] == 'open']
                closed_prs = [pr for pr in prs if pr['state'] == 'closed']

                if open_prs:
                    f.write(f"### 🟢 Open PRs ({len(open_prs)})\n\n")
                    MarkdownGenerator._write_pr_list(f, open_prs)

                if closed_prs:
                    f.write(f"### 🔴 Closed PRs ({len(closed_prs)})\n\n")
                    MarkdownGenerator._write_pr_list(f, closed_prs)

                f.write("\n---\n\n")

        print(f"\n✅ Summary saved to: {output_file}")

    @staticmethod
    def _write_pr_list(f, prs: List[Dict]):
        """Ghi danh sách PRs vào file"""
        for pr in prs:
            # PR Header
            f.write(f"#### #{pr['number']} - {pr['title']}\n\n")

            # Metadata
            f.write(f"- **Author:** @{pr['user']['login']}\n")
            f.write(f"- **Created:** {pr['created_at'][:10]}\n")
            f.write(f"- **Updated:** {pr['updated_at'][:10]}\n")
            f.write(f"- **Status:** {pr['state']}")

            if pr.get('merged'):
                f.write(" (merged)")
            f.write("\n")

            # Labels
            if pr.get('labels'):
                labels = ", ".join([f"`{label['name']}`" for label in pr['labels']])
                f.write(f"- **Labels:** {labels}\n")

            # Link
            f.write(f"- **Link:** {pr['html_url']}\n")

            # Description
            if pr.get('body') and pr['body'].strip():
                f.write(f"\n**Description:**\n\n")
                # Indent description
                description = pr['body'].strip()
                f.write(f"> {description[:500]}")  # Limit length
                if len(description) > 500:
                    f.write("...\n")
                else:
                    f.write("\n")

            f.write("\n")


def main():
    """Main function"""
    print("🚀 Forgejo PR Collector")
    print("=" * 50)

    # Validate configuration
    if ACCESS_TOKEN == "your_access_token_here":
        print("❌ Error: Please set your ACCESS_TOKEN in the script")
        return

    if FORGEJO_URL == "https://your-forgejo-domain.com":
        print("❌ Error: Please set your FORGEJO_URL in the script")
        return

    # Initialize collector
    collector = ForgejoCollector(FORGEJO_URL, ACCESS_TOKEN)

    # Collect PRs
    all_prs = collector.collect_all_prs(
        owner=OWNER,
        repos=REPOS,
        state=PR_STATE,
        days_back=DAYS_BACK
    )

    # Generate markdown
    MarkdownGenerator.generate_summary(all_prs, OUTPUT_FILE)

    print("\n✨ Done!")


if __name__ == "__main__":
    main()
