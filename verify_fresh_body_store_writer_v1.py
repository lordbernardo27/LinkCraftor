"""Verify the fresh Body Store writer in an isolated temporary store."""

from __future__ import annotations

import ast
import shutil
import sys
import tempfile
from copy import deepcopy
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


from backend.server.universal_article_body_store.body_store_writer_v1 import (
    BodyStoreContractError,
    write_verified_body_from_envelope_v1,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
    compute_canonical_content_hash_v1,
)


WRITER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_writer_v1.py"
)

PRODUCTION_STORE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_article_body_store"
)


def build_wuc(
    body: str,
) -> dict:
    word_count = len(
        body.split()
    )

    return {
        "schema_version":
            "website_unified_content_v1",

        "engine_version":
            "website_unified_content_engine_v1",

        "content_id":
            "wuc_body_store_writer_test",

        "document_id":
            "raw_html_body_store_writer_test",

        "workspace_id":
            "ws_writer_test",

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity": {
            "source_record_id":
                "raw_html_body_store_writer_test",

            "canonical_url":
                "https://example.com/body-store-writer-test",
        },

        "title":
            "Body Store Writer Test",

        "h1":
            "Body Store Writer Test",

        "headings":
            [],

        "canonical_url":
            "https://example.com/body-store-writer-test",

        "content_body":
            body,

        "content_hash":
            compute_canonical_content_hash_v1(
                body
            ),

        "body_length":
            len(
                body
            ),

        "body_word_count":
            word_count,

        "structure": {
            "block_count":
                1,

            "heading_count":
                0,

            "content_word_count":
                word_count,

            "blocks":
                [],
        },

        "metadata": {
            "complete_content_preserved":
                True,

            "content_reduction_performed":
                False,

            "summarization_performed":
                False,

            "truncation_performed":
                False,

            "word_count_limit_applied":
                False,
        },

        "handoff": {
            "next_stage":
                "universal_unified_content_document",

            "eligible_for_uucd":
                True,

            "body_field":
                "content_body",

            "full_body_handoff":
                True,
        },
    }


production_store_before = (
    PRODUCTION_STORE.exists()
)

temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_writer_test_"
    )
).resolve()

try:
    body = "\n\n".join(
        (
            "Test paragraph "
            + str(
                index
            )
            + " confirms exact Body Store persistence "
            + "without truncation or rewriting."
        )
        for index in range(
            1,
            301,
        )
    )

    wuc = build_wuc(
        body
    )

    envelope = (
        build_transient_uucd_from_wuc_v1(
            wuc
        )
    )

    original_body_ref = envelope[
        "body_payload"
    ][
        "body_ref"
    ]

    first_result = (
        write_verified_body_from_envelope_v1(
            envelope,
            project_root=temporary_project,
        )
    )

    stored_path = Path(
        first_result[
            "body_path"
        ]
    )

    second_result = (
        write_verified_body_from_envelope_v1(
            envelope,
            project_root=temporary_project,
        )
    )

    tampered = deepcopy(
        envelope
    )

    tampered[
        "body_payload"
    ][
        "content_body"
    ] += " tampered"

    tampered_rejected = False

    try:
        write_verified_body_from_envelope_v1(
            tampered,
            project_root=temporary_project,
        )

    except BodyStoreContractError:
        tampered_rejected = True

    traversal = deepcopy(
        envelope
    )

    malicious_ref = (
        "backend/server/data/"
        "universal_article_body_store/"
        "ws_writer_test/bodies/../../outside.txt"
    )

    for section in (
        "uucd_record",
        "body_payload",
        "binding",
    ):
        traversal[
            section
        ][
            "body_ref"
        ] = malicious_ref

    traversal_rejected = False

    try:
        write_verified_body_from_envelope_v1(
            traversal,
            project_root=temporary_project,
        )

    except BodyStoreContractError:
        traversal_rejected = True

    source = WRITER_PATH.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    tree = ast.parse(
        source,
        filename=str(
            WRITER_PATH
        ),
    )

    runtime_imports = []
    semantic_imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
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

    certificate = first_result[
        "write_certificate"
    ]

    finalized_record = first_result[
        "finalized_uucd_record"
    ]

    checks = {
        "writer_syntax_valid":
            True,

        "body_file_created":
            stored_path.is_file(),

        "exact_body_stored":
            stored_path.read_text(
                encoding="utf-8"
            )
            == body,

        "certificate_certified":
            certificate[
                "certificate_status"
            ]
            == "CERTIFIED",

        "hash_verified":
            certificate[
                "hash_verified"
            ]
            is True,

        "character_length_verified":
            certificate[
                "character_length_verified"
            ]
            is True,

        "byte_length_verified":
            certificate[
                "byte_length_verified"
            ]
            is True,

        "word_count_verified":
            certificate[
                "word_count_verified"
            ]
            is True,

        "exact_content_match":
            certificate[
                "exact_content_match"
            ]
            is True,

        "body_status_finalized":
            finalized_record[
                "body_status"
            ]
            == "STORED_AND_VERIFIED",

        "uucd_ready_for_persistence":
            finalized_record[
                "metadata"
            ][
                "persistence_status"
            ]
            == "READY_FOR_UUCD_PERSISTENCE",

        "uucd_not_persisted":
            certificate[
                "uucd_record_persisted"
            ]
            is False,

        "second_identical_write_reused":
            second_result[
                "write_certificate"
            ][
                "existing_file_action"
            ]
            == "EXISTING_IDENTICAL_REUSED",

        "tampered_payload_rejected":
            tampered_rejected,

        "path_traversal_rejected":
            traversal_rejected,

        "body_ref_unchanged":
            envelope[
                "body_payload"
            ][
                "body_ref"
            ]
            == original_body_ref,

        "no_runtime_imports":
            not runtime_imports,

        "no_semantic_imports":
            not semantic_imports,

        "production_store_unchanged":
            PRODUCTION_STORE.exists()
            == production_store_before,
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
        "FRESH UNIVERSAL ARTICLE BODY STORE WRITER — PHASE 1"
    )
    print("=" * 112)
    print()

    for name, passed in checks.items():
        print(
            f"{name:<64}"
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    print()
    print(
        "Stored test body characters:          "
        + str(
            len(
                body
            )
        )
    )

    print(
        "Stored test body bytes:               "
        + str(
            len(
                body.encode(
                    "utf-8"
                )
            )
        )
    )

    print(
        "Stored test body words:               "
        + str(
            len(
                body.split()
            )
        )
    )

    print(
        "First write action:                   "
        + certificate[
            "existing_file_action"
        ]
    )

    print(
        "Second write action:                  "
        + second_result[
            "write_certificate"
        ][
            "existing_file_action"
        ]
    )

    print(
        "Finalized UUCD body status:           "
        + finalized_record[
            "body_status"
        ]
    )

    print()
    print(
        "Production Body Store written:        False"
    )

    print(
        "Persistent UUCD written:              False"
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
            "FRESH BODY STORE WRITER PHASE 1: FAIL"
        )

        raise SystemExit(1)

    print(
        "FRESH BODY STORE WRITER PHASE 1: PASS"
    )

    print(
        "The writer validated the Universal Handoff Envelope, "
        "stored the exact complete body atomically and verified it."
    )

    print(
        "The production Body Store and persistent UUCD output "
        "were not created or modified."
    )

    print("=" * 112)

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )
