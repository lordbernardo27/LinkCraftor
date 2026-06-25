# backend/server/routes/external/auto.py
from __future__ import annotations

"""
External AUTO dataset routes.

Phase 1.19.2 only creates the scaffold.
Actual routes will be migrated gradually:

- POST /import
- POST /clear
- POST /owner/auto/cleanup
- GET  /owner/auto/cleanup
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.server.routes.external.shared import (
    AUTO_PATH,
    IMPORT_RUNS_INDEX_PATH,
)

router = APIRouter()


class AutoMigrationStatus(BaseModel):
    ok: bool = True
    phase: str = "1.19.2"
    status: str = "auto_router_scaffold_created"
    auto_path: str = str(AUTO_PATH)
    import_runs_index_path: str = str(IMPORT_RUNS_INDEX_PATH)


@router.get("/auto/status")
async def auto_status() -> Dict[str, Any]:
    return AutoMigrationStatus().model_dump()

from backend.server.routes.external.runtime import (
    _safe_read_json,
    _atomic_write_json,
)


from fastapi import File, HTTPException, UploadFile
from backend.server.routes.external.runtime import (
    _safe_read_list,
    _normalize_url_for_storage,
    _is_blocked,
    _make_key,
)


