"""Back up and delete the obsolete Website Unified Content architecture."""

from __future__ import annotations

import ast
import hashlib
import json
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
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\wuc_full_reset_20260724_215312"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_full_reset_deletion_verification.json"
)

# ---------------------------------------------------------------------
# Dedicated WUC implementation files to remove.
# ---------------------------------------------------------------------

TARGET_FILES = [
    # Legacy persistent Store.
    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_store.py"
    ),

    # Legacy readers/checkers coupled to the Store.
    (
        SERVER_ROOT
        / "stores"
        / "crawled_article_viewer.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_article_integrity_checker.py"
    ),

    # Legacy website pipeline implementation that writes WUC bodies.
    (
        SERVER_ROOT
        / "stores"
        / "website_source_pipeline_orchestrator.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_uucd_rebuild_engine.py"
    ),

    # Old WUC workers.
    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker.py"
    ),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker_v2.py"
    ),

    (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_orchestrator.py"
    ),

    # Existing WUC builder/verifier/certifier implementation.
    # These are deleted because WUC will now be rebuilt cleanly.
    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_builder_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_verifier_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_certifier_v2.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "website_unified_content_handoff_v2.py"
    ),
]

TARGET_DIRECTORIES = [
    # Prohibited intermediate WUC body Store.
    (
        DATA_ROOT
        / "website_unified_content"
    ),
]

# Local scripts created only for WUC scanning, migration, or verification.
OPTIONAL_ROOT_FILES = [
    (
        PROJECT_ROOT
        / "scan_wuc_article_validation_handoff.py"
    ),

    (
        PROJECT_ROOT
        / "scan_wuc_intermediate_storage_exact.py"
    ),

    (
        PROJECT_ROOT
        / "scan_wuc_legacy_store_dependency_contract.py"
    ),

    (
        PROJECT_ROOT
        / "scan_wuc_store_remaining_active_dependencies.py"
    ),

    (
        PROJECT_ROOT
        / "verify_wuc_direct_uucd_handoff_v2.py"
    ),
]

# ---------------------------------------------------------------------
# Protected architecture.
# These paths must survive unchanged.
# ---------------------------------------------------------------------

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "website_article_integrity": (
        DATA_ROOT
        / "website_article_integrity"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "article_validation_engine": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_engine_v3.py"
    ),

    "article_validation_runner": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_runner_v3.py"
    ),

    "article_validation_runtime_registration": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_runtime_registration.py"
    ),

    "uucd_convergence": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_convergence.py"
    ),

    "universal_article_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),
}

EXCLUDED_SCAN_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

DELETED_MODULE_TERMS = {
    "website_unified_content_store",
    "website_unified_content_builder_v2",
    "website_unified_content_verifier_v2",
    "website_unified_content_certifier_v2",
    "website_unified_content_handoff_v2",
    "website_unified_content_batch_worker",
    "website_unified_content_batch_worker_v2",
    "website_unified_content_orchestrator",
    "website_uucd_rebuild_engine",
    "website_source_pipeline_orchestrator",
    "website_article_integrity_checker",
    "crawled_article_viewer",
}


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
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
            for candidate in path.rglob("*")
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        relative_path = file_path.relative_to(
            path
        ).as_posix()

        digest.update(
            relative_path.encode(
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


def relative(
    path: Path,
) -> str:
    try:
        return path.resolve().relative_to(
            PROJECT_ROOT
        ).as_posix()

    except ValueError:
        return str(
            path.resolve()
        )


def ensure_inside_project(
    path: Path,
) -> None:
    try:
        path.resolve().relative_to(
            PROJECT_ROOT
        )

    except ValueError as exc:
        raise RuntimeError(
            "Deletion target is outside the LinkCraftor project: "
            + str(
                path
            )
        ) from exc


def excluded_from_scan(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_SCAN_PARTS
        for part in path.parts
    )


def backup_path(
    source: Path,
) -> Path:
    relative_path = source.resolve().relative_to(
        PROJECT_ROOT
    )

    return (
        BACKUP_ROOT
        / relative_path
    )


def backup_item(
    source: Path,
) -> str:
    destination = backup_path(
        source
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
        )

    else:
        shutil.copy2(
            source,
            destination,
        )

    return relative(
        destination
    )


def delete_item(
    path: Path,
) -> None:
    ensure_inside_project(
        path
    )

    if path.is_dir():
        shutil.rmtree(
            path
        )

    elif path.exists():
        path.unlink()


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


def scan_remaining_references() -> list[dict[str, Any]]:
    findings: list[
        dict[str, Any]
    ] = []

    for path in SERVER_ROOT.rglob(
        "*.py"
    ):
        if (
            not path.is_file()
            or excluded_from_scan(
                path
            )
        ):
            continue

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        matches: list[
            dict[str, Any]
        ] = []

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):
            lowered = line.casefold()

            matched_terms = sorted(
                term
                for term in DELETED_MODULE_TERMS
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
                        line.strip()[:1000],
                }
            )

        if not matches:
            continue

        syntax_valid = True
        syntax_error = None

        try:
            ast.parse(
                source,
                filename=str(
                    path
                ),
            )

        except SyntaxError as exc:
            syntax_valid = False

            syntax_error = {
                "line_number":
                    exc.lineno,

                "message":
                    exc.msg,

                "text":
                    str(
                        exc.text or ""
                    ).strip(),
            }

        findings.append(
            {
                "path":
                    relative(
                        path
                    ),

                "syntax_valid":
                    syntax_valid,

                "syntax_error":
                    syntax_error,

                "matches":
                    matches,
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
print("=" * 104)
print(
    "WEBSITE UNIFIED CONTENT — FULL LEGACY ARCHITECTURE RESET"
)
print("=" * 104)
print()

failures: list[str] = []

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

protected_before = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

for name, path in PROTECTED_PATHS.items():
    if not path.exists():
        # The Universal Article Body Store may not yet exist.
        if name == "universal_article_body_store":
            continue

        failures.append(
            "Protected path was missing before deletion: "
            + name
            + " -> "
            + str(
                path
            )
        )

if failures:
    report = {
        "schema_version":
            "wuc_full_reset_deletion_verification_v1",

        "verification_status":
            "FAIL",

        "workspace_id":
            WORKSPACE_ID,

        "phase":
            "PRE_DELETION_PROTECTION_CHECK",

        "failures":
            failures,
    }

    write_json(
        REPORT_PATH,
        report,
    )

    for failure in failures:
        print(
            "FAIL: "
            + failure
        )

    raise SystemExit(1)


all_targets = (
    TARGET_FILES
    + OPTIONAL_ROOT_FILES
    + TARGET_DIRECTORIES
)

existing_targets = [
    path.resolve()
    for path in all_targets
    if path.exists()
]

missing_targets = [
    relative(
        path
    )
    for path in all_targets
    if not path.exists()
]

backed_up_items: list[str] = []
deleted_items: list[str] = []

for path in existing_targets:
    ensure_inside_project(
        path
    )

    backed_up_items.append(
        backup_item(
            path
        )
    )

for path in existing_targets:
    delete_item(
        path
    )

    deleted_items.append(
        relative(
            path
        )
    )


remaining_target_paths = [
    relative(
        path
    )
    for path in all_targets
    if path.exists()
]

if remaining_target_paths:
    failures.append(
        "Some WUC deletion targets still exist."
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
            "Protected architecture changed during WUC reset: "
            + name
        )


remaining_references = (
    scan_remaining_references()
)

report = {
    "schema_version":
        "wuc_full_reset_deletion_verification_v1",

    "verification_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "workspace_id":
        WORKSPACE_ID,

    "backup_root":
        str(
            BACKUP_ROOT
        ),

    "backed_up_items":
        backed_up_items,

    "deleted_items":
        deleted_items,

    "already_absent_items":
        missing_targets,

    "remaining_target_paths":
        remaining_target_paths,

    "protected_paths_unchanged":
        protected_unchanged,

    "remaining_active_reference_file_count":
        len(
            remaining_references
        ),

    "remaining_active_references":
        remaining_references,

    "legacy_wuc_store_module_exists":
        (
            SERVER_ROOT
            / "stores"
            / "website_unified_content_store.py"
        ).exists(),

    "legacy_wuc_data_root_exists":
        (
            DATA_ROOT
            / "website_unified_content"
        ).exists(),

    "canonical_wuc_available":
        False,

    "wuc_runtime_registered":
        False,

    "wuc_jobs_executed":
        False,

    "uucd_modified":
        False,

    "failures":
        failures,
}

write_json(
    REPORT_PATH,
    report,
)


print(
    "Items backed up:                  "
    + str(
        len(
            backed_up_items
        )
    )
)

print(
    "Items deleted:                    "
    + str(
        len(
            deleted_items
        )
    )
)

print(
    "Items already absent:             "
    + str(
        len(
            missing_targets
        )
    )
)

print(
    "Remaining deletion targets:       "
    + str(
        len(
            remaining_target_paths
        )
    )
)

print(
    "Legacy WUC Store module exists:   "
    + str(
        report[
            "legacy_wuc_store_module_exists"
        ]
    )
)

print(
    "Legacy WUC data root exists:      "
    + str(
        report[
            "legacy_wuc_data_root_exists"
        ]
    )
)

print(
    "Remaining active reference files: "
    + str(
        len(
            remaining_references
        )
    )
)

print()
print(
    "PROTECTED ARCHITECTURE"
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
    "REMAINING REFERENCES TO DELETED WUC MODULES"
)

if remaining_references:
    for finding in remaining_references:
        print()
        print(
            "  "
            + finding[
                "path"
            ]
        )

        for match in finding[
            "matches"
        ]:
            print(
                "    line "
                + str(
                    match[
                        "line_number"
                    ]
                )
                + ": "
                + ", ".join(
                    match[
                        "matched_terms"
                    ]
                )
            )

else:
    print(
        "  None"
    )

print()
print(
    "Canonical WUC available:          False"
)

print(
    "WUC runtime registered:           False"
)

print(
    "WUC jobs executed:                False"
)

print(
    "UUCD modified:                    False"
)

print()
print(
    "Backup location: "
    + str(
        BACKUP_ROOT
    )
)

print(
    "Verification report: "
    + str(
        REPORT_PATH
    )
)

print()

if failures:
    print(
        "WUC FULL RESET DELETION: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 104)

    raise SystemExit(1)

print(
    "WUC FULL RESET DELETION: PASS"
)

print(
    "The legacy WUC Store, WUC data, workers, builders, "
    "orchestrators and dedicated dependents were removed."
)

print(
    "UDARE, Website Article Integrity, Article Validation "
    "and UUCD convergence remain unchanged."
)

print(
    "Any remaining references shown above must be rewired "
    "when the fresh WUC is built."
)

print("=" * 104)
