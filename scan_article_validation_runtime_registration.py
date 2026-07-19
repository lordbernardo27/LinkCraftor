"""Scan the current runtime foundation before registering Article Validation."""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


WORKSPACE_ID = "ws_whattoexpect_com"

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_runtime_registration_preflight.json"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "node_modules",
}

RUNTIME_FILENAME_TERMS = {
    "runtime",
    "registry",
    "orchestrat",
    "queue",
    "worker",
    "job",
    "task",
    "scheduler",
    "progress",
    "status",
    "retry",
    "dead_letter",
    "dispatcher",
}

RUNTIME_CONTENT_TERMS = {
    "job_registry",
    "task_registry",
    "runtime_registry",
    "register_job",
    "register_task",
    "job_type",
    "task_type",
    "enqueue",
    "queue_name",
    "worker",
    "progress",
    "job_status",
    "runtime_status",
    "dispatch",
    "orchestrator",
    "retry",
    "dead_letter",
}

ARTICLE_VALIDATION_TERMS = {
    "article_validation",
    "article-validation",
    "ARTICLE_VALIDATION",
}

INTEGRITY_TERMS = {
    "website_article_integrity",
    "website-article-integrity",
    "WEBSITE_ARTICLE_INTEGRITY",
}

REGISTRATION_NAME_HINTS = {
    "register",
    "registry",
    "job",
    "task",
    "handler",
    "worker",
    "dispatch",
    "execute",
    "run",
    "enqueue",
}


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


def relative(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(
                PROJECT_ROOT
            )
        )
    except ValueError:
        return str(path)


def read_text(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )


def matching_lines(
    text: str,
    terms: set[str],
    *,
    maximum: int = 30,
) -> list[dict[str, Any]]:
    lowered_terms = {
        term.casefold()
        for term in terms
    }

    matches: list[dict[str, Any]] = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lowered_line = line.casefold()

        matched_terms = sorted(
            term
            for term in lowered_terms
            if term in lowered_line
        )

        if not matched_terms:
            continue

        matches.append(
            {
                "line_number":
                    line_number,

                "matched_terms":
                    matched_terms,

                "line":
                    line.strip()[:500],
            }
        )

        if len(matches) >= maximum:
            break

    return matches


def parse_ast_details(
    path: Path,
    text: str,
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "syntax_valid":
            True,

        "syntax_error":
            None,

        "functions":
            [],

        "classes":
            [],

        "assignments":
            [],

        "decorators":
            [],

        "imports":
            [],
    }

    try:
        tree = ast.parse(
            text,
            filename=str(path),
        )

    except SyntaxError as exc:
        details[
            "syntax_valid"
        ] = False

        details[
            "syntax_error"
        ] = {
            "line_number":
                exc.lineno,

            "message":
                exc.msg,
        }

        return details

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            details[
                "functions"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,
                }
            )

            for decorator in node.decorator_list:
                try:
                    rendered = ast.unparse(
                        decorator
                    )

                except Exception:
                    rendered = (
                        decorator.__class__.__name__
                    )

                details[
                    "decorators"
                ].append(
                    {
                        "target":
                            node.name,

                        "target_type":
                            "function",

                        "line_number":
                            node.lineno,

                        "decorator":
                            rendered,
                    }
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            details[
                "classes"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,
                }
            )

            for decorator in node.decorator_list:
                try:
                    rendered = ast.unparse(
                        decorator
                    )

                except Exception:
                    rendered = (
                        decorator.__class__.__name__
                    )

                details[
                    "decorators"
                ].append(
                    {
                        "target":
                            node.name,

                        "target_type":
                            "class",

                        "line_number":
                            node.lineno,

                        "decorator":
                            rendered,
                    }
                )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            names: list[str] = []

            targets = (
                node.targets
                if isinstance(
                    node,
                    ast.Assign,
                )
                else [
                    node.target
                ]
            )

            for target in targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    names.append(
                        target.id
                    )

            for name in names:
                lowered_name = name.casefold()

                if any(
                    hint in lowered_name
                    for hint in (
                        "registry",
                        "jobs",
                        "tasks",
                        "handlers",
                        "workers",
                        "runtime",
                        "queue",
                    )
                ):
                    details[
                        "assignments"
                    ].append(
                        {
                            "name":
                                name,

                            "line_number":
                                node.lineno,
                        }
                    )

        elif isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                details[
                    "imports"
                ].append(
                    {
                        "module":
                            alias.name,

                        "line_number":
                            node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            for alias in node.names:
                details[
                    "imports"
                ].append(
                    {
                        "module":
                            (
                                module
                                + "."
                                + alias.name
                            ).strip("."),

                        "line_number":
                            node.lineno,
                    }
                )

    details[
        "functions"
    ].sort(
        key=lambda item: (
            item[
                "line_number"
            ],
            item[
                "name"
            ],
        )
    )

    details[
        "classes"
    ].sort(
        key=lambda item: (
            item[
                "line_number"
            ],
            item[
                "name"
            ],
        )
    )

    details[
        "assignments"
    ].sort(
        key=lambda item: (
            item[
                "line_number"
            ],
            item[
                "name"
            ],
        )
    )

    details[
        "decorators"
    ].sort(
        key=lambda item: (
            item[
                "line_number"
            ],
            item[
                "target"
            ],
        )
    )

    return details


def likely_registration_symbols(
    ast_details: dict[str, Any],
) -> list[dict[str, Any]]:
    symbols: list[
        dict[str, Any]
    ] = []

    for symbol_type in (
        "functions",
        "classes",
        "assignments",
    ):
        for item in ast_details.get(
            symbol_type,
            [],
        ):
            name = str(
                item.get(
                    "name"
                )
                or ""
            )

            lowered = name.casefold()

            if any(
                hint in lowered
                for hint in REGISTRATION_NAME_HINTS
            ):
                symbols.append(
                    {
                        "symbol_type":
                            symbol_type.rstrip(
                                "s"
                            ),

                        "name":
                            name,

                        "line_number":
                            item.get(
                                "line_number"
                            ),
                    }
                )

    return symbols


def write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if not SERVER_ROOT.is_dir():
    raise FileNotFoundError(
        "Backend server root is missing: "
        + str(
            SERVER_ROOT
        )
    )


python_files = sorted(
    (
        path
        for path in SERVER_ROOT.rglob(
            "*.py"
        )
        if (
            path.is_file()
            and not excluded(
                path
            )
        )
    ),
    key=lambda path: (
        path.as_posix()
    ),
)


runtime_candidates: list[
    dict[str, Any]
] = []

article_validation_references: list[
    dict[str, Any]
] = []

integrity_references: list[
    dict[str, Any]
] = []

runtime_term_counts: Counter[str] = Counter()

syntax_failure_files: list[str] = []


for path in python_files:
    text = read_text(
        path
    )

    lowered_path = relative(
        path
    ).casefold()

    lowered_text = text.casefold()

    filename_matches = sorted(
        term
        for term in RUNTIME_FILENAME_TERMS
        if term in lowered_path
    )

    content_matches = sorted(
        term
        for term in RUNTIME_CONTENT_TERMS
        if term in lowered_text
    )

    for term in content_matches:
        runtime_term_counts[
            term
        ] += 1

    ast_details = parse_ast_details(
        path,
        text,
    )

    if not ast_details[
        "syntax_valid"
    ]:
        syntax_failure_files.append(
            relative(
                path
            )
        )

    if (
        filename_matches
        or content_matches
    ):
        runtime_candidates.append(
            {
                "path":
                    relative(
                        path
                    ),

                "filename_matches":
                    filename_matches,

                "content_matches":
                    content_matches,

                "likely_registration_symbols":
                    likely_registration_symbols(
                        ast_details
                    ),

                "registry_assignments":
                    ast_details.get(
                        "assignments",
                        [],
                    ),

                "decorators":
                    ast_details.get(
                        "decorators",
                        [],
                    )[:30],

                "runtime_lines":
                    matching_lines(
                        text,
                        RUNTIME_CONTENT_TERMS,
                        maximum=30,
                    ),

                "syntax_valid":
                    ast_details[
                        "syntax_valid"
                    ],
            }
        )

    article_matches = matching_lines(
        text,
        ARTICLE_VALIDATION_TERMS,
        maximum=50,
    )

    if article_matches:
        article_validation_references.append(
            {
                "path":
                    relative(
                        path
                    ),

                "matches":
                    article_matches,

                "likely_registration_symbols":
                    likely_registration_symbols(
                        ast_details
                    ),
            }
        )

    integrity_matches = matching_lines(
        text,
        INTEGRITY_TERMS,
        maximum=50,
    )

    if integrity_matches:
        integrity_references.append(
            {
                "path":
                    relative(
                        path
                    ),

                "matches":
                    integrity_matches,

                "likely_registration_symbols":
                    likely_registration_symbols(
                        ast_details
                    ),
            }
        )


runtime_candidates.sort(
    key=lambda item: (
        -len(
            item[
                "filename_matches"
            ]
        ),
        -len(
            item[
                "content_matches"
            ]
        ),
        item[
            "path"
        ],
    )
)


high_priority_candidates = [
    candidate
    for candidate in runtime_candidates
    if (
        candidate[
            "likely_registration_symbols"
        ]
        or candidate[
            "registry_assignments"
        ]
        or candidate[
            "decorators"
        ]
    )
]


existing_article_validation_registration_signals = []

for reference in article_validation_references:
    path_text = reference[
        "path"
    ].casefold()

    match_text = " ".join(
        match[
            "line"
        ].casefold()
        for match in reference[
            "matches"
        ]
    )

    if any(
        term in (
            path_text
            + " "
            + match_text
        )
        for term in (
            "register",
            "registry",
            "job_type",
            "task_type",
            "handler",
            "queue",
            "worker",
            "dispatch",
        )
    ):
        existing_article_validation_registration_signals.append(
            reference
        )


integrity_registration_candidates = []

for reference in integrity_references:
    path_text = reference[
        "path"
    ].casefold()

    match_text = " ".join(
        match[
            "line"
        ].casefold()
        for match in reference[
            "matches"
        ]
    )

    if any(
        term in (
            path_text
            + " "
            + match_text
        )
        for term in (
            "register",
            "registry",
            "job_type",
            "task_type",
            "handler",
            "queue",
            "worker",
            "dispatch",
            "runtime",
        )
    ):
        integrity_registration_candidates.append(
            reference
        )


report = {
    "schema_version":
        "article_validation_runtime_registration_preflight_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "python_files_scanned":
        len(
            python_files
        ),

    "runtime_candidate_count":
        len(
            runtime_candidates
        ),

    "high_priority_runtime_candidate_count":
        len(
            high_priority_candidates
        ),

    "article_validation_reference_file_count":
        len(
            article_validation_references
        ),

    "integrity_reference_file_count":
        len(
            integrity_references
        ),

    "existing_article_validation_registration_signal_count":
        len(
            existing_article_validation_registration_signals
        ),

    "integrity_registration_candidate_count":
        len(
            integrity_registration_candidates
        ),

    "syntax_failure_files":
        syntax_failure_files,

    "runtime_term_file_counts":
        dict(
            runtime_term_counts.most_common()
        ),

    "high_priority_runtime_candidates":
        high_priority_candidates[:40],

    "all_runtime_candidates":
        runtime_candidates[:100],

    "article_validation_references":
        article_validation_references,

    "existing_article_validation_registration_signals":
        existing_article_validation_registration_signals,

    "integrity_registration_candidates":
        integrity_registration_candidates,

    "source_files_modified":
        False,

    "runtime_configuration_modified":
        False,

    "jobs_enqueued":
        False,

    "workers_started":
        False,

    "article_validation_executed":
        False,
}


write_json(
    REPORT_PATH,
    report,
)


print()
print("=" * 104)
print(
    "ARTICLE VALIDATION RUNTIME REGISTRATION — PREFLIGHT SCAN"
)
print("=" * 104)
print()

print(
    "Python files scanned:                         "
    + str(
        report[
            "python_files_scanned"
        ]
    )
)

print(
    "Runtime candidate files:                     "
    + str(
        report[
            "runtime_candidate_count"
        ]
    )
)

print(
    "High-priority runtime candidates:            "
    + str(
        report[
            "high_priority_runtime_candidate_count"
        ]
    )
)

print(
    "Website Article Integrity registration candidates: "
    + str(
        report[
            "integrity_registration_candidate_count"
        ]
    )
)

print(
    "Existing Article Validation registration signals:  "
    + str(
        report[
            "existing_article_validation_registration_signal_count"
        ]
    )
)

print(
    "Python syntax failures:                      "
    + str(
        len(
            syntax_failure_files
        )
    )
)

print()
print(
    "HIGH-PRIORITY RUNTIME FILES"
)

if high_priority_candidates:
    for candidate in high_priority_candidates[
        :20
    ]:
        print()
        print(
            "  "
            + candidate[
                "path"
            ]
        )

        if candidate[
            "likely_registration_symbols"
        ]:
            symbols = ", ".join(
                (
                    symbol[
                        "name"
                    ]
                    + "@"
                    + str(
                        symbol[
                            "line_number"
                        ]
                    )
                )
                for symbol
                in candidate[
                    "likely_registration_symbols"
                ][
                    :12
                ]
            )

            print(
                "    Symbols: "
                + symbols
            )

        if candidate[
            "registry_assignments"
        ]:
            assignments = ", ".join(
                (
                    assignment[
                        "name"
                    ]
                    + "@"
                    + str(
                        assignment[
                            "line_number"
                        ]
                    )
                )
                for assignment
                in candidate[
                    "registry_assignments"
                ][
                    :12
                ]
            )

            print(
                "    Registries: "
                + assignments
            )

else:
    print(
        "  No high-priority runtime files detected."
    )

print()
print(
    "WEBSITE ARTICLE INTEGRITY RUNTIME CANDIDATES"
)

if integrity_registration_candidates:
    for candidate in integrity_registration_candidates[
        :20
    ]:
        print(
            "  "
            + candidate[
                "path"
            ]
        )

else:
    print(
        "  No Integrity runtime registration candidate detected."
    )

print()
print(
    "ARTICLE VALIDATION EXISTING REGISTRATION SIGNALS"
)

if existing_article_validation_registration_signals:
    for candidate in (
        existing_article_validation_registration_signals[
            :20
        ]
    ):
        print(
            "  "
            + candidate[
                "path"
            ]
        )

else:
    print(
        "  No existing Article Validation runtime registration detected."
    )

print()
print(
    "Source files modified:                       False"
)

print(
    "Runtime configuration modified:              False"
)

print(
    "Jobs enqueued:                               False"
)

print(
    "Workers started:                             False"
)

print(
    "Article Validation executed:                 False"
)

print()
print(
    "Preflight report: "
    + str(
        REPORT_PATH
    )
)

print()
print(
    "ARTICLE VALIDATION RUNTIME REGISTRATION PREFLIGHT: PASS"
)

print(
    "The current runtime foundation was scanned without modification."
)

print("=" * 104)
