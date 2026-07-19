from __future__ import annotations

import inspect
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping


# =====================================================================
# UDARE UNIVERSAL RUNTIME CONTRACT — PHASE 2
# =====================================================================
#
# Included:
#   - Pipeline registration
#   - Stage registration
#   - Payload contract
#   - Universal job-creator adapter
#   - Persisted job-status reader
#   - Test-job cancellation adapter
#
# Excluded:
#   - Dedicated UDARE queue
#   - UDARE worker handler
#   - Batch population
#   - Reconstruction execution
#   - UDARE Store population
#   - Integrity validation
#   - Article validation
# =====================================================================


UDARE_RUNTIME_CONTRACT_VERSION = (
    "udare_runtime_contract_v1"
)

UDARE_RUNTIME_REGISTRATION_VERSION = (
    "udare_runtime_registration_v1"
)

WEBSITE_RECONSTRUCTION_PIPELINE = (
    "website_reconstruction"
)

UDARE_RECONSTRUCTION_STAGE = (
    "udare_reconstruction"
)

UDARE_ENGINE_VERSION = (
    "universal_dom_article_reconstruction_engine_v1_8"
)

UDARE_TARGET_STORE = (
    "udare_store_v1"
)

UDARE_ARTICLE_DOCUMENT_FORMAT = (
    "udare_article_reader_document_v1"
)

UDARE_SOURCE_STORE_VERSION = (
    "raw_website_html_store_v1"
)

DEFAULT_PRODUCT_ID = "linkcraftor"
DEFAULT_PRIORITY = "normal"
DEFAULT_PRIORITY_VALUE = 5
DEFAULT_MAX_ATTEMPTS = 3


REQUIRED_UDARE_PAYLOAD_FIELDS = (
    "workspace_id",
    "source_store_version",
    "source_record_id",
    "html_id",
    "source_url",
    "udare_engine",
    "target_store",
    "article_document_format",
)


UDARE_RUNTIME_STAGE_REGISTRY_V1: Dict[str, Any] = {
    "schema_version":
        UDARE_RUNTIME_REGISTRATION_VERSION,

    "pipeline":
        WEBSITE_RECONSTRUCTION_PIPELINE,

    "stage":
        UDARE_RECONSTRUCTION_STAGE,

    "stage_type":
        "reconstruction",

    "source_store_version":
        UDARE_SOURCE_STORE_VERSION,

    "engine":
        UDARE_ENGINE_VERSION,

    "target_store":
        UDARE_TARGET_STORE,

    "article_document_format":
        UDARE_ARTICLE_DOCUMENT_FORMAT,

    "runtime":
        "universal_knowledge_runtime",

    "job_creator":
        "create_universal_knowledge_job",

    "job_status_reader":
        "read_job_status",

    "job_status_updater":
        "update_job_status",

    "queue_handler_registered":
        False,

    "worker_handler_registered":
        False,

    "batch_population_enabled":
        False,

    "execution_enabled":
        False,

    "phase":
        "phase_2_runtime_integration",
}


class UdareRuntimeContractError(
    RuntimeError
):
    """UDARE runtime contract or adapter failure."""


def get_udare_runtime_registration_v1(
) -> Dict[str, Any]:
    return deepcopy(
        UDARE_RUNTIME_STAGE_REGISTRY_V1
    )


def validate_udare_runtime_payload_v1(
    payload: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(
        payload,
        Mapping,
    ):
        raise UdareRuntimeContractError(
            "UDARE runtime payload must be a mapping."
        )

    missing_fields = [
        field
        for field in REQUIRED_UDARE_PAYLOAD_FIELDS
        if not str(
            payload.get(
                field,
                "",
            )
            or ""
        ).strip()
    ]

    if missing_fields:
        raise UdareRuntimeContractError(
            "Missing UDARE runtime payload fields: "
            + ", ".join(
                missing_fields
            )
        )

    exact_values = {
        "source_store_version":
            UDARE_SOURCE_STORE_VERSION,

        "udare_engine":
            UDARE_ENGINE_VERSION,

        "target_store":
            UDARE_TARGET_STORE,

        "article_document_format":
            UDARE_ARTICLE_DOCUMENT_FORMAT,
    }

    mismatches = []

    for field, expected in (
        exact_values.items()
    ):
        actual = str(
            payload.get(
                field,
                "",
            )
            or ""
        )

        if actual != expected:
            mismatches.append(
                f"{field}={actual!r}; "
                f"expected {expected!r}"
            )

    if mismatches:
        raise UdareRuntimeContractError(
            "UDARE runtime payload mismatch: "
            + "; ".join(
                mismatches
            )
        )

    return {
        "ok":
            True,

        "schema_version":
            UDARE_RUNTIME_CONTRACT_VERSION,

        "workspace_id":
            str(
                payload[
                    "workspace_id"
                ]
            ),

        "source_record_id":
            str(
                payload[
                    "source_record_id"
                ]
            ),

        "html_id":
            str(
                payload[
                    "html_id"
                ]
            ),

        "source_url":
            str(
                payload[
                    "source_url"
                ]
            ),
    }


def build_udare_runtime_payload_v1(
    *,
    workspace_id: str,
    source_record_id: str,
    html_id: str,
    source_url: str,
    correlation_id: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = {
        "schema_version":
            UDARE_RUNTIME_CONTRACT_VERSION,

        "workspace_id":
            str(
                workspace_id
            ).strip(),

        "source_store_version":
            UDARE_SOURCE_STORE_VERSION,

        "source_record_id":
            str(
                source_record_id
            ).strip(),

        "html_id":
            str(
                html_id
            ).strip(),

        "source_url":
            str(
                source_url
            ).strip(),

        "udare_engine":
            UDARE_ENGINE_VERSION,

        "target_store":
            UDARE_TARGET_STORE,

        "article_document_format":
            UDARE_ARTICLE_DOCUMENT_FORMAT,

        "correlation_id":
            str(
                correlation_id
                or ""
            ).strip(),

        "metadata":
            dict(
                metadata
                or {}
            ),

        "execution_controls": {
            "execute_now":
                False,

            "queue_handler_required":
                True,

            "worker_handler_required":
                True,

            "store_population_allowed":
                False,

            "phase":
                "phase_2_runtime_integration",
        },
    }

    validate_udare_runtime_payload_v1(
        payload
    )

    return payload


def _normalize_result_v1(
    value: Any,
) -> Any:
    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key):
                _normalize_result_v1(
                    child
                )
            for key, child
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            _normalize_result_v1(
                child
            )
            for child in value
        ]

    if hasattr(
        value,
        "model_dump",
    ):
        return _normalize_result_v1(
            value.model_dump()
        )

    if hasattr(
        value,
        "dict",
    ):
        try:
            return _normalize_result_v1(
                value.dict()
            )
        except Exception:
            pass

    if hasattr(
        value,
        "__dict__",
    ):
        return _normalize_result_v1(
            vars(
                value
            )
        )

    return str(
        value
    )


def _invoke_by_signature_v1(
    function: Callable[..., Any],
    values: Mapping[str, Any],
) -> Any:
    signature = inspect.signature(
        function
    )

    positional_arguments = []
    keyword_arguments: Dict[str, Any] = {}

    accepts_var_keyword = any(
        parameter.kind
        == inspect.Parameter.VAR_KEYWORD
        for parameter
        in signature.parameters.values()
    )

    for name, parameter in (
        signature.parameters.items()
    ):
        if parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }:
            continue

        if name in values:
            value = values[
                name
            ]

        elif (
            parameter.default
            is not inspect.Parameter.empty
        ):
            continue

        else:
            raise UdareRuntimeContractError(
                "Unsupported required parameter in "
                f"{function.__name__}: {name}"
            )

        if (
            parameter.kind
            == inspect.Parameter.POSITIONAL_ONLY
        ):
            positional_arguments.append(
                value
            )
        else:
            keyword_arguments[
                name
            ] = value

    if accepts_var_keyword:
        for name in (
            "user_id",
            "product_id",
            "pipeline",
            "stage",
            "payload_ref",
            "priority",
            "status",
            "max_attempts",
            "enqueue",
            "run_immediately",
            "execute",
            "dispatch",
            "auto_run",
        ):
            if (
                name in values
                and name
                not in keyword_arguments
            ):
                keyword_arguments[
                    name
                ] = values[
                    name
                ]

    return function(
        *positional_arguments,
        **keyword_arguments,
    )



def _priority_value_v1(
    value: Any,
) -> int:
    """
    Convert user-facing priority names to the universal runtime's
    integer priority contract. Lower numbers represent higher priority.
    """

    if isinstance(
        value,
        bool,
    ):
        return DEFAULT_PRIORITY_VALUE

    if isinstance(
        value,
        int,
    ):
        return max(
            1,
            min(
                10,
                value,
            ),
        )

    text = str(
        value
        or ""
    ).strip().casefold()

    named_priorities = {
        "critical":
            1,

        "urgent":
            1,

        "high":
            3,

        "normal":
            5,

        "medium":
            5,

        "low":
            7,

        "background":
            9,
    }

    if text in named_priorities:
        return named_priorities[
            text
        ]

    try:
        parsed = int(
            text
        )

    except (
        TypeError,
        ValueError,
    ):
        return DEFAULT_PRIORITY_VALUE

    return max(
        1,
        min(
            10,
            parsed,
        ),
    )


def _creator_values_v1(
    *,
    payload: Mapping[str, Any],
    user_id: str,
    product_id: str,
    priority: str,
) -> Dict[str, Any]:
    source_record_id = str(
        payload[
            "source_record_id"
        ]
    )

    workspace_id = str(
        payload[
            "workspace_id"
        ]
    )

    metadata = {
        "runtime_contract_version":
            UDARE_RUNTIME_CONTRACT_VERSION,

        "runtime_registration_version":
            UDARE_RUNTIME_REGISTRATION_VERSION,

        "pipeline":
            WEBSITE_RECONSTRUCTION_PIPELINE,

        "stage":
            UDARE_RECONSTRUCTION_STAGE,

        "execution_enabled":
            False,
    }

    values: Dict[str, Any] = {
        # Canonical names
        "workspace_id":
            workspace_id,

        "user_id":
            user_id,

        "product_id":
            product_id,

        "pipeline":
            WEBSITE_RECONSTRUCTION_PIPELINE,

        "stage":
            UDARE_RECONSTRUCTION_STAGE,

        "payload":
            dict(
                payload
            ),

        "payload_ref":
            source_record_id,

        "payload_reference":
            source_record_id,

        "priority":
            _priority_value_v1(
                priority
            ),

        "status":
            "registered",

        "attempts":
            0,

        "attempt_count":
            0,

        "max_attempts":
            DEFAULT_MAX_ATTEMPTS,

        "metadata":
            metadata,

        # Execution suppression
        "enqueue":
            False,

        "run_immediately":
            False,

        "execute":
            False,

        "dispatch":
            False,

        "auto_run":
            False,

        # Common aliases
        "job_type":
            UDARE_RECONSTRUCTION_STAGE,

        "task_type":
            UDARE_RECONSTRUCTION_STAGE,

        "operation":
            UDARE_RECONSTRUCTION_STAGE,

        "operation_name":
            UDARE_RECONSTRUCTION_STAGE,

        "pipeline_name":
            WEBSITE_RECONSTRUCTION_PIPELINE,

        "stage_name":
            UDARE_RECONSTRUCTION_STAGE,

        "input_payload":
            dict(
                payload
            ),

        "job_payload":
            dict(
                payload
            ),

        "source_id":
            source_record_id,

        "source_ref":
            source_record_id,

        "source_reference":
            source_record_id,

        "source_type":
            "website_raw_html",

        "queue_name":
            "universal_knowledge",

        "queue":
            "universal_knowledge",

        "owner_id":
            user_id,

        "tenant_id":
            workspace_id,
    }

    return values


def create_udare_reconstruction_job_v1(
    *,
    payload: Mapping[str, Any],
    user_id: str = "system",
    product_id: str = DEFAULT_PRODUCT_ID,
    priority: str = DEFAULT_PRIORITY,
) -> Dict[str, Any]:
    validate_udare_runtime_payload_v1(
        payload
    )

    from backend.server.jobs import (
        universal_knowledge_orchestrator
        as orchestrator
    )

    creator = getattr(
        orchestrator,
        "create_universal_knowledge_job",
        None,
    )

    if not callable(
        creator
    ):
        raise UdareRuntimeContractError(
            "create_universal_knowledge_job "
            "was not found."
        )

    values = _creator_values_v1(
        payload=
            payload,

        user_id=
            str(
                user_id
                or "system"
            ),

        product_id=
            str(
                product_id
                or DEFAULT_PRODUCT_ID
            ),

        priority=
            str(
                priority
                or DEFAULT_PRIORITY
            ),
    )

    raw_result = _invoke_by_signature_v1(
        creator,
        values,
    )

    return {
        "ok":
            True,

        "pipeline":
            WEBSITE_RECONSTRUCTION_PIPELINE,

        "stage":
            UDARE_RECONSTRUCTION_STAGE,

        "payload":
            dict(
                payload
            ),

        "creator":
            (
                "backend.server.jobs."
                "universal_knowledge_orchestrator."
                "create_universal_knowledge_job"
            ),

        "creator_signature":
            str(
                inspect.signature(
                    creator
                )
            ),

        "execution_requested":
            False,

        "raw_result":
            _normalize_result_v1(
                raw_result
            ),
    }


def read_udare_job_status_v1(
    *,
    job_id: str,
    workspace_id: str,
) -> Dict[str, Any]:
    from backend.server.jobs import (
        universal_knowledge_orchestrator
        as orchestrator
    )

    reader = getattr(
        orchestrator,
        "read_job_status",
        None,
    )

    if not callable(
        reader
    ):
        raise UdareRuntimeContractError(
            "read_job_status was not found."
        )

    values = {
        "job_id":
            job_id,

        "id":
            job_id,

        "workspace_id":
            workspace_id,

        "tenant_id":
            workspace_id,
    }

    raw_result = _invoke_by_signature_v1(
        reader,
        values,
    )

    return {
        "ok":
            True,

        "reader_signature":
            str(
                inspect.signature(
                    reader
                )
            ),

        "raw_result":
            _normalize_result_v1(
                raw_result
            ),
    }


def cancel_udare_job_v1(
    *,
    job_id: str,
    workspace_id: str,
    reason: str,
) -> Dict[str, Any]:
    from backend.server.jobs import (
        universal_knowledge_orchestrator
        as orchestrator
    )

    updater = getattr(
        orchestrator,
        "update_job_status",
        None,
    )

    if not callable(
        updater
    ):
        raise UdareRuntimeContractError(
            "update_job_status was not found."
        )

    values = {
        "job_id":
            job_id,

        "id":
            job_id,

        "workspace_id":
            workspace_id,

        "tenant_id":
            workspace_id,

        "status":
            "cancelled",

        "new_status":
            "cancelled",

        "state":
            "cancelled",

        "error":
            reason,

        "error_info":
            reason,

        "message":
            reason,

        "progress":
            0,

        "lease_owner":
            None,
    }

    raw_result = _invoke_by_signature_v1(
        updater,
        values,
    )

    return {
        "ok":
            True,

        "updater_signature":
            str(
                inspect.signature(
                    updater
                )
            ),

        "raw_result":
            _normalize_result_v1(
                raw_result
            ),
    }


def explain_udare_runtime_contract_v1(
) -> Dict[str, Any]:
    return {
        "registration":
            get_udare_runtime_registration_v1(),

        "payload_fields":
            list(
                REQUIRED_UDARE_PAYLOAD_FIELDS
            ),

        "dedicated_queue_created":
            False,

        "worker_handler_created":
            False,

        "batch_population_enabled":
            False,

        "reconstruction_execution_enabled":
            False,

        "store_population_enabled":
            False,
    }
