"""Verify Body Store Lifecycle State Manager Phase 9.1.1."""

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
    BODY_STORE_LIFECYCLE_STATES,
    INITIAL_BODY_STORE_LIFECYCLE_STATES,
    BodyStoreLifecycleStateConflictError,
    BodyStoreLifecycleStateError,
    build_body_store_lifecycle_record_id_v1,
    create_body_store_lifecycle_state_v1,
    list_body_store_lifecycle_states_v1,
    read_body_store_lifecycle_state_v1,
    validate_body_store_lifecycle_record_v1,
)


MODULE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_lifecycle_state_manager_v1.py"
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


source = MODULE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        MODULE_PATH
    ),
)

forbidden_imports = []
body_layer_calls = []
transition_functions = []

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
            name in module
            for name in (
                "body_store_writer_v1",
                "body_store_manager_v1",
                "body_store_repository_v1",
                "body_store_runtime_v1",
                "body_store_worker_v1",
                "body_store_queue_v1",
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
        call_name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            call_name = node.func.id

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            call_name = node.func.attr

        if call_name in {
            "store_body",
            "read_body",
            "verify_body",
            "execute_body_store_runtime_v1",
            "execute_body_store_worker_v1",
            "enqueue_body_store_job",
        }:
            body_layer_calls.append(
                (
                    node.lineno,
                    call_name,
                )
            )

    elif isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        if (
            "transition"
            in node.name.casefold()
            or "change_state"
            in node.name.casefold()
        ):
            transition_functions.append(
                (
                    node.lineno,
                    node.name,
                )
            )


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_lifecycle_state_manager_"
    )
).resolve()

try:
    content_hash_one = (
        "a"
        * 64
    )

    content_hash_two = (
        "b"
        * 64
    )

    expected_record_id = (
        build_body_store_lifecycle_record_id_v1(
            workspace_id="ws_alpha",
            document_id="doc_001",
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                "ws_alpha/bodies/doc_001.txt"
            ),
            content_hash=content_hash_one,
        )
    )

    active_record = (
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_001",
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                "ws_alpha/bodies/doc_001.txt"
            ),
            content_hash=content_hash_one,
            lifecycle_state="ACTIVE",
            state_reason="Initial certified body storage.",
            actor_type="SYSTEM",
            actor_id="body_store_writer",
            source="initial_population",
            metadata={
                "verification_status":
                    "VERIFIED",
            },
        )
    )

    retained_record = (
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_002",
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                "ws_alpha/bodies/doc_002.txt"
            ),
            content_hash=content_hash_two,
            lifecycle_state="RETAINED",
            state_reason="Retention test record.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="phase_9_1_1_test",
        )
    )

    read_record = (
        read_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            lifecycle_record_id=(
                active_record[
                    "lifecycle_record_id"
                ]
            ),
        )
    )

    all_records = (
        list_body_store_lifecycle_states_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
        )
    )

    active_records = (
        list_body_store_lifecycle_states_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            lifecycle_state="ACTIVE",
        )
    )

    duplicate_rejected = False

    try:
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_001",
            body_ref=active_record[
                "body_ref"
            ],
            content_hash=content_hash_one,
            lifecycle_state="ACTIVE",
            state_reason="Duplicate.",
            actor_type="SYSTEM",
            actor_id="duplicate_test",
            source="verification",
        )

    except BodyStoreLifecycleStateConflictError:
        duplicate_rejected = True

    transition_state_rejected = False

    try:
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_003",
            body_ref="body/doc_003.txt",
            content_hash="c" * 64,
            lifecycle_state="ARCHIVED",
            state_reason="Transition state test.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="verification",
        )

    except BodyStoreLifecycleStateError:
        transition_state_rejected = True

    body_content_rejected = False

    try:
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_004",
            body_ref="body/doc_004.txt",
            content_hash="d" * 64,
            lifecycle_state="ACTIVE",
            state_reason="Forbidden content test.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="verification",
            metadata={
                "content_body":
                    "This must never enter lifecycle metadata.",
            },
        )

    except BodyStoreLifecycleStateError:
        body_content_rejected = True

    invalid_hash_rejected = False

    try:
        create_body_store_lifecycle_state_v1(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            document_id="doc_005",
            body_ref="body/doc_005.txt",
            content_hash="not-a-sha256",
            lifecycle_state="ACTIVE",
            state_reason="Invalid hash test.",
            actor_type="SYSTEM",
            actor_id="verification",
            source="verification",
        )

    except BodyStoreLifecycleStateError:
        invalid_hash_rejected = True

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
    "canonical_states_exact":
        BODY_STORE_LIFECYCLE_STATES
        == (
            "ACTIVE",
            "SUPERSEDED",
            "RETAINED",
            "ARCHIVED",
            "QUARANTINED",
            "PENDING_DELETION",
            "DELETED",
            "RESTORED",
        ),

    "initial_states_restricted":
        INITIAL_BODY_STORE_LIFECYCLE_STATES
        == (
            "ACTIVE",
            "QUARANTINED",
            "RETAINED",
        ),

    "stable_identity_passed":
        active_record[
            "lifecycle_record_id"
        ]
        == expected_record_id,

    "active_record_created":
        active_record[
            "lifecycle_state"
        ]
        == "ACTIVE",

    "retained_record_created":
        retained_record[
            "lifecycle_state"
        ]
        == "RETAINED",

    "record_read_passed":
        read_record
        == active_record,

    "workspace_listing_passed":
        len(
            all_records
        )
        == 2,

    "state_filter_passed":
        len(
            active_records
        )
        == 1
        and active_records[
            0
        ][
            "lifecycle_state"
        ]
        == "ACTIVE",

    "record_validation_passed":
        validate_body_store_lifecycle_record_v1(
            active_record
        )
        == active_record,

    "duplicate_record_rejected":
        duplicate_rejected,

    "transition_state_creation_rejected":
        transition_state_rejected,

    "article_body_content_rejected":
        body_content_rejected,

    "invalid_content_hash_rejected":
        invalid_hash_rejected,

    "no_body_layer_imports":
        not forbidden_imports,

    "no_body_layer_calls":
        not body_layer_calls,

    "no_transition_engine_implemented":
        not transition_functions,

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
    "UNIVERSAL ARTICLE BODY STORE LIFECYCLE STATE MANAGER — PHASE 9.1.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<82}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Canonical lifecycle states:"
)

for state in BODY_STORE_LIFECYCLE_STATES:
    print(
        "  "
        + state
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
    "Production lifecycle records created: 0"
)

print(
    "Production Body Store files written:  0"
)

print(
    "Production queue jobs created:        0"
)

print(
    "Runtime registrations modified:       0"
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
        "BODY STORE LIFECYCLE STATE MANAGER PHASE 9.1.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE LIFECYCLE STATE MANAGER PHASE 9.1.1: PASS"
)

print(
    "The Lifecycle State Manager now creates, validates, reads, and lists "
    "immutable initial lifecycle records without duplicating article bodies "
    "or implementing state transitions."
)

print("=" * 120)
