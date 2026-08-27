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
    "=== U3.15 STEP 1 — CERTIFICATION EVIDENCE ==="
)


required_evidence = {
    # --------------------------------------------------------
    # U3.13 behavioral certification evidence
    # --------------------------------------------------------
    "U3_13_SUCCESS_FORMATS": (
        Path(
            "backend/server/verification_scans/"
            "u3_13_intake_success_formats_verification.txt"
        ),
        "U3.13_INTAKE_SUCCESS_FORMATS_VERIFICATION: PASS",
    ),

    "U3_13_FAILURE_ROLLBACK": (
        Path(
            "backend/server/verification_scans/"
            "u3_13_intake_failure_rollback_verification.txt"
        ),
        "U3.13_INTAKE_FAILURE_ROLLBACK_VERIFICATION: PASS",
    ),

    "U3_13_PREVIEW_READ_BOUNDARY": (
        Path(
            "backend/server/verification_scans/"
            "u3_13_preview_read_boundary_verification.txt"
        ),
        "U3.13_PREVIEW_READ_BOUNDARY_VERIFICATION: PASS",
    ),

    "U3_13_DUPLICATE_RESULT_CONTRACT": (
        Path(
            "backend/server/verification_scans/"
            "u3_13_duplicate_result_contract_verification.txt"
        ),
        "U3.13_DUPLICATE_RESULT_CONTRACT_VERIFICATION: PASS",
    ),

    "U3_13_POST_INTAKE_UDUC_FAILURE": (
        Path(
            "backend/server/verification_scans/"
            "u3_13_post_intake_uduc_failure_verification.txt"
        ),
        "U3.13_POST_INTAKE_UDUC_FAILURE_VERIFICATION: PASS",
    ),

    # --------------------------------------------------------
    # U3.14 build/integration certification evidence
    # --------------------------------------------------------
    "U3_14_IMPORT_BUILD": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_import_build_surface_verification.txt"
        ),
        "U3.14_IMPORT_BUILD_SURFACE_VERIFICATION: PASS",
    ),

    "U3_14_ROUTE_WIRING": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_route_wiring_verification.txt"
        ),
        "U3.14_ROUTE_WIRING_VERIFICATION: PASS",
    ),

    "U3_14_PREMATURE_INTEGRATION": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_premature_integration_boundary_verification.txt"
        ),
        "U3.14_PREMATURE_INTEGRATION_BOUNDARY_VERIFICATION: PASS",
    ),

    "U3_14_FULL_INTEGRATION_SMOKE": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_full_integration_smoke_verification.txt"
        ),
        "U3.14_FULL_INTEGRATION_SMOKE_VERIFICATION: PASS",
    ),

    "U3_14_FINAL_CERTIFICATION": (
        Path(
            "backend/server/verification_scans/"
            "u3_14_final_certification.txt"
        ),
        "U3.14_FINAL_CERTIFICATION: PASS",
    ),
}


print()
print("=== REQUIRED LOGS / PASS MARKERS ===")

for label, (path, marker) in required_evidence.items():
    exists = path.is_file()

    check(
        f"{label}_LOG_EXISTS",
        exists,
    )

    content = read_log(path)

    check(
        f"{label}_PASS_MARKER",
        marker in content,
    )


print()
print("=== CERTIFICATION EVIDENCE COUNTS ===")

expected_count = len(required_evidence)

existing_count = sum(
    1
    for path, _marker
    in required_evidence.values()
    if path.is_file()
)

passing_count = sum(
    1
    for path, marker
    in required_evidence.values()
    if marker in read_log(path)
)

print(
    "EXPECTED_EVIDENCE_COUNT:",
    expected_count,
)

print(
    "EXISTING_EVIDENCE_COUNT:",
    existing_count,
)

print(
    "PASSING_EVIDENCE_COUNT:",
    passing_count,
)

check(
    "ALL_REQUIRED_EVIDENCE_EXISTS",
    existing_count == expected_count,
)

check(
    "ALL_REQUIRED_EVIDENCE_PASSES",
    passing_count == expected_count,
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
        "U3.15_CERTIFICATION_EVIDENCE_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.15 certification evidence verification failed."
    )

print(
    "U3.15_CERTIFICATION_EVIDENCE_VERIFICATION: PASS"
)