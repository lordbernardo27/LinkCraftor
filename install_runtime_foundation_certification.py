# -*- coding: utf-8 -*-
"""Production installer for the Runtime Foundation Certification module.

This installer performs a transactional, verified installation of the
already-reviewed ``runtime_foundation_certification.py`` production module
(Phase 1.1.15). It verifies the exact baseline SHA-256 and size, backs up
any existing target, installs atomically, and then exercises the installed
module in place: compile and import verification, an AST-based
forbidden-import scan, a double execution of ``RuntimeFoundationCertification``
with determinism and immutability verification across implementation,
certification, matrix and report fingerprints, verification of the complete
14-component certification matrix, and runtime-audited confirmation that the
production module performs no filesystem writes, no network access and no
production-state mutation. Any failure triggers a full rollback to the
pre-installation state. On success it writes a certification-evidence file
and prints a PASS/FAIL matrix.

The installer itself is permitted to touch the filesystem (backup, atomic
replace, evidence); the *production module* is the subject under test and is
held to the no-write / no-network contract while it executes.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Baseline contract for the reviewed production module
# ---------------------------------------------------------------------------

MODULE_FILENAME: str = "runtime_foundation_certification.py"
MODULE_IMPORT_NAME: str = "runtime_foundation_certification"

#: Exact baseline of the reviewed production module. Installation aborts
#: unless the source matches both values byte-for-byte.
BASELINE_SHA256: str = (
    "10d447d953981498ead5c3f113175dde7ac26b81f44712c744888a5c3246edcd"
)
BASELINE_SIZE: int = 46921

#: Foundation expectations the installed module must satisfy.
EXPECTED_COMPONENT_COUNT: int = 14
EXPECTED_PRESENCE_SECTION: str = "COMPONENT_PRESENCE"
EXPECTED_COMPONENT_ROLES: tuple[str, ...] = (
    "universal_runtime_kernel",
    "runtime_configuration",
    "runtime_environment",
    "runtime_service_registry",
    "runtime_lifecycle_manager",
    "runtime_boot_process",
    "runtime_shutdown_process",
    "runtime_versioning",
    "runtime_compatibility_layer",
    "runtime_feature_flags",
    "runtime_capability_negotiation",
    "runtime_persistence_interface",
    "runtime_state_store_abstraction",
    "runtime_schema_management",
)

#: Modules the production module must never import (I/O, network, DB,
#: process). Roots are matched against the head of any imported name.
FORBIDDEN_IMPORT_ROOTS: frozenset[str] = frozenset(
    {
        "os", "io", "pathlib", "shutil", "tempfile", "fileinput",
        "socket", "ssl", "http", "urllib", "ftplib", "asyncio",
        "requests", "aiohttp", "websocket", "websockets",
        "sqlite3", "psycopg2", "pymysql", "mysql", "sqlalchemy",
        "pymongo", "redis",
        "subprocess", "multiprocessing", "ctypes",
    }
)

#: Ordered installer verification steps, used to render the PASS/FAIL matrix.
_ORDERED_CHECKS: tuple[tuple[str, str], ...] = (
    ("baseline_sha256", "verify baseline SHA-256"),
    ("baseline_size", "verify baseline size"),
    ("backup_created", "create backup of existing target"),
    ("transactional_install", "transactional installation"),
    ("compile_verification", "compile verification"),
    ("import_verification", "import verification"),
    ("ast_forbidden_scan", "AST forbidden-import scan"),
    ("double_execution", "execute certification twice"),
    ("deterministic_implementation", "deterministic implementation fingerprint"),
    ("deterministic_certification", "deterministic certification fingerprint"),
    ("deterministic_matrix", "deterministic matrix fingerprint"),
    ("deterministic_report", "deterministic report fingerprint"),
    ("immutable_report", "immutable report"),
    ("identity_stability", "certification identity stability"),
    ("complete_matrix", "complete 14-component matrix"),
    ("no_state_mutation", "no production state mutation"),
    ("no_filesystem_writes", "no filesystem writes by module"),
    ("no_network_access", "no network access by module"),
    ("evidence_generated", "generate certification evidence"),
)


# ---------------------------------------------------------------------------
# Runtime audit hook (observes the module while it executes)
# ---------------------------------------------------------------------------

# A single, permanently installed audit hook records sensitive events, but
# only while _AUDIT_ACTIVE is true. PEP 578 hooks cannot be removed, so
# gating by a flag keeps installer-side file operations out of the record.
_AUDIT_ACTIVE: list[bool] = [False]
_WRITE_EVENTS: list[str] = []
_NETWORK_EVENTS: list[str] = []
_PROCESS_EVENTS: list[str] = []

_WRITE_FLAG_MASK = (
    os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
)
_WRITE_EVENT_NAMES = frozenset(
    {
        "os.rename", "os.replace", "os.remove", "os.unlink", "os.mkdir",
        "os.rmdir", "os.makedirs", "os.truncate", "os.chmod", "os.chown",
        "os.link", "os.symlink", "shutil.copyfile", "shutil.copymode",
        "shutil.copystat", "shutil.move", "shutil.rmtree",
    }
)
_NETWORK_EVENT_PREFIXES = ("socket.", "urllib.", "ssl.", "http.")
_NETWORK_EVENT_NAMES = frozenset(
    {"socket.connect", "socket.getaddrinfo", "socket.gethostbyname"}
)
_PROCESS_EVENT_PREFIXES = ("subprocess.",)
_PROCESS_EVENT_NAMES = frozenset(
    {"os.system", "os.exec", "os.posix_spawn", "os.fork"}
)


def _audit_hook(event: str, args: tuple) -> None:
    if not _AUDIT_ACTIVE[0]:
        return
    if event == "open":
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else None
        writing = False
        if isinstance(mode, str) and any(ch in mode for ch in "wax+"):
            writing = True
        elif mode is None and isinstance(flags, int) and (
            flags & _WRITE_FLAG_MASK
        ):
            writing = True
        if writing:
            _WRITE_EVENTS.append(f"open:{args[0]!r}:{mode}")
        return
    if event in _WRITE_EVENT_NAMES:
        _WRITE_EVENTS.append(event)
        return
    if event in _NETWORK_EVENT_NAMES or event.startswith(
        _NETWORK_EVENT_PREFIXES
    ):
        _NETWORK_EVENTS.append(event)
        return
    if event in _PROCESS_EVENT_NAMES or event.startswith(
        _PROCESS_EVENT_PREFIXES
    ) or event.startswith("os.exec"):
        _PROCESS_EVENTS.append(event)
        return


sys.addaudithook(_audit_hook)


# ---------------------------------------------------------------------------
# Canonicalisation mirror (must match the production module exactly)
# ---------------------------------------------------------------------------


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# ---------------------------------------------------------------------------
# Result matrix
# ---------------------------------------------------------------------------


class _Matrix:
    """Accumulates and renders the installer PASS/FAIL matrix."""

    def __init__(self) -> None:
        self._status: dict[str, str] = {}
        self._detail: dict[str, str] = {}

    def record(self, key: str, status: str, detail: str = "") -> None:
        self._status[key] = status
        self._detail[key] = detail

    def passed(self, key: str, detail: str = "") -> None:
        self.record(key, "PASS", detail)

    def failed(self, key: str, detail: str = "") -> None:
        self.record(key, "FAIL", detail)

    def fill_skipped(self) -> None:
        for key, _ in _ORDERED_CHECKS:
            self._status.setdefault(key, "SKIP")

    def all_passed(self) -> bool:
        return all(
            self._status.get(key) == "PASS" for key, _ in _ORDERED_CHECKS
        )

    def render(self, rolled_back: bool) -> str:
        width = 62
        line = "=" * width
        rows = [line, " Runtime Foundation Certification - Installation", line]
        for index, (key, label) in enumerate(_ORDERED_CHECKS, start=1):
            status = self._status.get(key, "SKIP")
            leader = label + " "
            dots = "." * max(3, width - len(leader) - 8)
            rows.append(f" [{index:>2}] {leader}{dots} {status}")
            detail = self._detail.get(key, "")
            if detail and status != "PASS":
                rows.append(f"        -> {detail}")
        rows.append(line)
        passed = sum(
            1 for key, _ in _ORDERED_CHECKS
            if self._status.get(key) == "PASS"
        )
        total = len(_ORDERED_CHECKS)
        overall = "PASS" if self.all_passed() else "FAIL"
        rows.append(f" RESULT: {overall}  ({passed}/{total} checks)")
        if rolled_back:
            rows.append(" ROLLBACK: performed - target restored to baseline")
        rows.append(line)
        return "\n".join(rows)

    def summary(self) -> dict[str, object]:
        return {
            "checks": [
                {
                    "key": key,
                    "label": label,
                    "status": self._status.get(key, "SKIP"),
                    "detail": self._detail.get(key, ""),
                }
                for key, label in _ORDERED_CHECKS
            ],
            "overall": "PASS" if self.all_passed() else "FAIL",
        }


class _AbortInstall(Exception):
    """Raised to abort installation and trigger rollback."""

    def __init__(self, key: str, detail: str) -> None:
        super().__init__(detail)
        self.key = key
        self.detail = detail


# ---------------------------------------------------------------------------
# Installer
# ---------------------------------------------------------------------------


class _Installer:
    """Transactional installer with rollback for the certification module."""

    def __init__(
        self, source_path: str, target_dir: str, evidence_path: str
    ) -> None:
        self.source_path = os.path.abspath(source_path)
        self.target_dir = os.path.abspath(target_dir)
        self.target_path = os.path.join(self.target_dir, MODULE_FILENAME)
        self.evidence_path = os.path.abspath(evidence_path)
        self.matrix = _Matrix()
        self._backup_path: str | None = None
        self._target_preexisting = False
        self._installed = False
        self._source_bytes = b""
        self._report_one: dict = {}
        self._report_two: dict = {}

    # -- small helpers ------------------------------------------------------

    def _abort(self, key: str, detail: str) -> None:
        self.matrix.failed(key, detail)
        raise _AbortInstall(key, detail)

    def _load_installed_module(self):
        import importlib

        if self.target_dir not in sys.path:
            sys.path.insert(0, self.target_dir)
        importlib.invalidate_caches()
        sys.modules.pop(MODULE_IMPORT_NAME, None)
        return importlib.import_module(MODULE_IMPORT_NAME)

    # -- verification steps -------------------------------------------------

    def _verify_baseline(self) -> None:
        if not os.path.isfile(self.source_path):
            self._abort("baseline_sha256",
                        f"source not found: {self.source_path}")
        with open(self.source_path, "rb") as handle:
            self._source_bytes = handle.read()

        digest = hashlib.sha256(self._source_bytes).hexdigest()
        if digest != BASELINE_SHA256:
            self._abort(
                "baseline_sha256",
                f"expected {BASELINE_SHA256}, got {digest}",
            )
        self.matrix.passed("baseline_sha256", digest)

        size = len(self._source_bytes)
        if size != BASELINE_SIZE:
            self._abort(
                "baseline_size", f"expected {BASELINE_SIZE}, got {size}"
            )
        self.matrix.passed("baseline_size", f"{size} bytes")

    def _create_backup(self) -> None:
        os.makedirs(self.target_dir, exist_ok=True)
        if os.path.isfile(self.target_path):
            self._target_preexisting = True
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            self._backup_path = f"{self.target_path}.backup-{stamp}"
            shutil.copy2(self.target_path, self._backup_path)
            self.matrix.passed("backup_created", self._backup_path)
        else:
            self.matrix.passed("backup_created", "no existing target")

    def _install(self) -> None:
        handle, tmp_path = tempfile.mkstemp(
            prefix=".rfc-install-", dir=self.target_dir
        )
        try:
            with os.fdopen(handle, "wb") as writer:
                writer.write(self._source_bytes)
                writer.flush()
                os.fsync(writer.fileno())
            os.replace(tmp_path, self.target_path)
        except Exception as exc:  # noqa: BLE001
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            self._abort("transactional_install", f"{type(exc).__name__}: {exc}")
        self._installed = True
        # Confirm the installed bytes match the verified source exactly.
        with open(self.target_path, "rb") as reader:
            if hashlib.sha256(reader.read()).hexdigest() != BASELINE_SHA256:
                self._abort(
                    "transactional_install",
                    "installed file digest mismatch",
                )
        self.matrix.passed("transactional_install", self.target_path)

    def _verify_compile(self) -> None:
        import py_compile

        try:
            py_compile.compile(self.target_path, doraise=True)
        except Exception as exc:  # noqa: BLE001
            self._abort("compile_verification", f"{type(exc).__name__}: {exc}")
        self.matrix.passed("compile_verification", "byte-compiled cleanly")

    def _verify_import(self):
        try:
            module = self._load_installed_module()
        except Exception as exc:  # noqa: BLE001
            self._abort("import_verification", f"{type(exc).__name__}: {exc}")
        for attribute in (
            "RuntimeFoundationCertification", "FOUNDATION_COMPONENTS"
        ):
            if not hasattr(module, attribute):
                self._abort(
                    "import_verification", f"missing attribute {attribute}"
                )
        self.matrix.passed("import_verification", "module imported")
        return module

    def _verify_ast(self) -> None:
        try:
            tree = ast.parse(
                self._source_bytes.decode("utf-8"), filename=self.target_path
            )
        except SyntaxError as exc:
            self._abort("ast_forbidden_scan", f"syntax error: {exc}")

        offenders: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in FORBIDDEN_IMPORT_ROOTS:
                        offenders.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    root = node.module.split(".")[0]
                    if root in FORBIDDEN_IMPORT_ROOTS:
                        offenders.append(node.module)
        if offenders:
            self._abort(
                "ast_forbidden_scan",
                "forbidden imports: " + ", ".join(sorted(set(offenders))),
            )
        self.matrix.passed("ast_forbidden_scan", "no forbidden imports")

    def _execute_twice(self, module) -> None:
        # Prevent first-time-import bytecode writes from being attributed to
        # the module under audit, then execute exactly twice under audit.
        previous_dont_write = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        environ_before = dict(os.environ)
        module_ids_before = {
            name: id(mod) for name, mod in list(sys.modules.items())
        }
        _WRITE_EVENTS.clear()
        _NETWORK_EVENTS.clear()
        _PROCESS_EVENTS.clear()
        certifier = module.RuntimeFoundationCertification()
        try:
            _AUDIT_ACTIVE[0] = True
            report_one = certifier.certify()
            report_two = certifier.certify()
        except Exception as exc:  # noqa: BLE001
            self._abort("double_execution", f"{type(exc).__name__}: {exc}")
        finally:
            _AUDIT_ACTIVE[0] = False
            sys.dont_write_bytecode = previous_dont_write

        if not (report_one.get("certified") and report_two.get("certified")):
            self._abort(
                "double_execution",
                "module did not certify on both runs: "
                + ",".join(report_one.get("failure_codes", []) or ["?"]),
            )
        # Retain plain copies for downstream checks and evidence.
        self._report_one = json.loads(_canonical_json(dict(report_one)))
        self._report_two = json.loads(_canonical_json(dict(report_two)))
        self._environ_before = environ_before
        self._module_ids_before = module_ids_before
        self.matrix.passed("double_execution", "two certified runs")

    def _verify_determinism(self) -> None:
        one, two = self._report_one, self._report_two
        for field, key in (
            ("implementation_fingerprint", "deterministic_implementation"),
            ("certification_fingerprint", "deterministic_certification"),
            ("matrix_fingerprint", "deterministic_matrix"),
        ):
            value_one = one.get(field)
            value_two = two.get(field)
            if not (isinstance(value_one, str) and len(value_one) == 64):
                self._abort(key, f"{field} is not a 64-hex digest")
            if value_one != value_two:
                self._abort(
                    key, f"{field} drifted between runs"
                )
            self.matrix.passed(key, value_one[:16] + "...")

        # The report fingerprint intentionally binds the generation
        # timestamp. Prove it is a deterministic digest of report content by
        # recomputing it, and prove the timestamp is the only source of
        # variation by recomputing with generated_at normalised.
        def recompute(report: dict, normalise: bool) -> str:
            core = {k: v for k, v in report.items() if k != "report_fingerprint"}
            if normalise:
                core["generated_at"] = "NORMALISED"
            return _sha256_hex(_canonical_json(core))

        if recompute(one, False) != one.get("report_fingerprint"):
            self._abort(
                "deterministic_report", "run one report fingerprint invalid"
            )
        if recompute(two, False) != two.get("report_fingerprint"):
            self._abort(
                "deterministic_report", "run two report fingerprint invalid"
            )
        if recompute(one, True) != recompute(two, True):
            self._abort(
                "deterministic_report",
                "report fingerprint varies beyond the timestamp",
            )
        self.matrix.passed(
            "deterministic_report", "reproducible modulo timestamp"
        )

    def _verify_immutable(self, module) -> None:
        certifier = module.RuntimeFoundationCertification()
        report = certifier.certify()
        try:
            report["certified"] = False  # type: ignore[index]
            self._abort("immutable_report", "report mapping was mutable")
        except TypeError:
            pass
        last = certifier.last_report()
        try:
            last["certified"] = False  # type: ignore[index]
            self._abort("immutable_report", "last_report mapping was mutable")
        except TypeError:
            pass
        if certifier.certification_fingerprint() != report.get(
            "report_fingerprint"
        ):
            self._abort(
                "immutable_report", "certification_fingerprint accessor drift"
            )
        self.matrix.passed("immutable_report", "read-only report")

    def _verify_identity(self) -> None:
        one, two = self._report_one, self._report_two
        identity_one = one.get("certification_id")
        if identity_one != two.get("certification_id"):
            self._abort(
                "identity_stability", "certification_id changed between runs"
            )
        if not (
            isinstance(identity_one, str)
            and identity_one.startswith("rfc-cert-")
        ):
            self._abort("identity_stability", "malformed certification_id")
        self.matrix.passed("identity_stability", identity_one)

    def _verify_complete_matrix(self) -> None:
        report = self._report_one
        if not report.get("complete"):
            self._abort("complete_matrix", "matrix reported incomplete")
        if not report.get("certified"):
            self._abort("complete_matrix", "foundation not certified")
        if report.get("failure_codes"):
            self._abort(
                "complete_matrix",
                "failure codes: " + ",".join(report["failure_codes"]),
            )
        presence = None
        for section in report.get("sections", []):
            if section.get("name") == EXPECTED_PRESENCE_SECTION:
                presence = section
                break
        if presence is None:
            self._abort("complete_matrix", "presence section absent")
        if len(presence.get("checks", [])) != EXPECTED_COMPONENT_COUNT:
            self._abort(
                "complete_matrix",
                f"expected {EXPECTED_COMPONENT_COUNT} presence checks",
            )
        seen_roles = {
            check.get("check_id", "").split("presence.", 1)[-1]
            for check in presence.get("checks", [])
        }
        missing = [
            role for role in EXPECTED_COMPONENT_ROLES if role not in seen_roles
        ]
        if missing:
            self._abort(
                "complete_matrix", "missing roles: " + ",".join(missing)
            )
        if any(
            check.get("status") != "pass"
            for check in presence.get("checks", [])
        ):
            self._abort("complete_matrix", "a component failed presence")
        self.matrix.passed(
            "complete_matrix",
            f"{EXPECTED_COMPONENT_COUNT}/{EXPECTED_COMPONENT_COUNT} components",
        )

    def _verify_no_state_mutation(self) -> None:
        if dict(os.environ) != self._environ_before:
            self._abort(
                "no_state_mutation", "process environment was mutated"
            )
        for name, ident in self._module_ids_before.items():
            current = sys.modules.get(name)
            if current is not None and id(current) != ident:
                self._abort(
                    "no_state_mutation",
                    f"pre-existing module replaced: {name}",
                )
        if self._process_events():
            self._abort(
                "no_state_mutation",
                "process events: " + ",".join(self._process_events()),
            )
        self.matrix.passed(
            "no_state_mutation", "environment and module table intact"
        )

    def _process_events(self) -> list[str]:
        return sorted(set(_PROCESS_EVENTS))

    def _verify_no_writes(self) -> None:
        writes = sorted(set(_WRITE_EVENTS))
        if writes:
            self._abort(
                "no_filesystem_writes",
                "write events: " + "; ".join(writes[:5]),
            )
        self.matrix.passed(
            "no_filesystem_writes", "no write events observed"
        )

    def _verify_no_network(self) -> None:
        network = sorted(set(_NETWORK_EVENTS))
        if network:
            self._abort(
                "no_network_access",
                "network events: " + "; ".join(network[:5]),
            )
        self.matrix.passed("no_network_access", "no network events observed")

    def _generate_evidence(self) -> None:
        report = self._report_one
        evidence = {
            "kind": "runtime.foundation.certification.installation_evidence",
            "generated_at": _now(),
            "module": {
                "filename": MODULE_FILENAME,
                "target_path": self.target_path,
                "baseline_sha256": BASELINE_SHA256,
                "baseline_size": BASELINE_SIZE,
            },
            "certification": {
                "certification_id": report.get("certification_id"),
                "phase": report.get("phase"),
                "subsystem": report.get("subsystem"),
                "certified": report.get("certified"),
                "complete": report.get("complete"),
                "status": report.get("status"),
                "passed_checks": report.get("passed_checks"),
                "failed_checks": report.get("failed_checks"),
                "total_checks": report.get("total_checks"),
                "implementation_fingerprint": report.get(
                    "implementation_fingerprint"
                ),
                "certification_fingerprint": report.get(
                    "certification_fingerprint"
                ),
                "matrix_fingerprint": report.get("matrix_fingerprint"),
                "report_fingerprint_run_one": report.get("report_fingerprint"),
                "report_fingerprint_run_two": self._report_two.get(
                    "report_fingerprint"
                ),
                "section_summaries": report.get("section_summaries"),
            },
            "installer_matrix": self.matrix.summary(),
        }
        payload = _canonical_json(evidence)
        evidence["evidence_fingerprint"] = _sha256_hex(payload)
        directory = os.path.dirname(self.evidence_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        handle, tmp_path = tempfile.mkstemp(
            prefix=".rfc-evidence-", dir=directory or None
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as writer:
                json.dump(evidence, writer, indent=2, sort_keys=True)
                writer.write("\n")
                writer.flush()
                os.fsync(writer.fileno())
            os.replace(tmp_path, self.evidence_path)
        except Exception as exc:  # noqa: BLE001
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            self._abort("evidence_generated", f"{type(exc).__name__}: {exc}")
        self.matrix.passed("evidence_generated", self.evidence_path)

    # -- rollback -----------------------------------------------------------

    def _rollback(self) -> bool:
        if not self._installed:
            return False
        try:
            if self._target_preexisting and self._backup_path:
                os.replace(self._backup_path, self.target_path)
            elif os.path.exists(self.target_path):
                os.remove(self.target_path)
            return True
        except Exception:  # noqa: BLE001
            return False

    # -- orchestration ------------------------------------------------------

    def run(self) -> int:
        rolled_back = False
        try:
            self._verify_baseline()
            self._create_backup()
            self._install()
            self._verify_compile()
            module = self._verify_import()
            self._verify_ast()
            self._execute_twice(module)
            self._verify_determinism()
            self._verify_immutable(module)
            self._verify_identity()
            self._verify_complete_matrix()
            self._verify_no_state_mutation()
            self._verify_no_writes()
            self._verify_no_network()
            self._generate_evidence()
        except _AbortInstall:
            rolled_back = self._rollback()
        except Exception as exc:  # noqa: BLE001
            self.matrix.failed(
                "transactional_install",
                f"unexpected: {type(exc).__name__}: {exc}",
            )
            traceback.print_exc()
            rolled_back = self._rollback()

        self.matrix.fill_skipped()
        print(self.matrix.render(rolled_back))
        return 0 if self.matrix.all_passed() else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _project_root() -> str:
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Install and verify the Runtime Foundation Certification module."
        )
    )
    parser.add_argument(
        "--source",
        default=_default_source(),
        help="path to the reviewed runtime_foundation_certification.py source",
    )
    parser.add_argument(
        "--target-dir",
        default=_default_runtime_dir(),
        help="directory to install the module into (the runtime package dir)",
    )
    parser.add_argument(
        "--evidence",
        default=None,
        help="path for the generated certification evidence JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    evidence = (
        args.evidence
        or _default_evidence()
    )
    installer = _Installer(args.source, args.target_dir, evidence)
    return installer.run()


if __name__ == "__main__":
    raise SystemExit(main())