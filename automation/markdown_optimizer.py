#!/usr/bin/env python3
"""Markdown Structure Optimizer for AI Comprehension

Adds YAML frontmatter and structured metadata to markdown files
to improve AI understanding and knowledge retrieval.

Features:
- Add YAML frontmatter with metadata
- Extract and structure document info
- Maintain backward compatibility
- Preserve existing content
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MarkdownOptimizer:
    """Optimize markdown files for AI comprehension."""

    def __init__(self, wiki_root: Path):
        self.wiki_root = Path(wiki_root)

    def add_frontmatter(self, file_path: Path, metadata: Optional[Dict] = None) -> bool:
        """Add YAML frontmatter to markdown file."""
        try:
            # Read existing content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if frontmatter already exists
            if content.startswith('---'):
                print(f"⚠️  {file_path.name} already has frontmatter, skipping")
                return False

            # Auto-detect metadata if not provided
            if metadata is None:
                metadata = self._extract_metadata(file_path, content)

            # Generate frontmatter
            frontmatter = self._generate_frontmatter(metadata)

            # Combine frontmatter + content
            new_content = f"{frontmatter}\n{content}"

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ Added frontmatter to {file_path.name}")
            return True

        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            return False

    def _extract_metadata(self, file_path: Path, content: str) -> Dict:
        """Extract metadata from file path and content."""
        # Get title from first heading or filename
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem.replace('-', ' ').title()

        # Detect tags from content
        tags = self._detect_tags(file_path, content)

        # Get file stats
        stat = file_path.stat()
        created = datetime.fromtimestamp(stat.st_birthtime).strftime('%Y-%m-%d')
        updated = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')

        # Detect document type
        doc_type = self._detect_type(file_path, content)

        # Find related files
        related = self._find_related(file_path, content)

        return {
            'title': title,
            'type': doc_type,
            'tags': tags,
            'created': created,
            'updated': updated,
            'related': related,
        }

    def _detect_tags(self, file_path: Path, content: str) -> List[str]:
        """Detect tags from file location and content."""
        tags = []

        # From directory
        parent = file_path.parent.name
        if parent != 'wiki':
            tags.append(parent)

        # From content keywords
        keywords = {
            'work': ['crm', 'project', 'team', 'task', 'issue'],
            'automation': ['script', 'cron', 'daemon', 'bot'],
            'setup': ['config', 'install', 'setup'],
            'planning': ['plan', 'goal', 'roadmap', 'strategy'],
            'documentation': ['guide', 'manual', 'readme', 'how-to'],
        }

        content_lower = content.lower()
        for tag, words in keywords.items():
            if any(word in content_lower for word in words):
                if tag not in tags:
                    tags.append(tag)

        return tags[:5]  # Limit to 5 tags

    def _detect_type(self, file_path: Path, content: str) -> str:
        """Detect document type."""
        name_lower = file_path.name.lower()
        content_lower = content.lower()

        if 'backlog' in name_lower:
            return 'backlog'
        elif 'plan' in name_lower or 'roadmap' in name_lower:
            return 'planning'
        elif 'workflow' in name_lower or 'manual' in name_lower:
            return 'process'
        elif 'setup' in name_lower or 'config' in name_lower:
            return 'configuration'
        elif 'readme' in name_lower:
            return 'documentation'
        elif '## ' in content and '- [ ]' in content:
            return 'task-list'
        else:
            return 'note'

    def _find_related(self, file_path: Path, content: str) -> List[str]:
        """Find related files mentioned in content."""
        related = []

        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+\.md)\)', content)
        for _, link in links:
            # Convert to relative path
            if not link.startswith('http'):
                related.append(link)

        # Find file references
        file_refs = re.findall(r'`([a-zA-Z0-9_-]+\.md)`', content)
        related.extend(file_refs)

        # Deduplicate
        return list(set(related))[:5]  # Limit to 5

    def _generate_frontmatter(self, metadata: Dict) -> str:
        """Generate YAML frontmatter."""
        lines = ['---']
        lines.append(f'title: "{metadata["title"]}"')
        lines.append(f'type: {metadata["type"]}')

        if metadata['tags']:
            tags_str = ', '.join(metadata['tags'])
            lines.append(f'tags: [{tags_str}]')

        lines.append(f'created: {metadata["created"]}')
        lines.append(f'updated: {metadata["updated"]}')

        if metadata['related']:
            lines.append('related:')
            for rel in metadata['related']:
                lines.append(f'  - {rel}')

        lines.append('---')
        return '\n'.join(lines)

    def optimize_structure(self, file_path: Path) -> bool:
        """Optimize markdown structure for AI."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if already has frontmatter
            if content.startswith('---'):
                # Already optimized
                return False

            # Add frontmatter
            return self.add_frontmatter(file_path)

        except Exception as e:
            print(f"❌ Error optimizing {file_path.name}: {e}")
            return False

    def process_directory(self, directory: Path, recursive: bool = False) -> Dict:
        """Process all markdown files in directory."""
        stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
        }

        pattern = '**/*.md' if recursive else '*.md'
        for md_file in directory.glob(pattern):
            # Skip automation directory (already has docs)
            if 'automation' in md_file.parts:
                stats['skipped'] += 1
                continue

            # Skip hidden files
            if md_file.name.startswith('.'):
                stats['skipped'] += 1
                continue

            # Process file
            if self.optimize_structure(md_file):
                stats['processed'] += 1
            else:
                stats['skipped'] += 1

        return stats


def main():
    """Main entry point."""
    wiki_root = Path("/Users/nqcdan/dev/wiki")
    optimizer = MarkdownOptimizer(wiki_root)

    print("🔧 Optimizing markdown structure for AI comprehension...")
    print()

    # Process key directories
    directories = [
        (wiki_root, False),  # Root level
        (wiki_root / "work", False),
        (wiki_root / "notes", False),
        (wiki_root / "rulebooks", False),
        (wiki_root / "setup", False),
    ]

    total_stats = {'processed': 0, 'skipped': 0, 'errors': 0}

    for directory, recursive in directories:
        if not directory.exists():
            continue

        print(f"📁 Processing {directory.name}/")
        stats = optimizer.process_directory(directory, recursive)

        for key in total_stats:
            total_stats[key] += stats[key]

        print(f"   Processed: {stats['processed']}, Skipped: {stats['skipped']}")
        print()

    print("✅ Optimization complete!")
    print(f"   Total processed: {total_stats['processed']}")
    print(f"   Total skipped: {total_stats['skipped']}")
    print()
    print("📝 Files now have YAML frontmatter with:")
    print("   - Title, type, tags")
    print("   - Created/updated dates")
    print("   - Related documents")


if __name__ == "__main__":
    main()
