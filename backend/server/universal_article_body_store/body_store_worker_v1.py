"""Canonical synchronous Universal Article Body Store Worker.

Placement:

Caller / future queue
    -> Body Store Worker
    -> Body Store Runtime
    -> Body Store Repository
    -> Writer / Management Layer
    -> Persistent Body Store

The Worker executes one supplied job envelope at a time. It does not
create, persist, claim, lease, retry, acknowledge, or consume jobs.
It does not duplicate Runtime operation dispatch.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from backend.server.universal_article_body_store.body_store_runtime_v1 import (
    execute_body_store_runtime_v1,
)


BODY_STORE_WORKER_VERSION = (
    "universal_article_body_store_worker_v1"
)

BODY_STORE_WORKER_JOB_SCHEMA_VERSION = (
    "body_store_worker_job_v1"
)

BODY_STORE_WORKER_RESULT_SCHEMA_VERSION = (
    "body_store_worker_result_v1"
)


class BodyStoreWorkerContractError(
    ValueError
):
    """Raised when a Body Store Worker job envelope is invalid."""


class BodyStoreWorkerExecutionError(
    RuntimeError
):
    """Raised when Runtime execution fails and raising is requested."""


def _now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _new_worker_execution_id() -> str:
    return (
        "body_store_worker_"
        + uuid4().hex
    )


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreWorkerContractError(
            field_name
            + " must be a mapping."
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreWorkerContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreWorkerContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_positive_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 1
    ):
        raise BodyStoreWorkerContractError(
            field_name
            + " must be a positive integer."
        )

    return value


def _success_result(
    *,
    worker_execution_id: str,
    job_id: str,
    attempt: int,
    started_at: str,
    runtime_result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "worker_result_schema_version":
            BODY_STORE_WORKER_RESULT_SCHEMA_VERSION,

        "worker_version":
            BODY_STORE_WORKER_VERSION,

        "worker_execution_id":
            worker_execution_id,

        "job_id":
            job_id,

        "attempt":
            attempt,

        "worker_status":
            "COMPLETED",

        "success":
            True,

        "started_at":
            started_at,

        "completed_at":
            _now_iso(),

        "runtime_result":
            dict(
                runtime_result
            ),

        "error":
            None,

        "execution_mode":
            "SYNCHRONOUS",

        "queue_used":
            False,

        "runtime_registration_used":
            False,

        "retry_performed":
            False,
    }


def _failure_result(
    *,
    worker_execution_id: str,
    job_id: str | None,
    attempt: int | None,
    started_at: str,
    runtime_result: Mapping[str, Any] | None,
    error: Exception | Mapping[str, Any],
) -> dict[str, Any]:
    if isinstance(
        error,
        Mapping,
    ):
        normalized_error = {
            "error_type":
                str(
                    error.get(
                        "error_type",
                        "RuntimeFailure",
                    )
                ),

            "message":
                str(
                    error.get(
                        "message",
                        "Body Store Runtime execution failed.",
                    )
                ),
        }

    else:
        normalized_error = {
            "error_type":
                type(
                    error
                ).__name__,

            "message":
                str(
                    error
                ),
        }

    return {
        "worker_result_schema_version":
            BODY_STORE_WORKER_RESULT_SCHEMA_VERSION,

        "worker_version":
            BODY_STORE_WORKER_VERSION,

        "worker_execution_id":
            worker_execution_id,

        "job_id":
            job_id,

        "attempt":
            attempt,

        "worker_status":
            "FAILED",

        "success":
            False,

        "started_at":
            started_at,

        "completed_at":
            _now_iso(),

        "runtime_result":
            (
                dict(
                    runtime_result
                )
                if runtime_result is not None
                else None
            ),

        "error":
            normalized_error,

        "execution_mode":
            "SYNCHRONOUS",

        "queue_used":
            False,

        "runtime_registration_used":
            False,

        "retry_performed":
            False,
    }


def execute_body_store_worker_v1(
    job: Mapping[str, Any],
    *,
    project_root: str | Path,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Execute one supplied Body Store Worker job synchronously."""

    worker_execution_id = (
        _new_worker_execution_id()
    )

    started_at = _now_iso()

    job_id: str | None = None
    attempt: int | None = None
    runtime_result: Mapping[str, Any] | None = None

    try:
        job_mapping = _require_mapping(
            job,
            field_name="job",
        )

        schema_version = _require_string(
            job_mapping.get(
                "job_schema_version"
            ),
            field_name="job.job_schema_version",
        )

        if (
            schema_version
            != BODY_STORE_WORKER_JOB_SCHEMA_VERSION
        ):
            raise BodyStoreWorkerContractError(
                "Unsupported Body Store Worker job schema: "
                + schema_version
            )

        job_id = _require_string(
            job_mapping.get(
                "job_id"
            ),
            field_name="job.job_id",
        )

        attempt = _require_positive_integer(
            job_mapping.get(
                "attempt",
                1,
            ),
            field_name="job.attempt",
        )

        runtime_request = _require_mapping(
            job_mapping.get(
                "runtime_request"
            ),
            field_name="job.runtime_request",
        )

        runtime_result = (
            execute_body_store_runtime_v1(
                runtime_request,
                project_root=project_root,
            )
        )

        if (
            runtime_result.get(
                "success"
            )
            is not True
        ):
            runtime_error = runtime_result.get(
                "error"
            )

            failure = _failure_result(
                worker_execution_id=worker_execution_id,
                job_id=job_id,
                attempt=attempt,
                started_at=started_at,
                runtime_result=runtime_result,
                error=(
                    runtime_error
                    if isinstance(
                        runtime_error,
                        Mapping,
                    )
                    else {
                        "error_type":
                            "RuntimeFailure",

                        "message":
                            "Body Store Runtime execution failed.",
                    }
                ),
            )

            if raise_on_failure:
                raise BodyStoreWorkerExecutionError(
                    failure[
                        "error"
                    ][
                        "message"
                    ]
                )

            return failure

        return _success_result(
            worker_execution_id=worker_execution_id,
            job_id=job_id,
            attempt=attempt,
            started_at=started_at,
            runtime_result=runtime_result,
        )

    except Exception as exc:
        if (
            raise_on_failure
            and isinstance(
                exc,
                (
                    BodyStoreWorkerContractError,
                    BodyStoreWorkerExecutionError,
                ),
            )
        ):
            raise

        failure = _failure_result(
            worker_execution_id=worker_execution_id,
            job_id=job_id,
            attempt=attempt,
            started_at=started_at,
            runtime_result=runtime_result,
            error=exc,
        )

        if raise_on_failure:
            raise

        return failure
