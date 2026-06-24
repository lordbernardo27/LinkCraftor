from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Body, HTTPException

from pydantic import BaseModel

from backend.server.routes.external.shared import (
    AUDIT_PATH,
    AUTO_PATH,
    SNAPSHOT_DIR,
)


class OwnerRollbackRequest(BaseModel):
    import_run_id: str
    preview: bool = True


def _snapshot_path(run_id: str) -> Path:
    safe = "".join(c for c in str(run_id or "") if c.isalnum() or c in ("_", "-"))
    return SNAPSHOT_DIR / f"{safe}.json"


def _safe_read_list(path: Path) -> list:
    try:
        if not path.exists():
            return []
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _audit(event: str, payload: Dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rec = {"event": event, **(payload or {})}
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

router = APIRouter(tags=["external-import-runs-runtime"])


@router.get("/import_runs/status")
def import_runs_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.import_runs",
        "routes": [
            "/owner/import/runs",
            "/owner/import/rollback",
        ],
    }


@router.get("/owner/import/runs")
async def owner_import_runs(limit: int = 20):
    limit = max(1, int(limit or 20))
    if not AUDIT_PATH.exists():
        return {"ok": True, "count": 0, "items": [], "path": str(AUDIT_PATH)}

    items: List[Dict[str, Any]] = []
    try:
        lines = AUDIT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in reversed(lines):
            line = (line or "").strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            ev = str(rec.get("event") or "")
            if ev not in ("owner_sitemap_commit_auto", "owner_import_rollback", "owner_resolver_add"):
                continue

            items.append(rec)
            if len(items) >= limit:
                break

        items.reverse()
        return {"ok": True, "count": len(items), "items": items, "path": str(AUDIT_PATH)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"import_runs_error: {type(e).__name__}: {str(e)}")


@router.post("/owner/import/rollback")
async def owner_import_rollback(payload: OwnerRollbackRequest = Body(...)):
    run_id = (payload.import_run_id or "").strip()
    if not run_id:
        raise HTTPException(status_code=400, detail="import_run_id is required")

    snap_path = _snapshot_path(run_id)
    if not snap_path.exists():
        raise HTTPException(status_code=404, detail=f"snapshot not found for import_run_id={run_id}")

    before_count = len(_safe_read_list(AUTO_PATH))
    snap_data = _safe_read_list(snap_path)
    after_count = len(snap_data)

    if payload.preview:
        return {
            "ok": True,
            "preview": True,
            "import_run_id": run_id,
            "auto_before_count": before_count,
            "auto_after_count": after_count,
            "snapshot_path": str(snap_path),
            "action": "would_restore_snapshot",
        }

    _atomic_write_json(AUTO_PATH, snap_data)

    _audit("owner_import_rollback", {
        "import_run_id": run_id,
        "snapshot_path": str(snap_path),
        "auto_before_count": before_count,
        "auto_after_count": after_count,
    })

    return {
        "ok": True,
        "preview": False,
        "import_run_id": run_id,
        "auto_before_count": before_count,
        "auto_after_count": after_count,
        "snapshot_path": str(snap_path),
        "action": "restored",
    }
