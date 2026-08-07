from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    CRAWLER_SESSION_SCHEMA_VERSION,
    CrawlSession,
    CrawlSessionLimits,
    CrawlSessionStatistics,
    CrawlSessionStatus,
    TERMINAL_CRAWL_SESSION_STATUSES,
    explain_crawler_session_models_v1,
)

ROOT = PROJECT_ROOT

MODELS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "session_models.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


print("")
print("============================================================")
print(" PHASE 1.2.4 - CRAWLER SESSION MODELS VERIFICATION")
print("============================================================")
print("")

results: list[dict[str, object]] = []


def record(name: str, passed: bool, detail: str = "") -> None:
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


# 1. FILE EXISTENCE

models_exists = MODELS_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "session_models.py exists",
    models_exists,
    str(MODELS_PATH),
)

record(
    "__init__.py exists",
    init_exists,
    str(INIT_PATH),
)

check(models_exists, "session_models.py is missing.")
check(init_exists, "__init__.py is missing.")


# 2. PYTHON COMPILATION

py_compile.compile(
    str(MODELS_PATH),
    doraise=True,
)
record(
    "session_models.py compiles",
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


# 3. PUBLIC API

check(
    CRAWLER_SESSION_SCHEMA_VERSION
    == "crawler_session.v1",
    "Unexpected crawler session schema version.",
)

record(
    "schema version is crawler_session.v1",
    True,
)

expected_statuses = {
    "created",
    "running",
    "paused",
    "stopping",
    "completed",
    "failed",
    "cancelled",
}

actual_statuses = {
    status.value
    for status in CrawlSessionStatus
}

check(
    actual_statuses == expected_statuses,
    "Crawler session statuses are incorrect.",
)

record(
    "canonical lifecycle statuses are complete",
    True,
    ", ".join(sorted(actual_statuses)),
)

expected_terminal_statuses = {
    "completed",
    "failed",
    "cancelled",
}

actual_terminal_statuses = {
    status.value
    for status in TERMINAL_CRAWL_SESSION_STATUSES
}

check(
    actual_terminal_statuses
    == expected_terminal_statuses,
    "Terminal crawler session statuses are incorrect.",
)

record(
    "terminal statuses are correct",
    True,
    ", ".join(sorted(actual_terminal_statuses)),
)


# 4. LIMIT MODEL

limits = CrawlSessionLimits(
    maximum_urls=1000,
    maximum_domains=50,
    maximum_depth=5,
    maximum_runtime_seconds=3600,
)

check(
    limits.to_dict()
    == {
        "maximum_urls": 1000,
        "maximum_domains": 50,
        "maximum_depth": 5,
        "maximum_runtime_seconds": 3600,
    },
    "CrawlSessionLimits serialization failed.",
)

record(
    "crawler session limits serialize correctly",
    True,
)

reconstructed_limits = (
    CrawlSessionLimits.from_mapping(
        limits.to_dict()
    )
)

check(
    reconstructed_limits.to_dict()
    == limits.to_dict(),
    "CrawlSessionLimits reconstruction failed.",
)

record(
    "crawler session limits reconstruct correctly",
    True,
)

try:
    CrawlSessionLimits(
        maximum_urls=-1,
    )
except ValueError:
    record(
        "negative session limit is rejected",
        True,
    )
else:
    raise AssertionError(
        "Negative crawler session limits were accepted."
    )


# 5. STATISTICS MODEL

statistics = CrawlSessionStatistics(
    seeds_registered=3,
    urls_discovered=25,
    urls_scheduled=20,
    fetches_attempted=10,
    fetches_succeeded=8,
    fetches_failed=2,
    pages_accepted=7,
    pages_rejected=1,
)

statistics_payload = statistics.to_dict()

check(
    statistics_payload["seeds_registered"] == 3,
    "Statistics seed count is incorrect.",
)

check(
    statistics_payload["fetches_succeeded"] == 8,
    "Statistics fetch success count is incorrect.",
)

record(
    "crawler session statistics serialize correctly",
    True,
)

reconstructed_statistics = (
    CrawlSessionStatistics.from_mapping(
        statistics_payload
    )
)

check(
    reconstructed_statistics.to_dict()
    == statistics_payload,
    "CrawlSessionStatistics reconstruction failed.",
)

record(
    "crawler session statistics reconstruct correctly",
    True,
)

try:
    CrawlSessionStatistics(
        urls_discovered=-1,
    )
except ValueError:
    record(
        "negative statistics value is rejected",
        True,
    )
else:
    raise AssertionError(
        "Negative crawler statistics were accepted."
    )


# 6. SESSION MODEL

session = CrawlSession(
    crawl_session_id="crawl_session_test_001",
    workspace_id="ws_crawler_test",
    session_name="Technology Crawl Test",
    status=CrawlSessionStatus.CREATED,
    limits=limits,
    statistics=statistics,
    metadata={
        "test_mode": True,
        "initiated_by": "phase_1_2_4_verification",
    },
)

check(
    session.is_terminal is False,
    "New crawler session must not be terminal.",
)

record(
    "new crawler session is non-terminal",
    True,
)

session_payload = session.to_dict()

check(
    session_payload["crawl_session_id"]
    == "crawl_session_test_001",
    "Crawler session identity serialization failed.",
)

check(
    session_payload["workspace_id"]
    == "ws_crawler_test",
    "Crawler workspace serialization failed.",
)

check(
    session_payload["status"] == "created",
    "Crawler status serialization failed.",
)

check(
    session_payload["source_type"]
    == "autonomous_public_web_crawler",
    "Crawler source type is incorrect.",
)

record(
    "crawler session serializes correctly",
    True,
)

reconstructed_session = CrawlSession.from_dict(
    session_payload
)

check(
    reconstructed_session.to_dict()
    == session_payload,
    "Crawler session reconstruction failed.",
)

record(
    "crawler session reconstructs correctly",
    True,
)

json_payload = json.dumps(
    session_payload,
    indent=2,
    ensure_ascii=False,
)

decoded = json.loads(json_payload)

check(
    decoded["crawl_session_id"]
    == "crawl_session_test_001",
    "Crawler session JSON round-trip failed.",
)

record(
    "crawler session is JSON serializable",
    True,
)

session.status = CrawlSessionStatus.COMPLETED

check(
    session.is_terminal is True,
    "Completed crawler session must be terminal.",
)

record(
    "completed crawler session is terminal",
    True,
)


# 7. INVALID INPUT VALIDATION

invalid_cases = [
    {
        "name": "empty crawl_session_id rejected",
        "kwargs": {
            "crawl_session_id": "",
            "workspace_id": "ws_test",
            "session_name": "Test",
        },
    },
    {
        "name": "empty workspace_id rejected",
        "kwargs": {
            "crawl_session_id": "crawl_test",
            "workspace_id": "",
            "session_name": "Test",
        },
    },
    {
        "name": "empty session_name rejected",
        "kwargs": {
            "crawl_session_id": "crawl_test",
            "workspace_id": "ws_test",
            "session_name": "",
        },
    },
    {
        "name": "invalid status rejected",
        "kwargs": {
            "crawl_session_id": "crawl_test",
            "workspace_id": "ws_test",
            "session_name": "Test",
            "status": "unknown_status",
        },
    },
]

for invalid_case in invalid_cases:
    try:
        CrawlSession(
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


# 8. EXPLANATION CONTRACT

explanation = (
    explain_crawler_session_models_v1()
)

check(
    explanation.get("ok") is True,
    "Explanation contract did not return ok=True.",
)

check(
    explanation.get("schema_version")
    == CRAWLER_SESSION_SCHEMA_VERSION,
    "Explanation schema version is incorrect.",
)

check(
    explanation.get("component")
    == "crawler_session_models",
    "Explanation component name is incorrect.",
)

check(
    "session persistence"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Persistence boundary is missing.",
)

check(
    "web page fetching"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Fetching boundary is missing.",
)

record(
    "model explanation contract is correct",
    True,
)


# 9. FINAL RESULT

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
    print("CRAWLER SESSION MODELS VERIFICATION: FAIL")
    raise SystemExit(1)

print("")
print("CRAWLER SESSION MODELS VERIFICATION: PASS")
print("")
print(json.dumps(explanation, indent=2))
