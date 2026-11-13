"""
LinkCraftor — Universal Coordination Framework

Phase 8.7 — Workflow State Persistence Certification.

Certifies frozen Phase 8.1 through 8.6 source and freeze authorities.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Tuple


PERSISTENCE_CERTIFICATION_VERSION: Final[str] = (
    "persistence_certification_v8.7.0"
)

PERSISTENCE_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "persistence_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[tuple[tuple[str, str, str], ...]] = (
    ("8.1", "repository.py", "E7A8379FABF9047F150E24DF4B2B9F138F4CE285C1B3D3EC43DD2F1A454C69DB"),
    ("8.2", "stage_state_store.py", "D7EA771B1461C10166697CF1DCA4B9B90B1D0ECEA7573555204B329EF5E32016"),
    ("8.3", "checkpointing.py", "DB79D0B23BE69387B116EEC470047350F070C5EAC669B97C83E93F6349A19669"),
    ("8.4", "workflow_pause.py", "E731FF3CF9AB81EF8E50E6CC9689E7299629F8641AE882B8B66193CA01A6C2C0"),
    ("8.5", "workflow_resume.py", "97BD18B3F632FF6D38869BDA58885E6CD1F7CB69A35A2333C2723848B8957B42"),
    ("8.6", "restart_recovery.py", "D9CFABD4E3062C5840C363B3639ECADB52D9D71F714808B99A080C988AC45EFC"),
)


_EXPECTED_FREEZE_SHA256: Final[tuple[tuple[str, str, str], ...]] = (
    ("8.1", "workflow_store.phase_8_1.freeze.json", "700DF28A15294D2868794CEF7477082658027345185FEA8BD9EC3D7183D20AC7"),
    ("8.2", "stage_state_store.phase_8_2.freeze.json", "B0067C4525475B2390869BEC5973339AE2E9DAF3735A3586DDF0D5C960B1B421"),
    ("8.3", "checkpointing.phase_8_3.freeze.json", "57CE9CBD368698C27F01E22FE315A301AE8015B8427F1FC42650395031CA163A"),
    ("8.4", "workflow_pause.phase_8_4.freeze.json", "22B08A0431A2DC8D7A35A7FBD6C25F1A790C8E4D223644659EE46028D4BCD23C"),
    ("8.5", "workflow_resume.phase_8_5.freeze.json", "948184003CA8DCCBC24BDCA44AACC9EA4A6A5FFA65F55D04FDD7F808B1A70637"),
    ("8.6", "restart_recovery.phase_8_6.freeze.json", "3CDF7A5E5BA12DDFDE7241A5CA07034D68CCAA82FAFD6201D9C81D8C59B4AA28"),
)


EXPECTED_PHASE_8_COMPOSITE: Final[str] = (
    "82D6A282395EBDE8B8DABDBA845500A229315D3030607F7E7D8D3C5C5E1692D6"
)


@dataclass(frozen=True, slots=True)
class PersistenceCertificationResult:

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

    violations: Tuple[str, ...]

    certification_version: str = (
        PERSISTENCE_CERTIFICATION_VERSION
    )

    schema_version: str = (
        PERSISTENCE_CERTIFICATION_SCHEMA_VERSION
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
        for phase, filename, _expected
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
        for phase, filename, _expected
        in _EXPECTED_FREEZE_SHA256
    )


def phase_8_composite(
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


def evaluate_persistence_certification() -> PersistenceCertificationResult:

    violations = []

    actual_sources = (
        actual_source_hashes()
    )

    actual_freezes = (
        actual_freeze_hashes()
    )

    expected_sources = {
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_SOURCE_SHA256
    }

    expected_freezes = {
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_FREEZE_SHA256
    }

    for phase, actual in actual_sources:

        if (
            actual
            != expected_sources[
                phase
            ]
        ):
            violations.append(
                f"Phase {phase} production SHA256 mismatch"
            )

    for phase, actual in actual_freezes:

        if (
            actual
            != expected_freezes[
                phase
            ]
        ):
            violations.append(
                f"Phase {phase} freeze SHA256 mismatch"
            )

    composite = phase_8_composite(
        actual_sources
    )

    if (
        composite
        != EXPECTED_PHASE_8_COMPOSITE
    ):
        violations.append(
            "Phase 8 composite fingerprint mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return PersistenceCertificationResult(
        is_certified=
            not canonical_violations,

        source_sha256=
            actual_sources,

        freeze_sha256=
            actual_freezes,

        composite_fingerprint=
            composite,

        violations=
            canonical_violations,
    )


__all__ = [
    "PERSISTENCE_CERTIFICATION_VERSION",
    "PERSISTENCE_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_PHASE_8_COMPOSITE",
    "PersistenceCertificationResult",
    "actual_source_hashes",
    "actual_freeze_hashes",
    "phase_8_composite",
    "evaluate_persistence_certification",
]
