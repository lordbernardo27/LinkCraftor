from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "scan_uri_phase_1_1_15_runtime_foundation.py"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime("%Y%m%dT%H%M%SZ")

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_foundation_scan_filename_fix_{TIMESTAMP}"
    / TARGET.name
)


REPLACEMENTS = [
    (
        '"runtime_kernel.py"',
        '"universal_runtime_kernel.py"',
    ),
    (
        '"runtime_lifecycle.py"',
        '"runtime_lifecycle_manager.py"',
    ),
    (
        '"runtime_boot.py"',
        '"runtime_boot_process.py"',
    ),
    (
        '"runtime_shutdown.py"',
        '"runtime_shutdown_process.py"',
    ),
]


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:

    print("=" * 78)
    print("RUNTIME FOUNDATION SCAN FILENAME FIX")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Scan script does not exist: {TARGET}"
        )

    source = TARGET.read_text(
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

        for old, new in REPLACEMENTS:

            count = source.count(old)

            if count != 1:
                raise RuntimeError(
                    f"Expected exactly one occurrence of {old}, "
                    f"found {count}."
                )

            source = source.replace(
                old,
                new,
                1,
            )

        TARGET.write_text(
            source,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        verification = TARGET.read_text(
            encoding="utf-8"
        )

        for _, new in REPLACEMENTS:

            if new not in verification:
                raise AssertionError(
                    f"Verification failed for {new}"
                )

    except Exception:

        rollback()

        print("ROLLBACK COMPLETE")
        print(traceback.format_exc())

        return 1

    print("Backup creation:            PASS")
    print("Kernel filename fix:        PASS")
    print("Lifecycle filename fix:     PASS")
    print("Boot filename fix:          PASS")
    print("Shutdown filename fix:      PASS")
    print("Compilation:               PASS")
    print()
    print(f"Backup: {BACKUP}")
    print()
    print("RUNTIME FOUNDATION SCAN PATCH: PASS")
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
