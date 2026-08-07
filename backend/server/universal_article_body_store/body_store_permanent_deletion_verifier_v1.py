from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_PERMANENT_DELETION_VERIFIER_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_VERIFIER_SCHEMA = (
    "body_store_permanent_deletion_verifier.v1"
)


class PermanentDeletionVerificationError(
    ValueError
):
    """Raised when permanent deletion verification fails."""


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
        raise PermanentDeletionVerificationError(
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
        raise PermanentDeletionVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_permanent_deletion_verification_checksum_v1(
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
def verify_permanent_deletion_bundle_structure_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle = _require_mapping(
        deletion_bundle,
        field_name="deletion_bundle",
    )

    required_sections = (
        "deletion_plan",
        "execution_package",
        "deletion_result",
        "result_verification",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in bundle
    )

    result = {
        "structure_valid":
            not missing_sections,

        "missing_sections":
            missing_sections,

        "required_sections":
            required_sections,
    }

    return _freeze(
        result
    )


def verify_permanent_deletion_identity_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    structure = (
        verify_permanent_deletion_bundle_structure_v1(
            deletion_bundle=deletion_bundle,
        )
    )

    if structure[
        "structure_valid"
    ] is not True:
        raise PermanentDeletionVerificationError(
            "Permanent deletion bundle structure is incomplete."
        )

    deletion_plan = deletion_bundle[
        "deletion_plan"
    ]

    execution_package = deletion_bundle[
        "execution_package"
    ]

    deletion_result = deletion_bundle[
        "deletion_result"
    ]

    deletion_request = deletion_plan[
        "deletion_request"
    ]

    deletion_plan_id_matches = (
        deletion_plan[
            "deletion_plan_id"
        ]
        == execution_package[
            "deletion_plan_id"
        ]
        == deletion_result[
            "deletion_plan_id"
        ]
    )

    deletion_request_id_matches = (
        deletion_request[
            "deletion_request_id"
        ]
        == execution_package[
            "deletion_request_id"
        ]
        == deletion_result[
            "deletion_request_id"
        ]
    )

    archive_id_matches = (
        deletion_request[
            "archive_id"
        ]
        == execution_package[
            "archive_id"
        ]
        == deletion_result[
            "archive_id"
        ]
    )

    workspace_id_matches = (
        deletion_request[
            "workspace_id"
        ]
        == execution_package[
            "workspace_id"
        ]
        == deletion_result[
            "workspace_id"
        ]
    )

    body_id_matches = (
        deletion_request[
            "body_id"
        ]
        == execution_package[
            "body_id"
        ]
        == deletion_result[
            "body_id"
        ]
    )

    lifecycle_record_id_matches = (
        deletion_request[
            "lifecycle_record_id"
        ]
        == execution_package[
            "lifecycle_record_id"
        ]
        == deletion_result[
            "lifecycle_record_id"
        ]
    )

    result = {
        "deletion_plan_id_matches":
            deletion_plan_id_matches,

        "deletion_request_id_matches":
            deletion_request_id_matches,

        "archive_id_matches":
            archive_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "body_id_matches":
            body_id_matches,

        "lifecycle_record_id_matches":
            lifecycle_record_id_matches,

        "identity_verified":
            all(
                (
                    deletion_plan_id_matches,
                    deletion_request_id_matches,
                    archive_id_matches,
                    workspace_id_matches,
                    body_id_matches,
                    lifecycle_record_id_matches,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_permanent_deletion_boundaries_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    deletion_request = deletion_bundle[
        "deletion_plan"
    ][
        "deletion_request"
    ]

    result = {
        "retention_expired":
            deletion_request[
                "retention_expired"
            ]
            is True,

        "deletion_eligible":
            deletion_request[
                "deletion_eligible"
            ]
            is True,

        "legal_hold_inactive":
            deletion_request[
                "legal_hold_active"
            ]
            is False,

        "archive_verified":
            deletion_request[
                "archive_verified"
            ]
            is True,

        "recovery_closed":
            deletion_request[
                "recovery_closed"
            ]
            is True,
    }

    result[
        "boundaries_verified"
    ] = all(
        result.values()
    )

    return _freeze(
        result
    )
def verify_permanent_deletion_filesystem_result_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    deletion_result = deletion_bundle[
        "deletion_result"
    ]

    archive_removed = (
        deletion_result[
            "archive_exists_after"
        ]
        is False
    )

    body_store_removed_or_absent = (
        deletion_result[
            "body_store_exists_after"
        ]
        is False
    )

    lifecycle_preserved = (
        deletion_result[
            "lifecycle_exists_after"
        ]
        is True
    )

    archive_delete_confirmed = (
        deletion_result[
            "archive_delete_performed"
        ]
        is True
    )

    lifecycle_transition_confirmed = (
        deletion_result[
            "lifecycle_transition_performed"
        ]
        is True
    )

    deletion_status_valid = (
        deletion_result[
            "deletion_status"
        ]
        == "DELETED"
    )

    result = {
        "archive_removed":
            archive_removed,

        "body_store_removed_or_absent":
            body_store_removed_or_absent,

        "lifecycle_preserved":
            lifecycle_preserved,

        "archive_delete_confirmed":
            archive_delete_confirmed,

        "lifecycle_transition_confirmed":
            lifecycle_transition_confirmed,

        "deletion_status_valid":
            deletion_status_valid,

        "filesystem_result_verified":
            all(
                (
                    archive_removed,
                    body_store_removed_or_absent,
                    lifecycle_preserved,
                    archive_delete_confirmed,
                    lifecycle_transition_confirmed,
                    deletion_status_valid,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_permanent_deletion_lifecycle_v1(
    *,
    project_root: Path,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    deletion_result = deletion_bundle[
        "deletion_result"
    ]

    workspace_id = _require_string(
        deletion_result[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    lifecycle_record_id = _require_string(
        deletion_result[
            "lifecycle_record_id"
        ],
        field_name="lifecycle_record_id",
    )

    lifecycle_path = (
        project_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
        / workspace_id
        / (
            lifecycle_record_id
            + ".json"
        )
    ).resolve()

    if not lifecycle_path.is_file():
        raise PermanentDeletionVerificationError(
            "Permanent deletion lifecycle record was not preserved."
        )

    lifecycle_payload = json.loads(
        lifecycle_path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        lifecycle_payload,
        dict,
    ):
        raise PermanentDeletionVerificationError(
            "Lifecycle record must contain a JSON object."
        )

    state_valid = (
        lifecycle_payload.get(
            "state"
        )
        == "PERMANENTLY_DELETED"
    )

    lifecycle_state_valid = (
        lifecycle_payload.get(
            "lifecycle_state"
        )
        == "PERMANENTLY_DELETED"
    )

    permanent_deletion_marker_valid = (
        lifecycle_payload.get(
            "permanent_deletion"
        )
        is True
    )

    execution_id_matches = (
        lifecycle_payload.get(
            "deletion_execution_id"
        )
        == deletion_result[
            "deletion_execution_id"
        ]
    )

    result = {
        "lifecycle_path":
            lifecycle_path.as_posix(),

        "lifecycle_exists":
            True,

        "state_valid":
            state_valid,

        "lifecycle_state_valid":
            lifecycle_state_valid,

        "permanent_deletion_marker_valid":
            permanent_deletion_marker_valid,

        "execution_id_matches":
            execution_id_matches,

        "lifecycle_verified":
            all(
                (
                    state_valid,
                    lifecycle_state_valid,
                    permanent_deletion_marker_valid,
                    execution_id_matches,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_permanent_deletion_workspace_isolation_v1(
    *,
    project_root: Path,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    deletion_result = deletion_bundle[
        "deletion_result"
    ]

    workspace_id = _require_string(
        deletion_result[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    deletion_plan = deletion_bundle[
        "deletion_plan"
    ]

    archive_relative_path = _require_string(
        deletion_plan[
            "archive_relative_path"
        ],
        field_name="archive_relative_path",
    )

    body_store_relative_path = _require_string(
        deletion_plan[
            "body_store_relative_path"
        ],
        field_name="body_store_relative_path",
    )

    lifecycle_relative_path = _require_string(
        deletion_plan[
            "lifecycle_relative_path"
        ],
        field_name="lifecycle_relative_path",
    )

    expected_workspace_segment = (
        "/"
        + workspace_id
        + "/"
    )

    archive_path_isolated = (
        expected_workspace_segment
        in (
            "/"
            + archive_relative_path.replace(
                "\\",
                "/",
            )
            + "/"
        )
    )

    body_store_path_isolated = (
        expected_workspace_segment
        in (
            "/"
            + body_store_relative_path.replace(
                "\\",
                "/",
            )
            + "/"
        )
    )

    lifecycle_path_isolated = (
        expected_workspace_segment
        in (
            "/"
            + lifecycle_relative_path.replace(
                "\\",
                "/",
            )
            + "/"
        )
    )

    project_root_resolved = (
        project_root.resolve()
    )

    result = {
        "project_root":
            project_root_resolved.as_posix(),

        "workspace_id":
            workspace_id,

        "archive_path_isolated":
            archive_path_isolated,

        "body_store_path_isolated":
            body_store_path_isolated,

        "lifecycle_path_isolated":
            lifecycle_path_isolated,

        "workspace_isolation_verified":
            all(
                (
                    archive_path_isolated,
                    body_store_path_isolated,
                    lifecycle_path_isolated,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_permanent_deletion_bundle_v1(
    *,
    project_root: Path,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    structure = (
        verify_permanent_deletion_bundle_structure_v1(
            deletion_bundle=deletion_bundle,
        )
    )

    identity = (
        verify_permanent_deletion_identity_v1(
            deletion_bundle=deletion_bundle,
        )
    )

    boundaries = (
        verify_permanent_deletion_boundaries_v1(
            deletion_bundle=deletion_bundle,
        )
    )

    filesystem_result = (
        verify_permanent_deletion_filesystem_result_v1(
            deletion_bundle=deletion_bundle,
        )
    )

    lifecycle = (
        verify_permanent_deletion_lifecycle_v1(
            project_root=project_root,
            deletion_bundle=deletion_bundle,
        )
    )

    workspace_isolation = (
        verify_permanent_deletion_workspace_isolation_v1(
            project_root=project_root,
            deletion_bundle=deletion_bundle,
        )
    )

    deletion_result = deletion_bundle[
        "deletion_result"
    ]

    verification_material = {
        "deletion_execution_id":
            deletion_result[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            deletion_result[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            deletion_result[
                "deletion_request_id"
            ],

        "workspace_id":
            deletion_result[
                "workspace_id"
            ],

        "body_id":
            deletion_result[
                "body_id"
            ],
    }

    verification_id = (
        "body_store_permanent_deletion_verification_"
        + calculate_permanent_deletion_verification_checksum_v1(
            payload=verification_material,
        )
    )

    result = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_PERMANENT_DELETION_VERIFIER_VERSION,

        "verification_id":
            verification_id,

        "deletion_execution_id":
            deletion_result[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            deletion_result[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            deletion_result[
                "deletion_request_id"
            ],

        "archive_id":
            deletion_result[
                "archive_id"
            ],

        "workspace_id":
            deletion_result[
                "workspace_id"
            ],

        "body_id":
            deletion_result[
                "body_id"
            ],

        "lifecycle_record_id":
            deletion_result[
                "lifecycle_record_id"
            ],

        "structure":
            structure,

        "identity":
            identity,

        "boundaries":
            boundaries,

        "filesystem_result":
            filesystem_result,

        "lifecycle":
            lifecycle,

        "workspace_isolation":
            workspace_isolation,

        "deletion_verified":
            all(
                (
                    structure[
                        "structure_valid"
                    ],
                    identity[
                        "identity_verified"
                    ],
                    boundaries[
                        "boundaries_verified"
                    ],
                    filesystem_result[
                        "filesystem_result_verified"
                    ],
                    lifecycle[
                        "lifecycle_verified"
                    ],
                    workspace_isolation[
                        "workspace_isolation_verified"
                    ],
                )
            ),

        "archive_delete_performed":
            deletion_result[
                "archive_delete_performed"
            ]
            is True,

        "body_store_delete_performed":
            deletion_result[
                "body_store_delete_performed"
            ]
            is True,

        "lifecycle_transition_performed":
            deletion_result[
                "lifecycle_transition_performed"
            ]
            is True,

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


def summarize_permanent_deletion_verification_v1(
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

        "deletion_execution_id":
            verification[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            verification[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            verification[
                "deletion_request_id"
            ],

        "archive_id":
            verification[
                "archive_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "body_id":
            verification[
                "body_id"
            ],

        "lifecycle_record_id":
            verification[
                "lifecycle_record_id"
            ],

        "deletion_verified":
            verification[
                "deletion_verified"
            ],

        "structure_valid":
            verification[
                "structure"
            ][
                "structure_valid"
            ],

        "identity_verified":
            verification[
                "identity"
            ][
                "identity_verified"
            ],

        "boundaries_verified":
            verification[
                "boundaries"
            ][
                "boundaries_verified"
            ],

        "filesystem_result_verified":
            verification[
                "filesystem_result"
            ][
                "filesystem_result_verified"
            ],

        "lifecycle_verified":
            verification[
                "lifecycle"
            ][
                "lifecycle_verified"
            ],

        "workspace_isolation_verified":
            verification[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ],

        "archive_delete_performed":
            verification[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            verification[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            verification[
                "lifecycle_transition_performed"
            ],

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
def certify_permanent_deletion_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    verification = _require_mapping(
        verification_result,
        field_name="verification_result",
    )

    summary = (
        summarize_permanent_deletion_verification_v1(
            verification_result=verification,
        )
    )

    certification = {
        "certification_version":
            "body_store_permanent_deletion_verifier_certification.v1",

        "verification_id":
            verification[
                "verification_id"
            ],

        "deletion_execution_id":
            verification[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            verification[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            verification[
                "deletion_request_id"
            ],

        "archive_id":
            verification[
                "archive_id"
            ],

        "workspace_id":
            verification[
                "workspace_id"
            ],

        "body_id":
            verification[
                "body_id"
            ],

        "lifecycle_record_id":
            verification[
                "lifecycle_record_id"
            ],

        "certified":
            verification[
                "deletion_verified"
            ]
            is True,

        "deletion_verified":
            verification[
                "deletion_verified"
            ],

        "summary":
            summary,

        "structure":
            verification[
                "structure"
            ],

        "identity":
            verification[
                "identity"
            ],

        "boundaries":
            verification[
                "boundaries"
            ],

        "filesystem_result":
            verification[
                "filesystem_result"
            ],

        "lifecycle":
            verification[
                "lifecycle"
            ],

        "workspace_isolation":
            verification[
                "workspace_isolation"
            ],

        "archive_delete_performed":
            verification[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            verification[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            verification[
                "lifecycle_transition_performed"
            ],

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
    "BODY_STORE_PERMANENT_DELETION_VERIFIER_VERSION",
    "BODY_STORE_PERMANENT_DELETION_VERIFIER_SCHEMA",
    "PermanentDeletionVerificationError",
    "calculate_permanent_deletion_verification_checksum_v1",
    "verify_permanent_deletion_bundle_structure_v1",
    "verify_permanent_deletion_identity_v1",
    "verify_permanent_deletion_boundaries_v1",
    "verify_permanent_deletion_filesystem_result_v1",
    "verify_permanent_deletion_lifecycle_v1",
    "verify_permanent_deletion_workspace_isolation_v1",
    "verify_permanent_deletion_bundle_v1",
    "summarize_permanent_deletion_verification_v1",
    "certify_permanent_deletion_verification_v1",
]
