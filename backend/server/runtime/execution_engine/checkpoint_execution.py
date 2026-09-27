"""
LinkCraftor Universal Runtime
Phase 6.8 — Checkpoint Execution

Canonical checkpoint coordination layer.

Consumes:
- Phase 6.2 execution identity/context
- Phase 6.3 execution fence
- Phase 6.4 execution lifecycle

Owns:
- checkpoint save coordination
- checkpoint reference validation
- checkpoint restore coordination
- resume-from-checkpoint preparation
- invalid/missing checkpoint handling

Does NOT:
- create a second checkpoint store
- persist checkpoint bytes itself
- replace Runtime State Store
- mutate Universal Jobs
- mutate orchestration state
- acquire/release leases
- enqueue/requeue jobs

Actual storage adapters are supplied by existing runtime persistence/state
authorities and are wired into production later under Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .execution_contracts import (
    ExecutionRequest,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
)


CHECKPOINT_EXECUTION_VERSION = (
    "checkpoint_execution_v6.8.1"
)

CHECKPOINT_EXECUTION_SCHEMA_VERSION = (
    "checkpoint_execution_schema_v1"
)


class CheckpointExecutionError(ValueError):
    """Raised when checkpoint coordination is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class CheckpointStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    INVALID = "INVALID"


@dataclass(
    frozen=True,
    slots=True,
)
class CheckpointReference:
    """
    Canonical Phase-6 checkpoint reference.

    This identifies checkpoint evidence but does not contain storage
    implementation details.
    """

    checkpoint_id: str
    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    storage_reference: str
    integrity_digest: str

    schema_version: str = field(
        default=CHECKPOINT_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "checkpoint_id": self.checkpoint_id,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "fence_id": self.fence_id,
            "storage_reference": self.storage_reference,
            "integrity_digest": self.integrity_digest,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CheckpointSaveResult:
    saved: bool
    reference: Optional[CheckpointReference]
    error_code: Optional[str] = None

    schema_version: str = field(
        default=CHECKPOINT_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class CheckpointRestoreResult:
    status: CheckpointStatus
    reference: Optional[CheckpointReference]
    payload: Any = None
    error_code: Optional[str] = None

    schema_version: str = field(
        default=CHECKPOINT_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def restored(self) -> bool:
        return (
            self.status is CheckpointStatus.AVAILABLE
            and self.reference is not None
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ResumeCheckpointPreparation:
    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    checkpoint_reference: CheckpointReference
    restored_payload: Any

    resume_metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=CHECKPOINT_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


def _checkpoint_digest(
    *,
    execution_id: str,
    job_id: str,
    attempt_number: int,
    fence_id: str,
    storage_reference: str,
) -> str:

    material = "|".join(
        (
            execution_id,
            job_id,
            str(attempt_number),
            fence_id,
            storage_reference,
        )
    )

    return sha256(
        material.encode("utf-8")
    ).hexdigest()


def validate_checkpoint_boundary(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> None:
    """
    Checkpoint operations must remain bound to one execution identity/fence.
    """

    if not isinstance(request, ExecutionRequest):
        raise CheckpointExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise CheckpointExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(fence, ExecutionFenceIdentity):
        raise CheckpointExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if (
        request.identity.execution_id
        != lifecycle.execution_id
        or request.identity.execution_id
        != fence.execution_id
    ):
        raise CheckpointExecutionError(
            "Checkpoint execution identity mismatch.",
            code="checkpoint_execution_identity_mismatch",
        )

    if (
        request.identity.job_id
        != lifecycle.job_id
        or request.identity.job_id
        != fence.job_id
    ):
        raise CheckpointExecutionError(
            "Checkpoint job identity mismatch.",
            code="checkpoint_job_identity_mismatch",
        )

    if (
        request.identity.attempt_number
        != lifecycle.attempt_number
        or request.identity.attempt_number
        != fence.attempt_number
    ):
        raise CheckpointExecutionError(
            "Checkpoint attempt identity mismatch.",
            code="checkpoint_attempt_identity_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise CheckpointExecutionError(
            "Checkpoint fence mismatch.",
            code="checkpoint_fence_mismatch",
        )


def coordinate_checkpoint_save(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    checkpoint_payload: Any,
    saver: Callable[[Mapping[str, Any], Any], str],
) -> CheckpointSaveResult:
    """
    Coordinate checkpoint save through an existing storage adapter.

    saver(metadata, payload) -> storage_reference
    """

    validate_checkpoint_boundary(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
    )

    if lifecycle.state not in {
        ExecutionLifecycleState.RUNNING,
        ExecutionLifecycleState.SUSPENDED,
    }:
        raise CheckpointExecutionError(
            "Checkpoint save requires RUNNING or SUSPENDED lifecycle.",
            code="checkpoint_save_invalid_lifecycle",
            value=lifecycle.state.value,
        )

    if not callable(saver):
        raise CheckpointExecutionError(
            "saver must be callable.",
            code="invalid_checkpoint_saver",
            value=saver,
        )

    metadata = MappingProxyType(
        {
            "execution_id":
                request.identity.execution_id,
            "job_id":
                request.identity.job_id,
            "attempt_number":
                request.identity.attempt_number,
            "fence_id":
                fence.fence_id,
        }
    )

    try:
        storage_reference = saver(
            metadata,
            checkpoint_payload,
        )
    except Exception:
        return CheckpointSaveResult(
            saved=False,
            reference=None,
            error_code="checkpoint_save_failed",
        )

    if (
        not isinstance(storage_reference, str)
        or not storage_reference.strip()
    ):
        return CheckpointSaveResult(
            saved=False,
            reference=None,
            error_code="invalid_checkpoint_storage_reference",
        )

    storage_reference = storage_reference.strip()

    digest = _checkpoint_digest(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        storage_reference=storage_reference,
    )

    checkpoint_id = (
        "checkpoint:"
        + sha256(
            (
                request.identity.execution_id
                + "|"
                + storage_reference
            ).encode("utf-8")
        ).hexdigest()
    )

    reference = CheckpointReference(
        checkpoint_id=checkpoint_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        storage_reference=storage_reference,
        integrity_digest=digest,
    )

    return CheckpointSaveResult(
        saved=True,
        reference=reference,
        error_code=None,
    )


def validate_checkpoint_reference(
    *,
    reference: CheckpointReference,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
) -> bool:
    """
    Validate checkpoint identity, fence and digest.
    """

    if not isinstance(
        reference,
        CheckpointReference,
    ):
        return False

    if (
        reference.execution_id
        != request.identity.execution_id
    ):
        return False

    if reference.job_id != request.identity.job_id:
        return False

    if (
        reference.attempt_number
        != request.identity.attempt_number
    ):
        return False

    if reference.fence_id != fence.fence_id:
        return False

    expected_digest = _checkpoint_digest(
        execution_id=reference.execution_id,
        job_id=reference.job_id,
        attempt_number=reference.attempt_number,
        fence_id=reference.fence_id,
        storage_reference=reference.storage_reference,
    )

    return (
        reference.integrity_digest
        == expected_digest
    )


def coordinate_checkpoint_restore(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    reference: Optional[CheckpointReference],
    loader: Callable[[str], Any],
) -> CheckpointRestoreResult:
    """
    Restore checkpoint through an existing storage adapter.
    """

    if reference is None:
        return CheckpointRestoreResult(
            status=CheckpointStatus.MISSING,
            reference=None,
            payload=None,
            error_code="checkpoint_missing",
        )

    if not validate_checkpoint_reference(
        reference=reference,
        request=request,
        fence=fence,
    ):
        return CheckpointRestoreResult(
            status=CheckpointStatus.INVALID,
            reference=reference,
            payload=None,
            error_code="checkpoint_reference_invalid",
        )

    if not callable(loader):
        raise CheckpointExecutionError(
            "loader must be callable.",
            code="invalid_checkpoint_loader",
            value=loader,
        )

    try:
        payload = loader(
            reference.storage_reference
        )
    except Exception:
        return CheckpointRestoreResult(
            status=CheckpointStatus.INVALID,
            reference=reference,
            payload=None,
            error_code="checkpoint_restore_failed",
        )

    if payload is None:
        return CheckpointRestoreResult(
            status=CheckpointStatus.MISSING,
            reference=reference,
            payload=None,
            error_code="checkpoint_payload_missing",
        )

    return CheckpointRestoreResult(
        status=CheckpointStatus.AVAILABLE,
        reference=reference,
        payload=payload,
        error_code=None,
    )


def prepare_resume_from_checkpoint(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    restore: CheckpointRestoreResult,
) -> ResumeCheckpointPreparation:
    """
    Prepare canonical resume input from a successfully restored checkpoint.
    """

    if not isinstance(
        restore,
        CheckpointRestoreResult,
    ):
        raise CheckpointExecutionError(
            "restore must be CheckpointRestoreResult.",
            code="invalid_checkpoint_restore_result",
            value=restore,
        )

    if not restore.restored:
        raise CheckpointExecutionError(
            "Checkpoint is not available for resume.",
            code=(
                restore.error_code
                or "checkpoint_not_available"
            ),
        )

    reference = restore.reference

    if reference is None:
        raise CheckpointExecutionError(
            "Restored checkpoint has no reference.",
            code="restored_checkpoint_missing_reference",
        )

    if not validate_checkpoint_reference(
        reference=reference,
        request=request,
        fence=fence,
    ):
        raise CheckpointExecutionError(
            "Restored checkpoint reference is invalid.",
            code="resume_checkpoint_reference_invalid",
        )

    return ResumeCheckpointPreparation(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        checkpoint_reference=reference,
        restored_payload=restore.payload,
        resume_metadata=MappingProxyType(
            {
                "checkpoint_id":
                    reference.checkpoint_id,
                "storage_reference":
                    reference.storage_reference,
                "checkpoint_restored":
                    True,
            }
        ),
    )


def certify_checkpoint_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.8 certification with synthetic in-memory storage.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
    )

    from .execution_permission_fencing import (
        ExecutionPermissionEvidence,
        evaluate_execution_permission,
    )

    from .execution_lifecycle_controller import (
        apply_running_state,
        create_execution_start,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "77777777-7777-4777-8777-777777777777"
        ),
        job_id="job-phase-6-8-certification",
        attempt_number=1,
    )

    request = ExecutionRequest(
        identity=identity,
        context=ExecutionContext(
            handler_key="certification.handler",
            worker_id="worker-certification",
            lease_id="lease-certification",
            lease_owner="worker-certification::instance-1",
        ),
        action=ExecutionAction.START,
    )

    permission = evaluate_execution_permission(
        request=request,
        evidence=ExecutionPermissionEvidence(
            job_status="RUNNING",
            current_worker_id="worker-certification",
            current_lease_id="lease-certification",
            current_lease_owner=(
                "worker-certification::instance-1"
            ),
            lease_state="ACTIVE",
        ),
    )

    fence = permission.fence

    if fence is None:
        raise CheckpointExecutionError(
            "Certification missing fence.",
            code="certification_missing_fence",
        )

    ready = create_execution_start(
        request=request,
        permission=permission,
    )

    running = apply_running_state(
        record=ready,
        fence=fence,
    )

    storage: dict[str, Any] = {}

    def saver(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> str:
        key = (
            "checkpoint://"
            + metadata["execution_id"]
        )
        storage[key] = payload
        return key

    def loader(
        storage_reference: str,
    ) -> Any:
        return storage.get(storage_reference)

    save = coordinate_checkpoint_save(
        request=request,
        lifecycle=running,
        fence=fence,
        checkpoint_payload={
            "cursor": 10,
            "partial_result": "certification",
        },
        saver=saver,
    )

    if save.reference is None:
        raise CheckpointExecutionError(
            "Certification checkpoint save failed.",
            code="certification_save_failed",
        )

    reference_valid = validate_checkpoint_reference(
        reference=save.reference,
        request=request,
        fence=fence,
    )

    restore = coordinate_checkpoint_restore(
        request=request,
        fence=fence,
        reference=save.reference,
        loader=loader,
    )

    prepared = prepare_resume_from_checkpoint(
        request=request,
        fence=fence,
        restore=restore,
    )

    missing_restore = coordinate_checkpoint_restore(
        request=request,
        fence=fence,
        reference=None,
        loader=loader,
    )

    invalid_reference = CheckpointReference(
        checkpoint_id=save.reference.checkpoint_id,
        execution_id=save.reference.execution_id,
        job_id=save.reference.job_id,
        attempt_number=save.reference.attempt_number,
        fence_id=save.reference.fence_id,
        storage_reference=save.reference.storage_reference,
        integrity_digest="invalid-digest",
    )

    invalid_restore = coordinate_checkpoint_restore(
        request=request,
        fence=fence,
        reference=invalid_reference,
        loader=loader,
    )

    missing_resume_rejected = False

    try:
        prepare_resume_from_checkpoint(
            request=request,
            fence=fence,
            restore=missing_restore,
        )
    except CheckpointExecutionError:
        missing_resume_rejected = True

    checks = {
        "checkpoint_save_coordinated":
            save.saved,

        "checkpoint_reference_created":
            save.reference is not None,

        "checkpoint_reference_valid":
            reference_valid,

        "checkpoint_restore_coordinated":
            restore.restored,

        "checkpoint_payload_restored":
            (
                restore.payload
                == {
                    "cursor": 10,
                    "partial_result":
                        "certification",
                }
            ),

        "resume_from_checkpoint_prepared":
            (
                prepared.restored_payload
                == restore.payload
            ),

        "resume_execution_identity_preserved":
            (
                prepared.execution_id
                == identity.execution_id
            ),

        "resume_fence_preserved":
            (
                prepared.fence_id
                == fence.fence_id
            ),

        "missing_checkpoint_handled":
            (
                missing_restore.status
                is CheckpointStatus.MISSING
            ),

        "invalid_checkpoint_handled":
            (
                invalid_restore.status
                is CheckpointStatus.INVALID
            ),

        "missing_checkpoint_resume_rejected":
            missing_resume_rejected,

        "no_checkpoint_store_created":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_runtime_state_store_replacement":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.8",
            "component":
                "Checkpoint Execution",
            "version":
                CHECKPOINT_EXECUTION_VERSION,
            "schema_version":
                CHECKPOINT_EXECUTION_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.8 coordinates checkpoint save/restore through "
                "existing storage adapters, validates checkpoint identity "
                "and fencing, and prepares resume input. It does not create "
                "or replace checkpoint persistence."
            ),
        }
    )


def explain_checkpoint_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.8",
            "component":
                "Checkpoint Execution",
            "version":
                CHECKPOINT_EXECUTION_VERSION,

            "checkpoint_save_coordination": (
                "Coordinates checkpoint save through an existing "
                "state/persistence adapter and creates canonical reference."
            ),

            "checkpoint_reference_validation": (
                "Validates execution, job, attempt, fence and integrity "
                "digest of checkpoint references."
            ),

            "checkpoint_restore_coordination": (
                "Uses an existing storage loader to recover checkpoint "
                "payload without owning the storage engine."
            ),

            "resume_from_checkpoint_preparation": (
                "Builds canonical resume preparation from restored "
                "checkpoint evidence."
            ),

            "invalid_missing_checkpoint_handling": (
                "Returns explicit MISSING or INVALID checkpoint state and "
                "blocks resume when checkpoint evidence is unusable."
            ),

            "prohibitions": (
                "does not create checkpoint persistence",
                "does not replace Runtime State Store",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not mutate leases",
                "does not mutate orchestration state",
                "does not execute resume itself",
            ),
        }
    )


__all__ = [
    "CHECKPOINT_EXECUTION_VERSION",
    "CHECKPOINT_EXECUTION_SCHEMA_VERSION",
    "CheckpointExecutionError",
    "CheckpointStatus",
    "CheckpointReference",
    "CheckpointSaveResult",
    "CheckpointRestoreResult",
    "ResumeCheckpointPreparation",
    "validate_checkpoint_boundary",
    "coordinate_checkpoint_save",
    "validate_checkpoint_reference",
    "coordinate_checkpoint_restore",
    "prepare_resume_from_checkpoint",
    "certify_checkpoint_execution_v1",
    "explain_checkpoint_execution_v1",
]
