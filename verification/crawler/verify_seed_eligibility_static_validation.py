from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.server.crawler.seed_eligibility import (
    SeedEligibilityDecision,
    SeedEligibilityReasonCode,
    build_static_seed_eligibility_result,
    normalize_seed_hostname,
    normalize_static_seed_target,
    validate_static_eligibility_transition,
)

from backend.server.crawler.seed_models import (
    UniversalWebSeed,
    UniversalWebSeedStatus,
)

checks = 0
passed = 0


def check(
    condition: bool,
    name: str,
) -> None:
    global checks
    global passed

    checks += 1

    if not condition:
        print(f"[FAIL] {name}")
        raise AssertionError(name)

    passed += 1
    print(f"[PASS] {name}")


check(
    normalize_seed_hostname(
        "Example.COM."
    )
    == "example.com",
    "hostname normalization",
)

check(
    normalize_static_seed_target(
        seed_type="url",
        original_value="Example.com/article#section",
    )
    == "https://example.com/article",
    "scheme-less URL defaults to HTTPS",
)

check(
    normalize_static_seed_target(
        seed_type="url",
        original_value="HTTPS://Example.com:443/article",
    )
    == "https://example.com/article",
    "default HTTPS port removed",
)

check(
    normalize_static_seed_target(
        seed_type="domain",
        original_value="https://Example.com/path?q=1",
    )
    == "https://example.com/",
    "domain seed normalizes to host root",
)

check(
    validate_static_eligibility_transition(
        current_stage="seed_state",
        next_stage="target_extraction",
    )
    is True,
    "valid static transition",
)

invalid_transition_rejected = False

try:
    validate_static_eligibility_transition(
        current_stage="seed_state",
        next_stage="robots_validation",
    )
except ValueError:
    invalid_transition_rejected = True

check(
    invalid_transition_rejected,
    "invalid static transition rejected",
)

active_seed = UniversalWebSeed(
    seed_id="seed_static_active",
    workspace_id="ws_static_test",
    seed_type="url",
    original_value="example.com/article",
)

active_result = (
    build_static_seed_eligibility_result(
        active_seed
    )
)

check(
    active_result.decision
    == SeedEligibilityDecision.REVIEW,
    "statically valid seed remains review",
)

check(
    active_result.reason_code
    == SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED,
    "statically valid seed requires network checks",
)

check(
    active_result.normalized_target
    == "https://example.com/article",
    "normalized target preserved in result",
)

check(
    active_result.is_eligible is False,
    "static validation alone cannot grant eligibility",
)

check(
    len(active_result.evidence) == 8,
    "complete static evidence chain",
)

disabled_seed = UniversalWebSeed(
    seed_id="seed_static_disabled",
    workspace_id="ws_static_test",
    seed_type="url",
    original_value="https://example.com/",
    enabled=False,
    status=UniversalWebSeedStatus.DISABLED,
    disabled_at="2026-08-11T00:00:00+00:00",
)

disabled_result = (
    build_static_seed_eligibility_result(
        disabled_seed
    )
)

check(
    disabled_result.decision
    == SeedEligibilityDecision.INELIGIBLE,
    "disabled seed is ineligible",
)

check(
    disabled_result.reason_code
    == SeedEligibilityReasonCode.SEED_NOT_ACTIVE,
    "disabled seed reason code",
)

invalid_scheme_seed = UniversalWebSeed(
    seed_id="seed_static_ftp",
    workspace_id="ws_static_test",
    seed_type="url",
    original_value="ftp://example.com/file",
)

invalid_scheme_result = (
    build_static_seed_eligibility_result(
        invalid_scheme_seed
    )
)

check(
    invalid_scheme_result.decision
    == SeedEligibilityDecision.INELIGIBLE,
    "unsupported scheme is ineligible",
)

check(
    invalid_scheme_result.reason_code
    == SeedEligibilityReasonCode.INVALID_TARGET,
    "unsupported scheme produces invalid-target normalization failure",
)

print("")
print("============================================================")
print("STATIC SEED ELIGIBILITY VERIFICATION")
print("============================================================")
print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks - passed}")

if checks != passed:
    raise SystemExit(1)

print("")
print(
    "STATIC SEED ELIGIBILITY VERIFICATION: PASS"
)
