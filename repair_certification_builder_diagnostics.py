from __future__ import annotations

import py_compile
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "install_runtime_schema_certification.py"
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
    / f"certification_builder_diagnostics_{TIMESTAMP}"
    / TARGET.name
)


OLD_BLOCK = '''            except Exception as exc:
                checks = (
                    CertificationCheck(
                        check_id=(
                            section_name
                            .lower()
                            + ".builder"
                        ),
                        section=section_name,
                        requirement=(
                            "section builder must complete"
                        ),
                        status=(
                            CertificationStatus.FAIL
                        ),
                        detail=(
                            f"{type(exc).__name__}: {exc}"
                        ),
                    ),
                )
'''


NEW_BLOCK = '''            except Exception as exc:
                import traceback

                print("=" * 78)
                print(
                    "CERTIFICATION SECTION "
                    f"BUILDER FAILURE: {section_name}"
                )
                print("=" * 78)
                traceback.print_exc()
                print("=" * 78)

                checks = (
                    CertificationCheck(
                        check_id=(
                            section_name
                            .lower()
                            + ".builder"
                        ),
                        section=section_name,
                        requirement=(
                            "section builder must complete"
                        ),
                        status=(
                            CertificationStatus.FAIL
                        ),
                        detail=(
                            f"{type(exc).__name__}: {exc}"
                        ),
                    ),
                )
'''


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:
    print("=" * 78)
    print("CERTIFICATION INSTALLER DIAGNOSTIC PATCH")
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
            "Expected exactly one certification "
            "section-builder exception block, "
            f"but found {occurrence_count}. "
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

        verification = TARGET.read_text(
            encoding="utf-8"
        )

        if (
            "CERTIFICATION SECTION "
            not in verification
        ):
            raise AssertionError(
                "Diagnostic block was not installed."
            )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The diagnostic patch failed, so the "
            "original installer was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Backup creation:               PASS")
    print("Exact block detection:          PASS")
    print("Diagnostic output insertion:   PASS")
    print("Installer compilation:         PASS")
    print("Post-write verification:       PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print(
        "CERTIFICATION DIAGNOSTIC PATCH: PASS"
    )
    print(
        "NO PRODUCTION MODULE WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
