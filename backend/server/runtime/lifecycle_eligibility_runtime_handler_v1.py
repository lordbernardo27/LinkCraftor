"""
Canonical Lifecycle Eligibility Runtime Handler v1.

Canonical position:

    Persisted canonical UUCD
        ->
    uucd_runtime_handoff Universal Job
        ->
    Universal Runtime Worker
        ->
    Runtime Registration Dispatcher
        ->
    Lifecycle Eligibility
        ->
    Semantic Intelligence Runtime Reader

Responsibility:

Determine whether one persisted canonical UUCD is eligible to proceed
from runtime handoff into the Semantic Intelligence Runtime Reader.

This handler verifies references and canonical persistence evidence.
It does NOT perform semantic analysis and does NOT copy body content
into the runtime job.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from backend.server.stores.source_lifecycle_control import (
    evaluate_source_semantic_readiness,
)


LIFECYCLE_ELIGIBILITY_HANDLER_VERSION = (
    "lifecycle_eligibility_runtime_handler_v1"
)

LIFECYCLE_ELIGIBILITY_RESULT_SCHEMA_VERSION = (
    "lifecycle_eligibility_result_v1"
)

LIFECYCLE_ELIGIBILITY_CERTIFICATE_SCHEMA_VERSION = (
    "lifecycle_eligibility_certificate_v1"
)

EXPECTED_JOB_TYPE = (
    "uucd_runtime_handoff"
)

NEXT_STAGE = (
    "semantic_intelligence_runtime_reader"
)

SHA256_PATTERN = re.compile(
    r"^[a-f0-9]{64}$"
)

DOCUMENT_ID_PATTERN = re.compile(
    r"^uucd_[a-f0-9]{32}$"
)

REQUIRED_PAYLOAD_FIELDS = (
    "document_id",
    "content_ref",
    "body_ref",
    "source_type",
    "content_hash",
    "persistence_fingerprint",
)


class LifecycleEligibilityError(
    RuntimeError
):
    """Base error for canonical Lifecycle Eligibility."""


class LifecycleEligibilityContractError(
    LifecycleEligibilityError
):
    """Raised when runtime input violates the eligibility contract."""


class LifecycleEligibilityReferenceError(
    LifecycleEligibilityError
):
    """Raised when canonical persisted references cannot be verified."""


def _project_root() -> Path:
    return Path(
        __file__
    ).resolve().parents[3]


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise LifecycleEligibilityContractError(
            f"{field_name} must be a mapping."
        )

    return value


def _require_text(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise LifecycleEligibilityContractError(
            f"{field_name} must be a string."
        )

    cleaned = value.strip()

    if not cleaned:
        raise LifecycleEligibilityContractError(
            f"{field_name} must not be empty."
        )

    return cleaned


def _require_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:

    digest = _require_text(
        value,
        field_name=field_name,
    ).casefold()

    if not SHA256_PATTERN.fullmatch(
        digest
    ):
        raise LifecycleEligibilityContractError(
            f"{field_name} must be a SHA-256 digest."
        )

    return digest


def _resolve_project_reference(
    reference: str,
) -> Path:

    root = _project_root().resolve()

    candidate = Path(
        reference
    )

    if not candidate.is_absolute():
        candidate = (
            root
            / candidate
        )

    resolved = candidate.resolve()

    try:
        resolved.relative_to(
            root
        )
    except ValueError as exc:
        raise LifecycleEligibilityReferenceError(
            "Canonical reference escapes the LinkCraftor project root."
        ) from exc

    return resolved


def _read_persisted_uucd(
    *,
    content_ref: str,
) -> Mapping[str, Any]:

    path = _resolve_project_reference(
        content_ref
    )

    if not path.exists():
        raise LifecycleEligibilityReferenceError(
            f"Persisted UUCD reference does not exist: {content_ref}"
        )

    if not path.is_file():
        raise LifecycleEligibilityReferenceError(
            "Persisted UUCD reference is not a file."
        )

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        raise LifecycleEligibilityReferenceError(
            "Persisted UUCD JSON could not be read."
        ) from exc

    if not isinstance(
        payload,
        Mapping,
    ):
        raise LifecycleEligibilityReferenceError(
            "Persisted UUCD JSON must contain a mapping."
        )

    return payload


def _verify_body_reference(
    *,
    body_ref: str,
    expected_content_hash: str,
) -> dict[str, Any]:

    path = _resolve_project_reference(
        body_ref
    )

    if not path.exists():
        raise LifecycleEligibilityReferenceError(
            f"Body reference does not exist: {body_ref}"
        )

    if not path.is_file():
        raise LifecycleEligibilityReferenceError(
            "Body reference is not a file."
        )

    body_bytes = path.read_bytes()

    if not body_bytes:
        raise LifecycleEligibilityReferenceError(
            "Referenced body is empty."
        )

    calculated_hash = hashlib.sha256(
        body_bytes
    ).hexdigest()

    if (
        calculated_hash
        != expected_content_hash
    ):
        raise LifecycleEligibilityReferenceError(
            "Referenced body SHA-256 does not match content_hash."
        )

    return {
        "body_exists":
            True,

        "body_non_empty":
            True,

        "body_sha256_verified":
            True,

        "body_byte_count":
            len(
                body_bytes
            ),
    }


def evaluate_lifecycle_eligibility_v1(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Evaluate one claimed uucd_runtime_handoff job.

    Successful return means the article is eligible to proceed to the
    Semantic Intelligence Runtime Reader.
    """

    runtime_job = _require_mapping(
        job,
        field_name="job",
    )

    job_id = _require_text(
        runtime_job.get(
            "job_id"
        ),
        field_name="job.job_id",
    )

    workspace_id = _require_text(
        runtime_job.get(
            "workspace_id"
        ),
        field_name="job.workspace_id",
    )

    job_type = _require_text(
        runtime_job.get(
            "job_type"
        ),
        field_name="job.job_type",
    )

    if job_type != EXPECTED_JOB_TYPE:
        raise LifecycleEligibilityContractError(
            "Lifecycle Eligibility received the wrong job_type."
        )

    payload = _require_mapping(
        runtime_job.get(
            "payload"
        ),
        field_name="job.payload",
    )

    if "content_body" in payload:
        raise LifecycleEligibilityContractError(
            "Runtime payload must never contain content_body."
        )

    missing_fields = [
        field_name
        for field_name in REQUIRED_PAYLOAD_FIELDS
        if field_name not in payload
    ]

    if missing_fields:
        raise LifecycleEligibilityContractError(
            "Lifecycle Eligibility payload is missing required fields: "
            + ", ".join(
                missing_fields
            )
        )

    document_id = _require_text(
        payload.get(
            "document_id"
        ),
        field_name="payload.document_id",
    )

    if not DOCUMENT_ID_PATTERN.fullmatch(
        document_id
    ):
        raise LifecycleEligibilityContractError(
            "payload.document_id is not a canonical UUCD identifier."
        )

    content_ref = _require_text(
        payload.get(
            "content_ref"
        ),
        field_name="payload.content_ref",
    )

    body_ref = _require_text(
        payload.get(
            "body_ref"
        ),
        field_name="payload.body_ref",
    )

    source_type = _require_text(
        payload.get(
            "source_type"
        ),
        field_name="payload.source_type",
    )

    content_hash = _require_sha256(
        payload.get(
            "content_hash"
        ),
        field_name="payload.content_hash",
    )

    persistence_fingerprint = _require_sha256(
        payload.get(
            "persistence_fingerprint"
        ),
        field_name="payload.persistence_fingerprint",
    )

    persisted_uucd = _read_persisted_uucd(
        content_ref=content_ref
    )

    if "content_body" in persisted_uucd:
        raise LifecycleEligibilityContractError(
            "Persisted canonical UUCD must not contain content_body."
        )

    if (
        persisted_uucd.get(
            "schema_version"
        )
        != "universal_unified_content_document_v2"
    ):
        raise LifecycleEligibilityContractError(
            "Persisted UUCD must use universal_unified_content_document_v2."
        )

    comparisons = {
        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "source_type":
            source_type,

        "content_ref":
            content_ref,

        "body_ref":
            body_ref,

        "content_hash":
            content_hash,
    }

    for field_name, expected in comparisons.items():

        if (
            persisted_uucd.get(
                field_name
            )
            != expected
        ):
            raise LifecycleEligibilityContractError(
                f"Persisted UUCD {field_name} does not match "
                "the canonical runtime payload."
            )

    metadata = _require_mapping(
        persisted_uucd.get(
            "metadata"
        ),
        field_name="persisted_uucd.metadata",
    )

    if (
        metadata.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise LifecycleEligibilityContractError(
            "Persisted UUCD metadata is not PERSISTED_AND_VERIFIED."
        )

    handoff = _require_mapping(
        persisted_uucd.get(
            "handoff"
        ),
        field_name="persisted_uucd.handoff",
    )

    if (
        handoff.get(
            "uucd_persisted"
        )
        is not True
    ):
        raise LifecycleEligibilityContractError(
            "Persisted UUCD handoff does not confirm uucd_persisted=true."
        )

    if (
        handoff.get(
            "body_store_verified"
        )
        is not True
    ):
        raise LifecycleEligibilityContractError(
            "Persisted UUCD handoff does not confirm body_store_verified=true."
        )

    if (
        handoff.get(
            "next_stage"
        )
        != "runtime_queue_handoff"
    ):
        raise LifecycleEligibilityContractError(
            "Persisted UUCD is not eligible for runtime_queue_handoff."
        )

    persistence = _require_mapping(
        persisted_uucd.get(
            "persistence"
        ),
        field_name="persisted_uucd.persistence",
    )

    if (
        persistence.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise LifecycleEligibilityContractError(
            "Persistence record is not PERSISTED_AND_VERIFIED."
        )

    if (
        persistence.get(
            "content_body_stored_here"
        )
        is not False
    ):
        raise LifecycleEligibilityContractError(
            "Persistence record must confirm content_body_stored_here=false."
        )

    stored_fingerprint = _require_sha256(
        persistence.get(
            "input_record_sha256"
        ),
        field_name="persisted_uucd.persistence.input_record_sha256",
    )

    if (
        stored_fingerprint
        != persistence_fingerprint
    ):
        raise LifecycleEligibilityContractError(
            "Persistence fingerprint does not match the runtime payload."
        )

    body_verification = _verify_body_reference(
        body_ref=body_ref,
        expected_content_hash=content_hash,
    )

    source_id = _require_text(
        persisted_uucd.get(
            "source_id"
        ),
        field_name="persisted_uucd.source_id",
    )

    semantic_readiness = evaluate_source_semantic_readiness(
        workspace_id=workspace_id,
        source_type=source_type,
        source_id=source_id,
        document_id=document_id,
        content_hash=content_hash,
    )

    if semantic_readiness.get("eligible") is not True:
        reasons = semantic_readiness.get("reasons") or []
        raise LifecycleEligibilityContractError(
            "Semantic Readiness Gate blocked this source: "
            + ", ".join(str(reason) for reason in reasons)
        )

    certificate = {
        "certificate_schema_version":
            LIFECYCLE_ELIGIBILITY_CERTIFICATE_SCHEMA_VERSION,

        "certificate_status":
            "CERTIFIED",

        "handler_version":
            LIFECYCLE_ELIGIBILITY_HANDLER_VERSION,

        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "source_type":
            source_type,

        "content_ref":
            content_ref,

        "body_ref":
            body_ref,

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,

        "uucd_v2_verified":
            True,

        "uucd_persistence_verified":
            True,

        "body_store_verified":
            True,

        "content_body_in_runtime_job":
            False,

        "content_body_in_persisted_uucd":
            False,

        "source_id":
            source_id,

        "workspace_authorized":
            True,

        "source_authorized":
            True,

        "required_version_references_valid":
            True,

        "semantic_processing_authorized":
            True,

        "semantic_readiness_status":
            semantic_readiness.get(
                "readiness_status"
            ),

        "lifecycle_eligible":
            True,

        "semantic_processing_performed":
            False,

        "next_stage":
            NEXT_STAGE,
    }

    return {
        "schema_version":
            LIFECYCLE_ELIGIBILITY_RESULT_SCHEMA_VERSION,

        "handler_version":
            LIFECYCLE_ELIGIBILITY_HANDLER_VERSION,

        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "lifecycle_eligible":
            True,

        "eligibility_status":
            "ELIGIBLE",

        "body_verification":
            body_verification,

        "certificate":
            certificate,

        "next_stage":
            NEXT_STAGE,
    }


def handle_lifecycle_eligibility_runtime_v1(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Runtime Registration handler entry point.
    """

    return evaluate_lifecycle_eligibility_v1(
        job
    )


def explain_lifecycle_eligibility_runtime_handler_v1() -> dict[str, Any]:

    return {
        "component":
            "Lifecycle Eligibility Runtime Handler",

        "version":
            LIFECYCLE_ELIGIBILITY_HANDLER_VERSION,

        "job_type":
            EXPECTED_JOB_TYPE,

        "required_payload_fields":
            list(
                REQUIRED_PAYLOAD_FIELDS
            ),

        "checks": [
            "canonical UUCD v2 identity",
            "PERSISTED_AND_VERIFIED metadata",
            "runtime_queue_handoff eligibility",
            "persistence fingerprint",
            "body reference existence",
            "body SHA-256 integrity",
            "content_body exclusion",
        ],

        "lifecycle_decision":
            "ELIGIBLE or fail closed",

        "semantic_processing_performed":
            False,

        "next_stage":
            NEXT_STAGE,
    }


__all__ = [
    "LIFECYCLE_ELIGIBILITY_HANDLER_VERSION",
    "LIFECYCLE_ELIGIBILITY_RESULT_SCHEMA_VERSION",
    "LIFECYCLE_ELIGIBILITY_CERTIFICATE_SCHEMA_VERSION",
    "EXPECTED_JOB_TYPE",
    "NEXT_STAGE",
    "REQUIRED_PAYLOAD_FIELDS",
    "LifecycleEligibilityError",
    "LifecycleEligibilityContractError",
    "LifecycleEligibilityReferenceError",
    "evaluate_lifecycle_eligibility_v1",
    "handle_lifecycle_eligibility_runtime_v1",
    "explain_lifecycle_eligibility_runtime_handler_v1",
]
