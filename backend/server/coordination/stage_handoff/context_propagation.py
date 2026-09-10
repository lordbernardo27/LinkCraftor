"""
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
