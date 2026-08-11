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
    build_network_safe_seed_eligibility_result,
    classify_seed_network_address,
    validate_seed_public_network_safety,
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
            socket.AF_INET6,
            socket.SOCK_STREAM,
            6,
            "",
            (
                "2001:4860:4860::8888",
                0,
                0,
                0,
            ),
        ),
    ]


def fake_mixed_resolver(
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
            ("127.0.0.1", 0),
        ),
    ]


public_v4 = classify_seed_network_address(
    "8.8.8.8"
)

check(
    public_v4["is_safe"] is True,
    "public IPv4 accepted",
)

public_v6 = classify_seed_network_address(
    "2001:4860:4860::8888"
)

check(
    public_v6["is_safe"] is True,
    "public IPv6 accepted",
)

loopback = classify_seed_network_address(
    "127.0.0.1"
)

check(
    loopback["is_safe"] is False
    and "loopback" in loopback["reasons"],
    "IPv4 loopback rejected",
)

private_v4 = classify_seed_network_address(
    "10.0.0.1"
)

check(
    private_v4["is_safe"] is False,
    "private IPv4 rejected",
)

link_local = classify_seed_network_address(
    "169.254.10.20"
)

check(
    link_local["is_safe"] is False
    and "link_local" in link_local["reasons"],
    "IPv4 link-local rejected",
)

unspecified = classify_seed_network_address(
    "0.0.0.0"
)

check(
    unspecified["is_safe"] is False
    and "unspecified" in unspecified["reasons"],
    "unspecified IPv4 rejected",
)

loopback_v6 = classify_seed_network_address(
    "::1"
)

check(
    loopback_v6["is_safe"] is False
    and "loopback" in loopback_v6["reasons"],
    "IPv6 loopback rejected",
)

private_v6 = classify_seed_network_address(
    "fc00::1"
)

check(
    private_v6["is_safe"] is False,
    "IPv6 unique-local rejected",
)

safe_evidence = (
    validate_seed_public_network_safety(
        [
            "8.8.8.8",
            "2001:4860:4860::8888",
        ]
    )
)

check(
    safe_evidence.passed is True,
    "all-public address set passes",
)

mixed_evidence = (
    validate_seed_public_network_safety(
        [
            "8.8.8.8",
            "127.0.0.1",
        ]
    )
)

check(
    mixed_evidence.passed is False,
    "mixed public and unsafe set fails closed",
)

check(
    mixed_evidence.reason_code
    == SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET,
    "mixed-address failure reason",
)

empty_evidence = (
    validate_seed_public_network_safety([])
)

check(
    empty_evidence.passed is False,
    "empty address set fails closed",
)

seed = UniversalWebSeed(
    seed_id="seed_network_safe",
    workspace_id="ws_network_test",
    seed_type="url",
    original_value="example.com/article",
)

safe_result = (
    build_network_safe_seed_eligibility_result(
        seed,
        resolver=fake_public_resolver,
    )
)

check(
    safe_result.decision
    == SeedEligibilityDecision.REVIEW,
    "network-safe seed remains review",
)

check(
    safe_result.reason_code
    == SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED,
    "network-safe seed requires later network checks",
)

check(
    safe_result.is_eligible is False,
    "network safety alone cannot grant eligibility",
)

check(
    safe_result.evidence[-2].check
    == "public_network_safety",
    "network-safety evidence appended",
)

check(
    safe_result.evidence[-1].check
    == "target_reachability_required",
    "target-reachability handoff appended",
)

unsafe_result = (
    build_network_safe_seed_eligibility_result(
        seed,
        resolver=fake_mixed_resolver,
    )
)

check(
    unsafe_result.decision
    == SeedEligibilityDecision.INELIGIBLE,
    "mixed DNS result makes seed ineligible",
)

check(
    unsafe_result.reason_code
    == SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET,
    "unsafe result reason code",
)

check(
    unsafe_result.is_eligible is False,
    "unsafe network target cannot be eligible",
)

print("")
print("============================================================")
print("SEED ELIGIBILITY PUBLIC-NETWORK / SSRF SAFETY VERIFICATION")
print("============================================================")
print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks - passed}")

if checks != passed:
    raise SystemExit(1)

print("")
print(
    "SEED ELIGIBILITY PUBLIC-NETWORK / SSRF SAFETY "
    "VERIFICATION: PASS"
)
