
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
    workspace_root,
    ensure_workspace_saved_session_dirs,
    ensure_session_dirs,
    create_session_id,
)


router = APIRouter(prefix="/api/workspace", tags=["workspace-autosave"])


def fix_mojibake_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    text = value

    replacements = {
        "\u00e2\u20ac\u201d": "\u2014",
        "\u00e2\u20ac\u201c": "\u2013",
        "\u00e2\u20ac\u02dc": "\u2018",
        "\u00e2\u20ac\u2122": "\u2019",
        "\u00e2\u20ac\u0153": "\u201c",
        "\u00e2\u20ac\u009d": "\u201d",
        "\u00e2\u20ac\u00a6": "\u2026",
        "\u00c2\u00a0": " ",
        "\u00c2": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def deep_fix_mojibake(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: deep_fix_mojibake(v) for k, v in value.items()}
    if isinstance(value, list):
        return [deep_fix_mojibake(v) for v in value]
    return fix_mojibake_text(value)



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




# LC_CREATE_BLANK_WORKSPACE_ROUTE_3_3_1
@router.post("/create_blank")
def create_blank_workspace(payload: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()
    workspace_name = str(payload.get("workspace_name") or "").strip()
    session_id = str(payload.get("session_id") or "").strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    if not workspace_name:
        workspace_name = workspace_id.replace("ws_", "").replace("_", " ").title()

    if not session_id:
        session_id = create_session_id("blank_session")

    ensure_workspace_saved_session_dirs(workspace_id)
    ensure_session_dirs(workspace_id, session_id)

    root = workspace_root(workspace_id)
    now = utc_now_iso()

    profile = {
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "workspace_mode": "blank",
        "source_type": "blank",
        "created_at": now,
        "updated_at": now,
    }

    write_json(root / "workspace_profile.json", profile)

    create_session_manifest(
        workspace_id=workspace_id,
        session_id=session_id,
        domain="",
        title=workspace_name,
    )

    return {
        "ok": True,
        "workspace": profile,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "session_id": session_id,
    }


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

    clean_documents = deep_fix_mojibake([doc.model_dump() for doc in payload.documents])

    documents_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "active_document_id": payload.active_document_id,
        "documents": clean_documents,
        "updated_at": now,
    }

    imports_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "domain": payload.domain,
        "imported_urls": deep_fix_mojibake(payload.imported_urls),
        "import_stats": {
            "total_urls": len(payload.imported_urls),
            "source": "autosave",
        },
        "updated_at": now,
    }

    drafts_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "draft_topics": deep_fix_mojibake(payload.draft_topics),
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
        "raw_state": deep_fix_mojibake(payload.engine_state),
        "updated_at": now,
    }

    decisions_data = {
        "workspace_id": workspace_id,
        "session_id": session_id,
        "decisions": deep_fix_mojibake(payload.decisions),
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



@router.get("/saved-sessions")
def list_saved_workspace_sessions(workspace_id: str) -> Dict[str, Any]:
    workspace_id = workspace_id.strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    from backend.server.stores.workspace_session_store import saved_sessions_root

    root = saved_sessions_root(workspace_id)
    sessions = []

    if root.exists():
        for session_dir in sorted(root.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue

            manifest = read_json(session_dir / "manifest.json") or {}

            if not isinstance(manifest, dict):
                manifest = {}

            sessions.append({
                "session_id": manifest.get("session_id") or session_dir.name,
                "title": manifest.get("title") or session_dir.name,
                "domain": manifest.get("domain") or "",
                "created_at": manifest.get("created_at") or "",
                "updated_at": manifest.get("updated_at") or "",
                "active_document_id": manifest.get("active_document_id") or "",
                "path": str(session_dir),
            })

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "count": len(sessions),
        "sessions": sessions,
    }


@router.get("/saved-session")
def load_saved_workspace_session(workspace_id: str, session_id: str) -> Dict[str, Any]:
    workspace_id = workspace_id.strip()
    session_id = session_id.strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    root = session_root(workspace_id, session_id)

    if not root.exists():
        raise HTTPException(status_code=404, detail="saved session not found")

    manifest = read_json(root / "manifest.json") or {}
    documents = read_json(root / "documents" / "documents.json") or {}
    imported_sitemaps = read_json(root / "imports" / "imported_sitemaps.json") or {}
    draft_topics = read_json(root / "drafts" / "draft_topics.json") or {}
    engine_state = read_json(root / "engine" / "session_state.json") or {}
    decisions = read_json(root / "decisions" / "decisions.json") or {}

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "session_id": session_id,
        "manifest": manifest,
        "documents": documents,
        "imported_sitemaps": imported_sitemaps,
        "draft_topics": draft_topics,
        "engine_state": engine_state,
        "decisions": decisions,
    }



@router.get("/workspace-folder")
def list_workspace_folder_items() -> Dict[str, Any]:
    from backend.server.stores.workspace_session_store import DATA_DIR

    items = []

    if DATA_DIR.exists():
        for ws_dir in sorted(DATA_DIR.iterdir()):
            if not ws_dir.is_dir():
                continue

            workspace_id = ws_dir.name
            profile_path = ws_dir / "workspace_profile.json"
            profile = read_json(profile_path) or {}

            saved_root = ws_dir / "saved_sessions"
            latest_updated = ""
            latest_session_id = ""

            if saved_root.exists():
                for session_dir in saved_root.iterdir():
                    if not session_dir.is_dir():
                        continue

                    manifest = read_json(session_dir / "manifest.json") or {}
                    if not isinstance(manifest, dict):
                        manifest = {}

                    updated_at = manifest.get("updated_at") or manifest.get("created_at") or ""

                    if updated_at > latest_updated:
                        latest_updated = updated_at
                        latest_session_id = manifest.get("session_id") or session_dir.name

            workspace_name = ""
            if isinstance(profile, dict):
                workspace_name = profile.get("workspace_name") or ""

            if not workspace_name:
                workspace_name = workspace_id.replace("ws_", "").replace("_", " ").title()

            # LC_WORKSPACE_FOLDER_METADATA_3_2_5
            items.append({
                "workspace_id": workspace_id,
                "workspace_name": workspace_name,
                "latest_session_id": latest_session_id,
                "updated_at": latest_updated,
                "workspace_mode": profile.get("workspace_mode") if isinstance(profile, dict) else "",
                "site_url": profile.get("site_url") if isinstance(profile, dict) else "",
                "domain": profile.get("domain") if isinstance(profile, dict) else "",
                "source_type": profile.get("source_type") if isinstance(profile, dict) else "",
                # LC_WORK_FOLDER_CONNECTION_STATUS_6_8_BACKEND
                "connection_status": profile.get("connection_status") if isinstance(profile, dict) else "",
            })

    return {
        "ok": True,
        "count": len(items),
        "workspaces": items,
    }


@router.post("/workspace-folder/name")
def save_workspace_folder_name(payload: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()
    workspace_name = str(payload.get("workspace_name") or "").strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    if not workspace_name:
        raise HTTPException(status_code=400, detail="workspace_name is required")

    from backend.server.stores.workspace_session_store import workspace_root

    root = workspace_root(workspace_id)
    root.mkdir(parents=True, exist_ok=True)

    profile_path = root / "workspace_profile.json"
    existing = read_json(profile_path) or {}
    if not isinstance(existing, dict):
        existing = {}

    # LC_WORKSPACE_PROFILE_STANDARD_STRUCTURE_4_4
    now = utc_now_iso()

    data = dict(existing)
    data["workspace_id"] = workspace_id
    data["workspace_name"] = workspace_name
    data["workspace_mode"] = str(payload.get("workspace_mode") or data.get("workspace_mode") or "").strip()
    data["domain"] = str(payload.get("domain") or data.get("domain") or "").strip()
    data["site_url"] = str(payload.get("site_url") or data.get("site_url") or "").strip()
    data["source_type"] = str(payload.get("source_type") or data.get("source_type") or "").strip()
    data["created_at"] = str(data.get("created_at") or now)
    data["updated_at"] = now

    # Keep legacy sitemap_url only if an old caller still sends it.
    if payload.get("sitemap_url") is not None:
        data["sitemap_url"] = str(payload.get("sitemap_url") or "").strip()

    write_json(profile_path, data)

    return {
        "ok": True,
        "workspace": data,
    }





# LC_DISCONNECT_DOMAIN_ROUTE_6_4
@router.post("/disconnect_domain")
def disconnect_workspace_domain(payload: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(payload.get("workspace_id") or "").strip()

    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    from backend.server.stores.workspace_session_store import workspace_root

    root = workspace_root(workspace_id)
    root.mkdir(parents=True, exist_ok=True)

    profile_path = root / "workspace_profile.json"
    profile = read_json(profile_path) or {}

    if not isinstance(profile, dict):
        profile = {}

    old_domain = str(profile.get("domain") or "").strip()

    profile["workspace_id"] = workspace_id
    profile["domain"] = ""
    profile["connection_status"] = "disconnected"
    profile["disconnected_at"] = utc_now_iso()
    profile["updated_at"] = utc_now_iso()

    if "site_url" not in profile:
        profile["site_url"] = ""

    if "workspace_mode" not in profile:
        profile["workspace_mode"] = "blank"

    if "source_type" not in profile:
        profile["source_type"] = profile.get("workspace_mode") or "blank"

    write_json(profile_path, profile)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "old_domain": old_domain,
        "connection_status": "disconnected",
        "workspace": profile,
    }


@router.delete("/workspace-folder")
def delete_workspace_folder_item(workspace_id: str) -> Dict[str, Any]:
    if not workspace_id:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    from backend.server.stores.workspace_session_store import workspace_root
    import shutil

    root = workspace_root(workspace_id)

    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=404, detail="workspace not found")

    shutil.rmtree(root)

    return {
        "ok": True,
        "deleted_workspace_id": workspace_id,
    }
