from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    UniversalWebSeed,
    UniversalWebSeedStatus,
    UniversalWebSeedType,
    explain_universal_web_seed_models_v1,
)


ROOT = PROJECT_ROOT

SEED_MODELS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "seed_models.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)


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
print(" PHASE 1.1.4 - UNIVERSAL WEB SEED MODELS VERIFICATION")
print("============================================================")
print("")


# ------------------------------------------------------------
# 1. FILE EXISTENCE
# ------------------------------------------------------------

seed_models_exists = SEED_MODELS_PATH.is_file()
init_exists = INIT_PATH.is_file()

record(
    "seed_models.py exists",
    seed_models_exists,
    str(SEED_MODELS_PATH),
)

record(
    "__init__.py exists",
    init_exists,
    str(INIT_PATH),
)

check(
    seed_models_exists,
    "seed_models.py is missing.",
)

check(
    init_exists,
    "__init__.py is missing.",
)


# ------------------------------------------------------------
# 2. COMPILATION
# ------------------------------------------------------------

py_compile.compile(
    str(SEED_MODELS_PATH),
    doraise=True,
)

record(
    "seed_models.py compiles",
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
# 3. SCHEMA VERSION
# ------------------------------------------------------------

check(
    UNIVERSAL_WEB_SEED_SCHEMA_VERSION
    == "universal_web_seed.v1",
    "Unexpected Universal Web Seed schema version.",
)

record(
    "schema version is universal_web_seed.v1",
    True,
)


# ------------------------------------------------------------
# 4. SEED TYPES
# ------------------------------------------------------------

expected_seed_types = {
    "url",
    "domain",
    "sitemap",
    "rss_feed",
}

actual_seed_types = {
    seed_type.value
    for seed_type in UniversalWebSeedType
}

check(
    actual_seed_types == expected_seed_types,
    "Universal Web Seed types are incorrect.",
)

record(
    "all canonical seed types are present",
    True,
    ", ".join(sorted(actual_seed_types)),
)


# ------------------------------------------------------------
# 5. SEED STATUSES
# ------------------------------------------------------------

expected_statuses = {
    "registered",
    "disabled",
    "archived",
}

actual_statuses = {
    status.value
    for status in UniversalWebSeedStatus
}

check(
    actual_statuses == expected_statuses,
    "Universal Web Seed statuses are incorrect.",
)

record(
    "all canonical seed statuses are present",
    True,
    ", ".join(sorted(actual_statuses)),
)


# ------------------------------------------------------------
# 6. CREATE URL SEED
# ------------------------------------------------------------

url_seed = UniversalWebSeed(
    seed_id="seed_url_001",
    workspace_id="ws_seed_models_test",
    crawler_session_id="crawl_session_seed_test",
    seed_type=UniversalWebSeedType.URL,
    original_value="https://example.com/articles/start",
    priority=10,
    metadata={
        "test_case": "url_seed",
    },
)

check(
    url_seed.seed_type
    == UniversalWebSeedType.URL,
    "URL seed type is incorrect.",
)

check(
    url_seed.status
    == UniversalWebSeedStatus.REGISTERED,
    "New seed must be REGISTERED.",
)

check(
    url_seed.enabled is True,
    "New seed must be enabled.",
)

check(
    url_seed.is_active is True,
    "New registered seed must be active.",
)

record(
    "URL seed creates correctly",
    True,
)


# ------------------------------------------------------------
# 7. CREATE DOMAIN SEED
# ------------------------------------------------------------

domain_seed = UniversalWebSeed(
    seed_id="seed_domain_001",
    workspace_id="ws_seed_models_test",
    seed_type="domain",
    original_value="example.com",
    domain="example.com",
    root_domain="example.com",
    priority=5,
)

check(
    domain_seed.seed_type
    == UniversalWebSeedType.DOMAIN,
    "Domain seed type normalization failed.",
)

record(
    "domain seed creates correctly",
    True,
)


# ------------------------------------------------------------
# 8. CREATE SITEMAP SEED
# ------------------------------------------------------------

sitemap_seed = UniversalWebSeed(
    seed_id="seed_sitemap_001",
    workspace_id="ws_seed_models_test",
    seed_type="sitemap",
    original_value="https://example.com/sitemap.xml",
    domain="example.com",
)

check(
    sitemap_seed.seed_type
    == UniversalWebSeedType.SITEMAP,
    "Sitemap seed type normalization failed.",
)

record(
    "sitemap seed creates correctly",
    True,
)


# ------------------------------------------------------------
# 9. CREATE RSS FEED SEED
# ------------------------------------------------------------

rss_seed = UniversalWebSeed(
    seed_id="seed_rss_001",
    workspace_id="ws_seed_models_test",
    seed_type="rss_feed",
    original_value="https://example.com/feed.xml",
    domain="example.com",
)

check(
    rss_seed.seed_type
    == UniversalWebSeedType.RSS_FEED,
    "RSS feed seed type normalization failed.",
)

record(
    "RSS feed seed creates correctly",
    True,
)


# ------------------------------------------------------------
# 10. SERIALIZATION
# ------------------------------------------------------------

url_seed_payload = url_seed.to_dict()

check(
    url_seed_payload["schema_version"]
    == UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    "Serialized seed schema version is incorrect.",
)

check(
    url_seed_payload["seed_id"]
    == "seed_url_001",
    "Serialized seed identity is incorrect.",
)

check(
    url_seed_payload["workspace_id"]
    == "ws_seed_models_test",
    "Serialized seed workspace is incorrect.",
)

check(
    url_seed_payload["seed_type"] == "url",
    "Serialized seed type is incorrect.",
)

check(
    url_seed_payload["status"] == "registered",
    "Serialized seed status is incorrect.",
)

check(
    url_seed_payload["priority"] == 10,
    "Serialized seed priority is incorrect.",
)

record(
    "seed serializes correctly",
    True,
)


# ------------------------------------------------------------
# 11. RECONSTRUCTION
# ------------------------------------------------------------

reconstructed_url_seed = UniversalWebSeed.from_dict(
    url_seed_payload
)

check(
    reconstructed_url_seed.to_dict()
    == url_seed_payload,
    "Universal Web Seed reconstruction failed.",
)

record(
    "seed reconstructs correctly",
    True,
)


# ------------------------------------------------------------
# 12. JSON ROUND-TRIP
# ------------------------------------------------------------

json_payload = json.dumps(
    url_seed_payload,
    indent=2,
    ensure_ascii=False,
)

decoded_payload = json.loads(
    json_payload
)

check(
    decoded_payload["seed_id"]
    == "seed_url_001",
    "Universal Web Seed JSON round-trip failed.",
)

record(
    "seed is JSON serializable",
    True,
)


# ------------------------------------------------------------
# 13. OPTIONAL FIELD NORMALIZATION
# ------------------------------------------------------------

optional_seed = UniversalWebSeed(
    seed_id="seed_optional_001",
    workspace_id="ws_seed_models_test",
    seed_type="url",
    original_value="https://example.com",
    normalized_value="   ",
    domain="   ",
    root_domain="",
    crawler_session_id="   ",
)

check(
    optional_seed.normalized_value is None,
    "Blank normalized_value should become None.",
)

check(
    optional_seed.domain is None,
    "Blank domain should become None.",
)

check(
    optional_seed.root_domain is None,
    "Blank root_domain should become None.",
)

check(
    optional_seed.crawler_session_id is None,
    "Blank crawler_session_id should become None.",
)

record(
    "optional seed fields normalize correctly",
    True,
)


# ------------------------------------------------------------
# 14. TOUCH
# ------------------------------------------------------------

previous_updated_at = url_seed.updated_at

url_seed.touch()

check(
    url_seed.updated_at != previous_updated_at,
    "Seed touch did not update updated_at.",
)

record(
    "seed touch updates timestamp",
    True,
)


# ------------------------------------------------------------
# 15. DISABLED STATE
# ------------------------------------------------------------

disabled_seed = UniversalWebSeed(
    seed_id="seed_disabled_001",
    workspace_id="ws_seed_models_test",
    seed_type="url",
    original_value="https://example.com/disabled",
    enabled=False,
    status="disabled",
    enabled_at=None,
    disabled_at="2026-08-06T22:00:00+00:00",
)

check(
    disabled_seed.status
    == UniversalWebSeedStatus.DISABLED,
    "Disabled seed status is incorrect.",
)

check(
    disabled_seed.enabled is False,
    "Disabled seed must have enabled=False.",
)

check(
    disabled_seed.is_active is False,
    "Disabled seed must not be active.",
)

record(
    "disabled seed state validates correctly",
    True,
)


# ------------------------------------------------------------
# 16. ARCHIVED STATE
# ------------------------------------------------------------

archived_seed = UniversalWebSeed(
    seed_id="seed_archived_001",
    workspace_id="ws_seed_models_test",
    seed_type="domain",
    original_value="archived.example.com",
    enabled=False,
    status="archived",
    enabled_at=None,
    archived_at="2026-08-06T22:00:00+00:00",
)

check(
    archived_seed.status
    == UniversalWebSeedStatus.ARCHIVED,
    "Archived seed status is incorrect.",
)

check(
    archived_seed.is_active is False,
    "Archived seed must not be active.",
)

record(
    "archived seed state validates correctly",
    True,
)


# ------------------------------------------------------------
# 17. INVALID CORE INPUTS
# ------------------------------------------------------------

invalid_core_cases = [
    {
        "name": "empty seed_id rejected",
        "kwargs": {
            "seed_id": "",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
        },
    },
    {
        "name": "empty workspace_id rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "",
            "seed_type": "url",
            "original_value": "https://example.com",
        },
    },
    {
        "name": "empty original_value rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "",
        },
    },
    {
        "name": "invalid seed type rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "unknown",
            "original_value": "https://example.com",
        },
    },
    {
        "name": "invalid status rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "status": "unknown",
        },
    },
    {
        "name": "negative priority rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "priority": -1,
        },
    },
    {
        "name": "non-boolean enabled rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "enabled": "yes",
        },
    },
    {
        "name": "invalid metadata rejected",
        "kwargs": {
            "seed_id": "seed_test",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "metadata": "invalid",
        },
    },
]

for invalid_case in invalid_core_cases:
    try:
        UniversalWebSeed(
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
# 18. INVALID CONTROL STATES
# ------------------------------------------------------------

invalid_control_cases = [
    {
        "name": "registered disabled seed rejected",
        "kwargs": {
            "seed_id": "seed_invalid_registered",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "enabled": False,
            "status": "registered",
        },
    },
    {
        "name": "disabled enabled seed rejected",
        "kwargs": {
            "seed_id": "seed_invalid_disabled",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "enabled": True,
            "status": "disabled",
            "disabled_at": "2026-08-06T22:00:00+00:00",
        },
    },
    {
        "name": "disabled seed without timestamp rejected",
        "kwargs": {
            "seed_id": "seed_invalid_disabled_timestamp",
            "workspace_id": "ws_test",
            "seed_type": "url",
            "original_value": "https://example.com",
            "enabled": False,
            "status": "disabled",
            "disabled_at": None,
        },
    },
    {
        "name": "archived enabled seed rejected",
        "kwargs": {
            "seed_id": "seed_invalid_archived",
            "workspace_id": "ws_test",
            "seed_type": "domain",
            "original_value": "example.com",
            "enabled": True,
            "status": "archived",
            "archived_at": "2026-08-06T22:00:00+00:00",
        },
    },
    {
        "name": "archived seed without timestamp rejected",
        "kwargs": {
            "seed_id": "seed_invalid_archived_timestamp",
            "workspace_id": "ws_test",
            "seed_type": "domain",
            "original_value": "example.com",
            "enabled": False,
            "status": "archived",
            "archived_at": None,
        },
    },
]

for invalid_case in invalid_control_cases:
    try:
        UniversalWebSeed(
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
# 19. INVALID RECONSTRUCTION SOURCE
# ------------------------------------------------------------

try:
    UniversalWebSeed.from_dict(
        "invalid"
    )
except ValueError:
    record(
        "non-mapping reconstruction source rejected",
        True,
    )
else:
    raise AssertionError(
        "Non-mapping reconstruction source was accepted."
    )


# ------------------------------------------------------------
# 20. INVALID SCHEMA VERSION
# ------------------------------------------------------------

invalid_schema_payload = dict(
    url_seed_payload
)

invalid_schema_payload["schema_version"] = (
    "universal_web_seed.v999"
)

try:
    UniversalWebSeed.from_dict(
        invalid_schema_payload
    )
except ValueError:
    record(
        "unsupported schema version rejected",
        True,
    )
else:
    raise AssertionError(
        "Unsupported seed schema version was accepted."
    )


# ------------------------------------------------------------
# 21. EXPLANATION CONTRACT
# ------------------------------------------------------------

explanation = (
    explain_universal_web_seed_models_v1()
)

check(
    explanation.get("ok") is True,
    "Seed model explanation did not return ok=True.",
)

check(
    explanation.get("component")
    == "universal_web_seed_models",
    "Seed model explanation component is incorrect.",
)

check(
    explanation.get("schema_version")
    == UNIVERSAL_WEB_SEED_SCHEMA_VERSION,
    "Seed model explanation schema is incorrect.",
)

check(
    explanation.get("pipeline_stage")
    == "Universal Web Seed Registry",
    "Seed model explanation pipeline stage is incorrect.",
)

check(
    set(
        explanation.get(
            "supported_seed_types",
            [],
        )
    )
    == expected_seed_types,
    "Explanation seed types are incorrect.",
)

check(
    set(
        explanation.get(
            "supported_statuses",
            [],
        )
    )
    == expected_statuses,
    "Explanation statuses are incorrect.",
)

check(
    "seed eligibility validation"
    in explanation.get(
        "excluded_responsibilities",
        [],
    ),
    "Seed eligibility boundary is missing.",
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
    explanation.get("next_pipeline_stage")
    == "Seed Eligibility Validation",
    "Next pipeline stage is incorrect.",
)

record(
    "seed model explanation contract is correct",
    True,
)


# ------------------------------------------------------------
# 22. FINAL RESULT
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
        "UNIVERSAL WEB SEED MODELS "
        "VERIFICATION: FAIL"
    )
    raise SystemExit(1)

print("")
print(
    "UNIVERSAL WEB SEED MODELS "
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
