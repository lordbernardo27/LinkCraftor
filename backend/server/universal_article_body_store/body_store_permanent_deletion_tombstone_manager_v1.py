from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_contract_v1 import (
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION,
    certify_permanent_deletion_tombstone_contract_v1,
    validate_permanent_deletion_tombstone_contract_v1,
)


BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA = (
    "body_store_permanent_deletion_tombstone_manager.v1"
)

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STORE_NAME = (
    "universal_article_body_store_tombstones"
)

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA = (
    "body_store_permanent_deletion_tombstone_index.v1"
)


class PermanentDeletionTombstoneManagerError(
    ValueError
):
    """Raised when tombstone persistence cannot proceed safely."""


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        MappingProxyType,
    ):
        return value

    if isinstance(
        value,
        dict,
    ):
        return MappingProxyType(
            {
                key:
                    _freeze(
                        item
                    )

                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise PermanentDeletionTombstoneManagerError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionTombstoneManagerError(
            field_name
            + " must not be empty."
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
        raise PermanentDeletionTombstoneManagerError(
            field_name
            + " must be a mapping."
        )

    return value


def _json_ready(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(
                key
            ):
                _json_ready(
                    item
                )

            for key, item
            in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):
        return [
            _json_ready(
                item
            )

            for item
            in value
        ]

    if isinstance(
        value,
        list,
    ):
        return [
            _json_ready(
                item
            )

            for item
            in value
        ]

    return value


def calculate_tombstone_repository_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        _json_ready(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def resolve_tombstone_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STORE_NAME
    ).resolve()


def resolve_tombstone_workspace_root_v1(
    *,
    project_root: Path,
    workspace_id: str,
) -> Path:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    store_root = (
        resolve_tombstone_store_root_v1(
            project_root=project_root,
        )
    )

    workspace_root = (
        store_root
        / normalized_workspace_id
    ).resolve()

    try:
        workspace_root.relative_to(
            store_root
        )

    except ValueError as exc:
        raise PermanentDeletionTombstoneManagerError(
            "Workspace tombstone path escaped the managed store."
        ) from exc

    return workspace_root
def resolve_tombstone_record_path_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Path:

    normalized_tombstone_id = _require_string(
        tombstone_id,
        field_name="tombstone_id",
    )

    workspace_root = (
        resolve_tombstone_workspace_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    records_root = (
        workspace_root
        / "records"
    ).resolve()

    record_path = (
        records_root
        / (
            normalized_tombstone_id
            + ".json"
        )
    ).resolve()

    try:
        record_path.relative_to(
            records_root
        )

    except ValueError as exc:
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone record path escaped the managed records directory."
        ) from exc

    return record_path


def resolve_tombstone_index_path_v1(
    *,
    project_root: Path,
    workspace_id: str,
) -> Path:

    workspace_root = (
        resolve_tombstone_workspace_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    return (
        workspace_root
        / "index.json"
    ).resolve()


def build_tombstone_index_entry_v1(
    *,
    tombstone_contract: Mapping[str, Any],
    tombstone_record_path: Path,
    tombstone_record_checksum: str,
) -> Mapping[str, Any]:

    contract = _require_mapping(
        tombstone_contract,
        field_name="tombstone_contract",
    )

    if not isinstance(
        tombstone_record_path,
        Path,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "tombstone_record_path must be a Path."
        )

    normalized_record_checksum = _require_string(
        tombstone_record_checksum,
        field_name="tombstone_record_checksum",
    )

    entry = {
        "tombstone_id":
            contract[
                "tombstone_id"
            ],

        "body_id":
            contract[
                "body_id"
            ],

        "workspace_id":
            contract[
                "workspace_id"
            ],

        "archive_id":
            contract[
                "archive_id"
            ],

        "lifecycle_record_id":
            contract[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            contract[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            contract[
                "deletion_execution_id"
            ],

        "status":
            contract[
                "status"
            ],

        "contract_checksum":
            contract[
                "checksum"
            ],

        "record_checksum":
            normalized_record_checksum,

        "record_path":
            tombstone_record_path.as_posix(),

        "created_at":
            contract[
                "created_at"
            ],

        "contains_article_body":
            False,
    }

    return _freeze(
        entry
    )


def load_tombstone_index_v1(
    *,
    index_path: Path,
    workspace_id: str,
) -> dict[str, Any]:

    if not isinstance(
        index_path,
        Path,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "index_path must be a Path."
        )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    if not index_path.is_file():
        return {
            "schema":
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA,

            "manager_version":
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,

            "workspace_id":
                normalized_workspace_id,

            "tombstone_count":
                0,

            "tombstones":
                [],
        }

    payload = json.loads(
        index_path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone index must contain a JSON object."
        )

    if (
        payload.get(
            "schema"
        )
        != BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA
    ):
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone index schema is invalid."
        )

    if (
        payload.get(
            "workspace_id"
        )
        != normalized_workspace_id
    ):
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone index workspace identity does not match."
        )

    tombstones = payload.get(
        "tombstones"
    )

    if not isinstance(
        tombstones,
        list,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone index tombstones must be a list."
        )

    return payload
def persist_tombstone_contract_v1(
    *,
    project_root: Path,
    tombstone_contract: Mapping[str, Any],
) -> Mapping[str, Any]:

    contract = _require_mapping(
        tombstone_contract,
        field_name="tombstone_contract",
    )

    validation = (
        validate_permanent_deletion_tombstone_contract_v1(
            tombstone_contract=contract,
        )
    )

    if validation[
        "contract_valid"
    ] is not True:
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone contract validation failed."
        )

    certification = (
        certify_permanent_deletion_tombstone_contract_v1(
            tombstone_contract=contract,
        )
    )

    if certification[
        "certified"
    ] is not True:
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone contract certification failed."
        )

    workspace_id = _require_string(
        contract[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    tombstone_id = _require_string(
        contract[
            "tombstone_id"
        ],
        field_name="tombstone_id",
    )

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            tombstone_id=tombstone_id,
        )
    )

    index_path = (
        resolve_tombstone_index_path_v1(
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    if record_path.exists():
        existing_payload = json.loads(
            record_path.read_text(
                encoding="utf-8-sig",
            )
        )

        if not isinstance(
            existing_payload,
            dict,
        ):
            raise PermanentDeletionTombstoneManagerError(
                "Existing tombstone record is invalid."
            )

        if (
            existing_payload.get(
                "checksum"
            )
            != contract[
                "checksum"
            ]
        ):
            raise PermanentDeletionTombstoneManagerError(
                "A different tombstone already exists for this tombstone_id."
            )

        raise PermanentDeletionTombstoneManagerError(
            "Tombstone record already exists and is immutable."
        )

    record_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    index_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    record_payload = _json_ready(
        contract
    )

    forbidden_fields = {
        "content",
        "article_body",
        "body_text",
        "content_body",
        "raw_html",
        "html",
    }

    exposed_fields = sorted(
        field_name
        for field_name in forbidden_fields
        if field_name in record_payload
    )

    if exposed_fields:
        raise PermanentDeletionTombstoneManagerError(
            "Tombstone record contains forbidden article-content fields: "
            + ", ".join(
                exposed_fields
            )
        )

    record_checksum = (
        calculate_tombstone_repository_checksum_v1(
            payload=record_payload,
        )
    )

    record_path.write_text(
        json.dumps(
            record_payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    index_payload = (
        load_tombstone_index_v1(
            index_path=index_path,
            workspace_id=workspace_id,
        )
    )

    existing_entries = index_payload[
        "tombstones"
    ]

    duplicate_body_entry = next(
        (
            entry
            for entry in existing_entries
            if (
                isinstance(
                    entry,
                    dict,
                )
                and entry.get(
                    "body_id"
                )
                == contract[
                    "body_id"
                ]
            )
        ),
        None,
    )

    if duplicate_body_entry is not None:
        record_path.unlink(
            missing_ok=True,
        )

        raise PermanentDeletionTombstoneManagerError(
            "A tombstone already exists for this body_id."
        )

    index_entry = (
        build_tombstone_index_entry_v1(
            tombstone_contract=contract,
            tombstone_record_path=record_path,
            tombstone_record_checksum=record_checksum,
        )
    )

    updated_entries = [
        *existing_entries,
        _json_ready(
            index_entry
        ),
    ]

    updated_entries.sort(
        key=lambda entry: (
            str(
                entry.get(
                    "created_at",
                    "",
                )
            ),
            str(
                entry.get(
                    "tombstone_id",
                    "",
                )
            ),
        )
    )

    updated_index = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,

        "workspace_id":
            workspace_id,

        "tombstone_count":
            len(
                updated_entries
            ),

        "tombstones":
            updated_entries,
    }

    index_path.write_text(
        json.dumps(
            updated_index,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,

        "tombstone_id":
            tombstone_id,

        "body_id":
            contract[
                "body_id"
            ],

        "workspace_id":
            workspace_id,

        "record_path":
            record_path.as_posix(),

        "index_path":
            index_path.as_posix(),

        "contract_checksum":
            contract[
                "checksum"
            ],

        "record_checksum":
            record_checksum,

        "tombstone_persisted":
            record_path.is_file(),

        "index_updated":
            index_path.is_file(),

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )
def load_persisted_tombstone_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            tombstone_id=tombstone_id,
        )
    )

    if not record_path.is_file():
        raise PermanentDeletionTombstoneManagerError(
            "Persisted tombstone record was not found."
        )

    payload = json.loads(
        record_path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise PermanentDeletionTombstoneManagerError(
            "Persisted tombstone record must contain a JSON object."
        )

    validation = (
        validate_permanent_deletion_tombstone_contract_v1(
            tombstone_contract=payload,
        )
    )

    if validation[
        "contract_valid"
    ] is not True:
        raise PermanentDeletionTombstoneManagerError(
            "Persisted tombstone record failed contract validation."
        )

    return _freeze(
        payload
    )


def verify_persisted_tombstone_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            tombstone_id=tombstone_id,
        )
    )

    index_path = (
        resolve_tombstone_index_path_v1(
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    tombstone = (
        load_persisted_tombstone_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            tombstone_id=tombstone_id,
        )
    )

    index_payload = (
        load_tombstone_index_v1(
            index_path=index_path,
            workspace_id=workspace_id,
        )
    )

    matching_entry = next(
        (
            entry
            for entry in index_payload[
                "tombstones"
            ]
            if (
                isinstance(
                    entry,
                    dict,
                )
                and entry.get(
                    "tombstone_id"
                )
                == tombstone_id
            )
        ),
        None,
    )

    record_checksum = (
        calculate_tombstone_repository_checksum_v1(
            payload=tombstone,
        )
    )

    index_entry_present = (
        matching_entry
        is not None
    )

    contract_checksum_matches = (
        index_entry_present
        and matching_entry.get(
            "contract_checksum"
        )
        == tombstone[
            "checksum"
        ]
    )

    record_checksum_matches = (
        index_entry_present
        and matching_entry.get(
            "record_checksum"
        )
        == record_checksum
    )

    record_path_matches = (
        index_entry_present
        and matching_entry.get(
            "record_path"
        )
        == record_path.as_posix()
    )

    workspace_matches = (
        tombstone[
            "workspace_id"
        ]
        == workspace_id
        and (
            not index_entry_present
            or matching_entry.get(
                "workspace_id"
            )
            == workspace_id
        )
    )

    body_id_matches = (
        index_entry_present
        and matching_entry.get(
            "body_id"
        )
        == tombstone[
            "body_id"
        ]
    )

    contains_article_body = any(
        field_name
        in tombstone
        for field_name in {
            "content",
            "article_body",
            "body_text",
            "content_body",
            "raw_html",
            "html",
        }
    )

    result = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,

        "tombstone_id":
            tombstone_id,

        "workspace_id":
            workspace_id,

        "body_id":
            tombstone[
                "body_id"
            ],

        "record_path":
            record_path.as_posix(),

        "index_path":
            index_path.as_posix(),

        "record_present":
            record_path.is_file(),

        "index_present":
            index_path.is_file(),

        "index_entry_present":
            index_entry_present,

        "contract_checksum_matches":
            contract_checksum_matches,

        "record_checksum_matches":
            record_checksum_matches,

        "record_path_matches":
            record_path_matches,

        "workspace_matches":
            workspace_matches,

        "body_id_matches":
            body_id_matches,

        "article_body_exposed":
            contains_article_body,

        "tombstone_verified":
            all(
                (
                    record_path.is_file(),
                    index_path.is_file(),
                    index_entry_present,
                    contract_checksum_matches,
                    record_checksum_matches,
                    record_path_matches,
                    workspace_matches,
                    body_id_matches,
                    contains_article_body
                    is False,
                )
            ),

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )
def build_permanent_deletion_tombstone_manager_bundle_v1(
    *,
    project_root: Path,
    tombstone_contract: Mapping[str, Any],
) -> Mapping[str, Any]:

    contract = _require_mapping(
        tombstone_contract,
        field_name="tombstone_contract",
    )

    persistence_result = (
        persist_tombstone_contract_v1(
            project_root=project_root,
            tombstone_contract=contract,
        )
    )

    verification_result = (
        verify_persisted_tombstone_v1(
            project_root=project_root,
            workspace_id=contract[
                "workspace_id"
            ],
            tombstone_id=contract[
                "tombstone_id"
            ],
        )
    )

    if verification_result[
        "tombstone_verified"
    ] is not True:
        raise PermanentDeletionTombstoneManagerError(
            "Persisted tombstone verification failed."
        )

    bundle = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,

        "tombstone_contract":
            contract,

        "persistence_result":
            persistence_result,

        "verification_result":
            verification_result,

        "tombstone_id":
            contract[
                "tombstone_id"
            ],

        "body_id":
            contract[
                "body_id"
            ],

        "workspace_id":
            contract[
                "workspace_id"
            ],

        "archive_id":
            contract[
                "archive_id"
            ],

        "lifecycle_record_id":
            contract[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            contract[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            contract[
                "deletion_execution_id"
            ],

        "tombstone_persisted":
            persistence_result[
                "tombstone_persisted"
            ]
            is True,

        "index_updated":
            persistence_result[
                "index_updated"
            ]
            is True,

        "tombstone_verified":
            verification_result[
                "tombstone_verified"
            ]
            is True,

        "bundle_complete":
            all(
                (
                    persistence_result[
                        "tombstone_persisted"
                    ]
                    is True,
                    persistence_result[
                        "index_updated"
                    ]
                    is True,
                    verification_result[
                        "tombstone_verified"
                    ]
                    is True,
                )
            ),

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        bundle
    )


def verify_permanent_deletion_tombstone_manager_bundle_v1(
    *,
    manager_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle = _require_mapping(
        manager_bundle,
        field_name="manager_bundle",
    )

    required_sections = (
        "tombstone_contract",
        "persistence_result",
        "verification_result",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in bundle
    )

    contract = bundle.get(
        "tombstone_contract",
        {},
    )

    persistence_result = bundle.get(
        "persistence_result",
        {},
    )

    verification_result = bundle.get(
        "verification_result",
        {},
    )

    tombstone_id_matches = (
        contract.get(
            "tombstone_id"
        )
        == persistence_result.get(
            "tombstone_id"
        )
        == verification_result.get(
            "tombstone_id"
        )
        == bundle.get(
            "tombstone_id"
        )
    )

    body_id_matches = (
        contract.get(
            "body_id"
        )
        == persistence_result.get(
            "body_id"
        )
        == verification_result.get(
            "body_id"
        )
        == bundle.get(
            "body_id"
        )
    )

    workspace_id_matches = (
        contract.get(
            "workspace_id"
        )
        == persistence_result.get(
            "workspace_id"
        )
        == verification_result.get(
            "workspace_id"
        )
        == bundle.get(
            "workspace_id"
        )
    )

    persistence_confirmed = (
        persistence_result.get(
            "tombstone_persisted"
        )
        is True
        and persistence_result.get(
            "index_updated"
        )
        is True
    )

    verification_confirmed = (
        verification_result.get(
            "tombstone_verified"
        )
        is True
    )

    safety_boundaries_valid = all(
        (
            bundle.get(
                "article_body_exposed"
            )
            is False,
            bundle.get(
                "lifecycle_modified"
            )
            is False,
            bundle.get(
                "archive_modified"
            )
            is False,
            bundle.get(
                "body_store_modified"
            )
            is False,
            bundle.get(
                "runtime_job_created"
            )
            is False,
            bundle.get(
                "queue_job_created"
            )
            is False,
        )
    )

    result = {
        "bundle_valid":
            all(
                (
                    not missing_sections,
                    bundle.get(
                        "bundle_complete"
                    )
                    is True,
                    tombstone_id_matches,
                    body_id_matches,
                    workspace_id_matches,
                    persistence_confirmed,
                    verification_confirmed,
                    safety_boundaries_valid,
                )
            ),

        "missing_sections":
            missing_sections,

        "tombstone_id_matches":
            tombstone_id_matches,

        "body_id_matches":
            body_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "persistence_confirmed":
            persistence_confirmed,

        "verification_confirmed":
            verification_confirmed,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "article_body_exposed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )
__all__ = [
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STORE_NAME",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA",
    "PermanentDeletionTombstoneManagerError",
    "calculate_tombstone_repository_checksum_v1",
    "resolve_tombstone_store_root_v1",
    "resolve_tombstone_workspace_root_v1",
    "resolve_tombstone_record_path_v1",
    "resolve_tombstone_index_path_v1",
    "build_tombstone_index_entry_v1",
    "load_tombstone_index_v1",
    "persist_tombstone_contract_v1",
    "load_persisted_tombstone_v1",
    "verify_persisted_tombstone_v1",
    "build_permanent_deletion_tombstone_manager_bundle_v1",
    "verify_permanent_deletion_tombstone_manager_bundle_v1",
]
