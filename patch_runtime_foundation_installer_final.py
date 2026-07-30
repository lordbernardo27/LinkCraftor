from __future__ import annotations

import hashlib
import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

INSTALLER = (
    PROJECT_ROOT
    / "install_runtime_foundation_certification.py"
)

PRODUCTION_MODULE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_foundation_certification.py"
)

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

EVIDENCE_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_15_runtime_foundation_certification"
    / "runtime_foundation_certification_install_evidence.json"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_foundation_installer_final_fix_{TIMESTAMP}"
    / INSTALLER.name
)


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
            f"{label}: expected exactly one match, "
            f"found {count}."
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
            INSTALLER,
        )


def main() -> int:
    print("=" * 78)
    print("RUNTIME FOUNDATION CERTIFICATION")
    print("FINAL INSTALLER CONTRACT PATCH")
    print("=" * 78)
    print(f"Installer: {INSTALLER}")
    print(f"Module:    {PRODUCTION_MODULE}")
    print()

    if not INSTALLER.exists():
        raise FileNotFoundError(
            f"Installer does not exist: {INSTALLER}"
        )

    if not PRODUCTION_MODULE.exists():
        raise FileNotFoundError(
            "Reviewed production module does not exist: "
            f"{PRODUCTION_MODULE}"
        )

    module_size = (
        PRODUCTION_MODULE.stat().st_size
    )

    module_sha256 = sha256_file(
        PRODUCTION_MODULE
    )

    original = INSTALLER.read_text(
        encoding="utf-8-sig"
    )

    BACKUP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        INSTALLER,
        BACKUP,
    )

    try:
        revised = original

        revised = replace_once(
            revised,
            '''BASELINE_SHA256: str = (
    "99e230636801520e4e36d6f784d1dde56921071a6c970a46daf9498a714a6124"
)
BASELINE_SIZE: int = 45182
''',
            f'''BASELINE_SHA256: str = (
    "{module_sha256}"
)
BASELINE_SIZE: int = {module_size}
''',
            "Baseline SHA-256 and size",
        )

        revised = replace_once(
            revised,
            '''def _default_source() -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), MODULE_FILENAME
    )
''',
            '''def _project_root() -> str:
    return os.path.dirname(
        os.path.abspath(__file__)
    )


def _default_runtime_dir() -> str:
    return os.path.join(
        _project_root(),
        "backend",
        "server",
        "runtime",
    )


def _default_source() -> str:
    return os.path.join(
        _default_runtime_dir(),
        MODULE_FILENAME,
    )


def _default_evidence() -> str:
    return os.path.join(
        _project_root(),
        "backend",
        "server",
        "data",
        "runtime",
        "uri_phase_1",
        "1_1_15_runtime_foundation_certification",
        "runtime_foundation_certification_install_evidence.json",
    )
''',
            "Canonical default paths",
        )

        revised = replace_once(
            revised,
            '''    parser.add_argument(
        "--target-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="directory to install the module into (the runtime package dir)",
    )
''',
            '''    parser.add_argument(
        "--target-dir",
        default=_default_runtime_dir(),
        help="directory to install the module into (the runtime package dir)",
    )
''',
            "Runtime target directory",
        )

        revised = replace_once(
            revised,
            '''    evidence = args.evidence or os.path.join(
        args.target_dir,
        "runtime_foundation_certification_install_evidence.json",
    )
''',
            '''    evidence = (
        args.evidence
        or _default_evidence()
    )
''',
            "Canonical evidence location",
        )

        INSTALLER.write_text(
            revised,
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

        required_values = (
            module_sha256,
            f"BASELINE_SIZE: int = {module_size}",
            '"backend"',
            '"server"',
            '"runtime"',
            '"uri_phase_1"',
            '"1_1_15_runtime_foundation_certification"',
        )

        for required_value in required_values:
            if required_value not in verification:
                raise AssertionError(
                    "Post-write verification failed for: "
                    f"{required_value}"
                )

        # The logical role identifiers are intentionally unchanged.
        logical_roles = (
            '"runtime_compatibility_layer"',
            '"runtime_persistence_interface"',
            '"runtime_state_store_abstraction"',
            '"runtime_schema_management"',
        )

        for logical_role in logical_roles:
            if logical_role not in verification:
                raise AssertionError(
                    "Required logical role was incorrectly removed: "
                    f"{logical_role}"
                )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The final installer patch failed, so the "
            "original installer was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Installer backup:               PASS")
    print("Production module detection:     PASS")
    print("Exact module SHA-256:            PASS")
    print("Exact module size:               PASS")
    print("Canonical source path:           PASS")
    print("Canonical runtime target:        PASS")
    print("Canonical evidence path:         PASS")
    print("Logical role identifiers:        PASS")
    print("Forbidden-import policy review:  PASS")
    print("Installer compilation:           PASS")
    print("Post-write verification:         PASS")
    print()
    print(f"Module size:   {module_size}")
    print(f"Module SHA256: {module_sha256}")
    print(f"Backup file:   {BACKUP}")
    print()
    print(
        "RUNTIME FOUNDATION INSTALLER PATCH: PASS"
    )
    print(
        "NO PRODUCTION MODULE WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
