"""
LinkCraftor — Universal Coordination Framework

Phase 9.7 — Recovery Certification.

Final immutable certification authority for Phase 9.1 through 9.6.

This module verifies:
- exact frozen production source SHA256 values,
- exact predecessor freeze SHA256 values,
- exact Phase 9.1–9.6 composite identity,
- component version lineage.

This component does NOT:
- perform failure classification,
- perform workflow recovery,
- execute compensation,
- perform manual intervention,
- enforce recovery attempts,
- mutate workflow state,
- mutate Runtime state.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Tuple


RECOVERY_CERTIFICATION_VERSION: Final[str] = (
    "recovery_certification_v9.7.0"
)

RECOVERY_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "recovery_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "9.1",
        "failure_policy.py",
        "23FE473EA7EF314238FA8F1DC4256EE329FED6CC59ED31E6724D1173E74688C0",
    ),
    (
        "9.2",
        "terminal_failure_handling.py",
        "45A0F148C9E4F4CBB0AB8517DE09EDFD8E29D448DE9317B50EE39B9AEF65BC02",
    ),
    (
        "9.3",
        "workflow_recovery.py",
        "33307DDFDFBBBEE517634A203A351CBCEEFE58411353AB98F5CE1DCA953C7BD3",
    ),
    (
        "9.4",
        "compensation.py",
        "7391E3A875FF0F50D8A2384B7D41E1BE99A3B94EC8E6CB187CFBB71141417423",
    ),
    (
        "9.5",
        "manual_intervention.py",
        "9E99191F30C95883476491A49A00FEE3A7F334D7496D6EA2694F9D0BFC718B03",
    ),
    (
        "9.6",
        "recovery_loop_protection.py",
        "43A4782DFFC54CAC23103DA0C483DEA192292E0DA84D647079065E682D0ACE92",
    ),
)


_EXPECTED_FREEZE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "9.1",
        "failure_policy.phase_9_1.freeze.json",
        "D77CE26006DA43749073D2C67A3104FBF5F337F219A43B6EF5410E59450AAD6C",
    ),
    (
        "9.2",
        "terminal_failure_handling.phase_9_2.freeze.json",
        "887E01AB2B60FA2153EFC9EF9D8720B5EADAD99E0841A4E79FAB6C9B67E40726",
    ),
    (
        "9.3",
        "workflow_recovery.phase_9_3.freeze.json",
        "0D9486AAB31410237DDE081DAE8773ABDB107456C67B931FA6EE8A38D4E9A979",
    ),
    (
        "9.4",
        "compensation.phase_9_4.freeze.json",
        "881A82B97FDA6C435C00DE18E33DD608D897844641DD0DF879279C2EA4D48BCE",
    ),
    (
        "9.5",
        "manual_intervention.phase_9_5.freeze.json",
        "07BFA1D12A8C2E133AC86A06377D322759F06E8D044150C7F07698F808AC5C3D",
    ),
    (
        "9.6",
        "recovery_loop_protection.phase_9_6.freeze.json",
        "A28D38EFCF04A86269010049A0683FA4B06FA23EC033625AAB794E73B4136693",
    ),
)


EXPECTED_PHASE_9_PRECERT_COMPOSITE: Final[str] = (
    "BA214C149372BA385685B7AF31B13C10E9F6F145EA65A03B1C2D2863E2F84B87"
)


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryCertificationResult:

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
        RECOVERY_CERTIFICATION_VERSION
    )

    schema_version: str = (
        RECOVERY_CERTIFICATION_SCHEMA_VERSION
    )


def _root() -> Path:

    return Path(
        __file__
    ).resolve().parent


def _sha256(
    path: Path,
) -> str:

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


def phase_9_precert_composite(
    source_hashes: Tuple[
        Tuple[str, str],
        ...
    ],
) -> str:

    canonical = "\n".join(
        f"{phase}:{value}"
        for phase, value
        in source_hashes
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def evaluate_recovery_certification(
) -> RecoveryCertificationResult:

    violations = []

    source_hashes = (
        actual_source_hashes()
    )

    freeze_hashes = (
        actual_freeze_hashes()
    )

    expected_sources = {
        phase:
            expected
        for (
            phase,
            _filename,
            expected,
        )
        in _EXPECTED_SOURCE_SHA256
    }

    expected_freezes = {
        phase:
            expected
        for (
            phase,
            _filename,
            expected,
        )
        in _EXPECTED_FREEZE_SHA256
    }

    for phase, actual in source_hashes:

        if (
            actual
            != expected_sources[
                phase
            ]
        ):
            violations.append(
                f"Phase {phase} production SHA256 mismatch"
            )

    for phase, actual in freeze_hashes:

        if (
            actual
            != expected_freezes[
                phase
            ]
        ):
            violations.append(
                f"Phase {phase} freeze SHA256 mismatch"
            )

    composite = phase_9_precert_composite(
        source_hashes
    )

    if (
        composite
        != EXPECTED_PHASE_9_PRECERT_COMPOSITE
    ):
        violations.append(
            "Phase 9.1–9.6 composite mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return RecoveryCertificationResult(
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
    "RECOVERY_CERTIFICATION_VERSION",
    "RECOVERY_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_PHASE_9_PRECERT_COMPOSITE",
    "RecoveryCertificationResult",
    "actual_source_hashes",
    "actual_freeze_hashes",
    "phase_9_precert_composite",
    "evaluate_recovery_certification",
]
