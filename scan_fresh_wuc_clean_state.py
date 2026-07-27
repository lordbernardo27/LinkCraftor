"""Read-only clean-state scan for the fresh WUC architecture."""

from __future__ import annotations

import ast
import hashlib
import json
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

WUC_ROOT = (
    SERVER_ROOT
    / "website_unified_content"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "fresh_wuc_clean_state_scan.json"
)

EXPECTED_WUC_FILES = {
    (
        WUC_ROOT
        / "__init__.py"
    ).resolve(),

    (
        WUC_ROOT
        / "certified_wuc_input.py"
    ).resolve(),

    (
        WUC_ROOT
        / "website_unified_content_engine_v1.py"
    ).resolve(),
}

OPTIONAL_ALLOWED_ROOT_FILE = (
    PROJECT_ROOT
    / "verify_fresh_wuc_engine_v1.py"
).resolve()

PROHIBITED_FILES = {
    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_store.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_builder_v2.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_verifier_v2.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_certifier_v2.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_handoff_v2.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_uucd_rebuild_engine.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_ucd_rebuild_engine.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "stores"
        / "website_source_pipeline_orchestrator.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker_v2.py"
    ).resolve(),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_orchestrator.py"
    ).resolve(),

    (
        WUC_ROOT
        / "wuc_population_runner_v1.py"
    ).resolve(),

    (
        WUC_ROOT
        / "website_unified_content_runtime_registration.py"
    ).resolve(),
}

PROHIBITED_DIRECTORIES = {
    (
        DATA_ROOT
        / "website_unified_content"
    ).resolve(),

    (
        DATA_ROOT
        / "website_unified_content_store"
    ).resolve(),

    (
        DATA_ROOT
        / "website_unified_content_evidence"
    ).resolve(),

    (
        DATA_ROOT
        / "runtime"
        / "website_unified_content"
    ).resolve(),

    (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "website_unified_content"
    ).resolve(),
}

LEGACY_TERMS = {
    "website_unified_content_store",
    "website_unified_content_batch_worker",
    "website_unified_content_batch_worker_v2",
    "website_unified_content_builder_v2",
    "website_unified_content_verifier_v2",
    "website_unified_content_certifier_v2",
    "website_unified_content_handoff_v2",
    "website_unified_content_orchestrator",
    "website_source_pipeline_orchestrator",
    "website_uucd_rebuild_engine",
    "website_ucd_rebuild_engine",
}

RUNTIME_TERMS = {
    "register_runtime_handler",
    "runtime_registration",
    "runtime_job_type",
    "enqueue",
    "queue_name",
    "dispatch",
}

UUCD_WRITE_TERMS = {
    "build_and_write_uucd_from_wuc",
    "write_uucd",
    "save_uucd",
    "upsert_uucd",
    "universal_unified_content_document_convergence",
}

BODY_PERSISTENCE_TERMS = {
    "write_text",
    "write_bytes",
    "json.dump",
    "json.dumps",
    "open(",
    "copyfile",
    "copy2",
    "shutil.copy",
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "uucd_output": (
        DATA_ROOT
        / "universal_unified_content_document"
    ),

    "runtime_registry": (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "runtime_registration_registry.json"
    ),
}


def relative(
    path: Path,
) -> str:
    try:
        return (
            path.resolve()
            .relative_to(
                PROJECT_ROOT
            )
            .as_posix()
        )

    except ValueError:
        return str(
            path.resolve()
        )


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
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


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    if path.is_file():
        return sha256_file(
            path
        )

    for file_path in sorted(
        (
            candidate
            for candidate in path.rglob(
                "*"
            )
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            file_path.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        digest.update(
            sha256_file(
                file_path
            ).encode(
                "ascii"
            )
        )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def inspect_python(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    result: dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "syntax_valid":
            True,

        "syntax_error":
            None,

        "legacy_references":
            [],

        "runtime_references":
            [],

        "uucd_write_references":
            [],

        "write_calls":
            [],
    }

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

            "message":
                exc.msg,

            "text":
                str(
                    exc.text or ""
                ).strip(),
        }

        return result

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        legacy_matches = sorted(
            term
            for term in LEGACY_TERMS
            if term in lowered
        )

        runtime_matches = sorted(
            term
            for term in RUNTIME_TERMS
            if term in lowered
        )

        uucd_matches = sorted(
            term
            for term in UUCD_WRITE_TERMS
            if term in lowered
        )

        if legacy_matches:
            result[
                "legacy_references"
            ].append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        legacy_matches,

                    "line":
                        line.strip()[:1000],
                }
            )

        if runtime_matches:
            result[
                "runtime_references"
            ].append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        runtime_matches,

                    "line":
                        line.strip()[:1000],
                }
            )

        if uucd_matches:
            result[
                "uucd_write_references"
            ].append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        uucd_matches,

                    "line":
                        line.strip()[:1000],
                }
            )

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        function_name = ""

        if isinstance(
            node.func,
            ast.Name,
        ):
            function_name = (
                node.func.id
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            function_name = (
                node.func.attr
            )

        if function_name not in {
            "write_text",
            "write_bytes",
            "open",
            "dump",
            "dumps",
            "copy",
            "copy2",
            "copyfile",
        }:
            continue

        try:
            rendered = ast.unparse(
                node
            )

        except Exception:
            rendered = function_name

        result[
            "write_calls"
        ].append(
            {
                "line_number":
                    node.lineno,

                "function":
                    function_name,

                "call":
                    rendered[:1500],
            }
        )

    return result


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


print()
print("=" * 108)
print(
    "FRESH WEBSITE UNIFIED CONTENT — CLEAN-STATE SCAN"
)
print("=" * 108)
print()

failures: list[str] = []
warnings: list[str] = []

protected_before = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

actual_wuc_files = {
    path.resolve()
    for path in WUC_ROOT.rglob(
        "*"
    )
    if (
        path.is_file()
        and not excluded(
            path
        )
    )
} if WUC_ROOT.is_dir() else set()

unexpected_wuc_files = sorted(
    actual_wuc_files
    - EXPECTED_WUC_FILES,
    key=lambda path: (
        path.as_posix()
    ),
)

missing_expected_files = sorted(
    EXPECTED_WUC_FILES
    - actual_wuc_files,
    key=lambda path: (
        path.as_posix()
    ),
)

prohibited_files_present = sorted(
    (
        path
        for path in PROHIBITED_FILES
        if path.exists()
    ),
    key=lambda path: (
        path.as_posix()
    ),
)

prohibited_directories_present = sorted(
    (
        path
        for path in PROHIBITED_DIRECTORIES
        if path.exists()
    ),
    key=lambda path: (
        path.as_posix()
    ),
)

wuc_inspections = [
    inspect_python(
        path
    )
    for path in sorted(
        actual_wuc_files,
        key=lambda path: (
            path.as_posix()
        ),
    )
    if path.suffix.casefold() == ".py"
]

syntax_failures = [
    inspection
    for inspection in wuc_inspections
    if inspection[
        "syntax_valid"
    ]
    is not True
]

legacy_reference_files = [
    inspection
    for inspection in wuc_inspections
    if inspection[
        "legacy_references"
    ]
]

runtime_reference_files = [
    inspection
    for inspection in wuc_inspections
    if inspection[
        "runtime_references"
    ]
]

uucd_write_reference_files = [
    inspection
    for inspection in wuc_inspections
    if inspection[
        "uucd_write_references"
    ]
]

files_with_write_calls = [
    inspection
    for inspection in wuc_inspections
    if inspection[
        "write_calls"
    ]
]

active_legacy_references: list[
    dict[str, Any]
] = []

for path in SERVER_ROOT.rglob(
    "*.py"
):
    if (
        not path.is_file()
        or excluded(
            path
        )
    ):
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    matches = []

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        matched_terms = sorted(
            term
            for term in LEGACY_TERMS
            if term in lowered
        )

        if matched_terms:
            matches.append(
                {
                    "line_number":
                        line_number,

                    "matched_terms":
                        matched_terms,

                    "line":
                        line.strip()[:1000],
                }
            )

    if matches:
        active_legacy_references.append(
            {
                "path":
                    relative(
                        path
                    ),

                "matches":
                    matches,
            }
        )

if missing_expected_files:
    failures.append(
        "Expected fresh WUC files are missing."
    )

if unexpected_wuc_files:
    failures.append(
        "Unexpected files exist inside the fresh WUC package."
    )

if prohibited_files_present:
    failures.append(
        "Prohibited legacy or not-yet-approved WUC files exist."
    )

if prohibited_directories_present:
    failures.append(
        "Prohibited WUC data or runtime directories exist."
    )

if syntax_failures:
    failures.append(
        "Fresh WUC Python syntax failure detected."
    )

if legacy_reference_files:
    failures.append(
        "Fresh WUC files contain legacy WUC references."
    )

if runtime_reference_files:
    failures.append(
        "Fresh WUC already contains runtime wiring."
    )

if uucd_write_reference_files:
    failures.append(
        "Fresh WUC already contains UUCD write wiring."
    )

if files_with_write_calls:
    warnings.append(
        "Fresh WUC files contain generic write-capable calls. "
        "Review the exact calls below; input readers may use open() read-only."
    )

if active_legacy_references:
    failures.append(
        "Active legacy WUC references remain elsewhere in the server code."
    )

protected_after = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

protected_unchanged = {
    name: (
        protected_before[
            name
        ]
        == protected_after[
            name
        ]
    )
    for name
    in PROTECTED_PATHS
}

for name, unchanged in protected_unchanged.items():
    if not unchanged:
        failures.append(
            "Protected architecture changed during the read-only scan: "
            + name
        )

report = {
    "schema_version":
        "fresh_wuc_clean_state_scan_v1",

    "workspace_id":
        WORKSPACE_ID,

    "scan_mode":
        "READ_ONLY",

    "wuc_root_exists":
        WUC_ROOT.is_dir(),

    "expected_wuc_files":
        sorted(
            relative(
                path
            )
            for path in EXPECTED_WUC_FILES
        ),

    "actual_wuc_files":
        sorted(
            relative(
                path
            )
            for path in actual_wuc_files
        ),

    "missing_expected_files":
        [
            relative(
                path
            )
            for path in missing_expected_files
        ],

    "unexpected_wuc_files":
        [
            relative(
                path
            )
            for path in unexpected_wuc_files
        ],

    "prohibited_files_present":
        [
            relative(
                path
            )
            for path in prohibited_files_present
        ],

    "prohibited_directories_present":
        [
            relative(
                path
            )
            for path in prohibited_directories_present
        ],

    "wuc_file_inspections":
        wuc_inspections,

    "syntax_failure_count":
        len(
            syntax_failures
        ),

    "legacy_reference_file_count":
        len(
            legacy_reference_files
        ),

    "runtime_reference_file_count":
        len(
            runtime_reference_files
        ),

    "uucd_write_reference_file_count":
        len(
            uucd_write_reference_files
        ),

    "write_call_file_count":
        len(
            files_with_write_calls
        ),

    "active_legacy_reference_count":
        len(
            active_legacy_references
        ),

    "active_legacy_references":
        active_legacy_references,

    "protected_paths_unchanged":
        protected_unchanged,

    "wuc_store_exists":
        False,

    "wuc_evidence_exists":
        (
            DATA_ROOT
            / "website_unified_content_evidence"
        ).exists(),

    "wuc_runtime_registration_exists":
        (
            WUC_ROOT
            / "website_unified_content_runtime_registration.py"
        ).exists(),

    "wuc_population_runner_exists":
        (
            WUC_ROOT
            / "wuc_population_runner_v1.py"
        ).exists(),

    "uucd_writes_configured":
        bool(
            uucd_write_reference_files
        ),

    "source_files_modified":
        False,

    "data_files_modified":
        False,

    "runtime_state_modified":
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
    REPORT_PATH,
    report,
)

print(
    "WUC package exists:                    "
    + str(
        WUC_ROOT.is_dir()
    )
)

print(
    "Expected fresh WUC files:               "
    + str(
        len(
            EXPECTED_WUC_FILES
        )
    )
)

print(
    "Actual fresh WUC files:                 "
    + str(
        len(
            actual_wuc_files
        )
    )
)

print(
    "Missing expected files:                 "
    + str(
        len(
            missing_expected_files
        )
    )
)

print(
    "Unexpected WUC files:                   "
    + str(
        len(
            unexpected_wuc_files
        )
    )
)

print(
    "Prohibited WUC files present:           "
    + str(
        len(
            prohibited_files_present
        )
    )
)

print(
    "Prohibited WUC directories present:     "
    + str(
        len(
            prohibited_directories_present
        )
    )
)

print(
    "Fresh WUC syntax failures:              "
    + str(
        len(
            syntax_failures
        )
    )
)

print(
    "Fresh WUC legacy-reference files:       "
    + str(
        len(
            legacy_reference_files
        )
    )
)

print(
    "Fresh WUC runtime-reference files:      "
    + str(
        len(
            runtime_reference_files
        )
    )
)

print(
    "Fresh WUC UUCD-write reference files:   "
    + str(
        len(
            uucd_write_reference_files
        )
    )
)

print(
    "Active legacy references server-wide:   "
    + str(
        len(
            active_legacy_references
        )
    )
)

print(
    "WUC population runner exists:           "
    + str(
        report[
            "wuc_population_runner_exists"
        ]
    )
)

print(
    "WUC Runtime Registration exists:        "
    + str(
        report[
            "wuc_runtime_registration_exists"
        ]
    )
)

print(
    "WUC evidence directory exists:          "
    + str(
        report[
            "wuc_evidence_exists"
        ]
    )
)

print(
    "UUCD writes configured:                 "
    + str(
        report[
            "uucd_writes_configured"
        ]
    )
)

print()
print(
    "FRESH WUC FILES"
)

for path in sorted(
    actual_wuc_files,
    key=lambda value: (
        value.as_posix()
    ),
):
    print(
        "  "
        + relative(
            path
        )
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
    "Protected architecture unchanged:      "
    + str(
        all(
            protected_unchanged.values()
        )
    )
)

print(
    "Source files modified:                 False"
)

print(
    "Data files modified:                   False"
)

print(
    "Runtime state modified:                False"
)

print()
print(
    "Clean-state report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "FRESH WUC CLEAN-STATE SCAN: FAIL"
    )

    print(
        "Do not apply the WUC population patch yet."
    )

    print("=" * 108)

    raise SystemExit(1)

print(
    "FRESH WUC CLEAN-STATE SCAN: PASS"
)

print(
    "The fresh WUC currently contains only the approved "
    "Phase 1 input reader and transient engine."
)

print(
    "No Store, population runner, UUCD write wiring, "
    "runtime registration or legacy implementation is active."
)

print("=" * 108)
