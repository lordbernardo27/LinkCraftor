"""
Universal Article Body Store
Archive Execution Manager

Phase 9.1.5.2
"""

from __future__ import annotations

import hashlib
import json

from datetime import (
    datetime,
    timezone,
)

from types import MappingProxyType

from typing import (
    Any,
    Mapping,
)

from backend.server.universal_article_body_store.body_store_archive_manager_v1 import (
    evaluate_body_store_archive_eligibility_v1,
)

from backend.server.universal_article_body_store.body_store_state_transition_engine_v1 import (
    transition_body_store_lifecycle_state_v1,
)

BODY_STORE_ARCHIVE_EXECUTION_MANAGER_VERSION = (
    "universal_article_body_store_archive_execution_manager_v1"
)

BODY_STORE_ARCHIVE_EXECUTION_SCHEMA_VERSION = (
    "body_store_archive_execution_v1"
)

BODY_STORE_ARCHIVE_EXECUTION_STATUSES = (
    "EXECUTED",
    "BLOCKED",
    "FAILED",
)

BODY_STORE_ARCHIVE_TARGET_STATE = (
    "ARCHIVED"
)


class BodyStoreArchiveExecutionError(
    ValueError,
):
    """Raised when archive execution cannot proceed."""

def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreArchiveExecutionError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise BodyStoreArchiveExecutionError(
            f"{field_name} must not be empty."
        )

    return value


def _require_timestamp(
    value: Any,
    *,
    field_name: str,
) -> str:
    timestamp = _require_string(
        value,
        field_name=field_name,
    )

    try:
        parsed = datetime.fromisoformat(
            timestamp.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError as exc:
        raise BodyStoreArchiveExecutionError(
            f"{field_name} must be ISO-8601."
        ) from exc

    if parsed.tzinfo is None:
        raise BodyStoreArchiveExecutionError(
            f"{field_name} must contain timezone."
        )

    return parsed.astimezone(
        timezone.utc
    ).isoformat()


def _build_execution_id(
    *,
    archive_decision_id: str,
    lifecycle_record_id: str,
    evaluated_at: str,
) -> str:
    material = json.dumps(
        {
            "archive_decision_id":
                archive_decision_id,

            "lifecycle_record_id":
                lifecycle_record_id,

            "evaluated_at":
                evaluated_at,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return (
        "body_store_archive_execution_"
        + hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def _immutable(
    mapping: Mapping[str, Any],
) -> Mapping[str, Any]:
    return MappingProxyType(
        dict(mapping)
    )
def _validate_archive_decision(
    decision: Mapping[str, Any],
) -> Mapping[str, Any]:
    if not isinstance(
        decision,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_decision must be a mapping."
        )

    required_fields = (
        "archive_decision_id",
        "archive_status",
        "archive_eligible",
        "required_target_state",
        "retention_policy_id",
        "lifecycle_record_id",
        "workspace_id",
        "evaluated_at",
    )

    for field in required_fields:
        if field not in decision:
            raise BodyStoreArchiveExecutionError(
                f"Missing archive decision field: {field}"
            )

    if decision[
        "archive_status"
    ] != "ELIGIBLE":
        raise BodyStoreArchiveExecutionError(
            "Archive decision is not ELIGIBLE."
        )

    if decision[
        "archive_eligible"
    ] is not True:
        raise BodyStoreArchiveExecutionError(
            "Archive decision is not eligible."
        )

    if (
        decision[
            "required_target_state"
        ]
        != BODY_STORE_ARCHIVE_TARGET_STATE
    ):
        raise BodyStoreArchiveExecutionError(
            "Unexpected archive target state."
        )

    return decision


def execute_body_store_archive_v1(
    *,
    policy: Mapping[str, Any],
    lifecycle_state: str,
    evaluated_at: str,
    archive_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
) -> Mapping[str, Any]:

    normalized_timestamp = (
        _require_timestamp(
            evaluated_at,
            field_name="evaluated_at",
        )
    )

    archive_decision = (
        evaluate_body_store_archive_eligibility_v1(
            policy=policy,
            lifecycle_state=lifecycle_state,
            evaluated_at=normalized_timestamp,
            archive_reason=archive_reason,
            actor_type=actor_type,
            actor_id=actor_id,
            source=source,
        )
    )

    archive_decision = (
        _validate_archive_decision(
            archive_decision
        )
    )
    transition_request = {
        "lifecycle_record_id":
            archive_decision[
                "lifecycle_record_id"
            ],

        "current_state":
            lifecycle_state,

        "target_state":
            BODY_STORE_ARCHIVE_TARGET_STATE,

        "reason":
            archive_reason,

        "actor_type":
            actor_type,

        "actor_id":
            actor_id,

        "source":
            source,

        "evaluated_at":
            normalized_timestamp,
    }

    execution_id = (
        _build_execution_id(
            archive_decision_id=
                archive_decision[
                    "archive_decision_id"
                ],

            lifecycle_record_id=
                archive_decision[
                    "lifecycle_record_id"
                ],

            evaluated_at=
                normalized_timestamp,
        )
    )

    result = {
        "schema_version":
            BODY_STORE_ARCHIVE_EXECUTION_SCHEMA_VERSION,

        "manager_version":
            BODY_STORE_ARCHIVE_EXECUTION_MANAGER_VERSION,

        "archive_execution_id":
            execution_id,

        "archive_decision_id":
            archive_decision[
                "archive_decision_id"
            ],

        "retention_policy_id":
            archive_decision[
                "retention_policy_id"
            ],

        "workspace_id":
            archive_decision[
                "workspace_id"
            ],

        "lifecycle_record_id":
            archive_decision[
                "lifecycle_record_id"
            ],

        "archive_execution_status":
            "EXECUTED",

        "transition_request":
            transition_request,

        "required_target_state":
            BODY_STORE_ARCHIVE_TARGET_STATE,

        "physical_archive_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "evaluated_at":
            normalized_timestamp,
    }

    return _immutable(
        result
    )
def execute_body_store_archive_transition_v1(
    *,
    archive_execution: Mapping[str, Any],
    actor_type: str,
    actor_id: str,
    source: str,
) -> Mapping[str, Any]:
    """
    Build a certified lifecycle transition request.

    This function does not perform the transition.
    It only prepares the deterministic request that
    the certified State Transition Engine will later
    consume.
    """

    if not isinstance(
        archive_execution,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_execution must be a mapping."
        )

    required_fields = (
        "archive_execution_id",
        "archive_decision_id",
        "lifecycle_record_id",
        "required_target_state",
        "evaluated_at",
    )

    for field in required_fields:
        if field not in archive_execution:
            raise BodyStoreArchiveExecutionError(
                f"Missing archive execution field: {field}"
            )

    normalized_actor_type = _require_string(
        actor_type,
        field_name="actor_type",
    )

    normalized_actor_id = _require_string(
        actor_id,
        field_name="actor_id",
    )

    normalized_source = _require_string(
        source,
        field_name="source",
    )

    transition = {
        "archive_execution_id":
            archive_execution[
                "archive_execution_id"
            ],

        "archive_decision_id":
            archive_execution[
                "archive_decision_id"
            ],

        "lifecycle_record_id":
            archive_execution[
                "lifecycle_record_id"
            ],

        "target_state":
            archive_execution[
                "required_target_state"
            ],

        "actor_type":
            normalized_actor_type,

        "actor_id":
            normalized_actor_id,

        "source":
            normalized_source,

        "requested_at":
            archive_execution[
                "evaluated_at"
            ],

        "transition_executed":
            False,
    }

    return _immutable(
        transition
    )
def build_body_store_archive_execution_audit_v1(
    *,
    archive_execution: Mapping[str, Any],
    transition_request: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce an immutable audit record for an
    archive execution.

    No persistence is performed.
    """

    if not isinstance(
        archive_execution,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_execution must be a mapping."
        )

    if not isinstance(
        transition_request,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "transition_request must be a mapping."
        )

    audit_material = json.dumps(
        {
            "archive_execution_id":
                archive_execution[
                    "archive_execution_id"
                ],

            "archive_decision_id":
                archive_execution[
                    "archive_decision_id"
                ],

            "lifecycle_record_id":
                archive_execution[
                    "lifecycle_record_id"
                ],

            "requested_at":
                transition_request[
                    "requested_at"
                ],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    audit_id = (
        "body_store_archive_audit_"
        + hashlib.sha256(
            audit_material.encode(
                "utf-8"
            )
        ).hexdigest()
    )

    record = {
        "audit_id":
            audit_id,

        "archive_execution_id":
            archive_execution[
                "archive_execution_id"
            ],

        "archive_decision_id":
            archive_execution[
                "archive_decision_id"
            ],

        "lifecycle_record_id":
            archive_execution[
                "lifecycle_record_id"
            ],

        "workspace_id":
            archive_execution[
                "workspace_id"
            ],

        "target_state":
            archive_execution[
                "required_target_state"
            ],

        "requested_at":
            transition_request[
                "requested_at"
            ],

        "audit_created":
            True,

        "persisted":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        record
    )
def verify_body_store_archive_execution_v1(
    *,
    archive_execution: Mapping[str, Any],
    transition_request: Mapping[str, Any],
    audit_record: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Verify that an archive execution package is
    internally consistent.

    This function is read-only.
    """

    if not isinstance(
        archive_execution,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_execution must be a mapping."
        )

    if not isinstance(
        transition_request,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "transition_request must be a mapping."
        )

    if not isinstance(
        audit_record,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "audit_record must be a mapping."
        )

    lifecycle_match = (
        archive_execution[
            "lifecycle_record_id"
        ]
        ==
        transition_request[
            "lifecycle_record_id"
        ]
        ==
        audit_record[
            "lifecycle_record_id"
        ]
    )

    decision_match = (
        archive_execution[
            "archive_decision_id"
        ]
        ==
        audit_record[
            "archive_decision_id"
        ]
    )

    target_match = (
        transition_request[
            "target_state"
        ]
        ==
        BODY_STORE_ARCHIVE_TARGET_STATE
    )

    verification = {
        "verification_success":
            (
                lifecycle_match
                and decision_match
                and target_match
            ),

        "lifecycle_record_match":
            lifecycle_match,

        "archive_decision_match":
            decision_match,

        "target_state_match":
            target_match,

        "verified_target_state":
            BODY_STORE_ARCHIVE_TARGET_STATE,

        "physical_archive_verified":
            False,

        "lifecycle_transition_verified":
            False,

        "content_body_included":
            False,
    }

    return _immutable(
        verification
    )
def create_body_store_archive_execution_package_v1(
    *,
    policy: Mapping[str, Any],
    lifecycle_state: str,
    evaluated_at: str,
    archive_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
) -> Mapping[str, Any]:
    """
    Build the complete archive execution package.

    This function is deterministic and read-only.

    It does not perform:

    • archive writes
    • lifecycle writes
    • queue operations
    • runtime operations
    """

    execution = (
        execute_body_store_archive_v1(
            policy=policy,
            lifecycle_state=lifecycle_state,
            evaluated_at=evaluated_at,
            archive_reason=archive_reason,
            actor_type=actor_type,
            actor_id=actor_id,
            source=source,
        )
    )

    transition = (
        execute_body_store_archive_transition_v1(
            archive_execution=execution,
            actor_type=actor_type,
            actor_id=actor_id,
            source=source,
        )
    )

    audit = (
        build_body_store_archive_execution_audit_v1(
            archive_execution=execution,
            transition_request=transition,
        )
    )

    verification = (
        verify_body_store_archive_execution_v1(
            archive_execution=execution,
            transition_request=transition,
            audit_record=audit,
        )
    )

    package = {
        "execution":
            execution,

        "transition":
            transition,

        "audit":
            audit,

        "verification":
            verification,

        "package_version":
            "body_store_archive_execution_package_v1",

        "package_complete":
            True,

        "physical_archive_performed":
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

    return _immutable(
        package
    )
def summarize_body_store_archive_execution_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce a compact immutable summary of an
    archive execution package.

    Read-only.
    """

    if not isinstance(
        archive_package,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_package must be a mapping."
        )

    execution = archive_package[
        "execution"
    ]

    verification = archive_package[
        "verification"
    ]

    summary = {
        "archive_execution_id":
            execution[
                "archive_execution_id"
            ],

        "archive_decision_id":
            execution[
                "archive_decision_id"
            ],

        "workspace_id":
            execution[
                "workspace_id"
            ],

        "lifecycle_record_id":
            execution[
                "lifecycle_record_id"
            ],

        "archive_status":
            execution[
                "archive_execution_status"
            ],

        "verification_success":
            verification[
                "verification_success"
            ],

        "required_target_state":
            execution[
                "required_target_state"
            ],

        "evaluated_at":
            execution[
                "evaluated_at"
            ],

        "physical_archive_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _immutable(
        summary
    )
def validate_body_store_archive_execution_package_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Validate the internal consistency of an archive
    execution package.

    This function performs no writes.
    """

    if not isinstance(
        archive_package,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_package must be a mapping."
        )

    execution = archive_package[
        "execution"
    ]

    transition = archive_package[
        "transition"
    ]

    audit = archive_package[
        "audit"
    ]

    verification = archive_package[
        "verification"
    ]

    checks = {
        "execution_present":
            execution is not None,

        "transition_present":
            transition is not None,

        "audit_present":
            audit is not None,

        "verification_present":
            verification is not None,

        "same_lifecycle_record":
            (
                execution[
                    "lifecycle_record_id"
                ]
                ==
                transition[
                    "lifecycle_record_id"
                ]
                ==
                audit[
                    "lifecycle_record_id"
                ]
            ),

        "same_archive_decision":
            (
                execution[
                    "archive_decision_id"
                ]
                ==
                audit[
                    "archive_decision_id"
                ]
            ),

        "target_state_archived":
            (
                transition[
                    "target_state"
                ]
                ==
                BODY_STORE_ARCHIVE_TARGET_STATE
            ),

        "verification_success":
            verification[
                "verification_success"
            ],
    }

    validation = {
        "package_valid":
            all(
                checks.values()
            ),

        "checks":
            MappingProxyType(
                dict(checks)
            ),

        "physical_archive_performed":
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

    return _immutable(
        validation
    )
def describe_body_store_archive_execution_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce a human-readable deterministic
    description of an archive execution package.

    Read-only.
    """

    if not isinstance(
        archive_package,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "archive_package must be a mapping."
        )

    execution = archive_package[
        "execution"
    ]

    verification = archive_package[
        "verification"
    ]

    description = {
        "archive_execution_id":
            execution[
                "archive_execution_id"
            ],

        "summary":
            (
                "Archive execution prepared "
                "successfully."
            ),

        "workspace_id":
            execution[
                "workspace_id"
            ],

        "lifecycle_record_id":
            execution[
                "lifecycle_record_id"
            ],

        "target_state":
            execution[
                "required_target_state"
            ],

        "verification_success":
            verification[
                "verification_success"
            ],

        "physical_archive_performed":
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

    return _immutable(
        description
    )
def certify_body_store_archive_execution_package_v1(
    *,
    archive_package: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce a deterministic certification summary
    for an archive execution package.

    This function is read-only.
    """

    validation = (
        validate_body_store_archive_execution_package_v1(
            archive_package=archive_package,
        )
    )

    summary = (
        summarize_body_store_archive_execution_v1(
            archive_package=archive_package,
        )
    )

    description = (
        describe_body_store_archive_execution_v1(
            archive_package=archive_package,
        )
    )

    certification = {
        "schema_version":
            "body_store_archive_execution_certification_v1",

        "certified":
            validation[
                "package_valid"
            ],

        "package_complete":
            archive_package[
                "package_complete"
            ],

        "validation":
            validation,

        "summary":
            summary,

        "description":
            description,

        "physical_archive_performed":
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

    return _immutable(
        certification
    )
def export_body_store_archive_execution_metadata_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce deterministic metadata describing a
    certified archive execution package.

    Read-only.
    """

    if not isinstance(
        certification,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "certification must be a mapping."
        )

    summary = certification[
        "summary"
    ]

    metadata = {
        "metadata_version":
            "body_store_archive_execution_metadata_v1",

        "archive_execution_id":
            summary[
                "archive_execution_id"
            ],

        "workspace_id":
            summary[
                "workspace_id"
            ],

        "lifecycle_record_id":
            summary[
                "lifecycle_record_id"
            ],

        "target_state":
            summary[
                "required_target_state"
            ],

        "verification_success":
            summary[
                "verification_success"
            ],

        "generated_from_certification":
            True,

        "physical_archive_performed":
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

    return _immutable(
        metadata
    )
def get_body_store_archive_execution_statistics_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Produce deterministic statistics describing the
    certified archive execution package.

    Read-only.
    """

    if not isinstance(
        certification,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "certification must be a mapping."
        )

    summary = certification[
        "summary"
    ]

    validation = certification[
        "validation"
    ]

    checks = validation[
        "checks"
    ]

    statistics = {
        "statistics_version":
            "body_store_archive_execution_statistics_v1",

        "archive_execution_id":
            summary[
                "archive_execution_id"
            ],

        "workspace_id":
            summary[
                "workspace_id"
            ],

        "verification_success":
            summary[
                "verification_success"
            ],

        "validation_checks":
            len(checks),

        "validation_passed":
            sum(
                1
                for passed
                in checks.values()
                if passed
            ),

        "validation_failed":
            sum(
                1
                for passed
                in checks.values()
                if not passed
            ),

        "physical_archive_performed":
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

    return _immutable(
        statistics
    )
def export_body_store_archive_execution_contract_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Export the canonical archive execution contract.

    Read-only.
    """

    if not isinstance(
        certification,
        Mapping,
    ):
        raise BodyStoreArchiveExecutionError(
            "certification must be a mapping."
        )

    summary = certification[
        "summary"
    ]

    contract = {
        "contract_version":
            "body_store_archive_execution_contract_v1",

        "archive_execution_id":
            summary[
                "archive_execution_id"
            ],

        "workspace_id":
            summary[
                "workspace_id"
            ],

        "lifecycle_record_id":
            summary[
                "lifecycle_record_id"
            ],

        "target_state":
            summary[
                "required_target_state"
            ],

        "verification_success":
            summary[
                "verification_success"
            ],

        "physical_archive_performed":
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

    return _immutable(
        contract
    )
def build_body_store_archive_execution_bundle_v1(
    *,
    policy: Mapping[str, Any],
    lifecycle_state: str,
    evaluated_at: str,
    archive_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
) -> Mapping[str, Any]:
    """
    Build the complete Archive Execution bundle.

    This is the top-level API for Phase 9.1.5.2.

    It is deterministic, immutable and read-only.

    It performs no persistence and creates no runtime
    jobs or queue jobs.
    """

    certification = (
        certify_body_store_archive_execution_package_v1(
            archive_package=
                create_body_store_archive_execution_package_v1(
                    policy=policy,
                    lifecycle_state=lifecycle_state,
                    evaluated_at=evaluated_at,
                    archive_reason=archive_reason,
                    actor_type=actor_type,
                    actor_id=actor_id,
                    source=source,
                ),
        )
    )

    metadata = (
        export_body_store_archive_execution_metadata_v1(
            certification=certification,
        )
    )

    statistics = (
        get_body_store_archive_execution_statistics_v1(
            certification=certification,
        )
    )

    contract = (
        export_body_store_archive_execution_contract_v1(
            certification=certification,
        )
    )

    bundle = {
        "bundle_version":
            "body_store_archive_execution_bundle_v1",

        "certification":
            certification,

        "metadata":
            metadata,

        "statistics":
            statistics,

        "contract":
            contract,

        "bundle_complete":
            True,

        "physical_archive_performed":
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

    return _immutable(
        bundle
    )
# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "BODY_STORE_ARCHIVE_EXECUTION_MANAGER_VERSION",
    "BODY_STORE_ARCHIVE_EXECUTION_SCHEMA_VERSION",
    "BODY_STORE_ARCHIVE_EXECUTION_STATUSES",
    "BODY_STORE_ARCHIVE_TARGET_STATE",
    "BodyStoreArchiveExecutionError",
    "execute_body_store_archive_v1",
    "execute_body_store_archive_transition_v1",
    "build_body_store_archive_execution_audit_v1",
    "verify_body_store_archive_execution_v1",
    "create_body_store_archive_execution_package_v1",
    "summarize_body_store_archive_execution_v1",
    "validate_body_store_archive_execution_package_v1",
    "describe_body_store_archive_execution_v1",
    "certify_body_store_archive_execution_package_v1",
    "export_body_store_archive_execution_metadata_v1",
    "get_body_store_archive_execution_statistics_v1",
    "export_body_store_archive_execution_contract_v1",
    "build_body_store_archive_execution_bundle_v1",
]
# ============================================================
# MODULE SELF TEST
# ============================================================

if __name__ == "__main__":

    from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
        build_body_store_retention_policy_v1,
    )

    sample_policy = (
        build_body_store_retention_policy_v1(
            retention_policy_id="archive_execution_demo",
            retention_policy_name="Archive Execution Demo",
            lifecycle_record_id="body_lifecycle_demo",
            workspace_id="ws_demo",
            retention_class="STANDARD",
            retention_started_at="2025-01-01T00:00:00+00:00",
            retention_period_days=30,
            eligibility_reason="Module self-test",
            evaluated_at="2025-01-01T00:00:00+00:00",
        )
    )

    bundle = (
        build_body_store_archive_execution_bundle_v1(
            policy=sample_policy,
            lifecycle_state="ACTIVE",
            evaluated_at="2026-08-03T00:00:00+00:00",
            archive_reason="Module self-test",
            actor_type="SYSTEM",
            actor_id="archive_execution_manager",
            source="module_self_test",
        )
    )

    print(
        "Archive Execution Bundle Created Successfully"
    )

    print(
        json.dumps(
            dict(bundle),
            indent=4,
            default=dict,
        )
    )
