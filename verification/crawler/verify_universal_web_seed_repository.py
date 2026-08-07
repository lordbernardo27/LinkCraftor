from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION,
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    UniversalWebSeed,
    UniversalWebSeedStatus,
    UniversalWebSeedType,
    count_universal_web_seeds,
    create_universal_web_seed,
    delete_universal_web_seed,
    empty_universal_web_seed_store,
    explain_universal_web_seed_repository_v1,
    get_universal_web_seed,
    list_universal_web_seeds,
    load_universal_web_seed_store,
    require_universal_web_seed,
    save_universal_web_seed_store,
    universal_web_seed_exists,
    universal_web_seed_store_path,
    update_universal_web_seed,
    validate_universal_web_seed_store,
)


ROOT = PROJECT_ROOT

REPOSITORY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "seed_repository.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

TEST_WORKSPACE_ID = (
    "ws_universal_web_seed_repository_test"
)

SEED_ID_URL_HIGH = "seed_url_high"
SEED_ID_URL_LOW = "seed_url_low"
SEED_ID_DOMAIN = "seed_domain"
SEED_ID_SITEMAP = "seed_sitemap"
SEED_ID_RSS = "seed_rss"
SEED_ID_DISABLED = "seed_disabled"
SEED_ID_ARCHIVED = "seed_archived"


def check(
    condition: bool,
    message: str,
) -> None:
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
print(" PHASE 1.2.4 - UNIVERSAL WEB SEED REPOSITORY VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE
# ------------------------------------------------------------

repository_exists = REPOSITORY_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "seed_repository.py exists",
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
    "seed_repository.py is missing.",
)

check(
    init_exists,
    "__init__.py is missing.",
)


# ------------------------------------------------------------
# 2. COMPILATION
# ------------------------------------------------------------

py_compile.compile(
    str(REPOSITORY_PATH),
    doraise=True,
)

record(
    "seed_repository.py compiles",
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
# 3. CLEAN TEST STATE
# ------------------------------------------------------------

store_path = universal_web_seed_store_path(
    TEST_WORKSPACE_ID
)

if store_path.exists():
    store_path.unlink()

record(
    "previous test repository removed",
    not store_path.exists(),
    str(store_path),
)


# ------------------------------------------------------------
# 4. SCHEMA CONTRACT
# ------------------------------------------------------------

check(
    UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION
    == "universal_web_seed_repository.v1",
    "Unexpected seed repository schema version.",
)

check(
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION
    == "universal_web_seed.v1",
    "Unexpected seed model schema version.",
)

record(
    "repository and seed schema versions are correct",
    True,
)


# ------------------------------------------------------------
# 5. EMPTY STORE
# ------------------------------------------------------------

empty_store = empty_universal_web_seed_store(
    TEST_WORKSPACE_ID
)

check(
    empty_store["schema_version"]
    == UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION,
    "Empty repository schema is incorrect.",
)

check(
    empty_store["seed_schema_version"]
    == UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    "Empty repository seed schema is incorrect.",
)

check(
    empty_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Empty repository workspace is incorrect.",
)

check(
    empty_store["seeds"] == {},
    "Empty repository seeds field must be empty.",
)

record(
    "empty seed repository contract is correct",
    True,
)


# ------------------------------------------------------------
# 6. STORE VALIDATION
# ------------------------------------------------------------

validated_store = validate_universal_web_seed_store(
    empty_store,
    workspace_id=TEST_WORKSPACE_ID,
)

check(
    validated_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Validated repository workspace is incorrect.",
)

record(
    "empty seed repository validates correctly",
    True,
)

wrong_workspace_store = dict(
    empty_store
)

wrong_workspace_store["workspace_id"] = (
    "ws_wrong_workspace"
)

try:
    validate_universal_web_seed_store(
        wrong_workspace_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "repository workspace mismatch is rejected",
        True,
    )
else:
    raise AssertionError(
        "Repository workspace mismatch was accepted."
    )

wrong_repository_schema = dict(
    empty_store
)

wrong_repository_schema["schema_version"] = (
    "universal_web_seed_repository.v999"
)

try:
    validate_universal_web_seed_store(
        wrong_repository_schema,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "unsupported repository schema is rejected",
        True,
    )
else:
    raise AssertionError(
        "Unsupported repository schema was accepted."
    )

wrong_seed_schema = dict(
    empty_store
)

wrong_seed_schema["seed_schema_version"] = (
    "universal_web_seed.v999"
)

try:
    validate_universal_web_seed_store(
        wrong_seed_schema,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "unsupported seed schema is rejected",
        True,
    )
else:
    raise AssertionError(
        "Unsupported seed schema was accepted."
    )

wrong_seeds_field = dict(
    empty_store
)

wrong_seeds_field["seeds"] = []

try:
    validate_universal_web_seed_store(
        wrong_seeds_field,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "non-object seeds field is rejected",
        True,
    )
else:
    raise AssertionError(
        "Non-object seeds field was accepted."
    )


# ------------------------------------------------------------
# 7. SAVE AND LOAD EMPTY STORE
# ------------------------------------------------------------

saved_path = save_universal_web_seed_store(
    TEST_WORKSPACE_ID,
    empty_store,
)

check(
    saved_path.is_file(),
    "Seed repository file was not created.",
)

record(
    "empty seed repository saves atomically",
    True,
    str(saved_path),
)

loaded_empty_store = load_universal_web_seed_store(
    TEST_WORKSPACE_ID
)

check(
    loaded_empty_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Loaded repository workspace is incorrect.",
)

check(
    loaded_empty_store["seeds"] == {},
    "Loaded empty repository contains seeds.",
)

record(
    "empty seed repository loads correctly",
    True,
)


# ------------------------------------------------------------
# 8. CREATE ACTIVE SEEDS
# ------------------------------------------------------------

url_high = UniversalWebSeed(
    seed_id=SEED_ID_URL_HIGH,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.URL,
    original_value=(
        "https://example.com/high-priority"
    ),
    priority=100,
    registered_at="2026-08-06T20:00:00+00:00",
    created_at="2026-08-06T20:00:00+00:00",
    updated_at="2026-08-06T20:00:00+00:00",
)

url_low = UniversalWebSeed(
    seed_id=SEED_ID_URL_LOW,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.URL,
    original_value=(
        "https://example.com/low-priority"
    ),
    priority=10,
    registered_at="2026-08-06T19:00:00+00:00",
    created_at="2026-08-06T19:00:00+00:00",
    updated_at="2026-08-06T19:00:00+00:00",
)

domain_seed = UniversalWebSeed(
    seed_id=SEED_ID_DOMAIN,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.DOMAIN,
    original_value="example.com",
    domain="example.com",
    root_domain="example.com",
    priority=50,
    registered_at="2026-08-06T18:00:00+00:00",
    created_at="2026-08-06T18:00:00+00:00",
    updated_at="2026-08-06T18:00:00+00:00",
)

sitemap_seed = UniversalWebSeed(
    seed_id=SEED_ID_SITEMAP,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.SITEMAP,
    original_value="https://example.com/sitemap.xml",
    domain="example.com",
    priority=25,
    registered_at="2026-08-06T17:00:00+00:00",
    created_at="2026-08-06T17:00:00+00:00",
    updated_at="2026-08-06T17:00:00+00:00",
)

rss_seed = UniversalWebSeed(
    seed_id=SEED_ID_RSS,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.RSS_FEED,
    original_value="https://example.com/feed.xml",
    domain="example.com",
    priority=20,
    registered_at="2026-08-06T16:00:00+00:00",
    created_at="2026-08-06T16:00:00+00:00",
    updated_at="2026-08-06T16:00:00+00:00",
)

for seed in (
    url_high,
    url_low,
    domain_seed,
    sitemap_seed,
    rss_seed,
):
    created_seed = create_universal_web_seed(
        seed
    )

    check(
        created_seed.seed_id == seed.seed_id,
        f"Seed creation failed: {seed.seed_id}",
    )

record(
    "active seed records create correctly",
    True,
)


# ------------------------------------------------------------
# 9. CREATE DISABLED AND ARCHIVED SEEDS
# ------------------------------------------------------------

disabled_seed = UniversalWebSeed(
    seed_id=SEED_ID_DISABLED,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.URL,
    original_value="https://example.com/disabled",
    priority=5,
    enabled=False,
    status=UniversalWebSeedStatus.DISABLED,
    enabled_at=None,
    disabled_at="2026-08-06T21:00:00+00:00",
)

archived_seed = UniversalWebSeed(
    seed_id=SEED_ID_ARCHIVED,
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.DOMAIN,
    original_value="archived.example.com",
    domain="archived.example.com",
    root_domain="example.com",
    priority=1,
    enabled=False,
    status=UniversalWebSeedStatus.ARCHIVED,
    enabled_at=None,
    archived_at="2026-08-06T21:30:00+00:00",
)

create_universal_web_seed(
    disabled_seed
)

create_universal_web_seed(
    archived_seed
)

record(
    "disabled and archived seeds create correctly",
    True,
)


# ------------------------------------------------------------
# 10. DUPLICATE IDENTITY PROTECTION
# ------------------------------------------------------------

try:
    create_universal_web_seed(
        url_high
    )
except ValueError:
    record(
        "duplicate seed identity is rejected",
        True,
    )
else:
    raise AssertionError(
        "Duplicate seed identity was accepted."
    )


# ------------------------------------------------------------
# 11. RETRIEVE, REQUIRE, EXISTS
# ------------------------------------------------------------

retrieved_seed = get_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id=SEED_ID_URL_HIGH,
)

check(
    retrieved_seed is not None,
    "Created seed could not be retrieved.",
)

check(
    retrieved_seed.seed_id
    == SEED_ID_URL_HIGH,
    "Retrieved seed identity is incorrect.",
)

record(
    "seed retrieves correctly",
    True,
)

required_seed = require_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id=SEED_ID_URL_HIGH,
)

check(
    required_seed.seed_id
    == SEED_ID_URL_HIGH,
    "Required seed identity is incorrect.",
)

record(
    "required seed retrieves correctly",
    True,
)

check(
    universal_web_seed_exists(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=SEED_ID_URL_HIGH,
    )
    is True,
    "Seed existence check failed.",
)

record(
    "seed existence check passes",
    True,
)


# ------------------------------------------------------------
# 12. MISSING SEED BEHAVIOR
# ------------------------------------------------------------

missing_seed = get_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id="missing_seed",
)

check(
    missing_seed is None,
    "Missing seed should return None.",
)

record(
    "missing seed returns None",
    True,
)

try:
    require_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id="missing_seed",
    )
except KeyError:
    record(
        "requiring a missing seed raises KeyError",
        True,
    )
else:
    raise AssertionError(
        "Missing seed did not raise KeyError."
    )


# ------------------------------------------------------------
# 13. UPDATE SEED
# ------------------------------------------------------------

retrieved_seed.priority = 150
retrieved_seed.metadata["updated_by_test"] = True
retrieved_seed.touch()

updated_seed = update_universal_web_seed(
    retrieved_seed
)

check(
    updated_seed.priority == 150,
    "Seed priority update failed.",
)

check(
    updated_seed.metadata.get(
        "updated_by_test"
    )
    is True,
    "Seed metadata update failed.",
)

record(
    "seed updates correctly",
    True,
)

try:
    update_universal_web_seed(
        UniversalWebSeed(
            seed_id="missing_update_seed",
            workspace_id=TEST_WORKSPACE_ID,
            seed_type="url",
            original_value="https://example.com/missing",
        )
    )
except KeyError:
    record(
        "updating a missing seed raises KeyError",
        True,
    )
else:
    raise AssertionError(
        "Updating a missing seed was accepted."
    )


# ------------------------------------------------------------
# 14. LIST ALL AND ORDERING
# ------------------------------------------------------------

all_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID
)

check(
    len(all_seeds) == 7,
    "All-seed listing should return 7 records.",
)

all_seed_ids = [
    seed.seed_id
    for seed in all_seeds
]

check(
    all_seed_ids[0] == SEED_ID_URL_HIGH,
    "Highest-priority seed was not listed first.",
)

check(
    all_seed_ids[-1] == SEED_ID_ARCHIVED,
    "Lowest-priority seed was not listed last.",
)

record(
    "seed listing and deterministic ordering are correct",
    True,
    ", ".join(all_seed_ids),
)


# ------------------------------------------------------------
# 15. FILTER BY SEED TYPE
# ------------------------------------------------------------

url_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="url",
)

url_seed_ids = {
    seed.seed_id
    for seed in url_seeds
}

check(
    url_seed_ids
    == {
        SEED_ID_URL_HIGH,
        SEED_ID_URL_LOW,
        SEED_ID_DISABLED,
    },
    "URL seed filtering returned incorrect records.",
)

record(
    "seed type filtering works correctly",
    True,
)


# ------------------------------------------------------------
# 16. FILTER BY STATUS
# ------------------------------------------------------------

disabled_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    status="disabled",
)

check(
    [
        seed.seed_id
        for seed in disabled_seeds
    ]
    == [SEED_ID_DISABLED],
    "Disabled seed filtering is incorrect.",
)

archived_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    status="archived",
)

check(
    [
        seed.seed_id
        for seed in archived_seeds
    ]
    == [SEED_ID_ARCHIVED],
    "Archived seed filtering is incorrect.",
)

record(
    "seed status filtering works correctly",
    True,
)


# ------------------------------------------------------------
# 17. FILTER BY ENABLED AND ACTIVE
# ------------------------------------------------------------

enabled_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    enabled=True,
)

check(
    len(enabled_seeds) == 5,
    "Enabled seed filtering should return 5 records.",
)

inactive_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    enabled=False,
)

check(
    {
        seed.seed_id
        for seed in inactive_seeds
    }
    == {
        SEED_ID_DISABLED,
        SEED_ID_ARCHIVED,
    },
    "Disabled-state filtering returned incorrect records.",
)

active_seeds = list_universal_web_seeds(
    workspace_id=TEST_WORKSPACE_ID,
    active_only=True,
)

check(
    len(active_seeds) == 5,
    "Active-only filtering should return 5 records.",
)

check(
    all(
        seed.is_active
        for seed in active_seeds
    ),
    "Active-only filtering returned an inactive seed.",
)

record(
    "enabled and active filters work correctly",
    True,
)


# ------------------------------------------------------------
# 18. FILTERED COUNTS
# ------------------------------------------------------------

check(
    count_universal_web_seeds(
        workspace_id=TEST_WORKSPACE_ID,
    )
    == 7,
    "Total seed count should be 7.",
)

check(
    count_universal_web_seeds(
        workspace_id=TEST_WORKSPACE_ID,
        seed_type="url",
    )
    == 3,
    "URL seed count should be 3.",
)

check(
    count_universal_web_seeds(
        workspace_id=TEST_WORKSPACE_ID,
        status="disabled",
    )
    == 1,
    "Disabled seed count should be 1.",
)

check(
    count_universal_web_seeds(
        workspace_id=TEST_WORKSPACE_ID,
        active_only=True,
    )
    == 5,
    "Active seed count should be 5.",
)

record(
    "filtered seed counting works correctly",
    True,
)


# ------------------------------------------------------------
# 19. INVALID FILTERS
# ------------------------------------------------------------

invalid_filter_cases = [
    (
        "invalid seed type filter rejected",
        {
            "seed_type": "unknown",
        },
    ),
    (
        "invalid status filter rejected",
        {
            "status": "unknown",
        },
    ),
    (
        "non-boolean enabled filter rejected",
        {
            "enabled": "yes",
        },
    ),
    (
        "non-boolean active_only rejected",
        {
            "active_only": "yes",
        },
    ),
]

for name, kwargs in invalid_filter_cases:
    try:
        list_universal_web_seeds(
            workspace_id=TEST_WORKSPACE_ID,
            **kwargs,
        )
    except ValueError:
        record(
            name,
            True,
        )
    else:
        raise AssertionError(name)


# ------------------------------------------------------------
# 20. IDENTITY INTEGRITY VALIDATION
# ------------------------------------------------------------

valid_store = load_universal_web_seed_store(
    TEST_WORKSPACE_ID
)

identity_mismatch_store = json.loads(
    json.dumps(valid_store)
)

identity_payload = identity_mismatch_store[
    "seeds"
][SEED_ID_URL_LOW]

identity_mismatch_store["seeds"][
    "wrong_repository_key"
] = identity_payload

del identity_mismatch_store[
    "seeds"
][SEED_ID_URL_LOW]

try:
    validate_universal_web_seed_store(
        identity_mismatch_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "repository key and seed identity mismatch is rejected",
        True,
    )
else:
    raise AssertionError(
        "Seed identity mismatch was accepted."
    )


# ------------------------------------------------------------
# 21. RECORD WORKSPACE ISOLATION
# ------------------------------------------------------------

workspace_mismatch_store = json.loads(
    json.dumps(valid_store)
)

workspace_mismatch_store["seeds"][
    SEED_ID_DOMAIN
]["workspace_id"] = "ws_other_workspace"

try:
    validate_universal_web_seed_store(
        workspace_mismatch_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "cross-workspace seed record is rejected",
        True,
    )
else:
    raise AssertionError(
        "Cross-workspace seed record was accepted."
    )


# ------------------------------------------------------------
# 22. NON-OBJECT SEED RECORD
# ------------------------------------------------------------

non_object_record_store = json.loads(
    json.dumps(valid_store)
)

non_object_record_store["seeds"][
    "invalid_seed"
] = "not-an-object"

try:
    validate_universal_web_seed_store(
        non_object_record_store,
        workspace_id=TEST_WORKSPACE_ID,
    )
except ValueError:
    record(
        "non-object seed record is rejected",
        True,
    )
else:
    raise AssertionError(
        "Non-object seed record was accepted."
    )


# ------------------------------------------------------------
# 23. CORRUPTION DETECTION
# ------------------------------------------------------------

valid_store_text = json.dumps(
    valid_store,
    indent=2,
    ensure_ascii=False,
)

store_path.write_text(
    "{this is not valid json",
    encoding="utf-8",
)

try:
    load_universal_web_seed_store(
        TEST_WORKSPACE_ID
    )
except RuntimeError:
    record(
        "corrupt seed repository is rejected",
        True,
    )
else:
    raise AssertionError(
        "Corrupt seed repository was accepted."
    )

store_path.write_text(
    valid_store_text,
    encoding="utf-8",
)

restored_store = load_universal_web_seed_store(
    TEST_WORKSPACE_ID
)

check(
    restored_store["workspace_id"]
    == TEST_WORKSPACE_ID,
    "Seed repository restoration failed.",
)

record(
    "seed repository restores after corruption test",
    True,
)


# ------------------------------------------------------------
# 24. DELETE BEHAVIOR
# ------------------------------------------------------------

deleted = delete_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id=SEED_ID_RSS,
)

check(
    deleted is True,
    "Seed deletion should return True.",
)

check(
    universal_web_seed_exists(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=SEED_ID_RSS,
    )
    is False,
    "Deleted seed still exists.",
)

record(
    "seed physically deletes correctly",
    True,
)

missing_delete = delete_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id=SEED_ID_RSS,
    missing_ok=True,
)

check(
    missing_delete is False,
    "missing_ok deletion should return False.",
)

record(
    "missing_ok deletion behaves correctly",
    True,
)

try:
    delete_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=SEED_ID_RSS,
        missing_ok="yes",
    )
except ValueError:
    record(
        "non-boolean missing_ok is rejected",
        True,
    )
else:
    raise AssertionError(
        "Non-boolean missing_ok was accepted."
    )


# ------------------------------------------------------------
# 25. EXPLANATION CONTRACT
# ------------------------------------------------------------

explanation = (
    explain_universal_web_seed_repository_v1()
)

check(
    explanation.get("ok") is True,
    "Repository explanation did not return ok=True.",
)

check(
    explanation.get("component")
    == "universal_web_seed_repository",
    "Repository explanation component is incorrect.",
)

check(
    explanation.get("schema_version")
    == UNIVERSAL_WEB_SEED_REPOSITORY_SCHEMA_VERSION,
    "Repository explanation schema is incorrect.",
)

check(
    explanation.get("seed_schema_version")
    == UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    "Repository explanation seed schema is incorrect.",
)

check(
    explanation.get("atomic_write") is True,
    "Repository explanation must confirm atomic writes.",
)

check(
    explanation.get("read_retry_attempts") == 3,
    "Repository read retry count is incorrect.",
)

check(
    explanation.get("supported_filters")
    == [
        "seed_type",
        "status",
        "enabled",
        "active_only",
    ],
    "Repository filter contract is incorrect.",
)

check(
    explanation.get("ordering")
    == [
        "priority descending",
        "registered_at ascending",
        "seed_id ascending",
    ],
    "Repository ordering contract is incorrect.",
)

check(
    "seed registration orchestration"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Registration boundary is missing.",
)

check(
    "seed eligibility validation"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Eligibility boundary is missing.",
)

check(
    explanation.get("next_component")
    == "Seed Registration Engine",
    "Next component is incorrect.",
)

record(
    "seed repository explanation contract is correct",
    True,
)


# ------------------------------------------------------------
# 26. FINAL CLEANUP
# ------------------------------------------------------------

if store_path.exists():
    store_path.unlink()

check(
    not store_path.exists(),
    "Seed repository test cleanup failed.",
)

record(
    "test seed repository artifact removed",
    True,
)


# ------------------------------------------------------------
# 27. FINAL RESULT
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
print(
    "Checks passed:   "
    f"{len(results) - len(failed_checks)}"
)
print(f"Checks failed:   {len(failed_checks)}")

if failed_checks:
    print("")
    print(
        "UNIVERSAL WEB SEED REPOSITORY "
        "VERIFICATION: FAIL"
    )
    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED REPOSITORY "
    "VERIFICATION: PASS"
)
print("")
print(
    json.dumps(
        explanation,
        indent=2,
        ensure_ascii=False,
    )
)
