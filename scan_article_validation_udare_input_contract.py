"""Inspect the UDARE and Integrity input contract for Article Validation."""

from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

MANIFEST_PATH = (
    UDARE_ROOT
    / "manifests"
    / "udare_store_manifest.json"
)

CERTIFICATE_PATH = (
    DATA_ROOT
    / "website_article_integrity"
    / WORKSPACE_ID
    / "certification"
    / "website_article_integrity_certificate.json"
)

UDARE_STORE_SOURCE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "stores"
    / "udare_store.py"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_udare_input_contract_scan.json"
)


def load_json(
    path: Path,
) -> Any:
    return json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )


def describe_json(
    value: Any,
    *,
    depth: int = 0,
    max_depth: int = 3,
) -> Any:
    if depth >= max_depth:
        if isinstance(value, list):
            return {
                "type": "list",
                "length": len(value),
            }

        if isinstance(value, dict):
            return {
                "type": "dict",
                "keys": sorted(
                    str(key)
                    for key in value.keys()
                ),
            }

        return {
            "type": type(value).__name__,
            "value": value,
        }

    if isinstance(value, dict):
        return {
            str(key): describe_json(
                item,
                depth=depth + 1,
                max_depth=max_depth,
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return {
            "type": "list",
            "length": len(value),
            "sample": [
                describe_json(
                    item,
                    depth=depth + 1,
                    max_depth=max_depth,
                )
                for item in value[:2]
            ],
        }

    return value


def source_functions(
    path: Path,
) -> list[dict[str, Any]]:
    source = path.read_text(
        encoding="utf-8-sig",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    records: list[dict[str, Any]] = []

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        arguments = [
            argument.arg
            for argument in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            )
        ]

        records.append(
            {
                "name": node.name,
                "line": node.lineno,
                "end_line": node.end_lineno,
                "arguments": arguments,
            }
        )

    return records


def sample_article_documents() -> list[dict[str, Any]]:
    articles_root = (
        UDARE_ROOT
        / "articles"
    )

    if not articles_root.is_dir():
        return []

    records: list[dict[str, Any]] = []

    for path in sorted(
        articles_root.glob("*.html")
    )[:3]:
        text = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        records.append(
            {
                "path": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "size_bytes": path.stat().st_size,
                "first_500_characters": text[:500],
            }
        )

    return records


def sample_metadata_documents() -> list[dict[str, Any]]:
    candidates = []

    for directory_name in (
        "metadata",
        "records",
        "manifests",
    ):
        root = (
            UDARE_ROOT
            / directory_name
        )

        if not root.is_dir():
            continue

        candidates.extend(
            sorted(
                root.glob("*.json")
            )
        )

    records: list[dict[str, Any]] = []

    for path in candidates[:3]:
        try:
            value = load_json(path)

            records.append(
                {
                    "path": str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "description": describe_json(
                        value,
                        max_depth=3,
                    ),
                }
            )

        except Exception as exc:
            records.append(
                {
                    "path": str(path),
                    "error": repr(exc),
                }
            )

    return records


def main() -> int:
    print()
    print("=" * 92)
    print(
        "ARTICLE VALIDATION — UDARE CERTIFIED INPUT CONTRACT SCAN"
    )
    print("=" * 92)

    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"UDARE manifest missing: {MANIFEST_PATH}"
        )

    if not CERTIFICATE_PATH.is_file():
        raise FileNotFoundError(
            f"Integrity certificate missing: {CERTIFICATE_PATH}"
        )

    if not UDARE_STORE_SOURCE_PATH.is_file():
        raise FileNotFoundError(
            f"UDARE store source missing: {UDARE_STORE_SOURCE_PATH}"
        )

    manifest = load_json(
        MANIFEST_PATH
    )

    certificate = load_json(
        CERTIFICATE_PATH
    )

    functions = source_functions(
        UDARE_STORE_SOURCE_PATH
    )

    relevant_functions = [
        record
        for record in functions
        if any(
            term in record["name"].lower()
            for term in (
                "load",
                "validate",
                "article",
                "manifest",
                "list",
                "iter",
            )
        )
    ]

    articles_root = (
        UDARE_ROOT
        / "articles"
    )

    article_paths = (
        sorted(
            articles_root.glob("*.html")
        )
        if articles_root.is_dir()
        else []
    )

    report = {
        "schema_version": (
            "article_validation_"
            "udare_input_contract_scan_v1"
        ),
        "scan_mode": "READ_ONLY",
        "workspace_id": WORKSPACE_ID,
        "udare_root": str(
            UDARE_ROOT
        ),
        "manifest_path": str(
            MANIFEST_PATH
        ),
        "manifest_description": (
            describe_json(
                manifest,
                max_depth=4,
            )
        ),
        "integrity_certificate_path": str(
            CERTIFICATE_PATH
        ),
        "integrity_certificate_description": (
            describe_json(
                certificate,
                max_depth=4,
            )
        ),
        "active_html_document_count": len(
            article_paths
        ),
        "sample_article_documents": (
            sample_article_documents()
        ),
        "sample_metadata_documents": (
            sample_metadata_documents()
        ),
        "udare_store_functions": (
            relevant_functions
        ),
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

    coverage = certificate.get(
        "coverage",
        {}
    )

    print()
    print(
        "Active UDARE HTML documents:          "
        + str(
            len(article_paths)
        )
    )

    print(
        "Certificate status:                   "
        + str(
            certificate.get(
                "certification_status"
            )
        )
    )

    print(
        "Certificate ID:                       "
        + str(
            certificate.get(
                "certificate_id"
            )
        )
    )

    print(
        "Certified active count:               "
        + str(
            coverage.get(
                "active_certified_count"
            )
        )
    )

    print(
        "Integrity-quarantined count:           "
        + str(
            coverage.get(
                "quarantined_count"
            )
        )
    )

    print(
        "Deferred upstream count:               "
        + str(
            coverage.get(
                "deferred_upstream_count"
            )
        )
    )

    print()
    print("UDARE STORE FUNCTIONS")

    for record in relevant_functions:
        print(
            "  "
            + record["name"]
            + "("
            + ", ".join(
                record["arguments"]
            )
            + ")"
            + f"  lines {record['line']}-{record['end_line']}"
        )

    print()
    print("MANIFEST TOP-LEVEL KEYS")

    for key in sorted(
        str(key)
        for key in manifest.keys()
    ):
        print(
            "  - "
            + key
        )

    print()
    print("CERTIFICATE TOP-LEVEL KEYS")

    for key in sorted(
        str(key)
        for key in certificate.keys()
    ):
        print(
            "  - "
            + key
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

    print("=" * 92)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
