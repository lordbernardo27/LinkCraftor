from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_REPOSITORY_HASH = "75a50ab18baec03cecd6bbc932c5a7896bfad646d2a78158f5f0d7137d9bb558"
EXPECTED_CHECKER_HASH = "ed8ac237360ea6d6b9c59e1d6307e9e8ca9a60b6de6f32ff06981b4adbd36a1c"


HELPER_SOURCE = '''

_ATOMIC_REPLACE_MAX_ATTEMPTS = 20


def _atomic_replace_with_windows_retry(
    source: Path,
    target: Path,
) -> None:
    """Atomically replace target, tolerating transient Windows file locks."""
    for attempt in range(
        _ATOMIC_REPLACE_MAX_ATTEMPTS
    ):
        try:
            os.replace(
                source,
                target,
            )
            return
        except PermissionError:
            if (
                os.name != "nt"
                or attempt + 1
                >= _ATOMIC_REPLACE_MAX_ATTEMPTS
            ):
                raise

            time.sleep(
                min(
                    0.05 * (attempt + 1),
                    0.25,
                )
            )
'''


OLD_REPLACE = '''                os.replace(
                    temporary,
                    target,
                )'''


NEW_REPLACE = '''                _atomic_replace_with_windows_retry(
                    temporary,
                    target,
                )'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    repository = root / "backend/server/coordination/workflow_persistence/repository.py"
    checker = root / "_part_e_14_b_controlled_end_to_end_certification.py"
    failed_report = report
    checks = {
        "failed_14_b_report_exists": False,
        "windows_lock_failure_confirmed": False,
        "repository_precondition_hash": False,
        "checker_precondition_hash": False,
        "patch_not_previously_present": False,
        "candidate_repository_syntax": False,
        "candidate_checker_syntax": False,
        "repository_backup_created": False,
        "checker_backup_created": False,
        "bounded_windows_retry_added": False,
        "canonical_atomic_replace_retained": False,
        "corrected_14_b_certified": False,
        "failed_checks_empty": False,
        "not_run_checks_empty": False,
        "production_patch_retained": False,
    }
    evidence: dict[str, object] = {}
    error: dict[str, object] = {}
    backup_root: Path | None = None
    repository_original: bytes | None = None
    checker_original: bytes | None = None
    retained = False

    try:
        for required in (repository, checker):
            if not required.is_file():
                raise RuntimeError("Required file unavailable: " + str(required))

        checks["failed_14_b_report_exists"] = failed_report.is_file()
        if not checks["failed_14_b_report_exists"]:
            raise RuntimeError("The failed Part E 14-B report is unavailable.")
        failed_text = normalized(failed_report)
        checks["windows_lock_failure_confirmed"] = all(
            token in failed_text
            for token in (
                "CERTIFICATION STATUS: NOT_CERTIFIED",
                "PermissionError",
                "WinError 32",
                "workflow_persistence\\\\repository.py",
                "os.replace",
                "FINAL RESULT: PART E STEP 14 NOT_CERTIFIED",
            )
        )
        if not checks["windows_lock_failure_confirmed"]:
            raise RuntimeError("The expected Windows atomic-replace failure was not confirmed.")

        checks["repository_precondition_hash"] = sha256(repository) == EXPECTED_REPOSITORY_HASH
        checks["checker_precondition_hash"] = sha256(checker) == EXPECTED_CHECKER_HASH
        if not checks["repository_precondition_hash"] or not checks["checker_precondition_hash"]:
            raise RuntimeError("Repository or checker changed after the failed 14-B run.")

        repository_source = normalized(repository)
        checker_source = normalized(checker)
        checks["patch_not_previously_present"] = (
            "_atomic_replace_with_windows_retry" not in repository_source
            and OLD_REPLACE in repository_source
        )
        if not checks["patch_not_previously_present"]:
            raise RuntimeError("The Windows atomic-replace patch is already present or the anchor changed.")
        if repository_source.count("import tempfile\n") != 1:
            raise RuntimeError("The repository import anchor is not unique.")
        if repository_source.count("class WorkflowRepository:") != 1:
            raise RuntimeError("The WorkflowRepository class anchor is not unique.")
        if repository_source.count(OLD_REPLACE) != 1:
            raise RuntimeError("The canonical os.replace block is not unique.")

        repository_candidate = repository_source.replace(
            "import tempfile\n",
            "import tempfile\nimport time\n",
            1,
        ).replace(
            "class WorkflowRepository:",
            HELPER_SOURCE + "\n\nclass WorkflowRepository:",
            1,
        ).replace(
            OLD_REPLACE,
            NEW_REPLACE,
            1,
        )
        ast.parse(repository_candidate, filename=str(repository))
        checks["candidate_repository_syntax"] = True
        candidate_hash = hashlib.sha256(repository_candidate.encode("utf-8")).hexdigest()

        old_key = '"production_source_lineage_matches_14_a"'
        new_key = '"production_source_lineage_matches_14_a_with_certified_repository_fix"'
        if checker_source.count(EXPECTED_REPOSITORY_HASH) != 1:
            raise RuntimeError("The checker repository-hash anchor is not unique.")
        if checker_source.count(old_key) < 2:
            raise RuntimeError("The checker lineage-key anchors are incomplete.")
        old_header = '"Production source changes: NONE",'
        new_header = '"Production source changes: CERTIFIED WINDOWS ATOMIC-REPLACE COMPATIBILITY FIX",'
        if checker_source.count(old_header) != 1:
            raise RuntimeError("The checker report-header anchor is not unique.")
        checker_candidate = checker_source.replace(
            EXPECTED_REPOSITORY_HASH,
            candidate_hash,
            1,
        ).replace(
            old_key,
            new_key,
        ).replace(
            old_header,
            new_header,
            1,
        )
        ast.parse(checker_candidate, filename=str(checker))
        checks["candidate_checker_syntax"] = True

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_root = root / "backend/server/data/runtime_backups" / ("part_e_14_b_windows_atomic_fix_" + stamp)
        backup_root.mkdir(parents=True, exist_ok=False)
        repository_backup = backup_root / "repository.py"
        checker_backup = backup_root / checker.name
        shutil.copy2(repository, repository_backup)
        shutil.copy2(checker, checker_backup)
        checks["repository_backup_created"] = repository_backup.is_file()
        checks["checker_backup_created"] = checker_backup.is_file()

        repository_original = repository.read_bytes()
        checker_original = checker.read_bytes()
        write_text(repository, repository_candidate)
        write_text(checker, checker_candidate)
        py_compile.compile(str(repository), doraise=True)
        py_compile.compile(str(checker), doraise=True)
        checks["bounded_windows_retry_added"] = (
            repository.read_text(encoding="utf-8").count("def _atomic_replace_with_windows_retry(") == 1
            and "_ATOMIC_REPLACE_MAX_ATTEMPTS = 20" in repository.read_text(encoding="utf-8")
        )
        checks["canonical_atomic_replace_retained"] = (
            repository.read_text(encoding="utf-8").count("os.replace(") == 1
            and repository.read_text(encoding="utf-8").count("_atomic_replace_with_windows_retry(") == 2
        )

        completed = subprocess.run(
            [sys.executable, "-B", str(checker), str(root), str(report)],
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
        )
        result_text = normalized(report) if report.is_file() else ""
        checks["corrected_14_b_certified"] = (
            completed.returncode == 0
            and "CERTIFICATION STATUS: CERTIFIED" in result_text
            and "FINAL RESULT: PART E STEP 14 END-TO-END PIPELINE CERTIFIED" in result_text
        )
        checks["failed_checks_empty"] = "FAILED_CHECKS:\n[]" in result_text
        checks["not_run_checks_empty"] = "NOT_RUN_CHECKS:\n[]" in result_text
        checks["production_patch_retained"] = all(
            (
                checks["corrected_14_b_certified"],
                checks["failed_checks_empty"],
                checks["not_run_checks_empty"],
                checks["bounded_windows_retry_added"],
                checks["canonical_atomic_replace_retained"],
            )
        )
        evidence = {
            "backup": str(backup_root),
            "repository_original_sha256": EXPECTED_REPOSITORY_HASH,
            "repository_retained_sha256": sha256(repository),
            "checker_original_sha256": EXPECTED_CHECKER_HASH,
            "checker_retained_sha256": sha256(checker),
            "certification_exit_code": completed.returncode,
            "certification_stdout": completed.stdout,
            "certification_stderr": completed.stderr,
            "report": str(report),
            "fix": {
                "authority": "_atomic_replace_with_windows_retry",
                "attempts": 20,
                "windows_only_retry": True,
                "atomic_replace_retained": True,
            },
        }
        if not all(checks.values()):
            raise RuntimeError("The corrected Part E 14-B certification did not pass completely.")
        retained = True
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        if not retained:
            if repository_original is not None:
                repository.write_bytes(repository_original)
            if checker_original is not None:
                checker.write_bytes(checker_original)

    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    print("FAILED_CHECK_COUNT=" + str(sum(not passed for passed in checks.values())))
    print("BACKUP=" + str(backup_root or "NONE"))
    print("REPORT=" + str(report))
    print("WINDOWS_ATOMIC_PERSISTENCE_FIX_STATUS=" + ("CERTIFIED" if retained else "NOT_CERTIFIED"))
    print("PART_E_14_B_STATUS=" + ("CERTIFIED" if retained else "NOT_CERTIFIED"))
    if error:
        print("EXECUTION_ERROR=" + json.dumps(error, default=str))
    if evidence:
        print("EVIDENCE=" + json.dumps(evidence, default=str))
    return 0 if retained else 1


if __name__ == "__main__":
    raise SystemExit(main())
