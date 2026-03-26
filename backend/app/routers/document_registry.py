from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.server.pools.target_pools.document_registry_pool import (
    build_document_registry_pool,
)

router = APIRouter()


@router.post("/rebuild")
def rebuild_document_registry(workspace_id: str = Query(...)):
    try:
        out = build_document_registry_pool(workspace_id)
        return {"ok": True, **out}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview")
def preview_document_registry(workspace_id: str = Query(...), limit: int = Query(50, ge=1, le=500)):
    try:
        out = build_document_registry_pool(workspace_id)
        items = out.get("items") or []
        return {
            "ok": True,
            "workspace_id": workspace_id,
            "pool": "document_registry",
            "total": len(items),
            "limit": limit,
            "items": items[:limit],
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))