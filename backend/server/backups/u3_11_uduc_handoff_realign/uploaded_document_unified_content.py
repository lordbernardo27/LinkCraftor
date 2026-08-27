from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v1"
UDUC_PIPELINE_VERSION = "verification_6d_uduc_v1_1"

# FIX: anchored to the package (backend/server), matching files.py, instead
# of a CWD-relative "backend/server/data/..." string. Previously artifacts
# landed under whatever directory the server happened to be launched from,
# and _read_upload_index_hit silently found nothing.
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/server
UDUC_OUTPUT_DIR = BASE_DIR / "data" / "uploaded_document_unified_content"


@dataclass
class UploadedDocumentUnifiedContent:
    schema_version: str
    pipeline_version: str

    workspace_id: str
    document_id: str

    source_type: str
    source_format: str

    original_filename: str
    stored_filename: str
    stored_path: str

    title: str
    h1: str
    headings: List[str]

    content_body: str

    structure: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    extraction_status: str = ""
    extraction_confidence: float = 0.0

    created_at: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_workspace_id(workspace_id: str | None) -> str:
    raw = str(workspace_id or "default").strip()
    if not raw:
        raw = "default"
    raw = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw)
    return raw[:100]


def _safe_document_id(document_id: str | None, fallback: str = "") -> str:
    raw = str(document_id or fallback or "").strip()
    if not raw:
        raw = "unknown_document"
    raw = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw)
    return raw[:120]


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _read_upload_index_hit(workspace_id: str, document_id: str) -> Dict[str, Any]:
    candidates = [
        BASE_DIR / "data" / "docs" / workspace_id / "index.json",
        BASE_DIR / "data" / "uploads" / workspace_id / "index.json",
    ]

    for fp in candidates:
        if not fp.exists():
            continue

        try:
            raw = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue

        rows = raw if isinstance(raw, list) else raw.get("items", []) if isinstance(raw, dict) else []

        for row in rows:
            if isinstance(row, dict) and str(row.get("doc_id") or row.get("document_id") or "").strip() == document_id:
                return row

    # FIX: one debug breadcrumb instead of total silence — the enrichment
    # path (h1 / stored_name / bytes) being dead in production previously
    # had zero signal.
    print(f"[UDUC_INDEX_MISS] workspace={workspace_id} doc={document_id}")
    return {}


def _paragraphs_from_content_body(content_body: str) -> List[Dict[str, Any]]:
    """Split content_body into paragraphs on blank lines.

    Contract with upload_document_extractor: extracted text preserves
    paragraph boundaries as blank lines ("\\n\\n").

    Each paragraph now also carries start_char/end_char offsets into
    content_body so downstream consumers can locate paragraphs without
    re-searching (and so future schema versions can drop the duplicated
    text in favor of offsets).
    """
    raw = str(content_body or "")
    paragraphs: List[Dict[str, Any]] = []

    idx = 0
    for i, m in enumerate(re.finditer(r"[^\n]+(?:\n(?!\n)[^\n]*)*", raw), start=1):
        block = m.group(0).strip()
        if not block:
            continue
        idx += 1
        paragraphs.append(
            {
                "index": idx,
                "text": block,
                "start_char": m.start(),
                "end_char": m.end(),
                "char_count": len(block),
                "word_count": len([w for w in re.split(r"\s+", block) if w.strip()]),
            }
        )

    if not paragraphs and raw.strip():
        block = raw.strip()
        paragraphs = [{
            "index": 1,
            "text": block,
            "start_char": 0,
            "end_char": len(raw),
            "char_count": len(block),
            "word_count": len([w for w in re.split(r"\s+", block) if w.strip()]),
        }]

    return paragraphs


def _build_heading_map(headings: List[str], content_body: str) -> List[Dict[str, Any]]:
    body = str(content_body or "")
    out: List[Dict[str, Any]] = []

    search_from = 0
    for i, heading in enumerate(headings, start=1):
        h = str(heading or "").strip()
        if not h:
            continue

        # Search forward from the previous heading so repeated headings map
        # to successive positions instead of all pointing at the first hit.
        char_position = body.find(h, search_from)
        if char_position < 0:
            char_position = body.find(h)

        if char_position >= 0:
            search_from = char_position + len(h)

        out.append(
            {
                "index": i,
                "heading": h,
                "level": None,
                "char_position": char_position if char_position >= 0 else None,
            }
        )

    return out


def _build_uduc_structure(content_body: str, headings: List[str]) -> Dict[str, Any]:
    paragraphs = _paragraphs_from_content_body(content_body)
    heading_map = _build_heading_map(headings, content_body)

    # FIX: document_order is now actual reading order — headings and
    # paragraphs interleaved by character position — instead of "all
    # headings, then all paragraphs", which contradicted the field's name.
    ordered: List[tuple[int, Dict[str, Any]]] = []

    for h in heading_map:
        pos = h.get("char_position")
        ordered.append(
            (
                pos if isinstance(pos, int) else -1,
                {
                    "type": "heading",
                    "index": h.get("index"),
                    "text": h.get("heading"),
                    "char_position": h.get("char_position"),
                },
            )
        )

    for p in paragraphs:
        ordered.append(
            (
                int(p.get("start_char") or 0),
                {
                    "type": "paragraph",
                    "index": p.get("index"),
                    "text_preview": str(p.get("text") or "")[:160],
                    "start_char": p.get("start_char"),
                    "word_count": p.get("word_count"),
                },
            )
        )

    # Headings sort just before the paragraph that contains them (same
    # position): stable sort with heading entries added first achieves that.
    ordered.sort(key=lambda t: t[0])
    document_order = [item for _, item in ordered]

    word_count = len([w for w in re.split(r"\s+", str(content_body or "")) if w.strip()])

    return {
        "paragraphs": paragraphs,
        "heading_map": heading_map,
        "section_count": len(heading_map),
        "paragraph_count": len(paragraphs),
        "document_order": document_order,

        "first_heading": headings[0] if headings else "",
        "last_heading": headings[-1] if headings else "",
        "first_paragraph": paragraphs[0]["text"] if paragraphs else "",
        "last_paragraph": paragraphs[-1]["text"] if paragraphs else "",
        "estimated_word_count": word_count,
        "estimated_character_count": len(str(content_body or "")),

        "structure_version": "uduc_structure_v1_2",
        "boundary": {
            "preserves_content_body": True,
            "modifies_content_body": False,
            "performs_cleaning": False,
            "performs_semantic_analysis": False,
        },
    }


def build_uduc_from_upload_extraction_result(
    *,
    extraction_result: Any,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> UploadedDocumentUnifiedContent:
    """
    Convert UploadExtractionResult into Uploaded Document Unified Content.

    Boundary rules:
    - Does not extract documents.
    - Does not clean or rewrite content_body.
    - Does not perform phrase extraction.
    - Does not perform semantic analysis.
    - Does not build UUCD.
    """

    ws = _safe_workspace_id(workspace_id)

    if isinstance(extraction_result, dict):
        er = extraction_result
    else:
        er = {
            "source_path": getattr(extraction_result, "source_path", ""),
            "source_type": getattr(extraction_result, "source_type", ""),
            "title": getattr(extraction_result, "title", ""),
            "text": getattr(extraction_result, "text", ""),
            "headings": getattr(extraction_result, "headings", []),
            "metadata": getattr(extraction_result, "metadata", {}),
            "extraction_status": getattr(extraction_result, "extraction_status", ""),
            "extraction_confidence": getattr(extraction_result, "extraction_confidence", 0.0),
            "created_at": getattr(extraction_result, "created_at", ""),
        }

    meta = er.get("metadata") if isinstance(er.get("metadata"), dict) else {}
    src_meta = dict(source_metadata or {})

    inferred_document_id = (
        document_id
        or src_meta.get("doc_id")
        or src_meta.get("document_id")
        or meta.get("doc_id")
        or meta.get("document_id")
        or ""
    )

    doc_id = _safe_document_id(inferred_document_id)

    index_hit = _read_upload_index_hit(ws, doc_id) if doc_id != "unknown_document" else {}

    source_path = str(er.get("source_path") or stored_path or index_hit.get("stored_path") or "")
    source_type = str(er.get("source_type") or meta.get("source_type") or "").strip()
    source_format = source_type or str(meta.get("extension") or "").replace(".", "").strip() or "uploaded_document"

    original_name = (
        original_filename
        or src_meta.get("original_filename")
        or src_meta.get("filename")
        or meta.get("filename")
        or index_hit.get("filename")
        or Path(source_path).name
        or ""
    )

    stored_name = (
        stored_filename
        or src_meta.get("stored_filename")
        or src_meta.get("stored_name")
        or meta.get("stored_filename")
        or meta.get("stored_name")
        or index_hit.get("stored_name")
        or Path(source_path).name
        or ""
    )

    final_stored_path = (
        stored_path
        or src_meta.get("stored_path")
        or meta.get("stored_path")
        or index_hit.get("stored_path")
        or source_path
        or ""
    )

    title = str(er.get("title") or meta.get("title") or index_hit.get("h1") or "").strip()
    headings = _as_list(er.get("headings"))
    h1 = str(meta.get("h1") or index_hit.get("h1") or (headings[0] if headings else title) or "").strip()

    content_body = str(er.get("content_body") or er.get("text") or "").strip()
    structure = _build_uduc_structure(content_body, headings)

    extension = str(meta.get("extension") or Path(original_name).suffix.lower() or "").strip()

    # FIX: file_size falls back to None (was ""), avoiding mixed int/str typing.
    file_size = src_meta.get("file_size") or src_meta.get("bytes") or index_hit.get("bytes") or None

    merged_metadata: Dict[str, Any] = {
        "extension": extension,
        "file_size": file_size,
        "extraction_method": meta.get("method") or meta.get("extractor") or "",
        "extraction_timestamp": er.get("created_at") or _now_iso(),
        "paragraph_count": meta.get("paragraph_count"),
        "heading_count": meta.get("heading_count") if meta.get("heading_count") is not None else len(headings),
        "line_count": meta.get("line_count"),
        "source_metadata": {
            **src_meta,
            **meta,
        },
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "creates_uucd": False,
        },
    }

    return UploadedDocumentUnifiedContent(
        schema_version=UDUC_SCHEMA_VERSION,
        pipeline_version=UDUC_PIPELINE_VERSION,
        workspace_id=ws,
        document_id=doc_id,
        source_type="uploaded_document",
        source_format=source_format,
        original_filename=str(original_name or ""),
        stored_filename=str(stored_name or ""),
        stored_path=str(final_stored_path or ""),
        title=title,
        h1=h1,
        headings=headings,
        content_body=content_body,
        structure=structure,
        metadata=merged_metadata,
        extraction_status=str(er.get("extraction_status") or ""),
        extraction_confidence=_as_float(er.get("extraction_confidence"), 0.0),
        created_at=_now_iso(),
    )


def serialize_uduc(uduc: UploadedDocumentUnifiedContent) -> Dict[str, Any]:
    return asdict(uduc)


def uduc_output_path(workspace_id: str, document_id: str) -> Path:
    ws = _safe_workspace_id(workspace_id)
    doc = _safe_document_id(document_id)
    return UDUC_OUTPUT_DIR / ws / f"{doc}.json"


def write_uduc(uduc: UploadedDocumentUnifiedContent) -> Path:
    path = uduc_output_path(uduc.workspace_id, uduc.document_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(serialize_uduc(uduc), ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

    return path


def read_uduc(workspace_id: str, document_id: str) -> Dict[str, Any]:
    path = uduc_output_path(workspace_id, document_id)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def build_and_write_uduc_from_extraction_result(
    *,
    extraction_result: Any,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    uduc = build_uduc_from_upload_extraction_result(
        extraction_result=extraction_result,
        workspace_id=workspace_id,
        document_id=document_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        stored_path=stored_path,
        source_metadata=source_metadata,
    )

    path = write_uduc(uduc)

    return {
        "ok": True,
        "workspace_id": uduc.workspace_id,
        "document_id": uduc.document_id,
        "uduc_path": str(path),
        "uduc": serialize_uduc(uduc),
    }


def explain_uploaded_document_unified_content_v1() -> Dict[str, Any]:
    return {
        "stage": "Verification 6D",
        "component": "Uploaded Document Unified Content",
        "schema_version": UDUC_SCHEMA_VERSION,
        "pipeline_version": UDUC_PIPELINE_VERSION,
        "canonical_content_field": "content_body",
        "input": "UploadExtractionResult",
        "output": "UploadedDocumentUnifiedContent",
        "contract": {
            "paragraph_boundaries": "blank lines in content_body (from extractor)",
            "paragraph_offsets": "start_char/end_char into content_body",
            "document_order": "true reading order (headings + paragraphs interleaved)",
            "paths": "anchored to backend/server, not process CWD",
        },
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "creates_uucd": False,
        },
    }