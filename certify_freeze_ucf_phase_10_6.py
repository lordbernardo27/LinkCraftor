from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

OBS_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_observability"
)

P101 = OBS_ROOT / "workflow_progress.py"
P102 = OBS_ROOT / "workflow_metrics.py"
P103 = OBS_ROOT / "stage_metrics.py"
P104 = OBS_ROOT / "workflow_evidence.py"
P105 = OBS_ROOT / "audit_trail.py"

F101 = OBS_ROOT / "workflow_progress.phase_10_1.freeze.json"
F102 = OBS_ROOT / "workflow_metrics.phase_10_2.freeze.json"
F103 = OBS_ROOT / "stage_metrics.phase_10_3.freeze.json"
F104 = OBS_ROOT / "workflow_evidence.phase_10_4.freeze.json"
F105 = OBS_ROOT / "audit_trail.phase_10_5.freeze.json"

BATCH_FREEZE = (
    OBS_ROOT
    / "coordination_observability.phase_10_1_to_10_5.freeze.json"
)

P106 = (
    OBS_ROOT
    / "observability_certification.py"
)

F106 = (
    OBS_ROOT
    / "observability_certification.phase_10_6.freeze.json"
)

PHASE10_MASTER = (
    OBS_ROOT
    / "phase_10_observability.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_10_final_certification_report.txt"
)

PHASE9_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_recovery/"
    "phase_9_coordination_recovery.freeze.json"
)


EXPECTED_SOURCES = {
    "10.1":
        "D4D90A849ACA95643314B96673017E8198EC65DAF03B205CBF3FD6BCB9066AC9",

    "10.2":
        "C3E31D561431994507B18F8A852303A12CC082D2CE19352F45406A17815F6D42",

    "10.3":
        "DC1BFB42187C358EB46662FDA0BB68AB62E461A4D7C8305BDF64BB19FA7EA290",

    "10.4":
        "AB2D613AE8CFF291FF6C955F10F41200A1D7A405653646D6624A774236597E83",

    "10.5":
        "73B122F771C9FB859ABD5B16A03192F2A0EEB8EA66A9B3A815085B2DF26982D9",
}


EXPECTED_FREEZES = {
    "10.1":
        "86AF29FA6B281D3D0E5FFCD0132A4A6B9C33487F07A4FE6DFA5894F9C411C75A",

    "10.2":
        "AF336ADBB78B1B048B3C3124DC2E8A05ED3CD14F3A86AFA572E332D9E7BC8F23",

    "10.3":
        "D397E6EEF2FB92A17579A605C5BB0B5894D506695408AC60C68411ED549B8790",

    "10.4":
        "03C1BC75E5CDDC2A6DE319B2603C7C93CF27BF411F746258065DD40612922D51",

    "10.5":
        "41FC9212F0FEDD832B275AA13EB339DA7E6CB29A5C60E7AA050CF4A54BB57769",
}


EXPECTED_BATCH_FREEZE = (
    "3E57759F4B5DB2ADAF679B797C4AE7212949DA430E29FE4B565EE95DF03BB2EC"
)

EXPECTED_PRECERT_COMPOSITE = (
    "5F27777BCDC8860EF5CF8B6461E069FD3A6EA0BA3498EBEC2D9B224DB7AA57FF"
)

EXPECTED_PHASE9_MASTER = (
    "49499305D5CCBF98C7C9E26D0606D9D1F7F2E528110B04DF8E14369E20C68E0C"
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
        "backend.server.coordination.coordination_observability"
    )

    for name in tuple(
        sys.modules
    ):
        if name.startswith(prefix):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 10.6 OBSERVABILITY CERTIFICATION"
)


# ==================================================================
# 0 — AUTHORITY GUARD
# ==================================================================

section(
    "0 — PRE-CERTIFICATION AUTHORITY GUARD"
)


sources = {
    "10.1":
        P101,

    "10.2":
        P102,

    "10.3":
        P103,

    "10.4":
        P104,

    "10.5":
        P105,
}


freezes = {
    "10.1":
        F101,

    "10.2":
        F102,

    "10.3":
        F103,

    "10.4":
        F104,

    "10.5":
        F105,
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
    "10.1–10.5 batch freeze exact",
    BATCH_FREEZE.exists()
    and sha256(
        BATCH_FREEZE
    )
    == EXPECTED_BATCH_FREEZE,
)


check(
    "Phase 9 master freeze exact",
    PHASE9_MASTER.exists()
    and sha256(
        PHASE9_MASTER
    )
    == EXPECTED_PHASE9_MASTER,
)


check(
    "10.6 production not already installed",
    not P106.exists(),
)


check(
    "10.6 freeze not already installed",
    not F106.exists(),
)


check(
    "Phase 10 master freeze not already installed",
    not PHASE10_MASTER.exists(),
)


# ==================================================================
# 1 — PRECERT COMPOSITE
# ==================================================================

section(
    "1 — VERIFY 10.1–10.5 COMPOSITE"
)


canonical = "\n".join(
    f"{phase}:{EXPECTED_SOURCES[phase]}"
    for phase
    in (
        "10.1",
        "10.2",
        "10.3",
        "10.4",
        "10.5",
    )
)


actual_composite = hashlib.sha256(
    canonical.encode(
        "utf-8"
    )
).hexdigest().upper()


check(
    "10.1–10.5 composite exact",
    actual_composite
    == EXPECTED_PRECERT_COMPOSITE,
)


# ==================================================================
# 2 — INSTALL 10.6
# ==================================================================

section(
    "2 — INSTALL 10.6 OBSERVABILITY CERTIFICATION"
)


P106.write_text(
f'''"""
LinkCraftor — Universal Coordination Framework

Phase 10.6 — Observability Certification.

Read-only final certification authority for UCF Phase 10.1 through 10.5.

No workflow mutation.
No Runtime mutation.
No metric/log/telemetry emission.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Tuple


OBSERVABILITY_CERTIFICATION_VERSION: Final[str] = (
    "observability_certification_v10.6.0"
)

OBSERVABILITY_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "observability_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "10.1",
        "workflow_progress.py",
        "{EXPECTED_SOURCES['10.1']}",
    ),
    (
        "10.2",
        "workflow_metrics.py",
        "{EXPECTED_SOURCES['10.2']}",
    ),
    (
        "10.3",
        "stage_metrics.py",
        "{EXPECTED_SOURCES['10.3']}",
    ),
    (
        "10.4",
        "workflow_evidence.py",
        "{EXPECTED_SOURCES['10.4']}",
    ),
    (
        "10.5",
        "audit_trail.py",
        "{EXPECTED_SOURCES['10.5']}",
    ),
)


_EXPECTED_FREEZE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "10.1",
        "workflow_progress.phase_10_1.freeze.json",
        "{EXPECTED_FREEZES['10.1']}",
    ),
    (
        "10.2",
        "workflow_metrics.phase_10_2.freeze.json",
        "{EXPECTED_FREEZES['10.2']}",
    ),
    (
        "10.3",
        "stage_metrics.phase_10_3.freeze.json",
        "{EXPECTED_FREEZES['10.3']}",
    ),
    (
        "10.4",
        "workflow_evidence.phase_10_4.freeze.json",
        "{EXPECTED_FREEZES['10.4']}",
    ),
    (
        "10.5",
        "audit_trail.phase_10_5.freeze.json",
        "{EXPECTED_FREEZES['10.5']}",
    ),
)


EXPECTED_PRECERT_COMPOSITE: Final[str] = (
    "{EXPECTED_PRECERT_COMPOSITE}"
)


@dataclass(
    frozen=True,
    slots=True,
)
class ObservabilityCertificationResult:

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
        OBSERVABILITY_CERTIFICATION_VERSION
    )

    schema_version: str = (
        OBSERVABILITY_CERTIFICATION_SCHEMA_VERSION
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


def phase_10_precert_composite(
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


def evaluate_observability_certification(
) -> ObservabilityCertificationResult:

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

        if (
            actual
            != expected_sources[
                phase
            ]
        ):
            violations.append(
                f"Phase {{phase}} source SHA256 mismatch"
            )

    for phase, actual in freeze_hashes:

        if (
            actual
            != expected_freezes[
                phase
            ]
        ):
            violations.append(
                f"Phase {{phase}} freeze SHA256 mismatch"
            )

    composite = phase_10_precert_composite(
        source_hashes
    )

    if composite != EXPECTED_PRECERT_COMPOSITE:
        violations.append(
            "Phase 10.1–10.5 composite mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return ObservabilityCertificationResult(
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
    "OBSERVABILITY_CERTIFICATION_VERSION",
    "OBSERVABILITY_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_PRECERT_COMPOSITE",
    "ObservabilityCertificationResult",
    "actual_source_hashes",
    "actual_freeze_hashes",
    "phase_10_precert_composite",
    "evaluate_observability_certification",
]
''',
        encoding="utf-8",
    )


SHA106 = sha256(
    P106
)


print(
    "10.6 SOURCE SHA256:",
    SHA106,
)


# ==================================================================
# 3 — EXECUTE CERTIFICATION
# ==================================================================

section(
    "3 — EXECUTE 10.6 CERTIFICATION"
)


purge()


cert = importlib.import_module(
    "backend.server.coordination.coordination_observability."
    "observability_certification"
)


result = (
    cert.evaluate_observability_certification()
)


check(
    "10.6 certification succeeds",
    result.is_certified,
)


check(
    "10.6 zero violations",
    result.violations
    == (),
)


check(
    "10.6 composite exact",
    result.composite_fingerprint
    == EXPECTED_PRECERT_COMPOSITE,
)


for phase, actual in result.source_sha256:

    check(
        f"10.6 source lineage exact: {phase}",
        actual
        == EXPECTED_SOURCES[
            phase
        ],
    )


for phase, actual in result.freeze_sha256:

    check(
        f"10.6 freeze lineage exact: {phase}",
        actual
        == EXPECTED_FREEZES[
            phase
        ],
    )


# ==================================================================
# 4 — FINAL REPORT
# ==================================================================

section(
    "4 — FINAL PHASE 10 CERTIFICATION REPORT"
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
            "PHASE 10 — OBSERVABILITY FINAL CERTIFICATION",
            "",
            "10.1 Workflow Progress: CERTIFIED + FROZEN",
            "10.2 Workflow Metrics: CERTIFIED + FROZEN",
            "10.3 Stage Metrics: CERTIFIED + FROZEN",
            "10.4 Workflow Evidence: CERTIFIED + FROZEN",
            "10.5 Audit Trail: CERTIFIED + FROZEN",
            "10.6 Observability Certification: CERTIFIED",
            "",
            f"10.1 SHA256: {EXPECTED_SOURCES['10.1']}",
            f"10.2 SHA256: {EXPECTED_SOURCES['10.2']}",
            f"10.3 SHA256: {EXPECTED_SOURCES['10.3']}",
            f"10.4 SHA256: {EXPECTED_SOURCES['10.4']}",
            f"10.5 SHA256: {EXPECTED_SOURCES['10.5']}",
            f"10.6 SHA256: {SHA106}",
            "",
            f"10.1–10.5 COMPOSITE SHA256: {EXPECTED_PRECERT_COMPOSITE}",
            "",
            "Certified boundaries:",
            "- UCF observability is read-only",
            "- no workflow mutation",
            "- no Runtime mutation",
            "- no Runtime metrics duplication",
            "- no Runtime telemetry duplication",
            "- lifecycle history remains canonical transition evidence",
            "- stage-state store remains canonical stage-state evidence",
            "- Phase 9 remains canonical recovery authority",
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
# 5 — FREEZE 10.6
# ==================================================================

section(
    "5 — FREEZE 10.6"
)


write_json(
    F106,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "10.6",

        "component":
            "Observability Certification",

        "certified":
            True,

        "frozen":
            True,

        "production": {
            "path":
                "backend/server/coordination/"
                "coordination_observability/"
                "observability_certification.py",

            "version":
                "observability_certification_v10.6.0",

            "schema_version":
                "observability_certification_schema_v1",

            "sha256":
                SHA106,
        },

        "predecessor_sources":
            EXPECTED_SOURCES,

        "predecessor_freezes":
            EXPECTED_FREEZES,

        "phase_10_1_to_10_5_composite_sha256":
            EXPECTED_PRECERT_COMPOSITE,

        "batch_freeze_sha256":
            EXPECTED_BATCH_FREEZE,

        "phase_9_master_sha256":
            EXPECTED_PHASE9_MASTER,

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
            "11.0 Governance",
    },
)


F106_SHA = sha256(
    F106
)


# ==================================================================
# 6 — PHASE 10 MASTER FREEZE
# ==================================================================

section(
    "6 — PHASE 10 MASTER FREEZE"
)


phase10_sources = {
    **EXPECTED_SOURCES,
    "10.6":
        SHA106,
}


phase10_freezes = {
    **EXPECTED_FREEZES,
    "10.6":
        F106_SHA,
}


canonical_full = "\n".join(
    f"{phase}:{phase10_sources[phase]}"
    for phase
    in (
        "10.1",
        "10.2",
        "10.3",
        "10.4",
        "10.5",
        "10.6",
    )
)


PHASE10_COMPOSITE = hashlib.sha256(
    canonical_full.encode(
        "utf-8"
    )
).hexdigest().upper()


write_json(
    PHASE10_MASTER,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "10",

        "component":
            "Observability",

        "certified":
            True,

        "frozen":
            True,

        "components": {
            "10.1":
                "Workflow Progress",

            "10.2":
                "Workflow Metrics",

            "10.3":
                "Stage Metrics",

            "10.4":
                "Workflow Evidence",

            "10.5":
                "Audit Trail",

            "10.6":
                "Observability Certification",
        },

        "source_sha256":
            phase10_sources,

        "freeze_sha256":
            phase10_freezes,

        "phase_10_1_to_10_5_composite_sha256":
            EXPECTED_PRECERT_COMPOSITE,

        "phase_10_full_composite_sha256":
            PHASE10_COMPOSITE,

        "read_only":
            True,

        "runtime_observability_duplicated":
            False,

        "phase_9_master_sha256":
            EXPECTED_PHASE9_MASTER,

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
            "11.0 Governance",
    },
)


MASTER_SHA = sha256(
    PHASE10_MASTER
)


# ==================================================================
# 7 — FINAL VERIFICATION
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
    "Phase 9 master unchanged",
    sha256(
        PHASE9_MASTER
    )
    == EXPECTED_PHASE9_MASTER,
)


purge()


final_cert = importlib.import_module(
    "backend.server.coordination.coordination_observability."
    "observability_certification"
)


final_result = (
    final_cert.evaluate_observability_certification()
)


check(
    "final 10.6 certification passes",
    final_result.is_certified,
)


check(
    "final 10.6 zero violations",
    final_result.violations
    == (),
)


# ==================================================================
# 8 — FINAL STATUS
# ==================================================================

section(
    "8 — PHASE 10 FINAL STATUS"
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
    "PHASE 10.1 WORKFLOW PROGRESS: CERTIFIED + FROZEN"
)

print(
    "PHASE 10.2 WORKFLOW METRICS: CERTIFIED + FROZEN"
)

print(
    "PHASE 10.3 STAGE METRICS: CERTIFIED + FROZEN"
)

print(
    "PHASE 10.4 WORKFLOW EVIDENCE: CERTIFIED + FROZEN"
)

print(
    "PHASE 10.5 AUDIT TRAIL: CERTIFIED + FROZEN"
)

print(
    "PHASE 10.6 OBSERVABILITY CERTIFICATION: CERTIFIED + FROZEN"
)

print()

print(
    "10.6 SOURCE SHA256:",
    SHA106,
)

print(
    "10.6 FREEZE SHA256:",
    F106_SHA,
)

print(
    "PHASE 10.1–10.5 COMPOSITE SHA256:",
    EXPECTED_PRECERT_COMPOSITE,
)

print(
    "PHASE 10 FULL COMPOSITE SHA256:",
    PHASE10_COMPOSITE,
)

print(
    "PHASE 10 MASTER FREEZE SHA256:",
    MASTER_SHA,
)

print(
    "FINAL CERTIFICATION REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "PHASE 9 MODIFIED: FALSE"
)

print(
    "PHASE 10.1–10.5 MODIFIED DURING 10.6: FALSE"
)

print(
    "UNIVERSAL RUNTIME MODIFIED: FALSE"
)

print()

print(
    "PHASE 10 — OBSERVABILITY: CERTIFIED + FROZEN"
)

print(
    "NEXT: PHASE 11.0 — GOVERNANCE"
)

print("=" * 120)
