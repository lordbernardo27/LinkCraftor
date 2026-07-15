from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.server.stores.universal_content_body_formatter import (
    format_universal_content_body_v1,
)


DATA_ROOT = Path("backend/server/data")
STORE_DIR = DATA_ROOT / "website_unified_content"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in str(workspace_id or "default"))


def _content_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"web_content_{digest}"


def _store_path_v1(workspace_id: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"website_unified_content_{_safe_workspace_id_v1(workspace_id)}.json"


def load_website_unified_content_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "website_unified_content_store_v2",
            "workspace_id": workspace_id,
            "documents": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "website_unified_content_store_v2",
            "workspace_id": workspace_id,
            "documents": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recovered_from_error": True,
        }


def save_website_unified_content_store_v1(workspace_id: str, store: Dict[str, Any]) -> Path:
    path = _store_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def upsert_website_unified_content_document_v1(
    *,
    workspace_id: str,
    url: str,
    title: str = "",
    h1: str = "",
    article_body: str = "",
    headings: list | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    store = load_website_unified_content_store_v1(workspace_id)

    formatted_body = format_universal_content_body_v1(
        text=article_body,
        headings=headings or [],
        title=title,
    )

    content_text = str(
        formatted_body.get("content_body") or ""
    ).strip()
    content_id = _content_id_for_url_v1(url)
    now = datetime.now(timezone.utc).isoformat()

    document_metadata = dict(metadata or {})

    document_metadata["content_body_formatting"] = {
        "formatter": formatted_body.get("formatter"),
        "format": formatted_body.get("format"),
        "source_mode": formatted_body.get("source_mode"),
        "paragraph_count": formatted_body.get("paragraph_count"),
        "heading_count": formatted_body.get("heading_count"),
        "word_count": formatted_body.get("word_count"),
        "content_length": formatted_body.get("content_length"),
    }

    if h1:
        document_metadata["source_h1"] = h1

    if semantic_features:
        document_metadata["semantic_features"] = semantic_features

    document = {
        "content_id": content_id,
        "workspace_id": workspace_id,
        "source_type": "website_crawl",
        "url": str(url or "").strip(),
        "title": str(title or h1 or "").strip(),
        "article_body": content_text,
        "headings": list(headings or []),
        "metadata": document_metadata,
        "quality": dict(quality or {}),
        "created_or_updated_at_utc": now,
    }

    store.setdefault("documents", {})
    store["documents"][content_id] = document

    save_website_unified_content_store_v1(workspace_id, store)

    return document


def get_website_unified_content_document_v1(
    *,
    workspace_id: str,
    url: str | None = None,
    content_id: str | None = None,
) -> Dict[str, Any] | None:
    store = load_website_unified_content_store_v1(workspace_id)

    if content_id:
        return store.get("documents", {}).get(content_id)

    if url:
        return store.get("documents", {}).get(_content_id_for_url_v1(url))

    return None
