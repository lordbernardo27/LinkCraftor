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
    / f"diff_engine_target_nullable_fix_{TIMESTAMP}"
    / TARGET.name
)


OLD_BLOCK = '''                "nullable_value": {
                    "type": "string",
                    "nullable": True,
                },
'''


NEW_BLOCK = '''                "nullable_value": {
                    "type": "string",
                    "nullable": False,
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
    print("DIFF ENGINE TARGET NULLABILITY FIX")
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

    occurrence_count = original.count(
        OLD_BLOCK
    )

    if occurrence_count != 1:
        raise RuntimeError(
            "Expected exactly one target nullable-value fixture, "
            f"but found {occurrence_count}. No file was modified."
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
                "Old target nullability fixture still exists."
            )

        if verification_text.count(
            NEW_BLOCK
        ) != 1:
            raise AssertionError(
                "Corrected target nullability fixture "
                "was not installed exactly once."
            )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The repair failed, so the original installer "
            "was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Backup creation:                PASS")
    print("Exact fixture detection:        PASS")
    print("Target nullability repair:      PASS")
    print("Installer compilation:          PASS")
    print("Post-write verification:        PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print("DIFF ENGINE TARGET FIX: PASS")
    print("NO PRODUCTION MODULE WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
