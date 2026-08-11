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
    build_dns_checked_seed_eligibility_result,
    hostname_from_normalized_target,
    resolve_seed_hostname,
    validate_seed_dns_resolution,
)
from backend.server.crawler.seed_models import UniversalWebSeed

checks = 0
passed = 0

def check(condition: bool, name: str) -> None:
    global checks, passed
    checks += 1
    if not condition:
        print(f"[FAIL] {name}")
        raise AssertionError(name)
    passed += 1
    print(f"[PASS] {name}")

def fake_success_resolver(host, port, family, socktype):
    assert host == "example.com"
    assert port is None
    assert family == socket.AF_UNSPEC
    assert socktype == socket.SOCK_STREAM
    return [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
        (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            6,
            "",
            ("2606:2800:220:1:248:1893:25c8:1946", 0, 0, 0),
        ),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
    ]

def fake_failure_resolver(host, port, family, socktype):
    raise socket.gaierror("simulated DNS failure")

check(
    hostname_from_normalized_target("https://Example.COM/article")
    == "example.com",
    "hostname extraction",
)

addresses = resolve_seed_hostname(
    "Example.COM.",
    resolver=fake_success_resolver,
)

check(
    addresses
    == (
        "2606:2800:220:1:248:1893:25c8:1946",
        "93.184.216.34",
    ),
    "DNS addresses are unique and deterministic",
)

dns_evidence = validate_seed_dns_resolution(
    "https://example.com/article",
    resolver=fake_success_resolver,
)

check(dns_evidence.passed is True, "successful DNS evidence passes")
check(
    dns_evidence.reason_code == SeedEligibilityReasonCode.ELIGIBLE,
    "successful DNS evidence reason",
)
check(
    dns_evidence.details["address_count"] == 2,
    "DNS evidence address count",
)

failed_evidence = validate_seed_dns_resolution(
    "https://example.com/article",
    resolver=fake_failure_resolver,
)

check(failed_evidence.passed is False, "failed DNS evidence fails")
check(
    failed_evidence.reason_code
    == SeedEligibilityReasonCode.DNS_RESOLUTION_FAILED,
    "DNS failure reason code",
)

seed = UniversalWebSeed(
    seed_id="seed_dns_success",
    workspace_id="ws_dns_test",
    seed_type="url",
    original_value="example.com/article",
)

result = build_dns_checked_seed_eligibility_result(
    seed,
    resolver=fake_success_resolver,
)

check(
    result.decision == SeedEligibilityDecision.REVIEW,
    "DNS success remains review",
)
check(
    result.reason_code == SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED,
    "DNS success requires network safety",
)
check(result.is_eligible is False, "DNS alone cannot grant eligibility")
check(result.evidence[-2].check == "dns_resolution", "DNS evidence appended")
check(
    result.evidence[-1].check == "public_network_safety_required",
    "network-safety handoff appended",
)

failed_result = build_dns_checked_seed_eligibility_result(
    seed,
    resolver=fake_failure_resolver,
)

check(
    failed_result.decision == SeedEligibilityDecision.INELIGIBLE,
    "DNS failure makes seed ineligible",
)
check(
    failed_result.reason_code
    == SeedEligibilityReasonCode.DNS_RESOLUTION_FAILED,
    "DNS failure result reason",
)
check(
    failed_result.is_eligible is False,
    "DNS failure cannot be eligible",
)

print("")
print("============================================================")
print("SEED ELIGIBILITY DNS RESOLUTION VERIFICATION")
print("============================================================")
print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks - passed}")

if checks != passed:
    raise SystemExit(1)

print("")
print("SEED ELIGIBILITY DNS RESOLUTION VERIFICATION: PASS")

