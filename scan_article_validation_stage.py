"""Read-only scan of the LinkCraftor Article Validation stage."""

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

INTEGRITY_CERTIFICATE_PATH = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
    / "certification"
    / "website_article_integrity_certificate.json"
)

UDARE_MANIFEST_PATH = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
    / "manifests"
    / "udare_store_manifest.json"
)

RUNTIME_REGISTRY_PATH = (
    DATA_ROOT
    / "runtime"
    / "universal_runtime_registration"
    / "runtime_registration_registry.json"
)

WUC_PATH = (
    DATA_ROOT
    / "website_unified_content"
    / f"website_unified_content_{WORKSPACE_ID}.json"
)

REPORT_ROOT = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
)

REPORT_PATH = (
    REPORT_ROOT
    / "article_validation_stage_scan.json"
)

EXCLUDED_SOURCE_DIRECTORIES = {
    "__pycache__",
    "backups",
    "runtime_backups",
    "data",
    ".venv",
    "node_modules",
}

SOURCE_SEARCH_TERMS = (
    "article_validation",
    "article validation",
    "article_validator",
    "validation_engine",
    "validation result",
    "eligible_for_wuc",
    "website article validation",
)

CURRENT_INTEGRITY_REFERENCE_TERMS = (
    "website_article_integrity_certificate",
    "certified_active_articles",
    "website_article_integrity/certification",
    "website_article_integrity\\certification",
    "active_certified_count",
)

UDARE_REFERENCE_TERMS = (
    "udare_store",
    "udare store",
)

WUC_REFERENCE_TERMS = (
    "website_unified_content",
    "website unified content",
)

STATUS_FIELDS = (
    "status",
    "validation_status",
    "overall_status",
    "result",
    "decision",
    "eligibility_status",
    "article_status",
)

BOOLEAN_FIELDS = (
    "eligible",
    "validation_passed",
    "is_eligible",
    "passed",
    "valid",
    "eligible_for_wuc",
)

COUNT_FIELDS = (
    "total",
    "total_count",
    "total_rows",
    "record_count",
    "article_count",
    "articles_checked",
    "articles_validated",
    "eligible",
    "eligible_count",
    "eligible_articles",
    "passed",
    "pass_count",
    "failed",
    "fail_count",
    "blocked",
    "blocked_count",
    "quarantined",
    "quarantined_count",
    "deferred",
    "deferred_count",
)

LEGACY_COUNT_SIGNALS = {
    2225,
    2224,
    2203,
    22,
}

CURRENT_COUNT_SIGNALS = {
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


def load_json(
    path: Path,
) -> Any:
    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )


def active_python_files() -> list[Path]:
    paths: list[Path] = []

    for path in SERVER_ROOT.rglob("*.py"):
        parts = path.relative_to(
            SERVER_ROOT
        ).parts

        if any(
            part in EXCLUDED_SOURCE_DIRECTORIES
            for part in parts
        ):
            continue

        paths.append(path)

    return sorted(paths)


def is_article_validation_source(
    path: Path,
    source: str,
) -> bool:
    searchable = (
        path.as_posix()
        + "\n"
        + source
    ).lower()

    return any(
        term in searchable
        for term in SOURCE_SEARCH_TERMS
    )


def source_matches(
    source: str,
    terms: tuple[str, ...],
) -> bool:
    lowered = source.lower()

    return any(
        term.lower() in lowered
        for term in terms
    )


def scan_source_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    result: dict[str, Any] = {
        "path": relative(path),
        "size_bytes": path.stat().st_size,
        "syntax_valid": False,
        "syntax_error": None,
        "functions": [],
        "classes": [],
        "constants": [],
        "article_validation_matches": [],
        "references_udare_store": source_matches(
            source,
            UDARE_REFERENCE_TERMS,
        ),
        "references_integrity_certification": source_matches(
            source,
            CURRENT_INTEGRITY_REFERENCE_TERMS,
        ),
        "references_wuc": source_matches(
            source,
            WUC_REFERENCE_TERMS,
        ),
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

        tree = None

    if tree is not None:
        for node in tree.body:
            if isinstance(
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
                    }
                )

            elif isinstance(
                node,
                ast.ClassDef,
            ):
                result["classes"].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            elif isinstance(
                node,
                (
                    ast.Assign,
                    ast.AnnAssign,
                ),
            ):
                targets: list[ast.AST]

                if isinstance(
                    node,
                    ast.Assign,
                ):
                    targets = list(
                        node.targets
                    )
                else:
                    targets = [
                        node.target
                    ]

                for target in targets:
                    if not isinstance(
                        target,
                        ast.Name,
                    ):
                        continue

                    name = target.id

                    if any(
                        term in name.lower()
                        for term in (
                            "validation",
                            "eligible",
                            "blocked",
                            "quarantine",
                            "article",
                        )
                    ):
                        result["constants"].append(
                            {
                                "name": name,
                                "line": node.lineno,
                                "value_type": type(
                                    node.value
                                ).__name__,
                            }
                        )

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lowered_line = line.lower()

        if any(
            term in lowered_line
            for term in SOURCE_SEARCH_TERMS
        ):
            result[
                "article_validation_matches"
            ].append(
                {
                    "line": line_number,
                    "text": line.strip()[:500],
                }
            )

            if (
                len(
                    result[
                        "article_validation_matches"
                    ]
                )
                >= 40
            ):
                break

    return result


def validation_data_candidates() -> list[Path]:
    candidates: list[Path] = []

    if not DATA_ROOT.is_dir():
        return candidates

    for path in DATA_ROOT.rglob("*"):
        if not path.is_file():
            continue

        normalized = path.as_posix().lower()

        if any(
            term in normalized
            for term in (
                "article_validation",
                "article-validation",
                "articlevalidation",
                "website_article_validation",
            )
        ):
            candidates.append(path)

    return sorted(
        candidates
    )


def summarize_record_collection(
    records: list[Any],
) -> dict[str, Any]:
    status_counts: dict[
        str,
        Counter[str],
    ] = {
        field: Counter()
        for field in STATUS_FIELDS
    }

    boolean_counts: dict[
        str,
        Counter[str],
    ] = {
        field: Counter()
        for field in BOOLEAN_FIELDS
    }

    key_counts: Counter[str] = Counter()
    source_fields: Counter[str] = Counter()
    body_fields: Counter[str] = Counter()

    object_record_count = 0

    for record in records:
        if not isinstance(
            record,
            dict,
        ):
            continue

        object_record_count += 1

        for key in record:
            key_counts[str(key)] += 1

        for field in STATUS_FIELDS:
            if field in record:
                status_counts[field][
                    str(
                        record.get(field)
                    )
                ] += 1

        for field in BOOLEAN_FIELDS:
            if field in record:
                boolean_counts[field][
                    str(
                        record.get(field)
                    )
                ] += 1

        for field in (
            "source_type",
            "source_pipeline",
            "source_store",
            "input_store",
            "source_stage",
            "validation_version",
            "engine_version",
        ):
            if field in record:
                source_fields[
                    f"{field}={record.get(field)}"
                ] += 1

        for field in (
            "article_body",
            "content_body",
            "body_text",
            "article_text",
            "content",
        ):
            if field in record:
                body_fields[field] += 1

    return {
        "row_count": len(records),
        "object_record_count": (
            object_record_count
        ),
        "top_keys": dict(
            key_counts.most_common(50)
        ),
        "status_distributions": {
            field: dict(counter)
            for field, counter
            in status_counts.items()
            if counter
        },
        "boolean_distributions": {
            field: dict(counter)
            for field, counter
            in boolean_counts.items()
            if counter
        },
        "source_signals": dict(
            source_fields.most_common(50)
        ),
        "body_field_usage": dict(
            body_fields
        ),
    }


def scan_json_artifact(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(path),
        "size_bytes": path.stat().st_size,
        "suffix": path.suffix.lower(),
        "parse_status": "NOT_PARSED",
        "root_type": None,
        "counts": {},
        "collection_summary": None,
        "legacy_count_signals": [],
        "current_count_signals": [],
        "error": None,
    }

    try:
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
                            f"JSONL line {line_number}: {exc}"
                        )

                        break

            result["parse_status"] = (
                "PARSED"
                if result["error"] is None
                else "PARTIAL"
            )

            result["root_type"] = "jsonl"

            result["collection_summary"] = (
                summarize_record_collection(
                    records
                )
            )

            numeric_values = {
                len(records)
            }

        else:
            value = load_json(
                path
            )

            result["parse_status"] = "PARSED"
            result["root_type"] = type(
                value
            ).__name__

            numeric_values: set[int] = set()

            if isinstance(
                value,
                list,
            ):
                result[
                    "collection_summary"
                ] = summarize_record_collection(
                    value
                )

                numeric_values.add(
                    len(value)
                )

            elif isinstance(
                value,
                dict,
            ):
                count_values: dict[
                    str,
                    int,
                ] = {}

                for key, item in value.items():
                    if (
                        key in COUNT_FIELDS
                        and isinstance(
                            item,
                            int,
                        )
                    ):
                        count_values[
                            key
                        ] = item

                        numeric_values.add(
                            item
                        )

                for container_name in (
                    "summary",
                    "counts",
                    "statistics",
                    "coverage",
                    "result",
                ):
                    container = value.get(
                        container_name
                    )

                    if not isinstance(
                        container,
                        dict,
                    ):
                        continue

                    for key, item in container.items():
                        if isinstance(
                            item,
                            int,
                        ):
                            count_values[
                                f"{container_name}.{key}"
                            ] = item

                            numeric_values.add(
                                item
                            )

                result["counts"] = (
                    count_values
                )

                for key in (
                    "records",
                    "results",
                    "articles",
                    "documents",
                    "validation_results",
                ):
                    collection = value.get(key)

                    if isinstance(
                        collection,
                        list,
                    ):
                        result[
                            "collection_summary"
                        ] = summarize_record_collection(
                            collection
                        )

                        numeric_values.add(
                            len(collection)
                        )

                        break

            else:
                numeric_values = set()

        result["legacy_count_signals"] = (
            sorted(
                numeric_values
                & LEGACY_COUNT_SIGNALS
            )
        )

        result["current_count_signals"] = (
            sorted(
                numeric_values
                & CURRENT_COUNT_SIGNALS
            )
        )

    except Exception as exc:
        result["parse_status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def scan_integrity_certificate() -> dict[str, Any]:
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

    document = load_json(
        INTEGRITY_CERTIFICATE_PATH
    )

    result.update(
        {
            "certification_status": (
                document.get(
                    "certification_status"
                )
            ),
            "certification_scope": (
                document.get(
                    "certification_scope"
                )
            ),
            "coverage": document.get(
                "coverage",
                {},
            ),
            "certificate_id": (
                document.get(
                    "certificate_id"
                )
            ),
        }
    )

    return result


def scan_udare_manifest() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(
            UDARE_MANIFEST_PATH
        ),
        "exists": (
            UDARE_MANIFEST_PATH.is_file()
        ),
    }

    if not UDARE_MANIFEST_PATH.is_file():
        return result

    document = load_json(
        UDARE_MANIFEST_PATH
    )

    result.update(
        {
            "record_count": document.get(
                "record_count"
            ),
            "article_document_count": (
                document.get(
                    "article_document_count"
                )
            ),
            "metadata_record_count": (
                document.get(
                    "metadata_record_count"
                )
            ),
            "integrity_certification": (
                document.get(
                    "website_article_integrity_certification",
                    {},
                )
            ),
        }
    )

    return result


def scan_runtime_registry() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(
            RUNTIME_REGISTRY_PATH
        ),
        "exists": (
            RUNTIME_REGISTRY_PATH.is_file()
        ),
        "article_validation_registrations": [],
        "registration_count": 0,
    }

    if not RUNTIME_REGISTRY_PATH.is_file():
        return result

    document = load_json(
        RUNTIME_REGISTRY_PATH
    )

    registrations = document.get(
        "registrations",
        [],
    )

    if not isinstance(
        registrations,
        list,
    ):
        return result

    result["registration_count"] = len(
        registrations
    )

    result[
        "article_validation_registrations"
    ] = [
        registration
        for registration in registrations
        if (
            isinstance(
                registration,
                dict,
            )
            and (
                "article_validation"
                in str(
                    registration.get(
                        "job_type",
                        "",
                    )
                ).lower()
                or "article_validation"
                in str(
                    registration.get(
                        "pipeline",
                        "",
                    )
                ).lower()
                or "article validation"
                in str(
                    registration.get(
                        "description",
                        "",
                    )
                ).lower()
            )
        )
    ]

    return result


def scan_wuc_snapshot() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(
            WUC_PATH
        ),
        "exists": WUC_PATH.is_file(),
        "size_bytes": (
            WUC_PATH.stat().st_size
            if WUC_PATH.is_file()
            else 0
        ),
        "parse_status": "NOT_PARSED",
    }

    if not WUC_PATH.is_file():
        return result

    try:
        value = load_json(
            WUC_PATH
        )

        result["parse_status"] = "PARSED"

        if isinstance(
            value,
            list,
        ):
            records = value

        elif isinstance(
            value,
            dict,
        ):
            records = []

            for key in (
                "documents",
                "records",
                "articles",
                "content",
            ):
                candidate = value.get(key)

                if isinstance(
                    candidate,
                    list,
                ):
                    records = candidate
                    result[
                        "collection_field"
                    ] = key

                    break

            if not records:
                result[
                    "top_level_keys"
                ] = sorted(
                    str(key)
                    for key in value.keys()
                )[:100]

        else:
            records = []

        if records:
            result.update(
                summarize_record_collection(
                    records
                )
            )

    except Exception as exc:
        result["parse_status"] = "ERROR"
        result["error"] = repr(exc)

    return result


def classify(
    *,
    source_files: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    runtime_registry: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    source_count = len(
        source_files
    )

    artifact_count = len(
        artifacts
    )

    current_certification_reference_count = sum(
        1
        for record in source_files
        if record.get(
            "references_integrity_certification"
        )
    )

    udare_reference_count = sum(
        1
        for record in source_files
        if record.get(
            "references_udare_store"
        )
    )

    wuc_reference_count = sum(
        1
        for record in source_files
        if record.get(
            "references_wuc"
        )
    )

    legacy_artifacts = [
        artifact
        for artifact in artifacts
        if artifact.get(
            "legacy_count_signals"
        )
    ]

    current_artifacts = [
        artifact
        for artifact in artifacts
        if 2219 in artifact.get(
            "current_count_signals",
            [],
        )
    ]

    runtime_registration_count = len(
        runtime_registry.get(
            "article_validation_registrations",
            [],
        )
    )

    if source_count == 0:
        decision = (
            "ARTICLE_VALIDATION_IMPLEMENTATION_NOT_FOUND"
        )

        reasons.append(
            "No active Article Validation source files were found."
        )

    elif (
        current_certification_reference_count > 0
        and current_artifacts
        and runtime_registration_count > 0
    ):
        decision = (
            "CURRENT_ARTICLE_VALIDATION_IMPLEMENTATION_EXISTS"
        )

        reasons.append(
            "Article Validation source references the integrity-certified input."
        )

        reasons.append(
            "An Article Validation artifact contains the current "
            "2,219-record signal."
        )

        reasons.append(
            "Article Validation is present in Runtime Registration."
        )

    elif legacy_artifacts:
        decision = (
            "LEGACY_ARTICLE_VALIDATION_EXISTS_REALIGNMENT_REQUIRED"
        )

        reasons.append(
            "Article Validation source or artifacts exist."
        )

        reasons.append(
            "One or more artifacts contain legacy count signals "
            "such as 2,225 or 2,224."
        )

        if current_certification_reference_count == 0:
            reasons.append(
                "No source file clearly references the current "
                "Website Article Integrity certificate."
            )

        if runtime_registration_count == 0:
            reasons.append(
                "No Article Validation Runtime Registration was found."
            )

    else:
        decision = (
            "ARTICLE_VALIDATION_LOGIC_EXISTS_CURRENT_ALIGNMENT_NOT_CONFIRMED"
        )

        reasons.append(
            "Article Validation-related source files were found."
        )

        if current_certification_reference_count == 0:
            reasons.append(
                "Current integrity-certified input consumption "
                "was not confirmed."
            )

        if runtime_registration_count == 0:
            reasons.append(
                "Article Validation Runtime Registration was not found."
            )

    reasons.append(
        f"Article Validation source files found: {source_count}."
    )

    reasons.append(
        f"Article Validation data artifacts found: {artifact_count}."
    )

    reasons.append(
        "Source references: "
        f"UDARE={udare_reference_count}, "
        f"Integrity Certification={current_certification_reference_count}, "
        f"WUC={wuc_reference_count}."
    )

    return decision, reasons


def main() -> int:
    print()
    print("=" * 90)
    print(
        "ARTICLE VALIDATION STAGE — READ-ONLY ARCHITECTURE AND DATA SCAN"
    )
    print("=" * 90)

    all_python_files = (
        active_python_files()
    )

    source_records: list[
        dict[str, Any]
    ] = []

    unrelated_syntax_errors: list[
        dict[str, Any]
    ] = []

    for path in all_python_files:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        if not is_article_validation_source(
            path,
            source,
        ):
            try:
                ast.parse(
                    source,
                    filename=str(path),
                )
            except SyntaxError as exc:
                unrelated_syntax_errors.append(
                    {
                        "path": relative(path),
                        "line": exc.lineno,
                        "error": str(exc),
                    }
                )

            continue

        source_records.append(
            scan_source_file(
                path
            )
        )

    artifact_paths = (
        validation_data_candidates()
    )

    artifact_records: list[
        dict[str, Any]
    ] = []

    for path in artifact_paths:
        if path.suffix.lower() in {
            ".json",
            ".jsonl",
        }:
            artifact_records.append(
                scan_json_artifact(
                    path
                )
            )
        else:
            artifact_records.append(
                {
                    "path": relative(path),
                    "size_bytes": (
                        path.stat().st_size
                    ),
                    "suffix": (
                        path.suffix.lower()
                    ),
                    "parse_status": (
                        "NON_JSON_ARTIFACT"
                    ),
                }
            )

    integrity_certificate = (
        scan_integrity_certificate()
    )

    udare_manifest = (
        scan_udare_manifest()
    )

    runtime_registry = (
        scan_runtime_registry()
    )

    wuc_snapshot = (
        scan_wuc_snapshot()
    )

    decision, reasons = classify(
        source_files=source_records,
        artifacts=artifact_records,
        runtime_registry=runtime_registry,
    )

    current_contract = {
        "required_input_stage": (
            "Website Article Integrity Certification"
        ),
        "required_input_scope": (
            "ACTIVE_UDARE_STORE"
        ),
        "expected_active_input_count": 2219,
        "integrity_quarantined_count": 3,
        "deferred_upstream_count": 3,
        "article_body_modification_allowed": False,
        "wuc_generation_part_of_article_validation": False,
        "expected_next_stage": (
            "Website Unified Content"
        ),
    }

    report = {
        "schema_version": (
            "article_validation_stage_scan_v1"
        ),
        "generated_at": utc_now(),
        "scan_mode": "READ_ONLY",
        "workspace_id": WORKSPACE_ID,
        "project_root": str(
            PROJECT_ROOT
        ),
        "python_files_scanned": len(
            all_python_files
        ),
        "article_validation_source_file_count": len(
            source_records
        ),
        "article_validation_source_files": (
            source_records
        ),
        "article_validation_artifact_count": len(
            artifact_records
        ),
        "article_validation_artifacts": (
            artifact_records
        ),
        "integrity_certificate": (
            integrity_certificate
        ),
        "udare_manifest": (
            udare_manifest
        ),
        "runtime_registry": (
            runtime_registry
        ),
        "wuc_snapshot": (
            wuc_snapshot
        ),
        "current_required_contract": (
            current_contract
        ),
        "decision": decision,
        "decision_reasons": reasons,
        "unrelated_syntax_error_count": len(
            unrelated_syntax_errors
        ),
        "unrelated_syntax_errors": (
            unrelated_syntax_errors
        ),
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

    certification_coverage = (
        integrity_certificate.get(
            "coverage",
            {},
        )
    )

    registered_jobs = (
        runtime_registry.get(
            "article_validation_registrations",
            [],
        )
    )

    legacy_artifact_count = sum(
        1
        for artifact in artifact_records
        if artifact.get(
            "legacy_count_signals"
        )
    )

    current_artifact_count = sum(
        1
        for artifact in artifact_records
        if 2219 in artifact.get(
            "current_count_signals",
            [],
        )
    )

    integrity_reference_count = sum(
        1
        for record in source_records
        if record.get(
            "references_integrity_certification"
        )
    )

    print()
    print(
        f"Python files scanned:                    "
        f"{len(all_python_files)}"
    )

    print(
        f"Article Validation source files:         "
        f"{len(source_records)}"
    )

    print(
        f"Article Validation artifacts:            "
        f"{len(artifact_records)}"
    )

    print(
        f"Legacy-count artifacts:                  "
        f"{legacy_artifact_count}"
    )

    print(
        f"Current 2,219-count artifacts:           "
        f"{current_artifact_count}"
    )

    print(
        f"Integrity-certificate source references: "
        f"{integrity_reference_count}"
    )

    print(
        f"Article Validation runtime registrations:"
        f" {len(registered_jobs)}"
    )

    print()
    print(
        "Current integrity-certified active count: "
        f"{certification_coverage.get('active_certified_count')}"
    )

    print(
        "Current integrity quarantined count:       "
        f"{certification_coverage.get('quarantined_count')}"
    )

    print(
        "Current deferred upstream count:           "
        f"{certification_coverage.get('deferred_upstream_count')}"
    )

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
    print(
        "CURRENT REQUIRED ARTICLE VALIDATION INPUT"
    )

    print(
        "  Active integrity-certified articles: 2,219"
    )

    print(
        "  Integrity-quarantined articles:       3 excluded"
    )

    print(
        "  Deferred upstream pages:              3 excluded"
    )

    print(
        "  Article-body modification:            prohibited"
    )

    print(
        "  Next stage:                           Website Unified Content"
    )

    print()
    print(
        f"Scan report: {REPORT_PATH}"
    )

    print(
        "Source files modified: 0"
    )

    print("=" * 90)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
