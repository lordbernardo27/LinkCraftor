from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    ALLOWED_CRAWLER_SESSION_TRANSITIONS,
    CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION,
    CrawlSessionStatus,
    cancel_crawler_session,
    complete_crawler_session,
    create_crawler_session_request,
    crawler_session_store_path,
    explain_crawler_session_coordinator_v1,
    fail_crawler_session,
    generate_crawler_session_id,
    get_crawler_session_status,
    pause_crawler_session,
    request_stop_crawler_session,
    resume_crawler_session,
    start_crawler_session,
)

ROOT = PROJECT_ROOT

COORDINATOR_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "session_coordinator.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

TEST_WORKSPACE_ID = "ws_crawler_session_coordinator_test"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


results: list[dict[str, object]] = []


def record(
    name: str,
    passed: bool,
    detail: str = "",
) -> None:
    results.append(
        {
            "check": name,
            "passed": passed,
            "detail": detail,
        }
    )

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")


print("")
print("============================================================")
print(" PHASE 1.4.3 - CRAWLER SESSION COORDINATOR VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE AND COMPILATION
# ------------------------------------------------------------

coordinator_exists = COORDINATOR_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "session_coordinator.py exists",
    coordinator_exists,
    str(COORDINATOR_PATH),
)

record(
    "__init__.py exists",
    init_exists,
    str(INIT_PATH),
)

check(
    coordinator_exists,
    "session_coordinator.py is missing.",
)

check(
    init_exists,
    "__init__.py is missing.",
)

py_compile.compile(
    str(COORDINATOR_PATH),
    doraise=True,
)

record(
    "session_coordinator.py compiles",
    True,
)

py_compile.compile(
    str(INIT_PATH),
    doraise=True,
)

record(
    "__init__.py compiles",
    True,
)


# ------------------------------------------------------------
# 2. CLEAN TEST STATE
# ------------------------------------------------------------

store_path = crawler_session_store_path(
    TEST_WORKSPACE_ID
)

if store_path.exists():
    store_path.unlink()

record(
    "previous coordinator test store removed",
    not store_path.exists(),
    str(store_path),
)


# ------------------------------------------------------------
# 3. SCHEMA AND TRANSITION TABLE
# ------------------------------------------------------------

check(
    CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION
    == "crawler_session_coordinator.v1",
    "Unexpected coordinator schema version.",
)

record(
    "coordinator schema version is correct",
    True,
)

expected_transition_sources = {
    CrawlSessionStatus.CREATED,
    CrawlSessionStatus.RUNNING,
    CrawlSessionStatus.PAUSED,
    CrawlSessionStatus.STOPPING,
    CrawlSessionStatus.COMPLETED,
    CrawlSessionStatus.FAILED,
    CrawlSessionStatus.CANCELLED,
}

check(
    set(ALLOWED_CRAWLER_SESSION_TRANSITIONS.keys())
    == expected_transition_sources,
    "Coordinator transition table is incomplete.",
)

record(
    "transition table covers all lifecycle states",
    True,
)

check(
    CrawlSessionStatus.RUNNING
    in ALLOWED_CRAWLER_SESSION_TRANSITIONS[
        CrawlSessionStatus.CREATED
    ],
    "CREATED -> RUNNING transition is missing.",
)

check(
    CrawlSessionStatus.PAUSED
    in ALLOWED_CRAWLER_SESSION_TRANSITIONS[
        CrawlSessionStatus.RUNNING
    ],
    "RUNNING -> PAUSED transition is missing.",
)

check(
    CrawlSessionStatus.RUNNING
    in ALLOWED_CRAWLER_SESSION_TRANSITIONS[
        CrawlSessionStatus.PAUSED
    ],
    "PAUSED -> RUNNING transition is missing.",
)

check(
    CrawlSessionStatus.STOPPING
    in ALLOWED_CRAWLER_SESSION_TRANSITIONS[
        CrawlSessionStatus.RUNNING
    ],
    "RUNNING -> STOPPING transition is missing.",
)

check(
    CrawlSessionStatus.COMPLETED
    in ALLOWED_CRAWLER_SESSION_TRANSITIONS[
        CrawlSessionStatus.STOPPING
    ],
    "STOPPING -> COMPLETED transition is missing.",
)

record(
    "canonical lifecycle transitions are present",
    True,
)


# ------------------------------------------------------------
# 4. IDENTITY GENERATION
# ------------------------------------------------------------

generated_id_1 = generate_crawler_session_id()
generated_id_2 = generate_crawler_session_id()

check(
    generated_id_1.startswith("crawl_session_"),
    "Generated crawler session ID has the wrong prefix.",
)

check(
    generated_id_1 != generated_id_2,
    "Generated crawler session IDs are not unique.",
)

record(
    "crawler session identity generation is valid",
    True,
)


# ------------------------------------------------------------
# 5. CREATE SESSION
# ------------------------------------------------------------

session = create_crawler_session_request(
    workspace_id=TEST_WORKSPACE_ID,
    session_name="Coordinator Verification Session",
    limits={
        "maximum_urls": 500,
        "maximum_domains": 25,
        "maximum_depth": 4,
        "maximum_runtime_seconds": 1800,
    },
    metadata={
        "test_mode": True,
    },
)

session_id = session.crawl_session_id

check(
    session.status == CrawlSessionStatus.CREATED,
    "New crawler session must be CREATED.",
)

check(
    session.current_phase == "session_created",
    "New crawler session phase is incorrect.",
)

check(
    session.workspace_id == TEST_WORKSPACE_ID,
    "New crawler session workspace is incorrect.",
)

check(
    session.metadata["created_by"]
    == "crawler_session_coordinator",
    "Coordinator creation metadata is missing.",
)

check(
    session.metadata["execution_initialized"] is False,
    "Execution initialization flag must begin as False.",
)

record(
    "crawler session request creates correctly",
    True,
    session_id,
)


# ------------------------------------------------------------
# 6. STATUS RESPONSE
# ------------------------------------------------------------

status_created = get_crawler_session_status(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    status_created["ok"] is True,
    "Coordinator status response did not return ok=True.",
)

check(
    status_created["status"] == "created",
    "Created session status response is incorrect.",
)

check(
    status_created["is_terminal"] is False,
    "Created session must not be terminal.",
)

record(
    "created session status response is correct",
    True,
)


# ------------------------------------------------------------
# 7. START SESSION
# ------------------------------------------------------------

started = start_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    started.status == CrawlSessionStatus.RUNNING,
    "Crawler session did not enter RUNNING state.",
)

check(
    started.started_at is not None,
    "Started crawler session has no started_at timestamp.",
)

check(
    started.metadata["execution_authorized"] is True,
    "Started session must authorize execution.",
)

record(
    "crawler session starts correctly",
    True,
)


# ------------------------------------------------------------
# 8. INVALID START TRANSITION
# ------------------------------------------------------------

try:
    start_crawler_session(
        workspace_id=TEST_WORKSPACE_ID,
        crawl_session_id=session_id,
    )
except ValueError:
    record(
        "duplicate start transition is rejected",
        True,
    )
else:
    raise AssertionError(
        "RUNNING -> RUNNING transition was accepted."
    )


# ------------------------------------------------------------
# 9. PAUSE SESSION
# ------------------------------------------------------------

paused = pause_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    paused.status == CrawlSessionStatus.PAUSED,
    "Crawler session did not enter PAUSED state.",
)

check(
    paused.paused_at is not None,
    "Paused crawler session has no paused_at timestamp.",
)

check(
    paused.metadata["execution_authorized"] is False,
    "Paused session must block execution.",
)

record(
    "crawler session pauses correctly",
    True,
)


# ------------------------------------------------------------
# 10. RESUME SESSION
# ------------------------------------------------------------

resumed = resume_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    resumed.status == CrawlSessionStatus.RUNNING,
    "Crawler session did not return to RUNNING state.",
)

check(
    resumed.resumed_at is not None,
    "Resumed crawler session has no resumed_at timestamp.",
)

check(
    resumed.paused_at is None,
    "Resumed crawler session should clear paused_at.",
)

check(
    resumed.metadata["execution_authorized"] is True,
    "Resumed session must authorize execution.",
)

record(
    "crawler session resumes correctly",
    True,
)


# ------------------------------------------------------------
# 11. CONTROLLED STOP AND COMPLETION
# ------------------------------------------------------------

stopping = request_stop_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    stopping.status == CrawlSessionStatus.STOPPING,
    "Crawler session did not enter STOPPING state.",
)

check(
    stopping.stop_requested_at is not None,
    "Stopping session has no stop_requested_at timestamp.",
)

check(
    stopping.metadata["controlled_stop_requested"] is True,
    "Controlled stop metadata is missing.",
)

record(
    "controlled stop request works correctly",
    True,
)

completed = complete_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    completed.status == CrawlSessionStatus.COMPLETED,
    "Crawler session did not enter COMPLETED state.",
)

check(
    completed.completed_at is not None,
    "Completed crawler session has no completed_at timestamp.",
)

check(
    completed.is_terminal is True,
    "Completed crawler session must be terminal.",
)

check(
    completed.metadata["execution_completed"] is True,
    "Completion metadata is missing.",
)

record(
    "crawler session completes correctly",
    True,
)


# ------------------------------------------------------------
# 12. TERMINAL STATE PROTECTION
# ------------------------------------------------------------

terminal_operations = [
    (
        "pause completed session",
        lambda: pause_crawler_session(
            workspace_id=TEST_WORKSPACE_ID,
            crawl_session_id=session_id,
        ),
    ),
    (
        "resume completed session",
        lambda: resume_crawler_session(
            workspace_id=TEST_WORKSPACE_ID,
            crawl_session_id=session_id,
        ),
    ),
    (
        "cancel completed session",
        lambda: cancel_crawler_session(
            workspace_id=TEST_WORKSPACE_ID,
            crawl_session_id=session_id,
        ),
    ),
]

for name, operation in terminal_operations:
    try:
        operation()
    except ValueError:
        record(
            f"{name} is rejected",
            True,
        )
    else:
        raise AssertionError(
            f"{name} was accepted."
        )


# ------------------------------------------------------------
# 13. FAILED SESSION PATH
# ------------------------------------------------------------

failure_session = create_crawler_session_request(
    workspace_id=TEST_WORKSPACE_ID,
    session_name="Coordinator Failure Test",
)

failure_session = start_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=failure_session.crawl_session_id,
)

try:
    fail_crawler_session(
        workspace_id=TEST_WORKSPACE_ID,
        crawl_session_id=failure_session.crawl_session_id,
        failure_reason="",
    )
except ValueError:
    record(
        "empty failure reason is rejected",
        True,
    )
else:
    raise AssertionError(
        "Empty failure reason was accepted."
    )

failed = fail_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=failure_session.crawl_session_id,
    failure_reason="Verification failure test",
)

check(
    failed.status == CrawlSessionStatus.FAILED,
    "Crawler session did not enter FAILED state.",
)

check(
    failed.failed_at is not None,
    "Failed crawler session has no failed_at timestamp.",
)

check(
    failed.failure_reason
    == "Verification failure test",
    "Crawler session failure reason is incorrect.",
)

check(
    failed.is_terminal is True,
    "Failed crawler session must be terminal.",
)

record(
    "crawler session failure path works correctly",
    True,
)


# ------------------------------------------------------------
# 14. CANCELLED SESSION PATH
# ------------------------------------------------------------

cancel_session = create_crawler_session_request(
    workspace_id=TEST_WORKSPACE_ID,
    session_name="Coordinator Cancellation Test",
)

cancelled = cancel_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=cancel_session.crawl_session_id,
    cancellation_reason="Verification cancellation test",
)

check(
    cancelled.status == CrawlSessionStatus.CANCELLED,
    "Crawler session did not enter CANCELLED state.",
)

check(
    cancelled.cancelled_at is not None,
    "Cancelled crawler session has no cancelled_at timestamp.",
)

check(
    cancelled.failure_reason
    == "Verification cancellation test",
    "Cancellation reason was not preserved.",
)

check(
    cancelled.is_terminal is True,
    "Cancelled crawler session must be terminal.",
)

record(
    "crawler session cancellation path works correctly",
    True,
)


# ------------------------------------------------------------
# 15. INVALID INPUTS
# ------------------------------------------------------------

invalid_create_cases = [
    {
        "name": "empty workspace rejected",
        "kwargs": {
            "workspace_id": "",
            "session_name": "Test Session",
        },
    },
    {
        "name": "empty session name rejected",
        "kwargs": {
            "workspace_id": TEST_WORKSPACE_ID,
            "session_name": "",
        },
    },
    {
        "name": "invalid metadata rejected",
        "kwargs": {
            "workspace_id": TEST_WORKSPACE_ID,
            "session_name": "Test Session",
            "metadata": "invalid",
        },
    },
    {
        "name": "invalid limits rejected",
        "kwargs": {
            "workspace_id": TEST_WORKSPACE_ID,
            "session_name": "Test Session",
            "limits": "invalid",
        },
    },
]

for invalid_case in invalid_create_cases:
    try:
        create_crawler_session_request(
            **invalid_case["kwargs"]
        )
    except ValueError:
        record(
            invalid_case["name"],
            True,
        )
    else:
        raise AssertionError(
            invalid_case["name"]
        )


# ------------------------------------------------------------
# 16. EXPLANATION CONTRACT
# ------------------------------------------------------------

explanation = (
    explain_crawler_session_coordinator_v1()
)

check(
    explanation.get("ok") is True,
    "Coordinator explanation did not return ok=True.",
)

check(
    explanation.get("component")
    == "crawler_session_coordinator",
    "Coordinator explanation component is incorrect.",
)

check(
    explanation.get("schema_version")
    == CRAWLER_SESSION_COORDINATOR_SCHEMA_VERSION,
    "Coordinator explanation schema is incorrect.",
)

check(
    "validate crawler session lifecycle transitions"
    in explanation.get(
        "responsibilities",
        [],
    ),
    "Coordinator lifecycle responsibility is missing.",
)

check(
    "web page fetching"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Coordinator fetching boundary is missing.",
)

check(
    explanation.get("allowed_transitions", {}).get(
        "created"
    )
    == [
        "cancelled",
        "failed",
        "running",
    ],
    "Coordinator explanation transition map is incorrect.",
)

record(
    "coordinator explanation contract is correct",
    True,
)


# ------------------------------------------------------------
# 17. FINAL STATUS CHECK
# ------------------------------------------------------------

final_status = get_crawler_session_status(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=session_id,
)

check(
    final_status["status"] == "completed",
    "Final coordinator status is incorrect.",
)

check(
    final_status["is_terminal"] is True,
    "Final coordinator status must be terminal.",
)

record(
    "final coordinator status response is correct",
    True,
)


# ------------------------------------------------------------
# 18. CLEANUP
# ------------------------------------------------------------

if store_path.exists():
    store_path.unlink()

check(
    not store_path.exists(),
    "Coordinator verification artifact cleanup failed.",
)

record(
    "coordinator test repository artifact removed",
    True,
)


# ------------------------------------------------------------
# 19. FINAL RESULT
# ------------------------------------------------------------

failed_checks = [
    result
    for result in results
    if result["passed"] is not True
]

print("")
print("============================================================")
print(" VERIFICATION SUMMARY")
print("============================================================")
print(f"Checks executed: {len(results)}")
print(f"Checks passed:   {len(results) - len(failed_checks)}")
print(f"Checks failed:   {len(failed_checks)}")

if failed_checks:
    print("")
    print("CRAWLER SESSION COORDINATOR VERIFICATION: FAIL")
    raise SystemExit(1)

print("")
print("CRAWLER SESSION COORDINATOR VERIFICATION: PASS")
print("")
print(json.dumps(explanation, indent=2))
