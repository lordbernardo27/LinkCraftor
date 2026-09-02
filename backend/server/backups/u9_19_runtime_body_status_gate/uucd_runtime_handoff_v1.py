"""
Canonical UUCD -> Universal Runtime Handoff Adapter v1.

Canonical position:

    Canonical UUCD Persistence
        ->
    persisted canonical UUCD
        ->
    handoff_persisted_uucd_to_runtime_v1()
        ->
    Universal Job Creation Engine
        ->
    canonical Universal Job
        ->
    Orchestration Job Store

This component does:

- validate a persisted canonical UUCD Record;
- verify Stage 9 runtime-handoff eligibility;
- build the minimum metadata/reference-only runtime payload;
- derive a deterministic logical idempotency key;
- resolve Runtime Registration metadata;
- create exactly one canonical Universal Job identity;
- persist that SAME job_id into the orchestration job store;
- return an auditable handoff certificate.

This component does NOT:

- copy or persist article body content;
- permit content_body in the runtime payload;
- create a second independent job identity;
- use the retired universal_knowledge JSONL queue;
- execute workers;
- dispatch Runtime Registration handlers;
- perform semantic processing;
- mutate Runtime Registration;
- mark the job completed or failed.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping

from backend.server.orchestration.job_store import (
    create_job as create_orchestration_job,
    load_jobs as load_orchestration_jobs,
)
from backend.server.runtime.universal_jobs.creation_engine import (
    create_universal_job,
)
from backend.server.runtime.universal_runtime_registration import (
    get_runtime_registration,
)


UUCD_RUNTIME_HANDOFF_VERSION = (
    "uucd_runtime_handoff_v1"
)

UUCD_RUNTIME_HANDOFF_SCHEMA_VERSION = (
    "uucd_runtime_handoff_result_v1"
)

UUCD_RUNTIME_HANDOFF_CERTIFICATE_SCHEMA_VERSION = (
    "uucd_runtime_handoff_certificate_v1"
)

UUCD_RUNTIME_JOB_TYPE = (
    "uucd_runtime_handoff"
)

UUCD_RUNTIME_PIPELINE = (
    "universal_knowledge"
)

UUCD_RUNTIME_STAGE = (
    "runtime_queue_handoff"
)

UUCD_RUNTIME_REQUIRED_PAYLOAD_FIELDS = (
    "document_id",
    "content_ref",
    "body_ref",
    "source_type",
    "content_hash",
    "persistence_fingerprint",
)

SHA256_PATTERN = re.compile(
    r"^[a-f0-9]{64}$"
)

DOCUMENT_ID_PATTERN = re.compile(
    r"^uucd_[a-f0-9]{32}$"
)


class UUCDRuntimeHandoffError(
    RuntimeError
):
    """Base error for canonical UUCD runtime handoff."""


class UUCDRuntimeHandoffContractError(
    UUCDRuntimeHandoffError
):
    """Raised when persisted UUCD input violates the contract."""


class UUCDRuntimeHandoffRegistrationError(
    UUCDRuntimeHandoffError
):
    """Raised when required Runtime Registration is unavailable."""


class UUCDRuntimeHandoffPersistenceError(
    UUCDRuntimeHandoffError
):
    """Raised when canonical orchestration ingress fails."""


def _utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise UUCDRuntimeHandoffContractError(
            f"{field_name} must be a mapping."
        )

    return value


def _require_non_empty_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise UUCDRuntimeHandoffContractError(
            f"{field_name} must be a string."
        )

    cleaned = value.strip()

    if not cleaned:
        raise UUCDRuntimeHandoffContractError(
            f"{field_name} must not be empty."
        )

    return cleaned


def _require_sha256(
    value: Any,
    *,
    field_name: str,
) -> str:

    digest = _require_non_empty_string(
        value,
        field_name=field_name,
    ).casefold()

    if not SHA256_PATTERN.fullmatch(
        digest
    ):
        raise UUCDRuntimeHandoffContractError(
            f"{field_name} must be a SHA-256 digest."
        )

    return digest


def _validate_persisted_uucd(
    persisted_uucd_record: Mapping[str, Any],
) -> dict[str, Any]:

    record = _require_mapping(
        persisted_uucd_record,
        field_name="persisted_uucd_record",
    )

    if "content_body" in record:
        raise UUCDRuntimeHandoffContractError(
            "Persisted UUCD must not contain content_body."
        )

    workspace_id = _require_non_empty_string(
        record.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    document_id = _require_non_empty_string(
        record.get(
            "document_id"
        ),
        field_name="document_id",
    )

    if not DOCUMENT_ID_PATTERN.fullmatch(
        document_id
    ):
        raise UUCDRuntimeHandoffContractError(
            "document_id is not a canonical UUCD identifier."
        )

    source_type = _require_non_empty_string(
        record.get(
            "source_type"
        ),
        field_name="source_type",
    )

    content_ref = _require_non_empty_string(
        record.get(
            "content_ref"
        ),
        field_name="content_ref",
    )

    body_ref = _require_non_empty_string(
        record.get(
            "body_ref"
        ),
        field_name="body_ref",
    )

    content_hash = _require_sha256(
        record.get(
            "content_hash"
        ),
        field_name="content_hash",
    )

    metadata = _require_mapping(
        record.get(
            "metadata"
        ),
        field_name="metadata",
    )

    if (
        metadata.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise UUCDRuntimeHandoffContractError(
            "metadata.persistence_status must be "
            "PERSISTED_AND_VERIFIED."
        )

    handoff = _require_mapping(
        record.get(
            "handoff"
        ),
        field_name="handoff",
    )

    if (
        handoff.get(
            "uucd_persisted"
        )
        is not True
    ):
        raise UUCDRuntimeHandoffContractError(
            "handoff.uucd_persisted must be true."
        )

    if (
        handoff.get(
            "next_stage"
        )
        != UUCD_RUNTIME_STAGE
    ):
        raise UUCDRuntimeHandoffContractError(
            "handoff.next_stage must be "
            "runtime_queue_handoff."
        )

    if (
        handoff.get(
            "body_store_verified"
        )
        is not True
    ):
        raise UUCDRuntimeHandoffContractError(
            "handoff.body_store_verified must be true."
        )

    persistence = _require_mapping(
        record.get(
            "persistence"
        ),
        field_name="persistence",
    )

    if (
        persistence.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise UUCDRuntimeHandoffContractError(
            "persistence.persistence_status must be "
            "PERSISTED_AND_VERIFIED."
        )

    if (
        persistence.get(
            "content_body_stored_here"
        )
        is not False
    ):
        raise UUCDRuntimeHandoffContractError(
            "persistence.content_body_stored_here "
            "must be false."
        )

    persistence_fingerprint = _require_sha256(
        persistence.get(
            "input_record_sha256"
        ),
        field_name=(
            "persistence.input_record_sha256"
        ),
    )

    return {
        "record":
            record,

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
    }


def build_uucd_runtime_idempotency_key_v1(
    *,
    workspace_id: str,
    document_id: str,
    content_hash: str,
    persistence_fingerprint: str,
    job_type: str = UUCD_RUNTIME_JOB_TYPE,
) -> str:
    """
    Build deterministic logical identity for one UUCD runtime handoff.

    This is deliberately separate from the Universal Job's job_id.
    """

    material = {
        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,

        "job_type":
            job_type,
    }

    canonical = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    digest = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        "uucd_runtime_handoff_"
        + digest
    )


def build_uucd_runtime_payload_v1(
    persisted_uucd_record: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the canonical metadata/reference-only runtime payload.

    Article body bytes are never included here.
    """

    validated = _validate_persisted_uucd(
        persisted_uucd_record
    )

    payload = {
        "document_id":
            validated[
                "document_id"
            ],

        "content_ref":
            validated[
                "content_ref"
            ],

        "body_ref":
            validated[
                "body_ref"
            ],

        "source_type":
            validated[
                "source_type"
            ],

        "content_hash":
            validated[
                "content_hash"
            ],

        "persistence_fingerprint":
            validated[
                "persistence_fingerprint"
            ],
    }

    if "content_body" in payload:
        raise UUCDRuntimeHandoffContractError(
            "Runtime payload unexpectedly contains content_body."
        )

    return payload


def _resolve_runtime_registration(
    *,
    job_type: str,
    runtime_registration: Mapping[str, Any] | None,
) -> Mapping[str, Any]:

    registration: Mapping[str, Any] | None

    if runtime_registration is not None:

        registration = _require_mapping(
            runtime_registration,
            field_name="runtime_registration",
        )

    else:

        registration = (
            get_runtime_registration(
                job_type
            )
        )

    if registration is None:
        raise UUCDRuntimeHandoffRegistrationError(
            "No Runtime Registration exists for "
            f"job_type={job_type!r}."
        )

    registered_job_type = (
        _require_non_empty_string(
            registration.get(
                "job_type"
            ),
            field_name=(
                "runtime_registration.job_type"
            ),
        )
    )

    if registered_job_type != job_type:
        raise UUCDRuntimeHandoffRegistrationError(
            "Runtime Registration job_type does not "
            "match the UUCD runtime job type."
        )

    return registration


def _find_existing_orchestration_job_by_idempotency_key_v1(
    *,
    workspace_id: str,
    job_type: str,
    idempotency_key: str,
):
    """
    Return an existing canonical orchestration job for the same logical
    UUCD runtime handoff.

    Idempotency is logical identity, not a replacement job_id generator.
    """

    jobs = load_orchestration_jobs()

    matches = []

    for candidate in jobs.values():

        if (
            candidate.workspace_id
            != workspace_id
        ):
            continue

        if (
            candidate.job_type
            != job_type
        ):
            continue

        metadata = (
            candidate.metadata
            if isinstance(
                candidate.metadata,
                dict,
            )
            else {}
        )

        if (
            metadata.get(
                "idempotency_key"
            )
            != idempotency_key
        ):
            continue

        matches.append(
            candidate
        )

    if not matches:
        return None

    if len(matches) > 1:
        raise UUCDRuntimeHandoffPersistenceError(
            "Canonical orchestration store contains multiple jobs "
            "for the same UUCD runtime idempotency_key."
        )

    return matches[0]


def handoff_persisted_uucd_to_runtime_v1(
    persisted_uucd_record: Mapping[str, Any],
    *,
    runtime_registration: Mapping[str, Any] | None = None,
    user_id: str = "system",
    product_id: str = "linkcraftor",
    priority: int = 5,
) -> dict[str, Any]:
    """
    Create and persist one canonical Universal Job for a persisted UUCD.

    The Universal Job Creation Engine remains I/O-free.

    The resulting canonical Universal Job job_id is then supplied to the
    orchestration store through Stage 10.5's caller-owned identity ingress.
    """

    validated = _validate_persisted_uucd(
        persisted_uucd_record
    )

    payload = build_uucd_runtime_payload_v1(
        persisted_uucd_record
    )

    idempotency_key = (
        build_uucd_runtime_idempotency_key_v1(
            workspace_id=validated[
                "workspace_id"
            ],
            document_id=validated[
                "document_id"
            ],
            content_hash=validated[
                "content_hash"
            ],
            persistence_fingerprint=validated[
                "persistence_fingerprint"
            ],
            job_type=UUCD_RUNTIME_JOB_TYPE,
        )
    )

    registration = (
        _resolve_runtime_registration(
            job_type=UUCD_RUNTIME_JOB_TYPE,
            runtime_registration=runtime_registration,
        )
    )

    existing_orchestration_job = (
        _find_existing_orchestration_job_by_idempotency_key_v1(
            workspace_id=validated[
                "workspace_id"
            ],
            job_type=UUCD_RUNTIME_JOB_TYPE,
            idempotency_key=idempotency_key,
        )
    )

    if existing_orchestration_job is not None:

        existing_metadata = (
            existing_orchestration_job.metadata
            if isinstance(
                existing_orchestration_job.metadata,
                dict,
            )
            else {}
        )

        existing_canonical_job = (
            existing_metadata.get(
                "canonical_universal_job"
            )
        )

        if not isinstance(
            existing_canonical_job,
            Mapping,
        ):
            raise UUCDRuntimeHandoffPersistenceError(
                "Existing idempotent orchestration job does not "
                "contain canonical_universal_job metadata."
            )

        existing_job_id = (
            _require_non_empty_string(
                existing_orchestration_job.job_id,
                field_name="existing_orchestration_job.job_id",
            )
        )

        if (
            existing_canonical_job.get(
                "job_id"
            )
            != existing_job_id
        ):
            raise UUCDRuntimeHandoffPersistenceError(
                "Existing idempotent job violates canonical "
                "job identity preservation."
            )

        if (
            existing_canonical_job.get(
                "idempotency_key"
            )
            != idempotency_key
        ):
            raise UUCDRuntimeHandoffPersistenceError(
                "Existing canonical Universal Job idempotency_key "
                "does not match orchestration metadata."
            )

        return {
            "schema_version":
                UUCD_RUNTIME_HANDOFF_SCHEMA_VERSION,

            "handoff_version":
                UUCD_RUNTIME_HANDOFF_VERSION,

            "handoff_status":
                "IDEMPOTENT_REUSE",

            "job_id":
                existing_job_id,

            "canonical_universal_job":
                deepcopy(
                    dict(
                        existing_canonical_job
                    )
                ),

            "orchestration_job": {
                "job_id":
                    existing_orchestration_job.job_id,

                "workspace_id":
                    existing_orchestration_job.workspace_id,

                "job_type":
                    existing_orchestration_job.job_type,

                "status":
                    existing_orchestration_job.status,

                "priority":
                    existing_orchestration_job.priority,

                "payload":
                    deepcopy(
                        existing_orchestration_job.payload
                    ),

                "metadata":
                    deepcopy(
                        existing_orchestration_job.metadata
                    ),

                "assigned_worker_id":
                    existing_orchestration_job.assigned_worker_id,
            },

            "idempotency_key":
                idempotency_key,

            "idempotent_reuse":
                True,

            "new_universal_job_created":
                False,

            "new_orchestration_job_created":
                False,

            "body_content_in_job":
                False,

            "old_universal_knowledge_jsonl_used":
                False,

            "worker_executed":
                False,

            "handler_dispatched":
                False,

            "semantic_processing_performed":
                False,

            "next_stage":
                "universal_runtime_worker",
        }

    creation_result = create_universal_job(
        workspace_id=validated[
            "workspace_id"
        ],
        job_type=UUCD_RUNTIME_JOB_TYPE,
        payload=payload,
        metadata={
            "source_component":
                "Canonical UUCD Persistence",

            "handoff_adapter":
                UUCD_RUNTIME_HANDOFF_VERSION,

            "document_id":
                validated[
                    "document_id"
                ],

            "persistence_fingerprint":
                validated[
                    "persistence_fingerprint"
                ],

            "body_content_in_job":
                False,
        },
        user_id=user_id,
        product_id=product_id,
        pipeline=UUCD_RUNTIME_PIPELINE,
        stage=UUCD_RUNTIME_STAGE,
        payload_reference=validated[
            "content_ref"
        ],
        idempotency_key=idempotency_key,
        enqueue=True,
        runtime_registration=registration,
    )

    universal_job = (
        creation_result.job
    )

    canonical_job = (
        universal_job.to_canonical_dict()
    )

    canonical_job_id = (
        _require_non_empty_string(
            canonical_job.get(
                "job_id"
            ),
            field_name="canonical_job.job_id",
        )
    )

    if (
        canonical_job.get(
            "workspace_id"
        )
        != validated[
            "workspace_id"
        ]
    ):
        raise UUCDRuntimeHandoffContractError(
            "Universal Job workspace_id drifted "
            "from the persisted UUCD."
        )

    if (
        canonical_job.get(
            "payload_reference"
        )
        != validated[
            "content_ref"
        ]
    ):
        raise UUCDRuntimeHandoffContractError(
            "Universal Job payload_reference drifted "
            "from canonical UUCD content_ref."
        )

    if (
        canonical_job.get(
            "idempotency_key"
        )
        != idempotency_key
    ):
        raise UUCDRuntimeHandoffContractError(
            "Universal Job idempotency_key drifted."
        )

    try:

        orchestration_job = (
            create_orchestration_job(
                workspace_id=validated[
                    "workspace_id"
                ],
                job_type=UUCD_RUNTIME_JOB_TYPE,
                payload=deepcopy(
                    payload
                ),
                metadata={
                    "canonical_universal_job":
                        canonical_job,

                    "universal_job_contract_version":
                        canonical_job.get(
                            "contract_version"
                        ),

                    "payload_reference":
                        validated[
                            "content_ref"
                        ],

                    "idempotency_key":
                        idempotency_key,

                    "persistence_fingerprint":
                        validated[
                            "persistence_fingerprint"
                        ],

                    "handoff_adapter":
                        UUCD_RUNTIME_HANDOFF_VERSION,

                    "body_content_in_job":
                        False,
                },
                priority=priority,
                job_id=canonical_job_id,
            )
        )

    except Exception as exc:
        raise UUCDRuntimeHandoffPersistenceError(
            "Canonical orchestration ingress failed."
        ) from exc

    if (
        orchestration_job.job_id
        != canonical_job_id
    ):
        raise UUCDRuntimeHandoffPersistenceError(
            "Orchestration layer changed the "
            "canonical Universal Job identity."
        )

    if (
        orchestration_job.status
        != "queued"
    ):
        raise UUCDRuntimeHandoffPersistenceError(
            "New orchestration job must enter "
            "the canonical queue as status=queued."
        )

    certificate = {
        "certificate_schema_version":
            UUCD_RUNTIME_HANDOFF_CERTIFICATE_SCHEMA_VERSION,

        "certificate_status":
            "CERTIFIED",

        "handoff_version":
            UUCD_RUNTIME_HANDOFF_VERSION,

        "workspace_id":
            validated[
                "workspace_id"
            ],

        "document_id":
            validated[
                "document_id"
            ],

        "job_id":
            canonical_job_id,

        "job_type":
            UUCD_RUNTIME_JOB_TYPE,

        "pipeline":
            UUCD_RUNTIME_PIPELINE,

        "stage":
            UUCD_RUNTIME_STAGE,

        "payload_reference":
            validated[
                "content_ref"
            ],

        "body_ref":
            validated[
                "body_ref"
            ],

        "content_hash":
            validated[
                "content_hash"
            ],

        "persistence_fingerprint":
            validated[
                "persistence_fingerprint"
            ],

        "idempotency_key":
            idempotency_key,

        "job_identity_preserved":
            True,

        "orchestration_status":
            orchestration_job.status,

        "body_content_in_job":
            False,

        "old_universal_knowledge_jsonl_used":
            False,

        "runtime_registration_modified":
            False,

        "worker_executed":
            False,

        "handler_dispatched":
            False,

        "semantic_processing_performed":
            False,

        "certified_at":
            _utc_now_iso(),
    }

    return {
        "schema_version":
            UUCD_RUNTIME_HANDOFF_SCHEMA_VERSION,

        "handoff_status":
            "QUEUED",

        "job_id":
            canonical_job_id,

        "job_type":
            UUCD_RUNTIME_JOB_TYPE,

        "payload":
            deepcopy(
                payload
            ),

        "canonical_universal_job":
            canonical_job,

        "orchestration_job":
            {
                "job_id":
                    orchestration_job.job_id,

                "workspace_id":
                    orchestration_job.workspace_id,

                "job_type":
                    orchestration_job.job_type,

                "status":
                    orchestration_job.status,

                "priority":
                    orchestration_job.priority,
            },

        "handoff_certificate":
            certificate,

        "next_stage":
            "universal_runtime_worker",
    }


def explain_uucd_runtime_handoff_v1() -> dict[str, Any]:
    """Return the canonical Stage 10.7 handoff contract."""

    return {
        "component":
            "Canonical UUCD Runtime Handoff Adapter",

        "version":
            UUCD_RUNTIME_HANDOFF_VERSION,

        "job_type":
            UUCD_RUNTIME_JOB_TYPE,

        "pipeline":
            UUCD_RUNTIME_PIPELINE,

        "stage":
            UUCD_RUNTIME_STAGE,

        "required_payload_fields":
            list(
                UUCD_RUNTIME_REQUIRED_PAYLOAD_FIELDS
            ),

        "payload_reference_rule":
            "persisted_uucd.content_ref",

        "body_reference_rule":
            "payload.body_ref only; body bytes excluded",

        "idempotency_material": [
            "workspace_id",
            "document_id",
            "content_hash",
            "persistence_fingerprint",
            "job_type",
        ],

        "job_identity_rule":
            (
                "Universal Job Creation Engine creates one "
                "canonical job_id; orchestration persists "
                "that exact same job_id."
            ),

        "runtime_registration_required":
            True,

        "runtime_registration_mutated":
            False,

        "old_jsonl_queue_used":
            False,

        "worker_executed":
            False,

        "handler_dispatched":
            False,

        "semantic_processing_performed":
            False,

        "next_stage":
            "universal_runtime_worker",
    }


__all__ = [
    "UUCD_RUNTIME_HANDOFF_VERSION",
    "UUCD_RUNTIME_HANDOFF_SCHEMA_VERSION",
    "UUCD_RUNTIME_HANDOFF_CERTIFICATE_SCHEMA_VERSION",
    "UUCD_RUNTIME_JOB_TYPE",
    "UUCD_RUNTIME_PIPELINE",
    "UUCD_RUNTIME_STAGE",
    "UUCD_RUNTIME_REQUIRED_PAYLOAD_FIELDS",
    "UUCDRuntimeHandoffError",
    "UUCDRuntimeHandoffContractError",
    "UUCDRuntimeHandoffRegistrationError",
    "UUCDRuntimeHandoffPersistenceError",
    "build_uucd_runtime_idempotency_key_v1",
    "build_uucd_runtime_payload_v1",
    "handoff_persisted_uucd_to_runtime_v1",
    "explain_uucd_runtime_handoff_v1",
]

