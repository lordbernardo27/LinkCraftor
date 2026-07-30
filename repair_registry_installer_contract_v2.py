from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "install_runtime_schema_registry.py"
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
    / f"registry_installer_v2_contract_fix_{TIMESTAMP}"
    / TARGET.name
)


OLD = """            namespace_record = (
                self._namespaces
                .authorize_schema_namespace(
                    schema.namespace,
                    runtime_actor=(
                        runtime_actor
                    ),
                )
            )
"""


NEW = """            namespace_record = (
                self._namespaces
                .authorize_schema_namespace(
                    schema.namespace,
                    actor_id=actor,
                    runtime_actor=(
                        runtime_actor
                    ),
                )
            )
"""


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:

    print("=" * 78)
    print("REGISTRY INSTALLER CONTRACT FIX V2")
    print("=" * 78)
    print()

    if not TARGET.exists():
        raise FileNotFoundError(TARGET)

    source = TARGET.read_text(
        encoding="utf-8-sig"
    )

    count = source.count(OLD)

    if count != 1:
        raise RuntimeError(
            f"Expected one occurrence, found {count}."
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

        repaired = source.replace(
            OLD,
            NEW,
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

    except Exception:

        rollback()

        print("ROLLBACK COMPLETE")
        print(traceback.format_exc())

        return 1

    print("Backup:                 PASS")
    print("Contract repair:        PASS")
    print("Compilation:            PASS")
    print()
    print(f"Backup: {BACKUP}")
    print()
    print("REGISTRY INSTALLER PATCH V2: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
