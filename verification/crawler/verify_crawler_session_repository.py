from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION,
    CRAWLER_SESSION_SCHEMA_VERSION,
    CrawlSession,
    CrawlSessionLimits,
    CrawlSessionStatistics,
    CrawlSessionStatus,
    count_crawler_sessions,
    crawler_session_exists,
    crawler_session_store_path,
    create_crawler_session,
    delete_crawler_session,
    empty_crawler_session_store,
    explain_crawler_session_repository_v1,
    get_crawler_session,
    list_crawler_sessions,
    load_crawler_session_store,
    require_crawler_session,
    save_crawler_session_store,
    update_crawler_session,
    validate_crawler_session_store,
)

ROOT = PROJECT_ROOT

REPOSITORY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "session_repository.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

TEST_WORKSPACE_ID = "ws_crawler_repository_test"
SESSION_ID_1 = "crawl_session_repository_test_001"
SESSION_ID_2 = "crawl_session_repository_test_002"


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
print(" PHASE 1.3.3 - CRAWLER SESSION REPOSITORY VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE AND COMPILATION
# ------------------------------------------------------------

repository_exists = REPOSITORY_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "session_repository.py exists",
    repository_exists,
    str(REPOSITORY_PATH),
)

record(
    "__init__.py exists",
    init_exists,
    str(INIT_PATH),
)

check(
    repository_exists,
    "session_repository.py is missing.",
)

check(
    init_exists,
    "__init__.py is missing.",
)

py_compile.compile(
    str(REPOSITORY_PATH),
    doraise=True,
)

record(
    "session_repository.py compiles",
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
    "previous test store removed",
    not store_path.exists(),
    str(store_path),
)


# ------------------------------------------------------------
# 3. EMPTY STORE CONTRACT
# ------------------------------------------------------------

empty_store = empty_crawler_session_store(
    TEST_WORKSPACE_ID
)

check(
    empty_store["schema_version"]
    == CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION,
    "Empty store repository schema is incorrect.",
)

check(
    empty_store["crawler_session_schema_version"]
    == CRAWLER_SESSION_SCHEMA_VERSION,
    "Empty store session schema is incorrect.",
)

check(
    empty_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Empty store workspace is incorrect.",
)

check(
    empty_store["sessions"] == {},
    "Empty store sessions field is not empty.",
)

record(
    "empty repository contract is correct",
    True,
)


# ------------------------------------------------------------
# 4. STORE VALIDATION
# ------------------------------------------------------------

validated_empty_store = validate_crawler_session_store(
    empty_store,
    workspace_id=TEST_WORKSPACE_ID,
)

check(
    validated_empty_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Validated store workspace is incorrect.",
)

record(
    "empty store validates correctly",
    True,
)

invalid_workspace_store = dict(
    empty_store
)

invalid_workspace_store["workspace_id"] = (
    "ws_wrong_workspace"
)

try:
    validate_crawler_session_store(
        invalid_workspace_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "workspace mismatch is rejected",
        True,
    )
else:
    raise AssertionError(
        "Workspace mismatch was accepted."
    )

invalid_sessions_store = dict(
    empty_store
)

invalid_sessions_store["sessions"] = []

try:
    validate_crawler_session_store(
        invalid_sessions_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "non-object sessions field is rejected",
        True,
    )
else:
    raise AssertionError(
        "Invalid sessions field was accepted."
    )


# ------------------------------------------------------------
# 5. SAVE AND LOAD EMPTY STORE
# ------------------------------------------------------------

saved_path = save_crawler_session_store(
    TEST_WORKSPACE_ID,
    empty_store,
)

check(
    saved_path.is_file(),
    "Crawler session store was not created.",
)

record(
    "empty repository saves atomically",
    True,
    str(saved_path),
)

loaded_empty_store = load_crawler_session_store(
    TEST_WORKSPACE_ID
)

check(
    loaded_empty_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Loaded store workspace is incorrect.",
)

check(
    loaded_empty_store["sessions"] == {},
    "Loaded empty store contains sessions.",
)

record(
    "empty repository loads correctly",
    True,
)


# ------------------------------------------------------------
# 6. CREATE SESSION
# ------------------------------------------------------------

session_1 = CrawlSession(
    crawl_session_id=SESSION_ID_1,
    workspace_id=TEST_WORKSPACE_ID,
    session_name="Repository Test Session One",
    status=CrawlSessionStatus.CREATED,
    limits=CrawlSessionLimits(
        maximum_urls=100,
        maximum_domains=10,
        maximum_depth=3,
        maximum_runtime_seconds=600,
    ),
    statistics=CrawlSessionStatistics(
        seeds_registered=2,
    ),
    metadata={
        "test_case": "create_session",
    },
)

created_session_1 = create_crawler_session(
    session_1
)

check(
    created_session_1.crawl_session_id
    == SESSION_ID_1,
    "Created crawler session identity is incorrect.",
)

check(
    created_session_1.workspace_id
    == TEST_WORKSPACE_ID,
    "Created crawler session workspace is incorrect.",
)

record(
    "crawler session creates correctly",
    True,
)


# ------------------------------------------------------------
# 7. DUPLICATE PROTECTION
# ------------------------------------------------------------

try:
    create_crawler_session(
        session_1
    )
except ValueError:
    record(
        "duplicate crawler session is rejected",
        True,
    )
else:
    raise AssertionError(
        "Duplicate crawler session was accepted."
    )


# ------------------------------------------------------------
# 8. GET, REQUIRE, EXISTS, COUNT
# ------------------------------------------------------------

retrieved_session_1 = get_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=SESSION_ID_1,
)

check(
    retrieved_session_1 is not None,
    "Created crawler session could not be retrieved.",
)

check(
    retrieved_session_1.crawl_session_id
    == SESSION_ID_1,
    "Retrieved crawler session identity is incorrect.",
)

record(
    "crawler session retrieves correctly",
    True,
)

required_session_1 = require_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=SESSION_ID_1,
)

check(
    required_session_1.crawl_session_id
    == SESSION_ID_1,
    "Required crawler session is incorrect.",
)

record(
    "required crawler session retrieves correctly",
    True,
)

check(
    crawler_session_exists(
        workspace_id=TEST_WORKSPACE_ID,
        crawl_session_id=SESSION_ID_1,
    )
    is True,
    "Crawler session existence check failed.",
)

record(
    "crawler session existence check passes",
    True,
)

check(
    count_crawler_sessions(
        workspace_id=TEST_WORKSPACE_ID,
    )
    == 1,
    "Crawler session count should be 1.",
)

record(
    "crawler session count is correct",
    True,
)


# ------------------------------------------------------------
# 9. UPDATE SESSION
# ------------------------------------------------------------

retrieved_session_1.status = (
    CrawlSessionStatus.RUNNING
)

retrieved_session_1.current_phase = (
    "repository_verification_running"
)

retrieved_session_1.statistics.urls_discovered = 12

retrieved_session_1.touch()

updated_session_1 = update_crawler_session(
    retrieved_session_1
)

check(
    updated_session_1.status
    == CrawlSessionStatus.RUNNING,
    "Crawler session status update failed.",
)

check(
    updated_session_1.current_phase
    == "repository_verification_running",
    "Crawler session phase update failed.",
)

check(
    updated_session_1.statistics.urls_discovered
    == 12,
    "Crawler session statistics update failed.",
)

record(
    "crawler session updates correctly",
    True,
)


# ------------------------------------------------------------
# 10. CREATE SECOND SESSION AND LIST
# ------------------------------------------------------------

session_2 = CrawlSession(
    crawl_session_id=SESSION_ID_2,
    workspace_id=TEST_WORKSPACE_ID,
    session_name="Repository Test Session Two",
    status=CrawlSessionStatus.CREATED,
    metadata={
        "test_case": "list_sessions",
    },
)

created_session_2 = create_crawler_session(
    session_2
)

check(
    created_session_2.crawl_session_id
    == SESSION_ID_2,
    "Second crawler session creation failed.",
)

sessions = list_crawler_sessions(
    workspace_id=TEST_WORKSPACE_ID
)

check(
    len(sessions) == 2,
    "Crawler session listing should return 2 records.",
)

listed_ids = {
    session.crawl_session_id
    for session in sessions
}

check(
    listed_ids
    == {
        SESSION_ID_1,
        SESSION_ID_2,
    },
    "Crawler session listing returned incorrect records.",
)

record(
    "crawler sessions list correctly",
    True,
)

check(
    count_crawler_sessions(
        workspace_id=TEST_WORKSPACE_ID,
    )
    == 2,
    "Crawler session count should be 2.",
)

record(
    "crawler session count updates correctly",
    True,
)


# ------------------------------------------------------------
# 11. MISSING SESSION BEHAVIOR
# ------------------------------------------------------------

missing_session = get_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id="missing_session",
)

check(
    missing_session is None,
    "Missing crawler session should return None.",
)

record(
    "missing crawler session returns None",
    True,
)

try:
    require_crawler_session(
        workspace_id=TEST_WORKSPACE_ID,
        crawl_session_id="missing_session",
    )
except KeyError:
    record(
        "require missing crawler session raises KeyError",
        True,
    )
else:
    raise AssertionError(
        "Missing crawler session did not raise KeyError."
    )

try:
    update_crawler_session(
        CrawlSession(
            crawl_session_id="missing_session",
            workspace_id=TEST_WORKSPACE_ID,
            session_name="Missing Session",
        )
    )
except KeyError:
    record(
        "update missing crawler session raises KeyError",
        True,
    )
else:
    raise AssertionError(
        "Updating a missing crawler session was accepted."
    )


# ------------------------------------------------------------
# 12. DELETE SESSION
# ------------------------------------------------------------

deleted = delete_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=SESSION_ID_1,
)

check(
    deleted is True,
    "Crawler session delete should return True.",
)

check(
    crawler_session_exists(
        workspace_id=TEST_WORKSPACE_ID,
        crawl_session_id=SESSION_ID_1,
    )
    is False,
    "Deleted crawler session still exists.",
)

record(
    "crawler session deletes correctly",
    True,
)

missing_delete = delete_crawler_session(
    workspace_id=TEST_WORKSPACE_ID,
    crawl_session_id=SESSION_ID_1,
    missing_ok=True,
)

check(
    missing_delete is False,
    "missing_ok delete should return False.",
)

record(
    "missing_ok delete behaves correctly",
    True,
)


# ------------------------------------------------------------
# 13. CORRUPTION DETECTION
# ------------------------------------------------------------

valid_store_before_corruption = (
    load_crawler_session_store(
        TEST_WORKSPACE_ID
    )
)

valid_store_text = json.dumps(
    valid_store_before_corruption,
    indent=2,
    ensure_ascii=False,
)

store_path.write_text(
    "{this is not valid json",
    encoding="utf-8",
)

try:
    load_crawler_session_store(
        TEST_WORKSPACE_ID
    )
except RuntimeError:
    record(
        "corrupt repository document is rejected",
        True,
    )
else:
    raise AssertionError(
        "Corrupt crawler session store was accepted."
    )

store_path.write_text(
    valid_store_text,
    encoding="utf-8",
)

restored_store = load_crawler_session_store(
    TEST_WORKSPACE_ID
)

check(
    restored_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Crawler session store restoration failed.",
)

record(
    "repository document restores after corruption test",
    True,
)


# ------------------------------------------------------------
# 14. EXPLANATION CONTRACT
# ------------------------------------------------------------

explanation = (
    explain_crawler_session_repository_v1()
)

check(
    explanation.get("ok") is True,
    "Repository explanation did not return ok=True.",
)

check(
    explanation.get("component")
    == "crawler_session_repository",
    "Repository explanation component is incorrect.",
)

check(
    explanation.get("schema_version")
    == CRAWLER_SESSION_REPOSITORY_SCHEMA_VERSION,
    "Repository explanation schema is incorrect.",
)

check(
    explanation.get("atomic_write") is True,
    "Repository explanation must confirm atomic writes.",
)

check(
    explanation.get("read_retry_attempts") == 3,
    "Repository explanation retry count is incorrect.",
)

check(
    "crawler session lifecycle transitions"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Repository lifecycle boundary is missing.",
)

record(
    "repository explanation contract is correct",
    True,
)


# ------------------------------------------------------------
# 15. FINAL CLEANUP
# ------------------------------------------------------------

if store_path.exists():
    store_path.unlink()

check(
    not store_path.exists(),
    "Crawler repository test store cleanup failed.",
)

record(
    "test repository artifact removed",
    True,
)


# ------------------------------------------------------------
# 16. FINAL RESULT
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
    print("CRAWLER SESSION REPOSITORY VERIFICATION: FAIL")
    raise SystemExit(1)

print("")
print("CRAWLER SESSION REPOSITORY VERIFICATION: PASS")
print("")
print(json.dumps(explanation, indent=2))
