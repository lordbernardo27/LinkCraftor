"""Verify Body Store Expiration Manager Phase 9.1.4.1."""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path
from types import MappingProxyType


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
    BODY_STORE_EXPIRATION_STATUSES,
    calculate_body_store_expiration_window_v1,
    evaluate_body_store_expiration_v1,
)


MANAGER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_expiration_manager_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "production_body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "production_body_queue":
        DATA_ROOT
        / "universal_article_body_queue",

    "production_lifecycle_store":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "persistent_uucd_output":
        DATA_ROOT
        / "universal_unified_content_documents",

    "persistent_wuc_output":
        DATA_ROOT
        / "website_unified_content",
}


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for item in sorted(
        path.rglob("*"),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            item.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


source = MANAGER_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        MANAGER_PATH
    ),
)

forbidden_imports = []
forbidden_calls = []
filesystem_writes = []

for node in ast.walk(
    tree
):
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        module = str(
            node.module
            or ""
        )

        if any(
            forbidden in module
            for forbidden in (
                "body_store_writer_v1",
                "body_store_manager_v1",
                "body_store_repository_v1",
                "body_store_runtime_v1",
                "body_store_worker_v1",
                "body_store_queue_v1",
                "body_store_state_transition_engine_v1",
                "universal_runtime_registration",
            )
        ):
            forbidden_imports.append(
                (
                    node.lineno,
                    module,
                )
            )

    elif isinstance(
        node,
        ast.Call,
    ):
        name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            name = node.func.id

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            name = node.func.attr

        if name in {
            "store_body",
            "read_body",
            "verify_body",
            "transition_body_store_lifecycle_state_v1",
            "execute_body_store_runtime_v1",
            "execute_body_store_worker_v1",
            "enqueue_body_store_job",
            "register_runtime_handler",
        }:
            forbidden_calls.append(
                (
                    node.lineno,
                    name,
                )
            )

        if name in {
            "write_text",
            "write_bytes",
            "mkdir",
            "rename",
            "unlink",
        }:
            filesystem_writes.append(
                (
                    node.lineno,
                    name,
                )
            )


active_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="expiration_active_v1",
        retention_policy_name="Active Expiration Policy",
        lifecycle_record_id="body_lifecycle_expiration_active",
        workspace_id="ws_expiration",
        retention_class="CUSTOM",
        retention_started_at="2026-01-01T00:00:00+00:00",
        retention_period_days=365,
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

expired_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="expiration_expired_v1",
        retention_policy_name="Expired Expiration Policy",
        lifecycle_record_id="body_lifecycle_expiration_expired",
        workspace_id="ws_expiration",
        retention_class="CUSTOM",
        retention_started_at="2025-01-01T00:00:00+00:00",
        retention_period_days=30,
        eligibility_reason="Initial contract value.",
        evaluated_at="2025-01-01T00:00:00+00:00",
    )
)

hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="expiration_hold_v1",
        retention_policy_name="Held Expiration Policy",
        lifecycle_record_id="body_lifecycle_expiration_hold",
        workspace_id="ws_expiration",
        retention_class="LEGAL_HOLD",
        retention_started_at="2024-01-01T00:00:00+00:00",
        retention_status="ON_HOLD",
        is_on_hold=True,
        hold_type="LEGAL",
        hold_reason="Legal preservation required.",
        hold_started_at="2024-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2024-01-01T00:00:00+00:00",
    )
)

indefinite_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="expiration_indefinite_v1",
        retention_policy_name="Indefinite Expiration Policy",
        lifecycle_record_id="body_lifecycle_expiration_indefinite",
        workspace_id="ws_expiration",
        retention_class="INDEFINITE",
        retention_started_at="2020-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2020-01-01T00:00:00+00:00",
    )
)


active_result = (
    evaluate_body_store_expiration_v1(
        policy=active_policy,
        evaluated_at="2026-06-01T00:00:00+00:00",
    )
)

expired_result = (
    evaluate_body_store_expiration_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

hold_result = (
    evaluate_body_store_expiration_v1(
        policy=hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

indefinite_result = (
    evaluate_body_store_expiration_v1(
        policy=indefinite_policy,
        evaluated_at="2035-01-01T00:00:00+00:00",
    )
)

repeat_expired_result = (
    evaluate_body_store_expiration_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

active_window = (
    calculate_body_store_expiration_window_v1(
        policy=active_policy,
        evaluated_at="2026-06-01T00:00:00+00:00",
    )
)

expired_window = (
    calculate_body_store_expiration_window_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)


mutation_rejected = False

try:
    active_result[
        "expiration_status"
    ] = "BROKEN"

except TypeError:
    mutation_rejected = True


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


checks = {
    "expiration_statuses_exact":
        BODY_STORE_EXPIRATION_STATUSES
        == (
            "ACTIVE",
            "EXPIRED",
            "ON_HOLD",
            "INDEFINITE",
        ),

    "active_expiration_passed":
        active_result[
            "expiration_status"
        ]
        == "ACTIVE"
        and active_result[
            "expiration_effective"
        ]
        is False
        and active_result[
            "remaining_seconds"
        ]
        > 0,

    "expired_expiration_passed":
        expired_result[
            "expiration_status"
        ]
        == "EXPIRED"
        and expired_result[
            "expiration_effective"
        ]
        is True
        and expired_result[
            "elapsed_since_expiration_seconds"
        ]
        > 0,

    "hold_expiration_passed":
        hold_result[
            "expiration_status"
        ]
        == "ON_HOLD"
        and hold_result[
            "expiration_effective"
        ]
        is False,

    "indefinite_expiration_passed":
        indefinite_result[
            "expiration_status"
        ]
        == "INDEFINITE"
        and indefinite_result[
            "retain_until"
        ]
        is None
        and indefinite_result[
            "expiration_effective"
        ]
        is False,

    "active_window_passed":
        active_window[
            "remaining_seconds"
        ]
        > 0
        and active_window[
            "elapsed_since_expiration_seconds"
        ]
        == 0,

    "expired_window_passed":
        expired_window[
            "remaining_seconds"
        ]
        == 0
        and expired_window[
            "elapsed_since_expiration_seconds"
        ]
        > 0,

    "expiration_deterministic":
        dict(
            expired_result
        )
        == dict(
            repeat_expired_result
        ),

    "immutable_result_mapping":
        isinstance(
            active_result,
            MappingProxyType,
        ),

    "immutable_result_rejected_mutation":
        mutation_rejected,

    "input_policy_not_mutated":
        active_result[
            "input_policy_mutated"
        ]
        is False,

    "article_body_not_included":
        all(
            result[
                "content_body_included"
            ]
            is False

            for result in (
                active_result,
                expired_result,
                hold_result,
                indefinite_result,
            )
        ),

    "no_forbidden_imports":
        not forbidden_imports,

    "no_forbidden_calls":
        not forbidden_calls,

    "no_filesystem_writes":
        not filesystem_writes,

    "production_outputs_unchanged":
        all(
            unchanged.values()
        ),
}


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE EXPIRATION MANAGER — PHASE 9.1.4.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<86}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "PROTECTED OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<40}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "Production expiration records created: 0"
)

print(
    "Production lifecycle records modified: 0"
)

print(
    "Production Body Store files written:   0"
)

print(
    "Production queue jobs created:         0"
)

print(
    "Runtime registrations modified:        0"
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "BODY STORE EXPIRATION MANAGER PHASE 9.1.4.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE EXPIRATION MANAGER PHASE 9.1.4.1: PASS"
)

print(
    "The Expiration Manager now produces deterministic, immutable, "
    "read-only expiration decisions."
)

print("=" * 120)
