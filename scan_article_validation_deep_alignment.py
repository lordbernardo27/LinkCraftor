"""Deep read-only alignment scan for Article Validation."""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
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

INITIAL_SCAN_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_stage_scan.json"
)

REPORT_ROOT = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
)

REPORT_PATH = (
    REPORT_ROOT
    / "article_validation_deep_alignment_scan.json"
)

INTEGRITY_CERTIFICATE_PATH = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
    / "certification"
    / "website_article_integrity_certificate.json"
)

BODY_FIELDS = {
    "article_body",
    "content_body",
    "body_text",
    "article_text",
    "content",
    "html",
    "body_html",
}

LEGACY_COUNTS = {
    2225,
    2224,
    2203,
    22,
}

CURRENT_COUNTS = {
    2219,
}

IMPORTANT_REFERENCE_TERMS = {
    "integrity_certificate": (
        "website_article_integrity_certificate",
        "active_certified_count",
        "website_article_integrity/certification",
        "website_article_integrity\\certification",
    ),
    "udare_store": (
        "udare_store",
        "udare store",
    ),
    "wuc": (
        "website_unified_content",
        "website unified content",
    ),
    "runtime_registration": (
        "register_runtime_handler",
        "register_universal_runtime_handler",
        "universal_runtime_registration",
    ),
    "article_body": tuple(
        sorted(BODY_FIELDS)
    ),
}

WRITE_METHODS = {
    "write",
    "writelines",
    "write_text",
    "write_bytes",
    "dump",
    "dumps",
    "replace",
    "rename",
    "unlink",
    "mkdir",
    "touch",
}

ENTRYPOINT_TERMS = (
    "run",
    "execute",
    "validate",
    "build",
    "generate",
    "process",
    "orchestrate",
    "create",
)

VALIDATION_TERMS = (
    "article_validation",
    "article_validator",
    "validate_article",
    "validation_engine",
    "validation_result",
    "eligible_for_wuc",
)

EXCLUDED_PATH_PARTS = {
    "__pycache__",
    "backups",
    "runtime_backups",
    ".venv",
    "node_modules",
}


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def relative(
    path: Path,
) -> str:
    try:
        return path.relative_to(
            PROJECT_ROOT
        ).as_posix()
    except ValueError:
        return str(path)


def load_json(
    path: Path,
) -> Any:
    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )


def normalize_report_path(
    value: Any,
) -> Path:
    text = str(
        value or ""
    ).strip()

    if not text:
        return PROJECT_ROOT

    path = Path(text)

    if path.is_absolute():
        return path

    return (
        PROJECT_ROOT
        / path
    ).resolve()


def function_arguments(
    node: ast.FunctionDef
    | ast.AsyncFunctionDef,
) -> list[str]:
    arguments: list[str] = []

    for argument in (
        list(node.args.posonlyargs)
        + list(node.args.args)
        + list(node.args.kwonlyargs)
    ):
        arguments.append(
            argument.arg
        )

    if node.args.vararg:
        arguments.append(
            "*" + node.args.vararg.arg
        )

    if node.args.kwarg:
        arguments.append(
            "**" + node.args.kwarg.arg
        )

    return arguments


def call_name(
    node: ast.Call,
) -> str:
    function = node.func

    if isinstance(
        function,
        ast.Name,
    ):
        return function.id

    if isinstance(
        function,
        ast.Attribute,
    ):
        parts: list[str] = []
        current: ast.AST = function

        while isinstance(
            current,
            ast.Attribute,
        ):
            parts.append(
                current.attr
            )
            current = current.value

        if isinstance(
            current,
            ast.Name,
        ):
            parts.append(
                current.id
            )

        return ".".join(
            reversed(parts)
        )

    return ""


def literal_subscript_key(
    node: ast.Subscript,
) -> str | None:
    slice_node = node.slice

    if isinstance(
        slice_node,
        ast.Constant,
    ) and isinstance(
        slice_node.value,
        str,
    ):
        return slice_node.value

    return None


def body_mutation_signals(
    tree: ast.AST,
    source_lines: list[str],
) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        targets: list[ast.AST] = []

        if isinstance(
            node,
            ast.Assign,
        ):
            targets.extend(
                node.targets
            )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            targets.append(
                node.target
            )

        elif isinstance(
            node,
            ast.AugAssign,
        ):
            targets.append(
                node.target
            )

        for target in targets:
            if isinstance(
                target,
                ast.Subscript,
            ):
                key = literal_subscript_key(
                    target
                )

                if (
                    key
                    and key.lower()
                    in BODY_FIELDS
                ):
                    signals.append(
                        {
                            "line": getattr(
                                node,
                                "lineno",
                                None,
                            ),
                            "field": key,
                            "type": (
                                "BODY_FIELD_ASSIGNMENT"
                            ),
                            "text": (
                                source_lines[
                                    node.lineno - 1
                                ].strip()[:500]
                                if getattr(
                                    node,
                                    "lineno",
                                    None,
                                )
                                else ""
                            ),
                        }
                    )

            elif isinstance(
                target,
                ast.Attribute,
            ):
                if (
                    target.attr.lower()
                    in BODY_FIELDS
                ):
                    signals.append(
                        {
                            "line": getattr(
                                node,
                                "lineno",
                                None,
                            ),
                            "field": target.attr,
                            "type": (
                                "BODY_ATTRIBUTE_ASSIGNMENT"
                            ),
                            "text": (
                                source_lines[
                                    node.lineno - 1
                                ].strip()[:500]
                                if getattr(
                                    node,
                                    "lineno",
                                    None,
                                )
                                else ""
                            ),
                        }
                    )

    return signals


def classify_source_role(
    path: Path,
    functions: list[dict[str, Any]],
    classes: list[dict[str, Any]],
) -> str:
    lowered_path = path.as_posix().lower()
    function_names = {
        item["name"].lower()
        for item in functions
    }

    class_names = {
        item["name"].lower()
        for item in classes
    }

    if (
        "test" in path.name.lower()
        or "/tests/" in lowered_path
        or "\\tests\\" in lowered_path
    ):
        return "TEST_OR_VERIFICATION"

    if "/routes/" in lowered_path:
        return "API_ROUTE"

    if (
        "/workers/" in lowered_path
        or "worker" in path.name.lower()
    ):
        return "WORKER"

    if (
        "/jobs/" in lowered_path
        or "orchestrator" in path.name.lower()
    ):
        return "ORCHESTRATION"

    if (
        "/stores/" in lowered_path
        or "store" in path.name.lower()
    ):
        return "STORE_OR_ADAPTER"

    if any(
        "validate" in name
        or "validation" in name
        for name in (
            function_names
            | class_names
        )
    ):
        return "VALIDATION_ENGINE"

    return "SUPPORTING_MODULE"


def canonical_score(
    *,
    path: Path,
    role: str,
    functions: list[dict[str, Any]],
    references: dict[str, bool],
    output_paths: list[str],
    write_calls: list[dict[str, Any]],
) -> int:
    score = 0
    lowered_path = path.as_posix().lower()

    if role == "VALIDATION_ENGINE":
        score += 10

    if role == "ORCHESTRATION":
        score += 7

    if role == "WORKER":
        score += 6

    if role == "API_ROUTE":
        score += 2

    if role == "TEST_OR_VERIFICATION":
        score -= 10

    if "article_validation" in lowered_path:
        score += 5

    if references.get(
        "integrity_certificate"
    ):
        score += 8

    if references.get(
        "udare_store"
    ):
        score += 4

    if references.get("wuc"):
        score += 2

    if references.get(
        "runtime_registration"
    ):
        score += 2

    entrypoints = [
        function
        for function in functions
        if (
            any(
                function["name"].lower().startswith(
                    term
                )
                for term in ENTRYPOINT_TERMS
            )
            and (
                "validat"
                in function["name"].lower()
                or "article"
                in function["name"].lower()
            )
        )
    ]

    score += min(
        len(entrypoints) * 3,
        12,
    )

    if output_paths:
        score += 2

    if write_calls:
        score += 1

    return score


def scan_source(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    source_lines = source.splitlines()
    lowered_source = source.lower()

    result: dict[str, Any] = {
        "path": relative(path),
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size,
        "syntax_valid": False,
        "syntax_error": None,
        "role": None,
        "canonical_score": 0,
        "imports": [],
        "functions": [],
        "classes": [],
        "references": {},
        "reference_lines": {},
        "write_calls": [],
        "output_path_literals": [],
        "body_mutation_signals": [],
    }

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

        result["syntax_valid"] = True

    except SyntaxError as exc:
        result["syntax_error"] = {
            "line": exc.lineno,
            "offset": exc.offset,
            "message": str(exc),
        }

        return result

    imports: list[str] = []
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    write_calls: list[dict[str, Any]] = []
    output_path_literals: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            for alias in node.names:
                imports.append(
                    (
                        module
                        + "."
                        + alias.name
                    ).strip(".")
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "arguments": (
                        function_arguments(node)
                    ),
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                }
            )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            name = call_name(node)
            method = name.split(".")[-1]

            if method in WRITE_METHODS:
                write_calls.append(
                    {
                        "line": getattr(
                            node,
                            "lineno",
                            None,
                        ),
                        "call": name,
                        "text": (
                            source_lines[
                                node.lineno - 1
                            ].strip()[:500]
                            if getattr(
                                node,
                                "lineno",
                                None,
                            )
                            else ""
                        ),
                    }
                )

        elif isinstance(
            node,
            ast.Constant,
        ) and isinstance(
            node.value,
            str,
        ):
            value = node.value.strip()
            lowered_value = value.lower()

            if (
                any(
                    suffix in lowered_value
                    for suffix in (
                        ".json",
                        ".jsonl",
                        ".html",
                        ".txt",
                    )
                )
                and (
                    "validation"
                    in lowered_value
                    or "article"
                    in lowered_value
                    or "eligible"
                    in lowered_value
                )
            ):
                output_path_literals.add(
                    value[:1000]
                )

    references: dict[str, bool] = {}
    reference_lines: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for reference_name, terms in (
        IMPORTANT_REFERENCE_TERMS.items()
    ):
        references[
            reference_name
        ] = any(
            term.lower()
            in lowered_source
            for term in terms
        )

        matches: list[
            dict[str, Any]
        ] = []

        for line_number, line in enumerate(
            source_lines,
            start=1,
        ):
            lowered_line = line.lower()

            if any(
                term.lower()
                in lowered_line
                for term in terms
            ):
                matches.append(
                    {
                        "line": line_number,
                        "text": (
                            line.strip()[:500]
                        ),
                    }
                )

                if len(matches) >= 20:
                    break

        reference_lines[
            reference_name
        ] = matches

    role = classify_source_role(
        path,
        functions,
        classes,
    )

    result.update(
        {
            "imports": sorted(
                set(imports)
            ),
            "functions": sorted(
                functions,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "classes": sorted(
                classes,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "references": references,
            "reference_lines": (
                reference_lines
            ),
            "write_calls": (
                write_calls[:100]
            ),
            "output_path_literals": (
                sorted(
                    output_path_literals
                )
            ),
            "body_mutation_signals": (
                body_mutation_signals(
                    tree,
                    source_lines,
                )
            ),
            "role": role,
        }
    )

    result["canonical_score"] = (
        canonical_score(
            path=path,
            role=role,
            functions=functions,
            references=references,
            output_paths=result[
                "output_path_literals"
            ],
            write_calls=write_calls,
        )
    )

    return result


def recursive_integer_fields(
    value: Any,
    *,
    prefix: str = "",
    depth: int = 0,
) -> dict[str, int]:
    if depth > 4:
        return {}

    results: dict[str, int] = {}

    if isinstance(
        value,
        dict,
    ):
        for key, item in value.items():
            path = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            if (
                isinstance(item, int)
                and not isinstance(
                    item,
                    bool,
                )
            ):
                results[path] = item

            elif isinstance(
                item,
                (
                    dict,
                    list,
                ),
            ):
                results.update(
                    recursive_integer_fields(
                        item,
                        prefix=path,
                        depth=depth + 1,
                    )
                )

    elif isinstance(
        value,
        list,
    ):
        results[
            f"{prefix}.__length__"
            if prefix
            else "__length__"
        ] = len(value)

    return results


def summarize_json_records(
    records: list[Any],
) -> dict[str, Any]:
    status_counts: Counter[str] = (
        Counter()
    )

    decision_counts: Counter[str] = (
        Counter()
    )

    eligibility_counts: Counter[str] = (
        Counter()
    )

    key_counts: Counter[str] = Counter()
    body_fields_present: Counter[str] = (
        Counter()
    )

    object_count = 0

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        object_count += 1

        for key in record:
            key_counts[
                str(key)
            ] += 1

        for field in (
            "status",
            "validation_status",
            "overall_status",
            "result",
        ):
            if field in record:
                status_counts[
                    f"{field}={record.get(field)}"
                ] += 1

        for field in (
            "decision",
            "validation_decision",
            "outcome",
        ):
            if field in record:
                decision_counts[
                    f"{field}={record.get(field)}"
                ] += 1

        for field in (
            "eligible",
            "is_eligible",
            "eligible_for_wuc",
            "passed",
            "valid",
        ):
            if field in record:
                eligibility_counts[
                    f"{field}={record.get(field)}"
                ] += 1

        for field in BODY_FIELDS:
            if field in record:
                body_fields_present[
                    field
                ] += 1

    return {
        "row_count": len(records),
        "object_record_count": (
            object_count
        ),
        "top_keys": dict(
            key_counts.most_common(60)
        ),
        "status_counts": dict(
            status_counts
        ),
        "decision_counts": dict(
            decision_counts
        ),
        "eligibility_counts": dict(
            eligibility_counts
        ),
        "body_fields_present": dict(
            body_fields_present
        ),
    }


def scan_artifact(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(path),
        "exists": path.is_file(),
        "size_bytes": (
            path.stat().st_size
            if path.is_file()
            else 0
        ),
        "modified_at": (
            datetime.fromtimestamp(
                path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
            if path.is_file()
            else None
        ),
        "suffix": path.suffix.lower(),
        "parse_status": "NOT_PARSED",
        "root_type": None,
        "integer_fields": {},
        "record_summary": None,
        "legacy_count_signals": [],
        "current_count_signals": [],
        "classification": "UNKNOWN",
        "error": None,
    }

    if not path.is_file():
        result["classification"] = (
            "MISSING"
        )

        return result

    try:
        numeric_values: set[int] = set()

        if path.suffix.lower() == ".jsonl":
            records: list[Any] = []

            with path.open(
                "r",
                encoding="utf-8-sig",
                errors="replace",
            ) as handle:
                for line_number, line in enumerate(
                    handle,
                    start=1,
                ):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        records.append(
                            json.loads(line)
                        )
                    except json.JSONDecodeError as exc:
                        result["error"] = (
                            f"Line {line_number}: {exc}"
                        )

                        break

            result["parse_status"] = (
                "PARSED"
                if result["error"] is None
                else "PARTIAL"
            )

            result["root_type"] = "jsonl"
            result["record_summary"] = (
                summarize_json_records(
                    records
                )
            )

            numeric_values.add(
                len(records)
            )

        elif path.suffix.lower() == ".json":
            value = load_json(
                path
            )

            result["parse_status"] = (
                "PARSED"
            )

            result["root_type"] = type(
                value
            ).__name__

            integer_fields = (
                recursive_integer_fields(
                    value
                )
            )

            result["integer_fields"] = (
                integer_fields
            )

            numeric_values.update(
                integer_fields.values()
            )

            if isinstance(
                value,
                list,
            ):
                result["record_summary"] = (
                    summarize_json_records(
                        value
                    )
                )

            elif isinstance(
                value,
                dict,
            ):
                for key in (
                    "records",
                    "results",
                    "articles",
                    "documents",
                    "validation_results",
                    "ledger",
                ):
                    collection = value.get(
                        key
                    )

                    if isinstance(
                        collection,
                        list,
                    ):
                        result[
                            "record_collection_field"
                        ] = key

                        result[
                            "record_summary"
                        ] = summarize_json_records(
                            collection
                        )

                        break

        else:
            result["parse_status"] = (
                "NON_JSON"
            )

        result["legacy_count_signals"] = (
            sorted(
                numeric_values
                & LEGACY_COUNTS
            )
        )

        result["current_count_signals"] = (
            sorted(
                numeric_values
                & CURRENT_COUNTS
            )
        )

        if result[
            "legacy_count_signals"
        ]:
            result["classification"] = (
                "LEGACY_ARTIFACT"
            )

        elif 2219 in result[
            "current_count_signals"
        ]:
            result["classification"] = (
                "CURRENT_COUNT_ARTIFACT"
            )

        elif (
            "article_validation"
            in path.as_posix().lower()
        ):
            result["classification"] = (
                "VALIDATION_ARTIFACT_UNALIGNED"
            )

        else:
            result["classification"] = (
                "RELATED_ARTIFACT"
            )

    except Exception as exc:
        result["parse_status"] = "ERROR"
        result["classification"] = (
            "UNREADABLE"
        )
        result["error"] = repr(exc)

    return result


def inspect_integrity_certificate() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(
            INTEGRITY_CERTIFICATE_PATH
        ),
        "exists": (
            INTEGRITY_CERTIFICATE_PATH.is_file()
        ),
    }

    if not INTEGRITY_CERTIFICATE_PATH.is_file():
        return result

    certificate = load_json(
        INTEGRITY_CERTIFICATE_PATH
    )

    coverage = certificate.get(
        "coverage",
        {},
    )

    result.update(
        {
            "certification_status": (
                certificate.get(
                    "certification_status"
                )
            ),
            "certificate_id": (
                certificate.get(
                    "certificate_id"
                )
            ),
            "coverage": coverage,
            "active_certified_count": (
                coverage.get(
                    "active_certified_count"
                )
            ),
            "quarantined_count": (
                coverage.get(
                    "quarantined_count"
                )
            ),
            "deferred_upstream_count": (
                coverage.get(
                    "deferred_upstream_count"
                )
            ),
        }
    )

    return result


def derive_decision(
    *,
    source_records: list[
        dict[str, Any]
    ],
    artifact_records: list[
        dict[str, Any]
    ],
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    executable_candidates = [
        record
        for record in source_records
        if (
            record.get(
                "canonical_score",
                0,
            )
            >= 8
            and record.get(
                "role"
            )
            in {
                "VALIDATION_ENGINE",
                "ORCHESTRATION",
                "WORKER",
            }
        )
    ]

    certificate_readers = [
        record
        for record in source_records
        if record.get(
            "references",
            {},
        ).get(
            "integrity_certificate"
        )
    ]

    body_mutators = [
        record
        for record in source_records
        if record.get(
            "body_mutation_signals"
        )
    ]

    legacy_artifacts = [
        record
        for record in artifact_records
        if record.get(
            "classification"
        )
        == "LEGACY_ARTIFACT"
    ]

    current_artifacts = [
        record
        for record in artifact_records
        if record.get(
            "classification"
        )
        == "CURRENT_COUNT_ARTIFACT"
    ]

    if not executable_candidates:
        decision = (
            "ARTICLE_VALIDATION_REBUILD_REQUIRED"
        )

        reasons.append(
            "No strong executable Article Validation "
            "engine candidate was identified."
        )

    elif len(
        executable_candidates
    ) == 1:
        decision = (
            "ARTICLE_VALIDATION_CANONICAL_ENGINE_IDENTIFIED"
        )

        reasons.append(
            "One primary executable Article Validation "
            "candidate was identified."
        )

    else:
        decision = (
            "ARTICLE_VALIDATION_MULTIPLE_ENGINE_CANDIDATES"
        )

        reasons.append(
            "Multiple executable Article Validation "
            "candidates require consolidation."
        )

    if not certificate_readers:
        reasons.append(
            "No Article Validation source consumes the "
            "Website Article Integrity certificate."
        )
    else:
        reasons.append(
            f"Integrity-certificate readers identified: "
            f"{len(certificate_readers)}."
        )

    if legacy_artifacts:
        reasons.append(
            f"Legacy validation artifacts identified: "
            f"{len(legacy_artifacts)}."
        )

    if not current_artifacts:
        reasons.append(
            "No current 2,219-record Article Validation "
            "artifact exists."
        )

    if body_mutators:
        reasons.append(
            f"Potential article-body mutation modules: "
            f"{len(body_mutators)}."
        )
    else:
        reasons.append(
            "No direct article-body assignment was detected."
        )

    return decision, reasons


def main() -> int:
    print()
    print("=" * 94)
    print(
        "ARTICLE VALIDATION — DEEP READ-ONLY ALIGNMENT SCAN"
    )
    print("=" * 94)

    if not INITIAL_SCAN_PATH.is_file():
        raise FileNotFoundError(
            "Initial Article Validation scan report "
            f"was not found: {INITIAL_SCAN_PATH}"
        )

    initial_report = load_json(
        INITIAL_SCAN_PATH
    )

    source_entries = initial_report.get(
        "article_validation_source_files",
        [],
    )

    artifact_entries = initial_report.get(
        "article_validation_artifacts",
        [],
    )

    if not isinstance(
        source_entries,
        list,
    ):
        source_entries = []

    if not isinstance(
        artifact_entries,
        list,
    ):
        artifact_entries = []

    source_paths: list[Path] = []

    for entry in source_entries:
        if not isinstance(
            entry,
            dict,
        ):
            continue

        path = normalize_report_path(
            entry.get("path")
        )

        if (
            path.is_file()
            and not any(
                part in EXCLUDED_PATH_PARTS
                for part in path.parts
            )
        ):
            source_paths.append(
                path
            )

    source_paths = sorted(
        set(source_paths)
    )

    artifact_paths: list[Path] = []

    for entry in artifact_entries:
        if not isinstance(
            entry,
            dict,
        ):
            continue

        path = normalize_report_path(
            entry.get("path")
        )

        artifact_paths.append(
            path
        )

    artifact_paths = sorted(
        set(artifact_paths)
    )

    source_records = [
        scan_source(path)
        for path in source_paths
    ]

    artifact_records = [
        scan_artifact(path)
        for path in artifact_paths
    ]

    ranked_sources = sorted(
        source_records,
        key=lambda record: (
            -int(
                record.get(
                    "canonical_score",
                    0,
                )
            ),
            str(
                record.get(
                    "path",
                    "",
                )
            ),
        ),
    )

    decision, reasons = derive_decision(
        source_records=source_records,
        artifact_records=artifact_records,
    )

    certificate = (
        inspect_integrity_certificate()
    )

    body_mutation_modules = [
        {
            "path": record["path"],
            "signals": record[
                "body_mutation_signals"
            ],
        }
        for record in source_records
        if record.get(
            "body_mutation_signals"
        )
    ]

    legacy_artifacts = [
        record["path"]
        for record in artifact_records
        if record.get(
            "classification"
        )
        == "LEGACY_ARTIFACT"
    ]

    current_artifacts = [
        record["path"]
        for record in artifact_records
        if record.get(
            "classification"
        )
        == "CURRENT_COUNT_ARTIFACT"
    ]

    integrity_readers = [
        record["path"]
        for record in source_records
        if record.get(
            "references",
            {},
        ).get(
            "integrity_certificate"
        )
    ]

    wuc_writers_or_references = [
        record["path"]
        for record in source_records
        if record.get(
            "references",
            {},
        ).get("wuc")
    ]

    recommended_patch_targets = [
        {
            "path": record["path"],
            "role": record["role"],
            "canonical_score": (
                record["canonical_score"]
            ),
            "references_integrity_certificate": (
                record.get(
                    "references",
                    {},
                ).get(
                    "integrity_certificate"
                )
            ),
            "references_udare_store": (
                record.get(
                    "references",
                    {},
                ).get(
                    "udare_store"
                )
            ),
            "references_wuc": (
                record.get(
                    "references",
                    {},
                ).get("wuc")
            ),
        }
        for record in ranked_sources[:8]
    ]

    report = {
        "schema_version": (
            "article_validation_deep_alignment_scan_v1"
        ),
        "generated_at": utc_now(),
        "scan_mode": "READ_ONLY",
        "workspace_id": WORKSPACE_ID,
        "initial_scan_report": relative(
            INITIAL_SCAN_PATH
        ),
        "integrity_certificate": (
            certificate
        ),
        "source_file_count": len(
            source_records
        ),
        "artifact_count": len(
            artifact_records
        ),
        "ranked_source_files": (
            ranked_sources
        ),
        "artifact_records": (
            artifact_records
        ),
        "integrity_certificate_readers": (
            integrity_readers
        ),
        "wuc_related_sources": (
            wuc_writers_or_references
        ),
        "body_mutation_modules": (
            body_mutation_modules
        ),
        "legacy_artifacts": (
            legacy_artifacts
        ),
        "current_2219_artifacts": (
            current_artifacts
        ),
        "recommended_patch_targets": (
            recommended_patch_targets
        ),
        "required_realignment_contract": {
            "input_certificate": relative(
                INTEGRITY_CERTIFICATE_PATH
            ),
            "input_scope": (
                "ACTIVE_INTEGRITY_CERTIFIED_UDARE_ARTICLES"
            ),
            "expected_active_input_count": 2219,
            "excluded_integrity_quarantine_count": 3,
            "excluded_deferred_upstream_count": 3,
            "article_body_modification_allowed": False,
            "article_body_copy_required": False,
            "validation_output_type": (
                "METADATA_AND_LEDGER_ONLY"
            ),
            "next_stage": (
                "Website Unified Content"
            ),
            "runtime_registration_required": True,
        },
        "decision": decision,
        "decision_reasons": reasons,
        "source_files_modified": [],
    }

    REPORT_ROOT.mkdir(
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
        f"Source files inspected:              "
        f"{len(source_records)}"
    )

    print(
        f"Artifacts inspected:                 "
        f"{len(artifact_records)}"
    )

    print(
        f"Integrity certificate readers:       "
        f"{len(integrity_readers)}"
    )

    print(
        f"WUC-related source files:             "
        f"{len(wuc_writers_or_references)}"
    )

    print(
        f"Potential body-mutation modules:      "
        f"{len(body_mutation_modules)}"
    )

    print(
        f"Legacy validation artifacts:          "
        f"{len(legacy_artifacts)}"
    )

    print(
        f"Current 2,219 validation artifacts:   "
        f"{len(current_artifacts)}"
    )

    print()
    print(
        "TOP ARTICLE VALIDATION SOURCE CANDIDATES"
    )

    for record in ranked_sources:
        print(
            "  "
            f"[score={record.get('canonical_score', 0):>2}] "
            f"[{record.get('role')}] "
            f"{record.get('path')}"
        )

        functions = [
            function["name"]
            for function in record.get(
                "functions",
                [],
            )
            if (
                "validat"
                in function["name"].lower()
                or "article"
                in function["name"].lower()
                or function["name"].lower().startswith(
                    ("run", "execute", "process")
                )
            )
        ]

        if functions:
            print(
                "       functions: "
                + ", ".join(
                    functions[:12]
                )
            )

        references = record.get(
            "references",
            {},
        )

        print(
            "       references: "
            f"certificate={references.get('integrity_certificate')}, "
            f"udare={references.get('udare_store')}, "
            f"wuc={references.get('wuc')}, "
            f"runtime={references.get('runtime_registration')}"
        )

        if record.get(
            "body_mutation_signals"
        ):
            print(
                "       WARNING: article-body mutation signal detected"
            )

    print()
    print("LEGACY ARTIFACTS")

    if legacy_artifacts:
        for path in legacy_artifacts:
            print(
                "  - "
                + path
            )
    else:
        print("  - None")

    print()
    print("POTENTIAL BODY-MUTATION MODULES")

    if body_mutation_modules:
        for record in body_mutation_modules:
            print(
                "  - "
                + record["path"]
            )

            for signal in record[
                "signals"
            ][:10]:
                print(
                    "      "
                    f"line {signal.get('line')}: "
                    f"{signal.get('field')} "
                    f"({signal.get('type')})"
                )
    else:
        print("  - None detected")

    print()
    print("DECISION")
    print(
        "  "
        + decision
    )

    print()
    print("REASONS")

    for reason in reasons:
        print(
            "  - "
            + reason
        )

    print()
    print("REQUIRED REALIGNMENT CONTRACT")

    print(
        "  Input:                    "
        "2,219 active integrity-certified UDARE articles"
    )

    print(
        "  Integrity quarantine:     "
        "3 excluded"
    )

    print(
        "  Deferred upstream pages:  "
        "3 excluded"
    )

    print(
        "  Article body modification:"
        " prohibited"
    )

    print(
        "  Validation output:        "
        "metadata and ledger only"
    )

    print(
        "  Next stage:               "
        "Website Unified Content"
    )

    print()
    print(
        "Deep alignment report: "
        + str(REPORT_PATH)
    )

    print(
        "Source files modified: 0"
    )

    print("=" * 94)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
