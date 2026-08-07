from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_contract_v1 import (
    SUPPORTED_STATES,
    certify_lifecycle_integrity_scanner_request_v1,
    validate_lifecycle_integrity_scanner_request_v1,
)


BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION = "1.0"

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_engine.v1"
)

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_report.v1"
)

BODY_STORE_LIFECYCLE_INTEGRITY_FINDING_SCHEMA = (
    "body_store_lifecycle_integrity_finding.v1"
)

SUPPORTED_FINDING_SEVERITIES = (
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

SUPPORTED_FINDING_TYPES = (
    "STORE_ABSENT",
    "INVALID_JSON_RECORD",
    "MISSING_BODY_STORE_RECORD",
    "MISSING_LIFECYCLE_RECORD",
    "UNSUPPORTED_LIFECYCLE_STATE",
    "ARCHIVE_EVIDENCE_MISSING",
    "TOMBSTONE_EVIDENCE_MISSING",
    "ORPHAN_ARCHIVE_RECORD",
    "ORPHAN_TOMBSTONE_RECORD",
    "WORKSPACE_ID_MISMATCH",
    "BODY_ID_MISMATCH",
    "DUPLICATE_LIFECYCLE_IDENTITY",
    "CHECKSUM_MISMATCH",
    "RETENTION_STATE_INCONSISTENCY",
    "DELETED_CONTENT_STILL_PRESENT",
    "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION",
)


class LifecycleIntegrityScannerEngineError(
    ValueError
):
    """Raised when lifecycle integrity scanning cannot proceed safely."""


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
        raise LifecycleIntegrityScannerEngineError(
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
        raise LifecycleIntegrityScannerEngineError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleIntegrityScannerEngineError(
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


def calculate_lifecycle_integrity_scanner_checksum_v1(
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


def resolve_body_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleIntegrityScannerEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store"
    ).resolve()


def resolve_lifecycle_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleIntegrityScannerEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
    ).resolve()


def resolve_archive_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleIntegrityScannerEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
    ).resolve()


def resolve_tombstone_store_root_v1(
    *,
    project_root: Path,
) -> Path:

    if not isinstance(
        project_root,
        Path,
    ):
        raise LifecycleIntegrityScannerEngineError(
            "project_root must be a Path."
        )

    return (
        project_root.resolve()
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_tombstones"
    ).resolve()


def _iter_json_files(
    *,
    root: Path,
) -> Iterable[Path]:

    if not root.exists():
        return ()

    return tuple(
        path
        for path in sorted(
            root.rglob(
                "*.json"
            ),
            key=lambda candidate: (
                candidate.as_posix()
            ),
        )
        if path.is_file()
    )


def _load_json_object(
    *,
    path: Path,
) -> tuple[
    dict[str, Any] | None,
    str | None,
]:

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )

    except OSError as exc:
        return (
            None,
            "FILE_READ_ERROR: "
            + str(
                exc
            ),
        )

    except json.JSONDecodeError as exc:
        return (
            None,
            "JSON_DECODE_ERROR: "
            + str(
                exc
            ),
        )

    if not isinstance(
        payload,
        dict,
    ):
        return (
            None,
            "JSON_ROOT_NOT_OBJECT",
        )

    return (
        payload,
        None,
    )
def _extract_workspace_id(
    *,
    payload: Mapping[str, Any],
    path: Path,
    store_root: Path,
) -> str | None:

    workspace_id = payload.get(
        "workspace_id"
    )

    if (
        isinstance(
            workspace_id,
            str,
        )
        and workspace_id.strip()
    ):
        return workspace_id.strip()

    try:
        relative_path = path.relative_to(
            store_root
        )

    except ValueError:
        return None

    if not relative_path.parts:
        return None

    candidate = relative_path.parts[
        0
    ]

    if not candidate:
        return None

    return candidate


def _extract_body_id(
    *,
    payload: Mapping[str, Any],
    path: Path,
) -> str | None:

    body_id = payload.get(
        "body_id"
    )

    if (
        isinstance(
            body_id,
            str,
        )
        and body_id.strip()
    ):
        return body_id.strip()

    stem = path.stem.strip()

    if not stem:
        return None

    return stem


def _normalize_lifecycle_state(
    *,
    payload: Mapping[str, Any],
) -> str | None:

    candidates = (
        payload.get(
            "lifecycle_state"
        ),
        payload.get(
            "state"
        ),
        payload.get(
            "current_state"
        ),
        payload.get(
            "target_state"
        ),
    )

    for candidate in candidates:
        if not isinstance(
            candidate,
            str,
        ):
            continue

        normalized = (
            candidate
            .strip()
            .upper()
        )

        if normalized:
            return normalized

    return None


def _record_in_workspace(
    *,
    expected_workspace_id: str,
    record_workspace_id: str | None,
) -> bool:

    return (
        record_workspace_id
        == expected_workspace_id
    )


def create_lifecycle_integrity_finding_v1(
    *,
    scan_request_id: str,
    workspace_id: str,
    finding_type: str,
    severity: str,
    source_store: str,
    source_path: str,
    body_id: str | None,
    lifecycle_state: str | None,
    message: str,
    evidence: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:

    normalized_scan_request_id = _require_string(
        scan_request_id,
        field_name="scan_request_id",
    )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_finding_type = _require_string(
        finding_type,
        field_name="finding_type",
    ).upper()

    if (
        normalized_finding_type
        not in SUPPORTED_FINDING_TYPES
    ):
        raise LifecycleIntegrityScannerEngineError(
            "Unsupported lifecycle integrity finding type: "
            + normalized_finding_type
        )

    normalized_severity = _require_string(
        severity,
        field_name="severity",
    ).upper()

    if (
        normalized_severity
        not in SUPPORTED_FINDING_SEVERITIES
    ):
        raise LifecycleIntegrityScannerEngineError(
            "Unsupported lifecycle integrity finding severity: "
            + normalized_severity
        )

    normalized_source_store = _require_string(
        source_store,
        field_name="source_store",
    )

    normalized_source_path = _require_string(
        source_path,
        field_name="source_path",
    )

    normalized_message = _require_string(
        message,
        field_name="message",
    )

    normalized_body_id = (
        body_id.strip()
        if (
            isinstance(
                body_id,
                str,
            )
            and body_id.strip()
        )
        else None
    )

    normalized_lifecycle_state = (
        lifecycle_state.strip().upper()
        if (
            isinstance(
                lifecycle_state,
                str,
            )
            and lifecycle_state.strip()
        )
        else None
    )

    evidence_payload = (
        dict(
            evidence
        )
        if isinstance(
            evidence,
            Mapping,
        )
        else {}
    )

    finding_identity = {
        "scan_request_id":
            normalized_scan_request_id,

        "workspace_id":
            normalized_workspace_id,

        "finding_type":
            normalized_finding_type,

        "severity":
            normalized_severity,

        "source_store":
            normalized_source_store,

        "source_path":
            normalized_source_path,

        "body_id":
            normalized_body_id,

        "lifecycle_state":
            normalized_lifecycle_state,

        "message":
            normalized_message,

        "evidence":
            evidence_payload,
    }

    finding_id = (
        "lifecycle_integrity_finding_"
        + calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=finding_identity,
        )
    )

    finding = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_FINDING_SCHEMA,

        "finding_id":
            finding_id,

        **finding_identity,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "read_only":
            True,
    }

    finding[
        "finding_checksum"
    ] = (
        calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=finding,
        )
    )

    return _freeze(
        finding
    )


def _build_invalid_json_finding(
    *,
    scan_request_id: str,
    workspace_id: str,
    source_store: str,
    source_path: Path,
    error: str,
) -> Mapping[str, Any]:

    return create_lifecycle_integrity_finding_v1(
        scan_request_id=scan_request_id,
        workspace_id=workspace_id,
        finding_type="INVALID_JSON_RECORD",
        severity="ERROR",
        source_store=source_store,
        source_path=source_path.as_posix(),
        body_id=None,
        lifecycle_state=None,
        message=(
            "The integrity scanner could not read this JSON record."
        ),
        evidence={
            "error":
                error,
        },
    )


def _build_store_absent_finding(
    *,
    scan_request_id: str,
    workspace_id: str,
    source_store: str,
    store_root: Path,
) -> Mapping[str, Any]:

    return create_lifecycle_integrity_finding_v1(
        scan_request_id=scan_request_id,
        workspace_id=workspace_id,
        finding_type="STORE_ABSENT",
        severity="INFO",
        source_store=source_store,
        source_path=store_root.as_posix(),
        body_id=None,
        lifecycle_state=None,
        message=(
            "The source store is absent. "
            "This is reported as an informational condition."
        ),
        evidence={
            "store_present":
                False,
        },
    )
def collect_body_store_records_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    workspace_id = _require_string(
        request[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    scan_request_id = _require_string(
        request[
            "scan_request_id"
        ],
        field_name="scan_request_id",
    )

    store_root = (
        resolve_body_store_root_v1(
            project_root=project_root,
        )
    )

    workspace_root = (
        store_root
        / workspace_id
    ).resolve()

    findings: list[Mapping[str, Any]] = []
    records: list[dict[str, Any]] = []

    json_files_read = 0
    valid_records = 0
    invalid_records = 0
    out_of_workspace_records = 0

    if not workspace_root.exists():
        findings.append(
            _build_store_absent_finding(
                scan_request_id=scan_request_id,
                workspace_id=workspace_id,
                source_store="BODY_STORE",
                store_root=workspace_root,
            )
        )

    for path in _iter_json_files(
        root=workspace_root,
    ):
        json_files_read += 1

        payload, load_error = (
            _load_json_object(
                path=path,
            )
        )

        if payload is None:
            invalid_records += 1

            findings.append(
                _build_invalid_json_finding(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    source_store="BODY_STORE",
                    source_path=path,
                    error=(
                        load_error
                        or "UNKNOWN_JSON_ERROR"
                    ),
                )
            )

            continue

        record_workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=store_root,
            )
        )

        body_id = (
            _extract_body_id(
                payload=payload,
                path=path,
            )
        )

        if not _record_in_workspace(
            expected_workspace_id=workspace_id,
            record_workspace_id=record_workspace_id,
        ):
            out_of_workspace_records += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="WORKSPACE_ID_MISMATCH",
                    severity="ERROR",
                    source_store="BODY_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=None,
                    message=(
                        "The Body Store record workspace identity "
                        "does not match the requested workspace."
                    ),
                    evidence={
                        "expected_workspace_id":
                            workspace_id,

                        "record_workspace_id":
                            record_workspace_id,
                    },
                )
            )

            continue

        valid_records += 1

        records.append(
            {
                "source_path":
                    path.as_posix(),

                "workspace_id":
                    record_workspace_id,

                "body_id":
                    body_id,

                "payload":
                    payload,
            }
        )

    body_ids = tuple(
        sorted(
            {
                record[
                    "body_id"
                ]

                for record in records

                if record[
                    "body_id"
                ]
            }
        )
    )

    result = {
        "source_store":
            "BODY_STORE",

        "store_root":
            store_root.as_posix(),

        "workspace_root":
            workspace_root.as_posix(),

        "store_present":
            workspace_root.exists(),

        "json_files_read":
            json_files_read,

        "valid_records":
            valid_records,

        "invalid_records":
            invalid_records,

        "out_of_workspace_records":
            out_of_workspace_records,

        "body_ids":
            body_ids,

        "body_count":
            len(
                body_ids
            ),

        "records":
            tuple(
                records
            ),

        "findings":
            tuple(
                findings
            ),

        "finding_count":
            len(
                findings
            ),

        "records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_lifecycle_store_records_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    workspace_id = _require_string(
        request[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    scan_request_id = _require_string(
        request[
            "scan_request_id"
        ],
        field_name="scan_request_id",
    )

    store_root = (
        resolve_lifecycle_store_root_v1(
            project_root=project_root,
        )
    )

    workspace_root = (
        store_root
        / workspace_id
    ).resolve()

    findings: list[Mapping[str, Any]] = []
    records: list[dict[str, Any]] = []

    json_files_read = 0
    valid_records = 0
    invalid_records = 0
    out_of_workspace_records = 0
    unsupported_state_records = 0

    if not workspace_root.exists():
        findings.append(
            _build_store_absent_finding(
                scan_request_id=scan_request_id,
                workspace_id=workspace_id,
                source_store="LIFECYCLE_STORE",
                store_root=workspace_root,
            )
        )

    for path in _iter_json_files(
        root=workspace_root,
    ):
        json_files_read += 1

        payload, load_error = (
            _load_json_object(
                path=path,
            )
        )

        if payload is None:
            invalid_records += 1

            findings.append(
                _build_invalid_json_finding(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    source_store="LIFECYCLE_STORE",
                    source_path=path,
                    error=(
                        load_error
                        or "UNKNOWN_JSON_ERROR"
                    ),
                )
            )

            continue

        record_workspace_id = (
            _extract_workspace_id(
                payload=payload,
                path=path,
                store_root=store_root,
            )
        )

        body_id = (
            _extract_body_id(
                payload=payload,
                path=path,
            )
        )

        lifecycle_state = (
            _normalize_lifecycle_state(
                payload=payload,
            )
        )

        if not _record_in_workspace(
            expected_workspace_id=workspace_id,
            record_workspace_id=record_workspace_id,
        ):
            out_of_workspace_records += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="WORKSPACE_ID_MISMATCH",
                    severity="ERROR",
                    source_store="LIFECYCLE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=lifecycle_state,
                    message=(
                        "The lifecycle record workspace identity "
                        "does not match the requested workspace."
                    ),
                    evidence={
                        "expected_workspace_id":
                            workspace_id,

                        "record_workspace_id":
                            record_workspace_id,
                    },
                )
            )

            continue

        if (
            lifecycle_state
            not in SUPPORTED_STATES
        ):
            unsupported_state_records += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="UNSUPPORTED_LIFECYCLE_STATE",
                    severity="ERROR",
                    source_store="LIFECYCLE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=lifecycle_state,
                    message=(
                        "The lifecycle record contains an unsupported "
                        "or missing lifecycle state."
                    ),
                    evidence={
                        "supported_states":
                            SUPPORTED_STATES,

                        "observed_state":
                            lifecycle_state,
                    },
                )
            )

        valid_records += 1

        records.append(
            {
                "source_path":
                    path.as_posix(),

                "workspace_id":
                    record_workspace_id,

                "body_id":
                    body_id,

                "lifecycle_state":
                    lifecycle_state,

                "payload":
                    payload,
            }
        )

    body_id_counts: dict[str, int] = {}

    for record in records:
        body_id = record[
            "body_id"
        ]

        if not body_id:
            continue

        body_id_counts[
            body_id
        ] = (
            body_id_counts.get(
                body_id,
                0,
            )
            + 1
        )

    duplicate_body_ids = tuple(
        sorted(
            body_id
            for body_id, count
            in body_id_counts.items()
            if count > 1
        )
    )

    for duplicate_body_id in duplicate_body_ids:
        findings.append(
            create_lifecycle_integrity_finding_v1(
                scan_request_id=scan_request_id,
                workspace_id=workspace_id,
                finding_type="DUPLICATE_LIFECYCLE_IDENTITY",
                severity="ERROR",
                source_store="LIFECYCLE_STORE",
                source_path=workspace_root.as_posix(),
                body_id=duplicate_body_id,
                lifecycle_state=None,
                message=(
                    "More than one lifecycle record exists "
                    "for the same body identity."
                ),
                evidence={
                    "record_count":
                        body_id_counts[
                            duplicate_body_id
                        ],
                },
            )
        )

    body_ids = tuple(
        sorted(
            body_id_counts.keys()
        )
    )

    result = {
        "source_store":
            "LIFECYCLE_STORE",

        "store_root":
            store_root.as_posix(),

        "workspace_root":
            workspace_root.as_posix(),

        "store_present":
            workspace_root.exists(),

        "json_files_read":
            json_files_read,

        "valid_records":
            valid_records,

        "invalid_records":
            invalid_records,

        "out_of_workspace_records":
            out_of_workspace_records,

        "unsupported_state_records":
            unsupported_state_records,

        "duplicate_body_ids":
            duplicate_body_ids,

        "body_ids":
            body_ids,

        "body_count":
            len(
                body_ids
            ),

        "records":
            tuple(
                records
            ),

        "findings":
            tuple(
                findings
            ),

        "finding_count":
            len(
                findings
            ),

        "records_modified":
            0,
    }

    return _freeze(
        result
    )
def collect_archive_store_records_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    workspace_id = _require_string(
        request["workspace_id"],
        field_name="workspace_id",
    )

    scan_request_id = _require_string(
        request["scan_request_id"],
        field_name="scan_request_id",
    )

    store_root = resolve_archive_store_root_v1(
        project_root=project_root,
    )

    workspace_root = (
        store_root
        / workspace_id
    ).resolve()

    findings: list[Mapping[str, Any]] = []
    records: list[dict[str, Any]] = []

    json_files_read = 0
    valid_records = 0
    invalid_records = 0
    out_of_workspace_records = 0
    retention_inconsistencies = 0

    if not workspace_root.exists():
        findings.append(
            _build_store_absent_finding(
                scan_request_id=scan_request_id,
                workspace_id=workspace_id,
                source_store="ARCHIVE_STORE",
                store_root=workspace_root,
            )
        )

    for path in _iter_json_files(
        root=workspace_root,
    ):
        json_files_read += 1

        payload, load_error = _load_json_object(
            path=path,
        )

        if payload is None:
            invalid_records += 1

            findings.append(
                _build_invalid_json_finding(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    source_store="ARCHIVE_STORE",
                    source_path=path,
                    error=(
                        load_error
                        or "UNKNOWN_JSON_ERROR"
                    ),
                )
            )

            continue

        record_workspace_id = _extract_workspace_id(
            payload=payload,
            path=path,
            store_root=store_root,
        )

        body_id = _extract_body_id(
            payload=payload,
            path=path,
        )

        archive_id = payload.get(
            "archive_id"
        )

        normalized_archive_id = (
            archive_id.strip()
            if (
                isinstance(
                    archive_id,
                    str,
                )
                and archive_id.strip()
            )
            else path.stem
        )

        if not _record_in_workspace(
            expected_workspace_id=workspace_id,
            record_workspace_id=record_workspace_id,
        ):
            out_of_workspace_records += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="WORKSPACE_ID_MISMATCH",
                    severity="ERROR",
                    source_store="ARCHIVE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state="ARCHIVED",
                    message=(
                        "The archive record workspace identity "
                        "does not match the requested workspace."
                    ),
                    evidence={
                        "expected_workspace_id":
                            workspace_id,

                        "record_workspace_id":
                            record_workspace_id,

                        "archive_id":
                            normalized_archive_id,
                    },
                )
            )

            continue

        retention_expired = payload.get(
            "retention_expired"
        )

        legal_hold_active = payload.get(
            "legal_hold_active"
        )

        if (
            retention_expired is True
            and legal_hold_active is True
        ):
            retention_inconsistencies += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="RETENTION_STATE_INCONSISTENCY",
                    severity="WARNING",
                    source_store="ARCHIVE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state="ARCHIVED",
                    message=(
                        "The archive reports expired retention while "
                        "a legal hold remains active."
                    ),
                    evidence={
                        "archive_id":
                            normalized_archive_id,

                        "retention_expired":
                            retention_expired,

                        "legal_hold_active":
                            legal_hold_active,
                    },
                )
            )

        valid_records += 1

        records.append(
            {
                "source_path":
                    path.as_posix(),

                "workspace_id":
                    record_workspace_id,

                "body_id":
                    body_id,

                "archive_id":
                    normalized_archive_id,

                "retention_expired":
                    retention_expired,

                "legal_hold_active":
                    legal_hold_active,

                "payload":
                    payload,
            }
        )

    archive_ids = tuple(
        sorted(
            {
                record["archive_id"]
                for record in records
                if record["archive_id"]
            }
        )
    )

    body_ids = tuple(
        sorted(
            {
                record["body_id"]
                for record in records
                if record["body_id"]
            }
        )
    )

    result = {
        "source_store":
            "ARCHIVE_STORE",

        "store_root":
            store_root.as_posix(),

        "workspace_root":
            workspace_root.as_posix(),

        "store_present":
            workspace_root.exists(),

        "json_files_read":
            json_files_read,

        "valid_records":
            valid_records,

        "invalid_records":
            invalid_records,

        "out_of_workspace_records":
            out_of_workspace_records,

        "retention_inconsistencies":
            retention_inconsistencies,

        "archive_ids":
            archive_ids,

        "archive_count":
            len(
                archive_ids
            ),

        "body_ids":
            body_ids,

        "body_count":
            len(
                body_ids
            ),

        "records":
            tuple(
                records
            ),

        "findings":
            tuple(
                findings
            ),

        "finding_count":
            len(
                findings
            ),

        "records_modified":
            0,
    }

    return _freeze(
        result
    )


def collect_tombstone_store_records_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    workspace_id = _require_string(
        request["workspace_id"],
        field_name="workspace_id",
    )

    scan_request_id = _require_string(
        request["scan_request_id"],
        field_name="scan_request_id",
    )

    store_root = resolve_tombstone_store_root_v1(
        project_root=project_root,
    )

    workspace_root = (
        store_root
        / workspace_id
    ).resolve()

    findings: list[Mapping[str, Any]] = []
    records: list[dict[str, Any]] = []

    json_files_read = 0
    index_files_skipped = 0
    valid_records = 0
    invalid_records = 0
    out_of_workspace_records = 0
    content_boundary_violations = 0
    checksum_mismatches = 0

    forbidden_content_fields = {
        "content",
        "article_body",
        "body_text",
        "content_body",
        "raw_html",
        "html",
    }

    if not workspace_root.exists():
        findings.append(
            _build_store_absent_finding(
                scan_request_id=scan_request_id,
                workspace_id=workspace_id,
                source_store="TOMBSTONE_STORE",
                store_root=workspace_root,
            )
        )

    for path in _iter_json_files(
        root=workspace_root,
    ):
        json_files_read += 1

        if path.name == "index.json":
            index_files_skipped += 1
            continue

        payload, load_error = _load_json_object(
            path=path,
        )

        if payload is None:
            invalid_records += 1

            findings.append(
                _build_invalid_json_finding(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    source_store="TOMBSTONE_STORE",
                    source_path=path,
                    error=(
                        load_error
                        or "UNKNOWN_JSON_ERROR"
                    ),
                )
            )

            continue

        record_workspace_id = _extract_workspace_id(
            payload=payload,
            path=path,
            store_root=store_root,
        )

        body_id = _extract_body_id(
            payload=payload,
            path=path,
        )

        tombstone_id = payload.get(
            "tombstone_id"
        )

        normalized_tombstone_id = (
            tombstone_id.strip()
            if (
                isinstance(
                    tombstone_id,
                    str,
                )
                and tombstone_id.strip()
            )
            else path.stem
        )

        lifecycle_state = _normalize_lifecycle_state(
            payload=payload,
        )

        if lifecycle_state is None:
            status = payload.get(
                "status"
            )

            lifecycle_state = (
                status.strip().upper()
                if (
                    isinstance(
                        status,
                        str,
                    )
                    and status.strip()
                )
                else None
            )

        if not _record_in_workspace(
            expected_workspace_id=workspace_id,
            record_workspace_id=record_workspace_id,
        ):
            out_of_workspace_records += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="WORKSPACE_ID_MISMATCH",
                    severity="ERROR",
                    source_store="TOMBSTONE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=lifecycle_state,
                    message=(
                        "The tombstone workspace identity does not "
                        "match the requested workspace."
                    ),
                    evidence={
                        "expected_workspace_id":
                            workspace_id,

                        "record_workspace_id":
                            record_workspace_id,

                        "tombstone_id":
                            normalized_tombstone_id,
                    },
                )
            )

            continue

        exposed_fields = tuple(
            sorted(
                forbidden_content_fields.intersection(
                    payload.keys()
                )
            )
        )

        content_boundary_valid = (
            not exposed_fields
            and payload.get(
                "contains_article_body"
            )
            is False
        )

        if not content_boundary_valid:
            content_boundary_violations += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type=(
                        "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION"
                    ),
                    severity="CRITICAL",
                    source_store="TOMBSTONE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=lifecycle_state,
                    message=(
                        "The tombstone contains or claims to contain "
                        "deleted article content."
                    ),
                    evidence={
                        "tombstone_id":
                            normalized_tombstone_id,

                        "forbidden_fields":
                            exposed_fields,

                        "contains_article_body":
                            payload.get(
                                "contains_article_body"
                            ),
                    },
                )
            )

        stored_checksum = payload.get(
            "checksum"
        )

        checksum_source = {
            key:
                value

            for key, value
            in payload.items()

            if key != "checksum"
        }

        calculated_checksum = (
            calculate_lifecycle_integrity_scanner_checksum_v1(
                payload=checksum_source,
            )
        )

        checksum_valid = (
            stored_checksum is None
            or stored_checksum
            == calculated_checksum
        )

        if not checksum_valid:
            checksum_mismatches += 1

            findings.append(
                create_lifecycle_integrity_finding_v1(
                    scan_request_id=scan_request_id,
                    workspace_id=workspace_id,
                    finding_type="CHECKSUM_MISMATCH",
                    severity="CRITICAL",
                    source_store="TOMBSTONE_STORE",
                    source_path=path.as_posix(),
                    body_id=body_id,
                    lifecycle_state=lifecycle_state,
                    message=(
                        "The tombstone checksum does not match "
                        "its current stored content."
                    ),
                    evidence={
                        "tombstone_id":
                            normalized_tombstone_id,

                        "stored_checksum":
                            stored_checksum,

                        "calculated_checksum":
                            calculated_checksum,
                    },
                )
            )

        valid_records += 1

        records.append(
            {
                "source_path":
                    path.as_posix(),

                "workspace_id":
                    record_workspace_id,

                "body_id":
                    body_id,

                "tombstone_id":
                    normalized_tombstone_id,

                "archive_id":
                    payload.get(
                        "archive_id"
                    ),

                "lifecycle_state":
                    lifecycle_state,

                "content_boundary_valid":
                    content_boundary_valid,

                "checksum_valid":
                    checksum_valid,

                "payload":
                    payload,
            }
        )

    tombstone_ids = tuple(
        sorted(
            {
                record["tombstone_id"]
                for record in records
                if record["tombstone_id"]
            }
        )
    )

    body_ids = tuple(
        sorted(
            {
                record["body_id"]
                for record in records
                if record["body_id"]
            }
        )
    )

    result = {
        "source_store":
            "TOMBSTONE_STORE",

        "store_root":
            store_root.as_posix(),

        "workspace_root":
            workspace_root.as_posix(),

        "store_present":
            workspace_root.exists(),

        "json_files_read":
            json_files_read,

        "index_files_skipped":
            index_files_skipped,

        "valid_records":
            valid_records,

        "invalid_records":
            invalid_records,

        "out_of_workspace_records":
            out_of_workspace_records,

        "content_boundary_violations":
            content_boundary_violations,

        "checksum_mismatches":
            checksum_mismatches,

        "tombstone_ids":
            tombstone_ids,

        "tombstone_count":
            len(
                tombstone_ids
            ),

        "body_ids":
            body_ids,

        "body_count":
            len(
                body_ids
            ),

        "records":
            tuple(
                records
            ),

        "findings":
            tuple(
                findings
            ),

        "finding_count":
            len(
                findings
            ),

        "records_modified":
            0,
    }

    return _freeze(
        result
    )
def build_lifecycle_integrity_report_v1(
    *,
    project_root: Path,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    validation = (
        validate_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    if not validation["request_valid"]:
        raise LifecycleIntegrityScannerEngineError(
            "Lifecycle Integrity Scanner request validation failed."
        )

    certification = (
        certify_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    workspace_id = _require_string(
        request["workspace_id"],
        field_name="workspace_id",
    )

    scan_request_id = _require_string(
        request["scan_request_id"],
        field_name="scan_request_id",
    )

    body_store = collect_body_store_records_v1(
        project_root=project_root,
        scan_request=request,
    )

    lifecycle_store = collect_lifecycle_store_records_v1(
        project_root=project_root,
        scan_request=request,
    )

    archive_store = collect_archive_store_records_v1(
        project_root=project_root,
        scan_request=request,
    )

    tombstone_store = collect_tombstone_store_records_v1(
        project_root=project_root,
        scan_request=request,
    )

    findings = (
        tuple(body_store["findings"])
        + tuple(lifecycle_store["findings"])
        + tuple(archive_store["findings"])
        + tuple(tombstone_store["findings"])
    )

    body_ids = set(body_store["body_ids"])
    lifecycle_ids = set(lifecycle_store["body_ids"])
    archive_ids = set(archive_store["body_ids"])
    tombstone_ids = set(tombstone_store["body_ids"])

    missing_lifecycle = sorted(
        body_ids - lifecycle_ids
    )

    missing_body_store = sorted(
        lifecycle_ids - body_ids
    )

    orphan_archives = sorted(
        archive_ids - lifecycle_ids
    )

    orphan_tombstones = sorted(
        tombstone_ids - lifecycle_ids
    )

    report = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA,

        "engine_schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA,

        "engine_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION,

        "scan_request_id":
            scan_request_id,

        "workspace_id":
            workspace_id,

        "contract_certified":
            certification["certified"],

        "validation_passed":
            validation["request_valid"],

        "body_store":
            body_store,

        "lifecycle_store":
            lifecycle_store,

        "archive_store":
            archive_store,

        "tombstone_store":
            tombstone_store,

        "missing_lifecycle_records":
            tuple(missing_lifecycle),

        "missing_body_store_records":
            tuple(missing_body_store),

        "orphan_archive_records":
            tuple(orphan_archives),

        "orphan_tombstone_records":
            tuple(orphan_tombstones),

        "findings":
            findings,

        "finding_count":
            len(findings),

        "stores_scanned":
            4,

        "scan_executed":
            True,

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

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    report["report_checksum"] = (
        calculate_lifecycle_integrity_scanner_checksum_v1(
            payload=report,
        )
    )

    return _freeze(report)


__all__ = [
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA",
    "BODY_STORE_LIFECYCLE_INTEGRITY_FINDING_SCHEMA",
    "SUPPORTED_FINDING_SEVERITIES",
    "SUPPORTED_FINDING_TYPES",
    "build_lifecycle_integrity_report_v1",
    "collect_body_store_records_v1",
    "collect_lifecycle_store_records_v1",
    "collect_archive_store_records_v1",
    "collect_tombstone_store_records_v1",
]
