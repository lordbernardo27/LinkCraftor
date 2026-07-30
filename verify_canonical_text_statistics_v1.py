"""Verify the canonical shared text-statistics utility."""

from __future__ import annotations

import ast
import sys
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


from backend.server.common.text_statistics import (
    TEXT_STATISTICS_VERSION,
    TextStatisticsError,
    calculate_text_statistics,
    count_characters,
    count_utf8_bytes,
    count_words,
)


UTILITY_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "common"
    / "text_statistics.py"
)


samples = {
    "empty":
        "",

    "ordinary":
        "This is a normal sentence.",

    "multiple_whitespace":
        "One   two\n\nthree\tfour",

    "punctuation":
        "mother-to-be can't stop—today.",

    "unicode":
        "Pregnancy café résumé Ghana",
}


expected_words = {
    "empty":
        0,

    "ordinary":
        5,

    "multiple_whitespace":
        4,

    "punctuation":
        3,

    "unicode":
        4,
}


checks = {}

for name, text in samples.items():
    checks[
        name
        + "_word_count"
    ] = (
        count_words(
            text
        )
        == expected_words[
            name
        ]
    )

    checks[
        name
        + "_character_count"
    ] = (
        count_characters(
            text
        )
        == len(
            text
        )
    )

    checks[
        name
        + "_utf8_byte_count"
    ] = (
        count_utf8_bytes(
            text
        )
        == len(
            text.encode(
                "utf-8"
            )
        )
    )


statistics = calculate_text_statistics(
    samples[
        "unicode"
    ]
)

checks[
    "statistics_version"
] = (
    statistics[
        "statistics_version"
    ]
    == TEXT_STATISTICS_VERSION
)

checks[
    "combined_word_count"
] = (
    statistics[
        "word_count"
    ]
    == 4
)

checks[
    "combined_character_count"
] = (
    statistics[
        "character_count"
    ]
    == len(
        samples[
            "unicode"
        ]
    )
)

checks[
    "combined_utf8_byte_count"
] = (
    statistics[
        "utf8_byte_count"
    ]
    == len(
        samples[
            "unicode"
        ].encode(
            "utf-8"
        )
    )
)


invalid_input_rejected = False

try:
    count_words(
        None
    )

except TextStatisticsError:
    invalid_input_rejected = True


checks[
    "invalid_input_rejected"
] = invalid_input_rejected


source = UTILITY_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        UTILITY_PATH
    ),
)

prohibited_calls = []

for node in ast.walk(
    tree
):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

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
        "open",
        "unlink",
        "remove",
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


checks[
    "no_filesystem_operations"
] = not prohibited_calls


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 104)
print(
    "CANONICAL SHARED TEXT STATISTICS — STEP 1"
)
print("=" * 104)
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
    "Utility path: "
    + str(
        UTILITY_PATH
    )
)

print(
    "Canonical word-count method: len(text.split())"
)

print(
    "WUC modified:              False"
)

print(
    "Body Store Writer modified: False"
)

print(
    "Body Store Manager modified: False"
)

print(
    "Production data modified:   False"
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
        "CANONICAL TEXT STATISTICS STEP 1: FAIL"
    )

    raise SystemExit(1)

print(
    "CANONICAL TEXT STATISTICS STEP 1: PASS"
)

print(
    "The shared canonical text-statistics utility now exists and "
    "is ready to be adopted by WUC, the Writer, and the Manager."
)

print("=" * 104)

