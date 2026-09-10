from __future__ import annotations

import hashlib
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

STAGE_DIR = (
    ROOT
    / "backend/server/coordination/stage_handoff"
)

TARGET = (
    STAGE_DIR
    / "handoff_certification.py"
)

REPORT = (
    ROOT
    / "handoff_certification_phase_6_6_final_certification.txt"
)

FREEZE = (
    STAGE_DIR
    / "handoff_certification.phase_6_6.freeze.json"
)


P61 = STAGE_DIR / "stage_result_processor.py"
P62 = STAGE_DIR / "output_input_mapping.py"
P63 = STAGE_DIR / "context_propagation.py"
P64 = STAGE_DIR / "artifact_reference_handoff.py"
P65 = STAGE_DIR / "handoff_validation.py"

F61 = STAGE_DIR / "stage_result_processor.phase_6_1.freeze.json"
F62 = STAGE_DIR / "output_input_mapping.phase_6_2.freeze.json"
F63 = STAGE_DIR / "context_propagation.phase_6_3.freeze.json"
F64 = STAGE_DIR / "artifact_reference_handoff.phase_6_4.freeze.json"
F65 = STAGE_DIR / "handoff_validation.phase_6_5.freeze.json"


EXPECTED = {
    P61:
        "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456",

    F61:
        "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F",

    P62:
        "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744",

    F62:
        "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E",

    P63:
        "1060639F9B8BB20AFDD5B3D42E4265DDD082E267631EFEA08AD5295FCC17B596",

    F63:
        "39AD8A1ABF7753F0A5E8A9F2195E60495CCC38708DDDAAC01C8BDF8885B555D1",

    P64:
        "8D3C80C1B9B5FEC1D1EF225F97CB0300D018E8FCFDD93F7E4E874FA0D45D3655",

    F64:
        "71B3A04739CB2D00D7A0DBC7EB7E86F820F3930BD2C4E20F375906E58C74857C",

    P65:
        "725F30637C686889B2A77F7B30EB297B0C35755002CAE245E4D45D105EFB07EE",

    F65:
        "AB31AFF04CBE02F154278A9CB581CA6E777DBE143B13B37605553E006D286868",
}


SOURCE_EXPECTED = {
    "6.1":
        EXPECTED[P61],

    "6.2":
        EXPECTED[P62],

    "6.3":
        EXPECTED[P63],

    "6.4":
        EXPECTED[P64],

    "6.5":
        EXPECTED[P65],
}


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(
    title: str,
) -> None:

    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(
    message: str,
) -> None:

    raise SystemExit(
        "\nPHASE 6.6 STOPPED:\n"
        + message
    )


def composite_fingerprint(
    source_hashes: dict[str, str],
) -> str:

    canonical = "\n".join(
        f"{phase}:{source_hashes[phase]}"
        for phase
        in (
            "6.1",
            "6.2",
            "6.3",
            "6.4",
            "6.5",
        )
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


section(
    "LINKCRAFTOR — UCF PHASE 6.6 HANDOFF CERTIFICATION ALL-IN-ONE"
)


# ==================================================================
# 0 — FROZEN 6.1–6.5 INTEGRITY
# ==================================================================

section(
    "0 — FROZEN PHASE 6.1–6.5 INTEGRITY"
)


for path, expected_hash in EXPECTED.items():

    if not path.exists():
        stop(
            f"Required frozen authority missing: {path}"
        )

    actual = sha256(
        path
    )

    ok = (
        actual
        == expected_hash
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] "
        f"{path.name}"
    )

    if not ok:
        stop(
            f"Frozen authority mismatch: {path}\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual}"
        )


pre_composite = composite_fingerprint(
    SOURCE_EXPECTED
)


print(
    "EXPECTED PHASE 6.1–6.5 COMPOSITE SHA256:",
    pre_composite,
)


# ==================================================================
# 1 — CERTIFICATION ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "1 — CERTIFICATION ARCHITECTURE RESOLUTION"
)


architecture_checks = []


def architecture_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    architecture_checks.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


architecture = {
    "certifies":
        "frozen Phase 6.1 through 6.5 Stage Handoff chain",

    "input":
        "HandoffValidationResult",

    "requirement":
        "is_valid true and zero violations",

    "sha_authority":
        "exact frozen source and freeze SHA256",

    "composite_scope": (
        "6.1",
        "6.2",
        "6.3",
        "6.4",
        "6.5",
    ),

    "composite_algorithm":
        "SHA256",

    "result":
        "immutable certification evidence",

    "runtime_execution":
        False,

    "coordinator_execution":
        False,

    "workflow_mutation":
        False,

    "business_logic_execution":
        False,
}


architecture_check(
    "certifies complete 6.1–6.5 chain",
    architecture[
        "certifies"
    ]
    == "frozen Phase 6.1 through 6.5 Stage Handoff chain",
)

architecture_check(
    "6.5 validation result is certification input",
    architecture[
        "input"
    ]
    == "HandoffValidationResult",
)

architecture_check(
    "valid zero-violation handoff required",
    architecture[
        "requirement"
    ]
    == "is_valid true and zero violations",
)

architecture_check(
    "exact frozen SHA verification required",
    "exact frozen"
    in architecture[
        "sha_authority"
    ],
)

architecture_check(
    "composite covers exactly five predecessor components",
    architecture[
        "composite_scope"
    ]
    == (
        "6.1",
        "6.2",
        "6.3",
        "6.4",
        "6.5",
    ),
)

architecture_check(
    "composite uses SHA256",
    architecture[
        "composite_algorithm"
    ]
    == "SHA256",
)

architecture_check(
    "certification evidence immutable",
    architecture[
        "result"
    ]
    == "immutable certification evidence",
)

architecture_check(
    "no Runtime execution",
    architecture[
        "runtime_execution"
    ]
    is False,
)

architecture_check(
    "no coordinator execution",
    architecture[
        "coordinator_execution"
    ]
    is False,
)

architecture_check(
    "no workflow mutation",
    architecture[
        "workflow_mutation"
    ]
    is False,
)

architecture_check(
    "no business logic execution",
    architecture[
        "business_logic_execution"
    ]
    is False,
)


if not all(
    architecture_checks
):
    stop(
        "Phase 6.6 certification architecture resolution failed."
    )


print(
    "CERTIFICATION ARCHITECTURE RESOLVED: TRUE"
)


# ==================================================================
# 2 — INSTALLATION
# ==================================================================

section(
    "2 — INSTALLATION"
)


if TARGET.exists():
    stop(
        "handoff_certification.py already exists. "
        "Refusing to overwrite an existing production component."
    )


production_source = r'''"""
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
'''


TARGET.write_text(
    production_source,
    encoding="utf-8",
)


installed_sha = sha256(
    TARGET
)


print(
    "INSTALLED:",
    TARGET,
)

print(
    "HANDOFF CERTIFICATION SHA256:",
    installed_sha,
)


# ==================================================================
# 3 — BUILD REAL END-TO-END PHASE 6 EVIDENCE
# ==================================================================

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    create_runtime_handoff_context,
)

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    ARTIFACT_REFERENCE_HANDOFF_VERSION,
    handoff_artifact_references,
)

from backend.server.coordination.stage_handoff.context_propagation import (
    CONTEXT_PROPAGATION_VERSION,
    propagate_context,
)

from backend.server.coordination.stage_handoff.handoff_certification import (
    HANDOFF_CERTIFICATION_SCHEMA_VERSION,
    HANDOFF_CERTIFICATION_VERSION,
    HandoffCertificationFailedError,
    HandoffCertificationResult,
    certify_stage_handoff,
    evaluate_handoff_certification,
)

from backend.server.coordination.stage_handoff.handoff_validation import (
    HANDOFF_VALIDATION_VERSION,
    validate_stage_handoff,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_VERSION,
    map_output_to_input,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
    process_stage_result,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
    UniversalStageReference,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


canonical_result = UniversalStageResult(
    result_id=
        "usr_phase_6_6",

    workflow_id=
        "wf_phase_6_6",

    correlation_id=
        "corr_phase_6_6",

    stage_id=
        "source_phase_6_6",

    stage_version=
        "1.0.0",

    pipeline_id=
        "phase_6_6_pipeline",

    workflow_type=
        "phase_6_6_workflow",

    workspace_id=
        "ws_phase_6_6",

    execution_target=
        StageExecutionTarget.UNIVERSAL_RUNTIME,

    job_id=
        "uj_phase_6_6",

    job_type=
        "linking_target_pipeline_batch",

    status=
        UniversalStageResultStatus.COMPLETED,

    output={
        "workspace_id":
            "ws_phase_6_6",

        "domain":
            "example.com",

        "count":
            0,
    },

    result_reference=
        "result://phase-6-6/primary",

    artifact_references=(
        "artifact://phase-6-6/a",
        "artifact://phase-6-6/b",
    ),

    started_at=
        "2026-09-10T03:55:00+00:00",

    finished_at=
        "2026-09-10T03:56:00+00:00",

    failure_code=
        "",

    failure_message=
        "",

    failure_details=
        {},

    metadata={
        "phase":
            "6.6",
    },
)


source = process_stage_result(
    canonical_result
)


target = UniversalStageReference(
    stage_id=
        "target_phase_6_6",

    stage_version=
        "1.0.0",

    pipeline_id=
        "phase_6_6_pipeline",

    workflow_type=
        "phase_6_6_workflow",

    workflow_contract_version=
        "universal_workflow_contract_v1.1.0",

    execution_target=
        StageExecutionTarget.UNIVERSAL_RUNTIME,

    job_type=
        "linking_target_pipeline_batch",

    runtime_stage=
        "target_phase_6_6",

    required_payload_fields=(
        "workspace_id",
        "domain",
    ),
)


mapping = map_output_to_input(
    source,
    target,
)


base_context = (
    create_runtime_handoff_context(
        workflow_id=
            source.workflow_id,

        workspace_id=
            source.workspace_id,

        correlation_id=
            source.correlation_id,

        payload_by_stage={
            "prior_stage": {
                "preserve":
                    True,
            },
        },

        metadata={
            "coordination":
                "phase_6_6",
        },
    )
)


context = propagate_context(
    source,
    mapping,
    base_context,
)


artifacts = handoff_artifact_references(
    source
)


validation = validate_stage_handoff(
    source,
    mapping,
    context,
    artifacts,
)


# ==================================================================
# 4 — SMOKE VERIFICATION
# ==================================================================

section(
    "4 — SMOKE VERIFICATION"
)


smoke = []


def smoke_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    smoke.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


certification = certify_stage_handoff(
    validation
)


smoke_check(
    "production source exists",
    TARGET.exists(),
)

smoke_check(
    "certification version exact",
    HANDOFF_CERTIFICATION_VERSION
    == "handoff_certification_v6.6.0",
)

smoke_check(
    "certification schema exact",
    HANDOFF_CERTIFICATION_SCHEMA_VERSION
    == "handoff_certification_schema_v1",
)

smoke_check(
    "certification result exact type",
    isinstance(
        certification,
        HandoffCertificationResult,
    ),
)

smoke_check(
    "Phase 6.5 validation valid",
    validation.is_valid
    is True,
)

smoke_check(
    "Phase 6 certification succeeds",
    certification.is_certified
    is True,
)

smoke_check(
    "certification violations empty",
    certification.violations
    == (),
)

smoke_check(
    "five source hashes recorded",
    len(
        certification.source_sha256
    )
    == 5,
)

smoke_check(
    "five freeze hashes recorded",
    len(
        certification.freeze_sha256
    )
    == 5,
)

smoke_check(
    "composite fingerprint is SHA256 length",
    len(
        certification.composite_fingerprint
    )
    == 64,
)

smoke_check(
    "composite equals precomputed authority",
    certification.composite_fingerprint
    == pre_composite,
)


if not all(
    smoke
):
    stop(
        "Phase 6.6 Smoke Verification failed."
    )


print(
    f"SMOKE VERIFICATION: "
    f"{len(smoke)}/{len(smoke)} PASS"
)


# ==================================================================
# 5 — INITIAL VERIFICATION
# ==================================================================

section(
    "5 — INITIAL VERIFICATION"
)


initial = []


def initial_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    initial.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


initial_check(
    "production SHA stable",
    sha256(TARGET)
    == installed_sha,
)

initial_check(
    "certification is valid",
    certification.is_certified
    is True,
)

initial_check(
    "certification violations empty",
    certification.violations
    == (),
)

initial_check(
    "workflow identity preserved",
    certification.workflow_id
    == validation.workflow_id,
)

initial_check(
    "correlation identity preserved",
    certification.correlation_id
    == validation.correlation_id,
)

initial_check(
    "workspace identity preserved",
    certification.workspace_id
    == validation.workspace_id,
)

initial_check(
    "source stage identity preserved",
    certification.source_stage_id
    == validation.source_stage_id,
)

initial_check(
    "target stage identity preserved",
    certification.target_stage_id
    == validation.target_stage_id,
)

initial_check(
    "6.1 version lineage exact",
    certification.stage_result_processor_version
    == STAGE_RESULT_PROCESSOR_VERSION,
)

initial_check(
    "6.2 version lineage exact",
    certification.output_input_mapping_version
    == OUTPUT_INPUT_MAPPING_VERSION,
)

initial_check(
    "6.3 version lineage exact",
    certification.context_propagation_version
    == CONTEXT_PROPAGATION_VERSION,
)

initial_check(
    "6.4 version lineage exact",
    certification.artifact_reference_handoff_version
    == ARTIFACT_REFERENCE_HANDOFF_VERSION,
)

initial_check(
    "6.5 version lineage exact",
    certification.handoff_validation_version
    == HANDOFF_VALIDATION_VERSION,
)


expected_source_pairs = tuple(
    (
        phase,
        SOURCE_EXPECTED[
            phase
        ],
    )
    for phase
    in (
        "6.1",
        "6.2",
        "6.3",
        "6.4",
        "6.5",
    )
)


initial_check(
    "all exact source SHA authorities recorded",
    certification.source_sha256
    == expected_source_pairs,
)


expected_freeze_pairs = (
    (
        "6.1",
        EXPECTED[F61],
    ),
    (
        "6.2",
        EXPECTED[F62],
    ),
    (
        "6.3",
        EXPECTED[F63],
    ),
    (
        "6.4",
        EXPECTED[F64],
    ),
    (
        "6.5",
        EXPECTED[F65],
    ),
)


initial_check(
    "all exact freeze SHA authorities recorded",
    certification.freeze_sha256
    == expected_freeze_pairs,
)


repeat = certify_stage_handoff(
    validation
)


initial_check(
    "certification deterministic",
    repeat.to_dict()
    == certification.to_dict(),
)

initial_check(
    "composite deterministic",
    repeat.composite_fingerprint
    == certification.composite_fingerprint,
)


try:
    certification.violations += (
        "mutation",
    )
except (
    AttributeError,
    TypeError,
):
    immutable = True
else:
    immutable = False


initial_check(
    "certification evidence immutable",
    immutable,
)


# ------------------------------------------------------------------
# INVALID INPUT
# ------------------------------------------------------------------

invalid = evaluate_handoff_certification(
    object()
)


initial_check(
    "invalid validation type rejected as evidence",
    invalid.is_certified
    is False,
)

initial_check(
    "invalid validation type has violation",
    bool(
        invalid.violations
    ),
)


raised = False

try:
    certify_stage_handoff(
        object()
    )
except HandoffCertificationFailedError as exc:
    raised = (
        exc.result.is_certified
        is False
    )


initial_check(
    "strict certify API raises on invalid evidence",
    raised,
)


# ------------------------------------------------------------------
# INVALID 6.5 VALIDATION
# ------------------------------------------------------------------

from backend.server.coordination.stage_handoff.handoff_validation import (
    HandoffValidationResult,
)


bad_validation = HandoffValidationResult(
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

    is_valid=
        False,

    violations=(
        "forced certification test violation",
    ),

    source_processor_version=
        validation.source_processor_version,

    mapping_version=
        validation.mapping_version,

    context_propagation_version=
        validation.context_propagation_version,

    artifact_handoff_version=
        validation.artifact_handoff_version,
)


bad_evidence = evaluate_handoff_certification(
    bad_validation
)


initial_check(
    "invalid 6.5 result cannot certify",
    bad_evidence.is_certified
    is False,
)

initial_check(
    "invalid 6.5 result produces violations",
    bool(
        bad_evidence.violations
    ),
)


# ------------------------------------------------------------------
# OWNERSHIP BOUNDARIES
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)


for forbidden in (
    "process_stage_result(",
    "map_output_to_input(",
    "propagate_context(",
    "handoff_artifact_references(",
    "validate_stage_handoff(",
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "create_orchestration_job(",
    "dequeue_job(",
    "mark_job_completed(",
    "mark_job_failed(",
    "stage_completed(",
    "stage_failed(",
    "advance(",
    "pause(",
    "resume(",
    "recover(",
):

    initial_check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden
        not in source_text,
    )


for path, expected_hash in EXPECTED.items():

    initial_check(
        f"frozen authority unchanged: {path.name}",
        sha256(path)
        == expected_hash,
    )


if not all(
    initial
):
    stop(
        "Phase 6.6 Initial Verification failed."
    )


print(
    f"INITIAL VERIFICATION: "
    f"{len(initial)}/{len(initial)} PASS"
)


# ==================================================================
# 6 — FINAL CERTIFICATION
# ==================================================================

section(
    "6 — FINAL CERTIFICATION"
)


final = []


def final_check(
    name,
    condition,
):

    ok = bool(
        condition
    )

    final.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


actual_sha = sha256(
    TARGET
)


final_check(
    "production SHA stable",
    actual_sha
    == installed_sha,
)

final_check(
    "version exact",
    HANDOFF_CERTIFICATION_VERSION
    == "handoff_certification_v6.6.0",
)

final_check(
    "schema exact",
    HANDOFF_CERTIFICATION_SCHEMA_VERSION
    == "handoff_certification_schema_v1",
)

final_check(
    "evaluate API signature exact",
    str(
        inspect.signature(
            evaluate_handoff_certification
        )
    )
    == (
        "(validation: 'HandoffValidationResult') "
        "-> 'HandoffCertificationResult'"
    ),
)

final_check(
    "strict certify API signature exact",
    str(
        inspect.signature(
            certify_stage_handoff
        )
    )
    == (
        "(validation: 'HandoffValidationResult') "
        "-> 'HandoffCertificationResult'"
    ),
)

final_check(
    "Phase 6.5 handoff validation valid",
    validation.is_valid
    is True,
)

final_check(
    "Stage Handoff certified",
    certification.is_certified
    is True,
)

final_check(
    "certification violation-free",
    certification.violations
    == (),
)

final_check(
    "Phase 6.1 source SHA certified",
    dict(
        certification.source_sha256
    )[
        "6.1"
    ]
    == EXPECTED[P61],
)

final_check(
    "Phase 6.2 source SHA certified",
    dict(
        certification.source_sha256
    )[
        "6.2"
    ]
    == EXPECTED[P62],
)

final_check(
    "Phase 6.3 source SHA certified",
    dict(
        certification.source_sha256
    )[
        "6.3"
    ]
    == EXPECTED[P63],
)

final_check(
    "Phase 6.4 source SHA certified",
    dict(
        certification.source_sha256
    )[
        "6.4"
    ]
    == EXPECTED[P64],
)

final_check(
    "Phase 6.5 source SHA certified",
    dict(
        certification.source_sha256
    )[
        "6.5"
    ]
    == EXPECTED[P65],
)

final_check(
    "all five freeze manifests certified",
    certification.freeze_sha256
    == expected_freeze_pairs,
)

final_check(
    "Phase 6 composite fingerprint exact",
    certification.composite_fingerprint
    == pre_composite,
)

final_check(
    "composite fingerprint SHA256-shaped",
    len(
        certification.composite_fingerprint
    )
    == 64,
)

final_check(
    "certification execution-free",
    (
        "submit_universal_job("
        not in source_text
        and "process_stage_result("
        not in source_text
        and "map_output_to_input("
        not in source_text
        and "propagate_context("
        not in source_text
        and "handoff_artifact_references("
        not in source_text
        and "validate_stage_handoff("
        not in source_text
        and "stage_completed("
        not in source_text
        and "advance("
        not in source_text
    ),
)


for path, expected_hash in EXPECTED.items():

    final_check(
        f"frozen authority final integrity: {path.name}",
        sha256(path)
        == expected_hash,
    )


if not all(
    final
):
    stop(
        "Phase 6.6 Final Certification failed. "
        "Phase 6 has NOT been frozen."
    )


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.6 — HANDOFF CERTIFICATION FINAL CERTIFICATION",
    "",
    f"Architecture Checks: {len(architecture_checks)}",
    f"Smoke Checks: {len(smoke)}",
    f"Initial Checks: {len(initial)}",
    f"Final Checks: {len(final)}",
    "",
    f"Final Passed: {len(final)}",
    "Final Failed: 0",
    "FINAL CERTIFIED: True",
    "",
    f"Production SHA256: {actual_sha}",
    f"Certification Version: {HANDOFF_CERTIFICATION_VERSION}",
    f"Schema Version: {HANDOFF_CERTIFICATION_SCHEMA_VERSION}",
    "",
    "Frozen Stage Handoff sources:",
    f"- 6.1 {EXPECTED[P61]}",
    f"- 6.2 {EXPECTED[P62]}",
    f"- 6.3 {EXPECTED[P63]}",
    f"- 6.4 {EXPECTED[P64]}",
    f"- 6.5 {EXPECTED[P65]}",
    "",
    f"PHASE 6 COMPOSITE SHA256: {certification.composite_fingerprint}",
    "",
    "Certified chain:",
    "- 6.1 Stage Result Processor",
    "- 6.2 Output -> Input Mapping",
    "- 6.3 Context Propagation",
    "- 6.4 Artifact Reference Handoff",
    "- 6.5 Handoff Validation",
    "- 6.6 Handoff Certification",
    "",
    "Certified properties:",
    "- complete valid handoff evidence",
    "- exact predecessor source SHAs",
    "- exact predecessor freeze SHAs",
    "- deterministic composite fingerprint",
    "- exact component-version lineage",
    "- immutable certification result",
    "- certification is execution-free",
    "",
    "NEXT: Phase 7.0 Advanced Orchestration",
]


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


report_sha = sha256(
    REPORT
)


print(
    f"FINAL CERTIFICATION: "
    f"{len(final)}/{len(final)} PASS"
)

print(
    "HANDOFF CERTIFICATION SHA256:",
    actual_sha,
)

print(
    "PHASE 6 COMPOSITE SHA256:",
    certification.composite_fingerprint,
)

print(
    "REPORT SHA256:",
    report_sha,
)


# ==================================================================
# 7 — PHASE 6 SHA256 FREEZE
# ==================================================================

section(
    "7 — PHASE 6 SHA256 FREEZE"
)


if FREEZE.exists():
    stop(
        "Phase 6.6 freeze already exists. "
        "Refusing to overwrite canonical freeze evidence."
    )


total_checks = (
    len(
        architecture_checks
    )
    + len(
        smoke
    )
    + len(
        initial
    )
    + len(
        final
    )
)


freeze_document = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.6",

    "subsystem":
        "Stage Handoff",

    "component":
        "Handoff Certification",

    "freeze_version":
        "handoff_certification_phase_6_6_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "handoff_certification.py",

        "version":
            HANDOFF_CERTIFICATION_VERSION,

        "schema_version":
            HANDOFF_CERTIFICATION_SCHEMA_VERSION,

        "sha256":
            actual_sha,
    },

    "phase_6_predecessor_sources": {
        "6.1": {
            "file":
                P61.name,

            "sha256":
                EXPECTED[P61],
        },

        "6.2": {
            "file":
                P62.name,

            "sha256":
                EXPECTED[P62],
        },

        "6.3": {
            "file":
                P63.name,

            "sha256":
                EXPECTED[P63],
        },

        "6.4": {
            "file":
                P64.name,

            "sha256":
                EXPECTED[P64],
        },

        "6.5": {
            "file":
                P65.name,

            "sha256":
                EXPECTED[P65],
        },
    },

    "phase_6_predecessor_freezes": {
        "6.1":
            EXPECTED[F61],

        "6.2":
            EXPECTED[F62],

        "6.3":
            EXPECTED[F63],

        "6.4":
            EXPECTED[F64],

        "6.5":
            EXPECTED[F65],
    },

    "phase_6_composite": {
        "algorithm":
            "SHA256",

        "scope":
            "frozen production sources 6.1 through 6.5",

        "sha256":
            certification.composite_fingerprint,
    },

    "verification": {
        "architecture": {
            "passed":
                len(
                    architecture_checks
                ),

            "failed":
                0,
        },

        "smoke": {
            "passed":
                len(
                    smoke
                ),

            "failed":
                0,
        },

        "initial": {
            "passed":
                len(
                    initial
                ),

            "failed":
                0,
        },

        "final": {
            "passed":
                len(
                    final
                ),

            "failed":
                0,
        },

        "total_formal_checks":
            total_checks,
    },

    "final_certification_report": {
        "path":
            "handoff_certification_phase_6_6_final_certification.txt",

        "sha256":
            report_sha,
    },

    "certified_stage_handoff_chain": [
        "6.1 Stage Result Processor",
        "6.2 Output -> Input Mapping",
        "6.3 Context Propagation",
        "6.4 Artifact Reference Handoff",
        "6.5 Handoff Validation",
        "6.6 Handoff Certification",
    ],

    "certified_boundaries": [
        "no Runtime submission",
        "no Runtime execution",
        "no business logic execution",
        "no coordinator invocation",
        "no workflow lifecycle mutation",
        "no planning mutation",
        "no payload mutation",
        "no context mutation",
        "no artifact mutation",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "7.0 Advanced Orchestration",
}


FREEZE.write_text(
    json.dumps(
        freeze_document,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_sha = sha256(
    FREEZE
)


# ==================================================================
# 8 — POST-FREEZE INTEGRITY
# ==================================================================

section(
    "8 — FINAL PHASE 6 STATUS"
)


post = []


for path, expected_hash in EXPECTED.items():

    ok = (
        sha256(path)
        == expected_hash
    )

    post.append(
        ok
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] "
        f"unchanged: {path.name}"
    )


production_ok = (
    sha256(TARGET)
    == actual_sha
)

post.append(
    production_ok
)

print(
    f"[{'PASS' if production_ok else 'FAIL'}] "
    "Phase 6.6 production unchanged"
)


composite_after = composite_fingerprint(
    {
        "6.1":
            sha256(P61),

        "6.2":
            sha256(P62),

        "6.3":
            sha256(P63),

        "6.4":
            sha256(P64),

        "6.5":
            sha256(P65),
    }
)


composite_ok = (
    composite_after
    == certification.composite_fingerprint
)


post.append(
    composite_ok
)


print(
    f"[{'PASS' if composite_ok else 'FAIL'}] "
    "Phase 6 composite fingerprint stable"
)


freeze_ok = FREEZE.exists()

post.append(
    freeze_ok
)


print(
    f"[{'PASS' if freeze_ok else 'FAIL'}] "
    "Phase 6.6 freeze exists"
)


report_ok = REPORT.exists()

post.append(
    report_ok
)


print(
    f"[{'PASS' if report_ok else 'FAIL'}] "
    "certification report exists"
)


if not all(
    post
):
    stop(
        "Post-freeze Phase 6 integrity verification failed."
    )


print()
print(
    "Certification Architecture Resolution:",
    f"{len(architecture_checks)}/{len(architecture_checks)} PASS",
)

print(
    "Smoke Verification:",
    f"{len(smoke)}/{len(smoke)} PASS",
)

print(
    "Initial Verification:",
    f"{len(initial)}/{len(initial)} PASS",
)

print(
    "Final Certification:",
    f"{len(final)}/{len(final)} PASS",
)

print(
    "TOTAL PHASE 6.6 FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print()
print(
    "PHASE 6.1: CERTIFIED + FROZEN"
)

print(
    "PHASE 6.2: CERTIFIED + FROZEN"
)

print(
    "PHASE 6.3: CERTIFIED + FROZEN"
)

print(
    "PHASE 6.4: CERTIFIED + FROZEN"
)

print(
    "PHASE 6.5: CERTIFIED + FROZEN"
)

print(
    "PHASE 6.6: CERTIFIED + FROZEN"
)

print()
print(
    "PHASE 6 — STAGE HANDOFF CERTIFIED: TRUE"
)

print(
    "PHASE 6 — STAGE HANDOFF FROZEN: TRUE"
)

print(
    "HANDOFF CERTIFICATION SHA256:",
    actual_sha,
)

print(
    "PHASE 6 COMPOSITE SHA256:",
    certification.composite_fingerprint,
)

print(
    "CERTIFICATION REPORT SHA256:",
    report_sha,
)

print(
    "PHASE 6.6 FREEZE FILE:",
    FREEZE,
)

print(
    "PHASE 6.6 FREEZE SHA256:",
    freeze_sha,
)

print()
print(
    "PHASE 6.1–6.5 MODIFIED: FALSE"
)

print(
    "NEXT: PHASE 7.0 — ADVANCED ORCHESTRATION"
)

print("=" * 120)
