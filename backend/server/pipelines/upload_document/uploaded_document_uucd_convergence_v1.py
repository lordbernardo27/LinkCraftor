"""
Canonical Uploaded Document UUCD Convergence Coordinator v1.

Responsibility
--------------
Compose already-certified canonical stages after the Uploaded Document
pipeline has produced a READY_FOR_BODY_STORE UUCD handoff envelope.

Boundary:

READY_FOR_BODY_STORE
    -> Universal Article Body Store
    -> STORED_AND_VERIFIED
    -> READY_FOR_UUCD_PERSISTENCE
    -> Canonical UUCD Persistence
    -> PERSISTED_AND_VERIFIED
    -> Source Governance

This coordinator does NOT:
- execute Universal Runtime Infrastructure;
- create queue jobs;
- execute Semantic Intelligence;
- execute scorer.py;
- execute linking;
- execute highlighting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from backend.server.stores.persisted_uucd_source_governance_v1 import (
    govern_persisted_uucd_source_v1,
)
from backend.server.universal_article_body_store.body_store_writer_v1 import (
    write_verified_body_from_envelope_v1,
)
from backend.server.universal_unified_content_document.uucd_persistence_v1 import (
    persist_finalized_uucd_v1,
)


UPLOADED_DOCUMENT_UUCD_CONVERGENCE_VERSION = (
    "uploaded_document_uucd_convergence_v1"
)

DEFAULT_PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[4]
)


class UploadedDocumentUUCDConvergenceError(
    RuntimeError
):
    """Raised when canonical uploaded-document convergence fails."""


def converge_uploaded_document_uucd_v1(
    envelope: Mapping[str, Any],
    *,
    project_root: str | Path = DEFAULT_PROJECT_ROOT,
    overwrite: bool = False,
    authorized_by: str = "system",
) -> dict[str, Any]:
    """
    Complete canonical convergence for one READY_FOR_BODY_STORE envelope.

    The input envelope remains owned by the UUCD creation stage.
    This function delegates all storage, persistence, and governance
    responsibilities to their canonical modules.
    """

    if not isinstance(
        envelope,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "UUCD envelope must be a mapping."
        )

    if (
        envelope.get(
            "envelope_status"
        )
        != "READY_FOR_BODY_STORE"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "UUCD envelope must be READY_FOR_BODY_STORE."
        )

    root = Path(
        project_root
    ).resolve()

    # ------------------------------------------------------------
    # 1. Universal Article Body Store
    # ------------------------------------------------------------

    body_store_result = (
        write_verified_body_from_envelope_v1(
            envelope,
            project_root=root,
            overwrite=overwrite,
        )
    )

    if not isinstance(
        body_store_result,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Body Store writer returned a non-mapping result."
        )

    if (
        body_store_result.get(
            "write_status"
        )
        != "STORED_AND_VERIFIED"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Body Store write did not reach STORED_AND_VERIFIED."
        )

    finalized_uucd_record = (
        body_store_result.get(
            "finalized_uucd_record"
        )
    )

    if not isinstance(
        finalized_uucd_record,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Body Store result does not contain finalized_uucd_record."
        )

    if (
        finalized_uucd_record.get(
            "body_status"
        )
        != "STORED_AND_VERIFIED"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Finalized UUCD body_status is not STORED_AND_VERIFIED."
        )

    finalized_metadata = (
        finalized_uucd_record.get(
            "metadata"
        )
    )

    if (
        not isinstance(
            finalized_metadata,
            Mapping,
        )
        or finalized_metadata.get(
            "persistence_status"
        )
        != "READY_FOR_UUCD_PERSISTENCE"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Finalized UUCD is not READY_FOR_UUCD_PERSISTENCE."
        )

    finalized_handoff = (
        finalized_uucd_record.get(
            "handoff"
        )
    )

    if (
        not isinstance(
            finalized_handoff,
            Mapping,
        )
        or finalized_handoff.get(
            "eligible_for_uucd_persistence"
        )
        is not True
        or finalized_handoff.get(
            "body_store_verified"
        )
        is not True
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Finalized UUCD persistence handoff is invalid."
        )

    # ------------------------------------------------------------
    # 2. Canonical UUCD Persistence
    # ------------------------------------------------------------

    persistence_result = (
        persist_finalized_uucd_v1(
            finalized_uucd_record,
            project_root=root,
            overwrite=overwrite,
        )
    )

    if not isinstance(
        persistence_result,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "UUCD persistence returned a non-mapping result."
        )

    if (
        persistence_result.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "UUCD persistence did not reach PERSISTED_AND_VERIFIED."
        )

    persisted_uucd_record = (
        persistence_result.get(
            "persisted_uucd_record"
        )
    )

    if not isinstance(
        persisted_uucd_record,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Persistence result does not contain persisted_uucd_record."
        )

    persistence = (
        persisted_uucd_record.get(
            "persistence"
        )
    )

    if (
        not isinstance(
            persistence,
            Mapping,
        )
        or persistence.get(
            "persistence_status"
        )
        != "PERSISTED_AND_VERIFIED"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Persisted UUCD record is not PERSISTED_AND_VERIFIED."
        )

    if (
        persisted_uucd_record.get(
            "body_status"
        )
        != "STORED_AND_VERIFIED"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Persisted UUCD body_status is not STORED_AND_VERIFIED."
        )

    if (
        "content_body"
        in persisted_uucd_record
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Permanent UUCD must not contain content_body."
        )

    # ------------------------------------------------------------
    # 3. Source Authorization + Lifecycle + Version Governance
    # ------------------------------------------------------------

    governance_result = (
        govern_persisted_uucd_source_v1(
            persisted_uucd_record,
            authorized_by=authorized_by,
        )
    )

    if not isinstance(
        governance_result,
        Mapping,
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Source governance returned a non-mapping result."
        )

    if (
        governance_result.get(
            "status"
        )
        != "SOURCE_GOVERNANCE_COMPLETE"
    ):
        raise UploadedDocumentUUCDConvergenceError(
            "Source governance did not complete successfully."
        )

    return {
        "schema_version":
            "uploaded_document_uucd_convergence_result_v1",

        "convergence_version":
            UPLOADED_DOCUMENT_UUCD_CONVERGENCE_VERSION,

        "status":
            "UPLOADED_DOCUMENT_UUCD_CONVERGENCE_COMPLETE",

        "workspace_id":
            persisted_uucd_record.get(
                "workspace_id"
            ),

        "source_type":
            persisted_uucd_record.get(
                "source_type"
            ),

        "source_id":
            persisted_uucd_record.get(
                "source_id"
            ),

        "document_id":
            persisted_uucd_record.get(
                "document_id"
            ),

        "content_hash":
            persisted_uucd_record.get(
                "content_hash"
            ),

        "body_ref":
            persisted_uucd_record.get(
                "body_ref"
            ),

        "content_ref":
            persisted_uucd_record.get(
                "content_ref"
            ),

        "body_store_result":
            dict(
                body_store_result
            ),

        "persistence_result":
            dict(
                persistence_result
            ),

        "governance_result":
            dict(
                governance_result
            ),

        "runtime_executed":
            False,

        "queue_job_created":
            False,

        "semantic_processing_performed":
            False,

        "next_stage":
            "semantic_readiness_gate",
    }


__all__ = [
    "UPLOADED_DOCUMENT_UUCD_CONVERGENCE_VERSION",
    "DEFAULT_PROJECT_ROOT",
    "UploadedDocumentUUCDConvergenceError",
    "converge_uploaded_document_uucd_v1",
]
