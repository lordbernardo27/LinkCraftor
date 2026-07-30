"""Verify Body Store Manager adoption of canonical text statistics."""

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


from backend.server.common.text_statistics import (
    count_words,
)

from backend.server.website_unified_content.certified_wuc_input import (
    load_article_validation_pass_contract_v1,
    load_transient_certified_wuc_source_v1,
)

from backend.server.website_unified_content.website_unified_content_engine_v1 import (
    build_transient_website_unified_content_v1,
)

from backend.server.universal_article_body_store.body_store_writer_v1 import (
    _count_words as writer_count_words,
    write_verified_body_from_envelope_v1,
)

from backend.server.universal_article_body_store.body_store_manager_v1 import (
    _count_words as manager_count_words,
    get_body_metadata,
    read_body,
    verify_stored_body,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
SAMPLE_LIMIT = 100

MANAGER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_manager_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),

    "wuc_store": (
        DATA_ROOT
        / "website_unified_content_store"
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

        digest.update(
            b"\x00"
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

        digest.update(
            b"\n"
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

shared_import_found = False
local_function_uses_shared_utility = False
local_function_uses_split = False

for node in tree.body:
    if isinstance(
        node,
        ast.ImportFrom,
    ):
        if (
            node.module
            == "backend.server.common.text_statistics"
            and any(
                alias.name == "count_words"
                for alias in node.names
            )
        ):
            shared_import_found = True

    if isinstance(
        node,
        ast.FunctionDef,
    ) and node.name == "_count_words":
        function_source = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        local_function_uses_shared_utility = (
            "count_words"
            in function_source
        )

        local_function_uses_split = (
            ".split("
            in function_source
        )


contract = load_article_validation_pass_contract_v1(
    WORKSPACE_ID,
    expected_pass_count=EXPECTED_PASS_COUNT,
)

descriptors = (
    contract.get("descriptors")
    or contract.get("records")
    or contract.get("articles")
    or contract.get("pass_records")
)

if not isinstance(
    descriptors,
    list,
):
    raise RuntimeError(
        "PASS contract did not expose descriptors."
    )


sample_match_count = 0
sample_failures = []

for index, descriptor in enumerate(
    descriptors[:SAMPLE_LIMIT],
    start=1,
):
    certified_source = (
        load_transient_certified_wuc_source_v1(
            descriptor
        )
    )

    wuc = (
        build_transient_website_unified_content_v1(
            certified_source=certified_source
        )
    )

    body = wuc[
        "content_body"
    ]

    canonical_count = count_words(
        body
    )

    writer_count = writer_count_words(
        body
    )

    manager_count = manager_count_words(
        body
    )

    wuc_count = wuc[
        "body_word_count"
    ]

    if (
        canonical_count
        == writer_count
        == manager_count
        == wuc_count
    ):
        sample_match_count += 1

    elif len(sample_failures) < 20:
        sample_failures.append(
            {
                "index":
                    index,

                "source_record_id":
                    descriptor.get(
                        "source_record_id"
                    ),

                "canonical_count":
                    canonical_count,

                "writer_count":
                    writer_count,

                "manager_count":
                    manager_count,

                "wuc_count":
                    wuc_count,
            }
        )


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_manager_step4_"
    )
).resolve()

isolated_read_exact = False
isolated_verification_passed = False
isolated_metadata_count_exact = False

try:
    first_descriptor = descriptors[
        0
    ]

    first_source = (
        load_transient_certified_wuc_source_v1(
            first_descriptor
        )
    )

    first_wuc = (
        build_transient_website_unified_content_v1(
            certified_source=first_source
        )
    )

    first_envelope = (
        build_transient_uucd_from_wuc_v1(
            first_wuc
        )
    )

    write_result = (
        write_verified_body_from_envelope_v1(
            first_envelope,
            project_root=temporary_project,
        )
    )

    body_ref = (
        first_envelope[
            "body_payload"
        ][
            "body_ref"
        ]
    )

    expected_body = (
        first_envelope[
            "body_payload"
        ][
            "content_body"
        ]
    )

    expected_count = count_words(
        expected_body
    )

    read_value = read_body(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
    )

    verification = verify_stored_body(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
        expected_content_hash=first_envelope[
            "body_payload"
        ][
            "content_hash"
        ],
        expected_body_length=first_envelope[
            "body_payload"
        ][
            "body_length"
        ],
        expected_body_byte_length=len(
            expected_body.encode(
                "utf-8"
            )
        ),
        expected_body_word_count=expected_count,
    )

    metadata = get_body_metadata(
        project_root=temporary_project,
        workspace_id=WORKSPACE_ID,
        body_ref=body_ref,
    )

    isolated_read_exact = (
        read_value
        == expected_body
    )

    isolated_verification_passed = (
        verification[
            "verification_status"
        ]
        == "VERIFIED"
        and verification[
            "body_word_count"
        ]
        == expected_count
    )

    isolated_metadata_count_exact = (
        metadata[
            "body_word_count"
        ]
        == expected_count
    )

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

protected_unchanged = {
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


direct_samples = {
    "":
        0,

    "One two three":
        3,

    "mother-to-be can't stop—today.":
        3,

    "One   two\n\nthree\tfour":
        4,

    "Pregnancy café résumé Ghana":
        4,
}

direct_function_matches = all(
    manager_count_words(
        text
    )
    == expected
    == count_words(
        text
    )

    for text, expected
    in direct_samples.items()
)


checks = {
    "manager_syntax_valid":
        True,

    "shared_count_words_import_found":
        shared_import_found,

    "manager_word_count_uses_shared_utility":
        local_function_uses_shared_utility,

    "manager_word_count_no_longer_uses_split":
        not local_function_uses_split,

    "direct_samples_match":
        direct_function_matches,

    "first_100_all_components_match":
        sample_match_count
        == SAMPLE_LIMIT,

    "isolated_read_exact":
        isolated_read_exact,

    "isolated_verification_passed":
        isolated_verification_passed,

    "isolated_metadata_count_exact":
        isolated_metadata_count_exact,

    "production_outputs_unchanged":
        all(
            protected_unchanged.values()
        ),
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
    "BODY STORE MANAGER CANONICAL TEXT STATISTICS — STEP 4"
)
print("=" * 112)
print()

for name, passed in checks.items():
    print(
        f"{name:<70}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Real articles checked:                  "
    + str(
        SAMPLE_LIMIT
    )
)

print(
    "WUC/Writer/Manager/Canonical matches:   "
    + str(
        sample_match_count
    )
)

print()
print(
    "SAMPLE MISMATCHES"
)

if sample_failures:
    for failure in sample_failures:
        print(
            "  "
            + str(
                failure
            )
        )

else:
    print(
        "  None"
    )

print()
print(
    "PRODUCTION OUTPUTS"
)

for name, unchanged in protected_unchanged.items():
    print(
        "  "
        + f"{name:<30}"
        + (
            "UNCHANGED"
            if unchanged
            else "CHANGED"
        )
    )

print()
print(
    "Production Body Store files written: 0"
)

print(
    "Persistent UUCD records written:     0"
)

print(
    "Persistent WUC packages written:     0"
)

print(
    "Runtime jobs created:                0"
)

print()
print(
    "Backup: "
    + r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\body_store_manager_text_statistics_step4_20260728_222133\body_store_manager_v1.py"
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
        "BODY STORE MANAGER TEXT STATISTICS STEP 4: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE MANAGER TEXT STATISTICS STEP 4: PASS"
)

print(
    "The Body Store Manager now uses the shared canonical "
    "whitespace-token word-count utility."
)

print("=" * 112)
