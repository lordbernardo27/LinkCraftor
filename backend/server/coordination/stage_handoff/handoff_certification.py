"""
LinkCraftor
Universal Coordination Framework

PHASE 6.6 — Handoff Certification

Certifies the complete frozen Stage Handoff chain:

6.1 Stage Result Processor
6.2 Output -> Input Mapping
6.3 Context Propagation
6.4 Artifact Reference Handoff
6.5 Handoff Validation

Pattern
-------
Phase 6.6 follows the established UCF subsystem certification pattern:

- consume immutable validation evidence,
- verify exact frozen predecessor source SHA256 values,
- verify exact predecessor freeze-manifest SHA256 values,
- verify component version lineage,
- generate deterministic certification evidence,
- compute a deterministic composite SHA256 fingerprint over frozen
  production components 6.1 through 6.5.

Phase 6.6 does not:
- process Runtime results,
- map payloads,
- propagate context,
- hand off artifacts,
- submit Runtime work,
- invoke coordinators,
- advance workflow state,
- execute business logic.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Tuple

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    ARTIFACT_REFERENCE_HANDOFF_VERSION,
)

from backend.server.coordination.stage_handoff.context_propagation import (
    CONTEXT_PROPAGATION_VERSION,
)

from backend.server.coordination.stage_handoff.handoff_validation import (
    HANDOFF_VALIDATION_VERSION,
    HandoffValidationResult,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_VERSION,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
)


HANDOFF_CERTIFICATION_VERSION: Final[str] = (
    "handoff_certification_v6.6.0"
)

HANDOFF_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "handoff_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "6.1",
        "stage_result_processor.py",
        "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456",
    ),
    (
        "6.2",
        "output_input_mapping.py",
        "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744",
    ),
    (
        "6.3",
        "context_propagation.py",
        "1060639F9B8BB20AFDD5B3D42E4265DDD082E267631EFEA08AD5295FCC17B596",
    ),
    (
        "6.4",
        "artifact_reference_handoff.py",
        "8D3C80C1B9B5FEC1D1EF225F97CB0300D018E8FCFDD93F7E4E874FA0D45D3655",
    ),
    (
        "6.5",
        "handoff_validation.py",
        "725F30637C686889B2A77F7B30EB297B0C35755002CAE245E4D45D105EFB07EE",
    ),
)


_EXPECTED_FREEZE_SHA256: Final[
    tuple[
        tuple[str, str, str],
        ...
    ]
] = (
    (
        "6.1",
        "stage_result_processor.phase_6_1.freeze.json",
        "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F",
    ),
    (
        "6.2",
        "output_input_mapping.phase_6_2.freeze.json",
        "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E",
    ),
    (
        "6.3",
        "context_propagation.phase_6_3.freeze.json",
        "39AD8A1ABF7753F0A5E8A9F2195E60495CCC38708DDDAAC01C8BDF8885B555D1",
    ),
    (
        "6.4",
        "artifact_reference_handoff.phase_6_4.freeze.json",
        "71B3A04739CB2D00D7A0DBC7EB7E86F820F3930BD2C4E20F375906E58C74857C",
    ),
    (
        "6.5",
        "handoff_validation.phase_6_5.freeze.json",
        "AB31AFF04CBE02F154278A9CB581CA6E777DBE143B13B37605553E006D286868",
    ),
)


class HandoffCertificationFailedError(
    ValueError
):
    """
    Raised when the complete frozen Stage Handoff chain cannot be certified.
    """

    def __init__(
        self,
        message: str,
        *,
        result: "HandoffCertificationResult",
    ) -> None:

        super().__init__(
            message
        )

        self.result = result


@dataclass(
    frozen=True,
    slots=True,
)
class HandoffCertificationResult:

    is_certified: bool

    workflow_id: str
    correlation_id: str
    workspace_id: str
    source_stage_id: str
    target_stage_id: str

    violations: Tuple[str, ...]

    source_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    freeze_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    composite_fingerprint: str

    stage_result_processor_version: str
    output_input_mapping_version: str
    context_propagation_version: str
    artifact_reference_handoff_version: str
    handoff_validation_version: str

    certification_version: str = (
        HANDOFF_CERTIFICATION_VERSION
    )

    schema_version: str = (
        HANDOFF_CERTIFICATION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "is_certified":
                self.is_certified,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "source_stage_id":
                self.source_stage_id,

            "target_stage_id":
                self.target_stage_id,

            "violations":
                list(
                    self.violations
                ),

            "source_sha256": {
                phase:
                    value
                for phase, value
                in self.source_sha256
            },

            "freeze_sha256": {
                phase:
                    value
                for phase, value
                in self.freeze_sha256
            },

            "composite_fingerprint":
                self.composite_fingerprint,

            "stage_result_processor_version":
                self.stage_result_processor_version,

            "output_input_mapping_version":
                self.output_input_mapping_version,

            "context_propagation_version":
                self.context_propagation_version,

            "artifact_reference_handoff_version":
                self.artifact_reference_handoff_version,

            "handoff_validation_version":
                self.handoff_validation_version,

            "certification_version":
                self.certification_version,

            "schema_version":
                self.schema_version,
        }


def _sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def _stage_handoff_root() -> Path:

    return Path(
        __file__
    ).resolve().parent


def _actual_source_hashes() -> tuple[
    tuple[str, str],
    ...
]:

    root = _stage_handoff_root()

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


def _actual_freeze_hashes() -> tuple[
    tuple[str, str],
    ...
]:

    root = _stage_handoff_root()

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


def _phase_6_composite_fingerprint(
    source_hashes: tuple[
        tuple[str, str],
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


def evaluate_handoff_certification(
    validation: HandoffValidationResult,
) -> HandoffCertificationResult:

    violations: list[str] = []

    if not isinstance(
        validation,
        HandoffValidationResult,
    ):

        return HandoffCertificationResult(
            is_certified=False,
            workflow_id="",
            correlation_id="",
            workspace_id="",
            source_stage_id="",
            target_stage_id="",
            violations=(
                "validation must be HandoffValidationResult",
            ),
            source_sha256=(),
            freeze_sha256=(),
            composite_fingerprint="",
            stage_result_processor_version=
                STAGE_RESULT_PROCESSOR_VERSION,
            output_input_mapping_version=
                OUTPUT_INPUT_MAPPING_VERSION,
            context_propagation_version=
                CONTEXT_PROPAGATION_VERSION,
            artifact_reference_handoff_version=
                ARTIFACT_REFERENCE_HANDOFF_VERSION,
            handoff_validation_version=
                HANDOFF_VALIDATION_VERSION,
        )

    if not validation.is_valid:
        violations.append(
            "Phase 6.5 handoff validation is not valid"
        )

    if validation.violations:
        violations.append(
            "Phase 6.5 handoff validation contains violations"
        )

    if (
        validation.source_processor_version
        != STAGE_RESULT_PROCESSOR_VERSION
    ):
        violations.append(
            "Phase 6.1 version lineage mismatch"
        )

    if (
        validation.mapping_version
        != OUTPUT_INPUT_MAPPING_VERSION
    ):
        violations.append(
            "Phase 6.2 version lineage mismatch"
        )

    if (
        validation.context_propagation_version
        != CONTEXT_PROPAGATION_VERSION
    ):
        violations.append(
            "Phase 6.3 version lineage mismatch"
        )

    if (
        validation.artifact_handoff_version
        != ARTIFACT_REFERENCE_HANDOFF_VERSION
    ):
        violations.append(
            "Phase 6.4 version lineage mismatch"
        )

    if (
        validation.validation_version
        != HANDOFF_VALIDATION_VERSION
    ):
        violations.append(
            "Phase 6.5 version lineage mismatch"
        )

    actual_source_hashes = (
        _actual_source_hashes()
    )

    expected_source_hashes = {
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_SOURCE_SHA256
    }

    for phase, actual in actual_source_hashes:

        expected = (
            expected_source_hashes[
                phase
            ]
        )

        if actual != expected:
            violations.append(
                f"Frozen Phase {phase} production SHA256 mismatch"
            )

    actual_freeze_hashes = (
        _actual_freeze_hashes()
    )

    expected_freeze_hashes = {
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_FREEZE_SHA256
    }

    for phase, actual in actual_freeze_hashes:

        expected = (
            expected_freeze_hashes[
                phase
            ]
        )

        if actual != expected:
            violations.append(
                f"Frozen Phase {phase} freeze SHA256 mismatch"
            )

    composite = (
        _phase_6_composite_fingerprint(
            actual_source_hashes
        )
    )

    canonical_violations = tuple(
        violations
    )

    return HandoffCertificationResult(
        is_certified=
            not canonical_violations,

        workflow_id=
            validation.workflow_id,

        correlation_id=
            validation.correlation_id,

        workspace_id=
            validation.workspace_id,

        source_stage_id=
            validation.source_stage_id,

        target_stage_id=
            validation.target_stage_id,

        violations=
            canonical_violations,

        source_sha256=
            actual_source_hashes,

        freeze_sha256=
            actual_freeze_hashes,

        composite_fingerprint=
            composite,

        stage_result_processor_version=
            STAGE_RESULT_PROCESSOR_VERSION,

        output_input_mapping_version=
            OUTPUT_INPUT_MAPPING_VERSION,

        context_propagation_version=
            CONTEXT_PROPAGATION_VERSION,

        artifact_reference_handoff_version=
            ARTIFACT_REFERENCE_HANDOFF_VERSION,

        handoff_validation_version=
            HANDOFF_VALIDATION_VERSION,
    )


def certify_stage_handoff(
    validation: HandoffValidationResult,
) -> HandoffCertificationResult:

    result = (
        evaluate_handoff_certification(
            validation
        )
    )

    if not result.is_certified:

        raise HandoffCertificationFailedError(
            "Stage Handoff certification failed.",
            result=result,
        )

    return result


__all__ = [
    "HANDOFF_CERTIFICATION_VERSION",
    "HANDOFF_CERTIFICATION_SCHEMA_VERSION",
    "HandoffCertificationFailedError",
    "HandoffCertificationResult",
    "evaluate_handoff_certification",
    "certify_stage_handoff",
]
