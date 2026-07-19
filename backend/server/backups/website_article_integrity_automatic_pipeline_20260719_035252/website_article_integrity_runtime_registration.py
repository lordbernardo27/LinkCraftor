"""Website Article Integrity Universal Runtime Registration.

This module connects the six Website Article Integrity business-logic
stages to the shared LinkCraftor Universal Runtime Infrastructure.

It does not create separate queues, worker pools, retry systems,
leases, dead letters, schedulers or job-state infrastructure.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Callable


REGISTRATION_VERSION = (
    "website_article_integrity_runtime_registration_v1"
)

PIPELINE = "website_article_integrity"

DEFAULT_PROJECT_ROOT = (
    Path(__file__).resolve().parents[4]
)

JOB_TYPE_STRUCTURE = (
    "website_article_structure_validation"
)

JOB_TYPE_COMPONENTS = (
    "website_article_component_validation"
)

JOB_TYPE_CORRUPTION = (
    "website_article_corruption_truncation"
)

JOB_TYPE_REPORT = (
    "website_integrity_report_generation"
)

JOB_TYPE_QUARANTINE = (
    "website_article_quarantine"
)

JOB_TYPE_CERTIFICATION = (
    "website_article_integrity_certification"
)

REGISTERED_JOB_TYPES = (
    JOB_TYPE_STRUCTURE,
    JOB_TYPE_COMPONENTS,
    JOB_TYPE_CORRUPTION,
    JOB_TYPE_REPORT,
    JOB_TYPE_QUARANTINE,
    JOB_TYPE_CERTIFICATION,
)

STAGE_STRUCTURE = "structure_validation"
STAGE_COMPONENTS = "component_validation"
STAGE_CORRUPTION = "corruption_truncation"
STAGE_REPORT = "report_generation"
STAGE_QUARANTINE = "quarantine"
STAGE_CERTIFICATION = "certification"

VALID_OPERATIONS = {
    "execute",
    "preflight",
    "registration_test",
}

COMMON_REQUIRED_FIELDS = (
    "expected_store_count",
    "expected_upstream_count",
    "deferred_upstream_count",
)

QUARANTINE_REQUIRED_FIELDS = (
    "expected_store_count_before",
    "expected_active_count_after",
    "expected_quarantine_count",
    "deferred_upstream_count",
)

CERTIFICATION_REQUIRED_FIELDS = (
    "expected_upstream_count",
    "expected_assessed_count",
    "expected_active_count",
    "expected_quarantine_count",
    "deferred_upstream_count",
)


def _payload(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    raw_payload = job.get(
        "payload",
        {},
    )

    if raw_payload is None:
        return {}

    if not isinstance(
        raw_payload,
        Mapping,
    ):
        raise TypeError(
            "Website Article Integrity job payload "
            "must be a mapping."
        )

    return dict(
        raw_payload
    )


def _workspace_id(
    job: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> str:
    value = str(
        job.get("workspace_id")
        or payload.get("workspace_id")
        or ""
    ).strip()

    if not value:
        raise ValueError(
            "Website Article Integrity runtime job "
            "has no workspace_id."
        )

    return value


def _project_root(
    payload: Mapping[str, Any],
) -> Path:
    value = payload.get(
        "project_root"
    )

    if value:
        return Path(
            str(value)
        ).expanduser().resolve()

    return DEFAULT_PROJECT_ROOT


def _operation(
    payload: Mapping[str, Any],
) -> str:
    value = str(
        payload.get("operation")
        or "execute"
    ).strip().lower()

    if value not in VALID_OPERATIONS:
        raise ValueError(
            "Unsupported Website Article Integrity "
            f"operation: {value}"
        )

    return value


def _required_integer(
    payload: Mapping[str, Any],
    field_name: str,
) -> int:
    if field_name not in payload:
        raise ValueError(
            f"Missing required payload field: {field_name}"
        )

    try:
        value = int(
            payload[field_name]
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"Payload field {field_name} must be an integer."
        ) from exc

    if value < 0:
        raise ValueError(
            f"Payload field {field_name} cannot be negative."
        )

    return value


def _load_json(
    path: Path,
) -> dict[str, Any] | None:
    if not path.is_file():
        return None

    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def _data_root(
    project_root: Path,
) -> Path:
    return (
        project_root
        / "backend"
        / "server"
        / "data"
    )


def _udare_root(
    project_root: Path,
    workspace_id: str,
) -> Path:
    return (
        _data_root(project_root)
        / "udare_store"
        / workspace_id
    )


def _integrity_root(
    project_root: Path,
    workspace_id: str,
) -> Path:
    return (
        _data_root(project_root)
        / "website_article_integrity"
        / workspace_id
    )


def _required_input_paths(
    *,
    stage: str,
    project_root: Path,
    workspace_id: str,
) -> list[Path]:
    udare_root = _udare_root(
        project_root,
        workspace_id,
    )

    integrity_root = _integrity_root(
        project_root,
        workspace_id,
    )

    structure_root = (
        integrity_root
        / "structure"
    )

    component_root = (
        integrity_root
        / "components"
    )

    corruption_root = (
        integrity_root
        / "corruption_truncation"
    )

    report_root = (
        integrity_root
        / "report"
    )

    quarantine_root = (
        integrity_root
        / "quarantine"
    )

    common_udare_paths = [
        udare_root / "articles",
        udare_root / "metadata",
        (
            udare_root
            / "manifests"
            / "udare_store_manifest.json"
        ),
    ]

    if stage == STAGE_STRUCTURE:
        return common_udare_paths

    if stage == STAGE_COMPONENTS:
        return [
            *common_udare_paths,
            (
                structure_root
                / "structure_summary.json"
            ),
        ]

    if stage == STAGE_CORRUPTION:
        return [
            *common_udare_paths,
            (
                component_root
                / "component_results.jsonl"
            ),
            (
                component_root
                / "component_summary.json"
            ),
        ]

    if stage == STAGE_REPORT:
        return [
            (
                structure_root
                / "structure_results.jsonl"
            ),
            (
                component_root
                / "component_results.jsonl"
            ),
            (
                corruption_root
                / "corruption_truncation_results.jsonl"
            ),
        ]

    if stage == STAGE_QUARANTINE:
        return [
            (
                report_root
                / "website_integrity_report.json"
            ),
            (
                report_root
                / "website_integrity_ledger.jsonl"
            ),
            (
                report_root
                / "website_integrity_failures.jsonl"
            ),
        ]

    if stage == STAGE_CERTIFICATION:
        return [
            *common_udare_paths,
            (
                udare_root
                / "index.html"
            ),
            (
                report_root
                / "website_integrity_report.json"
            ),
            (
                report_root
                / "website_integrity_ledger.jsonl"
            ),
            (
                quarantine_root
                / "manifests"
                / "quarantine_manifest.json"
            ),
            (
                quarantine_root
                / "quarantine_records.jsonl"
            ),
            (
                quarantine_root
                / "quarantine_execution.json"
            ),
        ]

    raise ValueError(
        f"Unknown Website Article Integrity stage: {stage}"
    )


def _registration_test_result(
    *,
    job_type: str,
    stage: str,
    workspace_id: str,
) -> dict[str, Any]:
    return {
        "ok": True,
        "operation": "registration_test",
        "registration_test_passed": True,
        "registration_version": (
            REGISTRATION_VERSION
        ),
        "pipeline": PIPELINE,
        "stage": stage,
        "job_type": job_type,
        "workspace_id": workspace_id,
        "business_logic_executed": False,
        "source_files_modified": False,
    }


def _preflight_result(
    *,
    job_type: str,
    stage: str,
    project_root: Path,
    workspace_id: str,
) -> dict[str, Any]:
    required_paths = (
        _required_input_paths(
            stage=stage,
            project_root=project_root,
            workspace_id=workspace_id,
        )
    )

    missing_paths = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    udare_root = _udare_root(
        project_root,
        workspace_id,
    )

    integrity_root = _integrity_root(
        project_root,
        workspace_id,
    )

    active_article_count = (
        sum(
            1
            for path in (
                udare_root
                / "articles"
            ).rglob("*.html")
            if path.is_file()
        )
        if (
            udare_root
            / "articles"
        ).is_dir()
        else 0
    )

    active_metadata_count = (
        sum(
            1
            for path in (
                udare_root
                / "metadata"
            ).glob("*.json")
            if path.is_file()
        )
        if (
            udare_root
            / "metadata"
        ).is_dir()
        else 0
    )

    quarantine_article_root = (
        integrity_root
        / "quarantine"
        / "articles"
    )

    quarantine_metadata_root = (
        integrity_root
        / "quarantine"
        / "metadata"
    )

    quarantine_article_count = (
        sum(
            1
            for path in quarantine_article_root.rglob(
                "*.html"
            )
            if path.is_file()
        )
        if quarantine_article_root.is_dir()
        else 0
    )

    quarantine_metadata_count = (
        sum(
            1
            for path in quarantine_metadata_root.glob(
                "*.json"
            )
            if path.is_file()
        )
        if quarantine_metadata_root.is_dir()
        else 0
    )

    return {
        "ok": not missing_paths,
        "operation": "preflight",
        "preflight_status": (
            "READY"
            if not missing_paths
            else "BLOCKED"
        ),
        "registration_version": (
            REGISTRATION_VERSION
        ),
        "pipeline": PIPELINE,
        "stage": stage,
        "job_type": job_type,
        "workspace_id": workspace_id,
        "required_input_count": len(
            required_paths
        ),
        "missing_input_count": len(
            missing_paths
        ),
        "missing_inputs": missing_paths,
        "active_article_count": (
            active_article_count
        ),
        "active_metadata_count": (
            active_metadata_count
        ),
        "quarantine_article_count": (
            quarantine_article_count
        ),
        "quarantine_metadata_count": (
            quarantine_metadata_count
        ),
        "business_logic_executed": False,
        "source_files_modified": False,
    }


def _existing_completion(
    *,
    stage: str,
    project_root: Path,
    workspace_id: str,
    payload: Mapping[str, Any],
) -> dict[str, Any] | None:
    integrity_root = _integrity_root(
        project_root,
        workspace_id,
    )

    if stage == STAGE_STRUCTURE:
        path = (
            integrity_root
            / "structure"
            / "structure_summary.json"
        )

        document = _load_json(path)

        if (
            document
            and document.get(
                "execution_status"
            )
            == "COMPLETE"
            and document.get(
                "articles_validated"
            )
            == _required_integer(
                payload,
                "expected_store_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    if stage == STAGE_COMPONENTS:
        path = (
            integrity_root
            / "components"
            / "component_summary.json"
        )

        document = _load_json(path)

        if (
            document
            and document.get(
                "execution_status"
            )
            == "COMPLETE"
            and document.get(
                "articles_validated"
            )
            == _required_integer(
                payload,
                "expected_store_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    if stage == STAGE_CORRUPTION:
        path = (
            integrity_root
            / "corruption_truncation"
            / "corruption_truncation_summary.json"
        )

        document = _load_json(path)

        if (
            document
            and document.get(
                "execution_status"
            )
            == "COMPLETE"
            and document.get(
                "articles_checked"
            )
            == _required_integer(
                payload,
                "expected_store_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    if stage == STAGE_REPORT:
        path = (
            integrity_root
            / "report"
            / "website_integrity_report.json"
        )

        document = _load_json(path)
        summary = (
            document.get("summary", {})
            if document
            else {}
        )

        if (
            document
            and document.get(
                "report_status"
            )
            == "COMPLETE"
            and summary.get(
                "articles_assessed"
            )
            == _required_integer(
                payload,
                "expected_store_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    if stage == STAGE_QUARANTINE:
        path = (
            integrity_root
            / "quarantine"
            / "manifests"
            / "quarantine_manifest.json"
        )

        document = _load_json(path)

        if (
            document
            and document.get(
                "execution_status"
            )
            == "COMPLETE"
            and document.get(
                "active_record_count_after"
            )
            == _required_integer(
                payload,
                "expected_active_count_after",
            )
            and document.get(
                "quarantined_record_count"
            )
            == _required_integer(
                payload,
                "expected_quarantine_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    if stage == STAGE_CERTIFICATION:
        path = (
            integrity_root
            / "certification"
            / "website_article_integrity_certificate.json"
        )

        document = _load_json(path)
        coverage = (
            document.get("coverage", {})
            if document
            else {}
        )

        if (
            document
            and document.get(
                "certification_status"
            )
            == "CERTIFIED"
            and coverage.get(
                "active_certified_count"
            )
            == _required_integer(
                payload,
                "expected_active_count",
            )
            and coverage.get(
                "quarantined_count"
            )
            == _required_integer(
                payload,
                "expected_quarantine_count",
            )
        ):
            return {
                "artifact_path": str(path),
                "document": document,
            }

    return None


def _execute_business_stage(
    *,
    stage: str,
    project_root: Path,
    workspace_id: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    force_rebuild = bool(
        payload.get("force_rebuild", False)
    )

    existing = _existing_completion(
        stage=stage,
        project_root=project_root,
        workspace_id=workspace_id,
        payload=payload,
    )

    if (
        existing is not None
        and not force_rebuild
    ):
        return {
            "ok": True,
            "operation": "execute",
            "execution_status": (
                "ALREADY_COMPLETE"
            ),
            "idempotent_reuse": True,
            "pipeline": PIPELINE,
            "stage": stage,
            "workspace_id": workspace_id,
            "artifact_path": existing[
                "artifact_path"
            ],
            "result": existing["document"],
        }

    if stage == STAGE_STRUCTURE:
        from backend.server.integrity.website_article_integrity.website_article_structure_validator import (
            run_structure_validation,
        )

        result = run_structure_validation(
            project_root=project_root,
            workspace_id=workspace_id,
            expected_store_count=(
                _required_integer(
                    payload,
                    "expected_store_count",
                )
            ),
            expected_upstream_count=(
                _required_integer(
                    payload,
                    "expected_upstream_count",
                )
            ),
            deferred_upstream_count=(
                _required_integer(
                    payload,
                    "deferred_upstream_count",
                )
            ),
        )

    elif stage == STAGE_COMPONENTS:
        from backend.server.integrity.website_article_integrity.website_article_component_validator import (
            run_component_validation,
        )

        result = run_component_validation(
            project_root=project_root,
            workspace_id=workspace_id,
            expected_store_count=(
                _required_integer(
                    payload,
                    "expected_store_count",
                )
            ),
            expected_upstream_count=(
                _required_integer(
                    payload,
                    "expected_upstream_count",
                )
            ),
            deferred_upstream_count=(
                _required_integer(
                    payload,
                    "deferred_upstream_count",
                )
            ),
        )

    elif stage == STAGE_CORRUPTION:
        from backend.server.integrity.website_article_integrity.website_article_corruption_truncation_detector import (
            run_corruption_truncation_detection,
        )

        result = (
            run_corruption_truncation_detection(
                project_root=project_root,
                workspace_id=workspace_id,
                expected_store_count=(
                    _required_integer(
                        payload,
                        "expected_store_count",
                    )
                ),
                expected_upstream_count=(
                    _required_integer(
                        payload,
                        "expected_upstream_count",
                    )
                ),
                deferred_upstream_count=(
                    _required_integer(
                        payload,
                        "deferred_upstream_count",
                    )
                ),
            )
        )

    elif stage == STAGE_REPORT:
        from backend.server.integrity.website_article_integrity.website_integrity_report_generator import (
            generate_website_integrity_report,
        )

        result = generate_website_integrity_report(
            project_root=project_root,
            workspace_id=workspace_id,
            expected_store_count=(
                _required_integer(
                    payload,
                    "expected_store_count",
                )
            ),
            expected_upstream_count=(
                _required_integer(
                    payload,
                    "expected_upstream_count",
                )
            ),
            deferred_upstream_count=(
                _required_integer(
                    payload,
                    "deferred_upstream_count",
                )
            ),
        )

    elif stage == STAGE_QUARANTINE:
        from backend.server.integrity.website_article_integrity.website_article_quarantine_manager import (
            execute_quarantine,
        )

        result = execute_quarantine(
            project_root=project_root,
            workspace_id=workspace_id,
            expected_store_count_before=(
                _required_integer(
                    payload,
                    "expected_store_count_before",
                )
            ),
            expected_active_count_after=(
                _required_integer(
                    payload,
                    "expected_active_count_after",
                )
            ),
            expected_quarantine_count=(
                _required_integer(
                    payload,
                    "expected_quarantine_count",
                )
            ),
            deferred_upstream_count=(
                _required_integer(
                    payload,
                    "deferred_upstream_count",
                )
            ),
        )

    elif stage == STAGE_CERTIFICATION:
        from backend.server.integrity.website_article_integrity.website_article_integrity_certifier import (
            certify_website_article_integrity,
        )

        result = certify_website_article_integrity(
            project_root=project_root,
            workspace_id=workspace_id,
            expected_upstream_count=(
                _required_integer(
                    payload,
                    "expected_upstream_count",
                )
            ),
            expected_assessed_count=(
                _required_integer(
                    payload,
                    "expected_assessed_count",
                )
            ),
            expected_active_count=(
                _required_integer(
                    payload,
                    "expected_active_count",
                )
            ),
            expected_quarantine_count=(
                _required_integer(
                    payload,
                    "expected_quarantine_count",
                )
            ),
            deferred_upstream_count=(
                _required_integer(
                    payload,
                    "deferred_upstream_count",
                )
            ),
        )

    else:
        raise ValueError(
            f"Unsupported integrity stage: {stage}"
        )

    return {
        "ok": True,
        "operation": "execute",
        "execution_status": "COMPLETE",
        "idempotent_reuse": False,
        "pipeline": PIPELINE,
        "stage": stage,
        "workspace_id": workspace_id,
        "result": result,
    }


def _handle_stage(
    *,
    job: Mapping[str, Any],
    job_type: str,
    stage: str,
) -> dict[str, Any]:
    if not isinstance(
        job,
        Mapping,
    ):
        raise TypeError(
            "Website Article Integrity runtime job "
            "must be a mapping."
        )

    payload = _payload(job)
    workspace_id = _workspace_id(
        job,
        payload,
    )
    project_root = _project_root(
        payload
    )
    operation = _operation(
        payload
    )

    if operation == "registration_test":
        return _registration_test_result(
            job_type=job_type,
            stage=stage,
            workspace_id=workspace_id,
        )

    if operation == "preflight":
        return _preflight_result(
            job_type=job_type,
            stage=stage,
            project_root=project_root,
            workspace_id=workspace_id,
        )

    return _execute_business_stage(
        stage=stage,
        project_root=project_root,
        workspace_id=workspace_id,
        payload=payload,
    )


def handle_structure_validation(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_STRUCTURE,
        stage=STAGE_STRUCTURE,
    )


def handle_component_validation(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_COMPONENTS,
        stage=STAGE_COMPONENTS,
    )


def handle_corruption_truncation(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_CORRUPTION,
        stage=STAGE_CORRUPTION,
    )


def handle_report_generation(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_REPORT,
        stage=STAGE_REPORT,
    )


def handle_quarantine(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_QUARANTINE,
        stage=STAGE_QUARANTINE,
    )


def handle_certification(
    *,
    job: Mapping[str, Any],
) -> dict[str, Any]:
    return _handle_stage(
        job=job,
        job_type=JOB_TYPE_CERTIFICATION,
        stage=STAGE_CERTIFICATION,
    )


REGISTRATION_DEFINITIONS: tuple[
    dict[str, Any],
    ...,
] = (
    {
        "job_type": JOB_TYPE_STRUCTURE,
        "stage": STAGE_STRUCTURE,
        "handler": handle_structure_validation,
        "description": (
            "Validate the structure of reconstructed "
            "UDARE article documents."
        ),
        "required_payload_fields": (
            COMMON_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            "udare_store_completed",
        ),
        "successor_stages": (
            STAGE_COMPONENTS,
        ),
        "phase": "4.4.1",
    },
    {
        "job_type": JOB_TYPE_COMPONENTS,
        "stage": STAGE_COMPONENTS,
        "handler": handle_component_validation,
        "description": (
            "Validate required article components "
            "and metadata identity resolution."
        ),
        "required_payload_fields": (
            COMMON_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            STAGE_STRUCTURE,
        ),
        "successor_stages": (
            STAGE_CORRUPTION,
        ),
        "phase": "4.4.2",
    },
    {
        "job_type": JOB_TYPE_CORRUPTION,
        "stage": STAGE_CORRUPTION,
        "handler": handle_corruption_truncation,
        "description": (
            "Detect corruption and truncation in "
            "reconstructed article documents."
        ),
        "required_payload_fields": (
            COMMON_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            STAGE_COMPONENTS,
        ),
        "successor_stages": (
            STAGE_REPORT,
        ),
        "phase": "4.4.3",
    },
    {
        "job_type": JOB_TYPE_REPORT,
        "stage": STAGE_REPORT,
        "handler": handle_report_generation,
        "description": (
            "Consolidate Website Article Integrity "
            "results into the integrity report."
        ),
        "required_payload_fields": (
            COMMON_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            STAGE_CORRUPTION,
        ),
        "successor_stages": (
            STAGE_QUARANTINE,
        ),
        "phase": "4.4.4",
    },
    {
        "job_type": JOB_TYPE_QUARANTINE,
        "stage": STAGE_QUARANTINE,
        "handler": handle_quarantine,
        "description": (
            "Move failed article and metadata pairs "
            "into reversible quarantine."
        ),
        "required_payload_fields": (
            QUARANTINE_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            STAGE_REPORT,
        ),
        "successor_stages": (
            STAGE_CERTIFICATION,
        ),
        "phase": "4.4.5",
    },
    {
        "job_type": JOB_TYPE_CERTIFICATION,
        "stage": STAGE_CERTIFICATION,
        "handler": handle_certification,
        "description": (
            "Certify the active Website Article "
            "Integrity PASS set."
        ),
        "required_payload_fields": (
            CERTIFICATION_REQUIRED_FIELDS
        ),
        "predecessor_stages": (
            STAGE_QUARANTINE,
        ),
        "successor_stages": (
            "article_validation",
        ),
        "phase": "4.4.6",
    },
)


HANDLER_BY_JOB_TYPE: dict[
    str,
    Callable[..., dict[str, Any]],
] = {
    definition["job_type"]: definition[
        "handler"
    ]
    for definition in REGISTRATION_DEFINITIONS
}


def register_website_article_integrity_runtime_handlers(
    *,
    persist: bool = True,
    replace: bool = True,
) -> dict[str, Any]:
    from backend.server.runtime.universal_runtime_registration import (
        ensure_persisted_runtime_registrations_loaded,
        register_runtime_handler,
        runtime_registration_snapshot,
    )

    ensure_persisted_runtime_registrations_loaded()

    registrations: list[
        dict[str, Any]
    ] = []

    for definition in REGISTRATION_DEFINITIONS:
        registrations.append(
            register_runtime_handler(
                job_type=definition[
                    "job_type"
                ],
                handler=definition[
                    "handler"
                ],
                pipeline=PIPELINE,
                stage=definition[
                    "stage"
                ],
                description=definition[
                    "description"
                ],
                required_payload_fields=(
                    definition[
                        "required_payload_fields"
                    ]
                ),
                predecessor_stages=(
                    definition[
                        "predecessor_stages"
                    ]
                ),
                successor_stages=(
                    definition[
                        "successor_stages"
                    ]
                ),
                idempotency_fields=(
                    "workspace_id",
                    "job_type",
                    "payload_ref",
                ),
                retry_policy={
                    "max_attempts": (
                        2
                        if definition[
                            "stage"
                        ]
                        in {
                            STAGE_QUARANTINE,
                            STAGE_CERTIFICATION,
                        }
                        else 3
                    ),
                    "backoff": "exponential",
                },
                concurrency_policy={
                    "scope": "workspace",
                    "max_concurrent": 1,
                },
                metadata={
                    "registration_version": (
                        REGISTRATION_VERSION
                    ),
                    "phase": definition[
                        "phase"
                    ],
                    "business_domain": (
                        "website_article_integrity"
                    ),
                    "uses_universal_runtime": True,
                    "separate_queue_required": False,
                    "separate_worker_required": False,
                },
                replace=replace,
                persist=persist,
            )
        )

    snapshot = (
        runtime_registration_snapshot()
    )

    return {
        "ok": True,
        "registration_version": (
            REGISTRATION_VERSION
        ),
        "pipeline": PIPELINE,
        "registered_count": len(
            registrations
        ),
        "registered_job_types": [
            record["job_type"]
            for record in registrations
        ],
        "registrations": registrations,
        "registry_sha256": snapshot[
            "registry_sha256"
        ],
        "persistent_registry_path": (
            snapshot[
                "persistent_registry_path"
            ]
        ),
        "automatic_trigger_registered": False,
        "automatic_trigger_note": (
            "Automatic triggering after UDARE Store "
            "completion is a separate step."
        ),
    }
