"""Canonical per-document UUCD persistence v1.

Responsibility
--------------
Persist exactly one finalized UUCD Record after the Universal Article
Body Store has independently verified the corresponding article body.

Canonical order:

    UUCD Engine
        ->
    Universal Handoff Envelope
        ->
    Body Store Writer
        ->
    body STORED_AND_VERIFIED
        ->
    finalized_uucd_record
        ->
    READY_FOR_UUCD_PERSISTENCE
        ->
    persist_finalized_uucd_v1()
        ->
    canonical per-document UUCD JSON

This component does not:
- build UUCD Records;
- write article body content;
- accept content_body inside a UUCD Record;
- execute runtime jobs;
- create queue jobs;
- perform semantic processing;
- manage lifecycle deletion/archive/purge;
- recreate the retired workspace-level aggregate UUCD store.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_repository_v1 import (
    verify_body,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    REQUIRED_UUCD_RECORD_FIELDS,
    UUCD_SCHEMA_VERSION,
)


UUCD_PERSISTENCE_VERSION = (
    "uucd_persistence_v1"
)

UUCD_PERSISTENCE_SCHEMA_VERSION = (
    "uucd_persistence_record_v1"
)

UUCD_PERSISTENCE_CERTIFICATE_SCHEMA_VERSION = (
    "uucd_persistence_certificate_v1"
)

UUCD_STORE_ROOT_RELATIVE = (
    Path("backend")
    / "server"
    / "data"
    / "universal_unified_content_documents"
)

WORKSPACE_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"
)

DOCUMENT_ID_PATTERN = re.compile(
    r"^uucd_[a-f0-9]{32}$"
)

SHA256_PATTERN = re.compile(
    r"^[a-f0-9]{64}$"
)


class UUCDPersistenceError(RuntimeError):
    """Base error for canonical UUCD persistence."""


class UUCDPersistenceContractError(
    UUCDPersistenceError
):
    """Raised when the finalized UUCD input violates the contract."""


class UUCDPersistencePathError(
    UUCDPersistenceError
):
    """Raised when a UUCD persistence path is not canonical."""


class UUCDPersistenceConflictError(
    UUCDPersistenceError
):
    """Raised when different content already occupies content_ref."""


class UUCDPersistenceVerificationError(
    UUCDPersistenceError
):
    """Raised when persisted-record verification fails."""


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
        raise UUCDPersistenceContractError(
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
        raise UUCDPersistenceContractError(
            f"{field_name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise UUCDPersistenceContractError(
            f"{field_name} must not be empty."
        )

    return normalized


def _require_positive_int(
    value: Any,
    *,
    field_name: str,
) -> int:

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value <= 0
    ):
        raise UUCDPersistenceContractError(
            f"{field_name} must be a positive integer."
        )

    return value


def _require_workspace_id(
    value: Any,
) -> str:

    workspace_id = _require_non_empty_string(
        value,
        field_name="workspace_id",
    )

    if not WORKSPACE_ID_PATTERN.fullmatch(
        workspace_id
    ):
        raise UUCDPersistenceContractError(
            "workspace_id is invalid."
        )

    return workspace_id


def _require_document_id(
    value: Any,
) -> str:

    document_id = _require_non_empty_string(
        value,
        field_name="document_id",
    )

    if not DOCUMENT_ID_PATTERN.fullmatch(
        document_id
    ):
        raise UUCDPersistenceContractError(
            "document_id is not a canonical UUCD identifier."
        )

    return document_id


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
        raise UUCDPersistenceContractError(
            f"{field_name} must be a SHA-256 digest."
        )

    return digest


def _project_root(
    project_root: str | Path,
) -> Path:

    root = Path(
        project_root
    ).resolve()

    if not root.exists():
        raise UUCDPersistencePathError(
            "project_root does not exist."
        )

    if not root.is_dir():
        raise UUCDPersistencePathError(
            "project_root must be a directory."
        )

    return root


def _is_inside(
    child: Path,
    parent: Path,
) -> bool:

    try:
        child.relative_to(
            parent
        )
        return True

    except ValueError:
        return False


def canonical_uucd_content_ref_v1(
    *,
    workspace_id: str,
    document_id: str,
) -> str:
    """Return canonical project-relative per-document UUCD content_ref."""

    workspace = _require_workspace_id(
        workspace_id
    )

    document = _require_document_id(
        document_id
    )

    return (
        UUCD_STORE_ROOT_RELATIVE
        / workspace
        / "documents"
        / f"{document}.json"
    ).as_posix()


def _resolve_canonical_uucd_path(
    *,
    project_root: Path,
    workspace_id: str,
    document_id: str,
    supplied_content_ref: Any,
) -> Path:

    content_ref = _require_non_empty_string(
        supplied_content_ref,
        field_name="content_ref",
    )

    normalized_supplied = (
        content_ref.replace(
            "\\",
            "/",
        )
    )

    expected_ref = (
        canonical_uucd_content_ref_v1(
            workspace_id=workspace_id,
            document_id=document_id,
        )
    )

    if normalized_supplied != expected_ref:
        raise UUCDPersistencePathError(
            "content_ref does not match the canonical per-document UUCD path."
        )

    supplied = Path(
        normalized_supplied
    )

    if supplied.is_absolute():
        raise UUCDPersistencePathError(
            "content_ref must be project-relative."
        )

    store_root = (
        project_root
        / UUCD_STORE_ROOT_RELATIVE
    ).resolve()

    workspace_root = (
        store_root
        / workspace_id
        / "documents"
    ).resolve()

    target_path = (
        project_root
        / supplied
    ).resolve()

    if not _is_inside(
        workspace_root,
        store_root,
    ):
        raise UUCDPersistencePathError(
            "Workspace UUCD root escapes the canonical store."
        )

    if not _is_inside(
        target_path,
        workspace_root,
    ):
        raise UUCDPersistencePathError(
            "content_ref escapes the canonical workspace UUCD directory."
        )

    if target_path.parent != workspace_root:
        raise UUCDPersistencePathError(
            "UUCD JSON must be stored directly inside the workspace documents directory."
        )

    if target_path.suffix.casefold() != ".json":
        raise UUCDPersistencePathError(
            "Canonical UUCD files must use .json."
        )

    if target_path.name != f"{document_id}.json":
        raise UUCDPersistencePathError(
            "Canonical UUCD filename must match document_id."
        )

    return target_path


def _canonical_json_bytes(
    payload: Mapping[str, Any],
) -> bytes:

    try:
        text = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise UUCDPersistenceContractError(
            "UUCD Record is not JSON serializable."
        ) from exc

    return (
        text
        + "\n"
    ).encode(
        "utf-8"
    )


def _canonical_fingerprint(
    payload: Mapping[str, Any],
) -> str:

    compact = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        compact
    ).hexdigest()


def _validate_finalized_record(
    finalized_uucd_record: Mapping[str, Any],
) -> dict[str, Any]:

    record = deepcopy(
        dict(
            finalized_uucd_record
        )
    )

    missing = sorted(
        REQUIRED_UUCD_RECORD_FIELDS
        - set(
            record
        )
    )

    if missing:
        raise UUCDPersistenceContractError(
            "Finalized UUCD Record is missing required fields: "
            + ", ".join(
                missing
            )
        )

    if "content_body" in record:
        raise UUCDPersistenceContractError(
            "Finalized UUCD Record must not contain content_body."
        )

    if record.get(
        "schema_version"
    ) != UUCD_SCHEMA_VERSION:
        raise UUCDPersistenceContractError(
            "Finalized UUCD Record schema_version is invalid."
        )

    workspace_id = _require_workspace_id(
        record.get(
            "workspace_id"
        )
    )

    document_id = _require_document_id(
        record.get(
            "document_id"
        )
    )

    content_hash = _require_sha256(
        record.get(
            "content_hash"
        ),
        field_name="content_hash",
    )

    body_ref = _require_non_empty_string(
        record.get(
            "body_ref"
        ),
        field_name="body_ref",
    )

    content_ref = _require_non_empty_string(
        record.get(
            "content_ref"
        ),
        field_name="content_ref",
    )

    body_length = _require_positive_int(
        record.get(
            "body_length"
        ),
        field_name="body_length",
    )

    body_word_count = _require_positive_int(
        record.get(
            "body_word_count"
        ),
        field_name="body_word_count",
    )

    if record.get(
        "body_status"
    ) != "STORED_AND_VERIFIED":
        raise UUCDPersistenceContractError(
            "body_status must be STORED_AND_VERIFIED before UUCD persistence."
        )

    metadata = _require_mapping(
        record.get(
            "metadata"
        ),
        field_name="metadata",
    )

    if metadata.get(
        "body_store_write_verified"
    ) is not True:
        raise UUCDPersistenceContractError(
            "metadata.body_store_write_verified must be true."
        )

    if metadata.get(
        "persistence_status"
    ) != "READY_FOR_UUCD_PERSISTENCE":
        raise UUCDPersistenceContractError(
            "metadata.persistence_status must be READY_FOR_UUCD_PERSISTENCE."
        )

    handoff = _require_mapping(
        record.get(
            "handoff"
        ),
        field_name="handoff",
    )

    if handoff.get(
        "next_stage"
    ) != "uucd_persistence":
        raise UUCDPersistenceContractError(
            "handoff.next_stage must be uucd_persistence."
        )

    if handoff.get(
        "eligible_for_uucd_persistence"
    ) is not True:
        raise UUCDPersistenceContractError(
            "handoff.eligible_for_uucd_persistence must be true."
        )

    if handoff.get(
        "body_store_verified"
    ) is not True:
        raise UUCDPersistenceContractError(
            "handoff.body_store_verified must be true."
        )

    return {
        "record":
            record,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "content_hash":
            content_hash,

        "content_ref":
            content_ref,

        "body_ref":
            body_ref,

        "body_length":
            body_length,

        "body_word_count":
            body_word_count,

        "input_record_sha256":
            _canonical_fingerprint(
                record
            ),
    }


def _verify_body_prerequisite(
    *,
    project_root: Path,
    validated: Mapping[str, Any],
) -> dict[str, Any]:

    try:
        verification = verify_body(
            project_root=project_root,
            workspace_id=validated[
                "workspace_id"
            ],
            body_ref=validated[
                "body_ref"
            ],
            expected_content_hash=validated[
                "content_hash"
            ],
            expected_body_length=validated[
                "body_length"
            ],
            expected_body_word_count=validated[
                "body_word_count"
            ],
        )

    except Exception as exc:
        raise UUCDPersistenceVerificationError(
            "Body Store prerequisite verification failed."
        ) from exc

    if not isinstance(
        verification,
        Mapping,
    ):
        raise UUCDPersistenceVerificationError(
            "Body Store verification did not return a mapping."
        )

    if verification.get(
        "verification_status"
    ) != "VERIFIED":
        raise UUCDPersistenceVerificationError(
            "Body Store did not return VERIFIED."
        )

    if verification.get(
        "content_hash"
    ) != validated[
        "content_hash"
    ]:
        raise UUCDPersistenceVerificationError(
            "Verified body content_hash does not match the finalized UUCD Record."
        )

    if verification.get(
        "body_length"
    ) != validated[
        "body_length"
    ]:
        raise UUCDPersistenceVerificationError(
            "Verified body_length does not match the finalized UUCD Record."
        )

    if verification.get(
        "body_word_count"
    ) != validated[
        "body_word_count"
    ]:
        raise UUCDPersistenceVerificationError(
            "Verified body_word_count does not match the finalized UUCD Record."
        )

    return dict(
        verification
    )


def _build_persisted_record(
    *,
    validated: Mapping[str, Any],
    persisted_at: str,
) -> dict[str, Any]:

    record = deepcopy(
        validated[
            "record"
        ]
    )

    metadata = deepcopy(
        dict(
            record.get(
                "metadata"
            )
            or {}
        )
    )

    metadata[
        "persistence_status"
    ] = "PERSISTED_AND_VERIFIED"

    metadata[
        "uucd_persistence_version"
    ] = UUCD_PERSISTENCE_VERSION

    metadata[
        "uucd_persisted_at"
    ] = persisted_at

    record[
        "metadata"
    ] = metadata

    handoff = deepcopy(
        dict(
            record.get(
                "handoff"
            )
            or {}
        )
    )

    handoff.update(
        {
            "eligible_for_uucd_persistence":
                False,

            "uucd_persisted":
                True,

            "next_stage":
                "runtime_queue_handoff",
        }
    )

    record[
        "handoff"
    ] = handoff

    record[
        "persistence"
    ] = {
        "schema_version":
            UUCD_PERSISTENCE_SCHEMA_VERSION,

        "persistence_version":
            UUCD_PERSISTENCE_VERSION,

        "persistence_status":
            "PERSISTED_AND_VERIFIED",

        "storage_model":
            "PER_DOCUMENT_JSON",

        "input_record_sha256":
            validated[
                "input_record_sha256"
            ],

        "persisted_at":
            persisted_at,

        "content_body_stored_here":
            False,
    }

    return record


def _atomic_write(
    *,
    target_path: Path,
    payload: bytes,
) -> None:

    target_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(
                target_path.parent
            ),
            prefix=(
                "."
                + target_path.name
                + "."
            ),
            suffix=".tmp",
            delete=False,
        ) as handle:

            temporary_path = Path(
                handle.name
            )

            handle.write(
                payload
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_path,
            target_path,
        )

        temporary_path = None

    finally:
        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            temporary_path.unlink()


def _load_existing_record(
    target_path: Path,
) -> dict[str, Any]:

    if target_path.is_symlink():
        raise UUCDPersistenceConflictError(
            "Canonical UUCD target must not be a symbolic link."
        )

    if not target_path.is_file():
        raise UUCDPersistenceConflictError(
            "Canonical UUCD target exists but is not a regular file."
        )

    try:
        raw = target_path.read_bytes()

        decoded = raw.decode(
            "utf-8"
        )

        loaded = json.loads(
            decoded
        )

    except Exception as exc:
        raise UUCDPersistenceVerificationError(
            "Existing canonical UUCD JSON cannot be read safely."
        ) from exc

    if not isinstance(
        loaded,
        dict,
    ):
        raise UUCDPersistenceVerificationError(
            "Existing canonical UUCD JSON must contain an object."
        )

    return loaded


def _verify_persisted_record(
    *,
    target_path: Path,
    expected_record: Mapping[str, Any],
) -> dict[str, Any]:

    loaded = _load_existing_record(
        target_path
    )

    if loaded != dict(
        expected_record
    ):
        raise UUCDPersistenceVerificationError(
            "Persisted UUCD readback does not exactly match the expected record."
        )

    raw = target_path.read_bytes()

    return {
        "verification_status":
            "VERIFIED",

        "json_valid":
            True,

        "utf8_valid":
            True,

        "exact_record_match":
            True,

        "serialized_byte_length":
            len(
                raw
            ),

        "serialized_sha256":
            hashlib.sha256(
                raw
            ).hexdigest(),

        "content_body_present":
            "content_body" in loaded,
    }


def persist_finalized_uucd_v1(
    finalized_uucd_record: Mapping[str, Any],
    *,
    project_root: str | Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Persist one finalized UUCD Record to its canonical per-document JSON."""

    if not isinstance(
        finalized_uucd_record,
        Mapping,
    ):
        raise UUCDPersistenceContractError(
            "finalized_uucd_record must be a mapping."
        )

    if not isinstance(
        overwrite,
        bool,
    ):
        raise UUCDPersistenceContractError(
            "overwrite must be boolean."
        )

    root = _project_root(
        project_root
    )

    validated = _validate_finalized_record(
        finalized_uucd_record
    )

    target_path = _resolve_canonical_uucd_path(
        project_root=root,
        workspace_id=validated[
            "workspace_id"
        ],
        document_id=validated[
            "document_id"
        ],
        supplied_content_ref=validated[
            "content_ref"
        ],
    )

    body_verification = (
        _verify_body_prerequisite(
            project_root=root,
            validated=validated,
        )
    )

    action = "CREATED"
    persisted_record: dict[str, Any]

    previous_bytes: bytes | None = None

    if target_path.exists():

        existing = _load_existing_record(
            target_path
        )

        existing_persistence = (
            existing.get(
                "persistence"
            )
        )

        if isinstance(
            existing_persistence,
            Mapping,
        ) and (
            existing_persistence.get(
                "input_record_sha256"
            )
            == validated[
                "input_record_sha256"
            ]
        ):
            persisted_record = existing
            action = "EXISTING_IDENTICAL_REUSED"

        elif not overwrite:
            raise UUCDPersistenceConflictError(
                "A different canonical UUCD Record already exists for this document_id."
            )

        else:
            previous_bytes = (
                target_path.read_bytes()
            )

            persisted_record = (
                _build_persisted_record(
                    validated=validated,
                    persisted_at=_utc_now_iso(),
                )
            )

            action = "OVERWRITTEN"

    else:
        persisted_record = (
            _build_persisted_record(
                validated=validated,
                persisted_at=_utc_now_iso(),
            )
        )

    if action != "EXISTING_IDENTICAL_REUSED":

        serialized = _canonical_json_bytes(
            persisted_record
        )

        try:
            _atomic_write(
                target_path=target_path,
                payload=serialized,
            )

            persistence_verification = (
                _verify_persisted_record(
                    target_path=target_path,
                    expected_record=persisted_record,
                )
            )

        except Exception:

            if action == "OVERWRITTEN":

                if previous_bytes is not None:
                    _atomic_write(
                        target_path=target_path,
                        payload=previous_bytes,
                    )

            elif action == "CREATED":

                if target_path.exists():
                    target_path.unlink()

            raise

    else:
        persistence_verification = (
            _verify_persisted_record(
                target_path=target_path,
                expected_record=persisted_record,
            )
        )

    if persistence_verification.get(
        "content_body_present"
    ):
        raise UUCDPersistenceVerificationError(
            "Persisted UUCD unexpectedly contains content_body."
        )

    certificate = {
        "certificate_schema_version":
            UUCD_PERSISTENCE_CERTIFICATE_SCHEMA_VERSION,

        "persistence_version":
            UUCD_PERSISTENCE_VERSION,

        "certificate_status":
            "CERTIFIED",

        "workspace_id":
            validated[
                "workspace_id"
            ],

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

        "content_hash":
            validated[
                "content_hash"
            ],

        "body_length":
            validated[
                "body_length"
            ],

        "body_word_count":
            validated[
                "body_word_count"
            ],

        "body_verification":
            body_verification,

        "persistence_verification":
            persistence_verification,

        "persistence_action":
            action,

        "uucd_record_persisted":
            True,

        "content_body_persisted_in_uucd":
            False,

        "runtime_executed":
            False,

        "queue_job_created":
            False,

        "semantic_processing_performed":
            False,

        "certified_at":
            _utc_now_iso(),
    }

    return {
        "persistence_status":
            "PERSISTED_AND_VERIFIED",

        "persistence_action":
            action,

        "uucd_path":
            str(
                target_path
            ),

        "persisted_uucd_record":
            persisted_record,

        "persistence_certificate":
            certificate,

        "next_stage":
            "runtime_queue_handoff",
    }


def explain_uucd_persistence_v1() -> dict[str, Any]:
    """Return the canonical Stage 9 persistence contract."""

    return {
        "component":
            "Canonical UUCD Persistence",

        "version":
            UUCD_PERSISTENCE_VERSION,

        "input":
            "finalized_uucd_record",

        "required_schema":
            UUCD_SCHEMA_VERSION,

        "required_body_status":
            "STORED_AND_VERIFIED",

        "required_input_persistence_status":
            "READY_FOR_UUCD_PERSISTENCE",

        "independent_body_store_verification":
            True,

        "storage_model":
            "PER_DOCUMENT_JSON",

        "canonical_root":
            UUCD_STORE_ROOT_RELATIVE.as_posix(),

        "content_body_allowed":
            False,

        "atomic_write":
            True,

        "idempotent_identical_reuse":
            True,

        "conflict_rejection":
            True,

        "post_write_readback_verification":
            True,

        "runtime_executed":
            False,

        "queue_job_created":
            False,

        "semantic_processing":
            False,

        "next_stage":
            "runtime_queue_handoff",
    }
