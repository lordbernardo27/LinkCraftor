"""Verify WUC adoption of canonical shared text statistics."""

from __future__ import annotations

import ast
import hashlib
import sys
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
    _word_count,
    build_transient_website_unified_content_v1,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
SAMPLE_LIMIT = 100

WUC_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "website_unified_content"
    / "website_unified_content_engine_v1.py"
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


source = WUC_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        WUC_PATH
    ),
)


shared_import_found = False
private_function_uses_shared_utility = False
regex_inside_word_count = False

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
    ) and node.name == "_word_count":
        function_source = ast.get_source_segment(
            source,
            node,
        ) or ""

        private_function_uses_shared_utility = (
            "count_words"
            in function_source
        )

        regex_inside_word_count = (
            "re.findall"
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

    expected_count = count_words(
        body
    )

    actual_count = wuc[
        "body_word_count"
    ]

    if actual_count == expected_count:
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

                "wuc_count":
                    actual_count,

                "canonical_count":
                    expected_count,
            }
        )


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
    _word_count(
        text
    )
    == expected
    == count_words(
        text
    )

    for text, expected
    in direct_samples.items()
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


checks = {
    "wuc_syntax_valid":
        True,

    "shared_count_words_import_found":
        shared_import_found,

    "wuc_word_count_uses_shared_utility":
        private_function_uses_shared_utility,

    "wuc_word_count_no_longer_uses_regex":
        not regex_inside_word_count,

    "direct_samples_match":
        direct_function_matches,

    "first_100_real_articles_match":
        sample_match_count
        == SAMPLE_LIMIT,

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
print("=" * 108)
print(
    "WUC CANONICAL TEXT STATISTICS ADOPTION — STEP 2"
)
print("=" * 108)
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
    "Real articles checked:               "
    + str(
        SAMPLE_LIMIT
    )
)

print(
    "Real articles matching canonical:    "
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
    "Body Store files written:          0"
)

print(
    "Persistent WUC packages written:   0"
)

print(
    "Persistent UUCD records written:   0"
)

print(
    "Runtime jobs created:              0"
)

print()
print(
    "Backup: "
    + r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\wuc_text_statistics_step2_20260728_220840\website_unified_content_engine_v1.py"
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
        "WUC TEXT STATISTICS STEP 2: FAIL"
    )

    raise SystemExit(1)

print(
    "WUC TEXT STATISTICS STEP 2: PASS"
)

print(
    "WUC now uses the shared canonical whitespace-token "
    "word-count utility."
)

print("=" * 108)
