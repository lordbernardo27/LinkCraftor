"""Verify the fresh UUCD core engine without persistent output."""

from __future__ import annotations

import ast
import hashlib
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


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


from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    REQUIRED_UUCD_FIELDS,
    UUCDContractError,
    build_transient_uucd_from_wuc_v1,
    compute_canonical_content_hash_v1,
)


ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_unified_content_document"
    / "uucd_engine_v1.py"
)

PROHIBITED_OUTPUTS = [
    (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
        / "universal_unified_content_documents"
    ),

    (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store"
    ),
]


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def synthetic_wuc(
    *,
    content_body: str,
    source_record_id: str,
    title: str,
) -> dict[str, Any]:
    content_hash = (
        compute_canonical_content_hash_v1(
            content_body
        )
    )

    word_count = len(
        content_body.split()
    )

    return {
        "schema_version":
            "website_unified_content_v1",

        "engine_version":
            "website_unified_content_engine_v1",

        "content_id":
            "wuc_"
            + source_record_id,

        "document_id":
            source_record_id,

        "workspace_id":
            "ws_test",

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity": {
            "source_record_id":
                source_record_id,

            "canonical_url":
                (
                    "https://example.com/"
                    + source_record_id
                ),

            "udare_article_path":
                (
                    "backend/server/data/udare_store/"
                    "ws_test/articles/"
                    + source_record_id
                    + ".html"
                ),

            "udare_article_sha256":
                "a" * 64,
        },

        "title":
            title,

        "h1":
            title,

        "headings": [
            {
                "heading_id":
                    "heading_1",

                "level":
                    1,

                "text":
                    title,

                "block_index":
                    0,
            }
        ],

        "canonical_url":
            (
                "https://example.com/"
                + source_record_id
            ),

        "content_body":
            content_body,

        "content_hash":
            content_hash,

        "body_length":
            len(
                content_body
            ),

        "body_word_count":
            word_count,

        "structure": {
            "block_count":
                2,

            "heading_count":
                1,

            "content_word_count":
                word_count,

            "blocks": [
                {
                    "block_id":
                        "block_1",

                    "block_index":
                        0,

                    "block_type":
                        "heading",

                    "tag":
                        "h1",

                    "text":
                        title,

                    "text_sha256":
                        sha256_text(
                            title
                        ),

                    "word_count":
                        len(
                            title.split()
                        ),
                },

                {
                    "block_id":
                        "block_2",

                    "block_index":
                        1,

                    "block_type":
                        "paragraph",

                    "tag":
                        "p",

                    "text":
                        content_body,

                    "text_sha256":
                        content_hash,

                    "word_count":
                        word_count,
                },
            ],
        },

        "metadata": {
            "article_validation_status":
                "PASS",

            "article_validation_run_id":
                "validation_test_run",

            "article_validation_certificate_id":
                "validation_test_certificate",

            "wuc_persistence_mode":
                "TRANSIENT",

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

            "article_body_persisted_by_wuc":
                False,

            "intermediate_wuc_store_created":
                False,

            "performs_reconstruction":
                False,

            "performs_article_validation":
                False,

            "performs_semantic_analysis":
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

write_calls = []
runtime_imports = []
body_store_imports = []

for node in ast.walk(
    tree
):
    if isinstance(
        node,
        ast.Call,
    ):
        function_name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            function_name = (
                node.func.id
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            function_name = (
                node.func.attr
            )

        if function_name in {
            "write_text",
            "write_bytes",
            "open",
            "dump",
            "copy",
            "copy2",
            "mkdir",
            "makedirs",
            "unlink",
            "remove",
            "rmtree",
        }:
            write_calls.append(
                {
                    "function":
                        function_name,

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

        if "article_body_store" in module:
            body_store_imports.append(
                module
            )

    elif isinstance(
        node,
        ast.Import,
    ):
        for alias in node.names:
            module = alias.name.casefold()

            if "runtime" in module:
                runtime_imports.append(
                    module
                )

            if "article_body_store" in module:
                body_store_imports.append(
                    module
                )


short_body = (
    "This is a complete short article used to verify "
    "that UUCD has no minimum word-count requirement."
)

long_body = "\n\n".join(
    (
        "Paragraph "
        + str(
            index
        )
        + " contains complete retained article content "
        + "for full-body preservation verification."
    )
    for index in range(
        1,
        401,
    )
)

short_wuc = synthetic_wuc(
    content_body=short_body,
    source_record_id="short_article",
    title="Short Article",
)

long_wuc = synthetic_wuc(
    content_body=long_body,
    source_record_id="long_article",
    title="Long Article",
)

short_before = deepcopy(
    short_wuc
)

long_before = deepcopy(
    long_wuc
)

short_uucd = (
    build_transient_uucd_from_wuc_v1(
        short_wuc
    )
)

long_uucd = (
    build_transient_uucd_from_wuc_v1(
        long_wuc
    )
)


bad_hash_wuc = deepcopy(
    short_wuc
)

bad_hash_wuc[
    "content_hash"
] = "0" * 64

bad_hash_rejected = False

try:
    build_transient_uucd_from_wuc_v1(
        bad_hash_wuc
    )

except UUCDContractError:
    bad_hash_rejected = True


ineligible_wuc = deepcopy(
    short_wuc
)

ineligible_wuc[
    "handoff"
][
    "eligible_for_uucd"
] = False

ineligible_rejected = False

try:
    build_transient_uucd_from_wuc_v1(
        ineligible_wuc
    )

except UUCDContractError:
    ineligible_rejected = True


checks = {
    "engine_syntax_valid":
        True,

    "required_uucd_fields_present":
        REQUIRED_UUCD_FIELDS.issubset(
            short_uucd
        ),

    "short_article_full_body_preserved":
        short_uucd[
            "content_body"
        ]
        == short_body,

    "long_article_full_body_preserved":
        long_uucd[
            "content_body"
        ]
        == long_body,

    "short_body_length_preserved":
        short_uucd[
            "body_length"
        ]
        == len(
            short_body
        ),

    "long_body_length_preserved":
        long_uucd[
            "body_length"
        ]
        == len(
            long_body
        ),

    "short_content_hash_verified":
        short_uucd[
            "content_hash"
        ]
        == compute_canonical_content_hash_v1(
            short_body
        ),

    "long_content_hash_verified":
        long_uucd[
            "content_hash"
        ]
        == compute_canonical_content_hash_v1(
            long_body
        ),

    "stable_document_id":
        short_uucd[
            "document_id"
        ]
        == build_transient_uucd_from_wuc_v1(
            short_wuc
        )[
            "document_id"
        ],

    "stable_body_ref":
        short_uucd[
            "body_ref"
        ]
        == build_transient_uucd_from_wuc_v1(
            short_wuc
        )[
            "body_ref"
        ],

    "body_status_pending":
        short_uucd[
            "body_status"
        ]
        == "PENDING_BODY_STORE_WRITE",

    "body_store_handoff_ready":
        short_uucd[
            "handoff"
        ][
            "eligible_for_body_store"
        ]
        is True,

    "full_body_handoff_true":
        short_uucd[
            "handoff"
        ][
            "full_body_handoff"
        ]
        is True,

    "uucd_is_transient":
        short_uucd[
            "metadata"
        ][
            "uucd_persistence_mode"
        ]
        == "TRANSIENT",

    "no_content_reduction":
        short_uucd[
            "metadata"
        ][
            "content_reduction_performed"
        ]
        is False,

    "no_summarization":
        short_uucd[
            "metadata"
        ][
            "summarization_performed"
        ]
        is False,

    "no_truncation":
        short_uucd[
            "metadata"
        ][
            "truncation_performed"
        ]
        is False,

    "no_word_count_limit":
        short_uucd[
            "metadata"
        ][
            "word_count_limit_applied"
        ]
        is False,

    "wuc_input_not_mutated_short":
        short_wuc
        == short_before,

    "wuc_input_not_mutated_long":
        long_wuc
        == long_before,

    "bad_hash_rejected":
        bad_hash_rejected,

    "ineligible_wuc_rejected":
        ineligible_rejected,

    "no_filesystem_write_calls":
        not write_calls,

    "no_runtime_imports":
        not runtime_imports,

    "no_body_store_imports":
        not body_store_imports,

    "uucd_output_directory_absent":
        PROHIBITED_OUTPUTS[
            0
        ].exists()
        is False,

    "body_store_output_directory_absent":
        PROHIBITED_OUTPUTS[
            1
        ].exists()
        is False,
}


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 108)
print(
    "FRESH UUCD ENGINE — PHASE 1 VERIFICATION"
)
print("=" * 108)
print()

for name, passed in checks.items():
    print(
        f"{name:<58}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Short test body characters:           "
    + str(
        len(
            short_body
        )
    )
)

print(
    "Long test body characters:            "
    + str(
        len(
            long_body
        )
    )
)

print(
    "Long test body words:                 "
    + str(
        len(
            long_body.split()
        )
    )
)

print(
    "Generated UUCD fields:                "
    + str(
        len(
            short_uucd
        )
    )
)

print(
    "Generated document ID:                "
    + short_uucd[
        "document_id"
    ]
)

print(
    "Generated future body_ref:            "
    + short_uucd[
        "body_ref"
    ]
)

print()
print(
    "UUCD persistence performed:           False"
)

print(
    "Body Store write performed:           False"
)

print(
    "Runtime Registration created:         False"
)

print(
    "Worker created:                       False"
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
        "FRESH UUCD ENGINE PHASE 1: FAIL"
    )

    raise SystemExit(1)

print(
    "FRESH UUCD ENGINE PHASE 1: PASS"
)

print(
    "The new UUCD engine accepts the frozen WUC contract and "
    "preserves the complete article body without reduction."
)

print(
    "No UUCD document, Body Store file, runtime handler, queue, "
    "worker or persistent output was created."
)

print("=" * 108)
