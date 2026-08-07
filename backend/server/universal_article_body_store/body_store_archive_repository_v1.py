from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple

BODY_STORE_ARCHIVE_REPOSITORY_VERSION = "1.0"

BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA = (
    "body_store_archive_repository.v1"
)

BODY_STORE_ARCHIVE_REPOSITORY_STATUSES = (
    "ACTIVE",
    "ARCHIVED",
    "RESTORED",
)

BODY_STORE_ARCHIVE_CHECKSUM_ALGORITHM = (
    "sha256"
)

BODY_STORE_ARCHIVE_ROOT_FOLDER = (
    "archive"
)

BODY_STORE_ARCHIVE_INDEX_FILENAME = (
    "archive_index.json"
)

BODY_STORE_ARCHIVE_METADATA_FILENAME = (
    "archive_metadata.json"
)


def _immutable(
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
                k: _immutable(v)
                for k, v in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _immutable(v)
            for v in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _immutable(v)
            for v in value
        )

    return value


def calculate_archive_checksum_v1(
    *,
    content: str,
) -> str:

    return hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()


def build_archive_storage_paths_v1(
    *,
    workspace_id: str,
    body_id: str,
) -> Mapping[str, str]:

    relative_root = (
        Path(
            BODY_STORE_ARCHIVE_ROOT_FOLDER
        )
        / workspace_id
        / body_id
    )

    result = {
        "archive_root":
            relative_root.as_posix(),

        "archive_index":
            (
                relative_root
                / BODY_STORE_ARCHIVE_INDEX_FILENAME
            ).as_posix(),

        "archive_metadata":
            (
                relative_root
                / BODY_STORE_ARCHIVE_METADATA_FILENAME
            ).as_posix(),
    }

    return _immutable(
        result
    )


def create_archive_metadata_v1(
    *,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    archive_reason: str,
    archived_at: str,
    actor_type: str,
    actor_id: str,
    content: str,
) -> Mapping[str, Any]:

    checksum = (
        calculate_archive_checksum_v1(
            content=content,
        )
    )

    paths = (
        build_archive_storage_paths_v1(
            workspace_id=workspace_id,
            body_id=body_id,
        )
    )
    metadata = {
        "schema_version":
            BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA,

        "repository_version":
            BODY_STORE_ARCHIVE_REPOSITORY_VERSION,

        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "body_id":
            body_id,

        "archive_status":
            "ARCHIVED",

        "archive_reason":
            archive_reason,

        "archived_at":
            archived_at,

        "actor_type":
            actor_type,

        "actor_id":
            actor_id,

        "archive_checksum":
            checksum,

        "checksum_algorithm":
            BODY_STORE_ARCHIVE_CHECKSUM_ALGORITHM,

        "archive_root":
            paths[
                "archive_root"
            ],

        "archive_index_path":
            paths[
                "archive_index"
            ],

        "archive_metadata_path":
            paths[
                "archive_metadata"
            ],

        "archive_verified":
            False,

        "physical_archive_performed":
            False,

        "content_length":
            len(content),

        "content_body_included":
            False,
    }

    return _immutable(
        metadata
    )


def build_archive_record_v1(
    *,
    archive_metadata: Mapping[str, Any],
    content: str,
) -> Mapping[str, Any]:

    if not isinstance(
        archive_metadata,
        Mapping,
    ):
        raise TypeError(
            "archive_metadata must be a mapping."
        )

    required_fields = (
        "archive_id",
        "workspace_id",
        "body_id",
        "archive_checksum",
        "archive_status",
        "archived_at",
    )

    for field in required_fields:
        if field not in archive_metadata:
            raise ValueError(
                f"Missing archive metadata field: {field}"
            )

    calculated_checksum = (
        calculate_archive_checksum_v1(
            content=content,
        )
    )

    if (
        calculated_checksum
        != archive_metadata[
            "archive_checksum"
        ]
    ):
        raise ValueError(
            "Archive content checksum does not match metadata."
        )

    record = {
        "schema_version":
            BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA,

        "repository_version":
            BODY_STORE_ARCHIVE_REPOSITORY_VERSION,

        "archive_id":
            archive_metadata[
                "archive_id"
            ],

        "workspace_id":
            archive_metadata[
                "workspace_id"
            ],

        "body_id":
            archive_metadata[
                "body_id"
            ],

        "archive_status":
            archive_metadata[
                "archive_status"
            ],

        "archive_checksum":
            archive_metadata[
                "archive_checksum"
            ],

        "checksum_algorithm":
            archive_metadata[
                "checksum_algorithm"
            ],

        "archived_at":
            archive_metadata[
                "archived_at"
            ],

        "archive_reason":
            archive_metadata[
                "archive_reason"
            ],

        "actor_type":
            archive_metadata[
                "actor_type"
            ],

        "actor_id":
            archive_metadata[
                "actor_id"
            ],

        "archive_root":
            archive_metadata[
                "archive_root"
            ],

        "archive_index_path":
            archive_metadata[
                "archive_index_path"
            ],

        "archive_metadata_path":
            archive_metadata[
                "archive_metadata_path"
            ],

        "content":
            content,

        "content_length":
            len(content),

        "archive_verified":
            False,

        "physical_archive_performed":
            False,
    }

    return _immutable(
        record
    )
def verify_archive_record_v1(
    *,
    archive_record: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        archive_record,
        Mapping,
    ):
        raise TypeError(
            "archive_record must be a mapping."
        )

    required_fields = (
        "archive_id",
        "workspace_id",
        "body_id",
        "archive_status",
        "archive_checksum",
        "checksum_algorithm",
        "content",
        "content_length",
    )

    missing_fields = tuple(
        field
        for field in required_fields
        if field not in archive_record
    )

    if missing_fields:
        raise ValueError(
            "Missing archive record fields: "
            + ", ".join(
                missing_fields
            )
        )

    content = archive_record[
        "content"
    ]

    if not isinstance(
        content,
        str,
    ):
        raise TypeError(
            "Archive record content must be a string."
        )

    calculated_checksum = (
        calculate_archive_checksum_v1(
            content=content,
        )
    )

    checksum_matches = (
        calculated_checksum
        == archive_record[
            "archive_checksum"
        ]
    )

    content_length_matches = (
        len(content)
        == archive_record[
            "content_length"
        ]
    )

    status_valid = (
        archive_record[
            "archive_status"
        ]
        in BODY_STORE_ARCHIVE_REPOSITORY_STATUSES
    )

    algorithm_valid = (
        archive_record[
            "checksum_algorithm"
        ]
        == BODY_STORE_ARCHIVE_CHECKSUM_ALGORITHM
    )

    verification = {
        "archive_id":
            archive_record[
                "archive_id"
            ],

        "workspace_id":
            archive_record[
                "workspace_id"
            ],

        "body_id":
            archive_record[
                "body_id"
            ],

        "archive_verified":
            all(
                (
                    checksum_matches,
                    content_length_matches,
                    status_valid,
                    algorithm_valid,
                )
            ),

        "checksum_matches":
            checksum_matches,

        "content_length_matches":
            content_length_matches,

        "status_valid":
            status_valid,

        "algorithm_valid":
            algorithm_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            archive_record[
                "archive_checksum"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        verification
    )


def build_archive_index_entry_v1(
    *,
    archive_record: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:

    if verification[
        "archive_verified"
    ] is not True:
        raise ValueError(
            "Archive record must pass verification."
        )

    index_entry = {
        "archive_id":
            archive_record[
                "archive_id"
            ],

        "workspace_id":
            archive_record[
                "workspace_id"
            ],

        "body_id":
            archive_record[
                "body_id"
            ],

        "archive_status":
            archive_record[
                "archive_status"
            ],

        "archive_checksum":
            archive_record[
                "archive_checksum"
            ],

        "archived_at":
            archive_record[
                "archived_at"
            ],

        "archive_root":
            archive_record[
                "archive_root"
            ],

        "archive_index_path":
            archive_record[
                "archive_index_path"
            ],

        "archive_metadata_path":
            archive_record[
                "archive_metadata_path"
            ],

        "archive_verified":
            True,

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        index_entry
    )
def create_archive_repository_package_v1(
    *,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    archive_reason: str,
    archived_at: str,
    actor_type: str,
    actor_id: str,
    content: str,
) -> Mapping[str, Any]:

    metadata = (
        create_archive_metadata_v1(
            archive_id=archive_id,
            workspace_id=workspace_id,
            body_id=body_id,
            archive_reason=archive_reason,
            archived_at=archived_at,
            actor_type=actor_type,
            actor_id=actor_id,
            content=content,
        )
    )

    record = (
        build_archive_record_v1(
            archive_metadata=metadata,
            content=content,
        )
    )

    verification = (
        verify_archive_record_v1(
            archive_record=record,
        )
    )

    index_entry = (
        build_archive_index_entry_v1(
            archive_record=record,
            verification=verification,
        )
    )

    package = {
        "schema_version":
            BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA,

        "repository_version":
            BODY_STORE_ARCHIVE_REPOSITORY_VERSION,

        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "body_id":
            body_id,

        "metadata":
            metadata,

        "record":
            record,

        "verification":
            verification,

        "index_entry":
            index_entry,

        "package_complete":
            True,

        "archive_verified":
            verification[
                "archive_verified"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _immutable(
        package
    )


def summarize_archive_repository_package_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        archive_package,
        Mapping,
    ):
        raise TypeError(
            "archive_package must be a mapping."
        )

    summary = {
        "archive_id":
            archive_package[
                "archive_id"
            ],

        "workspace_id":
            archive_package[
                "workspace_id"
            ],

        "body_id":
            archive_package[
                "body_id"
            ],

        "archive_status":
            archive_package[
                "record"
            ][
                "archive_status"
            ],

        "archive_checksum":
            archive_package[
                "record"
            ][
                "archive_checksum"
            ],

        "archive_verified":
            archive_package[
                "verification"
            ][
                "archive_verified"
            ],

        "archive_root":
            archive_package[
                "metadata"
            ][
                "archive_root"
            ],

        "archive_index_path":
            archive_package[
                "metadata"
            ][
                "archive_index_path"
            ],

        "archive_metadata_path":
            archive_package[
                "metadata"
            ][
                "archive_metadata_path"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        summary
    )


def validate_archive_repository_package_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        archive_package,
        Mapping,
    ):
        raise TypeError(
            "archive_package must be a mapping."
        )

    required_sections = (
        "metadata",
        "record",
        "verification",
        "index_entry",
    )

    sections_present = all(
        section in archive_package
        for section in required_sections
    )

    identifier_match = (
        archive_package[
            "metadata"
        ][
            "archive_id"
        ]
        ==
        archive_package[
            "record"
        ][
            "archive_id"
        ]
        ==
        archive_package[
            "verification"
        ][
            "archive_id"
        ]
        ==
        archive_package[
            "index_entry"
        ][
            "archive_id"
        ]
    )

    workspace_match = (
        archive_package[
            "metadata"
        ][
            "workspace_id"
        ]
        ==
        archive_package[
            "record"
        ][
            "workspace_id"
        ]
        ==
        archive_package[
            "verification"
        ][
            "workspace_id"
        ]
        ==
        archive_package[
            "index_entry"
        ][
            "workspace_id"
        ]
    )

    checksum_match = (
        archive_package[
            "record"
        ][
            "archive_checksum"
        ]
        ==
        archive_package[
            "index_entry"
        ][
            "archive_checksum"
        ]
    )

    validation = {
        "package_valid":
            all(
                (
                    sections_present,
                    identifier_match,
                    workspace_match,
                    checksum_match,
                    archive_package[
                        "verification"
                    ][
                        "archive_verified"
                    ],
                )
            ),

        "sections_present":
            sections_present,

        "identifier_match":
            identifier_match,

        "workspace_match":
            workspace_match,

        "checksum_match":
            checksum_match,

        "archive_verified":
            archive_package[
                "verification"
            ][
                "archive_verified"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        validation
    )
def certify_archive_repository_package_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    validation = (
        validate_archive_repository_package_v1(
            archive_package=archive_package,
        )
    )

    summary = (
        summarize_archive_repository_package_v1(
            archive_package=archive_package,
        )
    )

    certification = {
        "certification_version":
            "body_store_archive_repository_certification_v1",

        "archive_id":
            archive_package[
                "archive_id"
            ],

        "workspace_id":
            archive_package[
                "workspace_id"
            ],

        "body_id":
            archive_package[
                "body_id"
            ],

        "certified":
            validation[
                "package_valid"
            ],

        "package_complete":
            archive_package[
                "package_complete"
            ],

        "archive_verified":
            archive_package[
                "archive_verified"
            ],

        "validation":
            validation,

        "summary":
            summary,

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _immutable(
        certification
    )


def export_archive_repository_contract_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        certification,
        Mapping,
    ):
        raise TypeError(
            "certification must be a mapping."
        )

    summary = certification[
        "summary"
    ]

    contract = {
        "contract_version":
            "body_store_archive_repository_contract_v1",

        "repository_schema":
            BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA,

        "repository_version":
            BODY_STORE_ARCHIVE_REPOSITORY_VERSION,

        "archive_id":
            summary[
                "archive_id"
            ],

        "workspace_id":
            summary[
                "workspace_id"
            ],

        "body_id":
            summary[
                "body_id"
            ],

        "archive_status":
            summary[
                "archive_status"
            ],

        "archive_checksum":
            summary[
                "archive_checksum"
            ],

        "archive_verified":
            summary[
                "archive_verified"
            ],

        "archive_root":
            summary[
                "archive_root"
            ],

        "archive_index_path":
            summary[
                "archive_index_path"
            ],

        "archive_metadata_path":
            summary[
                "archive_metadata_path"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _immutable(
        contract
    )


def build_archive_repository_bundle_v1(
    *,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    archive_reason: str,
    archived_at: str,
    actor_type: str,
    actor_id: str,
    content: str,
) -> Mapping[str, Any]:

    archive_package = (
        create_archive_repository_package_v1(
            archive_id=archive_id,
            workspace_id=workspace_id,
            body_id=body_id,
            archive_reason=archive_reason,
            archived_at=archived_at,
            actor_type=actor_type,
            actor_id=actor_id,
            content=content,
        )
    )

    certification = (
        certify_archive_repository_package_v1(
            archive_package=archive_package,
        )
    )

    contract = (
        export_archive_repository_contract_v1(
            certification=certification,
        )
    )

    bundle = {
        "bundle_version":
            "body_store_archive_repository_bundle_v1",

        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "body_id":
            body_id,

        "archive_package":
            archive_package,

        "certification":
            certification,

        "contract":
            contract,

        "bundle_complete":
            True,

        "certified":
            certification[
                "certified"
            ],

        "archive_verified":
            certification[
                "archive_verified"
            ],

        "physical_archive_performed":
            False,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _immutable(
        bundle
    )
# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "BODY_STORE_ARCHIVE_REPOSITORY_VERSION",
    "BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA",
    "BODY_STORE_ARCHIVE_REPOSITORY_STATUSES",
    "BODY_STORE_ARCHIVE_CHECKSUM_ALGORITHM",
    "BODY_STORE_ARCHIVE_ROOT_FOLDER",
    "BODY_STORE_ARCHIVE_INDEX_FILENAME",
    "BODY_STORE_ARCHIVE_METADATA_FILENAME",
    "calculate_archive_checksum_v1",
    "build_archive_storage_paths_v1",
    "create_archive_metadata_v1",
    "build_archive_record_v1",
    "verify_archive_record_v1",
    "build_archive_index_entry_v1",
    "create_archive_repository_package_v1",
    "summarize_archive_repository_package_v1",
    "validate_archive_repository_package_v1",
    "certify_archive_repository_package_v1",
    "export_archive_repository_contract_v1",
    "build_archive_repository_bundle_v1",
]


if __name__ == "__main__":

    sample_bundle = (
        build_archive_repository_bundle_v1(
            archive_id="archive_repository_demo_v1",
            workspace_id="ws_archive_repository_demo",
            body_id="body_archive_repository_demo",
            archive_reason="Archive Repository module self-test.",
            archived_at="2026-08-04T00:00:00+00:00",
            actor_type="SYSTEM",
            actor_id="archive_repository_self_test",
            content="Archive Repository verification content.",
        )
    )

    print(
        "Archive Repository Bundle Created Successfully"
    )

    print(
        json.dumps(
            dict(
                sample_bundle
            ),
            indent=4,
            default=dict,
        )
    )
