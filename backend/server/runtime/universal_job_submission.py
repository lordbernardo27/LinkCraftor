from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable, Mapping, Optional

from backend.server.orchestration.service import (
    create_orchestration_job,
)
from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationResult,
    create_universal_job,
)
from backend.server.runtime.universal_runtime_registration import (
    get_runtime_registration,
)


UNIVERSAL_JOB_SUBMISSION_VERSION = (
    "universal_job_submission_v1"
)

UNIVERSAL_JOB_SUBMISSION_PROJECTION_VERSION = (
    "universal_job_submission_projection_v1"
)

UNIVERSAL_JOB_SUBMISSION_METADATA_KEY = (
    "universal_runtime_submission"
)


class UniversalJobSubmissionError(RuntimeError):
    """Universal Runtime submission boundary failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
    ) -> None:
        super().__init__(message)
        self.code = str(code)


def _canonical_orchestration_priority(
    value: Any,
) -> int:
    """
    Project the already-normalized Universal Job priority into the
    current orchestration store's integer priority representation.

    This is intentionally NOT the canonical Job Priority authority.
    Phase 2.1.6 remains responsible for final Universal Job priority
    semantics.
    """

    raw = getattr(
        value,
        "value",
        value,
    )

    if isinstance(
        raw,
        bool,
    ):
        raise UniversalJobSubmissionError(
            "Boolean priority cannot be projected into orchestration.",
            code="invalid_orchestration_priority",
        )

    if isinstance(
        raw,
        int,
    ):
        return raw

    if isinstance(
        raw,
        float,
    ):
        if raw.is_integer():
            return int(raw)

        raise UniversalJobSubmissionError(
            "Non-integral priority cannot be projected into orchestration.",
            code="invalid_orchestration_priority",
        )

    text = str(
        raw
    ).strip()

    if (
        text
        and text.lstrip(
            "+-"
        ).isdigit()
    ):
        return int(
            text
        )

    raise UniversalJobSubmissionError(
        (
            "Canonical Universal Job priority cannot currently be "
            "projected into the orchestration integer priority field."
        ),
        code="invalid_orchestration_priority",
    )


def _build_orchestration_metadata(
    *,
    creation_result: UniversalJobCreationResult,
) -> dict[str, Any]:
    """
    Preserve creation-time metadata while carrying a namespaced snapshot
    of the canonical Universal Job into orchestration.

    The snapshot prevents orchestration persistence from becoming a
    second job-contract authority.
    """

    creation_document = (
        creation_result.to_dict()
    )

    creation_metadata = dict(
        creation_document.get(
            "metadata"
        )
        or {}
    )

    if (
        UNIVERSAL_JOB_SUBMISSION_METADATA_KEY
        in creation_metadata
    ):
        raise UniversalJobSubmissionError(
            (
                "Creation metadata uses the reserved "
                f"{UNIVERSAL_JOB_SUBMISSION_METADATA_KEY!r} key."
            ),
            code="reserved_submission_metadata_key",
        )

    creation_metadata[
        UNIVERSAL_JOB_SUBMISSION_METADATA_KEY
    ] = {
        "schema_version": (
            UNIVERSAL_JOB_SUBMISSION_PROJECTION_VERSION
        ),
        "submission_version": (
            UNIVERSAL_JOB_SUBMISSION_VERSION
        ),
        "canonical_job": dict(
            creation_document.get(
                "job"
            )
            or {}
        ),
        "registration": (
            creation_document.get(
                "registration"
            )
        ),
        "fingerprints": {
            "identity": creation_document.get(
                "identity_fingerprint"
            ),
            "contract": creation_document.get(
                "contract_fingerprint"
            ),
            "content": creation_document.get(
                "content_fingerprint"
            ),
        },
    }

    return creation_metadata


def submit_universal_job(
    *,
    workspace_id: str,
    job_type: str,
    payload: Optional[
        Mapping[str, Any]
    ] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
    user_id: str = "system",
    product_id: str = "linkcraftor",
    pipeline: str = "",
    stage: str = "",
    payload_reference: Optional[str] = None,
    priority: Any = 5,
    parent_job_id: Optional[str] = None,
    dependency_job_ids: Optional[
        Iterable[Any]
    ] = None,
    batch_id: Optional[str] = None,
    pipeline_run_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    maximum_attempts: Optional[int] = None,
    job_id: Optional[str] = None,
    created_at: Optional[str] = None,
    supported_job_types: Optional[
        Iterable[Any]
    ] = None,
    runtime_registration: Optional[
        Mapping[str, Any]
    ] = None,
    enqueue: bool = True,
) -> dict[str, Any]:
    """
    Create one canonical Universal Job and submit that SAME identity
    into the LinkCraftor orchestration store.

    This is an I/O boundary.

    Creation authority:
        Universal Job Creation Engine

    Registration authority:
        Universal Runtime Registration

    Persistence / queue authority:
        orchestration.service -> orchestration.job_store

    The Creation Engine remains I/O-free.
    """

    if not enqueue:
        raise UniversalJobSubmissionError(
            (
                "Universal job submission currently represents the "
                "persisted queued ingress and therefore requires "
                "enqueue=True."
            ),
            code="submission_requires_enqueue",
        )

    effective_registration = (
        runtime_registration
    )

    if effective_registration is None:
        effective_registration = (
            get_runtime_registration(
                job_type
            )
        )

    creation_result = (
        create_universal_job(
            workspace_id=workspace_id,
            job_type=job_type,
            payload=payload,
            metadata=metadata,
            user_id=user_id,
            product_id=product_id,
            pipeline=pipeline,
            stage=stage,
            payload_reference=(
                payload_reference
            ),
            priority=priority,
            parent_job_id=(
                parent_job_id
            ),
            dependency_job_ids=(
                dependency_job_ids
            ),
            batch_id=batch_id,
            pipeline_run_id=(
                pipeline_run_id
            ),
            idempotency_key=(
                idempotency_key
            ),
            maximum_attempts=(
                maximum_attempts
            ),
            enqueue=True,
            job_id=job_id,
            created_at=created_at,
            supported_job_types=(
                supported_job_types
            ),
            runtime_registration=(
                effective_registration
            ),
        )
    )

    creation_document = (
        creation_result.to_dict()
    )

    canonical_job = dict(
        creation_document.get(
            "job"
        )
        or {}
    )

    canonical_job_id = str(
        canonical_job.get(
            "job_id"
        )
        or ""
    ).strip()

    if not canonical_job_id:
        raise UniversalJobSubmissionError(
            (
                "Universal Job Creation Engine returned "
                "no canonical job_id."
            ),
            code="missing_canonical_job_id",
        )

    canonical_workspace_id = str(
        canonical_job.get(
            "workspace_id"
        )
        or workspace_id
        or ""
    ).strip()

    canonical_job_type = str(
        canonical_job.get(
            "job_type"
        )
        or job_type
        or ""
    ).strip()

    orchestration_priority = (
        _canonical_orchestration_priority(
            canonical_job.get(
                "priority",
                priority,
            )
        )
    )

    orchestration_metadata = (
        _build_orchestration_metadata(
            creation_result=(
                creation_result
            )
        )
    )

    orchestration_job = (
        create_orchestration_job(
            workspace_id=(
                canonical_workspace_id
            ),
            job_type=(
                canonical_job_type
            ),
            payload=dict(
                creation_document.get(
                    "payload"
                )
                or {}
            ),
            metadata=(
                orchestration_metadata
            ),
            priority=(
                orchestration_priority
            ),
            job_id=(
                canonical_job_id
            ),
        )
    )

    persisted_job_id = str(
        orchestration_job.job_id
        or ""
    ).strip()

    if (
        persisted_job_id
        != canonical_job_id
    ):
        raise UniversalJobSubmissionError(
            (
                "Orchestration persisted a different job identity "
                "than the canonical Universal Job identity."
            ),
            code="orchestration_identity_mismatch",
        )

    persisted_status = str(
        orchestration_job.status
        or ""
    ).strip()

    if (
        persisted_status
        != "queued"
    ):
        raise UniversalJobSubmissionError(
            (
                "Submitted Universal Job was not persisted "
                "with queued orchestration status."
            ),
            code="orchestration_not_queued",
        )

    result = dict(
        canonical_job
    )

    # Preserve the payload and creation metadata in the familiar
    # job-shaped result consumed by existing pipeline callers.
    result[
        "payload"
    ] = dict(
        creation_document.get(
            "payload"
        )
        or {}
    )

    result[
        "metadata"
    ] = dict(
        creation_document.get(
            "metadata"
        )
        or {}
    )

    result[
        "registration"
    ] = (
        creation_document.get(
            "registration"
        )
    )

    result[
        "identity_fingerprint"
    ] = creation_document.get(
        "identity_fingerprint"
    )

    result[
        "contract_fingerprint"
    ] = creation_document.get(
        "contract_fingerprint"
    )

    result[
        "content_fingerprint"
    ] = creation_document.get(
        "content_fingerprint"
    )

    result[
        "orchestration"
    ] = asdict(
        orchestration_job
    )

    result[
        "submission"
    ] = {
        "submission_version": (
            UNIVERSAL_JOB_SUBMISSION_VERSION
        ),
        "persisted": True,
        "queued": True,
        "canonical_identity_preserved": True,
    }

    return result


def explain_universal_job_submission_v1(
) -> dict[str, Any]:
    return {
        "component": (
            "Universal Job Submission / Orchestration Ingress"
        ),
        "version": (
            UNIVERSAL_JOB_SUBMISSION_VERSION
        ),
        "scope": "LinkCraftor-wide",
        "canonical_operation": (
            "submit_universal_job"
        ),
        "creation_authority": (
            "Universal Job Creation Engine"
        ),
        "registration_authority": (
            "Universal Runtime Registration"
        ),
        "persistence_authority": (
            "orchestration.service / orchestration.job_store"
        ),
        "queue_authority": (
            "orchestration.queue"
        ),
        "identity_rule": (
            "The canonical Universal Job job_id is persisted "
            "unchanged into orchestration."
        ),
        "prohibitions": [
            (
                "does not generate a second runtime job identity"
            ),
            (
                "does not move persistence into the "
                "Universal Job Creation Engine"
            ),
            (
                "does not use the legacy "
                "universal_knowledge_orchestrator"
            ),
            (
                "does not define final Job Priority semantics; "
                "Phase 2.1.6 remains authoritative"
            ),
        ],
    }


__all__ = [
    "UNIVERSAL_JOB_SUBMISSION_VERSION",
    "UNIVERSAL_JOB_SUBMISSION_PROJECTION_VERSION",
    "UNIVERSAL_JOB_SUBMISSION_METADATA_KEY",
    "UniversalJobSubmissionError",
    "submit_universal_job",
    "explain_universal_job_submission_v1",
]
