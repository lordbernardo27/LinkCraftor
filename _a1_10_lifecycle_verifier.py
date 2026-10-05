from __future__ import annotations

import ast
import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace
import warnings


warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

MAIN_PATH = (
    ROOT
    / "backend/server/main.py"
)

GATEWAY_PATH = (
    ROOT
    / "backend/server/runtime/"
    "runtime_application_lifecycle.py"
)


passed = 0


def check(
    label: str,
    condition: bool,
) -> None:
    global passed

    if not condition:
        print(f"{label}: FAIL")
        raise AssertionError(label)

    passed += 1
    print(f"{label}: PASS")


main_source = MAIN_PATH.read_text(
    encoding="utf-8-sig"
)

gateway_source = GATEWAY_PATH.read_text(
    encoding="utf-8-sig"
)

ast.parse(
    main_source,
    filename=str(MAIN_PATH),
)

ast.parse(
    gateway_source,
    filename=str(GATEWAY_PATH),
)

check("MAIN_SYNTAX", True)
check("LIFECYCLE_GATEWAY_SYNTAX", True)

import backend.server.runtime.runtime_application_lifecycle as lifecycle_gateway
import backend.server.main as main_module

check(
    "LIFECYCLE_GATEWAY_IMPORT",
    lifecycle_gateway is not None,
)

check(
    "MAIN_MODULE_IMPORT",
    main_module is not None,
)

check(
    "FASTAPI_APPLICATION_AVAILABLE",
    main_module.app is not None,
)

check(
    "ONE_LIFECYCLE_IMPORT",
    main_source.count(
        "linkcraftor_runtime_lifespan,"
    ) == 2,
)

check(
    "FASTAPI_LIFESPAN_BOUND",
    "lifespan=linkcraftor_runtime_lifespan"
    in main_source,
)

check(
    "CANONICAL_BOOT_BOUND",
    "await boot_runtime("
    in gateway_source,
)

check(
    "CANONICAL_SHUTDOWN_BOUND",
    "await shutdown_runtime("
    in gateway_source,
)

check(
    "DRAIN_BEFORE_STOP_ACTIVE",
    "drain_before_stop=True"
    in gateway_source,
)

check(
    "BOOT_EVIDENCE_PUBLISHED",
    "runtime_boot_evidence"
    in gateway_source,
)

check(
    "SHUTDOWN_EVIDENCE_PUBLISHED",
    "runtime_shutdown_evidence"
    in gateway_source,
)

check(
    "SHUTDOWN_SNAPSHOT_PUBLISHED",
    "runtime_shutdown_snapshot"
    in gateway_source,
)

check(
    "BOOT_FAILURE_FAILS_CLOSED",
    '"boot_failed"'
    in gateway_source,
)

check(
    "SHUTDOWN_FAILURE_FAILS_CLOSED",
    '"shutdown_failed"'
    in gateway_source,
)

check(
    "PROJECT_ROOT_CANONICAL",
    ".parents[3]"
    in gateway_source,
)

check(
    "RUNTIME_BOOT_PROCESS_RETAINED",
    (
        ROOT
        / "backend/server/runtime/"
        "runtime_boot_process.py"
    ).exists(),
)

check(
    "RUNTIME_SHUTDOWN_PROCESS_RETAINED",
    (
        ROOT
        / "backend/server/runtime/"
        "runtime_shutdown_process.py"
    ).exists(),
)


events = []

fake_boot_process = SimpleNamespace(
    name="fake_boot_process"
)

fake_boot_context = SimpleNamespace(
    boot_id="runtime_boot_test",
    attempt=1,
    project_root=ROOT,
    configuration=SimpleNamespace(),
    environment=SimpleNamespace(),
    kernel=SimpleNamespace(),
    service_registry=SimpleNamespace(),
    lifecycle_manager=SimpleNamespace(),
    service_keys=(),
    booted_at="2026-10-05T05:00:00Z",
)

fake_shutdown_process = SimpleNamespace(
    snapshot=lambda: SimpleNamespace(
        status="stopped",
        attempt=1,
        shutdown_id="runtime_shutdown_test",
        stage="shutdown",
        generation=1,
        event_count=1,
        events=(),
        boot_id="runtime_boot_test",
        boot_status="stopped",
        kernel_state="stopped",
        lifecycle_phase="stopped",
        failure_reason=None,
        completed_failures=(),
    )
)

fake_shutdown_context = SimpleNamespace(
    shutdown_id="runtime_shutdown_test",
    attempt=1,
    boot_id="runtime_boot_test",
    started_at="2026-10-05T05:01:00Z",
    completed_at="2026-10-05T05:02:00Z",
    drain_requested=True,
    drain_performed=True,
    service_count=0,
    failures=(),
    kernel_state="stopped",
    lifecycle_phase="stopped",
    boot_status="stopped",
)


def mapping(value):
    return dict(vars(value))


original_context_mapping = (
    lifecycle_gateway._context_mapping
)

original_boot_runtime = (
    lifecycle_gateway.boot_runtime
)

original_shutdown_runtime = (
    lifecycle_gateway.shutdown_runtime
)


async def fake_boot_runtime(**kwargs):
    events.append("boot")
    return (
        fake_boot_process,
        fake_boot_context,
    )


async def fake_shutdown_runtime(**kwargs):
    events.append("shutdown")

    check(
        "SHUTDOWN_RECEIVES_SAME_BOOT_PROCESS",
        kwargs.get("boot_process")
        is fake_boot_process,
    )

    check(
        "SHUTDOWN_REQUESTS_DRAIN",
        kwargs.get("drain_before_stop")
        is True,
    )

    return (
        fake_shutdown_process,
        fake_shutdown_context,
    )


async def exercise_lifecycle():
    application = SimpleNamespace(
        state=SimpleNamespace()
    )

    lifecycle_gateway.boot_runtime = (
        fake_boot_runtime
    )

    lifecycle_gateway.shutdown_runtime = (
        fake_shutdown_runtime
    )

    lifecycle_gateway._context_mapping = (
        mapping
    )

    try:
        async with (
            lifecycle_gateway
            .linkcraftor_runtime_lifespan(
                application
            )
        ):
            check(
                "STARTUP_STATUS_RUNNING",
                application.state
                .runtime_lifecycle_status
                == "running",
            )

            check(
                "BOOT_PROCESS_PUBLISHED",
                application.state
                .runtime_boot_process
                is fake_boot_process,
            )

            check(
                "BOOT_CONTEXT_PUBLISHED",
                application.state
                .runtime_boot_context
                is fake_boot_context,
            )

            check(
                "BOOT_RAN_BEFORE_APPLICATION",
                events == ["boot"],
            )

        check(
            "SHUTDOWN_STATUS_STOPPED",
            application.state
            .runtime_lifecycle_status
            == "stopped",
        )

        check(
            "SHUTDOWN_PROCESS_PUBLISHED",
            application.state
            .runtime_shutdown_process
            is fake_shutdown_process,
        )

        check(
            "SHUTDOWN_CONTEXT_PUBLISHED",
            application.state
            .runtime_shutdown_context
            is fake_shutdown_context,
        )

        check(
            "SHUTDOWN_RAN_AFTER_APPLICATION",
            events == [
                "boot",
                "shutdown",
            ],
        )

        check(
            "SHUTDOWN_EVIDENCE_AVAILABLE",
            application.state
            .runtime_shutdown_evidence[
                "shutdown_id"
            ]
            == "runtime_shutdown_test",
        )

    finally:
        lifecycle_gateway.boot_runtime = (
            original_boot_runtime
        )

        lifecycle_gateway.shutdown_runtime = (
            original_shutdown_runtime
        )

        lifecycle_gateway._context_mapping = (
            original_context_mapping
        )


asyncio.run(
    exercise_lifecycle()
)


failure_events = []


async def failing_boot_runtime(**kwargs):
    failure_events.append("boot_failed")
    raise RuntimeError(
        "certification boot failure"
    )


async def verify_boot_failure():
    application = SimpleNamespace(
        state=SimpleNamespace()
    )

    lifecycle_gateway.boot_runtime = (
        failing_boot_runtime
    )

    try:
        try:
            async with (
                lifecycle_gateway
                .linkcraftor_runtime_lifespan(
                    application
                )
            ):
                raise AssertionError(
                    "Application body must not run."
                )
        except RuntimeError as exc:
            check(
                "BOOT_FAILURE_PROPAGATED",
                str(exc)
                == "certification boot failure",
            )

        check(
            "BOOT_FAILURE_STATUS_PUBLISHED",
            application.state
            .runtime_lifecycle_status
            == "boot_failed",
        )

        check(
            "BOOT_FAILURE_PREVENTS_APPLICATION",
            failure_events
            == ["boot_failed"],
        )

    finally:
        lifecycle_gateway.boot_runtime = (
            original_boot_runtime
        )


asyncio.run(
    verify_boot_failure()
)


check(
    "MAIN_APP_USES_GATEWAY_FUNCTION",
    (
        main_module.app.router
        .lifespan_context
        is lifecycle_gateway
        .linkcraftor_runtime_lifespan
    ),
)

print(f"TESTS_PASSED={passed}")
print("TESTS_FAILED=0")
print("A1_10_FINAL_CERTIFICATION=PASS")