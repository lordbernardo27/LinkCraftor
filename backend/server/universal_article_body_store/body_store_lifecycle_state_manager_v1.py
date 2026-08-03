"""Universal Article Body Store Lifecycle State Manager.

Phase 9.1.1 responsibility:

- define canonical lifecycle states;
- create immutable initial lifecycle-state records;
- validate lifecycle-state records;
- read lifecycle-state records;
- list lifecycle-state records by workspace;
- preserve references to stored article bodies without duplicating content.

This module does not:

- transition an existing record between states;
- archive, restore, delete, quarantine, or supersede bodies;
- read or write article content;
- call the Body Store Writer, Manager, Repository, Runtime, Worker, or Queue;
- register runtime handlers;
- modify the persistent Universal Article Body Store.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


BODY_STORE_LIFECYCLE_STATE_MANAGER_VERSION = (
    "universal_article_body_store_lifecycle_state_manager_v1"
)

BODY_STORE_LIFECYCLE_RECORD_SCHEMA_VERSION = (
    "body_store_lifecycle_state_record_v1"
)

BODY_STORE_LIFECYCLE_STATES = (
    "ACTIVE",
    "SUPERSEDED",
    "RETAINED",
    "ARCHIVED",
    "QUARANTINED",
    "PENDING_DELETION",
    "DELETED",
    "RESTORED",
)

INITIAL_BODY_STORE_LIFECYCLE_STATES = (
    "ACTIVE",
    "QUARANTINED",
    "RETAINED",
)

_FORBIDDEN_BODY_FIELDS = {
    "content_body",
    "article_body",
    "body_payload",
    "raw_body",
    "full_text",
}

_SAFE_SEGMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,199}$"
)


class BodyStoreLifecycleStateError(
    ValueError
):
    """Base error for invalid lifecycle-state operations."""


class BodyStoreLifecycleStateConflictError(
    BodyStoreLifecycleStateError
):
    """Raised when an immutable lifecycle record already exists."""


class BodyStoreLifecycleStateNotFoundError(
    FileNotFoundError
):
    """Raised when a lifecycle-state record cannot be found."""


def _now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreLifecycleStateError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreLifecycleStateError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_safe_segment(
    value: Any,
    *,
    field_name: str,
) -> str:
    normalized = _require_string(
        value,
        field_name=field_name,
    )

    if not _SAFE_SEGMENT_PATTERN.fullmatch(
        normalized
    ):
        raise BodyStoreLifecycleStateError(
            field_name
            + " contains unsupported path characters."
        )

    return normalized


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreLifecycleStateError(
            field_name
            + " must be a mapping."
        )

    return value


def _contains_forbidden_body_content(
    value: Any,
) -> bool:
    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            if str(
                key
            ).casefold() in _FORBIDDEN_BODY_FIELDS:
                return True

            if _contains_forbidden_body_content(
                item
            ):
                return True

        return False

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return any(
            _contains_forbidden_body_content(
                item
            )
            for item in value
        )

    return False


def _normalize_content_hash(
    value: Any,
) -> str:
    normalized = _require_string(
        value,
        field_name="content_hash",
    ).casefold()

    if not re.fullmatch(
        r"[0-9a-f]{64}",
        normalized,
    ):
        raise BodyStoreLifecycleStateError(
            "content_hash must be a 64-character SHA-256 hexadecimal value."
        )

    return normalized


def _normalize_initial_state(
    value: Any,
) -> str:
    normalized = _require_string(
        value,
        field_name="lifecycle_state",
    ).upper()

    if normalized not in BODY_STORE_LIFECYCLE_STATES:
        raise BodyStoreLifecycleStateError(
            "Unsupported lifecycle state: "
            + normalized
        )

    if normalized not in INITIAL_BODY_STORE_LIFECYCLE_STATES:
        raise BodyStoreLifecycleStateError(
            "Phase 9.1.1 may create only initial states: "
            + ", ".join(
                INITIAL_BODY_STORE_LIFECYCLE_STATES
            )
            + ". State changes require the Phase 9.1.2 "
            "State Transition Engine."
        )

    return normalized


def _lifecycle_root(
    *,
    project_root: str | Path,
) -> Path:
    return (
        Path(
            project_root
        ).resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
        / "states"
    )


def _workspace_root(
    *,
    project_root: str | Path,
    workspace_id: str,
) -> Path:
    return (
        _lifecycle_root(
            project_root=project_root
        )
        / workspace_id
    )


def build_body_store_lifecycle_record_id_v1(
    *,
    workspace_id: str,
    document_id: str,
    body_ref: str,
    content_hash: str,
) -> str:
    """Build a stable lifecycle identity from immutable body references."""

    normalized_workspace = _require_safe_segment(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_document = _require_safe_segment(
        document_id,
        field_name="document_id",
    )

    normalized_body_ref = _require_string(
        body_ref,
        field_name="body_ref",
    )

    normalized_hash = _normalize_content_hash(
        content_hash
    )

    identity_material = "\n".join(
        (
            normalized_workspace,
            normalized_document,
            normalized_body_ref,
            normalized_hash,
        )
    )

    return (
        "body_lifecycle_"
        + hashlib.sha256(
            identity_material.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def _record_path(
    *,
    project_root: str | Path,
    workspace_id: str,
    lifecycle_record_id: str,
) -> Path:
    normalized_workspace = _require_safe_segment(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_record_id = _require_safe_segment(
        lifecycle_record_id,
        field_name="lifecycle_record_id",
    )

    return (
        _workspace_root(
            project_root=project_root,
            workspace_id=normalized_workspace,
        )
        / (
            normalized_record_id
            + ".json"
        )
    )


def _write_json_atomic(
    path: Path,
    record: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.parent / (
        ".lc_"
        + hashlib.sha256(
            (
                str(
                    path
                )
                + _now_iso()
            ).encode(
                "utf-8"
            )
        ).hexdigest()[
            :12
        ]
        + ".tmp"
    )

    try:
        temporary_path.write_text(
            json.dumps(
                dict(
                    record
                ),
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        os.replace(
            temporary_path,
            path,
        )

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def validate_body_store_lifecycle_record_v1(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and normalize one lifecycle-state record."""

    mapping = dict(
        _require_mapping(
            record,
            field_name="record",
        )
    )

    if _contains_forbidden_body_content(
        mapping
    ):
        raise BodyStoreLifecycleStateError(
            "Lifecycle records must not contain article body content."
        )

    schema_version = _require_string(
        mapping.get(
            "schema_version"
        ),
        field_name="schema_version",
    )

    if (
        schema_version
        != BODY_STORE_LIFECYCLE_RECORD_SCHEMA_VERSION
    ):
        raise BodyStoreLifecycleStateError(
            "Unsupported lifecycle record schema version."
        )

    manager_version = _require_string(
        mapping.get(
            "manager_version"
        ),
        field_name="manager_version",
    )

    if (
        manager_version
        != BODY_STORE_LIFECYCLE_STATE_MANAGER_VERSION
    ):
        raise BodyStoreLifecycleStateError(
            "Unsupported Lifecycle State Manager version."
        )

    workspace_id = _require_safe_segment(
        mapping.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    document_id = _require_safe_segment(
        mapping.get(
            "document_id"
        ),
        field_name="document_id",
    )

    body_ref = _require_string(
        mapping.get(
            "body_ref"
        ),
        field_name="body_ref",
    )

    content_hash = _normalize_content_hash(
        mapping.get(
            "content_hash"
        )
    )

    lifecycle_record_id = _require_safe_segment(
        mapping.get(
            "lifecycle_record_id"
        ),
        field_name="lifecycle_record_id",
    )

    expected_record_id = (
        build_body_store_lifecycle_record_id_v1(
            workspace_id=workspace_id,
            document_id=document_id,
            body_ref=body_ref,
            content_hash=content_hash,
        )
    )

    if lifecycle_record_id != expected_record_id:
        raise BodyStoreLifecycleStateError(
            "lifecycle_record_id does not match the canonical body identity."
        )

    lifecycle_state = _require_string(
        mapping.get(
            "lifecycle_state"
        ),
        field_name="lifecycle_state",
    ).upper()

    if lifecycle_state not in BODY_STORE_LIFECYCLE_STATES:
        raise BodyStoreLifecycleStateError(
            "Unsupported lifecycle state: "
            + lifecycle_state
        )

    state_reason = _require_string(
        mapping.get(
            "state_reason"
        ),
        field_name="state_reason",
    )

    actor_type = _require_string(
        mapping.get(
            "actor_type"
        ),
        field_name="actor_type",
    )

    actor_id = _require_string(
        mapping.get(
            "actor_id"
        ),
        field_name="actor_id",
    )

    source = _require_string(
        mapping.get(
            "source"
        ),
        field_name="source",
    )

    created_at = _require_string(
        mapping.get(
            "created_at"
        ),
        field_name="created_at",
    )

    try:
        parsed_created_at = datetime.fromisoformat(
            created_at
        )

    except ValueError as exc:
        raise BodyStoreLifecycleStateError(
            "created_at must be a valid ISO-8601 timestamp."
        ) from exc

    if parsed_created_at.tzinfo is None:
        raise BodyStoreLifecycleStateError(
            "created_at must include timezone information."
        )

    metadata = dict(
        _require_mapping(
            mapping.get(
                "metadata",
                {},
            ),
            field_name="metadata",
        )
    )

    if _contains_forbidden_body_content(
        metadata
    ):
        raise BodyStoreLifecycleStateError(
            "Lifecycle metadata must not contain article body content."
        )

    previous_state_value = mapping.get(
        "previous_state"
    )

    previous_state = None

    if previous_state_value is not None:
        previous_state = _require_string(
            previous_state_value,
            field_name="previous_state",
        ).upper()

        if previous_state not in BODY_STORE_LIFECYCLE_STATES:
            raise BodyStoreLifecycleStateError(
                "Unsupported previous lifecycle state: "
                + previous_state
            )

    transition_count = mapping.get(
        "transition_count",
        0,
    )

    if (
        not isinstance(
            transition_count,
            int,
        )
        or isinstance(
            transition_count,
            bool,
        )
        or transition_count < 0
    ):
        raise BodyStoreLifecycleStateError(
            "transition_count must be a non-negative integer."
        )

    updated_at_value = mapping.get(
        "updated_at"
    )

    updated_at = None

    if updated_at_value is not None:
        updated_at = _require_string(
            updated_at_value,
            field_name="updated_at",
        )

        try:
            parsed_updated_at = datetime.fromisoformat(
                updated_at
            )

        except ValueError as exc:
            raise BodyStoreLifecycleStateError(
                "updated_at must be a valid ISO-8601 timestamp."
            ) from exc

        if parsed_updated_at.tzinfo is None:
            raise BodyStoreLifecycleStateError(
                "updated_at must include timezone information."
            )

    last_transition = dict(
        _require_mapping(
            mapping.get(
                "last_transition",
                {},
            ),
            field_name="last_transition",
        )
    )

    if _contains_forbidden_body_content(
        last_transition
    ):
        raise BodyStoreLifecycleStateError(
            "Transition metadata must not contain article body content."
        )

    if transition_count == 0:
        if previous_state is not None:
            raise BodyStoreLifecycleStateError(
                "Initial lifecycle records must not define previous_state."
            )

        if updated_at is not None:
            raise BodyStoreLifecycleStateError(
                "Initial lifecycle records must not define updated_at."
            )

        if last_transition:
            raise BodyStoreLifecycleStateError(
                "Initial lifecycle records must not define last_transition."
            )

    else:
        if previous_state is None:
            raise BodyStoreLifecycleStateError(
                "Transitioned lifecycle records require previous_state."
            )

        if updated_at is None:
            raise BodyStoreLifecycleStateError(
                "Transitioned lifecycle records require updated_at."
            )

        if not last_transition:
            raise BodyStoreLifecycleStateError(
                "Transitioned lifecycle records require last_transition."
            )

    return {
        "schema_version":
            schema_version,

        "manager_version":
            manager_version,

        "lifecycle_record_id":
            lifecycle_record_id,

        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "body_ref":
            body_ref,

        "content_hash":
            content_hash,

        "lifecycle_state":
            lifecycle_state,

        "state_reason":
            state_reason,

        "actor_type":
            actor_type,

        "actor_id":
            actor_id,

        "source":
            source,

        "created_at":
            created_at,

        "updated_at":
            updated_at,

        "previous_state":
            previous_state,

        "metadata":
            metadata,

        "last_transition":
            last_transition,

        "content_body_included":
            False,

        "transition_count":
            transition_count,
    }


def create_body_store_lifecycle_state_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    document_id: str,
    body_ref: str,
    content_hash: str,
    lifecycle_state: str = "ACTIVE",
    state_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one immutable initial lifecycle-state record."""

    normalized_workspace = _require_safe_segment(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_document = _require_safe_segment(
        document_id,
        field_name="document_id",
    )

    normalized_body_ref = _require_string(
        body_ref,
        field_name="body_ref",
    )

    normalized_hash = _normalize_content_hash(
        content_hash
    )

    normalized_state = _normalize_initial_state(
        lifecycle_state
    )

    normalized_metadata = (
        {}
        if metadata is None
        else dict(
            _require_mapping(
                metadata,
                field_name="metadata",
            )
        )
    )

    if _contains_forbidden_body_content(
        normalized_metadata
    ):
        raise BodyStoreLifecycleStateError(
            "Lifecycle metadata must not contain article body content."
        )

    lifecycle_record_id = (
        build_body_store_lifecycle_record_id_v1(
            workspace_id=normalized_workspace,
            document_id=normalized_document,
            body_ref=normalized_body_ref,
            content_hash=normalized_hash,
        )
    )

    path = _record_path(
        project_root=project_root,
        workspace_id=normalized_workspace,
        lifecycle_record_id=lifecycle_record_id,
    )

    if path.exists():
        raise BodyStoreLifecycleStateConflictError(
            "Lifecycle-state record already exists: "
            + lifecycle_record_id
        )

    record = validate_body_store_lifecycle_record_v1(
        {
            "schema_version":
                BODY_STORE_LIFECYCLE_RECORD_SCHEMA_VERSION,

            "manager_version":
                BODY_STORE_LIFECYCLE_STATE_MANAGER_VERSION,

            "lifecycle_record_id":
                lifecycle_record_id,

            "workspace_id":
                normalized_workspace,

            "document_id":
                normalized_document,

            "body_ref":
                normalized_body_ref,

            "content_hash":
                normalized_hash,

            "lifecycle_state":
                normalized_state,

            "state_reason":
                state_reason,

            "actor_type":
                actor_type,

            "actor_id":
                actor_id,

            "source":
                source,

            "created_at":
                _now_iso(),

            "metadata":
                normalized_metadata,
        }
    )

    _write_json_atomic(
        path,
        record,
    )

    return record


def read_body_store_lifecycle_state_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    lifecycle_record_id: str,
) -> dict[str, Any]:
    """Read and validate one lifecycle-state record."""

    path = _record_path(
        project_root=project_root,
        workspace_id=workspace_id,
        lifecycle_record_id=lifecycle_record_id,
    )

    if not path.is_file():
        raise BodyStoreLifecycleStateNotFoundError(
            "Lifecycle-state record not found: "
            + lifecycle_record_id
        )

    value = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    return validate_body_store_lifecycle_record_v1(
        _require_mapping(
            value,
            field_name="stored lifecycle record",
        )
    )


def list_body_store_lifecycle_states_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    lifecycle_state: str | None = None,
) -> list[dict[str, Any]]:
    """List validated lifecycle-state records for one workspace."""

    normalized_workspace = _require_safe_segment(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_filter = None

    if lifecycle_state is not None:
        normalized_filter = _require_string(
            lifecycle_state,
            field_name="lifecycle_state",
        ).upper()

        if normalized_filter not in BODY_STORE_LIFECYCLE_STATES:
            raise BodyStoreLifecycleStateError(
                "Unsupported lifecycle-state filter: "
                + normalized_filter
            )

    workspace_root = _workspace_root(
        project_root=project_root,
        workspace_id=normalized_workspace,
    )

    if not workspace_root.is_dir():
        return []

    records = []

    for path in sorted(
        workspace_root.glob(
            "*.json"
        )
    ):
        value = json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

        record = validate_body_store_lifecycle_record_v1(
            _require_mapping(
                value,
                field_name="stored lifecycle record",
            )
        )

        if (
            normalized_filter is not None
            and record[
                "lifecycle_state"
            ]
            != normalized_filter
        ):
            continue

        records.append(
            record
        )

    records.sort(
        key=lambda item: (
            item[
                "created_at"
            ],
            item[
                "lifecycle_record_id"
            ],
        )
    )

    return records


