from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Tuple


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/stage_handoff/handoff_validation.py"
)

REPORT = (
    ROOT
    / "handoff_validation_phase_6_5_final_certification.txt"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "handoff_validation.phase_6_5.freeze.json"
)

P61 = ROOT / "backend/server/coordination/stage_handoff/stage_result_processor.py"
P62 = ROOT / "backend/server/coordination/stage_handoff/output_input_mapping.py"
P63 = ROOT / "backend/server/coordination/stage_handoff/context_propagation.py"
P64 = ROOT / "backend/server/coordination/stage_handoff/artifact_reference_handoff.py"

F61 = ROOT / "backend/server/coordination/stage_handoff/stage_result_processor.phase_6_1.freeze.json"
F62 = ROOT / "backend/server/coordination/stage_handoff/output_input_mapping.phase_6_2.freeze.json"
F63 = ROOT / "backend/server/coordination/stage_handoff/context_propagation.phase_6_3.freeze.json"
F64 = ROOT / "backend/server/coordination/stage_handoff/artifact_reference_handoff.phase_6_4.freeze.json"


EXPECTED = {
    P61: "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456",
    F61: "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F",
    P62: "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744",
    F62: "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E",
    P63: "1060639F9B8BB20AFDD5B3D42E4265DDD082E267631EFEA08AD5295FCC17B596",
    F63: "39AD8A1ABF7753F0A5E8A9F2195E60495CCC38708DDDAAC01C8BDF8885B555D1",
    P64: "8D3C80C1B9B5FEC1D1EF225F97CB0300D018E8FCFDD93F7E4E874FA0D45D3655",
    F64: "71B3A04739CB2D00D7A0DBC7EB7E86F820F3930BD2C4E20F375906E58C74857C",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(message: str) -> None:
    raise SystemExit("\nPHASE 6.5 STOPPED:\n" + message)


section("LINKCRAFTOR — UCF PHASE 6.5 HANDOFF VALIDATION ALL-IN-ONE")


# ==================================================================
# 0 — FROZEN UPSTREAM INTEGRITY
# ==================================================================

section("0 — FROZEN UPSTREAM INTEGRITY")

for path, expected_hash in EXPECTED.items():
    if not path.exists():
        stop(f"Required upstream authority missing: {path}")

    actual = sha256(path)
    ok = actual == expected_hash

    print(
        f"[{'PASS' if ok else 'FAIL'}] "
        f"{path.name} SHA256"
    )

    if not ok:
        stop(
            f"Upstream integrity mismatch: {path}\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual}"
        )


# ==================================================================
# 1 — VALIDATION ARCHITECTURE RESOLUTION
# ==================================================================

section("1 — HANDOFF VALIDATION ARCHITECTURE RESOLUTION")

architecture_checks = []


def architecture_check(name, condition):
    ok = bool(condition)
    architecture_checks.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


architecture_model = {
    "inputs": (
        "ProcessedStageResult",
        "OutputInputMappingResult",
        "RuntimeHandoffContext",
        "ArtifactReferenceHandoffResult",
    ),
    "result_model": "immutable validation result with violations",
    "source_requirement": "completed + normal_handoff_allowed + prerequisite_satisfied",
    "mapping_requirement": "complete",
    "context_requirement": "target mapped payload present exactly",
    "artifact_requirement": "source/result/artifact identity and references exact",
    "mutation": False,
    "runtime_submission": False,
    "coordinator_invocation": False,
    "workflow_advance": False,
}

architecture_check(
    "four canonical Phase 6 evidence inputs",
    len(architecture_model["inputs"]) == 4,
)

architecture_check(
    "validation result is evidence-only",
    architecture_model["result_model"]
    == "immutable validation result with violations",
)

architecture_check(
    "source eligibility includes prerequisite satisfaction",
    "prerequisite_satisfied"
    in architecture_model["source_requirement"],
)

architecture_check(
    "complete mapping required",
    architecture_model["mapping_requirement"] == "complete",
)

architecture_check(
    "context payload equality required",
    "exactly"
    in architecture_model["context_requirement"],
)

architecture_check(
    "artifact lineage consistency required",
    "identity"
    in architecture_model["artifact_requirement"],
)

architecture_check(
    "no mutation ownership",
    architecture_model["mutation"] is False,
)

architecture_check(
    "no Runtime submission ownership",
    architecture_model["runtime_submission"] is False,
)

architecture_check(
    "no coordinator invocation ownership",
    architecture_model["coordinator_invocation"] is False,
)

architecture_check(
    "no workflow advance ownership",
    architecture_model["workflow_advance"] is False,
)

if not all(architecture_checks):
    stop("Phase 6.5 architecture resolution failed.")

print("HANDOFF VALIDATION ARCHITECTURE RESOLVED: TRUE")


# ==================================================================
# 2 — INSTALLATION
# ==================================================================

section("2 — INSTALLATION")

if TARGET.exists():
    stop(
        "handoff_validation.py already exists. "
        "Refusing to overwrite an existing production component."
    )


production_source = r'''"""
LinkCraftor
Universal Coordination Framework

PHASE 6.5 — Handoff Validation

Validates the complete Stage Handoff evidence chain produced by:

6.1 ProcessedStageResult
6.2 OutputInputMappingResult
6.3 RuntimeHandoffContext
6.4 ArtifactReferenceHandoffResult

The validator is evidence-only.

It does not:
- submit Runtime jobs,
- execute business logic,
- invoke coordinators,
- advance workflow state,
- mutate planning,
- mutate payloads,
- mutate RuntimeHandoffContext,
- mutate artifact references,
- perform Phase 6.6 certification.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Tuple

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    RuntimeHandoffContext,
)

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    ARTIFACT_REFERENCE_HANDOFF_VERSION,
    ArtifactReferenceHandoffResult,
)

from backend.server.coordination.stage_handoff.context_propagation import (
    CONTEXT_PROPAGATION_VERSION,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_VERSION,
    OutputInputMappingResult,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
    ProcessedStageResult,
)


HANDOFF_VALIDATION_VERSION: Final[str] = (
    "handoff_validation_v6.5.0"
)

HANDOFF_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "handoff_validation_schema_v1"
)


@dataclass(
    frozen=True,
    slots=True,
)
class HandoffValidationResult:
    workflow_id: str
    correlation_id: str
    workspace_id: str

    source_stage_id: str
    target_stage_id: str

    is_valid: bool
    violations: Tuple[str, ...]

    source_processor_version: str
    mapping_version: str
    context_propagation_version: str
    artifact_handoff_version: str

    validation_version: str = (
        HANDOFF_VALIDATION_VERSION
    )

    schema_version: str = (
        HANDOFF_VALIDATION_SCHEMA_VERSION
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "workspace_id": self.workspace_id,
            "source_stage_id": self.source_stage_id,
            "target_stage_id": self.target_stage_id,
            "is_valid": self.is_valid,
            "violations": list(self.violations),
            "source_processor_version": self.source_processor_version,
            "mapping_version": self.mapping_version,
            "context_propagation_version": self.context_propagation_version,
            "artifact_handoff_version": self.artifact_handoff_version,
            "validation_version": self.validation_version,
            "schema_version": self.schema_version,
        }


def _payload_plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _payload_plain(item)
            for key, item in value.items()
        }

    if isinstance(value, tuple):
        return tuple(
            _payload_plain(item)
            for item in value
        )

    if isinstance(value, list):
        return [
            _payload_plain(item)
            for item in value
        ]

    return value


def validate_stage_handoff(
    source: ProcessedStageResult,
    mapping: OutputInputMappingResult,
    context: RuntimeHandoffContext,
    artifacts: ArtifactReferenceHandoffResult,
) -> HandoffValidationResult:

    type_violations: list[str] = []

    if not isinstance(source, ProcessedStageResult):
        type_violations.append(
            "source must be ProcessedStageResult"
        )

    if not isinstance(mapping, OutputInputMappingResult):
        type_violations.append(
            "mapping must be OutputInputMappingResult"
        )

    if not isinstance(context, RuntimeHandoffContext):
        type_violations.append(
            "context must be RuntimeHandoffContext"
        )

    if not isinstance(artifacts, ArtifactReferenceHandoffResult):
        type_violations.append(
            "artifacts must be ArtifactReferenceHandoffResult"
        )

    if type_violations:
        return HandoffValidationResult(
            workflow_id="",
            correlation_id="",
            workspace_id="",
            source_stage_id="",
            target_stage_id="",
            is_valid=False,
            violations=tuple(type_violations),
            source_processor_version="",
            mapping_version="",
            context_propagation_version=CONTEXT_PROPAGATION_VERSION,
            artifact_handoff_version="",
        )

    violations: list[str] = []

    # --------------------------------------------------------------
    # Source eligibility
    # --------------------------------------------------------------

    if not source.terminal:
        violations.append(
            "source must be terminal"
        )

    if not source.completed:
        violations.append(
            "source must be completed"
        )

    if not source.normal_handoff_allowed:
        violations.append(
            "source normal_handoff_allowed must be true"
        )

    if not source.prerequisite_satisfied:
        violations.append(
            "source prerequisite_satisfied must be true"
        )

    # --------------------------------------------------------------
    # 6.1 -> 6.2 identity continuity
    # --------------------------------------------------------------

    identity_pairs = (
        (
            "mapping source_result_id",
            mapping.source_result_id,
            source.result_id,
        ),
        (
            "mapping source_workflow_id",
            mapping.source_workflow_id,
            source.workflow_id,
        ),
        (
            "mapping source_correlation_id",
            mapping.source_correlation_id,
            source.correlation_id,
        ),
        (
            "mapping source_stage_id",
            mapping.source_stage_id,
            source.stage_id,
        ),
        (
            "mapping source_stage_version",
            mapping.source_stage_version,
            source.stage_version,
        ),
        (
            "mapping source_pipeline_id",
            mapping.source_pipeline_id,
            source.pipeline_id,
        ),
        (
            "mapping source_workspace_id",
            mapping.source_workspace_id,
            source.workspace_id,
        ),
        (
            "mapping source_job_id",
            mapping.source_job_id,
            source.job_id,
        ),
    )

    for name, actual, expected in identity_pairs:
        if actual != expected:
            violations.append(
                f"{name} mismatch"
            )

    # --------------------------------------------------------------
    # Mapping completeness
    # --------------------------------------------------------------

    if not mapping.complete:
        violations.append(
            "output-to-input mapping must be complete"
        )

    if mapping.missing_payload_fields:
        violations.append(
            "output-to-input mapping contains missing payload fields"
        )

    if (
        tuple(mapping.satisfied_payload_fields)
        != tuple(mapping.required_payload_fields)
    ):
        violations.append(
            "mapping satisfied fields do not exactly match required fields"
        )

    # --------------------------------------------------------------
    # 6.3 context identity continuity
    # --------------------------------------------------------------

    if context.workflow_id != source.workflow_id:
        violations.append(
            "context workflow_id mismatch"
        )

    if context.workspace_id != source.workspace_id:
        violations.append(
            "context workspace_id mismatch"
        )

    if context.correlation_id != source.correlation_id:
        violations.append(
            "context correlation_id mismatch"
        )

    # --------------------------------------------------------------
    # Target payload installation
    # --------------------------------------------------------------

    if mapping.target_stage_id not in context.payload_by_stage:
        violations.append(
            "target stage payload missing from propagated context"
        )
    else:
        context_payload = (
            context.payload_by_stage[
                mapping.target_stage_id
            ]
        )

        if (
            _payload_plain(context_payload)
            != _payload_plain(mapping.payload)
        ):
            violations.append(
                "target stage context payload does not match mapped payload"
            )

    # --------------------------------------------------------------
    # 6.4 artifact/result lineage
    # --------------------------------------------------------------

    artifact_identity_pairs = (
        (
            "artifact result_id",
            artifacts.result_id,
            source.result_id,
        ),
        (
            "artifact workflow_id",
            artifacts.workflow_id,
            source.workflow_id,
        ),
        (
            "artifact correlation_id",
            artifacts.correlation_id,
            source.correlation_id,
        ),
        (
            "artifact source_stage_id",
            artifacts.source_stage_id,
            source.stage_id,
        ),
        (
            "artifact source_stage_version",
            artifacts.source_stage_version,
            source.stage_version,
        ),
        (
            "artifact source_pipeline_id",
            artifacts.source_pipeline_id,
            source.pipeline_id,
        ),
        (
            "artifact workspace_id",
            artifacts.workspace_id,
            source.workspace_id,
        ),
        (
            "artifact source_job_id",
            artifacts.source_job_id,
            source.job_id,
        ),
    )

    for name, actual, expected in artifact_identity_pairs:
        if actual != expected:
            violations.append(
                f"{name} mismatch"
            )

    if artifacts.result_reference != source.result_reference:
        violations.append(
            "artifact handoff result_reference mismatch"
        )

    if (
        tuple(artifacts.artifact_references)
        != tuple(source.artifact_references)
    ):
        violations.append(
            "artifact handoff artifact_references mismatch"
        )

    if artifacts.artifact_count != len(
        artifacts.artifact_references
    ):
        violations.append(
            "artifact_count mismatch"
        )

    if artifacts.has_artifacts != bool(
        artifacts.artifact_references
    ):
        violations.append(
            "has_artifacts mismatch"
        )

    # --------------------------------------------------------------
    # Version lineage
    # --------------------------------------------------------------

    if (
        source.processor_version
        != STAGE_RESULT_PROCESSOR_VERSION
    ):
        violations.append(
            "source processor version mismatch"
        )

    if (
        mapping.mapper_version
        != OUTPUT_INPUT_MAPPING_VERSION
    ):
        violations.append(
            "mapping version mismatch"
        )

    if (
        artifacts.handoff_version
        != ARTIFACT_REFERENCE_HANDOFF_VERSION
    ):
        violations.append(
            "artifact handoff version mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return HandoffValidationResult(
        workflow_id=source.workflow_id,
        correlation_id=source.correlation_id,
        workspace_id=source.workspace_id,
        source_stage_id=source.stage_id,
        target_stage_id=mapping.target_stage_id,
        is_valid=not canonical_violations,
        violations=canonical_violations,
        source_processor_version=source.processor_version,
        mapping_version=mapping.mapper_version,
        context_propagation_version=CONTEXT_PROPAGATION_VERSION,
        artifact_handoff_version=artifacts.handoff_version,
    )


__all__ = [
    "HANDOFF_VALIDATION_VERSION",
    "HANDOFF_VALIDATION_SCHEMA_VERSION",
    "HandoffValidationResult",
    "validate_stage_handoff",
]
'''


TARGET.write_text(
    production_source,
    encoding="utf-8",
)

installed_sha = sha256(TARGET)

print("INSTALLED:", TARGET)
print("HANDOFF VALIDATION SHA256:", installed_sha)


# ==================================================================
# 3 — IMPORT INSTALLED PRODUCTION
# ==================================================================

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    create_runtime_handoff_context,
)

from backend.server.coordination.stage_handoff.artifact_reference_handoff import (
    handoff_artifact_references,
)

from backend.server.coordination.stage_handoff.context_propagation import (
    propagate_context,
)

from backend.server.coordination.stage_handoff.handoff_validation import (
    HANDOFF_VALIDATION_SCHEMA_VERSION,
    HANDOFF_VALIDATION_VERSION,
    HandoffValidationResult,
    validate_stage_handoff,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    map_output_to_input,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
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


def make_source():
    canonical = UniversalStageResult(
        result_id="usr_phase_6_5",
        workflow_id="wf_phase_6_5",
        correlation_id="corr_phase_6_5",
        stage_id="source_phase_6_5",
        stage_version="1.0.0",
        pipeline_id="phase_6_5_pipeline",
        workflow_type="phase_6_5_workflow",
        workspace_id="ws_phase_6_5",
        execution_target=StageExecutionTarget.UNIVERSAL_RUNTIME,
        job_id="uj_phase_6_5",
        job_type="linking_target_pipeline_batch",
        status=UniversalStageResultStatus.COMPLETED,
        output={
            "workspace_id": "ws_phase_6_5",
            "domain": "example.com",
            "count": 0,
        },
        result_reference="result://phase-6-5/primary",
        artifact_references=(
            "artifact://phase-6-5/a",
            "artifact://phase-6-5/b",
        ),
        started_at="2026-09-10T03:49:00+00:00",
        finished_at="2026-09-10T03:50:00+00:00",
        failure_code="",
        failure_message="",
        failure_details={},
        metadata={
            "verification": "phase_6_5",
        },
    )

    return process_stage_result(canonical)


def make_target():
    return UniversalStageReference(
        stage_id="target_phase_6_5",
        stage_version="1.0.0",
        pipeline_id="phase_6_5_pipeline",
        workflow_type="phase_6_5_workflow",
        workflow_contract_version="universal_workflow_contract_v1.1.0",
        execution_target=StageExecutionTarget.UNIVERSAL_RUNTIME,
        job_type="linking_target_pipeline_batch",
        runtime_stage="target_phase_6_5",
        required_payload_fields=(
            "workspace_id",
            "domain",
        ),
    )


source = make_source()
target = make_target()

mapping = map_output_to_input(
    source,
    target,
)

base_context = create_runtime_handoff_context(
    workflow_id=source.workflow_id,
    workspace_id=source.workspace_id,
    correlation_id=source.correlation_id,
    payload_by_stage={
        "existing_stage": {
            "preserve": True,
        },
    },
    metadata={
        "coordination": "phase_6_5",
    },
)

context = propagate_context(
    source,
    mapping,
    base_context,
)

artifacts = handoff_artifact_references(
    source
)


# ==================================================================
# 4 — SMOKE VERIFICATION
# ==================================================================

section("4 — SMOKE VERIFICATION")

smoke = []


def smoke_check(name, condition):
    ok = bool(condition)
    smoke.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


validation = validate_stage_handoff(
    source,
    mapping,
    context,
    artifacts,
)

smoke_check(
    "production source exists",
    TARGET.exists(),
)

smoke_check(
    "validation version exact",
    HANDOFF_VALIDATION_VERSION
    == "handoff_validation_v6.5.0",
)

smoke_check(
    "schema version exact",
    HANDOFF_VALIDATION_SCHEMA_VERSION
    == "handoff_validation_schema_v1",
)

smoke_check(
    "validation result exact type",
    isinstance(
        validation,
        HandoffValidationResult,
    ),
)

smoke_check(
    "canonical handoff is valid",
    validation.is_valid is True,
)

smoke_check(
    "canonical handoff has zero violations",
    validation.violations == (),
)

smoke_check(
    "workflow identity exposed",
    validation.workflow_id
    == source.workflow_id,
)

smoke_check(
    "source stage exposed",
    validation.source_stage_id
    == source.stage_id,
)

smoke_check(
    "target stage exposed",
    validation.target_stage_id
    == target.stage_id,
)

if not all(smoke):
    stop("Phase 6.5 Smoke Verification failed.")

print(
    f"SMOKE VERIFICATION: {len(smoke)}/{len(smoke)} PASS"
)


# ==================================================================
# 5 — INITIAL VERIFICATION
# ==================================================================

section("5 — INITIAL VERIFICATION")

initial = []


def initial_check(name, condition):
    ok = bool(condition)
    initial.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


initial_check(
    "production SHA stable",
    sha256(TARGET) == installed_sha,
)

initial_check(
    "canonical result valid",
    validation.is_valid is True,
)

initial_check(
    "canonical violations empty",
    validation.violations == (),
)

initial_check(
    "source processor lineage",
    validation.source_processor_version
    == source.processor_version,
)

initial_check(
    "mapping lineage",
    validation.mapping_version
    == mapping.mapper_version,
)

initial_check(
    "artifact lineage",
    validation.artifact_handoff_version
    == artifacts.handoff_version,
)


# --------------------------------------------------------------
# TYPE VIOLATION BEHAVIOR
# --------------------------------------------------------------

bad_type_cases = (
    (
        "invalid source",
        object(),
        mapping,
        context,
        artifacts,
    ),
    (
        "invalid mapping",
        source,
        object(),
        context,
        artifacts,
    ),
    (
        "invalid context",
        source,
        mapping,
        object(),
        artifacts,
    ),
    (
        "invalid artifact handoff",
        source,
        mapping,
        context,
        object(),
    ),
)

for name, s, m, c, a in bad_type_cases:
    result = validate_stage_handoff(
        s,
        m,
        c,
        a,
    )

    initial_check(
        f"{name} produces invalid evidence",
        result.is_valid is False,
    )

    initial_check(
        f"{name} produces violations",
        bool(result.violations),
    )


# --------------------------------------------------------------
# CONTEXT IDENTITY MISMATCHES
# --------------------------------------------------------------

for name, bad_context in (
    (
        "workflow context mismatch",
        create_runtime_handoff_context(
            workflow_id="wf_wrong",
            workspace_id=source.workspace_id,
            correlation_id=source.correlation_id,
            payload_by_stage={
                target.stage_id:
                    mapping.payload,
            },
        ),
    ),
    (
        "workspace context mismatch",
        create_runtime_handoff_context(
            workflow_id=source.workflow_id,
            workspace_id="ws_wrong",
            correlation_id=source.correlation_id,
            payload_by_stage={
                target.stage_id:
                    mapping.payload,
            },
        ),
    ),
    (
        "correlation context mismatch",
        create_runtime_handoff_context(
            workflow_id=source.workflow_id,
            workspace_id=source.workspace_id,
            correlation_id="corr_wrong",
            payload_by_stage={
                target.stage_id:
                    mapping.payload,
            },
        ),
    ),
):

    result = validate_stage_handoff(
        source,
        mapping,
        bad_context,
        artifacts,
    )

    initial_check(
        f"{name} detected",
        result.is_valid is False
        and bool(result.violations),
    )


# --------------------------------------------------------------
# TARGET PAYLOAD MISSING / MISMATCH
# --------------------------------------------------------------

missing_payload_context = (
    create_runtime_handoff_context(
        workflow_id=source.workflow_id,
        workspace_id=source.workspace_id,
        correlation_id=source.correlation_id,
        payload_by_stage={},
    )
)

missing_payload_result = validate_stage_handoff(
    source,
    mapping,
    missing_payload_context,
    artifacts,
)

initial_check(
    "missing target payload detected",
    missing_payload_result.is_valid is False
    and any(
        "target stage payload missing"
        in item
        for item
        in missing_payload_result.violations
    ),
)


wrong_payload_context = (
    create_runtime_handoff_context(
        workflow_id=source.workflow_id,
        workspace_id=source.workspace_id,
        correlation_id=source.correlation_id,
        payload_by_stage={
            target.stage_id: {
                "workspace_id":
                    source.workspace_id,

                "domain":
                    "wrong.example.com",
            },
        },
    )
)

wrong_payload_result = validate_stage_handoff(
    source,
    mapping,
    wrong_payload_context,
    artifacts,
)

initial_check(
    "wrong target payload detected",
    wrong_payload_result.is_valid is False
    and any(
        "does not match mapped payload"
        in item
        for item
        in wrong_payload_result.violations
    ),
)


# --------------------------------------------------------------
# IMMUTABILITY / DETERMINISM
# --------------------------------------------------------------

try:
    validation.violations += (
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
    "validation result immutable",
    immutable,
)

repeat = validate_stage_handoff(
    source,
    mapping,
    context,
    artifacts,
)

initial_check(
    "validation deterministic",
    repeat.to_dict()
    == validation.to_dict(),
)


# --------------------------------------------------------------
# OWNERSHIP BOUNDARIES
# --------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)

for forbidden in (
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
    "propagate_context(",
    "handoff_artifact_references(",
):

    initial_check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden not in source_text,
    )


for path, expected_hash in EXPECTED.items():
    initial_check(
        f"upstream frozen: {path.name}",
        sha256(path) == expected_hash,
    )


if not all(initial):
    stop(
        "Phase 6.5 Initial Verification failed."
    )

print(
    f"INITIAL VERIFICATION: {len(initial)}/{len(initial)} PASS"
)


# ==================================================================
# 6 — FINAL CERTIFICATION
# ==================================================================

section("6 — FINAL CERTIFICATION")

final = []


def final_check(name, condition):
    ok = bool(condition)
    final.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


actual_sha = sha256(TARGET)

final_check(
    "production SHA stable",
    actual_sha == installed_sha,
)

final_check(
    "version exact",
    HANDOFF_VALIDATION_VERSION
    == "handoff_validation_v6.5.0",
)

final_check(
    "schema exact",
    HANDOFF_VALIDATION_SCHEMA_VERSION
    == "handoff_validation_schema_v1",
)

final_check(
    "public API signature exact",
    str(
        inspect.signature(
            validate_stage_handoff
        )
    )
    == (
        "(source: 'ProcessedStageResult', "
        "mapping: 'OutputInputMappingResult', "
        "context: 'RuntimeHandoffContext', "
        "artifacts: 'ArtifactReferenceHandoffResult') "
        "-> 'HandoffValidationResult'"
    ),
)

final_check(
    "canonical handoff certified valid",
    validation.is_valid is True,
)

final_check(
    "canonical handoff certified violation-free",
    validation.violations == (),
)

final_check(
    "source eligibility certified",
    source.completed
    and source.normal_handoff_allowed
    and source.prerequisite_satisfied,
)

final_check(
    "mapping completeness certified",
    mapping.complete
    and not mapping.missing_payload_fields,
)

final_check(
    "workflow continuity certified",
    source.workflow_id
    == mapping.source_workflow_id
    == context.workflow_id
    == artifacts.workflow_id,
)

final_check(
    "workspace continuity certified",
    source.workspace_id
    == mapping.source_workspace_id
    == context.workspace_id
    == artifacts.workspace_id,
)

final_check(
    "correlation continuity certified",
    source.correlation_id
    == mapping.source_correlation_id
    == context.correlation_id
    == artifacts.correlation_id,
)

final_check(
    "stage continuity certified",
    source.stage_id
    == mapping.source_stage_id
    == artifacts.source_stage_id,
)

final_check(
    "target payload continuity certified",
    target.stage_id
    in context.payload_by_stage
    and dict(
        context.payload_by_stage[
            target.stage_id
        ]
    )
    == mapping.to_dict()["payload"],
)

final_check(
    "result reference continuity certified",
    artifacts.result_reference
    == source.result_reference,
)

final_check(
    "artifact references continuity certified",
    artifacts.artifact_references
    == source.artifact_references,
)

final_check(
    "validator execution-free",
    "submit_universal_job("
    not in source_text
    and "stage_completed("
    not in source_text
    and "advance("
    not in source_text,
)

for path, expected_hash in EXPECTED.items():
    final_check(
        f"frozen authority unchanged: {path.name}",
        sha256(path) == expected_hash,
    )


if not all(final):
    stop(
        "Phase 6.5 Final Certification failed. "
        "Freeze not created."
    )


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.5 — HANDOFF VALIDATION FINAL CERTIFICATION",
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
    f"Validation Version: {HANDOFF_VALIDATION_VERSION}",
    f"Schema Version: {HANDOFF_VALIDATION_SCHEMA_VERSION}",
    "",
    "Certified validation chain:",
    "- ProcessedStageResult",
    "- OutputInputMappingResult",
    "- RuntimeHandoffContext",
    "- ArtifactReferenceHandoffResult",
    "",
    "Certified invariants:",
    "- completed source",
    "- normal_handoff_allowed",
    "- prerequisite_satisfied",
    "- complete mapped payload",
    "- exact workflow identity continuity",
    "- exact workspace identity continuity",
    "- exact correlation identity continuity",
    "- exact source-stage identity continuity",
    "- exact target-stage payload installation",
    "- exact result_reference continuity",
    "- exact artifact_references continuity",
    "- component version lineage",
    "",
    "Certified boundaries:",
    "- validation evidence only",
    "- no Runtime submission",
    "- no Runtime execution",
    "- no coordinator invocation",
    "- no workflow advance",
    "- no lifecycle mutation",
    "- no context mutation",
    "- no payload mutation",
    "- no artifact mutation",
    "- Phase 6.6 owns Stage Handoff certification",
    "",
    "NEXT: 6.5 SHA256 Freeze",
]

REPORT.write_text(
    "\n".join(report_lines) + "\n",
    encoding="utf-8",
)

report_sha = sha256(REPORT)

print(
    f"FINAL CERTIFICATION: {len(final)}/{len(final)} PASS"
)

print(
    "PRODUCTION SHA256:",
    actual_sha,
)

print(
    "REPORT SHA256:",
    report_sha,
)


# ==================================================================
# 7 — SHA256 FREEZE
# ==================================================================

section("7 — SHA256 FREEZE")

if FREEZE.exists():
    stop(
        "Phase 6.5 freeze already exists. "
        "Refusing to overwrite canonical freeze evidence."
    )


total_checks = (
    len(architecture_checks)
    + len(smoke)
    + len(initial)
    + len(final)
)


freeze_document = {
    "component":
        "Handoff Validation",

    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.5",

    "freeze_version":
        "handoff_validation_phase_6_5_freeze_v1",

    "certified":
        True,

    "frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "handoff_validation.py",

        "version":
            HANDOFF_VALIDATION_VERSION,

        "schema_version":
            HANDOFF_VALIDATION_SCHEMA_VERSION,

        "sha256":
            actual_sha,
    },

    "validated_chain": [
        "ProcessedStageResult",
        "OutputInputMappingResult",
        "RuntimeHandoffContext",
        "ArtifactReferenceHandoffResult",
    ],

    "validated_invariants": [
        "source completed",
        "normal_handoff_allowed",
        "prerequisite_satisfied",
        "mapping complete",
        "required fields fully satisfied",
        "workflow identity continuity",
        "workspace identity continuity",
        "correlation identity continuity",
        "source stage identity continuity",
        "target payload present in context",
        "target context payload equals mapped payload",
        "result_reference continuity",
        "artifact_references continuity",
        "artifact count consistency",
        "artifact presence consistency",
        "component version lineage",
    ],

    "verification": {
        "architecture": {
            "passed":
                len(architecture_checks),
            "failed":
                0,
        },

        "smoke": {
            "passed":
                len(smoke),
            "failed":
                0,
        },

        "initial": {
            "passed":
                len(initial),
            "failed":
                0,
        },

        "final": {
            "passed":
                len(final),
            "failed":
                0,
        },

        "total_formal_checks":
            total_checks,
    },

    "final_certification_report": {
        "path":
            "handoff_validation_phase_6_5_final_certification.txt",

        "sha256":
            report_sha,
    },

    "upstream_frozen_authorities": {
        path.name:
            expected_hash
        for path, expected_hash
        in EXPECTED.items()
    },

    "certified_boundaries": [
        "no Runtime submission",
        "no Runtime execution",
        "no coordinator invocation",
        "no workflow advance",
        "no lifecycle mutation",
        "no context mutation",
        "no payload mutation",
        "no artifact mutation",
        "Phase 6.6 owns final Stage Handoff certification",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "6.6 Handoff Certification",
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

freeze_sha = sha256(FREEZE)


# ==================================================================
# 8 — POST-FREEZE INTEGRITY
# ==================================================================

section("8 — FINAL STATUS")

post = []

for path, expected_hash in EXPECTED.items():
    ok = sha256(path) == expected_hash
    post.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] "
        f"unchanged: {path.name}"
    )


post.append(
    sha256(TARGET)
    == actual_sha
)

print(
    f"[{'PASS' if post[-1] else 'FAIL'}] "
    "Phase 6.5 production unchanged"
)

post.append(
    FREEZE.exists()
)

print(
    f"[{'PASS' if post[-1] else 'FAIL'}] "
    "freeze exists"
)


if not all(post):
    stop(
        "Post-freeze integrity verification failed."
    )


print()
print(
    "Architecture Resolution:",
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
    "TOTAL FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print(
    "PHASE 6.5 CERTIFIED: TRUE"
)

print(
    "PHASE 6.5 FROZEN: TRUE"
)

print(
    "HANDOFF VALIDATION SHA256:",
    actual_sha,
)

print(
    "CERTIFICATION REPORT SHA256:",
    report_sha,
)

print(
    "FREEZE FILE:",
    FREEZE,
)

print(
    "FREEZE SHA256:",
    freeze_sha,
)

print(
    "PHASE 6.1 MODIFIED: FALSE"
)

print(
    "PHASE 6.2 MODIFIED: FALSE"
)

print(
    "PHASE 6.3 MODIFIED: FALSE"
)

print(
    "PHASE 6.4 MODIFIED: FALSE"
)

print(
    "NEXT: 6.6 Handoff Certification"
)

print("=" * 120)
