"""Retire the incompatible legacy Universal Article Body Store writer."""

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
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\legacy_universal_article_body_store_retirement_20260727_002057"
).resolve()

LEGACY_BODY_STORE_CODE = (
    SERVER_ROOT
    / "stores"
    / "universal_article_body_store.py"
)

BODY_STORE_OUTPUT = (
    DATA_ROOT
    / "universal_article_body_store"
)

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "legacy_universal_article_body_store_retirement_v1.json"
)

PROTECTED_PATHS = {
    "fresh_uucd_package": (
        SERVER_ROOT
        / "universal_unified_content_document"
    ),

    "wuc_package": (
        SERVER_ROOT
        / "website_unified_content"
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

    "uploaded_document_unified_content": (
        SERVER_ROOT
        / "stores"
        / "uploaded_document_unified_content.py"
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
    "backend.server.stores.universal_article_body_store",
    "stores.universal_article_body_store",
    "universal_article_body_store import",
    "build_universal_article_body_store_from_uucd_payload_v2",
    "build_universal_article_body_store_from_uucd_file_v2",
    "write_universal_article_body",
    "save_universal_article_body",
    "persist_universal_article_body",
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
    "LEGACY UNIVERSAL ARTICLE BODY STORE — CONTROLLED RETIREMENT"
)
print("=" * 112)
print()

failures: list[str] = []

if not LEGACY_BODY_STORE_CODE.is_file():
    failures.append(
        "Legacy Body Store implementation is missing before retirement: "
        + str(
            LEGACY_BODY_STORE_CODE
        )
    )

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

if BODY_STORE_OUTPUT.exists():
    failures.append(
        "Body Store output directory unexpectedly exists. "
        "This retirement step expects no persisted Body Store data."
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

source_hash = sha256_file(
    LEGACY_BODY_STORE_CODE
)

backup_path = backup_file(
    LEGACY_BODY_STORE_CODE
)

backup_hash = sha256_file(
    backup_path
)

if source_hash != backup_hash:
    failures.append(
        "Legacy Body Store backup hash mismatch."
    )

if not failures:
    LEGACY_BODY_STORE_CODE.unlink()


legacy_code_still_exists = (
    LEGACY_BODY_STORE_CODE.exists()
)

if legacy_code_still_exists:
    failures.append(
        "Legacy Body Store implementation still exists after retirement."
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
            if term.casefold()
            in lowered
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
        "legacy_universal_article_body_store_retirement_v1",

    "workspace_id":
        WORKSPACE_ID,

    "retirement_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "retired_file": {
        "original_path":
            relative(
                LEGACY_BODY_STORE_CODE
            ),

        "backup_path":
            str(
                backup_path
            ),

        "sha256":
            source_hash,

        "backup_verified":
            source_hash
            == backup_hash,

        "original_exists_after_retirement":
            legacy_code_still_exists,
    },

    "protected_components_unchanged":
        protected_unchanged,

    "remaining_reference_file_count":
        len(
            remaining_references
        ),

    "remaining_references":
        remaining_references,

    "body_store_output_exists":
        BODY_STORE_OUTPUT.exists(),

    "fresh_body_store_writer_created":
        False,

    "body_store_data_written":
        False,

    "fresh_uucd_modified":
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
    "Legacy Body Store code retired:         "
    + str(
        not legacy_code_still_exists
    )
)

print(
    "Backup verified:                        "
    + str(
        source_hash
        == backup_hash
    )
)

print(
    "Remaining active reference files:       "
    + str(
        len(
            remaining_references
        )
    )
)

print(
    "Body Store output currently exists:     "
    + str(
        BODY_STORE_OUTPUT.exists()
    )
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
    "Fresh Body Store writer created: False"
)

print(
    "Body Store data written:         False"
)

print(
    "Fresh UUCD modified:              False"
)

print(
    "Runtime state modified:           False"
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
        "LEGACY UNIVERSAL ARTICLE BODY STORE RETIREMENT: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 112)

    raise SystemExit(1)

print(
    "LEGACY UNIVERSAL ARTICLE BODY STORE RETIREMENT: PASS"
)

print(
    "The incompatible Body Store implementation was backed up and retired."
)

if remaining_references:
    print(
        "Remaining active references were detected and must be cleaned "
        "before the fresh Body Store writer is created."
    )

else:
    print(
        "No active server-side references to the retired Body Store "
        "implementation remain."
    )

print("=" * 112)
