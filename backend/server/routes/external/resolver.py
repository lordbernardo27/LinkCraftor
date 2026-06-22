# backend/server/routes/external/resolver.py
from __future__ import annotations

"""
Owner Resolver routes.

Migrated gradually from:
backend/app/routers/external.py

Routes to own:
- GET  /owner/resolver/search
- POST /owner/resolver/add
"""

from typing import Any, Dict

from fastapi import APIRouter

from backend.server.routes.external.shared import (
    AUTO_PATH,
    IMPORT_RUNS_INDEX_PATH,
    AUDIT_PATH,
)

router = APIRouter()


@router.get("/resolver/status")
def resolver_status() -> Dict[str, Any]:
    return {
        "ok": True,
        "phase": "1.21.2",
        "status": "resolver_router_scaffold_created",
        "auto_path": str(AUTO_PATH),
        "import_runs_index_path": str(IMPORT_RUNS_INDEX_PATH),
        "audit_path": str(AUDIT_PATH),
    }

import json
import urllib.parse
import urllib.request
from typing import List


def _pubmed_esearch(term: str, retmax: int = 50, retstart: int = 0) -> Dict[str, Any]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    q = urllib.parse.urlencode({
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": str(max(0, int(retmax))),
        "retstart": str(max(0, int(retstart))),
        "sort": "relevance",
    })
    url = f"{base}?{q}"

    try:
        with urllib.request.urlopen(url, timeout=12) as resp:
            raw = resp.read().decode("utf-8", errors="replace")

        data = json.loads(raw) or {}
        esr = data.get("esearchresult", {}) if isinstance(data, dict) else {}
        ids = esr.get("idlist", []) or []
        count = int(esr.get("count", 0) or 0)

        return {"count": count, "ids": [str(x) for x in ids if str(x).strip()]}
    except Exception:
        return {"count": 0, "ids": []}


def _pubmed_esummary_batched(id_list: List[str], batch_size: int = 200) -> Dict[str, Any]:
    if not id_list:
        return {}

    merged: Dict[str, Any] = {"result": {"uids": []}}
    all_uids: List[str] = []

    for i in range(0, len(id_list), batch_size):
        chunk = id_list[i:i + batch_size]
        base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        q = urllib.parse.urlencode({
            "db": "pubmed",
            "id": ",".join(chunk),
            "retmode": "json",
        })
        url = f"{base}?{q}"

        try:
            with urllib.request.urlopen(url, timeout=12) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw) or {}
        except Exception:
            continue

        result = data.get("result", {}) if isinstance(data, dict) else {}
        uids = result.get("uids", []) if isinstance(result, dict) else []

        for uid in uids:
            uid = str(uid).strip()
            if not uid:
                continue
            if uid not in all_uids:
                all_uids.append(uid)

            row = result.get(uid)
            if isinstance(row, dict):
                merged["result"][uid] = row

    merged["result"]["uids"] = all_uids
    return merged

from fastapi import HTTPException, Query
from backend.server.routes.external.owner_sources import _norm_label


def _slugify(s: str) -> str:
    import re
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


@router.get("/owner/resolver/search")
def owner_resolver_search(
    phrase: str = Query(..., description="Search phrase, e.g. 'amlodipine side effects'"),
    source_label: str = Query("pubmed", description="Provider label (only 'pubmed' supported)"),
    limit: int = Query(50, ge=1, le=5000, description="Number of results to return"),
    retstart: int = Query(0, ge=0, description="Pagination offset (0-based)"),
) -> Dict[str, Any]:
    p = (phrase or "").strip()
    if not p:
        raise HTTPException(status_code=400, detail="phrase is required")

    src = _norm_label(source_label)
    if src != "pubmed":
        raise HTTPException(status_code=400, detail="Only source_label=pubmed is supported in this step")

    es = _pubmed_esearch(p, retmax=int(limit), retstart=int(retstart))
    total_count = int(es.get("count", 0) or 0)
    ids = es.get("ids", []) or []

    if not ids:
        return {
            "ok": True,
            "source_label": src,
            "phrase": p,
            "total_count": total_count,
            "retstart": retstart,
            "limit": limit,
            "returned": 0,
            "has_more": False,
            "next_retstart": None,
            "items": [],
        }

    summ = _pubmed_esummary_batched(ids, batch_size=200)
    result = summ.get("result", {}) if isinstance(summ, dict) else {}
    uids = result.get("uids", []) if isinstance(result, dict) else []

    ordered = [str(x) for x in (uids or ids) if str(x).strip()]

    items = []
    returned = 0
    denom = max(1, len(ordered))

    for idx, pmid in enumerate(ordered):
        row = result.get(pmid)
        if not isinstance(row, dict):
            continue

        title = str(row.get("title") or "").strip()
        if title.endswith("."):
            title = title[:-1].strip()

        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        score = max(0.0, 1.0 - (idx / denom))

        pubdate = (row.get("pubdate") or "").strip()
        journal = (row.get("fulljournalname") or row.get("source") or "").strip()

        items.append({
            "id": pmid,
            "title": title or f"PubMed {pmid}",
            "title_slug": _slugify(title) if title else None,
            "url": url,
            "source_label": src,
            "score": round(score, 4),
            "pubdate": pubdate,
            "journal": journal,
        })
        returned += 1

    return {
        "ok": True,
        "source_label": src,
        "phrase": p,
        "total_count": total_count,
        "retstart": retstart,
        "limit": limit,
        "returned": returned,
        "has_more": (retstart + returned) < total_count,
        "next_retstart": (retstart + returned) if ((retstart + returned) < total_count) else None,
        "items": items,
    }


from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.server.routes.external.runtime import (
    _safe_read_list,
    _atomic_write_json,
    _normalize_url_for_storage,
    _make_key,
)



def _append_import_run_index(entry: Dict[str, Any], max_keep: Optional[int] = None) -> None:
    raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
    if not isinstance(raw, dict):
        raw = {}

    runs = raw.get("runs")
    if not isinstance(runs, list):
        runs = []

    runs.append(entry)

    if max_keep is not None:
        try:
            max_keep_int = int(max_keep)
            if max_keep_int > 0:
                runs = runs[-max_keep_int:]
        except Exception:
            pass

    raw["runs"] = runs
    raw["items"] = runs
    _atomic_write_json(IMPORT_RUNS_INDEX_PATH, raw)
class OwnerResolverSelection(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    title_slug: Optional[str] = None
    url: str
    source_label: Optional[str] = None
    score: Optional[float] = None
    pubdate: Optional[str] = None
    journal: Optional[str] = None


class OwnerResolverAddPayload(BaseModel):
    phrase: str = Field(..., description="Original phrase, e.g. 'amlodipine side effects'")
    source_label: str = Field(..., description="Provider/source label, e.g. 'pubmed'")
    selection: OwnerResolverSelection


@router.post("/owner/resolver/add")
def owner_resolver_add(payload: OwnerResolverAddPayload) -> Dict[str, Any]:
    phrase = (payload.phrase or "").strip()
    source_label = _norm_label(payload.source_label)

    if not phrase:
        raise HTTPException(status_code=400, detail="phrase is required")
    if not source_label:
        raise HTTPException(status_code=400, detail="source_label is required")

    sel = payload.selection
    raw_url = (sel.url or "").strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="selection.url is required")

    url = _normalize_url_for_storage(raw_url)
    if not url:
        raise HTTPException(status_code=400, detail="selection.url invalid after normalization")

    title = (sel.title or "").strip() or None
    title_slug = (sel.title_slug or "").strip() or (_slugify(title) if title else None)
    ext_id = (sel.id or "").strip() or None

    key = _make_key(f"{phrase}::{source_label}::{ext_id or url}")

    auto_items = _safe_read_list(AUTO_PATH)

    existing = next((x for x in auto_items if isinstance(x, dict) and (x.get("key") or "") == key), None)

    now = datetime.utcnow().isoformat() + "Z"

    candidate = {
        "key": key,
        "phrase": phrase,
        "url": url,
        "title": title,
        "title_slug": title_slug,
        "source_label": source_label,
        "resolver_id": ext_id,
        "source": source_label,
        "provider_id": ext_id,
        "added_at": now,
        "updated_at": now,
        "disabled": False,
    }

    if not existing:
        auto_items.append(candidate)
        action = "added"
        saved_record = candidate
    else:
        existing.update({
            "phrase": phrase,
            "url": url,
            "title": title,
            "title_slug": title_slug,
            "source_label": source_label,
            "resolver_id": ext_id,
            "source": source_label,
            "provider_id": ext_id,
            "updated_at": now,
        })
        existing.setdefault("added_at", now)
        existing.setdefault("disabled", False)
        action = "updated"
        saved_record = existing

    _atomic_write_json(AUTO_PATH, auto_items)

    import_run_id = f"owner_resolver_{int(datetime.utcnow().timestamp())}"

    try:
        audit = {
            "ts": now,
            "event": "owner_resolver_add",
            "phrase": phrase,
            "key": key,
            "source_label": source_label,
            "selection": {"url": url, "title": title, "title_slug": title_slug, "id": ext_id},
            "auto_added": 1 if action == "added" else 0,
            "auto_updated": 1 if action == "updated" else 0,
        }
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(audit, ensure_ascii=False) + "\n")

        _append_import_run_index({
            "ts": now,
            "event": "owner_resolver_add",
            "import_run_id": import_run_id,
            "source_label": source_label,
            "auto_added": 1 if action == "added" else 0,
            "auto_updated": 1 if action == "updated" else 0,
            "snapshot_path": "",
        }, max_keep=None)
    except Exception:
        pass

    return {
        "ok": True,
        "action": action,
        "import_run_id": import_run_id,
        "auto_path": str(AUTO_PATH),
        "record": saved_record,
    }

