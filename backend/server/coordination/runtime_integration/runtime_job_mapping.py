from __future__ import annotations

"""
LinkCraftor Universal Coordination Framework
Phase 5.2 - Runtime Job Mapping

Canonical responsibility:
    Deterministically convert frozen Phase 5.1 RuntimeHandoffIntent objects
    into canonical UniversalJobCreationRequest objects.

Boundary:
    Mapping only.

This component does NOT:
    - create UniversalJob objects
    - call the Universal Job Creation Engine
    - perform Runtime Registration lookup
    - submit jobs
    - persist jobs
    - enqueue jobs
    - dispatch handlers
    - execute business logic
    - establish workflow/job correlation
    - process Runtime completion
    - process Runtime failure
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    CoordinationRuntimeBridgeResult,
    RuntimeHandoffIntent,
)

from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)


RUNTIME_JOB_MAPPING_VERSION = (
    "runtime_job_mapping_v5.2.0"
)

RUNTIME_JOB_MAPPING_SCHEMA_VERSION = (
    "runtime_job_mapping_schema_v1"
)

RUNTIME_JOB_MAPPING_ENTRY_VERSION = (
    "runtime_job_mapping_entry_v5.2.0"
)

COORDINATION_METADATA_KEY = (
    "coordination"
)

RUNTIME_JOB_MAPPING_FIELD_COUNT = 6
RUNTIME_JOB_MAPPING_RESULT_FIELD_COUNT = 6


_EMPTY_MAP = MappingProxyType(
    {}
)


class RuntimeJobMappingError(
    ValueError
):
    """Base Phase 5.2 Runtime Job Mapping error."""


class RuntimeJobMappingValidationError(
    RuntimeJobMappingError
):
    """Raised when Phase 5.2 mapping input violates the contract."""

    def __init__(
        self,
        message: str,
        *,
        violations: tuple[str, ...] = (),
    ) -> None:

        super().__init__(
            message
        )

        self.violations = tuple(
            str(
                item
            )
            for item
            in violations
        )


def _clean_required_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    normalized = str(
        value
        or ""
    ).strip()

    if not normalized:

        raise RuntimeJobMappingValidationError(
            f"{field_name} is required.",
            violations=(
                f"{field_name} is required",
            ),
        )

    return normalized


def _freeze_value(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return MappingProxyType(
            {
                key: _freeze_value(
                    item
                )
                for (
                    key,
                    item,
                )
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):

        return tuple(
            _freeze_value(
                item
            )
            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):

        return tuple(
            _freeze_value(
                item
            )
            for item
            in value
        )

    if isinstance(
        value,
        set,
    ):

        return frozenset(
            _freeze_value(
                item
            )
            for item
            in value
        )

    if isinstance(
        value,
        frozenset,
    ):

        return frozenset(
            _freeze_value(
                item
            )
            for item
            in value
        )

    return value


def _freeze_mapping(
    value: Mapping[str, Any],
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):

        raise RuntimeJobMappingValidationError(
            f"{field_name} must be a mapping.",
            violations=(
                f"{field_name} must be a mapping",
            ),
        )

    return MappingProxyType(
        {
            str(
                key
            ): _freeze_value(
                item
            )
            for (
                key,
                item,
            )
            in value.items()
        }
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeJobMapping:
    """
    One immutable Phase 5.2 mapping.

    creation_request is the exact downstream Runtime creation-request
    contract. No Universal Job has been created at this stage.
    """

    workflow_id: str
    correlation_id: str
    stage_id: str
    wave_index: int
    creation_request: UniversalJobCreationRequest
    mapping_version: str = (
        RUNTIME_JOB_MAPPING_ENTRY_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        _clean_required_text(
            self.workflow_id,
            field_name="workflow_id",
        )

        _clean_required_text(
            self.correlation_id,
            field_name="correlation_id",
        )

        _clean_required_text(
            self.stage_id,
            field_name="stage_id",
        )

        if (
            not isinstance(
                self.wave_index,
                int,
            )
            or isinstance(
                self.wave_index,
                bool,
            )
            or self.wave_index < 0
        ):

            raise RuntimeJobMappingValidationError(
                "wave_index must be a non-negative integer.",
                violations=(
                    "wave_index must be a non-negative integer",
                ),
            )

        if not isinstance(
            self.creation_request,
            UniversalJobCreationRequest,
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "creation_request must be "
                    "UniversalJobCreationRequest."
                ),
                violations=(
                    (
                        "creation_request must be "
                        "UniversalJobCreationRequest"
                    ),
                ),
            )

        if (
            self.creation_request.pipeline_run_id
            is not None
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "Phase 5.2 must not establish "
                    "pipeline_run_id."
                ),
                violations=(
                    "pipeline_run_id belongs downstream of Phase 5.2",
                ),
            )

        if (
            self.creation_request.job_id
            is not None
        ):

            raise RuntimeJobMappingValidationError(
                "Phase 5.2 must not generate job_id.",
                violations=(
                    "job_id belongs to Universal Job Creation Engine",
                ),
            )

        if (
            self.creation_request.idempotency_key
            is not None
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "Phase 5.2 must not generate "
                    "idempotency_key."
                ),
                violations=(
                    (
                        "idempotency_key requires a separate "
                        "authoritative identity policy"
                    ),
                ),
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeJobMappingResult:
    """Immutable result for one Phase 5.1 bridge result."""

    workflow_id: str
    mapping_count: int
    mappings: tuple[
        RuntimeJobMapping,
        ...,
    ]
    stage_ids: tuple[str, ...]
    mapper_version: str = (
        RUNTIME_JOB_MAPPING_VERSION
    )
    schema_version: str = (
        RUNTIME_JOB_MAPPING_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        workflow_id = (
            _clean_required_text(
                self.workflow_id,
                field_name="workflow_id",
            )
        )

        if (
            not isinstance(
                self.mapping_count,
                int,
            )
            or isinstance(
                self.mapping_count,
                bool,
            )
            or self.mapping_count < 0
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "mapping_count must be a "
                    "non-negative integer."
                ),
                violations=(
                    (
                        "mapping_count must be a "
                        "non-negative integer"
                    ),
                ),
            )

        if not isinstance(
            self.mappings,
            tuple,
        ):

            raise RuntimeJobMappingValidationError(
                "mappings must be a tuple.",
                violations=(
                    "mappings must be immutable tuple",
                ),
            )

        if not isinstance(
            self.stage_ids,
            tuple,
        ):

            raise RuntimeJobMappingValidationError(
                "stage_ids must be a tuple.",
                violations=(
                    "stage_ids must be immutable tuple",
                ),
            )

        if (
            self.mapping_count
            != len(
                self.mappings
            )
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "mapping_count does not match "
                    "mappings length."
                ),
                violations=(
                    "mapping_count must equal len(mappings)",
                ),
            )

        mapping_stage_ids = tuple(
            mapping.stage_id
            for mapping
            in self.mappings
        )

        if (
            mapping_stage_ids
            != self.stage_ids
        ):

            raise RuntimeJobMappingValidationError(
                (
                    "stage_ids do not match mapping "
                    "ordering."
                ),
                violations=(
                    (
                        "stage_ids must exactly preserve "
                        "mapping stage ordering"
                    ),
                ),
            )

        if len(
            set(
                self.stage_ids
            )
        ) != len(
            self.stage_ids
        ):

            raise RuntimeJobMappingValidationError(
                "stage_ids contains duplicates.",
                violations=(
                    "stage_ids must be unique",
                ),
            )

        for mapping in self.mappings:

            if not isinstance(
                mapping,
                RuntimeJobMapping,
            ):

                raise RuntimeJobMappingValidationError(
                    (
                        "mappings contains a non-"
                        "RuntimeJobMapping value."
                    ),
                    violations=(
                        (
                            "every mappings entry must be "
                            "RuntimeJobMapping"
                        ),
                    ),
                )

            if (
                mapping.workflow_id
                != workflow_id
            ):

                raise RuntimeJobMappingValidationError(
                    (
                        "RuntimeJobMapping workflow_id "
                        "does not match result workflow_id."
                    ),
                    violations=(
                        (
                            "all mappings must belong to "
                            "the result workflow"
                        ),
                    ),
                )


def _build_creation_metadata(
    intent: RuntimeHandoffIntent,
) -> Mapping[str, Any]:

    if not isinstance(
        intent.metadata,
        Mapping,
    ):

        raise RuntimeJobMappingValidationError(
            "RuntimeHandoffIntent.metadata must be a mapping.",
            violations=(
                "intent.metadata must be a mapping",
            ),
        )

    if (
        COORDINATION_METADATA_KEY
        in intent.metadata
    ):

        raise RuntimeJobMappingValidationError(
            (
                "RuntimeHandoffIntent.metadata already "
                "contains reserved key 'coordination'."
            ),
            violations=(
                (
                    "Phase 5.2 refuses to overwrite existing "
                    "coordination metadata"
                ),
            ),
        )

    metadata = {
        str(
            key
        ): _freeze_value(
            value
        )
        for (
            key,
            value,
        )
        in intent.metadata.items()
    }

    metadata[
        COORDINATION_METADATA_KEY
    ] = MappingProxyType(
        {
            "workflow_id":
                intent.workflow_id,

            "correlation_id":
                intent.correlation_id,

            "stage_id":
                intent.stage_id,

            "stage_version":
                intent.stage_version,

            "workflow_type":
                intent.workflow_type,

            "wave_index":
                intent.wave_index,

            "execution_semantics":
                intent.execution_semantics,

            "required_payload_fields":
                tuple(
                    intent.required_payload_fields
                ),

            "stage_reference_contract_version":
                intent.stage_reference_contract_version,

            "runtime_handoff_intent_version":
                intent.intent_version,
        }
    )

    return MappingProxyType(
        metadata
    )


def map_runtime_handoff_intent_to_creation_request(
    *,
    intent: RuntimeHandoffIntent,
) -> RuntimeJobMapping:

    """
    Convert one frozen Phase 5.1 handoff intent into one immutable
    UniversalJobCreationRequest.

    No job creation, registration lookup, persistence, queue write,
    dispatch, execution, or workflow/job correlation occurs here.
    """

    if not isinstance(
        intent,
        RuntimeHandoffIntent,
    ):

        raise RuntimeJobMappingValidationError(
            (
                "intent must be "
                "RuntimeHandoffIntent."
            ),
            violations=(
                (
                    "Phase 5.2 input must be "
                    "RuntimeHandoffIntent"
                ),
            ),
        )

    workflow_id = _clean_required_text(
        intent.workflow_id,
        field_name="workflow_id",
    )

    workspace_id = _clean_required_text(
        intent.workspace_id,
        field_name="workspace_id",
    )

    correlation_id = _clean_required_text(
        intent.correlation_id,
        field_name="correlation_id",
    )

    stage_id = _clean_required_text(
        intent.stage_id,
        field_name="stage_id",
    )

    pipeline_id = _clean_required_text(
        intent.pipeline_id,
        field_name="pipeline_id",
    )

    job_type = _clean_required_text(
        intent.job_type,
        field_name="job_type",
    )

    runtime_stage = _clean_required_text(
        intent.runtime_stage,
        field_name="runtime_stage",
    )

    payload = _freeze_mapping(
        intent.payload,
        field_name="intent.payload",
    )

    metadata = _build_creation_metadata(
        intent
    )

    request = UniversalJobCreationRequest(
        workspace_id=workspace_id,
        job_type=job_type,
        payload=payload,
        metadata=metadata,
        pipeline=pipeline_id,
        stage=runtime_stage,
        enqueue=True,
    )

    return RuntimeJobMapping(
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        stage_id=stage_id,
        wave_index=intent.wave_index,
        creation_request=request,
    )


def map_runtime_handoffs_to_job_requests(
    *,
    bridge_result: CoordinationRuntimeBridgeResult,
) -> RuntimeJobMappingResult:

    """
    Map one complete frozen Phase 5.1 bridge result.

    Intent ordering is preserved exactly.
    Empty bridge results produce zero mappings.
    """

    if not isinstance(
        bridge_result,
        CoordinationRuntimeBridgeResult,
    ):

        raise RuntimeJobMappingValidationError(
            (
                "bridge_result must be "
                "CoordinationRuntimeBridgeResult."
            ),
            violations=(
                (
                    "Phase 5.2 input must be the "
                    "Phase 5.1 bridge result"
                ),
            ),
        )

    workflow_id = _clean_required_text(
        bridge_result.workflow_id,
        field_name="bridge_result.workflow_id",
    )

    if (
        bridge_result.handoff_count
        != len(
            bridge_result.intents
        )
    ):

        raise RuntimeJobMappingValidationError(
            (
                "Phase 5.1 handoff_count does not "
                "match intents length."
            ),
            violations=(
                (
                    "bridge_result.handoff_count must equal "
                    "len(bridge_result.intents)"
                ),
            ),
        )

    if (
        tuple(
            bridge_result.planned_stage_ids
        )
        != tuple(
            intent.stage_id
            for intent
            in bridge_result.intents
        )
    ):

        raise RuntimeJobMappingValidationError(
            (
                "Phase 5.1 planned_stage_ids do not "
                "match intent ordering."
            ),
            violations=(
                (
                    "Phase 5.2 requires certified Phase 5.1 "
                    "intent ordering"
                ),
            ),
        )

    mappings = tuple(
        map_runtime_handoff_intent_to_creation_request(
            intent=intent
        )
        for intent
        in bridge_result.intents
    )

    stage_ids = tuple(
        mapping.stage_id
        for mapping
        in mappings
    )

    return RuntimeJobMappingResult(
        workflow_id=workflow_id,
        mapping_count=len(
            mappings
        ),
        mappings=mappings,
        stage_ids=stage_ids,
    )


def runtime_job_mapping_snapshot(
    result: RuntimeJobMappingResult,
) -> Mapping[str, Any]:

    if not isinstance(
        result,
        RuntimeJobMappingResult,
    ):

        raise RuntimeJobMappingValidationError(
            (
                "result must be "
                "RuntimeJobMappingResult."
            ),
            violations=(
                "snapshot input must be RuntimeJobMappingResult",
            ),
        )

    return MappingProxyType(
        {
            "workflow_id":
                result.workflow_id,

            "mapping_count":
                result.mapping_count,

            "stage_ids":
                result.stage_ids,

            "mappings":
                tuple(
                    MappingProxyType(
                        {
                            "workflow_id":
                                item.workflow_id,

                            "correlation_id":
                                item.correlation_id,

                            "stage_id":
                                item.stage_id,

                            "wave_index":
                                item.wave_index,

                            "creation_request":
                                item.creation_request,
                        }
                    )
                    for item
                    in result.mappings
                ),

            "mapper_version":
                result.mapper_version,

            "schema_version":
                result.schema_version,
        }
    )


def explain_runtime_job_mapping_v5_2(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.2",

            "component":
                "Runtime Job Mapping",

            "version":
                RUNTIME_JOB_MAPPING_VERSION,

            "schema_version":
                RUNTIME_JOB_MAPPING_SCHEMA_VERSION,

            "upstream_authority":
                "Phase 5.1 RuntimeHandoffIntent",

            "downstream_authority":
                "Universal Job Creation Engine",

            "canonical_operation":
                "map_runtime_handoffs_to_job_requests",

            "direct_mapping":
                MappingProxyType(
                    {
                        "workspace_id":
                            "workspace_id",

                        "job_type":
                            "job_type",

                        "payload":
                            "payload",

                        "pipeline_id":
                            "pipeline",

                        "runtime_stage":
                            "stage",
                    }
                ),

            "correlation_boundary":
                MappingProxyType(
                    {
                        "workflow_id_to_pipeline_run_id":
                            False,

                        "correlation_id_to_pipeline_run_id":
                            False,

                        "pipeline_run_id":
                            None,

                        "phase_5_3_owns_correlation":
                            True,
                    }
                ),

            "execution_properties":
                MappingProxyType(
                    {
                        "read_only":
                            True,

                        "deterministic":
                            True,

                        "fail_closed":
                            True,

                        "universal_job_creation":
                            False,

                        "job_id_generation":
                            False,

                        "pipeline_run_id_generation":
                            False,

                        "idempotency_key_generation":
                            False,

                        "runtime_registration_lookup":
                            False,

                        "submission":
                            False,

                        "persistence":
                            False,

                        "queue_write":
                            False,

                        "dispatch":
                            False,

                        "business_execution":
                            False,

                        "completion_processing":
                            False,

                        "failure_processing":
                            False,

                        "workflow_job_correlation":
                            False,
                    }
                ),
        }
    )


__all__ = (
    "RUNTIME_JOB_MAPPING_VERSION",
    "RUNTIME_JOB_MAPPING_SCHEMA_VERSION",
    "RUNTIME_JOB_MAPPING_ENTRY_VERSION",
    "RUNTIME_JOB_MAPPING_FIELD_COUNT",
    "RUNTIME_JOB_MAPPING_RESULT_FIELD_COUNT",
    "COORDINATION_METADATA_KEY",
    "RuntimeJobMappingError",
    "RuntimeJobMappingValidationError",
    "RuntimeJobMapping",
    "RuntimeJobMappingResult",
    "map_runtime_handoff_intent_to_creation_request",
    "map_runtime_handoffs_to_job_requests",
    "runtime_job_mapping_snapshot",
    "explain_runtime_job_mapping_v5_2",
)
