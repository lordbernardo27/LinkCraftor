# backend/server/routes/engine_scoring.py
import json
import re
from pathlib import Path

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..stores.link_decision_store import save_link_decision

from .engine_decisions import get_aggregated_link_feedback
from ..engine.scoring import score_candidates_for_phrase
from ..engine.profiles import PROFILES, normalize_profile_id
from ..engine.link_decision_builder import build_link_decision
from ..stores.workspace_profile_store import get_workspace_profile, set_workspace_profile

router = APIRouter(prefix="/api/engine", tags=["engine"])


class PhraseContextModel(BaseModel):
    # Added for Decision Intelligence memory lookup
    workspaceId: Optional[str] = None

    phraseText: str
    contextText: Optional[str] = None
    docId: Optional[str] = None
    sectionId: Optional[str] = None
    position: Optional[int] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    graphVector: Optional[List[float]] = None
    graphRelations: List[Dict[str, Any]] = Field(default_factory=list)
    contextType: Optional[str] = None
    sectionType: Optional[str] = None
    intent: Optional[str] = None
    discourseRole: Optional[str] = None


class CandidateModel(BaseModel):
    id: str
    title: str
    url: str
    docId: Optional[str] = None
    sectionId: Optional[str] = None
    sourceType: Optional[str] = None
    isExternal: Optional[bool] = False
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    topicTypes: List[str] = Field(default_factory=list)
    sectionRoles: List[str] = Field(default_factory=list)
    intentTags: List[str] = Field(default_factory=list)
    discourseTags: List[str] = Field(default_factory=list)
    graphVector: Optional[List[float]] = None
    graphRelations: List[Dict[str, Any]] = Field(default_factory=list)
    domain: Optional[str] = None
    isCanonicalTopic: Optional[bool] = False


class ScoreRequest(BaseModel):
    phraseCtx: PhraseContextModel
    candidates: List[CandidateModel]
    profile: Optional[str] = None


class WorkspaceProfileRequest(BaseModel):
    workspaceId: str
    profile: str

def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw or raw.lower() == "default":
        return "default"
    if raw.lower().startswith("ws_"):
        return raw

    s = raw.lower()
    s = s.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return f"ws_{s or 'workspace'}"[:80]


def _load_supporting_intelligence_inputs(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    here = Path(__file__).resolve()
    server_dir = here.parents[1]

    path = (
        server_dir
        / "data"
        / "phrase_pools"
        / "active"
        / f"active_phrase_pool_{ws}.json"
    )

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "enabled": False,
            "reason": "active_phrase_pool_not_found",
            "runtime_highlight_injection_allowed": False,
            "sources": {},
        }

    supporting = obj.get("supporting_intelligence_inputs")
    if not isinstance(supporting, dict):
        return {
            "enabled": False,
            "reason": "supporting_intelligence_inputs_missing",
            "runtime_highlight_injection_allowed": False,
            "sources": {},
        }

    supporting["runtime_highlight_injection_allowed"] = False
    return supporting

def _load_imported_di_signal(workspace_id: str, phrase_text: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    phrase_norm = re.sub(r"\s+", " ", str(phrase_text or "").lower().strip())

    if not phrase_norm:
        return {
            "enabled": False,
            "reason": "empty_phrase",
            "has_match": False,
        }

    here = Path(__file__).resolve()
    server_dir = here.parents[1]

    path = (
        server_dir
        / "data"
        / "phrase_pools"
        / "imported"
        / f"imported_phrase_pool_{ws}.json"
    )

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "enabled": False,
            "reason": "imported_pool_not_found",
            "has_match": False,
        }

    phrases = obj.get("phrases") if isinstance(obj.get("phrases"), dict) else {}

    def toks(s: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]{2,}", str(s or "").lower()))

    phrase_tokens = toks(phrase_norm)
    best = None
    best_score = 0.0

    for imported_phrase, rec in phrases.items():
        imported_norm = re.sub(r"\s+", " ", str(imported_phrase or "").lower().strip())
        imported_tokens = toks(imported_norm)

        if not imported_tokens:
            continue

        overlap = len(phrase_tokens & imported_tokens) / max(1, len(phrase_tokens | imported_tokens))

        exact = 1.0 if phrase_norm == imported_norm else 0.0
        contains = 0.75 if phrase_norm in imported_norm or imported_norm in phrase_norm else 0.0
        pool_score = float((rec or {}).get("score") or 0.0)
        if pool_score > 1:
            pool_score = pool_score / 100.0

        signal_score = max(exact, contains, overlap)
        signal_score = round((signal_score * 0.75) + (pool_score * 0.25), 4)

        if signal_score > best_score:
            best_score = signal_score
            best = {
                "phrase": imported_norm,
                "score": signal_score,
                "pool_score": round(pool_score, 4),
                "urls": (rec or {}).get("urls") or [],
                "snippets": (rec or {}).get("snippets") or [],
                "source_type": (rec or {}).get("source_type"),
                "vertical": (rec or {}).get("vertical"),
            }

    return {
        "enabled": True,
        "source": "imported_pool",
        "runtime_highlight_injection_allowed": False,
        "has_match": bool(best and best_score >= 0.35),
        "best_match": best if best and best_score >= 0.35 else None,
    }


@router.post("/workspace-profile")
def set_workspace_profile_endpoint(payload: WorkspaceProfileRequest):
    workspace_id = str(payload.workspaceId or "").strip()
    profile = normalize_profile_id(payload.profile)

    saved_profile = set_workspace_profile(workspace_id, profile)

    return {
        "ok": True,
        "workspaceId": workspace_id,
        "profile": saved_profile,
    }


@router.get("/workspace-profile/{workspace_id}")
def get_workspace_profile_endpoint(workspace_id: str):
    workspace_key = str(workspace_id or "").strip()
    profile = get_workspace_profile(workspace_key)

    return {
        "ok": True,
        "workspaceId": workspace_key,
        "profile": profile,
    }


@router.get("/profiles")
def list_profiles_endpoint():
    preferred_order = ["general", "medical", "saas", "finance", "ecommerce"]

    items = []
    for profile_id in preferred_order:
        profile = PROFILES.get(profile_id)
        if not profile:
            continue
        items.append({
            "id": profile_id,
            "display_name": profile.get("display_name", profile_id),
        })

    for profile_id, profile in PROFILES.items():
        if profile_id in preferred_order:
            continue
        items.append({
            "id": profile_id,
            "display_name": profile.get("display_name", profile_id),
        })

    return {
        "ok": True,
        "profiles": items,
    }


@router.post("/score")
def score_endpoint(payload: ScoreRequest, debug: bool = False):
    phrase_ctx = payload.phraseCtx.model_dump()
    candidates = [c.model_dump() for c in payload.candidates]
    workspace_id = phrase_ctx.get("workspaceId") or "default"

    # Normal behavior: resolve profile from workspace only.
    profile = normalize_profile_id(get_workspace_profile(workspace_id))

    # Optional internal/testing override: only allowed in debug mode.
    if debug and payload.profile:
        profile = normalize_profile_id(payload.profile)

    supporting_intelligence_inputs = _load_supporting_intelligence_inputs(workspace_id)

    imported_di_signal = _load_imported_di_signal(
        workspace_id,
        phrase_ctx.get("phraseText"),
    )

    # Debug mode: keep extra payload, but still run scoring.
    debug_payload = None
    if debug:
        debug_payload = {
            "phrase_ctx": phrase_ctx,
            "candidate_count": len(candidates),
            "candidates_sample": candidates[:3],
            "supporting_intelligence_inputs": supporting_intelligence_inputs,
            "imported_di_signal": imported_di_signal,
        }

    # ---- Decision Intelligence: load feedback memory for this workspace/doc ----
    doc_id = phrase_ctx.get("docId")
    feedback_map = get_aggregated_link_feedback(workspaceId=workspace_id, docId=doc_id)

    out = score_candidates_for_phrase(
        phrase_ctx,
        candidates,
        feedback_map=feedback_map,
        profile=profile,
        debug=debug,
        imported_di_signal=imported_di_signal,
    )

    built_decision = None
    if out:
            built_decision = build_link_decision(
            phrase_ctx,
            out,
            supporting_intelligence_inputs=supporting_intelligence_inputs,
            imported_di_signal=imported_di_signal,
        )

    if built_decision and not debug:
      save_link_decision(workspace_id, built_decision)

    return {
        "ok": True,
        "results": out,
        "profile": profile,
        "debug": debug,
        "debug_payload": debug_payload,
        "built_decision": built_decision if debug else None,
    }