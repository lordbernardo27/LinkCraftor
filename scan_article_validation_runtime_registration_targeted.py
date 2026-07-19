"""Targeted read-only scan for Article Validation Runtime Registration."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

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

PREFLIGHT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_runtime_registration_preflight.json"
)

OUTPUT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_runtime_registration_targeted_scan.json"
)

CANONICAL_REGISTRAR_PATH = (
    SERVER_ROOT
    / "runtime"
    / "universal_runtime_registration.py"
)

INTEGRITY_REGISTRATION_PATH = (
    SERVER_ROOT
    / "integrity"
    / "website_article_integrity"
    / "website_article_integrity_runtime_registration.py"
)

INTEGRITY_AUTOMATION_PATH = (
    SERVER_ROOT
    / "runtime"
    / "website_article_integrity_automation.py"
)

ARTICLE_VALIDATION_REGISTRATION_PATH = (
    SERVER_ROOT
    / "article_validation"
    / "article_validation_runtime_registration.py"
)

ARTICLE_VALIDATION_RUNNER_PATH = (
    SERVER_ROOT
    / "article_validation"
    / "article_validation_runner_v3.py"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


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


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


def render_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    arguments: list[str] = []

    positional = (
        list(
            node.args.posonlyargs
        )
        + list(
            node.args.args
        )
    )

    defaults_offset = (
        len(positional)
        - len(node.args.defaults)
    )

    for index, argument in enumerate(
        positional
    ):
        rendered = argument.arg

        default_index = (
            index
            - defaults_offset
        )

        if default_index >= 0:
            try:
                default_value = ast.unparse(
                    node.args.defaults[
                        default_index
                    ]
                )

            except Exception:
                default_value = "..."

            rendered += (
                "="
                + default_value
            )

        arguments.append(
            rendered
        )

    if node.args.vararg:
        arguments.append(
            "*"
            + node.args.vararg.arg
        )

    elif node.args.kwonlyargs:
        arguments.append("*")

    for argument, default in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
    ):
        rendered = argument.arg

        if default is not None:
            try:
                rendered += (
                    "="
                    + ast.unparse(
                        default
                    )
                )

            except Exception:
                rendered += "=..."

        arguments.append(
            rendered
        )

    if node.args.kwarg:
        arguments.append(
            "**"
            + node.args.kwarg.arg
        )

    prefix = (
        "async def "
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        else "def "
    )

    return (
        prefix
        + node.name
        + "("
        + ", ".join(
            arguments
        )
        + ")"
    )


def inspect_python_file(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "exists":
            path.is_file(),

        "syntax_valid":
            None,

        "syntax_error":
            None,

        "functions":
            [],

        "classes":
            [],

        "important_assignments":
            [],

        "registration_calls":
            [],

        "decorators":
            [],

        "job_type_literals":
            [],

        "handler_references":
            [],
    }

    if not path.is_file():
        return result

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        result[
            "syntax_valid"
        ] = False

        result[
            "syntax_error"
        ] = {
            "line_number":
                exc.lineno,

            "offset":
                exc.offset,

            "message":
                exc.msg,

            "text":
                str(
                    exc.text or ""
                ).strip(),
        }

        return result

    result[
        "syntax_valid"
    ] = True

    important_names = {
        "REGISTRY_ROOT",
        "REGISTRY_PATH",
        "RUNTIME_JOB_TYPE",
        "JOB_TYPE",
        "QUEUE_NAME",
        "HANDLER_REFERENCE",
        "REGISTRATION_VERSION",
        "RUNTIME_REGISTRATION_VERSION",
        "RUNTIME_STAGE_REGISTRY",
    }

    registration_function_names = {
        "register_runtime_handler",
        "runtime_handler",
        "unregister_runtime_handler",
        "has_runtime_handler",
        "is_runtime_job_type_registered",
    }

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            result[
                "functions"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,

                    "signature":
                        render_signature(
                            node
                        ),
                }
            )

            for decorator in (
                node.decorator_list
            ):
                try:
                    rendered = ast.unparse(
                        decorator
                    )

                except Exception:
                    rendered = (
                        decorator.__class__.__name__
                    )

                result[
                    "decorators"
                ].append(
                    {
                        "target":
                            node.name,

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
            result[
                "classes"
            ].append(
                {
                    "name":
                        node.name,

                    "line_number":
                        node.lineno,
                }
            )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
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
                if not isinstance(
                    target,
                    ast.Name,
                ):
                    continue

                name = target.id

                if (
                    name in important_names
                    or "REGISTRY" in name
                    or "JOB_TYPE" in name
                    or "HANDLER" in name
                    or "QUEUE" in name
                ):
                    value_node = (
                        node.value
                    )

                    try:
                        rendered_value = ast.unparse(
                            value_node
                        )

                    except Exception:
                        rendered_value = "..."

                    result[
                        "important_assignments"
                    ].append(
                        {
                            "name":
                                name,

                            "line_number":
                                node.lineno,

                            "value":
                                rendered_value[:1000],
                        }
                    )

        elif isinstance(
            node,
            ast.Call,
        ):
            called_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                called_name = (
                    node.func.id
                )

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                called_name = (
                    node.func.attr
                )

            if (
                called_name
                in registration_function_names
            ):
                try:
                    rendered_call = ast.unparse(
                        node
                    )

                except Exception:
                    rendered_call = called_name

                result[
                    "registration_calls"
                ].append(
                    {
                        "function":
                            called_name,

                        "line_number":
                            node.lineno,

                        "call":
                            rendered_call[:2000],
                    }
                )

        elif isinstance(
            node,
            ast.Constant,
        ) and isinstance(
            node.value,
            str,
        ):
            value = node.value

            lowered = value.casefold()

            if (
                "article_validation"
                in lowered
                or "website_article_integrity"
                in lowered
                or (
                    "job"
                    in lowered
                    and len(value) <= 150
                )
            ):
                result[
                    "job_type_literals"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "value":
                            value,
                    }
                )

            if (
                ":" in value
                and (
                    "backend.server"
                    in value
                    or "article_validation"
                    in lowered
                    or "website_article_integrity"
                    in lowered
                )
            ):
                result[
                    "handler_references"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "value":
                            value,
                    }
                )

    for key in (
        "functions",
        "classes",
        "important_assignments",
        "registration_calls",
        "decorators",
        "job_type_literals",
        "handler_references",
    ):
        result[
            key
        ].sort(
            key=lambda item: (
                int(
                    item.get(
                        "line_number"
                    )
                    or 0
                ),
                str(item),
            )
        )

    return result


def source_excerpts(
    path: Path,
    terms: set[str],
    *,
    context_lines: int = 3,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []

    lines = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    ).splitlines()

    matched_ranges: list[
        tuple[int, int]
    ] = []

    lowered_terms = {
        term.casefold()
        for term in terms
    }

    for index, line in enumerate(
        lines
    ):
        lowered_line = line.casefold()

        if not any(
            term in lowered_line
            for term in lowered_terms
        ):
            continue

        start = max(
            0,
            index - context_lines,
        )

        end = min(
            len(lines),
            index + context_lines + 1,
        )

        matched_ranges.append(
            (
                start,
                end,
            )
        )

    merged: list[
        tuple[int, int]
    ] = []

    for start, end in (
        matched_ranges
    ):
        if (
            merged
            and start
            <= merged[-1][1]
        ):
            merged[-1] = (
                merged[-1][0],
                max(
                    merged[-1][1],
                    end,
                ),
            )

        else:
            merged.append(
                (
                    start,
                    end,
                )
            )

    excerpts: list[
        dict[str, Any]
    ] = []

    for start, end in merged[
        :20
    ]:
        excerpts.append(
            {
                "start_line":
                    start + 1,

                "end_line":
                    end,

                "lines":
                    [
                        {
                            "line_number":
                                line_number + 1,

                            "text":
                                lines[
                                    line_number
                                ][:1000],
                        }
                        for line_number
                        in range(
                            start,
                            end,
                        )
                    ],
            }
        )

    return excerpts


if not PREFLIGHT_REPORT_PATH.is_file():
    raise FileNotFoundError(
        "Runtime preflight report is missing: "
        + str(
            PREFLIGHT_REPORT_PATH
        )
    )

preflight = load_json(
    PREFLIGHT_REPORT_PATH
)

syntax_failure_files = [
    str(value)
    for value in (
        preflight.get(
            "syntax_failure_files"
        )
        or []
    )
]

syntax_failure_details: list[
    dict[str, Any]
] = []

for relative_path in (
    syntax_failure_files
):
    path = (
        PROJECT_ROOT
        / relative_path
    ).resolve()

    syntax_failure_details.append(
        inspect_python_file(
            path
        )
    )


canonical_registrar = inspect_python_file(
    CANONICAL_REGISTRAR_PATH
)

integrity_registration = inspect_python_file(
    INTEGRITY_REGISTRATION_PATH
)

integrity_automation = inspect_python_file(
    INTEGRITY_AUTOMATION_PATH
)

article_validation_runner = inspect_python_file(
    ARTICLE_VALIDATION_RUNNER_PATH
)

article_validation_registration_exists = (
    ARTICLE_VALIDATION_REGISTRATION_PATH.is_file()
)


registry_files: list[
    dict[str, Any]
] = []

for path in DATA_ROOT.rglob(
    "*.json"
):
    if excluded(
        path
    ):
        continue

    lowered_name = path.name.casefold()
    lowered_path = relative(
        path
    ).casefold()

    if not (
        "registry"
        in lowered_name
        or "runtime_registration"
        in lowered_path
        or "runtime_registry"
        in lowered_path
    ):
        continue

    entry: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "size_bytes":
            path.stat().st_size,

        "contains_article_validation":
            False,

        "contains_website_article_integrity":
            False,

        "top_level_type":
            None,

        "top_level_keys":
            [],
    }

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    entry[
        "contains_article_validation"
    ] = (
        "article_validation"
        in text.casefold()
    )

    entry[
        "contains_website_article_integrity"
    ] = (
        "website_article_integrity"
        in text.casefold()
    )

    try:
        value = json.loads(
            text
        )

        entry[
            "top_level_type"
        ] = type(value).__name__

        if isinstance(
            value,
            dict,
        ):
            entry[
                "top_level_keys"
            ] = sorted(
                str(key)
                for key
                in value.keys()
            )[:50]

    except Exception as exc:
        entry[
            "json_error"
        ] = str(exc)

    registry_files.append(
        entry
    )

registry_files.sort(
    key=lambda item: (
        item[
            "path"
        ]
    )
)


report = {
    "schema_version":
        "article_validation_runtime_registration_targeted_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "preflight_syntax_failure_files":
        syntax_failure_files,

    "syntax_failure_details":
        syntax_failure_details,

    "canonical_registrar":
        canonical_registrar,

    "canonical_registrar_excerpts":
        source_excerpts(
            CANONICAL_REGISTRAR_PATH,
            {
                "register_runtime_handler",
                "runtime_handler",
                "REGISTRY_PATH",
                "persist",
                "handler_reference",
            },
        ),

    "integrity_registration":
        integrity_registration,

    "integrity_registration_excerpts":
        source_excerpts(
            INTEGRITY_REGISTRATION_PATH,
            {
                "register_runtime_handler",
                "runtime_handler",
                "job_type",
                "handler",
                "registration",
            },
        ),

    "integrity_automation":
        integrity_automation,

    "integrity_automation_excerpts":
        source_excerpts(
            INTEGRITY_AUTOMATION_PATH,
            {
                "website_article_integrity",
                "enqueue",
                "execute",
                "register",
                "runtime",
            },
        ),

    "article_validation_runner":
        article_validation_runner,

    "article_validation_registration_path":
        relative(
            ARTICLE_VALIDATION_REGISTRATION_PATH
        ),

    "article_validation_registration_exists":
        article_validation_registration_exists,

    "active_registry_files":
        registry_files,

    "runtime_backups_excluded":
        True,

    "source_files_modified":
        False,

    "runtime_registry_modified":
        False,

    "jobs_enqueued":
        False,

    "workers_started":
        False,
}


write_json(
    OUTPUT_REPORT_PATH,
    report,
)


print()
print("=" * 108)
print(
    "ARTICLE VALIDATION RUNTIME REGISTRATION — TARGETED ACTIVE SCAN"
)
print("=" * 108)
print()

print(
    "Canonical registrar exists:              "
    + str(
        CANONICAL_REGISTRAR_PATH.is_file()
    )
)

print(
    "Canonical registrar syntax valid:        "
    + str(
        canonical_registrar[
            "syntax_valid"
        ]
    )
)

print(
    "Integrity registration exists:           "
    + str(
        INTEGRITY_REGISTRATION_PATH.is_file()
    )
)

print(
    "Integrity registration syntax valid:     "
    + str(
        integrity_registration[
            "syntax_valid"
        ]
    )
)

print(
    "Article Validation runner exists:        "
    + str(
        ARTICLE_VALIDATION_RUNNER_PATH.is_file()
    )
)

print(
    "Article Validation registration exists:  "
    + str(
        article_validation_registration_exists
    )
)

print(
    "Active registry JSON files found:        "
    + str(
        len(
            registry_files
        )
    )
)

print(
    "Preflight syntax-failure files:          "
    + str(
        len(
            syntax_failure_files
        )
    )
)

print()
print(
    "PREFLIGHT SYNTAX FAILURE DETAILS"
)

if syntax_failure_details:
    for detail in (
        syntax_failure_details
    ):
        print(
            "  File: "
            + detail[
                "path"
            ]
        )

        print(
            "  Syntax valid: "
            + str(
                detail[
                    "syntax_valid"
                ]
            )
        )

        if detail[
            "syntax_error"
        ]:
            print(
                "  Error: "
                + json.dumps(
                    detail[
                        "syntax_error"
                    ],
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )

        print()

else:
    print(
        "  None"
    )

print(
    "CANONICAL REGISTRAR REGISTRATION FUNCTIONS"
)

registrar_functions = [
    function
    for function
    in canonical_registrar[
        "functions"
    ]
    if any(
        term in function[
            "name"
        ].casefold()
        for term in (
            "register",
            "handler",
            "persist",
            "load",
        )
    )
]

for function in (
    registrar_functions
):
    print(
        "  "
        + function[
            "signature"
        ]
        + " @ line "
        + str(
            function[
                "line_number"
            ]
        )
    )

print()
print(
    "INTEGRITY REGISTRATION CALLS"
)

if integrity_registration[
    "registration_calls"
]:
    for call in (
        integrity_registration[
            "registration_calls"
        ]
    ):
        print(
            "  "
            + call[
                "function"
            ]
            + " @ line "
            + str(
                call[
                    "line_number"
                ]
            )
        )

        print(
            "    "
            + call[
                "call"
            ]
        )

else:
    print(
        "  No direct registration calls detected."
    )

print()
print(
    "INTEGRITY JOB/HANDLER LITERALS"
)

combined_literals = (
    integrity_registration[
        "job_type_literals"
    ]
    + integrity_registration[
        "handler_references"
    ]
)

if combined_literals:
    seen: set[
        tuple[int, str]
    ] = set()

    for item in combined_literals:
        key = (
            int(
                item[
                    "line_number"
                ]
            ),
            str(
                item[
                    "value"
                ]
            ),
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        print(
            "  line "
            + str(
                item[
                    "line_number"
                ]
            )
            + ": "
            + str(
                item[
                    "value"
                ]
            )
        )

else:
    print(
        "  None detected."
    )

print()
print(
    "ACTIVE REGISTRY FILES"
)

if registry_files:
    for registry in registry_files:
        print(
            "  "
            + registry[
                "path"
            ]
        )

        print(
            "    Contains Integrity registration: "
            + str(
                registry[
                    "contains_website_article_integrity"
                ]
            )
        )

        print(
            "    Contains Article Validation registration: "
            + str(
                registry[
                    "contains_article_validation"
                ]
            )
        )

else:
    print(
        "  No active registry JSON files detected."
    )

print()
print(
    "Runtime backups excluded:                 True"
)

print(
    "Source files modified:                    False"
)

print(
    "Runtime registry modified:                False"
)

print(
    "Jobs enqueued:                            False"
)

print(
    "Workers started:                          False"
)

print()
print(
    "Targeted report: "
    + str(
        OUTPUT_REPORT_PATH
    )
)

print()
print(
    "ARTICLE VALIDATION RUNTIME REGISTRATION "
    "TARGETED SCAN: PASS"
)

print(
    "The active registration contract was inspected "
    "without modifying runtime state."
)

print("=" * 108)
