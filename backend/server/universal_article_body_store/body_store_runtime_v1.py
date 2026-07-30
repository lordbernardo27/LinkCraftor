"""Canonical synchronous Universal Article Body Store Runtime.

Placement:

Caller
    -> Body Store Runtime
    -> Body Store Repository
    -> Writer / Management Layer
    -> Persistent Body Store

This Runtime does not create jobs, queues, workers, Runtime Registration,
background execution, lifecycle actions, semantic processing, or direct
filesystem access.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from backend.server.universal_article_body_store.body_store_repository_v1 import (
    body_exists as repository_body_exists,
    get_metadata as repository_get_metadata,
    list_workspace_bodies as repository_list_workspace_bodies,
    read_body as repository_read_body,
    store_body as repository_store_body,
    verify_body as repository_verify_body,
)


BODY_STORE_RUNTIME_VERSION = (
    "universal_article_body_store_runtime_v1"
)

BODY_STORE_RUNTIME_OPERATIONS = frozenset(
    {
        "store",
        "read",
        "verify",
        "metadata",
        "list",
    }
)


class BodyStoreRuntimeContractError(
    ValueError
):
    """Raised when a Body Store Runtime request is invalid."""


def _now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _new_execution_id() -> str:
    return (
        "body_store_runtime_"
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
        raise BodyStoreRuntimeContractError(
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
        raise BodyStoreRuntimeContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreRuntimeContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _optional_non_negative_integer(
    value: Any,
    *,
    field_name: str,
) -> int | None:
    if value is None:
        return None

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 0
    ):
        raise BodyStoreRuntimeContractError(
            field_name
            + " must be a non-negative integer or None."
        )

    return value


def _normalize_operation(
    operation: Any,
) -> str:
    normalized = _require_string(
        operation,
        field_name="operation",
    ).casefold()

    if normalized not in BODY_STORE_RUNTIME_OPERATIONS:
        raise BodyStoreRuntimeContractError(
            "Unsupported Body Store Runtime operation: "
            + normalized
        )

    return normalized


def _success_result(
    *,
    execution_id: str,
    operation: str,
    workspace_id: str | None,
    started_at: str,
    result: Any,
) -> dict[str, Any]:
    return {
        "runtime_schema_version":
            "body_store_runtime_result_v1",

        "runtime_version":
            BODY_STORE_RUNTIME_VERSION,

        "execution_id":
            execution_id,

        "operation":
            operation,

        "workspace_id":
            workspace_id,

        "runtime_status":
            "COMPLETED",

        "success":
            True,

        "started_at":
            started_at,

        "completed_at":
            _now_iso(),

        "result":
            result,

        "error":
            None,

        "execution_mode":
            "SYNCHRONOUS",

        "queue_used":
            False,

        "worker_used":
            False,

        "runtime_registration_used":
            False,
    }


def _failure_result(
    *,
    execution_id: str,
    operation: str,
    workspace_id: str | None,
    started_at: str,
    error: Exception,
) -> dict[str, Any]:
    return {
        "runtime_schema_version":
            "body_store_runtime_result_v1",

        "runtime_version":
            BODY_STORE_RUNTIME_VERSION,

        "execution_id":
            execution_id,

        "operation":
            operation,

        "workspace_id":
            workspace_id,

        "runtime_status":
            "FAILED",

        "success":
            False,

        "started_at":
            started_at,

        "completed_at":
            _now_iso(),

        "result":
            None,

        "error": {
            "error_type":
                type(
                    error
                ).__name__,

            "message":
                str(
                    error
                ),
        },

        "execution_mode":
            "SYNCHRONOUS",

        "queue_used":
            False,

        "worker_used":
            False,

        "runtime_registration_used":
            False,
    }


def _execute_repository_operation(
    *,
    operation: str,
    payload: Mapping[str, Any],
    project_root: str | Path,
) -> tuple[Any, str | None]:
    if operation == "store":
        envelope = _require_mapping(
            payload.get(
                "envelope"
            ),
            field_name="payload.envelope",
        )

        overwrite = payload.get(
            "overwrite",
            False,
        )

        if not isinstance(
            overwrite,
            bool,
        ):
            raise BodyStoreRuntimeContractError(
                "payload.overwrite must be a boolean."
            )

        workspace_id = None

        uucd_record = envelope.get(
            "uucd_record"
        )

        if isinstance(
            uucd_record,
            Mapping,
        ):
            value = uucd_record.get(
                "workspace_id"
            )

            if isinstance(
                value,
                str,
            ):
                workspace_id = value

        result = repository_store_body(
            envelope,
            project_root=project_root,
            overwrite=overwrite,
        )

        return (
            result,
            workspace_id,
        )

    workspace_id = _require_string(
        payload.get(
            "workspace_id"
        ),
        field_name="payload.workspace_id",
    )

    if operation == "list":
        verify_each = payload.get(
            "verify_each",
            False,
        )

        if not isinstance(
            verify_each,
            bool,
        ):
            raise BodyStoreRuntimeContractError(
                "payload.verify_each must be a boolean."
            )

        result = repository_list_workspace_bodies(
            project_root=project_root,
            workspace_id=workspace_id,
            verify_each=verify_each,
        )

        return (
            result,
            workspace_id,
        )

    body_ref = _require_string(
        payload.get(
            "body_ref"
        ),
        field_name="payload.body_ref",
    )

    if operation == "read":
        result = repository_read_body(
            project_root=project_root,
            workspace_id=workspace_id,
            body_ref=body_ref,
        )

        return (
            result,
            workspace_id,
        )

    if operation == "metadata":
        result = repository_get_metadata(
            project_root=project_root,
            workspace_id=workspace_id,
            body_ref=body_ref,
        )

        return (
            result,
            workspace_id,
        )

    if operation == "verify":
        expected_content_hash = payload.get(
            "expected_content_hash"
        )

        if expected_content_hash is not None:
            expected_content_hash = _require_string(
                expected_content_hash,
                field_name="payload.expected_content_hash",
            )

        expected_body_length = (
            _optional_non_negative_integer(
                payload.get(
                    "expected_body_length"
                ),
                field_name="payload.expected_body_length",
            )
        )

        expected_body_byte_length = (
            _optional_non_negative_integer(
                payload.get(
                    "expected_body_byte_length"
                ),
                field_name="payload.expected_body_byte_length",
            )
        )

        expected_body_word_count = (
            _optional_non_negative_integer(
                payload.get(
                    "expected_body_word_count"
                ),
                field_name="payload.expected_body_word_count",
            )
        )

        result = repository_verify_body(
            project_root=project_root,
            workspace_id=workspace_id,
            body_ref=body_ref,
            expected_content_hash=expected_content_hash,
            expected_body_length=expected_body_length,
            expected_body_byte_length=expected_body_byte_length,
            expected_body_word_count=expected_body_word_count,
        )

        return (
            result,
            workspace_id,
        )

    raise BodyStoreRuntimeContractError(
        "Unsupported operation reached dispatcher: "
        + operation
    )


def execute_body_store_runtime_v1(
    request: Mapping[str, Any],
    *,
    project_root: str | Path,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Execute one synchronous Body Store operation.

    A normalized success or failure result is always returned unless
    raise_on_failure is True.
    """

    execution_id = _new_execution_id()
    started_at = _now_iso()

    operation = "UNKNOWN"
    workspace_id: str | None = None

    try:
        request_mapping = _require_mapping(
            request,
            field_name="request",
        )

        operation = _normalize_operation(
            request_mapping.get(
                "operation"
            )
        )

        payload = _require_mapping(
            request_mapping.get(
                "payload",
                {},
            ),
            field_name="request.payload",
        )

        (
            result,
            workspace_id,
        ) = _execute_repository_operation(
            operation=operation,
            payload=payload,
            project_root=project_root,
        )

        return _success_result(
            execution_id=execution_id,
            operation=operation,
            workspace_id=workspace_id,
            started_at=started_at,
            result=result,
        )

    except Exception as exc:
        failure = _failure_result(
            execution_id=execution_id,
            operation=operation,
            workspace_id=workspace_id,
            started_at=started_at,
            error=exc,
        )

        if raise_on_failure:
            raise

        return failure
