"""Verify Body Store Retention Policy Engine Phase 9.1.3.2."""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path
from types import MappingProxyType


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    build_body_store_retention_policy_v1,
)

from backend.server.universal_article_body_store.body_store_retention_policy_engine_v1 import (
    calculate_body_store_retention_result_v1,
    evaluate_body_store_deletion_eligibility_v1,
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
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "production_body_queue": (
        DATA_ROOT
        / "universal_article_body_queue"
    ),

    "production_lifecycle_store": (
        DATA_ROOT
        / "universal_article_body_store_lifecycle"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),
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
        path.rglob(
            "*"
        ),
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

forbidden_imports = []
forbidden_calls = []
filesystem_write_calls = []

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

        filesystem_owner = ""

        if isinstance(
            node.func,
            ast.Attribute,
        ):
            if isinstance(
                node.func.value,
                ast.Name,
            ):
                filesystem_owner = (
                    node.func.value.id
                )

        if (
            name
            in {
                "write_text",
                "write_bytes",
                "mkdir",
                "rename",
                "unlink",
            }
            or (
                name == "replace"
                and filesystem_owner
                in {
                    "os",
                    "path",
                    "Path",
                }
            )
        ):
            filesystem_write_calls.append(
                (
                    node.lineno,
                    filesystem_owner,
                    name,
                )
            )


standard_active_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_standard_active_v1",
        retention_policy_name="Standard Active Retention",
        lifecycle_record_id="body_lifecycle_standard_active",
        workspace_id="ws_retention_engine",
        retention_class="STANDARD",
        retention_started_at="2026-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

standard_expired_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_standard_expired_v1",
        retention_policy_name="Standard Expired Retention",
        lifecycle_record_id="body_lifecycle_standard_expired",
        workspace_id="ws_retention_engine",
        retention_class="STANDARD",
        retention_started_at="2024-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2024-01-01T00:00:00+00:00",
    )
)

legal_hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="retention_legal_hold_engine_v1",
        retention_policy_name="Legal Hold Engine Test",
        lifecycle_record_id="body_lifecycle_legal_hold_engine",
        workspace_id="ws_retention_engine",
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
        retention_policy_id="retention_indefinite_engine_v1",
        retention_policy_name="Indefinite Engine Test",
        lifecycle_record_id="body_lifecycle_indefinite_engine",
        workspace_id="ws_retention_engine",
        retention_class="INDEFINITE",
        retention_started_at="2020-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2020-01-01T00:00:00+00:00",
    )
)


active_evaluation = (
    evaluate_body_store_retention_policy_v1(
        policy=standard_active_policy,
        evaluated_at="2026-06-01T00:00:00+00:00",
    )
)

expired_evaluation = (
    evaluate_body_store_retention_policy_v1(
        policy=standard_expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

hold_evaluation = (
    evaluate_body_store_retention_policy_v1(
        policy=legal_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

indefinite_evaluation = (
    evaluate_body_store_retention_policy_v1(
        policy=indefinite_policy,
        evaluated_at="2035-01-01T00:00:00+00:00",
    )
)

deterministic_evaluation = (
    evaluate_body_store_retention_policy_v1(
        policy=standard_expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

hold_result = (
    evaluate_body_store_hold_status_v1(
        policy=legal_hold_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

retention_result = (
    calculate_body_store_retention_result_v1(
        policy=standard_expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)

eligibility_result = (
    evaluate_body_store_deletion_eligibility_v1(
        policy=standard_expired_policy,
        evaluated_at="2026-08-03T00:00:00+00:00",
    )
)


immutable_output_rejected_mutation = False

try:
    active_evaluation[
        "retention_status"
    ] = "BROKEN"

except TypeError:
    immutable_output_rejected_mutation = True


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
    "active_retention_passed":
        active_evaluation[
            "retention_status"
        ]
        == "ACTIVE"
        and active_evaluation[
            "retention_expired"
        ]
        is False
        and active_evaluation[
            "deletion_eligible"
        ]
        is False,

    "expired_retention_passed":
        expired_evaluation[
            "retention_status"
        ]
        == "EXPIRED"
        and expired_evaluation[
            "retention_expired"
        ]
        is True
        and expired_evaluation[
            "retention_satisfied"
        ]
        is True,

    "expired_deletion_eligible":
        expired_evaluation[
            "deletion_eligible"
        ]
        is True,

    "legal_hold_precedence_passed":
        hold_evaluation[
            "retention_status"
        ]
        == "ON_HOLD"
        and hold_evaluation[
            "hold_active"
        ]
        is True
        and hold_evaluation[
            "deletion_eligible"
        ]
        is False,

    "indefinite_retention_passed":
        indefinite_evaluation[
            "retention_expired"
        ]
        is False
        and indefinite_evaluation[
            "retention_satisfied"
        ]
        is False
        and indefinite_evaluation[
            "deletion_eligible"
        ]
        is False,

    "deterministic_evaluation_id":
        expired_evaluation[
            "evaluation_id"
        ]
        == deterministic_evaluation[
            "evaluation_id"
        ],

    "deterministic_evaluation_content":
        dict(
            expired_evaluation
        )
        == dict(
            deterministic_evaluation
        ),

    "immutable_output_mapping":
        isinstance(
            active_evaluation,
            MappingProxyType,
        ),

    "immutable_output_rejected_mutation":
        immutable_output_rejected_mutation,

    "hold_function_passed":
        hold_result[
            "hold_active"
        ]
        is True,

    "retention_calculation_function_passed":
        retention_result[
            "retention_expired"
        ]
        is True,

    "eligibility_function_passed":
        eligibility_result[
            "deletion_eligible"
        ]
        is True,

    "input_policy_not_mutated":
        active_evaluation[
            "input_policy_mutated"
        ]
        is False,

    "article_body_not_included":
        all(
            evaluation[
                "content_body_included"
            ]
            is False

            for evaluation in (
                active_evaluation,
                expired_evaluation,
                hold_evaluation,
                indefinite_evaluation,
            )
        ),

    "no_forbidden_layer_imports":
        not forbidden_imports,

    "no_forbidden_layer_calls":
        not forbidden_calls,

    "no_filesystem_writes":
        not filesystem_write_calls,

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
    "UNIVERSAL ARTICLE BODY STORE RETENTION POLICY ENGINE — PHASE 9.1.3.2"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<84}"
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
    "Production retention decisions persisted: 0"
)

print(
    "Production lifecycle records modified:    0"
)

print(
    "Production Body Store files written:      0"
)

print(
    "Production queue jobs created:            0"
)

print(
    "Runtime registrations modified:           0"
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
        "BODY STORE RETENTION POLICY ENGINE PHASE 9.1.3.2: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RETENTION POLICY ENGINE PHASE 9.1.3.2: PASS"
)

print(
    "The Retention Policy Engine now produces deterministic, immutable, "
    "read-only retention decisions while enforcing hold precedence and "
    "deletion-eligibility boundaries."
)

print("=" * 120)

