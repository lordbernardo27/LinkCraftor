"""
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
        "D4D90A849ACA95643314B96673017E8198EC65DAF03B205CBF3FD6BCB9066AC9",
    ),
    (
        "10.2",
        "workflow_metrics.py",
        "C3E31D561431994507B18F8A852303A12CC082D2CE19352F45406A17815F6D42",
    ),
    (
        "10.3",
        "stage_metrics.py",
        "DC1BFB42187C358EB46662FDA0BB68AB62E461A4D7C8305BDF64BB19FA7EA290",
    ),
    (
        "10.4",
        "workflow_evidence.py",
        "AB2D613AE8CFF291FF6C955F10F41200A1D7A405653646D6624A774236597E83",
    ),
    (
        "10.5",
        "audit_trail.py",
        "73B122F771C9FB859ABD5B16A03192F2A0EEB8EA66A9B3A815085B2DF26982D9",
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
        "86AF29FA6B281D3D0E5FFCD0132A4A6B9C33487F07A4FE6DFA5894F9C411C75A",
    ),
    (
        "10.2",
        "workflow_metrics.phase_10_2.freeze.json",
        "AF336ADBB78B1B048B3C3124DC2E8A05ED3CD14F3A86AFA572E332D9E7BC8F23",
    ),
    (
        "10.3",
        "stage_metrics.phase_10_3.freeze.json",
        "D397E6EEF2FB92A17579A605C5BB0B5894D506695408AC60C68411ED549B8790",
    ),
    (
        "10.4",
        "workflow_evidence.phase_10_4.freeze.json",
        "03C1BC75E5CDDC2A6DE319B2603C7C93CF27BF411F746258065DD40612922D51",
    ),
    (
        "10.5",
        "audit_trail.phase_10_5.freeze.json",
        "41FC9212F0FEDD832B275AA13EB339DA7E6CB29A5C60E7AA050CF4A54BB57769",
    ),
)


EXPECTED_PRECERT_COMPOSITE: Final[str] = (
    "5F27777BCDC8860EF5CF8B6461E069FD3A6EA0BA3498EBEC2D9B224DB7AA57FF"
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


def evaluate_observability_certification(
) -> ObservabilityCertificationResult:

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
                f"Phase {phase} source SHA256 mismatch"
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
