from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_contract_v1 import (
    validate_lifecycle_integrity_scanner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_engine_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_FINDING_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA,
    SUPPORTED_FINDING_SEVERITIES,
    SUPPORTED_FINDING_TYPES,
    build_lifecycle_integrity_report_v1,
    calculate_lifecycle_integrity_scanner_checksum_v1,
)


BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION = "1.0"

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_verifier.v1"
)


class LifecycleIntegrityScannerVerificationError(
    ValueError
):
    """Raised when independent integrity scanner verification fails."""


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
        raise LifecycleIntegrityScannerVerificationError(
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
        raise LifecycleIntegrityScannerVerificationError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleIntegrityScannerVerificationError(
            field_name
            + " must not be empty."
        )

    return normalized


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


def calculate_lifecycle_integrity_scanner_verification_checksum_v1(
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

def verify_lifecycle_integrity_scanner_request_identity_v1(
    *,
    scan_request: Mapping[str, Any],
    integrity_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    report = _require_mapping(
        integrity_report,
        field_name="integrity_report",
    )

    request_validation = (
        validate_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    request_id_matches = (
        request.get(
            "scan_request_id"
        )
        == report.get(
            "scan_request_id"
        )
    )

    workspace_matches = (
        request.get(
            "workspace_id"
        )
        == report.get(
            "workspace_id"
        )
    )

    contract_certified = (
        report.get(
            "contract_certified"
        )
        is True
    )

    validation_passed = (
        report.get(
            "validation_passed"
        )
        is True
    )

    result = {
        "request_valid":
            request_validation[
                "request_valid"
            ]
            is True,

        "request_checksum_valid":
            request_validation[
                "checksum_valid"
            ]
            is True,

        "request_id_matches":
            request_id_matches,

        "workspace_matches":
            workspace_matches,

        "contract_certified":
            contract_certified,

        "validation_passed":
            validation_passed,

        "request_identity_verified":
            all(
                (
                    request_validation[
                        "request_valid"
                    ]
                    is True,
                    request_validation[
                        "checksum_valid"
                    ]
                    is True,
                    request_id_matches,
                    workspace_matches,
                    contract_certified,
                    validation_passed,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_lifecycle_integrity_report_structure_v1(
    *,
    integrity_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        integrity_report,
        field_name="integrity_report",
    )

    required_fields = (
        "schema",
        "engine_schema",
        "engine_version",
        "scan_request_id",
        "workspace_id",
        "contract_certified",
        "validation_passed",
        "body_store",
        "lifecycle_store",
        "archive_store",
        "tombstone_store",
        "missing_lifecycle_records",
        "missing_body_store_records",
        "orphan_archive_records",
        "orphan_tombstone_records",
        "findings",
        "finding_count",
        "stores_scanned",
        "scan_executed",
        "read_only",
        "repair_planned",
        "repair_executed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "report_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in report
    )

    schema_valid = (
        report.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA
    )

    engine_schema_valid = (
        report.get(
            "engine_schema"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA
    )

    engine_version_valid = (
        report.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION
    )

    store_sections = (
        report.get(
            "body_store"
        ),
        report.get(
            "lifecycle_store"
        ),
        report.get(
            "archive_store"
        ),
        report.get(
            "tombstone_store"
        ),
    )

    store_sections_valid = all(
        isinstance(
            section,
            Mapping,
        )
        for section in store_sections
    )

    findings = report.get(
        "findings"
    )

    findings_collection_valid = isinstance(
        findings,
        (
            tuple,
            list,
        ),
    )

    finding_count_valid = (
        findings_collection_valid
        and report.get(
            "finding_count"
        )
        == len(
            findings
        )
    )

    stores_scanned_valid = (
        report.get(
            "stores_scanned"
        )
        == 4
    )

    execution_valid = (
        report.get(
            "scan_executed"
        )
        is True
    )

    checksum_source = {
        key:
            value

        for key, value
        in report.items()

        if key != "report_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=checksum_source,
        )
    )

    report_checksum_valid = (
        calculated_checksum
        == report.get(
            "report_checksum"
        )
    )

    result = {
        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "engine_schema_valid":
            engine_schema_valid,

        "engine_version_valid":
            engine_version_valid,

        "store_sections_valid":
            store_sections_valid,

        "findings_collection_valid":
            findings_collection_valid,

        "finding_count_valid":
            finding_count_valid,

        "stores_scanned_valid":
            stores_scanned_valid,

        "execution_valid":
            execution_valid,

        "report_checksum_valid":
            report_checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            report.get(
                "report_checksum"
            ),

        "report_structure_verified":
            all(
                (
                    not missing_fields,
                    schema_valid,
                    engine_schema_valid,
                    engine_version_valid,
                    store_sections_valid,
                    findings_collection_valid,
                    finding_count_valid,
                    stores_scanned_valid,
                    execution_valid,
                    report_checksum_valid,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_lifecycle_integrity_findings_v1(
    *,
    integrity_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        integrity_report,
        field_name="integrity_report",
    )

    findings = report.get(
        "findings",
        (),
    )

    if not isinstance(
        findings,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleIntegrityScannerVerificationError(
            "findings must be a tuple or list."
        )

    finding_schema_valid = True
    finding_type_valid = True
    finding_severity_valid = True
    finding_identity_valid = True
    finding_checksum_valid = True
    finding_safety_valid = True

    duplicate_finding_ids: set[str] = set()
    seen_finding_ids: set[str] = set()

    finding_type_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}

    for finding in findings:
        if not isinstance(
            finding,
            Mapping,
        ):
            finding_schema_valid = False
            finding_type_valid = False
            finding_severity_valid = False
            finding_identity_valid = False
            finding_checksum_valid = False
            finding_safety_valid = False
            continue

        if (
            finding.get(
                "schema"
            )
            != BODY_STORE_LIFECYCLE_INTEGRITY_FINDING_SCHEMA
        ):
            finding_schema_valid = False

        finding_type = finding.get(
            "finding_type"
        )

        if finding_type not in SUPPORTED_FINDING_TYPES:
            finding_type_valid = False

        elif isinstance(
            finding_type,
            str,
        ):
            finding_type_counts[
                finding_type
            ] = (
                finding_type_counts.get(
                    finding_type,
                    0,
                )
                + 1
            )

        severity = finding.get(
            "severity"
        )

        if severity not in SUPPORTED_FINDING_SEVERITIES:
            finding_severity_valid = False

        elif isinstance(
            severity,
            str,
        ):
            severity_counts[
                severity
            ] = (
                severity_counts.get(
                    severity,
                    0,
                )
                + 1
            )

        finding_id = finding.get(
            "finding_id"
        )

        if not (
            isinstance(
                finding_id,
                str,
            )
            and finding_id.strip()
        ):
            finding_identity_valid = False

        elif finding_id in seen_finding_ids:
            duplicate_finding_ids.add(
                finding_id
            )

        else:
            seen_finding_ids.add(
                finding_id
            )

        identity_material = {
            "scan_request_id":
                finding.get(
                    "scan_request_id"
                ),

            "workspace_id":
                finding.get(
                    "workspace_id"
                ),

            "finding_type":
                finding.get(
                    "finding_type"
                ),

            "severity":
                finding.get(
                    "severity"
                ),

            "source_store":
                finding.get(
                    "source_store"
                ),

            "source_path":
                finding.get(
                    "source_path"
                ),

            "body_id":
                finding.get(
                    "body_id"
                ),

            "lifecycle_state":
                finding.get(
                    "lifecycle_state"
                ),

            "message":
                finding.get(
                    "message"
                ),

            "evidence":
                finding.get(
                    "evidence",
                    {},
                ),
        }

        expected_finding_id = (
            "lifecycle_integrity_finding_"
            + calculate_lifecycle_integrity_scanner_checksum_v1(
                payload=identity_material,
            )
        )

        if finding_id != expected_finding_id:
            finding_identity_valid = False

        checksum_source = {
            key:
                value

            for key, value
            in finding.items()

            if key != "finding_checksum"
        }

        calculated_finding_checksum = (
            calculate_lifecycle_integrity_scanner_checksum_v1(
                payload=checksum_source,
            )
        )

        if (
            calculated_finding_checksum
            != finding.get(
                "finding_checksum"
            )
        ):
            finding_checksum_valid = False

        if not all(
            (
                finding.get(
                    "read_only"
                )
                is True,
                finding.get(
                    "repair_planned"
                )
                is False,
                finding.get(
                    "repair_executed"
                )
                is False,
            )
        ):
            finding_safety_valid = False

    duplicate_finding_ids_absent = (
        not duplicate_finding_ids
    )

    finding_count_matches = (
        report.get(
            "finding_count"
        )
        == len(
            findings
        )
    )

    result = {
        "finding_schema_valid":
            finding_schema_valid,

        "finding_type_valid":
            finding_type_valid,

        "finding_severity_valid":
            finding_severity_valid,

        "finding_identity_valid":
            finding_identity_valid,

        "finding_checksum_valid":
            finding_checksum_valid,

        "finding_safety_valid":
            finding_safety_valid,

        "duplicate_finding_ids_absent":
            duplicate_finding_ids_absent,

        "duplicate_finding_ids":
            tuple(
                sorted(
                    duplicate_finding_ids
                )
            ),

        "finding_count_matches":
            finding_count_matches,

        "finding_type_counts":
            finding_type_counts,

        "severity_counts":
            severity_counts,

        "findings_verified":
            all(
                (
                    finding_schema_valid,
                    finding_type_valid,
                    finding_severity_valid,
                    finding_identity_valid,
                    finding_checksum_valid,
                    finding_safety_valid,
                    duplicate_finding_ids_absent,
                    finding_count_matches,
                )
            ),
    }

    return _freeze(
        result
    )
def verify_lifecycle_integrity_cross_store_accuracy_v1(
    *,
    integrity_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    report = _require_mapping(
        integrity_report,
        field_name="integrity_report",
    )

    body_store = _require_mapping(
        report[
            "body_store"
        ],
        field_name="body_store",
    )

    lifecycle_store = _require_mapping(
        report[
            "lifecycle_store"
        ],
        field_name="lifecycle_store",
    )

    archive_store = _require_mapping(
        report[
            "archive_store"
        ],
        field_name="archive_store",
    )

    tombstone_store = _require_mapping(
        report[
            "tombstone_store"
        ],
        field_name="tombstone_store",
    )

    body_ids = set(
        body_store.get(
            "body_ids",
            (),
        )
    )

    lifecycle_ids = set(
        lifecycle_store.get(
            "body_ids",
            (),
        )
    )

    archive_body_ids = set(
        archive_store.get(
            "body_ids",
            (),
        )
    )

    tombstone_body_ids = set(
        tombstone_store.get(
            "body_ids",
            (),
        )
    )

    expected_missing_lifecycle = tuple(
        sorted(
            body_ids - lifecycle_ids
        )
    )

    expected_missing_body_store = tuple(
        sorted(
            lifecycle_ids - body_ids
        )
    )

    expected_orphan_archives = tuple(
        sorted(
            archive_body_ids - lifecycle_ids
        )
    )

    expected_orphan_tombstones = tuple(
        sorted(
            tombstone_body_ids - lifecycle_ids
        )
    )

    missing_lifecycle_matches = (
        tuple(
            report.get(
                "missing_lifecycle_records",
                (),
            )
        )
        == expected_missing_lifecycle
    )

    missing_body_store_matches = (
        tuple(
            report.get(
                "missing_body_store_records",
                (),
            )
        )
        == expected_missing_body_store
    )

    orphan_archive_matches = (
        tuple(
            report.get(
                "orphan_archive_records",
                (),
            )
        )
        == expected_orphan_archives
    )

    orphan_tombstone_matches = (
        tuple(
            report.get(
                "orphan_tombstone_records",
                (),
            )
        )
        == expected_orphan_tombstones
    )

    store_read_counts_valid = all(
        (
            body_store.get(
                "json_files_read",
                0,
            )
            >= body_store.get(
                "valid_records",
                0,
            ),

            lifecycle_store.get(
                "json_files_read",
                0,
            )
            >= lifecycle_store.get(
                "valid_records",
                0,
            ),

            archive_store.get(
                "json_files_read",
                0,
            )
            >= archive_store.get(
                "valid_records",
                0,
            ),

            tombstone_store.get(
                "json_files_read",
                0,
            )
            >= tombstone_store.get(
                "valid_records",
                0,
            ),
        )
    )

    store_mutation_counts_zero = all(
        (
            body_store.get(
                "records_modified"
            )
            == 0,

            lifecycle_store.get(
                "records_modified"
            )
            == 0,

            archive_store.get(
                "records_modified"
            )
            == 0,

            tombstone_store.get(
                "records_modified"
            )
            == 0,
        )
    )

    store_finding_counts_valid = all(
        (
            body_store.get(
                "finding_count"
            )
            == len(
                body_store.get(
                    "findings",
                    (),
                )
            ),

            lifecycle_store.get(
                "finding_count"
            )
            == len(
                lifecycle_store.get(
                    "findings",
                    (),
                )
            ),

            archive_store.get(
                "finding_count"
            )
            == len(
                archive_store.get(
                    "findings",
                    (),
                )
            ),

            tombstone_store.get(
                "finding_count"
            )
            == len(
                tombstone_store.get(
                    "findings",
                    (),
                )
            ),
        )
    )

    result = {
        "missing_lifecycle_matches":
            missing_lifecycle_matches,

        "missing_body_store_matches":
            missing_body_store_matches,

        "orphan_archive_matches":
            orphan_archive_matches,

        "orphan_tombstone_matches":
            orphan_tombstone_matches,

        "store_read_counts_valid":
            store_read_counts_valid,

        "store_mutation_counts_zero":
            store_mutation_counts_zero,

        "store_finding_counts_valid":
            store_finding_counts_valid,

        "cross_store_accuracy_verified":
            all(
                (
                    missing_lifecycle_matches,
                    missing_body_store_matches,
                    orphan_archive_matches,
                    orphan_tombstone_matches,
                    store_read_counts_valid,
                    store_mutation_counts_zero,
                    store_finding_counts_valid,
                )
            ),
    }

    return _freeze(
        result
    )


def verify_lifecycle_integrity_scanner_reproducibility_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
    integrity_report: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    original_report = _require_mapping(
        integrity_report,
        field_name="integrity_report",
    )

    reproduced_report = (
        build_lifecycle_integrity_report_v1(
            project_root=project_root,
            scan_request=request,
        )
    )

    original_comparable = {
        key:
            value

        for key, value
        in original_report.items()

        if key != "report_checksum"
    }

    reproduced_comparable = {
        key:
            value

        for key, value
        in reproduced_report.items()

        if key != "report_checksum"
    }

    content_matches = (
        _json_ready(
            original_comparable
        )
        == _json_ready(
            reproduced_comparable
        )
    )

    original_checksum_source = {
        key:
            value

        for key, value
        in original_report.items()

        if key != "report_checksum"
    }

    original_checksum_valid = (
        calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=original_checksum_source,
        )
        == original_report.get(
            "report_checksum"
        )
    )

    reproduced_checksum_source = {
        key:
            value

        for key, value
        in reproduced_report.items()

        if key != "report_checksum"
    }

    reproduced_checksum_valid = (
        calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=reproduced_checksum_source,
        )
        == reproduced_report.get(
            "report_checksum"
        )
    )

    result = {
        "content_matches":
            content_matches,

        "original_checksum_valid":
            original_checksum_valid,

        "reproduced_checksum_valid":
            reproduced_checksum_valid,

        "reproducibility_verified":
            all(
                (
                    content_matches,
                    original_checksum_valid,
                    reproduced_checksum_valid,
                )
            ),

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,
    }

    return _freeze(
        result
    )
def verify_lifecycle_integrity_scanner_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    report = build_lifecycle_integrity_report_v1(
        project_root=project_root,
        scan_request=request,
    )

    request_result = (
        verify_lifecycle_integrity_scanner_request_identity_v1(
            scan_request=request,
            integrity_report=report,
        )
    )

    structure_result = (
        verify_lifecycle_integrity_report_structure_v1(
            integrity_report=report,
        )
    )

    findings_result = (
        verify_lifecycle_integrity_findings_v1(
            integrity_report=report,
        )
    )

    accuracy_result = (
        verify_lifecycle_integrity_cross_store_accuracy_v1(
            integrity_report=report,
        )
    )

    reproducibility_result = (
        verify_lifecycle_integrity_scanner_reproducibility_v1(
            project_root=project_root,
            scan_request=request,
            integrity_report=report,
        )
    )

    verification = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_SCHEMA,

        "version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION,

        "scan_request_id":
            _require_string(
                request["scan_request_id"],
                field_name="scan_request_id",
            ),

        "workspace_id":
            _require_string(
                request["workspace_id"],
                field_name="workspace_id",
            ),

        "request":
            request_result,

        "structure":
            structure_result,

        "findings":
            findings_result,

        "cross_store_accuracy":
            accuracy_result,

        "reproducibility":
            reproducibility_result,

        "verification_passed":
            all(
                (
                    request_result["request_identity_verified"],
                    structure_result["report_structure_verified"],
                    findings_result["findings_verified"],
                    accuracy_result["cross_store_accuracy_verified"],
                    reproducibility_result["reproducibility_verified"],
                )
            ),

        "read_only":
            True,

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

    verification["verification_checksum"] = (
        calculate_lifecycle_integrity_scanner_verification_checksum_v1(
            payload=verification,
        )
    )

    return _freeze(
        verification
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_SCHEMA",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION",
    "calculate_lifecycle_integrity_scanner_verification_checksum_v1",
    "verify_lifecycle_integrity_scanner_request_identity_v1",
    "verify_lifecycle_integrity_report_structure_v1",
    "verify_lifecycle_integrity_findings_v1",
    "verify_lifecycle_integrity_cross_store_accuracy_v1",
    "verify_lifecycle_integrity_scanner_reproducibility_v1",
    "verify_lifecycle_integrity_scanner_v1",
]
