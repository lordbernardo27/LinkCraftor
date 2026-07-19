from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

AUTOMATION_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "website_article_integrity_automation.py"
)

QUEUE_RUNNER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "workers"
    / "universal_knowledge_queue_runner.py"
)

REGISTRATION_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "integrity"
    / "website_article_integrity"
    / "website_article_integrity_runtime_registration.py"
)


AUTOMATION_SOURCE = r'''"""Website Article Integrity automatic runtime continuation.

The automation uses the existing Universal Runtime Infrastructure.

Responsibilities:
- Detect complete UDARE queue drainage.
- Reconcile the completed UDARE Store.
- Create the first Website Article Integrity job exactly once.
- Create each succeeding integrity job exactly once.
- Derive quarantine counts from the integrity report.
- Derive certification counts from quarantine output.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUTOMATION_VERSION = (
    "website_article_integrity_automation_v1"
)

UDARE_JOB_TYPE = "udare_reconstruction"

PIPELINE = "website_article_integrity"

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

STAGE_STRUCTURE = "structure_validation"
STAGE_COMPONENTS = "component_validation"
STAGE_CORRUPTION = "corruption_truncation"
STAGE_REPORT = "report_generation"
STAGE_QUARANTINE = "quarantine"
STAGE_CERTIFICATION = "certification"

STAGE_SUCCESSORS: dict[
    str,
    tuple[str, str] | None,
] = {
    STAGE_STRUCTURE: (
        JOB_TYPE_COMPONENTS,
        STAGE_COMPONENTS,
    ),
    STAGE_COMPONENTS: (
        JOB_TYPE_CORRUPTION,
        STAGE_CORRUPTION,
    ),
    STAGE_CORRUPTION: (
        JOB_TYPE_REPORT,
        STAGE_REPORT,
    ),
    STAGE_REPORT: (
        JOB_TYPE_QUARANTINE,
        STAGE_QUARANTINE,
    ),
    STAGE_QUARANTINE: (
        JOB_TYPE_CERTIFICATION,
        STAGE_CERTIFICATION,
    ),
    STAGE_CERTIFICATION: None,
}

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

AUTOMATION_ROOT = (
    DATA_ROOT
    / "runtime"
    / "website_article_integrity_automation"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def safe_id(
    value: Any,
) -> str:
    text = str(
        value or ""
    ).strip()

    normalized = "".join(
        character
        if (
            character.isalnum()
            or character in {"-", "_", "."}
        )
        else "_"
        for character in text
    )

    normalized = normalized.strip(
        "._"
    )

    return normalized or "default"


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def atomic_write_json(
    path: Path,
    value: Mapping[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = (
        tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
        )
    )

    temporary_path = Path(
        temporary_name
    )

    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            json.dump(
                dict(value),
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )

            handle.write("\n")
            handle.flush()
            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary_path,
            path,
        )

    finally:
        temporary_path.unlink(
            missing_ok=True,
        )


def load_json(
    path: Path,
) -> dict[str, Any]:
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


def read_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []

    records: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()

            if not line:
                continue

            try:
                value = json.loads(
                    line
                )
            except json.JSONDecodeError:
                continue

            if isinstance(
                value,
                dict,
            ):
                records.append(
                    value
                )

    return records


def _integer_value(
    value: Any,
) -> int | None:
    try:
        converted = int(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if converted < 0:
        return None

    return converted


def _first_integer(
    mapping: Mapping[str, Any],
    names: Iterable[str],
) -> int | None:
    for name in names:
        value = _integer_value(
            mapping.get(name)
        )

        if value is not None:
            return value

    return None


def _job_type(
    job: Mapping[str, Any],
) -> str:
    return str(
        job.get("job_type")
        or job.get("stage")
        or ""
    ).strip()


def _job_payload(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    value = job.get(
        "payload",
        {},
    )

    if not isinstance(
        value,
        Mapping,
    ):
        return {}

    return dict(value)


def _job_metadata(
    job: Mapping[str, Any],
) -> dict[str, Any]:
    payload = _job_payload(job)

    value = payload.get(
        "metadata",
        {},
    )

    if not isinstance(
        value,
        Mapping,
    ):
        return {}

    return dict(value)


def _marker_root(
    workspace_id: str,
) -> Path:
    return (
        AUTOMATION_ROOT
        / safe_id(workspace_id)
    )


def _trigger_marker_path(
    workspace_id: str,
) -> Path:
    return (
        _marker_root(workspace_id)
        / "udare_to_integrity_trigger.json"
    )


def _trigger_lock_path(
    workspace_id: str,
) -> Path:
    return (
        _marker_root(workspace_id)
        / "udare_to_integrity_trigger.lock"
    )


def _acquire_lock(
    path: Path,
) -> int | None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        return os.open(
            path,
            os.O_CREAT
            | os.O_EXCL
            | os.O_WRONLY,
        )
    except FileExistsError:
        return None


def _release_lock(
    path: Path,
    descriptor: int | None,
) -> None:
    if descriptor is not None:
        try:
            os.close(
                descriptor
            )
        except OSError:
            pass

    path.unlink(
        missing_ok=True,
    )


def _all_runtime_jobs(
    workspace_id: str,
) -> list[dict[str, Any]]:
    from backend.server.jobs.universal_knowledge_orchestrator import (
        job_ledger_path,
        read_queue,
    )

    queued = read_queue(
        workspace_id,
        limit=100000,
    )

    ledger = read_jsonl(
        job_ledger_path(
            workspace_id
        )
    )

    combined: list[
        dict[str, Any]
    ] = []

    seen_job_ids: set[str] = set()

    for record in [
        *queued,
        *ledger,
    ]:
        if not isinstance(
            record,
            dict,
        ):
            continue

        job_id = str(
            record.get("job_id")
            or ""
        ).strip()

        if job_id and job_id in seen_job_ids:
            continue

        if job_id:
            seen_job_ids.add(
                job_id
            )

        combined.append(
            record
        )

    return combined


def _find_existing_pipeline_job(
    *,
    workspace_id: str,
    integrity_run_id: str,
    job_type: str,
) -> dict[str, Any] | None:
    for job in _all_runtime_jobs(
        workspace_id
    ):
        if _job_type(job) != job_type:
            continue

        payload = _job_payload(
            job
        )

        if (
            str(
                payload.get(
                    "integrity_run_id"
                )
                or ""
            ).strip()
            == integrity_run_id
        ):
            return job

    return None


def _create_pipeline_job_once(
    *,
    workspace_id: str,
    integrity_run_id: str,
    job_type: str,
    stage: str,
    payload: Mapping[str, Any],
    parent_job_id: str = "",
    batch_id: str = "",
    user_id: str = "system",
    product_id: str = "linkcraftor",
    priority: int = 4,
) -> dict[str, Any]:
    existing = (
        _find_existing_pipeline_job(
            workspace_id=workspace_id,
            integrity_run_id=(
                integrity_run_id
            ),
            job_type=job_type,
        )
    )

    if existing is not None:
        return {
            "ok": True,
            "created": False,
            "already_exists": True,
            "job_id": existing.get(
                "job_id"
            ),
            "job_type": job_type,
            "stage": stage,
            "status": existing.get(
                "status"
            ),
        }

    from backend.server.jobs.universal_knowledge_orchestrator import (
        create_universal_knowledge_job,
    )

    job_payload = dict(
        payload
    )

    job_payload[
        "integrity_run_id"
    ] = integrity_run_id

    job_payload[
        "pipeline"
    ] = PIPELINE

    job_payload[
        "stage"
    ] = stage

    job_payload[
        "auto_continue"
    ] = True

    job = create_universal_knowledge_job(
        workspace_id=workspace_id,
        job_type=job_type,
        payload=job_payload,
        user_id=user_id,
        product_id=product_id,
        pipeline=PIPELINE,
        stage=stage,
        payload_ref=str(
            job_payload.get(
                "payload_ref"
            )
            or job_payload.get(
                "udare_manifest_path"
            )
            or integrity_run_id
        ),
        priority=priority,
        parent_job_id=parent_job_id,
        batch_id=(
            batch_id
            or integrity_run_id
        ),
        enqueue=True,
    )

    return {
        "ok": True,
        "created": True,
        "already_exists": False,
        "job_id": job.get(
            "job_id"
        ),
        "job_type": job_type,
        "stage": stage,
        "status": job.get(
            "status"
        ),
        "job": job,
    }


def _derive_expected_upstream_count(
    *,
    processed_udare_jobs: list[
        Mapping[str, Any]
    ],
    manifest: Mapping[str, Any],
    actual_store_count: int,
) -> int:
    candidates: list[int] = []

    for job in processed_udare_jobs:
        payload = _job_payload(
            job
        )

        metadata = _job_metadata(
            job
        )

        for mapping in (
            payload,
            metadata,
        ):
            value = _first_integer(
                mapping,
                (
                    "expected_upstream_count",
                    "population_count",
                    "source_record_count",
                    "raw_html_record_count",
                ),
            )

            if value is not None:
                candidates.append(
                    value
                )

    manifest_value = _first_integer(
        manifest,
        (
            "expected_upstream_count",
            "source_record_count",
            "population_count",
        ),
    )

    if manifest_value is not None:
        candidates.append(
            manifest_value
        )

    if candidates:
        return max(candidates)

    return actual_store_count


def _derive_population_batch_id(
    processed_udare_jobs: list[
        Mapping[str, Any]
    ],
) -> str:
    for job in reversed(
        processed_udare_jobs
    ):
        payload = _job_payload(
            job
        )

        metadata = _job_metadata(
            job
        )

        value = str(
            job.get("batch_id")
            or metadata.get(
                "population_batch_id"
            )
            or payload.get(
                "correlation_id"
            )
            or ""
        ).strip()

        if value:
            return value

    return ""


def _manifest_path(
    workspace_id: str,
) -> Path:
    return (
        DATA_ROOT
        / "udare_store"
        / safe_id(workspace_id)
        / "manifests"
        / "udare_store_manifest.json"
    )


def maybe_trigger_website_article_integrity_after_udare_queue_drain(
    *,
    workspace_id: str,
    processed_jobs: Iterable[
        Mapping[str, Any]
    ],
    execution_results: Iterable[
        Mapping[str, Any]
    ],
    remaining_jobs: Iterable[
        Mapping[str, Any]
    ],
) -> dict[str, Any]:
    processed_udare_jobs = [
        job
        for job in processed_jobs
        if _job_type(job)
        == UDARE_JOB_TYPE
    ]

    if not processed_udare_jobs:
        return {
            "ok": True,
            "status": "NOT_APPLICABLE",
            "reason": (
                "No UDARE jobs were processed."
            ),
        }

    remaining_udare_jobs = [
        job
        for job in remaining_jobs
        if (
            _job_type(job)
            == UDARE_JOB_TYPE
            and str(
                job.get("status")
                or "queued"
            ).strip().lower()
            in {
                "queued",
                "registered",
                "running",
                "retrying",
            }
        )
    ]

    if remaining_udare_jobs:
        return {
            "ok": True,
            "status": "WAITING_FOR_UDARE",
            "remaining_udare_jobs": len(
                remaining_udare_jobs
            ),
        }

    workspace_id = safe_id(
        workspace_id
    )

    manifest_path = _manifest_path(
        workspace_id
    )

    if not manifest_path.is_file():
        return {
            "ok": False,
            "status": "BLOCKED",
            "reason": (
                "UDARE Store manifest does not exist."
            ),
            "manifest_path": str(
                manifest_path
            ),
        }

    manifest = load_json(
        manifest_path
    )

    record_count = _first_integer(
        manifest,
        (
            "record_count",
        ),
    )

    article_count = _first_integer(
        manifest,
        (
            "article_document_count",
        ),
    )

    metadata_count = _first_integer(
        manifest,
        (
            "metadata_record_count",
        ),
    )

    if (
        record_count is None
        or article_count is None
        or metadata_count is None
    ):
        return {
            "ok": False,
            "status": "BLOCKED",
            "reason": (
                "UDARE manifest counts are incomplete."
            ),
        }

    if not (
        record_count
        == article_count
        == metadata_count
    ):
        return {
            "ok": False,
            "status": "BLOCKED",
            "reason": (
                "UDARE article and metadata counts "
                "do not reconcile."
            ),
            "record_count": record_count,
            "article_document_count": (
                article_count
            ),
            "metadata_record_count": (
                metadata_count
            ),
        }

    expected_upstream_count = (
        _derive_expected_upstream_count(
            processed_udare_jobs=(
                processed_udare_jobs
            ),
            manifest=manifest,
            actual_store_count=record_count,
        )
    )

    if expected_upstream_count < record_count:
        return {
            "ok": False,
            "status": "BLOCKED",
            "reason": (
                "UDARE Store contains more records than "
                "the expected upstream count."
            ),
            "expected_upstream_count": (
                expected_upstream_count
            ),
            "record_count": record_count,
        }

    deferred_upstream_count = (
        expected_upstream_count
        - record_count
    )

    manifest_sha256 = sha256_file(
        manifest_path
    )

    population_batch_id = (
        _derive_population_batch_id(
            processed_udare_jobs
        )
    )

    run_seed = "|".join(
        (
            workspace_id,
            population_batch_id,
            str(expected_upstream_count),
            str(record_count),
            manifest_sha256,
        )
    )

    integrity_run_id = (
        "waini_"
        + hashlib.sha256(
            run_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    marker_path = (
        _trigger_marker_path(
            workspace_id
        )
    )

    if marker_path.is_file():
        marker = load_json(
            marker_path
        )

        if (
            marker.get(
                "integrity_run_id"
            )
            == integrity_run_id
            and marker.get("status")
            == "TRIGGERED"
        ):
            existing = (
                _find_existing_pipeline_job(
                    workspace_id=workspace_id,
                    integrity_run_id=(
                        integrity_run_id
                    ),
                    job_type=(
                        JOB_TYPE_STRUCTURE
                    ),
                )
            )

            return {
                "ok": True,
                "status": "ALREADY_TRIGGERED",
                "created": False,
                "integrity_run_id": (
                    integrity_run_id
                ),
                "job_id": (
                    existing.get("job_id")
                    if existing
                    else marker.get(
                        "first_job_id"
                    )
                ),
                "marker_path": str(
                    marker_path
                ),
            }

    lock_path = _trigger_lock_path(
        workspace_id
    )

    lock_descriptor = _acquire_lock(
        lock_path
    )

    if lock_descriptor is None:
        return {
            "ok": True,
            "status": "TRIGGER_LOCKED",
            "created": False,
            "integrity_run_id": (
                integrity_run_id
            ),
        }

    try:
        existing = (
            _find_existing_pipeline_job(
                workspace_id=workspace_id,
                integrity_run_id=(
                    integrity_run_id
                ),
                job_type=(
                    JOB_TYPE_STRUCTURE
                ),
            )
        )

        if existing is not None:
            marker = {
                "schema_version": (
                    AUTOMATION_VERSION
                ),
                "status": "TRIGGERED",
                "workspace_id": (
                    workspace_id
                ),
                "integrity_run_id": (
                    integrity_run_id
                ),
                "first_job_id": existing.get(
                    "job_id"
                ),
                "created": False,
                "recovered_existing_job": True,
                "expected_upstream_count": (
                    expected_upstream_count
                ),
                "expected_store_count": (
                    record_count
                ),
                "deferred_upstream_count": (
                    deferred_upstream_count
                ),
                "udare_manifest_path": str(
                    manifest_path
                ),
                "udare_manifest_sha256": (
                    manifest_sha256
                ),
                "updated_at": utc_now(),
            }

            atomic_write_json(
                marker_path,
                marker,
            )

            return {
                "ok": True,
                "status": "ALREADY_TRIGGERED",
                "created": False,
                "integrity_run_id": (
                    integrity_run_id
                ),
                "job_id": existing.get(
                    "job_id"
                ),
                "marker_path": str(
                    marker_path
                ),
            }

        final_udare_job = (
            processed_udare_jobs[-1]
        )

        final_payload = _job_payload(
            final_udare_job
        )

        user_id = str(
            final_udare_job.get(
                "user_id"
            )
            or final_payload.get(
                "user_id"
            )
            or "system"
        ).strip() or "system"

        product_id = str(
            final_udare_job.get(
                "product_id"
            )
            or final_payload.get(
                "product_id"
            )
            or "linkcraftor"
        ).strip() or "linkcraftor"

        failed_execution_count = sum(
            1
            for result in execution_results
            if (
                isinstance(
                    result,
                    Mapping,
                )
                and result.get("ok")
                is not True
            )
        )

        payload = {
            "schema_version": (
                AUTOMATION_VERSION
            ),
            "operation": "execute",
            "auto_continue": True,
            "project_root": str(
                PROJECT_ROOT
            ),
            "workspace_id": workspace_id,
            "integrity_run_id": (
                integrity_run_id
            ),
            "expected_store_count": (
                record_count
            ),
            "expected_store_count_before": (
                record_count
            ),
            "expected_assessed_count": (
                record_count
            ),
            "expected_upstream_count": (
                expected_upstream_count
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "udare_manifest_path": str(
                manifest_path
            ),
            "udare_manifest_sha256": (
                manifest_sha256
            ),
            "payload_ref": str(
                manifest_path
            ),
            "trigger": {
                "type": (
                    "udare_queue_drained"
                ),
                "source_pipeline": (
                    "website_reconstruction"
                ),
                "source_stage": (
                    "udare_reconstruction"
                ),
                "population_batch_id": (
                    population_batch_id
                ),
                "processed_final_batch_count": (
                    len(
                        processed_udare_jobs
                    )
                ),
                "failed_final_batch_count": (
                    failed_execution_count
                ),
                "triggered_at": utc_now(),
            },
            "max_attempts": 3,
        }

        created = (
            _create_pipeline_job_once(
                workspace_id=workspace_id,
                integrity_run_id=(
                    integrity_run_id
                ),
                job_type=(
                    JOB_TYPE_STRUCTURE
                ),
                stage=STAGE_STRUCTURE,
                payload=payload,
                parent_job_id=str(
                    final_udare_job.get(
                        "job_id"
                    )
                    or ""
                ),
                batch_id=(
                    population_batch_id
                    or integrity_run_id
                ),
                user_id=user_id,
                product_id=product_id,
                priority=4,
            )
        )

        marker = {
            "schema_version": (
                AUTOMATION_VERSION
            ),
            "status": "TRIGGERED",
            "workspace_id": workspace_id,
            "integrity_run_id": (
                integrity_run_id
            ),
            "first_job_id": created.get(
                "job_id"
            ),
            "created": created.get(
                "created"
            ),
            "expected_upstream_count": (
                expected_upstream_count
            ),
            "expected_store_count": (
                record_count
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "udare_manifest_path": str(
                manifest_path
            ),
            "udare_manifest_sha256": (
                manifest_sha256
            ),
            "population_batch_id": (
                population_batch_id
            ),
            "triggered_at": utc_now(),
        }

        atomic_write_json(
            marker_path,
            marker,
        )

        return {
            "ok": True,
            "status": "TRIGGERED",
            "created": created.get(
                "created"
            ),
            "integrity_run_id": (
                integrity_run_id
            ),
            "job_id": created.get(
                "job_id"
            ),
            "expected_upstream_count": (
                expected_upstream_count
            ),
            "expected_store_count": (
                record_count
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "marker_path": str(
                marker_path
            ),
        }

    finally:
        _release_lock(
            lock_path,
            lock_descriptor,
        )


def _extract_stage_document(
    stage_result: Mapping[str, Any],
) -> dict[str, Any]:
    value = stage_result.get(
        "result",
        {},
    )

    if isinstance(
        value,
        Mapping,
    ):
        return dict(value)

    return {}


def _derive_report_counts(
    document: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> dict[str, int]:
    summary_value = document.get(
        "summary",
        {},
    )

    summary = (
        dict(summary_value)
        if isinstance(
            summary_value,
            Mapping,
        )
        else {}
    )

    assessed = _first_integer(
        summary,
        (
            "articles_assessed",
            "total_articles",
            "total_records",
            "integrity_ledger_count",
        ),
    )

    if assessed is None:
        assessed = _first_integer(
            payload,
            (
                "expected_store_count",
                "expected_assessed_count",
            ),
        )

    failed = _first_integer(
        summary,
        (
            "overall_fail_count",
            "failed_count",
            "articles_failed",
            "quarantine_candidate_count",
            "distinct_failed_article_count",
        ),
    )

    passed = _first_integer(
        summary,
        (
            "overall_pass_count",
            "pass_count",
            "articles_passed",
            "active_pass_count",
        ),
    )

    if failed is None:
        failed = _first_integer(
            document,
            (
                "quarantine_candidate_count",
                "distinct_failed_article_count",
            ),
        )

    if (
        passed is None
        and assessed is not None
        and failed is not None
    ):
        passed = assessed - failed

    if (
        failed is None
        and assessed is not None
        and passed is not None
    ):
        failed = assessed - passed

    if (
        assessed is None
        or passed is None
        or failed is None
    ):
        raise RuntimeError(
            "Unable to derive quarantine counts "
            "from the Website Integrity Report."
        )

    if passed + failed != assessed:
        raise RuntimeError(
            "Website Integrity Report PASS and FAIL "
            "counts do not reconcile."
        )

    return {
        "expected_store_count_before": (
            assessed
        ),
        "expected_assessed_count": (
            assessed
        ),
        "expected_active_count_after": (
            passed
        ),
        "expected_active_count": (
            passed
        ),
        "expected_quarantine_count": (
            failed
        ),
    }


def _derive_quarantine_counts(
    document: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> dict[str, int]:
    active = _first_integer(
        document,
        (
            "active_record_count_after",
            "active_record_count",
        ),
    )

    quarantined = _first_integer(
        document,
        (
            "quarantined_record_count",
        ),
    )

    deferred = _first_integer(
        document,
        (
            "deferred_upstream_count",
        ),
    )

    assessed = _first_integer(
        payload,
        (
            "expected_assessed_count",
            "expected_store_count",
            "expected_store_count_before",
        ),
    )

    upstream = _first_integer(
        payload,
        (
            "expected_upstream_count",
        ),
    )

    if active is None:
        active = _first_integer(
            payload,
            (
                "expected_active_count_after",
                "expected_active_count",
            ),
        )

    if quarantined is None:
        quarantined = _first_integer(
            payload,
            (
                "expected_quarantine_count",
            ),
        )

    if deferred is None:
        deferred = _first_integer(
            payload,
            (
                "deferred_upstream_count",
            ),
        )

    if (
        active is None
        or quarantined is None
        or deferred is None
        or assessed is None
        or upstream is None
    ):
        raise RuntimeError(
            "Unable to derive certification counts "
            "from the quarantine output."
        )

    if active + quarantined != assessed:
        raise RuntimeError(
            "Quarantine counts do not reconcile "
            "with the assessed count."
        )

    if assessed + deferred != upstream:
        raise RuntimeError(
            "Assessed and deferred counts do not "
            "reconcile with the upstream count."
        )

    return {
        "expected_assessed_count": (
            assessed
        ),
        "expected_active_count": (
            active
        ),
        "expected_active_count_after": (
            active
        ),
        "expected_quarantine_count": (
            quarantined
        ),
        "deferred_upstream_count": (
            deferred
        ),
        "expected_upstream_count": (
            upstream
        ),
    }


def enqueue_website_article_integrity_successor(
    *,
    job: Mapping[str, Any],
    current_stage: str,
    stage_result: Mapping[str, Any],
) -> dict[str, Any]:
    successor = STAGE_SUCCESSORS.get(
        current_stage
    )

    if successor is None:
        return {
            "ok": True,
            "status": (
                "PIPELINE_COMPLETE"
            ),
            "created": False,
            "current_stage": (
                current_stage
            ),
        }

    payload = _job_payload(
        job
    )

    if (
        payload.get(
            "auto_continue",
            True,
        )
        is False
    ):
        return {
            "ok": True,
            "status": (
                "AUTO_CONTINUATION_DISABLED"
            ),
            "created": False,
            "current_stage": (
                current_stage
            ),
        }

    workspace_id = safe_id(
        job.get("workspace_id")
        or payload.get(
            "workspace_id"
        )
        or ""
    )

    integrity_run_id = str(
        payload.get(
            "integrity_run_id"
        )
        or ""
    ).strip()

    if not integrity_run_id:
        seed = "|".join(
            (
                workspace_id,
                str(
                    payload.get(
                        "udare_manifest_sha256"
                    )
                    or payload.get(
                        "payload_ref"
                    )
                    or ""
                ),
                str(
                    payload.get(
                        "expected_store_count"
                    )
                    or ""
                ),
            )
        )

        integrity_run_id = (
            "waini_"
            + hashlib.sha256(
                seed.encode("utf-8")
            ).hexdigest()[:24]
        )

    successor_job_type, successor_stage = (
        successor
    )

    successor_payload = dict(
        payload
    )

    successor_payload[
        "operation"
    ] = "execute"

    successor_payload[
        "auto_continue"
    ] = True

    successor_payload[
        "integrity_run_id"
    ] = integrity_run_id

    successor_payload[
        "previous_stage"
    ] = current_stage

    successor_payload[
        "stage"
    ] = successor_stage

    successor_payload[
        "job_type"
    ] = successor_job_type

    document = _extract_stage_document(
        stage_result
    )

    if current_stage == STAGE_REPORT:
        successor_payload.update(
            _derive_report_counts(
                document,
                successor_payload,
            )
        )

    if current_stage == STAGE_QUARANTINE:
        successor_payload.update(
            _derive_quarantine_counts(
                document,
                successor_payload,
            )
        )

    created = _create_pipeline_job_once(
        workspace_id=workspace_id,
        integrity_run_id=(
            integrity_run_id
        ),
        job_type=successor_job_type,
        stage=successor_stage,
        payload=successor_payload,
        parent_job_id=str(
            job.get("job_id")
            or ""
        ),
        batch_id=str(
            job.get("batch_id")
            or integrity_run_id
        ),
        user_id=str(
            job.get("user_id")
            or "system"
        ),
        product_id=str(
            job.get("product_id")
            or "linkcraftor"
        ),
        priority=int(
            job.get("priority")
            or 4
        ),
    )

    return {
        "ok": True,
        "status": (
            "SUCCESSOR_CREATED"
            if created.get("created")
            else "SUCCESSOR_ALREADY_EXISTS"
        ),
        "created": created.get(
            "created"
        ),
        "current_stage": (
            current_stage
        ),
        "successor_stage": (
            successor_stage
        ),
        "successor_job_type": (
            successor_job_type
        ),
        "successor_job_id": (
            created.get("job_id")
        ),
        "integrity_run_id": (
            integrity_run_id
        ),
    }
'''


QUEUE_RUNNER_FUNCTION = r'''def run_universal_knowledge_queue_v1(
    *,
    workspace_id: str,
    max_jobs: int = 20,
    job_type: str | None = None,
) -> Dict[str, Any]:
    ws = safe_id(workspace_id)
    queued = read_queue(
        ws,
        limit=10000,
    )

    pending = []
    remaining = []

    for job in queued:
        if job.get("status") != "queued":
            remaining.append(job)
            continue

        if (
            job_type
            and job.get("job_type")
            != job_type
        ):
            remaining.append(job)
            continue

        if len(pending) < int(max_jobs):
            pending.append(job)
        else:
            remaining.append(job)

    results = []

    for job in pending:
        result = execute_universal_knowledge_job_v1(
            job
        )

        results.append(result)

    pending_job_ids = {
        str(
            job.get("job_id")
            or ""
        )
        for job in pending
        if str(
            job.get("job_id")
            or ""
        ).strip()
    }

    latest_queue = read_queue(
        ws,
        limit=100000,
    )

    final_remaining = []
    seen_job_ids = set()

    for job in [
        *remaining,
        *latest_queue,
    ]:
        current_job_id = str(
            job.get("job_id")
            or ""
        ).strip()

        if (
            current_job_id
            and current_job_id
            in pending_job_ids
        ):
            continue

        deduplication_key = (
            current_job_id
            or repr(job)
        )

        if (
            deduplication_key
            in seen_job_ids
        ):
            continue

        seen_job_ids.add(
            deduplication_key
        )

        final_remaining.append(
            job
        )

    _write_remaining_queue_v1(
        ws,
        final_remaining,
    )

    from backend.server.runtime.website_article_integrity_automation import (
        maybe_trigger_website_article_integrity_after_udare_queue_drain,
    )

    post_run_automation = (
        maybe_trigger_website_article_integrity_after_udare_queue_drain(
            workspace_id=ws,
            processed_jobs=pending,
            execution_results=results,
            remaining_jobs=final_remaining,
        )
    )

    return {
        "ok": True,
        "workspace_id": ws,
        "max_jobs": int(max_jobs),
        "job_type_filter": job_type,
        "jobs_selected": len(pending),
        "jobs_executed": len(results),
        "jobs_remaining": len(
            final_remaining
        ),
        "results": results,
        "post_run_automation": (
            post_run_automation
        ),
    }
'''


REGISTRATION_HANDLE_STAGE_FUNCTION = r'''def _handle_stage(
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

    execution_result = (
        _execute_business_stage(
            stage=stage,
            project_root=project_root,
            workspace_id=workspace_id,
            payload=payload,
        )
    )

    if (
        execution_result.get("ok")
        is True
        and operation == "execute"
    ):
        from backend.server.runtime.website_article_integrity_automation import (
            enqueue_website_article_integrity_successor,
        )

        continuation = (
            enqueue_website_article_integrity_successor(
                job=job,
                current_stage=stage,
                stage_result=execution_result,
            )
        )

        execution_result[
            "runtime_continuation"
        ] = continuation

    return execution_result
'''


def replace_module_function(
    source: str,
    *,
    function_name: str,
    replacement: str,
) -> str:
    tree = ast.parse(
        source
    )

    target = None

    for node in tree.body:
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == function_name
        ):
            target = node
            break

    if target is None:
        raise RuntimeError(
            f"Function not found: {function_name}"
        )

    lines = source.splitlines(
        keepends=True
    )

    start_index = target.lineno - 1
    end_index = target.end_lineno

    replacement_text = (
        replacement.rstrip()
        + "\n\n"
    )

    return "".join(
        [
            *lines[:start_index],
            replacement_text,
            *lines[end_index:],
        ]
    )


def main() -> int:
    for required_path in (
        QUEUE_RUNNER_PATH,
        REGISTRATION_PATH,
    ):
        if not required_path.is_file():
            raise FileNotFoundError(
                f"Required source missing: {required_path}"
            )

    AUTOMATION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    AUTOMATION_PATH.write_text(
        AUTOMATION_SOURCE,
        encoding="utf-8",
    )

    queue_source = (
        QUEUE_RUNNER_PATH.read_text(
            encoding="utf-8-sig",
        )
    )

    patched_queue_source = (
        replace_module_function(
            queue_source,
            function_name=(
                "run_universal_knowledge_queue_v1"
            ),
            replacement=(
                QUEUE_RUNNER_FUNCTION
            ),
        )
    )

    ast.parse(
        patched_queue_source,
        filename=str(
            QUEUE_RUNNER_PATH
        ),
    )

    QUEUE_RUNNER_PATH.write_text(
        patched_queue_source,
        encoding="utf-8",
    )

    registration_source = (
        REGISTRATION_PATH.read_text(
            encoding="utf-8-sig",
        )
    )

    patched_registration_source = (
        replace_module_function(
            registration_source,
            function_name="_handle_stage",
            replacement=(
                REGISTRATION_HANDLE_STAGE_FUNCTION
            ),
        )
    )

    ast.parse(
        patched_registration_source,
        filename=str(
            REGISTRATION_PATH
        ),
    )

    REGISTRATION_PATH.write_text(
        patched_registration_source,
        encoding="utf-8",
    )

    for path in (
        AUTOMATION_PATH,
        QUEUE_RUNNER_PATH,
        REGISTRATION_PATH,
    ):
        ast.parse(
            path.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(path),
        )

    print(
        "WEBSITE ARTICLE INTEGRITY "
        "AUTOMATIC PIPELINE PATCH: PASS"
    )

    print(
        "Created:",
        AUTOMATION_PATH,
    )

    print(
        "Patched:",
        QUEUE_RUNNER_PATH,
    )

    print(
        "Patched:",
        REGISTRATION_PATH,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
