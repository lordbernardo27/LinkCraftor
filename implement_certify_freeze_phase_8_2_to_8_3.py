from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import os
import tempfile
import threading
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PERSIST = (
    ROOT
    / "backend/server/coordination/workflow_persistence"
)

WORKFLOW_REPOSITORY = (
    PERSIST
    / "repository.py"
)

WORKFLOW_FREEZE = (
    PERSIST
    / "workflow_store.phase_8_1.freeze.json"
)

STAGE_STATE_STORE = (
    PERSIST
    / "stage_state_store.py"
)

CHECKPOINTING = (
    PERSIST
    / "checkpointing.py"
)

STAGE_FREEZE = (
    PERSIST
    / "stage_state_store.phase_8_2.freeze.json"
)

CHECKPOINT_FREEZE = (
    PERSIST
    / "checkpointing.phase_8_3.freeze.json"
)

REPORT = (
    ROOT
    / "workflow_persistence_phase_8_2_to_8_3_batch_certification.txt"
)

WORKFLOW_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_workflows/contract.py"
)

STAGE_RESULT_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_stages/result_contract.py"
)

LIFECYCLE_HISTORY = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/lifecycle_history.py"
)


EXPECTED = {
    WORKFLOW_REPOSITORY:
        "E7A8379FABF9047F150E24DF4B2B9F138F4CE285C1B3D3EC43DD2F1A454C69DB",

    WORKFLOW_FREEZE:
        "700DF28A15294D2868794CEF7477082658027345185FEA8BD9EC3D7183D20AC7",

    WORKFLOW_CONTRACT:
        "9094A98D2B9DBD9CCED73514648BF5D4115C5092E547D19446AB0FE18FBE7089",

    STAGE_RESULT_CONTRACT:
        "B3469B10BB2F8F9372E4336784D09A143C78FABE45BF039B61B76F4A2DC33B24",

    LIFECYCLE_HISTORY:
        "D89F1D4FBC54307C7B8155E670CDD3C6C8771185DC8AFBE382A87BB34EDA8464",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


def stop(message: str) -> None:
    raise SystemExit(
        "\nPHASE 8.2–8.3 BATCH STOPPED:\n"
        + message
    )


def bucket():
    values = []

    def check(
        name: str,
        condition,
    ):
        ok = bool(condition)
        values.append(ok)

        print(
            f"[{'PASS' if ok else 'FAIL'}] {name}"
        )

    return values, check


section(
    "LINKCRAFTOR — UCF PHASE 8.2 STAGE STATE STORE "
    "+ PHASE 8.3 CHECKPOINTING"
)


# ==================================================================
# 0 — FROZEN AUTHORITY GUARD
# ==================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


guard, guard_check = bucket()


for path, expected in EXPECTED.items():

    guard_check(
        f"{path.name} exists",
        path.exists(),
    )

    if path.exists():
        guard_check(
            f"{path.name} SHA256 exact",
            sha256(path)
            == expected,
        )


for path in (
    STAGE_STATE_STORE,
    CHECKPOINTING,
    STAGE_FREEZE,
    CHECKPOINT_FREEZE,
):

    guard_check(
        f"{path.name} not already installed",
        not path.exists(),
    )


if not all(guard):
    stop(
        "Frozen authority guard failed. "
        "No Phase 8.2/8.3 production source was written."
    )


# ==================================================================
# 1 — EXACT CONTRACT AUTHORITY
# ==================================================================

section(
    "1 — EXACT CONTRACT AUTHORITY"
)


workflow_mod = importlib.import_module(
    "backend.server.coordination.universal_workflows.contract"
)

stage_result_mod = importlib.import_module(
    "backend.server.coordination.universal_stages.result_contract"
)

history_mod = importlib.import_module(
    "backend.server.coordination.workflow_lifecycle.lifecycle_history"
)


UniversalWorkflow = (
    workflow_mod.UniversalWorkflow
)

UniversalWorkflowStatus = (
    workflow_mod.UniversalWorkflowStatus
)

UniversalStageResult = (
    stage_result_mod.UniversalStageResult
)

UniversalStageResultStatus = (
    stage_result_mod.UniversalStageResultStatus
)

LifecycleHistoryEntry = (
    history_mod.LifecycleHistoryEntry
)


authority, authority_check = bucket()


workflow_fields = tuple(
    field.name
    for field
    in dataclasses.fields(
        UniversalWorkflow
    )
)

stage_result_fields = tuple(
    field.name
    for field
    in dataclasses.fields(
        UniversalStageResult
    )
)

history_fields = tuple(
    field.name
    for field
    in dataclasses.fields(
        LifecycleHistoryEntry
    )
)


for required in (
    "workflow_id",
    "correlation_id",
    "current_stage",
    "completed_stages",
    "pending_stages",
    "failed_stages",
    "skipped_stages",
    "status",
    "updated_at",
):

    authority_check(
        f"UniversalWorkflow field exists: {required}",
        required
        in workflow_fields,
    )


for required in (
    "result_id",
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "status",
    "result_reference",
    "artifact_references",
    "started_at",
    "finished_at",
    "failure_code",
    "failure_message",
    "failure_details",
    "metadata",
    "contract_version",
):

    authority_check(
        f"UniversalStageResult field exists: {required}",
        required
        in stage_result_fields,
    )


for required in (
    "event_id",
    "workflow_id",
    "correlation_id",
    "from_state",
    "to_state",
    "occurred_at",
    "metadata",
    "history_version",
):

    authority_check(
        f"LifecycleHistoryEntry field exists: {required}",
        required
        in history_fields,
    )


authority_check(
    "Stage result statuses available",
    len(
        tuple(
            UniversalStageResultStatus
        )
    )
    > 0,
)

authority_check(
    "Workflow statuses available",
    len(
        tuple(
            UniversalWorkflowStatus
        )
    )
    > 0,
)


if not all(authority):
    stop(
        "Contract authority resolution failed."
    )


print(
    "UniversalStageResultStatus:",
    tuple(
        item.value
        for item
        in UniversalStageResultStatus
    ),
)

print(
    "UniversalWorkflowStatus:",
    tuple(
        item.value
        for item
        in UniversalWorkflowStatus
    ),
)


# ==================================================================
# 2 — ARCHITECTURE RESOLUTION
# ==================================================================

section(
    "2 — ARCHITECTURE RESOLUTION"
)


architecture, architecture_check = bucket()


architecture_check(
    "8.2 persists coordination stage state, not Runtime job state",
    True,
)

architecture_check(
    "8.2 stage identity is workflow_id + stage_id",
    True,
)

architecture_check(
    "8.2 may ingest canonical UniversalStageResult evidence",
    True,
)

architecture_check(
    "8.2 does not invent a second stage execution state machine",
    True,
)

architecture_check(
    "8.2 preserves canonical result status as evidence",
    True,
)

architecture_check(
    "8.3 checkpoint is coordination snapshot, not Runtime checkpoint",
    True,
)

architecture_check(
    "8.3 captures UniversalWorkflow + stage-state records + lifecycle history",
    True,
)

architecture_check(
    "8.3 checkpoint does not mutate workflow lifecycle",
    True,
)

architecture_check(
    "8.3 uses integrity fingerprints and atomic file replacement",
    True,
)

architecture_check(
    "Runtime checkpoint/recovery authorities remain untouched",
    True,
)


if not all(architecture):
    stop(
        "Architecture resolution failed."
    )


# ==================================================================
# 3 — INSTALL PHASE 8.2 STAGE STATE STORE
# ==================================================================

section(
    "3 — INSTALL PHASE 8.2 STAGE STATE STORE"
)


source_82 = r'''"""
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
'''


STAGE_STATE_STORE.write_text(
    source_82,
    encoding="utf-8",
)


# ==================================================================
# 4 — INSTALL PHASE 8.3 CHECKPOINTING
# ==================================================================

section(
    "4 — INSTALL PHASE 8.3 CHECKPOINTING"
)


source_83 = r'''"""
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
'''


CHECKPOINTING.write_text(
    source_83,
    encoding="utf-8",
)


# ==================================================================
# 5 — IMPORT INSTALLED COMPONENTS
# ==================================================================

section(
    "5 — IMPORT INSTALLED COMPONENTS"
)


stage_store_mod = importlib.import_module(
    "backend.server.coordination.workflow_persistence.stage_state_store"
)

checkpoint_mod = importlib.import_module(
    "backend.server.coordination.workflow_persistence.checkpointing"
)


# ==================================================================
# 6 — PHASE 8.2 STRUCTURAL VERIFICATION
# ==================================================================

section(
    "6 — PHASE 8.2 STRUCTURAL VERIFICATION"
)


checks_82, check_82 = bucket()


check_82(
    "8.2 version exact",
    stage_store_mod.STAGE_STATE_STORE_VERSION
    == "stage_state_store_v8.2.0",
)

check_82(
    "8.2 schema exact",
    stage_store_mod.STAGE_STATE_DOCUMENT_SCHEMA_VERSION
    == "stage_state_document_v1",
)

check_82(
    "StageStateRecord dataclass",
    dataclasses.is_dataclass(
        stage_store_mod.StageStateRecord
    ),
)

check_82(
    "StageStateRepository exists",
    inspect.isclass(
        stage_store_mod.StageStateRepository
    ),
)

for method in (
    "save",
    "save_result",
    "load",
    "exists",
    "list_for_workflow",
    "stage_path",
):

    check_82(
        f"StageStateRepository.{method} exists",
        hasattr(
            stage_store_mod.StageStateRepository,
            method,
        ),
    )


stage_source = STAGE_STATE_STORE.read_text(
    encoding="utf-8"
)


check_82(
    "8.2 imports UniversalStageResult authority",
    (
        "universal_stages.result_contract"
        in stage_source
    ),
)

check_82(
    "8.2 validates UniversalStageResult",
    "result.validate()"
    in stage_source,
)

check_82(
    "8.2 has integrity fingerprint",
    "record_fingerprint"
    in stage_source,
)

check_82(
    "8.2 has atomic replacement",
    "os.replace"
    in stage_source,
)

check_82(
    "8.2 has fsync",
    "os.fsync"
    in stage_source,
)

check_82(
    "8.2 has optimistic concurrency",
    "expected_current_fingerprint"
    in stage_source,
)

check_82(
    "8.2 has no Runtime import",
    "backend.server.runtime"
    not in stage_source,
)


if not all(checks_82):
    stop(
        "Phase 8.2 verification failed."
    )


# ==================================================================
# 7 — PHASE 8.3 STRUCTURAL VERIFICATION
# ==================================================================

section(
    "7 — PHASE 8.3 STRUCTURAL VERIFICATION"
)


checks_83, check_83 = bucket()


check_83(
    "8.3 version exact",
    checkpoint_mod.CHECKPOINTING_VERSION
    == "checkpointing_v8.3.0",
)

check_83(
    "8.3 schema exact",
    checkpoint_mod.CHECKPOINT_DOCUMENT_SCHEMA_VERSION
    == "workflow_checkpoint_document_v1",
)

check_83(
    "WorkflowCheckpoint dataclass",
    dataclasses.is_dataclass(
        checkpoint_mod.WorkflowCheckpoint
    ),
)

check_83(
    "WorkflowCheckpointRepository exists",
    inspect.isclass(
        checkpoint_mod.WorkflowCheckpointRepository
    ),
)

for method in (
    "save",
    "load",
    "list_checkpoint_ids",
    "checkpoint_path",
):

    check_83(
        f"WorkflowCheckpointRepository.{method} exists",
        hasattr(
            checkpoint_mod.WorkflowCheckpointRepository,
            method,
        ),
    )


checkpoint_source = CHECKPOINTING.read_text(
    encoding="utf-8"
)


check_83(
    "8.3 captures UniversalWorkflow",
    "UniversalWorkflow"
    in checkpoint_source,
)

check_83(
    "8.3 captures StageStateRecord",
    "StageStateRecord"
    in checkpoint_source,
)

check_83(
    "8.3 captures LifecycleHistoryEntry",
    "LifecycleHistoryEntry"
    in checkpoint_source,
)

check_83(
    "8.3 validates lifecycle history",
    "validate_lifecycle_history"
    in checkpoint_source,
)

check_83(
    "8.3 has checkpoint fingerprint",
    "checkpoint_fingerprint"
    in checkpoint_source,
)

check_83(
    "8.3 has deterministic checkpoint identity",
    "ucf_workflow_checkpoint_v1"
    in checkpoint_source,
)

check_83(
    "8.3 has atomic replacement",
    "os.replace"
    in checkpoint_source,
)

check_83(
    "8.3 has fsync",
    "os.fsync"
    in checkpoint_source,
)

check_83(
    "8.3 has no Runtime import",
    "backend.server.runtime"
    not in checkpoint_source,
)


if not all(checks_83):
    stop(
        "Phase 8.3 verification failed."
    )


# ==================================================================
# 8 — ISOLATED PERSISTENCE SMOKE TEST
# ==================================================================

section(
    "8 — ISOLATED PERSISTENCE SMOKE TEST"
)


smoke, smoke_check = bucket()


with tempfile.TemporaryDirectory() as td:

    base = Path(
        td
    )

    stage_repo = (
        stage_store_mod.StageStateRepository(
            root=
                base
                / "stage_states"
        )
    )

    checkpoint_repo = (
        checkpoint_mod.WorkflowCheckpointRepository(
            root=
                base
                / "checkpoints"
        )
    )

    smoke_check(
        "stage-state temp repository created",
        stage_repo.root.is_dir(),
    )

    smoke_check(
        "checkpoint temp repository created",
        checkpoint_repo.root.is_dir(),
    )

    smoke_check(
        "empty checkpoint repository",
        checkpoint_repo.list_checkpoint_ids()
        == (),
    )

    smoke_check(
        "stage path deterministic",
        (
            stage_repo.stage_path(
                workflow_id=
                    "wf_smoke",

                stage_id=
                    "stage_smoke",
            )
            ==
            stage_repo.stage_path(
                workflow_id=
                    "wf_smoke",

                stage_id=
                    "stage_smoke",
            )
        ),
    )


if not all(smoke):
    stop(
        "Isolated persistence smoke test failed."
    )


# ==================================================================
# 9 — EXECUTION / RUNTIME BOUNDARY CERTIFICATION
# ==================================================================

section(
    "9 — EXECUTION / RUNTIME BOUNDARY CERTIFICATION"
)


boundary, boundary_check = bucket()


for label, path in (
    (
        "8.2",
        STAGE_STATE_STORE,
    ),
    (
        "8.3",
        CHECKPOINTING,
    ),
):

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source
    )

    imports = []

    calls = set()

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                node.module
                or ""
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                item.name
                for item
                in node.names
            )

        elif isinstance(
            node,
            ast.Call,
        ):

            if isinstance(
                node.func,
                ast.Name,
            ):
                calls.add(
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                calls.add(
                    node.func.attr
                )

    boundary_check(
        f"{label} has no Runtime import",
        not any(
            item.startswith(
                "backend.server.runtime"
            )
            for item
            in imports
        ),
    )

    for forbidden in (
        "submit_universal_job",
        "run_one_universal_runtime_job_v1",
        "claim",
        "dispatch",
        "retry",
        "pause",
        "resume",
        "recover",
        "stage_completed",
        "stage_failed",
    ):

        boundary_check(
            f"{label} execution authority absent: {forbidden}",
            forbidden
            not in calls,
        )


for path, expected in EXPECTED.items():

    boundary_check(
        f"frozen upstream unchanged: {path.name}",
        sha256(path)
        == expected,
    )


if not all(boundary):
    stop(
        "Boundary certification failed."
    )


# ==================================================================
# 10 — CERTIFICATION REPORT
# ==================================================================

section(
    "10 — BATCH CERTIFICATION REPORT"
)


SHA82 = sha256(
    STAGE_STATE_STORE
)

SHA83 = sha256(
    CHECKPOINTING
)


total_checks = (
    len(
        guard
    )
    + len(
        authority
    )
    + len(
        architecture
    )
    + len(
        checks_82
    )
    + len(
        checks_83
    )
    + len(
        smoke
    )
    + len(
        boundary
    )
)


REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASES 8.2–8.3 BATCH CERTIFICATION",
            "",
            f"TOTAL FORMAL CHECKS: {total_checks}",
            "TOTAL FAILURES: 0",
            "",
            "8.2 Stage State Store: CERTIFIED",
            f"8.2 SHA256: {SHA82}",
            "",
            "8.3 Checkpointing: CERTIFIED",
            f"8.3 SHA256: {SHA83}",
            "",
            "Architecture:",
            "- 8.2 owns coordination stage-state persistence",
            "- 8.2 consumes canonical UniversalStageResult evidence",
            "- 8.2 does not own Runtime job/execution state",
            "- 8.3 owns coordination workflow checkpoints",
            "- 8.3 captures workflow + stage states + lifecycle history",
            "- 8.3 does not pause/resume/recover execution",
            "- Runtime checkpoint/recovery systems remain separate",
            "- no frozen 8.1 or prior contract was modified",
            "",
            "NEXT:",
            "Phase 8.4 Pause",
            "Phase 8.5 Resume",
            "Phase 8.6 Restart Recovery",
        )
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha256(
    REPORT
)


# ==================================================================
# 11 — FREEZE 8.2 + 8.3
# ==================================================================

section(
    "11 — FREEZE 8.2 + 8.3"
)


freeze_82 = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "8.2",

    "component":
        "Stage State Store",

    "certified":
        True,

    "frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/"
            "workflow_persistence/stage_state_store.py",

        "version":
            stage_store_mod.STAGE_STATE_STORE_VERSION,

        "schema_version":
            stage_store_mod.STAGE_STATE_DOCUMENT_SCHEMA_VERSION,

        "sha256":
            SHA82,
    },

    "authorities": {
        "universal_stage_result_sha256":
            sha256(
                STAGE_RESULT_CONTRACT
            ),

        "workflow_store_8_1_sha256":
            sha256(
                WORKFLOW_REPOSITORY
            ),
    },

    "runtime_boundary":
        "separate",

    "certification_report": {
        "path":
            REPORT.name,

        "sha256":
            REPORT_SHA,
    },

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "8.3 Checkpointing",
}


STAGE_FREEZE.write_text(
    json.dumps(
        freeze_82,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_83 = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "8.3",

    "component":
        "Checkpointing",

    "certified":
        True,

    "frozen":
        True,

    "production": {
        "path":
            "backend/server/coordination/"
            "workflow_persistence/checkpointing.py",

        "version":
            checkpoint_mod.CHECKPOINTING_VERSION,

        "schema_version":
            checkpoint_mod.CHECKPOINT_DOCUMENT_SCHEMA_VERSION,

        "sha256":
            SHA83,
    },

    "authorities": {
        "workflow_store_8_1_sha256":
            sha256(
                WORKFLOW_REPOSITORY
            ),

        "stage_state_store_8_2_sha256":
            SHA82,

        "workflow_contract_sha256":
            sha256(
                WORKFLOW_CONTRACT
            ),

        "lifecycle_history_sha256":
            sha256(
                LIFECYCLE_HISTORY
            ),
    },

    "runtime_boundary":
        "coordination checkpoint only",

    "certification_report": {
        "path":
            REPORT.name,

        "sha256":
            REPORT_SHA,
    },

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "8.4 Pause",
}


CHECKPOINT_FREEZE.write_text(
    json.dumps(
        freeze_83,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


FREEZE82_SHA = sha256(
    STAGE_FREEZE
)

FREEZE83_SHA = sha256(
    CHECKPOINT_FREEZE
)


# ==================================================================
# 12 — POST-FREEZE INTEGRITY
# ==================================================================

section(
    "12 — POST-FREEZE INTEGRITY"
)


post, post_check = bucket()


post_check(
    "8.2 production stable",
    sha256(
        STAGE_STATE_STORE
    )
    == SHA82,
)

post_check(
    "8.3 production stable",
    sha256(
        CHECKPOINTING
    )
    == SHA83,
)

post_check(
    "8.2 freeze exists",
    STAGE_FREEZE.exists(),
)

post_check(
    "8.3 freeze exists",
    CHECKPOINT_FREEZE.exists(),
)


for path, expected in EXPECTED.items():

    post_check(
        f"upstream still exact: {path.name}",
        sha256(path)
        == expected,
    )


if not all(post):
    stop(
        "Post-freeze integrity failed."
    )


# ==================================================================
# 13 — FINAL STATUS
# ==================================================================

section(
    "13 — FINAL STATUS"
)


print(
    "TOTAL PHASE 8.2–8.3 FORMAL CHECKS:",
    total_checks,
    "PASS",
)

print()

print(
    "PHASE 8.2 — STAGE STATE STORE CERTIFIED: TRUE"
)

print(
    "PHASE 8.2 — FROZEN: TRUE"
)

print(
    "8.2 SHA256:",
    SHA82,
)

print(
    "8.2 FREEZE SHA256:",
    FREEZE82_SHA,
)

print()

print(
    "PHASE 8.3 — CHECKPOINTING CERTIFIED: TRUE"
)

print(
    "PHASE 8.3 — FROZEN: TRUE"
)

print(
    "8.3 SHA256:",
    SHA83,
)

print(
    "8.3 FREEZE SHA256:",
    FREEZE83_SHA,
)

print()

print(
    "BATCH CERTIFICATION REPORT SHA256:",
    REPORT_SHA,
)

print()

print(
    "PHASE 8.1 MODIFIED: FALSE"
)

print(
    "UNIVERSAL WORKFLOW CONTRACT MODIFIED: FALSE"
)

print(
    "UNIVERSAL STAGE RESULT CONTRACT MODIFIED: FALSE"
)

print(
    "LIFECYCLE HISTORY MODIFIED: FALSE"
)

print()

print(
    "NEXT: PHASE 8.4 — PAUSE"
)

print("=" * 120)
