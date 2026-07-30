from __future__ import annotations

import ast
import hashlib
import json
import py_compile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd().resolve()

SERVER_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

EVIDENCE_DIR = (
    SERVER_DIR
    / "data"
    / "runtime"
    / "uri_phase_2"
    / "2_1_1_universal_job_contract"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime("%Y%m%dT%H%M%SZ")

REPORT_JSON = (
    EVIDENCE_DIR
    / f"universal_job_contract_targeted_scan_{TIMESTAMP}.json"
)

REPORT_TEXT = (
    EVIDENCE_DIR
    / f"universal_job_contract_targeted_scan_{TIMESTAMP}.txt"
)

SUMMARY_JSON = (
    EVIDENCE_DIR
    / f"universal_job_contract_targeted_summary_{TIMESTAMP}.json"
)


REQUIRED_FIELDS = (
    "job_id",
    "workspace_id",
    "user_id",
    "product_id",
    "pipeline",
    "stage",
    "job_type",
    "payload_reference",
    "priority",
    "status",
    "attempts",
    "maximum_attempts",
    "lease_owner",
    "lease_id",
    "lease_started_at",
    "lease_expires_at",
    "parent_job_id",
    "dependency_job_ids",
    "batch_id",
    "pipeline_run_id",
    "progress",
    "checkpoint_reference",
    "result_reference",
    "artifact_references",
    "idempotency_key",
    "AU_reserved",
    "AU_consumed",
    "cost_record",
    "created_at",
    "scheduled_at",
    "started_at",
    "completed_at",
    "failed_at",
    "cancelled_at",
    "error_code",
    "error_message",
    "error_details",
)


JOB_SYMBOL_TERMS = (
    "job",
    "universaljob",
    "jobrecord",
    "jobcontract",
    "jobrequest",
    "jobresult",
    "create_job",
    "enqueue_job",
    "claim_job",
    "lease_job",
    "complete_job",
    "fail_job",
    "retry_job",
)


LEGACY_BOUNDARY_TERMS = (
    "queue",
    "worker",
    "dispatch",
    "orchestrator",
    "runtime_registration",
    "job_store",
    "job_repository",
    "job_registry",
    "sqlite",
    "jsonl",
    "write_text",
    "write_json",
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def string_value(
    node: ast.AST,
) -> str | None:
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    ):
        return node.value

    return None


def target_names(
    node: ast.AST,
) -> list[str]:
    if isinstance(node, ast.Name):
        return [node.id]

    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []

        for element in node.elts:
            names.extend(
                target_names(element)
            )

        return names

    return []


def extract_dict_keys(
    node: ast.Dict,
) -> list[str]:
    keys: list[str] = []

    for key in node.keys:
        if key is None:
            continue

        value = string_value(key)

        if value is not None:
            keys.append(value)

    return keys


def function_arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    arguments = (
        list(node.args.posonlyargs)
        + list(node.args.args)
        + list(node.args.kwonlyargs)
    )

    if node.args.vararg is not None:
        arguments.append(node.args.vararg)

    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)

    return [
        argument.arg
        for argument in arguments
    ]


def scan_file(
    path: Path,
) -> dict[str, Any] | None:
    try:
        source = path.read_text(
            encoding="utf-8-sig",
        )
    except UnicodeError:
        source = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    source_lower = source.lower()

    lexical_job_hit = any(
        term in source_lower
        for term in JOB_SYMBOL_TERMS
    )

    required_field_hits = [
        field
        for field in REQUIRED_FIELDS
        if field.lower() in source_lower
    ]

    if (
        not lexical_job_hit
        and len(required_field_hits) < 2
    ):
        return None

    result: dict[str, Any] = {
        "relative_path": (
            path.relative_to(
                PROJECT_ROOT
            ).as_posix()
        ),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "compile": "NOT_RUN",
        "ast_parse": "NOT_RUN",
        "classes": [],
        "functions": [],
        "job_named_classes": [],
        "job_named_functions": [],
        "function_contracts": [],
        "dataclass_contracts": [],
        "typed_dict_contracts": [],
        "dict_contracts": [],
        "required_field_hits": (
            required_field_hits
        ),
        "boundary_hits": [],
        "score": 0,
        "error": None,
    }

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )

        result["compile"] = "PASS"

    except Exception as exc:
        result["compile"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

        result["ast_parse"] = "PASS"

    except Exception as exc:
        result["ast_parse"] = "FAIL"

        if result["error"] is None:
            result["error"] = (
                f"{type(exc).__name__}: {exc}"
            )

        return result

    classes: list[str] = []
    functions: list[str] = []
    job_named_classes: list[str] = []
    job_named_functions: list[str] = []
    function_contracts: list[dict[str, Any]] = []
    dataclass_contracts: list[dict[str, Any]] = []
    typed_dict_contracts: list[dict[str, Any]] = []
    dictionary_contracts: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

            if "job" in node.name.lower():
                job_named_classes.append(
                    node.name
                )

            bases = []

            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)

            fields = []

            for child in node.body:
                if isinstance(child, ast.AnnAssign):
                    fields.extend(
                        target_names(
                            child.target
                        )
                    )

            decorators = []

            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(
                        decorator.id
                    )
                elif isinstance(decorator, ast.Call):
                    if isinstance(
                        decorator.func,
                        ast.Name,
                    ):
                        decorators.append(
                            decorator.func.id
                        )

            relevant_fields = [
                field
                for field in fields
                if field in REQUIRED_FIELDS
            ]

            if (
                relevant_fields
                and "dataclass" in decorators
            ):
                dataclass_contracts.append(
                    {
                        "class": node.name,
                        "fields": fields,
                        "required_fields": (
                            relevant_fields
                        ),
                    }
                )

            if (
                relevant_fields
                and "TypedDict" in bases
            ):
                typed_dict_contracts.append(
                    {
                        "class": node.name,
                        "fields": fields,
                        "required_fields": (
                            relevant_fields
                        ),
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(node.name)

            arguments = function_arguments(
                node
            )

            relevant_arguments = [
                argument
                for argument in arguments
                if argument in REQUIRED_FIELDS
            ]

            name_lower = node.name.lower()

            if "job" in name_lower:
                job_named_functions.append(
                    node.name
                )

            if (
                relevant_arguments
                or "job" in name_lower
            ):
                function_contracts.append(
                    {
                        "function": node.name,
                        "arguments": arguments,
                        "required_fields": (
                            relevant_arguments
                        ),
                        "async": isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),
                    }
                )

        elif isinstance(node, ast.Dict):
            keys = extract_dict_keys(
                node
            )

            relevant_keys = [
                key
                for key in keys
                if key in REQUIRED_FIELDS
            ]

            if len(relevant_keys) >= 2:
                dictionary_contracts.append(
                    {
                        "keys": keys,
                        "required_fields": (
                            relevant_keys
                        ),
                    }
                )

    result["classes"] = sorted(
        set(classes)
    )

    result["functions"] = sorted(
        set(functions)
    )

    result["job_named_classes"] = sorted(
        set(job_named_classes)
    )

    result["job_named_functions"] = sorted(
        set(job_named_functions)
    )

    result["function_contracts"] = (
        function_contracts
    )

    result["dataclass_contracts"] = (
        dataclass_contracts
    )

    result["typed_dict_contracts"] = (
        typed_dict_contracts
    )

    result["dict_contracts"] = (
        dictionary_contracts[:25]
    )

    result["boundary_hits"] = [
        term
        for term in LEGACY_BOUNDARY_TERMS
        if term in source_lower
    ]

    result["score"] = (
        len(
            result["job_named_classes"]
        )
        * 30
        + len(
            result["job_named_functions"]
        )
        * 15
        + len(
            result["dataclass_contracts"]
        )
        * 35
        + len(
            result["typed_dict_contracts"]
        )
        * 35
        + min(
            len(
                result["dict_contracts"]
            ),
            10,
        )
        * 10
        + min(
            len(
                required_field_hits
            ),
            38,
        )
        * 2
    )

    if result["score"] == 0:
        return None

    return result


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 2.1.1 — TARGETED UNIVERSAL JOB CONTRACT SCAN")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    candidates: list[dict[str, Any]] = []

    for path in SERVER_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue

        scanned = scan_file(path)

        if scanned is not None:
            candidates.append(
                scanned
            )

    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["relative_path"],
        )
    )

    canonical_candidates = [
        item
        for item in candidates
        if (
            item["dataclass_contracts"]
            or item["typed_dict_contracts"]
            or item["job_named_classes"]
        )
    ]

    legacy_record_candidates = [
        item
        for item in candidates
        if (
            item["dict_contracts"]
            or item["function_contracts"]
        )
    ]

    field_locations: dict[
        str,
        list[str],
    ] = defaultdict(list)

    for item in candidates:
        for field in item[
            "required_field_hits"
        ]:
            field_locations[field].append(
                item["relative_path"]
            )

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if not field_locations[field]
    ]

    conflicting_field_names = {
        "max_attempts": [],
        "retry_count": [],
        "retries": [],
        "payload": [],
        "result": [],
        "output_path": [],
        "owner": [],
        "claimed_by": [],
        "lease_until": [],
    }

    for path in SERVER_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue

        try:
            source_lower = path.read_text(
                encoding="utf-8-sig",
            ).lower()
        except UnicodeError:
            source_lower = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()

        for alias in conflicting_field_names:
            if alias in source_lower:
                conflicting_field_names[
                    alias
                ].append(
                    path.relative_to(
                        PROJECT_ROOT
                    ).as_posix()
                )

    readiness = {
        "canonical_contract_found": bool(
            canonical_candidates
        ),
        "canonical_contract_candidates": len(
            canonical_candidates
        ),
        "legacy_record_candidates": len(
            legacy_record_candidates
        ),
        "missing_required_fields": (
            missing_fields
        ),
        "required_field_coverage": (
            len(REQUIRED_FIELDS)
            - len(missing_fields)
        ),
        "required_field_total": len(
            REQUIRED_FIELDS
        ),
        "recommended_action": (
            "REVIEW_EXISTING_CANONICAL_CANDIDATES"
            if canonical_candidates
            else "BUILD_NEW_CANONICAL_CONTRACT"
        ),
    }

    report = {
        "scan": (
            "Phase 2.1.1 Targeted Universal "
            "Job Contract Discovery"
        ),
        "generated_at": TIMESTAMP,
        "candidate_count": len(
            candidates
        ),
        "canonical_candidates": (
            canonical_candidates
        ),
        "legacy_record_candidates": (
            legacy_record_candidates
        ),
        "all_ranked_candidates": (
            candidates
        ),
        "field_locations": dict(
            field_locations
        ),
        "missing_required_fields": (
            missing_fields
        ),
        "legacy_alias_locations": (
            conflicting_field_names
        ),
        "readiness": readiness,
        "production_files_modified": False,
    }

    summary = {
        "scan": report["scan"],
        "generated_at": TIMESTAMP,
        "candidate_count": len(
            candidates
        ),
        "canonical_candidate_count": len(
            canonical_candidates
        ),
        "legacy_record_candidate_count": len(
            legacy_record_candidates
        ),
        "required_field_coverage": (
            readiness[
                "required_field_coverage"
            ]
        ),
        "required_field_total": (
            readiness[
                "required_field_total"
            ]
        ),
        "missing_required_fields": (
            missing_fields
        ),
        "recommended_action": (
            readiness[
                "recommended_action"
            ]
        ),
        "production_files_modified": False,
    }

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    SUMMARY_JSON.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    lines = [
        "=" * 78,
        "PHASE 2.1.1 TARGETED UNIVERSAL JOB CONTRACT SCAN",
        "=" * 78,
        "",
        (
            f"Ranked candidates: "
            f"{len(candidates)}"
        ),
        (
            "Canonical contract candidates: "
            f"{len(canonical_candidates)}"
        ),
        (
            "Legacy record candidates: "
            f"{len(legacy_record_candidates)}"
        ),
        "",
        "TOP CANDIDATES",
        "-" * 78,
    ]

    print(
        f"Ranked candidates:             "
        f"{len(candidates)}"
    )

    print(
        f"Canonical contract candidates: "
        f"{len(canonical_candidates)}"
    )

    print(
        f"Legacy record candidates:      "
        f"{len(legacy_record_candidates)}"
    )

    print()
    print("TOP CANDIDATES")
    print("-" * 78)

    for item in candidates[:20]:
        print(
            f"Score {item['score']:>4} | "
            f"{item['relative_path']}"
        )

        print(
            "       job classes: "
            + (
                ", ".join(
                    item[
                        "job_named_classes"
                    ]
                )
                or "none"
            )
        )

        print(
            "       job functions: "
            + (
                ", ".join(
                    item[
                        "job_named_functions"
                    ][
                        :8
                    ]
                )
                or "none"
            )
        )

        print(
            "       required fields: "
            f"{len(item['required_field_hits'])}/"
            f"{len(REQUIRED_FIELDS)}"
        )

        print(
            "       boundary hits: "
            + (
                ", ".join(
                    item[
                        "boundary_hits"
                    ]
                )
                or "none"
            )
        )

        lines.extend(
            [
                (
                    f"Score {item['score']:>4} | "
                    f"{item['relative_path']}"
                ),
                (
                    "       job classes: "
                    + (
                        ", ".join(
                            item[
                                "job_named_classes"
                            ]
                        )
                        or "none"
                    )
                ),
                (
                    "       job functions: "
                    + (
                        ", ".join(
                            item[
                                "job_named_functions"
                            ][
                                :8
                            ]
                        )
                        or "none"
                    )
                ),
                (
                    "       required fields: "
                    f"{len(item['required_field_hits'])}/"
                    f"{len(REQUIRED_FIELDS)}"
                ),
                (
                    "       boundary hits: "
                    + (
                        ", ".join(
                            item[
                                "boundary_hits"
                            ]
                        )
                        or "none"
                    )
                ),
            ]
        )

    lines.extend(
        [
            "",
            "REQUIRED FIELD COVERAGE",
            "-" * 78,
        ]
    )

    print()
    print("REQUIRED FIELD COVERAGE")
    print("-" * 78)

    for field in REQUIRED_FIELDS:
        locations = field_locations[
            field
        ]

        marker = (
            "FOUND"
            if locations
            else "MISSING"
        )

        print(
            f"{marker:7} {field}"
        )

        lines.append(
            f"{marker:7} {field}"
        )

        for location in locations[:3]:
            lines.append(
                f"         {location}"
            )

    print()
    print(
        "Required field coverage: "
        f"{readiness['required_field_coverage']}/"
        f"{readiness['required_field_total']}"
    )

    print(
        "Recommended action:      "
        f"{readiness['recommended_action']}"
    )

    print()
    print(f"Evidence JSON: {REPORT_JSON}")
    print(f"Summary JSON:  {SUMMARY_JSON}")
    print(f"Evidence text: {REPORT_TEXT}")
    print()
    print(
        "TARGETED UNIVERSAL JOB CONTRACT SCAN: PASS"
    )
    print(
        "SCAN PASS DOES NOT CERTIFY AN EXISTING CONTRACT"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    lines.extend(
        [
            "",
            (
                "Required field coverage: "
                f"{readiness['required_field_coverage']}/"
                f"{readiness['required_field_total']}"
            ),
            (
                "Recommended action: "
                f"{readiness['recommended_action']}"
            ),
            "",
            f"Evidence JSON: {REPORT_JSON}",
            f"Summary JSON: {SUMMARY_JSON}",
            f"Evidence text: {REPORT_TEXT}",
            "",
            "NO PRODUCTION DATA WAS MODIFIED",
        ]
    )

    REPORT_TEXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
