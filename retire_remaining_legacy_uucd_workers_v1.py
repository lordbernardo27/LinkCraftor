"""Retire the remaining legacy UUCD worker and compatibility files."""

from __future__ import annotations

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
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\remaining_legacy_uucd_workers_retirement_20260726_234014"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "remaining_legacy_uucd_workers_retirement_v1.json"
)

RETIREMENT_TARGETS = {
    "legacy_orchestration_worker": (
        SERVER_ROOT
        / "orchestration"
        / "worker.py"
    ),

    "legacy_integrity_wrapper": (
        SERVER_ROOT
        / "stores"
        / "unified_content_integrity_checker.py"
    ),

    "legacy_universal_knowledge_worker": (
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_worker.py"
    ),
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
    "backend.server.workers.universal_knowledge_worker",
    "workers.universal_knowledge_worker",
    "unified_content_integrity_checker",
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
print("=" * 108)
print(
    "REMAINING LEGACY UUCD WORKERS — CONTROLLED RETIREMENT"
)
print("=" * 108)
print()

failures: list[str] = []

for name, path in PROTECTED_PATHS.items():
    if not path.exists():
        failures.append(
            "Protected component is missing before retirement: "
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

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

retired_files: list[
    dict[str, Any]
] = []

already_absent: list[
    dict[str, Any]
] = []


for name, source in RETIREMENT_TARGETS.items():
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
            "Retirement target is not a file: "
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

    backup_hash = sha256_file(
        destination
    )

    if source_hash != backup_hash:
        failures.append(
            "Backup verification failed for "
            + name
        )

        continue

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
                source_hash
                == backup_hash,

            "original_exists_after_retirement":
                source.exists(),
        }
    )


remaining_targets = {
    name:
        relative(
            path
        )
    for name, path
    in RETIREMENT_TARGETS.items()
    if path.exists()
}

if remaining_targets:
    failures.append(
        "One or more legacy worker files remain active."
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
            "Protected component changed during retirement: "
            + name
        )


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

    matches = []

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


report = {
    "schema_version":
        "remaining_legacy_uucd_workers_retirement_v1",

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

    "retirement_target_count":
        len(
            RETIREMENT_TARGETS
        ),

    "retired_file_count":
        len(
            retired_files
        ),

    "already_absent_count":
        len(
            already_absent
        ),

    "retired_files":
        retired_files,

    "already_absent":
        already_absent,

    "remaining_targets":
        remaining_targets,

    "protected_components_unchanged":
        protected_unchanged,

    "remaining_reference_file_count":
        len(
            remaining_references
        ),

    "remaining_references":
        remaining_references,

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
    "Retirement targets:                  "
    + str(
        len(
            RETIREMENT_TARGETS
        )
    )
)

print(
    "Files retired:                       "
    + str(
        len(
            retired_files
        )
    )
)

print(
    "Files already absent:                "
    + str(
        len(
            already_absent
        )
    )
)

print(
    "Legacy worker files still active:    "
    + str(
        len(
            remaining_targets
        )
    )
)

print(
    "Remaining reference files:           "
    + str(
        len(
            remaining_references
        )
    )
)

print()
print(
    "RETIRED FILES"
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
        "REMAINING LEGACY UUCD WORKERS RETIREMENT: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 108)

    raise SystemExit(1)

print(
    "REMAINING LEGACY UUCD WORKERS RETIREMENT: PASS"
)

print(
    "The obsolete orchestration worker, universal knowledge worker "
    "and compatibility integrity wrapper were backed up and deleted."
)

if remaining_references:
    print(
        "Other server files still mention retired worker or UUCD symbols. "
        "Those references must also be retired before rebuilding."
    )

else:
    print(
        "No active server-side references to the retired UUCD workers remain."
    )

print("=" * 108)
