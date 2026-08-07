from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_contract_v1 import (
    validate_permanent_deletion_tombstone_contract_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_manager_v1 import (
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,
    calculate_tombstone_repository_checksum_v1,
    load_persisted_tombstone_v1,
    load_tombstone_index_v1,
    resolve_tombstone_index_path_v1,
    resolve_tombstone_record_path_v1,
)


BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_SCHEMA = (
    "body_store_permanent_deletion_tombstone_verifier.v1"
)


class PermanentDeletionTombstoneVerificationError(
    ValueError
):
    """Raised when independent tombstone verification fails."""


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


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise PermanentDeletionTombstoneVerificationError(
            field_name
            + " must be a mapping."
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
        raise PermanentDeletionTombstoneVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionTombstoneVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_tombstone_verification_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        dict(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def verify_tombstone_record_integrity_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_tombstone_id = _require_string(
        tombstone_id,
        field_name="tombstone_id",
    )

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    if not record_path.is_file():
        raise PermanentDeletionTombstoneVerificationError(
            "Persisted tombstone record was not found."
        )

    tombstone = (
        load_persisted_tombstone_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    contract_validation = (
        validate_permanent_deletion_tombstone_contract_v1(
            tombstone_contract=tombstone,
        )
    )

    record_checksum = (
        calculate_tombstone_repository_checksum_v1(
            payload=tombstone,
        )
    )

    identity_valid = all(
        (
            tombstone.get(
                "workspace_id"
            )
            == normalized_workspace_id,
            tombstone.get(
                "tombstone_id"
            )
            == normalized_tombstone_id,
            bool(
                tombstone.get(
                    "body_id"
                )
            ),
            bool(
                tombstone.get(
                    "archive_id"
                )
            ),
            bool(
                tombstone.get(
                    "lifecycle_record_id"
                )
            ),
            bool(
                tombstone.get(
                    "deletion_request_id"
                )
            ),
            bool(
                tombstone.get(
                    "deletion_execution_id"
                )
            ),
        )
    )

    evidence_valid = all(
        (
            tombstone.get(
                "retention_verified"
            )
            is True,
            tombstone.get(
                "archive_verified"
            )
            is True,
            tombstone.get(
                "recovery_closed"
            )
            is True,
            tombstone.get(
                "legal_hold_verified"
            )
            is True,
            bool(
                tombstone.get(
                    "verification_id"
                )
            ),
            bool(
                tombstone.get(
                    "certification_id"
                )
            ),
        )
    )

    immutable_valid = (
        tombstone.get(
            "immutable"
        )
        is True
        and tombstone.get(
            "read_only"
        )
        is True
    )

    forbidden_content_fields = tuple(
        field_name
        for field_name in (
            "content",
            "article_body",
            "body_text",
            "content_body",
            "raw_html",
            "html",
        )
        if field_name in tombstone
    )

    content_free = (
        not forbidden_content_fields
        and tombstone.get(
            "contains_article_body"
        )
        is False
    )

    result = {
        "record_present":
            record_path.is_file(),

        "record_path":
            record_path.as_posix(),

        "contract_valid":
            contract_validation[
                "contract_valid"
            ]
            is True,

        "contract_checksum_valid":
            contract_validation[
                "checksum_valid"
            ]
            is True,

        "identity_valid":
            identity_valid,

        "evidence_valid":
            evidence_valid,

        "immutable_valid":
            immutable_valid,

        "content_free":
            content_free,

        "forbidden_content_fields":
            forbidden_content_fields,

        "record_checksum":
            record_checksum,

        "record_integrity_verified":
            all(
                (
                    record_path.is_file(),
                    contract_validation[
                        "contract_valid"
                    ]
                    is True,
                    contract_validation[
                        "checksum_valid"
                    ]
                    is True,
                    identity_valid,
                    evidence_valid,
                    immutable_valid,
                    content_free,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_tombstone_index_integrity_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_tombstone_id = _require_string(
        tombstone_id,
        field_name="tombstone_id",
    )

    index_path = (
        resolve_tombstone_index_path_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
        )
    )

    if not index_path.is_file():
        raise PermanentDeletionTombstoneVerificationError(
            "Persisted tombstone index was not found."
        )

    index_payload = (
        load_tombstone_index_v1(
            index_path=index_path,
            workspace_id=normalized_workspace_id,
        )
    )

    matching_entries = tuple(
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
            == normalized_tombstone_id
        )
    )

    entry_count_valid = (
        len(
            matching_entries
        )
        == 1
    )

    matching_entry = (
        matching_entries[
            0
        ]
        if entry_count_valid
        else {}
    )

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    tombstone = (
        load_persisted_tombstone_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    calculated_record_checksum = (
        calculate_tombstone_repository_checksum_v1(
            payload=tombstone,
        )
    )

    schema_valid = (
        index_payload.get(
            "schema"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA
    )

    manager_version_valid = (
        index_payload.get(
            "manager_version"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION
    )

    workspace_valid = (
        index_payload.get(
            "workspace_id"
        )
        == normalized_workspace_id
    )

    tombstone_count_valid = (
        index_payload.get(
            "tombstone_count"
        )
        == len(
            index_payload[
                "tombstones"
            ]
        )
    )

    entry_identity_valid = all(
        (
            entry_count_valid,
            matching_entry.get(
                "tombstone_id"
            )
            == tombstone[
                "tombstone_id"
            ],
            matching_entry.get(
                "body_id"
            )
            == tombstone[
                "body_id"
            ],
            matching_entry.get(
                "workspace_id"
            )
            == tombstone[
                "workspace_id"
            ],
            matching_entry.get(
                "archive_id"
            )
            == tombstone[
                "archive_id"
            ],
            matching_entry.get(
                "lifecycle_record_id"
            )
            == tombstone[
                "lifecycle_record_id"
            ],
            matching_entry.get(
                "deletion_request_id"
            )
            == tombstone[
                "deletion_request_id"
            ],
            matching_entry.get(
                "deletion_execution_id"
            )
            == tombstone[
                "deletion_execution_id"
            ],
        )
    )

    contract_checksum_matches = (
        entry_count_valid
        and matching_entry.get(
            "contract_checksum"
        )
        == tombstone[
            "checksum"
        ]
    )

    record_checksum_matches = (
        entry_count_valid
        and matching_entry.get(
            "record_checksum"
        )
        == calculated_record_checksum
    )

    record_path_matches = (
        entry_count_valid
        and matching_entry.get(
            "record_path"
        )
        == record_path.as_posix()
    )

    content_boundary_valid = (
        entry_count_valid
        and matching_entry.get(
            "contains_article_body"
        )
        is False
    )

    result = {
        "index_present":
            index_path.is_file(),

        "index_path":
            index_path.as_posix(),

        "schema_valid":
            schema_valid,

        "manager_version_valid":
            manager_version_valid,

        "workspace_valid":
            workspace_valid,

        "tombstone_count_valid":
            tombstone_count_valid,

        "entry_count_valid":
            entry_count_valid,

        "entry_identity_valid":
            entry_identity_valid,

        "contract_checksum_matches":
            contract_checksum_matches,

        "record_checksum_matches":
            record_checksum_matches,

        "record_path_matches":
            record_path_matches,

        "content_boundary_valid":
            content_boundary_valid,

        "index_integrity_verified":
            all(
                (
                    index_path.is_file(),
                    schema_valid,
                    manager_version_valid,
                    workspace_valid,
                    tombstone_count_valid,
                    entry_count_valid,
                    entry_identity_valid,
                    contract_checksum_matches,
                    record_checksum_matches,
                    record_path_matches,
                    content_boundary_valid,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_tombstone_workspace_isolation_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_tombstone_id = _require_string(
        tombstone_id,
        field_name="tombstone_id",
    )

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    index_path = (
        resolve_tombstone_index_path_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
        )
    )

    tombstone_store_root = (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_tombstones"
    ).resolve()

    workspace_root = (
        tombstone_store_root
        / normalized_workspace_id
    ).resolve()

    try:
        record_path.relative_to(
            workspace_root
        )

        record_path_isolated = True

    except ValueError:
        record_path_isolated = False

    try:
        index_path.relative_to(
            workspace_root
        )

        index_path_isolated = True

    except ValueError:
        index_path_isolated = False

    workspace_root_isolated = (
        workspace_root
        != tombstone_store_root
    )

    result = {
        "tombstone_store_root":
            tombstone_store_root.as_posix(),

        "workspace_root":
            workspace_root.as_posix(),

        "record_path_isolated":
            record_path_isolated,

        "index_path_isolated":
            index_path_isolated,

        "workspace_root_isolated":
            workspace_root_isolated,

        "workspace_isolation_verified":
            all(
                (
                    record_path_isolated,
                    index_path_isolated,
                    workspace_root_isolated,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_permanent_deletion_tombstone_v1(
    *,
    project_root: Path,
    workspace_id: str,
    tombstone_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_tombstone_id = _require_string(
        tombstone_id,
        field_name="tombstone_id",
    )

    record_integrity = (
        verify_tombstone_record_integrity_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    index_integrity = (
        verify_tombstone_index_integrity_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    workspace_isolation = (
        verify_tombstone_workspace_isolation_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    tombstone = (
        load_persisted_tombstone_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            tombstone_id=normalized_tombstone_id,
        )
    )

    verification_material = {
        "tombstone_id":
            tombstone[
                "tombstone_id"
            ],

        "body_id":
            tombstone[
                "body_id"
            ],

        "workspace_id":
            tombstone[
                "workspace_id"
            ],

        "archive_id":
            tombstone[
                "archive_id"
            ],

        "lifecycle_record_id":
            tombstone[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            tombstone[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            tombstone[
                "deletion_execution_id"
            ],

        "contract_checksum":
            tombstone[
                "checksum"
            ],

        "record_checksum":
            record_integrity[
                "record_checksum"
            ],
    }

    verification_id = (
        "body_store_permanent_deletion_tombstone_verification_"
        + calculate_tombstone_verification_checksum_v1(
            payload=verification_material,
        )
    )

    verification = {
        "schema":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION,

        "verification_id":
            verification_id,

        "tombstone_id":
            tombstone[
                "tombstone_id"
            ],

        "body_id":
            tombstone[
                "body_id"
            ],

        "workspace_id":
            tombstone[
                "workspace_id"
            ],

        "archive_id":
            tombstone[
                "archive_id"
            ],

        "lifecycle_record_id":
            tombstone[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            tombstone[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            tombstone[
                "deletion_execution_id"
            ],

        "record_integrity":
            record_integrity,

        "index_integrity":
            index_integrity,

        "workspace_isolation":
            workspace_isolation,

        "tombstone_verified":
            all(
                (
                    record_integrity[
                        "record_integrity_verified"
                    ]
                    is True,
                    index_integrity[
                        "index_integrity_verified"
                    ]
                    is True,
                    workspace_isolation[
                        "workspace_isolation_verified"
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

        "read_only":
            True,
    }

    return _freeze(
        verification
    )


def summarize_permanent_deletion_tombstone_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    summary = {
        "verification_id":
            verification[
                "verification_id"
            ],

        "tombstone_id":
            verification[
                "tombstone_id"
            ],

        "body_id":
            verification[
                "body_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "tombstone_verified":
            verification[
                "tombstone_verified"
            ],

        "record_integrity_verified":
            verification[
                "record_integrity"
            ][
                "record_integrity_verified"
            ],

        "index_integrity_verified":
            verification[
                "index_integrity"
            ][
                "index_integrity_verified"
            ],

        "workspace_isolation_verified":
            verification[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ],

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

        "read_only":
            True,
    }

    return _freeze(
        summary
    )
def certify_permanent_deletion_tombstone_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    summary = (
        summarize_permanent_deletion_tombstone_verification_v1(
            verification_result=verification,
        )
    )

    certification = {
        "schema":
            "body_store_permanent_deletion_tombstone_verifier_certification.v1",

        "verifier_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION,

        "verification_id":
            verification[
                "verification_id"
            ],

        "tombstone_id":
            verification[
                "tombstone_id"
            ],

        "body_id":
            verification[
                "body_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "archive_id":
            verification[
                "archive_id"
            ],

        "lifecycle_record_id":
            verification[
                "lifecycle_record_id"
            ],

        "deletion_request_id":
            verification[
                "deletion_request_id"
            ],

        "deletion_execution_id":
            verification[
                "deletion_execution_id"
            ],

        "certified":
            verification[
                "tombstone_verified"
            ]
            is True,

        "tombstone_verified":
            verification[
                "tombstone_verified"
            ],

        "summary":
            summary,

        "record_integrity":
            verification[
                "record_integrity"
            ],

        "index_integrity":
            verification[
                "index_integrity"
            ],

        "workspace_isolation":
            verification[
                "workspace_isolation"
            ],

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

        "read_only":
            True,
    }

    return _freeze(
        certification
    )


__all__ = [
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_SCHEMA",
    "PermanentDeletionTombstoneVerificationError",
    "calculate_tombstone_verification_checksum_v1",
    "verify_tombstone_record_integrity_v1",
    "verify_tombstone_index_integrity_v1",
    "verify_tombstone_workspace_isolation_v1",
    "verify_permanent_deletion_tombstone_v1",
    "summarize_permanent_deletion_tombstone_verification_v1",
    "certify_permanent_deletion_tombstone_verification_v1",
]
