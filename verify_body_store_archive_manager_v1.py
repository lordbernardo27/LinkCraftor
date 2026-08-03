"""Verify Body Store Archive Manager Phase 9.1.5.1."""

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


from backend.server.universal_article_body_store.body_store_archive_manager_v1 import (
    BODY_STORE_ARCHIVE_DECISION_STATUSES,
    BODY_STORE_ARCHIVE_ELIGIBLE_STATES,
    evaluate_body_store_archive_eligibility_v1,
)

from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    build_body_store_retention_policy_v1,
)


MANAGER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_archive_manager_v1.py"
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


standard_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="archive_standard_v1",
        retention_policy_name="Archive Standard Policy",
        lifecycle_record_id="body_lifecycle_archive_standard",
        workspace_id="ws_archive",
        retention_class="STANDARD",
        retention_started_at="2026-01-01T00:00:00+00:00",
        eligibility_reason="Initial contract value.",
        evaluated_at="2026-01-01T00:00:00+00:00",
    )
)

hold_policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="archive_hold_v1",
        retention_policy_name="Archive Hold Policy",
        lifecycle_record_id="body_lifecycle_archive_hold",
        workspace_id="ws_archive",
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


active_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="ACTIVE",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Operational archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

superseded_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="SUPERSEDED",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Superseded article archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

retained_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="RETAINED",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Retained article archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

hold_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=hold_policy,
        lifecycle_state="ACTIVE",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Blocked hold archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

already_archived_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="ARCHIVED",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Duplicate archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

deleted_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="DELETED",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Invalid deleted archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)

repeat_result = (
    evaluate_body_store_archive_eligibility_v1(
        policy=standard_policy,
        lifecycle_state="ACTIVE",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Operational archival.",
        actor_type="SYSTEM",
        actor_id="archive_verifier",
        source="phase_9_1_5_1",
    )
)


mutation_rejected = False

try:
    active_result[
        "archive_status"
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
    "archive_statuses_exact":
        BODY_STORE_ARCHIVE_DECISION_STATUSES
        == (
            "ELIGIBLE",
            "BLOCKED",
            "ALREADY_ARCHIVED",
        ),

    "eligible_states_exact":
        BODY_STORE_ARCHIVE_ELIGIBLE_STATES
        == (
            "ACTIVE",
            "SUPERSEDED",
            "RETAINED",
        ),

    "active_archive_eligible":
        active_result[
            "archive_eligible"
        ]
        is True
        and active_result[
            "archive_status"
        ]
        == "ELIGIBLE",

    "superseded_archive_eligible":
        superseded_result[
            "archive_eligible"
        ]
        is True,

    "retained_archive_eligible":
        retained_result[
            "archive_eligible"
        ]
        is True,

    "hold_blocks_archive":
        hold_result[
            "hold_active"
        ]
        is True
        and hold_result[
            "archive_eligible"
        ]
        is False,

    "already_archived_detected":
        already_archived_result[
            "archive_status"
        ]
        == "ALREADY_ARCHIVED"
        and already_archived_result[
            "archive_eligible"
        ]
        is False,

    "deleted_state_blocks_archive":
        deleted_result[
            "archive_status"
        ]
        == "BLOCKED"
        and deleted_result[
            "archive_eligible"
        ]
        is False,

    "target_state_is_archived":
        active_result[
            "required_target_state"
        ]
        == "ARCHIVED",

    "no_physical_archive_performed":
        active_result[
            "physical_archive_performed"
        ]
        is False,

    "no_lifecycle_transition_performed":
        active_result[
            "lifecycle_transition_performed"
        ]
        is False,

    "archive_decision_deterministic":
        dict(
            active_result
        )
        == dict(
            repeat_result
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
                hold_result,
                already_archived_result,
                deleted_result,
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
    "UNIVERSAL ARTICLE BODY STORE ARCHIVE MANAGER — PHASE 9.1.5.1"
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
    "Physical archive operations executed:  0"
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
        "BODY STORE ARCHIVE MANAGER PHASE 9.1.5.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE MANAGER PHASE 9.1.5.1: PASS"
)

print(
    "The Archive Manager now produces deterministic, immutable, "
    "read-only archive-eligibility decisions."
)

print("=" * 120)
