
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("backend/server/data/workspaces")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_slug(value: str) -> str:
    text = str(value or "default").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"^_+|_+$", "", text)
    return text or "default"


def workspace_root(workspace_id: str) -> Path:
    return DATA_DIR / safe_slug(workspace_id)


def saved_sessions_root(workspace_id: str) -> Path:
    return workspace_root(workspace_id) / "saved_sessions"


def ensure_workspace_saved_session_dirs(workspace_id: str) -> Dict[str, Any]:
    root = workspace_root(workspace_id)
    sessions = saved_sessions_root(workspace_id)

    root.mkdir(parents=True, exist_ok=True)
    sessions.mkdir(parents=True, exist_ok=True)

    return {
        "workspace_id": workspace_id,
        "workspace_root": str(root),
        "saved_sessions_root": str(sessions),
        "created_at": utc_now_iso(),
    }


def create_session_id(prefix: str = "session") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{safe_slug(prefix)}_{stamp}"


def session_root(workspace_id: str, session_id: str) -> Path:
    return saved_sessions_root(workspace_id) / safe_slug(session_id)


def ensure_session_dirs(workspace_id: str, session_id: str) -> Dict[str, Any]:
    root = session_root(workspace_id, session_id)

    folders = {
        "root": root,
        "documents": root / "documents",
        "imports": root / "imports",
        "drafts": root / "drafts",
        "engine": root / "engine",
        "decisions": root / "decisions",
    }

    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)

    return {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "paths": {key: str(value) for key, value in folders.items()},
        "created_at": utc_now_iso(),
    }


def write_json(path: Path, data: Dict[str, Any] | List[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any] | List[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def create_default_session_files(
    workspace_id: str,
    session_id: str,
    domain: str = "",
) -> Dict[str, Any]:
    ensure_session_dirs(workspace_id, session_id)
    root = session_root(workspace_id, session_id)

    files = {
        "documents": root / "documents" / "documents.json",
        "imported_sitemaps": root / "imports" / "imported_sitemaps.json",
        "draft_topics": root / "drafts" / "draft_topics.json",
        "engine_state": root / "engine" / "session_state.json",
        "decisions": root / "decisions" / "decisions.json",
    }

    defaults = {
        "documents": {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "active_document_id": "",
            "documents": [],
            "updated_at": utc_now_iso(),
        },
        "imported_sitemaps": {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "domain": domain,
            "imported_urls": [],
            "import_stats": {
                "total_urls": 0,
                "source": "",
            },
            "updated_at": utc_now_iso(),
        },
        "draft_topics": {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "draft_topics": [],
            "updated_at": utc_now_iso(),
        },
        "engine_state": {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "domain": domain,
            "active_document_id": "",
            "last_engine_run": None,
            "accepted_links": [],
            "rejected_links": [],
            "manual_links": [],
            "updated_at": utc_now_iso(),
        },
        "decisions": {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "decisions": [],
            "updated_at": utc_now_iso(),
        },
    }

    for key, file_path in files.items():
        if not file_path.exists():
            write_json(file_path, defaults[key])

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "session_id": session_id,
        "files": {key: str(path) for key, path in files.items()},
    }


def create_session_manifest(
    workspace_id: str,
    session_id: str,
    domain: str = "",
    title: str = "",
) -> Dict[str, Any]:
    ensure_session_dirs(workspace_id, session_id)
    create_default_session_files(workspace_id, session_id, domain)

    manifest = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "domain": domain,
        "title": title or session_id,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "version": "workspace_session_snapshot_v1",
        "contains": {
            "documents": True,
            "imported_sitemaps": True,
            "draft_topics": True,
            "engine_state": True,
            "decisions": True,
        },
        "files": {
            "documents": "documents/documents.json",
            "imported_sitemaps": "imports/imported_sitemaps.json",
            "draft_topics": "drafts/draft_topics.json",
            "engine_state": "engine/session_state.json",
            "decisions": "decisions/decisions.json",
        },
    }

    write_json(session_root(workspace_id, session_id) / "manifest.json", manifest)
    return manifest
