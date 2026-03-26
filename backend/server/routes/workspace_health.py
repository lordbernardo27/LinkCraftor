from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/workspace", tags=["workspace"])

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TARGET_POOLS_DIR = DATA_DIR / "target_pools"


def _safe_json_load(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _count_items(obj: Any) -> int:
    if obj is None:
        return 0

    if isinstance(obj, dict):
        # common pool structure: {"items": [...]}
        if "items" in obj and isinstance(obj["items"], list):
            return len(obj["items"])

        # imported compat/list-like shapes
        for k in ("urls", "data"):
            if k in obj and isinstance(obj[k], list):
                return len(obj[k])

        # live site pages shape
        if "pages" in obj and isinstance(obj["pages"], dict):
            return len(obj["pages"])
        if "pages" in obj and isinstance(obj["pages"], list):
            return len(obj["pages"])

        return len(obj)

    if isinstance(obj, list):
        return len(obj)

    return 0


def _extract_last_updated(obj: Any) -> str:
    if not isinstance(obj, dict):
        return ""
    return (
        obj.get("generated_at")
        or obj.get("last_updated_at_utc")
        or obj.get("last_import_at_utc")
        or ""
    )


def _pool_record(name: str, data_path: Path):
    data = _safe_json_load(data_path)
    return {
        "pool": name,
        "count": _count_items(data),
        "data_path": str(data_path),
        "last_updated_at_utc": _extract_last_updated(data),
    }


@router.get("/pools")
def workspace_pools(workspace_id: str = Query(..., description="workspace id")):
    live_data = TARGET_POOLS_DIR / "live_domain" / f"live_domain_target_pool_{workspace_id}.json"
    imported_data = TARGET_POOLS_DIR / "imported" / f"imported_target_pool_{workspace_id}.json"
    draft_data = TARGET_POOLS_DIR / "draft" / f"draft_target_pool_{workspace_id}.json"
    document_registry_data = (
        TARGET_POOLS_DIR / "document_registry" / f"document_registry_{workspace_id}.json"
    )

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "pools": [
            _pool_record("live_domain", live_data),
            _pool_record("imported", imported_data),
            _pool_record("draft", draft_data),
            _pool_record("document_registry", document_registry_data),
        ],
    }