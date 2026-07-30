from __future__ import annotations

import ast
import hashlib
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd().resolve()

TARGET_FILES = (
    PROJECT_ROOT / "backend/server/orchestration/models.py",
    PROJECT_ROOT / "backend/server/orchestration/schemas.py",
    PROJECT_ROOT / "backend/server/orchestration/job_store.py",
    PROJECT_ROOT / "backend/server/jobs/universal_knowledge_orchestrator.py",
    PROJECT_ROOT / "backend/server/runtime/udare_runtime_contract.py",
    PROJECT_ROOT / "backend/server/runtime/website_article_integrity_automation.py",
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend/server/data/runtime/uri_phase_2"
    / "2_1_1_universal_job_contract"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime("%Y%m%dT%H%M%SZ")

REPORT_JSON = (
    EVIDENCE_DIR
    / f"legacy_job_contract_exact_scan_{TIMESTAMP}.json"
)

REPORT_TEXT = (
    EVIDENCE_DIR
    / f"legacy_job_contract_exact_scan_{TIMESTAMP}.txt"
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


LEGACY_ALIASES = (
    "max_attempts",
    "retry_count",
    "retries",
    "payload",
    "result",
    "output_path",
    "claimed_by",
    "lease_until",
    "error",
    "metadata",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def annotation_text(node: ast.AST | None) -> str | None:
    if node is None:
        return None

    try:
        return ast.unparse(node)
    except Exception:
        return None


def default_text(node: ast.AST | None) -> str | None:
    if node is None:
        return None

    try:
        return ast.unparse(node)
    except Exception:
        return None


def class_contract(node: ast.ClassDef) -> dict[str, Any]:
    fields: list[dict[str, Any]] = []
    methods: list[dict[str, Any]] = []

    decorators = [
        ast.unparse(item)
        for item in node.decorator_list
    ]

    bases = [
        ast.unparse(base)
        for base in node.bases
    ]

    for child in node.body:
        if isinstance(child, ast.AnnAssign):
            if isinstance(child.target, ast.Name):
                fields.append(
                    {
                        "name": child.target.id,
                        "annotation": annotation_text(
                            child.annotation
                        ),
                        "default": default_text(
                            child.value
                        ),
                    }
                )

        elif isinstance(child, ast.Assign):
            value = default_text(child.value)

            for target in child.targets:
                if isinstance(target, ast.Name):
                    fields.append(
                        {
                            "name": target.id,
                            "annotation": None,
                            "default": value,
                        }
                    )

        elif isinstance(
            child,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            methods.append(
                {
                    "name": child.name,
                    "async": isinstance(
                        child,
                        ast.AsyncFunctionDef,
                    ),
                    "arguments": [
                        argument.arg
                        for argument in (
                            list(child.args.posonlyargs)
                            + list(child.args.args)
                            + list(child.args.kwonlyargs)
                        )
                    ],
                    "returns": annotation_text(
                        child.returns
                    ),
                }
            )

    return {
        "name": node.name,
        "decorators": decorators,
        "bases": bases,
        "fields": fields,
        "required_field_matches": [
            field["name"]
            for field in fields
            if field["name"] in REQUIRED_FIELDS
        ],
        "legacy_alias_matches": [
            field["name"]
            for field in fields
            if field["name"] in LEGACY_ALIASES
        ],
        "methods": methods,
    }


def function_contract(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, Any]:
    arguments = (
        list(node.args.posonlyargs)
        + list(node.args.args)
        + list(node.args.kwonlyargs)
    )

    argument_names = [
        item.arg
        for item in arguments
    ]

    return {
        "name": node.name,
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "arguments": argument_names,
        "required_field_matches": [
            item
            for item in argument_names
            if item in REQUIRED_FIELDS
        ],
        "legacy_alias_matches": [
            item
            for item in argument_names
            if item in LEGACY_ALIASES
        ],
        "returns": annotation_text(
            node.returns
        ),
    }


def dictionary_contract(node: ast.Dict) -> dict[str, Any] | None:
    keys: list[str] = []

    for key in node.keys:
        if (
            isinstance(key, ast.Constant)
            and isinstance(key.value, str)
        ):
            keys.append(key.value)

    matches = [
        key
        for key in keys
        if key in REQUIRED_FIELDS
    ]

    aliases = [
        key
        for key in keys
        if key in LEGACY_ALIASES
    ]

    if not matches and not aliases:
        return None

    return {
        "keys": keys,
        "required_field_matches": matches,
        "legacy_alias_matches": aliases,
    }


def scan_file(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "relative_path": (
            path.relative_to(PROJECT_ROOT).as_posix()
        ),
        "exists": path.exists(),
        "size": None,
        "sha256": None,
        "compile": "NOT_RUN",
        "ast_parse": "NOT_RUN",
        "classes": [],
        "functions": [],
        "dictionaries": [],
        "all_required_field_mentions": [],
        "all_legacy_alias_mentions": [],
        "error": None,
    }

    if not path.exists():
        result["error"] = "FILE_MISSING"
        return result

    result["size"] = path.stat().st_size
    result["sha256"] = sha256_file(path)

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
        return result

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )
        result["ast_parse"] = "PASS"
    except Exception as exc:
        result["ast_parse"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )
        return result

    result["classes"] = [
        class_contract(node)
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    ]

    result["functions"] = [
        function_contract(node)
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    dictionaries = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            contract = dictionary_contract(node)

            if contract is not None:
                dictionaries.append(contract)

    result["dictionaries"] = dictionaries[:100]

    source_lower = source.lower()

    result["all_required_field_mentions"] = [
        field
        for field in REQUIRED_FIELDS
        if field.lower() in source_lower
    ]

    result["all_legacy_alias_mentions"] = [
        alias
        for alias in LEGACY_ALIASES
        if alias.lower() in source_lower
    ]

    return result


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("2.1.1 — EXACT LEGACY JOB CONTRACT EXTRACTION")
    print("=" * 78)
    print()

    results = [
        scan_file(path)
        for path in TARGET_FILES
    ]

    complete_contracts = []

    for result in results:
        for contract in result["classes"]:
            complete_contracts.append(
                {
                    "file": result["relative_path"],
                    "kind": "class",
                    "name": contract["name"],
                    "field_count": len(
                        contract[
                            "required_field_matches"
                        ]
                    ),
                    "fields": contract[
                        "required_field_matches"
                    ],
                    "aliases": contract[
                        "legacy_alias_matches"
                    ],
                }
            )

        for index, contract in enumerate(
            result["dictionaries"],
            start=1,
        ):
            complete_contracts.append(
                {
                    "file": result["relative_path"],
                    "kind": "dictionary",
                    "name": f"dictionary_{index}",
                    "field_count": len(
                        contract[
                            "required_field_matches"
                        ]
                    ),
                    "fields": contract[
                        "required_field_matches"
                    ],
                    "aliases": contract[
                        "legacy_alias_matches"
                    ],
                }
            )

    complete_contracts.sort(
        key=lambda item: (
            -item["field_count"],
            item["file"],
            item["name"],
        )
    )

    maximum_coverage = (
        complete_contracts[0]["field_count"]
        if complete_contracts
        else 0
    )

    canonical_contract_found = (
        maximum_coverage
        == len(REQUIRED_FIELDS)
    )

    report = {
        "scan": (
            "2.1.1 Exact Legacy Job Contract Extraction"
        ),
        "generated_at": TIMESTAMP,
        "required_field_total": len(
            REQUIRED_FIELDS
        ),
        "files": results,
        "ranked_contracts": complete_contracts,
        "maximum_single_contract_coverage": (
            maximum_coverage
        ),
        "canonical_contract_found": (
            canonical_contract_found
        ),
        "recommended_action": (
            "ADOPT_EXISTING_CONTRACT"
            if canonical_contract_found
            else "BUILD_NEW_CANONICAL_CONTRACT_WITH_LEGACY_ADAPTERS"
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

    lines = [
        "=" * 78,
        "2.1.1 EXACT LEGACY JOB CONTRACT EXTRACTION",
        "=" * 78,
        "",
    ]

    for result in results:
        status = (
            "PASS"
            if (
                result["exists"]
                and result["compile"] == "PASS"
                and result["ast_parse"] == "PASS"
            )
            else "FAIL"
        )

        print(
            f"{status:4} {result['relative_path']}"
        )

        print(
            "     field mentions: "
            f"{len(result['all_required_field_mentions'])}/"
            f"{len(REQUIRED_FIELDS)}"
        )

        print(
            "     classes:        "
            f"{len(result['classes'])}"
        )

        print(
            "     dictionaries:   "
            f"{len(result['dictionaries'])}"
        )

        lines.extend(
            [
                (
                    f"{status:4} "
                    f"{result['relative_path']}"
                ),
                (
                    "     field mentions: "
                    f"{len(result['all_required_field_mentions'])}/"
                    f"{len(REQUIRED_FIELDS)}"
                ),
                (
                    "     classes: "
                    f"{len(result['classes'])}"
                ),
                (
                    "     dictionaries: "
                    f"{len(result['dictionaries'])}"
                ),
            ]
        )

    print()
    print("TOP EXACT CONTRACT STRUCTURES")
    print("-" * 78)

    lines.extend(
        [
            "",
            "TOP EXACT CONTRACT STRUCTURES",
            "-" * 78,
        ]
    )

    for contract in complete_contracts[:20]:
        print(
            f"{contract['field_count']:>2}/"
            f"{len(REQUIRED_FIELDS)} | "
            f"{contract['kind']:10} | "
            f"{contract['file']} | "
            f"{contract['name']}"
        )

        print(
            "       fields: "
            + (
                ", ".join(contract["fields"])
                or "none"
            )
        )

        print(
            "       aliases: "
            + (
                ", ".join(contract["aliases"])
                or "none"
            )
        )

        lines.extend(
            [
                (
                    f"{contract['field_count']:>2}/"
                    f"{len(REQUIRED_FIELDS)} | "
                    f"{contract['kind']:10} | "
                    f"{contract['file']} | "
                    f"{contract['name']}"
                ),
                (
                    "       fields: "
                    + (
                        ", ".join(contract["fields"])
                        or "none"
                    )
                ),
                (
                    "       aliases: "
                    + (
                        ", ".join(contract["aliases"])
                        or "none"
                    )
                ),
            ]
        )

    print()
    print(
        "Maximum single-contract coverage: "
        f"{maximum_coverage}/{len(REQUIRED_FIELDS)}"
    )

    print(
        "Canonical contract found:          "
        f"{canonical_contract_found}"
    )

    print(
        "Recommended action:                "
        f"{report['recommended_action']}"
    )

    print()
    print(f"Evidence JSON: {REPORT_JSON}")
    print(f"Evidence text: {REPORT_TEXT}")
    print()
    print(
        "EXACT LEGACY JOB CONTRACT SCAN: PASS"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    lines.extend(
        [
            "",
            (
                "Maximum single-contract coverage: "
                f"{maximum_coverage}/"
                f"{len(REQUIRED_FIELDS)}"
            ),
            (
                "Canonical contract found: "
                f"{canonical_contract_found}"
            ),
            (
                "Recommended action: "
                f"{report['recommended_action']}"
            ),
            "",
            f"Evidence JSON: {REPORT_JSON}",
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
    raise SystemExit(main())
