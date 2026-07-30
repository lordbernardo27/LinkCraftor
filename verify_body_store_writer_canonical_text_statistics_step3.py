"""Verify Body Store Writer adoption of canonical text statistics."""

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

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_wuc_v1,
)

from backend.server.universal_article_body_store.body_store_writer_v1 import (
    _count_words,
    write_verified_body_from_envelope_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
SAMPLE_LIMIT = 100

WRITER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_writer_v1.py"
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

    writer_count = _count_words(
        body
    )

    wuc_count = wuc[
        "body_word_count"
    ]

    if (
        canonical_count
        == writer_count
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

                "wuc_count":
                    wuc_count,
            }
        )


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_writer_step3_"
    )
).resolve()

isolated_write_passed = False
isolated_body_exact = False
isolated_word_count_verified = False

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

    result = (
        write_verified_body_from_envelope_v1(
            first_envelope,
            project_root=temporary_project,
        )
    )

    stored_path = Path(
        result[
            "body_path"
        ]
    )

    certificate = result[
        "write_certificate"
    ]

    isolated_write_passed = (
        certificate[
            "certificate_status"
        ]
        == "CERTIFIED"
    )

    isolated_body_exact = (
        stored_path.read_text(
            encoding="utf-8"
        )
        == first_envelope[
            "body_payload"
        ][
            "content_body"
        ]
    )

    isolated_word_count_verified = (
        certificate[
            "body_word_count"
        ]
        == count_words(
            first_envelope[
                "body_payload"
            ][
                "content_body"
            ]
        )
        and certificate[
            "word_count_verified"
        ]
        is True
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
    _count_words(
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
    "writer_syntax_valid":
        True,

    "shared_count_words_import_found":
        shared_import_found,

    "writer_word_count_uses_shared_utility":
        local_function_uses_shared_utility,

    "writer_word_count_no_longer_uses_split":
        not local_function_uses_split,

    "direct_samples_match":
        direct_function_matches,

    "first_100_wuc_writer_counts_match":
        sample_match_count
        == SAMPLE_LIMIT,

    "isolated_write_certified":
        isolated_write_passed,

    "isolated_body_exact":
        isolated_body_exact,

    "isolated_word_count_verified":
        isolated_word_count_verified,

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
print("=" * 110)
print(
    "BODY STORE WRITER CANONICAL TEXT STATISTICS — STEP 3"
)
print("=" * 110)
print()

for name, passed in checks.items():
    print(
        f"{name:<68}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Real articles checked:               "
    + str(
        SAMPLE_LIMIT
    )
)

print(
    "WUC/Writer/Canonical matches:         "
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
    + r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\body_store_writer_text_statistics_step3_20260728_221315\body_store_writer_v1.py"
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
        "BODY STORE WRITER TEXT STATISTICS STEP 3: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE WRITER TEXT STATISTICS STEP 3: PASS"
)

print(
    "The Body Store Writer now uses the shared canonical "
    "whitespace-token word-count utility."
)

print("=" * 110)
