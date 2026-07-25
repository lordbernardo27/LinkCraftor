from __future__ import annotations

import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "build_uri_phase_1_1_9_runtime_compatibility.py"
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
    / f"uri_phase1_1_9_builder_import_fix_{TIMESTAMP}"
    / TARGET.name
)


OLD_BLOCK = '''        compatibility_module = import_runtime_module(
            compatibility_module_name
        )

        versioning_module = import_runtime_module(
            versioning_module_name
        )

        kernel_module = import_runtime_module(
            kernel_module_name
        )

        registry_module = import_runtime_module(
            registry_module_name
        )
'''


NEW_BLOCK = '''        # Load dependencies before runtime_compatibility.
        #
        # runtime_compatibility imports RuntimeVersionManifest from the
        # canonical runtime_versioning module. Reloading runtime_versioning
        # after compatibility has imported it creates a second Python class
        # identity and causes valid manifests to fail isinstance checks.
        versioning_module = import_runtime_module(
            versioning_module_name
        )

        kernel_module = import_runtime_module(
            kernel_module_name
        )

        registry_module = import_runtime_module(
            registry_module_name
        )

        compatibility_module = import_runtime_module(
            compatibility_module_name
        )
'''


def main() -> int:
    print("=" * 78)
    print("URI 1.1.9 VERIFICATION HARNESS IMPORT-ORDER REPAIR")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Builder script does not exist: {TARGET}"
        )

    original = TARGET.read_text(
        encoding="utf-8-sig"
    )

    occurrence_count = original.count(
        OLD_BLOCK
    )

    if occurrence_count != 1:
        raise RuntimeError(
            "Expected exactly one old module-import block, "
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

    try:
        py_compile.compile(
            str(TARGET),
            doraise=True,
        )
    except Exception:
        shutil.copy2(
            BACKUP,
            TARGET,
        )

        print("ROLLBACK COMPLETE")
        print(
            "The builder repair failed verification, "
            "so the original builder was restored."
        )
        raise

    print("Import order repaired: PASS")
    print("Builder compilation:    PASS")
    print()
    print(f"Backup: {BACKUP}")
    print()
    print(
        "No Universal Runtime production module "
        "was modified by this repair."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
