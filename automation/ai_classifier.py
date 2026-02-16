#!/usr/bin/env python3
"""AI Classifier for PR/Issue Classification and Prioritization

This module provides AI-powered classification for Forgejo PRs and Issues.
Supports both local LLM (Ollama) and API-based models (OpenAI/Anthropic).

Usage:
    from ai_classifier import AIClassifier
    
    classifier = AIClassifier(provider="ollama")  # or "openai"
    result = classifier.classify_pr(pr_dict)
    # Returns: {category, priority, summary, confidence}
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import requests


class Provider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Category(Enum):
    FEATURE = "Feature"
    BUG = "Bug"
    ENHANCEMENT = "Enhancement"
    MAINTENANCE = "Maintenance"
    DOCUMENTATION = "Documentation"


class Priority(Enum):
    P0 = "P0"  # Critical, immediate action
    P1 = "P1"  # High priority, significant impact
    P2 = "P2"  # Normal priority


@dataclass
class ClassificationResult:
    category: Category
    priority: Priority
    summary: str
    confidence: float
    reasoning: str


class AIClassifier:
    """AI-powered classifier for PRs and Issues."""

    def __init__(
        self,
        provider: str = "ollama",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = Provider(provider)
        self.model = model or self._default_model()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.base_url = base_url or self._default_base_url()

    def _default_model(self) -> str:
        if self.provider == Provider.OLLAMA:
            return "llama3.2:3b"  # Fast, lightweight
        elif self.provider == Provider.OPENAI:
            return "gpt-4o-mini"
        elif self.provider == Provider.ANTHROPIC:
            return "claude-3-haiku-20240307"
        return "llama3.2:3b"

    def _default_base_url(self) -> str:
        if self.provider == Provider.OLLAMA:
            return "http://localhost:11434"
        elif self.provider == Provider.OPENAI:
            return "https://api.openai.com/v1"
        elif self.provider == Provider.ANTHROPIC:
            return "https://api.anthropic.com/v1"
        return "http://localhost:11434"



    def classify_issue(self, issue: Dict) -> ClassificationResult:
        """Classify an issue.

        Args:
            issue: Issue dict from Forgejo API

        Returns:
            ClassificationResult with category, priority, summary, confidence
        """
        title = issue.get("title", "")
        body = issue.get("body", "")
        labels = [lb.get("name", "") for lb in (issue.get("labels") or [])]

        prompt = self._build_classification_prompt(
            title=title,
            description=body,
            labels=labels,
            item_type="issue",
        )

        response = self._call_llm(prompt)
        return self._parse_classification_response(response)

    def detect_duplicates(
        self, item: Dict, existing: List[Dict], threshold: float = 0.8
    ) -> Optional[int]:
        """Detect if item is duplicate of existing items.

        Args:
            item: New PR/Issue dict
            existing: List of existing PR/Issue dicts
            threshold: Similarity threshold (0-1)

        Returns:
            ID of duplicate item if found, else None
        """
        if not existing:
            return None

        title = item.get("title", "")
        body = item.get("body", "")

        for ex in existing:
            ex_title = ex.get("title", "")
            ex_body = ex.get("body", "")

            similarity = self._calculate_similarity(
                title, body, ex_title, ex_body
            )

            if similarity >= threshold:
                return ex.get("number")

        return None

    def _build_classification_prompt(
        self,
        title: str,
        description: str,
        labels: List[str],
        item_type: str,
    ) -> str:
        return f"""Analyze this {item_type} and classify it.

Title: {title}

Description:
{description[:500]}  # Truncate long descriptions

Labels: {', '.join(labels) if labels else 'none'}

Classify into:
1. Category: Feature, Bug, Enhancement, Maintenance, Documentation
2. Priority: P0 (critical/urgent), P1 (high impact), P2 (normal)
3. Summary: One-line summary (max 100 chars)

Consider:
- Keywords like "fix", "bug", "crash" → Bug
- Keywords like "urgent", "critical", "production" → P0
- Keywords like "feature", "add", "new" → Feature
- Keywords like "improve", "refactor", "optimize" → Enhancement

Respond in JSON format:
{{
  "category": "Bug|Feature|Enhancement|Maintenance|Documentation",
  "priority": "P0|P1|P2",
  "summary": "one-line summary",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API and return response text."""
        if self.provider == Provider.OLLAMA:
            return self._call_ollama(prompt)
        elif self.provider == Provider.OPENAI:
            return self._call_openai(prompt)
        elif self.provider == Provider.ANTHROPIC:
            return self._call_anthropic(prompt)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama local API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except Exception as e:
            # Fallback: simple rule-based classification
            return self._fallback_classification(prompt)

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        if not self.api_key:
            return self._fallback_classification(prompt)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            return self._fallback_classification(prompt)

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        if not self.api_key:
            return self._fallback_classification(prompt)

        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]
        except Exception:
            return self._fallback_classification(prompt)

    def _fallback_classification(self, prompt: str) -> str:
        """Rule-based fallback when LLM unavailable."""
        text = prompt.lower()

        # Detect category
        if any(kw in text for kw in ["fix", "bug", "crash", "error", "broken"]):
            category = "Bug"
        elif any(kw in text for kw in ["feature", "add", "new", "implement"]):
            category = "Feature"
        elif any(kw in text for kw in ["improve", "refactor", "optimize", "enhance"]):
            category = "Enhancement"
        elif any(kw in text for kw in ["doc", "readme", "comment"]):
            category = "Documentation"
        else:
            category = "Maintenance"

        # Detect priority
        if any(kw in text for kw in ["urgent", "critical", "p0", "production", "hotfix"]):
            priority = "P0"
        elif any(kw in text for kw in ["important", "high", "p1"]):
            priority = "P1"
        else:
            priority = "P2"

        return json.dumps({
            "category": category,
            "priority": priority,
            "summary": "Auto-classified (fallback)",
            "confidence": 0.6,
            "reasoning": "Rule-based classification (LLM unavailable)",
        })

    def _parse_classification_response(self, response: str) -> ClassificationResult:
        """Parse LLM JSON response into ClassificationResult."""
        try:
            data = json.loads(response)
            return ClassificationResult(
                category=Category[data["category"].upper()],
                priority=Priority[data["priority"]],
                summary=data.get("summary", ""),
                confidence=float(data.get("confidence", 0.8)),
                reasoning=data.get("reasoning", ""),
            )
        except Exception:
            # Fallback to default
            return ClassificationResult(
                category=Category.MAINTENANCE,
                priority=Priority.P2,
                summary="Classification failed",
                confidence=0.5,
                reasoning="Failed to parse LLM response",
            )

    def _calculate_similarity(
        self, title1: str, body1: str, title2: str, body2: str
    ) -> float:
        """Calculate similarity between two items (simple approach).

        For production, consider using sentence-transformers embeddings.
        """
        # Simple token overlap similarity
        def tokenize(text: str) -> set:
            return set(re.findall(r"\w+", text.lower()))

        tokens1 = tokenize(f"{title1} {body1}")
        tokens2 = tokenize(f"{title2} {body2}")

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0


# Example usage
if __name__ == "__main__":
    # Test with sample PR
    sample_pr = {
        "title": "Fixes #123 - Fix critical bug in payment processing",
        "body": "This PR fixes a critical bug that causes payment failures in production.",
        "labels": [{"name": "bug"}, {"name": "urgent"}],
    }

    classifier = AIClassifier(provider="ollama")
    result = classifier.classify_pr(sample_pr)

    print(f"Category: {result.category.value}")
    print(f"Priority: {result.priority.value}")
    print(f"Summary: {result.summary}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Reasoning: {result.reasoning}")
