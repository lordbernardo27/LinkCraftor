
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.server.stores.workspace_session_store import (
    create_session_manifest,
    session_root,
    write_json,
    read_json,
    utc_now_iso,
)


router = APIRouter(prefix="/api/workspace", tags=["workspace-autosave"])


class AutosaveDocument(BaseModel):
    document_id: str = ""
    title: str = ""
    filename: str = ""
    html: str = ""
    text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AutosavePayload(BaseModel):
    workspace_id: str
    session_id: str
    domain: str = ""
    title: str = ""
    active_document_id: str = ""
    documents: List[AutosaveDocument] = Field(default_factory=list)
    imported_urls: List[Dict[str, Any]] = Field(default_factory=list)
    draft_topics: List[Dict[str, Any]] = Field(default_factory=list)
    engine_state: Dict[str, Any] = Field(default_factory=dict)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/autosave")
def autosave_workspace_session(payload: AutosavePayload) -> Dict[str, Any]:
    workspace_id = payload.workspace_id.strip()
    session_id = payload.session_id.strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    create_session_manifest(
        workspace_id=workspace_id,
        session_id=session_id,
        domain=payload.domain,
        title=payload.title or session_id,
    )

    root = session_root(workspace_id, session_id)
    now = utc_now_iso()

    documents_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "active_document_id": payload.active_document_id,
        "documents": [doc.model_dump() for doc in payload.documents],
        "updated_at": now,
    }

    imports_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "domain": payload.domain,
        "imported_urls": payload.imported_urls,
        "import_stats": {
            "total_urls": len(payload.imported_urls),
            "source": "autosave",
        },
        "updated_at": now,
    }

    drafts_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "draft_topics": payload.draft_topics,
        "updated_at": now,
    }

    engine_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "domain": payload.domain,
        "active_document_id": payload.active_document_id,
        "last_engine_run": payload.engine_state.get("last_engine_run"),
        "accepted_links": payload.engine_state.get("accepted_links", []),
        "rejected_links": payload.engine_state.get("rejected_links", []),
        "manual_links": payload.engine_state.get("manual_links", []),
        "raw_state": payload.engine_state,
        "updated_at": now,
    }

    decisions_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "decisions": payload.decisions,
        "updated_at": now,
    }

    write_json(root / "documents" / "documents.json", documents_data)
    write_json(root / "imports" / "imported_sitemaps.json", imports_data)
    write_json(root / "drafts" / "draft_topics.json", drafts_data)
    write_json(root / "engine" / "session_state.json", engine_data)
    write_json(root / "decisions" / "decisions.json", decisions_data)

    manifest_path = root / "manifest.json"
    manifest = read_json(manifest_path) or {}
    if isinstance(manifest, dict):
        manifest["updated_at"] = now
        manifest["domain"] = payload.domain
        manifest["title"] = payload.title or manifest.get("title") or session_id
        manifest["active_document_id"] = payload.active_document_id
        write_json(manifest_path, manifest)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "session_id": session_id,
        "saved_at": now,
        "saved": {
            "documents": len(payload.documents),
            "imported_urls": len(payload.imported_urls),
            "draft_topics": len(payload.draft_topics),
            "decisions": len(payload.decisions),
            "engine_state": True,
        },
        "session_path": str(root),
    }
