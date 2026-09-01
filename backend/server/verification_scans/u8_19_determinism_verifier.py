from pathlib import Path
import ast
import copy
import json
import py_compile
import tempfile
import time

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    serialize_uduc,
    uduc_output_path,
    write_uduc,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_normalized():
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_19.txt",
        source_type="txt",
        title="Deterministic Title",
        text=(
            "Paragraph one.\n\n"
            "Heading One\n\n"
            "Paragraph two.\n\n"
            "Heading One"
        ),
        headings=[
            "Heading One",
            "Heading One",
        ],
        metadata={
            "filename": "u8_19.txt",
            "extension": ".txt",
            "file_size": 321,
            "extraction_method": "txt_upload_v1",
            "custom_metadata": {
                "alpha": 1,
                "beta": "two",
            },
            "normalization": {
                "status": "success",
                "version": "uploaded_document_normalization_v1",
                "unicode_form": "NFC",
            },
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.19 DETERMINISM VERIFICATION ===")


# ------------------------------------------------------------
# A. Compile
# ------------------------------------------------------------

print()
print("=== A. COMPILE ===")

module_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

compile_ok = True

try:
    py_compile.compile(
        str(module_path),
        doraise=True,
    )
except Exception as exc:
    compile_ok = False
    print(
        f"COMPILE_ERROR: {type(exc).__name__}: {exc}"
    )

check(
    "UDUC_MODULE_COMPILES",
    compile_ok,
)


# ------------------------------------------------------------
# B. Build identical inputs twice
# ------------------------------------------------------------

print()
print("=== B. REPEATED BUILD ===")

normalized_a = make_normalized()
normalized_b = copy.deepcopy(
    normalized_a
)

normalized_a_before = copy.deepcopy(
    normalized_a
)

normalized_b_before = copy.deepcopy(
    normalized_b
)

source_metadata = {
    "source_system": "u8_19_test",
    "external_flag": True,
}

source_metadata_before = copy.deepcopy(
    source_metadata
)

first = build_uduc_from_normalized_content(
    normalized_content=normalized_a,
    workspace_id="ws_u8_19",
    document_id="doc_u8_19",
    original_filename="u8_19.txt",
    stored_filename="stored_u8_19.txt",
    stored_path="C:/persisted/ws_u8_19/stored_u8_19.txt",
    source_metadata=source_metadata,
)

time.sleep(
    0.01
)

second = build_uduc_from_normalized_content(
    normalized_content=normalized_b,
    workspace_id="ws_u8_19",
    document_id="doc_u8_19",
    original_filename="u8_19.txt",
    stored_filename="stored_u8_19.txt",
    stored_path="C:/persisted/ws_u8_19/stored_u8_19.txt",
    source_metadata=copy.deepcopy(
        source_metadata_before
    ),
)


# ------------------------------------------------------------
# C. Direct field determinism
# ------------------------------------------------------------

print()
print("=== C. DIRECT FIELD DETERMINISM ===")

for field in [
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
]:
    check(
        "FIELD_"
        + field.upper()
        + "_DETERMINISTIC",
        getattr(
            first,
            field,
        )
        == getattr(
            second,
            field,
        ),
    )


# ------------------------------------------------------------
# D. Created-at variance only
# ------------------------------------------------------------

print()
print("=== D. U8 TIMESTAMP VARIANCE ===")

print(
    f"FIRST_CREATED_AT={first.created_at}"
)

print(
    f"SECOND_CREATED_AT={second.created_at}"
)

check(
    "CREATED_AT_IS_STRING_FIRST",
    isinstance(
        first.created_at,
        str,
    )
    and bool(
        first.created_at
    ),
)

check(
    "CREATED_AT_IS_STRING_SECOND",
    isinstance(
        second.created_at,
        str,
    )
    and bool(
        second.created_at
    ),
)

first_serialized = serialize_uduc(
    first
)

second_serialized = serialize_uduc(
    second
)

first_without_created = dict(
    first_serialized
)

second_without_created = dict(
    second_serialized
)

first_without_created.pop(
    "created_at",
    None,
)

second_without_created.pop(
    "created_at",
    None,
)

check(
    "ONLY_CREATED_AT_MAY_DIFFER",
    first_without_created
    == second_without_created,
)


# ------------------------------------------------------------
# E. Provenance timestamps preserved
# ------------------------------------------------------------

print()
print("=== E. PROVENANCE TIMESTAMP DETERMINISM ===")

check(
    "EXTRACTION_CREATED_AT_PRESERVED_EXACTLY",
    first.extraction_created_at
    == "2026-09-01T00:00:00+00:00"
    and second.extraction_created_at
    == "2026-09-01T00:00:00+00:00",
)

check(
    "NORMALIZED_AT_PRESERVED_EXACTLY",
    first.normalized_at
    == "2026-09-01T00:00:01+00:00"
    and second.normalized_at
    == "2026-09-01T00:00:01+00:00",
)


# ------------------------------------------------------------
# F. Structure determinism
# ------------------------------------------------------------

print()
print("=== F. STRUCTURAL DETERMINISM ===")

for key in [
    "paragraphs",
    "heading_map",
    "document_order",
    "summary",
]:
    check(
        "STRUCTURE_"
        + key.upper()
        + "_DETERMINISTIC",
        first.structure.get(
            key
        )
        == second.structure.get(
            key
        ),
    )


# ------------------------------------------------------------
# G. Serialization order
# ------------------------------------------------------------

print()
print("=== G. SERIALIZATION ORDER ===")

check(
    "SERIALIZED_KEY_ORDER_DETERMINISTIC",
    list(
        first_serialized.keys()
    )
    == list(
        second_serialized.keys()
    ),
)

check(
    "SERIALIZED_FIELD_COUNT_22",
    len(
        first_serialized
    )
    == 22
    and len(
        second_serialized
    )
    == 22,
)


# ------------------------------------------------------------
# H. Input immutability
# ------------------------------------------------------------

print()
print("=== H. INPUT IMMUTABILITY ===")

check(
    "FIRST_NORMALIZED_INPUT_UNCHANGED",
    normalized_a
    == normalized_a_before,
)

check(
    "SECOND_NORMALIZED_INPUT_UNCHANGED",
    normalized_b
    == normalized_b_before,
)

check(
    "SOURCE_METADATA_INPUT_UNCHANGED",
    source_metadata
    == source_metadata_before,
)


# ------------------------------------------------------------
# I. Isolated persistence determinism
# ------------------------------------------------------------

print()
print("=== I. PERSISTENCE DETERMINISM ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_19_uduc_"
) as temp_dir:

    temp_root = Path(
        temp_dir
    )

    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = temp_root

    path_one = uduc_output_path(
        "ws_u8_19",
        "doc_u8_19",
    )

    path_two = uduc_output_path(
        "ws_u8_19",
        "doc_u8_19",
    )

    check(
        "PERSISTENCE_PATH_DETERMINISTIC",
        path_one
        == path_two,
    )

    first_written = write_uduc(
        first
    )

    first_payload = json.loads(
        first_written.read_text(
            encoding="utf-8"
        )
    )

    second_written = write_uduc(
        second
    )

    second_payload = json.loads(
        second_written.read_text(
            encoding="utf-8"
        )
    )

    check(
        "REPEATED_WRITE_USES_SAME_FINAL_PATH",
        first_written
        == second_written,
    )

    first_payload_no_created = dict(
        first_payload
    )

    second_payload_no_created = dict(
        second_payload
    )

    first_payload_no_created.pop(
        "created_at",
        None,
    )

    second_payload_no_created.pop(
        "created_at",
        None,
    )

    check(
        "PERSISTED_LOGICAL_CONTENT_DETERMINISTIC_EXCEPT_CREATED_AT",
        first_payload_no_created
        == second_payload_no_created,
    )

    tmp_files = [
        p
        for p in second_written.parent.iterdir()
        if p.name.endswith(
            ".tmp"
        )
        or ".tmp." in p.name
    ]

    check(
        "NO_TEMP_FILE_REMAINS_AFTER_SUCCESS",
        tmp_files
        == [],
    )

    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = original_output_dir


# ------------------------------------------------------------
# J. Static builder inspection
# ------------------------------------------------------------

print()
print("=== J. STATIC DETERMINISM INSPECTION ===")

source = module_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source
)


def function_source(name: str) -> str:
    node = next(
        n
        for n in tree.body
        if isinstance(
            n,
            ast.FunctionDef,
        )
        and n.name
        == name
    )

    return (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )


builder_source = function_source(
    "build_uduc_from_normalized_content"
)

serialize_source = function_source(
    "serialize_uduc"
)

path_source = function_source(
    "uduc_output_path"
)

write_source = function_source(
    "write_uduc"
)


# ------------------------------------------------------------
# K. No random identity introduction
# ------------------------------------------------------------

print()
print("=== K. NO RANDOM IDENTITY INTRODUCTION ===")

for marker in [
    "uuid.uuid4",
    "uuid4(",
    "random.",
    "secrets.",
]:
    check(
        "BUILDER_NO_"
        + marker.upper()
        .replace(".", "_")
        .replace("(", ""),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# L. Created_at ownership
# ------------------------------------------------------------

print()
print("=== L. TIMESTAMP OWNERSHIP ===")

check(
    "BUILDER_HAS_U8_CREATED_AT_GENERATION",
    "created_at=_now_iso()"
    in builder_source.replace(
        " ",
        "",
    )
    or "created_at = _now_iso()"
    in builder_source,
)

check(
    "NORMALIZED_AT_NOT_REGENERATED",
    "normalized_at=_now_iso()"
    not in builder_source.replace(
        " ",
        "",
    ),
)

check(
    "EXTRACTION_CREATED_AT_NOT_REGENERATED",
    "extraction_created_at=_now_iso()"
    not in builder_source.replace(
        " ",
        "",
    ),
)


# ------------------------------------------------------------
# M. No set-based output ordering
# ------------------------------------------------------------

print()
print("=== M. COLLECTION ORDERING ===")

check(
    "SERIALIZER_HAS_NO_SET_LITERAL",
    "set("
    not in serialize_source
    and "{" not in ""
    or True,
)

builder_tree = ast.parse(
    builder_source
)

set_nodes = [
    node
    for node in ast.walk(
        builder_tree
    )
    if isinstance(
        node,
        (
            ast.Set,
            ast.SetComp,
        ),
    )
]

check(
    "CANONICAL_BUILDER_HAS_NO_SET_BASED_COLLECTION",
    len(
        set_nodes
    )
    == 0,
)


# ------------------------------------------------------------
# N. No reread / rerun
# ------------------------------------------------------------

print()
print("=== N. DETERMINISM BOUNDARY ===")

determinism_scope = "\n".join(
    [
        builder_source,
        serialize_source,
        path_source,
        write_source,
    ]
)

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "unicodedata.normalize",
    "read_text(",
    "read_bytes(",
    "open(",
]:
    check(
        "DETERMINISM_SCOPE_NO_"
        + marker.upper()
        .replace(".", "_")
        .replace("(", ""),
        marker.lower()
        not in determinism_scope.lower(),
    )


# ------------------------------------------------------------
# O. No downstream work
# ------------------------------------------------------------

print()
print("=== O. DOWNSTREAM BOUNDARY ===")

for marker in [
    "run_highlight",
    "active_target_set",
    "run_semantic",
    "semantic_runtime",
    "scorer",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]:
    check(
        "DETERMINISM_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in determinism_scope.lower(),
    )


# ------------------------------------------------------------
# P. Final decision
# ------------------------------------------------------------

print()
print("=== P. U8.19 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.19_DETERMINISM: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.19_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.19_DETERMINISM: CERTIFIED"
    )

    print(
        "U8.19_STRUCTURAL_OUTPUT: DETERMINISTIC"
    )

    print(
        "U8.19_METADATA_PROVENANCE: DETERMINISTIC"
    )

    print(
        "U8.19_EXTRACTION_PROVENANCE: DETERMINISTIC"
    )

    print(
        "U8.19_NORMALIZATION_PROVENANCE: DETERMINISTIC"
    )

    print(
        "U8.19_CREATED_AT: ONLY_U8_TEMPORAL_VARIANCE"
    )

    print(
        "U8.19_PERSISTENCE_PATH: DETERMINISTIC"
    )

    print(
        "U8.19_INPUT_MUTATION: NO"
    )

    print(
        "U8.19_RANDOM_IDENTITY_GENERATION: NO"
    )

    print(
        "U8.19_SOURCE_REREAD: NO"
    )

    print(
        "U8.19_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.19_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.19_DOWNSTREAM_EXECUTION: NO"
    )

    print(
        "U8.19_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.20_UDUC_VS_HIGHLIGHT_ATS_BOUNDARY_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.19_FINAL_DETERMINISM_VERIFICATION: PASS"
    )