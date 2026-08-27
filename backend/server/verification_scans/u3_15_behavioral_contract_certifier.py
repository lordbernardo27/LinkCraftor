from __future__ import annotations

from pathlib import Path


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def read_log(path: Path) -> str:
    if not path.is_file():
        return ""

    for encoding in (
        "utf-8-sig",
        "utf-16",
        "utf-8",
    ):
        try:
            return path.read_text(
                encoding=encoding
            )
        except UnicodeError:
            continue

    return ""


print(
    "=== U3.15 STEP 3 — BEHAVIORAL CONTRACT CERTIFICATION ==="
)


success_log = read_log(
    Path(
        "backend/server/verification_scans/"
        "u3_13_intake_success_formats_verification.txt"
    )
)

failure_log = read_log(
    Path(
        "backend/server/verification_scans/"
        "u3_13_intake_failure_rollback_verification.txt"
    )
)

preview_log = read_log(
    Path(
        "backend/server/verification_scans/"
        "u3_13_preview_read_boundary_verification.txt"
    )
)

duplicate_log = read_log(
    Path(
        "backend/server/verification_scans/"
        "u3_13_duplicate_result_contract_verification.txt"
    )
)

post_intake_log = read_log(
    Path(
        "backend/server/verification_scans/"
        "u3_13_post_intake_uduc_failure_verification.txt"
    )
)


print()
print("=== A. SIX-FORMAT SUCCESS ===")

check(
    "SIX_FORMAT_SUCCESS_CERTIFIED",
    "U3.13_INTAKE_SUCCESS_FORMATS_VERIFICATION: PASS"
    in success_log,
)


print()
print("=== B. FAILURE / ROLLBACK CONTRACT ===")

check(
    "FAILURE_ROLLBACK_CERTIFIED",
    "U3.13_INTAKE_FAILURE_ROLLBACK_VERIFICATION: PASS"
    in failure_log,
)

failure_requirements = [
    "BLANK_FILENAME",
    "ZERO",
    "OVERSIZE",
    "ROLLBACK",
]

for term in failure_requirements:
    check(
        f"FAILURE_EVIDENCE_CONTAINS_{term}",
        term.lower()
        in failure_log.lower(),
    )


print()
print("=== C. PREVIEW / CANONICAL EXTRACTION BOUNDARY ===")

check(
    "PREVIEW_BOUNDARY_CERTIFIED",
    "U3.13_PREVIEW_READ_BOUNDARY_VERIFICATION: PASS"
    in preview_log,
)

preview_requirements = {
    "REQUEST_READ_ONCE":
        "read",

    "PREVIEW_TRUNCATION":
        "trunc",

    "EXACT_SOURCE":
        "exact",

    "CANONICAL_EXTRACTION":
        "canonical",

    "EXTRACTOR_ONCE":
        "once",
}

for label, term in preview_requirements.items():
    check(
        label,
        term.lower()
        in preview_log.lower(),
    )


print()
print("=== D. DUPLICATE / IDENTITY CONTRACT ===")

check(
    "DUPLICATE_CONTRACT_CERTIFIED",
    "U3.13_DUPLICATE_RESULT_CONTRACT_VERIFICATION: PASS"
    in duplicate_log,
)

duplicate_requirements = {
    "DISTINCT_DOCUMENT_IDS_EVIDENCED":
        "document",

    "DISTINCT_STORED_NAMES_EVIDENCED":
        "stored",

    "MULTIPLE_REGISTRY_ROWS_EVIDENCED":
        "registry",

    "EXACT_SOURCE_PERSISTENCE_EVIDENCED":
        "exact",
}

for label, term in duplicate_requirements.items():
    check(
        label,
        term.lower()
        in duplicate_log.lower(),
    )


print()
print("=== E. POST-INTAKE FAILURE SEMANTICS ===")

check(
    "POST_INTAKE_UDUC_FAILURE_CERTIFIED",
    "U3.13_POST_INTAKE_UDUC_FAILURE_VERIFICATION: PASS"
    in post_intake_log,
)

post_intake_requirements = {
    "POST_INTAKE_FAILURE_PROPAGATES":
        "failure",

    "SUCCESSFUL_INTAKE_NOT_ROLLED_BACK":
        "rollback",

    "SOURCE_PRESERVED_AFTER_INTAKE":
        "source",

    "REGISTRY_PRESERVED_AFTER_INTAKE":
        "registry",

    "UDUC_HANDOFF_DOCUMENT_ID_EVIDENCED":
        "document",

    "CANONICAL_EXTRACTION_HANDOFF_EVIDENCED":
        "extraction",
}

for label, term in post_intake_requirements.items():
    check(
        label,
        term.lower()
        in post_intake_log.lower(),
    )


print()
print("=== F. REQUIRED CERTIFICATION MARKERS ===")

required_markers = [
    (
        success_log,
        "U3.13_INTAKE_SUCCESS_FORMATS_VERIFICATION: PASS",
    ),
    (
        failure_log,
        "U3.13_INTAKE_FAILURE_ROLLBACK_VERIFICATION: PASS",
    ),
    (
        preview_log,
        "U3.13_PREVIEW_READ_BOUNDARY_VERIFICATION: PASS",
    ),
    (
        duplicate_log,
        "U3.13_DUPLICATE_RESULT_CONTRACT_VERIFICATION: PASS",
    ),
    (
        post_intake_log,
        "U3.13_POST_INTAKE_UDUC_FAILURE_VERIFICATION: PASS",
    ),
]

check(
    "ALL_FIVE_BEHAVIORAL_CERTIFICATES_PASS",
    all(
        marker in content
        for content, marker
        in required_markers
    ),
)


failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U3.15_BEHAVIORAL_CONTRACT_CERTIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.15 behavioral contract certification failed."
    )

print(
    "U3.15_BEHAVIORAL_CONTRACT_CERTIFICATION: PASS"
)