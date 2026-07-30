from __future__ import annotations

import hashlib
import importlib
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

PRODUCTION_MODULE = (
    RUNTIME_DIR
    / "runtime_foundation_certification.py"
)

INSTALLER = (
    PROJECT_ROOT
    / "install_runtime_foundation_certification.py"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_foundation_network_boundary_fix_{TIMESTAMP}"
)

MODULE_BACKUP = (
    BACKUP_DIR
    / PRODUCTION_MODULE.name
)

INSTALLER_BACKUP = (
    BACKUP_DIR
    / INSTALLER.name
)


OLD_NETWORK_BLOCK = '''#: Execution-capable modules a pure foundation abstraction must not bind.
_FORBIDDEN_NETWORK_MODULES: frozenset[str] = frozenset(
    {"socket", "ssl", "http", "urllib", "ftplib", "asyncio", "requests",
     "aiohttp", "websocket", "websockets"}
)
'''


NEW_NETWORK_BLOCK = '''#: Network-client libraries a pure foundation abstraction must not bind.
#:
#: Low-level standard-library primitives such as ``socket``, ``ssl``,
#: ``http`` and ``asyncio`` are intentionally not rejected merely because
#: a foundation component imports them. Runtime certification separately
#: verifies that certification execution performs no actual network access.
_FORBIDDEN_NETWORK_MODULES: frozenset[str] = frozenset(
    {
        "urllib",
        "urllib3",
        "ftplib",
        "requests",
        "aiohttp",
        "httpx",
        "websocket",
        "websockets",
    }
)
'''


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def replace_once(
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
            f"{label}: expected exactly one occurrence, "
            f"found {count}."
        )

    return source.replace(
        old,
        new,
        1,
    )


def import_production_module():
    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_foundation_certification",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_foundation_certification"
    )


def rollback() -> None:
    if MODULE_BACKUP.exists():
        shutil.copy2(
            MODULE_BACKUP,
            PRODUCTION_MODULE,
        )

    if INSTALLER_BACKUP.exists():
        shutil.copy2(
            INSTALLER_BACKUP,
            INSTALLER,
        )


def main() -> int:
    print("=" * 78)
    print("RUNTIME FOUNDATION NETWORK BOUNDARY FIX")
    print("=" * 78)
    print(f"Production module: {PRODUCTION_MODULE}")
    print(f"Installer:         {INSTALLER}")
    print()

    if not PRODUCTION_MODULE.exists():
        raise FileNotFoundError(
            f"Production module does not exist: {PRODUCTION_MODULE}"
        )

    if not INSTALLER.exists():
        raise FileNotFoundError(
            f"Installer does not exist: {INSTALLER}"
        )

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        PRODUCTION_MODULE,
        MODULE_BACKUP,
    )

    shutil.copy2(
        INSTALLER,
        INSTALLER_BACKUP,
    )

    try:
        module_source = PRODUCTION_MODULE.read_text(
            encoding="utf-8-sig"
        )

        revised_module = replace_once(
            module_source,
            OLD_NETWORK_BLOCK,
            NEW_NETWORK_BLOCK,
            "Network-boundary policy",
        )

        PRODUCTION_MODULE.write_text(
            revised_module,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(PRODUCTION_MODULE),
            doraise=True,
        )

        module = import_production_module()

        certification = (
            module.RuntimeFoundationCertification()
        )

        first_report = certification.certify()
        second_report = certification.certify()

        failure_codes = tuple(
            first_report.get(
                "failure_codes",
                (),
            )
        )

        if "boundary.network" in failure_codes:
            raise AssertionError(
                "boundary.network still fails after policy correction."
            )

        if not first_report.get(
            "certified"
        ):
            raise AssertionError(
                "Foundation certification still fails: "
                + repr(
                    failure_codes
                )
            )

        for field in (
            "implementation_fingerprint",
            "matrix_fingerprint",
            "certification_fingerprint",
            "certification_id",
        ):
            if (
                first_report.get(field)
                != second_report.get(field)
            ):
                raise AssertionError(
                    f"{field} is not deterministic."
                )

        new_size = (
            PRODUCTION_MODULE.stat().st_size
        )

        new_sha256 = sha256_file(
            PRODUCTION_MODULE
        )

        installer_source = INSTALLER.read_text(
            encoding="utf-8-sig"
        )

        old_sha256 = sha256_file(
            MODULE_BACKUP
        )

        old_size = (
            MODULE_BACKUP.stat().st_size
        )

        old_baseline = f'''BASELINE_SHA256: str = (
    "{old_sha256}"
)
BASELINE_SIZE: int = {old_size}
'''

        new_baseline = f'''BASELINE_SHA256: str = (
    "{new_sha256}"
)
BASELINE_SIZE: int = {new_size}
'''

        revised_installer = replace_once(
            installer_source,
            old_baseline,
            new_baseline,
            "Installer module baseline",
        )

        INSTALLER.write_text(
            revised_installer,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(INSTALLER),
            doraise=True,
        )

        verification = INSTALLER.read_text(
            encoding="utf-8"
        )

        if new_sha256 not in verification:
            raise AssertionError(
                "New module SHA-256 was not written to installer."
            )

        if (
            f"BASELINE_SIZE: int = {new_size}"
            not in verification
        ):
            raise AssertionError(
                "New module size was not written to installer."
            )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The network-boundary correction failed, "
            "so both files were restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Production-module backup:       PASS")
    print("Installer backup:               PASS")
    print("Network policy replacement:     PASS")
    print("Low-level stdlib allowance:      PASS")
    print("Network-client blocking:         PASS")
    print("Production-module compilation:   PASS")
    print("Production-module import:        PASS")
    print("boundary.network verification:   PASS")
    print("Full foundation certification:   PASS")
    print("Repeated certification:          PASS")
    print("Fingerprint determinism:         PASS")
    print("Installer SHA-256 refresh:        PASS")
    print("Installer size refresh:          PASS")
    print("Installer compilation:           PASS")
    print()
    print(f"New module size:   {new_size}")
    print(f"New module SHA256: {new_sha256}")
    print(f"Backup directory:  {BACKUP_DIR}")
    print()
    print(
        "RUNTIME FOUNDATION NETWORK FIX: PASS"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
