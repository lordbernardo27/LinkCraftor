from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.server.stores.raw_website_html_store import load_raw_website_html_store_v1
from backend.server.stores.html_cleaning_engine import clean_raw_html_v1

DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
STORE_DIR = DATA_ROOT / "clean_website_html"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in str(workspace_id or "default"))


def _store_path_v1(workspace_id: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"clean_website_html_{_safe_workspace_id_v1(workspace_id)}.json"


def load_clean_website_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    fp = _store_path_v1(workspace_id)
    if not fp.exists():
        return {
            "version": "clean_website_html_store_v1",
            "workspace_id": workspace_id,
            "updated_at_utc": None,
            "pages": {},
            "counts": {
                "raw_pages": 0,
                "cleaned_pages": 0,
                "failed_pages": 0,
            },
            "failures": [],
        }
    return json.loads(fp.read_text(encoding="utf-8"))


def save_clean_website_html_store_v1(workspace_id: str, store: Dict[str, Any]) -> Path:
    fp = _store_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    fp.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return fp


def build_clean_website_html_store_v1(
    *,
    workspace_id: str,
    limit: int | None = None,
) -> Dict[str, Any]:
    raw_store = load_raw_website_html_store_v1(workspace_id)
    raw_pages = raw_store.get("pages") or {}

    store = {
        "version": "clean_website_html_store_v1",
        "workspace_id": workspace_id,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_store_version": raw_store.get("version"),
        "pages": {},
        "counts": {
            "raw_pages": len(raw_pages),
            "attempted_pages": 0,
            "cleaned_pages": 0,
            "failed_pages": 0,
        },
        "failures": [],
    }

    items = list(raw_pages.items())
    if limit is not None:
        items = items[: int(limit)]

    for html_id, rec in items:
        store["counts"]["attempted_pages"] += 1

        try:
            result = clean_raw_html_v1(
                raw_html=rec.get("html", ""),
                url=rec.get("url", ""),
                title=rec.get("title", ""),
                metadata={
                    "html_id": html_id,
                    "raw_html_length": rec.get("html_length"),
                    "status_code": rec.get("status_code"),
                    "content_type": rec.get("content_type"),
                    "source_stage": "raw_website_html_store",
                },
            )

            clean_html = result.get("cleaned_html", "")

            if not clean_html:
                raise ValueError("cleaned_html_empty")

            store["pages"][html_id] = {
                "html_id": html_id,
                "workspace_id": workspace_id,
                "url": rec.get("url", ""),
                "title": rec.get("title", ""),
                "cleaned_html": clean_html,
                "original_length": result.get("original_length"),
                "cleaned_length": result.get("cleaned_length"),
                "removed_block_count": result.get("removed_block_count"),
                "cleaning_engine": result.get("engine"),
                "cleaned_at_utc": datetime.now(timezone.utc).isoformat(),
                "metadata": result.get("metadata", {}),
            }

            store["counts"]["cleaned_pages"] += 1

        except Exception as exc:
            store["counts"]["failed_pages"] += 1
            store["failures"].append({
                "html_id": html_id,
                "url": rec.get("url", ""),
                "error": str(exc),
            })

    save_clean_website_html_store_v1(workspace_id, store)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "store_path": str(_store_path_v1(workspace_id)),
        "counts": store["counts"],
        "failure_sample": store["failures"][:10],
    }


def explain_clean_website_html_store_v1() -> Dict[str, Any]:
    return {
        "name": "Clean Website HTML Store",
        "version": "clean_website_html_store_v1",
        "pipeline_stage": "HTML Cleaner",
        "input": "raw_website_html_store_v1",
        "output": "clean_website_html_store_v1",
        "next_stage": "Article Extractor",
    }
