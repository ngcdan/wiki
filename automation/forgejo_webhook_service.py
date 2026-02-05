#!/usr/bin/env python3
"""forgejo_webhook_service.py

Real-time webhook receiver for Forgejo/Gitea Pull Request events.

Flow:
- Receive webhook event
- Verify signature/token using WEBHOOK_SECRET (recommended)
- Rebuild/update work/OF1_Crm/BACKLOG.md between AUTO markers
- Auto git commit + push to main

Run (dev):
  cd automation
  source .venv/bin/activate
  uvicorn forgejo_webhook_service:app --host 0.0.0.0 --port 9009

Env:
- WEBHOOK_SECRET: shared secret configured in Forgejo webhook
- FORGEJO_URL / FORGEJO_TOKEN / FORGEJO_OWNER / FORGEJO_REPOS / PR_STATE / DAYS_BACK / BACKLOG_FILE
- GIT_REMOTE (default origin)
- GIT_BRANCH (default main)
"""

from __future__ import annotations

import hmac
import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException

# Import collector logic from sibling file
from forgejo_pr_collector import build_config, ForgejoCollector, _parse_iso_z  # type: ignore
from forgejo_pr_collector import _update_backlog  # type: ignore


app = FastAPI(title="Forgejo Webhook Service", version="1.0")


def _repo_root() -> Path:
    # automation/forgejo_webhook_service.py -> repo root is parent of automation
    return Path(__file__).resolve().parent.parent


def _verify_webhook(raw_body: bytes, headers: dict) -> None:
    secret = os.getenv("WEBHOOK_SECRET")
    if not secret:
        # Allow running without verification, but it's not recommended.
        return

    # Preferred: HMAC signature header (Gitea/Forgejo)
    sig = headers.get("x-gitea-signature") or headers.get("x-forgejo-signature")
    if sig:
        mac = hmac.new(secret.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256)
        expected = mac.hexdigest()
        if not hmac.compare_digest(expected, sig.strip()):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        return

    # Fallback: token header (some setups)
    token = headers.get("x-gitea-token") or headers.get("x-forgejo-token")
    if token:
        if not hmac.compare_digest(token.strip(), secret):
            raise HTTPException(status_code=401, detail="Invalid webhook token")
        return

    raise HTTPException(status_code=401, detail="Missing webhook signature/token")


def _should_process(event: str, payload: dict) -> bool:
    if event != "pull_request":
        return False

    action = payload.get("action")
    # Actions we care about; safe to be liberal.
    return action in {
        "opened",
        "edited",
        "reopened",
        "closed",
        "synchronized",
        "assigned",
        "unassigned",
        "labeled",
        "unlabeled",
        "review_requested",
        "review_request_removed",
    }


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd or _repo_root()),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{proc.stdout}")
    return proc.stdout


def _git_commit_and_push(backlog_file: Path) -> None:
    root = _repo_root()
    rel_path = os.path.relpath(str(backlog_file), str(root))

    status = _git("status", "--porcelain", cwd=root)
    if rel_path not in status:
        # Nothing changed in backlog
        return

    _git("add", rel_path, cwd=root)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"chore(crm): sync BACKLOG from Forgejo PRs ({ts})"
    _git("commit", "-m", msg, cwd=root)

    remote = os.getenv("GIT_REMOTE", "origin")
    branch = os.getenv("GIT_BRANCH", "main")
    _git("push", remote, branch, cwd=root)


def _run_sync() -> Path:
    cfg = build_config([])

    # Enforce scope: single repo only (as requested)
    if len(cfg.repos) != 1:
        raise RuntimeError(f"Expected exactly 1 repo in FORGEJO_REPOS, got: {cfg.repos}")

    collector = ForgejoCollector(cfg.base_url, cfg.token)

    cutoff = None
    if cfg.days_back is not None:
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=cfg.days_back)

    repo = cfg.repos[0]
    prs = list(collector.iter_pull_requests(cfg.owner, repo, cfg.state))
    if cutoff is not None:
        prs = [pr for pr in prs if pr.get("updated_at") and _parse_iso_z(pr["updated_at"]) >= cutoff]

    _update_backlog(cfg.backlog_file, prs)
    _git_commit_and_push(cfg.backlog_file)

    return cfg.backlog_file


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/webhook/forgejo")
async def forgejo_webhook(request: Request):
    raw = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}

    _verify_webhook(raw, headers)

    event = headers.get("x-gitea-event") or headers.get("x-forgejo-event")
    if not event:
        raise HTTPException(status_code=400, detail="Missing X-Gitea-Event header")

    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not _should_process(event, payload):
        return {"ok": True, "ignored": True, "event": event, "action": payload.get("action")}

    try:
        backlog = _run_sync()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True, "updated": str(backlog)}
