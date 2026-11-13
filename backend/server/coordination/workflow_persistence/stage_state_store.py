"""
LinkCraftor — Universal Coordination Framework

Phase 8.2 — Stage State Store

Durable coordination-level persistence for canonical stage-state evidence.

Ownership
---------
This store belongs to UCF / Coordination.

It does NOT own:
- Runtime job state,
- queue state,
- worker state,
- execution leases,
- Runtime checkpoints,
- Runtime retry/recovery.

The store does not create a second stage execution state machine.
Instead it persists canonical coordination evidence derived from
UniversalWorkflow and UniversalStageResult contracts.
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
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
)


STAGE_STATE_STORE_VERSION = (
    "stage_state_store_v8.2.0"
)

STAGE_STATE_DOCUMENT_SCHEMA_VERSION = (
    "stage_state_document_v1"
)


class StageStateStoreError(RuntimeError):
    pass


class StageStateNotFoundError(
    StageStateStoreError
):
    pass


class StageStateIntegrityError(
    StageStateStoreError
):
    pass


class StageStateConflictError(
    StageStateStoreError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class StageStateRecord:

    workflow_id: str
    correlation_id: str

    stage_id: str
    stage_version: str

    status: str

    result_id: Optional[str]
    result_reference: Optional[str]

    artifact_references: Tuple[str, ...]

    started_at: Optional[str]
    finished_at: Optional[str]

    failure_code: Optional[str]
    failure_message: Optional[str]

    failure_details: Mapping[str, Any]
    metadata: Mapping[str, Any]

    source_result_contract_version: Optional[str]

    recorded_at: str

    record_fingerprint: str

    store_version: str = (
        STAGE_STATE_STORE_VERSION
    )

    schema_version: str = (
        STAGE_STATE_DOCUMENT_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "status":
                self.status,

            "result_id":
                self.result_id,

            "result_reference":
                self.result_reference,

            "artifact_references":
                list(
                    self.artifact_references
                ),

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "failure_details":
                dict(
                    self.failure_details
                ),

            "metadata":
                dict(
                    self.metadata
                ),

            "source_result_contract_version":
                self.source_result_contract_version,

            "recorded_at":
                self.recorded_at,

            "record_fingerprint":
                self.record_fingerprint,

            "store_version":
                self.store_version,

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
        raise StageStateIntegrityError(
            f"{field_name} must be non-empty."
        )

    return text


def _optional_text(
    value: Any,
) -> Optional[str]:

    if value is None:
        return None

    text = str(
        value
    ).strip()

    return (
        text
        if text
        else None
    )


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


def _record_payload_without_fingerprint(
    *,
    workflow_id: str,
    correlation_id: str,
    stage_id: str,
    stage_version: str,
    status: str,
    result_id: Optional[str],
    result_reference: Optional[str],
    artifact_references: Tuple[str, ...],
    started_at: Optional[str],
    finished_at: Optional[str],
    failure_code: Optional[str],
    failure_message: Optional[str],
    failure_details: Mapping[str, Any],
    metadata: Mapping[str, Any],
    source_result_contract_version: Optional[str],
    recorded_at: str,
) -> dict[str, Any]:

    return {
        "workflow_id":
            workflow_id,

        "correlation_id":
            correlation_id,

        "stage_id":
            stage_id,

        "stage_version":
            stage_version,

        "status":
            status,

        "result_id":
            result_id,

        "result_reference":
            result_reference,

        "artifact_references":
            list(
                artifact_references
            ),

        "started_at":
            started_at,

        "finished_at":
            finished_at,

        "failure_code":
            failure_code,

        "failure_message":
            failure_message,

        "failure_details":
            dict(
                failure_details
            ),

        "metadata":
            dict(
                metadata
            ),

        "source_result_contract_version":
            source_result_contract_version,

        "recorded_at":
            recorded_at,

        "store_version":
            STAGE_STATE_STORE_VERSION,

        "schema_version":
            STAGE_STATE_DOCUMENT_SCHEMA_VERSION,
    }


def stage_state_from_result(
    result: UniversalStageResult,
) -> StageStateRecord:

    if not isinstance(
        result,
        UniversalStageResult,
    ):
        raise TypeError(
            "result must be UniversalStageResult."
        )

    validation = result.validate()

    if not validation.is_valid:
        raise StageStateIntegrityError(
            "UniversalStageResult validation failed: "
            + "; ".join(
                validation.violations
            )
        )

    recorded_at = _utc_now()

    payload = _record_payload_without_fingerprint(
        workflow_id=
            _required_text(
                result.workflow_id,
                field_name="workflow_id",
            ),

        correlation_id=
            _required_text(
                result.correlation_id,
                field_name="correlation_id",
            ),

        stage_id=
            _required_text(
                result.stage_id,
                field_name="stage_id",
            ),

        stage_version=
            _required_text(
                result.stage_version,
                field_name="stage_version",
            ),

        status=
            result.status.value,

        result_id=
            _required_text(
                result.result_id,
                field_name="result_id",
            ),

        result_reference=
            _optional_text(
                result.result_reference
            ),

        artifact_references=
            tuple(
                result.artifact_references
            ),

        started_at=
            _optional_text(
                result.started_at
            ),

        finished_at=
            _optional_text(
                result.finished_at
            ),

        failure_code=
            _optional_text(
                result.failure_code
            ),

        failure_message=
            _optional_text(
                result.failure_message
            ),

        failure_details=
            dict(
                result.failure_details
            ),

        metadata=
            dict(
                result.metadata
            ),

        source_result_contract_version=
            result.contract_version,

        recorded_at=
            recorded_at,
    )

    fingerprint = _sha256_payload(
        payload
    )

    return StageStateRecord(
        workflow_id=
            payload[
                "workflow_id"
            ],

        correlation_id=
            payload[
                "correlation_id"
            ],

        stage_id=
            payload[
                "stage_id"
            ],

        stage_version=
            payload[
                "stage_version"
            ],

        status=
            payload[
                "status"
            ],

        result_id=
            payload[
                "result_id"
            ],

        result_reference=
            payload[
                "result_reference"
            ],

        artifact_references=
            tuple(
                payload[
                    "artifact_references"
                ]
            ),

        started_at=
            payload[
                "started_at"
            ],

        finished_at=
            payload[
                "finished_at"
            ],

        failure_code=
            payload[
                "failure_code"
            ],

        failure_message=
            payload[
                "failure_message"
            ],

        failure_details=
            payload[
                "failure_details"
            ],

        metadata=
            payload[
                "metadata"
            ],

        source_result_contract_version=
            payload[
                "source_result_contract_version"
            ],

        recorded_at=
            recorded_at,

        record_fingerprint=
            fingerprint,
    )


class StageStateRepository:

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
            raise StageStateStoreError(
                "Stage-state repository root is not a directory."
            )

        self._lock = threading.RLock()

    @property
    def root(
        self,
    ) -> Path:

        return self._root

    def stage_path(
        self,
        *,
        workflow_id: Any,
        stage_id: Any,
    ) -> Path:

        workflow = _required_text(
            workflow_id,
            field_name="workflow_id",
        )

        stage = _required_text(
            stage_id,
            field_name="stage_id",
        )

        identity = hashlib.sha256(
            (
                workflow
                + "\0"
                + stage
            ).encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            self._root
            / f"stage_state_{identity}.json"
        )

    def exists(
        self,
        *,
        workflow_id: Any,
        stage_id: Any,
    ) -> bool:

        return self.stage_path(
            workflow_id=
                workflow_id,

            stage_id=
                stage_id,
        ).is_file()

    def save(
        self,
        record: StageStateRecord,
        *,
        expected_current_fingerprint: Optional[str] = None,
    ) -> StageStateRecord:

        if not isinstance(
            record,
            StageStateRecord,
        ):
            raise TypeError(
                "record must be StageStateRecord."
            )

        target = self.stage_path(
            workflow_id=
                record.workflow_id,

            stage_id=
                record.stage_id,
        )

        with self._lock:

            if expected_current_fingerprint is not None:

                if not target.is_file():
                    raise StageStateConflictError(
                        "Expected existing stage state, but none exists."
                    )

                current = self.load(
                    workflow_id=
                        record.workflow_id,

                    stage_id=
                        record.stage_id,
                )

                if (
                    current.record_fingerprint
                    != expected_current_fingerprint
                ):
                    raise StageStateConflictError(
                        "Stage-state fingerprint conflict."
                    )

            payload_without_fingerprint = (
                _record_payload_without_fingerprint(
                    workflow_id=
                        record.workflow_id,

                    correlation_id=
                        record.correlation_id,

                    stage_id=
                        record.stage_id,

                    stage_version=
                        record.stage_version,

                    status=
                        record.status,

                    result_id=
                        record.result_id,

                    result_reference=
                        record.result_reference,

                    artifact_references=
                        record.artifact_references,

                    started_at=
                        record.started_at,

                    finished_at=
                        record.finished_at,

                    failure_code=
                        record.failure_code,

                    failure_message=
                        record.failure_message,

                    failure_details=
                        record.failure_details,

                    metadata=
                        record.metadata,

                    source_result_contract_version=
                        record.source_result_contract_version,

                    recorded_at=
                        record.recorded_at,
                )
            )

            fingerprint = _sha256_payload(
                payload_without_fingerprint
            )

            if (
                fingerprint
                != record.record_fingerprint
            ):
                raise StageStateIntegrityError(
                    "Stage-state record fingerprint does not match content."
                )

            document = dict(
                payload_without_fingerprint
            )

            document[
                "record_fingerprint"
            ] = fingerprint

            text = (
                json.dumps(
                    document,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
                + "\n"
            )

            descriptor, temp_name = (
                tempfile.mkstemp(
                    dir=
                        str(
                            self._root
                        ),

                    prefix=
                        ".stage_state_",

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
                        text
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

            return record

    def save_result(
        self,
        result: UniversalStageResult,
        *,
        expected_current_fingerprint: Optional[str] = None,
    ) -> StageStateRecord:

        record = stage_state_from_result(
            result
        )

        return self.save(
            record,
            expected_current_fingerprint=
                expected_current_fingerprint,
        )

    def load(
        self,
        *,
        workflow_id: Any,
        stage_id: Any,
    ) -> StageStateRecord:

        target = self.stage_path(
            workflow_id=
                workflow_id,

            stage_id=
                stage_id,
        )

        with self._lock:

            if not target.is_file():
                raise StageStateNotFoundError(
                    "Persisted stage state does not exist."
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

                raise StageStateIntegrityError(
                    "Stage-state document cannot be decoded."
                ) from exc

            if not isinstance(
                document,
                Mapping,
            ):
                raise StageStateIntegrityError(
                    "Stage-state document must be a mapping."
                )

            if (
                document.get(
                    "store_version"
                )
                != STAGE_STATE_STORE_VERSION
            ):
                raise StageStateIntegrityError(
                    "Unsupported stage-state store version."
                )

            if (
                document.get(
                    "schema_version"
                )
                != STAGE_STATE_DOCUMENT_SCHEMA_VERSION
            ):
                raise StageStateIntegrityError(
                    "Unsupported stage-state schema version."
                )

            stored_fingerprint = _required_text(
                document.get(
                    "record_fingerprint"
                ),
                field_name=
                    "record_fingerprint",
            )

            payload = dict(
                document
            )

            payload.pop(
                "record_fingerprint",
                None,
            )

            actual_fingerprint = _sha256_payload(
                payload
            )

            if (
                stored_fingerprint
                != actual_fingerprint
            ):
                raise StageStateIntegrityError(
                    "Stage-state fingerprint mismatch."
                )

            return StageStateRecord(
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

                stage_id=
                    _required_text(
                        document.get(
                            "stage_id"
                        ),
                        field_name=
                            "stage_id",
                    ),

                stage_version=
                    _required_text(
                        document.get(
                            "stage_version"
                        ),
                        field_name=
                            "stage_version",
                    ),

                status=
                    _required_text(
                        document.get(
                            "status"
                        ),
                        field_name=
                            "status",
                    ),

                result_id=
                    _optional_text(
                        document.get(
                            "result_id"
                        )
                    ),

                result_reference=
                    _optional_text(
                        document.get(
                            "result_reference"
                        )
                    ),

                artifact_references=
                    tuple(
                        document.get(
                            "artifact_references",
                            (),
                        )
                    ),

                started_at=
                    _optional_text(
                        document.get(
                            "started_at"
                        )
                    ),

                finished_at=
                    _optional_text(
                        document.get(
                            "finished_at"
                        )
                    ),

                failure_code=
                    _optional_text(
                        document.get(
                            "failure_code"
                        )
                    ),

                failure_message=
                    _optional_text(
                        document.get(
                            "failure_message"
                        )
                    ),

                failure_details=
                    dict(
                        document.get(
                            "failure_details",
                            {},
                        )
                    ),

                metadata=
                    dict(
                        document.get(
                            "metadata",
                            {},
                        )
                    ),

                source_result_contract_version=
                    _optional_text(
                        document.get(
                            "source_result_contract_version"
                        )
                    ),

                recorded_at=
                    _required_text(
                        document.get(
                            "recorded_at"
                        ),
                        field_name=
                            "recorded_at",
                    ),

                record_fingerprint=
                    stored_fingerprint,
            )

    def list_for_workflow(
        self,
        workflow_id: Any,
    ) -> Tuple[StageStateRecord, ...]:

        workflow = _required_text(
            workflow_id,
            field_name=
                "workflow_id",
        )

        records = []

        with self._lock:

            for path in sorted(
                self._root.glob(
                    "stage_state_*.json"
                )
            ):

                try:
                    document = json.loads(
                        path.read_text(
                            encoding="utf-8"
                        )
                    )
                except Exception as exc:
                    raise StageStateIntegrityError(
                        "Repository contains unreadable stage-state document."
                    ) from exc

                if (
                    document.get(
                        "workflow_id"
                    )
                    != workflow
                ):
                    continue

                records.append(
                    self.load(
                        workflow_id=
                            workflow,

                        stage_id=
                            document.get(
                                "stage_id"
                            ),
                    )
                )

        return tuple(
            sorted(
                records,
                key=lambda item:
                    item.stage_id,
            )
        )


__all__ = [
    "STAGE_STATE_STORE_VERSION",
    "STAGE_STATE_DOCUMENT_SCHEMA_VERSION",
    "StageStateStoreError",
    "StageStateNotFoundError",
    "StageStateIntegrityError",
    "StageStateConflictError",
    "StageStateRecord",
    "StageStateRepository",
    "stage_state_from_result",
]
