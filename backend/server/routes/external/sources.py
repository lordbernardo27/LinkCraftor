from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from backend.server.routes.external.owner_sources import (
    OwnerSourceUpsert,
    OwnerSourceSetDefault,
    OwnerSourceDelete,
    OwnerSourceDefaults,
    _load_owner_sources,
    _atomic_write_json,
    SOURCES_PATH,
    _norm_label,
    _norm_domain,
    _clean_path_list,
    _clean_ext_list,
)

router = APIRouter(tags=["external-sources-runtime"])


@router.get("/sources/status")
def sources_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.sources",
        "routes": [
            "/owner/sources",
            "/owner/sources/upsert",
            "/owner/sources/delete",
            "/owner/sources/set_default",
        ],
    }


