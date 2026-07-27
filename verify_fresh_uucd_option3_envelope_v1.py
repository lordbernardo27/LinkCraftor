"""Verify the frozen Option 3 UUCD handoff envelope."""

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
    UUCDContractError,
    build_transient_uucd_from_wuc_v1,
    compute_canonical_content_hash_v1,
    validate_universal_handoff_envelope_v1,
)


ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_unified_content_document"
    / "uucd_engine_v1.py"
)

UUCD_OUTPUT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_unified_content_documents"
)

BODY_STORE_OUTPUT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_article_body_store"
)


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def make_wuc(
    content_body: str,
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
            "wuc_realistic_test",

        "document_id":
            "source_test_001",

        "workspace_id":
            "ws_test",

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity": {
            "source_record_id":
                "source_test_001",

            "canonical_url":
                "https://example.com/test",

            "udare_article_path":
                (
                    "backend/server/data/udare_store/"
                    "ws_test/articles/test.html"
                ),

            "udare_article_sha256":
                "a" * 64,
        },

        "title":
            "Option 3 Test Article",

        "h1":
            "Option 3 Test Article",

        "headings": [],

        "canonical_url":
            "https://example.com/test",

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
                1,

            "heading_count":
                0,

            "content_word_count":
                word_count,

            "blocks": [
                {
                    "block_id":
                        "block_1",

                    "block_index":
                        0,

                    "block_type":
                        "paragraph",

                    "tag":
                        "p",

                    "text":
                        content_body,

                    "text_sha256":
                        sha256_text(
                            content_body
                        ),

                    "word_count":
                        word_count,
                }
            ],
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


body = "\n\n".join(
    (
        "Paragraph "
        + str(
            index
        )
        + " contains the complete retained article body "
        + "for Option 3 envelope verification."
    )
    for index in range(
        1,
        301,
    )
)

wuc = make_wuc(
    body
)

wuc_before = deepcopy(
    wuc
)

envelope = (
    build_transient_uucd_from_wuc_v1(
        wuc
    )
)

record = envelope[
    "uucd_record"
]

payload = envelope[
    "body_payload"
]

binding = envelope[
    "binding"
]


tampered = deepcopy(
    envelope
)

tampered[
    "body_payload"
][
    "content_hash"
] = "0" * 64

tampered_rejected = False

try:
    validate_universal_handoff_envelope_v1(
        tampered
    )

except UUCDContractError:
    tampered_rejected = True


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

filesystem_calls = []
runtime_imports = []
body_store_imports = []

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
            "open",
            "write_text",
            "write_bytes",
            "mkdir",
            "replace",
            "rename",
            "unlink",
            "dump",
        }:
            filesystem_calls.append(
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

        if "article_body_store" in module:
            body_store_imports.append(
                module
            )


binding_fields = (
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
)


checks = {
    "engine_syntax_valid":
        True,

    "envelope_valid":
        validate_universal_handoff_envelope_v1(
            envelope
        )
        is True,

    "envelope_has_uucd_record":
        isinstance(
            record,
            dict,
        ),

    "envelope_has_body_payload":
        isinstance(
            payload,
            dict,
        ),

    "envelope_has_binding":
        isinstance(
            binding,
            dict,
        ),

    "uucd_record_excludes_content_body":
        "content_body"
        not in record,

    "body_payload_contains_content_body":
        payload[
            "content_body"
        ]
        == body,

    "complete_body_preserved":
        len(
            payload[
                "content_body"
            ]
        )
        == len(
            body
        ),

    "content_hash_preserved":
        payload[
            "content_hash"
        ]
        == compute_canonical_content_hash_v1(
            body
        ),

    "all_binding_fields_match":
        all(
            record[
                field
            ]
            == payload[
                field
            ]
            == binding[
                field
            ]
            for field in binding_fields
        ),

    "binding_status_verified":
        binding[
            "binding_status"
        ]
        == "BOUND_AND_VERIFIED",

    "body_status_pending":
        record[
            "body_status"
        ]
        == "PENDING_BODY_STORE_WRITE",

    "record_not_persisted":
        record[
            "metadata"
        ][
            "persistence_status"
        ]
        == "NOT_PERSISTED",

    "body_transport_declared":
        record[
            "metadata"
        ][
            "body_transport"
        ]
        == "UNIVERSAL_BODY_PAYLOAD",

    "wuc_not_mutated":
        wuc
        == wuc_before,

    "tampered_payload_rejected":
        tampered_rejected,

    "no_filesystem_calls":
        not filesystem_calls,

    "no_runtime_imports":
        not runtime_imports,

    "no_body_store_imports":
        not body_store_imports,

    "uucd_output_absent":
        UUCD_OUTPUT.exists()
        is False,

    "body_store_output_absent":
        BODY_STORE_OUTPUT.exists()
        is False,
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
    "FRESH UUCD — OPTION 3 UNIVERSAL HANDOFF ENVELOPE"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<62}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Article body characters:              "
    + str(
        len(
            body
        )
    )
)

print(
    "Article body words:                   "
    + str(
        len(
            body.split()
        )
    )
)

print(
    "UUCD record contains content_body:    "
    + str(
        "content_body"
        in record
    )
)

print(
    "Body payload contains content_body:   "
    + str(
        "content_body"
        in payload
    )
)

print(
    "Binding status:                       "
    + str(
        binding[
            "binding_status"
        ]
    )
)

print(
    "UUCD body status:                     "
    + str(
        record[
            "body_status"
        ]
    )
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
    "Backup location: "
    + r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\uucd_option3_contract_replacement_20260727_004338"
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
        "FRESH UUCD OPTION 3 ENVELOPE: FAIL"
    )

    raise SystemExit(1)

print(
    "FRESH UUCD OPTION 3 ENVELOPE: PASS"
)

print(
    "The canonical UUCD record contains no article body."
)

print(
    "The exact full article body is carried only by the "
    "cryptographically bound Universal Body Payload."
)

print(
    "No UUCD file, Body Store file, worker, queue or Runtime "
    "Registration was created."
)

print("=" * 112)
