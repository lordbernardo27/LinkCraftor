# backend/server/routes/engine_scoring.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .engine_decisions import get_aggregated_link_feedback
from ..engine.scoring import score_candidates_for_phrase

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


@router.post("/score")
def score_endpoint(payload: ScoreRequest):
    phrase_ctx = payload.phraseCtx.model_dump()
    candidates = [c.model_dump() for c in payload.candidates]

    # ---- Decision Intelligence: load feedback memory for this workspace/doc ----
    workspace_id = phrase_ctx.get("workspaceId") or "ws_demo"
    doc_id = phrase_ctx.get("docId")

    feedback_map = get_aggregated_link_feedback(workspaceId=workspace_id, docId=doc_id)

    out = score_candidates_for_phrase(
        phrase_ctx,
        candidates,
        feedback_map=feedback_map
    )

    return {"ok": True, "results": out}
