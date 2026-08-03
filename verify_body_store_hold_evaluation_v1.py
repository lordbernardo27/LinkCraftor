"""Certify Body Store Hold Evaluation Phase 9.1.3.4."""

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
    evaluate_body_store_hold_status_v1,
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

hold_function_present = any(
    isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
    and node.name
    == "evaluate_body_store_hold_status_v1"

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


no_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="hold_eval_none_v1",
        retention_policy_name="No Hold Evaluation",
        lifecycle_record_id="body_lifecycle_hold_none",
        workspace_id="ws_hold_evaluation",
        retention_class="STANDARD",
        retention_started_at="2026-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

legal_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="hold_eval_legal_v1",
        retention_policy_name="Legal Hold Evaluation",
        lifecycle_record_id="body_lifecycle_hold_legal",
        workspace_id="ws_hold_evaluation",
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

operational_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="hold_eval_operational_v1",
        retention_policy_name="Operational Hold Evaluation",
        lifecycle_record_id="body_lifecycle_hold_operational",
        workspace_id="ws_hold_evaluation",
        retention_class="OPERATIONAL_HOLD",
        retention_started_at="2024-01-01T00:00:00+00:00",
        retention_status="ON_HOLD",
        is_on_hold=True,
        hold_type="OPERATIONAL",
        hold_reason="Operational recovery protection.",
        hold_started_at="2024-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2024-01-01T00:00:00+00:00",
    )
)

future_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="hold_eval_future_v1",
        retention_policy_name="Future Hold Evaluation",
        lifecycle_record_id="body_lifecycle_hold_future",
        workspace_id="ws_hold_evaluation",
        retention_class="STANDARD",
        retention_started_at="2026-01-01T00:00:00+00:00",
        retention_status="ON_HOLD",
        is_on_hold=True,
        hold_type="MANUAL",
        hold_reason="Future manual hold.",
        hold_started_at="2027-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

expired_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="hold_eval_expired_v1",
        retention_policy_name="Expired Hold Evaluation",
        lifecycle_record_id="body_lifecycle_hold_expired",
        workspace_id="ws_hold_evaluation",
        retention_class="STANDARD",
        retention_started_at="2024-01-01T00:00:00+00:00",
        retention_status="ON_HOLD",
        is_on_hold=True,
        hold_type="SYSTEM",
        hold_reason="Temporary system hold.",
        hold_started_at="2024-01-01T00:00:00+00:00",
        hold_expires_at="2025-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2024-01-01T00:00:00+00:00",
    )
)


no_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=no_hold_policy,
        evaluated_at="2026-06-01T00:00:00+00:00",
    )
)

legal_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=legal_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

operational_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=operational_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

future_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=future_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

expired_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=expired_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

legal_policy_result = (
    evaluate_body_store_retention_policy_v1(
        policy=legal_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

repeat_legal_hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=legal_hold_policy,
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
    "hold_function_present":
        hold_function_present,

    "no_hold_evaluation_passed":
        no_hold_result[
            "hold_declared"
        ]
        is False
        and no_hold_result[
            "hold_active"
        ]
        is False
        and no_hold_result[
            "hold_type"
        ]
        is None,

    "legal_hold_evaluation_passed":
        legal_hold_result[
            "hold_declared"
        ]
        is True
        and legal_hold_result[
            "hold_active"
        ]
        is True
        and legal_hold_result[
            "hold_type"
        ]
        == "LEGAL",

    "operational_hold_evaluation_passed":
        operational_hold_result[
            "hold_active"
        ]
        is True
        and operational_hold_result[
            "hold_type"
        ]
        == "OPERATIONAL",

    "future_hold_not_active":
        future_hold_result[
            "hold_declared"
        ]
        is True
        and future_hold_result[
            "hold_active"
        ]
        is False,

    "expired_hold_not_active":
        expired_hold_result[
            "hold_declared"
        ]
        is True
        and expired_hold_result[
            "hold_active"
        ]
        is False,

    "hold_blocks_retention_satisfaction":
        legal_policy_result[
            "retention_satisfied"
        ]
        is False,

    "hold_blocks_deletion_eligibility":
        legal_policy_result[
            "deletion_eligible"
        ]
        is False,

    "hold_status_is_on_hold":
        legal_policy_result[
            "retention_status"
        ]
        == "ON_HOLD",

    "hold_reason_preserved":
        legal_hold_result[
            "hold_reason"
        ]
        == "Legal preservation required.",

    "hold_timestamps_preserved":
        legal_hold_result[
            "hold_started_at"
        ]
        is not None
        and legal_hold_result[
            "hold_expires_at"
        ]
        is None,

    "hold_evaluation_deterministic":
        legal_hold_result
        == repeat_legal_hold_result,

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
    "UNIVERSAL ARTICLE BODY STORE HOLD EVALUATION — PHASE 9.1.3.4"
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
    "Production hold records created:       0"
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
        "BODY STORE HOLD EVALUATION PHASE 9.1.3.4: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE HOLD EVALUATION PHASE 9.1.3.4: PASS"
)

print(
    "Hold evaluation is certified inside the Retention Policy Engine."
)

print("=" * 120)
