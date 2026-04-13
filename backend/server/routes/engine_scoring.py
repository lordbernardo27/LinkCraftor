# backend/server/routes/engine_scoring.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .engine_decisions import get_aggregated_link_feedback
from ..engine.scoring import score_candidates_for_phrase
from ..engine.profiles import PROFILES, normalize_profile_id
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

    # Debug mode: keep extra payload, but still run scoring.
    debug_payload = None
    if debug:
        debug_payload = {
            "phrase_ctx": phrase_ctx,
            "candidate_count": len(candidates),
            "candidates_sample": candidates[:3],
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
    )

    return {
        "ok": True,
        "results": out,
        "profile": profile,
        "debug": debug,
        "debug_payload": debug_payload,
    }