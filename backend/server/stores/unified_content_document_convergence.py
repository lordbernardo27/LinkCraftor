from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_ROOT = Path("backend/server/data")
STORE_DIR = DATA_ROOT / "unified_content_documents"


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in str(workspace_id or "default"))


def unified_document_id_v1(source_identifier: str, source_type: str = "") -> str:
    base = f"{source_type}::{source_identifier}"
    digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]
    return f"ucd_{digest}"


def _store_path_v1(workspace_id: str) -> Path:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return STORE_DIR / f"unified_content_documents_{_safe_workspace_id_v1(workspace_id)}.json"


def build_unified_content_document_v1(
    *,
    workspace_id: str,
    source_identifier: str,
    source_type: str,
    title: str = "",
    primary_content: str = "",
    headings: List[Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
    page_type: str = "article",
) -> Dict[str, Any]:
    content = str(primary_content or "").strip()
    now = datetime.now(timezone.utc).isoformat()
    document_id = unified_document_id_v1(source_identifier, source_type)

    return {
        "document_id": document_id,
        "schema_version": "unified_content_document_v1",
        "workspace_id": workspace_id,
        "source_identifier": source_identifier,
        "source_type": source_type,
        "title": title,
        "primary_content": content,
        "headings": headings or [],
        "metadata": {
            **(metadata or {}),
            "word_count": len(content.split()),
            "content_length": len(content),
            "heading_count": len(headings or []),
        },
        "quality": quality or {},
        "semantic_features": semantic_features or {},
        "page_type": page_type,
        "created_or_updated_at_utc": now,
    }


def load_unified_content_document_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _store_path_v1(workspace_id)

    if not path.exists():
        return {
            "version": "unified_content_document_store_v1",
            "workspace_id": workspace_id,
            "documents": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        }

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "version": "unified_content_document_store_v1",
            "workspace_id": workspace_id,
            "documents": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "recovered_from_error": True,
        }


def save_unified_content_document_store_v1(
    workspace_id: str,
    store: Dict[str, Any],
) -> Path:
    path = _store_path_v1(workspace_id)
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def upsert_unified_content_document_v1(
    document: Dict[str, Any],
) -> Dict[str, Any]:
    workspace_id = document.get("workspace_id", "default")
    document_id = document.get("document_id")

    if not document_id:
        raise ValueError("Unified content document missing document_id.")

    store = load_unified_content_document_store_v1(workspace_id)
    store.setdefault("documents", {})
    store["documents"][document_id] = document

    save_unified_content_document_store_v1(workspace_id, store)

    return document


def get_unified_content_document_v1(
    *,
    workspace_id: str,
    document_id: str | None = None,
    source_identifier: str | None = None,
    source_type: str | None = None,
) -> Dict[str, Any] | None:
    store = load_unified_content_document_store_v1(workspace_id)

    if document_id:
        return store.get("documents", {}).get(document_id)

    if source_identifier and source_type:
        return store.get("documents", {}).get(
            unified_document_id_v1(source_identifier, source_type)
        )

    return None


def from_crawled_web_page_v1(
    *,
    workspace_id: str,
    url: str,
    title: str = "",
    primary_content: str = "",
    article_body: str = "",
    headings: List[Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_unified_content_document_v1(
        workspace_id=workspace_id,
        source_identifier=url,
        source_type="crawled_web_page",
        title=title,
        primary_content=primary_content or article_body,
        headings=headings or [],
        metadata=metadata or {},
        quality=quality or {},
        semantic_features=semantic_features or {},
        page_type="article",
    )


def from_uploaded_document_v1(
    *,
    workspace_id: str,
    source_identifier: str,
    source_type: str,
    title: str = "",
    primary_content: str = "",
    headings: List[Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_unified_content_document_v1(
        workspace_id=workspace_id,
        source_identifier=source_identifier,
        source_type=source_type,
        title=title,
        primary_content=primary_content,
        headings=headings or [],
        metadata=metadata or {},
        quality=quality or {},
        semantic_features=semantic_features or {},
        page_type="article",
    )


def validate_unified_content_document_v1(document: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "document_id",
        "schema_version",
        "workspace_id",
        "source_identifier",
        "source_type",
        "title",
        "primary_content",
        "headings",
        "metadata",
        "quality",
        "semantic_features",
        "page_type",
    ]

    missing = [k for k in required if k not in document]

    return {
        "valid": not missing,
        "missing": missing,
        "document_id": document.get("document_id"),
        "source_type": document.get("source_type"),
        "word_count": len(str(document.get("primary_content", "")).split()),
        "content_length": len(str(document.get("primary_content", ""))),
    }

SUPPORTED_UPLOAD_SOURCE_TYPES_V1 = {
    "docx": "docx_upload",
    "pdf": "pdf_upload",
    "txt": "txt_upload",
    "html": "html_upload",
    "htm": "html_upload",
    "md": "markdown_upload",
    "markdown": "markdown_upload",
}


def source_type_for_upload_extension_v1(extension: str) -> str:
    key = str(extension or "").strip().lower().lstrip(".")
    return SUPPORTED_UPLOAD_SOURCE_TYPES_V1.get(key, "uploaded_document")


def from_existing_upload_format_v1(
    *,
    workspace_id: str,
    source_identifier: str,
    extension: str,
    title: str = "",
    primary_content: str = "",
    headings: List[Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_unified_content_document_v1(
        workspace_id=workspace_id,
        source_identifier=source_identifier,
        source_type=source_type_for_upload_extension_v1(extension),
        title=title,
        primary_content=primary_content,
        headings=headings or [],
        metadata={
            **(metadata or {}),
            "extension": str(extension or "").strip().lower().lstrip("."),
        },
        quality=quality or {},
        semantic_features=semantic_features or {},
        page_type="article",
    )
