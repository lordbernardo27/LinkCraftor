from pathlib import Path
import py_compile
import uuid

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    _safe_document_id,
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
        source_path="C:/immutable/u8_12.txt",
        source_type="txt",
        title="Document Identity",
        text="Alpha beta",
        headings=[],
        metadata={
            "doc_id": "metadata_doc_id_must_not_win",
            "document_id": "metadata_document_id_must_not_win",
            "source_metadata": {
                "doc_id": "source_doc_id_must_not_win",
                "document_id": "source_document_id_must_not_win",
            },
            "filename": "u8_12.txt",
            "extension": ".txt",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        extraction_created_at="2026-09-01T00:00:00+00:00",
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at="2026-09-01T00:00:01+00:00",
    )


print("=== U8.12 DOCUMENT IDENTITY REGRESSION VERIFICATION ===")


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
# B. Valid canonical document ID
# ------------------------------------------------------------

print()
print("=== B. VALID DOCUMENT ID ===")

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="doc_alpha",
    original_filename="u8_12.txt",
)

check(
    "VALID_DOCUMENT_ID_PRESERVED",
    uduc.document_id == "doc_alpha",
)

check(
    "SERIALIZED_DOCUMENT_ID_PRESERVED",
    serialize_uduc(uduc)["document_id"]
    == "doc_alpha",
)


# ------------------------------------------------------------
# C. UUID preservation
# ------------------------------------------------------------

print()
print("=== C. UUID PRESERVATION ===")

canonical_uuid = str(
    uuid.uuid4()
)

uuid_uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id=canonical_uuid,
    original_filename="u8_12.txt",
)

check(
    "UUID_DOCUMENT_ID_PRESERVED",
    uuid_uduc.document_id
    == canonical_uuid,
)


# ------------------------------------------------------------
# D. Surrounding whitespace
# ------------------------------------------------------------

print()
print("=== D. SURROUNDING WHITESPACE ===")

safe = _safe_document_id(
    "  doc_alpha  "
)

check(
    "SURROUNDING_WHITESPACE_TRIMMED",
    safe == "doc_alpha",
)


# ------------------------------------------------------------
# E. None / blank rejection
# ------------------------------------------------------------

print()
print("=== E. NONE / BLANK REJECTION ===")

for label, value in [
    ("NONE", None),
    ("EMPTY", ""),
    ("WHITESPACE_ONLY", "   "),
]:
    raised = False

    try:
        _safe_document_id(
            value
        )
    except ValueError:
        raised = True

    check(
        f"{label}_DOCUMENT_ID_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# F. Canonical builder strictness
# ------------------------------------------------------------

print()
print("=== F. BUILDER STRICTNESS ===")

for label, value in [
    ("NONE", None),
    ("EMPTY", ""),
    ("WHITESPACE_ONLY", "   "),
]:
    raised = False

    try:
        build_uduc_from_normalized_content(
            normalized_content=make_normalized(),
            workspace_id="ws_u8_12",
            document_id=value,
            original_filename="u8_12.txt",
        )
    except ValueError:
        raised = True

    check(
        f"BUILDER_{label}_DOCUMENT_ID_REJECTED",
        raised,
    )


# ------------------------------------------------------------
# G. Metadata cannot override canonical identity
# ------------------------------------------------------------

print()
print("=== G. EXTERNAL DOCUMENT AUTHORITY ===")

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id="doc_external",
    original_filename="u8_12.txt",
)

check(
    "EXTERNAL_DOCUMENT_ID_IS_AUTHORITY",
    uduc.document_id
    == "doc_external",
)

for forbidden_value in [
    "metadata_doc_id_must_not_win",
    "metadata_document_id_must_not_win",
    "source_doc_id_must_not_win",
    "source_document_id_must_not_win",
]:
    check(
        "DOCUMENT_ID_NOT_METADATA_FALLBACK_"
        + forbidden_value.upper(),
        uduc.document_id
        != forbidden_value,
    )


# ------------------------------------------------------------
# H. Path safety
# ------------------------------------------------------------

print()
print("=== H. PATH SAFETY ===")

unsafe_input = "../doc:alpha/beta"

safe_document = _safe_document_id(
    unsafe_input
)

check(
    "PATH_SENSITIVE_DOCUMENT_NONEMPTY",
    bool(safe_document),
)

check(
    "PATH_SENSITIVE_NO_PARENT_TRAVERSAL",
    ".." not in safe_document,
)

check(
    "PATH_SENSITIVE_NO_FORWARD_SLASH",
    "/" not in safe_document,
)

check(
    "PATH_SENSITIVE_NO_BACKSLASH",
    "\\" not in safe_document,
)

uduc = build_uduc_from_normalized_content(
    normalized_content=make_normalized(),
    workspace_id="ws_u8_12",
    document_id=unsafe_input,
    original_filename="u8_12.txt",
)

output_path = Path(
    uduc_output_path(
        uduc.workspace_id,
        uduc.document_id,
    )
)

check(
    "OUTPUT_PATH_CONTAINS_WORKSPACE",
    uduc.workspace_id
    in output_path.parts,
)

check(
    "OUTPUT_FILENAME_MATCHES_DOCUMENT_ID",
    output_path.name
    == f"{uduc.document_id}.json",
)

check(
    "OUTPUT_PATH_NO_PARENT_COMPONENT",
    ".." not in output_path.parts,
)


# ------------------------------------------------------------
# I. Determinism
# ------------------------------------------------------------

print()
print("=== I. DETERMINISM ===")

first = _safe_document_id(
    "../doc:alpha/beta"
)

second = _safe_document_id(
    "../doc:alpha/beta"
)

check(
    "DOCUMENT_SANITIZATION_DETERMINISTIC",
    first == second,
)


# ------------------------------------------------------------
# J. Legacy fallback absence
# ------------------------------------------------------------

print()
print("=== J. LEGACY FALLBACK ABSENCE ===")

source = path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

for forbidden in [
    "unknown_document",
    "inferred_document_id",
    'src_meta.get("doc_id")',
    'src_meta.get("document_id")',
    'meta.get("doc_id")',
    'meta.get("document_id")',
]:
    check(
        "LEGACY_ABSENT_"
        + forbidden.upper()
        .replace('"', "")
        .replace("(", "_")
        .replace(")", "_")
        .replace(".", "_"),
        forbidden not in source,
    )

check(
    "STRICT_NONE_DOCUMENT_GUARD_PRESENT",
    "document_id is None"
    in source,
)

check(
    "STRICT_BLANK_DOCUMENT_GUARD_PRESENT",
    "document_id must be non-blank."
    in source,
)


# ------------------------------------------------------------
# K. No UUID generation inside UDUC builder
# ------------------------------------------------------------

print()
print("=== K. NO ID GENERATION INSIDE UDUC ===")

check(
    "NO_UUID4_GENERATION_IN_UDUC_MODULE",
    "uuid.uuid4"
    not in source
    and "uuid4("
    not in source,
)


# ------------------------------------------------------------
# L. Final certification
# ------------------------------------------------------------

print()
print("=== L. U8.12 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.12_DOCUMENT_IDENTITY_CONTRACT: FAIL"
    )

    print(
        "FAILED_CHECKS:"
    )

    for failure in failures:
        print(
            f" - {failure}"
        )

    raise RuntimeError(
        "U8.12 document identity regression verification failed."
    )

print(
    "U8.12_DOCUMENT_IDENTITY_CONTRACT: CERTIFIED"
)

print(
    "U8.12_DOCUMENT_AUTHORITY: EXTERNAL_PIPELINE_INPUT"
)

print(
    "U8.12_CANONICAL_ID_PROPAGATION: PRESERVED"
)

print(
    "U8.12_METADATA_DOCUMENT_FALLBACK: REMOVED"
)

print(
    "U8.12_SOURCE_METADATA_DOCUMENT_FALLBACK: REMOVED"
)

print(
    "U8.12_UNKNOWN_DOCUMENT_FALLBACK: REMOVED"
)

print(
    "U8.12_NONE_DOCUMENT_ID: REJECTED"
)

print(
    "U8.12_BLANK_DOCUMENT_ID: REJECTED"
)

print(
    "U8.12_UUID_GENERATION_INSIDE_UDUC: NO"
)

print(
    "U8.12_PATH_SAFETY: PRESERVED"
)

print(
    "U8.12_DETERMINISTIC: YES"
)

print(
    "U8.12_PRODUCTION_PATCH_OUTSTANDING: NO"
)

print(
    "U8.13_SOURCE_METADATA_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U8.12_FINAL_DOCUMENT_IDENTITY_REGRESSION_VERIFICATION: PASS"
)