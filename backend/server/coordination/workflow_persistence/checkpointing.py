"""
LinkCraftor — Universal Coordination Framework

Phase 8.3 — Checkpointing

Creates durable coordination-level workflow checkpoints.

A checkpoint captures:
- canonical UniversalWorkflow snapshot,
- persisted StageStateRecord snapshots,
- canonical lifecycle-history entries,
- integrity fingerprints.

This is not the Universal Runtime checkpoint subsystem.

It does not:
- claim jobs,
- pause/resume workers,
- retry jobs,
- mutate workflow lifecycle,
- execute recovery.

Those responsibilities remain in their owning phases/components.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    validate_lifecycle_history,
)

from backend.server.coordination.workflow_persistence.stage_state_store import (
    STAGE_STATE_STORE_VERSION,
    StageStateRecord,
)


CHECKPOINTING_VERSION = (
    "checkpointing_v8.3.0"
)

CHECKPOINT_DOCUMENT_SCHEMA_VERSION = (
    "workflow_checkpoint_document_v1"
)


class WorkflowCheckpointError(
    RuntimeError
):
    pass


class WorkflowCheckpointNotFoundError(
    WorkflowCheckpointError
):
    pass


class WorkflowCheckpointIntegrityError(
    WorkflowCheckpointError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowCheckpoint:

    checkpoint_id: str

    workflow_id: str
    correlation_id: str

    workflow_snapshot: Mapping[str, Any]

    stage_states: Tuple[
        Mapping[str, Any],
        ...
    ]

    lifecycle_history: Tuple[
        Mapping[str, Any],
        ...
    ]

    created_at: str

    checkpoint_fingerprint: str

    workflow_contract_version: str

    stage_state_store_version: str = (
        STAGE_STATE_STORE_VERSION
    )

    checkpointing_version: str = (
        CHECKPOINTING_VERSION
    )

    schema_version: str = (
        CHECKPOINT_DOCUMENT_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "checkpoint_id":
                self.checkpoint_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workflow_snapshot":
                dict(
                    self.workflow_snapshot
                ),

            "stage_states":
                [
                    dict(item)
                    for item
                    in self.stage_states
                ],

            "lifecycle_history":
                [
                    dict(item)
                    for item
                    in self.lifecycle_history
                ],

            "created_at":
                self.created_at,

            "checkpoint_fingerprint":
                self.checkpoint_fingerprint,

            "workflow_contract_version":
                self.workflow_contract_version,

            "stage_state_store_version":
                self.stage_state_store_version,

            "checkpointing_version":
                self.checkpointing_version,

            "schema_version":
                self.schema_version,
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
        raise WorkflowCheckpointIntegrityError(
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
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


_ATOMIC_REPLACE_MAX_ATTEMPTS = 20


def _atomic_replace(
    source: Path,
    target: Path,
) -> None:

    for attempt in range(
        _ATOMIC_REPLACE_MAX_ATTEMPTS
    ):

        try:
            os.replace(
                source,
                target,
            )
            return

        except PermissionError:

            if (
                os.name != "nt"
                or attempt + 1
                >= _ATOMIC_REPLACE_MAX_ATTEMPTS
            ):
                raise

            time.sleep(
                min(
                    0.05
                    * (
                        attempt
                        + 1
                    ),
                    0.25,
                )
            )


def _history_entry_dict(
    entry: LifecycleHistoryEntry,
) -> dict[str, Any]:

    return {
        "event_id":
            entry.event_id,

        "workflow_id":
            entry.workflow_id,

        "correlation_id":
            entry.correlation_id,

        "from_state":
            entry.from_state.value,

        "to_state":
            entry.to_state.value,

        "occurred_at":
            entry.occurred_at,

        "reason":
            entry.reason,

        "source":
            entry.source,

        "actor_id":
            entry.actor_id,

        "metadata":
            dict(
                entry.metadata
            ),

        "transition_validation_version":
            entry.transition_validation_version,

        "state_machine_version":
            entry.state_machine_version,

        "history_version":
            entry.history_version,
    }


def create_workflow_checkpoint(
    *,
    workflow: UniversalWorkflow,
    stage_states: Iterable[StageStateRecord] = (),
    lifecycle_history: Iterable[LifecycleHistoryEntry] = (),
) -> WorkflowCheckpoint:

    if not isinstance(
        workflow,
        UniversalWorkflow,
    ):
        raise TypeError(
            "workflow must be UniversalWorkflow."
        )

    workflow_validation = (
        workflow.validate()
    )

    if not workflow_validation.is_valid:
        raise WorkflowCheckpointIntegrityError(
            "UniversalWorkflow validation failed: "
            + "; ".join(
                workflow_validation.violations
            )
        )

    stage_records = tuple(
        stage_states
    )

    for record in stage_records:

        if not isinstance(
            record,
            StageStateRecord,
        ):
            raise TypeError(
                "stage_states must contain StageStateRecord values."
            )

        if (
            record.workflow_id
            != workflow.workflow_id
        ):
            raise WorkflowCheckpointIntegrityError(
                "Stage-state workflow identity mismatch."
            )

        if (
            record.correlation_id
            != workflow.correlation_id
        ):
            raise WorkflowCheckpointIntegrityError(
                "Stage-state correlation identity mismatch."
            )

    history = tuple(
        lifecycle_history
    )

    for entry in history:

        if not isinstance(
            entry,
            LifecycleHistoryEntry,
        ):
            raise TypeError(
                "lifecycle_history must contain LifecycleHistoryEntry values."
            )

        if (
            entry.workflow_id
            != workflow.workflow_id
        ):
            raise WorkflowCheckpointIntegrityError(
                "Lifecycle-history workflow identity mismatch."
            )

        if (
            entry.correlation_id
            != workflow.correlation_id
        ):
            raise WorkflowCheckpointIntegrityError(
                "Lifecycle-history correlation identity mismatch."
            )

    if history:

        history_validation = (
            validate_lifecycle_history(
                history
            )
        )

        if not history_validation.is_valid:
            raise WorkflowCheckpointIntegrityError(
                "Lifecycle history validation failed: "
                + "; ".join(
                    history_validation.violations
                )
            )

    workflow_snapshot = (
        workflow.to_canonical_dict()
    )

    stage_payloads = tuple(
        record.to_dict()
        for record
        in sorted(
            stage_records,
            key=lambda item:
                item.stage_id,
        )
    )

    history_payloads = tuple(
        _history_entry_dict(
            entry
        )
        for entry
        in history
    )

    created_at = _utc_now()

    material = {
        "workflow_id":
            workflow.workflow_id,

        "correlation_id":
            workflow.correlation_id,

        "workflow_snapshot":
            workflow_snapshot,

        "stage_states":
            list(
                stage_payloads
            ),

        "lifecycle_history":
            list(
                history_payloads
            ),

        "created_at":
            created_at,

        "workflow_contract_version":
            workflow.contract_version,

        "stage_state_store_version":
            STAGE_STATE_STORE_VERSION,

        "checkpointing_version":
            CHECKPOINTING_VERSION,

        "schema_version":
            CHECKPOINT_DOCUMENT_SCHEMA_VERSION,
    }

    checkpoint_fingerprint = (
        _sha256_payload(
            material
        )
    )

    checkpoint_id = hashlib.sha256(
        (
            "ucf_workflow_checkpoint_v1"
            + "\0"
            + workflow.workflow_id
            + "\0"
            + checkpoint_fingerprint
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return WorkflowCheckpoint(
        checkpoint_id=
            checkpoint_id,

        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        workflow_snapshot=
            workflow_snapshot,

        stage_states=
            stage_payloads,

        lifecycle_history=
            history_payloads,

        created_at=
            created_at,

        checkpoint_fingerprint=
            checkpoint_fingerprint,

        workflow_contract_version=
            workflow.contract_version,
    )


class WorkflowCheckpointRepository:

    def __init__(
        self,
        *,
        root: Path | str,
    ) -> None:

        self._root = Path(
            root
        ).resolve()

        self._root.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self._root.is_dir():
            raise WorkflowCheckpointError(
                "Checkpoint repository root is not a directory."
            )

        self._lock = threading.RLock()

    @property
    def root(
        self,
    ) -> Path:

        return self._root

    def checkpoint_path(
        self,
        checkpoint_id: Any,
    ) -> Path:

        checkpoint_id = (
            _required_text(
                checkpoint_id,
                field_name=
                    "checkpoint_id",
            )
        )

        return (
            self._root
            / (
                "checkpoint_"
                + checkpoint_id
                + ".json"
            )
        )

    def save(
        self,
        checkpoint: WorkflowCheckpoint,
    ) -> WorkflowCheckpoint:

        if not isinstance(
            checkpoint,
            WorkflowCheckpoint,
        ):
            raise TypeError(
                "checkpoint must be WorkflowCheckpoint."
            )

        target = self.checkpoint_path(
            checkpoint.checkpoint_id
        )

        document = checkpoint.to_dict()

        with self._lock:

            descriptor, temp_name = (
                tempfile.mkstemp(
                    dir=
                        str(
                            self._root
                        ),

                    prefix=
                        ".checkpoint_",

                    suffix=
                        ".tmp",
                )
            )

            temporary = Path(
                temp_name
            )

            try:

                with os.fdopen(
                    descriptor,
                    "w",
                    encoding="utf-8",
                    newline="\n",
                ) as stream:

                    stream.write(
                        json.dumps(
                            document,
                            ensure_ascii=False,
                            sort_keys=True,
                            indent=2,
                        )
                        + "\n"
                    )

                    stream.flush()

                    os.fsync(
                        stream.fileno()
                    )

                _atomic_replace(
                    temporary,
                    target,
                )

            finally:

                if temporary.exists():
                    temporary.unlink()

        return checkpoint

    def load(
        self,
        checkpoint_id: Any,
    ) -> WorkflowCheckpoint:

        target = self.checkpoint_path(
            checkpoint_id
        )

        with self._lock:

            if not target.is_file():
                raise WorkflowCheckpointNotFoundError(
                    "Workflow checkpoint does not exist."
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
            ) as exc:

                raise WorkflowCheckpointIntegrityError(
                    "Workflow checkpoint cannot be decoded."
                ) from exc

            if not isinstance(
                document,
                Mapping,
            ):
                raise WorkflowCheckpointIntegrityError(
                    "Workflow checkpoint must be a mapping."
                )

            if (
                document.get(
                    "checkpointing_version"
                )
                != CHECKPOINTING_VERSION
            ):
                raise WorkflowCheckpointIntegrityError(
                    "Unsupported checkpointing version."
                )

            if (
                document.get(
                    "schema_version"
                )
                != CHECKPOINT_DOCUMENT_SCHEMA_VERSION
            ):
                raise WorkflowCheckpointIntegrityError(
                    "Unsupported checkpoint schema."
                )

            stored_fingerprint = (
                _required_text(
                    document.get(
                        "checkpoint_fingerprint"
                    ),
                    field_name=
                        "checkpoint_fingerprint",
                )
            )

            material = {
                key:
                    document[key]
                for key
                in (
                    "workflow_id",
                    "correlation_id",
                    "workflow_snapshot",
                    "stage_states",
                    "lifecycle_history",
                    "created_at",
                    "workflow_contract_version",
                    "stage_state_store_version",
                    "checkpointing_version",
                    "schema_version",
                )
            }

            actual_fingerprint = (
                _sha256_payload(
                    material
                )
            )

            if (
                actual_fingerprint
                != stored_fingerprint
            ):
                raise WorkflowCheckpointIntegrityError(
                    "Checkpoint fingerprint mismatch."
                )

            expected_checkpoint_id = (
                hashlib.sha256(
                    (
                        "ucf_workflow_checkpoint_v1"
                        + "\0"
                        + _required_text(
                            document.get(
                                "workflow_id"
                            ),
                            field_name=
                                "workflow_id",
                        )
                        + "\0"
                        + stored_fingerprint
                    ).encode(
                        "utf-8"
                    )
                ).hexdigest().upper()
            )

            if (
                document.get(
                    "checkpoint_id"
                )
                != expected_checkpoint_id
            ):
                raise WorkflowCheckpointIntegrityError(
                    "Checkpoint identity mismatch."
                )

            return WorkflowCheckpoint(
                checkpoint_id=
                    expected_checkpoint_id,

                workflow_id=
                    _required_text(
                        document.get(
                            "workflow_id"
                        ),
                        field_name=
                            "workflow_id",
                    ),

                correlation_id=
                    _required_text(
                        document.get(
                            "correlation_id"
                        ),
                        field_name=
                            "correlation_id",
                    ),

                workflow_snapshot=
                    dict(
                        document.get(
                            "workflow_snapshot",
                            {},
                        )
                    ),

                stage_states=
                    tuple(
                        dict(item)
                        for item
                        in document.get(
                            "stage_states",
                            (),
                        )
                    ),

                lifecycle_history=
                    tuple(
                        dict(item)
                        for item
                        in document.get(
                            "lifecycle_history",
                            (),
                        )
                    ),

                created_at=
                    _required_text(
                        document.get(
                            "created_at"
                        ),
                        field_name=
                            "created_at",
                    ),

                checkpoint_fingerprint=
                    stored_fingerprint,

                workflow_contract_version=
                    _required_text(
                        document.get(
                            "workflow_contract_version"
                        ),
                        field_name=
                            "workflow_contract_version",
                    ),

                stage_state_store_version=
                    _required_text(
                        document.get(
                            "stage_state_store_version"
                        ),
                        field_name=
                            "stage_state_store_version",
                    ),
            )

    def list_checkpoint_ids(
        self,
    ) -> Tuple[str, ...]:

        ids = []

        with self._lock:

            for path in sorted(
                self._root.glob(
                    "checkpoint_*.json"
                )
            ):

                document = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

                checkpoint_id = (
                    _required_text(
                        document.get(
                            "checkpoint_id"
                        ),
                        field_name=
                            "checkpoint_id",
                    )
                )

                # Integrity validation.
                self.load(
                    checkpoint_id
                )

                ids.append(
                    checkpoint_id
                )

        return tuple(
            sorted(
                ids
            )
        )


__all__ = [
    "CHECKPOINTING_VERSION",
    "CHECKPOINT_DOCUMENT_SCHEMA_VERSION",
    "WorkflowCheckpointError",
    "WorkflowCheckpointNotFoundError",
    "WorkflowCheckpointIntegrityError",
    "WorkflowCheckpoint",
    "WorkflowCheckpointRepository",
    "create_workflow_checkpoint",
]
