from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_archive_repository_verifier_v1 import (
    verify_archive_repository_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_contract_v1 import (
    build_permanent_deletion_request_v1,
    certify_permanent_deletion_request_v1,
)


BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_MANAGER_SCHEMA = (
    "body_store_permanent_deletion_manager.v1"
)

BODY_STORE_PERMANENT_DELETION_PLAN_SCHEMA = (
    "body_store_permanent_deletion_plan.v1"
)

BODY_STORE_PERMANENT_DELETION_RESULT_SCHEMA = (
    "body_store_permanent_deletion_result.v1"
)


class PermanentDeletionManagerError(
    ValueError
):
    """Raised when permanent deletion cannot proceed."""


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
                key: _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
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
        raise PermanentDeletionManagerError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionManagerError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_permanent_deletion_payload_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "payload must be a mapping."
        )

    serialized = json.dumps(
        dict(payload),
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


def _resolve_managed_path_v1(
    *,
    project_root: Path,
    relative_path: str,
    managed_root_name: str,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise PermanentDeletionManagerError(
            "project_root must be a Path."
        )

    normalized_relative_path = _require_string(
        relative_path,
        field_name="relative_path",
    )

    normalized_managed_root_name = _require_string(
        managed_root_name,
        field_name="managed_root_name",
    )

    managed_root = (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / normalized_managed_root_name
    ).resolve()

    resolved_path = (
        managed_root
        / Path(
            normalized_relative_path
        )
    ).resolve()

    try:
        resolved_path.relative_to(
            managed_root
        )

    except ValueError as exc:
        raise PermanentDeletionManagerError(
            "Deletion path escaped its managed root."
        ) from exc

    if resolved_path == managed_root:
        raise PermanentDeletionManagerError(
            "Deletion cannot target the managed root itself."
        )

    return resolved_path
def build_permanent_deletion_plan_v1(
    *,
    project_root: Path,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    deletion_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    retention_expired: bool,
    deletion_eligible: bool,
    legal_hold_active: bool,
    recovery_closed: bool,
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

    repository_verification = (
        verify_archive_repository_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            archive_id=normalized_archive_id,
        )
    )

    archive_verified = (
        repository_verification[
            "repository_verified"
        ]
        is True
    )

    deletion_request = (
        build_permanent_deletion_request_v1(
            archive_id=normalized_archive_id,
            workspace_id=normalized_workspace_id,
            body_id=normalized_body_id,
            lifecycle_record_id=lifecycle_record_id,
            source_state=source_state,
            deletion_reason=deletion_reason,
            requested_by_type=requested_by_type,
            requested_by_id=requested_by_id,
            retention_expired=retention_expired,
            deletion_eligible=deletion_eligible,
            legal_hold_active=legal_hold_active,
            archive_verified=archive_verified,
            recovery_closed=recovery_closed,
            requested_at=requested_at,
        )
    )

    request_certification = (
        certify_permanent_deletion_request_v1(
            deletion_request=deletion_request,
        )
    )

    if request_certification[
        "certified"
    ] is not True:
        raise PermanentDeletionManagerError(
            "Permanent deletion request is not certified."
        )

    archive_relative_path = (
        Path(
            "archive"
        )
        / normalized_workspace_id
        / normalized_archive_id
    ).as_posix()

    body_store_relative_path = (
        Path(
            normalized_workspace_id
        )
        / "bodies"
        / (
            normalized_body_id
            + ".json"
        )
    ).as_posix()

    lifecycle_relative_path = (
        Path(
            normalized_workspace_id
        )
        / (
            lifecycle_record_id
            + ".json"
        )
    ).as_posix()

    plan_material = {
        "deletion_request_id":
            deletion_request[
                "deletion_request_id"
            ],

        "archive_id":
            normalized_archive_id,

        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "lifecycle_record_id":
            lifecycle_record_id,
    }

    deletion_plan_id = (
        "body_store_permanent_deletion_plan_"
        + calculate_permanent_deletion_payload_checksum_v1(
            payload=plan_material,
        )
    )

    plan = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_PLAN_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION,

        "deletion_plan_id":
            deletion_plan_id,

        "deletion_request":
            deletion_request,

        "request_certification":
            request_certification,

        "repository_verification":
            repository_verification,

        "archive_relative_path":
            archive_relative_path,

        "body_store_relative_path":
            body_store_relative_path,

        "lifecycle_relative_path":
            lifecycle_relative_path,

        "plan_ready":
            True,

        "archive_delete_performed":
            False,

        "body_store_delete_performed":
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
def verify_permanent_deletion_plan_v1(
    *,
    deletion_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        deletion_plan,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "deletion_plan must be a mapping."
        )

    required_sections = (
        "deletion_request",
        "request_certification",
        "repository_verification",
        "archive_relative_path",
        "body_store_relative_path",
        "lifecycle_relative_path",
    )

    missing_sections = tuple(
        section
        for section in required_sections
        if section not in deletion_plan
    )

    deletion_request = deletion_plan.get(
        "deletion_request",
        {},
    )

    request_certification = deletion_plan.get(
        "request_certification",
        {},
    )

    repository_verification = deletion_plan.get(
        "repository_verification",
        {},
    )

    identifiers_match = (
        deletion_request.get(
            "archive_id"
        )
        == repository_verification.get(
            "archive_id"
        )
        and deletion_request.get(
            "workspace_id"
        )
        == repository_verification.get(
            "workspace_id"
        )
    )

    request_ready = (
        deletion_request.get(
            "deletion_ready"
        )
        is True
        and deletion_request.get(
            "deletion_status"
        )
        == "READY"
    )

    request_certified = (
        request_certification.get(
            "certified"
        )
        is True
    )

    repository_verified = (
        repository_verification.get(
            "repository_verified"
        )
        is True
    )

    archive_path_present = bool(
        deletion_plan.get(
            "archive_relative_path"
        )
    )

    body_store_path_present = bool(
        deletion_plan.get(
            "body_store_relative_path"
        )
    )

    lifecycle_path_present = bool(
        deletion_plan.get(
            "lifecycle_relative_path"
        )
    )

    result = {
        "plan_valid":
            all(
                (
                    not missing_sections,
                    deletion_plan.get(
                        "plan_ready"
                    )
                    is True,
                    identifiers_match,
                    request_ready,
                    request_certified,
                    repository_verified,
                    archive_path_present,
                    body_store_path_present,
                    lifecycle_path_present,
                )
            ),

        "missing_sections":
            missing_sections,

        "identifiers_match":
            identifiers_match,

        "request_ready":
            request_ready,

        "request_certified":
            request_certified,

        "repository_verified":
            repository_verified,

        "archive_path_present":
            archive_path_present,

        "body_store_path_present":
            body_store_path_present,

        "lifecycle_path_present":
            lifecycle_path_present,

        "archive_delete_performed":
            False,

        "body_store_delete_performed":
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


def build_permanent_deletion_execution_package_v1(
    *,
    deletion_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    plan_verification = (
        verify_permanent_deletion_plan_v1(
            deletion_plan=deletion_plan,
        )
    )

    if plan_verification[
        "plan_valid"
    ] is not True:
        raise PermanentDeletionManagerError(
            "Permanent deletion plan verification failed."
        )

    deletion_request = deletion_plan[
        "deletion_request"
    ]

    execution_material = {
        "deletion_plan_id":
            deletion_plan[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            deletion_request[
                "deletion_request_id"
            ],

        "archive_id":
            deletion_request[
                "archive_id"
            ],

        "workspace_id":
            deletion_request[
                "workspace_id"
            ],

        "body_id":
            deletion_request[
                "body_id"
            ],
    }

    deletion_execution_id = (
        "body_store_permanent_deletion_execution_"
        + calculate_permanent_deletion_payload_checksum_v1(
            payload=execution_material,
        )
    )

    package = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_RESULT_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION,

        "deletion_execution_id":
            deletion_execution_id,

        "deletion_plan_id":
            deletion_plan[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            deletion_request[
                "deletion_request_id"
            ],

        "archive_id":
            deletion_request[
                "archive_id"
            ],

        "workspace_id":
            deletion_request[
                "workspace_id"
            ],

        "body_id":
            deletion_request[
                "body_id"
            ],

        "lifecycle_record_id":
            deletion_request[
                "lifecycle_record_id"
            ],

        "archive_relative_path":
            deletion_plan[
                "archive_relative_path"
            ],

        "body_store_relative_path":
            deletion_plan[
                "body_store_relative_path"
            ],

        "lifecycle_relative_path":
            deletion_plan[
                "lifecycle_relative_path"
            ],

        "plan_verification":
            plan_verification,

        "execution_ready":
            True,

        "deletion_status":
            "READY",

        "archive_delete_performed":
            False,

        "body_store_delete_performed":
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
        package
    )
def execute_permanent_deletion_v1(
    *,
    project_root: Path,
    execution_package: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        execution_package,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "execution_package must be a mapping."
        )

    if execution_package.get(
        "execution_ready"
    ) is not True:
        raise PermanentDeletionManagerError(
            "Permanent deletion execution package is not ready."
        )

    archive_path = (
        _resolve_managed_path_v1(
            project_root=project_root,
            relative_path=execution_package[
                "archive_relative_path"
            ],
            managed_root_name=(
                "universal_article_body_store_archive"
            ),
        )
    )

    body_store_path = (
        _resolve_managed_path_v1(
            project_root=project_root,
            relative_path=execution_package[
                "body_store_relative_path"
            ],
            managed_root_name=(
                "universal_article_body_store"
            ),
        )
    )

    lifecycle_path = (
        _resolve_managed_path_v1(
            project_root=project_root,
            relative_path=execution_package[
                "lifecycle_relative_path"
            ],
            managed_root_name=(
                "universal_article_body_store_lifecycle"
            ),
        )
    )

    archive_existed_before = (
        archive_path.exists()
    )

    body_store_existed_before = (
        body_store_path.exists()
    )

    lifecycle_existed_before = (
        lifecycle_path.exists()
    )

    archive_delete_performed = False
    body_store_delete_performed = False
    lifecycle_transition_performed = False

    if archive_path.is_dir():
        shutil.rmtree(
            archive_path
        )
        archive_delete_performed = True

    elif archive_path.is_file():
        archive_path.unlink()
        archive_delete_performed = True

    if body_store_path.is_file():
        body_store_path.unlink()
        body_store_delete_performed = True

    if lifecycle_path.is_file():
        lifecycle_payload = json.loads(
            lifecycle_path.read_text(
                encoding="utf-8-sig",
            )
        )

        if not isinstance(
            lifecycle_payload,
            dict,
        ):
            raise PermanentDeletionManagerError(
                "Lifecycle payload must be an object."
            )

        lifecycle_payload[
            "state"
        ] = (
            "PERMANENTLY_DELETED"
        )

        lifecycle_payload[
            "lifecycle_state"
        ] = (
            "PERMANENTLY_DELETED"
        )

        lifecycle_payload[
            "permanent_deletion"
        ] = True

        lifecycle_payload[
            "deletion_execution_id"
        ] = execution_package[
            "deletion_execution_id"
        ]

        lifecycle_path.write_text(
            json.dumps(
                lifecycle_payload,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )

        lifecycle_transition_performed = True

    result = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_RESULT_SCHEMA,

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION,

        "deletion_execution_id":
            execution_package[
                "deletion_execution_id"
            ],

        "deletion_plan_id":
            execution_package[
                "deletion_plan_id"
            ],

        "deletion_request_id":
            execution_package[
                "deletion_request_id"
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

        "archive_existed_before":
            archive_existed_before,

        "body_store_existed_before":
            body_store_existed_before,

        "lifecycle_existed_before":
            lifecycle_existed_before,

        "archive_exists_after":
            archive_path.exists(),

        "body_store_exists_after":
            body_store_path.exists(),

        "lifecycle_exists_after":
            lifecycle_path.exists(),

        "archive_delete_performed":
            archive_delete_performed,

        "body_store_delete_performed":
            body_store_delete_performed,

        "lifecycle_transition_performed":
            lifecycle_transition_performed,

        "deletion_status":
            (
                "DELETED"
                if archive_delete_performed
                else "FAILED"
            ),

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


def verify_permanent_deletion_result_v1(
    *,
    deletion_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        deletion_result,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "deletion_result must be a mapping."
        )

    archive_removed = (
        deletion_result.get(
            "archive_exists_after"
        )
        is False
    )

    body_store_removed_or_absent = (
        deletion_result.get(
            "body_store_exists_after"
        )
        is False
    )

    lifecycle_preserved = (
        deletion_result.get(
            "lifecycle_exists_after"
        )
        is True
    )

    deletion_status_valid = (
        deletion_result.get(
            "deletion_status"
        )
        == "DELETED"
    )

    result = {
        "deletion_verified":
            all(
                (
                    archive_removed,
                    body_store_removed_or_absent,
                    lifecycle_preserved,
                    deletion_status_valid,
                    deletion_result.get(
                        "archive_delete_performed"
                    )
                    is True,
                )
            ),

        "archive_removed":
            archive_removed,

        "body_store_removed_or_absent":
            body_store_removed_or_absent,

        "lifecycle_preserved":
            lifecycle_preserved,

        "deletion_status_valid":
            deletion_status_valid,

        "archive_delete_performed":
            deletion_result.get(
                "archive_delete_performed"
            )
            is True,

        "body_store_delete_performed":
            deletion_result.get(
                "body_store_delete_performed"
            )
            is True,

        "lifecycle_transition_performed":
            deletion_result.get(
                "lifecycle_transition_performed"
            )
            is True,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        result
    )
def build_permanent_deletion_manager_bundle_v1(
    *,
    project_root: Path,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    deletion_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    retention_expired: bool,
    deletion_eligible: bool,
    legal_hold_active: bool,
    recovery_closed: bool,
    requested_at: str,
) -> Mapping[str, Any]:

    deletion_plan = (
        build_permanent_deletion_plan_v1(
            project_root=project_root,
            archive_id=archive_id,
            workspace_id=workspace_id,
            body_id=body_id,
            lifecycle_record_id=lifecycle_record_id,
            source_state=source_state,
            deletion_reason=deletion_reason,
            requested_by_type=requested_by_type,
            requested_by_id=requested_by_id,
            retention_expired=retention_expired,
            deletion_eligible=deletion_eligible,
            legal_hold_active=legal_hold_active,
            recovery_closed=recovery_closed,
            requested_at=requested_at,
        )
    )

    execution_package = (
        build_permanent_deletion_execution_package_v1(
            deletion_plan=deletion_plan,
        )
    )

    deletion_result = (
        execute_permanent_deletion_v1(
            project_root=project_root,
            execution_package=execution_package,
        )
    )

    result_verification = (
        verify_permanent_deletion_result_v1(
            deletion_result=deletion_result,
        )
    )

    if result_verification[
        "deletion_verified"
    ] is not True:
        raise PermanentDeletionManagerError(
            "Permanent deletion result verification failed."
        )

    bundle = {
        "bundle_version":
            "body_store_permanent_deletion_manager_bundle.v1",

        "manager_version":
            BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION,

        "deletion_plan":
            deletion_plan,

        "execution_package":
            execution_package,

        "deletion_result":
            deletion_result,

        "result_verification":
            result_verification,

        "bundle_complete":
            True,

        "deletion_verified":
            result_verification[
                "deletion_verified"
            ],

        "deletion_status":
            deletion_result[
                "deletion_status"
            ],

        "archive_delete_performed":
            deletion_result[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            deletion_result[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            deletion_result[
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
        bundle
    )


def verify_permanent_deletion_manager_bundle_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        deletion_bundle,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "deletion_bundle must be a mapping."
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
        if section not in deletion_bundle
    )

    deletion_plan = deletion_bundle.get(
        "deletion_plan",
        {},
    )

    execution_package = deletion_bundle.get(
        "execution_package",
        {},
    )

    deletion_result = deletion_bundle.get(
        "deletion_result",
        {},
    )

    result_verification = deletion_bundle.get(
        "result_verification",
        {},
    )

    plan_id_matches = (
        deletion_plan.get(
            "deletion_plan_id"
        )
        == execution_package.get(
            "deletion_plan_id"
        )
        == deletion_result.get(
            "deletion_plan_id"
        )
    )

    request_id_matches = (
        deletion_plan.get(
            "deletion_request",
            {},
        ).get(
            "deletion_request_id"
        )
        == execution_package.get(
            "deletion_request_id"
        )
        == deletion_result.get(
            "deletion_request_id"
        )
    )

    archive_id_matches = (
        deletion_plan.get(
            "deletion_request",
            {},
        ).get(
            "archive_id"
        )
        == execution_package.get(
            "archive_id"
        )
        == deletion_result.get(
            "archive_id"
        )
    )

    workspace_id_matches = (
        deletion_plan.get(
            "deletion_request",
            {},
        ).get(
            "workspace_id"
        )
        == execution_package.get(
            "workspace_id"
        )
        == deletion_result.get(
            "workspace_id"
        )
    )

    body_id_matches = (
        deletion_plan.get(
            "deletion_request",
            {},
        ).get(
            "body_id"
        )
        == execution_package.get(
            "body_id"
        )
        == deletion_result.get(
            "body_id"
        )
    )

    lifecycle_record_id_matches = (
        deletion_plan.get(
            "deletion_request",
            {},
        ).get(
            "lifecycle_record_id"
        )
        == execution_package.get(
            "lifecycle_record_id"
        )
        == deletion_result.get(
            "lifecycle_record_id"
        )
    )

    result = {
        "bundle_valid":
            all(
                (
                    not missing_sections,
                    deletion_bundle.get(
                        "bundle_complete"
                    )
                    is True,
                    deletion_bundle.get(
                        "deletion_verified"
                    )
                    is True,
                    deletion_plan.get(
                        "plan_ready"
                    )
                    is True,
                    execution_package.get(
                        "execution_ready"
                    )
                    is True,
                    result_verification.get(
                        "deletion_verified"
                    )
                    is True,
                    plan_id_matches,
                    request_id_matches,
                    archive_id_matches,
                    workspace_id_matches,
                    body_id_matches,
                    lifecycle_record_id_matches,
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

        "lifecycle_record_id_matches":
            lifecycle_record_id_matches,

        "archive_delete_performed":
            deletion_bundle.get(
                "archive_delete_performed"
            )
            is True,

        "body_store_delete_performed":
            deletion_bundle.get(
                "body_store_delete_performed"
            )
            is True,

        "lifecycle_transition_performed":
            deletion_bundle.get(
                "lifecycle_transition_performed"
            )
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
def summarize_permanent_deletion_manager_bundle_v1(
    *,
    deletion_bundle: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        deletion_bundle,
        Mapping,
    ):
        raise PermanentDeletionManagerError(
            "deletion_bundle must be a mapping."
        )

    summary = {
        "deletion_plan_id":
            deletion_bundle[
                "deletion_plan"
            ][
                "deletion_plan_id"
            ],

        "deletion_request_id":
            deletion_bundle[
                "execution_package"
            ][
                "deletion_request_id"
            ],

        "deletion_execution_id":
            deletion_bundle[
                "execution_package"
            ][
                "deletion_execution_id"
            ],

        "deletion_verified":
            deletion_bundle[
                "deletion_verified"
            ],

        "deletion_status":
            deletion_bundle[
                "deletion_status"
            ],

        "archive_delete_performed":
            deletion_bundle[
                "archive_delete_performed"
            ],

        "body_store_delete_performed":
            deletion_bundle[
                "body_store_delete_performed"
            ],

        "lifecycle_transition_performed":
            deletion_bundle[
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


__all__ = [
    "BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION",
    "BODY_STORE_PERMANENT_DELETION_MANAGER_SCHEMA",
    "BODY_STORE_PERMANENT_DELETION_PLAN_SCHEMA",
    "BODY_STORE_PERMANENT_DELETION_RESULT_SCHEMA",
    "PermanentDeletionManagerError",
    "calculate_permanent_deletion_payload_checksum_v1",
    "build_permanent_deletion_plan_v1",
    "verify_permanent_deletion_plan_v1",
    "build_permanent_deletion_execution_package_v1",
    "execute_permanent_deletion_v1",
    "verify_permanent_deletion_result_v1",
    "build_permanent_deletion_manager_bundle_v1",
    "verify_permanent_deletion_manager_bundle_v1",
    "summarize_permanent_deletion_manager_bundle_v1",
]
