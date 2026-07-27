"""Back up and retire the obsolete UUCD implementation."""

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
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\legacy_uucd_implementation_retirement_20260726_233311"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "legacy_uucd_implementation_retirement_v1.json"
)

# Obsolete UUCD implementation only.
RETIREMENT_TARGETS = {
    "canonical_convergence": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_convergence.py"
    ),

    "legacy_convergence_wrapper": (
        SERVER_ROOT
        / "stores"
        / "unified_content_document_convergence.py"
    ),

    "canonical_viewer": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_viewer.py"
    ),

    "legacy_viewer_wrapper": (
        SERVER_ROOT
        / "stores"
        / "unified_content_document_viewer.py"
    ),

    "legacy_integrity_checker": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_integrity_checker.py"
    ),

    "legacy_validated_article_bridge": (
        SERVER_ROOT
        / "stores"
        / "validated_article_uucd_bridge.py"
    ),

    "legacy_validated_article_ucd_bridge": (
        SERVER_ROOT
        / "stores"
        / "validated_article_ucd_bridge.py"
    ),

    "legacy_canonical_store_builder": (
        SERVER_ROOT
        / "builders"
        / "build_canonical_uucd_store.py"
    ),
}

# These must not be deleted or changed.
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

    "source_asset_version_registry_builder": (
        SERVER_ROOT
        / "builders"
        / "build_source_asset_version_registry.py"
    ),

    "source_lifecycle_registry_builder": (
        SERVER_ROOT
        / "builders"
        / "build_source_lifecycle_snapshot_registry.py"
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

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

RETIRED_MODULE_TERMS = {
    "universal_unified_content_document_convergence",
    "unified_content_document_convergence",
    "universal_unified_content_document_viewer",
    "unified_content_document_viewer",
    "universal_unified_content_integrity_checker",
    "validated_article_uucd_bridge",
    "validated_article_ucd_bridge",
    "build_canonical_uucd_store",
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
        / source.relative_to(
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


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_PARTS
        for part in path.parts
    )


print()
print("=" * 108)
print(
    "LEGACY UUCD IMPLEMENTATION — CONTROLLED RETIREMENT"
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

            "original_exists_after_retirement":
                source.exists(),

            "backup_exists":
                destination.exists(),

            "backup_verified":
                source_hash
                == backup_hash,
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
        "One or more obsolete UUCD files remain active."
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
            for term in RETIRED_MODULE_TERMS
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
        "legacy_uucd_implementation_retirement_v1",

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
    "Obsolete UUCD files still active:    "
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
    "Fresh UUCD created:       False"
)

print(
    "UUCD data written:        False"
)

print(
    "Body Store data written:  False"
)

print(
    "Runtime state modified:   False"
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
        "LEGACY UUCD IMPLEMENTATION RETIREMENT: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 108)

    raise SystemExit(1)

print(
    "LEGACY UUCD IMPLEMENTATION RETIREMENT: PASS"
)

print(
    "The obsolete UUCD convergence, wrappers, viewer, integrity checker, "
    "validated-article bridges and canonical Store builder were retired."
)

if remaining_references:
    print(
        "Remaining imports or textual references were detected and must be "
        "cleaned before the fresh UUCD implementation is created."
    )

else:
    print(
        "No active server-side references to the retired implementation remain."
    )

print("=" * 108)
