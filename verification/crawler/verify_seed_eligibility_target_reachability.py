from __future__ import annotations

import socket
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.server.crawler.seed_eligibility import (
    SeedEligibilityDecision,
    SeedEligibilityReasonCode,
    build_reachable_seed_eligibility_result,
    validate_seed_target_reachability,
)

from backend.server.crawler.seed_models import (
    UniversalWebSeed,
)


checks = 0
passed = 0


def check(condition: bool, name: str) -> None:
    global checks
    global passed

    checks += 1

    if not condition:
        print(f"[FAIL] {name}")
        raise AssertionError(name)

    passed += 1
    print(f"[PASS] {name}")


def fake_public_resolver(
    host,
    port,
    family,
    socktype,
):
    return [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            ("8.8.8.8", 0),
        ),
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            ("1.1.1.1", 0),
        ),
    ]


def fake_success_probe(
    normalized_target,
    *,
    address,
    timeout_seconds,
):
    return {
        "reachable": True,
        "method": "HEAD",
        "status": 200,
        "reason": "OK",
        "address": address,
        "hostname": "example.com",
        "port": 443,
        "scheme": "https",
        "request_path": "/article",
        "redirect_detected": False,
        "location": None,
        "headers": {},
        "head_fallback_used": False,
    }


def fake_redirect_probe(
    normalized_target,
    *,
    address,
    timeout_seconds,
):
    return {
        "reachable": True,
        "method": "HEAD",
        "status": 301,
        "reason": "Moved Permanently",
        "address": address,
        "hostname": "example.com",
        "port": 443,
        "scheme": "https",
        "request_path": "/article",
        "redirect_detected": True,
        "location": "https://www.example.com/article",
        "headers": {
            "location": "https://www.example.com/article",
        },
        "head_fallback_used": False,
    }


def fake_failure_probe(
    normalized_target,
    *,
    address,
    timeout_seconds,
):
    return {
        "reachable": False,
        "method": None,
        "status": None,
        "reason": None,
        "address": address,
        "redirect_detected": False,
        "location": None,
        "headers": {},
        "head_fallback_used": False,
        "error": "simulated connection failure",
    }


def first_fail_second_success_probe(
    normalized_target,
    *,
    address,
    timeout_seconds,
):
    if address == "1.1.1.1":
        return fake_failure_probe(
            normalized_target,
            address=address,
            timeout_seconds=timeout_seconds,
        )

    return fake_success_probe(
        normalized_target,
        address=address,
        timeout_seconds=timeout_seconds,
    )


empty = validate_seed_target_reachability(
    "https://example.com/article",
    addresses=[],
    probe=fake_success_probe,
)

check(
    empty.passed is False,
    "empty approved-address set fails",
)

check(
    empty.reason_code
    == SeedEligibilityReasonCode.UNREACHABLE_TARGET,
    "empty approved-address reason",
)

success = validate_seed_target_reachability(
    "https://example.com/article",
    addresses=[
        "8.8.8.8",
    ],
    probe=fake_success_probe,
)

check(
    success.passed is True,
    "reachable target passes",
)

check(
    success.reason_code
    == SeedEligibilityReasonCode.ELIGIBLE,
    "reachable evidence reason",
)

check(
    success.details["status"] == 200,
    "reachable status preserved",
)

check(
    success.details["method"] == "HEAD",
    "reachable method preserved",
)

check(
    success.details["attempt_count"] == 1,
    "single successful attempt count",
)

redirect = validate_seed_target_reachability(
    "https://example.com/article",
    addresses=[
        "8.8.8.8",
    ],
    probe=fake_redirect_probe,
)

check(
    redirect.passed is True,
    "redirect response proves reachability",
)

check(
    redirect.details["redirect_detected"] is True,
    "redirect is recorded",
)

check(
    redirect.details["location"]
    == "https://www.example.com/article",
    "redirect location preserved",
)

failed = validate_seed_target_reachability(
    "https://example.com/article",
    addresses=[
        "8.8.8.8",
        "1.1.1.1",
    ],
    probe=fake_failure_probe,
)

check(
    failed.passed is False,
    "all failed probes produce failure",
)

check(
    failed.reason_code
    == SeedEligibilityReasonCode.UNREACHABLE_TARGET,
    "unreachable reason code",
)

check(
    failed.details["attempt_count"] == 2,
    "all approved addresses attempted",
)

partial = validate_seed_target_reachability(
    "https://example.com/article",
    addresses=[
        "1.1.1.1",
        "8.8.8.8",
    ],
    probe=first_fail_second_success_probe,
)

check(
    partial.passed is True,
    "later approved address may succeed",
)

check(
    partial.details["attempt_count"] == 2,
    "reachability stops after first success",
)

seed = UniversalWebSeed(
    seed_id="seed_reachability",
    workspace_id="ws_reachability_test",
    seed_type="url",
    original_value="example.com/article",
)

result = build_reachable_seed_eligibility_result(
    seed,
    resolver=fake_public_resolver,
    probe=fake_success_probe,
)

check(
    result.decision
    == SeedEligibilityDecision.REVIEW,
    "reachable seed remains review",
)

check(
    result.reason_code
    == SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED,
    "reachable seed requires redirect safety",
)

check(
    result.is_eligible is False,
    "reachability alone cannot grant eligibility",
)

check(
    result.evidence[-2].check
    == "target_reachability",
    "reachability evidence appended",
)

check(
    result.evidence[-1].check
    == "redirect_safety_required",
    "redirect-safety handoff appended",
)

unreachable_result = (
    build_reachable_seed_eligibility_result(
        seed,
        resolver=fake_public_resolver,
        probe=fake_failure_probe,
    )
)

check(
    unreachable_result.decision
    == SeedEligibilityDecision.INELIGIBLE,
    "unreachable seed is ineligible",
)

check(
    unreachable_result.reason_code
    == SeedEligibilityReasonCode.UNREACHABLE_TARGET,
    "unreachable result reason",
)

redirect_result = (
    build_reachable_seed_eligibility_result(
        seed,
        resolver=fake_public_resolver,
        probe=fake_redirect_probe,
    )
)

check(
    redirect_result.decision
    == SeedEligibilityDecision.REVIEW,
    "redirecting reachable seed remains review",
)

check(
    redirect_result.evidence[-1].details[
        "redirect_detected"
    ]
    is True,
    "redirect handoff records detected redirect",
)

print("")
print("============================================================")
print("SEED ELIGIBILITY TARGET REACHABILITY VERIFICATION")
print("============================================================")
print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks - passed}")

if checks != passed:
    raise SystemExit(1)

print("")
print(
    "SEED ELIGIBILITY TARGET REACHABILITY "
    "VERIFICATION: PASS"
)
