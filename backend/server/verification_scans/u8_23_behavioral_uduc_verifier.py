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
    build_uduc_from_normalized_content,
    serialize_uduc,
    write_uduc,
    read_uduc,
    uduc_output_path,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.23 BEHAVIORAL UDUC VERIFICATION ===")


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
# B. Canonical normalized input
# ------------------------------------------------------------

print()
print("=== B. CANONICAL NORMALIZED INPUT ===")

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u8_23.txt",
    source_type="txt",
    title="Canonical Title",
    text=(
        "Heading One\n\n"
        "Paragraph alpha beta.\n\n"
        "Heading One\n\n"
        "Paragraph gamma.\n\n"
        "Trailing paragraph."
    ),
    headings=[
        "Heading One",
        "Heading One",
        "Missing Heading",
    ],
    metadata={
        "filename": "u8_23.txt",
        "extension": ".txt",
        "file_size": 0,
        "extraction_method": "txt_upload_v1",
        "custom": {
            "alpha": 1,
            "beta": "two",
        },
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:15:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:15:01+00:00",
)

normalized_before = copy.deepcopy(
    normalized
)

source_metadata = {
    "source_system": "u8_23_test",
    "external_flag": True,
}

source_metadata_before = copy.deepcopy(
    source_metadata
)

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_23",
    document_id="doc_u8_23",
    original_filename="u8_23.txt",
    stored_filename="stored_u8_23.txt",
    stored_path="C:/persisted/ws_u8_23/stored_u8_23.txt",
    source_metadata=source_metadata,
)

serialized = serialize_uduc(
    uduc
)

check(
    "CANONICAL_NORMALIZED_INPUT_SUCCEEDS",
    isinstance(
        serialized,
        dict,
    ),
)


# ------------------------------------------------------------
# C. Exact 22-field contract
# ------------------------------------------------------------

print()
print("=== C. EXACT 22-FIELD CONTRACT ===")

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
    "FIELD_COUNT_22",
    len(serialized) == 22,
)

check(
    "FIELD_ORDER_EXACT",
    list(
        serialized.keys()
    )
    == expected_fields,
)

for field in expected_fields:
    check(
        "FIELD_"
        + field.upper()
        + "_PRESENT",
        field in serialized,
    )


# ------------------------------------------------------------
# D. Version + identity + source provenance
# ------------------------------------------------------------

print()
print("=== D. VERSIONS / IDENTITY / SOURCE ===")

check(
    "SCHEMA_VERSION_V2",
    serialized.get("schema_version")
    == "uploaded_document_unified_content_v2",
)

check(
    "PIPELINE_VERSION_V2",
    serialized.get("pipeline_version")
    == "uploaded_document_uduc_pipeline_v2",
)

check(
    "WORKSPACE_ID_PRESERVED",
    serialized.get("workspace_id")
    == "ws_u8_23",
)

check(
    "DOCUMENT_ID_PRESERVED",
    serialized.get("document_id")
    == "doc_u8_23",
)

check(
    "SOURCE_TYPE_PRESERVED",
    serialized.get("source_type")
    == "txt",
)

check(
    "SOURCE_FORMAT_PRESERVED",
    serialized.get("source_format")
    == "txt",
)

check(
    "ORIGINAL_FILENAME_PRESERVED",
    serialized.get("original_filename")
    == "u8_23.txt",
)

check(
    "STORED_FILENAME_PRESERVED",
    serialized.get("stored_filename")
    == "stored_u8_23.txt",
)

check(
    "STORED_PATH_PRESERVED",
    serialized.get("stored_path")
    == "C:/persisted/ws_u8_23/stored_u8_23.txt",
)


# ------------------------------------------------------------
# E. Title / H1 / headings / body
# ------------------------------------------------------------

print()
print("=== E. CONTENT AUTHORITY ===")

check(
    "TITLE_PRESERVED",
    serialized.get("title")
    == "Canonical Title",
)

check(
    "H1_FIRST_NORMALIZED_HEADING_WINS",
    serialized.get("h1")
    == "Heading One",
)

check(
    "HEADINGS_ORDER_PRESERVED",
    serialized.get("headings")
    == [
        "Heading One",
        "Heading One",
        "Missing Heading",
    ],
)

check(
    "DUPLICATE_HEADINGS_PRESERVED",
    serialized.get("headings").count(
        "Heading One"
    )
    == 2,
)

check(
    "CONTENT_BODY_PRESERVED_EXACTLY",
    serialized.get("content_body")
    == normalized.text,
)


# ------------------------------------------------------------
# F. H1 fallbacks
# ------------------------------------------------------------

print()
print("=== F. H1 FALLBACKS ===")

no_heading = copy.deepcopy(
    normalized
)

no_heading.headings = []
no_heading.title = "Fallback Title"

uduc_no_heading = build_uduc_from_normalized_content(
    normalized_content=no_heading,
    workspace_id="ws_u8_23",
    document_id="doc_u8_23_no_heading",
)

check(
    "H1_FALLS_BACK_TO_TITLE",
    uduc_no_heading.h1
    == "Fallback Title",
)


empty_h1 = copy.deepcopy(
    normalized
)

empty_h1.headings = []
empty_h1.title = ""

uduc_empty_h1 = build_uduc_from_normalized_content(
    normalized_content=empty_h1,
    workspace_id="ws_u8_23",
    document_id="doc_u8_23_empty_h1",
)

check(
    "H1_EMPTY_WHEN_NO_HEADINGS_OR_TITLE",
    uduc_empty_h1.h1
    == "",
)


# ------------------------------------------------------------
# G. Paragraph behavior
# ------------------------------------------------------------

print()
print("=== G. PARAGRAPH STRUCTURE ===")

structure = serialized.get(
    "structure",
    {},
)

paragraphs = structure.get(
    "paragraphs",
    [],
)

check(
    "PARAGRAPH_COUNT_EXPECTED",
    len(paragraphs) == 5,
)

paragraph_slices_ok = True
paragraph_counts_ok = True
paragraph_monotonic_ok = True

previous_end = -1

for paragraph in paragraphs:
    start = paragraph.get(
        "start_char"
    )

    end = paragraph.get(
        "end_char"
    )

    text = paragraph.get(
        "text"
    )

    if not (
        isinstance(start, int)
        and isinstance(end, int)
        and serialized["content_body"][
            start:end
        ]
        == text
    ):
        paragraph_slices_ok = False

    if paragraph.get(
        "char_count"
    ) != len(text):
        paragraph_counts_ok = False

    if paragraph.get(
        "word_count"
    ) != len(
        text.split()
    ):
        paragraph_counts_ok = False

    if start < previous_end:
        paragraph_monotonic_ok = False

    previous_end = end


check(
    "PARAGRAPH_SOURCE_SLICES_EXACT",
    paragraph_slices_ok,
)

check(
    "PARAGRAPH_CHAR_AND_WORD_COUNTS_CORRECT",
    paragraph_counts_ok,
)

check(
    "PARAGRAPH_OFFSETS_MONOTONIC_NON_OVERLAP",
    paragraph_monotonic_ok,
)


# ------------------------------------------------------------
# H. Heading map
# ------------------------------------------------------------

print()
print("=== H. HEADING MAP ===")

heading_map = structure.get(
    "heading_map",
    [],
)

check(
    "HEADING_MAP_COUNT_3",
    len(heading_map) == 3,
)

check(
    "HEADING_MAP_ORDER_PRESERVED",
    [
        item.get("heading")
        for item in heading_map
    ]
    == [
        "Heading One",
        "Heading One",
        "Missing Heading",
    ],
)

check(
    "HEADING_MAP_DUPLICATES_PRESERVED",
    sum(
        1
        for item in heading_map
        if item.get("heading")
        == "Heading One"
    )
    == 2,
)

positions = [
    item.get("char_position")
    for item in heading_map
]

check(
    "HEADING_FORWARD_MATCHING",
    positions[0] is not None
    and positions[1] is not None
    and positions[1] > positions[0],
)

check(
    "UNMATCHED_HEADING_RETAINED_WITH_NULL_POSITION",
    heading_map[-1].get("heading")
    == "Missing Heading"
    and heading_map[-1].get("char_position")
    is None,
)


# ------------------------------------------------------------
# I. Document order
# ------------------------------------------------------------

print()
print("=== I. DOCUMENT ORDER ===")

document_order = structure.get(
    "document_order",
    [],
)

positioned = [
    item
    for item in document_order
    if item.get("char_position")
    is not None
]

unmatched = [
    item
    for item in document_order
    if item.get("char_position")
    is None
]

position_values = [
    item.get("char_position")
    for item in positioned
]

check(
    "DOCUMENT_ORDER_POSITIONED_MONOTONIC",
    position_values
    == sorted(
        position_values
    ),
)

equal_position_heading_first = True

for index in range(
    len(positioned) - 1
):
    left = positioned[index]
    right = positioned[index + 1]

    if (
        left.get("char_position")
        == right.get("char_position")
        and left.get("type")
        != "heading"
    ):
        equal_position_heading_first = False


check(
    "DOCUMENT_ORDER_HEADING_BEFORE_PARAGRAPH_AT_EQUAL_POSITION",
    equal_position_heading_first,
)

check(
    "DOCUMENT_ORDER_UNMATCHED_HEADINGS_LAST",
    unmatched
    and unmatched[-1].get("type")
    == "heading"
    and unmatched[-1].get("text")
    == "Missing Heading",
)


# ------------------------------------------------------------
# J. Structural summary
# ------------------------------------------------------------

print()
print("=== J. STRUCTURAL SUMMARY ===")

summary = structure.get(
    "summary",
    {},
)

check(
    "SUMMARY_PARAGRAPH_COUNT_CORRECT",
    summary.get("paragraph_count")
    == len(paragraphs),
)

check(
    "SUMMARY_HEADING_COUNT_CORRECT",
    summary.get("heading_count")
    == len(heading_map),
)

check(
    "SUMMARY_CHARACTER_COUNT_CORRECT",
    summary.get("character_count")
    == len(
        serialized["content_body"]
    ),
)

check(
    "SUMMARY_WORD_COUNT_CORRECT",
    summary.get("word_count")
    == len(
        serialized["content_body"].split()
    ),
)


# ------------------------------------------------------------
# K. Metadata + extraction provenance
# ------------------------------------------------------------

print()
print("=== K. METADATA / EXTRACTION PROVENANCE ===")

metadata = serialized.get(
    "metadata",
    {},
)

check(
    "SOURCE_METADATA_MERGED",
    metadata.get("source_system")
    == "u8_23_test"
    and metadata.get("external_flag")
    is True,
)

check(
    "NORMALIZED_METADATA_PRESERVED",
    metadata.get("custom")
    == {
        "alpha": 1,
        "beta": "two",
    },
)

check(
    "EXTRACTION_STATUS_PRESERVED",
    serialized.get("extraction_status")
    == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    serialized.get("extraction_confidence")
    == 0.95,
)

check(
    "EXTRACTION_CREATED_AT_PRESERVED",
    serialized.get("extraction_created_at")
    == "2026-09-01T01:15:00+00:00",
)

check(
    "EXTRACTION_METHOD_PRESERVED",
    metadata.get("extraction_method")
    == "txt_upload_v1",
)

check(
    "ZERO_FILE_SIZE_PRESERVED",
    metadata.get("file_size")
    == 0,
)


# ------------------------------------------------------------
# L. Normalization provenance + U8 timestamp
# ------------------------------------------------------------

print()
print("=== L. NORMALIZATION PROVENANCE / CREATED_AT ===")

check(
    "NORMALIZATION_STATUS_PRESERVED",
    serialized.get("normalization_status")
    == "success",
)

check(
    "NORMALIZATION_VERSION_PRESERVED",
    serialized.get("normalization_version")
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZED_AT_PRESERVED",
    serialized.get("normalized_at")
    == "2026-09-01T01:15:01+00:00",
)

check(
    "U8_CREATED_AT_GENERATED",
    isinstance(
        serialized.get("created_at"),
        str,
    )
    and bool(
        serialized.get("created_at")
    ),
)


# ------------------------------------------------------------
# M. Input immutability
# ------------------------------------------------------------

print()
print("=== M. INPUT IMMUTABILITY ===")

check(
    "NORMALIZED_INPUT_UNCHANGED",
    normalized
    == normalized_before,
)

check(
    "SOURCE_METADATA_INPUT_UNCHANGED",
    source_metadata
    == source_metadata_before,
)


# ------------------------------------------------------------
# N. Failure behavior
# ------------------------------------------------------------

print()
print("=== N. FAILURE BEHAVIOR ===")

invalid_input_rejected = False

try:
    build_uduc_from_normalized_content(
        normalized_content="not-normalized",
        workspace_id="ws_u8_23",
        document_id="doc_invalid",
    )
except TypeError:
    invalid_input_rejected = True
except Exception:
    invalid_input_rejected = True


check(
    "INVALID_NORMALIZED_INPUT_REJECTED",
    invalid_input_rejected,
)


failed_normalization = copy.deepcopy(
    normalized
)

failed_normalization.normalization_status = (
    "normalization_error"
)

non_success_rejected = False

try:
    build_uduc_from_normalized_content(
        normalized_content=failed_normalization,
        workspace_id="ws_u8_23",
        document_id="doc_failed_norm",
    )
except ValueError:
    non_success_rejected = True
except Exception:
    non_success_rejected = True


check(
    "NON_SUCCESS_NORMALIZATION_REJECTED",
    non_success_rejected,
)


# ------------------------------------------------------------
# O. Persistence round trip
# ------------------------------------------------------------

print()
print("=== O. PERSISTENCE ROUND TRIP ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_23_uduc_"
) as temp_dir:

    temp_root = Path(
        temp_dir
    )

    uduc_module.UDUC_OUTPUT_DIR = temp_root

    expected_path = uduc_output_path(
        "ws_u8_23",
        "doc_u8_23",
    )

    written_path = write_uduc(
        uduc
    )

    check(
        "PERSISTENCE_PATH_DETERMINISTIC",
        written_path
        == expected_path,
    )

    check(
        "PERSISTED_FILE_EXISTS",
        written_path.exists(),
    )

    persisted = json.loads(
        written_path.read_text(
            encoding="utf-8"
        )
    )

    check(
        "PERSISTED_JSON_EQUALS_SERIALIZED_UDUC",
        persisted
        == serialized,
    )

    round_trip = read_uduc(
        "ws_u8_23",
        "doc_u8_23",
    )

    check(
        "READ_ROUND_TRIP_EQUALS_SERIALIZED_UDUC",
        round_trip
        == serialized,
    )

    missing = read_uduc(
        "ws_u8_23",
        "missing_doc",
    )

    check(
        "MISSING_READ_RETURNS_EMPTY_DICT",
        missing == {},
    )

    malformed_path = uduc_output_path(
        "ws_u8_23",
        "malformed_doc",
    )

    malformed_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    malformed_path.write_text(
        "{bad json",
        encoding="utf-8",
    )

    malformed_raises = False

    try:
        read_uduc(
            "ws_u8_23",
            "malformed_doc",
        )
    except json.JSONDecodeError:
        malformed_raises = True

    check(
        "MALFORMED_JSON_FAILURE_SURFACES",
        malformed_raises,
    )

    non_object_path = uduc_output_path(
        "ws_u8_23",
        "non_object_doc",
    )

    non_object_path.write_text(
        '["not", "object"]',
        encoding="utf-8",
    )

    non_object_raises = False

    try:
        read_uduc(
            "ws_u8_23",
            "non_object_doc",
        )
    except ValueError:
        non_object_raises = True

    check(
        "NON_OBJECT_JSON_REJECTED",
        non_object_raises,
    )

    uduc_module.UDUC_OUTPUT_DIR = original_output_dir


# ------------------------------------------------------------
# P. Static U8 boundary inspection
# ------------------------------------------------------------

print()
print("=== P. U8 BOUNDARY INSPECTION ===")

source = module_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source
)


def function_source(name: str) -> str:
    node = next(
        (
            n
            for n in tree.body
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
            source,
            node,
        )
        or ""
    )


core_scope = "\n".join(
    [
        function_source(
            "build_uduc_from_normalized_content"
        ),
        function_source(
            "serialize_uduc"
        ),
        function_source(
            "write_uduc"
        ),
        function_source(
            "read_uduc"
        ),
        function_source(
            "build_and_write_uduc_from_normalized_content"
        ),
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
        "CORE_NO_"
        + marker.upper()
        .replace(".", "_"),
        marker.lower()
        not in core_scope.lower(),
    )


for marker in [
    "run_uploaded_document_to_highlight_pipeline",
    "active_target_set",
    "run_semantic",
    "semantic_runtime",
    "scorer",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]:
    check(
        "CORE_NO_"
        + marker.upper(),
        marker.lower()
        not in core_scope.lower(),
    )


# ------------------------------------------------------------
# Q. Final decision
# ------------------------------------------------------------

print()
print("=== Q. U8.23 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.23_BEHAVIORAL_UDUC_VERIFICATION: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.23_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.23_BEHAVIORAL_UDUC_VERIFICATION: CERTIFIED"
    )

    print(
        "U8.23_CANONICAL_22_FIELD_CONTRACT: PASS"
    )

    print(
        "U8.23_CONTENT_STRUCTURE_BEHAVIOR: PASS"
    )

    print(
        "U8.23_H1_CONTRACT: PASS"
    )

    print(
        "U8.23_PARAGRAPH_STRUCTURE: PASS"
    )

    print(
        "U8.23_HEADING_MAP: PASS"
    )

    print(
        "U8.23_DOCUMENT_ORDER: PASS"
    )

    print(
        "U8.23_STRUCTURAL_SUMMARY: PASS"
    )

    print(
        "U8.23_EXTRACTION_PROVENANCE: PASS"
    )

    print(
        "U8.23_NORMALIZATION_PROVENANCE: PASS"
    )

    print(
        "U8.23_PERSISTENCE_ROUND_TRIP: PASS"
    )

    print(
        "U8.23_FAILURE_CONTRACT: PASS"
    )

    print(
        "U8.23_INPUT_MUTATION: NO"
    )

    print(
        "U8.23_SOURCE_REREAD: NO"
    )

    print(
        "U8.23_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.23_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.23_DOWNSTREAM_EXECUTION: NO"
    )

    print(
        "U8.23_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.24_BUILD_INTEGRATION_VERIFICATION_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.23_FINAL_BEHAVIORAL_VERIFICATION: PASS"
    )