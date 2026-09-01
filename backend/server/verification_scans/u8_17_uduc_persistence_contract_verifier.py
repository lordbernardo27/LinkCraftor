from pathlib import Path
import ast
import copy
import json
import py_compile
import tempfile

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    UDUC_PIPELINE_VERSION,
    UDUC_SCHEMA_VERSION,
    build_and_write_uduc_from_normalized_content,
    build_uduc_from_normalized_content,
    read_uduc,
    serialize_uduc,
    uduc_output_path,
    write_uduc,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_normalized(
    *,
    title="Persistence Title",
    text="Paragraph one.\n\nParagraph two.",
    headings=None,
):
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_17.txt",
        source_type="txt",
        title=title,
        text=text,
        headings=(
            list(headings)
            if headings is not None
            else ["Persistence Heading"]
        ),
        metadata={
            "filename": "u8_17.txt",
            "extension": ".txt",
            "file_size": 123,
            "extraction_method": "txt_upload_v1",
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


print("=== U8.17 UDUC PERSISTENCE CONTRACT VERIFICATION ===")


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
# B. Persistence function inventory
# ------------------------------------------------------------

print()
print("=== B. PERSISTENCE FUNCTION INVENTORY ===")

for name in [
    "uduc_output_path",
    "write_uduc",
    "read_uduc",
    "build_and_write_uduc_from_normalized_content",
    "build_and_write_uduc_from_extraction_result",
]:
    check(
        f"FUNCTION_{name.upper()}_PRESENT",
        hasattr(
            uduc_module,
            name,
        ),
    )


# ------------------------------------------------------------
# C. Version contract
# ------------------------------------------------------------

print()
print("=== C. VERSION CONTRACT ===")

check(
    "UDUC_SCHEMA_VERSION_IS_V2",
    UDUC_SCHEMA_VERSION
    == "uploaded_document_unified_content_v2",
)

check(
    "UDUC_PIPELINE_VERSION_IS_V2",
    UDUC_PIPELINE_VERSION
    == "uploaded_document_uduc_pipeline_v2",
)


# ------------------------------------------------------------
# D. Canonical 22-field object
# ------------------------------------------------------------

print()
print("=== D. CANONICAL 22-FIELD OBJECT ===")

normalized = make_normalized()
normalized_before = copy.deepcopy(
    normalized
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_17",
    document_id="doc_u8_17",
    original_filename="u8_17.txt",
    stored_filename="stored_u8_17.txt",
    stored_path="C:/persisted/ws_u8_17/stored_u8_17.txt",
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
    "SERIALIZED_FIELD_COUNT_22",
    len(
        serialized
    )
    == 22,
)

check(
    "SERIALIZED_FIELDS_EXACT",
    list(
        serialized.keys()
    )
    == expected_fields,
)


# ------------------------------------------------------------
# E. Temporary isolated persistence root
# ------------------------------------------------------------

print()
print("=== E. ISOLATED PERSISTENCE ROOT ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_17_uduc_"
) as temp_dir:

    temp_root = Path(
        temp_dir
    )

    patched_output_constant = False

    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = temp_root
        patched_output_constant = True

    print(
        f"TEMP_UDUC_ROOT={temp_root}"
    )

    check(
        "TEMP_ROOT_EXISTS",
        temp_root.exists(),
    )


    # --------------------------------------------------------
    # F. Output path contract
    # --------------------------------------------------------

    print()
    print("=== F. OUTPUT PATH CONTRACT ===")

    path_a = uduc_output_path(
        "ws_alpha",
        "doc_alpha",
    )

    path_a_repeat = uduc_output_path(
        "ws_alpha",
        "doc_alpha",
    )

    path_b = uduc_output_path(
        "ws_beta",
        "doc_alpha",
    )

    path_c = uduc_output_path(
        "ws_alpha",
        "doc_beta",
    )

    print(
        f"PATH_A={path_a}"
    )

    check(
        "OUTPUT_PATH_DETERMINISTIC",
        path_a
        == path_a_repeat,
    )

    check(
        "WORKSPACE_IDENTITY_ISOLATED",
        path_a
        != path_b,
    )

    check(
        "DOCUMENT_IDENTITY_ISOLATED",
        path_a
        != path_c,
    )

    check(
        "PATH_CONTAINS_WORKSPACE_ID",
        "ws_alpha"
        in str(
            path_a
        ),
    )

    check(
        "PATH_CONTAINS_DOCUMENT_ID",
        "doc_alpha"
        in str(
            path_a
        ),
    )


    # --------------------------------------------------------
    # G. Missing identity rejection
    # --------------------------------------------------------

    print()
    print("=== G. IDENTITY REJECTION ===")

    workspace_none_rejected = False

    try:
        uduc_output_path(
            None,
            "doc_alpha",
        )
    except Exception:
        workspace_none_rejected = True

    check(
        "MISSING_WORKSPACE_REJECTED",
        workspace_none_rejected,
    )


    workspace_blank_rejected = False

    try:
        uduc_output_path(
            "   ",
            "doc_alpha",
        )
    except Exception:
        workspace_blank_rejected = True

    check(
        "BLANK_WORKSPACE_REJECTED",
        workspace_blank_rejected,
    )


    document_none_rejected = False

    try:
        uduc_output_path(
            "ws_alpha",
            None,
        )
    except Exception:
        document_none_rejected = True

    check(
        "MISSING_DOCUMENT_REJECTED",
        document_none_rejected,
    )


    document_blank_rejected = False

    try:
        uduc_output_path(
            "ws_alpha",
            "   ",
        )
    except Exception:
        document_blank_rejected = True

    check(
        "BLANK_DOCUMENT_REJECTED",
        document_blank_rejected,
    )


    # --------------------------------------------------------
    # H. Direct write
    # --------------------------------------------------------

    print()
    print("=== H. DIRECT WRITE ===")

    written_path = write_uduc(
        uduc
    )

    check(
        "WRITE_RETURNS_PATH",
        isinstance(
            written_path,
            Path,
        ),
    )

    check(
        "FINAL_JSON_EXISTS",
        written_path.exists(),
    )

    check(
        "FINAL_PATH_MATCHES_OUTPUT_PATH",
        written_path
        == uduc_output_path(
            "ws_u8_17",
            "doc_u8_17",
        ),
    )


    raw_bytes = written_path.read_bytes()

    utf8_ok = True

    try:
        raw_text = raw_bytes.decode(
            "utf-8"
        )
    except UnicodeDecodeError:
        utf8_ok = False
        raw_text = ""

    check(
        "PERSISTED_JSON_UTF8",
        utf8_ok,
    )


    parsed = json.loads(
        raw_text
    )

    check(
        "PERSISTED_JSON_IS_OBJECT",
        isinstance(
            parsed,
            dict,
        ),
    )

    check(
        "PERSISTED_JSON_MATCHES_SERIALIZED_UDUC",
        parsed
        == serialized,
    )


    # --------------------------------------------------------
    # I. Persisted 22-field contract
    # --------------------------------------------------------

    print()
    print("=== I. PERSISTED SCHEMA ===")

    check(
        "PERSISTED_FIELD_COUNT_22",
        len(
            parsed
        )
        == 22,
    )

    check(
        "PERSISTED_SCHEMA_VERSION_V2",
        parsed.get(
            "schema_version"
        )
        == "uploaded_document_unified_content_v2",
    )

    check(
        "PERSISTED_PIPELINE_VERSION_V2",
        parsed.get(
            "pipeline_version"
        )
        == "uploaded_document_uduc_pipeline_v2",
    )

    for field in [
        "structure",
        "metadata",
        "h1",
        "extraction_status",
        "extraction_confidence",
        "extraction_created_at",
        "normalization_status",
        "normalization_version",
        "normalized_at",
    ]:
        check(
            "PERSISTED_FIELD_"
            + field.upper()
            + "_PRESENT",
            field
            in parsed,
        )


    # --------------------------------------------------------
    # J. Read contract
    # --------------------------------------------------------

    print()
    print("=== J. READ CONTRACT ===")

    read_back = read_uduc(
        "ws_u8_17",
        "doc_u8_17",
    )

    print(
        f"READ_UDUC_TYPE={type(read_back).__name__}"
    )

    check(
        "READ_UDUC_NOT_NONE_AFTER_WRITE",
        read_back
        is not None,
    )

    if isinstance(
        read_back,
        dict,
    ):
        read_serialized = read_back
    else:
        read_serialized = (
            serialize_uduc(
                read_back
            )
            if read_back is not None
            else None
        )

    check(
        "READ_ROUND_TRIP_MATCHES_WRITE",
        read_serialized
        == serialized,
    )


    missing_read_predictable = False
    missing_read_value = None

    try:
        missing_read_value = read_uduc(
            "ws_u8_17",
            "missing_document",
        )
        missing_read_predictable = True
    except FileNotFoundError:
        missing_read_predictable = True
    except Exception:
        missing_read_predictable = False

    check(
        "MISSING_READ_HANDLED_PREDICTABLY",
        missing_read_predictable,
    )

    print(
        f"MISSING_READ_VALUE={missing_read_value!r}"
    )


    # --------------------------------------------------------
    # K. Atomic overwrite behavior
    # --------------------------------------------------------

    print()
    print("=== K. ATOMIC OVERWRITE BEHAVIOR ===")

    first_path = written_path

    second_normalized = make_normalized(
        title="Updated Persistence Title",
        text="Updated body.",
        headings=[
            "Updated Heading",
        ],
    )

    second_uduc = build_uduc_from_normalized_content(
        normalized_content=second_normalized,
        workspace_id="ws_u8_17",
        document_id="doc_u8_17",
        original_filename="u8_17.txt",
        stored_filename="stored_u8_17.txt",
        stored_path="C:/persisted/ws_u8_17/stored_u8_17.txt",
    )

    second_serialized = serialize_uduc(
        second_uduc
    )

    second_path = write_uduc(
        second_uduc
    )

    check(
        "OVERWRITE_USES_SAME_FINAL_PATH",
        second_path
        == first_path,
    )

    overwritten = json.loads(
        second_path.read_text(
            encoding="utf-8"
        )
    )

    check(
        "OVERWRITE_REPLACES_PRIOR_CONTENT",
        overwritten
        == second_serialized,
    )

    check(
        "OVERWRITE_TITLE_UPDATED",
        overwritten.get(
            "title"
        )
        == "Updated Persistence Title",
    )


    sibling_json_files = list(
        second_path.parent.glob(
            "*.json"
        )
    )

    check(
        "NO_DUPLICATE_JSON_SIBLING_FOR_SAME_DOCUMENT",
        len(
            sibling_json_files
        )
        == 1,
    )


    tmp_candidates = [
        p
        for p in second_path.parent.iterdir()
        if p.name.endswith(
            ".tmp"
        )
        or ".tmp." in p.name
    ]

    check(
        "NO_TEMP_FILE_REMAINS_AFTER_SUCCESS",
        tmp_candidates
        == [],
    )


    # --------------------------------------------------------
    # L. Identity isolation writes
    # --------------------------------------------------------

    print()
    print("=== L. IDENTITY ISOLATION WRITES ===")

    ws_b_uduc = build_uduc_from_normalized_content(
        normalized_content=make_normalized(),
        workspace_id="ws_other",
        document_id="doc_u8_17",
    )

    doc_b_uduc = build_uduc_from_normalized_content(
        normalized_content=make_normalized(),
        workspace_id="ws_u8_17",
        document_id="doc_other",
    )

    ws_b_path = write_uduc(
        ws_b_uduc
    )

    doc_b_path = write_uduc(
        doc_b_uduc
    )

    check(
        "WORKSPACE_B_WRITE_ISOLATED",
        ws_b_path
        != second_path,
    )

    check(
        "DOCUMENT_B_WRITE_ISOLATED",
        doc_b_path
        != second_path,
    )

    check(
        "ALL_ISOLATED_FINAL_FILES_EXIST",
        second_path.exists()
        and ws_b_path.exists()
        and doc_b_path.exists(),
    )


    # --------------------------------------------------------
    # M. Canonical build-and-write entry
    # --------------------------------------------------------

    print()
    print("=== M. CANONICAL BUILD-AND-WRITE ENTRY ===")

    canonical_entry_normalized = make_normalized(
        title="Entry Point Title",
    )

    canonical_entry_before = copy.deepcopy(
        canonical_entry_normalized
    )

    entry_result = build_and_write_uduc_from_normalized_content(
        normalized_content=canonical_entry_normalized,
        workspace_id="ws_entry",
        document_id="doc_entry",
        original_filename="entry.txt",
        stored_filename="stored_entry.txt",
        stored_path="C:/persisted/ws_entry/stored_entry.txt",
    )

    print(
        f"BUILD_AND_WRITE_RETURN_TYPE={type(entry_result).__name__}"
    )

    check(
        "BUILD_AND_WRITE_DID_NOT_MUTATE_NORMALIZED_INPUT",
        canonical_entry_normalized
        == canonical_entry_before,
    )


    entry_path = uduc_output_path(
        "ws_entry",
        "doc_entry",
    )

    check(
        "BUILD_AND_WRITE_PERSISTED_FILE_EXISTS",
        entry_path.exists(),
    )


    # --------------------------------------------------------
    # N. Restore output constant
    # --------------------------------------------------------

    if patched_output_constant:
        uduc_module.UDUC_OUTPUT_DIR = original_output_dir


# ------------------------------------------------------------
# O. Static persistence inspection
# ------------------------------------------------------------

print()
print("=== O. STATIC PERSISTENCE INSPECTION ===")

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


path_source = function_source(
    "uduc_output_path"
)

write_source = function_source(
    "write_uduc"
)

read_source = function_source(
    "read_uduc"
)

canonical_entry_source = function_source(
    "build_and_write_uduc_from_normalized_content"
)


check(
    "WRITE_USES_JSON_SERIALIZATION",
    "json."
    in write_source.lower()
    or "serialize_uduc"
    in write_source,
)

check(
    "WRITE_HAS_TEMP_FILE_BEHAVIOR",
    ".tmp"
    in write_source,
)

check(
    "WRITE_HAS_REPLACE_BEHAVIOR",
    ".replace("
    in write_source
    or "os.replace"
    in write_source,
)

check(
    "WRITE_CREATES_PARENT_DIRECTORY",
    ".mkdir("
    in write_source,
)

check(
    "READ_USES_PERSISTED_JSON",
    "json."
    in read_source.lower(),
)


# ------------------------------------------------------------
# P. No source/extraction/normalization rerun
# ------------------------------------------------------------

print()
print("=== P. PERSISTENCE BOUNDARY ===")

persistence_scope = "\n".join(
    [
        path_source,
        write_source,
        read_source,
        canonical_entry_source,
    ]
)

for marker in [
    "extract_upload_document",
    "detect_upload_source_type",
    "normalize_uploaded_document_v1",
    "_normalize_title",
    "_normalize_headings",
    "unicodedata.normalize",
]:
    check(
        "PERSISTENCE_SCOPE_NO_"
        + marker.upper()
        .replace(".", "_"),
        marker.lower()
        not in persistence_scope.lower(),
    )


# ------------------------------------------------------------
# Q. No downstream coupling
# ------------------------------------------------------------

print()
print("=== Q. DOWNSTREAM BOUNDARY ===")

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
        "PERSISTENCE_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in persistence_scope.lower(),
    )


# ------------------------------------------------------------
# R. Input immutability
# ------------------------------------------------------------

print()
print("=== R. INPUT IMMUTABILITY ===")

check(
    "ORIGINAL_NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)


# ------------------------------------------------------------
# S. Final decision
# ------------------------------------------------------------

print()
print("=== S. U8.17 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.17_UDUC_PERSISTENCE_CONTRACT: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.17_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.17_UDUC_PERSISTENCE_CONTRACT: CERTIFIED"
    )

    print(
        "U8.17_PERSISTENCE_SCOPE: CANONICAL_UDUC_ONLY"
    )

    print(
        "U8.17_PATH_SCOPE: WORKSPACE_AND_DOCUMENT"
    )

    print(
        "U8.17_WRITE_ENCODING: UTF8_JSON"
    )

    print(
        "U8.17_ATOMIC_REPLACE: YES"
    )

    print(
        "U8.17_TEMP_FILE_CLEAN_AFTER_SUCCESS: YES"
    )

    print(
        "U8.17_ROUND_TRIP: PASS"
    )

    print(
        "U8.17_SOURCE_REREAD: NO"
    )

    print(
        "U8.17_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.17_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.17_DOWNSTREAM_EXECUTION: NO"
    )

    print(
        "U8.17_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.18_FAILURE_CONTRACT_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.17_FINAL_UDUC_PERSISTENCE_VERIFICATION: PASS"
    )