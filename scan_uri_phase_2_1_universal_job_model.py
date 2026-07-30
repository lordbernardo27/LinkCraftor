from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

SERVER_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_2"
    / "2_1_universal_job_model"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

REPORT_JSON = (
    EVIDENCE_DIR
    / f"universal_job_full_scan_{TIMESTAMP}.json"
)

REPORT_TEXT = (
    EVIDENCE_DIR
    / f"universal_job_full_scan_{TIMESTAMP}.txt"
)


PHASE_ITEMS = {
    "2.1.1 Universal Job Contract": {
        "filename_terms": (
            "universal_job",
            "job_contract",
            "job_model",
            "job_record",
            "job_definition",
        ),
        "symbol_terms": (
            "UniversalJob",
            "UniversalJobContract",
            "JobContract",
            "JobRecord",
            "JobDefinition",
            "JobStatus",
        ),
    },
    "2.1.2 Job Creation Engine": {
        "filename_terms": (
            "job_creation",
            "job_creator",
            "create_job",
            "job_factory",
        ),
        "symbol_terms": (
            "JobCreationEngine",
            "UniversalJobCreator",
            "JobCreator",
            "JobFactory",
            "create_job",
        ),
    },
    "2.1.3 Job Metadata": {
        "filename_terms": (
            "job_metadata",
            "metadata",
        ),
        "symbol_terms": (
            "JobMetadata",
            "UniversalJobMetadata",
            "JobMetadataContract",
        ),
    },
    "2.1.4 Job Payload Management": {
        "filename_terms": (
            "job_payload",
            "payload_management",
            "payload_reference",
        ),
        "symbol_terms": (
            "JobPayload",
            "JobPayloadManager",
            "PayloadReference",
            "JobPayloadReference",
        ),
    },
    "2.1.5 Job Priorities": {
        "filename_terms": (
            "job_priority",
            "priorities",
            "priority",
        ),
        "symbol_terms": (
            "JobPriority",
            "PriorityLevel",
            "PriorityPolicy",
        ),
    },
    "2.1.6 Job Dependencies": {
        "filename_terms": (
            "job_dependency",
            "dependencies",
            "dependency_graph",
        ),
        "symbol_terms": (
            "JobDependency",
            "JobDependencyGraph",
            "DependencyResolver",
            "dependency_job_ids",
        ),
    },
    "2.1.7 Job Chaining": {
        "filename_terms": (
            "job_chain",
            "chaining",
            "job_graph",
        ),
        "symbol_terms": (
            "JobChain",
            "JobChaining",
            "JobChainManager",
            "parent_job_id",
        ),
    },
    "2.1.8 Job Leasing": {
        "filename_terms": (
            "job_lease",
            "leasing",
            "lease",
        ),
        "symbol_terms": (
            "JobLease",
            "JobLeaseManager",
            "LeaseContract",
            "lease_owner",
            "lease_id",
        ),
    },
    "2.1.9 Job State Machine": {
        "filename_terms": (
            "job_state",
            "state_machine",
            "job_lifecycle",
        ),
        "symbol_terms": (
            "JobStateMachine",
            "JobState",
            "JobStatus",
            "JobTransition",
        ),
    },
    "2.1.10 Job Idempotency": {
        "filename_terms": (
            "job_idempotency",
            "idempotency",
        ),
        "symbol_terms": (
            "JobIdempotency",
            "IdempotencyPolicy",
            "IdempotencyResult",
        ),
    },
    "2.1.11 Duplicate Job Detection": {
        "filename_terms": (
            "duplicate_job",
            "job_duplicate",
            "deduplication",
            "dedupe",
        ),
        "symbol_terms": (
            "DuplicateJobDetector",
            "JobDuplicateDetector",
            "JobDeduplicator",
            "DuplicateJob",
        ),
    },
    "2.1.12 Idempotency-Key Management": {
        "filename_terms": (
            "idempotency_key",
            "job_key",
        ),
        "symbol_terms": (
            "IdempotencyKey",
            "IdempotencyKeyManager",
            "JobIdempotencyKey",
        ),
    },
    "2.1.13 Job Result Contract": {
        "filename_terms": (
            "job_result",
            "result_contract",
        ),
        "symbol_terms": (
            "JobResult",
            "UniversalJobResult",
            "JobResultContract",
            "JobFailure",
        ),
    },
    "2.1.14 Job Artifact References": {
        "filename_terms": (
            "job_artifact",
            "artifact_reference",
            "artifacts",
        ),
        "symbol_terms": (
            "JobArtifact",
            "ArtifactReference",
            "JobArtifactReference",
        ),
    },
    "2.1.15 Universal Job Certification": {
        "filename_terms": (
            "job_certification",
            "universal_job_certification",
        ),
        "symbol_terms": (
            "UniversalJobCertification",
            "JobCertification",
            "UniversalJobCertificationReport",
        ),
    },
}


REQUIRED_JOB_FIELDS = (
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


PROHIBITED_TERMS = (
    "queue.Queue",
    "asyncio.Queue",
    "create_worker",
    "start_worker",
    "consume_queue",
    "queue_consumer",
    "dispatch_job",
    "background_task",
    "RuntimeRegistration",
    "register_runtime",
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def parse_python_file(
    path: Path,
) -> dict:
    try:
        relative_path = path.relative_to(
            PROJECT_ROOT
        ).as_posix()
    except ValueError:
        relative_path = str(path)

    result = {
        "relative_path": relative_path,
        "absolute_path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "compile": "NOT_RUN",
        "ast_parse": "NOT_RUN",
        "import": "NOT_RUN",
        "module_name": None,
        "classes": [],
        "functions": [],
        "constants": [],
        "all_exports": [],
        "field_hits": [],
        "prohibited_hits": [],
        "source_terms": [],
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

        return result

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )

        tree = ast.parse(
            source
        )

        result["ast_parse"] = "PASS"

    except Exception as exc:
        result["ast_parse"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        return result

    result["classes"] = sorted(
        node.name
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
    )

    result["functions"] = sorted(
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    )

    constants = []

    for node in tree.body:
        if isinstance(
            node,
            ast.Assign,
        ):
            for target in node.targets:
                if (
                    isinstance(
                        target,
                        ast.Name,
                    )
                    and target.id.isupper()
                ):
                    constants.append(
                        target.id
                    )

                if (
                    isinstance(
                        target,
                        ast.Name,
                    )
                    and target.id == "__all__"
                    and isinstance(
                        node.value,
                        (
                            ast.List,
                            ast.Tuple,
                        ),
                    )
                ):
                    result[
                        "all_exports"
                    ] = sorted(
                        element.value
                        for element
                        in node.value.elts
                        if isinstance(
                            element,
                            ast.Constant,
                        )
                        and isinstance(
                            element.value,
                            str,
                        )
                    )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if (
                isinstance(
                    node.target,
                    ast.Name,
                )
                and node.target.id.isupper()
            ):
                constants.append(
                    node.target.id
                )

    result["constants"] = sorted(
        constants
    )

    source_lower = source.lower()

    result["field_hits"] = [
        field
        for field in REQUIRED_JOB_FIELDS
        if field.lower()
        in source_lower
    ]

    result["prohibited_hits"] = [
        term
        for term in PROHIBITED_TERMS
        if term.lower()
        in source_lower
    ]

    return result


def module_name_for_path(
    path: Path,
) -> str | None:
    try:
        relative = path.relative_to(
            RUNTIME_DIR
        )
    except ValueError:
        return None

    if path.name == "__init__.py":
        parts = relative.parts[
            :-1
        ]
    else:
        parts = (
            *relative.parts[:-1],
            path.stem,
        )

    if not parts:
        return None

    return ".".join(
        parts
    )


def try_import(
    file_result: dict,
    path: Path,
) -> None:
    module_name = module_name_for_path(
        path
    )

    file_result[
        "module_name"
    ] = module_name

    if module_name is None:
        file_result[
            "import"
        ] = "NOT_APPLICABLE"

        return

    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    try:
        importlib.invalidate_caches()

        importlib.import_module(
            module_name
        )

        file_result[
            "import"
        ] = "PASS"

    except Exception as exc:
        file_result[
            "import"
        ] = "FAIL"

        if file_result[
            "error"
        ] is None:
            file_result[
                "error"
            ] = (
                f"{type(exc).__name__}: {exc}"
            )


def score_candidate(
    file_result: dict,
    rules: dict,
) -> dict:
    relative_lower = file_result[
        "relative_path"
    ].lower()

    filename_hits = [
        term
        for term in rules[
            "filename_terms"
        ]
        if term in relative_lower
    ]

    symbols = (
        file_result[
            "classes"
        ]
        + file_result[
            "functions"
        ]
        + file_result[
            "constants"
        ]
        + file_result[
            "all_exports"
        ]
    )

    symbol_hits = [
        symbol
        for symbol in symbols
        if any(
            term.lower()
            in symbol.lower()
            for term in rules[
                "symbol_terms"
            ]
        )
    ]

    field_score = len(
        file_result[
            "field_hits"
        ]
    )

    score = (
        len(
            filename_hits
        )
        * 20
        + len(
            symbol_hits
        )
        * 10
        + min(
            field_score,
            10,
        )
    )

    return {
        **file_result,
        "filename_hits": filename_hits,
        "symbol_hits": symbol_hits,
        "score": score,
    }


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 2.1 — UNIVERSAL JOB MODEL FULL DISCOVERY SCAN")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    search_roots = [
        path
        for path in (
            RUNTIME_DIR,
            SERVER_DIR / "jobs",
            SERVER_DIR / "job",
            SERVER_DIR / "runtime_jobs",
            SERVER_DIR / "infrastructure",
        )
        if path.exists()
    ]

    python_paths = sorted(
        {
            path.resolve()
            for root in search_roots
            for path in root.rglob(
                "*.py"
            )
            if "__pycache__"
            not in path.parts
        }
    )

    file_results = []

    for path in python_paths:
        result = parse_python_file(
            path
        )

        if (
            result[
                "compile"
            ]
            == "PASS"
        ):
            try_import(
                result,
                path,
            )

        file_results.append(
            result
        )

    phase_results = {}

    for phase_item, rules in PHASE_ITEMS.items():
        candidates = [
            score_candidate(
                file_result,
                rules,
            )
            for file_result
            in file_results
        ]

        candidates = sorted(
            (
                candidate
                for candidate in candidates
                if candidate[
                    "score"
                ] > 0
            ),
            key=lambda candidate: (
                -candidate[
                    "score"
                ],
                candidate[
                    "relative_path"
                ],
            ),
        )

        phase_results[
            phase_item
        ] = candidates[
            :15
        ]

    field_locations = {
        field: sorted(
            file_result[
                "relative_path"
            ]
            for file_result
            in file_results
            if field in file_result[
                "field_hits"
            ]
        )
        for field in REQUIRED_JOB_FIELDS
    }

    missing_fields = [
        field
        for field, locations
        in field_locations.items()
        if not locations
    ]

    prohibited_findings = [
        {
            "relative_path": (
                file_result[
                    "relative_path"
                ]
            ),
            "hits": file_result[
                "prohibited_hits"
            ],
        }
        for file_result
        in file_results
        if file_result[
            "prohibited_hits"
        ]
    ]

    likely_existing_items = []

    for phase_item, candidates in phase_results.items():
        if (
            candidates
            and candidates[
                0
            ][
                "score"
            ] >= 20
        ):
            likely_existing_items.append(
                phase_item
            )

    compile_failures = [
        {
            "relative_path": (
                file_result[
                    "relative_path"
                ]
            ),
            "error": file_result[
                "error"
            ],
        }
        for file_result
        in file_results
        if file_result[
            "compile"
        ] == "FAIL"
    ]

    import_failures = [
        {
            "relative_path": (
                file_result[
                    "relative_path"
                ]
            ),
            "module_name": (
                file_result[
                    "module_name"
                ]
            ),
            "error": file_result[
                "error"
            ],
        }
        for file_result
        in file_results
        if file_result[
            "import"
        ] == "FAIL"
    ]

    report = {
        "scan": (
            "Phase 2.1 Universal Job "
            "Model Full Discovery Scan"
        ),
        "generated_at": TIMESTAMP,
        "project_root": str(
            PROJECT_ROOT
        ),
        "search_roots": [
            str(root)
            for root in search_roots
        ],
        "python_file_count": len(
            file_results
        ),
        "phase_items": (
            phase_results
        ),
        "required_job_fields": list(
            REQUIRED_JOB_FIELDS
        ),
        "field_locations": (
            field_locations
        ),
        "missing_required_fields": (
            missing_fields
        ),
        "likely_existing_items": (
            likely_existing_items
        ),
        "prohibited_findings": (
            prohibited_findings
        ),
        "compile_failures": (
            compile_failures
        ),
        "import_failures": (
            import_failures
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
        "PHASE 2.1 UNIVERSAL JOB MODEL FULL DISCOVERY SCAN",
        "=" * 78,
        "",
        f"Python files scanned: {len(file_results)}",
        "",
    ]

    for phase_item, candidates in phase_results.items():
        print(phase_item)
        print("-" * 78)

        lines.append(
            phase_item
        )

        if not candidates:
            print(
                "NO CANDIDATES FOUND"
            )

            lines.append(
                "  NO CANDIDATES FOUND"
            )

        else:
            for candidate in candidates[
                :5
            ]:
                print(
                    f"Score {candidate['score']:>3} | "
                    f"{candidate['relative_path']}"
                )

                print(
                    "      filename hits: "
                    + (
                        ", ".join(
                            candidate[
                                "filename_hits"
                            ]
                        )
                        or "none"
                    )
                )

                print(
                    "      symbol hits:   "
                    + (
                        ", ".join(
                            candidate[
                                "symbol_hits"
                            ]
                        )
                        or "none"
                    )
                )

                print(
                    "      job fields:    "
                    + str(
                        len(
                            candidate[
                                "field_hits"
                            ]
                        )
                    )
                )

                print(
                    "      compile/import: "
                    + candidate[
                        "compile"
                    ]
                    + "/"
                    + candidate[
                        "import"
                    ]
                )

                lines.extend(
                    [
                        (
                            f"  Score {candidate['score']:>3} | "
                            f"{candidate['relative_path']}"
                        ),
                        (
                            "      filename hits: "
                            + (
                                ", ".join(
                                    candidate[
                                        "filename_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      symbol hits: "
                            + (
                                ", ".join(
                                    candidate[
                                        "symbol_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      fields: "
                            + (
                                ", ".join(
                                    candidate[
                                        "field_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      prohibited hits: "
                            + (
                                ", ".join(
                                    candidate[
                                        "prohibited_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      compile/import: "
                            + candidate[
                                "compile"
                            ]
                            + "/"
                            + candidate[
                                "import"
                            ]
                        ),
                    ]
                )

        print()
        lines.append("")

    print("=" * 78)
    print("REQUIRED UNIVERSAL JOB FIELD COVERAGE")
    print("=" * 78)

    lines.extend(
        [
            "=" * 78,
            "REQUIRED UNIVERSAL JOB FIELD COVERAGE",
            "=" * 78,
        ]
    )

    for field in REQUIRED_JOB_FIELDS:
        locations = field_locations[
            field
        ]

        status = (
            "FOUND"
            if locations
            else "MISSING"
        )

        print(
            f"{status:7} {field}"
        )

        lines.append(
            f"{status:7} {field}"
        )

        for location in locations[
            :5
        ]:
            lines.append(
                f"        {location}"
            )

    print()
    print(
        f"Likely existing Phase 2.1 items: "
        f"{len(likely_existing_items)}/15"
    )
    print(
        f"Missing required fields:         "
        f"{len(missing_fields)}"
    )
    print(
        f"Compile failures:                "
        f"{len(compile_failures)}"
    )
    print(
        f"Import failures:                 "
        f"{len(import_failures)}"
    )
    print(
        f"Prohibited-boundary findings:    "
        f"{len(prohibited_findings)}"
    )
    print()
    print(f"Evidence JSON: {REPORT_JSON}")
    print(f"Evidence text: {REPORT_TEXT}")

    lines.extend(
        [
            "",
            (
                "Likely existing Phase 2.1 items: "
                f"{len(likely_existing_items)}/15"
            ),
            (
                "Missing required fields: "
                f"{len(missing_fields)}"
            ),
            (
                "Compile failures: "
                f"{len(compile_failures)}"
            ),
            (
                "Import failures: "
                f"{len(import_failures)}"
            ),
            (
                "Prohibited-boundary findings: "
                f"{len(prohibited_findings)}"
            ),
            "",
            f"Evidence JSON: {REPORT_JSON}",
            f"Evidence text: {REPORT_TEXT}",
            "",
            "NO PRODUCTION DATA WAS MODIFIED",
        ]
    )

    REPORT_TEXT.write_text(
        "\n".join(
            lines
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "PHASE 2.1 FULL DISCOVERY SCAN: PASS"
    )
    print(
        "SCAN PASS DOES NOT MEAN IMPLEMENTATION COMPLETE"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
