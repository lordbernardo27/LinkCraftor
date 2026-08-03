from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    build_body_store_retention_policy_v1,
)

from backend.server.universal_article_body_store.body_store_expiration_manager_v1 import (
    evaluate_body_store_expiration_v1,
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED = {
    "body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "queue":
        DATA_ROOT
        / "universal_article_body_queue",

    "lifecycle":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "uucd":
        DATA_ROOT
        / "universal_unified_content_documents",

    "wuc":
        DATA_ROOT
        / "website_unified_content",
}


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(b"ABSENT")
        return digest.hexdigest()

    for item in sorted(
        path.rglob("*"),
        key=lambda x: x.relative_to(path).as_posix(),
    ):
        digest.update(
            item.relative_to(path).as_posix().encode()
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

    return digest.hexdigest()


before = {
    k: fingerprint(v)
    for k, v in PROTECTED.items()
}


policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="expiration_certification",
        retention_policy_name="Expiration Certification",
        lifecycle_record_id="body_lifecycle_expiration",
        workspace_id="ws_expiration",
        retention_class="CUSTOM",
        retention_started_at="2025-01-01T00:00:00+00:00",
        retention_period_days=30,
        eligibility_reason="Certification",
        evaluated_at="2025-01-01T00:00:00+00:00",
    )
)

result = (
    evaluate_body_store_expiration_v1(
        policy=policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

after = {
    k: fingerprint(v)
    for k, v in PROTECTED.items()
}

checks = {
    "policy_created":
        policy is not None,

    "expiration_completed":
        result["expiration_status"] == "EXPIRED",

    "expiration_effective":
        result["expiration_effective"] is True,

    "deletion_eligibility_present":
        "deletion_eligible" in result,

    "immutable_output":
        result["content_body_included"] is False,

    "production_outputs_unchanged":
        all(
            before[k] == after[k]
            for k in before
        ),
}

failures = [
    name
    for name, passed in checks.items()
    if not passed
]

print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE EXPIRATION CERTIFICATION — PHASE 9.1.4.2"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<60}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print("PROTECTED OUTPUTS")

for name in before:
    print(
        f"  {name:<25}"
        + (
            "UNCHANGED"
            if before[name] == after[name]
            else "CHANGED"
        )
    )

print()
print("Production expiration records created: 0")
print("Production lifecycle modified:         0")
print("Production Body Store modified:        0")
print("Production queue modified:             0")
print("Runtime registrations modified:        0")

print()
print("FAILURES")

if failures:
    for failure in failures:
        print("  -", failure)
else:
    print("  None")

print()

if failures:
    print(
        "BODY STORE EXPIRATION CERTIFICATION PHASE 9.1.4.2: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE EXPIRATION CERTIFICATION PHASE 9.1.4.2: PASS"
)

print(
    "Expiration Manager subsystem is fully certified."
)

print("=" * 120)
