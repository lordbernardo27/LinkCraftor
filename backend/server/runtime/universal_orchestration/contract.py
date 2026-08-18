from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping


UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION = (
    "universal_runtime_orchestration_contract_v5.1.1"
)

UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION = (
    "universal_runtime_orchestration_schema_v1"
)

MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH = 200

MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS = 10_000


class UniversalRuntimeOrchestrationContractError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


def normalize_universal_orchestration_identifier(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise UniversalRuntimeOrchestrationContractError(
            (
                field_name
                + " must be a string."
            ),
            code="invalid_orchestration_identifier",
            value=value,
        )

    normalized = value.strip()

    if not normalized:

        raise UniversalRuntimeOrchestrationContractError(
            (
                field_name
                + " must not be empty."
            ),
            code="invalid_orchestration_identifier",
            value=value,
        )

    if (
        len(
            normalized
        )
        > MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH
    ):

        raise UniversalRuntimeOrchestrationContractError(
            (
                field_name
                + " exceeds the maximum supported length."
            ),
            code="orchestration_identifier_too_long",
            value=value,
        )

    if any(
        character.isspace()
        for character in normalized
    ):

        raise UniversalRuntimeOrchestrationContractError(
            (
                field_name
                + " must not contain whitespace."
            ),
            code="invalid_orchestration_identifier",
            value=value,
        )

    return normalized


def normalize_universal_orchestration_job_ids(
    values: Any,
) -> tuple[str, ...]:

    if isinstance(
        values,
        (
            str,
            bytes,
            bytearray,
        ),
    ):

        raise UniversalRuntimeOrchestrationContractError(
            "job_ids must be an iterable collection of job identifiers.",
            code="invalid_orchestration_job_ids",
            value=values,
        )

    try:

        raw_values = tuple(
            values
        )

    except TypeError as exc:

        raise UniversalRuntimeOrchestrationContractError(
            "job_ids must be iterable.",
            code="invalid_orchestration_job_ids",
            value=values,
        ) from exc

    if not raw_values:

        raise UniversalRuntimeOrchestrationContractError(
            "job_ids must contain at least one Universal Job reference.",
            code="orchestration_job_ids_empty",
            value=values,
        )

    if (
        len(
            raw_values
        )
        > MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS
    ):

        raise UniversalRuntimeOrchestrationContractError(
            "job_ids exceeds the maximum supported orchestration size.",
            code="orchestration_job_ids_too_many",
            value=len(
                raw_values
            ),
        )

    normalized = tuple(
        normalize_universal_orchestration_identifier(
            value,
            field_name="job_id",
        )
        for value in raw_values
    )

    if (
        len(
            normalized
        )
        != len(
            set(
                normalized
            )
        )
    ):

        raise UniversalRuntimeOrchestrationContractError(
            "job_ids contains duplicate Universal Job references.",
            code="duplicate_orchestration_job_id",
            value=normalized,
        )

    return tuple(
        sorted(
            normalized
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalRuntimeOrchestrationContract:

    workspace_id: str

    pipeline: str

    job_ids: tuple[str, ...]

    schema_version: str = (
        UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        workspace_id = (
            normalize_universal_orchestration_identifier(
                self.workspace_id,
                field_name="workspace_id",
            )
        )

        pipeline = (
            normalize_universal_orchestration_identifier(
                self.pipeline,
                field_name="pipeline",
            )
        )

        job_ids = (
            normalize_universal_orchestration_job_ids(
                self.job_ids
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION
        ):

            raise UniversalRuntimeOrchestrationContractError(
                "Invalid Runtime Orchestration schema_version.",
                code="invalid_orchestration_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "workspace_id",
            workspace_id,
        )

        object.__setattr__(
            self,
            "pipeline",
            pipeline,
        )

        object.__setattr__(
            self,
            "job_ids",
            job_ids,
        )

    @property
    def job_count(
        self,
    ) -> int:

        return len(
            self.job_ids
        )

    def contains_job(
        self,
        job_id: Any,
    ) -> bool:

        normalized = (
            normalize_universal_orchestration_identifier(
                job_id,
                field_name="job_id",
            )
        )

        return (
            normalized
            in self.job_ids
        )


def create_universal_runtime_orchestration_contract(
    *,
    workspace_id: Any,
    pipeline: Any,
    job_ids: Iterable[Any],
) -> UniversalRuntimeOrchestrationContract:

    return UniversalRuntimeOrchestrationContract(
        workspace_id=workspace_id,
        pipeline=pipeline,
        job_ids=tuple(
            job_ids
        ),
    )


def explain_universal_runtime_orchestration_contract_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.1",

            "component":
                "Universal Runtime Orchestration Contract",

            "version":
                UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION,

            "schema_version":
                UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION,

            "scope_rule": (
                "5.1.1 defines an immutable deterministic "
                "runtime orchestration request over canonical "
                "Universal Job references."
            ),

            "stored_fields": (
                "workspace_id",
                "pipeline",
                "job_ids",
                "schema_version",
            ),

            "job_reference_rule": (
                "job_ids reference canonical Universal Jobs; "
                "the orchestration contract does not duplicate "
                "Universal Job fields."
            ),

            "ordering_rule": (
                "job_ids are lexically canonicalized only for "
                "determinism; lexical order is not execution order."
            ),

            "run_identity_boundary": (
                "orchestration run identity belongs to "
                "5.1.2 Orchestration Run Identity."
            ),

            "state_boundary": (
                "orchestration lifecycle state and transitions "
                "belong to 5.1.3 Orchestration State Model."
            ),

            "dependency_boundary": (
                "dependency resolution belongs to "
                "5.1.4 Dependency Resolution."
            ),

            "planning_boundary": (
                "execution ordering and planning belong to "
                "5.1.5 Execution Planning."
            ),

            "readiness_boundary": (
                "stage/job readiness belongs to "
                "5.1.6 Stage Readiness Evaluation."
            ),

            "coordination_boundary": (
                "Universal Coordination Framework workflow and "
                "coordinator contracts remain above Runtime "
                "Orchestration and are not imported by 5.1.1."
            ),

            "execution_boundary": (
                "dispatch and actual execution belong outside "
                "5.1.1 and are not performed by this contract."
            ),

            "persistence_boundary": (
                "5.1.1 performs no persistence and does not "
                "access Runtime State Store."
            ),

            "prohibitions": (
                "does not define orchestration_run_id",
                "does not define orchestration lifecycle state",
                "does not transition orchestration state",
                "does not resolve dependencies",
                "does not determine execution order",
                "does not determine readiness",
                "does not perform fan-out",
                "does not perform fan-in",
                "does not evaluate conditional branches",
                "does not perform runtime handoffs",
                "does not track orchestration progress",
                "does not restore checkpoints",
                "does not perform orchestration recovery",
                "does not determine completion",
                "does not determine cancellation",
                "does not enqueue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire leases",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not persist orchestration state",
                "does not access Runtime State Store",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION",
    "UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION",
    "MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH",
    "MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS",
    "UniversalRuntimeOrchestrationContractError",
    "UniversalRuntimeOrchestrationContract",
    "normalize_universal_orchestration_identifier",
    "normalize_universal_orchestration_job_ids",
    "create_universal_runtime_orchestration_contract",
    "explain_universal_runtime_orchestration_contract_v1",
]
