from pathlib import Path
import ast
import py_compile

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    serialize_uduc,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.21 CORRECTED UDUC VS CURRENT CANONICAL UUCD BOUNDARY VERIFICATION ===")


# ------------------------------------------------------------
# A. Files
# ------------------------------------------------------------

print()
print("=== A. FILE INVENTORY ===")

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

upload_coordinator_path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

current_uucd_engine_path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_engine_v1.py"
)

current_uucd_persistence_path = Path(
    "backend/server/universal_unified_content_document/"
    "uucd_persistence_v1.py"
)

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("LIVE_UPLOAD_COORDINATOR", upload_coordinator_path),
    ("CURRENT_CANONICAL_UUCD_ENGINE", current_uucd_engine_path),
    ("CURRENT_CANONICAL_UUCD_PERSISTENCE", current_uucd_persistence_path),
]:
    check(
        f"{label}_EXISTS",
        path.exists(),
    )


# ------------------------------------------------------------
# B. Compile U8 production files
# ------------------------------------------------------------

print()
print("=== B. COMPILE ===")

for label, path in [
    ("UDUC_MODULE", uduc_path),
    ("LIVE_UPLOAD_COORDINATOR", upload_coordinator_path),
]:
    ok = True

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )
    except Exception as exc:
        ok = False
        print(
            f"{label}_COMPILE_ERROR="
            f"{type(exc).__name__}: {exc}"
        )

    check(
        f"{label}_COMPILES",
        ok,
    )


# ------------------------------------------------------------
# C. Source extraction
# ------------------------------------------------------------

print()
print("=== C. SOURCE EXTRACTION ===")

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_source = upload_coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_tree = ast.parse(
    uduc_source
)


def function_source(name: str) -> str:
    node = next(
        (
            n
            for n in uduc_tree.body
            if isinstance(
                n,
                ast.FunctionDef,
            )
            and n.name == name
        ),
        None,
    )

    if node is None:
        return ""

    return (
        ast.get_source_segment(
            uduc_source,
            node,
        )
        or ""
    )


builder_source = function_source(
    "build_uduc_from_normalized_content"
)

serializer_source = function_source(
    "serialize_uduc"
)

write_source = function_source(
    "write_uduc"
)

read_source = function_source(
    "read_uduc"
)

build_write_source = function_source(
    "build_and_write_uduc_from_normalized_content"
)

legacy_wrapper_source = function_source(
    "build_and_write_uduc_from_extraction_result"
)

uduc_scope = "\n".join(
    [
        builder_source,
        serializer_source,
        write_source,
        read_source,
        build_write_source,
    ]
)


# ------------------------------------------------------------
# D. UDUC core has no Current Canonical UUCD work
# ------------------------------------------------------------

print()
print("=== D. UDUC CORE VS CURRENT CANONICAL UUCD ===")

for marker in [
    "build_uucd",
    "write_uucd",
    "persist_uucd",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "current_canonical_uucd",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# E. Import boundary
# ------------------------------------------------------------

print()
print("=== E. UDUC IMPORT BOUNDARY ===")

for marker in [
    "universal_unified_content_document",
    "uucd_engine_v1",
    "uucd_persistence_v1",
]:
    check(
        "UDUC_MODULE_NO_IMPORT_"
        + marker.upper(),
        marker.lower()
        not in uduc_source.lower(),
    )


# ------------------------------------------------------------
# F. Live coordinator has no premature UUCD work
# ------------------------------------------------------------

print()
print("=== F. LIVE UPLOAD COORDINATOR VS UUCD ===")

coordinator_lower = coordinator_source.lower()

for marker in [
    "build_uucd",
    "write_uucd",
    "persist_uucd",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "current_canonical_uucd",
]:
    check(
        "LIVE_COORDINATOR_NO_"
        + marker.upper(),
        marker.lower()
        not in coordinator_lower,
    )


# ------------------------------------------------------------
# G. Behavioral canonical 22-field handoff
# ------------------------------------------------------------

print()
print("=== G. CANONICAL UDUC HANDOFF OBJECT ===")

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u8_21.txt",
    source_type="txt",
    title="U8.21 Handoff Title",
    text="Canonical UDUC handoff body.",
    headings=[
        "U8.21 Heading",
    ],
    metadata={
        "filename": "u8_21.txt",
        "extension": ".txt",
        "file_size": 421,
        "extraction_method": "txt_upload_v1",
        "normalization": {
            "status": "success",
            "version": "uploaded_document_normalization_v1",
        },
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:00:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:00:01+00:00",
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_21",
    document_id="doc_u8_21",
    original_filename="u8_21.txt",
    stored_filename="stored_u8_21.txt",
    stored_path="C:/persisted/ws_u8_21/stored_u8_21.txt",
)

serialized = serialize_uduc(
    uduc
)

expected_fields = [
    "schema_version",
    "pipeline_version",
    "workspace_id",
    "document_id",
    "source_type",
    "source_format",
    "original_filename",
    "stored_filename",
    "stored_path",
    "title",
    "h1",
    "headings",
    "content_body",
    "structure",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
    "normalization_status",
    "normalization_version",
    "normalized_at",
    "created_at",
]

check(
    "UDUC_HANDOFF_FIELD_COUNT_22",
    len(serialized) == 22,
)

check(
    "UDUC_HANDOFF_FIELDS_EXACT",
    list(serialized.keys())
    == expected_fields,
)

for field in expected_fields:
    check(
        "UDUC_HANDOFF_FIELD_"
        + field.upper()
        + "_PRESENT",
        field in serialized,
    )


# ------------------------------------------------------------
# H. Handoff contains canonical content and provenance
# ------------------------------------------------------------

print()
print("=== H. U9 HANDOFF SUFFICIENCY ===")

check(
    "HANDOFF_HAS_CANONICAL_CONTENT_BODY",
    serialized.get("content_body")
    == "Canonical UDUC handoff body.",
)

check(
    "HANDOFF_HAS_TITLE",
    serialized.get("title")
    == "U8.21 Handoff Title",
)

check(
    "HANDOFF_HAS_HEADINGS",
    serialized.get("headings")
    == ["U8.21 Heading"],
)

check(
    "HANDOFF_HAS_STRUCTURE",
    isinstance(
        serialized.get("structure"),
        dict,
    ),
)

check(
    "HANDOFF_HAS_METADATA",
    isinstance(
        serialized.get("metadata"),
        dict,
    ),
)

check(
    "HANDOFF_HAS_EXTRACTION_PROVENANCE",
    serialized.get("extraction_status")
    == "success"
    and serialized.get("extraction_confidence")
    == 0.95
    and serialized.get("extraction_created_at")
    == "2026-09-01T01:00:00+00:00",
)

check(
    "HANDOFF_HAS_NORMALIZATION_PROVENANCE",
    serialized.get("normalization_status")
    == "success"
    and serialized.get("normalization_version")
    == "uploaded_document_normalization_v1"
    and serialized.get("normalized_at")
    == "2026-09-01T01:00:01+00:00",
)


# ------------------------------------------------------------
# I. U8 reprocessing boundary
# ------------------------------------------------------------

print()
print("=== I. U8 REPROCESSING BOUNDARY ===")

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "unicodedata.normalize",
    "read_bytes(",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper()
        .replace(".", "_")
        .replace("(", ""),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# J. Universal runtime boundary
# ------------------------------------------------------------

print()
print("=== J. UNIVERSAL RUNTIME BOUNDARY ===")

for marker in [
    "body_store",
    "semantic_runtime",
    "run_semantic",
    "scorer",
    "runtime_reader",
    "route_dispatcher",
]:
    check(
        "UDUC_CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in uduc_scope.lower(),
    )


# ------------------------------------------------------------
# K. Legacy wrapper has no Current Canonical UUCD execution
# ------------------------------------------------------------

print()
print("=== K. LEGACY UDUC WRAPPER BOUNDARY ===")

if legacy_wrapper_source:
    for marker in [
        "build_uucd",
        "write_uucd",
        "uucd_engine_v1",
        "uucd_persistence_v1",
        "current_canonical_uucd",
    ]:
        check(
            "LEGACY_UDUC_WRAPPER_NO_"
            + marker.upper(),
            marker.lower()
            not in legacy_wrapper_source.lower(),
        )
else:
    check(
        "LEGACY_UDUC_WRAPPER_NOT_PRESENT",
        True,
    )


# ------------------------------------------------------------
# L. Narrow uploaded-document UUCD reference inventory
# ------------------------------------------------------------

print()
print("=== L. UPLOADED-DOCUMENT UUCD INVENTORY ===")

search_root = Path(
    "backend/server/pipelines/upload_document"
)

uucd_hits = []

for path in search_root.rglob(
    "*.py"
):
    if (
        "verification_scans"
        in path.parts
        or "backups"
        in path.parts
    ):
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        if "uucd" in line.lower():
            uucd_hits.append(
                (
                    str(path),
                    line_number,
                    line.strip(),
                )
            )


print(
    "UPLOADED_DOCUMENT_PRODUCTION_UUCD_REFERENCE_COUNT="
    + str(len(uucd_hits))
)

for path, line_number, line in uucd_hits:
    print(
        f"UUCD_REFERENCE: {path}:{line_number}: {line}"
    )


execution_terms = [
    "build_uucd(",
    "write_uucd(",
    "persist_uucd(",
    "run_uucd(",
]

execution_hits = [
    item
    for item in uucd_hits
    if any(
        term in item[2].lower()
        for term in execution_terms
    )
]

print(
    "UPLOADED_DOCUMENT_AUTHORITATIVE_UUCD_EXECUTION_HIT_COUNT="
    + str(len(execution_hits))
)

check(
    "NO_AUTHORITATIVE_UUCD_EXECUTION_IN_UPLOADED_DOCUMENT_PIPELINE",
    len(execution_hits) == 0,
)


# ------------------------------------------------------------
# M. Current Canonical UUCD infrastructure is separate
# ------------------------------------------------------------

print()
print("=== M. CURRENT CANONICAL UUCD INFRASTRUCTURE ===")

check(
    "CURRENT_CANONICAL_UUCD_ENGINE_OUTSIDE_UPLOAD_PIPELINE",
    "pipelines/upload_document"
    not in str(
        current_uucd_engine_path
    ).replace(
        "\\",
        "/",
    ),
)

check(
    "CURRENT_CANONICAL_UUCD_PERSISTENCE_OUTSIDE_UPLOAD_PIPELINE",
    "pipelines/upload_document"
    not in str(
        current_uucd_persistence_path
    ).replace(
        "\\",
        "/",
    ),
)


# ------------------------------------------------------------
# N. Explicit U8 → U9 handoff
# ------------------------------------------------------------

print()
print("=== N. U8 TO U9 HANDOFF ===")

check(
    "U8_OUTPUT_ARTIFACT_IS_CANONICAL_UDUC",
    "build_and_write_uduc_from_normalized_content"
    in coordinator_lower,
)

check(
    "U9_CONVERGENCE_NOT_IMPLEMENTED_INSIDE_U8",
    "build_uucd"
    not in uduc_scope.lower()
    and "write_uucd"
    not in uduc_scope.lower(),
)

print(
    "U8_TO_U9_HANDOFF="
    "CANONICAL_UDUC_TO_CURRENT_CANONICAL_UUCD"
)


# ------------------------------------------------------------
# O. Final certification
# ------------------------------------------------------------

print()
print("=== O. U8.21 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.21_UDUC_VS_CURRENT_CANONICAL_UUCD_BOUNDARY: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.21 corrected boundary verification failed."
    )


print(
    "U8.21_UDUC_VS_CURRENT_CANONICAL_UUCD_BOUNDARY: CERTIFIED"
)

print(
    "U8.21_U8_ENDS_AT: CANONICAL_UDUC_PERSISTENCE"
)

print(
    "U8.21_CURRENT_CANONICAL_UUCD_BUILD_INSIDE_U8: NO"
)

print(
    "U8.21_CURRENT_CANONICAL_UUCD_PERSISTENCE_INSIDE_U8: NO"
)

print(
    "U8.21_U9_OWNS: UDUC_TO_CURRENT_CANONICAL_UUCD_CONVERGENCE"
)

print(
    "U8.21_U9_HANDOFF_ARTIFACT: CANONICAL_UDUC"
)

print(
    "U8.21_CANONICAL_UDUC_HANDOFF_FIELDS: 22"
)

print(
    "U8.21_SOURCE_REREAD: NO"
)

print(
    "U8.21_EXTRACTION_RERUN: NO"
)

print(
    "U8.21_NORMALIZATION_RERUN: NO"
)

print(
    "U8.21_BODY_STORE_RUNTIME_EXECUTION: NO"
)

print(
    "U8.21_SEMANTIC_SCORER_EXECUTION: NO"
)

print(
    "U8.21_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U8.22_LEGACY_UDUC_CLEANUP_TRANSITION: AUTHORIZED"
)

print(
    "U8.21_FINAL_BOUNDARY_VERIFICATION: PASS"
)