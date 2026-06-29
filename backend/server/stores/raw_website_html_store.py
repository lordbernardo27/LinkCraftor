from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


DATA_ROOT = Path("backend/server/data")
STORE_DIR = DATA_ROOT / "raw_website_html"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in str(workspace_id or "default")
    )


def html_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"raw_html_{digest}"


def _store_path_v1(workspace_id: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"raw_website_html_{_safe_workspace_id_v1(workspace_id)}.json"


def load_raw_website_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recovered_from_error": True,
        }


def save_raw_website_html_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _store_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def upsert_raw_website_html_v1(
    *,
    workspace_id: str,
    url: str,
    html: str,
    title: str = "",
    status_code: int | None = None,
    content_type: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    store = load_raw_website_html_store_v1(workspace_id)

    html_id = html_id_for_url_v1(url)
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "html_id": html_id,
        "workspace_id": workspace_id,
        "url": url,
        "title": title,
        "html": str(html or ""),
        "html_length": len(str(html or "")),
        "status_code": status_code,
        "content_type": content_type,
        "metadata": metadata or {},
        "captured_at_utc": now,
        "source_type": "raw_website_html",
    }

    store.setdefault("pages", {})
    store["pages"][html_id] = record

    save_raw_website_html_store_v1(workspace_id, store)

    return record


def get_raw_website_html_v1(
    *,
    workspace_id: str,
    url: str | None = None,
    html_id: str | None = None,
) -> Dict[str, Any] | None:
    store = load_raw_website_html_store_v1(workspace_id)

    if html_id:
        return store.get("pages", {}).get(html_id)

    if url:
        return store.get("pages", {}).get(html_id_for_url_v1(url))

    return None
