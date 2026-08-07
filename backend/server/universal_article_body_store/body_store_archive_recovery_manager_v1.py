from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_archive_recovery_contract_v1 import (
    build_archive_recovery_request_v1,
    certify_archive_recovery_request_v1,
)

from backend.server.universal_article_body_store.body_store_archive_repository_manager_v1 import (
    load_archive_repository_v1,
)

from backend.server.universal_article_body_store.body_store_archive_repository_verifier_v1 import (
    verify_archive_repository_v1,
)


BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION = "1.0"

BODY_STORE_ARCHIVE_RECOVERY_MANAGER_SCHEMA = (
    "body_store_archive_recovery_manager.v1"
)

BODY_STORE_ARCHIVE_RECOVERY_PLAN_SCHEMA = (
    "body_store_archive_recovery_plan.v1"
)

BODY_STORE_ARCHIVE_RECOVERY_RESULT_SCHEMA = (
    "body_store_archive_recovery_result.v1"
)


class ArchiveRecoveryManagerError(
    ValueError
):
    """Raised when an archive recovery cannot proceed."""


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
        raise ArchiveRecoveryManagerError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ArchiveRecoveryManagerError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_recovery_payload_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise ArchiveRecoveryManagerError(
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
def build_archive_recovery_plan_v1(
    *,
    project_root: Path,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    recovery_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    requested_at: str,
) -> Mapping[str, Any]:

    normalized_archive_id = _require_string(
        archive_id,
        field_name="archive_id",
    )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_body_id = _require_string(
        body_id,
        field_name="body_id",
    )

    normalized_lifecycle_record_id = _require_string(
        lifecycle_record_id,
        field_name="lifecycle_record_id",
    )

    recovery_request = (
        build_archive_recovery_request_v1(
            archive_id=normalized_archive_id,
            workspace_id=normalized_workspace_id,
            body_id=normalized_body_id,
            lifecycle_record_id=normalized_lifecycle_record_id,
            source_state=source_state,
            recovery_reason=recovery_reason,
            requested_by_type=requested_by_type,
            requested_by_id=requested_by_id,
            requested_at=requested_at,
        )
    )

    request_certification = (
        certify_archive_recovery_request_v1(
            recovery_request=recovery_request,
        )
    )

    if request_certification[
        "certified"
    ] is not True:
        raise ArchiveRecoveryManagerError(
            "Archive recovery request is not certified."
        )

    repository_verification = (
        verify_archive_repository_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    if repository_verification[
        "repository_verified"
    ] is not True:
        raise ArchiveRecoveryManagerError(
            "Archive repository verification failed."
        )

    stored_repository = (
        load_archive_repository_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    stored_content = stored_repository[
        "content"
    ]

    if (
        stored_content[
            "body_id"
        ]
        != normalized_body_id
    ):
        raise ArchiveRecoveryManagerError(
            "Recovered archive body_id does not match request."
        )

    content = _require_string(
        stored_content[
            "content"
        ],
        field_name="content",
    )

    content_checksum = hashlib.sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()

    if (
        content_checksum
        != stored_content[
            "archive_checksum"
        ]
    ):
        raise ArchiveRecoveryManagerError(
            "Recovered archive content checksum does not match."
        )

    body_store_payload = {
        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "content":
            content,

        "content_length":
            len(
                content
            ),

        "content_checksum":
            content_checksum,

        "source_archive_id":
            normalized_archive_id,

        "source_lifecycle_record_id":
            normalized_lifecycle_record_id,

        "recovered_from_archive":
            True,
    }

    lifecycle_transition_request = {
        "lifecycle_record_id":
            normalized_lifecycle_record_id,

        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "current_state":
            recovery_request[
                "source_state"
            ],

        "target_state":
            recovery_request[
                "target_state"
            ],

        "reason":
            recovery_request[
                "recovery_reason"
            ],

        "actor_type":
            recovery_request[
                "requested_by_type"
            ],

        "actor_id":
            recovery_request[
                "requested_by_id"
            ],

        "requested_at":
            recovery_request[
                "requested_at"
            ],
    }

    plan_material = {
        "recovery_request_id":
            recovery_request[
                "recovery_request_id"
            ],

        "archive_id":
            normalized_archive_id,

        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "content_checksum":
            content_checksum,
    }

    recovery_plan_id = (
        "body_store_archive_recovery_plan_"
        + calculate_recovery_payload_checksum_v1(
            payload=plan_material,
        )
    )

    plan = {
        "schema_version":
            BODY_STORE_ARCHIVE_RECOVERY_PLAN_SCHEMA,

        "manager_version":
            BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION,

        "recovery_plan_id":
            recovery_plan_id,

        "recovery_request":
            recovery_request,

        "request_certification":
            request_certification,

        "repository_verification":
            repository_verification,

        "body_store_payload":
            body_store_payload,

        "lifecycle_transition_request":
            lifecycle_transition_request,

        "plan_ready":
            True,

        "archive_read_performed":
            True,

        "archive_verification_performed":
            True,

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
        plan
    )
def verify_archive_recovery_plan_v1(
    *,
    recovery_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        recovery_plan,
        Mapping,
    ):
        raise ArchiveRecoveryManagerError(
            "recovery_plan must be a mapping."
        )

    required_sections = (
        "recovery_request",
        "request_certification",
        "repository_verification",
        "body_store_payload",
        "lifecycle_transition_request",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in recovery_plan
    )

    request = recovery_plan.get(
        "recovery_request",
        {},
    )

    body_store_payload = recovery_plan.get(
        "body_store_payload",
        {},
    )

    transition_request = recovery_plan.get(
        "lifecycle_transition_request",
        {},
    )

    workspace_matches = (
        request.get(
            "workspace_id"
        )
        == body_store_payload.get(
            "workspace_id"
        )
        == transition_request.get(
            "workspace_id"
        )
    )

    body_id_matches = (
        request.get(
            "body_id"
        )
        == body_store_payload.get(
            "body_id"
        )
        == transition_request.get(
            "body_id"
        )
    )

    lifecycle_record_matches = (
        request.get(
            "lifecycle_record_id"
        )
        == body_store_payload.get(
            "source_lifecycle_record_id"
        )
        == transition_request.get(
            "lifecycle_record_id"
        )
    )

    source_state_valid = (
        transition_request.get(
            "current_state"
        )
        == "ARCHIVED"
    )

    target_state_valid = (
        transition_request.get(
            "target_state"
        )
        == "ACTIVE"
    )

    content = body_store_payload.get(
        "content"
    )

    content_valid = (
        isinstance(
            content,
            str,
        )
        and bool(
            content
        )
    )

    calculated_checksum = (
        hashlib.sha256(
            content.encode(
                "utf-8"
            )
        ).hexdigest()
        if content_valid
        else ""
    )

    checksum_matches = (
        calculated_checksum
        == body_store_payload.get(
            "content_checksum"
        )
    )

    result = {
        "plan_valid":
            all(
                (
                    not missing_sections,
                    recovery_plan.get(
                        "plan_ready"
                    )
                    is True,
                    recovery_plan[
                        "request_certification"
                    ][
                        "certified"
                    ]
                    is True,
                    recovery_plan[
                        "repository_verification"
                    ][
                        "repository_verified"
                    ]
                    is True,
                    workspace_matches,
                    body_id_matches,
                    lifecycle_record_matches,
                    source_state_valid,
                    target_state_valid,
                    content_valid,
                    checksum_matches,
                )
            ),

        "missing_sections":
            missing_sections,

        "workspace_matches":
            workspace_matches,

        "body_id_matches":
            body_id_matches,

        "lifecycle_record_matches":
            lifecycle_record_matches,

        "source_state_valid":
            source_state_valid,

        "target_state_valid":
            target_state_valid,

        "content_valid":
            content_valid,

        "checksum_matches":
            checksum_matches,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            body_store_payload.get(
                "content_checksum"
            ),

        "archive_read_performed":
            recovery_plan.get(
                "archive_read_performed"
            )
            is True,

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )


def build_archive_recovery_execution_package_v1(
    *,
    recovery_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    plan_verification = (
        verify_archive_recovery_plan_v1(
            recovery_plan=recovery_plan,
        )
    )

    if plan_verification[
        "plan_valid"
    ] is not True:
        raise ArchiveRecoveryManagerError(
            "Archive recovery plan verification failed."
        )

    request = recovery_plan[
        "recovery_request"
    ]

    body_store_payload = recovery_plan[
        "body_store_payload"
    ]

    transition_request = recovery_plan[
        "lifecycle_transition_request"
    ]

    execution_material = {
        "recovery_plan_id":
            recovery_plan[
                "recovery_plan_id"
            ],

        "recovery_request_id":
            request[
                "recovery_request_id"
            ],

        "archive_id":
            request[
                "archive_id"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "body_id":
            request[
                "body_id"
            ],

        "content_checksum":
            body_store_payload[
                "content_checksum"
            ],
    }

    recovery_execution_id = (
        "body_store_archive_recovery_execution_"
        + calculate_recovery_payload_checksum_v1(
            payload=execution_material,
        )
    )

    package = {
        "schema_version":
            BODY_STORE_ARCHIVE_RECOVERY_RESULT_SCHEMA,

        "manager_version":
            BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION,

        "recovery_execution_id":
            recovery_execution_id,

        "recovery_plan_id":
            recovery_plan[
                "recovery_plan_id"
            ],

        "recovery_request_id":
            request[
                "recovery_request_id"
            ],

        "archive_id":
            request[
                "archive_id"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "body_id":
            request[
                "body_id"
            ],

        "lifecycle_record_id":
            request[
                "lifecycle_record_id"
            ],

        "body_store_payload":
            body_store_payload,

        "lifecycle_transition_request":
            transition_request,

        "plan_verification":
            plan_verification,

        "execution_ready":
            True,

        "archive_read_performed":
            True,

        "archive_verification_performed":
            True,

        "body_store_write_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "recovery_status":
            "READY",

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        package
    )
def summarize_archive_recovery_execution_v1(
    *,
    execution_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        execution_package,
        Mapping,
    ):
        raise ArchiveRecoveryManagerError(
            "execution_package must be a mapping."
        )

    summary = {
        "recovery_execution_id":
            execution_package[
                "recovery_execution_id"
            ],

        "recovery_plan_id":
            execution_package[
                "recovery_plan_id"
            ],

        "recovery_request_id":
            execution_package[
                "recovery_request_id"
            ],

        "archive_id":
            execution_package[
                "archive_id"
            ],

        "workspace_id":
            execution_package[
                "workspace_id"
            ],

        "body_id":
            execution_package[
                "body_id"
            ],

        "lifecycle_record_id":
            execution_package[
                "lifecycle_record_id"
            ],

        "recovery_status":
            execution_package[
                "recovery_status"
            ],

        "execution_ready":
            execution_package[
                "execution_ready"
            ],

        "archive_read_performed":
            execution_package[
                "archive_read_performed"
            ],

        "archive_verification_performed":
            execution_package[
                "archive_verification_performed"
            ],

        "body_store_write_performed":
            execution_package[
                "body_store_write_performed"
            ],

        "lifecycle_transition_performed":
            execution_package[
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


def certify_archive_recovery_execution_v1(
    *,
    execution_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    summary = (
        summarize_archive_recovery_execution_v1(
            execution_package=execution_package,
        )
    )

    plan_verification = execution_package[
        "plan_verification"
    ]

    certification = {
        "certification_version":
            "body_store_archive_recovery_manager_certification.v1",

        "recovery_execution_id":
            execution_package[
                "recovery_execution_id"
            ],

        "recovery_plan_id":
            execution_package[
                "recovery_plan_id"
            ],

        "recovery_request_id":
            execution_package[
                "recovery_request_id"
            ],

        "archive_id":
            execution_package[
                "archive_id"
            ],

        "workspace_id":
            execution_package[
                "workspace_id"
            ],

        "body_id":
            execution_package[
                "body_id"
            ],

        "lifecycle_record_id":
            execution_package[
                "lifecycle_record_id"
            ],

        "certified":
            (
                execution_package[
                    "execution_ready"
                ]
                is True
                and plan_verification[
                    "plan_valid"
                ]
                is True
            ),

        "recovery_status":
            execution_package[
                "recovery_status"
            ],

        "summary":
            summary,

        "plan_verification":
            plan_verification,

        "archive_read_performed":
            True,

        "archive_verification_performed":
            True,

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


def build_archive_recovery_manager_bundle_v1(
    *,
    project_root: Path,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    recovery_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    requested_at: str,
) -> Mapping[str, Any]:

    recovery_plan = (
        build_archive_recovery_plan_v1(
            project_root=project_root,
            archive_id=archive_id,
            workspace_id=workspace_id,
            body_id=body_id,
            lifecycle_record_id=lifecycle_record_id,
            source_state=source_state,
            recovery_reason=recovery_reason,
            requested_by_type=requested_by_type,
            requested_by_id=requested_by_id,
            requested_at=requested_at,
        )
    )

    execution_package = (
        build_archive_recovery_execution_package_v1(
            recovery_plan=recovery_plan,
        )
    )

    certification = (
        certify_archive_recovery_execution_v1(
            execution_package=execution_package,
        )
    )

    bundle = {
        "bundle_version":
            "body_store_archive_recovery_manager_bundle.v1",

        "manager_version":
            BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION,

        "recovery_plan":
            recovery_plan,

        "execution_package":
            execution_package,

        "certification":
            certification,

        "bundle_complete":
            True,

        "certified":
            certification[
                "certified"
            ],

        "recovery_status":
            execution_package[
                "recovery_status"
            ],

        "archive_read_performed":
            True,

        "archive_verification_performed":
            True,

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
        bundle
    )
def verify_archive_recovery_manager_bundle_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        recovery_bundle,
        Mapping,
    ):
        raise ArchiveRecoveryManagerError(
            "recovery_bundle must be a mapping."
        )

    required_sections = (
        "recovery_plan",
        "execution_package",
        "certification",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in recovery_bundle
    )

    recovery_plan = recovery_bundle.get(
        "recovery_plan",
        {},
    )

    execution_package = recovery_bundle.get(
        "execution_package",
        {},
    )

    certification = recovery_bundle.get(
        "certification",
        {},
    )

    plan_id_matches = (
        recovery_plan.get(
            "recovery_plan_id"
        )
        == execution_package.get(
            "recovery_plan_id"
        )
        == certification.get(
            "recovery_plan_id"
        )
    )

    request_id_matches = (
        recovery_plan.get(
            "recovery_request",
            {},
        ).get(
            "recovery_request_id"
        )
        == execution_package.get(
            "recovery_request_id"
        )
        == certification.get(
            "recovery_request_id"
        )
    )

    archive_id_matches = (
        recovery_plan.get(
            "recovery_request",
            {},
        ).get(
            "archive_id"
        )
        == execution_package.get(
            "archive_id"
        )
        == certification.get(
            "archive_id"
        )
    )

    workspace_id_matches = (
        recovery_plan.get(
            "recovery_request",
            {},
        ).get(
            "workspace_id"
        )
        == execution_package.get(
            "workspace_id"
        )
        == certification.get(
            "workspace_id"
        )
    )

    body_id_matches = (
        recovery_plan.get(
            "recovery_request",
            {},
        ).get(
            "body_id"
        )
        == execution_package.get(
            "body_id"
        )
        == certification.get(
            "body_id"
        )
    )

    result = {
        "bundle_valid":
            all(
                (
                    not missing_sections,
                    recovery_bundle.get(
                        "bundle_complete"
                    )
                    is True,
                    recovery_bundle.get(
                        "certified"
                    )
                    is True,
                    recovery_plan.get(
                        "plan_ready"
                    )
                    is True,
                    execution_package.get(
                        "execution_ready"
                    )
                    is True,
                    certification.get(
                        "certified"
                    )
                    is True,
                    plan_id_matches,
                    request_id_matches,
                    archive_id_matches,
                    workspace_id_matches,
                    body_id_matches,
                )
            ),

        "missing_sections":
            missing_sections,

        "plan_id_matches":
            plan_id_matches,

        "request_id_matches":
            request_id_matches,

        "archive_id_matches":
            archive_id_matches,

        "workspace_id_matches":
            workspace_id_matches,

        "body_id_matches":
            body_id_matches,

        "archive_read_performed":
            recovery_bundle.get(
                "archive_read_performed"
            )
            is True,

        "archive_verification_performed":
            recovery_bundle.get(
                "archive_verification_performed"
            )
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


def summarize_archive_recovery_manager_bundle_v1(
    *,
    recovery_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    bundle_verification = (
        verify_archive_recovery_manager_bundle_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    execution_package = recovery_bundle[
        "execution_package"
    ]

    summary = {
        "recovery_execution_id":
            execution_package[
                "recovery_execution_id"
            ],

        "recovery_plan_id":
            execution_package[
                "recovery_plan_id"
            ],

        "recovery_request_id":
            execution_package[
                "recovery_request_id"
            ],

        "archive_id":
            execution_package[
                "archive_id"
            ],

        "workspace_id":
            execution_package[
                "workspace_id"
            ],

        "body_id":
            execution_package[
                "body_id"
            ],

        "lifecycle_record_id":
            execution_package[
                "lifecycle_record_id"
            ],

        "recovery_status":
            recovery_bundle[
                "recovery_status"
            ],

        "bundle_complete":
            recovery_bundle[
                "bundle_complete"
            ],

        "bundle_certified":
            recovery_bundle[
                "certified"
            ],

        "bundle_valid":
            bundle_verification[
                "bundle_valid"
            ],

        "archive_read_performed":
            True,

        "archive_verification_performed":
            True,

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
# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION",
    "BODY_STORE_ARCHIVE_RECOVERY_MANAGER_SCHEMA",
    "BODY_STORE_ARCHIVE_RECOVERY_PLAN_SCHEMA",
    "BODY_STORE_ARCHIVE_RECOVERY_RESULT_SCHEMA",
    "ArchiveRecoveryManagerError",
    "calculate_recovery_payload_checksum_v1",
    "build_archive_recovery_plan_v1",
    "verify_archive_recovery_plan_v1",
    "build_archive_recovery_execution_package_v1",
    "summarize_archive_recovery_execution_v1",
    "certify_archive_recovery_execution_v1",
    "build_archive_recovery_manager_bundle_v1",
    "verify_archive_recovery_manager_bundle_v1",
    "summarize_archive_recovery_manager_bundle_v1",
]


if __name__ == "__main__":
    project_root = Path(
        r"C:\Users\HP\Documents\LinkCraftor"
    ).resolve()

    bundle = (
        build_archive_recovery_manager_bundle_v1(
            project_root=project_root,
            archive_id="archive_recovery_manager_demo",
            workspace_id="ws_archive_recovery_demo",
            body_id="body_archive_recovery_demo",
            lifecycle_record_id="body_lifecycle_recovery_demo",
            source_state="ARCHIVED",
            recovery_reason="Archive Recovery Manager self-test.",
            requested_by_type="SYSTEM",
            requested_by_id="archive_recovery_manager_self_test",
            requested_at="2026-08-04T01:00:00+00:00",
        )
    )

    summary = (
        summarize_archive_recovery_manager_bundle_v1(
            recovery_bundle=bundle,
        )
    )

    print(
        "Archive Recovery Manager bundle created successfully."
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
    