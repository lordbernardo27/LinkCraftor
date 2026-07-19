"""Verify Website Article Integrity Universal Runtime Registration."""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.integrity.website_article_integrity.website_article_integrity_runtime_registration import (
    HANDLER_BY_JOB_TYPE,
    JOB_TYPE_CERTIFICATION,
    JOB_TYPE_COMPONENTS,
    JOB_TYPE_CORRUPTION,
    JOB_TYPE_QUARANTINE,
    JOB_TYPE_REPORT,
    JOB_TYPE_STRUCTURE,
    PIPELINE,
    REGISTERED_JOB_TYPES,
    REGISTRATION_DEFINITIONS,
)

from backend.server.jobs.universal_knowledge_orchestrator import (
    SUPPORTED_JOB_TYPES,
    create_universal_knowledge_job,
    failure_path,
    job_ledger_path,
    job_status_path,
    progress_path,
    queue_path,
)

from backend.server.runtime import (
    universal_runtime_registration as registration_module,
)

from backend.server.workers.universal_knowledge_worker import (
    execute_universal_knowledge_job_v1,
)


PRODUCTION_WORKSPACE_ID = (
    "ws_whattoexpect_com"
)

TEST_WORKSPACE_ID = (
    "ws_website_article_integrity_registration_test"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "universal_runtime_registration"
    / "website_article_integrity"
    / "website_article_integrity_registration_verification.json"
)

REGISTRATION_MODULE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "integrity"
    / "website_article_integrity"
    / "website_article_integrity_runtime_registration.py"
)

PERSISTENT_REGISTRY_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "universal_runtime_registration"
    / "runtime_registration_registry.json"
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

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


def source_has_function(
    path: Path,
    function_name: str,
) -> bool:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8-sig",
        ),
        filename=str(path),
    )

    return any(
        isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == function_name
        for node in tree.body
    )


def contract_payload() -> dict[str, Any]:
    return {
        "operation": "registration_test",
        "expected_store_count": 2222,
        "expected_upstream_count": 2225,
        "deferred_upstream_count": 3,
        "expected_store_count_before": 2222,
        "expected_active_count_after": 2219,
        "expected_quarantine_count": 3,
        "expected_assessed_count": 2222,
        "expected_active_count": 2219,
    }


def preflight_payload() -> dict[str, Any]:
    value = contract_payload()
    value["operation"] = "preflight"
    value["project_root"] = str(
        PROJECT_ROOT
    )
    return value


def clean_test_artifacts(
    job_ids: list[str],
) -> None:
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

    for job_id in job_ids:
        paths.add(
            job_status_path(
                TEST_WORKSPACE_ID,
                job_id,
            )
        )

        paths.add(
            progress_path(
                TEST_WORKSPACE_ID,
                job_id,
            )
        )

    for path in paths:
        path.unlink(
            missing_ok=True
        )

    possible_workspace_directories: set[
        Path
    ] = set()

    for path in paths:
        current = path.parent

        for _ in range(6):
            if current.name == TEST_WORKSPACE_ID:
                possible_workspace_directories.add(
                    current
                )
                break

            if current == current.parent:
                break

            current = current.parent

    for directory in sorted(
        possible_workspace_directories,
        key=lambda item: len(
            item.parts
        ),
        reverse=True,
    ):
        shutil.rmtree(
            directory,
            ignore_errors=True,
        )


def main() -> int:
    print()
    print("=" * 86)
    print(
        "WEBSITE ARTICLE INTEGRITY — "
        "RUNTIME REGISTRATION VERIFICATION"
    )
    print("=" * 86)

    failures: list[str] = []
    job_ids: list[str] = []

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

    udare_fingerprint_before = (
        directory_fingerprint(
            production_udare_root
        )
    )

    integrity_fingerprint_before = (
        directory_fingerprint(
            production_integrity_root
        )
    )

    try:
        if not REGISTRATION_MODULE_PATH.is_file():
            failures.append(
                "Website Article Integrity registration "
                "module is missing."
            )
        else:
            try:
                ast.parse(
                    REGISTRATION_MODULE_PATH.read_text(
                        encoding="utf-8-sig",
                    ),
                    filename=str(
                        REGISTRATION_MODULE_PATH
                    ),
                )
            except SyntaxError as exc:
                failures.append(
                    f"Registration module syntax error: {exc}"
                )

        required_handler_functions = (
            "handle_structure_validation",
            "handle_component_validation",
            "handle_corruption_truncation",
            "handle_report_generation",
            "handle_quarantine",
            "handle_certification",
            (
                "register_website_article_integrity_"
                "runtime_handlers"
            ),
        )

        for function_name in (
            required_handler_functions
        ):
            if (
                REGISTRATION_MODULE_PATH.is_file()
                and not source_has_function(
                    REGISTRATION_MODULE_PATH,
                    function_name,
                )
            ):
                failures.append(
                    "Required registration function missing: "
                    f"{function_name}"
                )

        if len(REGISTERED_JOB_TYPES) != 6:
            failures.append(
                "Registration module does not define "
                "exactly six integrity job types."
            )

        if len(
            set(REGISTERED_JOB_TYPES)
        ) != 6:
            failures.append(
                "Website Article Integrity job types "
                "are not unique."
            )

        if (
            "udare_reconstruction"
            not in SUPPORTED_JOB_TYPES
        ):
            failures.append(
                "Existing UDARE static registration "
                "was not preserved."
            )

        if len(SUPPORTED_JOB_TYPES) < 33:
            failures.append(
                "Existing static supported-job-type "
                "collection was reduced."
            )

        if not PERSISTENT_REGISTRY_PATH.is_file():
            failures.append(
                "Persistent runtime registration "
                "registry does not exist."
            )

        registration_module.clear_runtime_registration_memory()

        reload_result = (
            registration_module
            .load_persisted_runtime_registrations(
                force=True
            )
        )

        registrations = {
            record.get("job_type"): record
            for record in (
                registration_module
                .list_runtime_registrations()
            )
        }

        for definition in (
            REGISTRATION_DEFINITIONS
        ):
            job_type = definition[
                "job_type"
            ]

            registration = registrations.get(
                job_type
            )

            if not isinstance(
                registration,
                dict,
            ):
                failures.append(
                    "Persistent registration missing: "
                    f"{job_type}"
                )
                continue

            if (
                registration.get("pipeline")
                != PIPELINE
            ):
                failures.append(
                    f"Incorrect pipeline registration: "
                    f"{job_type}"
                )

            if (
                registration.get("stage")
                != definition["stage"]
            ):
                failures.append(
                    f"Incorrect stage registration: "
                    f"{job_type}"
                )

            if (
                registration.get("persistent")
                is not True
            ):
                failures.append(
                    f"Registration is not persistent: "
                    f"{job_type}"
                )

            if (
                set(
                    registration.get(
                        "required_payload_fields",
                        [],
                    )
                )
                != set(
                    definition[
                        "required_payload_fields"
                    ]
                )
            ):
                failures.append(
                    "Required payload contract differs: "
                    f"{job_type}"
                )

            if (
                registration.get(
                    "predecessor_stages"
                )
                != list(
                    definition[
                        "predecessor_stages"
                    ]
                )
            ):
                failures.append(
                    "Predecessor stage mapping differs: "
                    f"{job_type}"
                )

            if (
                registration.get(
                    "successor_stages"
                )
                != list(
                    definition[
                        "successor_stages"
                    ]
                )
            ):
                failures.append(
                    "Successor stage mapping differs: "
                    f"{job_type}"
                )

        if (
            reload_result.get(
                "registration_count",
                0,
            )
            < 6
        ):
            failures.append(
                "Persistent registry reload did not "
                "load all integrity handlers."
            )

        for definition in (
            REGISTRATION_DEFINITIONS
        ):
            job_type = definition[
                "job_type"
            ]

            job = create_universal_knowledge_job(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                job_type=job_type,
                payload=contract_payload(),
                user_id="system",
                product_id="linkcraftor",
                pipeline=PIPELINE,
                stage=definition["stage"],
                payload_ref=(
                    "website_article_integrity_"
                    "registration_verification"
                ),
                priority=1,
                enqueue=False,
            )

            job_id = str(
                job.get("job_id")
                or ""
            )

            job_ids.append(
                job_id
            )

            if (
                job.get("status")
                != "registered"
            ):
                failures.append(
                    f"Universal job creation failed: "
                    f"{job_type}"
                )

            execution = (
                execute_universal_knowledge_job_v1(
                    job
                )
            )

            if execution.get("ok") is not True:
                failures.append(
                    f"Universal worker dispatch failed: "
                    f"{job_type}"
                )
                continue

            if (
                execution.get(
                    "dispatch_mode"
                )
                != (
                    "universal_runtime_registration"
                )
            ):
                failures.append(
                    "Job did not use registry-driven "
                    f"dispatch: {job_type}"
                )

            result = execution.get(
                "result",
                {},
            )

            handler_result = (
                result.get(
                    "handler_result",
                    {},
                )
                if isinstance(result, dict)
                else {}
            )

            if (
                handler_result.get(
                    "registration_test_passed"
                )
                is not True
            ):
                failures.append(
                    "Registered handler contract test "
                    f"failed: {job_type}"
                )

            if (
                handler_result.get(
                    "business_logic_executed"
                )
                is not False
            ):
                failures.append(
                    "Registration verification executed "
                    f"business logic unexpectedly: {job_type}"
                )

        for definition in (
            REGISTRATION_DEFINITIONS
        ):
            job_type = definition[
                "job_type"
            ]

            handler = (
                HANDLER_BY_JOB_TYPE[
                    job_type
                ]
            )

            result = handler(
                job={
                    "workspace_id": (
                        PRODUCTION_WORKSPACE_ID
                    ),
                    "job_type": job_type,
                    "payload": (
                        preflight_payload()
                    ),
                }
            )

            if (
                result.get(
                    "preflight_status"
                )
                != "READY"
            ):
                failures.append(
                    "Production workspace preflight "
                    f"was not READY: {job_type}; "
                    f"missing={result.get('missing_inputs')}"
                )

            if (
                result.get(
                    "business_logic_executed"
                )
                is not False
            ):
                failures.append(
                    "Preflight executed business logic: "
                    f"{job_type}"
                )

    finally:
        clean_test_artifacts(
            job_ids
        )

    udare_fingerprint_after = (
        directory_fingerprint(
            production_udare_root
        )
    )

    integrity_fingerprint_after = (
        directory_fingerprint(
            production_integrity_root
        )
    )

    if (
        udare_fingerprint_before
        != udare_fingerprint_after
    ):
        failures.append(
            "Production UDARE Store changed during "
            "runtime registration verification."
        )

    if (
        integrity_fingerprint_before
        != integrity_fingerprint_after
    ):
        failures.append(
            "Production Website Article Integrity "
            "artifacts changed during registration verification."
        )

    registered_integrity_types = sorted(
        job_type
        for job_type in registrations
        if job_type in REGISTERED_JOB_TYPES
    )

    report = {
        "schema_version": (
            "website_article_integrity_"
            "runtime_registration_verification_v1"
        ),
        "verification_status": (
            "PASS"
            if not failures
            else "FAIL"
        ),
        "pipeline": PIPELINE,
        "required_registration_count": 6,
        "registered_integrity_count": len(
            registered_integrity_types
        ),
        "registered_integrity_job_types": (
            registered_integrity_types
        ),
        "persistent_registry_reload": (
            reload_result
        ),
        "universal_job_creation_verified": (
            not any(
                "job creation"
                in failure.lower()
                for failure in failures
            )
        ),
        "universal_worker_dispatch_verified": (
            not any(
                "dispatch"
                in failure.lower()
                for failure in failures
            )
        ),
        "production_preflight_verified": (
            not any(
                "preflight"
                in failure.lower()
                for failure in failures
            )
        ),
        "production_udare_unchanged": (
            udare_fingerprint_before
            == udare_fingerprint_after
        ),
        "production_integrity_artifacts_unchanged": (
            integrity_fingerprint_before
            == integrity_fingerprint_after
        ),
        "automatic_udare_trigger_registered": False,
        "automatic_udare_trigger_note": (
            "Automatic creation of the first integrity "
            "job after UDARE completion is not part "
            "of this registration step."
        ),
        "failures": failures,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        f"Registered integrity handlers:    "
        f"{len(registered_integrity_types)}"
    )

    for job_type in (
        registered_integrity_types
    ):
        print(
            f"  - {job_type}"
        )

    print()
    print(
        "Persistent registry reload:       "
        f"{'PASS' if reload_result.get('registration_count', 0) >= 6 else 'FAIL'}"
    )
    print(
        "Universal job creation:           "
        f"{'PASS' if report['universal_job_creation_verified'] else 'FAIL'}"
    )
    print(
        "Registry-driven worker dispatch:  "
        f"{'PASS' if report['universal_worker_dispatch_verified'] else 'FAIL'}"
    )
    print(
        "Production preflight:             "
        f"{'PASS' if report['production_preflight_verified'] else 'FAIL'}"
    )
    print(
        "Production UDARE unchanged:       "
        f"{'PASS' if report['production_udare_unchanged'] else 'FAIL'}"
    )
    print(
        "Integrity artifacts unchanged:    "
        f"{'PASS' if report['production_integrity_artifacts_unchanged'] else 'FAIL'}"
    )
    print(
        "Automatic UDARE trigger:          "
        "NOT INCLUDED IN THIS STEP"
    )
    print()
    print(
        f"Verification report: {REPORT_PATH}"
    )
    print()

    if failures:
        print(
            "WEBSITE ARTICLE INTEGRITY "
            "RUNTIME REGISTRATION VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                f"  - {failure}"
            )

        print("=" * 86)
        return 1

    print(
        "WEBSITE ARTICLE INTEGRITY "
        "RUNTIME REGISTRATION VERIFICATION: PASS"
    )

    print(
        "All six Website Article Integrity handlers "
        "are persistently registered."
    )

    print(
        "The universal job creator accepts all six "
        "registered job types."
    )

    print(
        "The existing universal worker dispatches "
        "all six handlers through the runtime registry."
    )

    print(
        "No production article, metadata, quarantine, "
        "report or certification artifact was modified."
    )

    print(
        "The automatic trigger after UDARE completion "
        "remains a separate pending step."
    )

    print("=" * 86)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
