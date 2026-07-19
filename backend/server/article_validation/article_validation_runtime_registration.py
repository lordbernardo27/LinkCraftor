"""Universal runtime registration for Article Validation v3."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from backend.server.article_validation.article_validation_engine_v3 import (
    ARTICLE_VALIDATION_ENGINE_VERSION,
)
from backend.server.article_validation.article_validation_runner_v3 import (
    RUNNER_VERSION,
    run_article_validation_population_v3,
)
from backend.server.article_validation.certified_article_validation_input import (
    load_certified_article_validation_input,
)
from backend.server.runtime.universal_runtime_registration import (
    ensure_persisted_runtime_registrations_loaded,
    register_runtime_handler,
)


REGISTRATION_VERSION = (
    "article_validation_runtime_registration_v1"
)

PIPELINE = "website_source_pipeline"
STAGE = "article_validation"

JOB_TYPE_ARTICLE_VALIDATION = (
    "article_validation_population_v3"
)

PREDECESSOR_STAGES = (
    "website_article_integrity_certification",
)

SUCCESSOR_STAGES = (
    "website_unified_content",
)

HANDLER_REFERENCE = (
    "backend.server.article_validation."
    "article_validation_runtime_registration:"
    "execute_article_validation_runtime_job_v1"
)

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

REGISTRATION_EVIDENCE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "universal_runtime_registration"
    / "article_validation"
    / "article_validation_registration.json"
)


class ArticleValidationRuntimeRegistrationError(
    RuntimeError
):
    """Raised when Article Validation runtime registration is invalid."""


def _safe_name(
    value: Any,
    *,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise ArticleValidationRuntimeRegistrationError(
            f"{field_name} is required."
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.:-]+",
        normalized,
    ):
        raise ArticleValidationRuntimeRegistrationError(
            f"{field_name} contains unsupported characters."
        )

    return normalized


def _positive_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    try:
        normalized = int(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ArticleValidationRuntimeRegistrationError(
            f"{field_name} must be an integer."
        ) from exc

    if normalized <= 0:
        raise ArticleValidationRuntimeRegistrationError(
            f"{field_name} must be greater than zero."
        )

    return normalized


def _job_payload(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    nested_payload = job.get(
        "payload"
    )

    if isinstance(
        nested_payload,
        Mapping,
    ):
        payload.update(
            nested_payload
        )

    for field_name in (
        "workspace_id",
        "expected_active_count",
        "run_id",
        "batch_size",
        "payload_ref",
    ):
        if (
            field_name not in payload
            and field_name in job
        ):
            payload[
                field_name
            ] = job[
                field_name
            ]

    return payload


def _certified_active_count(
    workspace_id: str,
) -> int:
    certified_input = (
        load_certified_article_validation_input(
            workspace_id
        )
    )

    records = certified_input.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise ArticleValidationRuntimeRegistrationError(
            "Certified Article Validation input records are invalid."
        )

    if not records:
        raise ArticleValidationRuntimeRegistrationError(
            "Certified Article Validation input is empty."
        )

    return len(
        records
    )


def execute_article_validation_runtime_job_v1(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute all certified Article Validation inputs through runtime."""

    if not isinstance(
        job,
        Mapping,
    ):
        raise ArticleValidationRuntimeRegistrationError(
            "Article Validation runtime job must be a mapping."
        )

    payload = _job_payload(
        job
    )

    workspace_id = _safe_name(
        payload.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    certified_active_count = (
        _certified_active_count(
            workspace_id
        )
    )

    supplied_expected_count = payload.get(
        "expected_active_count"
    )

    if supplied_expected_count is None:
        expected_active_count = (
            certified_active_count
        )

    else:
        expected_active_count = (
            _positive_integer(
                supplied_expected_count,
                field_name=(
                    "expected_active_count"
                ),
            )
        )

        if (
            expected_active_count
            != certified_active_count
        ):
            raise ArticleValidationRuntimeRegistrationError(
                "Expected active count does not match "
                "the certified Integrity input count: "
                f"{expected_active_count} != "
                f"{certified_active_count}"
            )

    batch_size = _positive_integer(
        payload.get(
            "batch_size"
        )
        or 100,
        field_name="batch_size",
    )

    run_id = str(
        payload.get(
            "run_id"
        )
        or ""
    ).strip()

    result = (
        run_article_validation_population_v3(
            workspace_id=workspace_id,
            expected_active_count=(
                expected_active_count
            ),
            run_id=run_id,
            batch_size=batch_size,
        )
    )

    return {
        "runtime_job_type":
            JOB_TYPE_ARTICLE_VALIDATION,

        "pipeline":
            PIPELINE,

        "stage":
            STAGE,

        "workspace_id":
            workspace_id,

        "expected_active_count":
            expected_active_count,

        "processed_count":
            result.get(
                "processed_count"
            ),

        "pass_count":
            result.get(
                "pass_count"
            ),

        "fail_count":
            result.get(
                "fail_count"
            ),

        "run_id":
            result.get(
                "run_id"
            ),

        "certificate_id":
            result.get(
                "certificate_id"
            ),

        "artifact_paths":
            result.get(
                "artifact_paths"
            ),

        "article_bodies_stored":
            False,

        "article_bodies_modified":
            False,

        "article_bodies_copied":
            False,

        "intermediate_article_store_created":
            False,
    }


def _write_json(
    path: Path,
    payload: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            dict(
                payload
            ),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def registration_definition_v1() -> dict[str, Any]:
    return {
        "registration_version":
            REGISTRATION_VERSION,

        "job_type":
            JOB_TYPE_ARTICLE_VALIDATION,

        "handler_reference":
            HANDLER_REFERENCE,

        "pipeline":
            PIPELINE,

        "stage":
            STAGE,

        "description":
            (
                "Validate all Website Article Integrity-certified "
                "active UDARE articles and produce evidence-only "
                "Article Validation manifests, reports, ledgers "
                "and certification."
            ),

        "required_payload_fields":
            (
                "workspace_id",
            ),

        "predecessor_stages":
            PREDECESSOR_STAGES,

        "successor_stages":
            SUCCESSOR_STAGES,

        "idempotency_fields":
            (
                "workspace_id",
                "job_type",
                "payload_ref",
            ),

        "retry_policy": {
            "max_attempts":
                2,

            "backoff":
                "exponential",
        },

        "concurrency_policy": {
            "scope":
                "workspace",

            "max_concurrent":
                1,
        },

        "metadata": {
            "business_domain":
                "article_validation",

            "engine_version":
                ARTICLE_VALIDATION_ENGINE_VERSION,

            "runner_version":
                RUNNER_VERSION,

            "uses_universal_runtime":
                True,

            "separate_queue_required":
                False,

            "separate_worker_required":
                False,

            "evidence_only":
                True,

            "article_body_store_created":
                False,

            "article_bodies_copied":
                False,

            "word_count_rule":
                False,

            "single_paragraph_allowed":
                True,

            "duplicate_ratio_affects_pass_fail":
                False,
        },
    }


def register_article_validation_runtime_v1(
    *,
    replace: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    ensure_persisted_runtime_registrations_loaded()

    definition = registration_definition_v1()

    register_runtime_handler(
        job_type=definition[
            "job_type"
        ],
        handler=(
            execute_article_validation_runtime_job_v1
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
            **definition[
                "metadata"
            ],

            "registration_version":
                REGISTRATION_VERSION,
        },
        replace=replace,
        persist=persist,
    )

    evidence = {
        **definition,

        "registered":
            True,

        "persisted":
            bool(
                persist
            ),

        "jobs_enqueued":
            False,

        "workers_started":
            False,

        "article_validation_executed":
            False,

        "intermediate_article_store_exists":
            False,
    }

    _write_json(
        REGISTRATION_EVIDENCE_PATH,
        evidence,
    )

    return evidence
