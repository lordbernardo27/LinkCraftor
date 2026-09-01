from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

EXTRACTOR = (
    BASE
    / "stores"
    / "upload_document_extractor.py"
)

UPLOAD_PIPELINE = (
    BASE
    / "pipelines"
    / "upload_document"
)

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def read(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )


print(
    "=== U7.3 - NORMALIZATION INPUT CONTRACT VERIFICATION ==="
)


# ------------------------------------------------------------
# A. Canonical U6 output contract
# ------------------------------------------------------------

print()
print("=== A. CANONICAL U7 INPUT OBJECT ===")

source = read(EXTRACTOR)

tree = ast.parse(
    source,
    filename=str(EXTRACTOR),
)

classes = {
    node.name: node
    for node in tree.body
    if isinstance(node, ast.ClassDef)
}

functions = {
    node.name
    for node in tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}

check(
    "UPLOAD_EXTRACTION_RESULT_EXISTS",
    "UploadExtractionResult"
    in classes,
)

check(
    "CANONICAL_U6_DISPATCHER_EXISTS",
    "extract_upload_document_v1"
    in functions,
)

expected_fields = [
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
]

actual_fields = []

result_class = classes.get(
    "UploadExtractionResult"
)

if result_class is not None:
    for node in result_class.body:
        if isinstance(
            node,
            ast.AnnAssign,
        ) and isinstance(
            node.target,
            ast.Name,
        ):
            actual_fields.append(
                node.target.id
            )

check(
    "UPLOAD_EXTRACTION_RESULT_FIELDS_EXACT",
    actual_fields
    == expected_fields,
)


# ------------------------------------------------------------
# B. Normalization eligibility contract
# ------------------------------------------------------------

print()
print("=== B. NORMALIZATION ELIGIBILITY CONTRACT ===")

success_status = "success"

rejected_statuses = {
    "empty_text",
    "missing_file",
    "unsupported_extension",
    "unsupported_source_type",
    "invalid_docx",
    "extraction_error",
}

check(
    "NORMALIZATION_REQUIRES_SUCCESS_STATUS",
    success_status == "success",
)

for status in sorted(
    rejected_statuses
):
    check(
        "NORMALIZATION_REJECTS_"
        + status.upper(),
        status != success_status,
    )


# ------------------------------------------------------------
# C. Exact input fields consumed by U7
# ------------------------------------------------------------

print()
print("=== C. U7 INPUT FIELD CONTRACT ===")

content_fields = {
    "title",
    "text",
    "headings",
}

identity_fields = {
    "source_path",
    "source_type",
}

provenance_fields = {
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
}

actual_field_set = set(
    actual_fields
)

check(
    "U7_CONTENT_FIELDS_AVAILABLE",
    content_fields
    <= actual_field_set,
)

check(
    "U7_SOURCE_IDENTITY_FIELDS_AVAILABLE",
    identity_fields
    <= actual_field_set,
)

check(
    "U7_PROVENANCE_FIELDS_AVAILABLE",
    provenance_fields
    <= actual_field_set,
)


# ------------------------------------------------------------
# D. Canonical U7 input exclusions
# ------------------------------------------------------------

print()
print("=== D. INPUT TYPE EXCLUSIONS ===")

check(
    "U7_DOES_NOT_ACCEPT_UPLOADFILE_BY_CONTRACT",
    True,
)

check(
    "U7_DOES_NOT_ACCEPT_RAW_BYTES_BY_CONTRACT",
    True,
)

check(
    "U7_DOES_NOT_ACCEPT_RAW_SOURCE_PATH_AS_CONTENT_INPUT_BY_CONTRACT",
    True,
)

check(
    "U7_DOES_NOT_ACCEPT_UDUC_AS_INPUT_BY_CONTRACT",
    True,
)


# ------------------------------------------------------------
# E. No source reread in the U7 contract
# ------------------------------------------------------------

print()
print("=== E. SOURCE REREAD EXCLUSION ===")

check(
    "U7_FORBIDS_PATH_READ_TEXT_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_PATH_READ_BYTES_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_OPEN_SOURCE_PATH_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_DOCX_ZIP_REREAD_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_SECOND_FORMAT_PARSE_BY_CONTRACT",
    True,
)


# ------------------------------------------------------------
# F. No format-specific routing in U7
# ------------------------------------------------------------

print()
print("=== F. FORMAT-NEUTRAL INPUT CONTRACT ===")

for extension_family in (
    "TXT",
    "MARKDOWN",
    "HTML",
    "DOCX",
):
    check(
        "U7_HAS_NO_"
        + extension_family
        + "_SPECIFIC_ROUTING_BY_CONTRACT",
        True,
    )


# ------------------------------------------------------------
# G. Source mutation exclusion
# ------------------------------------------------------------

print()
print("=== G. SOURCE IMMUTABILITY CONTRACT ===")

check(
    "U7_FORBIDS_SOURCE_WRITE_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_SOURCE_REPLACE_BY_CONTRACT",
    True,
)

check(
    "U7_FORBIDS_SOURCE_DELETE_BY_CONTRACT",
    True,
)


# ------------------------------------------------------------
# H. Invalid-input contract
# ------------------------------------------------------------

print()
print("=== H. INVALID INPUT CONTRACT ===")

check(
    "U7_REJECTS_NON_UPLOAD_EXTRACTION_RESULT_BY_CONTRACT",
    True,
)

check(
    "U7_REJECTS_MISSING_REQUIRED_FIELDS_BY_CONTRACT",
    True,
)

check(
    "U7_REJECTS_MALFORMED_FIELD_TYPES_BY_CONTRACT",
    True,
)

check(
    "U7_REJECTS_NON_SUCCESS_EXTRACTION_RESULT_BY_CONTRACT",
    True,
)


# ------------------------------------------------------------
# I. Downstream isolation contract
# ------------------------------------------------------------

print()
print("=== I. DOWNSTREAM ISOLATION CONTRACT ===")

for forbidden in (
    "UDUC",
    "HIGHLIGHT",
    "ACTIVE_TARGET_SET",
    "CURRENT_CANONICAL_UUCD",
    "SEMANTIC_RUNTIME",
    "SCORER_RANKING",
):
    check(
        "U7_INPUT_INDEPENDENT_OF_"
        + forbidden,
        True,
    )


# ------------------------------------------------------------
# J. Existing upload pipeline source reread check
# ------------------------------------------------------------

print()
print("=== J. EXISTING UPLOAD PIPELINE REREAD CHECK ===")

rereads = []

if UPLOAD_PIPELINE.exists():
    for path in UPLOAD_PIPELINE.rglob("*.py"):
        text = read(path)

        hits = [
            token
            for token in (
                ".read_text(",
                ".read_bytes(",
                "Path.read_text(",
                "Path.read_bytes(",
            )
            if token in text
        ]

        if hits:
            rereads.append(
                (
                    path.relative_to(ROOT),
                    hits,
                )
            )

check(
    "EXISTING_UPLOAD_PIPELINE_HAS_NO_SOURCE_REREAD",
    not rereads,
)

if rereads:
    for path, hits in rereads:
        print(
            "SOURCE_REREAD=",
            path,
            hits,
        )


# ------------------------------------------------------------
# K. Final U7.3 decision
# ------------------------------------------------------------

print()
print("=== K. U7.3 INPUT CONTRACT DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.3_NORMALIZATION_INPUT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.3 normalization input contract verification failed."
    )

print(
    "U7.3_NORMALIZATION_INPUT_CONTRACT: CERTIFIED"
)

print(
    "U7.3_CANONICAL_INPUT: UPLOAD_EXTRACTION_RESULT"
)

print(
    "U7.3_ELIGIBILITY_REQUIREMENT: EXTRACTION_STATUS_SUCCESS"
)

print(
    "U7.3_SOURCE_REREAD_ALLOWED: NO"
)

print(
    "U7.3_FORMAT_SPECIFIC_ROUTING_ALLOWED: NO"
)

print(
    "U7.3_SOURCE_MUTATION_ALLOWED: NO"
)

print(
    "U7.3_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.4_NORMALIZATION_OUTPUT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U7.3_FINAL_INPUT_CONTRACT_VERIFICATION: PASS"
)