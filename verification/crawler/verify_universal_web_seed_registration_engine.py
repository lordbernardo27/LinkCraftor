from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION,
    UniversalWebSeed,
    UniversalWebSeedStatus,
    UniversalWebSeedType,
    build_universal_web_seed_registration_record,
    build_universal_web_seed_registration_result,
    count_universal_web_seeds,
    explain_universal_web_seed_registration_engine_v1,
    generate_universal_web_seed_id,
    get_universal_web_seed,
    register_universal_web_seed,
    universal_web_seed_exists,
    universal_web_seed_store_path,
)


ROOT = PROJECT_ROOT

ENGINE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "seed_registration_engine.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

TEST_WORKSPACE_ID = (
    "ws_universal_web_seed_registration_test"
)

EXPLICIT_SEED_ID = "web_seed_explicit_test_001"
OVERWRITE_SEED_ID = "web_seed_overwrite_test_001"


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
print(" PHASE 1.3.4 - UNIVERSAL WEB SEED REGISTRATION")
print(" ENGINE VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE
# ------------------------------------------------------------

engine_exists = ENGINE_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "seed_registration_engine.py exists",
    engine_exists,
    str(ENGINE_PATH),
)

record(
    "__init__.py exists",
    init_exists,
    str(INIT_PATH),
)

check(
    engine_exists,
    "seed_registration_engine.py is missing.",
)

check(
    init_exists,
    "__init__.py is missing.",
)


# ------------------------------------------------------------
# 2. COMPILATION
# ------------------------------------------------------------

py_compile.compile(
    str(ENGINE_PATH),
    doraise=True,
)

record(
    "seed_registration_engine.py compiles",
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
    "previous registration test repository removed",
    not store_path.exists(),
    str(store_path),
)


# ------------------------------------------------------------
# 4. SCHEMA VERSION
# ------------------------------------------------------------

check(
    UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION
    == "universal_web_seed_registration.v1",
    "Unexpected registration schema version.",
)

record(
    "registration schema version is correct",
    True,
)


# ------------------------------------------------------------
# 5. IDENTITY GENERATION
# ------------------------------------------------------------

generated_id_1 = generate_universal_web_seed_id()
generated_id_2 = generate_universal_web_seed_id()

check(
    generated_id_1.startswith("web_seed_"),
    "Generated seed identity has the wrong prefix.",
)

check(
    generated_id_2.startswith("web_seed_"),
    "Second generated identity has the wrong prefix.",
)

check(
    generated_id_1 != generated_id_2,
    "Generated seed identities are not unique.",
)

check(
    len(generated_id_1) > len("web_seed_"),
    "Generated seed identity is incomplete.",
)

record(
    "seed identity generation is valid and unique",
    True,
    generated_id_1,
)


# ------------------------------------------------------------
# 6. BUILD RECORD WITHOUT PERSISTENCE
# ------------------------------------------------------------

record_only = (
    build_universal_web_seed_registration_record(
        workspace_id=TEST_WORKSPACE_ID,
        seed_type="url",
        original_value="https://example.com/record-only",
        crawler_session_id="crawl_session_registration_test",
        priority=25,
        registered_by="verification_user",
        registered_source="verification_suite",
        metadata={
            "purpose": "record_only",
        },
    )
)

check(
    isinstance(record_only, UniversalWebSeed),
    "Registration record builder did not return UniversalWebSeed.",
)

check(
    record_only.seed_id.startswith("web_seed_"),
    "Registration record did not receive a generated seed ID.",
)

check(
    record_only.workspace_id == TEST_WORKSPACE_ID,
    "Registration record workspace is incorrect.",
)

check(
    record_only.seed_type == UniversalWebSeedType.URL,
    "Registration record seed type is incorrect.",
)

check(
    record_only.original_value
    == "https://example.com/record-only",
    "Registration record original value is incorrect.",
)

check(
    record_only.priority == 25,
    "Registration record priority is incorrect.",
)

check(
    record_only.crawler_session_id
    == "crawl_session_registration_test",
    "Crawler-session association was not preserved.",
)

check(
    record_only.registered_by
    == "verification_user",
    "Registration actor was not preserved.",
)

check(
    record_only.registered_source
    == "verification_suite",
    "Registration source was not preserved.",
)

check(
    record_only.metadata["purpose"]
    == "record_only",
    "Caller metadata was not preserved.",
)

check(
    record_only.metadata["eligibility_evaluated"]
    is False,
    "New seed must not claim eligibility evaluation.",
)

check(
    record_only.metadata["frontier_inserted"]
    is False,
    "New seed must not claim frontier insertion.",
)

check(
    record_only.metadata["target_normalized"]
    is False,
    "New seed must not claim target normalization.",
)

check(
    universal_web_seed_exists(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=record_only.seed_id,
    )
    is False,
    "Record builder unexpectedly persisted the seed.",
)

record(
    "registration record builds without persistence",
    True,
)


# ------------------------------------------------------------
# 7. REGISTER URL SEED
# ------------------------------------------------------------

url_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="url",
    original_value="https://example.com/articles/start",
    crawler_session_id="crawl_session_registration_test",
    priority=100,
    registered_by="verification_user",
    registered_source="verification_suite",
    metadata={
        "category": "url_test",
    },
)

url_seed_id = url_result["seed_id"]

check(
    url_result["ok"] is True,
    "URL registration did not return ok=True.",
)

check(
    url_result["status"] == "registered",
    "URL registration status is incorrect.",
)

check(
    url_result["created"] is True,
    "New URL registration must return created=True.",
)

check(
    url_result["seed_type"] == "url",
    "URL result seed type is incorrect.",
)

check(
    url_result["next_pipeline_stage"]
    == "Seed Eligibility Validation",
    "URL result points to the wrong next pipeline stage.",
)

check(
    universal_web_seed_exists(
        workspace_id=TEST_WORKSPACE_ID,
        seed_id=url_seed_id,
    )
    is True,
    "Registered URL seed was not persisted.",
)

record(
    "URL seed registers and persists correctly",
    True,
    url_seed_id,
)


# ------------------------------------------------------------
# 8. REGISTER DOMAIN SEED
# ------------------------------------------------------------

domain_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type=UniversalWebSeedType.DOMAIN,
    original_value="example.com",
    priority=80,
)

check(
    domain_result["seed_type"] == "domain",
    "Domain seed registration failed.",
)

record(
    "domain seed registers correctly",
    True,
)


# ------------------------------------------------------------
# 9. REGISTER SITEMAP SEED
# ------------------------------------------------------------

sitemap_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="sitemap",
    original_value="https://example.com/sitemap.xml",
    priority=60,
)

check(
    sitemap_result["seed_type"] == "sitemap",
    "Sitemap seed registration failed.",
)

record(
    "sitemap seed registers correctly",
    True,
)


# ------------------------------------------------------------
# 10. REGISTER RSS FEED SEED
# ------------------------------------------------------------

rss_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="rss_feed",
    original_value="https://example.com/feed.xml",
    priority=40,
)

check(
    rss_result["seed_type"] == "rss_feed",
    "RSS-feed seed registration failed.",
)

record(
    "RSS-feed seed registers correctly",
    True,
)


# ------------------------------------------------------------
# 11. EXPLICIT SEED ID
# ------------------------------------------------------------

explicit_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="url",
    original_value="https://example.com/explicit-id",
    seed_id=EXPLICIT_SEED_ID,
)

check(
    explicit_result["seed_id"]
    == EXPLICIT_SEED_ID,
    "Explicit seed identity was not preserved.",
)

check(
    explicit_result["created"] is True,
    "Explicit new identity must return created=True.",
)

record(
    "caller-supplied seed identity is supported",
    True,
)


# ------------------------------------------------------------
# 12. DUPLICATE IDENTITY REJECTION
# ------------------------------------------------------------

try:
    register_universal_web_seed(
        workspace_id=TEST_WORKSPACE_ID,
        seed_type="url",
        original_value="https://example.com/duplicate-id",
        seed_id=EXPLICIT_SEED_ID,
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
# 13. OVERWRITE EXISTING SEED
# ------------------------------------------------------------

first_overwrite_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="url",
    original_value="https://example.com/original",
    priority=1,
    seed_id=OVERWRITE_SEED_ID,
)

check(
    first_overwrite_result["created"] is True,
    "Initial overwrite-test seed was not created.",
)

replacement_result = register_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_type="url",
    original_value="https://example.com/replacement",
    priority=999,
    seed_id=OVERWRITE_SEED_ID,
    overwrite=True,
)

check(
    replacement_result["status"] == "replaced",
    "Overwrite result status must be replaced.",
)

check(
    replacement_result["created"] is False,
    "Overwrite of an existing seed must return created=False.",
)

replacement_seed = get_universal_web_seed(
    workspace_id=TEST_WORKSPACE_ID,
    seed_id=OVERWRITE_SEED_ID,
)

check(
    replacement_seed is not None,
    "Replacement seed could not be retrieved.",
)

check(
    replacement_seed.original_value
    == "https://example.com/replacement",
    "Overwrite did not replace the seed target.",
)

check(
    replacement_seed.priority == 999,
    "Overwrite did not replace seed priority.",
)

record(
    "existing seed overwrite works correctly",
    True,
)


# ------------------------------------------------------------
# 14. RESULT BUILDER
# ------------------------------------------------------------

manual_result = (
    build_universal_web_seed_registration_result(
        seed=record_only,
        created=True,
    )
)

check(
    manual_result["component"]
    == "universal_web_seed_registration_engine",
    "Result builder component is incorrect.",
)

check(
    manual_result["schema_version"]
    == UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION,
    "Result builder schema is incorrect.",
)

check(
    manual_result["status"] == "registered",
    "Result builder registration status is incorrect.",
)

check(
    manual_result["seed"]["seed_id"]
    == record_only.seed_id,
    "Result builder did not serialize the seed.",
)

record(
    "stable registration result builds correctly",
    True,
)


# ------------------------------------------------------------
# 15. REPOSITORY COUNT
# ------------------------------------------------------------

check(
    count_universal_web_seeds(
        workspace_id=TEST_WORKSPACE_ID,
    )
    == 6,
    "Expected 6 persisted seed records.",
)

record(
    "registration engine persisted expected seed count",
    True,
)


# ------------------------------------------------------------
# 16. INVALID REGISTRATION REQUESTS
# ------------------------------------------------------------

invalid_registration_cases = [
    (
        "empty workspace rejected",
        {
            "workspace_id": "",
            "seed_type": "url",
            "original_value": "https://example.com",
        },
    ),
    (
        "empty original value rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "",
        },
    ),
    (
        "invalid seed type rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "unsupported",
            "original_value": "https://example.com",
        },
    ),
    (
        "negative priority rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "priority": -1,
        },
    ),
    (
        "empty registered_by rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "registered_by": "",
        },
    ),
    (
        "empty registered_source rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "registered_source": "",
        },
    ),
    (
        "invalid metadata rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "metadata": "invalid",
        },
    ),
    (
        "empty explicit seed ID rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "seed_id": "",
        },
    ),
    (
        "non-boolean overwrite rejected",
        {
            "workspace_id": TEST_WORKSPACE_ID,
            "seed_type": "url",
            "original_value": "https://example.com",
            "overwrite": "yes",
        },
    ),
]

for name, kwargs in invalid_registration_cases:
    try:
        register_universal_web_seed(
            **kwargs
        )
    except ValueError:
        record(
            name,
            True,
        )
    else:
        raise AssertionError(name)


# ------------------------------------------------------------
# 17. INVALID RESULT BUILDER INPUTS
# ------------------------------------------------------------

try:
    build_universal_web_seed_registration_result(
        seed="invalid",
        created=True,
    )
except ValueError:
    record(
        "invalid result seed is rejected",
        True,
    )
else:
    raise AssertionError(
        "Invalid result seed was accepted."
    )

try:
    build_universal_web_seed_registration_result(
        seed=record_only,
        created="yes",
    )
except ValueError:
    record(
        "non-boolean created result flag is rejected",
        True,
    )
else:
    raise AssertionError(
        "Non-boolean created result flag was accepted."
    )


# ------------------------------------------------------------
# 18. EXPLANATION CONTRACT
# ------------------------------------------------------------

explanation = (
    explain_universal_web_seed_registration_engine_v1()
)

check(
    explanation.get("ok") is True,
    "Registration explanation did not return ok=True.",
)

check(
    explanation.get("component")
    == "universal_web_seed_registration_engine",
    "Registration explanation component is incorrect.",
)

check(
    explanation.get("schema_version")
    == UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION,
    "Registration explanation schema is incorrect.",
)

check(
    explanation.get("operation_scope")
    == "single seed registration",
    "Registration operation scope is incorrect.",
)

check(
    explanation.get("identity_prefix")
    == "web_seed_",
    "Registration identity prefix is incorrect.",
)

check(
    set(
        explanation.get(
            "supported_seed_types",
            [],
        )
    )
    == {
        "url",
        "domain",
        "sitemap",
        "rss_feed",
    },
    "Registration explanation seed types are incorrect.",
)

check(
    explanation.get("success_statuses")
    == [
        "registered",
        "replaced",
    ],
    "Registration success statuses are incorrect.",
)

check(
    "duplicate seed-target detection"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Duplicate-target boundary is missing.",
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
    "Crawl Frontier insertion"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Crawl Frontier boundary is missing.",
)

check(
    explanation.get("next_component")
    == "Seed Controls",
    "Next registry component is incorrect.",
)

check(
    explanation.get("next_pipeline_stage")
    == "Seed Eligibility Validation",
    "Next crawler pipeline stage is incorrect.",
)

record(
    "registration engine explanation contract is correct",
    True,
)


# ------------------------------------------------------------
# 19. FINAL CLEANUP
# ------------------------------------------------------------

if store_path.exists():
    store_path.unlink()

check(
    not store_path.exists(),
    "Registration verification cleanup failed.",
)

record(
    "registration test repository artifact removed",
    True,
)


# ------------------------------------------------------------
# 20. FINAL RESULT
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
        "UNIVERSAL WEB SEED REGISTRATION ENGINE "
        "VERIFICATION: FAIL"
    )
    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED REGISTRATION ENGINE "
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
