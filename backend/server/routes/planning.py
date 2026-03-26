from fastapi import APIRouter, Query
import os, json, re
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/api/planning", tags=["planning"])


def _data_dir() -> str:
    # backend/server/data
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _ws_safe(ws: str) -> str:
    ws = (ws or "default").strip().lower()
    return re.sub(r"[^a-z0-9_\-]", "_", ws)[:80] or "default"


def _safe_read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _path_imported_urls(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"imported_urls_{ws}.json")


def _path_draft_topics(workspace_id: str) -> str:
    ws = _ws_safe(workspace_id)
    return os.path.join(_data_dir(), f"draft_topic_{ws}.json")


@router.get("/draft_audit")
async def draft_audit(
    workspace_id: str = Query("default"),
    limit: int = Query(5000, ge=1, le=200000),
):
    """
    Draft Audit (PRE-PUBLISH WORKFLOW)

    Draft topics are INTERNAL PLACEHOLDER targets used for linking now,
    even before pages are published.

    "matched"  = drafts that already have >=1 inbound link pointing to them
                 via a draft placeholder target (lc:draft:<topic_id> or linkcraftor://draft/<topic_id>).
    "missing"  = drafts with 0 inbound placeholder links.

    NOTE: imported sitemap URLs are NOT used to evaluate draft matching.
    They are returned only as a count for UI continuity.
    """

    ws = _ws_safe(workspace_id)

    imported_path = _path_imported_urls(workspace_id)
    draft_path = _path_draft_topics(workspace_id)

    imported_raw = _safe_read_json(imported_path)
    draft_raw = _safe_read_json(draft_path)

    imported_list = imported_raw if isinstance(imported_raw, list) else []
    draft_list = draft_raw if isinstance(draft_raw, list) else []

    # --- helper: extract draft topic_id from placeholder href/url ---
    def _extract_draft_topic_id(val: str) -> Optional[str]:
        try:
            s = str(val or "").strip()
        except Exception:
            return None
        if not s:
            return None

        low = s.lower()

        # Form 1: lc:draft:<topic_id>
        if low.startswith("lc:draft:"):
            return s[len("lc:draft:") :].strip() or None

        # Form 2: linkcraftor://draft/<topic_id>
        if low.startswith("linkcraftor://draft/"):
            return s[len("linkcraftor://draft/") :].strip().strip("/") or None

        return None

    # --- scan decisions.jsonl for inbound draft placeholder links ---
    # decisions live in backend/server/routes/engine_decisions.py as DECISIONS_PATH
    # Import safely here to avoid circular import issues.
    try:
        from .engine_decisions import DECISIONS_PATH  # type: ignore
    except Exception:
        DECISIONS_PATH = os.path.join(_data_dir(), "decisions.jsonl")

    inbound_counts: Dict[str, int] = {}

    if os.path.exists(DECISIONS_PATH):
        try:
            with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = (line or "").strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue

                    # Workspace filter (only count events for this workspace if present)
                    w = obj.get("workspaceId") or obj.get("workspace_id") or obj.get("workspace")
                    if w and _ws_safe(str(w)) != ws:
                        continue

                    # Candidate URL / href is stored on accepted/rejected decisions
                    cand = obj.get("candidate") or {}
                    url = cand.get("url") or cand.get("href") or ""

                    tid = _extract_draft_topic_id(url)
                    if not tid:
                        continue

                    inbound_counts[tid] = int(inbound_counts.get(tid, 0)) + 1
        except Exception:
            # If decisions file is locked/corrupt, treat as no inbound links
            inbound_counts = {}

    # --- build matched/missing lists ---
    matched: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    no_planned_url: List[Dict[str, Any]] = []

    for rec in draft_list:
        if not isinstance(rec, dict):
            continue

        topic_id = str(rec.get("topic_id") or rec.get("id") or "").strip()
        planned_url = str(rec.get("planned_url") or "").strip()

        if not planned_url:
            no_planned_url.append(rec)

        # matched if we have inbound placeholder links for this topic_id
        if topic_id and inbound_counts.get(topic_id, 0) > 0:
            matched.append(rec)
        else:
            missing.append(rec)

    # Output (capped)
    matched_out = matched[:limit]
    missing_out = missing[:limit]
    no_planned_out = no_planned_url[:limit]

    return {
        "workspace_id": ws,
        "paths": {
            "imported_urls": imported_path,
            "draft_topics": draft_path,
            "decisions_path": os.path.abspath(DECISIONS_PATH),
        },
        "counts": {
            # kept for UI continuity
            "sitemap_urls": len(imported_list),
            "draft_topics_total": len(draft_list),

            # ✅ correct semantics now
            "matched": len(matched),
            "missing": len(missing),
            "no_planned_url": len(no_planned_url),

            # extra visibility
            "inbound_draft_links": int(sum(inbound_counts.values())) if inbound_counts else 0,
            "drafts_with_inbound": len([k for k, v in inbound_counts.items() if int(v) > 0]),
        },
        "matched": matched_out,
        "missing": missing_out,
        "no_planned_url": no_planned_out,
    }
