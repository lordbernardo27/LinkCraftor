from pathlib import Path
import ast
import tempfile

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    _safe_workspace_id,
    build_uduc_from_normalized_content,
    serialize_uduc,
    uduc_output_path,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_normalized() -> NormalizedUploadedDocumentContent:
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/workspace-test.txt",
        source_type="txt",
        title="Workspace Test",
        text="Alpha beta",
        headings=[],
        metadata={
            "workspace_id": "metadata_workspace_should_not_win",
            "filename": "workspace-test.txt",
            "extension": ".txt",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-08-31T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-08-31T00:00:01+00:00",
    )


print("=== U8.11 WORKSPACE IDENTITY VERIFICATION ===")


# ------------------------------------------------------------
# A. Inspect _safe_workspace_id behavior
# ------------------------------------------------------------

print()
print("=== A. SAFE WORKSPACE ID BEHAVIOR ===")

cases = [
    ("valid", "ws_alpha"),
    ("surrounding_whitespace", "  ws_alpha  "),
    ("path_sensitive", "../ws:alpha/beta"),
    ("empty", ""),
    ("whitespace_only", "   "),
    ("none", None),
]

for label, value in cases:
    try:
        result = _safe_workspace_id(value)
        print(
            f"{label}: INPUT={value!r} OUTPUT={result!r}"
        )
    except Exception as exc:
        print(
            f"{label}: INPUT={value!r} "
            f"ERROR={type(exc).__name__}: {exc}"
        )


# ------------------------------------------------------------
# B. Valid external workspace identity
# ------------------------------------------------------------

print()
print("=== B. VALID EXTERNAL WORKSPACE ID ===")

normalized = make_normalized()

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_alpha",
    document_id="doc_u8_11",
    original_filename="workspace-test.txt",
)

check(
    "VALID_WORKSPACE_ID_PRESERVED",
    uduc.workspace_id == "ws_alpha",
)

serialized = serialize_uduc(
    uduc
)

check(
    "SERIALIZED_WORKSPACE_ID_MATCHES_UDUC",
    serialized["workspace_id"]
    == uduc.workspace_id,
)


# ------------------------------------------------------------
# C. Metadata must not override external workspace
# ------------------------------------------------------------

print()
print("=== C. EXTERNAL AUTHORITY OVER METADATA ===")

check(
    "METADATA_WORKSPACE_DOES_NOT_OVERRIDE_EXTERNAL",
    uduc.workspace_id
    != normalized.metadata.get(
        "workspace_id"
    ),
)

check(
    "EXTERNAL_WORKSPACE_REMAINS_AUTHORITY",
    uduc.workspace_id
    == "ws_alpha",
)


# ------------------------------------------------------------
# D. Surrounding whitespace behavior
# ------------------------------------------------------------

print()
print("=== D. SURROUNDING WHITESPACE ===")

whitespace_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="  ws_alpha  ",
    document_id="doc_ws_space",
    original_filename="workspace-test.txt",
)

print(
    "SURROUNDING_WHITESPACE_RESULT="
    f"{whitespace_uduc.workspace_id!r}"
)

check(
    "SURROUNDING_WHITESPACE_NOT_DEFAULTED",
    whitespace_uduc.workspace_id
    != "default",
)


# ------------------------------------------------------------
# E. Path-sensitive characters
# ------------------------------------------------------------

print()
print("=== E. PATH-SENSITIVE WORKSPACE ID ===")

unsafe_input = "../ws:alpha/beta"

unsafe_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id=unsafe_input,
    document_id="doc_ws_unsafe",
    original_filename="workspace-test.txt",
)

print(
    "PATH_SENSITIVE_INPUT="
    f"{unsafe_input!r}"
)

print(
    "PATH_SENSITIVE_OUTPUT="
    f"{unsafe_uduc.workspace_id!r}"
)

check(
    "PATH_SENSITIVE_OUTPUT_NONEMPTY",
    bool(
        unsafe_uduc.workspace_id
    ),
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_PARENT_TRAVERSAL",
    ".." not in unsafe_uduc.workspace_id,
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_SLASH",
    "/" not in unsafe_uduc.workspace_id,
)

check(
    "PATH_SENSITIVE_OUTPUT_HAS_NO_BACKSLASH",
    "\\" not in unsafe_uduc.workspace_id,
)


# ------------------------------------------------------------
# F. Persistence path containment
# ------------------------------------------------------------

print()
print("=== F. PERSISTENCE PATH SAFETY ===")

path_value = uduc_output_path(
    unsafe_uduc.workspace_id,
    unsafe_uduc.document_id,
)

path_obj = Path(path_value)

print(
    f"UDUC_OUTPUT_PATH={path_obj}"
)

check(
    "OUTPUT_PATH_CONTAINS_SANITIZED_WORKSPACE_COMPONENT",
    unsafe_uduc.workspace_id
    in path_obj.parts,
)

check(
    "OUTPUT_PATH_HAS_NO_PARENT_COMPONENT",
    ".." not in path_obj.parts,
)


# ------------------------------------------------------------
# G. Blank/None workspace behavior
# ------------------------------------------------------------

print()
print("=== G. BLANK / NONE WORKSPACE BEHAVIOR ===")

blank_results = {}

for label, value in [
    ("empty", ""),
    ("whitespace_only", "   "),
    ("none", None),
]:
    try:
        candidate = build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id=value,
            document_id=f"doc_{label}",
            original_filename="workspace-test.txt",
        )

        blank_results[label] = (
            "returned",
            candidate.workspace_id,
        )

        print(
            f"{label}: RETURNED "
            f"{candidate.workspace_id!r}"
        )

    except Exception as exc:
        blank_results[label] = (
            "raised",
            type(exc).__name__,
        )

        print(
            f"{label}: RAISED "
            f"{type(exc).__name__}: {exc}"
        )


# We do NOT assume strict rejection yet.
# We only expose whether silent "default" invention remains.
silent_default_cases = [
    label
    for label, outcome in blank_results.items()
    if (
        outcome[0] == "returned"
        and outcome[1] == "default"
    )
]

check(
    "BLANK_WORKSPACE_SILENT_DEFAULT_ABSENT",
    len(silent_default_cases) == 0,
)


# ------------------------------------------------------------
# H. Determinism
# ------------------------------------------------------------

print()
print("=== H. DETERMINISM ===")

first = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_deterministic",
    document_id="doc_det_a",
    original_filename="workspace-test.txt",
)

second = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_deterministic",
    document_id="doc_det_b",
    original_filename="workspace-test.txt",
)

check(
    "WORKSPACE_ID_DETERMINISTIC",
    first.workspace_id
    == second.workspace_id
    == "ws_deterministic",
)


# ------------------------------------------------------------
# I. Static authority inspection
# ------------------------------------------------------------

print()
print("=== I. STATIC WORKSPACE AUTHORITY INSPECTION ===")

module_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = module_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(source)

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

safe_fn = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "_safe_workspace_id"
)

safe_source = (
    ast.get_source_segment(
        source,
        safe_fn,
    )
    or ""
)

print()
print("--- _safe_workspace_id ---")
print(safe_source)

print()
print("--- WORKSPACE REFERENCES IN CANONICAL BUILDER ---")

for line in builder_source.splitlines():
    if "workspace" in line.lower():
        print(line)


check(
    "BUILDER_DOES_NOT_READ_METADATA_WORKSPACE_ID",
    'meta.get("workspace_id")'
    not in builder_source
    and "src_meta.get(\"workspace_id\")"
    not in builder_source,
)

check(
    "SAFE_WORKSPACE_FUNCTION_PRESENT",
    bool(safe_source),
)

check(
    "DEFAULT_LITERAL_PRESENT_IN_SAFE_WORKSPACE",
    '"default"' in safe_source
    or "'default'" in safe_source,
)


# ------------------------------------------------------------
# J. Downstream boundary
# ------------------------------------------------------------

print()
print("=== J. DOWNSTREAM BOUNDARY ===")

forbidden = [
    "run_highlight",
    "active_target_set",
    "run_semantic",
    "semantic_runtime",
    "build_uucd",
    "write_uucd",
    "current_canonical_uucd",
]

for marker in forbidden:
    check(
        "BUILDER_NO_"
        + marker.upper(),
        marker.lower()
        not in builder_source.lower(),
    )


# ------------------------------------------------------------
# K. Final decision
# ------------------------------------------------------------

print()
print("=== K. U8.11 FINAL DECISION ===")

hard_failures = [
    name
    for name, status in results
    if (
        status != "PASS"
        and name
        != "BLANK_WORKSPACE_SILENT_DEFAULT_ABSENT"
    )
]

if hard_failures:
    print(
        "U8.11_WORKSPACE_IDENTITY_CONTRACT: FAIL"
    )

    print(
        "HARD_FAILED_CHECKS:"
    )

    for failure in hard_failures:
        print(
            f" - {failure}"
        )

elif silent_default_cases:
    print(
        "U8.11_WORKSPACE_IDENTITY_CONTRACT: REVIEW_REQUIRED"
    )

    print(
        "U8.11_SILENT_DEFAULT_WORKSPACE_CASES:"
        + ",".join(silent_default_cases)
    )

    print(
        "U8.11_PRIMARY_DECISION:"
        " REMOVE_SILENT_DEFAULT_AND_REQUIRE_EXTERNAL_WORKSPACE_ID"
    )

    print(
        "U8.11_PATCH_DECISION_REQUIRED: YES"
    )

else:
    print(
        "U8.11_WORKSPACE_IDENTITY_CONTRACT: CERTIFIED"
    )

    print(
        "U8.11_WORKSPACE_AUTHORITY: EXTERNAL_PIPELINE_INPUT"
    )

    print(
        "U8.11_METADATA_OVERRIDE: NO"
    )

    print(
        "U8.11_SILENT_DEFAULT_WORKSPACE: NO"
    )

    print(
        "U8.11_PATH_SAFETY: PASS"
    )

    print(
        "U8.11_DETERMINISTIC: YES"
    )

    print(
        "U8.11_PRODUCTION_PATCH_REQUIRED: NO"
    )

    print(
        "U8.12_DOCUMENT_IDENTITY_CONTRACT_TRANSITION: AUTHORIZED"
    )

    print(
        "U8.11_FINAL_WORKSPACE_IDENTITY_VERIFICATION: PASS"
    )