from pathlib import Path
import shutil


root = Path("backend/server")

uduc_path = (
    root
    / "stores"
    / "uploaded_document_unified_content.py"
)

coordinator_path = (
    root
    / "pipelines"
    / "upload_document"
    / "coordinator.py"
)

backup_dir = (
    root
    / "backups"
    / "u8_5_u7_to_uduc_handoff_realignment"
)

backup_dir.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 1. SAFETY BACKUPS
# ============================================================

shutil.copy2(
    uduc_path,
    backup_dir
    / "uploaded_document_unified_content.py",
)

shutil.copy2(
    coordinator_path,
    backup_dir
    / "coordinator.py",
)

print(
    "U8.5_UDUC_BACKUP_CREATED: YES"
)

print(
    "U8.5_COORDINATOR_BACKUP_CREATED: YES"
)


# ============================================================
# 2. PATCH UDUC MODULE
# ============================================================

uduc = uduc_path.read_text(
    encoding="utf-8-sig",
)


old_typing = (
    "from typing import Any, Dict, List, Optional\n"
)

new_typing = '''from typing import Any, Dict, List, Optional

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)
from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
    normalize_uploaded_document_v1,
)
'''

if old_typing not in uduc:
    raise RuntimeError(
        "U8.5 could not locate UDUC typing import."
    )

uduc = uduc.replace(
    old_typing,
    new_typing,
    1,
)


old_versions = '''UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v1"
UDUC_PIPELINE_VERSION = "verification_6d_uduc_v1_1"
'''

new_versions = '''UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v2"
UDUC_PIPELINE_VERSION = "uploaded_document_uduc_pipeline_v2"
'''

if old_versions not in uduc:
    raise RuntimeError(
        "U8.5 could not locate UDUC version constants."
    )

uduc = uduc.replace(
    old_versions,
    new_versions,
    1,
)


old_dataclass = '''@dataclass
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
'''

new_dataclass = '''@dataclass
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
'''

if old_dataclass not in uduc:
    raise RuntimeError(
        "U8.5 could not locate existing UDUC dataclass."
    )

uduc = uduc.replace(
    old_dataclass,
    new_dataclass,
    1,
)


builder_start = (
    uduc.index(
        "def build_uduc_from_upload_extraction_result("
    )
)

builder_end = (
    uduc.index(
        "\ndef serialize_uduc(",
        builder_start,
    )
)


new_builder_block = r'''def _coerce_upload_extraction_result(
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
'''

uduc = (
    uduc[:builder_start]
    + new_builder_block
    + uduc[builder_end:]
)


writer_start = (
    uduc.index(
        "def build_and_write_uduc_from_extraction_result("
    )
)

writer_end = (
    uduc.index(
        "\ndef explain_uploaded_document_unified_content_v1(",
        writer_start,
    )
)


new_writer_block = r'''def build_and_write_uduc_from_normalized_content(
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
'''

uduc = (
    uduc[:writer_start]
    + new_writer_block
    + uduc[writer_end:]
)


# Update explain contract without touching unrelated structure.
uduc = uduc.replace(
    '"input": "UploadExtractionResult",',
    '"input": "NormalizedUploadedDocumentContent",',
    1,
)

uduc_path.write_text(
    uduc,
    encoding="utf-8",
)

print(
    "U8.5_UDUC_V2_PATCH_APPLIED: YES"
)


# ============================================================
# 3. PATCH TOP UPLOAD COORDINATOR
# ============================================================

coordinator = coordinator_path.read_text(
    encoding="utf-8-sig",
)


old_import = '''from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_extraction_result,
)
'''

new_import = '''from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)
from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)
from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_normalized_content,
)
'''

if old_import not in coordinator:
    raise RuntimeError(
        "U8.5 could not locate coordinator UDUC import."
    )

coordinator = coordinator.replace(
    old_import,
    new_import,
    1,
)


old_uduc_call = '''    # ------------------------------------------------------------
    # Canonical UDUC construction + persistence.
    # ------------------------------------------------------------

    uduc_result = build_and_write_uduc_from_extraction_result(
        extraction_result=extraction_result,
        workspace_id=normalized_workspace_id,
        document_id=document_id,
        original_filename=_required_string(
            document_metadata,
            "filename",
        ),
        stored_filename=_required_string(
            document_metadata,
            "stored_name",
        ),
        source_metadata=document_metadata,
    )
'''

new_uduc_call = '''    # ------------------------------------------------------------
    # Canonical U7 normalization.
    #
    # Pipeline 2 returns the serialized UploadExtractionResult for
    # compatibility. Reconstruct the canonical U6 result, then pass it
    # through U7 before UDUC construction.
    # ------------------------------------------------------------

    extraction_metadata = extraction_result.get(
        "metadata"
    )

    if not isinstance(
        extraction_metadata,
        dict,
    ):
        extraction_metadata = {}

    extraction_headings = extraction_result.get(
        "headings"
    )

    if not isinstance(
        extraction_headings,
        list,
    ) or not all(
        isinstance(
            heading,
            str,
        )
        for heading in extraction_headings
    ):
        raise RuntimeError(
            "Pipeline 2 extraction headings are malformed."
        )

    canonical_extraction_result = UploadExtractionResult(
        source_path=str(
            extraction_result.get(
                "source_path"
            )
            or ""
        ),
        source_type=str(
            extraction_result.get(
                "source_type"
            )
            or ""
        ),
        title=str(
            extraction_result.get(
                "title"
            )
            or ""
        ),
        text=str(
            extraction_result.get(
                "text"
            )
            or ""
        ),
        headings=list(
            extraction_headings
        ),
        metadata=dict(
            extraction_metadata
        ),
        extraction_status=str(
            extraction_result.get(
                "extraction_status"
            )
            or ""
        ),
        extraction_confidence=float(
            extraction_result.get(
                "extraction_confidence"
            )
            or 0.0
        ),
        created_at=str(
            extraction_result.get(
                "created_at"
            )
            or ""
        ),
    )

    normalized_content = (
        normalize_uploaded_document_v1(
            canonical_extraction_result
        )
    )

    if (
        normalized_content.normalization_status
        != "success"
    ):
        raise RuntimeError(
            "Canonical uploaded-document normalization did not complete successfully."
        )

    # ------------------------------------------------------------
    # Canonical U8 UDUC construction + persistence.
    # ------------------------------------------------------------

    uduc_result = build_and_write_uduc_from_normalized_content(
        normalized_content=normalized_content,
        workspace_id=normalized_workspace_id,
        document_id=document_id,
        original_filename=_required_string(
            document_metadata,
            "filename",
        ),
        stored_filename=_required_string(
            document_metadata,
            "stored_name",
        ),
        source_metadata=document_metadata,
    )
'''

if old_uduc_call not in coordinator:
    raise RuntimeError(
        "U8.5 could not locate coordinator UDUC call block."
    )

coordinator = coordinator.replace(
    old_uduc_call,
    new_uduc_call,
    1,
)

coordinator_path.write_text(
    coordinator,
    encoding="utf-8",
)

print(
    "U8.5_COORDINATOR_HANDOFF_PATCH_APPLIED: YES"
)


# ============================================================
# 4. STATIC POST-PATCH ASSERTIONS
# ============================================================

patched_uduc = uduc_path.read_text(
    encoding="utf-8-sig",
)

patched_coordinator = (
    coordinator_path.read_text(
        encoding="utf-8-sig",
    )
)


required_uduc_markers = [
    'UDUC_SCHEMA_VERSION = "uploaded_document_unified_content_v2"',
    'UDUC_PIPELINE_VERSION = "uploaded_document_uduc_pipeline_v2"',
    "def build_uduc_from_normalized_content(",
    "def build_and_write_uduc_from_normalized_content(",
    "extraction_created_at: str =",
    "normalization_status: str =",
    "normalization_version: str =",
    "normalized_at: str =",
    "normalize_uploaded_document_v1(",
]

for marker in required_uduc_markers:
    if marker not in patched_uduc:
        raise RuntimeError(
            f"Missing patched UDUC marker: {marker}"
        )


required_coordinator_markers = [
    "UploadExtractionResult",
    "normalize_uploaded_document_v1",
    "build_and_write_uduc_from_normalized_content",
    "canonical_extraction_result = UploadExtractionResult(",
    "normalized_content =",
]

for marker in required_coordinator_markers:
    if marker not in patched_coordinator:
        raise RuntimeError(
            f"Missing coordinator marker: {marker}"
        )


print(
    "U8.5_STATIC_POST_PATCH_ASSERTIONS: PASS"
)

print(
    "U8.5_CANONICAL_HANDOFF: "
    "UploadExtractionResult -> "
    "NormalizedUploadedDocumentContent -> "
    "UploadedDocumentUnifiedContent"
)

print(
    "U8.5_LEGACY_EXTRACTION_BUILDER_BYPASSES_U7: NO"
)

print(
    "U8.5_PRODUCTION_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.5_NEXT_STEP: COMPILE_AND_HANDOFF_VERIFICATION"
)