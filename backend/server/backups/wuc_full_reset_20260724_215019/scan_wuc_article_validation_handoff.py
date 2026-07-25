"""Read-only scan of the Article Validation to WUC handoff."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


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

ARTICLE_VALIDATION_SCAN_ROOT = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
)

ARTICLE_VALIDATION_EVIDENCE_ROOT = (
    DATA_ROOT
    / "article_validation_evidence"
    / WORKSPACE_ID
)

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

UDARE_ARTICLES_ROOT = (
    UDARE_ROOT
    / "articles"
)

OUTPUT_REPORT_PATH = (
    ARTICLE_VALIDATION_SCAN_ROOT
    / "website_unified_content_handoff_scan.json"
)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

EXPECTED_PASS_COUNT = 2219

BODY_FIELD_NAMES = {
    "article_body",
    "body",
    "body_html",
    "content_body",
    "content_html",
    "html",
    "raw_html",
    "clean_html",
    "article_html",
    "text",
    "full_text",
}

WUC_NAME_TERMS = {
    "website_unified_content",
    "website unified content",
    "wuc",
}

HANDOFF_TERMS = {
    "article_validation_pass_manifest",
    "pass_manifest",
    "article_validation",
    "article_reference",
    "article_path",
    "article_sha256",
    "udare_store",
    "udare",
}

WRITE_CALL_NAMES = {
    "write_text",
    "write_bytes",
    "open",
    "mkdir",
    "replace",
    "rename",
    "copy",
    "copy2",
    "copyfile",
    "copytree",
    "move",
}

INTERMEDIATE_STORE_TERMS = {
    "website_unified_content_store",
    "wuc_store",
    "website_content_store",
    "unified_content_store",
    "certified_website_article_store",
    "article_validation_store",
}

ALLOWED_WUC_EVIDENCE_TERMS = {
    "report",
    "verification",
    "manifest",
    "ledger",
    "certificate",
    "diagnostic",
    "status",
    "progress",
    "runtime",
    "audit",
    "checkpoint",
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
            path.resolve().relative_to(
                PROJECT_ROOT
            )
        )

    except ValueError:
        return str(
            path.resolve()
        )


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


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    output: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                value = json.loads(
                    stripped
                )

            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL at {path}:{line_number}"
                ) from exc

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    f"Expected object at {path}:{line_number}"
                )

            output.append(
                value
            )

    return output


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


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def resolve_reference(
    value: Any,
) -> Path:
    raw = str(
        value or ""
    ).strip()

    if not raw:
        raise RuntimeError(
            "Empty article reference."
        )

    path = Path(
        raw
    )

    if not path.is_absolute():
        path = (
            PROJECT_ROOT
            / path
        )

    return path.resolve()


def find_authoritative_population_report() -> Path:
    preferred = (
        ARTICLE_VALIDATION_SCAN_ROOT
        / "article_validation_population_v3_verification.json"
    )

    if preferred.is_file():
        report = load_json(
            preferred
        )

        if (
            str(
                report.get(
                    "verification_status"
                )
                or ""
            ).upper()
            == "PASS"
            and int(
                report.get(
                    "pass_count"
                )
                or report.get(
                    "article_validation_pass_count"
                )
                or 0
            )
            == EXPECTED_PASS_COUNT
        ):
            return preferred

    candidates = sorted(
        ARTICLE_VALIDATION_SCAN_ROOT.glob(
            "*population*v3*verification*.json"
        ),
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    for path in candidates:
        try:
            report = load_json(
                path
            )

        except Exception:
            continue

        pass_count = int(
            report.get(
                "pass_count"
            )
            or report.get(
                "article_validation_pass_count"
            )
            or 0
        )

        fail_count = int(
            report.get(
                "fail_count"
            )
            or report.get(
                "article_validation_fail_count"
            )
            or 0
        )

        if (
            pass_count
            == EXPECTED_PASS_COUNT
            and fail_count
            == 0
        ):
            return path

    raise FileNotFoundError(
        "Could not locate the authoritative "
        "2,219 PASS / 0 FAIL Article Validation report."
    )


def find_artifact_path(
    report: dict[str, Any],
    candidate_keys: Iterable[str],
) -> Path | None:
    artifact_paths = report.get(
        "artifact_paths"
    )

    mappings: list[
        dict[str, Any]
    ] = []

    if isinstance(
        artifact_paths,
        dict,
    ):
        mappings.append(
            artifact_paths
        )

    mappings.append(
        report
    )

    for mapping in mappings:
        for key in candidate_keys:
            value = mapping.get(
                key
            )

            if not value:
                continue

            path = resolve_reference(
                value
            )

            if path.is_file():
                return path

    return None


def find_pass_manifest(
    report: dict[str, Any],
) -> Path:
    direct = find_artifact_path(
        report,
        (
            "pass_manifest",
            "article_validation_pass_manifest",
            "pass_manifest_path",
            "article_validation_pass_manifest_path",
        ),
    )

    if direct is not None:
        return direct

    run_id = str(
        report.get(
            "run_id"
        )
        or ""
    ).strip()

    search_roots: list[
        Path
    ] = []

    if run_id:
        search_roots.append(
            ARTICLE_VALIDATION_EVIDENCE_ROOT
            / "runs"
            / run_id
        )

    search_roots.extend(
        [
            ARTICLE_VALIDATION_EVIDENCE_ROOT,
            DATA_ROOT,
        ]
    )

    candidates: list[
        Path
    ] = []

    for root in search_roots:
        if not root.is_dir():
            continue

        for pattern in (
            "article_validation_pass_manifest.jsonl",
            "*pass*manifest*.jsonl",
        ):
            for path in root.rglob(
                pattern
            ):
                if excluded(
                    path
                ):
                    continue

                candidates.append(
                    path.resolve()
                )

    unique_candidates = sorted(
        set(
            candidates
        ),
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    for path in unique_candidates:
        try:
            count = sum(
                1
                for line in path.read_text(
                    encoding="utf-8-sig",
                ).splitlines()
                if line.strip()
            )

        except Exception:
            continue

        if count == EXPECTED_PASS_COUNT:
            return path

    raise FileNotFoundError(
        "Could not locate the authoritative "
        "Article Validation PASS manifest."
    )


def detect_body_fields(
    value: Any,
    *,
    prefix: str = "",
) -> list[str]:
    findings: list[
        str
    ] = []

    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            key_text = str(
                key
            )

            child_prefix = (
                f"{prefix}.{key_text}"
                if prefix
                else key_text
            )

            if (
                key_text.casefold()
                in BODY_FIELD_NAMES
            ):
                findings.append(
                    child_prefix
                )

            findings.extend(
                detect_body_fields(
                    child,
                    prefix=child_prefix,
                )
            )

    elif isinstance(
        value,
        list,
    ):
        for index, child in enumerate(
            value
        ):
            findings.extend(
                detect_body_fields(
                    child,
                    prefix=(
                        f"{prefix}[{index}]"
                    ),
                )
            )

    return findings


def inspect_python_file(
    path: Path,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "syntax_valid":
            True,

        "syntax_error":
            None,

        "functions":
            [],

        "classes":
            [],

        "imports":
            [],

        "handoff_lines":
            [],

        "intermediate_store_lines":
            [],

        "write_operations":
            [],

        "path_assignments":
            [],
    }

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    lines = source.splitlines()

    for line_number, line in enumerate(
        lines,
        start=1,
    ):
        lowered = line.casefold()

        matched_handoff_terms = sorted(
            term
            for term in HANDOFF_TERMS
            if term in lowered
        )

        if matched_handoff_terms:
            result[
                "handoff_lines"
            ].append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        matched_handoff_terms,

                    "line":
                        line.strip()[:500],
                }
            )

        matched_store_terms = sorted(
            term
            for term in INTERMEDIATE_STORE_TERMS
            if term in lowered
        )

        if matched_store_terms:
            result[
                "intermediate_store_lines"
            ].append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        matched_store_terms,

                    "line":
                        line.strip()[:500],
                }
            )

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
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

    for node in ast.walk(
        tree
    ):
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
            ast.Import,
        ):
            for alias in node.names:
                result[
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
                result[
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

            if called_name in WRITE_CALL_NAMES:
                try:
                    rendered = ast.unparse(
                        node
                    )

                except Exception:
                    rendered = (
                        called_name
                    )

                result[
                    "write_operations"
                ].append(
                    {
                        "line_number":
                            node.lineno,

                        "function":
                            called_name,

                        "call":
                            rendered[:1000],
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

                if any(
                    term in name.casefold()
                    for term in (
                        "path",
                        "store",
                        "output",
                        "root",
                        "manifest",
                        "article",
                    )
                ):
                    try:
                        rendered = ast.unparse(
                            node.value
                        )

                    except Exception:
                        rendered = "..."

                    result[
                        "path_assignments"
                    ].append(
                        {
                            "name":
                                name,

                            "line_number":
                                node.lineno,

                            "value":
                                rendered[:1000],
                        }
                    )

    for key in (
        "functions",
        "classes",
        "imports",
        "handoff_lines",
        "intermediate_store_lines",
        "write_operations",
        "path_assignments",
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
                str(
                    item
                ),
            )
        )

    return result


def classify_wuc_file(
    path: Path,
    inspection: dict[str, Any],
) -> str:
    lowered_path = relative(
        path
    ).casefold()

    if "orchestrator" in lowered_path:
        return "ORCHESTRATOR"

    if "worker" in lowered_path:
        return "WORKER"

    if "runtime" in lowered_path:
        return "RUNTIME"

    if "route" in lowered_path:
        return "ROUTE"

    if inspection[
        "handoff_lines"
    ]:
        return "HANDOFF_READER_OR_PROCESSOR"

    return "WUC_RELATED"


def find_active_wuc_files() -> list[Path]:
    candidates: set[
        Path
    ] = set()

    for path in SERVER_ROOT.rglob(
        "*.py"
    ):
        if (
            excluded(
                path
            )
            or not path.is_file()
        ):
            continue

        lowered_path = relative(
            path
        ).casefold()

        if any(
            term.replace(
                " ",
                "_",
            )
            in lowered_path
            for term in WUC_NAME_TERMS
        ):
            candidates.add(
                path.resolve()
            )

            continue

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        ).casefold()

        if (
            "website_unified_content"
            in source
        ):
            candidates.add(
                path.resolve()
            )

    return sorted(
        candidates,
        key=lambda path: (
            relative(
                path
            )
        ),
    )


def find_suspicious_wuc_directories() -> list[dict[str, Any]]:
    findings: list[
        dict[str, Any]
    ] = []

    for path in DATA_ROOT.rglob(
        "*"
    ):
        if (
            not path.is_dir()
            or excluded(
                path
            )
        ):
            continue

        name = path.name.casefold()
        full = relative(
            path
        ).casefold()

        wuc_named = (
            "website_unified_content"
            in name
            or name
            in {
                "wuc",
                "wuc_store",
                "website_content_store",
                "website_unified_content_store",
            }
        )

        if not wuc_named:
            continue

        file_count = sum(
            1
            for candidate in path.rglob(
                "*"
            )
            if candidate.is_file()
        )

        html_count = sum(
            1
            for candidate in path.rglob(
                "*.html"
            )
            if candidate.is_file()
        )

        body_like_count = sum(
            1
            for candidate in path.rglob(
                "*"
            )
            if (
                candidate.is_file()
                and any(
                    term in candidate.name.casefold()
                    for term in (
                        "body",
                        "article",
                        "content",
                    )
                )
            )
        )

        allowed_evidence_only = (
            any(
                term in full
                for term in ALLOWED_WUC_EVIDENCE_TERMS
            )
            and html_count == 0
        )

        findings.append(
            {
                "path":
                    relative(
                        path
                    ),

                "file_count":
                    file_count,

                "html_file_count":
                    html_count,

                "body_or_article_named_file_count":
                    body_like_count,

                "appears_evidence_only":
                    allowed_evidence_only,

                "potential_intermediate_store":
                    (
                        html_count > 0
                        or (
                            body_like_count > 0
                            and not allowed_evidence_only
                        )
                    ),
            }
        )

    return sorted(
        findings,
        key=lambda item: (
            item[
                "path"
            ]
        ),
    )


print()
print("=" * 108)
print(
    "WEBSITE UNIFIED CONTENT — ARTICLE VALIDATION HANDOFF SCAN"
)
print("=" * 108)

failures: list[
    str
] = []

warnings: list[
    str
] = []

population_report_path = (
    find_authoritative_population_report()
)

population_report = load_json(
    population_report_path
)

pass_manifest_path = find_pass_manifest(
    population_report
)

pass_records = load_jsonl(
    pass_manifest_path
)

if len(
    pass_records
) != EXPECTED_PASS_COUNT:
    failures.append(
        "Authoritative PASS manifest count is not "
        f"{EXPECTED_PASS_COUNT}: {len(pass_records)}"
    )

record_ids: list[
    str
] = []

missing_reference_records: list[
    str
] = []

missing_article_files: list[
    dict[str, Any]
] = []

references_outside_udare: list[
    dict[str, Any]
] = []

hash_mismatches: list[
    dict[str, Any]
] = []

body_field_findings: list[
    dict[str, Any]
] = []

reference_field_counts: Counter[
    str
] = Counter()

hash_field_counts: Counter[
    str
] = Counter()

resolved_article_paths: list[
    Path
] = []


for index, record in enumerate(
    pass_records
):
    record_id = str(
        record.get(
            "source_record_id"
        )
        or record.get(
            "document_id"
        )
        or record.get(
            "article_id"
        )
        or f"record_{index + 1}"
    )

    record_ids.append(
        record_id
    )

    found_body_fields = detect_body_fields(
        record
    )

    if found_body_fields:
        body_field_findings.append(
            {
                "source_record_id":
                    record_id,

                "body_fields":
                    found_body_fields,
            }
        )

    reference_value = None
    reference_field = None

    for candidate_field in (
        "article_reference",
        "article_path",
        "source_article_path",
        "udare_article_path",
        "content_ref",
    ):
        candidate_value = record.get(
            candidate_field
        )

        if candidate_value:
            reference_value = (
                candidate_value
            )

            reference_field = (
                candidate_field
            )

            break

    if reference_value is None:
        missing_reference_records.append(
            record_id
        )

        continue

    reference_field_counts[
        str(
            reference_field
        )
    ] += 1

    try:
        article_path = resolve_reference(
            reference_value
        )

    except Exception as exc:
        missing_article_files.append(
            {
                "source_record_id":
                    record_id,

                "article_reference":
                    str(
                        reference_value
                    ),

                "error":
                    str(
                        exc
                    ),
            }
        )

        continue

    resolved_article_paths.append(
        article_path
    )

    try:
        article_path.relative_to(
            UDARE_ARTICLES_ROOT.resolve()
        )

    except ValueError:
        references_outside_udare.append(
            {
                "source_record_id":
                    record_id,

                "article_reference":
                    str(
                        reference_value
                    ),

                "resolved_path":
                    str(
                        article_path
                    ),
            }
        )

    if not article_path.is_file():
        missing_article_files.append(
            {
                "source_record_id":
                    record_id,

                "article_reference":
                    str(
                        reference_value
                    ),

                "resolved_path":
                    str(
                        article_path
                    ),
            }
        )

        continue

    expected_hash = None
    hash_field = None

    for candidate_field in (
        "article_sha256",
        "article_hash",
        "content_hash",
        "source_sha256",
    ):
        candidate_value = record.get(
            candidate_field
        )

        if candidate_value:
            expected_hash = str(
                candidate_value
            ).strip().lower()

            hash_field = (
                candidate_field
            )

            break

    if expected_hash:
        hash_field_counts[
            str(
                hash_field
            )
        ] += 1

        actual_hash = sha256_file(
            article_path
        )

        if (
            expected_hash
            != actual_hash
        ):
            hash_mismatches.append(
                {
                    "source_record_id":
                        record_id,

                    "article_reference":
                        str(
                            reference_value
                        ),

                    "expected_sha256":
                        expected_hash,

                    "actual_sha256":
                        actual_hash,
                }
            )


duplicate_record_ids = sorted(
    record_id
    for record_id, count in Counter(
        record_ids
    ).items()
    if count > 1
)

duplicate_article_paths = sorted(
    str(
        path
    )
    for path, count in Counter(
        resolved_article_paths
    ).items()
    if count > 1
)


if missing_reference_records:
    failures.append(
        "PASS records without an article reference: "
        + str(
            len(
                missing_reference_records
            )
        )
    )

if missing_article_files:
    failures.append(
        "Referenced UDARE article files missing: "
        + str(
            len(
                missing_article_files
            )
        )
    )

if references_outside_udare:
    failures.append(
        "PASS records referencing files outside "
        "the UDARE articles directory: "
        + str(
            len(
                references_outside_udare
            )
        )
    )

if hash_mismatches:
    failures.append(
        "Referenced UDARE article hash mismatches: "
        + str(
            len(
                hash_mismatches
            )
        )
    )

if body_field_findings:
    failures.append(
        "Article Validation PASS records contain "
        "article-body fields: "
        + str(
            len(
                body_field_findings
            )
        )
    )

if duplicate_record_ids:
    failures.append(
        "Duplicate source record identifiers: "
        + str(
            len(
                duplicate_record_ids
            )
        )
    )

if duplicate_article_paths:
    failures.append(
        "Duplicate UDARE article references: "
        + str(
            len(
                duplicate_article_paths
            )
        )
    )


wuc_files = find_active_wuc_files()

wuc_inspections: list[
    dict[str, Any]
] = []

for path in wuc_files:
    inspection = inspect_python_file(
        path
    )

    inspection[
        "classification"
    ] = classify_wuc_file(
        path,
        inspection,
    )

    wuc_inspections.append(
        inspection
    )


wuc_syntax_failures = [
    inspection[
        "path"
    ]
    for inspection in wuc_inspections
    if not inspection[
        "syntax_valid"
    ]
]

handoff_aware_files = [
    inspection[
        "path"
    ]
    for inspection in wuc_inspections
    if inspection[
        "handoff_lines"
    ]
]

files_with_intermediate_store_terms = [
    {
        "path":
            inspection[
                "path"
            ],

        "lines":
            inspection[
                "intermediate_store_lines"
            ],
    }
    for inspection in wuc_inspections
    if inspection[
        "intermediate_store_lines"
    ]
]

files_with_write_operations = [
    {
        "path":
            inspection[
                "path"
            ],

        "write_operations":
            inspection[
                "write_operations"
            ],
    }
    for inspection in wuc_inspections
    if inspection[
        "write_operations"
    ]
]


suspicious_wuc_directories = (
    find_suspicious_wuc_directories()
)

potential_intermediate_directories = [
    item
    for item in suspicious_wuc_directories
    if item[
        "potential_intermediate_store"
    ]
]


if not wuc_files:
    warnings.append(
        "No active WUC-related Python files were detected."
    )

if not handoff_aware_files:
    warnings.append(
        "No active WUC file clearly references "
        "Article Validation, PASS manifests, or UDARE."
    )

if wuc_syntax_failures:
    warnings.append(
        "WUC-related Python syntax failures detected: "
        + str(
            len(
                wuc_syntax_failures
            )
        )
    )

if files_with_intermediate_store_terms:
    warnings.append(
        "Active WUC source contains intermediate-store terminology. "
        "These references require manual classification before handoff."
    )

if files_with_write_operations:
    warnings.append(
        "Active WUC source contains write operations. "
        "Their destinations must be classified as evidence, UUCD output, "
        "or prohibited intermediate content storage."
    )

if potential_intermediate_directories:
    failures.append(
        "Potential active WUC intermediate content directories detected: "
        + str(
            len(
                potential_intermediate_directories
            )
        )
    )


report = {
    "schema_version":
        "website_unified_content_handoff_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "authoritative_population_report":
        relative(
            population_report_path
        ),

    "authoritative_run_id":
        population_report.get(
            "run_id"
        ),

    "authoritative_certificate_id":
        population_report.get(
            "certificate_id"
        ),

    "pass_manifest_path":
        relative(
            pass_manifest_path
        ),

    "expected_pass_count":
        EXPECTED_PASS_COUNT,

    "actual_pass_count":
        len(
            pass_records
        ),

    "unique_source_record_count":
        len(
            set(
                record_ids
            )
        ),

    "resolved_udare_article_count":
        len(
            resolved_article_paths
        ),

    "unique_resolved_udare_article_count":
        len(
            set(
                resolved_article_paths
            )
        ),

    "reference_field_counts":
        dict(
            reference_field_counts
        ),

    "hash_field_counts":
        dict(
            hash_field_counts
        ),

    "missing_reference_records":
        missing_reference_records,

    "missing_article_files":
        missing_article_files,

    "references_outside_udare":
        references_outside_udare,

    "hash_mismatches":
        hash_mismatches,

    "body_field_findings":
        body_field_findings,

    "duplicate_record_ids":
        duplicate_record_ids,

    "duplicate_article_paths":
        duplicate_article_paths,

    "active_wuc_file_count":
        len(
            wuc_files
        ),

    "active_wuc_files":
        wuc_inspections,

    "handoff_aware_wuc_files":
        handoff_aware_files,

    "wuc_syntax_failure_files":
        wuc_syntax_failures,

    "files_with_intermediate_store_terms":
        files_with_intermediate_store_terms,

    "files_with_write_operations":
        files_with_write_operations,

    "wuc_named_data_directories":
        suspicious_wuc_directories,

    "potential_intermediate_wuc_directories":
        potential_intermediate_directories,

    "article_validation_evidence_modified":
        False,

    "udare_store_modified":
        False,

    "wuc_source_modified":
        False,

    "runtime_state_modified":
        False,

    "jobs_enqueued":
        False,

    "workers_started":
        False,

    "wuc_executed":
        False,

    "warnings":
        warnings,

    "failures":
        failures,

    "scan_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),
}


write_json(
    OUTPUT_REPORT_PATH,
    report,
)


print()
print(
    "Authoritative run ID:                  "
    + str(
        report[
            "authoritative_run_id"
        ]
    )
)

print(
    "Authoritative certificate ID:          "
    + str(
        report[
            "authoritative_certificate_id"
        ]
    )
)

print(
    "Article Validation PASS records:       "
    + str(
        report[
            "actual_pass_count"
        ]
    )
)

print(
    "Unique source record IDs:              "
    + str(
        report[
            "unique_source_record_count"
        ]
    )
)

print(
    "Resolved UDARE article references:     "
    + str(
        report[
            "resolved_udare_article_count"
        ]
    )
)

print(
    "Unique UDARE article references:       "
    + str(
        report[
            "unique_resolved_udare_article_count"
        ]
    )
)

print(
    "Missing article references:            "
    + str(
        len(
            missing_reference_records
        )
    )
)

print(
    "Missing UDARE article files:           "
    + str(
        len(
            missing_article_files
        )
    )
)

print(
    "References outside UDARE Store:        "
    + str(
        len(
            references_outside_udare
        )
    )
)

print(
    "UDARE article hash mismatches:         "
    + str(
        len(
            hash_mismatches
        )
    )
)

print(
    "PASS records containing body fields:   "
    + str(
        len(
            body_field_findings
        )
    )
)

print(
    "Active WUC-related Python files:       "
    + str(
        len(
            wuc_files
        )
    )
)

print(
    "WUC handoff-aware files:               "
    + str(
        len(
            handoff_aware_files
        )
    )
)

print(
    "WUC files with Store terminology:      "
    + str(
        len(
            files_with_intermediate_store_terms
        )
    )
)

print(
    "WUC files with write operations:       "
    + str(
        len(
            files_with_write_operations
        )
    )
)

print(
    "Potential intermediate WUC directories:"
    + " "
    + str(
        len(
            potential_intermediate_directories
        )
    )
)

print()
print(
    "ACTIVE WUC FILES"
)

if wuc_inspections:
    for inspection in wuc_inspections:
        print(
            "  "
            + inspection[
                "path"
            ]
        )

        print(
            "    Classification: "
            + inspection[
                "classification"
            ]
        )

        print(
            "    Handoff references: "
            + str(
                len(
                    inspection[
                        "handoff_lines"
                    ]
                )
            )
        )

        print(
            "    Write operations: "
            + str(
                len(
                    inspection[
                        "write_operations"
                    ]
                )
            )
        )

        print(
            "    Store-term references: "
            + str(
                len(
                    inspection[
                        "intermediate_store_lines"
                    ]
                )
            )
        )

else:
    print(
        "  None detected."
    )

print()
print(
    "WARNINGS"
)

if warnings:
    for warning in warnings:
        print(
            "  - "
            + warning
        )

else:
    print(
        "  None"
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
print(
    "Article Validation evidence modified: False"
)

print(
    "UDARE Store modified:                 False"
)

print(
    "WUC source modified:                  False"
)

print(
    "Runtime state modified:               False"
)

print(
    "WUC executed:                         False"
)

print()
print(
    "Handoff scan report: "
    + str(
        OUTPUT_REPORT_PATH
    )
)

print()

if failures:
    print(
        "WEBSITE UNIFIED CONTENT HANDOFF SCAN: FAIL"
    )

    print(
        "The scan found conditions that must be resolved "
        "before WUC handoff implementation."
    )

    print("=" * 108)

    raise SystemExit(1)

print(
    "WEBSITE UNIFIED CONTENT HANDOFF SCAN: PASS"
)

print(
    "The Article Validation PASS manifest and original "
    "UDARE references are structurally ready for WUC review."
)

print(
    "No files or runtime state were modified."
)

print("=" * 108)
