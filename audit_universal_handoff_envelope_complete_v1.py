"""Complete read-only audit of the Universal Handoff Envelope."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


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
    BINDING_FIELD_NAMES,
    BODY_PAYLOAD_SCHEMA_VERSION,
    HANDOFF_ENVELOPE_SCHEMA_VERSION,
    REQUIRED_BINDING_FIELDS,
    REQUIRED_BODY_PAYLOAD_FIELDS,
    REQUIRED_UUCD_RECORD_FIELDS,
    UUCDContractError,
    UUCD_ENGINE_VERSION,
    UUCD_SCHEMA_VERSION,
    build_transient_uucd_from_wuc_v1,
    compute_canonical_content_hash_v1,
    validate_universal_handoff_envelope_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"

ENGINE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_unified_content_document"
    / "uucd_engine_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

UUCD_OUTPUT = (
    DATA_ROOT
    / "universal_unified_content_documents"
)

BODY_STORE_OUTPUT = (
    DATA_ROOT
    / "universal_article_body_store"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "universal_handoff_envelope_complete_audit_v1.json"
)

EXPECTED_ENVELOPE_FIELDS = {
    "envelope_schema_version",
    "engine_version",
    "uucd_record",
    "body_payload",
    "binding",
    "envelope_status",
}

EXPECTED_BODY_PAYLOAD_FIELDS = {
    "payload_schema_version",
    "document_id",
    "workspace_id",
    "source_type",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "content_encoding",
}

EXPECTED_BINDING_FIELDS = {
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "binding_hash",
    "binding_status",
}

FORBIDDEN_RECORD_BODY_KEYS = {
    "content_body",
    "article_body",
    "body",
    "raw_html",
    "clean_html",
    "full_text",
    "article_text",
}

FILESYSTEM_WRITE_CALLS = {
    "open",
    "write",
    "write_text",
    "write_bytes",
    "dump",
    "mkdir",
    "makedirs",
    "replace",
    "rename",
    "unlink",
    "remove",
    "rmtree",
    "copy",
    "copy2",
}

RUNTIME_CALLS = {
    "register_runtime_handler",
    "register_job",
    "enqueue",
    "dispatch",
    "create_job",
    "submit_job",
    "run_job",
}

SEMANTIC_CALLS = {
    "embed",
    "embedding",
    "extract_entities",
    "build_topic_cluster",
    "semantic_analysis",
    "reason",
}


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def count_words(
    value: str,
) -> int:
    return len(
        value.split()
    )


def find_keys_recursive(
    value: Any,
    *,
    target_keys: set[str],
    path: str = "$",
) -> list[str]:
    results: list[str] = []

    if isinstance(
        value,
        Mapping,
    ):
        for key, child in value.items():
            child_path = (
                path
                + "."
                + str(
                    key
                )
            )

            if str(
                key
            ) in target_keys:
                results.append(
                    child_path
                )

            results.extend(
                find_keys_recursive(
                    child,
                    target_keys=target_keys,
                    path=child_path,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            results.extend(
                find_keys_recursive(
                    child,
                    target_keys=target_keys,
                    path=(
                        path
                        + "["
                        + str(
                            index
                        )
                        + "]"
                    ),
                )
            )

    return results


def make_realistic_wuc(
    content_body: str,
) -> dict[str, Any]:
    content_hash = (
        compute_canonical_content_hash_v1(
            content_body
        )
    )

    word_count = count_words(
        content_body
    )

    title = (
        "Complete Universal Handoff Envelope Audit Article"
    )

    headings = [
        {
            "heading_id":
                "heading_1",

            "level":
                1,

            "text":
                title,

            "block_index":
                0,
        },
        {
            "heading_id":
                "heading_2",

            "level":
                2,

            "text":
                "Envelope Verification",

            "block_index":
                2,
        },
    ]

    structure = {
        "block_count":
            3,

        "heading_count":
            2,

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
                    count_words(
                        title
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
            {
                "block_id":
                    "block_3",

                "block_index":
                    2,

                "block_type":
                    "heading",

                "tag":
                    "h2",

                "text":
                    "Envelope Verification",

                "text_sha256":
                    sha256_text(
                        "Envelope Verification"
                    ),

                "word_count":
                    2,
            },
        ],
    }

    source_identity = {
        "source_record_id":
            "raw_html_complete_envelope_audit",

        "canonical_url":
            "https://example.com/complete-envelope-audit",

        "udare_article_path":
            (
                "backend/server/data/udare_store/"
                + WORKSPACE_ID
                + "/articles/complete-envelope-audit.html"
            ),

        "udare_article_sha256":
            "a" * 64,

        "source_snapshot_reference":
            "snapshot_complete_envelope_audit",

        "version_asset_reference":
            "version_asset_complete_envelope_audit",
    }

    return {
        "schema_version":
            "website_unified_content_v1",

        "engine_version":
            "website_unified_content_engine_v1",

        "content_id":
            "wuc_complete_envelope_audit",

        "document_id":
            "raw_html_complete_envelope_audit",

        "workspace_id":
            WORKSPACE_ID,

        "source_type":
            "website",

        "source_format":
            "html",

        "source_identity":
            source_identity,

        "title":
            title,

        "h1":
            title,

        "headings":
            headings,

        "canonical_url":
            source_identity[
                "canonical_url"
            ],

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

        "structure":
            structure,

        "metadata": {
            "article_validation_status":
                "PASS",

            "article_validation_run_id":
                "article_validation_audit",

            "article_validation_certificate_id":
                "article_validation_certificate_audit",

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


content_body = "\n\n".join(
    (
        "Paragraph "
        + str(
            index
        )
        + " contains complete retained article content "
        + "for exhaustive Universal Handoff Envelope verification. "
        + "The body must pass through without summarization, "
        + "truncation, rewriting, normalization, or reduction."
    )
    for index in range(
        1,
        501,
    )
)

wuc = make_realistic_wuc(
    content_body
)

wuc_before = deepcopy(
    wuc
)

envelope_one = (
    build_transient_uucd_from_wuc_v1(
        wuc
    )
)

envelope_two = (
    build_transient_uucd_from_wuc_v1(
        wuc
    )
)

uucd_record = envelope_one[
    "uucd_record"
]

body_payload = envelope_one[
    "body_payload"
]

binding = envelope_one[
    "binding"
]


tamper_results: dict[
    str,
    bool
] = {}

for field in BINDING_FIELD_NAMES:
    tampered = deepcopy(
        envelope_one
    )

    original = tampered[
        "body_payload"
    ][
        field
    ]

    if isinstance(
        original,
        int,
    ):
        changed = original + 1

    else:
        changed = (
            str(
                original
            )
            + "_tampered"
        )

    tampered[
        "body_payload"
    ][
        field
    ] = changed

    rejected = False

    try:
        validate_universal_handoff_envelope_v1(
            tampered
        )

    except UUCDContractError:
        rejected = True

    tamper_results[
        "body_payload."
        + field
    ] = rejected


record_tamper_results: dict[
    str,
    bool
] = {}

for field in BINDING_FIELD_NAMES:
    tampered = deepcopy(
        envelope_one
    )

    original = tampered[
        "uucd_record"
    ][
        field
    ]

    if isinstance(
        original,
        int,
    ):
        changed = original + 1

    else:
        changed = (
            str(
                original
            )
            + "_tampered"
        )

    tampered[
        "uucd_record"
    ][
        field
    ] = changed

    rejected = False

    try:
        validate_universal_handoff_envelope_v1(
            tampered
        )

    except UUCDContractError:
        rejected = True

    record_tamper_results[
        "uucd_record."
        + field
    ] = rejected


binding_tamper_results: dict[
    str,
    bool
] = {}

for field in (
    *BINDING_FIELD_NAMES,
    "binding_hash",
):
    tampered = deepcopy(
        envelope_one
    )

    original = tampered[
        "binding"
    ][
        field
    ]

    if isinstance(
        original,
        int,
    ):
        changed = original + 1

    else:
        changed = (
            str(
                original
            )
            + "_tampered"
        )

    tampered[
        "binding"
    ][
        field
    ] = changed

    rejected = False

    try:
        validate_universal_handoff_envelope_v1(
            tampered
        )

    except UUCDContractError:
        rejected = True

    binding_tamper_results[
        "binding."
        + field
    ] = rejected


body_content_tampered = deepcopy(
    envelope_one
)

body_content_tampered[
    "body_payload"
][
    "content_body"
] += "\nTAMPERED"

body_content_tamper_rejected = False

try:
    validate_universal_handoff_envelope_v1(
        body_content_tampered
    )

except UUCDContractError:
    body_content_tamper_rejected = True


missing_field_tests: dict[
    str,
    bool
] = {}

for section, field in (
    (
        "uucd_record",
        "document_id",
    ),
    (
        "uucd_record",
        "body_ref",
    ),
    (
        "body_payload",
        "content_body",
    ),
    (
        "body_payload",
        "content_hash",
    ),
    (
        "binding",
        "binding_hash",
    ),
):
    tampered = deepcopy(
        envelope_one
    )

    del tampered[
        section
    ][
        field
    ]

    rejected = False

    try:
        validate_universal_handoff_envelope_v1(
            tampered
        )

    except UUCDContractError:
        rejected = True

    missing_field_tests[
        section
        + "."
        + field
    ] = rejected


record_body_key_locations = (
    find_keys_recursive(
        uucd_record,
        target_keys=FORBIDDEN_RECORD_BODY_KEYS,
    )
)

payload_body_key_locations = (
    find_keys_recursive(
        body_payload,
        target_keys={
            "content_body",
        },
    )
)


engine_source = ENGINE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

engine_tree = ast.parse(
    engine_source,
    filename=str(
        ENGINE_PATH
    ),
)

filesystem_calls = []
runtime_calls = []
semantic_calls = []
runtime_imports = []
body_store_imports = []

for node in ast.walk(
    engine_tree
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

        if name in FILESYSTEM_WRITE_CALLS:
            filesystem_calls.append(
                {
                    "function":
                        name,

                    "line":
                        node.lineno,
                }
            )

        if name in RUNTIME_CALLS:
            runtime_calls.append(
                {
                    "function":
                        name,

                    "line":
                        node.lineno,
                }
            )

        if name in SEMANTIC_CALLS:
            semantic_calls.append(
                {
                    "function":
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


checks = {
    "engine_syntax_valid":
        True,

    "envelope_validation_passes":
        validate_universal_handoff_envelope_v1(
            envelope_one
        )
        is True,

    "exact_envelope_fields":
        set(
            envelope_one
        )
        == EXPECTED_ENVELOPE_FIELDS,

    "correct_envelope_schema_version":
        envelope_one[
            "envelope_schema_version"
        ]
        == HANDOFF_ENVELOPE_SCHEMA_VERSION,

    "correct_engine_version":
        envelope_one[
            "engine_version"
        ]
        == UUCD_ENGINE_VERSION,

    "correct_envelope_status":
        envelope_one[
            "envelope_status"
        ]
        == "READY_FOR_BODY_STORE",

    "exact_uucd_record_fields":
        set(
            uucd_record
        )
        == REQUIRED_UUCD_RECORD_FIELDS,

    "correct_uucd_schema_version":
        uucd_record[
            "schema_version"
        ]
        == UUCD_SCHEMA_VERSION,

    "exact_body_payload_fields":
        set(
            body_payload
        )
        == EXPECTED_BODY_PAYLOAD_FIELDS,

    "correct_body_payload_schema":
        body_payload[
            "payload_schema_version"
        ]
        == BODY_PAYLOAD_SCHEMA_VERSION,

    "exact_binding_fields":
        set(
            binding
        )
        == EXPECTED_BINDING_FIELDS,

    "uucd_record_contains_no_body_fields":
        not record_body_key_locations,

    "body_payload_has_single_content_body":
        payload_body_key_locations
        == [
            "$.content_body"
        ],

    "body_payload_full_body_exact":
        body_payload[
            "content_body"
        ]
        == wuc[
            "content_body"
        ],

    "body_payload_hash_exact":
        body_payload[
            "content_hash"
        ]
        == wuc[
            "content_hash"
        ],

    "body_payload_length_exact":
        body_payload[
            "body_length"
        ]
        == len(
            wuc[
                "content_body"
            ]
        ),

    "body_payload_word_count_exact":
        body_payload[
            "body_word_count"
        ]
        == wuc[
            "body_word_count"
        ],

    "source_identity_preserved":
        uucd_record[
            "source_identity"
        ]
        == wuc[
            "source_identity"
        ],

    "structure_preserved":
        uucd_record[
            "structure"
        ]
        == wuc[
            "structure"
        ],

    "headings_preserved":
        uucd_record[
            "headings"
        ]
        == wuc[
            "headings"
        ],

    "title_preserved":
        uucd_record[
            "title"
        ]
        == wuc[
            "title"
        ],

    "canonical_url_preserved":
        uucd_record[
            "canonical_url"
        ]
        == wuc[
            "canonical_url"
        ],

    "all_binding_fields_match":
        all(
            uucd_record[
                field
            ]
            == body_payload[
                field
            ]
            == binding[
                field
            ]
            for field in BINDING_FIELD_NAMES
        ),

    "binding_status_verified":
        binding[
            "binding_status"
        ]
        == "BOUND_AND_VERIFIED",

    "all_body_payload_binding_tampering_rejected":
        all(
            tamper_results.values()
        ),

    "all_uucd_record_binding_tampering_rejected":
        all(
            record_tamper_results.values()
        ),

    "all_binding_tampering_rejected":
        all(
            binding_tamper_results.values()
        ),

    "body_content_tampering_rejected":
        body_content_tamper_rejected,

    "missing_required_fields_rejected":
        all(
            missing_field_tests.values()
        ),

    "deterministic_document_id":
        envelope_one[
            "uucd_record"
        ][
            "document_id"
        ]
        == envelope_two[
            "uucd_record"
        ][
            "document_id"
        ],

    "deterministic_content_ref":
        envelope_one[
            "uucd_record"
        ][
            "content_ref"
        ]
        == envelope_two[
            "uucd_record"
        ][
            "content_ref"
        ],

    "deterministic_body_ref":
        envelope_one[
            "uucd_record"
        ][
            "body_ref"
        ]
        == envelope_two[
            "uucd_record"
        ][
            "body_ref"
        ],

    "deterministic_binding_hash":
        envelope_one[
            "binding"
        ][
            "binding_hash"
        ]
        == envelope_two[
            "binding"
        ][
            "binding_hash"
        ],

    "uucd_body_status_pending":
        uucd_record[
            "body_status"
        ]
        == "PENDING_BODY_STORE_WRITE",

    "uucd_not_persisted":
        uucd_record[
            "metadata"
        ][
            "persistence_status"
        ]
        == "NOT_PERSISTED",

    "verified_body_required_before_persistence":
        uucd_record[
            "handoff"
        ][
            "requires_verified_body_before_persistence"
        ]
        is True,

    "no_content_reduction":
        uucd_record[
            "metadata"
        ][
            "content_reduction_performed"
        ]
        is False,

    "no_summarization":
        uucd_record[
            "metadata"
        ][
            "summarization_performed"
        ]
        is False,

    "no_truncation":
        uucd_record[
            "metadata"
        ][
            "truncation_performed"
        ]
        is False,

    "no_word_count_limit":
        uucd_record[
            "metadata"
        ][
            "word_count_limit_applied"
        ]
        is False,

    "wuc_input_not_mutated":
        wuc
        == wuc_before,

    "no_filesystem_write_calls":
        not filesystem_calls,

    "no_runtime_calls":
        not runtime_calls,

    "no_semantic_calls":
        not semantic_calls,

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


report = {
    "schema_version":
        "universal_handoff_envelope_complete_audit_v1",

    "workspace_id":
        WORKSPACE_ID,

    "audit_mode":
        "READ_ONLY",

    "audit_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "checks":
        checks,

    "envelope_fields":
        sorted(
            envelope_one
        ),

    "uucd_record_fields":
        sorted(
            uucd_record
        ),

    "body_payload_fields":
        sorted(
            body_payload
        ),

    "binding_fields":
        sorted(
            binding
        ),

    "record_body_key_locations":
        record_body_key_locations,

    "payload_body_key_locations":
        payload_body_key_locations,

    "body_payload_tamper_results":
        tamper_results,

    "uucd_record_tamper_results":
        record_tamper_results,

    "binding_tamper_results":
        binding_tamper_results,

    "body_content_tamper_rejected":
        body_content_tamper_rejected,

    "missing_field_tests":
        missing_field_tests,

    "filesystem_calls":
        filesystem_calls,

    "runtime_calls":
        runtime_calls,

    "semantic_calls":
        semantic_calls,

    "runtime_imports":
        runtime_imports,

    "body_store_imports":
        body_store_imports,

    "article_body_characters":
        len(
            content_body
        ),

    "article_body_words":
        count_words(
            content_body
        ),

    "source_files_modified":
        False,

    "data_outputs_modified":
        False,

    "runtime_state_modified":
        False,

    "failures":
        failures,
}


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 118)
print(
    "UNIVERSAL HANDOFF ENVELOPE — COMPLETE CANONICAL AUDIT"
)
print("=" * 118)
print()

for name, passed in checks.items():
    print(
        f"{name:<72}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Envelope fields:                      "
    + str(
        len(
            envelope_one
        )
    )
)

print(
    "UUCD Record fields:                   "
    + str(
        len(
            uucd_record
        )
    )
)

print(
    "Body Payload fields:                  "
    + str(
        len(
            body_payload
        )
    )
)

print(
    "Binding fields:                       "
    + str(
        len(
            binding
        )
    )
)

print(
    "Article body characters:              "
    + str(
        len(
            content_body
        )
    )
)

print(
    "Article body words:                   "
    + str(
        count_words(
            content_body
        )
    )
)

print(
    "Forbidden body keys in UUCD Record:   "
    + str(
        len(
            record_body_key_locations
        )
    )
)

print(
    "content_body locations in payload:    "
    + str(
        payload_body_key_locations
    )
)

print(
    "Body Payload tamper tests passed:     "
    + str(
        sum(
            tamper_results.values()
        )
    )
    + "/"
    + str(
        len(
            tamper_results
        )
    )
)

print(
    "UUCD Record tamper tests passed:      "
    + str(
        sum(
            record_tamper_results.values()
        )
    )
    + "/"
    + str(
        len(
            record_tamper_results
        )
    )
)

print(
    "Binding tamper tests passed:          "
    + str(
        sum(
            binding_tamper_results.values()
        )
    )
    + "/"
    + str(
        len(
            binding_tamper_results
        )
    )
)

print()
print(
    "Persistent UUCD written:              False"
)

print(
    "Body Store body written:              False"
)

print(
    "Worker created:                       False"
)

print(
    "Queue created:                        False"
)

print(
    "Runtime Registration created:         False"
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
print(
    "Audit report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "UNIVERSAL HANDOFF ENVELOPE COMPLETE AUDIT: FAIL"
    )

    print(
        "Do not freeze the envelope until every failed check is resolved."
    )

    print("=" * 118)

    raise SystemExit(1)

print(
    "UNIVERSAL HANDOFF ENVELOPE COMPLETE AUDIT: PASS"
)

print(
    "The envelope, UUCD Record, Universal Body Payload and cryptographic "
    "binding satisfy the complete frozen Option 3 contract."
)

print(
    "The article body exists only in the transient Body Payload and "
    "all identity, integrity, deterministic-reference and tamper rules passed."
)

print("=" * 118)
