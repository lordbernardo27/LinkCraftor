"""Back up and remove legacy UUCD and Universal Article Body Store outputs."""

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
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\legacy_uucd_body_store_reset_20260726_004817"
).resolve()

LEGACY_UUCD_ROOT = (
    DATA_ROOT
    / "universal_unified_content_documents"
)

LEGACY_BODY_STORE_ROOT = (
    DATA_ROOT
    / "universal_article_body_store"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "legacy_uucd_body_store_deletion_verification.json"
)

TARGETS = {
    "legacy_uucd":
        LEGACY_UUCD_ROOT,

    "legacy_universal_article_body_store":
        LEGACY_BODY_STORE_ROOT,
}

# These are authoritative rebuild sources and must remain untouched.
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

    "wuc_evidence": (
        DATA_ROOT
        / "website_unified_content_evidence"
        / WORKSPACE_ID
    ),

    "wuc_verification": (
        DATA_ROOT
        / "article_validation_scan"
        / WORKSPACE_ID
        / "wuc_population_runner_v1_verification.json"
    ),

    "uploaded_source_identity_report": (
        DATA_ROOT
        / "article_validation_scan"
        / WORKSPACE_ID
        / "uploaded_uucd_authoritative_source_identity.json"
    ),

    "uucd_rebuild_coverage_report": (
        DATA_ROOT
        / "article_validation_scan"
        / WORKSPACE_ID
        / "uucd_rebuild_source_coverage.json"
    ),

    "wuc_engine": (
        SERVER_ROOT
        / "website_unified_content"
        / "website_unified_content_engine_v1.py"
    ),

    "wuc_runner": (
        SERVER_ROOT
        / "website_unified_content"
        / "wuc_population_runner_v1.py"
    ),

    "uucd_convergence_code": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_convergence.py"
    ),

    "body_store_code": (
        SERVER_ROOT
        / "stores"
        / "universal_article_body_store.py"
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


def count_files(
    path: Path,
) -> int:
    if not path.exists():
        return 0

    if path.is_file():
        return 1

    return sum(
        1
        for candidate in path.rglob(
            "*"
        )
        if candidate.is_file()
    )


def count_directories(
    path: Path,
) -> int:
    if not path.is_dir():
        return 0

    return sum(
        1
        for candidate in path.rglob(
            "*"
        )
        if candidate.is_dir()
    )


def total_bytes(
    path: Path,
) -> int:
    if not path.exists():
        return 0

    if path.is_file():
        return path.stat().st_size

    return sum(
        candidate.stat().st_size
        for candidate in path.rglob(
            "*"
        )
        if candidate.is_file()
    )


def backup_item(
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

    return destination


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


print()
print("=" * 108)
print(
    "LEGACY UUCD AND UNIVERSAL ARTICLE BODY STORE — CONTROLLED RESET"
)
print("=" * 108)
print()

failures: list[str] = []

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

for name, path in PROTECTED_PATHS.items():
    if not path.exists():
        failures.append(
            "Protected rebuild source is missing before deletion: "
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

target_inventory_before = {
    name: {
        "path":
            relative(
                path
            ),

        "exists":
            path.exists(),

        "file_count":
            count_files(
                path
            ),

        "directory_count":
            count_directories(
                path
            ),

        "total_bytes":
            total_bytes(
                path
            ),

        "fingerprint":
            fingerprint(
                path
            ),
    }
    for name, path
    in TARGETS.items()
}


backup_inventory: dict[
    str,
    dict[str, Any]
] = {}

deleted_targets: list[str] = []
already_absent_targets: list[str] = []

for name, source in TARGETS.items():
    if not source.exists():
        already_absent_targets.append(
            name
        )

        continue

    destination = backup_item(
        source
    )

    source_fingerprint = fingerprint(
        source
    )

    destination_fingerprint = fingerprint(
        destination
    )

    source_file_count = count_files(
        source
    )

    destination_file_count = count_files(
        destination
    )

    if (
        source_fingerprint
        != destination_fingerprint
    ):
        failures.append(
            "Backup fingerprint mismatch for "
            + name
        )

    if (
        source_file_count
        != destination_file_count
    ):
        failures.append(
            "Backup file-count mismatch for "
            + name
        )

    backup_inventory[
        name
    ] = {
        "source":
            relative(
                source
            ),

        "backup":
            str(
                destination
            ),

        "source_file_count":
            source_file_count,

        "backup_file_count":
            destination_file_count,

        "source_fingerprint":
            source_fingerprint,

        "backup_fingerprint":
            destination_fingerprint,

        "backup_verified":
            (
                source_fingerprint
                == destination_fingerprint
                and source_file_count
                == destination_file_count
            ),
    }


if failures:
    report = {
        "schema_version":
            "legacy_uucd_body_store_deletion_verification_v1",

        "verification_status":
            "FAIL",

        "phase":
            "BACKUP_VERIFICATION",

        "backup_root":
            str(
                BACKUP_ROOT
            ),

        "target_inventory_before":
            target_inventory_before,

        "backup_inventory":
            backup_inventory,

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


for name, target in TARGETS.items():
    if not target.exists():
        continue

    delete_item(
        target
    )

    deleted_targets.append(
        name
    )


remaining_targets = {
    name:
        relative(
            path
        )
    for name, path
    in TARGETS.items()
    if path.exists()
}

if remaining_targets:
    failures.append(
        "One or more legacy output directories still exist."
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
            "Protected rebuild source changed: "
            + name
        )


target_inventory_after = {
    name: {
        "path":
            relative(
                path
            ),

        "exists":
            path.exists(),

        "file_count":
            count_files(
                path
            ),

        "directory_count":
            count_directories(
                path
            ),

        "total_bytes":
            total_bytes(
                path
            ),
    }
    for name, path
    in TARGETS.items()
}


report = {
    "schema_version":
        "legacy_uucd_body_store_deletion_verification_v1",

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

    "target_inventory_before":
        target_inventory_before,

    "backup_inventory":
        backup_inventory,

    "deleted_targets":
        deleted_targets,

    "already_absent_targets":
        already_absent_targets,

    "remaining_targets":
        remaining_targets,

    "target_inventory_after":
        target_inventory_after,

    "protected_paths_unchanged":
        protected_unchanged,

    "source_files_modified":
        False,

    "runtime_state_modified":
        False,

    "wuc_executed":
        False,

    "uucd_rebuild_executed":
        False,

    "body_store_rebuild_executed":
        False,

    "failures":
        failures,
}

write_json(
    REPORT_PATH,
    report,
)


print(
    "Legacy UUCD existed before reset:        "
    + str(
        target_inventory_before[
            "legacy_uucd"
        ][
            "exists"
        ]
    )
)

print(
    "Legacy UUCD files backed up:             "
    + str(
        backup_inventory.get(
            "legacy_uucd",
            {},
        ).get(
            "backup_file_count",
            0,
        )
    )
)

print(
    "Legacy Body Store existed before reset:  "
    + str(
        target_inventory_before[
            "legacy_universal_article_body_store"
        ][
            "exists"
        ]
    )
)

print(
    "Legacy Body Store files backed up:       "
    + str(
        backup_inventory.get(
            "legacy_universal_article_body_store",
            {},
        ).get(
            "backup_file_count",
            0,
        )
    )
)

print(
    "Legacy UUCD directory exists now:        "
    + str(
        LEGACY_UUCD_ROOT.exists()
    )
)

print(
    "Legacy Body Store exists now:            "
    + str(
        LEGACY_BODY_STORE_ROOT.exists()
    )
)

print(
    "Remaining deletion targets:              "
    + str(
        len(
            remaining_targets
        )
    )
)

print()
print(
    "PROTECTED REBUILD SOURCES"
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
    "WUC executed:                 False"
)

print(
    "UUCD rebuild executed:        False"
)

print(
    "Body Store rebuild executed:  False"
)

print(
    "Runtime state modified:       False"
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
        "LEGACY UUCD AND BODY STORE RESET: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 108)

    raise SystemExit(1)

print(
    "LEGACY UUCD AND BODY STORE RESET: PASS"
)

print(
    "The legacy UUCD documents and Universal Article Body Store "
    "outputs were backed up, verified and deleted."
)

print(
    "All authoritative website, upload, WUC and runtime rebuild "
    "sources remain unchanged."
)

print("=" * 108)
