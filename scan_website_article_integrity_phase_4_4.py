from __future__ import annotations

import ast
import hashlib
import inspect
import json
import py_compile
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# CONFIGURATION
# ============================================================

WORKSPACE_ID = "ws_whattoexpect_com"

ROOT = Path("backend/server")
DATA_ROOT = ROOT / "data"

VALIDATOR_PATH = (
    ROOT
    / "stores"
    / "website_article_integrity_validator.py"
)

CHECKER_PATH = (
    ROOT
    / "stores"
    / "website_article_integrity_checker.py"
)

UDARE_STORE_MODULE_PATH = (
    ROOT
    / "stores"
    / "udare_store.py"
)

UDARE_WORKER_PATH = (
    ROOT
    / "workers"
    / "udare_reconstruction_worker.py"
)

UNIVERSAL_WORKER_PATH = (
    ROOT
    / "workers"
    / "universal_knowledge_worker.py"
)

QUEUE_RUNNER_PATH = (
    ROOT
    / "workers"
    / "universal_knowledge_queue_runner.py"
)

SOURCE_ORCHESTRATOR_PATH = (
    ROOT
    / "stores"
    / "website_source_pipeline_orchestrator.py"
)

WUC_WORKER_PATH = (
    ROOT
    / "workers"
    / "website_unified_content_batch_worker.py"
)

UDARE_ROOT = (
    DATA_ROOT
    / "udare_store"
    / WORKSPACE_ID
)

UDARE_ARTICLES = UDARE_ROOT / "articles"
UDARE_METADATA = UDARE_ROOT / "metadata"
UDARE_REVIEWS = UDARE_ROOT / "reviews"
UDARE_MANIFEST = UDARE_ROOT / "manifest.json"
UDARE_INDEX = UDARE_ROOT / "index.html"

REPORT_ROOT = (
    DATA_ROOT
    / "runtime"
    / "website_article_integrity_phase_4_4_scan"
)

JSON_REPORT = (
    REPORT_ROOT
    / "website_article_integrity_phase_4_4_scan.json"
)

TEXT_REPORT = (
    REPORT_ROOT
    / "website_article_integrity_phase_4_4_scan.txt"
)


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )


def read_json(path: Path) -> Any:
    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception as exc:
        return {
            "_read_error":
                f"{type(exc).__name__}: {exc}"
        }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def atomic_write_json(
    path: Path,
    value: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    temp.replace(path)


def atomic_write_text(
    path: Path,
    value: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp = path.with_suffix(
        path.suffix + ".tmp"
    )

    temp.write_text(
        value,
        encoding="utf-8",
    )

    temp.replace(path)


def parse_python_file(
    path: Path,
) -> dict[str, Any]:
    source = read_text(path)

    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes":
            path.stat().st_size
            if path.exists()
            else 0,
        "syntax_ok": False,
        "syntax_error": None,
        "functions": [],
        "classes": [],
        "imports": [],
        "constants": {},
    }

    if not source:
        return result

    try:
        tree = ast.parse(source)
        result["syntax_ok"] = True

    except SyntaxError as exc:
        result["syntax_error"] = (
            f"{exc.msg} at line "
            f"{exc.lineno}, column {exc.offset}"
        )
        return result

    functions = []
    classes = []
    imports = []
    constants = {}

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            positional = [
                argument.arg
                for argument
                in node.args.args
            ]

            keyword_only = [
                argument.arg
                for argument
                in node.args.kwonlyargs
            ]

            functions.append({
                "name": node.name,
                "line": node.lineno,
                "end_line":
                    getattr(
                        node,
                        "end_lineno",
                        node.lineno,
                    ),
                "arguments":
                    positional + keyword_only,
            })

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "end_line":
                    getattr(
                        node,
                        "end_lineno",
                        node.lineno,
                    ),
            })

        elif isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = str(
                node.module or ""
            )

            imports.extend(
                (
                    module
                    + "."
                    + alias.name
                ).strip(".")
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.Assign,
        ):
            if len(node.targets) != 1:
                continue

            target = node.targets[0]

            if not isinstance(
                target,
                ast.Name,
            ):
                continue

            if not target.id.isupper():
                continue

            try:
                constants[target.id] = (
                    ast.literal_eval(
                        node.value
                    )
                )
            except Exception:
                pass

    result["functions"] = sorted(
        functions,
        key=lambda item:
            item["line"],
    )

    result["classes"] = sorted(
        classes,
        key=lambda item:
            item["line"],
    )

    result["imports"] = sorted(
        set(imports)
    )

    result["constants"] = constants

    return result


def occurrence_report(
    source: str,
    terms: list[str],
) -> dict[str, Any]:
    lines = source.splitlines()
    output = {}

    for term in terms:
        matches = []

        pattern = re.compile(
            re.escape(term),
            flags=re.IGNORECASE,
        )

        for number, line in enumerate(
            lines,
            start=1,
        ):
            if pattern.search(line):
                matches.append({
                    "line": number,
                    "text": line.strip(),
                })

        output[term] = {
            "count": len(matches),
            "matches": matches[:30],
        }

    return output


def has_any(
    source: str,
    terms: list[str],
) -> bool:
    folded = source.casefold()

    return any(
        term.casefold() in folded
        for term in terms
    )


def function_names(
    parsed: dict[str, Any],
) -> list[str]:
    return [
        item["name"]
        for item in parsed.get(
            "functions",
            [],
        )
    ]


def manifest_count(
    manifest: Any,
) -> int | None:
    if not isinstance(
        manifest,
        dict,
    ):
        return None

    for field in (
        "record_count",
        "metadata_record_count",
        "article_document_count",
        "total_records",
        "count",
    ):
        value = manifest.get(field)

        if isinstance(value, int):
            return value

    records = manifest.get("records")

    if isinstance(records, list):
        return len(records)

    if isinstance(records, dict):
        return len(records)

    return None


# ============================================================
# SOURCE DISCOVERY
# ============================================================

preferred_paths = [
    VALIDATOR_PATH,
    CHECKER_PATH,
    UDARE_STORE_MODULE_PATH,
    UDARE_WORKER_PATH,
    UNIVERSAL_WORKER_PATH,
    QUEUE_RUNNER_PATH,
    SOURCE_ORCHESTRATOR_PATH,
    WUC_WORKER_PATH,
]

search_roots = [
    ROOT / "stores",
    ROOT / "workers",
    ROOT / "runtime",
    ROOT / "jobs",
    ROOT / "orchestration",
    ROOT / "routes",
    ROOT / "services",
]

search_terms = [
    "website_article_integrity",
    "article_integrity",
    "integrity_validator",
    "integrity_checker",
    "udare_store",
    "integrity_report",
    "integrity_result",
    "quarantine",
]

discovered: dict[str, Path] = {}

for path in preferred_paths:
    if path.exists():
        discovered[str(path)] = path

for directory in search_roots:
    if not directory.exists():
        continue

    for path in directory.rglob("*.py"):
        source = read_text(path)

        combined = (
            str(path)
            + "\n"
            + source
        ).casefold()

        if any(
            term.casefold() in combined
            for term in search_terms
        ):
            discovered[str(path)] = path

source_files = sorted(
    discovered.values(),
    key=lambda value:
        str(value),
)


# ============================================================
# PARSE SOURCE FILES
# ============================================================

source_reports = []

marker_terms = [
    "website_article_integrity",
    "build_website_article_integrity_result_v1",
    "check_website_article_integrity_v1",
    "udare_store",
    "articles/",
    "metadata/",
    "manifest.json",
    "raw_website_html",
    "reconstruct_universal_dom_article_v1",
    "content_blocks",
    "article_body",
    "raw_article_text",
    "raw_main_html",
    "title",
    "headings",
    "canonical_url",
    "word_count",
    "minimum_article_words",
    "article_block_structure",
    "printable_text",
    "html_leakage",
    "duplicate_block",
    "corruption",
    "truncation",
    "hash",
    "sha256",
    "report",
    "results",
    "failures",
    "quarantine",
    "certification",
    "queue",
    "job_type",
    "worker",
    "retry",
    "dead_letter",
    "progress",
    "Clean HTML",
    "Universal Content Body Formatter",
]

for path in source_files:
    parsed = parse_python_file(
        path
    )

    source = read_text(
        path
    )

    parsed["markers"] = (
        occurrence_report(
            source,
            marker_terms,
        )
    )

    source_reports.append(
        parsed
    )


# ============================================================
# FOCUSED VALIDATOR ANALYSIS
# ============================================================

validator_source = read_text(
    VALIDATOR_PATH
)

validator_parsed = parse_python_file(
    VALIDATOR_PATH
)

validator_functions = function_names(
    validator_parsed
)

validator_entry_candidates = [
    name
    for name in validator_functions
    if (
        "integrity" in name.casefold()
        or "validate" in name.casefold()
        or "check" in name.casefold()
    )
]

validator_has_udare_store_reference = (
    has_any(
        validator_source,
        [
            "udare_store",
            "load_udare",
            "read_udare",
            "get_udare",
            "articles/",
            "metadata/",
        ],
    )
)

validator_has_raw_html_reference = (
    has_any(
        validator_source,
        [
            "raw_website_html",
            "raw_main_html",
            "raw_html",
        ],
    )
)

validator_has_reconstruction_reference = (
    has_any(
        validator_source,
        [
            "reconstruct_universal_dom_article",
            "universal_dom_article_reconstruction",
        ],
    )
)

validator_accepts_content_blocks = (
    "content_blocks"
    in validator_source
)

validator_accepts_article_document = (
    has_any(
        validator_source,
        [
            "article_document",
            "article_path",
            "html_document",
            "reader_document",
        ],
    )
)

validator_checks = {
    "content_present":
        has_any(
            validator_source,
            [
                "content_present",
                "empty_article_body",
            ],
        ),

    "minimum_article_length":
        has_any(
            validator_source,
            [
                "minimum_article_words",
                "word_count",
                "below_150_words",
            ],
        ),

    "article_block_structure":
        has_any(
            validator_source,
            [
                "article_block_structure",
                "block_count",
                "paragraph_count",
            ],
        ),

    "word_sequence_preservation":
        has_any(
            validator_source,
            [
                "word_sequence_preserved",
                "word_sequence_changed",
            ],
        ),

    "printable_text":
        has_any(
            validator_source,
            [
                "printable_text",
                "printable_ratio",
                "invalid_text_encoding",
            ],
        ),

    "html_leakage":
        has_any(
            validator_source,
            [
                "html_leakage",
                "html_leakage_detected",
            ],
        ),

    "duplicate_blocks":
        has_any(
            validator_source,
            [
                "duplicate_block_ratio",
                "duplicate_blocks_detected",
                "structured_duplicate",
            ],
        ),

    "required_title":
        has_any(
            validator_source,
            [
                "title_present",
                "missing_title",
                "required_title",
            ],
        ),

    "required_canonical_url":
        has_any(
            validator_source,
            [
                "canonical_url_present",
                "missing_canonical_url",
                "required_canonical_url",
            ],
        ),

    "required_document_structure":
        has_any(
            validator_source,
            [
                "<!doctype html",
                "<html",
                "<head",
                "<body",
                "reader_document",
                "article_document_format",
            ],
        ),

    "explicit_corruption_detection":
        has_any(
            validator_source,
            [
                "corrupt",
                "corruption",
                "malformed",
                "invalid_document",
                "broken_document",
            ],
        ),

    "explicit_truncation_detection":
        has_any(
            validator_source,
            [
                "truncat",
                "abrupt_end",
                "incomplete_ending",
                "premature_end",
                "cut_off",
            ],
        ),

    "stored_hash_verification":
        has_any(
            validator_source,
            [
                "expected_document_sha256",
                "article_document_sha256",
                "sha256",
                "hash_mismatch",
            ],
        ),

    "non_mutating_contract":
        has_any(
            validator_source,
            [
                "non_mutating",
                "content_modified",
                "word_sequence_preserved",
                "removed_word_count",
            ],
        ),
}

validator_output_support = {
    "returns_status":
        has_any(
            validator_source,
            [
                '"status"',
                "'status'",
                "validation_failed",
                "validated",
            ],
        ),

    "returns_pass_boolean":
        has_any(
            validator_source,
            [
                '"passed"',
                "'passed'",
                '"ok"',
                "'ok'",
            ],
        ),

    "returns_checks":
        has_any(
            validator_source,
            [
                '"checks"',
                "'checks'",
            ],
        ),

    "returns_warnings":
        has_any(
            validator_source,
            [
                '"warnings"',
                "'warnings'",
            ],
        ),

    "returns_errors":
        has_any(
            validator_source,
            [
                '"errors"',
                "'errors'",
            ],
        ),

    "returns_statistics":
        has_any(
            validator_source,
            [
                '"statistics"',
                "'statistics'",
            ],
        ),

    "persists_report_itself":
        has_any(
            validator_source,
            [
                "write_json(",
                "atomic_write_json",
                "json.dump",
                "json.dumps",
                "report_path",
                "results_path",
            ],
        ),

    "persists_quarantine_itself":
        has_any(
            validator_source,
            [
                "quarantine_path",
                "quarantine_store",
                "persist_quarantine",
                "write_quarantine",
                "move_to_quarantine",
            ],
        ),
}

stale_flow_markers = {
    "mentions_clean_html":
        "clean html"
        in validator_source.casefold(),

    "mentions_universal_content_body_formatter":
        (
            "universal content body formatter"
            in validator_source.casefold()
        ),

    "mentions_direct_wuc_flow":
        (
            "website unified content"
            in validator_source.casefold()
        ),
}


# ============================================================
# UDARE STORE ANALYSIS
# ============================================================

udare_store_source = read_text(
    UDARE_STORE_MODULE_PATH
)

udare_store_parsed = parse_python_file(
    UDARE_STORE_MODULE_PATH
)

udare_store_functions = function_names(
    udare_store_parsed
)

udare_reader_candidates = [
    name
    for name in udare_store_functions
    if (
        any(
            token in name.casefold()
            for token in (
                "load",
                "read",
                "get",
                "list",
                "verify",
            )
        )
        and "udare" in name.casefold()
    )
]

udare_store_capabilities = {
    "module_exists":
        UDARE_STORE_MODULE_PATH.exists(),

    "syntax_ok":
        udare_store_parsed.get(
            "syntax_ok",
            False,
        ),

    "persists_html_documents":
        has_any(
            udare_store_source,
            [
                "persist_udare_article_document",
                "article_document_format",
                "articles",
            ],
        ),

    "stores_metadata_json":
        has_any(
            udare_store_source,
            [
                "metadata",
                "metadata_path",
                "record_schema_version",
            ],
        ),

    "verifies_store":
        has_any(
            udare_store_source,
            [
                "verify_udare_store",
            ],
        ),

    "verifies_sha256":
        has_any(
            udare_store_source,
            [
                "_sha256_bytes",
                "expected_document_sha256",
                "article_document_sha256",
            ],
        ),

    "provides_reader_api":
        bool(
            udare_reader_candidates
        ),

    "reader_candidates":
        udare_reader_candidates,
}


# ============================================================
# LIVE UDARE STORE POPULATION
# ============================================================

article_files = (
    sorted(
        UDARE_ARTICLES.glob(
            "*.html"
        )
    )
    if UDARE_ARTICLES.exists()
    else []
)

metadata_files = (
    sorted(
        UDARE_METADATA.glob(
            "*.json"
        )
    )
    if UDARE_METADATA.exists()
    else []
)

review_files = (
    sorted(
        UDARE_REVIEWS.glob(
            "*.html"
        )
    )
    if UDARE_REVIEWS.exists()
    else []
)

manifest = read_json(
    UDARE_MANIFEST
)

sample_articles = []

for path in article_files[:5]:
    content = path.read_bytes()

    text = content.decode(
        "utf-8-sig",
        errors="replace",
    )

    sample_articles.append({
        "path": str(path),
        "size_bytes": len(content),
        "sha256": sha256_bytes(content),
        "has_doctype":
            "<!doctype html"
            in text.casefold(),
        "has_html":
            "<html"
            in text.casefold(),
        "has_head":
            "<head"
            in text.casefold(),
        "has_body":
            "<body"
            in text.casefold(),
        "has_article":
            "<article"
            in text.casefold(),
    })

udare_population = {
    "root_exists":
        UDARE_ROOT.exists(),

    "articles_directory_exists":
        UDARE_ARTICLES.exists(),

    "metadata_directory_exists":
        UDARE_METADATA.exists(),

    "reviews_directory_exists":
        UDARE_REVIEWS.exists(),

    "manifest_exists":
        UDARE_MANIFEST.exists(),

    "index_exists":
        UDARE_INDEX.exists(),

    "article_document_count":
        len(article_files),

    "metadata_record_count":
        len(metadata_files),

    "review_document_count":
        len(review_files),

    "manifest_reported_count":
        manifest_count(
            manifest
        ),

    "article_metadata_count_match":
        (
            len(article_files)
            == len(metadata_files)
        ),

    "sample_articles":
        sample_articles,
}


# ============================================================
# RUNTIME, QUEUE, WORKER AND ORCHESTRATION ANALYSIS
# ============================================================

runtime_terms = [
    "website_article_integrity",
    "article_integrity",
    "integrity_validation",
]

runtime_files = [
    UNIVERSAL_WORKER_PATH,
    QUEUE_RUNNER_PATH,
    SOURCE_ORCHESTRATOR_PATH,
    WUC_WORKER_PATH,
]

runtime_scan = {}

for path in runtime_files:
    source = read_text(
        path
    )

    runtime_scan[str(path)] = {
        "exists": path.exists(),

        "mentions_integrity":
            has_any(
                source,
                runtime_terms,
            ),

        "mentions_udare_store":
            has_any(
                source,
                [
                    "udare_store",
                    "article_path",
                    "metadata_path",
                ],
            ),

        "mentions_integrity_job_type":
            has_any(
                source,
                [
                    "website_article_integrity",
                    "article_integrity_validation",
                ],
            ),

        "mentions_retry":
            "retry"
            in source.casefold(),

        "mentions_dead_letter":
            (
                "dead_letter"
                in source.casefold()
                or "dead letter"
                in source.casefold()
            ),

        "mentions_progress":
            "progress"
            in source.casefold(),
    }

dedicated_integrity_worker_files = [
    str(path)
    for path in source_files
    if (
        "worker"
        in path.name.casefold()
        and (
            "integrity"
            in path.name.casefold()
            or has_any(
                read_text(path),
                [
                    "website_article_integrity",
                    "article_integrity_validation",
                ],
            )
        )
    )
]

dedicated_integrity_job_signals = []

for report in source_reports:
    path = report["path"]
    source = read_text(
        Path(path)
    )

    if not has_any(
        source,
        runtime_terms,
    ):
        continue

    if has_any(
        source,
        [
            "job_type",
            "create_universal_knowledge_job",
            "create_pipeline_batch_jobs",
            "enqueue",
        ],
    ):
        dedicated_integrity_job_signals.append(
            path
        )


# ============================================================
# REPORT, QUARANTINE AND CERTIFICATION ARTIFACT DISCOVERY
# ============================================================

artifact_terms = [
    "website_article_integrity",
    "article_integrity",
]

runtime_artifacts = []

if DATA_ROOT.exists():
    for path in DATA_ROOT.rglob("*"):
        if not path.is_file():
            continue

        folded = str(path).casefold()

        if any(
            term in folded
            for term in artifact_terms
        ):
            runtime_artifacts.append({
                "path": str(path),
                "size_bytes":
                    path.stat().st_size,
                "modified_at_utc":
                    datetime.fromtimestamp(
                        path.stat().st_mtime,
                        tz=timezone.utc,
                    ).isoformat(),
            })

runtime_artifacts = sorted(
    runtime_artifacts,
    key=lambda item:
        item["path"],
)

report_artifacts = [
    item
    for item in runtime_artifacts
    if any(
        token in item["path"].casefold()
        for token in (
            "report",
            "result",
            "certification",
            "failure",
        )
    )
]

quarantine_artifacts = [
    item
    for item in runtime_artifacts
    if "quarantine"
    in item["path"].casefold()
]

certification_artifacts = [
    item
    for item in runtime_artifacts
    if "certif"
    in item["path"].casefold()
]


# ============================================================
# CHECKLIST ASSESSMENT
# ============================================================

checklist = {
    "4.4.1_validate_reconstructed_article_structure": {
        "status":
            "PARTIAL"
            if (
                validator_checks[
                    "article_block_structure"
                ]
            )
            else "FAIL",

        "evidence": {
            "article_block_structure":
                validator_checks[
                    "article_block_structure"
                ],

            "required_document_structure":
                validator_checks[
                    "required_document_structure"
                ],

            "accepts_udare_article_document":
                validator_accepts_article_document,
        },

        "reason": (
            "The existing validator checks text/block structure, "
            "but must be confirmed against the persisted UDARE HTML "
            "reader-document structure."
        ),
    },

    "4.4.2_validate_required_article_components": {
        "status":
            "PARTIAL"
            if (
                validator_checks[
                    "content_present"
                ]
            )
            else "FAIL",

        "evidence": {
            "body_required":
                validator_checks[
                    "content_present"
                ],

            "title_required":
                validator_checks[
                    "required_title"
                ],

            "canonical_url_required":
                validator_checks[
                    "required_canonical_url"
                ],

            "headings_or_blocks_checked":
                validator_checks[
                    "article_block_structure"
                ],
        },

        "reason": (
            "The body is checked, but explicit required-component "
            "validation for the complete UDARE Store document must "
            "be confirmed."
        ),
    },

    "4.4.3_detect_corruption_and_truncation": {
        "status":
            (
                "PASS"
                if (
                    validator_checks[
                        "explicit_corruption_detection"
                    ]
                    and validator_checks[
                        "explicit_truncation_detection"
                    ]
                    and validator_checks[
                        "stored_hash_verification"
                    ]
                )
                else "PARTIAL"
            ),

        "evidence": {
            "printable_text":
                validator_checks[
                    "printable_text"
                ],

            "html_leakage":
                validator_checks[
                    "html_leakage"
                ],

            "word_sequence_preservation":
                validator_checks[
                    "word_sequence_preservation"
                ],

            "stored_hash_verification":
                validator_checks[
                    "stored_hash_verification"
                ],

            "explicit_corruption_detection":
                validator_checks[
                    "explicit_corruption_detection"
                ],

            "explicit_truncation_detection":
                validator_checks[
                    "explicit_truncation_detection"
                ],
        },

        "reason": (
            "The existing validator detects several integrity "
            "problems, but explicit persisted-document corruption "
            "and truncation rules may be absent."
        ),
    },

    "4.4.4_generate_website_integrity_report": {
        "status":
            (
                "PASS"
                if report_artifacts
                else "PARTIAL"
                if validator_output_support[
                    "returns_checks"
                ]
                else "FAIL"
            ),

        "evidence": {
            "validator_returns_structured_result":
                (
                    validator_output_support[
                        "returns_checks"
                    ]
                    and validator_output_support[
                        "returns_statistics"
                    ]
                ),

            "validator_persists_report":
                validator_output_support[
                    "persists_report_itself"
                ],

            "existing_report_artifact_count":
                len(report_artifacts),
        },

        "reason": (
            "Historical reports may exist, but the production "
            "UDARE Store-to-Integrity report writer must be verified."
        ),
    },

    "4.4.5_quarantine_failed_articles": {
        "status":
            (
                "PASS"
                if (
                    validator_output_support[
                        "persists_quarantine_itself"
                    ]
                    or quarantine_artifacts
                )
                else "FAIL"
            ),

        "evidence": {
            "validator_persists_quarantine":
                validator_output_support[
                    "persists_quarantine_itself"
                ],

            "quarantine_artifact_count":
                len(quarantine_artifacts),
        },

        "reason": (
            "Returning validation_failed is not sufficient. "
            "A durable quarantine record/path and downstream block "
            "must exist."
        ),
    },

    "4.4.6_certify_website_article_integrity": {
        "status":
            (
                "PARTIAL"
                if certification_artifacts
                else "FAIL"
            ),

        "evidence": {
            "existing_certification_artifact_count":
                len(certification_artifacts),

            "dedicated_integrity_worker_count":
                len(
                    dedicated_integrity_worker_files
                ),

            "dedicated_job_signal_count":
                len(
                    dedicated_integrity_job_signals
                ),

            "reads_current_udare_store":
                validator_has_udare_store_reference,
        },

        "reason": (
            "Historical certification does not prove the new "
            "UDARE Store-based production stage is certified."
        ),
    },
}


# ============================================================
# ARCHITECTURAL BLOCKERS
# ============================================================

blockers = []

if not VALIDATOR_PATH.exists():
    blockers.append(
        "Website Article Integrity validator file is missing."
    )

if not validator_parsed.get(
    "syntax_ok",
    False,
):
    blockers.append(
        "Website Article Integrity validator has invalid Python syntax."
    )

if not validator_has_udare_store_reference:
    blockers.append(
        "The existing validator is not visibly connected to the UDARE Store."
    )

if validator_has_raw_html_reference:
    blockers.append(
        "The existing validator still exposes Raw HTML-oriented inputs or references."
    )

if validator_has_reconstruction_reference:
    blockers.append(
        "The integrity stage contains or references reconstruction logic."
    )

if not validator_accepts_article_document:
    blockers.append(
        "The validator does not visibly accept the persisted UDARE article document."
    )

if not validator_checks[
    "explicit_truncation_detection"
]:
    blockers.append(
        "No explicit truncation-detection rule was found."
    )

if not validator_checks[
    "stored_hash_verification"
]:
    blockers.append(
        "No explicit UDARE Store document-hash verification was found in the validator."
    )

if not (
    validator_output_support[
        "persists_quarantine_itself"
    ]
    or quarantine_artifacts
):
    blockers.append(
        "No durable Website Article Integrity quarantine implementation was found."
    )

if not dedicated_integrity_worker_files:
    blockers.append(
        "No dedicated Website Article Integrity worker was found."
    )

if not dedicated_integrity_job_signals:
    blockers.append(
        "No clear Website Article Integrity job creation or queue contract was found."
    )

if stale_flow_markers[
    "mentions_clean_html"
]:
    blockers.append(
        "The validator still contains the retired Clean HTML stage in its documented flow."
    )

if stale_flow_markers[
    "mentions_universal_content_body_formatter"
]:
    blockers.append(
        "The validator still contains the obsolete Universal Content Body Formatter flow."
    )


# ============================================================
# BUILD FINAL REPORT
# ============================================================

report = {
    "scan": {
        "name":
            "Website Article Integrity Phase 4.4 Existing Architecture Scan",

        "workspace_id":
            WORKSPACE_ID,

        "generated_at_utc":
            utc_now(),

        "operation":
            "READ_ONLY_SOURCE_AND_DATA_INSPECTION",

        "source_modified":
            False,

        "udare_store_modified":
            False,

        "raw_html_modified":
            False,

        "wuc_modified":
            False,

        "uucd_modified":
            False,

        "body_store_modified":
            False,

        "queues_modified":
            False,

        "jobs_created":
            0,

        "workers_executed":
            0,
    },

    "validator": {
        "path":
            str(
                VALIDATOR_PATH
            ),

        "exists":
            VALIDATOR_PATH.exists(),

        "syntax_ok":
            validator_parsed.get(
                "syntax_ok",
                False,
            ),

        "syntax_error":
            validator_parsed.get(
                "syntax_error"
            ),

        "constants":
            validator_parsed.get(
                "constants",
                {}
            ),

        "function_count":
            len(
                validator_functions
            ),

        "functions":
            validator_functions,

        "entry_candidates":
            validator_entry_candidates,

        "has_udare_store_reference":
            validator_has_udare_store_reference,

        "has_raw_html_reference":
            validator_has_raw_html_reference,

        "has_reconstruction_reference":
            validator_has_reconstruction_reference,

        "accepts_content_blocks":
            validator_accepts_content_blocks,

        "accepts_persisted_article_document":
            validator_accepts_article_document,

        "checks":
            validator_checks,

        "output_support":
            validator_output_support,

        "stale_flow_markers":
            stale_flow_markers,
    },

    "udare_store_module": {
        "path":
            str(
                UDARE_STORE_MODULE_PATH
            ),

        "function_count":
            len(
                udare_store_functions
            ),

        "functions":
            udare_store_functions,

        "capabilities":
            udare_store_capabilities,
    },

    "udare_population":
        udare_population,

    "runtime": {
        "file_scan":
            runtime_scan,

        "dedicated_integrity_worker_files":
            dedicated_integrity_worker_files,

        "dedicated_integrity_job_signals":
            sorted(
                set(
                    dedicated_integrity_job_signals
                )
            ),
    },

    "artifacts": {
        "total_integrity_related":
            len(
                runtime_artifacts
            ),

        "report_artifacts":
            report_artifacts,

        "quarantine_artifacts":
            quarantine_artifacts,

        "certification_artifacts":
            certification_artifacts,
    },

    "phase_4_4_checklist":
        checklist,

    "blocking_findings":
        blockers,

    "source_files":
        source_reports,

    "decision": (
        "EXISTING_IMPLEMENTATION_REQUIRES_REPAIR"
        if blockers
        else "EXISTING_IMPLEMENTATION_READY_FOR_CONTROLLED_VERIFICATION"
    ),
}

atomic_write_json(
    JSON_REPORT,
    report,
)


# ============================================================
# TEXT REPORT
# ============================================================

lines = []

lines.append(
    "=" * 116
)

lines.append(
    "PHASE 4.4 — WEBSITE ARTICLE INTEGRITY EXISTING ARCHITECTURE SCAN"
)

lines.append(
    "=" * 116
)

lines.append(
    f"Workspace: {WORKSPACE_ID}"
)

lines.append(
    "Operation: READ ONLY"
)

lines.append("")

lines.append(
    "UDARE STORE"
)

lines.append(
    "-" * 116
)

lines.append(
    f"Store root exists: {udare_population['root_exists']}"
)

lines.append(
    "Article documents: "
    f"{udare_population['article_document_count']}"
)

lines.append(
    "Metadata records: "
    f"{udare_population['metadata_record_count']}"
)

lines.append(
    "Article/metadata counts match: "
    f"{udare_population['article_metadata_count_match']}"
)

lines.append(
    f"Manifest exists: {udare_population['manifest_exists']}"
)

lines.append(
    f"Index exists: {udare_population['index_exists']}"
)

lines.append("")

lines.append(
    "EXISTING VALIDATOR"
)

lines.append(
    "-" * 116
)

lines.append(
    f"Path: {VALIDATOR_PATH}"
)

lines.append(
    f"Exists: {VALIDATOR_PATH.exists()}"
)

lines.append(
    "Syntax valid: "
    f"{validator_parsed.get('syntax_ok', False)}"
)

lines.append(
    "UDARE Store reference: "
    f"{validator_has_udare_store_reference}"
)

lines.append(
    "Raw HTML reference: "
    f"{validator_has_raw_html_reference}"
)

lines.append(
    "Reconstruction reference: "
    f"{validator_has_reconstruction_reference}"
)

lines.append(
    "Accepts content_blocks: "
    f"{validator_accepts_content_blocks}"
)

lines.append(
    "Accepts persisted UDARE article document: "
    f"{validator_accepts_article_document}"
)

lines.append("")

lines.append(
    "PHASE 4.4 CHECKLIST"
)

lines.append(
    "-" * 116
)

for item, assessment in checklist.items():
    lines.append(
        f"{item}: {assessment['status']}"
    )

lines.append("")

lines.append(
    "RUNTIME"
)

lines.append(
    "-" * 116
)

lines.append(
    "Dedicated integrity workers found: "
    f"{len(dedicated_integrity_worker_files)}"
)

lines.append(
    "Dedicated integrity job signals found: "
    f"{len(dedicated_integrity_job_signals)}"
)

lines.append(
    "Queues modified: False"
)

lines.append(
    "Jobs created: 0"
)

lines.append(
    "Workers executed: 0"
)

lines.append("")

lines.append(
    "BLOCKING FINDINGS"
)

lines.append(
    "-" * 116
)

if blockers:
    for number, blocker in enumerate(
        blockers,
        start=1,
    ):
        lines.append(
            f"{number}. {blocker}"
        )
else:
    lines.append(
        "No blocking finding detected by the static scan."
    )

lines.append("")

lines.append(
    "DECISION"
)

lines.append(
    "-" * 116
)

lines.append(
    report["decision"]
)

lines.append("")

lines.append(
    f"JSON report: {JSON_REPORT}"
)

lines.append(
    f"Text report: {TEXT_REPORT}"
)

lines.append("")

lines.append(
    "Source modified: False"
)

lines.append(
    "UDARE Store modified: False"
)

lines.append(
    "Raw HTML modified: False"
)

lines.append(
    "WUC modified: False"
)

lines.append(
    "UUCD modified: False"
)

lines.append(
    "Body Store modified: False"
)

lines.append(
    "Queues modified: False"
)

lines.append(
    "Jobs created: 0"
)

lines.append(
    "Workers executed: 0"
)

text_report = "\n".join(
    lines
)

atomic_write_text(
    TEXT_REPORT,
    text_report,
)


# ============================================================
# TERMINAL OUTPUT
# ============================================================

print()
print(
    text_report
)
print()

