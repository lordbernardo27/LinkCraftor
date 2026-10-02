"""
Canonical Universal Runtime Worker v1.

Canonical position:

    Canonical Orchestration Job Store
        ->
    dequeue_job(worker_id=...)
        ->
    atomic QUEUED -> RUNNING claim
        ->
    Universal Runtime Worker
        ->
    Runtime Registration Dispatcher
        ->
    registered handler
        ->
    COMPLETED or FAILED

This worker is intentionally one-shot.

It does:
- atomically claim at most one queued orchestration job;
- preserve the existing canonical job_id;
- convert OrchestrationJob into the Runtime Registration dispatch mapping;
- invoke the canonical Runtime Registration dispatcher;
- mark successful execution COMPLETED;
- mark exceptions FAILED;
- return an auditable worker result.

It does NOT:
- create jobs;
- mint replacement job identities;
- write the retired Universal Knowledge JSONL queue;
- use the older Universal Knowledge status/progress files;
- run an infinite polling loop;
- perform Runtime Registration mutation.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Callable, Mapping

from backend.server.orchestration.models import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_QUEUED,
    JOB_STATUS_RUNNING,
    OrchestrationJob,
)
from backend.server.orchestration.queue import (
    dequeue_job,
)
from backend.server.orchestration.service import (
    mark_job_completed,
    mark_job_failed,
)

from backend.server.orchestration.job_store import (
    update_job_status,
)
from backend.server.runtime.universal_runtime_registration import (
    dispatch_registered_runtime_handler,
    get_runtime_registration,
)


UNIVERSAL_RUNTIME_WORKER_VERSION = (
    "universal_runtime_worker_v1"
)

UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION = (
    "universal_runtime_worker_result_v1"
)


class UniversalRuntimeWorkerError(
    RuntimeError
):
    """Base error for canonical Universal Runtime Worker."""


class UniversalRuntimeWorkerContractError(
    UniversalRuntimeWorkerError
):
    """Raised when a claimed orchestration job violates the worker contract."""


class UniversalRuntimeWorkerFinalizationError(
    UniversalRuntimeWorkerError
):
    """Raised when canonical terminal-state persistence fails."""


def _datetime_value(
    value: Any,
) -> Any:
    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    return value


def orchestration_job_to_runtime_mapping_v1(
    job: OrchestrationJob,
) -> dict[str, Any]:
    """
    Convert one claimed OrchestrationJob into the canonical Runtime
    Registration dispatch mapping.

    This preserves job identity and does not reconstruct a new job.
    """

    if not isinstance(
        job,
        OrchestrationJob,
    ):
        raise UniversalRuntimeWorkerContractError(
            "job must be an OrchestrationJob."
        )

    job_id = str(
        job.job_id
        or ""
    ).strip()

    if not job_id:
        raise UniversalRuntimeWorkerContractError(
            "Claimed orchestration job has no job_id."
        )

    workspace_id = str(
        job.workspace_id
        or ""
    ).strip()

    if not workspace_id:
        raise UniversalRuntimeWorkerContractError(
            "Claimed orchestration job has no workspace_id."
        )

    job_type = str(
        job.job_type
        or ""
    ).strip()

    if not job_type:
        raise UniversalRuntimeWorkerContractError(
            "Claimed orchestration job has no job_type."
        )

    if job.status != JOB_STATUS_RUNNING:
        raise UniversalRuntimeWorkerContractError(
            "Worker may execute only a job already atomically "
            "claimed as RUNNING."
        )

    payload = job.payload

    if not isinstance(
        payload,
        Mapping,
    ):
        raise UniversalRuntimeWorkerContractError(
            "Claimed orchestration job payload must be a mapping."
        )

    metadata = job.metadata

    if not isinstance(
        metadata,
        Mapping,
    ):
        raise UniversalRuntimeWorkerContractError(
            "Claimed orchestration job metadata must be a mapping."
        )

    return {
        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "job_type":
            job_type,

        "status":
            job.status,

        "priority":
            job.priority,

        "created_at":
            _datetime_value(
                job.created_at
            ),

        "updated_at":
            _datetime_value(
                job.updated_at
            ),

        "started_at":
            _datetime_value(
                job.started_at
            ),

        "payload":
            deepcopy(
                dict(
                    payload
                )
            ),

        "metadata":
            deepcopy(
                dict(
                    metadata
                )
            ),
    }


def _runtime_retry_policy_v1(
    *,
    job_type: str,
) -> dict[str, Any]:
    """
    Resolve executable retry policy from Runtime Registration.

    Supports both:
      - maximum_attempts
      - max_attempts
    """

    registration = get_runtime_registration(
        job_type
    )

    if not isinstance(
        registration,
        Mapping,
    ):
        return {
            "maximum_attempts": 1,
            "retry_on_handler_error": False,
            "retry_on_contract_error": False,
        }

    raw_policy = registration.get(
        "retry_policy"
    )

    policy = (
        raw_policy
        if isinstance(
            raw_policy,
            Mapping,
        )
        else {}
    )

    raw_maximum_attempts = policy.get(
        "maximum_attempts",
        policy.get(
            "max_attempts",
            1,
        ),
    )

    try:
        maximum_attempts = int(
            raw_maximum_attempts
        )
    except (
        TypeError,
        ValueError,
    ):
        maximum_attempts = 1

    maximum_attempts = max(
        1,
        maximum_attempts,
    )

    retry_on_handler_error = bool(
        policy.get(
            "retry_on_handler_error",
            policy.get(
                "retryable",
                False,
            ),
        )
    )

    retry_on_contract_error = bool(
        policy.get(
            "retry_on_contract_error",
            False,
        )
    )

    return {
        "maximum_attempts":
            maximum_attempts,

        "retry_on_handler_error":
            retry_on_handler_error,

        "retry_on_contract_error":
            retry_on_contract_error,
    }


def _runtime_failure_is_contract_error_v1(
    exc: Exception,
) -> bool:
    """
    Classify canonical contract failures without coupling the
    universal worker to individual stage exception classes.
    """

    return type(
        exc
    ).__name__.endswith(
        "ContractError"
    )


def _runtime_failure_attempt_number_v1(
    metadata: Mapping[str, Any],
) -> int:
    """
    Return this failure's 1-based attempt number.
    """

    raw_previous = metadata.get(
        "runtime_failure_attempt_count",
        0,
    )

    try:
        previous = int(
            raw_previous
        )
    except (
        TypeError,
        ValueError,
    ):
        previous = 0

    previous = max(
        0,
        previous,
    )

    return previous + 1


def _requeue_same_runtime_job_v1(
    *,
    job_id: str,
    worker_id: str,
    error: Exception,
    attempt_number: int,
    maximum_attempts: int,
) -> OrchestrationJob:
    """
    Requeue the SAME canonical orchestration record.

    This function MUST NOT create a new Universal Job or a new
    orchestration job_id.
    """

    requeued = update_job_status(
        job_id,
        JOB_STATUS_QUEUED,
        metadata={
            "worker_id":
                worker_id,

            "runtime_worker_version":
                UNIVERSAL_RUNTIME_WORKER_VERSION,

            "runtime_dispatch_completed":
                False,

            "runtime_dispatch_failed":
                True,

            "runtime_retry_scheduled":
                True,

            "runtime_failure_attempt_count":
                attempt_number,

            "runtime_maximum_attempts":
                maximum_attempts,

            "runtime_retry_remaining":
                max(
                    0,
                    maximum_attempts
                    - attempt_number,
                ),

            "runtime_dispatch_error_type":
                type(
                    error
                ).__name__,

            "runtime_dispatch_error_message":
                str(
                    error
                ),

            "canonical_job_id_preserved":
                True,

            "retry_created_new_job":
                False,

            "old_universal_knowledge_jsonl_used":
                False,
        },

        error_message=None,
    )

    if requeued.job_id != job_id:
        raise UniversalRuntimeWorkerFinalizationError(
            "Same-job retry changed canonical job identity."
        )

    if requeued.status != JOB_STATUS_QUEUED:
        raise UniversalRuntimeWorkerFinalizationError(
            "Same-job retry did not persist QUEUED status."
        )

    return requeued


def run_one_universal_runtime_job_v1(
    *,
    worker_id: str = "universal_runtime_worker_v1",
    dispatcher: Callable[
        [Mapping[str, Any]],
        dict[str, Any],
    ] = dispatch_registered_runtime_handler,
) -> dict[str, Any]:
    """
    Claim and execute at most one canonical orchestration job.

    Returns IDLE when no queued work exists.

    The dequeue operation itself owns QUEUED -> RUNNING.
    """

    canonical_worker_id = str(
        worker_id
        or ""
    ).strip()

    if not canonical_worker_id:
        raise UniversalRuntimeWorkerContractError(
            "worker_id must not be empty."
        )

    if not callable(
        dispatcher
    ):
        raise UniversalRuntimeWorkerContractError(
            "dispatcher must be callable."
        )

    claimed_job = dequeue_job(
        worker_id=canonical_worker_id
    )

    if claimed_job is None:
        return {
            "schema_version":
                UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION,

            "worker_version":
                UNIVERSAL_RUNTIME_WORKER_VERSION,

            "worker_id":
                canonical_worker_id,

            "worker_status":
                "IDLE",

            "job_claimed":
                False,

            "job_id":
                None,

            "dispatch_performed":
                False,

            "terminal_status":
                None,
        }

    job_id = str(
        claimed_job.job_id
        or ""
    ).strip()

    if not job_id:
        raise UniversalRuntimeWorkerContractError(
            "dequeue_job returned a claimed job without job_id."
        )

    if claimed_job.status != JOB_STATUS_RUNNING:
        raise UniversalRuntimeWorkerContractError(
            "dequeue_job returned a job that is not RUNNING."
        )

    runtime_job = (
        orchestration_job_to_runtime_mapping_v1(
            claimed_job
        )
    )

    if runtime_job[
        "job_id"
    ] != job_id:
        raise UniversalRuntimeWorkerContractError(
            "Runtime mapping changed canonical job identity."
        )

    try:
        dispatch_result = dispatcher(
            runtime_job
        )

        if dispatch_result is None:
            dispatch_result = {}

        if not isinstance(
            dispatch_result,
            Mapping,
        ):
            dispatch_result = {
                "value":
                    dispatch_result,
            }

        completed_job = mark_job_completed(
            job_id,
            metadata={
                "worker_id":
                    canonical_worker_id,

                "runtime_worker_version":
                    UNIVERSAL_RUNTIME_WORKER_VERSION,

                "runtime_dispatch_completed":
                    True,

                "runtime_dispatch_result":
                    deepcopy(
                        dict(
                            dispatch_result
                        )
                    ),

                "canonical_job_id_preserved":
                    True,

                "old_universal_knowledge_jsonl_used":
                    False,
            },
        )

        if (
            completed_job.job_id
            != job_id
        ):
            raise UniversalRuntimeWorkerFinalizationError(
                "Completion changed canonical job identity."
            )

        if (
            completed_job.status
            != JOB_STATUS_COMPLETED
        ):
            raise UniversalRuntimeWorkerFinalizationError(
                "Completion did not persist COMPLETED status."
            )

        return {
            "schema_version":
                UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION,

            "worker_version":
                UNIVERSAL_RUNTIME_WORKER_VERSION,

            "worker_id":
                canonical_worker_id,

            "worker_status":
                "COMPLETED",

            "job_claimed":
                True,

            "job_id":
                job_id,

            "job_type":
                claimed_job.job_type,

            "claimed_status":
                JOB_STATUS_RUNNING,

            "dispatch_performed":
                True,

            "dispatch_result":
                deepcopy(
                    dict(
                        dispatch_result
                    )
                ),

            "terminal_status":
                completed_job.status,

            "canonical_job_id_preserved":
                True,

            "old_universal_knowledge_jsonl_used":
                False,
        }

    except UniversalRuntimeWorkerFinalizationError:
        raise

    except Exception as exc:

        error_message = (
            f"{type(exc).__name__}: {exc}"
        )

        claimed_metadata = (
            claimed_job.metadata
            if isinstance(
                claimed_job.metadata,
                Mapping,
            )
            else {}
        )

        attempt_number = (
            _runtime_failure_attempt_number_v1(
                claimed_metadata
            )
        )

        retry_policy = (
            _runtime_retry_policy_v1(
                job_type=
                    claimed_job.job_type
            )
        )

        maximum_attempts = int(
            retry_policy[
                "maximum_attempts"
            ]
        )

        contract_error = (
            _runtime_failure_is_contract_error_v1(
                exc
            )
        )

        if contract_error:
            retry_type_allowed = bool(
                retry_policy[
                    "retry_on_contract_error"
                ]
            )
        else:
            retry_type_allowed = bool(
                retry_policy[
                    "retry_on_handler_error"
                ]
            )

        retry_ceiling_allows = (
            attempt_number
            < maximum_attempts
        )

        retry_allowed = (
            retry_type_allowed
            and retry_ceiling_allows
        )

        # ====================================================
        # RETRY PATH
        # SAME canonical job_id -> QUEUED
        # ====================================================

        if retry_allowed:

            try:
                requeued_job = (
                    _requeue_same_runtime_job_v1(
                        job_id=
                            job_id,

                        worker_id=
                            canonical_worker_id,

                        error=
                            exc,

                        attempt_number=
                            attempt_number,

                        maximum_attempts=
                            maximum_attempts,
                    )
                )

            except Exception as finalization_exc:
                raise UniversalRuntimeWorkerFinalizationError(
                    "Runtime dispatch failed and same-job retry "
                    "could not be persisted."
                ) from finalization_exc

            return {
                "schema_version":
                    UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION,

                "worker_version":
                    UNIVERSAL_RUNTIME_WORKER_VERSION,

                "worker_id":
                    canonical_worker_id,

                "worker_status":
                    "RETRY_QUEUED",

                "job_claimed":
                    True,

                "job_id":
                    job_id,

                "job_type":
                    claimed_job.job_type,

                "claimed_status":
                    JOB_STATUS_RUNNING,

                "dispatch_performed":
                    True,

                "dispatch_succeeded":
                    False,

                "dispatch_error_type":
                    type(
                        exc
                    ).__name__,

                "dispatch_error":
                    str(
                        exc
                    ),

                "contract_error":
                    contract_error,

                "retry_type_allowed":
                    retry_type_allowed,

                "retry_ceiling_allows":
                    retry_ceiling_allows,

                "retry_allowed":
                    True,

                "retry_scheduled":
                    True,

                "attempt_number":
                    attempt_number,

                "maximum_attempts":
                    maximum_attempts,

                "queue_status":
                    requeued_job.status,

                "terminal_status":
                    None,

                "canonical_job_id_preserved":
                    True,

                "retry_created_new_job":
                    False,

                "old_universal_knowledge_jsonl_used":
                    False,
            }

        # ====================================================
        # TERMINAL FAILURE PATH
        # SAME canonical job_id -> FAILED
        # ====================================================

        try:
            failed_job = mark_job_failed(
                job_id,
                error_message,
                metadata={
                    "worker_id":
                        canonical_worker_id,

                    "runtime_worker_version":
                        UNIVERSAL_RUNTIME_WORKER_VERSION,

                    "runtime_dispatch_completed":
                        False,

                    "runtime_dispatch_failed":
                        True,

                    "runtime_retry_scheduled":
                        False,

                    "runtime_failure_attempt_count":
                        attempt_number,

                    "runtime_maximum_attempts":
                        maximum_attempts,

                    "runtime_retry_type_allowed":
                        retry_type_allowed,

                    "runtime_retry_exhausted":
                        (
                            retry_type_allowed
                            and not retry_ceiling_allows
                        ),

                    "runtime_contract_error":
                        contract_error,

                    "runtime_dispatch_error_type":
                        type(
                            exc
                        ).__name__,

                    "canonical_job_id_preserved":
                        True,

                    "retry_created_new_job":
                        False,

                    "old_universal_knowledge_jsonl_used":
                        False,
                },
            )

        except Exception as finalization_exc:
            raise UniversalRuntimeWorkerFinalizationError(
                "Runtime dispatch failed and FAILED status "
                "could not be persisted."
            ) from finalization_exc

        if failed_job.job_id != job_id:
            raise UniversalRuntimeWorkerFinalizationError(
                "Failure finalization changed canonical job identity."
            )

        if failed_job.status != JOB_STATUS_FAILED:
            raise UniversalRuntimeWorkerFinalizationError(
                "Failure finalization did not persist FAILED status."
            )

        return {
            "schema_version":
                UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION,

            "worker_version":
                UNIVERSAL_RUNTIME_WORKER_VERSION,

            "worker_id":
                canonical_worker_id,

            "worker_status":
                "FAILED",

            "job_claimed":
                True,

            "job_id":
                job_id,

            "job_type":
                claimed_job.job_type,

            "claimed_status":
                JOB_STATUS_RUNNING,

            "dispatch_performed":
                True,

            "dispatch_succeeded":
                False,

            "dispatch_error_type":
                type(
                    exc
                ).__name__,

            "dispatch_error":
                str(
                    exc
                ),

            "contract_error":
                contract_error,

            "retry_type_allowed":
                retry_type_allowed,

            "retry_ceiling_allows":
                retry_ceiling_allows,

            "retry_allowed":
                False,

            "retry_scheduled":
                False,

            "attempt_number":
                attempt_number,

            "maximum_attempts":
                maximum_attempts,

            "retry_exhausted":
                (
                    retry_type_allowed
                    and not retry_ceiling_allows
                ),

            "terminal_status":
                failed_job.status,

            "canonical_job_id_preserved":
                True,

            "retry_created_new_job":
                False,

            "old_universal_knowledge_jsonl_used":
                False,
        }



def explain_universal_runtime_worker_v1() -> dict[str, Any]:
    """Return the canonical Stage 10.8 worker contract."""

    return {
        "component":
            "Universal Runtime Worker",

        "version":
            UNIVERSAL_RUNTIME_WORKER_VERSION,

        "execution_model":
            "one-shot",

        "queue_source":
            "canonical orchestration persisted job store",

        "claim_operation":
            "dequeue_job(worker_id=...)",

        "claim_transition":
            "QUEUED -> RUNNING owned by dequeue_job",

        "dispatcher":
            "dispatch_registered_runtime_handler",

        "success_transition":
            "RUNNING -> COMPLETED via mark_job_completed",

        "failure_transition":
            (
                "RUNNING -> QUEUED for permitted retry; "
                "RUNNING -> FAILED when retry is disallowed "
                "or exhausted"
            ),

        "retry_policy_source":
            "Runtime Registration retry_policy",

        "retry_job_identity_rule":
            "same canonical job_id; no replacement job",

        "canonical_job_id_preserved":
            True,

        "old_universal_knowledge_jsonl_used":
            False,

        "older_execute_registered_runtime_job_v1_used":
            False,

        "infinite_loop":
            False,
    }


__all__ = [
    "UNIVERSAL_RUNTIME_WORKER_VERSION",
    "UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION",
    "UniversalRuntimeWorkerError",
    "UniversalRuntimeWorkerContractError",
    "UniversalRuntimeWorkerFinalizationError",
    "orchestration_job_to_runtime_mapping_v1",
    "run_one_universal_runtime_job_v1",
    "explain_universal_runtime_worker_v1",
]
