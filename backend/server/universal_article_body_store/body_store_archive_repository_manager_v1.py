from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping

from backend.server.universal_article_body_store.body_store_archive_repository_v1 import (
    build_archive_repository_bundle_v1,
)

ARCHIVE_REPOSITORY_MANAGER_VERSION = "1.0"

ARCHIVE_REPOSITORY_MANAGER_SCHEMA = (
    "body_store_archive_repository_manager.v1"
)

ARCHIVE_DIRECTORY_NAME = "archive"

ARCHIVE_INDEX_FILENAME = (
    "archive_index.json"
)

ARCHIVE_METADATA_FILENAME = (
    "archive_metadata.json"
)

ARCHIVE_CONTENT_FILENAME = (
    "archive_content.json"
)


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
                k: _freeze(v)
                for k, v in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(v)
            for v in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(v)
            for v in value
        )

    return value


def calculate_repository_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    serialized = json.dumps(
        payload,
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def build_repository_paths_v1(
    *,
    workspace_id: str,
    archive_id: str,
) -> Mapping[str, str]:

    root = (
        Path(
            ARCHIVE_DIRECTORY_NAME
        )
        / workspace_id
        / archive_id
    )

    result = {
        "repository_root":
            root.as_posix(),

        "archive_index":
            (
                root
                / ARCHIVE_INDEX_FILENAME
            ).as_posix(),

        "archive_metadata":
            (
                root
                / ARCHIVE_METADATA_FILENAME
            ).as_posix(),

        "archive_content":
            (
                root
                / ARCHIVE_CONTENT_FILENAME
            ).as_posix(),
    }

    return _freeze(
        result
    )


def create_repository_descriptor_v1(
    *,
    bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    contract = bundle[
        "contract"
    ]

    paths = (
        build_repository_paths_v1(
            workspace_id=contract[
                "workspace_id"
            ],
            archive_id=contract[
                "archive_id"
            ],
        )
    )
    descriptor = {
        "schema_version":
            ARCHIVE_REPOSITORY_MANAGER_SCHEMA,

        "manager_version":
            ARCHIVE_REPOSITORY_MANAGER_VERSION,

        "archive_id":
            contract[
                "archive_id"
            ],

        "workspace_id":
            contract[
                "workspace_id"
            ],

        "body_id":
            contract[
                "body_id"
            ],

        "archive_status":
            contract[
                "archive_status"
            ],

        "archive_checksum":
            contract[
                "archive_checksum"
            ],

        "archive_verified":
            contract[
                "archive_verified"
            ],

        "repository_root":
            paths[
                "repository_root"
            ],

        "archive_index_path":
            paths[
                "archive_index"
            ],

        "archive_metadata_path":
            paths[
                "archive_metadata"
            ],

        "archive_content_path":
            paths[
                "archive_content"
            ],

        "repository_checksum":
            calculate_repository_checksum_v1(
                payload=contract,
            ),

        "repository_write_performed":
            False,

        "index_write_performed":
            False,

        "metadata_write_performed":
            False,

        "content_write_performed":
            False,

        "physical_archive_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        descriptor
    )


def build_repository_write_plan_v1(
    *,
    bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    descriptor = (
        create_repository_descriptor_v1(
            bundle=bundle,
        )
    )

    archive_package = bundle[
        "archive_package"
    ]

    record = archive_package[
        "record"
    ]

    metadata = archive_package[
        "metadata"
    ]

    index_entry = archive_package[
        "index_entry"
    ]

    write_plan = {
        "schema_version":
            "body_store_archive_repository_write_plan.v1",

        "archive_id":
            descriptor[
                "archive_id"
            ],

        "workspace_id":
            descriptor[
                "workspace_id"
            ],

        "body_id":
            descriptor[
                "body_id"
            ],

        "repository_root":
            descriptor[
                "repository_root"
            ],

        "archive_index_path":
            descriptor[
                "archive_index_path"
            ],

        "archive_metadata_path":
            descriptor[
                "archive_metadata_path"
            ],

        "archive_content_path":
            descriptor[
                "archive_content_path"
            ],

        "index_payload":
            index_entry,

        "metadata_payload":
            metadata,

        "content_payload":
            {
                "archive_id":
                    record[
                        "archive_id"
                    ],

                "workspace_id":
                    record[
                        "workspace_id"
                    ],

                "body_id":
                    record[
                        "body_id"
                    ],

                "archive_checksum":
                    record[
                        "archive_checksum"
                    ],

                "checksum_algorithm":
                    record[
                        "checksum_algorithm"
                    ],

                "content":
                    record[
                        "content"
                    ],

                "content_length":
                    record[
                        "content_length"
                    ],
            },

        "repository_checksum":
            descriptor[
                "repository_checksum"
            ],

        "write_ready":
            (
                descriptor[
                    "archive_verified"
                ]
                is True
            ),

        "repository_write_performed":
            False,

        "index_write_performed":
            False,

        "metadata_write_performed":
            False,

        "content_write_performed":
            False,

        "physical_archive_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        write_plan
    )
def _resolve_repository_path_v1(
    *,
    project_root: Path,
    relative_path: str,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise TypeError(
            "project_root must be a Path."
        )

    if not isinstance(
        relative_path,
        str,
    ):
        raise TypeError(
            "relative_path must be a string."
        )

    normalized_relative_path = (
        relative_path.strip()
    )

    if not normalized_relative_path:
        raise ValueError(
            "relative_path must not be empty."
        )

    root = project_root.resolve()

    resolved_path = (
        root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
        / Path(
            normalized_relative_path
        )
    ).resolve()

    archive_root = (
        root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
    ).resolve()

    try:
        resolved_path.relative_to(
            archive_root
        )

    except ValueError as exc:
        raise ValueError(
            "Repository path escaped the archive root."
        ) from exc

    return resolved_path


def _serialize_repository_payload_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise TypeError(
            "payload must be a mapping."
        )

    return (
        json.dumps(
            dict(
                payload
            ),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            default=dict,
        )
        + "\n"
    )


def _write_repository_json_atomic_v1(
    *,
    path: Path,
    payload: Mapping[str, Any],
) -> None:

    if not isinstance(
        path,
        Path,
    ):
        raise TypeError(
            "path must be a Path."
        )

    serialized = (
        _serialize_repository_payload_v1(
            payload=payload,
        )
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        "."
        + path.name
        + ".tmp"
    )

    temporary_path.write_text(
        serialized,
        encoding="utf-8",
    )

    temporary_path.replace(
        path
    )


def _read_repository_json_v1(
    *,
    path: Path,
) -> Dict[str, Any]:

    if not isinstance(
        path,
        Path,
    ):
        raise TypeError(
            "path must be a Path."
        )

    if not path.is_file():
        raise FileNotFoundError(
            "Archive repository file not found: "
            + str(
                path
            )
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Archive repository payload must be an object."
        )

    return payload


def verify_repository_write_plan_v1(
    *,
    write_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        write_plan,
        Mapping,
    ):
        raise TypeError(
            "write_plan must be a mapping."
        )

    required_fields = (
        "archive_id",
        "workspace_id",
        "body_id",
        "archive_index_path",
        "archive_metadata_path",
        "archive_content_path",
        "index_payload",
        "metadata_payload",
        "content_payload",
        "repository_checksum",
        "write_ready",
    )

    missing_fields = tuple(
        field
        for field in required_fields
        if field not in write_plan
    )

    if missing_fields:
        raise ValueError(
            "Missing repository write-plan fields: "
            + ", ".join(
                missing_fields
            )
        )

    content_payload = write_plan[
        "content_payload"
    ]

    content = content_payload[
        "content"
    ]

    stored_checksum = content_payload[
        "archive_checksum"
    ]

    calculated_checksum = hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()

    verification = {
        "write_plan_valid":
            (
                write_plan[
                    "write_ready"
                ]
                is True
                and stored_checksum
                == calculated_checksum
            ),

        "write_ready":
            write_plan[
                "write_ready"
            ],

        "archive_checksum_matches":
            stored_checksum
            == calculated_checksum,

        "stored_archive_checksum":
            stored_checksum,

        "calculated_archive_checksum":
            calculated_checksum,

        "repository_checksum_present":
            bool(
                write_plan[
                    "repository_checksum"
                ]
            ),

        "repository_write_performed":
            False,

        "index_write_performed":
            False,

        "metadata_write_performed":
            False,

        "content_write_performed":
            False,
    }

    return _freeze(
        verification
    )
def store_archive_repository_v1(
    *,
    project_root: Path,
    write_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = (
        verify_repository_write_plan_v1(
            write_plan=write_plan,
        )
    )

    if verification[
        "write_plan_valid"
    ] is not True:
        raise ValueError(
            "Archive repository write plan is invalid."
        )

    index_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=write_plan[
                "archive_index_path"
            ],
        )
    )

    metadata_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=write_plan[
                "archive_metadata_path"
            ],
        )
    )

    content_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=write_plan[
                "archive_content_path"
            ],
        )
    )

    _write_repository_json_atomic_v1(
        path=index_path,
        payload=write_plan[
            "index_payload"
        ],
    )

    _write_repository_json_atomic_v1(
        path=metadata_path,
        payload=write_plan[
            "metadata_payload"
        ],
    )

    _write_repository_json_atomic_v1(
        path=content_path,
        payload=write_plan[
            "content_payload"
        ],
    )

    result = {
        "schema_version":
            ARCHIVE_REPOSITORY_MANAGER_SCHEMA,

        "manager_version":
            ARCHIVE_REPOSITORY_MANAGER_VERSION,

        "archive_id":
            write_plan[
                "archive_id"
            ],

        "workspace_id":
            write_plan[
                "workspace_id"
            ],

        "body_id":
            write_plan[
                "body_id"
            ],

        "repository_root":
            write_plan[
                "repository_root"
            ],

        "archive_index_path":
            write_plan[
                "archive_index_path"
            ],

        "archive_metadata_path":
            write_plan[
                "archive_metadata_path"
            ],

        "archive_content_path":
            write_plan[
                "archive_content_path"
            ],

        "repository_checksum":
            write_plan[
                "repository_checksum"
            ],

        "repository_write_performed":
            True,

        "index_write_performed":
            True,

        "metadata_write_performed":
            True,

        "content_write_performed":
            True,

        "physical_archive_performed":
            True,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )


def load_archive_repository_v1(
    *,
    project_root: Path,
    workspace_id: str,
    archive_id: str,
) -> Mapping[str, Any]:

    paths = (
        build_repository_paths_v1(
            workspace_id=workspace_id,
            archive_id=archive_id,
        )
    )

    index_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=paths[
                "archive_index"
            ],
        )
    )

    metadata_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=paths[
                "archive_metadata"
            ],
        )
    )

    content_path = (
        _resolve_repository_path_v1(
            project_root=project_root,
            relative_path=paths[
                "archive_content"
            ],
        )
    )

    loaded = {
        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "index":
            _read_repository_json_v1(
                path=index_path,
            ),

        "metadata":
            _read_repository_json_v1(
                path=metadata_path,
            ),

        "content":
            _read_repository_json_v1(
                path=content_path,
            ),

        "repository_read_performed":
            True,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        loaded
    )


def verify_stored_archive_repository_v1(
    *,
    stored_repository: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        stored_repository,
        Mapping,
    ):
        raise TypeError(
            "stored_repository must be a mapping."
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

    content = content_payload[
        "content"
    ]

    calculated_checksum = hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()

    stored_checksum = content_payload[
        "archive_checksum"
    ]

    identifiers_match = (
        stored_repository[
            "archive_id"
        ]
        ==
        index_payload[
            "archive_id"
        ]
        ==
        metadata_payload[
            "archive_id"
        ]
        ==
        content_payload[
            "archive_id"
        ]
    )

    workspace_match = (
        stored_repository[
            "workspace_id"
        ]
        ==
        index_payload[
            "workspace_id"
        ]
        ==
        metadata_payload[
            "workspace_id"
        ]
        ==
        content_payload[
            "workspace_id"
        ]
    )

    verification = {
        "stored_repository_verified":
            (
                identifiers_match
                and workspace_match
                and stored_checksum
                == calculated_checksum
            ),

        "identifiers_match":
            identifiers_match,

        "workspace_match":
            workspace_match,

        "archive_checksum_matches":
            stored_checksum
            == calculated_checksum,

        "stored_archive_checksum":
            stored_checksum,

        "calculated_archive_checksum":
            calculated_checksum,

        "repository_read_performed":
            True,

        "repository_write_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        verification
    )
def execute_archive_repository_manager_v1(
    *,
    project_root: Path,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    archive_reason: str,
    archived_at: str,
    actor_type: str,
    actor_id: str,
    content: str,
) -> Mapping[str, Any]:

    repository_bundle = (
        build_archive_repository_bundle_v1(
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

    if repository_bundle[
        "certified"
    ] is not True:
        raise ValueError(
            "Archive repository bundle is not certified."
        )

    write_plan = (
        build_repository_write_plan_v1(
            bundle=repository_bundle,
        )
    )

    write_verification = (
        verify_repository_write_plan_v1(
            write_plan=write_plan,
        )
    )

    if write_verification[
        "write_plan_valid"
    ] is not True:
        raise ValueError(
            "Archive repository write-plan verification failed."
        )

    store_result = (
        store_archive_repository_v1(
            project_root=project_root,
            write_plan=write_plan,
        )
    )

    loaded_repository = (
        load_archive_repository_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            archive_id=archive_id,
        )
    )

    stored_verification = (
        verify_stored_archive_repository_v1(
            stored_repository=loaded_repository,
        )
    )

    if stored_verification[
        "stored_repository_verified"
    ] is not True:
        raise ValueError(
            "Stored Archive Repository verification failed."
        )

    result = {
        "schema_version":
            ARCHIVE_REPOSITORY_MANAGER_SCHEMA,

        "manager_version":
            ARCHIVE_REPOSITORY_MANAGER_VERSION,

        "archive_id":
            archive_id,

        "workspace_id":
            workspace_id,

        "body_id":
            body_id,

        "repository_bundle":
            repository_bundle,

        "write_plan":
            write_plan,

        "write_verification":
            write_verification,

        "store_result":
            store_result,

        "loaded_repository":
            loaded_repository,

        "stored_verification":
            stored_verification,

        "manager_completed":
            True,

        "repository_write_performed":
            store_result[
                "repository_write_performed"
            ],

        "physical_archive_performed":
            store_result[
                "physical_archive_performed"
            ],

        "stored_repository_verified":
            stored_verification[
                "stored_repository_verified"
            ],

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )


def summarize_archive_repository_manager_v1(
    *,
    manager_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        manager_result,
        Mapping,
    ):
        raise TypeError(
            "manager_result must be a mapping."
        )

    summary = {
        "archive_id":
            manager_result[
                "archive_id"
            ],

        "workspace_id":
            manager_result[
                "workspace_id"
            ],

        "body_id":
            manager_result[
                "body_id"
            ],

        "manager_completed":
            manager_result[
                "manager_completed"
            ],

        "repository_write_performed":
            manager_result[
                "repository_write_performed"
            ],

        "physical_archive_performed":
            manager_result[
                "physical_archive_performed"
            ],

        "stored_repository_verified":
            manager_result[
                "stored_repository_verified"
            ],

        "archive_index_path":
            manager_result[
                "store_result"
            ][
                "archive_index_path"
            ],

        "archive_metadata_path":
            manager_result[
                "store_result"
            ][
                "archive_metadata_path"
            ],

        "archive_content_path":
            manager_result[
                "store_result"
            ][
                "archive_content_path"
            ],

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        summary
    )
# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "ARCHIVE_REPOSITORY_MANAGER_VERSION",
    "ARCHIVE_REPOSITORY_MANAGER_SCHEMA",
    "ARCHIVE_DIRECTORY_NAME",
    "ARCHIVE_INDEX_FILENAME",
    "ARCHIVE_METADATA_FILENAME",
    "ARCHIVE_CONTENT_FILENAME",
    "calculate_repository_checksum_v1",
    "build_repository_paths_v1",
    "create_repository_descriptor_v1",
    "build_repository_write_plan_v1",
    "verify_repository_write_plan_v1",
    "store_archive_repository_v1",
    "load_archive_repository_v1",
    "verify_stored_archive_repository_v1",
    "execute_archive_repository_manager_v1",
    "summarize_archive_repository_manager_v1",
]


if __name__ == "__main__":

    project_root = Path(
        r"C:\Users\HP\Documents\LinkCraftor"
    ).resolve()

    result = (
        execute_archive_repository_manager_v1(
            project_root=project_root,
            archive_id="archive_repository_manager_demo",
            workspace_id="ws_archive_repository_manager_demo",
            body_id="body_archive_repository_manager_demo",
            archive_reason="Archive Repository Manager self-test.",
            archived_at="2026-08-04T00:00:00+00:00",
            actor_type="SYSTEM",
            actor_id="archive_repository_manager_self_test",
            content="Archive Repository Manager verification content.",
        )
    )

    summary = (
        summarize_archive_repository_manager_v1(
            manager_result=result,
        )
    )

    print(
        "Archive Repository Manager completed successfully."
    )

    print(
        json.dumps(
            dict(
                summary
            ),
            indent=4,
            default=dict,
        )
    )
