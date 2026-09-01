from pathlib import Path
import py_compile

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


def make_normalized():
    return NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u8_11.txt",
        source_type="txt",
        title="Workspace",
        text="Alpha beta",
        headings=[],
        metadata={
            "workspace_id": "metadata_must_not_win",
            "filename": "u8_11.txt",
            "extension": ".txt",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-08-31T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-08-31T00:00:01+00:00",
    )


print("=== U8.11 WORKSPACE IDENTITY REGRESSION VERIFICATION ===")


# ------------------------------------------------------------
# A. Compile
# ------------------------------------------------------------

print()
print("=== A. COMPILE ===")

path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

compile_ok = True

try:
    py_compile.compile(
        str(path),
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
# B. Valid identity
# ------------------------------------------------------------

print()
print("=== B. VALID WORKSPACE ID ===")

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_alpha",
    document_id="doc_u8_11",
    original_filename="u8_11.txt",
)

check(
    "VALID_WORKSPACE_ID_PRESERVED",
    uduc.workspace_id == "ws_alpha",
)

check(
    "SERIALIZED_WORKSPACE_ID_PRESERVED",
    serialize_uduc(uduc)["workspace_id"]
    == "ws_alpha",
)


# ------------------------------------------------------------
# C. Surrounding whitespace
# ------------------------------------------------------------

print()
print("=== C. SURROUNDING WHITESPACE ===")

ws = _safe_workspace_id(
    "  ws_alpha  "
)

check(
    "SURROUNDING_WHITESPACE_TRIMMED",
    ws == "ws_alpha",
)


# ------------------------------------------------------------
# D. None / blank rejection
# ------------------------------------------------------------

print()
print("=== D. NONE / BLANK REJECTION ===")

for label, value in [
    ("NONE", None),
    ("EMPTY", ""),
    ("WHITESPACE_ONLY", "   "),
]:
    raised = False

    try:
        _safe_workspace_id(
            value
        )
    except ValueError:
        raised = True

    check(
        f"{label}_WORKSPACE_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# E. Canonical builder rejects missing workspace
# ------------------------------------------------------------

print()
print("=== E. BUILDER STRICTNESS ===")

for label, value in [
    ("NONE", None),
    ("EMPTY", ""),
    ("WHITESPACE_ONLY", "   "),
]:
    raised = False

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id=value,
            document_id=f"doc_{label.lower()}",
            original_filename="u8_11.txt",
        )
    except ValueError:
        raised = True

    check(
        f"BUILDER_{label}_WORKSPACE_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# F. Metadata cannot override external identity
# ------------------------------------------------------------

print()
print("=== F. EXTERNAL AUTHORITY ===")

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_external",
    document_id="doc_external",
    original_filename="u8_11.txt",
)

check(
    "EXTERNAL_WORKSPACE_IS_AUTHORITY",
    uduc.workspace_id == "ws_external",
)

check(
    "METADATA_WORKSPACE_CANNOT_OVERRIDE",
    uduc.workspace_id
    != "metadata_must_not_win",
)


# ------------------------------------------------------------
# G. Path safety
# ------------------------------------------------------------

print()
print("=== G. PATH SAFETY ===")

unsafe_input = "../ws:alpha/beta"

safe = _safe_workspace_id(
    unsafe_input
)

check(
    "PATH_SENSITIVE_WORKSPACE_NONEMPTY",
    bool(safe),
)

check(
    "PATH_SENSITIVE_NO_PARENT_TRAVERSAL",
    ".." not in safe,
)

check(
    "PATH_SENSITIVE_NO_FORWARD_SLASH",
    "/" not in safe,
)

check(
    "PATH_SENSITIVE_NO_BACKSLASH",
    "\\" not in safe,
)

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id=unsafe_input,
    document_id="doc_safe_path",
    original_filename="u8_11.txt",
)

output_path = Path(
    uduc_output_path(
        uduc.workspace_id,
        uduc.document_id,
    )
)

check(
    "PERSISTENCE_PATH_CONTAINS_SAFE_WORKSPACE",
    uduc.workspace_id
    in output_path.parts,
)

check(
    "PERSISTENCE_PATH_NO_PARENT_COMPONENT",
    ".." not in output_path.parts,
)


# ------------------------------------------------------------
# H. Determinism
# ------------------------------------------------------------

print()
print("=== H. DETERMINISM ===")

first = _safe_workspace_id(
    "../ws:alpha/beta"
)

second = _safe_workspace_id(
    "../ws:alpha/beta"
)

check(
    "WORKSPACE_SANITIZATION_DETERMINISTIC",
    first == second,
)


# ------------------------------------------------------------
# I. Static legacy fallback absence
# ------------------------------------------------------------

print()
print("=== I. LEGACY FALLBACK ABSENCE ===")

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

check(
    "LEGACY_DEFAULT_OR_EXPRESSION_ABSENT",
    'workspace_id or "default"'
    not in source,
)

check(
    "LEGACY_RAW_DEFAULT_ASSIGNMENT_ABSENT",
    'raw = "default"'
    not in source,
)

check(
    "STRICT_NONE_GUARD_PRESENT",
    "workspace_id is None"
    in source,
)

check(
    "STRICT_BLANK_GUARD_PRESENT",
    "workspace_id must be non-blank."
    in source,
)


# ------------------------------------------------------------
# J. Final certification
# ------------------------------------------------------------

print()
print("=== J. U8.11 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.11_WORKSPACE_IDENTITY_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.11 regression verification failed."
    )

print(
    "U8.11_WORKSPACE_IDENTITY_CONTRACT: CERTIFIED"
)

print(
    "U8.11_WORKSPACE_AUTHORITY: EXTERNAL_PIPELINE_INPUT"
)

print(
    "U8.11_SILENT_DEFAULT_WORKSPACE: REMOVED"
)

print(
    "U8.11_NONE_WORKSPACE: REJECTED"
)

print(
    "U8.11_BLANK_WORKSPACE: REJECTED"
)

print(
    "U8.11_METADATA_OVERRIDE: NO"
)

print(
    "U8.11_PATH_SAFETY: PRESERVED"
)

print(
    "U8.11_DETERMINISTIC: YES"
)

print(
    "U8.11_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.12_DOCUMENT_IDENTITY_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.11_FINAL_WORKSPACE_IDENTITY_REGRESSION_VERIFICATION: PASS"
)