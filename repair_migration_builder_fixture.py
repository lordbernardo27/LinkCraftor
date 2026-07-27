from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "install_runtime_schema_migration.py"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"migration_builder_fixture_fix_{TIMESTAMP}"
    / TARGET.name
)


OLD_SOURCE_FIELDS = '''            "fields": {
                "identifier": {
                    "type": "integer",
                    "required": False,
                    "nullable": True,
                    "default": 1,
                    "description": "Old field.",
                    "constraints": {
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
                "removed": {
                    "type": "string",
                },
            }
'''


NEW_SOURCE_FIELDS = '''            "fields": {
                "type_change": {
                    "type": "integer",
                },
                "required_change": {
                    "type": "string",
                    "required": False,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": True,
                },
                "constraint_change": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "old",
                },
                "description_change": {
                    "type": "string",
                    "description": "Old field.",
                },
                "removed": {
                    "type": "string",
                },
            }
'''


OLD_TARGET_FIELDS = '''            "fields": {
                "identifier": {
                    "type": "number",
                    "required": True,
                    "nullable": False,
                    "description": "New field.",
                    "constraints": {
                        "minimum": 10,
                        "maximum": 90,
                    },
                },
                "added": {
                    "type": "string",
                    "required": True,
                    "default": "backfill",
                },
            }
'''


NEW_TARGET_FIELDS = '''            "fields": {
                "type_change": {
                    "type": "number",
                },
                "required_change": {
                    "type": "string",
                    "required": True,
                },
                "nullable_change": {
                    "type": "string",
                    "nullable": False,
                },
                "constraint_change": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 10,
                        "maximum": 90,
                    },
                },
                "default_change": {
                    "type": "string",
                    "default": "new",
                },
                "description_change": {
                    "type": "string",
                    "description": "New field.",
                },
                "added": {
                    "type": "string",
                    "required": True,
                    "default": "backfill",
                },
            }
'''


def replace_exactly_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    count = source.count(
        old
    )

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, "
            f"found {count}. No file was modified."
        )

    return source.replace(
        old,
        new,
        1,
    )


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:
    print("=" * 78)
    print("MIGRATION BUILDER VERIFICATION-FIXTURE REPAIR")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Installer does not exist: {TARGET}"
        )

    original = TARGET.read_text(
        encoding="utf-8-sig"
    )

    BACKUP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET,
        BACKUP,
    )

    try:
        repaired = replace_exactly_once(
            original,
            OLD_SOURCE_FIELDS,
            NEW_SOURCE_FIELDS,
            "Source fixture replacement",
        )

        repaired = replace_exactly_once(
            repaired,
            OLD_TARGET_FIELDS,
            NEW_TARGET_FIELDS,
            "Target fixture replacement",
        )

        TARGET.write_text(
            repaired,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        verification_text = TARGET.read_text(
            encoding="utf-8"
        )

        if OLD_SOURCE_FIELDS in verification_text:
            raise AssertionError(
                "Old source fixture remains."
            )

        if OLD_TARGET_FIELDS in verification_text:
            raise AssertionError(
                "Old target fixture remains."
            )

        if verification_text.count(
            NEW_SOURCE_FIELDS
        ) != 1:
            raise AssertionError(
                "New source fixture was not installed exactly once."
            )

        if verification_text.count(
            NEW_TARGET_FIELDS
        ) != 1:
            raise AssertionError(
                "New target fixture was not installed exactly once."
            )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The fixture repair failed, so the original "
            "installer was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Backup creation:                PASS")
    print("Source fixture replacement:     PASS")
    print("Target fixture replacement:     PASS")
    print("Independent operation coverage: PASS")
    print("Installer compilation:          PASS")
    print("Post-write verification:        PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print("MIGRATION BUILDER FIX: PASS")
    print("NO PRODUCTION MODULE WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
