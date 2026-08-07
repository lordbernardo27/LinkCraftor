from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_VERSION = "1.0"

BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_SCHEMA = (
    "body_store_archive_recovery_verifier.v1"
)


class ArchiveRecoveryVerificationError(
    ValueError
):
    """Raised when an archive recovery package fails verification."""


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
        raise ArchiveRecoveryVerificationError(
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
        raise ArchiveRecoveryVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ArchiveRecoveryVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_recovery_verification_checksum_v1(
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
def verify_recovery_bundle_structure_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle = _require_mapping(
        recovery_bundle,
        field_name="recovery_bundle",
    )

    required_sections = (
        "recovery_plan",
        "execution_package",
        "certification",
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


def verify_recovery_bundle_identity_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    structure = (
        verify_recovery_bundle_structure_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    if structure[
        "structure_valid"
    ] is not True:
        raise ArchiveRecoveryVerificationError(
            "Recovery bundle structure is incomplete."
        )

    recovery_plan = recovery_bundle[
        "recovery_plan"
    ]

    execution_package = recovery_bundle[
        "execution_package"
    ]

    certification = recovery_bundle[
        "certification"
    ]

    recovery_request = recovery_plan[
        "recovery_request"
    ]

    archive_id_matches = (
        recovery_request[
            "archive_id"
        ]
        == execution_package[
            "archive_id"
        ]
        == certification[
            "archive_id"
        ]
    )

    workspace_id_matches = (
        recovery_request[
            "workspace_id"
        ]
        == execution_package[
            "workspace_id"
        ]
        == certification[
            "workspace_id"
        ]
    )

    body_id_matches = (
        recovery_request[
            "body_id"
        ]
        == execution_package[
            "body_id"
        ]
        == certification[
            "body_id"
        ]
    )

    lifecycle_record_id_matches = (
        recovery_request[
            "lifecycle_record_id"
        ]
        == execution_package[
            "lifecycle_record_id"
        ]
        == certification[
            "lifecycle_record_id"
        ]
    )

    recovery_plan_id_matches = (
        recovery_plan[
            "recovery_plan_id"
        ]
        == execution_package[
            "recovery_plan_id"
        ]
        == certification[
            "recovery_plan_id"
        ]
    )

    recovery_request_id_matches = (
        recovery_request[
            "recovery_request_id"
        ]
        == execution_package[
            "recovery_request_id"
        ]
        == certification[
            "recovery_request_id"
        ]
    )

    result = {
        "archive_id_matches":
            archive_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "body_id_matches":
            body_id_matches,

        "lifecycle_record_id_matches":
            lifecycle_record_id_matches,

        "recovery_plan_id_matches":
            recovery_plan_id_matches,

        "recovery_request_id_matches":
            recovery_request_id_matches,

        "identity_verified":
            all(
                (
                    archive_id_matches,
                    workspace_id_matches,
                    body_id_matches,
                    lifecycle_record_id_matches,
                    recovery_plan_id_matches,
                    recovery_request_id_matches,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_recovery_content_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    execution_package = recovery_bundle[
        "execution_package"
    ]

    body_store_payload = execution_package[
        "body_store_payload"
    ]

    content = _require_string(
        body_store_payload[
            "content"
        ],
        field_name="content",
    )

    stored_checksum = _require_string(
        body_store_payload[
            "content_checksum"
        ],
        field_name="content_checksum",
    )

    calculated_checksum = hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()

    content_length_matches = (
        body_store_payload[
            "content_length"
        ]
        == len(
            content
        )
    )

    checksum_matches = (
        stored_checksum
        == calculated_checksum
    )

    archive_source_present = bool(
        body_store_payload.get(
            "source_archive_id"
        )
    )

    lifecycle_source_present = bool(
        body_store_payload.get(
            "source_lifecycle_record_id"
        )
    )

    result = {
        "content_length_matches":
            content_length_matches,

        "checksum_matches":
            checksum_matches,

        "archive_source_present":
            archive_source_present,

        "lifecycle_source_present":
            lifecycle_source_present,

        "stored_checksum":
            stored_checksum,

        "calculated_checksum":
            calculated_checksum,

        "content_verified":
            all(
                (
                    content_length_matches,
                    checksum_matches,
                    archive_source_present,
                    lifecycle_source_present,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_recovery_transition_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    execution_package = recovery_bundle[
        "execution_package"
    ]

    transition_request = execution_package[
        "lifecycle_transition_request"
    ]

    current_state_valid = (
        transition_request[
            "current_state"
        ]
        == "ARCHIVED"
    )

    target_state_valid = (
        transition_request[
            "target_state"
        ]
        == "ACTIVE"
    )

    workspace_id_matches = (
        transition_request[
            "workspace_id"
        ]
        == execution_package[
            "workspace_id"
        ]
    )

    body_id_matches = (
        transition_request[
            "body_id"
        ]
        == execution_package[
            "body_id"
        ]
    )

    lifecycle_record_id_matches = (
        transition_request[
            "lifecycle_record_id"
        ]
        == execution_package[
            "lifecycle_record_id"
        ]
    )

    actor_present = (
        bool(
            transition_request.get(
                "actor_type"
            )
        )
        and bool(
            transition_request.get(
                "actor_id"
            )
        )
    )

    reason_present = bool(
        transition_request.get(
            "reason"
        )
    )

    requested_at_present = bool(
        transition_request.get(
            "requested_at"
        )
    )

    result = {
        "current_state_valid":
            current_state_valid,

        "target_state_valid":
            target_state_valid,

        "workspace_id_matches":
            workspace_id_matches,

        "body_id_matches":
            body_id_matches,

        "lifecycle_record_id_matches":
            lifecycle_record_id_matches,

        "actor_present":
            actor_present,

        "reason_present":
            reason_present,

        "requested_at_present":
            requested_at_present,

        "transition_verified":
            all(
                (
                    current_state_valid,
                    target_state_valid,
                    workspace_id_matches,
                    body_id_matches,
                    lifecycle_record_id_matches,
                    actor_present,
                    reason_present,
                    requested_at_present,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_recovery_workspace_isolation_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    recovery_plan = recovery_bundle[
        "recovery_plan"
    ]

    execution_package = recovery_bundle[
        "execution_package"
    ]

    certification = recovery_bundle[
        "certification"
    ]

    request = recovery_plan[
        "recovery_request"
    ]

    repository_verification = recovery_plan[
        "repository_verification"
    ]

    workspace_id = request[
        "workspace_id"
    ]

    request_workspace_matches = (
        workspace_id
        == execution_package[
            "workspace_id"
        ]
    )

    certification_workspace_matches = (
        workspace_id
        == certification[
            "workspace_id"
        ]
    )

    repository_workspace_matches = (
        workspace_id
        == repository_verification[
            "workspace_id"
        ]
    )

    repository_isolated = (
        repository_verification[
            "paths"
        ][
            "workspace_isolated"
        ]
        is True
    )

    result = {
        "request_workspace_matches":
            request_workspace_matches,

        "certification_workspace_matches":
            certification_workspace_matches,

        "repository_workspace_matches":
            repository_workspace_matches,

        "repository_isolated":
            repository_isolated,

        "workspace_isolation_verified":
            all(
                (
                    request_workspace_matches,
                    certification_workspace_matches,
                    repository_workspace_matches,
                    repository_isolated,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_archive_recovery_bundle_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    structure = (
        verify_recovery_bundle_structure_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    identity = (
        verify_recovery_bundle_identity_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    content = (
        verify_recovery_content_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    transition = (
        verify_recovery_transition_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    workspace_isolation = (
        verify_recovery_workspace_isolation_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    verification_material = {
        "recovery_execution_id":
            recovery_bundle[
                "execution_package"
            ][
                "recovery_execution_id"
            ],

        "recovery_plan_id":
            recovery_bundle[
                "execution_package"
            ][
                "recovery_plan_id"
            ],

        "recovery_request_id":
            recovery_bundle[
                "execution_package"
            ][
                "recovery_request_id"
            ],

        "content_checksum":
            content[
                "calculated_checksum"
            ],
    }

    verification_id = (
        "body_store_archive_recovery_verification_"
        + calculate_recovery_verification_checksum_v1(
            payload=verification_material,
        )
    )

    result = {
        "schema_version":
            BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_VERSION,

        "verification_id":
            verification_id,

        "structure":
            structure,

        "identity":
            identity,

        "content":
            content,

        "transition":
            transition,

        "workspace_isolation":
            workspace_isolation,

        "recovery_verified":
            all(
                (
                    structure[
                        "structure_valid"
                    ],
                    identity[
                        "identity_verified"
                    ],
                    content[
                        "content_verified"
                    ],
                    transition[
                        "transition_verified"
                    ],
                    workspace_isolation[
                        "workspace_isolation_verified"
                    ],
                )
            ),

        "archive_read_performed":
            recovery_bundle[
                "archive_read_performed"
            ]
            is True,

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
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
def summarize_archive_recovery_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        verification_result,
        Mapping,
    ):
        raise ArchiveRecoveryVerificationError(
            "verification_result must be a mapping."
        )

    summary = {
        "verification_id":
            verification_result[
                "verification_id"
            ],

        "recovery_verified":
            verification_result[
                "recovery_verified"
            ],

        "structure_valid":
            verification_result[
                "structure"
            ][
                "structure_valid"
            ],

        "identity_verified":
            verification_result[
                "identity"
            ][
                "identity_verified"
            ],

        "content_verified":
            verification_result[
                "content"
            ][
                "content_verified"
            ],

        "transition_verified":
            verification_result[
                "transition"
            ][
                "transition_verified"
            ],

        "workspace_isolation_verified":
            verification_result[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ],

        "archive_read_performed":
            verification_result[
                "archive_read_performed"
            ],

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
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


def certify_archive_recovery_verification_v1(
    *,
    verification_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    summary = (
        summarize_archive_recovery_verification_v1(
            verification_result=verification_result,
        )
    )

    certification = {
        "certification_version":
            "body_store_archive_recovery_verifier_certification.v1",

        "verification_id":
            verification_result[
                "verification_id"
            ],

        "certified":
            verification_result[
                "recovery_verified"
            ],

        "recovery_verified":
            verification_result[
                "recovery_verified"
            ],

        "summary":
            summary,

        "structure":
            verification_result[
                "structure"
            ],

        "identity":
            verification_result[
                "identity"
            ],

        "content":
            verification_result[
                "content"
            ],

        "transition":
            verification_result[
                "transition"
            ],

        "workspace_isolation":
            verification_result[
                "workspace_isolation"
            ],

        "archive_read_performed":
            verification_result[
                "archive_read_performed"
            ],

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
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
    "BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_VERSION",
    "BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_SCHEMA",
    "ArchiveRecoveryVerificationError",
    "calculate_recovery_verification_checksum_v1",
    "verify_recovery_bundle_structure_v1",
    "verify_recovery_bundle_identity_v1",
    "verify_recovery_content_v1",
    "verify_recovery_transition_v1",
    "verify_recovery_workspace_isolation_v1",
    "verify_archive_recovery_bundle_v1",
    "summarize_archive_recovery_verification_v1",
    "certify_archive_recovery_verification_v1",
]
