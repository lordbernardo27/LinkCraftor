"""Verify the read-only Body Store Management Layer in isolation."""

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

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.universal_article_body_store.body_store_manager_v1 import (
    BodyStoreAccessError,
    BodyStoreCorruptionError,
    BodyStoreMissingError,
    body_exists,
    get_body_metadata,
    list_workspace_bodies,
    locate_body,
    read_body,
    verify_stored_body,
)


MANAGER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_manager_v1.py"
)

PRODUCTION_STORE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_article_body_store"
)


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for candidate in sorted(
        path.rglob("*"),
        key=lambda item: (
            item.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            candidate.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


production_before = fingerprint(
    PRODUCTION_STORE
)

temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_manager_test_"
    )
).resolve()

try:
    workspace_id = "ws_manager_test"

    body_root = (
        temporary_project
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store"
        / workspace_id
        / "bodies"
    )

    body_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    body_one = (
        "This is the first complete stored article body.\n\n"
        "It must be read and verified without modification."
    )

    body_two = (
        "This is the second stored body used for workspace listing."
    )

    body_one_path = (
        body_root
        / "article-one_uucd_aaaaaaaaaaaa.txt"
    )

    body_two_path = (
        body_root
        / "article-two_uucd_bbbbbbbbbbbb.txt"
    )

    body_one_path.write_text(
        body_one,
        encoding="utf-8",
        newline="",
    )

    body_two_path.write_text(
        body_two,
        encoding="utf-8",
        newline="",
    )

    body_one_ref = (
        body_one_path.relative_to(
            temporary_project
        ).as_posix()
    )

    body_two_ref = (
        body_two_path.relative_to(
            temporary_project
        ).as_posix()
    )

    expected_hash = hashlib.sha256(
        body_one.encode(
            "utf-8"
        )
    ).hexdigest()

    located = locate_body(
        project_root=temporary_project,
        workspace_id=workspace_id,
        body_ref=body_one_ref,
    )

    read_value = read_body(
        project_root=temporary_project,
        workspace_id=workspace_id,
        body_ref=body_one_ref,
    )

    verification = verify_stored_body(
        project_root=temporary_project,
        workspace_id=workspace_id,
        body_ref=body_one_ref,
        expected_content_hash=expected_hash,
        expected_body_length=len(
            body_one
        ),
        expected_body_byte_length=len(
            body_one.encode(
                "utf-8"
            )
        ),
        expected_body_word_count=len(
            body_one.split()
        ),
    )

    metadata = get_body_metadata(
        project_root=temporary_project,
        workspace_id=workspace_id,
        body_ref=body_one_ref,
    )

    listing = list_workspace_bodies(
        project_root=temporary_project,
        workspace_id=workspace_id,
        verify_each=True,
    )

    missing_ref = (
        "backend/server/data/"
        "universal_article_body_store/"
        + workspace_id
        + "/bodies/missing.txt"
    )

    missing_exists_false = (
        body_exists(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=missing_ref,
        )
        is False
    )

    missing_read_rejected = False

    try:
        read_body(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=missing_ref,
        )

    except BodyStoreMissingError:
        missing_read_rejected = True

    traversal_rejected = False

    try:
        locate_body(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                + workspace_id
                + "/bodies/../../outside.txt"
            ),
            require_exists=False,
        )

    except BodyStoreAccessError:
        traversal_rejected = True

    wrong_workspace_rejected = False

    try:
        locate_body(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                "ws_other/bodies/body.txt"
            ),
            require_exists=False,
        )

    except BodyStoreAccessError:
        wrong_workspace_rejected = True

    bad_extension_rejected = False

    try:
        locate_body(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=(
                "backend/server/data/"
                "universal_article_body_store/"
                + workspace_id
                + "/bodies/body.json"
            ),
            require_exists=False,
        )

    except BodyStoreAccessError:
        bad_extension_rejected = True

    hash_mismatch_rejected = False

    try:
        verify_stored_body(
            project_root=temporary_project,
            workspace_id=workspace_id,
            body_ref=body_one_ref,
            expected_content_hash="0" * 64,
        )

    except BodyStoreCorruptionError:
        hash_mismatch_rejected = True

    original_body_one_bytes = (
        body_one_path.read_bytes()
    )

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

    prohibited_calls = []
    runtime_imports = []
    semantic_imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
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
                "write_text",
                "write_bytes",
                "unlink",
                "remove",
                "rmtree",
                "replace",
                "rename",
            }:
                prohibited_calls.append(
                    {
                        "name":
                            name,

                        "line":
                            node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            ).casefold()

            if "runtime" in module:
                runtime_imports.append(
                    module
                )

            if any(
                term in module
                for term in (
                    "semantic",
                    "embedding",
                    "reasoning",
                )
            ):
                semantic_imports.append(
                    module
                )

    checks = {
        "manager_syntax_valid":
            True,

        "locate_body_returns_exact_path":
            located
            == body_one_path.resolve(),

        "body_exists_true":
            body_exists(
                project_root=temporary_project,
                workspace_id=workspace_id,
                body_ref=body_one_ref,
            )
            is True,

        "read_body_exact":
            read_value
            == body_one,

        "verification_status_verified":
            verification[
                "verification_status"
            ]
            == "VERIFIED",

        "verification_hash_exact":
            verification[
                "content_hash"
            ]
            == expected_hash,

        "verification_length_exact":
            verification[
                "body_length"
            ]
            == len(
                body_one
            ),

        "verification_byte_length_exact":
            verification[
                "body_byte_length"
            ]
            == len(
                body_one.encode(
                    "utf-8"
                )
            ),

        "verification_word_count_exact":
            verification[
                "body_word_count"
            ]
            == len(
                body_one.split()
            ),

        "metadata_excludes_body":
            metadata[
                "body_included"
            ]
            is False,

        "listing_finds_two_bodies":
            listing[
                "body_count"
            ]
            == 2,

        "listing_verifies_two_bodies":
            listing[
                "verified_count"
            ]
            == 2,

        "listing_contains_no_body_content":
            listing[
                "body_content_included"
            ]
            is False,

        "missing_body_exists_false":
            missing_exists_false,

        "missing_body_read_rejected":
            missing_read_rejected,

        "path_traversal_rejected":
            traversal_rejected,

        "wrong_workspace_rejected":
            wrong_workspace_rejected,

        "invalid_extension_rejected":
            bad_extension_rejected,

        "hash_mismatch_detected":
            hash_mismatch_rejected,

        "body_one_not_modified":
            body_one_path.read_bytes()
            == original_body_one_bytes,

        "no_write_or_delete_calls":
            not prohibited_calls,

        "no_runtime_imports":
            not runtime_imports,

        "no_semantic_imports":
            not semantic_imports,

        "production_store_unchanged":
            fingerprint(
                PRODUCTION_STORE
            )
            == production_before,
    }

    failures = [
        name
        for name, passed
        in checks.items()
        if passed is not True
    ]

    print()
    print("=" * 112)
    print(
        "UNIVERSAL ARTICLE BODY STORE MANAGEMENT LAYER — PHASE 1"
    )
    print("=" * 112)
    print()

    for name, passed in checks.items():
        print(
            f"{name:<66}"
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    print()
    print(
        "Bodies listed:                        "
        + str(
            listing[
                "body_count"
            ]
        )
    )

    print(
        "Bodies verified:                      "
        + str(
            listing[
                "verified_count"
            ]
        )
    )

    print(
        "Corrupted bodies:                     "
        + str(
            listing[
                "corrupted_count"
            ]
        )
    )

    print()
    print(
        "Production Body Store read:           False"
    )

    print(
        "Production Body Store modified:       False"
    )

    print(
        "Body deletion enabled:                False"
    )

    print(
        "UUCD persistence performed:           False"
    )

    print(
        "Runtime Registration created:         False"
    )

    print(
        "Worker or queue created:              False"
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
            "BODY STORE MANAGEMENT LAYER PHASE 1: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE MANAGEMENT LAYER PHASE 1: PASS"
    )

    print(
        "The read-only management layer located, read, listed, "
        "and verified isolated stored bodies without modifying them."
    )

    print(
        "No production Body Store body, persistent UUCD record, "
        "worker, queue, or Runtime Registration was created."
    )

    print("=" * 112)

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )
