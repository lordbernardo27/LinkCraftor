# backend/server/site_reader/store.py
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _data_dir() -> str:
    # This file is: backend/server/site_reader/store.py
    # Data dir is:  backend/server/data/
    here = os.path.dirname(os.path.abspath(__file__))  # .../backend/server/site_reader
    server_dir = os.path.dirname(here)                 # .../backend/server
    return os.path.join(server_dir, "data")


def _ws_suffix(workspace_id: str) -> str:
    ws = (workspace_id or "default").strip()
    return ws if ws else "default"


def _path_sources(workspace_id: str) -> str:
    return os.path.join(_data_dir(), f"site_sources_{_ws_suffix(workspace_id)}.json")


def _path_pages(workspace_id: str) -> str:
    return os.path.join(_data_dir(), f"site_pages_{_ws_suffix(workspace_id)}.json")


def _path_phrase_index(workspace_id: str) -> str:
    return os.path.join(_data_dir(), f"site_phrase_index_{_ws_suffix(workspace_id)}.json")


def _read_json(path: str, default: Any) -> Any:
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fail-safe: never crash the pipeline because a JSON file got corrupted.
        return default


def _atomic_write_json(path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Atomic write: write to temp file then replace
    fd, tmp_path = tempfile.mkstemp(prefix="._tmp_", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


# -----------------------------
# Sources registry
# -----------------------------
def load_site_sources(workspace_id: str = "default") -> Dict[str, Any]:
    """
    Shape:
    {
      "workspace_id": "default",
      "sources": [
        { "domain": "example.com", "created_at": "...", "updated_at": "...", "seed_paths": ["/blog"] }
      ]
    }
    """
    return _read_json(_path_sources(workspace_id), {"workspace_id": _ws_suffix(workspace_id), "sources": []})


def save_site_sources(workspace_id: str, data: Dict[str, Any]) -> None:
    data["workspace_id"] = _ws_suffix(workspace_id)
    data["updated_at"] = _utc_now_iso()
    _atomic_write_json(_path_sources(workspace_id), data)


# -----------------------------
# Pages registry (URL + H1 + extracted text/headings later)
# -----------------------------
def load_site_pages(workspace_id: str = "default") -> Dict[str, Any]:
    """
    Shape:
    {
      "workspace_id":"default",
      "pages": {
         "https://example.com/blog/post-a": {
            "url":"...",
            "domain":"example.com",
            "h1":"...",
            "h2":[],
            "h3":[],
            "clean_text":"",
            "content_hash":"",
            "last_fetched_at":"..."
         }
      }
    }
    """
    return _read_json(_path_pages(workspace_id), {"workspace_id": _ws_suffix(workspace_id), "pages": {}})


def save_site_pages(workspace_id: str, data: Dict[str, Any]) -> None:
    data["workspace_id"] = _ws_suffix(workspace_id)
    data["updated_at"] = _utc_now_iso()
    _atomic_write_json(_path_pages(workspace_id), data)


# -----------------------------
# Phrase index (what the highlighter consumes)
# -----------------------------
def load_site_phrase_index(workspace_id: str = "default") -> Dict[str, Any]:
    """
    Shape:
    {
      "workspace_id":"default",
      "phrases": {
        "pregnancy due date": {
          "phrase":"Pregnancy due date",
          "norm":"pregnancy due date",
          "bucket":"internal_strong|semantic_optional",
          "type":"live_h1|live_url_slug|heading_h2|heading_h3|body_phrase",
          "confidence":0.9,
          "aliases":[],
          "source_count": 3,
          "updated_at":"..."
        }
      }
    }
    """
    return _read_json(_path_phrase_index(workspace_id), {"workspace_id": _ws_suffix(workspace_id), "phrases": {}})


def save_site_phrase_index(workspace_id: str, data: Dict[str, Any]) -> None:
    data["workspace_id"] = _ws_suffix(workspace_id)
    data["updated_at"] = _utc_now_iso()
    _atomic_write_json(_path_phrase_index(workspace_id), data)
