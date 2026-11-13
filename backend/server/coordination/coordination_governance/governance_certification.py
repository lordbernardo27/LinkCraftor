"""
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
        "9B19D0FCAC54429C9B7F522538243991E44C315E0B9729B779D7F27E144A9A1F",
    ),
    (
        "11.2",
        "workflow_idempotency.py",
        "AA923FEEE6ACDDD5EC5DFFF42D0235A759CD17163BAB75FAA88D04C4E6B768B1",
    ),
    (
        "11.3",
        "duplicate_protection.py",
        "B44E9C1ECC629BF92F29E6DFCC3E072D18DDA67DE4585D651D32548A7F002FB0",
    ),
    (
        "11.4",
        "version_governance.py",
        "DFB012E6EBB11B98C6501215E060D6DF66A9612ACCABC396F9FDC2188AB1F2CA",
    ),
    (
        "11.5",
        "coordinator_lifecycle.py",
        "8D52B2196BDAB144A82B778A5A4449755E3983DDB852B4D6908FBE495DAF12F3",
    ),
    (
        "11.6",
        "security_boundaries.py",
        "DD5A47D76A368AD72D0B2C8DFF8D00BDB4C35692F8CADDA65EC487DFA1F192C9",
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
        "5E6DF349A0298DCBC4724CC59F1B39E9EED270B5B07947EEA10D7E432EF40A93",
    ),
    (
        "11.2",
        "workflow_idempotency.phase_11_2.freeze.json",
        "222490B973B2E3B28DACA39F3C9DE42705CE90D091FAA9890B0D408A7ABD981F",
    ),
    (
        "11.3",
        "duplicate_protection.phase_11_3.freeze.json",
        "3790A1255E14F05DB8E2B7E2E66D5136EEED7D8D7E0DD6D0F59B62521A9D1A16",
    ),
    (
        "11.4",
        "version_governance.phase_11_4.freeze.json",
        "0E2E4A41377FCE12345B6C2C30DB596E1D0AA2993803C0D84C689ED930082F1C",
    ),
    (
        "11.5",
        "coordinator_lifecycle.phase_11_5.freeze.json",
        "724E38953D17020492B7094E447C346AA45B2BB02CA312C0BA430EA114FBE58C",
    ),
    (
        "11.6",
        "security_boundaries.phase_11_6.freeze.json",
        "E006FED4179FB2C38C830AE88DFBF2C779A0FF8305071603B7C8332675F706A3",
    ),
)


EXPECTED_PRECERT_COMPOSITE: Final[str] = (
    "5B7699C3586578F85C3A382F3113871725CC41AB019B90EF844D75C85BCCFF4E"
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


def evaluate_governance_certification(
) -> GovernanceCertificationResult:

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

        if actual != expected_sources[
            phase
        ]:
            violations.append(
                f"Phase {phase} source SHA256 mismatch"
            )

    for phase, actual in freeze_hashes:

        if actual != expected_freezes[
            phase
        ]:
            violations.append(
                f"Phase {phase} freeze SHA256 mismatch"
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
