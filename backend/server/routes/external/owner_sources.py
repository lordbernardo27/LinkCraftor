# backend/server/routes/external/owner_sources.py
from __future__ import annotations

"""
Owner Sources routes.

Migrated gradually from:
backend/app/routers/external.py

Routes to own:
- GET  /owner/sources
- GET  /owner/counts
- POST /owner/sources/upsert
- POST /owner/sources/set_default
- POST /owner/sources/delete
"""

from typing import Any, Dict

from fastapi import APIRouter

from backend.server.routes.external.shared import (
    AUTO_PATH,
    MANUAL_PATH,
    SOURCES_PATH,
)

router = APIRouter()


@router.get("/owner_sources/status")
def owner_sources_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "phase": "1.20.2",
        "status": "owner_sources_router_scaffold_created",
        "manual_path": str(MANUAL_PATH),
        "auto_path": str(AUTO_PATH),
        "sources_path": str(SOURCES_PATH),
    }

import json
from pathlib import Path
from fastapi import HTTPException


@router.get("/owner/counts")
def owner_counts() -> Dict[str, Any]:
    def _count_records(path: Path) -> int:
        try:
            if not path.exists():
                return 0
            raw = path.read_text(encoding="utf-8", errors="replace").strip()
            if not raw:
                return 0
            data = json.loads(raw)
            if isinstance(data, list):
                return len(data)
            if isinstance(data, dict):
                if isinstance(data.get("items"), list):
                    return len(data["items"])
                if isinstance(data.get("runs"), list):
                    return len(data["runs"])
            return 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"count_failed:{path.name}:{e}")

    manual_count = _count_records(MANUAL_PATH)
    auto_count = _count_records(AUTO_PATH)

    return {
        "ok": True,
        "manual_count": manual_count,
        "auto_count": auto_count,
        "total_count": manual_count + auto_count,
        "manual_path": str(MANUAL_PATH),
        "auto_path": str(AUTO_PATH),
    }


DEFAULT_SOURCES = {
    "default_source": "mayoclinic",
    "sources": {
        "mayoclinic": {
            "label": "mayoclinic",
            "domain": "mayoclinic.org",
            "defaults": {
                "include_paths": [
                    "/healthy-lifestyle/",
                    "/diseases-conditions/",
                    "/drugs-supplements/",
                    "/symptoms/",
                    "/symptoms-causes/",
                    "/diagnosis-treatment/",
                ],
                "exclude_paths": ["/news/", "/about/", "/careers/"],
                "block_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"],
                "block_lang_prefixes": [
                    "/ar/", "/zh-hans/", "/es/", "/fr/", "/de/",
                    "/pt/", "/it/", "/ru/", "/tr/", "/vi/",
                ],
                "allow_lang_prefixes": [],
                "require_host_match": True,
                "allowed_hosts": [],
            },
        }
    },
}


from backend.server.routes.external.runtime import (
    _safe_read_json,
    _atomic_write_json,
)


def _migrate_owner_sources(existing: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(existing, dict):
        return DEFAULT_SOURCES

    out = dict(existing)

    if "default_source" not in out:
        out["default_source"] = DEFAULT_SOURCES.get("default_source", "mayoclinic")

    if "sources" not in out or not isinstance(out.get("sources"), dict):
        out["sources"] = {}

    sources = out["sources"]
    def_sources = DEFAULT_SOURCES.get("sources", {})

    for label, src_def in def_sources.items():
        if label not in sources or not isinstance(sources.get(label), dict):
            sources[label] = src_def
            continue

    return out


def _load_owner_sources() -> Dict[str, Any]:
    if not SOURCES_PATH.exists():
        _atomic_write_json(SOURCES_PATH, DEFAULT_SOURCES)

    raw = _safe_read_json(SOURCES_PATH)
    if not isinstance(raw, dict):
        raw = DEFAULT_SOURCES

    migrated = _migrate_owner_sources(raw)

    try:
        if migrated != raw:
            _atomic_write_json(SOURCES_PATH, migrated)
    except Exception:
        pass

    return migrated


@router.get("/owner/sources")
def owner_sources() -> Dict[str, Any]:
    cfg = _load_owner_sources()
    return {
        "ok": True,
        "default_source": cfg.get("default_source"),
        "sources": cfg.get("sources", {}),
    }



import re
from typing import List
from pydantic import BaseModel, Field


class OwnerSourceDefaults(BaseModel):
    include_paths: List[str] = Field(default_factory=list)
    exclude_paths: List[str] = Field(default_factory=list)
    block_extensions: List[str] = Field(default_factory=list)
    block_lang_prefixes: List[str] = Field(default_factory=list)
    allow_lang_prefixes: List[str] = Field(default_factory=list)
    require_host_match: bool = True
    allowed_hosts: List[str] = Field(default_factory=list)


class OwnerSourceUpsert(BaseModel):
    label: str = Field(..., description="Unique source key/label, e.g. 'nhs'")
    domain: str = Field(..., description="Domain only, no scheme, e.g. 'nhs.uk'")
    defaults: OwnerSourceDefaults = Field(default_factory=OwnerSourceDefaults)
    set_as_default: bool = False


def _norm_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\-_]", "", s)
    return s


def _norm_domain(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = s.split("/")[0].strip()
    s = s.split(":")[0].strip()
    return s


def _clean_path_list(xs: List[str]) -> List[str]:
    out: List[str] = []
    for x in xs or []:
        t = (x or "").strip()
        if not t:
            continue
        if not t.startswith("/"):
            t = "/" + t
        out.append(t)

    seen = set()
    uniq: List[str] = []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def _clean_ext_list(xs: List[str]) -> List[str]:
    out: List[str] = []
    for x in xs or []:
        t = (x or "").strip().lower()
        if not t:
            continue
        if not t.startswith("."):
            t = "." + t
        out.append(t)

    seen = set()
    uniq: List[str] = []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


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


class OwnerSourceSetDefault(BaseModel):
    label: str = Field(..., description="Source label to set as default")


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


class OwnerSourceDelete(BaseModel):
    label: str = Field(..., description="Source label to delete")


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
