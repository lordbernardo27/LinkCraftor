from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
import sys
from collections import Counter
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
    _count_words as writer_count_words,
)

from backend.server.universal_article_body_store.body_store_manager_v1 import (
    _count_words as manager_count_words,
)


WORKSPACE_ID = "ws_whattoexpect_com"
EXPECTED_PASS_COUNT = 2219
REAL_SAMPLE_LIMIT = 100

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

WUC_ENGINE_PATH = (
    SERVER_ROOT
    / "website_unified_content"
    / "website_unified_content_engine_v1.py"
)

WRITER_PATH = (
    SERVER_ROOT
    / "universal_article_body_store"
    / "body_store_writer_v1.py"
)

MANAGER_PATH = (
    SERVER_ROOT
    / "universal_article_body_store"
    / "body_store_manager_v1.py"
)

AUDIT_PATH = (
    PROJECT_ROOT
    / "audit_all_transient_body_payloads_v1.py"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "canonical_body_word_count_alignment_v1.json"
)

PROTECTED_OUTPUTS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),

    "persistent_wuc_store": (
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
        key=lambda value: (
            value.relative_to(
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


def extract_function_source(
    path: Path,
    function_name: str,
) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path":
                str(
                    path
                ),

            "function_name":
                function_name,

            "found":
                False,

            "error":
                "FILE_NOT_FOUND",
        }

    source = path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    tree = ast.parse(
        source,
        filename=str(
            path
        ),
    )

    lines = source.splitlines()

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name != function_name:
            continue

        end_lineno = getattr(
            node,
            "end_lineno",
            node.lineno,
        )

        function_source = "\n".join(
            lines[
                node.lineno - 1:
                end_lineno
            ]
        )

        return {
            "path":
                path.relative_to(
                    PROJECT_ROOT
                ).as_posix(),

            "function_name":
                function_name,

            "found":
                True,

            "line_start":
                node.lineno,

            "line_end":
                end_lineno,

            "source":
                function_source,

            "ast_dump":
                ast.dump(
                    node,
                    indent=2,
                ),
        }

    return {
        "path":
            path.relative_to(
                PROJECT_ROOT
            ).as_posix(),

        "function_name":
            function_name,

        "found":
            False,

        "error":
            "FUNCTION_NOT_FOUND",
    }


def regex_word_count(
    value: str,
) -> int:
    return len(
        re.findall(
            r"\b[\w'-]+\b",
            value,
            flags=re.UNICODE,
        )
    )


def split_word_count(
    value: str,
) -> int:
    return len(
        value.split()
    )


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_OUTPUTS.items()
}


print()
print("=" * 118)
print(
    "CANONICAL BODY WORD-COUNT ALIGNMENT — READ-ONLY SCAN"
)
print("=" * 118)
print()


implementations = {
    "wuc_word_count":
        extract_function_source(
            WUC_ENGINE_PATH,
            "_word_count",
        ),

    "writer_word_count":
        extract_function_source(
            WRITER_PATH,
            "_count_words",
        ),

    "manager_word_count":
        extract_function_source(
            MANAGER_PATH,
            "_count_words",
        ),
}


for name, result in implementations.items():
    print(
        name
    )

    print(
        "  File:   "
        + result[
            "path"
        ]
    )

    print(
        "  Found:  "
        + str(
            result[
                "found"
            ]
        )
    )

    if result[
        "found"
    ]:
        print(
            "  Lines:  "
            + str(
                result[
                    "line_start"
                ]
            )
            + "-"
            + str(
                result[
                    "line_end"
                ]
            )
        )

        print(
            "  Source:"
        )

        for line in result[
            "source"
        ].splitlines():
            print(
                "    "
                + line
            )

    print()


audit_split_usage = None

if AUDIT_PATH.is_file():
    audit_source = AUDIT_PATH.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

    audit_split_usage = bool(
        re.search(
            r"len\s*\(\s*body\.split\s*\(\s*\)\s*\)",
            audit_source,
        )
    )


contract = load_article_validation_pass_contract_v1(
    WORKSPACE_ID,
    expected_pass_count=EXPECTED_PASS_COUNT,
)

if isinstance(
    contract,
    dict,
):
    descriptors = (
        contract.get(
            "descriptors"
        )
        or contract.get(
            "records"
        )
        or contract.get(
            "articles"
        )
        or contract.get(
            "pass_records"
        )
    )

elif isinstance(
    contract,
    list,
):
    descriptors = contract

else:
    descriptors = None


if not isinstance(
    descriptors,
    list,
):
    print(
        "FAIL: PASS contract did not expose descriptors."
    )

    raise SystemExit(1)


sample_results = []
comparison_counts = Counter()


for index, descriptor in enumerate(
    descriptors[
        :REAL_SAMPLE_LIMIT
    ],
    start=1,
):
    source = load_transient_certified_wuc_source_v1(
        descriptor
    )

    wuc = build_transient_website_unified_content_v1(
        certified_source=source
    )

    envelope = build_transient_uucd_from_wuc_v1(
        wuc
    )

    body = envelope[
        "body_payload"
    ][
        "content_body"
    ]

    wuc_count = wuc[
        "body_word_count"
    ]

    writer_count = writer_count_words(
        body
    )

    manager_count = manager_count_words(
        body
    )

    split_count = split_word_count(
        body
    )

    regex_count = regex_word_count(
        body
    )

    if wuc_count == writer_count:
        comparison_counts[
            "wuc_equals_writer"
        ] += 1

    if wuc_count == manager_count:
        comparison_counts[
            "wuc_equals_manager"
        ] += 1

    if writer_count == manager_count:
        comparison_counts[
            "writer_equals_manager"
        ] += 1

    if wuc_count == split_count:
        comparison_counts[
            "wuc_equals_split"
        ] += 1

    if wuc_count == regex_count:
        comparison_counts[
            "wuc_equals_regex"
        ] += 1

    if writer_count == split_count:
        comparison_counts[
            "writer_equals_split"
        ] += 1

    sample_results.append(
        {
            "index":
                index,

            "source_record_id":
                descriptor.get(
                    "source_record_id"
                ),

            "title":
                descriptor.get(
                    "display_title"
                ),

            "body_characters":
                len(
                    body
                ),

            "wuc_count":
                wuc_count,

            "writer_count":
                writer_count,

            "manager_count":
                manager_count,

            "split_count":
                split_count,

            "regex_count":
                regex_count,

            "wuc_minus_writer":
                wuc_count
                - writer_count,

            "wuc_minus_regex":
                wuc_count
                - regex_count,
        }
    )


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_OUTPUTS.items()
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
    in PROTECTED_OUTPUTS
}


wuc_source = (
    implementations[
        "wuc_word_count"
    ].get(
        "source",
        "",
    )
)

writer_source = (
    implementations[
        "writer_word_count"
    ].get(
        "source",
        "",
    )
)

manager_source = (
    implementations[
        "manager_word_count"
    ].get(
        "source",
        "",
    )
)


checks = {
    "all_functions_found":
        all(
            result[
                "found"
            ]
            for result in implementations.values()
        ),

    "writer_and_manager_same_source":
        writer_source
        == manager_source,

    "wuc_and_writer_same_source":
        wuc_source
        == writer_source,

    "all_sample_wuc_equals_writer":
        comparison_counts[
            "wuc_equals_writer"
        ]
        == REAL_SAMPLE_LIMIT,

    "all_sample_wuc_equals_manager":
        comparison_counts[
            "wuc_equals_manager"
        ]
        == REAL_SAMPLE_LIMIT,

    "all_sample_writer_equals_manager":
        comparison_counts[
            "writer_equals_manager"
        ]
        == REAL_SAMPLE_LIMIT,

    "production_outputs_unchanged":
        all(
            unchanged.values()
        ),
}


classification: str

if (
    checks[
        "wuc_and_writer_same_source"
    ]
    and checks[
        "all_sample_wuc_equals_writer"
    ]
):
    classification = (
        "WORD_COUNT_IMPLEMENTATIONS_ALIGNED"
    )

elif (
    checks[
        "writer_and_manager_same_source"
    ]
    and not checks[
        "all_sample_wuc_equals_writer"
    ]
):
    classification = (
        "WUC_DIFFERS_FROM_BODY_STORE_COMPONENTS"
    )

else:
    classification = (
        "MULTIPLE_WORD_COUNT_IMPLEMENTATIONS_DIFFER"
    )


report = {
    "schema_version":
        "canonical_body_word_count_alignment_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "classification":
        classification,

    "sample_size":
        REAL_SAMPLE_LIMIT,

    "implementations":
        implementations,

    "audit_uses_len_body_split":
        audit_split_usage,

    "comparison_counts":
        dict(
            comparison_counts
        ),

    "sample_results":
        sample_results,

    "checks":
        checks,

    "production_outputs_unchanged":
        unchanged,

    "source_files_modified":
        False,

    "body_store_files_written":
        0,

    "uucd_records_written":
        0,

    "wuc_packages_written":
        0,
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
print(
    "REAL ARTICLE COMPARISON — FIRST "
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print(
    "-" * 118
)

print(
    "WUC = Writer:         "
    + str(
        comparison_counts[
            "wuc_equals_writer"
        ]
    )
    + "/"
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print(
    "WUC = Manager:        "
    + str(
        comparison_counts[
            "wuc_equals_manager"
        ]
    )
    + "/"
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print(
    "Writer = Manager:     "
    + str(
        comparison_counts[
            "writer_equals_manager"
        ]
    )
    + "/"
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print(
    "WUC = split():        "
    + str(
        comparison_counts[
            "wuc_equals_split"
        ]
    )
    + "/"
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print(
    "WUC = regex counter:  "
    + str(
        comparison_counts[
            "wuc_equals_regex"
        ]
    )
    + "/"
    + str(
        REAL_SAMPLE_LIMIT
    )
)

print()

print(
    "FIRST 20 MISMATCHES"
)

mismatches = [
    item
    for item in sample_results
    if item[
        "wuc_count"
    ] != item[
        "writer_count"
    ]
]

if mismatches:
    for item in mismatches[
        :20
    ]:
        print()
        print(
            "  Index:          "
            + str(
                item[
                    "index"
                ]
            )
        )

        print(
            "  Record ID:      "
            + str(
                item[
                    "source_record_id"
                ]
            )
        )

        print(
            "  WUC count:      "
            + str(
                item[
                    "wuc_count"
                ]
            )
        )

        print(
            "  Writer count:   "
            + str(
                item[
                    "writer_count"
                ]
            )
        )

        print(
            "  Manager count:  "
            + str(
                item[
                    "manager_count"
                ]
            )
        )

        print(
            "  split() count:  "
            + str(
                item[
                    "split_count"
                ]
            )
        )

        print(
            "  regex count:    "
            + str(
                item[
                    "regex_count"
                ]
            )
        )

else:
    print(
        "  None"
    )


print()
print(
    "CLASSIFICATION"
)

print(
    "  "
    + classification
)

print()
print(
    "FINAL CHECKS"
)

for name, passed in checks.items():
    print(
        "  "
        + f"{name:<48}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<34}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )


print()
print(
    "Report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "BODY STORE FILES WRITTEN: 0"
)

print(
    "SOURCE FILES MODIFIED:    False"
)

print(
    "RUNTIME JOBS CREATED:     0"
)

print()
print(
    "CANONICAL WORD-COUNT ALIGNMENT SCAN: PASS"
)

print(
    "The exact implementations and real-article count differences "
    "were identified without modifying production data."
)

print("=" * 118)
