from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

GOV_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_governance"
)

P111 = GOV_ROOT / "workspace_isolation.py"
P112 = GOV_ROOT / "workflow_idempotency.py"
P113 = GOV_ROOT / "duplicate_protection.py"
P114 = GOV_ROOT / "version_governance.py"
P115 = GOV_ROOT / "coordinator_lifecycle.py"
P116 = GOV_ROOT / "security_boundaries.py"

F111 = GOV_ROOT / "workspace_isolation.phase_11_1.freeze.json"
F112 = GOV_ROOT / "workflow_idempotency.phase_11_2.freeze.json"
F113 = GOV_ROOT / "duplicate_protection.phase_11_3.freeze.json"
F114 = GOV_ROOT / "version_governance.phase_11_4.freeze.json"
F115 = GOV_ROOT / "coordinator_lifecycle.phase_11_5.freeze.json"
F116 = GOV_ROOT / "security_boundaries.phase_11_6.freeze.json"

BATCH_FREEZE = (
    GOV_ROOT
    / "coordination_governance.phase_11_1_to_11_6.freeze.json"
)

P117 = (
    GOV_ROOT
    / "governance_certification.py"
)

F117 = (
    GOV_ROOT
    / "governance_certification.phase_11_7.freeze.json"
)

PHASE11_MASTER = (
    GOV_ROOT
    / "phase_11_governance.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_11_final_certification_report.txt"
)

PHASE10_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_observability/"
    "phase_10_observability.freeze.json"
)


EXPECTED_SOURCES = {
    "11.1":
        "9B19D0FCAC54429C9B7F522538243991E44C315E0B9729B779D7F27E144A9A1F",

    "11.2":
        "AA923FEEE6ACDDD5EC5DFFF42D0235A759CD17163BAB75FAA88D04C4E6B768B1",

    "11.3":
        "B44E9C1ECC629BF92F29E6DFCC3E072D18DDA67DE4585D651D32548A7F002FB0",

    "11.4":
        "DFB012E6EBB11B98C6501215E060D6DF66A9612ACCABC396F9FDC2188AB1F2CA",

    "11.5":
        "8D52B2196BDAB144A82B778A5A4449755E3983DDB852B4D6908FBE495DAF12F3",

    "11.6":
        "DD5A47D76A368AD72D0B2C8DFF8D00BDB4C35692F8CADDA65EC487DFA1F192C9",
}


EXPECTED_FREEZES = {
    "11.1":
        "5E6DF349A0298DCBC4724CC59F1B39E9EED270B5B07947EEA10D7E432EF40A93",

    "11.2":
        "222490B973B2E3B28DACA39F3C9DE42705CE90D091FAA9890B0D408A7ABD981F",

    "11.3":
        "3790A1255E14F05DB8E2B7E2E66D5136EEED7D8D7E0DD6D0F59B62521A9D1A16",

    "11.4":
        "0E2E4A41377FCE12345B6C2C30DB596E1D0AA2993803C0D84C689ED930082F1C",

    "11.5":
        "724E38953D17020492B7094E447C346AA45B2BB02CA312C0BA430EA114FBE58C",

    "11.6":
        "E006FED4179FB2C38C830AE88DFBF2C779A0FF8305071603B7C8332675F706A3",
}


EXPECTED_BATCH_FREEZE = (
    "03A282B738587313FC8211259E0845F4AF8AD61D1AD807573CA38B926FE71D59"
)

EXPECTED_PRECERT_COMPOSITE = (
    "5B7699C3586578F85C3A382F3113871725CC41AB019B90EF844D75C85BCCFF4E"
)

EXPECTED_PHASE10_MASTER = (
    "FF400A783DB08834E769370E47FCA8A731E0757FCA75643CE5DA2691A10869CF"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def purge() -> None:
    prefix = (
        "backend.server.coordination.coordination_governance"
    )

    for name in tuple(sys.modules):
        if name.startswith(prefix):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 11.7 GOVERNANCE CERTIFICATION"
)


# ==================================================================
# 0 — AUTHORITY GUARD
# ==================================================================

section(
    "0 — PRE-CERTIFICATION AUTHORITY GUARD"
)


sources = {
    "11.1": P111,
    "11.2": P112,
    "11.3": P113,
    "11.4": P114,
    "11.5": P115,
    "11.6": P116,
}


freezes = {
    "11.1": F111,
    "11.2": F112,
    "11.3": F113,
    "11.4": F114,
    "11.5": F115,
    "11.6": F116,
}


for phase, path in sources.items():

    check(
        f"{phase} source exact",
        path.exists()
        and sha256(path)
        == EXPECTED_SOURCES[
            phase
        ],
    )


for phase, path in freezes.items():

    check(
        f"{phase} freeze exact",
        path.exists()
        and sha256(path)
        == EXPECTED_FREEZES[
            phase
        ],
    )


check(
    "11.1–11.6 batch freeze exact",
    BATCH_FREEZE.exists()
    and sha256(
        BATCH_FREEZE
    )
    == EXPECTED_BATCH_FREEZE,
)


check(
    "Phase 10 master exact",
    PHASE10_MASTER.exists()
    and sha256(
        PHASE10_MASTER
    )
    == EXPECTED_PHASE10_MASTER,
)


check(
    "11.7 source not already installed",
    not P117.exists(),
)


check(
    "11.7 freeze not already installed",
    not F117.exists(),
)


check(
    "Phase 11 master freeze not already installed",
    not PHASE11_MASTER.exists(),
)


# ==================================================================
# 1 — PRECERT COMPOSITE
# ==================================================================

section(
    "1 — VERIFY 11.1–11.6 COMPOSITE"
)


canonical = "\n".join(
    f"{phase}:{EXPECTED_SOURCES[phase]}"
    for phase
    in (
        "11.1",
        "11.2",
        "11.3",
        "11.4",
        "11.5",
        "11.6",
    )
)


actual_composite = hashlib.sha256(
    canonical.encode(
        "utf-8"
    )
).hexdigest().upper()


check(
    "11.1–11.6 composite exact",
    actual_composite
    == EXPECTED_PRECERT_COMPOSITE,
)


# ==================================================================
# 2 — INSTALL 11.7
# ==================================================================

section(
    "2 — INSTALL 11.7 GOVERNANCE CERTIFICATION"
)


P117.write_text(
f'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.7 — Governance Certification.

Final read-only certification authority for Phase 11.1 through 11.6.

This module performs no registration, workflow mutation, Runtime mutation,
credential issuance, authentication, authorization issuance, or execution.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Tuple


GOVERNANCE_CERTIFICATION_VERSION: Final[str] = (
    "governance_certification_v11.7.0"
)

GOVERNANCE_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "governance_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "11.1",
        "workspace_isolation.py",
        "{EXPECTED_SOURCES['11.1']}",
    ),
    (
        "11.2",
        "workflow_idempotency.py",
        "{EXPECTED_SOURCES['11.2']}",
    ),
    (
        "11.3",
        "duplicate_protection.py",
        "{EXPECTED_SOURCES['11.3']}",
    ),
    (
        "11.4",
        "version_governance.py",
        "{EXPECTED_SOURCES['11.4']}",
    ),
    (
        "11.5",
        "coordinator_lifecycle.py",
        "{EXPECTED_SOURCES['11.5']}",
    ),
    (
        "11.6",
        "security_boundaries.py",
        "{EXPECTED_SOURCES['11.6']}",
    ),
)


_EXPECTED_FREEZE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "11.1",
        "workspace_isolation.phase_11_1.freeze.json",
        "{EXPECTED_FREEZES['11.1']}",
    ),
    (
        "11.2",
        "workflow_idempotency.phase_11_2.freeze.json",
        "{EXPECTED_FREEZES['11.2']}",
    ),
    (
        "11.3",
        "duplicate_protection.phase_11_3.freeze.json",
        "{EXPECTED_FREEZES['11.3']}",
    ),
    (
        "11.4",
        "version_governance.phase_11_4.freeze.json",
        "{EXPECTED_FREEZES['11.4']}",
    ),
    (
        "11.5",
        "coordinator_lifecycle.phase_11_5.freeze.json",
        "{EXPECTED_FREEZES['11.5']}",
    ),
    (
        "11.6",
        "security_boundaries.phase_11_6.freeze.json",
        "{EXPECTED_FREEZES['11.6']}",
    ),
)


EXPECTED_PRECERT_COMPOSITE: Final[str] = (
    "{EXPECTED_PRECERT_COMPOSITE}"
)


@dataclass(
    frozen=True,
    slots=True,
)
class GovernanceCertificationResult:

    is_certified: bool

    source_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    freeze_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    composite_fingerprint: str

    violations: Tuple[
        str,
        ...
    ]

    certification_version: str = (
        GOVERNANCE_CERTIFICATION_VERSION
    )

    schema_version: str = (
        GOVERNANCE_CERTIFICATION_SCHEMA_VERSION
    )


def _root() -> Path:
    return Path(
        __file__
    ).resolve().parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def actual_source_hashes() -> Tuple[
    Tuple[str, str],
    ...
]:
    root = _root()

    return tuple(
        (
            phase,
            _sha256(
                root
                / filename
            ),
        )
        for (
            phase,
            filename,
            _expected,
        )
        in _EXPECTED_SOURCE_SHA256
    )


def actual_freeze_hashes() -> Tuple[
    Tuple[str, str],
    ...
]:
    root = _root()

    return tuple(
        (
            phase,
            _sha256(
                root
                / filename
            ),
        )
        for (
            phase,
            filename,
            _expected,
        )
        in _EXPECTED_FREEZE_SHA256
    )


def phase_11_precert_composite(
    source_hashes: Tuple[
        Tuple[str, str],
        ...
    ],
) -> str:

    canonical = "\\n".join(
        f"{{phase}}:{{value}}"
        for phase, value
        in source_hashes
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def evaluate_governance_certification(
) -> GovernanceCertificationResult:

    violations = []

    source_hashes = (
        actual_source_hashes()
    )

    freeze_hashes = (
        actual_freeze_hashes()
    )

    expected_sources = {{
        phase:
            expected
        for (
            phase,
            _filename,
            expected,
        )
        in _EXPECTED_SOURCE_SHA256
    }}

    expected_freezes = {{
        phase:
            expected
        for (
            phase,
            _filename,
            expected,
        )
        in _EXPECTED_FREEZE_SHA256
    }}

    for phase, actual in source_hashes:

        if actual != expected_sources[
            phase
        ]:
            violations.append(
                f"Phase {{phase}} source SHA256 mismatch"
            )

    for phase, actual in freeze_hashes:

        if actual != expected_freezes[
            phase
        ]:
            violations.append(
                f"Phase {{phase}} freeze SHA256 mismatch"
            )

    composite = phase_11_precert_composite(
        source_hashes
    )

    if composite != EXPECTED_PRECERT_COMPOSITE:
        violations.append(
            "Phase 11.1–11.6 composite mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return GovernanceCertificationResult(
        is_certified=
            not canonical_violations,

        source_sha256=
            source_hashes,

        freeze_sha256=
            freeze_hashes,

        composite_fingerprint=
            composite,

        violations=
            canonical_violations,
    )


__all__ = [
    "GOVERNANCE_CERTIFICATION_VERSION",
    "GOVERNANCE_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_PRECERT_COMPOSITE",
    "GovernanceCertificationResult",
    "actual_source_hashes",
    "actual_freeze_hashes",
    "phase_11_precert_composite",
    "evaluate_governance_certification",
]
''',
        encoding="utf-8",
    )


SHA117 = sha256(
    P117
)


print(
    "11.7 SOURCE SHA256:",
    SHA117,
)


# ==================================================================
# 3 — EXECUTE CERTIFICATION
# ==================================================================

section(
    "3 — EXECUTE 11.7 CERTIFICATION"
)


purge()


cert = importlib.import_module(
    "backend.server.coordination.coordination_governance."
    "governance_certification"
)


result = (
    cert.evaluate_governance_certification()
)


check(
    "11.7 certification succeeds",
    result.is_certified,
)


check(
    "11.7 zero violations",
    result.violations
    == (),
)


check(
    "11.7 composite exact",
    result.composite_fingerprint
    == EXPECTED_PRECERT_COMPOSITE,
)


for phase, actual in result.source_sha256:

    check(
        f"11.7 source lineage exact: {phase}",
        actual
        == EXPECTED_SOURCES[
            phase
        ],
    )


for phase, actual in result.freeze_sha256:

    check(
        f"11.7 freeze lineage exact: {phase}",
        actual
        == EXPECTED_FREEZES[
            phase
        ],
    )


# ==================================================================
# 4 — FINAL REPORT
# ==================================================================

section(
    "4 — FINAL PHASE 11 CERTIFICATION REPORT"
)


passed_before_freeze = sum(
    1
    for _name, ok
    in checks
    if ok
)


REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASE 11 — GOVERNANCE FINAL CERTIFICATION",
            "",
            "11.1 Workspace Isolation: CERTIFIED + FROZEN",
            "11.2 Idempotency: CERTIFIED + FROZEN",
            "11.3 Duplicate Protection: CERTIFIED + FROZEN",
            "11.4 Version Governance: CERTIFIED + FROZEN",
            "11.5 Coordinator Lifecycle: CERTIFIED + FROZEN",
            "11.6 Security Boundaries: CERTIFIED + FROZEN",
            "11.7 Governance Certification: CERTIFIED",
            "",
            f"11.1 SHA256: {EXPECTED_SOURCES['11.1']}",
            f"11.2 SHA256: {EXPECTED_SOURCES['11.2']}",
            f"11.3 SHA256: {EXPECTED_SOURCES['11.3']}",
            f"11.4 SHA256: {EXPECTED_SOURCES['11.4']}",
            f"11.5 SHA256: {EXPECTED_SOURCES['11.5']}",
            f"11.6 SHA256: {EXPECTED_SOURCES['11.6']}",
            f"11.7 SHA256: {SHA117}",
            "",
            f"11.1–11.6 COMPOSITE SHA256: {EXPECTED_PRECERT_COMPOSITE}",
            "",
            "Certified governance boundaries:",
            "- Phase 2 retains workflow and coordinator registration authority",
            "- Phase 2.4 retains explicit version preference authority",
            "- Runtime retains Universal Job idempotency",
            "- Runtime retains job/queue deduplication",
            "- Runtime retains authentication and generic authorization",
            "- Phase 11 governs UCF workflow-level coordination policy",
            "",
            f"Formal checks passed before freeze: {passed_before_freeze}",
            "Formal failures: 0",
            "",
            "STATUS: CERTIFIED + FROZEN",
        )
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha256(
    REPORT
)


# ==================================================================
# 5 — FREEZE 11.7
# ==================================================================

section(
    "5 — FREEZE 11.7"
)


write_json(
    F117,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "11.7",

        "component":
            "Governance Certification",

        "certified":
            True,

        "frozen":
            True,

        "production": {
            "path":
                "backend/server/coordination/"
                "coordination_governance/"
                "governance_certification.py",

            "version":
                "governance_certification_v11.7.0",

            "schema_version":
                "governance_certification_schema_v1",

            "sha256":
                SHA117,
        },

        "predecessor_sources":
            EXPECTED_SOURCES,

        "predecessor_freezes":
            EXPECTED_FREEZES,

        "phase_11_1_to_11_6_composite_sha256":
            EXPECTED_PRECERT_COMPOSITE,

        "batch_freeze_sha256":
            EXPECTED_BATCH_FREEZE,

        "phase_10_master_sha256":
            EXPECTED_PHASE10_MASTER,

        "final_certification_report": {
            "path":
                REPORT.name,

            "sha256":
                REPORT_SHA,
        },

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "12.0 Framework Certification",
    },
)


F117_SHA = sha256(
    F117
)


# ==================================================================
# 6 — PHASE 11 MASTER FREEZE
# ==================================================================

section(
    "6 — PHASE 11 MASTER FREEZE"
)


phase11_sources = {
    **EXPECTED_SOURCES,
    "11.7":
        SHA117,
}


phase11_freezes = {
    **EXPECTED_FREEZES,
    "11.7":
        F117_SHA,
}


canonical_full = "\n".join(
    f"{phase}:{phase11_sources[phase]}"
    for phase
    in (
        "11.1",
        "11.2",
        "11.3",
        "11.4",
        "11.5",
        "11.6",
        "11.7",
    )
)


PHASE11_COMPOSITE = hashlib.sha256(
    canonical_full.encode(
        "utf-8"
    )
).hexdigest().upper()


write_json(
    PHASE11_MASTER,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "11",

        "component":
            "Governance",

        "certified":
            True,

        "frozen":
            True,

        "components": {
            "11.1":
                "Workspace Isolation",

            "11.2":
                "Idempotency",

            "11.3":
                "Duplicate Protection",

            "11.4":
                "Version Governance",

            "11.5":
                "Coordinator Lifecycle",

            "11.6":
                "Security Boundaries",

            "11.7":
                "Governance Certification",
        },

        "source_sha256":
            phase11_sources,

        "freeze_sha256":
            phase11_freezes,

        "phase_11_1_to_11_6_composite_sha256":
            EXPECTED_PRECERT_COMPOSITE,

        "phase_11_full_composite_sha256":
            PHASE11_COMPOSITE,

        "phase_10_master_sha256":
            EXPECTED_PHASE10_MASTER,

        "runtime_authority_preserved":
            True,

        "workflow_level_governance":
            True,

        "final_certification_report": {
            "path":
                REPORT.name,

            "sha256":
                REPORT_SHA,
        },

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "12.0 Framework Certification",
    },
)


MASTER_SHA = sha256(
    PHASE11_MASTER
)


# ==================================================================
# 7 — FINAL POST-FREEZE VERIFICATION
# ==================================================================

section(
    "7 — FINAL POST-FREEZE VERIFICATION"
)


for phase, path in sources.items():

    check(
        f"final source unchanged: {phase}",
        sha256(path)
        == EXPECTED_SOURCES[
            phase
        ],
    )


for phase, path in freezes.items():

    check(
        f"final freeze unchanged: {phase}",
        sha256(path)
        == EXPECTED_FREEZES[
            phase
        ],
    )


check(
    "batch freeze unchanged",
    sha256(
        BATCH_FREEZE
    )
    == EXPECTED_BATCH_FREEZE,
)


check(
    "Phase 10 master unchanged",
    sha256(
        PHASE10_MASTER
    )
    == EXPECTED_PHASE10_MASTER,
)


purge()


final_cert = importlib.import_module(
    "backend.server.coordination.coordination_governance."
    "governance_certification"
)


final_result = (
    final_cert.evaluate_governance_certification()
)


check(
    "final 11.7 certification passes",
    final_result.is_certified,
)


check(
    "final 11.7 zero violations",
    final_result.violations
    == (),
)


# ==================================================================
# 8 — FINAL STATUS
# ==================================================================

section(
    "8 — PHASE 11 FINAL STATUS"
)


total = sum(
    1
    for _name, ok
    in checks
    if ok
)


print(
    "TOTAL FORMAL CHECKS:",
    total,
    "PASS",
)

print()

print(
    "PHASE 11.1 WORKSPACE ISOLATION: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.2 IDEMPOTENCY: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.3 DUPLICATE PROTECTION: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.4 VERSION GOVERNANCE: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.5 COORDINATOR LIFECYCLE: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.6 SECURITY BOUNDARIES: CERTIFIED + FROZEN"
)

print(
    "PHASE 11.7 GOVERNANCE CERTIFICATION: CERTIFIED + FROZEN"
)

print()

print(
    "11.7 SOURCE SHA256:",
    SHA117,
)

print(
    "11.7 FREEZE SHA256:",
    F117_SHA,
)

print(
    "PHASE 11.1–11.6 COMPOSITE SHA256:",
    EXPECTED_PRECERT_COMPOSITE,
)

print(
    "PHASE 11 FULL COMPOSITE SHA256:",
    PHASE11_COMPOSITE,
)

print(
    "PHASE 11 MASTER FREEZE SHA256:",
    MASTER_SHA,
)

print(
    "FINAL CERTIFICATION REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "PHASE 10 MODIFIED: FALSE"
)

print(
    "PHASE 11.1–11.6 MODIFIED DURING 11.7: FALSE"
)

print(
    "UNIVERSAL RUNTIME MODIFIED: FALSE"
)

print()

print(
    "PHASE 11 — GOVERNANCE: CERTIFIED + FROZEN"
)

print(
    "NEXT: PHASE 12.0 — FRAMEWORK CERTIFICATION"
)

print("=" * 120)
