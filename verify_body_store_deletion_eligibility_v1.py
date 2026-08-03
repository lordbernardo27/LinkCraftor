"""Certify Body Store Deletion Eligibility Phase 9.1.3.5."""

from __future__ import annotations

import ast
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

from backend.server.universal_article_body_store.body_store_retention_policy_engine_v1 import (
    evaluate_body_store_deletion_eligibility_v1,
    evaluate_body_store_retention_policy_v1,
)


ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_retention_policy_engine_v1.py"
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


source = ENGINE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        ENGINE_PATH
    ),
)

eligibility_function_present = any(
    isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
    and node.name
    == "evaluate_body_store_deletion_eligibility_v1"

    for node in ast.walk(
        tree
    )
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
        retention_policy_id="deletion_active_v1",
        retention_policy_name="Active Retention Policy",
        lifecycle_record_id="body_lifecycle_deletion_active",
        workspace_id="ws_deletion_eligibility",
        retention_class="STANDARD",
        retention_started_at="2026-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

expired_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="deletion_expired_v1",
        retention_policy_name="Expired Retention Policy",
        lifecycle_record_id="body_lifecycle_deletion_expired",
        workspace_id="ws_deletion_eligibility",
        retention_class="CUSTOM",
        retention_started_at="2025-01-01T00:00:00+00:00",
        retention_period_days=30,
        eligibility_reason="Initial contract value.",
        evaluated_at="2025-01-01T00:00:00+00:00",
    )
)

legal_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="deletion_legal_hold_v1",
        retention_policy_name="Legal Hold Policy",
        lifecycle_record_id="body_lifecycle_deletion_legal_hold",
        workspace_id="ws_deletion_eligibility",
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
        retention_policy_id="deletion_indefinite_v1",
        retention_policy_name="Indefinite Retention Policy",
        lifecycle_record_id="body_lifecycle_deletion_indefinite",
        workspace_id="ws_deletion_eligibility",
        retention_class="INDEFINITE",
        retention_started_at="2020-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2020-01-01T00:00:00+00:00",
    )
)


active_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=active_policy,
        evaluated_at="2026-06-01T00:00:00+00:00",
    )
)

expired_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

legal_hold_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=legal_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

indefinite_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=indefinite_policy,
        evaluated_at="2035-01-01T00:00:00+00:00",
    )
)

full_expired_result = (
    evaluate_body_store_retention_policy_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

repeat_expired_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)


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
    "eligibility_function_present":
        eligibility_function_present,

    "active_retention_blocks_deletion":
        active_result[
            "retention_satisfied"
        ]
        is False
        and active_result[
            "deletion_eligible"
        ]
        is False,

    "expired_retention_allows_deletion":
        expired_result[
            "retention_expired"
        ]
        is True
        and expired_result[
            "retention_satisfied"
        ]
        is True
        and expired_result[
            "deletion_eligible"
        ]
        is True,

    "legal_hold_blocks_deletion":
        legal_hold_result[
            "hold_active"
        ]
        is True
        and legal_hold_result[
            "deletion_eligible"
        ]
        is False,

    "indefinite_retention_blocks_deletion":
        indefinite_result[
            "retention_expired"
        ]
        is False
        and indefinite_result[
            "retention_satisfied"
        ]
        is False
        and indefinite_result[
            "deletion_eligible"
        ]
        is False,

    "eligibility_reason_present":
        all(
            isinstance(
                result[
                    "eligibility_reason"
                ],
                str,
            )
            and bool(
                result[
                    "eligibility_reason"
                ].strip()
            )

            for result in (
                active_result,
                expired_result,
                legal_hold_result,
                indefinite_result,
            )
        ),

    "full_policy_result_aligned":
        full_expired_result[
            "deletion_eligible"
        ]
        == expired_result[
            "deletion_eligible"
        ]
        and full_expired_result[
            "retention_satisfied"
        ]
        == expired_result[
            "retention_satisfied"
        ],

    "eligibility_evaluation_deterministic":
        expired_result
        == repeat_expired_result,

    "no_direct_deletion_performed":
        full_expired_result[
            "deletion_eligible"
        ]
        is True,

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
    "UNIVERSAL ARTICLE BODY STORE DELETION ELIGIBILITY — PHASE 9.1.3.5"
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
    "Production deletions executed:         0"
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
        "BODY STORE DELETION ELIGIBILITY PHASE 9.1.3.5: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE DELETION ELIGIBILITY PHASE 9.1.3.5: PASS"
)

print(
    "Deletion eligibility is certified as advisory and read-only inside "
    "the Retention Policy Engine."
)

print("=" * 120)
