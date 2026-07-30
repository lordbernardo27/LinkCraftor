from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()

TARGET = PROJECT_ROOT / "install_runtime_schema_registry.py"

TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"registry_transaction_snapshot_fix_{TIMESTAMP}"
    / TARGET.name
)

OLD1 = """            "ownership_subject_history": copy.deepcopy(
                getattr(
                    self._ownership,
                    "_subject_history",
                    {},
                )
            ),
"""

NEW1 = """            "ownership_subject_history": {
                key: list(value)
                for key, value in getattr(
                    self._ownership,
                    "_subject_history",
                    {},
                ).items()
            },
"""

OLD2 = """            "ownership_owner_subjects": copy.deepcopy(
                getattr(
                    self._ownership,
                    "_owner_subjects",
                    {},
                )
            ),
"""

NEW2 = """            "ownership_owner_subjects": {
                key: set(value)
                for key, value in getattr(
                    self._ownership,
                    "_owner_subjects",
                    {},
                ).items()
            },
"""

OLD3 = """            "audit_subject_index": copy.deepcopy(
                self._audit._subject_index
            ),
"""

NEW3 = """            "audit_subject_index": {
                key: list(value)
                for key, value in self._audit._subject_index.items()
            },
"""

def rollback():
    if BACKUP.exists():
        shutil.copy2(BACKUP, TARGET)

def replace_once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one occurrence, found {count}.")
    return text.replace(old, new, 1)

def main():
    print("=" * 78)
    print("REGISTRY TRANSACTION SNAPSHOT FIX")
    print("=" * 78)

    source = TARGET.read_text(encoding="utf-8-sig")

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TARGET, BACKUP)

    try:
        source = replace_once(source, OLD1, NEW1)
        source = replace_once(source, OLD2, NEW2)
        source = replace_once(source, OLD3, NEW3)

        TARGET.write_text(
            source,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(str(TARGET), doraise=True)

    except Exception:
        rollback()
        print("ROLLBACK COMPLETE")
        print(traceback.format_exc())
        return 1

    print("Snapshot serialization: PASS")
    print("Compilation: PASS")
    print()
    print(f"Backup: {BACKUP}")
    print()
    print("TRANSACTION SNAPSHOT FIX: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
