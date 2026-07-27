from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


UUCD_SCHEMA_VERSION = "universal_unified_content_document_v1"
UUCD_PIPELINE_VERSION = "verification_6e_uucd_convergence_v1"

UUCD_OUTPUT_DIR = Path("backend/server/data/universal_unified_content_documents")


@dataclass
class UniversalUnifiedContentDocument:
    schema_version: str
    pipeline_version: str

    workspace_id: str
    document_id: str

    source_type: str
    source_format: str

    source_identity: Dict[str, Any]

    title: str
    h1: str
    headings: List[str]

    content_body: str
    structure: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value: str | None, fallback: str = "unknown") -> str:
    raw = str(value or fallback).strip() or fallback
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", raw)[:140]


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def build_uucd_from_uploaded_document_unified_content_v1(
    uduc: Dict[str, Any],
) -> UniversalUnifiedContentDocument:
    """
    Convert Uploaded Document Unified Content into UUCD.

    Boundary:
    - Does not extract.
    - Does not clean.
    - Does not rewrite content_body.
    - Does not perform phrase extraction.
    - Does not perform semantic analysis.
    """

    workspace_id = _safe_id(uduc.get("workspace_id"), "default")
    document_id = _safe_id(uduc.get("document_id"), "unknown_document")

    content_body = str(uduc.get("content_body") or "")

    source_identity = {
        "input_type": "uploaded_document_unified_content",
        "original_filename": uduc.get("original_filename") or "",
        "stored_filename": uduc.get("stored_filename") or "",
        "stored_path": uduc.get("stored_path") or "",
    }

    metadata = {
        "input_schema_version": uduc.get("schema_version"),
        "input_pipeline_version": uduc.get("pipeline_version"),
        "source_metadata": uduc.get("metadata") or {},
        "extraction_status": uduc.get("extraction_status") or "",
        "extraction_confidence": uduc.get("extraction_confidence") or 0.0,
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "modifies_content_body": False,
        },
    }

    return UniversalUnifiedContentDocument(
        schema_version=UUCD_SCHEMA_VERSION,
        pipeline_version=UUCD_PIPELINE_VERSION,
        workspace_id=workspace_id,
        document_id=document_id,
        source_type="uploaded_document",
        source_format=str(uduc.get("source_format") or ""),
        source_identity=source_identity,
        title=str(uduc.get("title") or ""),
        h1=str(uduc.get("h1") or ""),
        headings=_as_list(uduc.get("headings")),
        content_body=content_body,
        structure=uduc.get("structure") if isinstance(uduc.get("structure"), dict) else {},
        metadata=metadata,
        created_at=_now_iso(),
    )


def build_uucd_from_website_unified_content_v1(
    wuc: Dict[str, Any],
) -> UniversalUnifiedContentDocument:
    """
    Convert Website Unified Content into UUCD.

    This function is intentionally tolerant because existing website unified content
    may use body_text, article_text, or content_body depending on version.
    """

    workspace_id = _safe_id(wuc.get("workspace_id"), "default")
    document_id = _safe_id(
        wuc.get("document_id") or wuc.get("content_id") or wuc.get("page_id") or wuc.get("url_hash"),
        "unknown_website_document",
    )

    content_body = str(
        wuc.get("content_body") or wuc.get("article_body") or wuc.get("primary_content") or wuc.get("body_text") or wuc.get("article_text") or ""
    )

    source_identity = {
        "input_type": "website_unified_content",
        "url": wuc.get("url") or wuc.get("canonical_url") or "",
        "canonical_url": wuc.get("canonical_url") or "",
        "source_url": wuc.get("source_url") or "",
    }

    metadata = {
        "input_schema_version": wuc.get("schema_version"),
        "input_pipeline_version": wuc.get("pipeline_version"),
        "source_metadata": wuc.get("metadata") or {},
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "modifies_content_body": False,
        },
    }

    return UniversalUnifiedContentDocument(
        schema_version=UUCD_SCHEMA_VERSION,
        pipeline_version=UUCD_PIPELINE_VERSION,
        workspace_id=workspace_id,
        document_id=document_id,
        source_type="website",
        source_format=str(wuc.get("source_format") or "html"),
        source_identity=source_identity,
        title=str(wuc.get("title") or ""),
        h1=str(wuc.get("h1") or ""),
        headings=_as_list(wuc.get("headings") or wuc.get("h2") or []),
        content_body=content_body,
        structure=wuc.get("structure") if isinstance(wuc.get("structure"), dict) else {},
        metadata=metadata,
        created_at=_now_iso(),
    )


def serialize_uucd(uucd: UniversalUnifiedContentDocument) -> Dict[str, Any]:
    return asdict(uucd)


def uucd_output_path(workspace_id: str, document_id: str) -> Path:
    ws = _safe_id(workspace_id, "default")
    doc = _safe_id(document_id, "unknown_document")
    return UUCD_OUTPUT_DIR / ws / f"{doc}.json"


def write_uucd(uucd: UniversalUnifiedContentDocument) -> Path:
    path = uucd_output_path(uucd.workspace_id, uucd.document_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(serialize_uucd(uucd), indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)

    return path


def read_uucd(workspace_id: str, document_id: str) -> Dict[str, Any]:
    path = uucd_output_path(workspace_id, document_id)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def build_and_write_uucd_from_uduc_v1(uduc: Dict[str, Any]) -> Dict[str, Any]:
    uucd = build_uucd_from_uploaded_document_unified_content_v1(uduc)
    path = write_uucd(uucd)

    return {
        "ok": True,
        "uucd_path": str(path),
        "uucd": serialize_uucd(uucd),
    }


def build_and_write_uucd_from_wuc_v1(wuc: Dict[str, Any]) -> Dict[str, Any]:
    uucd = build_uucd_from_website_unified_content_v1(wuc)
    path = write_uucd(uucd)

    return {
        "ok": True,
        "uucd_path": str(path),
        "uucd": serialize_uucd(uucd),
    }


# Backward-compatible aliases for older callers.
def from_uploaded_document_v1(uploaded_document: Dict[str, Any]) -> Dict[str, Any]:
    return serialize_uucd(build_uucd_from_uploaded_document_unified_content_v1(uploaded_document))


def from_existing_upload_format_v1(uploaded_document: Dict[str, Any]) -> Dict[str, Any]:
    return from_uploaded_document_v1(uploaded_document)


def explain_uucd_convergence_v1() -> Dict[str, Any]:
    return {
        "stage": "Verification 6E",
        "component": "Universal Unified Content Document",
        "schema_version": UUCD_SCHEMA_VERSION,
        "pipeline_version": UUCD_PIPELINE_VERSION,
        "canonical_content_field": "content_body",
        "accepted_inputs": [
            "Website Unified Content",
            "Uploaded Document Unified Content",
        ],
        "output": "UniversalUnifiedContentDocument",
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "modifies_content_body": False,
        },
        "next_stage": "Phase 4.6.1 Semantic Article Reader",
    }



def load_universal_unified_content_document_store_v1(workspace_id: str) -> Dict[str, Any]:
    ws = _safe_id(workspace_id, "default")
    root = UUCD_OUTPUT_DIR / ws

    documents = {}

    if root.exists():
        for path in root.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                document_id = data.get("document_id") or path.stem
                documents[document_id] = data
            except Exception:
                continue

    return {
        "version": UUCD_SCHEMA_VERSION,
        "workspace_id": ws,
        "documents": documents,
        "document_count": len(documents),
    }
