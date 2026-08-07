from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_archive_repository_manager_v1 import (
    build_repository_paths_v1,
    load_archive_repository_v1,
)


ARCHIVE_REPOSITORY_VERIFIER_VERSION = "1.0"

ARCHIVE_REPOSITORY_VERIFIER_SCHEMA = (
    "body_store_archive_repository_verifier.v1"
)

ARCHIVE_REPOSITORY_REQUIRED_SECTIONS = (
    "index",
    "metadata",
    "content",
)


class ArchiveRepositoryVerificationError(
    ValueError
):
    """Raised when a stored archive cannot be verified."""


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
        raise ArchiveRepositoryVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ArchiveRepositoryVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_stored_archive_checksum_v1(
    *,
    content: str,
) -> str:

    normalized_content = _require_string(
        content,
        field_name="content",
    )

    return hashlib.sha256(
        normalized_content.encode(
            "utf-8"
        )
    ).hexdigest()


def calculate_repository_payload_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise ArchiveRepositoryVerificationError(
            "payload must be a mapping."
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
def verify_archive_repository_sections_v1(
    *,
    stored_repository: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        stored_repository,
        Mapping,
    ):
        raise ArchiveRepositoryVerificationError(
            "stored_repository must be a mapping."
        )

    missing_sections = tuple(
        section
        for section in ARCHIVE_REPOSITORY_REQUIRED_SECTIONS
        if section not in stored_repository
    )

    result = {
        "sections_present":
            not missing_sections,

        "missing_sections":
            missing_sections,

        "required_sections":
            ARCHIVE_REPOSITORY_REQUIRED_SECTIONS,
    }

    return _freeze(
        result
    )


def verify_archive_repository_identifiers_v1(
    *,
    stored_repository: Mapping[str, Any],
) -> Mapping[str, Any]:

    section_result = (
        verify_archive_repository_sections_v1(
            stored_repository=stored_repository,
        )
    )

    if section_result[
        "sections_present"
    ] is not True:
        raise ArchiveRepositoryVerificationError(
            "Stored repository sections are incomplete."
        )

    index_payload = stored_repository[
        "index"
    ]

    metadata_payload = stored_repository[
        "metadata"
    ]

    content_payload = stored_repository[
        "content"
    ]

    archive_id = _require_string(
        stored_repository.get(
            "archive_id"
        ),
        field_name="archive_id",
    )

    workspace_id = _require_string(
        stored_repository.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    body_id = _require_string(
        content_payload.get(
            "body_id"
        ),
        field_name="body_id",
    )

    archive_id_matches = (
        archive_id
        == index_payload.get(
            "archive_id"
        )
        == metadata_payload.get(
            "archive_id"
        )
        == content_payload.get(
            "archive_id"
        )
    )

    workspace_id_matches = (
        workspace_id
        == index_payload.get(
            "workspace_id"
        )
        == metadata_payload.get(
            "workspace_id"
        )
        == content_payload.get(
            "workspace_id"
        )
    )

    body_id_matches = (
        body_id
        == index_payload.get(
            "body_id"
        )
        == metadata_payload.get(
            "body_id"
        )
        == content_payload.get(
            "body_id"
        )
    )

    result = {
        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "body_id":
            body_id,

        "archive_id_matches":
            archive_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "body_id_matches":
            body_id_matches,

        "identifiers_verified":
            all(
                (
                    archive_id_matches,
                    workspace_id_matches,
                    body_id_matches,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_archive_repository_checksum_v1(
    *,
    stored_repository: Mapping[str, Any],
) -> Mapping[str, Any]:

    content_payload = stored_repository[
        "content"
    ]

    content = _require_string(
        content_payload.get(
            "content"
        ),
        field_name="content",
    )

    stored_checksum = _require_string(
        content_payload.get(
            "archive_checksum"
        ),
        field_name="archive_checksum",
    )

    calculated_checksum = (
        calculate_stored_archive_checksum_v1(
            content=content,
        )
    )

    checksum_matches = (
        stored_checksum
        == calculated_checksum
    )

    content_length_matches = (
        content_payload.get(
            "content_length"
        )
        == len(
            content
        )
    )

    result = {
        "stored_checksum":
            stored_checksum,

        "calculated_checksum":
            calculated_checksum,

        "checksum_matches":
            checksum_matches,

        "content_length_matches":
            content_length_matches,

        "checksum_verified":
            (
                checksum_matches
                and content_length_matches
            ),
    }

    return _freeze(
        result
    )
def verify_archive_repository_paths_v1(
    *,
    project_root: Path,
    workspace_id: str,
    archive_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_archive_id = _require_string(
        archive_id,
        field_name="archive_id",
    )

    paths = (
        build_repository_paths_v1(
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    archive_root = (
        project_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
    ).resolve()

    index_path = (
        archive_root
        / paths[
            "archive_index"
        ]
    ).resolve()

    metadata_path = (
        archive_root
        / paths[
            "archive_metadata"
        ]
    ).resolve()

    content_path = (
        archive_root
        / paths[
            "archive_content"
        ]
    ).resolve()

    expected_workspace_segment = (
        Path(
            "archive"
        )
        / normalized_workspace_id
        / normalized_archive_id
    ).as_posix()

    result = {
        "archive_root":
            archive_root.as_posix(),

        "index_path":
            index_path.as_posix(),

        "metadata_path":
            metadata_path.as_posix(),

        "content_path":
            content_path.as_posix(),

        "index_exists":
            index_path.is_file(),

        "metadata_exists":
            metadata_path.is_file(),

        "content_exists":
            content_path.is_file(),

        "workspace_isolated":
            expected_workspace_segment
            in index_path.as_posix()
            and expected_workspace_segment
            in metadata_path.as_posix()
            and expected_workspace_segment
            in content_path.as_posix(),

        "paths_verified":
            (
                index_path.is_file()
                and metadata_path.is_file()
                and content_path.is_file()
                and expected_workspace_segment
                in index_path.as_posix()
                and expected_workspace_segment
                in metadata_path.as_posix()
                and expected_workspace_segment
                in content_path.as_posix()
            ),
    }

    return _freeze(
        result
    )


def verify_archive_repository_v1(
    *,
    project_root: Path,
    workspace_id: str,
    archive_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_archive_id = _require_string(
        archive_id,
        field_name="archive_id",
    )

    stored_repository = (
        load_archive_repository_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    sections = (
        verify_archive_repository_sections_v1(
            stored_repository=stored_repository,
        )
    )

    identifiers = (
        verify_archive_repository_identifiers_v1(
            stored_repository=stored_repository,
        )
    )

    checksum = (
        verify_archive_repository_checksum_v1(
            stored_repository=stored_repository,
        )
    )

    paths = (
        verify_archive_repository_paths_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    result = {
        "schema_version":
            ARCHIVE_REPOSITORY_VERIFIER_SCHEMA,

        "verifier_version":
            ARCHIVE_REPOSITORY_VERIFIER_VERSION,

        "archive_id":
            normalized_archive_id,

        "workspace_id":
            normalized_workspace_id,

        "sections":
            sections,

        "identifiers":
            identifiers,

        "checksum":
            checksum,

        "paths":
            paths,

        "repository_verified":
            all(
                (
                    sections[
                        "sections_present"
                    ],
                    identifiers[
                        "identifiers_verified"
                    ],
                    checksum[
                        "checksum_verified"
                    ],
                    paths[
                        "paths_verified"
                    ],
                )
            ),

        "repository_read_performed":
            True,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        result
    )
def summarize_archive_repository_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        verification_result,
        Mapping,
    ):
        raise ArchiveRepositoryVerificationError(
            "verification_result must be a mapping."
        )

    summary = {
        "archive_id":
            verification_result[
                "archive_id"
            ],

        "workspace_id":
            verification_result[
                "workspace_id"
            ],

        "repository_verified":
            verification_result[
                "repository_verified"
            ],

        "sections_present":
            verification_result[
                "sections"
            ][
                "sections_present"
            ],

        "identifiers_verified":
            verification_result[
                "identifiers"
            ][
                "identifiers_verified"
            ],

        "checksum_verified":
            verification_result[
                "checksum"
            ][
                "checksum_verified"
            ],

        "paths_verified":
            verification_result[
                "paths"
            ][
                "paths_verified"
            ],

        "workspace_isolated":
            verification_result[
                "paths"
            ][
                "workspace_isolated"
            ],

        "repository_read_performed":
            True,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        summary
    )


def certify_archive_repository_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    summary = (
        summarize_archive_repository_verification_v1(
            verification_result=verification_result,
        )
    )

    certification = {
        "certification_version":
            "body_store_archive_repository_verifier_certification_v1",

        "archive_id":
            summary[
                "archive_id"
            ],

        "workspace_id":
            summary[
                "workspace_id"
            ],

        "certified":
            summary[
                "repository_verified"
            ],

        "repository_verified":
            summary[
                "repository_verified"
            ],

        "sections_present":
            summary[
                "sections_present"
            ],

        "identifiers_verified":
            summary[
                "identifiers_verified"
            ],

        "checksum_verified":
            summary[
                "checksum_verified"
            ],

        "paths_verified":
            summary[
                "paths_verified"
            ],

        "workspace_isolated":
            summary[
                "workspace_isolated"
            ],

        "summary":
            summary,

        "repository_read_performed":
            True,

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

    return _freeze(
        certification
    )


__all__ = [
    "ARCHIVE_REPOSITORY_VERIFIER_VERSION",
    "ARCHIVE_REPOSITORY_VERIFIER_SCHEMA",
    "ARCHIVE_REPOSITORY_REQUIRED_SECTIONS",
    "ArchiveRepositoryVerificationError",
    "calculate_stored_archive_checksum_v1",
    "calculate_repository_payload_checksum_v1",
    "verify_archive_repository_sections_v1",
    "verify_archive_repository_identifiers_v1",
    "verify_archive_repository_checksum_v1",
    "verify_archive_repository_paths_v1",
    "verify_archive_repository_v1",
    "summarize_archive_repository_verification_v1",
    "certify_archive_repository_verification_v1",
]
