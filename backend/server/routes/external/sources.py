from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from backend.app.routers.external import (
    OwnerSourceUpsert,
    OwnerSourceSetDefault,
    OwnerSourceDelete,
    _load_owner_sources,
    _atomic_write_json,
    SOURCES_PATH,
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


@router.get("/owner/sources")
def owner_list_sources() -> Dict[str, Any]:
    """
    Owner-only: returns backend-owned authority sources config.
    Protected by main.py middleware because path starts with /api/external/owner/
    """
    cfg = _load_owner_sources()
    return {"ok": True, "default_source": cfg.get("default_source"), "sources": cfg.get("sources", {})}


@router.post("/owner/sources/upsert")
def owner_upsert_source(payload: OwnerSourceUpsert) -> Dict[str, Any]:
    cfg = _load_owner_sources()

    label = _norm_label(payload.label)
    domain = _norm_domain(payload.domain)

    if not label:
        raise HTTPException(status_code=400, detail="label is required")
    if not domain:
        raise HTTPException(status_code=400, detail="domain is required")
    if "/" in domain:
        raise HTTPException(status_code=400, detail="domain must not contain path segments")
    if "." not in domain:
        raise HTTPException(status_code=400, detail="domain looks invalid (expected a dot)")

    d = payload.defaults or OwnerSourceDefaults()

    source_obj = {
        "label": label,
        "domain": domain,
        "defaults": {
            "include_paths": _clean_path_list(d.include_paths),
            "exclude_paths": _clean_path_list(d.exclude_paths),
            "block_extensions": _clean_ext_list(d.block_extensions),
            "block_lang_prefixes": _clean_path_list(d.block_lang_prefixes),
            "allow_lang_prefixes": _clean_path_list(d.allow_lang_prefixes),
            "require_host_match": bool(d.require_host_match),
            "allowed_hosts": [h.strip().lower() for h in (d.allowed_hosts or []) if str(h).strip()],
        },
    }

    if not isinstance(cfg.get("sources"), dict):
        cfg["sources"] = {}

    cfg["sources"][label] = source_obj

    if bool(payload.set_as_default):
        cfg["default_source"] = label

    _atomic_write_json(SOURCES_PATH, cfg)

    return {
        "ok": True,
        "saved": label,
        "default_source": cfg.get("default_source"),
        "sources_count": len(cfg.get("sources") or {}),
    }


@router.post("/owner/sources/delete")
def owner_delete_source(payload: OwnerSourceDelete) -> Dict[str, Any]:
    cfg = _load_owner_sources()

    label = _norm_label(payload.label)
    if not label:
        raise HTTPException(status_code=400, detail="label is required")

    sources = cfg.get("sources")
    if not isinstance(sources, dict) or label not in sources:
        raise HTTPException(status_code=404, detail=f"source not found: {label}")

    if len(sources) <= 1:
        raise HTTPException(status_code=400, detail="cannot delete the last remaining source")

    sources.pop(label, None)

    if cfg.get("default_source") == label:
        cfg["default_source"] = next(iter(sources.keys()), None)

    _atomic_write_json(SOURCES_PATH, cfg)

    return {
        "ok": True,
        "deleted": label,
        "default_source": cfg.get("default_source"),
        "sources_count": len(sources),
    }


@router.post("/owner/sources/set_default")
def owner_set_default_source(payload: OwnerSourceSetDefault) -> Dict[str, Any]:
    cfg = _load_owner_sources()

    label = _norm_label(payload.label)
    if not label:
        raise HTTPException(status_code=400, detail="label is required")

    sources = cfg.get("sources")
    if not isinstance(sources, dict) or label not in sources:
        raise HTTPException(status_code=404, detail=f"source not found: {label}")

    cfg["default_source"] = label
    _atomic_write_json(SOURCES_PATH, cfg)

    return {"ok": True, "default_source": label, "sources_count": len(sources)}
