from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "install_runtime_schema_diff_engine.py"
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
    / f"diff_engine_builder_fixture_fix_{TIMESTAMP}"
    / TARGET.name
)


OLD_BLOCK = '''                "nullable_value": {
                    "type": "string",
                    "nullable": False,
                    "default": None,
                },
'''


NEW_BLOCK = '''                "nullable_value": {
                    "type": "string",
                    "nullable": True,
                    "default": None,
                },
'''


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:
    print("=" * 78)
    print("DIFF ENGINE BUILDER TEST-FIXTURE REPAIR")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Builder does not exist: {TARGET}"
        )

    original = TARGET.read_text(
        encoding="utf-8-sig"
    )

    occurrence_count = original.count(
        OLD_BLOCK
    )

    if occurrence_count != 1:
        raise RuntimeError(
            "Expected exactly one invalid nullable-value "
            f"test fixture, but found {occurrence_count}. "
            "No file was modified."
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
        repaired = original.replace(
            OLD_BLOCK,
            NEW_BLOCK,
            1,
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

        if OLD_BLOCK in verification_text:
            raise AssertionError(
                "Invalid test fixture still exists."
            )

        if verification_text.count(
            NEW_BLOCK
        ) != 1:
            raise AssertionError(
                "Corrected test fixture was not installed exactly once."
            )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The builder repair failed, so the original "
            "installer was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Backup creation:                PASS")
    print("Exact fixture detection:        PASS")
    print("Invalid fixture replacement:    PASS")
    print("Builder compilation:            PASS")
    print("Post-write verification:        PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print("DIFF ENGINE BUILDER FIX: PASS")
    print("NO PRODUCTION MODULE WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
