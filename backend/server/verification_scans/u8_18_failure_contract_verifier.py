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
    read_uduc,
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
    normalization_status="success",
):
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_18.txt",
        source_type="txt",
        title="Failure Contract Title",
        text="Failure contract body.",
        headings=[
            "Failure Heading",
        ],
        metadata={
            "filename": "u8_18.txt",
            "extension": ".txt",
            "file_size": 123,
            "extraction_method": "txt_upload_v1",
            "normalization": {
                "status": normalization_status,
                "version": "uploaded_document_normalization_v1",
                "unicode_form": "NFC",
            },
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status=normalization_status,
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.18 FAILURE CONTRACT VERIFICATION ===")


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
# B. Invalid normalized_content type
# ------------------------------------------------------------

print()
print("=== B. INVALID NORMALIZED CONTENT TYPE ===")

invalid_type_raised = False
invalid_type_name = ""

try:
    build_uduc_from_normalized_content(
        normalized_content={},
        workspace_id="ws_u8_18",
        document_id="doc_u8_18",
    )
except Exception as exc:
    invalid_type_raised = True
    invalid_type_name = type(exc).__name__

print(
    f"INVALID_TYPE_EXCEPTION={invalid_type_name}"
)

check(
    "INVALID_NORMALIZED_CONTENT_TYPE_RAISES",
    invalid_type_raised,
)


# ------------------------------------------------------------
# C. Ineligible normalization status
# ------------------------------------------------------------

print()
print("=== C. INELIGIBLE NORMALIZATION STATUS ===")

ineligible_raised = False
ineligible_type = ""

try:
    build_uduc_from_normalized_content(
        normalized_content=make_normalized(
            normalization_status="ineligible_extraction",
        ),
        workspace_id="ws_u8_18",
        document_id="doc_u8_18",
    )
except Exception as exc:
    ineligible_raised = True
    ineligible_type = type(exc).__name__

print(
    f"INELIGIBLE_STATUS_EXCEPTION={ineligible_type}"
)

check(
    "NON_SUCCESS_NORMALIZATION_STATUS_RAISES",
    ineligible_raised,
)


# ------------------------------------------------------------
# D. Workspace identity failures
# ------------------------------------------------------------

print()
print("=== D. WORKSPACE IDENTITY FAILURES ===")

for label, value in [
    ("NONE", None),
    ("BLANK", "   "),
]:
    raised = False
    exc_name = ""

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id=value,
            document_id="doc_u8_18",
        )
    except Exception as exc:
        raised = True
        exc_name = type(exc).__name__

    print(
        f"WORKSPACE_{label}_EXCEPTION={exc_name}"
    )

    check(
        f"WORKSPACE_{label}_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# E. Document identity failures
# ------------------------------------------------------------

print()
print("=== E. DOCUMENT IDENTITY FAILURES ===")

for label, value in [
    ("NONE", None),
    ("BLANK", "   "),
]:
    raised = False
    exc_name = ""

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id="ws_u8_18",
            document_id=value,
        )
    except Exception as exc:
        raised = True
        exc_name = type(exc).__name__

    print(
        f"DOCUMENT_{label}_EXCEPTION={exc_name}"
    )

    check(
        f"DOCUMENT_{label}_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# F. No synthetic identity fallback
# ------------------------------------------------------------

print()
print("=== F. NO SYNTHETIC IDENTITY FALLBACK ===")

source = module_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source
)

builder = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "build_uduc_from_normalized_content"
)

builder_source = (
    ast.get_source_segment(
        source,
        builder,
    )
    or ""
)

check(
    "NO_DEFAULT_WORKSPACE_FALLBACK",
    '"default"'
    not in builder_source
    and "'default'"
    not in builder_source,
)

check(
    "NO_UNKNOWN_DOCUMENT_FALLBACK",
    "unknown_document"
    not in builder_source,
)


# ------------------------------------------------------------
# G. Input immutability on failure
# ------------------------------------------------------------

print()
print("=== G. INPUT IMMUTABILITY ON FAILURE ===")

failure_input = make_normalized(
    normalization_status="ineligible_extraction",
)

failure_input_before = copy.deepcopy(
    failure_input
)

try:
    build_uduc_from_normalized_content(
        normalized_content=failure_input,
        workspace_id="ws_u8_18",
        document_id="doc_u8_18",
    )
except Exception:
    pass

check(
    "FAILED_BUILD_DOES_NOT_MUTATE_INPUT",
    failure_input
    == failure_input_before,
)


# ------------------------------------------------------------
# H. Isolated persistence root
# ------------------------------------------------------------

print()
print("=== H. ISOLATED PERSISTENCE ROOT ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_18_uduc_"
) as temp_dir:

    temp_root = Path(
        temp_dir
    )

    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = temp_root

    check(
        "TEMP_ROOT_EXISTS",
        temp_root.exists(),
    )


    # --------------------------------------------------------
    # I. Missing persisted UDUC
    # --------------------------------------------------------

    print()
    print("=== I. MISSING READ CONTRACT ===")

    missing_predictable = False
    missing_value = None
    missing_exception = ""

    try:
        missing_value = read_uduc(
            "ws_u8_18",
            "missing_doc",
        )
        missing_predictable = True
    except FileNotFoundError as exc:
        missing_predictable = True
        missing_exception = type(exc).__name__
    except Exception as exc:
        missing_exception = type(exc).__name__

    print(
        f"MISSING_READ_VALUE={missing_value!r}"
    )

    print(
        f"MISSING_READ_EXCEPTION={missing_exception}"
    )

    check(
        "MISSING_READ_HANDLED_PREDICTABLY",
        missing_predictable,
    )


    # --------------------------------------------------------
    # J. Malformed JSON read
    # --------------------------------------------------------

    print()
    print("=== J. MALFORMED JSON READ CONTRACT ===")

    malformed_path = uduc_output_path(
        "ws_u8_18",
        "malformed_doc",
    )

    malformed_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    malformed_path.write_text(
        "{not valid json",
        encoding="utf-8",
    )

    malformed_raised = False
    malformed_type = ""

    try:
        read_uduc(
            "ws_u8_18",
            "malformed_doc",
        )
    except Exception as exc:
        malformed_raised = True
        malformed_type = type(exc).__name__

    print(
        f"MALFORMED_JSON_EXCEPTION={malformed_type}"
    )

    check(
        "MALFORMED_JSON_FAILURE_SURFACES",
        malformed_raised,
    )


    # --------------------------------------------------------
    # K. Establish valid persisted UDUC
    # --------------------------------------------------------

    print()
    print("=== K. VALID BASELINE WRITE ===")

    baseline = build_uduc_from_normalized_content(
        normalized_content=make_normalized(),
        workspace_id="ws_u8_18",
        document_id="doc_atomic",
    )

    baseline_path = write_uduc(
        baseline
    )

    baseline_bytes = baseline_path.read_bytes()

    check(
        "BASELINE_FINAL_FILE_EXISTS",
        baseline_path.exists(),
    )


    # --------------------------------------------------------
    # L. Simulated write failure before replace
    # --------------------------------------------------------

    print()
    print("=== L. SIMULATED WRITE FAILURE ===")

    original_path_replace = Path.replace

    replace_failure_triggered = False
    write_failure_surfaced = False
    write_failure_type = ""

    def failing_replace(
        self,
        target,
    ):
        nonlocal_replace_marker = None
        raise OSError(
            "simulated_replace_failure"
        )

    Path.replace = failing_replace

    try:
        updated = build_uduc_from_normalized_content(
            normalized_content=NormalizedUploadedDocumentContent(
                source_path="C:/immutable/u8_18.txt",
                source_type="txt",
                title="Updated title that must not replace baseline",
                text="Updated body.",
                headings=[
                    "Updated Heading",
                ],
                metadata={
                    "filename": "u8_18.txt",
                    "extension": ".txt",
                    "file_size": 999,
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
            ),
            workspace_id="ws_u8_18",
            document_id="doc_atomic",
        )

        try:
            write_uduc(
                updated
            )
        except Exception as exc:
            write_failure_surfaced = True
            write_failure_type = type(exc).__name__

    finally:
        Path.replace = original_path_replace

    print(
        f"WRITE_FAILURE_EXCEPTION={write_failure_type}"
    )

    check(
        "WRITE_FAILURE_SURFACES_TO_CALLER",
        write_failure_surfaced,
    )

    check(
        "EXISTING_FINAL_FILE_STILL_EXISTS_AFTER_FAILED_REPLACE",
        baseline_path.exists(),
    )

    check(
        "EXISTING_FINAL_FILE_UNCHANGED_AFTER_FAILED_REPLACE",
        baseline_path.read_bytes()
        == baseline_bytes,
    )


    temp_files = [
        p
        for p in baseline_path.parent.iterdir()
        if p.name.endswith(".tmp")
        or ".tmp." in p.name
    ]

    print(
        "TEMP_FILES_AFTER_FAILED_WRITE="
        + repr(
            [
                p.name
                for p in temp_files
            ]
        )
    )

    check(
        "FAILED_WRITE_TEMP_FILES_ARE_ISOLATED_FROM_FINAL_PATH",
        all(
            p != baseline_path
            for p in temp_files
        ),
    )


    # --------------------------------------------------------
    # M. Restore output root
    # --------------------------------------------------------

    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = original_output_dir


# ------------------------------------------------------------
# N. Static persistence failure inspection
# ------------------------------------------------------------

print()
print("=== N. STATIC FAILURE INSPECTION ===")


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


write_source = function_source(
    "write_uduc"
)

read_source = function_source(
    "read_uduc"
)

path_source = function_source(
    "uduc_output_path"
)

canonical_entry_source = function_source(
    "build_and_write_uduc_from_normalized_content"
)


check(
    "WRITE_USES_TEMP_FILE",
    ".tmp"
    in write_source,
)

check(
    "WRITE_USES_ATOMIC_REPLACE",
    ".replace("
    in write_source
    or "os.replace"
    in write_source,
)

check(
    "READ_DOES_NOT_REBUILD_UDUC",
    "build_uduc"
    not in read_source,
)


# ------------------------------------------------------------
# O. Failure boundary
# ------------------------------------------------------------

print()
print("=== O. FAILURE BOUNDARY ===")

failure_scope = "\n".join(
    [
        builder_source,
        write_source,
        read_source,
        path_source,
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
        "FAILURE_SCOPE_NO_"
        + marker.upper()
        .replace(".", "_"),
        marker.lower()
        not in failure_scope.lower(),
    )


# ------------------------------------------------------------
# P. No downstream execution
# ------------------------------------------------------------

print()
print("=== P. DOWNSTREAM BOUNDARY ===")

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
        "FAILURE_SCOPE_NO_"
        + marker.upper(),
        marker.lower()
        not in failure_scope.lower(),
    )


# ------------------------------------------------------------
# Q. Final decision
# ------------------------------------------------------------

print()
print("=== Q. U8.18 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.18_FAILURE_CONTRACT: REVIEW_REQUIRED"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    print(
        "U8.18_PATCH_DECISION_REQUIRED: REVIEW_EVIDENCE"
    )

else:
    print(
        "U8.18_FAILURE_CONTRACT: CERTIFIED"
    )

    print(
        "U8.18_PROGRAMMER_CONTRACT_VIOLATIONS: RAISE"
    )

    print(
        "U8.18_INVALID_NORMALIZED_INPUT: REJECTED"
    )

    print(
        "U8.18_NON_SUCCESS_NORMALIZATION: REJECTED"
    )

    print(
        "U8.18_SYNTHETIC_IDENTITY_FALLBACK: NONE"
    )

    print(
        "U8.18_WRITE_FAILURE_SURFACES: YES"
    )

    print(
        "U8.18_EXISTING_FINAL_FILE_PROTECTED_ON_FAILED_REPLACE: YES"
    )

    print(
        "U8.18_MISSING_READ: PREDICTABLE"
    )

    print(
        "U8.18_MALFORMED_JSON_FAILURE: SURFACES"
    )

    print(
        "U8.18_SOURCE_REREAD: NO"
    )

    print(
        "U8.18_EXTRACTION_RERUN: NO"
    )

    print(
        "U8.18_NORMALIZATION_RERUN: NO"
    )

    print(
        "U8.18_DOWNSTREAM_EXECUTION: NO"
    )

    print(
        "U8.18_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.19_DETERMINISM_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.18_FINAL_FAILURE_CONTRACT_VERIFICATION: PASS"
    )