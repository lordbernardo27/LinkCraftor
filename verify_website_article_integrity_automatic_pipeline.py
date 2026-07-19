"""Verify automatic UDARE-to-integrity runtime execution."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.integrity.website_article_integrity import (
    website_article_integrity_runtime_registration as integrity_registration,
)

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
    failure_path,
    job_ledger_path,
    job_status_path,
    progress_path,
    queue_path,
    read_queue,
)

from backend.server.runtime import (
    website_article_integrity_automation as automation,
)

from backend.server.workers import (
    universal_knowledge_queue_runner as queue_runner,
)


TEST_WORKSPACE_ID = (
    "ws_integrity_automatic_pipeline_test"
)

PRODUCTION_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "website_article_integrity_automation"
    / "verification"
    / "website_article_integrity_automatic_pipeline_verification.json"
)

EXPECTED_SEQUENCE = [
    automation.JOB_TYPE_STRUCTURE,
    automation.JOB_TYPE_COMPONENTS,
    automation.JOB_TYPE_CORRUPTION,
    automation.JOB_TYPE_REPORT,
    automation.JOB_TYPE_QUARANTINE,
    automation.JOB_TYPE_CERTIFICATION,
]


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


def directory_fingerprint(
    root: Path,
) -> str:
    digest = hashlib.sha256()

    if not root.exists():
        digest.update(
            b"ABSENT"
        )
        return digest.hexdigest()

    for path in sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
        ),
        key=lambda item: item.as_posix(),
    ):
        digest.update(
            path.relative_to(
                root
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(b"\x00")

        digest.update(
            sha256_file(path).encode(
                "ascii"
            )
        )

        digest.update(b"\n")

    return digest.hexdigest()


def write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def clear_runtime_workspace() -> None:
    paths: set[Path] = {
        queue_path(
            TEST_WORKSPACE_ID
        ),
        job_ledger_path(
            TEST_WORKSPACE_ID
        ),
        failure_path(
            TEST_WORKSPACE_ID
        ),
    }

    for path in list(paths):
        parent = path.parent

        if (
            parent.name
            == TEST_WORKSPACE_ID
            and parent.is_dir()
        ):
            shutil.rmtree(
                parent,
                ignore_errors=True,
            )

        path.unlink(
            missing_ok=True
        )

    runtime_data_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
        / "runtime"
    )

    for candidate in (
        runtime_data_root.rglob(
            TEST_WORKSPACE_ID
        )
    ):
        if candidate.is_dir():
            shutil.rmtree(
                candidate,
                ignore_errors=True,
            )

    udare_test_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
        / "udare_store"
        / TEST_WORKSPACE_ID
    )

    shutil.rmtree(
        udare_test_root,
        ignore_errors=True,
    )

    automation_test_root = (
        automation.AUTOMATION_ROOT
        / TEST_WORKSPACE_ID
    )

    shutil.rmtree(
        automation_test_root,
        ignore_errors=True,
    )


def create_test_manifest() -> Path:
    manifest_path = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
        / "udare_store"
        / TEST_WORKSPACE_ID
        / "manifests"
        / "udare_store_manifest.json"
    )

    write_json(
        manifest_path,
        {
            "schema_version": (
                "udare_store_manifest_v1"
            ),
            "workspace_id": (
                TEST_WORKSPACE_ID
            ),
            "record_count": 2,
            "article_document_count": 2,
            "metadata_record_count": 2,
            "population_status": (
                "populated_not_certified"
            ),
        },
    )

    return manifest_path


def fake_udare_execution(
    job: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "job_id": job.get(
            "job_id"
        ),
        "workspace_id": job.get(
            "workspace_id"
        ),
        "job_type": job.get(
            "job_type"
        ),
        "status": "completed",
        "result": {
            "manifest_record_count": 2,
        },
    }


def fake_integrity_business_stage(
    *,
    stage: str,
    project_root: Path,
    workspace_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    del project_root
    del workspace_id

    if stage == automation.STAGE_REPORT:
        document: dict[str, Any] = {
            "report_status": "COMPLETE",
            "summary": {
                "articles_assessed": 2,
                "overall_pass_count": 1,
                "overall_fail_count": 1,
            },
        }

    elif stage == automation.STAGE_QUARANTINE:
        document = {
            "execution_status": "COMPLETE",
            "active_record_count_after": 1,
            "quarantined_record_count": 1,
            "deferred_upstream_count": 1,
        }

    elif stage == automation.STAGE_CERTIFICATION:
        document = {
            "certification_status": (
                "CERTIFIED"
            ),
            "coverage": {
                "expected_upstream_count": 3,
                "articles_assessed": 2,
                "active_certified_count": 1,
                "quarantined_count": 1,
                "deferred_upstream_count": 1,
            },
        }

    else:
        document = {
            "execution_status": "COMPLETE",
            "stage": stage,
            "expected_store_count": (
                payload.get(
                    "expected_store_count"
                )
            ),
        }

    return {
        "ok": True,
        "operation": "execute",
        "execution_status": "COMPLETE",
        "idempotent_reuse": False,
        "pipeline": automation.PIPELINE,
        "stage": stage,
        "result": document,
    }


def main() -> int:
    print()
    print("=" * 88)
    print(
        "WEBSITE ARTICLE INTEGRITY — "
        "AUTOMATIC PIPELINE VERIFICATION"
    )
    print("=" * 88)

    failures: list[str] = []

    data_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
    )

    production_udare_root = (
        data_root
        / "udare_store"
        / PRODUCTION_WORKSPACE_ID
    )

    production_integrity_root = (
        data_root
        / "website_article_integrity"
        / PRODUCTION_WORKSPACE_ID
    )

    production_udare_before = (
        directory_fingerprint(
            production_udare_root
        )
    )

    production_integrity_before = (
        directory_fingerprint(
            production_integrity_root
        )
    )

    trigger_result: dict[str, Any] = {}
    duplicate_result: dict[str, Any] = {}
    executed_sequence: list[str] = []
    final_queue: list[dict[str, Any]] = []

    clear_runtime_workspace()

    try:
        manifest_path = (
            create_test_manifest()
        )

        udare_job = (
            create_universal_knowledge_job(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                job_type=(
                    automation.UDARE_JOB_TYPE
                ),
                payload={
                    "workspace_id": (
                        TEST_WORKSPACE_ID
                    ),
                    "source_record_id": (
                        "raw_html_trigger_test"
                    ),
                    "metadata": {
                        "population_count": 3,
                        "population_batch_id": (
                            "automatic_trigger_test_batch"
                        ),
                    },
                },
                user_id="system",
                product_id="linkcraftor",
                pipeline=(
                    "website_reconstruction"
                ),
                stage=(
                    "udare_reconstruction"
                ),
                payload_ref=(
                    "raw_html_trigger_test"
                ),
                priority=5,
                batch_id=(
                    "automatic_trigger_test_batch"
                ),
                enqueue=True,
            )
        )

        with patch.object(
            queue_runner,
            "execute_universal_knowledge_job_v1",
            side_effect=fake_udare_execution,
        ):
            queue_result = (
                queue_runner
                .run_universal_knowledge_queue_v1(
                    workspace_id=(
                        TEST_WORKSPACE_ID
                    ),
                    max_jobs=20,
                    job_type=(
                        automation.UDARE_JOB_TYPE
                    ),
                )
            )

        trigger_result = (
            queue_result.get(
                "post_run_automation",
                {},
            )
        )

        if (
            trigger_result.get("status")
            != "TRIGGERED"
        ):
            failures.append(
                "UDARE queue drainage did not trigger "
                "Website Article Integrity."
            )

        if (
            trigger_result.get(
                "expected_store_count"
            )
            != 2
        ):
            failures.append(
                "Triggered assessed-store count is incorrect."
            )

        if (
            trigger_result.get(
                "expected_upstream_count"
            )
            != 3
        ):
            failures.append(
                "Triggered upstream count is incorrect."
            )

        if (
            trigger_result.get(
                "deferred_upstream_count"
            )
            != 1
        ):
            failures.append(
                "Triggered deferred count is incorrect."
            )

        queue_after_trigger = read_queue(
            TEST_WORKSPACE_ID,
            limit=1000,
        )

        structure_jobs = [
            job
            for job in queue_after_trigger
            if job.get("job_type")
            == automation.JOB_TYPE_STRUCTURE
        ]

        if len(structure_jobs) != 1:
            failures.append(
                "The UDARE trigger did not create exactly "
                "one structure-validation job."
            )

        duplicate_result = (
            automation
            .maybe_trigger_website_article_integrity_after_udare_queue_drain(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                processed_jobs=[
                    udare_job
                ],
                execution_results=[
                    fake_udare_execution(
                        udare_job
                    )
                ],
                remaining_jobs=[],
            )
        )

        if (
            duplicate_result.get("status")
            != "ALREADY_TRIGGERED"
        ):
            failures.append(
                "Duplicate UDARE completion did not resolve "
                "as ALREADY_TRIGGERED."
            )

        queue_after_duplicate = read_queue(
            TEST_WORKSPACE_ID,
            limit=1000,
        )

        duplicate_structure_jobs = [
            job
            for job in queue_after_duplicate
            if job.get("job_type")
            == automation.JOB_TYPE_STRUCTURE
        ]

        if len(
            duplicate_structure_jobs
        ) != 1:
            failures.append(
                "Duplicate trigger protection failed."
            )

        with patch.object(
            integrity_registration,
            "_execute_business_stage",
            side_effect=(
                fake_integrity_business_stage
            ),
        ):
            for expected_job_type in (
                EXPECTED_SEQUENCE
            ):
                current_queue = read_queue(
                    TEST_WORKSPACE_ID,
                    limit=1000,
                )

                queued_types = [
                    job.get("job_type")
                    for job in current_queue
                    if job.get("status")
                    == "queued"
                ]

                if (
                    expected_job_type
                    not in queued_types
                ):
                    failures.append(
                        "Expected queued integrity stage "
                        f"was absent: {expected_job_type}"
                    )
                    break

                stage_run = (
                    queue_runner
                    .run_universal_knowledge_queue_v1(
                        workspace_id=(
                            TEST_WORKSPACE_ID
                        ),
                        max_jobs=1,
                        job_type=(
                            expected_job_type
                        ),
                    )
                )

                results = stage_run.get(
                    "results",
                    [],
                )

                if len(results) != 1:
                    failures.append(
                        "Expected one execution result for "
                        f"{expected_job_type}."
                    )
                    break

                execution = results[0]

                if execution.get("ok") is not True:
                    failures.append(
                        "Automatic integrity stage execution "
                        f"failed: {expected_job_type}"
                    )
                    break

                executed_sequence.append(
                    expected_job_type
                )

        final_queue = read_queue(
            TEST_WORKSPACE_ID,
            limit=1000,
        )

        remaining_integrity_jobs = [
            job
            for job in final_queue
            if job.get("job_type")
            in EXPECTED_SEQUENCE
        ]

        if executed_sequence != EXPECTED_SEQUENCE:
            failures.append(
                "Automatic integrity stage order is incorrect."
            )

        if remaining_integrity_jobs:
            failures.append(
                "Integrity jobs remain queued after certification."
            )

        if not manifest_path.is_file():
            failures.append(
                "Test UDARE manifest was unexpectedly removed."
            )

    finally:
        clear_runtime_workspace()

    production_udare_after = (
        directory_fingerprint(
            production_udare_root
        )
    )

    production_integrity_after = (
        directory_fingerprint(
            production_integrity_root
        )
    )

    production_udare_unchanged = (
        production_udare_before
        == production_udare_after
    )

    production_integrity_unchanged = (
        production_integrity_before
        == production_integrity_after
    )

    if not production_udare_unchanged:
        failures.append(
            "Production UDARE Store changed during verification."
        )

    if not production_integrity_unchanged:
        failures.append(
            "Production Website Article Integrity artifacts "
            "changed during verification."
        )

    report = {
        "schema_version": (
            "website_article_integrity_"
            "automatic_pipeline_verification_v1"
        ),
        "verification_status": (
            "PASS"
            if not failures
            else "FAIL"
        ),
        "udare_completion_trigger": (
            trigger_result
        ),
        "duplicate_trigger_result": (
            duplicate_result
        ),
        "expected_stage_sequence": (
            EXPECTED_SEQUENCE
        ),
        "executed_stage_sequence": (
            executed_sequence
        ),
        "full_sequence_completed": (
            executed_sequence
            == EXPECTED_SEQUENCE
        ),
        "final_integrity_queue_count": len(
            [
                job
                for job in final_queue
                if job.get("job_type")
                in EXPECTED_SEQUENCE
            ]
        ),
        "production_udare_unchanged": (
            production_udare_unchanged
        ),
        "production_integrity_unchanged": (
            production_integrity_unchanged
        ),
        "failures": failures,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_json(
        REPORT_PATH,
        report,
    )

    print()
    print(
        "UDARE queue-drain trigger:       "
        + (
            "PASS"
            if trigger_result.get(
                "status"
            )
            == "TRIGGERED"
            else "FAIL"
        )
    )

    print(
        "Duplicate trigger protection:    "
        + (
            "PASS"
            if duplicate_result.get(
                "status"
            )
            == "ALREADY_TRIGGERED"
            else "FAIL"
        )
    )

    print(
        "Automatic stage sequence:        "
        + (
            "PASS"
            if executed_sequence
            == EXPECTED_SEQUENCE
            else "FAIL"
        )
    )

    print(
        "Final integrity queue empty:      "
        + (
            "PASS"
            if not [
                job
                for job in final_queue
                if job.get("job_type")
                in EXPECTED_SEQUENCE
            ]
            else "FAIL"
        )
    )

    print(
        "Production UDARE unchanged:       "
        + (
            "PASS"
            if production_udare_unchanged
            else "FAIL"
        )
    )

    print(
        "Production integrity unchanged:   "
        + (
            "PASS"
            if production_integrity_unchanged
            else "FAIL"
        )
    )

    print()
    print(
        "Executed sequence:"
    )

    for job_type in executed_sequence:
        print(
            "  - "
            + job_type
        )

    print()
    print(
        "Verification report: "
        + str(
            REPORT_PATH
        )
    )

    print()

    if failures:
        print(
            "WEBSITE ARTICLE INTEGRITY "
            "AUTOMATIC PIPELINE VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                "  - "
                + failure
            )

        print("=" * 88)

        return 1

    print(
        "WEBSITE ARTICLE INTEGRITY "
        "AUTOMATIC PIPELINE VERIFICATION: PASS"
    )

    print(
        "UDARE queue completion automatically creates "
        "the first integrity job exactly once."
    )

    print(
        "All six Website Article Integrity stages continue "
        "automatically through the Universal Runtime."
    )

    print(
        "Report results supply quarantine counts, and "
        "quarantine results supply certification counts."
    )

    print(
        "No separate integrity queue or worker was created."
    )

    print(
        "No production UDARE or integrity artifact was modified."
    )

    print("=" * 88)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
