from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException

from backend.app.routers.external import (
    OwnerRollbackRequest,
    AUDIT_PATH,
    AUTO_PATH,
    _snapshot_path,
    _safe_read_list,
    _atomic_write_json,
    _audit,
)

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
