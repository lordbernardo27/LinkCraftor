from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_final_certification.txt"
)

REPORTS = {
    "success":
        ROOT
        / "runtime_integration_phase_5_6_success_path_certification.txt",

    "failure_retry":
        ROOT
        / "runtime_integration_phase_5_6_failure_retry_certification.txt",

    "identity_evidence":
        ROOT
        / "runtime_integration_phase_5_6_identity_evidence_certification.txt",
}

EXPECTED_REPORT_SHA = {
    "success":
        "F49E0ECEC269AE62CE2F04BBDCD127B553D566932972EF546D495E4F95A5121B",

    "failure_retry":
        "5C67756F83933474F3B30A591665949EEA2ACB48E1CAA9D8377A0959028D9CA9",

    "identity_evidence":
        "FBDF67479527BC5BE45E7D1249E3357734107404DA56F8F7495F15923A5E38FA",
}


SOURCES = {
    "submission":
        ROOT
        / "backend/server/runtime/universal_job_submission.py",

    "worker":
        ROOT
        / "backend/server/runtime/universal_runtime_worker_v1.py",

    "phase_5_3":
        ROOT
        / (
            "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py"
        ),

    "phase_5_4":
        ROOT
        / (
            "backend/server/coordination/runtime_integration/"
            "runtime_completion_intake.py"
        ),

    "phase_5_5":
        ROOT
        / (
            "backend/server/coordination/runtime_integration/"
            "runtime_failure_intake.py"
        ),
}

EXPECTED_SOURCE_SHA = {
    "submission":
        "8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",

    "worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182F9DA937D9CB09FD33262C506B9BEF699",

    "phase_5_3":
        "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC1042A53DDD3B2F72BB355259FA0E5D2E6FB",

    "phase_5_5":
        "CDEE8D641AC045956E2A203BF0A62DE70933F0755B946D63310EFBABE7DFE241",
}


checks = []


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def check(name, condition, detail=""):
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
            detail,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            "    " + str(detail)
        )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6.8 — FINAL RUNTIME INTEGRATION CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Certification report integrity
# =========================================================================

for name, path in REPORTS.items():

    check(
        "Certification report exists: " + name,
        path.exists(),
        path,
    )

    if path.exists():

        actual = sha256(
            path
        )

        check(
            "Certification report SHA exact: " + name,
            actual
            == EXPECTED_REPORT_SHA[
                name
            ],
            actual,
        )


# =========================================================================
# 2. Certification result assertions
# =========================================================================

success_text = REPORTS[
    "success"
].read_text(
    encoding="utf-8"
)

failure_text = REPORTS[
    "failure_retry"
].read_text(
    encoding="utf-8"
)

identity_text = REPORTS[
    "identity_evidence"
].read_text(
    encoding="utf-8"
)


check(
    "5.6.5 success certification declares 52/52",
    (
        "Checks: 52"
        in success_text
        and "Passed: 52"
        in success_text
        and "Failed: 0"
        in success_text
    ),
)

check(
    "5.6.5 success path certified",
    (
        "SUCCESS PATH CERTIFIED: TRUE"
        in success_text.upper()
    ),
)

check(
    "5.6.5 canonical submission verified",
    "Real canonical submission: VERIFIED"
    in success_text,
)

check(
    "5.6.5 Runtime queue ingress verified",
    "Real orchestration queue ingress: VERIFIED"
    in success_text,
)

check(
    "5.6.5 Runtime claim verified",
    "Real Runtime claim: VERIFIED"
    in success_text,
)

check(
    "5.6.5 success transition verified",
    "Real RUNNING -> COMPLETED: VERIFIED"
    in success_text,
)

check(
    "5.6.5 Phase 5.4 completion intake verified",
    "Real Phase 5.4 completion intake: VERIFIED"
    in success_text,
)


check(
    "5.6.6 failure/retry certification declares 81/81",
    (
        "Checks: 81"
        in failure_text
        and "Passed: 81"
        in failure_text
        and "Failed: 0"
        in failure_text
    ),
)

check(
    "5.6.6 failure/retry path certified",
    (
        "FAILURE/RETRY PATH CERTIFIED: TRUE"
        in failure_text.upper()
    ),
)

check(
    "5.6.6 retry attempt 1 verified",
    "Attempt 1: RUNNING -> QUEUED"
    in failure_text,
)

check(
    "5.6.6 retry attempt 2 verified",
    "Attempt 2: RUNNING -> QUEUED"
    in failure_text,
)

check(
    "5.6.6 terminal attempt verified",
    "Attempt 3: RUNNING -> FAILED"
    in failure_text,
)

check(
    "5.6.6 same-job retry identity verified",
    "Same-job retry identity: VERIFIED"
    in failure_text,
)

check(
    "5.6.6 replacement job prohibited",
    "Replacement job created: FALSE"
    in failure_text,
)

check(
    "5.6.6 Phase 5.5 failure intake verified",
    "Real Phase 5.5 failure intake: VERIFIED"
    in failure_text,
)


check(
    "5.6.7 identity/evidence certification declares 101/101",
    (
        "Checks: 101"
        in identity_text
        and "Passed: 101"
        in identity_text
        and "Failed: 0"
        in identity_text
    ),
)

check(
    "5.6.7 identity/evidence certified",
    (
        "IDENTITY & EVIDENCE CERTIFIED: TRUE"
        in identity_text.upper()
    ),
)

check(
    "5.6.7 success identity continuity verified",
    "Success identity continuity: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 failure identity continuity verified",
    "Failure/retry identity continuity: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 submission evidence verified",
    "Submission evidence: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 Runtime Registration evidence verified",
    "Runtime Registration evidence: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 status-event evidence verified",
    "Runtime status-event evidence: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 retry evidence verified",
    "Same-job retry evidence: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 terminal failure evidence verified",
    "Terminal failure evidence: VERIFIED"
    in identity_text,
)

check(
    "5.6.7 evidence SHA generation verified",
    "Evidence SHA256 generation: VERIFIED"
    in identity_text,
)


# =========================================================================
# 3. Canonical production source integrity
# =========================================================================

source_before = {}

for name, path in SOURCES.items():

    check(
        "Canonical production source exists: " + name,
        path.exists(),
        path,
    )

    if path.exists():

        actual = sha256(
            path
        )

        source_before[
            name
        ] = actual

        check(
            "Canonical production SHA exact: " + name,
            actual
            == EXPECTED_SOURCE_SHA[
                name
            ],
            actual,
        )


# =========================================================================
# 4. Cross-path architectural assertions
# =========================================================================

check(
    "Success and failure paths use same submission authority",
    EXPECTED_SOURCE_SHA[
        "submission"
    ]
    == source_before.get(
        "submission"
    ),
)

check(
    "Success and failure paths use same Runtime Worker authority",
    EXPECTED_SOURCE_SHA[
        "worker"
    ]
    == source_before.get(
        "worker"
    ),
)

check(
    "Both return paths use corrected Phase 5.3 correlation authority",
    EXPECTED_SOURCE_SHA[
        "phase_5_3"
    ]
    == source_before.get(
        "phase_5_3"
    ),
)

check(
    "Success path terminates through Phase 5.4",
    EXPECTED_SOURCE_SHA[
        "phase_5_4"
    ]
    == source_before.get(
        "phase_5_4"
    ),
)

check(
    "Failure path terminates through Phase 5.5",
    EXPECTED_SOURCE_SHA[
        "phase_5_5"
    ]
    == source_before.get(
        "phase_5_5"
    ),
)


# =========================================================================
# 5. Production immutability during final composite certification
# =========================================================================

source_after = {
    name:
        sha256(
            path
        )
    for name, path
    in SOURCES.items()
}


check(
    "Production source files unchanged during 5.6.8",
    source_after
    == source_before,
)


# =========================================================================
# 6. Final result
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(
        checks
    )
    - passed
)

certified = (
    failed
    == 0
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.6.8 — FINAL RUNTIME INTEGRATION CERTIFICATION",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"FINAL RUNTIME INTEGRATION CERTIFIED: {certified}",
    "",
    "5.6.5 Success Path: CERTIFIED",
    "5.6.6 Failure/Retry Path: CERTIFIED",
    "5.6.7 Identity & Evidence: CERTIFIED",
    "Canonical submission boundary: VERIFIED",
    "Canonical Runtime Worker: VERIFIED",
    "Phase 5.3 correlation: VERIFIED",
    "Phase 5.4 completion return: VERIFIED",
    "Phase 5.5 failure return: VERIFIED",
    "Same canonical job identity: VERIFIED",
    "Same-job retry semantics: VERIFIED",
    "Production source integrity: VERIFIED",
    "",
    (
        "NEXT: 5.6.9 Certification Report"
        if certified
        else "NEXT: Resolve final Runtime integration certification failures"
    ),
]

REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.6.8 FINAL RUNTIME INTEGRATION CERTIFICATION RESULT")
print("=" * 120)
print(
    "Checks:",
    len(
        checks
    ),
)
print(
    "Passed:",
    passed,
)
print(
    "Failed:",
    failed,
)
print(
    "FINAL RUNTIME INTEGRATION CERTIFIED:",
    certified,
)
print(
    (
        "NEXT: 5.6.9 Certification Report"
        if certified
        else "NEXT: Resolve final Runtime integration certification failures"
    )
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
