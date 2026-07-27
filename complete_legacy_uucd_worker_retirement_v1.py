"""Complete retirement of legacy UUCD workers and their active references."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
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

BACKUP_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\complete_legacy_uucd_worker_retirement_20260726_234558"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "complete_legacy_uucd_worker_retirement_v1.json"
)

MAIN_PATH = (
    SERVER_ROOT
    / "main.py"
)

SITE_WORKSPACE_PATH = (
    SERVER_ROOT
    / "routes"
    / "site_workspace.py"
)

DELETE_TARGETS = {
    "automatic_canonical_rebuild_runner": (
        SERVER_ROOT
        / "runtime"
        / "automatic_canonical_rebuild_runner.py"
    ),

    "live_route_orchestration_hooks": (
        SERVER_ROOT
        / "runtime"
        / "live_route_orchestration_hooks.py"
    ),

    "registry_driven_canonical_rebuild_manager": (
        SERVER_ROOT
        / "runtime"
        / "registry_driven_canonical_rebuild_manager.py"
    ),

    "universal_knowledge_queue_runner": (
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_queue_runner.py"
    ),
}

EDIT_TARGETS = {
    "main":
        MAIN_PATH,

    "site_workspace":
        SITE_WORKSPACE_PATH,
}

PROTECTED_PATHS = {
    "wuc_package": (
        SERVER_ROOT
        / "website_unified_content"
    ),

    "uploaded_document_unified_content": (
        SERVER_ROOT
        / "stores"
        / "uploaded_document_unified_content.py"
    ),

    "universal_article_body_store_code": (
        SERVER_ROOT
        / "stores"
        / "universal_article_body_store.py"
    ),

    "uucd_body_store_certification_code": (
        SERVER_ROOT
        / "stores"
        / "uucd_body_store_certification.py"
    ),

    "source_lifecycle_control": (
        SERVER_ROOT
        / "stores"
        / "source_lifecycle_control.py"
    ),

    "universal_knowledge_orchestrator": (
        SERVER_ROOT
        / "jobs"
        / "universal_knowledge_orchestrator.py"
    ),

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

    "wuc_evidence": (
        DATA_ROOT
        / "website_unified_content_evidence"
        / WORKSPACE_ID
    ),

    "runtime_registry": (
        DATA_ROOT
        / "runtime"
        / "universal_runtime_registration"
        / "runtime_registration_registry.json"
    ),
}

RETIRED_TERMS = {
    "backend.server.orchestration.worker",
    "orchestration.worker",
    "run_one_job",
    "backend.server.workers.universal_knowledge_worker",
    "workers.universal_knowledge_worker",
    "execute_universal_knowledge_job_v1",
    "backend.server.workers.universal_knowledge_queue_runner",
    "universal_knowledge_queue_runner",
    "automatic_canonical_rebuild_runner",
    "live_route_orchestration_hooks",
    "registry_driven_canonical_rebuild_manager",
    "universal_unified_content_document_convergence",
    "build_and_write_uucd_from_uduc_v1",
}

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}


def ensure_inside_project(
    path: Path,
) -> None:
    try:
        path.resolve().relative_to(
            PROJECT_ROOT
        )

    except ValueError as exc:
        raise RuntimeError(
            "Refusing to operate outside LinkCraftor: "
            + str(
                path
            )
        ) from exc


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


def backup_file(
    source: Path,
) -> Path:
    ensure_inside_project(
        source
    )

    destination = (
        BACKUP_ROOT
        / source.resolve().relative_to(
            PROJECT_ROOT
        )
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        source,
        destination,
    )

    if sha256_file(
        source
    ) != sha256_file(
        destination
    ):
        raise RuntimeError(
            "Backup verification failed: "
            + str(
                source
            )
        )

    return destination


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


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
print("=" * 112)
print(
    "COMPLETE LEGACY UUCD WORKER AND REFERENCE RETIREMENT"
)
print("=" * 112)
print()

failures: list[str] = []
changes: list[
    dict[str, Any]
] = []

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

for name, path in {
    **PROTECTED_PATHS,
    **EDIT_TARGETS,
}.items():
    if not path.exists():
        failures.append(
            "Required component is missing before retirement: "
            + name
            + " -> "
            + str(
                path
            )
        )

if failures:
    for failure in failures:
        print(
            "FAIL: "
            + failure
        )

    raise SystemExit(1)


protected_before = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}


# ------------------------------------------------------------------
# Back up the two core files before editing.
# ------------------------------------------------------------------

for name, path in EDIT_TARGETS.items():
    destination = backup_file(
        path
    )

    changes.append(
        {
            "action":
                "BACKUP_BEFORE_EDIT",

            "name":
                name,

            "path":
                relative(
                    path
                ),

            "backup":
                str(
                    destination
                ),
        }
    )


# ------------------------------------------------------------------
# Remove the obsolete background worker from main.py.
# ------------------------------------------------------------------

main_source = MAIN_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

main_pattern = re.compile(
    r"""
    \n?
    [ \t]*\#[ \t]*-+[ \t]*\n
    [ \t]*\#[ \t]*Phase[ \t]+2\.3[ \t]+Background[ \t]+Worker[ \t]+Startup[ \t]*\n
    [ \t]*\#[ \t]*-+[ \t]*\n
    [ \t]*async[ \t]+def[ \t]+_linkcraftor_background_worker_loop\(\):[ \t]*\n
    .*?
    [ \t]*@app\.on_event\("startup"\)[ \t]*\n
    [ \t]*async[ \t]+def[ \t]+_start_linkcraftor_background_worker\(\):[ \t]*\n
    [ \t]+asyncio\.create_task\(_linkcraftor_background_worker_loop\(\)\)[ \t]*\n
    [ \t]+log\.info\("\[BACKGROUND_WORKER\][^"]*"\)[ \t]*\n?
    """,
    flags=(
        re.DOTALL
        | re.VERBOSE
    ),
)

main_updated, main_replacements = (
    main_pattern.subn(
        "\n",
        main_source,
        count=1,
    )
)

if main_replacements != 1:
    failures.append(
        "Expected exactly one legacy background-worker block "
        f"in main.py; found {main_replacements}."
    )

else:
    MAIN_PATH.write_text(
        main_updated,
        encoding="utf-8",
    )

    changes.append(
        {
            "action":
                "REMOVE_LEGACY_BACKGROUND_WORKER_BLOCK",

            "path":
                relative(
                    MAIN_PATH
                ),

            "replacement_count":
                main_replacements,
        }
    )


# ------------------------------------------------------------------
# Remove synchronous deleted-worker execution from site_workspace.py.
# Keep job creation so future workers can process the queued job.
# ------------------------------------------------------------------

site_source = SITE_WORKSPACE_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

worker_import_pattern = re.compile(
    r"""
    ^[ \t]*from[ \t]+
    backend\.server\.workers\.universal_knowledge_worker
    [ \t]+import[ \t]+
    execute_universal_knowledge_job_v1
    [ \t]*\r?\n
    """,
    flags=(
        re.MULTILINE
        | re.VERBOSE
    ),
)

site_updated, import_replacements = (
    worker_import_pattern.subn(
        "",
        site_source,
        count=1,
    )
)

if import_replacements != 1:
    failures.append(
        "Expected exactly one universal knowledge worker import "
        f"in site_workspace.py; found {import_replacements}."
    )


execution_pattern = re.compile(
    r"""
    ^(?P<indent>[ \t]*)
    job_result[ \t]*=[ \t]*
    execute_universal_knowledge_job_v1\(job\)
    [ \t]*\r?\n
    """,
    flags=(
        re.MULTILINE
        | re.VERBOSE
    ),
)

site_updated, execution_replacements = (
    execution_pattern.subn(
        "",
        site_updated,
        count=1,
    )
)

if execution_replacements != 1:
    failures.append(
        "Expected exactly one synchronous worker execution "
        f"in site_workspace.py; found {execution_replacements}."
    )


job_result_reference_pattern = re.compile(
    r"""
    (?P<prefix>
        ["']job["']
        [ \t]*:
        [ \t]*
    )
    job_result
    """,
    flags=re.VERBOSE,
)

site_updated, job_reference_replacements = (
    job_result_reference_pattern.subn(
        r"\g<prefix>job",
        site_updated,
        count=1,
    )
)

if job_reference_replacements != 1:
    failures.append(
        "Expected exactly one returned job_result reference "
        f"in site_workspace.py; found {job_reference_replacements}."
    )


# Make the route’s state explicit: the domain request created a queued job,
# but no worker has executed it yet.
connected_pattern = re.compile(
    r"""
    (?P<prefix>
        ["']connected["']
        [ \t]*:
        [ \t]*
    )
    True
    """,
    flags=re.VERBOSE,
)

site_updated, connected_replacements = (
    connected_pattern.subn(
        r"\g<prefix>False",
        site_updated,
        count=1,
    )
)

if connected_replacements != 1:
    failures.append(
        "Expected exactly one connected=True field "
        f"in site_workspace.py; found {connected_replacements}."
    )


job_line_pattern = re.compile(
    r"""
    (?P<indent>[ \t]*)
    ["']job["']
    [ \t]*:
    [ \t]*
    job
    [ \t]*,
    """,
    flags=re.VERBOSE,
)

site_updated, status_replacements = (
    job_line_pattern.subn(
        (
            r'\g<indent>"execution_status": '
            r'"QUEUED_AWAITING_FRESH_WORKER",\n'
            r'\g<indent>"job": job,'
        ),
        site_updated,
        count=1,
    )
)

if status_replacements != 1:
    failures.append(
        "Expected exactly one job return field for adding queued status; "
        f"found {status_replacements}."
    )


if not failures:
    SITE_WORKSPACE_PATH.write_text(
        site_updated,
        encoding="utf-8",
    )

    changes.append(
        {
            "action":
                "REMOVE_SYNCHRONOUS_LEGACY_WORKER_EXECUTION",

            "path":
                relative(
                    SITE_WORKSPACE_PATH
                ),

            "worker_import_removed":
                import_replacements,

            "worker_execution_removed":
                execution_replacements,

            "job_result_replaced":
                job_reference_replacements,

            "connected_state_changed":
                connected_replacements,

            "queued_status_added":
                status_replacements,
        }
    )


# ------------------------------------------------------------------
# Back up and delete the four dedicated legacy files.
# ------------------------------------------------------------------

retired_files: list[
    dict[str, Any]
] = []

already_absent: list[
    dict[str, Any]
] = []

if not failures:
    for name, source in DELETE_TARGETS.items():
        if not source.exists():
            already_absent.append(
                {
                    "name":
                        name,

                    "path":
                        relative(
                            source
                        ),
                }
            )

            continue

        if not source.is_file():
            failures.append(
                "Deletion target is not a file: "
                + str(
                    source
                )
            )

            continue

        source_hash = sha256_file(
            source
        )

        destination = backup_file(
            source
        )

        source.unlink()

        retired_files.append(
            {
                "name":
                    name,

                "original_path":
                    relative(
                        source
                    ),

                "backup_path":
                    str(
                        destination
                    ),

                "sha256":
                    source_hash,

                "backup_verified":
                    sha256_file(
                        destination
                    )
                    == source_hash,

                "original_exists_after_retirement":
                    source.exists(),
            }
        )


# ------------------------------------------------------------------
# Syntax verification of the edited core files.
# ------------------------------------------------------------------

syntax_results: dict[
    str,
    dict[str, Any]
] = {}

for name, path in EDIT_TARGETS.items():
    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        ast.parse(
            source,
            filename=str(
                path
            ),
        )

        syntax_results[
            name
        ] = {
            "path":
                relative(
                    path
                ),

            "syntax_valid":
                True,

            "error":
                None,
        }

    except Exception as exc:
        syntax_results[
            name
        ] = {
            "path":
                relative(
                    path
                ),

            "syntax_valid":
                False,

            "error":
                str(
                    exc
                ),
        }

        failures.append(
            "Syntax verification failed for "
            + relative(
                path
            )
            + ": "
            + str(
                exc
            )
        )


# ------------------------------------------------------------------
# Verify deleted files are absent.
# ------------------------------------------------------------------

remaining_delete_targets = {
    name:
        relative(
            path
        )
    for name, path
    in DELETE_TARGETS.items()
    if path.exists()
}

if remaining_delete_targets:
    failures.append(
        "One or more dedicated legacy runtime files remain."
    )


# ------------------------------------------------------------------
# Verify protected architecture remained unchanged.
# ------------------------------------------------------------------

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
            "Protected component changed during retirement: "
            + name
        )


# ------------------------------------------------------------------
# Final active-reference scan.
# ------------------------------------------------------------------

remaining_references: list[
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

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    matches: list[
        dict[str, Any]
    ] = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        lowered = line.casefold()

        matched_terms = sorted(
            term
            for term in RETIRED_TERMS
            if term in lowered
        )

        if not matched_terms:
            continue

        matches.append(
            {
                "line_number":
                    line_number,

                "matched_terms":
                    matched_terms,

                "line":
                    line.strip()[:1500],
            }
        )

    if matches:
        remaining_references.append(
            {
                "path":
                    relative(
                        path
                    ),

                "matches":
                    matches,
            }
        )

if remaining_references:
    failures.append(
        "Active references to retired workers or UUCD symbols remain."
    )


# ------------------------------------------------------------------
# Final checks and report.
# ------------------------------------------------------------------

checks = {
    "main_background_worker_removed":
        (
            "backend.server.orchestration.worker"
            not in MAIN_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
            and "run_one_job"
            not in MAIN_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
            and "_linkcraftor_background_worker_loop"
            not in MAIN_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_workspace_worker_import_removed":
        (
            "universal_knowledge_worker"
            not in SITE_WORKSPACE_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_workspace_worker_execution_removed":
        (
            "execute_universal_knowledge_job_v1"
            not in SITE_WORKSPACE_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_workspace_still_creates_job":
        (
            "create_universal_knowledge_job"
            in SITE_WORKSPACE_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "site_workspace_marks_job_queued":
        (
            "QUEUED_AWAITING_FRESH_WORKER"
            in SITE_WORKSPACE_PATH.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        ),

    "core_files_syntax_valid":
        all(
            result[
                "syntax_valid"
            ]
            for result in syntax_results.values()
        ),

    "dedicated_legacy_files_absent":
        not remaining_delete_targets,

    "zero_remaining_active_references":
        not remaining_references,

    "protected_components_unchanged":
        all(
            protected_unchanged.values()
        ),
}

for name, passed in checks.items():
    if passed is not True:
        failures.append(
            "Final verification failed: "
            + name
        )


report = {
    "schema_version":
        "complete_legacy_uucd_worker_retirement_v1",

    "workspace_id":
        WORKSPACE_ID,

    "retirement_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "backup_root":
        str(
            BACKUP_ROOT
        ),

    "checks":
        checks,

    "changes":
        changes,

    "retired_files":
        retired_files,

    "already_absent":
        already_absent,

    "remaining_delete_targets":
        remaining_delete_targets,

    "remaining_reference_file_count":
        len(
            remaining_references
        ),

    "remaining_references":
        remaining_references,

    "syntax_results":
        syntax_results,

    "protected_components_unchanged":
        protected_unchanged,

    "fresh_worker_created":
        False,

    "fresh_uucd_created":
        False,

    "uucd_data_written":
        False,

    "body_store_data_written":
        False,

    "runtime_state_modified":
        False,

    "failures":
        failures,
}

write_json(
    REPORT_PATH,
    report,
)


print(
    "Core files edited:                     "
    + str(
        len(
            EDIT_TARGETS
        )
    )
)

print(
    "Dedicated legacy files retired:        "
    + str(
        len(
            retired_files
        )
    )
)

print(
    "Dedicated files already absent:        "
    + str(
        len(
            already_absent
        )
    )
)

print(
    "Legacy files still active:             "
    + str(
        len(
            remaining_delete_targets
        )
    )
)

print(
    "Remaining active reference files:      "
    + str(
        len(
            remaining_references
        )
    )
)

print()
print(
    "FINAL CHECKS"
)

for name, passed in checks.items():
    print(
        "  "
        + f"{name:<48}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "RETIRED DEDICATED FILES"
)

if retired_files:
    for item in retired_files:
        print(
            "  "
            + item[
                "original_path"
            ]
        )

else:
    print(
        "  None"
    )

print()
print(
    "PROTECTED COMPONENTS"
)

for name, unchanged in protected_unchanged.items():
    print(
        "  "
        + name
        + ": "
        + (
            "UNCHANGED"
            if unchanged
            else "CHANGED"
        )
    )

print()
print(
    "REMAINING REFERENCES"
)

if remaining_references:
    for result in remaining_references:
        print()
        print(
            "  FILE: "
            + result[
                "path"
            ]
        )

        for match in result[
            "matches"
        ]:
            print(
                "    Line "
                + str(
                    match[
                        "line_number"
                    ]
                )
                + ": "
                + match[
                    "line"
                ]
            )

else:
    print(
        "  None"
    )

print()
print(
    "Fresh worker created:      False"
)

print(
    "Fresh UUCD created:        False"
)

print(
    "UUCD data written:         False"
)

print(
    "Body Store data written:   False"
)

print(
    "Runtime state modified:    False"
)

print()
print(
    "Backup location: "
    + str(
        BACKUP_ROOT
    )
)

print(
    "Retirement report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "COMPLETE LEGACY UUCD WORKER RETIREMENT: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 112)

    raise SystemExit(1)

print(
    "COMPLETE LEGACY UUCD WORKER RETIREMENT: PASS"
)

print(
    "All remaining legacy UUCD worker files, runtime runners and "
    "active core-file references were safely retired."
)

print(
    "Job creation remains available, but execution is intentionally "
    "queued until the fresh worker and Runtime Registration are built."
)

print("=" * 112)
