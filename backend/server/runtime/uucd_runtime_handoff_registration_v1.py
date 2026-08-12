"""
Runtime Registration for canonical UUCD -> Lifecycle Eligibility handoff.
"""

from __future__ import annotations

from typing import Any

from backend.server.runtime.lifecycle_eligibility_runtime_handler_v1 import (
    REQUIRED_PAYLOAD_FIELDS,
    handle_lifecycle_eligibility_runtime_v1,
)
from backend.server.runtime.universal_runtime_registration import (
    register_runtime_handler,
)


UUCD_RUNTIME_HANDOFF_REGISTRATION_VERSION = (
    "uucd_runtime_handoff_registration_v1"
)

UUCD_RUNTIME_HANDOFF_JOB_TYPE = (
    "uucd_runtime_handoff"
)

UUCD_RUNTIME_HANDOFF_PIPELINE = (
    "universal_knowledge"
)

UUCD_RUNTIME_HANDOFF_STAGE = (
    "lifecycle_eligibility"
)


def register_uucd_runtime_handoff_v1(
    *,
    persist: bool = True,
    replace: bool = False,
) -> dict[str, Any]:
    """
    Register the canonical UUCD runtime handoff with Lifecycle Eligibility.

    No worker execution or job creation occurs here.
    """

    return register_runtime_handler(
        job_type=
            UUCD_RUNTIME_HANDOFF_JOB_TYPE,

        handler=
            handle_lifecycle_eligibility_runtime_v1,

        pipeline=
            UUCD_RUNTIME_HANDOFF_PIPELINE,

        stage=
            UUCD_RUNTIME_HANDOFF_STAGE,

        description=(
            "Validate persisted canonical UUCD and Body Store "
            "evidence before Semantic Intelligence Runtime Reader."
        ),

        required_payload_fields=
            REQUIRED_PAYLOAD_FIELDS,

        predecessor_stages=(
            "runtime_queue_handoff",
        ),

        successor_stages=(
            "semantic_intelligence_runtime_reader",
        ),

        idempotency_fields=(
            "document_id",
            "content_hash",
            "persistence_fingerprint",
        ),

        retry_policy={
            "maximum_attempts":
                3,

            "retry_on_handler_error":
                True,

            "retry_on_contract_error":
                False,
        },

        concurrency_policy={
            "scope":
                "document",

            "allow_parallel_documents":
                True,

            "allow_parallel_same_document":
                False,
        },

        metadata={
            "registration_version":
                UUCD_RUNTIME_HANDOFF_REGISTRATION_VERSION,

            "canonical_uucd_schema":
                "universal_unified_content_document_v2",

            "body_transport":
                "reference_only",

            "content_body_allowed":
                False,

            "semantic_processing_performed":
                False,

            "next_stage":
                "semantic_intelligence_runtime_reader",
        },

        replace=
            replace,

        persist=
            persist,
    )


def explain_uucd_runtime_handoff_registration_v1() -> dict[str, Any]:

    return {
        "component":
            "UUCD Runtime Handoff Registration",

        "version":
            UUCD_RUNTIME_HANDOFF_REGISTRATION_VERSION,

        "job_type":
            UUCD_RUNTIME_HANDOFF_JOB_TYPE,

        "pipeline":
            UUCD_RUNTIME_HANDOFF_PIPELINE,

        "stage":
            UUCD_RUNTIME_HANDOFF_STAGE,

        "handler":
            (
                "handle_lifecycle_eligibility_runtime_v1"
            ),

        "required_payload_fields":
            list(
                REQUIRED_PAYLOAD_FIELDS
            ),

        "predecessor_stage":
            "runtime_queue_handoff",

        "successor_stage":
            "semantic_intelligence_runtime_reader",

        "registration_has_side_effect_on_import":
            False,

        "worker_execution":
            False,

        "semantic_processing_performed":
            False,
    }


__all__ = [
    "UUCD_RUNTIME_HANDOFF_REGISTRATION_VERSION",
    "UUCD_RUNTIME_HANDOFF_JOB_TYPE",
    "UUCD_RUNTIME_HANDOFF_PIPELINE",
    "UUCD_RUNTIME_HANDOFF_STAGE",
    "register_uucd_runtime_handoff_v1",
    "explain_uucd_runtime_handoff_registration_v1",
]
