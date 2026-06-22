from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter

from backend.app.routers.external import (
    ExternalCandidate,
    _make_key,
    _ensure_resolve_index_uptodate,
    _RESOLVE_INDEX,
    _normalize_url_for_storage,
)

router = APIRouter(tags=["external-resolve-runtime"])


@router.get("/resolve/status")
def resolve_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "router": "external.resolve",
        "routes": [
            "/resolve",
        ],
    }


@router.get("/resolve", response_model=List[ExternalCandidate])
async def external_resolve(phrase: str, lang: str = "en", source_label: Optional[str] = None):
    q = (phrase or "").strip()
    if not q:
        return []

    query_key = _make_key(q)
    _ensure_resolve_index_uptodate()

    manual_hits = _RESOLVE_INDEX["manual_by_key"].get(query_key, []) or []
    auto_hits = _RESOLVE_INDEX["auto_by_key"].get(query_key, []) or []

    hits = manual_hits if manual_hits else auto_hits

    want_label = (source_label or "").strip().lower()
    if want_label:
        hits = [
            it for it in hits
            if str((it or {}).get("source_label") or "").strip().lower() == want_label
        ]

    out: List[ExternalCandidate] = []
    for item in hits[:8]:
        if not isinstance(item, dict):
            continue
        url = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not url:
            continue
        out.append(
            ExternalCandidate(
                phrase=q,
                url=url,
                title=item.get("title") or item.get("phrase") or q,
                score=float(item.get("score", 1.0) or 1.0),
                source=str(item.get("source") or ("manual" if manual_hits else "auto")),
                source_label=(str(item.get("source_label")).strip() if item.get("source_label") else None),
            )
        )

    out.sort(key=lambda x: x.score, reverse=True)
    return out
