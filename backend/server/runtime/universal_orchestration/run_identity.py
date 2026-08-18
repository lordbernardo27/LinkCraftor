from __future__ import annotations

import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.runtime.universal_orchestration.contract import (
    MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH,
    UniversalRuntimeOrchestrationContract,
    normalize_universal_orchestration_identifier,
)


UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION = (
    "universal_orchestration_run_identity_v5.1.2"
)

UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION = (
    "universal_orchestration_run_identity_schema_v1"
)

UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM = "sha256"


class UniversalOrchestrationRunIdentityError(
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


def normalize_universal_orchestration_run_id(
    value: Any,
) -> str:

    try:

        return normalize_universal_orchestration_identifier(
            value,
            field_name="orchestration_run_id",
        )

    except Exception as exc:

        if isinstance(
            exc,
            UniversalOrchestrationRunIdentityError,
        ):

            raise

        code = getattr(
            exc,
            "code",
            "invalid_orchestration_run_id",
        )

        if code == "orchestration_identifier_too_long":

            code = "orchestration_run_id_too_long"

        else:

            code = "invalid_orchestration_run_id"

        raise UniversalOrchestrationRunIdentityError(
            "Invalid orchestration_run_id.",
            code=code,
            value=value,
        ) from exc


def _require_orchestration_contract(
    value: Any,
) -> UniversalRuntimeOrchestrationContract:

    if not isinstance(
        value,
        UniversalRuntimeOrchestrationContract,
    ):

        raise UniversalOrchestrationRunIdentityError(
            (
                "contract must be a "
                "UniversalRuntimeOrchestrationContract."
            ),
            code="invalid_orchestration_run_contract",
            value=value,
        )

    return value


def _length_prefixed(
    value: str,
) -> str:

    return (
        str(
            len(
                value
            )
        )
        + ":"
        + value
    )


def calculate_universal_orchestration_contract_fingerprint(
    contract: Any,
) -> str:

    canonical_contract = (
        _require_orchestration_contract(
            contract
        )
    )

    parts = (
        "universal_runtime_orchestration_contract_identity_v1",
        canonical_contract.schema_version,
        canonical_contract.workspace_id,
        canonical_contract.pipeline,
        str(
            canonical_contract.job_count
        ),
        *canonical_contract.job_ids,
    )

    material = "|".join(
        _length_prefixed(
            str(
                part
            )
        )
        for part in parts
    )

    return hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def calculate_universal_orchestration_run_identity_fingerprint(
    *,
    orchestration_run_id: Any,
    contract: Any,
) -> str:

    normalized_run_id = (
        normalize_universal_orchestration_run_id(
            orchestration_run_id
        )
    )

    canonical_contract = (
        _require_orchestration_contract(
            contract
        )
    )

    contract_fingerprint = (
        calculate_universal_orchestration_contract_fingerprint(
            canonical_contract
        )
    )

    parts = (
        UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION,
        normalized_run_id,
        contract_fingerprint,
    )

    material = "|".join(
        _length_prefixed(
            str(
                part
            )
        )
        for part in parts
    )

    return hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationRunIdentity:

    orchestration_run_id: str

    contract: UniversalRuntimeOrchestrationContract

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        run_id = (
            normalize_universal_orchestration_run_id(
                self.orchestration_run_id
            )
        )

        canonical_contract = (
            _require_orchestration_contract(
                self.contract
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationRunIdentityError(
                "Invalid Orchestration Run Identity schema_version.",
                code="invalid_orchestration_run_identity_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "orchestration_run_id",
            run_id,
        )

        object.__setattr__(
            self,
            "contract",
            canonical_contract,
        )

    @property
    def workspace_id(
        self,
    ) -> str:

        return self.contract.workspace_id

    @property
    def pipeline(
        self,
    ) -> str:

        return self.contract.pipeline

    @property
    def job_ids(
        self,
    ) -> tuple[str, ...]:

        return self.contract.job_ids

    @property
    def job_count(
        self,
    ) -> int:

        return self.contract.job_count

    @property
    def contract_fingerprint(
        self,
    ) -> str:

        return (
            calculate_universal_orchestration_contract_fingerprint(
                self.contract
            )
        )

    @property
    def identity_fingerprint(
        self,
    ) -> str:

        return (
            calculate_universal_orchestration_run_identity_fingerprint(
                orchestration_run_id=self.orchestration_run_id,
                contract=self.contract,
            )
        )


def create_universal_orchestration_run_identity(
    *,
    orchestration_run_id: Any,
    contract: Any,
) -> UniversalOrchestrationRunIdentity:

    return UniversalOrchestrationRunIdentity(
        orchestration_run_id=orchestration_run_id,
        contract=contract,
    )


def explain_universal_orchestration_run_identity_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.2",

            "component":
                "Universal Orchestration Run Identity",

            "version":
                UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION,

            "hash_algorithm":
                UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM,

            "stored_fields": (
                "orchestration_run_id",
                "contract",
                "schema_version",
            ),

            "identity_rule": (
                "One runtime orchestration run is identified by a "
                "caller-supplied orchestration_run_id bound to one "
                "immutable 5.1.1 Universal Runtime Orchestration Contract."
            ),

            "generation_rule": (
                "5.1.2 validates caller-supplied orchestration_run_id "
                "and does not generate identifiers using UUIDs, "
                "randomness, timestamps, wall clock, counters, or storage."
            ),

            "contract_binding_rule": (
                "The run identity stores the immutable 5.1.1 contract "
                "rather than duplicating workspace_id, pipeline, or job_ids."
            ),

            "contract_fingerprint_rule": (
                "contract_fingerprint is deterministically derived from "
                "the exact canonical 5.1.1 contract and is not stored."
            ),

            "identity_fingerprint_rule": (
                "identity_fingerprint is deterministically derived from "
                "orchestration_run_id, contract_fingerprint, and the "
                "5.1.2 identity schema version and is not stored."
            ),

            "multiple_run_rule": (
                "The same 5.1.1 orchestration contract may participate "
                "in multiple independently identified orchestration runs."
            ),

            "pipeline_run_boundary": (
                "Universal Job pipeline_run_id remains optional "
                "job-lineage/correlation evidence and is not the "
                "5.1.2 orchestration_run_id."
            ),

            "batch_boundary": (
                "Universal Job batch_id remains grouping/correlation "
                "evidence and is not orchestration_run_id."
            ),

            "job_boundary": (
                "Universal Job job_id identifies one job and is not "
                "orchestration_run_id."
            ),

            "workflow_boundary": (
                "Universal Coordination Framework workflow_id remains "
                "a higher-layer coordination identity and is not "
                "orchestration_run_id."
            ),

            "correlation_boundary": (
                "Coordination correlation_id remains separate from "
                "Runtime Orchestration run identity."
            ),

            "state_boundary": (
                "Orchestration lifecycle state belongs to "
                "5.1.3 Orchestration State Model."
            ),

            "persistence_boundary": (
                "5.1.2 performs no persistence and does not access "
                "Runtime State Store."
            ),

            "execution_boundary": (
                "5.1.2 performs no queue, worker, Runtime Registration, "
                "handler dispatch, or job execution activity."
            ),

            "prohibitions": (
                "does not generate orchestration_run_id",
                "does not use UUID generation",
                "does not use randomness",
                "does not use timestamps for identity",
                "does not use wall clock",
                "does not use counters for identity",
                "does not use storage for identity generation",
                "does not redefine Universal Job job_id",
                "does not redefine Universal Job pipeline_run_id",
                "does not redefine Universal Job batch_id",
                "does not redefine Coordination workflow_id",
                "does not redefine Coordination correlation_id",
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
                "does not acquire worker leases",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not persist orchestration identity",
                "does not access Runtime State Store",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION",
    "UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM",
    "UniversalOrchestrationRunIdentityError",
    "UniversalOrchestrationRunIdentity",
    "normalize_universal_orchestration_run_id",
    "calculate_universal_orchestration_contract_fingerprint",
    "calculate_universal_orchestration_run_identity_fingerprint",
    "create_universal_orchestration_run_identity",
    "explain_universal_orchestration_run_identity_v1",
]
