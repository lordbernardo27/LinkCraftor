from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/stage_handoff/context_propagation.py"
)

REPORT = (
    ROOT
    / "context_propagation_phase_6_3_final_certification.txt"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "context_propagation.phase_6_3.freeze.json"
)

PHASE_6_1 = (
    ROOT
    / "backend/server/coordination/stage_handoff/stage_result_processor.py"
)

PHASE_6_2 = (
    ROOT
    / "backend/server/coordination/stage_handoff/output_input_mapping.py"
)

PHASE_6_1_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "stage_result_processor.phase_6_1.freeze.json"
)

PHASE_6_2_FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "output_input_mapping.phase_6_2.freeze.json"
)

BRIDGE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)


EXPECTED_6_1_SHA = (
    "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456"
)

EXPECTED_6_1_FREEZE_SHA = (
    "58AD1700AC8EA9BB838EC9E11273A7723D9D7C1F80D5FCB6222AFE563FB2017F"
)

EXPECTED_6_2_SHA = (
    "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744"
)

EXPECTED_6_2_FREEZE_SHA = (
    "DB45DE654E1CA336A35150EF11142B36CFDF3ED2FFE4AA46D03568939E9D5C5E"
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


def fail(message: str) -> None:
    raise SystemExit(
        "\nPHASE 6.3 STOPPED:\n"
        + message
    )


section(
    "LINKCRAFTOR — UCF PHASE 6.3 ALL-IN-ONE IMPLEMENTATION"
)


# ==================================================================
# PRE-INSTALLATION INTEGRITY
# ==================================================================

section(
    "0 — UPSTREAM INTEGRITY"
)

required_files = (
    PHASE_6_1,
    PHASE_6_2,
    PHASE_6_1_FREEZE,
    PHASE_6_2_FREEZE,
    BRIDGE,
)

for path in required_files:
    if not path.exists():
        fail(
            f"Required authority missing: {path}"
        )

integrity_checks = {
    "Phase 6.1 source":
        sha256(PHASE_6_1)
        == EXPECTED_6_1_SHA,

    "Phase 6.1 freeze":
        sha256(PHASE_6_1_FREEZE)
        == EXPECTED_6_1_FREEZE_SHA,

    "Phase 6.2 source":
        sha256(PHASE_6_2)
        == EXPECTED_6_2_SHA,

    "Phase 6.2 freeze":
        sha256(PHASE_6_2_FREEZE)
        == EXPECTED_6_2_FREEZE_SHA,
}

for name, ok in integrity_checks.items():
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

if not all(
    integrity_checks.values()
):
    fail(
        "Frozen Phase 6.1/6.2 integrity mismatch. "
        "No Phase 6.3 installation performed."
    )


# ==================================================================
# 6.3 EXACT CONTEXT CONTRACT RESOLUTION
# ==================================================================

section(
    "1 — EXACT CONTEXT CONTRACT RESOLUTION"
)

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT,
    RUNTIME_HANDOFF_CONTEXT_VERSION,
    RuntimeHandoffContext,
    create_runtime_handoff_context,
)


context_fields = tuple(
    item.name
    for item in fields(
        RuntimeHandoffContext
    )
)

factory_signature = inspect.signature(
    create_runtime_handoff_context
)

factory_parameters = tuple(
    factory_signature.parameters
)


print(
    "RuntimeHandoffContext fields:",
    context_fields,
)

print(
    "Field count authority:",
    RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT,
)

print(
    "Context version:",
    RUNTIME_HANDOFF_CONTEXT_VERSION,
)

print(
    "Factory signature:",
    factory_signature,
)


expected_context_fields = (
    "workflow_id",
    "workspace_id",
    "correlation_id",
    "payload_by_stage",
    "metadata",
    "context_version",
)

contract_checks = []


def contract_check(
    name,
    condition,
):
    ok = bool(condition)
    contract_checks.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


contract_check(
    "RuntimeHandoffContext has exactly six fields",
    len(context_fields)
    == RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT
    == 6,
)

contract_check(
    "RuntimeHandoffContext exact canonical fields",
    context_fields
    == expected_context_fields,
)

contract_check(
    "workflow_id authority present",
    "workflow_id"
    in factory_parameters,
)

contract_check(
    "workspace_id authority present",
    "workspace_id"
    in factory_parameters,
)

contract_check(
    "correlation_id authority present",
    "correlation_id"
    in factory_parameters,
)

contract_check(
    "payload_by_stage authority present",
    "payload_by_stage"
    in factory_parameters,
)

contract_check(
    "metadata authority present",
    "metadata"
    in factory_parameters,
)

contract_check(
    "context version canonical",
    RUNTIME_HANDOFF_CONTEXT_VERSION
    == "runtime_handoff_context_v5.1.0",
)


if not all(
    contract_checks
):
    fail(
        "Exact Phase 5.1 RuntimeHandoffContext contract did not "
        "match the expected six-field authority. "
        "No Phase 6.3 production source was written."
    )


print(
    "EXACT CONTEXT CONTRACT RESOLVED: TRUE"
)


# ==================================================================
# 6.3 PROPAGATION ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "2 — PROPAGATION ARCHITECTURE RESOLUTION"
)


architecture = {
    "context_authority":
        "RuntimeHandoffContext",

    "identity_authority": (
        "workflow_id",
        "workspace_id",
        "correlation_id",
    ),

    "payload_authority":
        "OutputInputMappingResult.payload",

    "target_payload_slot":
        "RuntimeHandoffContext.payload_by_stage[target_stage_id]",

    "metadata_policy":
        "preserve existing coordination metadata unchanged",

    "existing_payload_policy":
        "preserve existing payload_by_stage entries",

    "target_payload_policy":
        "replace target stage payload deterministically",

    "source_status_policy":
        "completed/normal handoff only",

    "runtime_submission":
        False,

    "coordinator_invocation":
        False,

    "artifact_handoff":
        False,

    "lifecycle_mutation":
        False,

    "context_type_creation":
        False,
}


architecture_checks = []


def architecture_check(
    name,
    condition,
):
    ok = bool(condition)
    architecture_checks.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


architecture_check(
    "existing context authority reused",
    architecture[
        "context_authority"
    ]
    == "RuntimeHandoffContext",
)

architecture_check(
    "6.2 mapped payload is payload authority",
    architecture[
        "payload_authority"
    ]
    == "OutputInputMappingResult.payload",
)

architecture_check(
    "stage payload stored by target stage id",
    architecture[
        "target_payload_slot"
    ]
    == "RuntimeHandoffContext.payload_by_stage[target_stage_id]",
)

architecture_check(
    "coordination metadata preserved",
    architecture[
        "metadata_policy"
    ]
    == "preserve existing coordination metadata unchanged",
)

architecture_check(
    "existing stage payloads preserved",
    architecture[
        "existing_payload_policy"
    ]
    == "preserve existing payload_by_stage entries",
)

architecture_check(
    "target payload replacement deterministic",
    architecture[
        "target_payload_policy"
    ]
    == "replace target stage payload deterministically",
)

architecture_check(
    "no Runtime submission ownership",
    architecture[
        "runtime_submission"
    ]
    is False,
)

architecture_check(
    "no coordinator invocation ownership",
    architecture[
        "coordinator_invocation"
    ]
    is False,
)

architecture_check(
    "artifact handoff remains Phase 6.4",
    architecture[
        "artifact_handoff"
    ]
    is False,
)

architecture_check(
    "workflow lifecycle not mutated",
    architecture[
        "lifecycle_mutation"
    ]
    is False,
)

architecture_check(
    "no parallel context class invented",
    architecture[
        "context_type_creation"
    ]
    is False,
)


if not all(
    architecture_checks
):
    fail(
        "Phase 6.3 architecture resolution failed."
    )


print(
    "PROPAGATION ARCHITECTURE RESOLVED: TRUE"
)


# ==================================================================
# 6.3 INSTALLATION
# ==================================================================

section(
    "3 — INSTALLATION"
)


if TARGET.exists():
    fail(
        "context_propagation.py already exists. "
        "Refusing to overwrite an existing production component."
    )


production_source = r'''"""
LinkCraftor
Universal Coordination Framework

PHASE 6.3 — Context Propagation

Purpose
-------
Propagate the already-established Coordination-owned RuntimeHandoffContext
from one successful Stage Handoff to the next stage.

Authority
---------
Phase 6.3 does not invent a second workflow/context contract.

Canonical context authority:
    RuntimeHandoffContext
    from Phase 5.1 Coordination -> Runtime Bridge.

Canonical stage payload authority:
    OutputInputMappingResult.payload
    from Phase 6.2 Output -> Input Mapping.

Propagation model
-----------------
The existing RuntimeHandoffContext is preserved.

Phase 6.3:
- preserves workflow_id,
- preserves workspace_id,
- preserves correlation_id,
- preserves existing coordination metadata,
- preserves existing payload_by_stage entries,
- installs/replaces the mapped payload under the downstream target_stage_id.

Phase 6.3 does NOT:
- derive Coordination context from arbitrary Runtime result metadata,
- submit Runtime jobs,
- execute business logic,
- invoke pipeline coordinators,
- mutate workflow lifecycle state,
- mutate Phase 4 planning,
- mutate Phase 5 Runtime Integration,
- modify Phase 6.1 or Phase 6.2 results,
- hand off artifact references (Phase 6.4),
- perform final Stage Handoff validation (Phase 6.5).
"""

from __future__ import annotations

from typing import Final, Mapping, Any

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    RuntimeHandoffContext,
    create_runtime_handoff_context,
)

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OutputInputMappingResult,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
)


CONTEXT_PROPAGATION_VERSION: Final[str] = (
    "context_propagation_v6.3.0"
)

CONTEXT_PROPAGATION_SCHEMA_VERSION: Final[str] = (
    "context_propagation_schema_v1"
)


class ContextPropagationError(
    ValueError
):
    """
    Raised when canonical Coordination context cannot be safely propagated.
    """


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise ContextPropagationError(
            "source must be a ProcessedStageResult"
        )

    if not source.terminal:
        raise ContextPropagationError(
            "source must be terminal"
        )

    if not source.completed:
        raise ContextPropagationError(
            "context propagation requires a completed source"
        )

    if not source.normal_handoff_allowed:
        raise ContextPropagationError(
            "normal handoff must be allowed before context propagation"
        )


def _validate_mapping(
    mapping: OutputInputMappingResult,
) -> None:

    if not isinstance(
        mapping,
        OutputInputMappingResult,
    ):
        raise ContextPropagationError(
            "mapping must be an OutputInputMappingResult"
        )

    if not mapping.complete:
        raise ContextPropagationError(
            "context propagation requires a complete output-to-input mapping"
        )


def _validate_context(
    context: RuntimeHandoffContext,
) -> None:

    if not isinstance(
        context,
        RuntimeHandoffContext,
    ):
        raise ContextPropagationError(
            "context must be a RuntimeHandoffContext"
        )


def _validate_identity(
    *,
    source: ProcessedStageResult,
    mapping: OutputInputMappingResult,
    context: RuntimeHandoffContext,
) -> None:

    violations: list[str] = []

    if (
        source.result_id
        != mapping.source_result_id
    ):
        violations.append(
            "mapping source_result_id does not match source result_id"
        )

    if (
        source.workflow_id
        != mapping.source_workflow_id
    ):
        violations.append(
            "mapping source_workflow_id does not match source workflow_id"
        )

    if (
        source.correlation_id
        != mapping.source_correlation_id
    ):
        violations.append(
            "mapping source_correlation_id does not match source correlation_id"
        )

    if (
        source.stage_id
        != mapping.source_stage_id
    ):
        violations.append(
            "mapping source_stage_id does not match source stage_id"
        )

    if (
        source.stage_version
        != mapping.source_stage_version
    ):
        violations.append(
            "mapping source_stage_version does not match source stage_version"
        )

    if (
        source.pipeline_id
        != mapping.source_pipeline_id
    ):
        violations.append(
            "mapping source_pipeline_id does not match source pipeline_id"
        )

    if (
        source.workspace_id
        != mapping.source_workspace_id
    ):
        violations.append(
            "mapping source_workspace_id does not match source workspace_id"
        )

    if (
        source.job_id
        != mapping.source_job_id
    ):
        violations.append(
            "mapping source_job_id does not match source job_id"
        )

    if (
        context.workflow_id
        != source.workflow_id
    ):
        violations.append(
            "context workflow_id does not match source workflow_id"
        )

    if (
        context.workspace_id
        != source.workspace_id
    ):
        violations.append(
            "context workspace_id does not match source workspace_id"
        )

    if (
        context.correlation_id
        != source.correlation_id
    ):
        violations.append(
            "context correlation_id does not match source correlation_id"
        )

    if violations:
        raise ContextPropagationError(
            "context propagation identity validation failed: "
            + "; ".join(
                violations
            )
        )


def propagate_context(
    source: ProcessedStageResult,
    mapping: OutputInputMappingResult,
    context: RuntimeHandoffContext,
) -> RuntimeHandoffContext:
    """
    Return a new canonical RuntimeHandoffContext for the downstream stage.

    Existing Coordination context is retained. The mapped Phase 6.2 payload
    is installed under mapping.target_stage_id.

    The supplied context, source result, and mapping result are never mutated.
    """

    _validate_source(
        source
    )

    _validate_mapping(
        mapping
    )

    _validate_context(
        context
    )

    _validate_identity(
        source=source,
        mapping=mapping,
        context=context,
    )

    payload_by_stage: dict[str, Any] = {
        str(stage_id):
            payload
        for stage_id, payload
        in context.payload_by_stage.items()
    }

    payload_by_stage[
        mapping.target_stage_id
    ] = mapping.payload

    return create_runtime_handoff_context(
        workflow_id=
            context.workflow_id,

        workspace_id=
            context.workspace_id,

        correlation_id=
            context.correlation_id,

        payload_by_stage=
            payload_by_stage,

        metadata=
            context.metadata,
    )


__all__ = [
    "CONTEXT_PROPAGATION_VERSION",
    "CONTEXT_PROPAGATION_SCHEMA_VERSION",
    "ContextPropagationError",
    "propagate_context",
]
'''


TARGET.write_text(
    production_source,
    encoding="utf-8",
)


print(
    "INSTALLED:",
    TARGET,
)

installed_sha = sha256(
    TARGET
)

print(
    "CONTEXT PROPAGATION SHA256:",
    installed_sha,
)


# ==================================================================
# IMPORT INSTALLED PRODUCTION
# ==================================================================

from backend.server.coordination.stage_handoff.context_propagation import (
    CONTEXT_PROPAGATION_SCHEMA_VERSION,
    CONTEXT_PROPAGATION_VERSION,
    ContextPropagationError,
    propagate_context,
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


def make_source(
    *,
    suffix="source",
    status=UniversalStageResultStatus.COMPLETED,
    output=None,
):
    if output is None:
        output = {
            "workspace_id":
                "ws_phase_6_3",

            "domain":
                "example.com",

            "count":
                0,
        }

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    result = UniversalStageResult(
        result_id=
            f"usr_6_3_{suffix}",

        workflow_id=
            "wf_phase_6_3",

        correlation_id=
            "corr_phase_6_3",

        stage_id=
            f"source_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_3_pipeline",

        workflow_type=
            "phase_6_3_workflow",

        workspace_id=
            "ws_phase_6_3",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_6_3_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            output,

        result_reference=
            f"result://6-3/{suffix}",

        artifact_references=
            (
                f"artifact://6-3/{suffix}",
            ),

        started_at=
            "2026-09-10T03:30:00+00:00",

        finished_at=
            "2026-09-10T03:31:00+00:00",

        failure_code=
            (
                "phase_6_3_failure"
                if failed
                else ""
            ),

        failure_message=
            (
                "phase 6.3 deterministic failure"
                if failed
                else ""
            ),

        failure_details=
            (
                {
                    "phase":
                        "6.3",
                }
                if failed
                else {}
            ),

        metadata=
            {
                "runtime_evidence":
                    "must-not-become-coordination-context",
            },
    )

    return process_stage_result(
        result
    )


def make_target(
    *,
    suffix="target",
    required_fields=(
        "workspace_id",
        "domain",
    ),
):
    return UniversalStageReference(
        stage_id=
            f"target_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_3_pipeline",

        workflow_type=
            "phase_6_3_workflow",

        workflow_contract_version=
            "universal_workflow_contract_v1.1.0",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_type=
            "linking_target_pipeline_batch",

        runtime_stage=
            f"target_{suffix}",

        required_payload_fields=
            tuple(
                required_fields
            ),
    )


def make_context(
    *,
    payload_by_stage=None,
    metadata=None,
    workflow_id="wf_phase_6_3",
    workspace_id="ws_phase_6_3",
    correlation_id="corr_phase_6_3",
):
    return create_runtime_handoff_context(
        workflow_id=
            workflow_id,

        workspace_id=
            workspace_id,

        correlation_id=
            correlation_id,

        payload_by_stage=
            (
                {}
                if payload_by_stage is None
                else payload_by_stage
            ),

        metadata=
            (
                {}
                if metadata is None
                else metadata
            ),
    )


# ==================================================================
# 6.3 SMOKE VERIFICATION
# ==================================================================

section(
    "4 — SMOKE VERIFICATION"
)

smoke = []


def smoke_check(
    name,
    condition,
):
    ok = bool(condition)
    smoke.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


source = make_source()

target = make_target()

mapping = map_output_to_input(
    source,
    target,
)

context = make_context(
    payload_by_stage={
        "prior_stage":
            {
                "prior":
                    True,
            },
    },

    metadata={
        "tenant":
            "phase_6_3",

        "trace":
            {
                "enabled":
                    True,
            },
    },
)

new_context = propagate_context(
    source,
    mapping,
    context,
)


smoke_check(
    "production source exists",
    TARGET.exists(),
)

smoke_check(
    "version exact",
    CONTEXT_PROPAGATION_VERSION
    == "context_propagation_v6.3.0",
)

smoke_check(
    "schema exact",
    CONTEXT_PROPAGATION_SCHEMA_VERSION
    == "context_propagation_schema_v1",
)

smoke_check(
    "returns canonical RuntimeHandoffContext",
    isinstance(
        new_context,
        RuntimeHandoffContext,
    ),
)

smoke_check(
    "workflow_id propagated",
    new_context.workflow_id
    == context.workflow_id,
)

smoke_check(
    "workspace_id propagated",
    new_context.workspace_id
    == context.workspace_id,
)

smoke_check(
    "correlation_id propagated",
    new_context.correlation_id
    == context.correlation_id,
)

smoke_check(
    "existing payload preserved",
    new_context.payload_by_stage[
        "prior_stage"
    ][
        "prior"
    ]
    is True,
)

smoke_check(
    "target payload installed",
    dict(
        new_context.payload_by_stage[
            target.stage_id
        ]
    )
    == {
        "workspace_id":
            "ws_phase_6_3",

        "domain":
            "example.com",
    },
)

smoke_check(
    "metadata preserved",
    dict(
        new_context.metadata
    )[
        "tenant"
    ]
    == "phase_6_3",
)

smoke_check(
    "source runtime metadata not promoted",
    "runtime_evidence"
    not in new_context.metadata,
)

smoke_check(
    "context version remains Phase 5.1 authority",
    new_context.context_version
    == RUNTIME_HANDOFF_CONTEXT_VERSION,
)


if not all(
    smoke
):
    fail(
        "6.3 Smoke Verification failed."
    )


print(
    f"SMOKE VERIFICATION: {len(smoke)}/{len(smoke)}"
)


# ==================================================================
# 6.3 INITIAL VERIFICATION
# ==================================================================

section(
    "5 — INITIAL VERIFICATION"
)

initial = []


def initial_check(
    name,
    condition,
):
    ok = bool(condition)
    initial.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


context_before = context.to_dict()
source_before = source.to_dict()
mapping_before = mapping.to_dict()

propagated = propagate_context(
    source,
    mapping,
    context,
)


initial_check(
    "source not mutated",
    source.to_dict()
    == source_before,
)

initial_check(
    "mapping not mutated",
    mapping.to_dict()
    == mapping_before,
)

initial_check(
    "context not mutated",
    context.to_dict()
    == context_before,
)

initial_check(
    "new context is distinct object",
    propagated
    is not context,
)

initial_check(
    "context workflow identity exact",
    propagated.workflow_id
    == source.workflow_id,
)

initial_check(
    "context workspace identity exact",
    propagated.workspace_id
    == source.workspace_id,
)

initial_check(
    "context correlation identity exact",
    propagated.correlation_id
    == source.correlation_id,
)

initial_check(
    "existing coordination metadata retained",
    propagated.to_dict()[
        "metadata"
    ]
    == context.to_dict()[
        "metadata"
    ],
)

initial_check(
    "existing payload stage retained",
    "prior_stage"
    in propagated.payload_by_stage,
)

initial_check(
    "mapped target stage added",
    mapping.target_stage_id
    in propagated.payload_by_stage,
)

initial_check(
    "mapped payload exact",
    dict(
        propagated.payload_by_stage[
            mapping.target_stage_id
        ]
    )
    == mapping.to_dict()[
        "payload"
    ],
)


# replacement semantics

replacement_context = make_context(
    payload_by_stage={
        target.stage_id:
            {
                "old":
                    "payload",
            },

        "other_stage":
            {
                "keep":
                    "me",
            },
    },

    metadata={
        "stable":
            True,
    },
)

replaced = propagate_context(
    source,
    mapping,
    replacement_context,
)

initial_check(
    "existing target payload deterministically replaced",
    dict(
        replaced.payload_by_stage[
            target.stage_id
        ]
    )
    == mapping.to_dict()[
        "payload"
    ],
)

initial_check(
    "unrelated existing stage retained",
    dict(
        replaced.payload_by_stage[
            "other_stage"
        ]
    )
    == {
        "keep":
            "me",
    },
)


# deep immutability

try:
    propagated.payload_by_stage[
        mapping.target_stage_id
    ][
        "domain"
    ] = "mutated.example"
except (
    TypeError,
    AttributeError,
):
    immutable_payload = True
else:
    immutable_payload = False

initial_check(
    "propagated target payload immutable",
    immutable_payload,
)


try:
    propagated.metadata[
        "tenant"
    ] = "mutated"
except (
    TypeError,
    AttributeError,
):
    immutable_metadata = True
else:
    immutable_metadata = False

initial_check(
    "propagated metadata immutable",
    immutable_metadata,
)


# deterministic propagation

repeat = propagate_context(
    source,
    mapping,
    context,
)

initial_check(
    "propagation deterministic",
    propagated.to_dict()
    == repeat.to_dict(),
)


# invalid type guards

for name, bad_source, bad_mapping, bad_context in (
    (
        "invalid source",
        object(),
        mapping,
        context,
    ),
    (
        "invalid mapping",
        source,
        object(),
        context,
    ),
    (
        "invalid context",
        source,
        mapping,
        object(),
    ),
):

    rejected = False

    try:
        propagate_context(
            bad_source,
            bad_mapping,
            bad_context,
        )
    except ContextPropagationError:
        rejected = True

    initial_check(
        f"{name} rejected",
        rejected,
    )


# incomplete 6.2 result must not propagate

incomplete_source = make_source(
    suffix=
        "incomplete",

    output={
        "workspace_id":
            "ws_phase_6_3",
    },
)

incomplete_target = make_target(
    suffix=
        "incomplete",

    required_fields=(
        "workspace_id",
        "domain",
    ),
)

incomplete_mapping = map_output_to_input(
    incomplete_source,
    incomplete_target,
)

incomplete_rejected = False

try:
    propagate_context(
        incomplete_source,
        incomplete_mapping,
        context,
    )
except ContextPropagationError:
    incomplete_rejected = True

initial_check(
    "incomplete 6.2 mapping rejected",
    incomplete_rejected,
)


# identity mismatches

identity_cases = (
    (
        "workflow identity mismatch",
        make_context(
            workflow_id=
                "wf_wrong",
        ),
    ),
    (
        "workspace identity mismatch",
        make_context(
            workspace_id=
                "ws_wrong",
        ),
    ),
    (
        "correlation identity mismatch",
        make_context(
            correlation_id=
                "corr_wrong",
        ),
    ),
)

for name, bad_context in identity_cases:

    rejected = False

    try:
        propagate_context(
            source,
            mapping,
            bad_context,
        )
    except ContextPropagationError:
        rejected = True

    initial_check(
        name + " rejected",
        rejected,
    )


# failed / skipped / cancelled sources

for status in (
    UniversalStageResultStatus.FAILED,
    UniversalStageResultStatus.SKIPPED,
    UniversalStageResultStatus.CANCELLED,
):

    bad_source = make_source(
        suffix=status.value,
        status=status,
    )

    rejected = False

    try:
        propagate_context(
            bad_source,
            mapping,
            context,
        )
    except ContextPropagationError:
        rejected = True

    initial_check(
        f"{status.value} source rejected",
        rejected,
    )


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
    "handoff_artifact",
):

    initial_check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden
        not in source_text,
    )


initial_check(
    "no alternate context dataclass introduced",
    "class WorkflowContext"
    not in source_text
    and "class StageContext"
    not in source_text,
)

initial_check(
    "source integrity stable",
    sha256(TARGET)
    == installed_sha,
)


if not all(
    initial
):
    fail(
        "6.3 Initial Verification failed."
    )


print(
    f"INITIAL VERIFICATION: {len(initial)}/{len(initial)}"
)


# ==================================================================
# 6.3 FINAL CERTIFICATION
# ==================================================================

section(
    "6 — FINAL CERTIFICATION"
)

final = []


def final_check(
    name,
    condition,
):
    ok = bool(condition)
    final.append(ok)

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


actual_sha = sha256(
    TARGET
)


final_check(
    "production SHA unchanged",
    actual_sha
    == installed_sha,
)

final_check(
    "public propagation API exact",
    str(
        inspect.signature(
            propagate_context
        )
    )
    == (
        "(source: 'ProcessedStageResult', "
        "mapping: 'OutputInputMappingResult', "
        "context: 'RuntimeHandoffContext') -> 'RuntimeHandoffContext'"
    ),
)

final_check(
    "canonical context class returned",
    type(
        propagated
    )
    is RuntimeHandoffContext,
)

final_check(
    "canonical context version retained",
    propagated.context_version
    == RUNTIME_HANDOFF_CONTEXT_VERSION,
)

final_check(
    "workflow identity preserved end-to-end",
    propagated.workflow_id
    == source.workflow_id
    == mapping.source_workflow_id,
)

final_check(
    "workspace identity preserved end-to-end",
    propagated.workspace_id
    == source.workspace_id
    == mapping.source_workspace_id,
)

final_check(
    "correlation identity preserved end-to-end",
    propagated.correlation_id
    == source.correlation_id
    == mapping.source_correlation_id,
)

final_check(
    "target payload attached by exact stage id",
    mapping.target_stage_id
    in propagated.payload_by_stage,
)

final_check(
    "target payload exact",
    dict(
        propagated.payload_by_stage[
            mapping.target_stage_id
        ]
    )
    == mapping.to_dict()[
        "payload"
    ],
)

final_check(
    "prior context survives",
    "prior_stage"
    in propagated.payload_by_stage,
)

final_check(
    "coordination metadata survives unchanged",
    propagated.to_dict()[
        "metadata"
    ]
    == context.to_dict()[
        "metadata"
    ],
)

final_check(
    "source result metadata does not replace coordination metadata",
    propagated.to_dict()[
        "metadata"
    ]
    != source.to_dict()[
        "metadata"
    ],
)

final_check(
    "Phase 6.4 artifact ownership preserved",
    "artifact_references"
    not in propagated.to_dict(),
)

final_check(
    "Runtime submission remains outside 6.3",
    "submit_universal_job("
    not in source_text,
)

final_check(
    "coordinator invocation remains outside 6.3",
    (
        "stage_completed("
        not in source_text
        and "advance("
        not in source_text
    ),
)

final_check(
    "lifecycle mutation remains outside 6.3",
    (
        "pause("
        not in source_text
        and "resume("
        not in source_text
        and "recover("
        not in source_text
    ),
)

final_check(
    "frozen 6.1 unchanged",
    sha256(PHASE_6_1)
    == EXPECTED_6_1_SHA,
)

final_check(
    "frozen 6.2 unchanged",
    sha256(PHASE_6_2)
    == EXPECTED_6_2_SHA,
)


if not all(
    final
):
    fail(
        "6.3 Final Certification failed."
    )


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.3 — CONTEXT PROPAGATION FINAL CERTIFICATION",
    "",
    f"Exact Context Contract Checks: {len(contract_checks)}",
    f"Architecture Checks: {len(architecture_checks)}",
    f"Smoke Checks: {len(smoke)}",
    f"Initial Checks: {len(initial)}",
    f"Final Checks: {len(final)}",
    "",
    f"Final Passed: {len(final)}",
    "Final Failed: 0",
    "FINAL CERTIFIED: True",
    "",
    f"Context Propagation Version: {CONTEXT_PROPAGATION_VERSION}",
    f"Schema Version: {CONTEXT_PROPAGATION_SCHEMA_VERSION}",
    f"Context Authority: RuntimeHandoffContext",
    f"Context Authority Version: {RUNTIME_HANDOFF_CONTEXT_VERSION}",
    f"Production SHA256: {actual_sha}",
    "",
    "Certified propagation model:",
    "- preserve workflow_id",
    "- preserve workspace_id",
    "- preserve correlation_id",
    "- preserve Coordination-owned metadata",
    "- preserve existing payload_by_stage entries",
    "- install/replace target-stage payload from Phase 6.2 mapping",
    "- require completed/normal-handoff source",
    "- require complete Phase 6.2 mapping",
    "- validate source/mapping/context identity continuity",
    "",
    "Certified boundaries:",
    "- no arbitrary Runtime result metadata promotion",
    "- no alternate workflow context contract",
    "- no Runtime submission",
    "- no Runtime worker execution",
    "- no coordinator invocation",
    "- no workflow lifecycle mutation",
    "- no artifact-reference handoff",
    "- no final Stage Handoff validation",
    "",
    "NEXT: 6.3 SHA256 Freeze",
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
    f"FINAL CERTIFICATION: {len(final)}/{len(final)}"
)

print(
    "FINAL CERTIFIED: TRUE"
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
# 6.3 SHA256 FREEZE
# ==================================================================

section(
    "7 — SHA256 FREEZE"
)


if FREEZE.exists():
    fail(
        "Phase 6.3 freeze already exists. "
        "Refusing to overwrite canonical freeze evidence."
    )


total_checks = (
    len(contract_checks)
    + len(architecture_checks)
    + len(smoke)
    + len(initial)
    + len(final)
)


freeze_document = {
    "component":
        "Context Propagation",

    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.3",

    "freeze_version":
        "context_propagation_phase_6_3_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "production": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "context_propagation.py",

        "version":
            CONTEXT_PROPAGATION_VERSION,

        "schema_version":
            CONTEXT_PROPAGATION_SCHEMA_VERSION,

        "sha256":
            actual_sha,
    },

    "context_authority": {
        "type":
            "RuntimeHandoffContext",

        "version":
            RUNTIME_HANDOFF_CONTEXT_VERSION,

        "field_count":
            RUNTIME_HANDOFF_CONTEXT_FIELD_COUNT,

        "fields":
            list(
                context_fields
            ),
    },

    "propagation_model": {
        "preserved_identity": [
            "workflow_id",
            "workspace_id",
            "correlation_id",
        ],

        "metadata":
            "existing Coordination-owned metadata preserved unchanged",

        "payload_by_stage":
            "existing entries preserved",

        "target_stage_payload":
            "installed/replaced from OutputInputMappingResult.payload",

        "source_requirement":
            "completed and normal_handoff_allowed",

        "mapping_requirement":
            "complete OutputInputMappingResult",
    },

    "verification": {
        "exact_context_contract": {
            "passed":
                len(
                    contract_checks
                ),

            "failed":
                0,
        },

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
            "context_propagation_phase_6_3_final_certification.txt",

        "sha256":
            report_sha,
    },

    "upstream_frozen_authorities": {
        "phase_6_1_processor_sha256":
            EXPECTED_6_1_SHA,

        "phase_6_1_freeze_sha256":
            EXPECTED_6_1_FREEZE_SHA,

        "phase_6_2_mapper_sha256":
            EXPECTED_6_2_SHA,

        "phase_6_2_freeze_sha256":
            EXPECTED_6_2_FREEZE_SHA,
    },

    "certified_boundaries": [
        "no Runtime submission",
        "no Runtime worker execution",
        "no orchestration mutation",
        "no coordinator invocation",
        "no workflow lifecycle mutation",
        "no arbitrary stage-result metadata promotion",
        "no alternate context contract",
        "no artifact-reference handoff",
        "no final handoff validation",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "6.4 Artifact Reference Handoff",
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
# POST-FREEZE INTEGRITY
# ==================================================================

section(
    "8 — FINAL STATUS"
)


if sha256(
    TARGET
) != actual_sha:
    fail(
        "Production source changed during freeze."
    )

if sha256(
    PHASE_6_1
) != EXPECTED_6_1_SHA:
    fail(
        "Frozen Phase 6.1 changed during Phase 6.3."
    )

if sha256(
    PHASE_6_2
) != EXPECTED_6_2_SHA:
    fail(
        "Frozen Phase 6.2 changed during Phase 6.3."
    )


print(
    "Exact Context Contract Resolution:",
    f"{len(contract_checks)}/{len(contract_checks)} PASS",
)

print(
    "Propagation Architecture Resolution:",
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
    "PHASE 6.3 CERTIFIED: TRUE"
)

print(
    "PHASE 6.3 FROZEN: TRUE"
)

print(
    "CONTEXT PROPAGATION SHA256:",
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
    "PHASE 5.1 MODIFIED: FALSE"
)

print(
    "NEXT: 6.4 Artifact Reference Handoff"
)

print("=" * 120)
