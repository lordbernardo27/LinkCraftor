"""Runtime Registration for the Universal Article Body Store.

Execution chain:

Registered runtime job
    -> Body Store registration handler
    -> Body Store Worker
    -> Body Store Runtime
    -> Body Store Repository
    -> Writer / Management Layer

This module does not execute the Runtime directly and does not access the
Repository, Writer, Manager, Queue storage, or article-body storage directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from backend.server.runtime.universal_runtime_registration import (
    ensure_persisted_runtime_registrations_loaded,
    register_runtime_handler,
)

from backend.server.universal_article_body_store.body_store_worker_v1 import (
    BODY_STORE_WORKER_JOB_SCHEMA_VERSION,
    execute_body_store_worker_v1,
)


BODY_STORE_RUNTIME_REGISTRATION_VERSION = (
    "universal_article_body_store_runtime_registration_v1"
)

BODY_STORE_RUNTIME_PIPELINE = (
    "universal_article_body_store"
)

BODY_STORE_REGISTERED_JOB_TYPES = (
    "body_store.store",
    "body_store.read",
    "body_store.verify",
    "body_store.metadata",
    "body_store.list",
)

_PROJECT_ROOT = Path(
    __file__
).resolve().parents[
    3
]


class BodyStoreRuntimeRegistrationError(
    ValueError
):
    """Raised when a registered Body Store runtime job is malformed."""


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreRuntimeRegistrationError(
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
        raise BodyStoreRuntimeRegistrationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreRuntimeRegistrationError(
            field_name
            + " must not be empty."
        )

    return normalized


def _job_to_mapping(
    job: Any,
) -> Mapping[str, Any]:
    if isinstance(
        job,
        Mapping,
    ):
        return job

    to_dict = getattr(
        job,
        "to_dict",
        None,
    )

    if callable(
        to_dict
    ):
        value = to_dict()

        return _require_mapping(
            value,
            field_name="job.to_dict()",
        )

    fields = {}

    for name in (
        "job_id",
        "job_type",
        "workspace_id",
        "payload",
        "attempt",
        "priority",
        "payload_ref",
    ):
        if hasattr(
            job,
            name,
        ):
            fields[
                name
            ] = getattr(
                job,
                name
            )

    if fields:
        return fields

    raise BodyStoreRuntimeRegistrationError(
        "job must be a mapping or expose a supported job contract."
    )


def _extract_payload(
    job_mapping: Mapping[str, Any],
) -> Mapping[str, Any]:
    payload = job_mapping.get(
        "payload",
        {},
    )

    return _require_mapping(
        payload,
        field_name="job.payload",
    )


def _runtime_operation_from_job_type(
    job_type: str,
) -> str:
    mapping = {
        "body_store.store":
            "store",

        "body_store.read":
            "read",

        "body_store.verify":
            "verify",

        "body_store.metadata":
            "metadata",

        "body_store.list":
            "list",
    }

    try:
        return mapping[
            job_type
        ]

    except KeyError as exc:
        raise BodyStoreRuntimeRegistrationError(
            "Unsupported registered Body Store job type: "
            + job_type
        ) from exc


def _build_runtime_request(
    *,
    job_type: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    supplied_runtime_request = payload.get(
        "runtime_request"
    )

    if supplied_runtime_request is not None:
        runtime_request = dict(
            _require_mapping(
                supplied_runtime_request,
                field_name="job.payload.runtime_request",
            )
        )

        expected_operation = (
            _runtime_operation_from_job_type(
                job_type
            )
        )

        supplied_operation = _require_string(
            runtime_request.get(
                "operation"
            ),
            field_name="runtime_request.operation",
        ).casefold()

        if (
            supplied_operation
            != expected_operation
        ):
            raise BodyStoreRuntimeRegistrationError(
                "Runtime operation does not match the registered job type."
            )

        return runtime_request

    operation = _runtime_operation_from_job_type(
        job_type
    )

    runtime_payload = dict(
        payload
    )

    runtime_payload.pop(
        "runtime_request",
        None,
    )

    return {
        "operation":
            operation,

        "payload":
            runtime_payload,
    }


def execute_body_store_registered_job_v1(
    job: Any,
) -> dict[str, Any]:
    """Adapt one registered runtime job into a Body Store Worker job."""

    job_mapping = _job_to_mapping(
        job
    )

    job_type = _require_string(
        job_mapping.get(
            "job_type"
        ),
        field_name="job.job_type",
    )

    if (
        job_type
        not in BODY_STORE_REGISTERED_JOB_TYPES
    ):
        raise BodyStoreRuntimeRegistrationError(
            "Unsupported Body Store registered job type: "
            + job_type
        )

    payload = _extract_payload(
        job_mapping
    )

    job_id = _require_string(
        job_mapping.get(
            "job_id"
        ),
        field_name="job.job_id",
    )

    attempt = job_mapping.get(
        "attempt",
        1,
    )

    if (
        not isinstance(
            attempt,
            int,
        )
        or isinstance(
            attempt,
            bool,
        )
        or attempt < 1
    ):
        raise BodyStoreRuntimeRegistrationError(
            "job.attempt must be a positive integer."
        )

    runtime_request = _build_runtime_request(
        job_type=job_type,
        payload=payload,
    )

    worker_job = {
        "job_schema_version":
            BODY_STORE_WORKER_JOB_SCHEMA_VERSION,

        "job_id":
            job_id,

        "attempt":
            attempt,

        "runtime_request":
            runtime_request,
    }

    return execute_body_store_worker_v1(
        worker_job,
        project_root=_PROJECT_ROOT,
    )


def body_store_runtime_registration_definitions_v1(
) -> tuple[dict[str, Any], ...]:
    """Return the five canonical Body Store registration definitions."""

    common = {
        "pipeline":
            BODY_STORE_RUNTIME_PIPELINE,

        "description":
            "Execute a Universal Article Body Store operation.",

        "predecessor_stages":
            (),

        "successor_stages":
            (),

        "idempotency_fields":
            (
                "workspace_id",
                "job_type",
                "payload_ref",
            ),

        "retry_policy": {
            "max_attempts":
                3,

            "backoff":
                "exponential",
        },

        "concurrency_policy": {
            "scope":
                "workspace",

            "max_concurrent":
                1,
        },
    }

    return (
        {
            **common,

            "job_type":
                "body_store.store",

            "stage":
                "body_store_write",

            "required_payload_fields":
                (
                    "envelope",
                ),

            "description":
                "Store one verified Universal Article Body payload.",
        },

        {
            **common,

            "job_type":
                "body_store.read",

            "stage":
                "body_store_read",

            "required_payload_fields":
                (
                    "workspace_id",
                    "body_ref",
                ),

            "description":
                "Read one Universal Article Body through the certified layers.",
        },

        {
            **common,

            "job_type":
                "body_store.verify",

            "stage":
                "body_store_verify",

            "required_payload_fields":
                (
                    "workspace_id",
                    "body_ref",
                ),

            "description":
                "Verify one stored Universal Article Body.",
        },

        {
            **common,

            "job_type":
                "body_store.metadata",

            "stage":
                "body_store_metadata",

            "required_payload_fields":
                (
                    "workspace_id",
                    "body_ref",
                ),

            "description":
                "Read metadata for one stored Universal Article Body.",
        },

        {
            **common,

            "job_type":
                "body_store.list",

            "stage":
                "body_store_list",

            "required_payload_fields":
                (
                    "workspace_id",
                ),

            "description":
                "List Universal Article Bodies for one workspace.",
        },
    )


def register_body_store_runtime_v1(
    *,
    replace: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    """Register all five Body Store job types canonically."""

    ensure_persisted_runtime_registrations_loaded()

    registrations = []

    definitions = (
        body_store_runtime_registration_definitions_v1()
    )

    for definition in definitions:
        registration = register_runtime_handler(
            job_type=definition[
                "job_type"
            ],
            handler=(
                execute_body_store_registered_job_v1
            ),
            pipeline=definition[
                "pipeline"
            ],
            stage=definition[
                "stage"
            ],
            description=definition[
                "description"
            ],
            required_payload_fields=definition[
                "required_payload_fields"
            ],
            predecessor_stages=definition[
                "predecessor_stages"
            ],
            successor_stages=definition[
                "successor_stages"
            ],
            idempotency_fields=definition[
                "idempotency_fields"
            ],
            retry_policy=definition[
                "retry_policy"
            ],
            concurrency_policy=definition[
                "concurrency_policy"
            ],
            metadata={
                "registration_version":
                    BODY_STORE_RUNTIME_REGISTRATION_VERSION,

                "business_domain":
                    "universal_article_body_store",

                "uses_body_store_worker":
                    True,

                "uses_body_store_runtime":
                    True,

                "uses_body_store_repository":
                    True,

                "separate_queue_required":
                    True,

                "article_body_in_registration":
                    False,
            },
            replace=replace,
            persist=persist,
        )

        registrations.append(
            registration
        )

    return {
        "registration_version":
            BODY_STORE_RUNTIME_REGISTRATION_VERSION,

        "pipeline":
            BODY_STORE_RUNTIME_PIPELINE,

        "registered_job_types":
            [
                registration[
                    "job_type"
                ]
                for registration in registrations
            ],

        "registration_count":
            len(
                registrations
            ),

        "persisted":
            persist,

        "registrations":
            registrations,
    }
