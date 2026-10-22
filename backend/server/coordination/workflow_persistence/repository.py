"""Atomic persistence for canonical Universal Workflow instances."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
    UniversalWorkflowContractError,
)


WORKFLOW_PERSISTENCE_VERSION = (
    "workflow_persistence_v1.0.0"
)

WORKFLOW_PERSISTENCE_DOCUMENT_SCHEMA_VERSION = (
    "workflow_persistence_document_v1"
)


class WorkflowPersistenceError(RuntimeError):
    """Base error for workflow persistence."""


class WorkflowPersistenceNotFoundError(
    WorkflowPersistenceError
):
    """The requested persisted workflow does not exist."""


class WorkflowPersistenceIntegrityError(
    WorkflowPersistenceError
):
    """Persisted workflow integrity validation failed."""


class WorkflowPersistenceConflictError(
    WorkflowPersistenceError
):
    """Optimistic concurrency validation failed."""


@dataclass(frozen=True, slots=True)
class WorkflowPersistenceEvidence:
    workflow_id: str
    path: str
    workflow_content_fingerprint: str
    workflow_identity_fingerprint: str
    document_fingerprint: str
    persisted_at: str
    persistence_version: str = (
        WORKFLOW_PERSISTENCE_VERSION
    )
    schema_version: str = (
        WORKFLOW_PERSISTENCE_DOCUMENT_SCHEMA_VERSION
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "path": self.path,
            "workflow_content_fingerprint": (
                self.workflow_content_fingerprint
            ),
            "workflow_identity_fingerprint": (
                self.workflow_identity_fingerprint
            ),
            "document_fingerprint": (
                self.document_fingerprint
            ),
            "persisted_at": self.persisted_at,
            "persistence_version": (
                self.persistence_version
            ),
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True, slots=True)
class WorkflowPersistenceRecord:
    workflow: UniversalWorkflow
    evidence: WorkflowPersistenceEvidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": (
                self.workflow.to_canonical_dict()
            ),
            "evidence": self.evidence.to_dict(),
        }


def _required_text(
    value: Any,
    *,
    field_name: str,
) -> str:
    text = str(
        value
        if value is not None
        else ""
    ).strip()

    if not text:
        raise WorkflowPersistenceIntegrityError(
            f"{field_name} must be non-empty."
        )

    return text


def _canonical_json(
    payload: Mapping[str, Any],
) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256_payload(
    payload: Mapping[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(
            payload
        ).encode("utf-8")
    ).hexdigest()


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


class WorkflowRepository:
    """One atomic repository for Universal Workflow instances."""

    def __init__(
        self,
        *,
        root: Path | str,
    ) -> None:
        repository_root = Path(
            root
        ).resolve()

        repository_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not repository_root.is_dir():
            raise WorkflowPersistenceError(
                "Workflow repository root is not a directory."
            )

        self._root = repository_root
        self._lock = threading.RLock()

    @property
    def root(self) -> Path:
        return self._root

    def workflow_path(
        self,
        workflow_id: Any,
    ) -> Path:
        normalized = _required_text(
            workflow_id,
            field_name="workflow_id",
        )

        identity_hash = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

        return (
            self._root
            / f"workflow_{identity_hash}.json"
        )

    def exists(
        self,
        workflow_id: Any,
    ) -> bool:
        return self.workflow_path(
            workflow_id
        ).is_file()

    def save_workflow(
        self,
        workflow: UniversalWorkflow,
        *,
        expected_current_fingerprint: Optional[str] = None,
    ) -> WorkflowPersistenceEvidence:
        if not isinstance(
            workflow,
            UniversalWorkflow,
        ):
            raise TypeError(
                "workflow must be a UniversalWorkflow."
            )

        validation = workflow.validate()

        if not validation.is_valid:
            raise WorkflowPersistenceIntegrityError(
                "Workflow contract validation failed: "
                + "; ".join(validation.violations)
            )

        workflow_id = _required_text(
            workflow.workflow_id,
            field_name="workflow_id",
        )

        target = self.workflow_path(
            workflow_id
        )

        with self._lock:
            if expected_current_fingerprint is not None:
                expected = _required_text(
                    expected_current_fingerprint,
                    field_name=(
                        "expected_current_fingerprint"
                    ),
                )

                if not target.is_file():
                    raise WorkflowPersistenceConflictError(
                        "Expected an existing workflow, "
                        "but no persisted workflow exists."
                    )

                current = self.load_workflow_record(
                    workflow_id
                )

                if (
                    current.evidence
                    .workflow_content_fingerprint
                    != expected
                ):
                    raise WorkflowPersistenceConflictError(
                        "Persisted workflow fingerprint "
                        "does not match the expected value."
                    )

            workflow_payload = (
                workflow.to_canonical_dict()
            )

            content_fingerprint = (
                workflow.content_fingerprint()
            )

            identity_fingerprint = (
                workflow.identity_fingerprint()
            )

            persisted_at = _utc_now()

            document_without_fingerprint = {
                "schema_version": (
                    WORKFLOW_PERSISTENCE_DOCUMENT_SCHEMA_VERSION
                ),
                "persistence_version": (
                    WORKFLOW_PERSISTENCE_VERSION
                ),
                "workflow_id": workflow_id,
                "workflow_contract_version": (
                    workflow.contract_version
                ),
                "workflow_content_fingerprint": (
                    content_fingerprint
                ),
                "workflow_identity_fingerprint": (
                    identity_fingerprint
                ),
                "persisted_at": persisted_at,
                "workflow": workflow_payload,
            }

            document_fingerprint = _sha256_payload(
                document_without_fingerprint
            )

            document = dict(
                document_without_fingerprint
            )

            document["document_fingerprint"] = (
                document_fingerprint
            )

            payload = (
                json.dumps(
                    document,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n"
            )

            descriptor, temporary_name = (
                tempfile.mkstemp(
                    dir=str(self._root),
                    prefix=".workflow_",
                    suffix=".tmp",
                )
            )

            temporary = Path(
                temporary_name
            )

            try:
                with os.fdopen(
                    descriptor,
                    "w",
                    encoding="utf-8",
                    newline="\n",
                ) as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(
                        stream.fileno()
                    )

                os.replace(
                    temporary,
                    target,
                )

                try:
                    directory_descriptor = os.open(
                        str(self._root),
                        os.O_RDONLY,
                    )
                except OSError:
                    directory_descriptor = None

                if directory_descriptor is not None:
                    try:
                        os.fsync(
                            directory_descriptor
                        )
                    except OSError:
                        pass
                    finally:
                        os.close(
                            directory_descriptor
                        )

            finally:
                if temporary.exists():
                    temporary.unlink()

            return WorkflowPersistenceEvidence(
                workflow_id=workflow_id,
                path=str(target),
                workflow_content_fingerprint=(
                    content_fingerprint
                ),
                workflow_identity_fingerprint=(
                    identity_fingerprint
                ),
                document_fingerprint=(
                    document_fingerprint
                ),
                persisted_at=persisted_at,
            )

    def load_workflow_record(
        self,
        workflow_id: Any,
    ) -> WorkflowPersistenceRecord:
        normalized_id = _required_text(
            workflow_id,
            field_name="workflow_id",
        )

        target = self.workflow_path(
            normalized_id
        )

        with self._lock:
            if not target.is_file():
                raise WorkflowPersistenceNotFoundError(
                    "Persisted workflow does not exist: "
                    + normalized_id
                )

            try:
                document = json.loads(
                    target.read_text(
                        encoding="utf-8"
                    )
                )
            except (
                OSError,
                json.JSONDecodeError,
            ) as error:
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow document "
                    "cannot be decoded."
                ) from error

            if not isinstance(
                document,
                Mapping,
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow document "
                    "must be a mapping."
                )

            if (
                document.get("schema_version")
                != WORKFLOW_PERSISTENCE_DOCUMENT_SCHEMA_VERSION
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Unsupported workflow persistence schema."
                )

            if (
                document.get("persistence_version")
                != WORKFLOW_PERSISTENCE_VERSION
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Unsupported workflow persistence version."
                )

            stored_document_fingerprint = (
                _required_text(
                    document.get(
                        "document_fingerprint"
                    ),
                    field_name=(
                        "document_fingerprint"
                    ),
                )
            )

            document_without_fingerprint = dict(
                document
            )

            document_without_fingerprint.pop(
                "document_fingerprint",
                None,
            )

            actual_document_fingerprint = (
                _sha256_payload(
                    document_without_fingerprint
                )
            )

            if (
                stored_document_fingerprint
                != actual_document_fingerprint
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow document "
                    "fingerprint does not match."
                )

            stored_workflow_id = _required_text(
                document.get(
                    "workflow_id"
                ),
                field_name="workflow_id",
            )

            if stored_workflow_id != normalized_id:
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow identity mismatch."
                )

            workflow_payload = document.get(
                "workflow"
            )

            if not isinstance(
                workflow_payload,
                Mapping,
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow payload "
                    "must be a mapping."
                )

            try:
                workflow = UniversalWorkflow.from_dict(
                    workflow_payload
                )
            except (
                UniversalWorkflowContractError,
                TypeError,
                ValueError,
                KeyError,
            ) as error:
                raise WorkflowPersistenceIntegrityError(
                    "Persisted workflow reconstruction failed."
                ) from error

            if workflow.workflow_id != normalized_id:
                raise WorkflowPersistenceIntegrityError(
                    "Reconstructed workflow identity mismatch."
                )

            content_fingerprint = (
                workflow.content_fingerprint()
            )

            identity_fingerprint = (
                workflow.identity_fingerprint()
            )

            if (
                document.get(
                    "workflow_content_fingerprint"
                )
                != content_fingerprint
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Workflow content fingerprint "
                    "does not match."
                )

            if (
                document.get(
                    "workflow_identity_fingerprint"
                )
                != identity_fingerprint
            ):
                raise WorkflowPersistenceIntegrityError(
                    "Workflow identity fingerprint "
                    "does not match."
                )

            evidence = WorkflowPersistenceEvidence(
                workflow_id=normalized_id,
                path=str(target),
                workflow_content_fingerprint=(
                    content_fingerprint
                ),
                workflow_identity_fingerprint=(
                    identity_fingerprint
                ),
                document_fingerprint=(
                    stored_document_fingerprint
                ),
                persisted_at=_required_text(
                    document.get(
                        "persisted_at"
                    ),
                    field_name="persisted_at",
                ),
            )

            return WorkflowPersistenceRecord(
                workflow=workflow,
                evidence=evidence,
            )

    def load_workflow(
        self,
        workflow_id: Any,
    ) -> UniversalWorkflow:
        return self.load_workflow_record(
            workflow_id
        ).workflow

    def list_workflow_ids(
        self,
    ) -> Tuple[str, ...]:
        workflow_ids: list[str] = []

        with self._lock:
            for path in sorted(
                self._root.glob(
                    "workflow_*.json"
                )
            ):
                try:
                    document = json.loads(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )
                except (
                    OSError,
                    json.JSONDecodeError,
                ) as error:
                    raise WorkflowPersistenceIntegrityError(
                        "Repository contains an unreadable "
                        "workflow document."
                    ) from error

                if not isinstance(
                    document,
                    Mapping,
                ):
                    raise WorkflowPersistenceIntegrityError(
                        "Repository contains a malformed "
                        "workflow document."
                    )

                workflow_id = _required_text(
                    document.get(
                        "workflow_id"
                    ),
                    field_name="workflow_id",
                )

                self.load_workflow_record(
                    workflow_id
                )

                workflow_ids.append(
                    workflow_id
                )

        return tuple(
            sorted(workflow_ids)
        )


__all__ = [
    "WORKFLOW_PERSISTENCE_DOCUMENT_SCHEMA_VERSION",
    "WORKFLOW_PERSISTENCE_VERSION",
    "WorkflowPersistenceConflictError",
    "WorkflowPersistenceError",
    "WorkflowPersistenceEvidence",
    "WorkflowPersistenceIntegrityError",
    "WorkflowPersistenceNotFoundError",
    "WorkflowPersistenceRecord",
    "WorkflowRepository",
]
