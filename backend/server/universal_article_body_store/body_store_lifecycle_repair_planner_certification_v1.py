from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_verifier_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,
    verify_lifecycle_repair_planner_v1,
)


BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA = (
    "body_store_lifecycle_repair_planner_certification.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA = (
    "body_store_lifecycle_repair_planner_certification_bundle.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION = "1.0"


class LifecycleRepairPlannerCertificationError(
    ValueError
):
    """Raised when Lifecycle Repair Planner certification cannot be produced."""


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
        Mapping,
    ):
        return MappingProxyType(
            {
                str(
                    key
                ):
                    _freeze(
                        item
                    )

                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
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
        (
            tuple,
            list,
        ),
    ):
        return [
            _json_ready(
                item
            )

            for item
            in value
        ]

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
        raise LifecycleRepairPlannerCertificationError(
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
        raise LifecycleRepairPlannerCertificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairPlannerCertificationError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_lifecycle_repair_planner_certification_checksum_v1(
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
def build_lifecycle_repair_planner_certification_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    scanner_certificate = _require_mapping(
        scanner_certification,
        field_name="scanner_certification",
    )

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    verification = (
        verify_lifecycle_repair_planner_v1(
            planner_request=request,
            scanner_certification=scanner_certificate,
            findings=findings,
            repair_plan=plan,
        )
    )

    if (
        verification[
            "verification_passed"
        ]
        is not True
    ):
        raise LifecycleRepairPlannerCertificationError(
            "Lifecycle Repair Planner verification "
            "did not pass. Certification refused."
        )

    verification_checksum = _require_string(
        verification.get(
            "verification_checksum"
        ),
        field_name="verification.verification_checksum",
    )

    repair_plan_id = _require_string(
        verification.get(
            "repair_plan_id"
        ),
        field_name="verification.repair_plan_id",
    )

    repair_plan_request_id = _require_string(
        verification.get(
            "repair_plan_request_id"
        ),
        field_name="verification.repair_plan_request_id",
    )

    workspace_id = _require_string(
        verification.get(
            "workspace_id"
        ),
        field_name="verification.workspace_id",
    )

    certification_identity = {
        "repair_plan_id":
            repair_plan_id,

        "repair_plan_request_id":
            repair_plan_request_id,

        "workspace_id":
            workspace_id,

        "verification_checksum":
            verification_checksum,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,

        "certification_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION,
    }

    certification_identity_checksum = (
        calculate_lifecycle_repair_planner_certification_checksum_v1(
            payload=certification_identity,
        )
    )

    certification_id = (
        "repair_planner_certification_"
        + certification_identity_checksum[
            :24
        ]
    )

    certification = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA,

        "certification_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,

        "certification_id":
            certification_id,

        "repair_plan_id":
            repair_plan_id,

        "repair_plan_request_id":
            repair_plan_request_id,

        "workspace_id":
            workspace_id,

        "scanner_scan_request_id":
            verification.get(
                "scanner_scan_request_id"
            ),

        "scanner_verification_checksum":
            verification.get(
                "scanner_verification_checksum"
            ),

        "verification_checksum":
            verification_checksum,

        "verification_passed":
            verification[
                "verification_passed"
            ]
            is True,

        "identity_verified":
            verification[
                "identity_verified"
            ]
            is True,

        "actions_verified":
            verification[
                "actions_verified"
            ]
            is True,

        "safety_verified":
            verification[
                "safety_verified"
            ]
            is True,

        "reproducibility_verified":
            verification[
                "reproducibility_verified"
            ]
            is True,

        "repair_action_count":
            verification[
                "repair_action_count"
            ],

        "automatically_planned_action_count":
            verification[
                "automatically_planned_action_count"
            ],

        "manual_review_action_count":
            verification[
                "manual_review_action_count"
            ],

        "verification":
            verification,

        "certified":
            True,

        "certification_scope":
            "REPAIR_PLANNER_ONLY",

        "planner_mode":
            "PLAN_ONLY",

        "repair_plan_generated":
            verification[
                "repair_plan_generated"
            ]
            is True,

        "repair_planned":
            verification[
                "repair_planned"
            ]
            is True,

        "execution_authorized":
            False,

        "execution_status":
            "NOT_EXECUTED",

        "repair_executed":
            False,

        "read_only":
            True,

        "production_mutation_allowed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    certification_checksum_source = dict(
        certification
    )

    certification[
        "certification_checksum"
    ] = (
        calculate_lifecycle_repair_planner_certification_checksum_v1(
            payload=certification_checksum_source,
        )
    )

    return _freeze(
        certification
    )


def summarize_lifecycle_repair_planner_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    certificate = _require_mapping(
        certification,
        field_name="certification",
    )

    return _freeze(
        {
            "certification_id":
                certificate.get(
                    "certification_id"
                ),

            "repair_plan_id":
                certificate.get(
                    "repair_plan_id"
                ),

            "repair_plan_request_id":
                certificate.get(
                    "repair_plan_request_id"
                ),

            "workspace_id":
                certificate.get(
                    "workspace_id"
                ),

            "certified":
                certificate.get(
                    "certified"
                )
                is True,

            "verification_passed":
                certificate.get(
                    "verification_passed"
                )
                is True,

            "identity_verified":
                certificate.get(
                    "identity_verified"
                )
                is True,

            "actions_verified":
                certificate.get(
                    "actions_verified"
                )
                is True,

            "safety_verified":
                certificate.get(
                    "safety_verified"
                )
                is True,

            "reproducibility_verified":
                certificate.get(
                    "reproducibility_verified"
                )
                is True,

            "repair_action_count":
                certificate.get(
                    "repair_action_count",
                    0,
                ),

            "automatically_planned_action_count":
                certificate.get(
                    "automatically_planned_action_count",
                    0,
                ),

            "manual_review_action_count":
                certificate.get(
                    "manual_review_action_count",
                    0,
                ),

            "certification_scope":
                certificate.get(
                    "certification_scope"
                ),

            "planner_mode":
                certificate.get(
                    "planner_mode"
                ),

            "repair_plan_generated":
                certificate.get(
                    "repair_plan_generated"
                )
                is True,

            "repair_planned":
                certificate.get(
                    "repair_planned"
                )
                is True,

            "execution_authorized":
                certificate.get(
                    "execution_authorized"
                ),

            "repair_executed":
                certificate.get(
                    "repair_executed"
                ),

            "production_mutation_allowed":
                certificate.get(
                    "production_mutation_allowed"
                ),

            "runtime_job_created":
                certificate.get(
                    "runtime_job_created"
                ),

            "queue_job_created":
                certificate.get(
                    "queue_job_created"
                ),

            "certification_checksum":
                certificate.get(
                    "certification_checksum"
                ),
        }
    )
from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_verifier_v1 import (
    calculate_lifecycle_repair_planner_verification_checksum_v1,
)


def validate_lifecycle_repair_planner_certification_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    certificate = _require_mapping(
        certification,
        field_name="certification",
    )

    required_fields = (
        "schema",
        "certification_version",
        "contract_version",
        "engine_version",
        "verifier_version",
        "certification_id",
        "repair_plan_id",
        "repair_plan_request_id",
        "workspace_id",
        "scanner_scan_request_id",
        "scanner_verification_checksum",
        "verification_checksum",
        "verification_passed",
        "identity_verified",
        "actions_verified",
        "safety_verified",
        "reproducibility_verified",
        "repair_action_count",
        "automatically_planned_action_count",
        "manual_review_action_count",
        "verification",
        "certified",
        "certification_scope",
        "planner_mode",
        "repair_plan_generated",
        "repair_planned",
        "execution_authorized",
        "execution_status",
        "repair_executed",
        "read_only",
        "production_mutation_allowed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "certification_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in certificate
    )

    schema_valid = (
        certificate.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA
    )

    certification_version_valid = (
        certificate.get(
            "certification_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION
    )

    contract_version_valid = (
        certificate.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
    )

    engine_version_valid = (
        certificate.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION
    )

    verifier_version_valid = (
        certificate.get(
            "verifier_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION
    )

    certification_id_valid = (
        isinstance(
            certificate.get(
                "certification_id"
            ),
            str,
        )
        and bool(
            str(
                certificate.get(
                    "certification_id",
                    "",
                )
            ).strip()
        )
    )

    repair_plan_id_valid = (
        isinstance(
            certificate.get(
                "repair_plan_id"
            ),
            str,
        )
        and bool(
            str(
                certificate.get(
                    "repair_plan_id",
                    "",
                )
            ).strip()
        )
    )

    repair_plan_request_id_valid = (
        isinstance(
            certificate.get(
                "repair_plan_request_id"
            ),
            str,
        )
        and bool(
            str(
                certificate.get(
                    "repair_plan_request_id",
                    "",
                )
            ).strip()
        )
    )

    workspace_id_valid = (
        isinstance(
            certificate.get(
                "workspace_id"
            ),
            str,
        )
        and bool(
            str(
                certificate.get(
                    "workspace_id",
                    "",
                )
            ).strip()
        )
    )

    verification = certificate.get(
        "verification"
    )

    verification_mapping_valid = isinstance(
        verification,
        Mapping,
    )

    verification_passed = (
        verification_mapping_valid
        and verification.get(
            "verification_passed"
        )
        is True
    )

    identity_verified = (
        verification_mapping_valid
        and verification.get(
            "identity_verified"
        )
        is True
    )

    actions_verified = (
        verification_mapping_valid
        and verification.get(
            "actions_verified"
        )
        is True
    )

    safety_verified = (
        verification_mapping_valid
        and verification.get(
            "safety_verified"
        )
        is True
    )

    reproducibility_verified = (
        verification_mapping_valid
        and verification.get(
            "reproducibility_verified"
        )
        is True
    )

    verification_identity_matches = all(
        (
            verification_mapping_valid,

            certificate.get(
                "repair_plan_id"
            )
            == verification.get(
                "repair_plan_id"
            ),

            certificate.get(
                "repair_plan_request_id"
            )
            == verification.get(
                "repair_plan_request_id"
            ),

            certificate.get(
                "workspace_id"
            )
            == verification.get(
                "workspace_id"
            ),

            certificate.get(
                "scanner_scan_request_id"
            )
            == verification.get(
                "scanner_scan_request_id"
            ),

            certificate.get(
                "scanner_verification_checksum"
            )
            == verification.get(
                "scanner_verification_checksum"
            ),
        )
    )

    verification_checksum_source = {
        key:
            value

        for key, value
        in verification.items()

        if key != "verification_checksum"
    } if verification_mapping_valid else {}

    calculated_verification_checksum = (
        calculate_lifecycle_repair_planner_verification_checksum_v1(
            payload=verification_checksum_source,
        )
        if verification_mapping_valid
        else ""
    )

    embedded_verification_checksum_valid = (
        verification_mapping_valid
        and verification.get(
            "verification_checksum"
        )
        == calculated_verification_checksum
    )

    certification_verification_checksum_matches = (
        verification_mapping_valid
        and certificate.get(
            "verification_checksum"
        )
        == verification.get(
            "verification_checksum"
        )
    )

    verification_flags_match = all(
        (
            certificate.get(
                "verification_passed"
            )
            is verification_passed,

            certificate.get(
                "identity_verified"
            )
            is identity_verified,

            certificate.get(
                "actions_verified"
            )
            is actions_verified,

            certificate.get(
                "safety_verified"
            )
            is safety_verified,

            certificate.get(
                "reproducibility_verified"
            )
            is reproducibility_verified,
        )
    )

    count_fields_match = all(
        (
            verification_mapping_valid,

            certificate.get(
                "repair_action_count"
            )
            == verification.get(
                "repair_action_count"
            ),

            certificate.get(
                "automatically_planned_action_count"
            )
            == verification.get(
                "automatically_planned_action_count"
            ),

            certificate.get(
                "manual_review_action_count"
            )
            == verification.get(
                "manual_review_action_count"
            ),
        )
    )

    certification_scope_valid = (
        certificate.get(
            "certification_scope"
        )
        == "REPAIR_PLANNER_ONLY"
    )

    planner_mode_valid = (
        certificate.get(
            "planner_mode"
        )
        == "PLAN_ONLY"
    )

    safety_boundaries_valid = all(
        (
            certificate.get(
                "certified"
            )
            is True,

            certificate.get(
                "repair_plan_generated"
            )
            is True,

            certificate.get(
                "repair_planned"
            )
            is True,

            certificate.get(
                "execution_authorized"
            )
            is False,

            certificate.get(
                "execution_status"
            )
            == "NOT_EXECUTED",

            certificate.get(
                "repair_executed"
            )
            is False,

            certificate.get(
                "read_only"
            )
            is True,

            certificate.get(
                "production_mutation_allowed"
            )
            is False,

            certificate.get(
                "lifecycle_modified"
            )
            is False,

            certificate.get(
                "archive_modified"
            )
            is False,

            certificate.get(
                "tombstone_modified"
            )
            is False,

            certificate.get(
                "body_store_modified"
            )
            is False,

            certificate.get(
                "runtime_job_created"
            )
            is False,

            certificate.get(
                "queue_job_created"
            )
            is False,
        )
    )

    certification_identity = {
        "repair_plan_id":
            certificate.get(
                "repair_plan_id"
            ),

        "repair_plan_request_id":
            certificate.get(
                "repair_plan_request_id"
            ),

        "workspace_id":
            certificate.get(
                "workspace_id"
            ),

        "verification_checksum":
            certificate.get(
                "verification_checksum"
            ),

        "contract_version":
            certificate.get(
                "contract_version"
            ),

        "engine_version":
            certificate.get(
                "engine_version"
            ),

        "verifier_version":
            certificate.get(
                "verifier_version"
            ),

        "certification_version":
            certificate.get(
                "certification_version"
            ),
    }

    expected_certification_identity_checksum = (
        calculate_lifecycle_repair_planner_certification_checksum_v1(
            payload=certification_identity,
        )
    )

    expected_certification_id = (
        "repair_planner_certification_"
        + expected_certification_identity_checksum[
            :24
        ]
    )

    certification_id_matches = (
        certificate.get(
            "certification_id"
        )
        == expected_certification_id
    )

    certification_checksum_source = {
        key:
            value

        for key, value
        in certificate.items()

        if key != "certification_checksum"
    }

    calculated_certification_checksum = (
        calculate_lifecycle_repair_planner_certification_checksum_v1(
            payload=certification_checksum_source,
        )
    )

    certification_checksum_valid = (
        calculated_certification_checksum
        == certificate.get(
            "certification_checksum"
        )
    )

    certification_valid = all(
        (
            not missing_fields,
            schema_valid,
            certification_version_valid,
            contract_version_valid,
            engine_version_valid,
            verifier_version_valid,
            certification_id_valid,
            repair_plan_id_valid,
            repair_plan_request_id_valid,
            workspace_id_valid,
            verification_mapping_valid,
            verification_passed,
            identity_verified,
            actions_verified,
            safety_verified,
            reproducibility_verified,
            verification_identity_matches,
            embedded_verification_checksum_valid,
            certification_verification_checksum_matches,
            verification_flags_match,
            count_fields_match,
            certification_scope_valid,
            planner_mode_valid,
            safety_boundaries_valid,
            certification_id_matches,
            certification_checksum_valid,
        )
    )

    return _freeze(
        {
            "certification_valid":
                certification_valid,

            "missing_fields":
                missing_fields,

            "schema_valid":
                schema_valid,

            "certification_version_valid":
                certification_version_valid,

            "contract_version_valid":
                contract_version_valid,

            "engine_version_valid":
                engine_version_valid,

            "verifier_version_valid":
                verifier_version_valid,

            "certification_id_valid":
                certification_id_valid,

            "certification_id_matches":
                certification_id_matches,

            "repair_plan_id_valid":
                repair_plan_id_valid,

            "repair_plan_request_id_valid":
                repair_plan_request_id_valid,

            "workspace_id_valid":
                workspace_id_valid,

            "verification_mapping_valid":
                verification_mapping_valid,

            "verification_passed":
                verification_passed,

            "identity_verified":
                identity_verified,

            "actions_verified":
                actions_verified,

            "safety_verified":
                safety_verified,

            "reproducibility_verified":
                reproducibility_verified,

            "verification_identity_matches":
                verification_identity_matches,

            "embedded_verification_checksum_valid":
                embedded_verification_checksum_valid,

            "certification_verification_checksum_matches":
                certification_verification_checksum_matches,

            "verification_flags_match":
                verification_flags_match,

            "count_fields_match":
                count_fields_match,

            "certification_scope_valid":
                certification_scope_valid,

            "planner_mode_valid":
                planner_mode_valid,

            "safety_boundaries_valid":
                safety_boundaries_valid,

            "certification_checksum_valid":
                certification_checksum_valid,

            "calculated_verification_checksum":
                calculated_verification_checksum,

            "calculated_certification_checksum":
                calculated_certification_checksum,

            "stored_certification_checksum":
                certificate.get(
                    "certification_checksum"
                ),

            "repair_executed":
                False,

            "production_mutation_allowed":
                False,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,
        }
    )
def build_lifecycle_repair_planner_certification_bundle_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    certification = (
        build_lifecycle_repair_planner_certification_v1(
            planner_request=planner_request,
            scanner_certification=scanner_certification,
            findings=findings,
            repair_plan=repair_plan,
        )
    )

    validation = (
        validate_lifecycle_repair_planner_certification_v1(
            certification=certification,
        )
    )

    if (
        validation[
            "certification_valid"
        ]
        is not True
    ):
        raise LifecycleRepairPlannerCertificationError(
            "Lifecycle Repair Planner certification "
            "failed independent validation."
        )

    summary = (
        summarize_lifecycle_repair_planner_certification_v1(
            certification=certification,
        )
    )

    bundle = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA,

        "certification_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,

        "bundle_certified":
            validation[
                "certification_valid"
            ]
            is True,

        "certification":
            certification,

        "validation":
            validation,

        "summary":
            summary,

        "certification_id":
            certification[
                "certification_id"
            ],

        "repair_plan_id":
            certification[
                "repair_plan_id"
            ],

        "repair_plan_request_id":
            certification[
                "repair_plan_request_id"
            ],

        "workspace_id":
            certification[
                "workspace_id"
            ],

        "verification_checksum":
            certification[
                "verification_checksum"
            ],

        "certification_checksum":
            certification[
                "certification_checksum"
            ],

        "certification_scope":
            "REPAIR_PLANNER_ONLY",

        "planner_mode":
            "PLAN_ONLY",

        "repair_plan_generated":
            certification[
                "repair_plan_generated"
            ]
            is True,

        "repair_planned":
            certification[
                "repair_planned"
            ]
            is True,

        "execution_authorized":
            False,

        "execution_status":
            "NOT_EXECUTED",

        "repair_executed":
            False,

        "read_only":
            True,

        "production_mutation_allowed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    bundle_checksum_source = dict(
        bundle
    )

    bundle[
        "bundle_checksum"
    ] = (
        calculate_lifecycle_repair_planner_certification_checksum_v1(
            payload=bundle_checksum_source,
        )
    )

    return _freeze(
        bundle
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION",
    "LifecycleRepairPlannerCertificationError",
    "calculate_lifecycle_repair_planner_certification_checksum_v1",
    "build_lifecycle_repair_planner_certification_v1",
    "summarize_lifecycle_repair_planner_certification_v1",
    "validate_lifecycle_repair_planner_certification_v1",
    "build_lifecycle_repair_planner_certification_bundle_v1",
]
