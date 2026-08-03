"""Verify Body Store State Transition Engine Phase 9.1.2."""

from __future__ import annotations

import ast
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.server.universal_article_body_store.body_store_lifecycle_state_manager_v1 import (
    create_body_store_lifecycle_state_v1,
    read_body_store_lifecycle_state_v1,
)

from backend.server.universal_article_body_store.body_store_state_transition_engine_v1 import (
    BODY_STORE_LEGAL_STATE_TRANSITIONS,
    BodyStoreIllegalStateTransitionError,
    BodyStoreStateTransitionConflictError,
    BodyStoreStateTransitionError,
    can_transition_body_store_state_v1,
    list_allowed_body_store_transitions_v1,
    transition_body_store_lifecycle_state_v1,
    validate_body_store_state_transition_v1,
)


ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_state_transition_engine_v1.py"
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

forbidden_imports = []
forbidden_calls = []

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


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_state_transition_engine_"
    )
).resolve()

try:
    active_record = (
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            document_id="doc_transition_001",
            body_ref="body/doc_transition_001.txt",
            content_hash="a" * 64,
            lifecycle_state="ACTIVE",
            state_reason="Initial active state.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )
    )

    lifecycle_record_id = active_record[
        "lifecycle_record_id"
    ]

    archived_result = (
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="ARCHIVED",
            transition_reason="Archive transition verification.",
            actor_type="SYSTEM",
            actor_id="transition_verifier",
            source="phase_9_1_2",
            expected_current_state="ACTIVE",
            expected_transition_count=0,
        )
    )

    restored_result = (
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="RESTORED",
            transition_reason="Restore transition verification.",
            actor_type="SYSTEM",
            actor_id="transition_verifier",
            source="phase_9_1_2",
            expected_current_state="ARCHIVED",
            expected_transition_count=1,
        )
    )

    active_again_result = (
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="ACTIVE",
            transition_reason="Return restored record to active.",
            actor_type="SYSTEM",
            actor_id="transition_verifier",
            source="phase_9_1_2",
            expected_current_state="RESTORED",
            expected_transition_count=2,
        )
    )

    final_record = (
        read_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
        )
    )

    illegal_direct_delete_rejected = False

    try:
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="DELETED",
            transition_reason="Illegal direct deletion.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )

    except BodyStoreIllegalStateTransitionError:
        illegal_direct_delete_rejected = True

    stale_state_rejected = False

    try:
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="RETAINED",
            transition_reason="Stale-state verification.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
            expected_current_state="ARCHIVED",
        )

    except BodyStoreStateTransitionConflictError:
        stale_state_rejected = True

    stale_count_rejected = False

    try:
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="RETAINED",
            transition_reason="Stale-count verification.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
            expected_transition_count=1,
        )

    except BodyStoreStateTransitionConflictError:
        stale_count_rejected = True

    body_content_rejected = False

    try:
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=lifecycle_record_id,
            target_state="RETAINED",
            transition_reason="Forbidden content verification.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
            metadata={
                "content_body":
                    "Article content must never enter transition metadata.",
            },
        )

    except BodyStoreStateTransitionError:
        body_content_rejected = True

    deletion_record = (
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            document_id="doc_transition_002",
            body_ref="body/doc_transition_002.txt",
            content_hash="b" * 64,
            lifecycle_state="ACTIVE",
            state_reason="Deletion path initial state.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )
    )

    pending_result = (
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=deletion_record[
                "lifecycle_record_id"
            ],
            target_state="PENDING_DELETION",
            transition_reason="Approved deletion path.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )
    )

    deleted_result = (
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=deletion_record[
                "lifecycle_record_id"
            ],
            target_state="DELETED",
            transition_reason="Terminal-state verification.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )
    )

    deleted_terminal_rejected = False

    try:
        transition_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_transition",
            lifecycle_record_id=deletion_record[
                "lifecycle_record_id"
            ],
            target_state="RESTORED",
            transition_reason="Illegal deleted-state restoration.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_2",
        )

    except BodyStoreIllegalStateTransitionError:
        deleted_terminal_rejected = True

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
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
    "transition_map_complete":
        set(
            BODY_STORE_LEGAL_STATE_TRANSITIONS
        )
        == {
            "ACTIVE",
            "SUPERSEDED",
            "RETAINED",
            "ARCHIVED",
            "QUARANTINED",
            "PENDING_DELETION",
            "DELETED",
            "RESTORED",
        },

    "deleted_state_terminal":
        BODY_STORE_LEGAL_STATE_TRANSITIONS[
            "DELETED"
        ]
        == (),

    "transition_query_passed":
        can_transition_body_store_state_v1(
            current_state="ACTIVE",
            target_state="ARCHIVED",
        )
        is True,

    "invalid_transition_query_passed":
        can_transition_body_store_state_v1(
            current_state="ACTIVE",
            target_state="DELETED",
        )
        is False,

    "allowed_transition_listing_passed":
        "RESTORED"
        in list_allowed_body_store_transitions_v1(
            "ARCHIVED"
        ),

    "transition_validation_passed":
        validate_body_store_state_transition_v1(
            current_state="ARCHIVED",
            target_state="RESTORED",
        )[
            "allowed"
        ]
        is True,

    "active_to_archived_passed":
        archived_result[
            "record"
        ][
            "lifecycle_state"
        ]
        == "ARCHIVED",

    "archived_to_restored_passed":
        restored_result[
            "record"
        ][
            "lifecycle_state"
        ]
        == "RESTORED",

    "restored_to_active_passed":
        active_again_result[
            "record"
        ][
            "lifecycle_state"
        ]
        == "ACTIVE",

    "transition_count_incremented":
        final_record[
            "transition_count"
        ]
        == 3,

    "previous_state_preserved":
        final_record[
            "previous_state"
        ]
        == "RESTORED",

    "last_transition_preserved":
        final_record[
            "last_transition"
        ][
            "to_state"
        ]
        == "ACTIVE",

    "identity_preserved":
        final_record[
            "lifecycle_record_id"
        ]
        == lifecycle_record_id
        and final_record[
            "content_hash"
        ]
        == "a" * 64,

    "illegal_direct_delete_rejected":
        illegal_direct_delete_rejected,

    "stale_current_state_rejected":
        stale_state_rejected,

    "stale_transition_count_rejected":
        stale_count_rejected,

    "article_body_content_rejected":
        body_content_rejected,

    "pending_deletion_path_passed":
        pending_result[
            "record"
        ][
            "lifecycle_state"
        ]
        == "PENDING_DELETION",

    "deleted_transition_passed":
        deleted_result[
            "record"
        ][
            "lifecycle_state"
        ]
        == "DELETED",

    "deleted_terminal_transition_rejected":
        deleted_terminal_rejected,

    "no_forbidden_layer_imports":
        not forbidden_imports,

    "no_forbidden_layer_calls":
        not forbidden_calls,

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
    "UNIVERSAL ARTICLE BODY STORE STATE TRANSITION ENGINE — PHASE 9.1.2"
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
    "Canonical legal transitions:"
)

for state, targets in (
    BODY_STORE_LEGAL_STATE_TRANSITIONS.items()
):
    rendered_targets = (
        ", ".join(
            targets
        )
        if targets
        else "<TERMINAL>"
    )

    print(
        "  "
        + f"{state:<20}"
        + " -> "
        + rendered_targets
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
    "Production lifecycle transitions applied: 0"
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
        "BODY STORE STATE TRANSITION ENGINE PHASE 9.1.2: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE STATE TRANSITION ENGINE PHASE 9.1.2: PASS"
)

print(
    "The State Transition Engine now validates and atomically applies "
    "legal lifecycle-state changes while preserving immutable body identity "
    "and rejecting stale, illegal, and body-content-bearing transitions."
)

print("=" * 120)
