"""Targeted read-only scan of canonical Article Validation components."""

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

WORKSPACE_ID = "ws_whattoexpect_com"

TARGET_SOURCE_PATHS = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "stores"
    / "article_validation_engine.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "stores"
    / "article_validation_store.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "workers"
    / "certified_website_article_batch_worker.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "stores"
    / "certified_website_article_store.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "workers"
    / "website_unified_content_batch_worker.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "workers"
    / "website_unified_content_batch_worker_v2.py",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "phase_4_5_14_article_body_batch_completion_engine.py",
)

LEGACY_ARTIFACT_PATHS = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "final_website_pipeline_certification"
    / "article_validation_review"
    / "article_validation_v1_final_certification.json",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "final_website_pipeline_certification"
    / "article_validation_review"
    / "article_validation_v1_final_results.json",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "final_website_pipeline_certification"
    / "article_validation_review"
    / "article_validation_v2_final_certification.json",

    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "final_website_pipeline_certification"
    / "article_validation_review"
    / "article_validation_v2_final_results.json",
)

REPORT_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_canonical_component_scan.json"
)

BODY_FIELD_NAMES = {
    "article_body",
    "content_body",
    "body_text",
    "article_text",
    "content",
    "html",
    "body_html",
}

IMPORTANT_TERMS = {
    "integrity_certificate": (
        "website_article_integrity_certificate",
        "active_certified_count",
        "certification_status",
    ),
    "udare_store": (
        "udare_store",
        "load_udare",
    ),
    "article_validation": (
        "article_validation",
        "validate_article",
        "validation_result",
    ),
    "certified_article_store": (
        "certified_website_article_store",
        "certified website article store",
    ),
    "wuc": (
        "website_unified_content",
        "website unified content",
    ),
    "runtime": (
        "register_runtime_handler",
        "universal_runtime_registration",
        "create_universal_knowledge_job",
    ),
}

WRITE_CALLS = {
    "write",
    "writelines",
    "write_text",
    "write_bytes",
    "dump",
    "replace",
    "rename",
    "unlink",
}

LEGACY_COUNTS = {
    2225,
    2224,
    2203,
    22,
}

CURRENT_COUNTS = {
    2219,
    3,
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


def call_name(
    node: ast.Call,
) -> str:
    value = node.func

    if isinstance(value, ast.Name):
        return value.id

    if isinstance(value, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = value

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


def function_arguments(
    node: ast.FunctionDef
    | ast.AsyncFunctionDef,
) -> list[str]:
    arguments = [
        argument.arg
        for argument in (
            list(node.args.posonlyargs)
            + list(node.args.args)
            + list(node.args.kwonlyargs)
        )
    ]

    if node.args.vararg:
        arguments.append(
            "*" + node.args.vararg.arg
        )

    if node.args.kwarg:
        arguments.append(
            "**" + node.args.kwarg.arg
        )

    return arguments


def literal_key(
    node: ast.Subscript,
) -> str | None:
    value = node.slice

    if (
        isinstance(value, ast.Constant)
        and isinstance(value.value, str)
    ):
        return value.value

    return None


def inspect_source(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(path),
        "exists": path.is_file(),
        "syntax_valid": False,
        "syntax_error": None,
        "imports": [],
        "functions": [],
        "classes": [],
        "calls": [],
        "write_calls": [],
        "string_paths": [],
        "numeric_constants": [],
        "references": {},
        "body_assignments": [],
    }

    if not path.is_file():
        return result

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    source_lines = source.splitlines()
    lowered_source = source.lower()

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

    imports: set[str] = set()
    calls: list[dict[str, Any]] = []
    write_calls: list[dict[str, Any]] = []
    string_paths: set[str] = set()
    numeric_constants: set[int] = set()
    body_assignments: list[
        dict[str, Any]
    ] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(
                    alias.name
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.add(
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
            result["functions"].append(
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

        elif isinstance(node, ast.ClassDef):
            result["classes"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

        elif isinstance(node, ast.Call):
            name = call_name(node)

            calls.append(
                {
                    "name": name,
                    "line": getattr(
                        node,
                        "lineno",
                        None,
                    ),
                }
            )

            if (
                name.split(".")[-1]
                in WRITE_CALLS
            ):
                write_calls.append(
                    {
                        "name": name,
                        "line": getattr(
                            node,
                            "lineno",
                            None,
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

        elif isinstance(node, ast.Constant):
            if (
                isinstance(node.value, int)
                and not isinstance(
                    node.value,
                    bool,
                )
            ):
                numeric_constants.add(
                    node.value
                )

            elif isinstance(
                node.value,
                str,
            ):
                value = node.value.strip()
                lowered = value.lower()

                if any(
                    suffix in lowered
                    for suffix in (
                        ".json",
                        ".jsonl",
                        ".html",
                        ".txt",
                    )
                ):
                    string_paths.add(
                        value[:1000]
                    )

        targets: list[ast.AST] = []

        if isinstance(node, ast.Assign):
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
            field_name: str | None = None

            if isinstance(
                target,
                ast.Subscript,
            ):
                field_name = literal_key(
                    target
                )

            elif isinstance(
                target,
                ast.Attribute,
            ):
                field_name = target.attr

            if (
                field_name
                and field_name.lower()
                in BODY_FIELD_NAMES
            ):
                body_assignments.append(
                    {
                        "field": field_name,
                        "line": getattr(
                            node,
                            "lineno",
                            None,
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

    result["imports"] = sorted(
        imports
    )

    result["calls"] = calls[:300]

    result["write_calls"] = (
        write_calls[:100]
    )

    result["string_paths"] = sorted(
        string_paths
    )

    result["numeric_constants"] = sorted(
        numeric_constants
    )

    result["body_assignments"] = (
        body_assignments
    )

    for name, terms in (
        IMPORTANT_TERMS.items()
    ):
        result["references"][name] = {
            "present": any(
                term.lower()
                in lowered_source
                for term in terms
            ),
            "lines": [
                {
                    "line": line_number,
                    "text": line.strip()[:500],
                }
                for line_number, line
                in enumerate(
                    source_lines,
                    start=1,
                )
                if any(
                    term.lower()
                    in line.lower()
                    for term in terms
                )
            ][:30],
        }

    return result


def recursive_integer_fields(
    value: Any,
    prefix: str = "",
    depth: int = 0,
) -> dict[str, int]:
    if depth > 6:
        return {}

    values: dict[str, int] = {}

    if isinstance(value, dict):
        for key, item in value.items():
            field = (
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
                values[field] = item

            elif isinstance(
                item,
                (
                    dict,
                    list,
                ),
            ):
                values.update(
                    recursive_integer_fields(
                        item,
                        field,
                        depth + 1,
                    )
                )

    elif isinstance(value, list):
        values[
            (
                f"{prefix}.__length__"
                if prefix
                else "__length__"
            )
        ] = len(value)

    return values


def inspect_artifact(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(path),
        "exists": path.is_file(),
        "parse_status": "NOT_PARSED",
        "root_type": None,
        "top_level_keys": [],
        "integer_fields": {},
        "legacy_count_signals": [],
        "current_count_signals": [],
        "sample_record_keys": [],
        "error": None,
    }

    if not path.is_file():
        return result

    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        )

        result["parse_status"] = "PARSED"
        result["root_type"] = type(
            value
        ).__name__

        if isinstance(value, dict):
            result["top_level_keys"] = sorted(
                str(key)
                for key in value.keys()
            )

            for collection_name in (
                "records",
                "results",
                "articles",
                "validation_results",
                "ledger",
            ):
                collection = value.get(
                    collection_name
                )

                if (
                    isinstance(collection, list)
                    and collection
                    and isinstance(
                        collection[0],
                        dict,
                    )
                ):
                    result[
                        "sample_collection"
                    ] = collection_name

                    result[
                        "sample_record_keys"
                    ] = sorted(
                        str(key)
                        for key
                        in collection[0].keys()
                    )

                    break

        elif (
            isinstance(value, list)
            and value
            and isinstance(
                value[0],
                dict,
            )
        ):
            result["sample_record_keys"] = (
                sorted(
                    str(key)
                    for key
                    in value[0].keys()
                )
            )

        integer_fields = (
            recursive_integer_fields(
                value
            )
        )

        result["integer_fields"] = (
            integer_fields
        )

        numeric_values = set(
            integer_fields.values()
        )

        result[
            "legacy_count_signals"
        ] = sorted(
            numeric_values
            & LEGACY_COUNTS
        )

        result[
            "current_count_signals"
        ] = sorted(
            numeric_values
            & CURRENT_COUNTS
        )

    except Exception as exc:
        result["parse_status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def classify_component(
    record: dict[str, Any],
) -> str:
    path = str(
        record.get("path", "")
    ).lower()

    functions = {
        str(
            item.get("name", "")
        ).lower()
        for item in record.get(
            "functions",
            []
        )
    }

    if (
        path.endswith(
            "article_validation_engine.py"
        )
        and "validate_article_v1"
        in functions
    ):
        return "PRIMARY_VALIDATION_ENGINE"

    if path.endswith(
        "article_validation_store.py"
    ):
        return "VALIDATION_RESULT_STORE"

    if path.endswith(
        "certified_website_article_batch_worker.py"
    ):
        return "LEGACY_BATCH_WORKER_CANDIDATE"

    if path.endswith(
        "certified_website_article_store.py"
    ):
        return "LEGACY_STORE_CANDIDATE"

    if (
        "website_unified_content_batch_worker"
        in path
    ):
        return "DOWNSTREAM_WUC_WORKER"

    if (
        "article_body_batch_completion"
        in path
    ):
        return "DOWNSTREAM_BODY_COMPLETION"

    return "UNCLASSIFIED"


def main() -> int:
    print()
    print("=" * 96)
    print(
        "ARTICLE VALIDATION — CANONICAL COMPONENT CONTRACT SCAN"
    )
    print("=" * 96)

    source_records = [
        inspect_source(path)
        for path in TARGET_SOURCE_PATHS
    ]

    for record in source_records:
        record["component_classification"] = (
            classify_component(
                record
            )
        )

    artifact_records = [
        inspect_artifact(path)
        for path in LEGACY_ARTIFACT_PATHS
    ]

    primary_engines = [
        record
        for record in source_records
        if record[
            "component_classification"
        ]
        == "PRIMARY_VALIDATION_ENGINE"
    ]

    validation_stores = [
        record
        for record in source_records
        if record[
            "component_classification"
        ]
        == "VALIDATION_RESULT_STORE"
    ]

    legacy_workers = [
        record
        for record in source_records
        if record[
            "component_classification"
        ]
        == "LEGACY_BATCH_WORKER_CANDIDATE"
    ]

    legacy_stores = [
        record
        for record in source_records
        if record[
            "component_classification"
        ]
        == "LEGACY_STORE_CANDIDATE"
    ]

    body_mutation_records = [
        record
        for record in source_records
        if record.get(
            "body_assignments"
        )
    ]

    certificate_consumers = [
        record
        for record in source_records
        if record.get(
            "references",
            {},
        ).get(
            "integrity_certificate",
            {},
        ).get("present")
    ]

    udare_consumers = [
        record
        for record in source_records
        if record.get(
            "references",
            {},
        ).get(
            "udare_store",
            {},
        ).get("present")
    ]

    runtime_connected = [
        record
        for record in source_records
        if record.get(
            "references",
            {},
        ).get(
            "runtime",
            {},
        ).get("present")
    ]

    report = {
        "schema_version": (
            "article_validation_"
            "canonical_component_scan_v1"
        ),
        "generated_at": utc_now(),
        "scan_mode": "READ_ONLY",
        "workspace_id": WORKSPACE_ID,
        "source_records": source_records,
        "legacy_artifact_records": (
            artifact_records
        ),
        "summary": {
            "primary_engine_count": len(
                primary_engines
            ),
            "validation_store_count": len(
                validation_stores
            ),
            "legacy_worker_candidate_count": len(
                legacy_workers
            ),
            "legacy_store_candidate_count": len(
                legacy_stores
            ),
            "integrity_certificate_consumer_count": len(
                certificate_consumers
            ),
            "udare_consumer_count": len(
                udare_consumers
            ),
            "runtime_connected_component_count": len(
                runtime_connected
            ),
            "body_mutation_component_count": len(
                body_mutation_records
            ),
            "legacy_artifact_count": len(
                [
                    artifact
                    for artifact
                    in artifact_records
                    if artifact.get(
                        "legacy_count_signals"
                    )
                ]
            ),
        },
        "required_target_architecture": {
            "input": (
                "2,219 active integrity-certified "
                "UDARE article documents"
            ),
            "primary_engine": (
                "article_validation_engine.py"
            ),
            "output_store": (
                "article_validation_store.py"
            ),
            "separate_certified_article_store_allowed": (
                False
            ),
            "article_body_modification_allowed": (
                False
            ),
            "article_body_copy_allowed": False,
            "output_scope": (
                "validation metadata, decisions, "
                "ledger and report only"
            ),
            "next_stage": (
                "Website Unified Content"
            ),
            "runtime_registration_required": (
                True
            ),
        },
        "source_files_modified": [],
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
        "Primary Article Validation engines:       "
        + str(
            len(primary_engines)
        )
    )

    print(
        "Article Validation result stores:         "
        + str(
            len(validation_stores)
        )
    )

    print(
        "Legacy batch-worker candidates:           "
        + str(
            len(legacy_workers)
        )
    )

    print(
        "Legacy certified-store candidates:        "
        + str(
            len(legacy_stores)
        )
    )

    print(
        "Integrity certificate consumers:          "
        + str(
            len(certificate_consumers)
        )
    )

    print(
        "UDARE Store consumers:                    "
        + str(
            len(udare_consumers)
        )
    )

    print(
        "Runtime-connected validation components:  "
        + str(
            len(runtime_connected)
        )
    )

    print(
        "Body-mutation components:                 "
        + str(
            len(body_mutation_records)
        )
    )

    print()
    print("COMPONENTS")

    for record in source_records:
        print()
        print(
            "  "
            + record[
                "component_classification"
            ]
        )

        print(
            "    Path: "
            + record["path"]
        )

        print(
            "    Syntax: "
            + (
                "PASS"
                if record[
                    "syntax_valid"
                ]
                else "FAIL"
            )
        )

        function_names = [
            function["name"]
            for function
            in record.get(
                "functions",
                []
            )
        ]

        print(
            "    Functions: "
            + (
                ", ".join(
                    function_names
                )
                if function_names
                else "None"
            )
        )

        references = record.get(
            "references",
            {},
        )

        print(
            "    References: "
            + "certificate="
            + str(
                references.get(
                    "integrity_certificate",
                    {},
                ).get("present")
            )
            + ", udare="
            + str(
                references.get(
                    "udare_store",
                    {},
                ).get("present")
            )
            + ", validation="
            + str(
                references.get(
                    "article_validation",
                    {},
                ).get("present")
            )
            + ", certified_store="
            + str(
                references.get(
                    "certified_article_store",
                    {},
                ).get("present")
            )
            + ", wuc="
            + str(
                references.get(
                    "wuc",
                    {},
                ).get("present")
            )
            + ", runtime="
            + str(
                references.get(
                    "runtime",
                    {},
                ).get("present")
            )
        )

        print(
            "    Write calls: "
            + str(
                len(
                    record.get(
                        "write_calls",
                        []
                    )
                )
            )
        )

        print(
            "    Body assignments: "
            + str(
                len(
                    record.get(
                        "body_assignments",
                        []
                    )
                )
            )
        )

        if record.get(
            "string_paths"
        ):
            print(
                "    Path literals:"
            )

            for value in record[
                "string_paths"
            ]:
                print(
                    "      - "
                    + value
                )

    print()
    print("LEGACY VALIDATION ARTIFACTS")

    for artifact in artifact_records:
        print()
        print(
            "  "
            + artifact["path"]
        )

        print(
            "    Exists: "
            + str(
                artifact["exists"]
            )
        )

        print(
            "    Parse status: "
            + artifact[
                "parse_status"
            ]
        )

        print(
            "    Legacy count signals: "
            + str(
                artifact[
                    "legacy_count_signals"
                ]
            )
        )

        print(
            "    Current count signals: "
            + str(
                artifact[
                    "current_count_signals"
                ]
            )
        )

        print(
            "    Top-level keys: "
            + ", ".join(
                artifact[
                    "top_level_keys"
                ][:30]
            )
        )

        print(
            "    Sample record keys: "
            + ", ".join(
                artifact[
                    "sample_record_keys"
                ][:40]
            )
        )

    print()
    print(
        "TARGET ARCHITECTURE"
    )

    print(
        "  Input:             "
        "2,219 active certified UDARE articles"
    )

    print(
        "  Validation engine: article_validation_engine.py"
    )

    print(
        "  Output store:      article_validation_store.py"
    )

    print(
        "  Certified store:   prohibited as a separate body store"
    )

    print(
        "  Article bodies:    read-only"
    )

    print(
        "  Output:            validation metadata and ledger only"
    )

    print(
        "  Next stage:        Website Unified Content"
    )

    print()
    print(
        "Report: "
        + str(
            REPORT_PATH
        )
    )

    print(
        "Source files modified: 0"
    )

    print("=" * 96)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
