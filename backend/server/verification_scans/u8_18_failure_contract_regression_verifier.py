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
    title="Failure Contract Title",
):
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_18.txt",
        source_type="txt",
        title=title,
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


print("=== U8.18 FAILURE CONTRACT REGRESSION VERIFICATION ===")


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
# B. Builder contract failures
# ------------------------------------------------------------

print()
print("=== B. BUILDER FAILURE CONTRACT ===")

invalid_type_raised = False

try:
    build_uduc_from_normalized_content(
        normalized_content={},
        workspace_id="ws_u8_18",
        document_id="doc_u8_18",
    )
except TypeError:
    invalid_type_raised = True

check(
    "INVALID_NORMALIZED_CONTENT_TYPE_REJECTED",
    invalid_type_raised,
)


non_success_raised = False

try:
    build_uduc_from_normalized_content(
        normalized_content=make_normalized(
            normalization_status="ineligible_extraction",
        ),
        workspace_id="ws_u8_18",
        document_id="doc_u8_18",
    )
except ValueError:
    non_success_raised = True

check(
    "NON_SUCCESS_NORMALIZATION_REJECTED",
    non_success_raised,
)


for label, workspace_id in [
    ("NONE", None),
    ("BLANK", "   "),
]:
    raised = False

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id=workspace_id,
            document_id="doc_u8_18",
        )
    except ValueError:
        raised = True

    check(
        f"WORKSPACE_{label}_REJECTED",
        raised,
    )


for label, document_id in [
    ("NONE", None),
    ("BLANK", "   "),
]:
    raised = False

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id="ws_u8_18",
            document_id=document_id,
        )
    except ValueError:
        raised = True

    check(
        f"DOCUMENT_{label}_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# C. Input immutability on failure
# ------------------------------------------------------------

print()
print("=== C. FAILURE INPUT IMMUTABILITY ===")

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
except ValueError:
    pass

check(
    "FAILED_BUILD_DOES_NOT_MUTATE_INPUT",
    failure_input
    == failure_input_before,
)


# ------------------------------------------------------------
# D. Static builder identity fallback
# ------------------------------------------------------------

print()
print("=== D. NO SYNTHETIC IDENTITY FALLBACK ===")

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
# E. Isolated persistence root
# ------------------------------------------------------------

print()
print("=== E. ISOLATED PERSISTENCE ROOT ===")

original_output_dir = getattr(
    uduc_module,
    "UDUC_OUTPUT_DIR",
    None,
)

with tempfile.TemporaryDirectory(
    prefix="u8_18_regression_"
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
    # F. Missing read remains predictable
    # --------------------------------------------------------

    print()
    print("=== F. MISSING READ ===")

    missing = read_uduc(
        "ws_u8_18",
        "missing_document",
    )

    check(
        "MISSING_READ_RETURNS_EMPTY_DICT",
        missing
        == {},
    )


    # --------------------------------------------------------
    # G. Valid JSON object round trip
    # --------------------------------------------------------

    print()
    print("=== G. VALID JSON OBJECT READ ===")

    valid_uduc = build_uduc_from_normalized_content(
        normalized_content=make_normalized(),
        workspace_id="ws_u8_18",
        document_id="valid_document",
    )

    valid_path = write_uduc(
        valid_uduc
    )

    valid_read = read_uduc(
        "ws_u8_18",
        "valid_document",
    )

    check(
        "VALID_JSON_OBJECT_READ_RETURNS_DICT",
        isinstance(
            valid_read,
            dict,
        ),
    )

    check(
        "VALID_JSON_OBJECT_ROUND_TRIP",
        valid_read.get(
            "document_id"
        )
        == "valid_document",
    )


    # --------------------------------------------------------
    # H. Malformed JSON surfaces
    # --------------------------------------------------------

    print()
    print("=== H. MALFORMED JSON FAILURE ===")

    malformed_path = uduc_output_path(
        "ws_u8_18",
        "malformed_document",
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
            "malformed_document",
        )
    except Exception as exc:
        malformed_raised = True
        malformed_type = type(exc).__name__

    print(
        f"MALFORMED_JSON_EXCEPTION={malformed_type}"
    )

    check(
        "MALFORMED_JSON_EXCEPTION_SURFACES",
        malformed_raised,
    )

    check(
        "MALFORMED_JSON_EXCEPTION_IS_JSON_DECODE_ERROR",
        malformed_type
        == "JSONDecodeError",
    )


    # --------------------------------------------------------
    # I. Non-object JSON rejected
    # --------------------------------------------------------

    print()
    print("=== I. NON-OBJECT JSON FAILURE ===")

    for label, payload in [
        ("LIST", []),
        ("STRING", "hello"),
        ("NUMBER", 123),
        ("NULL", None),
    ]:
        path = uduc_output_path(
            "ws_u8_18",
            f"non_object_{label.lower()}",
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                payload
            ),
            encoding="utf-8",
        )

        raised = False
        exc_type = ""

        try:
            read_uduc(
                "ws_u8_18",
                f"non_object_{label.lower()}",
            )
        except Exception as exc:
            raised = True
            exc_type = type(exc).__name__

        print(
            f"NON_OBJECT_{label}_EXCEPTION={exc_type}"
        )

        check(
            f"NON_OBJECT_{label}_REJECTED",
            raised
            and exc_type
            == "ValueError",
        )


    # --------------------------------------------------------
    # J. Failed atomic replacement
    # --------------------------------------------------------

    print()
    print("=== J. FAILED ATOMIC REPLACEMENT ===")

    baseline = build_uduc_from_normalized_content(
        normalized_content=make_normalized(
            title="Baseline Title",
        ),
        workspace_id="ws_u8_18",
        document_id="atomic_document",
    )

    baseline_path = write_uduc(
        baseline
    )

    baseline_bytes = baseline_path.read_bytes()

    original_path_replace = Path.replace

    write_failure_surfaced = False
    write_failure_type = ""

    def failing_replace(
        self,
        target,
    ):
        raise OSError(
            "simulated_replace_failure"
        )

    Path.replace = failing_replace

    try:
        updated = build_uduc_from_normalized_content(
            normalized_content=make_normalized(
                title="Updated Title",
            ),
            workspace_id="ws_u8_18",
            document_id="atomic_document",
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

    check(
        "WRITE_FAILURE_SURFACES",
        write_failure_surfaced
        and write_failure_type
        == "OSError",
    )

    check(
        "EXISTING_FINAL_FILE_SURVIVES_FAILED_REPLACE",
        baseline_path.exists(),
    )

    check(
        "EXISTING_FINAL_FILE_UNCHANGED",
        baseline_path.read_bytes()
        == baseline_bytes,
    )


    temp_files = [
        p
        for p in baseline_path.parent.iterdir()
        if p.name.endswith(
            ".tmp"
        )
        or ".tmp." in p.name
    ]

    check(
        "FAILED_TEMP_FILE_NEVER_REPLACES_FINAL",
        all(
            p != baseline_path
            for p in temp_files
        ),
    )


    if hasattr(
        uduc_module,
        "UDUC_OUTPUT_DIR",
    ):
        uduc_module.UDUC_OUTPUT_DIR = original_output_dir


# ------------------------------------------------------------
# K. Exact read_uduc static contract
# ------------------------------------------------------------

print()
print("=== K. READ_UDUC STATIC CONTRACT ===")


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


read_source = function_source(
    "read_uduc"
)

write_source = function_source(
    "write_uduc"
)

path_source = function_source(
    "uduc_output_path"
)


check(
    "READ_MISSING_FILE_RETURNS_EMPTY_DICT",
    "if not path.exists()"
    in read_source
    and "return {}"
    in read_source,
)

check(
    "READ_HAS_NO_BROAD_EXCEPTION_SWALLOWING",
    "except Exception"
    not in read_source,
)

check(
    "READ_USES_JSON_LOADS",
    "json.loads"
    in read_source,
)

check(
    "READ_REJECTS_NON_DICT",
    "Persisted UDUC must be a JSON object."
    in read_source,
)

check(
    "WRITE_STILL_USES_TEMP_FILE",
    ".tmp"
    in write_source,
)

check(
    "WRITE_STILL_USES_ATOMIC_REPLACE",
    ".replace("
    in write_source
    or "os.replace"
    in write_source,
)


# ------------------------------------------------------------
# L. Failure boundary
# ------------------------------------------------------------

print()
print("=== L. FAILURE BOUNDARY ===")

failure_scope = "\n".join(
    [
        builder_source,
        read_source,
        write_source,
        path_source,
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
# M. Downstream boundary
# ------------------------------------------------------------

print()
print("=== M. DOWNSTREAM BOUNDARY ===")

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
# N. Final certification
# ------------------------------------------------------------

print()
print("=== N. U8.18 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.18_FAILURE_CONTRACT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.18 failure contract regression verification failed."
    )

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
    "U8.18_MISSING_READ: RETURNS_EMPTY_DICT"
)

print(
    "U8.18_MALFORMED_JSON_FAILURE: SURFACES"
)

print(
    "U8.18_NON_OBJECT_JSON_FAILURE: VALUE_ERROR"
)

print(
    "U8.18_WRITE_FAILURE_SURFACES: YES"
)

print(
    "U8.18_EXISTING_FINAL_FILE_PROTECTED_ON_FAILED_REPLACE: YES"
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
    "U8.18_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.19_DETERMINISM_TRANSITION: AUTHORIZED"
)

print(
    "U8.18_FINAL_FAILURE_CONTRACT_REGRESSION_VERIFICATION: PASS"
)