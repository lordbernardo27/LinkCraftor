"""
LinkCraftor
Universal Coordination Framework

PHASE 6.2 ? Output -> Input Mapping

Responsibility
--------------
Project the output of one successfully completed ProcessedStageResult into
the exact top-level payload fields declared by a downstream
UniversalStageReference.required_payload_fields.

Canonical authorities:
- ProcessedStageResult.output
- UniversalStageReference.required_payload_fields
- Runtime Creation Engine required-field semantics

Phase 6.2 v1 mapping rule:
For each downstream required payload field, select the value from the
upstream ProcessedStageResult.output using the exact same top-level key.

A required field is considered missing when:
- the key is absent,
- the value is None,
- the value is the empty string "".

Values such as 0, False, [], and {} are not considered missing.

This component does NOT:
- invent source-field -> target-field rename mappings,
- implement nested-path mappings,
- propagate workflow context (Phase 6.3),
- hand off artifact references (Phase 6.4),
- perform cross-stage handoff validation (Phase 6.5),
- submit Runtime jobs,
- invoke coordinators,
- execute business logic,
- mutate workflow lifecycle state,
- mutate Phase 4 planning state,
- mutate Phase 5 Runtime Integration state,
- modify the downstream UniversalStageReference,
- replace Runtime's final payload enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
)

from backend.server.coordination.universal_stages.contract import (
    UniversalStageReference,
)


OUTPUT_INPUT_MAPPING_VERSION: Final[str] = (
    "output_input_mapping_v6.2.0"
)

OUTPUT_INPUT_MAPPING_SCHEMA_VERSION: Final[str] = (
    "output_input_mapping_schema_v1"
)


class OutputInputMappingError(
    ValueError
):
    """
    Raised when a safe Phase 6.2 output -> input mapping cannot be produced.
    """


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                str(key):
                    _freeze(item)
                for key, item in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        set,
    ):
        return tuple(
            sorted(
                (
                    _freeze(item)
                    for item in value
                ),
                key=repr,
            )
        )

    return value


def _thaw(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key):
                _thaw(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
        return [
            _thaw(item)
            for item in value
        ]

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class OutputInputMappingResult:
    """
    Immutable result of one Phase 6.2 exact-name payload projection.
    """

    source_result_id: str
    source_workflow_id: str
    source_correlation_id: str
    source_stage_id: str
    source_stage_version: str
    source_pipeline_id: str
    source_workspace_id: str
    source_job_id: str

    target_stage_id: str
    target_stage_version: str
    target_pipeline_id: str
    target_workflow_type: str
    target_execution_target: str
    target_job_type: str
    target_runtime_stage: str

    required_payload_fields: Tuple[str, ...]
    satisfied_payload_fields: Tuple[str, ...]
    missing_payload_fields: Tuple[str, ...]

    payload: Mapping[str, Any]

    complete: bool

    source_processor_version: str
    target_stage_reference_contract_version: str

    mapper_version: str = (
        OUTPUT_INPUT_MAPPING_VERSION
    )

    schema_version: str = (
        OUTPUT_INPUT_MAPPING_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "required_payload_fields",
            tuple(
                self.required_payload_fields
            ),
        )

        object.__setattr__(
            self,
            "satisfied_payload_fields",
            tuple(
                self.satisfied_payload_fields
            ),
        )

        object.__setattr__(
            self,
            "missing_payload_fields",
            tuple(
                self.missing_payload_fields
            ),
        )

        object.__setattr__(
            self,
            "payload",
            _freeze(
                self.payload
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "source_result_id":
                self.source_result_id,

            "source_workflow_id":
                self.source_workflow_id,

            "source_correlation_id":
                self.source_correlation_id,

            "source_stage_id":
                self.source_stage_id,

            "source_stage_version":
                self.source_stage_version,

            "source_pipeline_id":
                self.source_pipeline_id,

            "source_workspace_id":
                self.source_workspace_id,

            "source_job_id":
                self.source_job_id,

            "target_stage_id":
                self.target_stage_id,

            "target_stage_version":
                self.target_stage_version,

            "target_pipeline_id":
                self.target_pipeline_id,

            "target_workflow_type":
                self.target_workflow_type,

            "target_execution_target":
                self.target_execution_target,

            "target_job_type":
                self.target_job_type,

            "target_runtime_stage":
                self.target_runtime_stage,

            "required_payload_fields":
                list(
                    self.required_payload_fields
                ),

            "satisfied_payload_fields":
                list(
                    self.satisfied_payload_fields
                ),

            "missing_payload_fields":
                list(
                    self.missing_payload_fields
                ),

            "payload":
                _thaw(
                    self.payload
                ),

            "complete":
                self.complete,

            "source_processor_version":
                self.source_processor_version,

            "target_stage_reference_contract_version":
                self.target_stage_reference_contract_version,

            "mapper_version":
                self.mapper_version,

            "schema_version":
                self.schema_version,
        }


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise OutputInputMappingError(
            "source must be a ProcessedStageResult"
        )

    if not source.terminal:
        raise OutputInputMappingError(
            "ProcessedStageResult must be terminal"
        )

    if not source.normal_handoff_allowed:
        raise OutputInputMappingError(
            "normal output-to-input mapping is not allowed for "
            f"source disposition {source.disposition.value!r}"
        )

    if not source.completed:
        raise OutputInputMappingError(
            "normal output-to-input mapping requires a completed source"
        )


def _validate_target(
    target: UniversalStageReference,
) -> None:

    if not isinstance(
        target,
        UniversalStageReference,
    ):
        raise OutputInputMappingError(
            "target must be a UniversalStageReference"
        )

    # UniversalStageReference is already canonicalized and validated by
    # its contract constructor. Phase 6.2 consumes that authority without
    # inventing a second stage-reference validation model.


def _is_missing_required_value(
    *,
    payload: Mapping[str, Any],
    field_name: str,
) -> bool:

    return (
        field_name not in payload
        or payload.get(
            field_name
        ) is None
        or payload.get(
            field_name
        ) == ""
    )


def map_output_to_input(
    source: ProcessedStageResult,
    target: UniversalStageReference,
) -> OutputInputMappingResult:
    """
    Produce an exact-name top-level projection for one downstream stage.

    Only fields declared by target.required_payload_fields are projected.
    Extra upstream output fields are not automatically copied.

    Runtime remains the final enforcement authority when a Universal Job
    is later created.
    """

    _validate_source(
        source
    )

    _validate_target(
        target
    )

    required_fields = tuple(
        target.required_payload_fields
    )

    mapped_payload: dict[str, Any] = {}

    satisfied_fields: list[str] = []
    missing_fields: list[str] = []

    source_output = source.output

    for field_name in required_fields:

        if _is_missing_required_value(
            payload=source_output,
            field_name=field_name,
        ):
            missing_fields.append(
                field_name
            )
            continue

        mapped_payload[
            field_name
        ] = source_output[
            field_name
        ]

        satisfied_fields.append(
            field_name
        )

    complete = (
        len(
            missing_fields
        )
        == 0
    )

    execution_target = (
        target.execution_target.value
        if hasattr(
            target.execution_target,
            "value",
        )
        else str(
            target.execution_target
        )
    )

    return OutputInputMappingResult(
        source_result_id=
            source.result_id,

        source_workflow_id=
            source.workflow_id,

        source_correlation_id=
            source.correlation_id,

        source_stage_id=
            source.stage_id,

        source_stage_version=
            source.stage_version,

        source_pipeline_id=
            source.pipeline_id,

        source_workspace_id=
            source.workspace_id,

        source_job_id=
            source.job_id,

        target_stage_id=
            target.stage_id,

        target_stage_version=
            target.stage_version,

        target_pipeline_id=
            target.pipeline_id,

        target_workflow_type=
            target.workflow_type,

        target_execution_target=
            execution_target,

        target_job_type=
            target.job_type,

        target_runtime_stage=
            target.runtime_stage,

        required_payload_fields=
            required_fields,

        satisfied_payload_fields=
            tuple(
                satisfied_fields
            ),

        missing_payload_fields=
            tuple(
                missing_fields
            ),

        payload=
            mapped_payload,

        complete=
            complete,

        source_processor_version=
            source.processor_version,

        target_stage_reference_contract_version=
            target.contract_version,
    )


__all__ = [
    "OUTPUT_INPUT_MAPPING_VERSION",
    "OUTPUT_INPUT_MAPPING_SCHEMA_VERSION",
    "OutputInputMappingError",
    "OutputInputMappingResult",
    "map_output_to_input",
]
