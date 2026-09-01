from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)
from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
    normalize_uploaded_document_v1,
)


UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v2"
UDUC_PIPELINE_VERSION = "uploaded_document_uduc_pipeline_v2"

# FIX: anchored to the package (backend/server), matching files.py, instead
# of a CWD-relative "backend/server/data/..." string. Previously artifacts
# landed under whatever directory the server happened to be launched from,
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
    extraction_created_at: str = ""

    normalization_status: str = ""
    normalization_version: str = ""
    normalized_at: str = ""

    created_at: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_workspace_id(workspace_id: str | None) -> str:
    if workspace_id is None:
        raise ValueError(
            "workspace_id is required."
        )

    raw = str(workspace_id).strip()

    if not raw:
        raise ValueError(
            "workspace_id must be non-blank."
        )

    raw = re.sub(
        r"[^a-zA-Z0-9_\-]",
        "_",
        raw,
    )

    if not raw:
        raise ValueError(
            "workspace_id is invalid after sanitization."
        )

    return raw[:100]


def _safe_document_id(document_id: str | None, fallback: str = "") -> str:
    raw = str(document_id or fallback or "").strip()
    if not raw:
        raw = "unknown_document"
    raw = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw)
    return raw[:120]


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


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
        block = m.group(0)
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

    if not paragraphs and raw:
        block = raw
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
        h = heading
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
    ordered: List[
        tuple[int, int, Dict[str, Any]]
    ] = []

    for h in heading_map:
        pos = h.get("char_position")
        ordered.append(
            (
                0 if isinstance(pos, int) else 1,
                pos if isinstance(pos, int) else 0,
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
                0,
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

    # Positioned entries sort by their real content position.
    # Stable ordering keeps headings before paragraphs at equal positions
    # because heading entries are added first.
    #
    # Unmatched headings retain char_position=None and sort after all
    # positioned content rather than receiving a synthetic document position.
    ordered.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    document_order = [
        item
        for _, _, item in ordered
    ]

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


def _coerce_upload_extraction_result(
    extraction_result: Any,
) -> UploadExtractionResult:
    """
    Compatibility-only adapter for legacy callers.

    The canonical U8 input is NormalizedUploadedDocumentContent.
    Any legacy extraction-result input must pass through U7 before
    UDUC construction.
    """

    if isinstance(
        extraction_result,
        UploadExtractionResult,
    ):
        return extraction_result

    if isinstance(
        extraction_result,
        dict,
    ):
        data = extraction_result
    else:
        data = {
            "source_path": getattr(
                extraction_result,
                "source_path",
                "",
            ),
            "source_type": getattr(
                extraction_result,
                "source_type",
                "",
            ),
            "title": getattr(
                extraction_result,
                "title",
                "",
            ),
            "text": getattr(
                extraction_result,
                "text",
                "",
            ),
            "headings": getattr(
                extraction_result,
                "headings",
                [],
            ),
            "metadata": getattr(
                extraction_result,
                "metadata",
                {},
            ),
            "extraction_status": getattr(
                extraction_result,
                "extraction_status",
                "",
            ),
            "extraction_confidence": getattr(
                extraction_result,
                "extraction_confidence",
                0.0,
            ),
            "created_at": getattr(
                extraction_result,
                "created_at",
                "",
            ),
        }

    title = data.get("title")
    text = data.get("text")
    headings = data.get("headings")
    metadata = data.get("metadata")

    if not isinstance(title, str):
        raise TypeError(
            "UploadExtractionResult.title must be a string."
        )

    if not isinstance(text, str):
        raise TypeError(
            "UploadExtractionResult.text must be a string."
        )

    if not isinstance(headings, list):
        raise TypeError(
            "UploadExtractionResult.headings must be a list."
        )

    if not all(
        isinstance(value, str)
        for value in headings
    ):
        raise TypeError(
            "UploadExtractionResult.headings must contain only strings."
        )

    if not isinstance(metadata, dict):
        metadata = {}

    return UploadExtractionResult(
        source_path=str(
            data.get("source_path") or ""
        ),
        source_type=str(
            data.get("source_type") or ""
        ),
        title=title,
        text=text,
        headings=list(headings),
        metadata=dict(metadata),
        extraction_status=str(
            data.get("extraction_status")
            or ""
        ),
        extraction_confidence=_as_float(
            data.get("extraction_confidence"),
            0.0,
        ),
        created_at=str(
            data.get("created_at")
            or ""
        ),
    )


def build_uduc_from_normalized_content(
    *,
    normalized_content: NormalizedUploadedDocumentContent,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> UploadedDocumentUnifiedContent:
    """
    Build canonical UDUC v2 from the canonical U7 output.

    Canonical boundary:
        NormalizedUploadedDocumentContent
        -> UDUC structural/schema construction
        -> UploadedDocumentUnifiedContent

    U8 derives structure but does not re-normalize or rewrite the
    canonical U7 title, text, or headings.
    """

    if not isinstance(
        normalized_content,
        NormalizedUploadedDocumentContent,
    ):
        raise TypeError(
            "Expected NormalizedUploadedDocumentContent."
        )

    if (
        normalized_content.normalization_status
        != "success"
    ):
        raise ValueError(
            "UDUC requires successfully normalized content."
        )

    ws = _safe_workspace_id(
        workspace_id
    )

    meta = (
        dict(normalized_content.metadata)
        if isinstance(
            normalized_content.metadata,
            dict,
        )
        else {}
    )

    src_meta = dict(
        source_metadata or {}
    )

    inferred_document_id = (
        document_id
        or src_meta.get("doc_id")
        or src_meta.get("document_id")
        or meta.get("doc_id")
        or meta.get("document_id")
        or ""
    )

    doc_id = _safe_document_id(
        inferred_document_id
    )

    source_path = str(
        normalized_content.source_path
        or stored_path
        or src_meta.get("stored_path")
        or ""
    )

    normalized_source_type = (
        normalized_content.source_type
    )

    source_format = (
        normalized_source_type
        or str(
            meta.get("extension")
            or ""
        ).replace(
            ".",
            "",
        ).strip()
        or "uploaded_document"
    )

    original_name = (
        original_filename
        or src_meta.get(
            "original_filename"
        )
        or src_meta.get("filename")
        or meta.get("filename")
        or Path(source_path).name
        or ""
    )

    stored_name = (
        stored_filename
        or src_meta.get(
            "stored_filename"
        )
        or src_meta.get("stored_name")
        or meta.get(
            "stored_filename"
        )
        or meta.get("stored_name")
        or Path(source_path).name
        or ""
    )

    final_stored_path = (
        stored_path
        or src_meta.get("stored_path")
        or meta.get("stored_path")
        or source_path
        or ""
    )

    # Canonical U7 content authority.
    # Do not strip, clean, normalize, or infer these values.
    title = normalized_content.title
    headings = list(
        normalized_content.headings
    )
    content_body = (
        normalized_content.text
    )

    # Existing H1 compatibility behavior remains temporarily.
    # U8.16 owns the final H1 contract decision.
    h1 = str(
        meta.get("h1")
        or src_meta.get("h1")
        or (
            headings[0]
            if headings
            else title
        )
        or ""
    ).strip()

    structure = _build_uduc_structure(
        content_body,
        headings,
    )

    extension = str(
        meta.get("extension")
        or Path(
            str(original_name or "")
        ).suffix.lower()
        or ""
    ).strip()

    file_size = (
        src_meta.get("file_size")
        or src_meta.get("bytes")
        or None
    )

    normalization_metadata = (
        dict(
            meta.get("normalization")
        )
        if isinstance(
            meta.get("normalization"),
            dict,
        )
        else {}
    )

    merged_metadata: Dict[str, Any] = {
        "extension": extension,
        "file_size": file_size,
        "extraction_method": (
            meta.get("method")
            or meta.get("extractor")
            or ""
        ),
        "extraction_timestamp": (
            normalized_content.extraction_created_at
        ),
        "paragraph_count": meta.get(
            "paragraph_count"
        ),
        "heading_count": (
            meta.get("heading_count")
            if meta.get("heading_count")
            is not None
            else len(headings)
        ),
        "line_count": meta.get(
            "line_count"
        ),
        "source_metadata": {
            **src_meta,
            **meta,
        },
        "normalization": (
            normalization_metadata
        ),
        "boundary": {
            "performs_extraction": False,
            "performs_normalization": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "creates_uucd": False,
        },
    }

    return UploadedDocumentUnifiedContent(
        schema_version=(
            UDUC_SCHEMA_VERSION
        ),
        pipeline_version=(
            UDUC_PIPELINE_VERSION
        ),
        workspace_id=ws,
        document_id=doc_id,
        source_type="uploaded_document",
        source_format=source_format,
        original_filename=str(
            original_name or ""
        ),
        stored_filename=str(
            stored_name or ""
        ),
        stored_path=str(
            final_stored_path or ""
        ),
        title=title,
        h1=h1,
        headings=headings,
        content_body=content_body,
        structure=structure,
        metadata=merged_metadata,
        extraction_status=(
            normalized_content.extraction_status
        ),
        extraction_confidence=_as_float(
            normalized_content.extraction_confidence,
            0.0,
        ),
        extraction_created_at=(
            normalized_content.extraction_created_at
        ),
        normalization_status=(
            normalized_content.normalization_status
        ),
        normalization_version=(
            normalized_content.normalization_version
        ),
        normalized_at=(
            normalized_content.normalized_at
        ),
        created_at=_now_iso(),
    )


def build_uduc_from_upload_extraction_result(
    *,
    extraction_result: Any,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> UploadedDocumentUnifiedContent:
    """
    Legacy compatibility wrapper.

    Direct extraction-result input is no longer canonical.
    This wrapper must pass through U7 before UDUC construction.
    """

    canonical_extraction = (
        _coerce_upload_extraction_result(
            extraction_result
        )
    )

    normalized_content = (
        normalize_uploaded_document_v1(
            canonical_extraction
        )
    )

    if (
        normalized_content.normalization_status
        != "success"
    ):
        raise ValueError(
            "Legacy UDUC compatibility input could not be normalized successfully."
        )

    return build_uduc_from_normalized_content(
        normalized_content=(
            normalized_content
        ),
        workspace_id=workspace_id,
        document_id=document_id,
        original_filename=(
            original_filename
        ),
        stored_filename=(
            stored_filename
        ),
        stored_path=stored_path,
        source_metadata=source_metadata,
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


def build_and_write_uduc_from_normalized_content(
    *,
    normalized_content: NormalizedUploadedDocumentContent,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Canonical U8 builder + persistence entry point.
    """

    uduc = build_uduc_from_normalized_content(
        normalized_content=(
            normalized_content
        ),
        workspace_id=workspace_id,
        document_id=document_id,
        original_filename=(
            original_filename
        ),
        stored_filename=(
            stored_filename
        ),
        stored_path=stored_path,
        source_metadata=source_metadata,
    )

    path = write_uduc(
        uduc
    )

    return {
        "ok": True,
        "workspace_id": uduc.workspace_id,
        "document_id": uduc.document_id,
        "uduc_path": str(path),
        "uduc": serialize_uduc(uduc),
    }


def build_and_write_uduc_from_extraction_result(
    *,
    extraction_result: Any,
    workspace_id: str,
    document_id: str | None = None,
    original_filename: str | None = None,
    stored_filename: str | None = None,
    stored_path: str | None = None,
    source_metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Legacy compatibility wrapper.

    Extraction-result callers are forced through U7 before UDUC
    construction. This function is not the canonical U8 entry point.
    """

    uduc = build_uduc_from_upload_extraction_result(
        extraction_result=(
            extraction_result
        ),
        workspace_id=workspace_id,
        document_id=document_id,
        original_filename=(
            original_filename
        ),
        stored_filename=(
            stored_filename
        ),
        stored_path=stored_path,
        source_metadata=source_metadata,
    )

    path = write_uduc(
        uduc
    )

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
        "input": "NormalizedUploadedDocumentContent",
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
