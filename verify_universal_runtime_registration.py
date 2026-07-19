"""Verification for Universal Runtime Registration."""

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

from backend.server.jobs.universal_knowledge_orchestrator import (
    SUPPORTED_JOB_TYPES,
    create_universal_knowledge_job,
    explain_universal_runtime_registration_v1,
    failure_path,
    job_ledger_path,
    job_status_path,
    list_universal_runtime_registrations,
    progress_path,
    queue_path,
    read_universal_runtime_registration,
    register_universal_runtime_handler,
    unregister_universal_runtime_handler,
)

from backend.server.runtime import (
    universal_runtime_registration as registration_module,
)

from backend.server.workers.universal_knowledge_worker import (
    execute_universal_knowledge_job_v1,
)


TEST_JOB_TYPE = (
    "universal_runtime_registration_contract_test"
)

TEST_WORKSPACE_ID = (
    "ws_universal_runtime_registration_test"
)

REPORT_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "universal_runtime_registration"
    / "verification"
)

REPORT_PATH = (
    REPORT_ROOT
    / "universal_runtime_registration_verification.json"
)


def verification_handler(
    *,
    job: dict[str, Any],
) -> dict[str, Any]:
    payload = job.get(
        "payload",
        {},
    )

    return {
        "verification_handler_executed": True,
        "workspace_id": job.get(
            "workspace_id"
        ),
        "payload_token": payload.get(
            "verification_token"
        ),
    }


def sha256_file(path: Path) -> str:
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


def source_has_function(
    path: Path,
    name: str,
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
        and node.name == name
        for node in tree.body
    )


def clean_test_runtime_artifacts(
    *,
    workspace_id: str,
    job_id: str,
) -> None:
    paths = (
        queue_path(
            workspace_id
        ),
        job_status_path(
            workspace_id,
            job_id,
        ),
        progress_path(
            workspace_id,
            job_id,
        ),
        job_ledger_path(
            workspace_id
        ),
        failure_path(
            workspace_id
        ),
    )

    parent_paths: set[Path] = set()

    for path in paths:
        parent_paths.add(
            path.parent
        )

        path.unlink(
            missing_ok=True
        )

    for parent in sorted(
        parent_paths,
        key=lambda item: len(
            item.parts
        ),
        reverse=True,
    ):
        if (
            parent.name
            == workspace_id
            and parent.is_dir()
        ):
            shutil.rmtree(
                parent,
                ignore_errors=True,
            )


def restore_registry_file(
    *,
    original_exists: bool,
    original_bytes: bytes | None,
) -> None:
    registry_path = (
        registration_module.REGISTRY_PATH
    )

    if original_exists:
        registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        registry_path.write_bytes(
            original_bytes or b""
        )
    else:
        registry_path.unlink(
            missing_ok=True
        )


def main() -> int:
    print()
    print("=" * 84)
    print(
        "UNIVERSAL RUNTIME REGISTRATION — VERIFICATION"
    )
    print("=" * 84)

    source_paths = {
        "registry": (
            PROJECT_ROOT
            / "backend"
            / "server"
            / "runtime"
            / "universal_runtime_registration.py"
        ),
        "orchestrator": (
            PROJECT_ROOT
            / "backend"
            / "server"
            / "jobs"
            / "universal_knowledge_orchestrator.py"
        ),
        "worker": (
            PROJECT_ROOT
            / "backend"
            / "server"
            / "workers"
            / "universal_knowledge_worker.py"
        ),
    }

    failures: list[str] = []

    for name, path in source_paths.items():
        if not path.is_file():
            failures.append(
                f"Required source file missing: {path}"
            )
            continue

        try:
            ast.parse(
                path.read_text(
                    encoding="utf-8-sig",
                ),
                filename=str(path),
            )
        except SyntaxError as exc:
            failures.append(
                f"{name} syntax error: {exc}"
            )

    required_registry_functions = (
        "register_runtime_handler",
        "unregister_runtime_handler",
        "load_persisted_runtime_registrations",
        "has_runtime_handler",
        "get_runtime_registration",
        "list_runtime_registrations",
        "dispatch_registered_runtime_handler",
        "execute_registered_runtime_job_v1",
        "runtime_registration_snapshot",
    )

    for function_name in (
        required_registry_functions
    ):
        if not source_has_function(
            source_paths["registry"],
            function_name,
        ):
            failures.append(
                "Registry function missing: "
                f"{function_name}"
            )

    required_orchestrator_functions = (
        "register_universal_runtime_handler",
        "unregister_universal_runtime_handler",
        "read_universal_runtime_registration",
        "list_universal_runtime_registrations",
        "explain_universal_runtime_registration_v1",
    )

    for function_name in (
        required_orchestrator_functions
    ):
        if not source_has_function(
            source_paths["orchestrator"],
            function_name,
        ):
            failures.append(
                "Orchestrator registration API missing: "
                f"{function_name}"
            )

    if (
        "udare_reconstruction"
        not in SUPPORTED_JOB_TYPES
    ):
        failures.append(
            "Existing UDARE static registration was lost."
        )

    static_supported_count = len(
        SUPPORTED_JOB_TYPES
    )

    if static_supported_count < 33:
        failures.append(
            "The existing static supported-job-type "
            "collection was unexpectedly reduced."
        )

    original_registry_path = (
        registration_module.REGISTRY_PATH
    )

    original_registry_exists = (
        original_registry_path.is_file()
    )

    original_registry_bytes = (
        original_registry_path.read_bytes()
        if original_registry_exists
        else None
    )

    job_id = ""

    try:
        unregister_universal_runtime_handler(
            TEST_JOB_TYPE,
            persist=False,
        )

        registration = (
            register_universal_runtime_handler(
                job_type=TEST_JOB_TYPE,
                handler=verification_handler,
                pipeline=(
                    "universal_runtime_registration"
                ),
                stage=(
                    "registration_contract_test"
                ),
                description=(
                    "Universal Runtime Registration "
                    "verification handler."
                ),
                required_payload_fields=(
                    "verification_token",
                ),
                predecessor_stages=(
                    "registration_created",
                ),
                successor_stages=(
                    "registration_verified",
                ),
                idempotency_fields=(
                    "workspace_id",
                    "verification_token",
                ),
                retry_policy={
                    "max_attempts": 3,
                },
                concurrency_policy={
                    "scope": "workspace",
                    "max_concurrent": 1,
                },
                metadata={
                    "verification_only": True,
                },
                persist=True,
            )
        )

        if (
            registration.get("job_type")
            != TEST_JOB_TYPE
        ):
            failures.append(
                "Registration returned the wrong job type."
            )

        if (
            registration.get("pipeline")
            != "universal_runtime_registration"
        ):
            failures.append(
                "Registration pipeline was not preserved."
            )

        if (
            registration.get("stage")
            != "registration_contract_test"
        ):
            failures.append(
                "Registration stage was not preserved."
            )

        if not original_registry_path.is_file():
            failures.append(
                "Persistent registration registry was not created."
            )

        duplicate_rejected = False

        try:
            register_universal_runtime_handler(
                job_type=TEST_JOB_TYPE,
                handler=verification_handler,
            )
        except ValueError:
            duplicate_rejected = True

        if not duplicate_rejected:
            failures.append(
                "Duplicate registration was not rejected."
            )

        read_back = (
            read_universal_runtime_registration(
                TEST_JOB_TYPE
            )
        )

        if not isinstance(
            read_back,
            dict,
        ):
            failures.append(
                "Registered handler could not be read back."
            )

        dynamic_job_types = {
            record.get("job_type")
            for record
            in list_universal_runtime_registrations()
        }

        if TEST_JOB_TYPE not in dynamic_job_types:
            failures.append(
                "Registration was not listed in the registry."
            )

        registration_module.clear_runtime_registration_memory()

        load_result = (
            registration_module
            .load_persisted_runtime_registrations(
                force=True
            )
        )

        if (
            load_result.get(
                "registration_count"
            )
            < 1
        ):
            failures.append(
                "Persistent registration did not reload."
            )

        if not registration_module.has_runtime_handler(
            TEST_JOB_TYPE
        ):
            failures.append(
                "Reloaded persistent handler is unavailable."
            )

        job = create_universal_knowledge_job(
            workspace_id=TEST_WORKSPACE_ID,
            job_type=TEST_JOB_TYPE,
            payload={
                "verification_token": (
                    "runtime_registration_pass"
                ),
                "max_attempts": 3,
            },
            user_id="system",
            product_id="linkcraftor",
            pipeline=(
                "universal_runtime_registration"
            ),
            stage=(
                "registration_contract_test"
            ),
            payload_ref=(
                "runtime_registration_verification"
            ),
            priority=1,
            enqueue=False,
        )

        job_id = str(
            job.get("job_id")
            or ""
        )

        if (
            job.get("status")
            != "registered"
        ):
            failures.append(
                "Dynamic job was not created with "
                "registered status."
            )

        execution = (
            execute_universal_knowledge_job_v1(
                job
            )
        )

        if execution.get("ok") is not True:
            failures.append(
                "Registered handler execution failed."
            )

        if (
            execution.get("dispatch_mode")
            != "universal_runtime_registration"
        ):
            failures.append(
                "Universal worker did not use registry-driven "
                "dispatch."
            )

        result = execution.get(
            "result",
            {},
        )

        handler_result = (
            result.get(
                "handler_result",
                {}
            )
            if isinstance(result, dict)
            else {}
        )

        if (
            handler_result.get(
                "verification_handler_executed"
            )
            is not True
        ):
            failures.append(
                "Registered business handler did not execute."
            )

        if (
            handler_result.get(
                "payload_token"
            )
            != "runtime_registration_pass"
        ):
            failures.append(
                "Registered handler did not receive the "
                "job payload."
            )

        missing_payload_job = dict(
            job
        )

        missing_payload_job["job_id"] = (
            job_id
            + "_missing_payload"
        )

        missing_payload_job["payload"] = {}

        missing_payload_execution = (
            execute_universal_knowledge_job_v1(
                missing_payload_job
            )
        )

        if (
            missing_payload_execution.get("ok")
            is not False
        ):
            failures.append(
                "Required payload-field enforcement failed."
            )

        explanation = (
            explain_universal_runtime_registration_v1()
        )

        if (
            explanation.get(
                "dynamic_registration_count",
                0,
            )
            < 1
        ):
            failures.append(
                "Runtime registration explanation did not "
                "include the dynamic handler."
            )

    finally:
        unregister_universal_runtime_handler(
            TEST_JOB_TYPE,
            persist=True,
        )

        restore_registry_file(
            original_exists=(
                original_registry_exists
            ),
            original_bytes=(
                original_registry_bytes
            ),
        )

        registration_module.clear_runtime_registration_memory()

        registration_module.load_persisted_runtime_registrations(
            force=True
        )

        if job_id:
            clean_test_runtime_artifacts(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                job_id=job_id,
            )

            clean_test_runtime_artifacts(
                workspace_id=(
                    TEST_WORKSPACE_ID
                ),
                job_id=(
                    job_id
                    + "_missing_payload"
                ),
            )

    remaining_dynamic_job_types = {
        record.get("job_type")
        for record in (
            list_universal_runtime_registrations()
        )
    }

    if TEST_JOB_TYPE in remaining_dynamic_job_types:
        failures.append(
            "Verification registration was not cleaned up."
        )

    unsupported_rejected = False

    try:
        create_universal_knowledge_job(
            workspace_id=(
                TEST_WORKSPACE_ID
            ),
            job_type=TEST_JOB_TYPE,
            payload={},
            enqueue=False,
        )
    except ValueError:
        unsupported_rejected = True

    if not unsupported_rejected:
        failures.append(
            "Unregistered dynamic job type remained accepted."
        )

    worker_source = source_paths[
        "worker"
    ].read_text(
        encoding="utf-8-sig",
    )

    if (
        "has_runtime_handler"
        not in worker_source
        or "execute_registered_runtime_job_v1"
        not in worker_source
    ):
        failures.append(
            "Universal worker is not connected to the "
            "runtime registry."
        )

    if (
        "udare_reconstruction"
        not in worker_source
    ):
        failures.append(
            "Existing UDARE worker fallback was removed."
        )

    orchestrator_source = source_paths[
        "orchestrator"
    ].read_text(
        encoding="utf-8-sig",
    )

    if (
        "is_runtime_job_type_registered"
        not in orchestrator_source
    ):
        failures.append(
            "Universal job creator is not connected to "
            "dynamic registration."
        )

    report = {
        "schema_version": (
            "universal_runtime_registration_verification_v1"
        ),
        "verification_status": (
            "PASS"
            if not failures
            else "FAIL"
        ),
        "static_supported_job_type_count": (
            static_supported_count
        ),
        "udare_static_registration_preserved": (
            "udare_reconstruction"
            in SUPPORTED_JOB_TYPES
        ),
        "generic_registration_api_present": (
            all(
                source_has_function(
                    source_paths["registry"],
                    function_name,
                )
                for function_name
                in required_registry_functions
            )
        ),
        "persistent_registration_round_trip": (
            not any(
                "Persistent registration"
                in failure
                for failure in failures
            )
        ),
        "registry_driven_worker_dispatch": (
            not any(
                "registry-driven dispatch"
                in failure
                or "Universal worker"
                in failure
                for failure in failures
            )
        ),
        "required_payload_validation": (
            not any(
                "payload-field"
                in failure
                for failure in failures
            )
        ),
        "verification_registration_cleaned": (
            TEST_JOB_TYPE
            not in remaining_dynamic_job_types
        ),
        "website_article_integrity_registered": False,
        "website_article_integrity_registration_note": (
            "The core Universal Runtime Registration mechanism "
            "is verified. Website Article Integrity handlers are "
            "not registered in this step."
        ),
        "source_files": {
            name: {
                "path": str(path),
                "sha256": (
                    sha256_file(path)
                    if path.is_file()
                    else None
                ),
            }
            for name, path
            in source_paths.items()
        },
        "failures": failures,
    }

    REPORT_ROOT.mkdir(
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
        f"Static supported job types:       "
        f"{static_supported_count}"
    )
    print(
        "UDARE static registration:       "
        f"{'PASS' if 'udare_reconstruction' in SUPPORTED_JOB_TYPES else 'FAIL'}"
    )
    print(
        "Generic registration API:        "
        f"{'PASS' if report['generic_registration_api_present'] else 'FAIL'}"
    )
    print(
        "Persistent registry round trip:  "
        f"{'PASS' if report['persistent_registration_round_trip'] else 'FAIL'}"
    )
    print(
        "Dynamic job creation:             "
        f"{'PASS' if unsupported_rejected else 'FAIL'}"
    )
    print(
        "Registry-driven worker dispatch: "
        f"{'PASS' if report['registry_driven_worker_dispatch'] else 'FAIL'}"
    )
    print(
        "Required payload validation:      "
        f"{'PASS' if report['required_payload_validation'] else 'FAIL'}"
    )
    print(
        "Test registration cleanup:        "
        f"{'PASS' if report['verification_registration_cleaned'] else 'FAIL'}"
    )
    print(
        "Website Integrity registered:     NO — intentionally deferred"
    )
    print()
    print(f"Report: {REPORT_PATH}")
    print()

    if failures:
        print(
            "UNIVERSAL RUNTIME REGISTRATION "
            "VERIFICATION: FAIL"
        )

        for failure in failures:
            print(
                f"  - {failure}"
            )

        print("=" * 84)
        return 1

    print(
        "UNIVERSAL RUNTIME REGISTRATION "
        "VERIFICATION: PASS"
    )

    print(
        "The reusable Universal Runtime Registration "
        "mechanism is now built."
    )

    print(
        "Registered handlers can be accepted by the universal "
        "job creator and dispatched by the existing universal worker."
    )

    print(
        "Existing static job types and the UDARE execution path "
        "remain preserved."
    )

    print(
        "Website Article Integrity has not yet been registered."
    )

    print("=" * 84)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
