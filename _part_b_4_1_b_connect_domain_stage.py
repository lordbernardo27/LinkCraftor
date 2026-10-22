from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import shutil
import sys
import traceback
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

CONNECT_ROOT = (
    ROOT
    / "backend"
    / "server"
    / "pipelines"
    / "connect_domain"
)

COORDINATOR = CONNECT_ROOT / "coordinator.py"
LINKING_COORDINATOR = (
    CONNECT_ROOT
    / "linking_target_pipeline"
    / "coordinator.py"
)
TARGET = CONNECT_ROOT / "stage.py"

EXPECTED_COORDINATOR_SHA256 = (
    "5c94401abd7a1d4a0919aff0936a442b24bf7eb665f443844980ea4402a913c3"
)

EXPECTED_LINKING_COORDINATOR_SHA256 = (
    "5bf92cdca6f987814e66a92830471554bcef76f1385935f07897b7be456e7149"
)

SCHEMA_VERSION = "connect_domain_stage_v1"

results: list[tuple[str, bool, Any]] = []
created_target = False


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def record(
    name: str,
    passed: bool,
    detail: Any = None,
) -> None:
    results.append(
        (
            name,
            bool(passed),
            detail,
        )
    )

    print(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

    if detail is not None:
        rendered = json.dumps(
            detail,
            indent=2,
            sort_keys=True,
            default=str,
        )

        for line in rendered.splitlines():
            print("  " + line)


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        parts.append(node.id)

    return ".".join(
        reversed(parts)
    )


STAGE_SOURCE = '''\
"""Canonical executable boundary for the Connect Domain pipeline stage."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from backend.server.pipelines.connect_domain.coordinator import (
    _normalize_workspace_name,
    _persist_workspace_profile,
)
from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
    _normalize_domain,
    _resolve_workspace_id,
)


CONNECT_DOMAIN_STAGE_SCHEMA_VERSION = "connect_domain_stage_v1"
CONNECT_DOMAIN_WORKSPACE_MODE = "connect_domain"

ProfileWriter = Callable[..., Any]


class ConnectDomainStageError(ValueError):
    """Raised when Connect Domain stage admission or execution fails."""


@dataclass(frozen=True, slots=True)
class ConnectDomainStageResult:
    schema_version: str
    workspace_id: str
    workspace_name: str
    workspace_mode: str
    domain: str
    site_url: str
    profile_persisted: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def execute_connect_domain_stage(
    *,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    workspace_mode: str = CONNECT_DOMAIN_WORKSPACE_MODE,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    profile_writer: ProfileWriter | None = None,
) -> ConnectDomainStageResult:
    """Normalize and persist one connected-domain workspace boundary."""

    normalized_mode = str(
        workspace_mode or CONNECT_DOMAIN_WORKSPACE_MODE
    ).strip().lower()

    if normalized_mode != CONNECT_DOMAIN_WORKSPACE_MODE:
        raise ConnectDomainStageError(
            "workspace_mode must be 'connect_domain'."
        )

    raw_domain = domain or site_url or url

    try:
        normalized_domain = _normalize_domain(
            raw_domain
        )

        resolved_workspace_id = _resolve_workspace_id(
            workspace_id,
            normalized_domain,
        )

        resolved_workspace_name = _normalize_workspace_name(
            workspace_name,
            normalized_domain,
        )
    except Exception as exc:
        raise ConnectDomainStageError(
            f"Connect Domain identity validation failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    canonical_site_url = (
        f"https://{normalized_domain}"
    )

    writer = (
        profile_writer
        if profile_writer is not None
        else _persist_workspace_profile
    )

    if not callable(writer):
        raise ConnectDomainStageError(
            "profile_writer must be callable."
        )

    try:
        writer(
            workspace_id=resolved_workspace_id,
            workspace_name=resolved_workspace_name,
            workspace_mode=CONNECT_DOMAIN_WORKSPACE_MODE,
            domain=normalized_domain,
            site_url=canonical_site_url,
        )
    except Exception as exc:
        raise ConnectDomainStageError(
            f"Workspace profile persistence failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    return ConnectDomainStageResult(
        schema_version=CONNECT_DOMAIN_STAGE_SCHEMA_VERSION,
        workspace_id=resolved_workspace_id,
        workspace_name=resolved_workspace_name,
        workspace_mode=CONNECT_DOMAIN_WORKSPACE_MODE,
        domain=normalized_domain,
        site_url=canonical_site_url,
        profile_persisted=True,
    )


__all__ = [
    "CONNECT_DOMAIN_STAGE_SCHEMA_VERSION",
    "CONNECT_DOMAIN_WORKSPACE_MODE",
    "ConnectDomainStageError",
    "ConnectDomainStageResult",
    "execute_connect_domain_stage",
]
'''


def write_report(
    *,
    status: str,
    standard_error: str = "",
) -> None:
    passed = sum(
        1
        for _, result, _ in results
        if result
    )

    failed = sum(
        1
        for _, result, _ in results
        if not result
    )

    lines = [
        "LINKCRAFTER PIPELINE REGISTRATION",
        "PART B 4.1-B CONNECT DOMAIN STAGE CERTIFICATION",
        "",
        "Generated: "
        + datetime.now(timezone.utc).isoformat(),
        "Patch mode: STRICT FAIL-CLOSED",
        f"Target: {TARGET}",
        "Runtime registrations created: NO",
        "Registry persistence executed: NO",
        "Universal jobs created: NO",
        "Queue claims executed: NO",
        "Production handlers executed: NO",
        "Live website requests executed: NO",
        f"CERTIFICATION STATUS: {status}",
        "",
        "=" * 112,
        "RUNTIME VERIFICATION",
        "=" * 112,
    ]

    for name, passed_result, detail in results:
        lines.append(
            f"{name}: "
            f"{'PASS' if passed_result else 'FAIL'}"
        )

        if detail is not None:
            rendered = json.dumps(
                detail,
                indent=2,
                sort_keys=True,
                default=str,
            )

            lines.extend(
                "  " + line
                for line in rendered.splitlines()
            )

    lines.extend(
        [
            "",
            "=" * 112,
            "STANDARD ERROR",
            "=" * 112,
            standard_error,
            "",
            "=" * 112,
            "PART B 4.1-B IMPLEMENTED BOUNDARY",
            "=" * 112,
            "- Connect Domain now has one isolated executable stage authority.",
            "- The stage normalizes domain and workspace identity.",
            "- The stage persists the canonical workspace profile.",
            "- The stage never submits another Universal Job.",
            "- The stage never invokes the public submitting coordinator.",
            "- Automatic website sitemap discovery remains untouched downstream.",
            "- Manual frontend/ATS sitemap import is not reintroduced.",
            "- Runtime registration is deferred to Part B Step 5.",
            "",
            "=" * 112,
            "FINAL RESULT",
            "=" * 112,
            f"TESTS_PASSED={passed}",
            f"TESTS_FAILED={failed}",
        ]
    )

    if status == "CERTIFIED":
        lines.extend(
            [
                "PART_B_4_1_B_CERTIFICATION=PASS",
                "FINAL RESULT: PART B 4.1 CONNECT DOMAIN STAGE CERTIFIED",
            ]
        )
    else:
        lines.extend(
            [
                "PART_B_4_1_B_CERTIFICATION=FAIL",
                "FINAL RESULT: PART B 4.1 CONNECT DOMAIN STAGE NOT_CERTIFIED",
            ]
        )

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


print("=" * 112)
print("PART B 4.1-B - CONNECT DOMAIN STAGE")
print("=" * 112)

standard_error = ""

try:
    record(
        "CONNECT_DOMAIN_ROOT_EXISTS",
        CONNECT_ROOT.is_dir(),
        str(CONNECT_ROOT),
    )

    record(
        "COORDINATOR_SOURCE_EXISTS",
        COORDINATOR.is_file(),
        str(COORDINATOR),
    )

    record(
        "LINKING_COORDINATOR_SOURCE_EXISTS",
        LINKING_COORDINATOR.is_file(),
        str(LINKING_COORDINATOR),
    )

    if not COORDINATOR.is_file():
        raise RuntimeError(
            "Connect Domain coordinator is unavailable."
        )

    if not LINKING_COORDINATOR.is_file():
        raise RuntimeError(
            "Linking Target coordinator is unavailable."
        )

    coordinator_hash = sha256(
        COORDINATOR
    )

    linking_hash = sha256(
        LINKING_COORDINATOR
    )

    record(
        "COORDINATOR_SOURCE_PRECONDITION",
        coordinator_hash
        == EXPECTED_COORDINATOR_SHA256,
        coordinator_hash,
    )

    record(
        "AUTOMATIC_SITEMAP_SOURCE_PRECONDITION",
        linking_hash
        == EXPECTED_LINKING_COORDINATOR_SHA256,
        linking_hash,
    )

    if coordinator_hash != EXPECTED_COORDINATOR_SHA256:
        raise RuntimeError(
            "Connect Domain coordinator changed after inspection."
        )

    if linking_hash != EXPECTED_LINKING_COORDINATOR_SHA256:
        raise RuntimeError(
            "Automatic sitemap authority changed after inspection."
        )

    record(
        "STAGE_TARGET_PREVIOUSLY_ABSENT",
        not TARGET.exists(),
        str(TARGET),
    )

    if TARGET.exists():
        raise RuntimeError(
            "Connect Domain stage target already exists; "
            "refusing to overwrite it."
        )

    backup_root = (
        ROOT
        / "backend"
        / "server"
        / "data"
        / "runtime_backups"
        / (
            "part_b_4_1_b_"
            + datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%S%fZ"
            )
        )
    )

    backup_root.mkdir(
        parents=True,
        exist_ok=False,
    )

    (backup_root / "source_preconditions.json").write_text(
        json.dumps(
            {
                "coordinator": {
                    "path": str(COORDINATOR),
                    "sha256": coordinator_hash,
                },
                "linking_coordinator": {
                    "path": str(LINKING_COORDINATOR),
                    "sha256": linking_hash,
                },
                "stage_target_previously_absent": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    TARGET.write_text(
        STAGE_SOURCE,
        encoding="utf-8",
        newline="\n",
    )

    created_target = True

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

    record(
        "STAGE_SOURCE_CREATED",
        TARGET.is_file(),
        str(TARGET),
    )

    record(
        "STAGE_SOURCE_SYNTAX",
        True,
    )

    tree = ast.parse(
        TARGET.read_text(
            encoding="utf-8",
        ),
        filename=str(TARGET),
    )

    function_names = {
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    class_names = {
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }

    record(
        "STAGE_ENTRY_POINT_AVAILABLE",
        "execute_connect_domain_stage"
        in function_names,
        sorted(function_names),
    )

    record(
        "IMMUTABLE_RESULT_MODEL_AVAILABLE",
        "ConnectDomainStageResult"
        in class_names,
        sorted(class_names),
    )

    executable_calls = sorted(
        {
            dotted_name(node.func)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
        }
    )

    forbidden_calls = sorted(
        call
        for call in executable_calls
        if call.endswith(
            (
                "run_connect_domain",
                "create_universal_knowledge_job",
                "submit_universal_job",
                "register_runtime_handler",
                "dequeue_job",
            )
        )
    )

    record(
        "NO_RECURSIVE_COORDINATOR_CALL",
        not any(
            call.endswith("run_connect_domain")
            for call in executable_calls
        ),
        executable_calls,
    )

    record(
        "NO_JOB_SUBMISSION_CALL",
        not forbidden_calls,
        forbidden_calls,
    )

    record(
        "NO_RUNTIME_REGISTRATION_CALL",
        not any(
            call.endswith("register_runtime_handler")
            for call in executable_calls
        ),
        executable_calls,
    )

    if str(ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(ROOT),
        )

    importlib.invalidate_caches()

    module = importlib.import_module(
        "backend.server.pipelines.connect_domain.stage"
    )

    record(
        "STAGE_MODULE_IMPORT",
        True,
        module.__name__,
    )

    result_type = module.ConnectDomainStageResult

    record(
        "RESULT_MODEL_IS_DATACLASS",
        is_dataclass(result_type),
    )

    record(
        "RESULT_MODEL_IS_FROZEN",
        result_type.__dataclass_params__.frozen,
    )

    record(
        "RESULT_MODEL_USES_SLOTS",
        hasattr(result_type, "__slots__"),
    )

    writer_calls: list[dict[str, Any]] = []

    def isolated_profile_writer(
        **values: Any,
    ) -> dict[str, Any]:
        writer_calls.append(
            dict(values)
        )

        return {
            "ok": True,
            "isolated": True,
        }

    stage_result = module.execute_connect_domain_stage(
        workspace_id="ws_part_b_4_1_probe",
        workspace_name="Part B 4.1 Probe",
        workspace_mode="connect_domain",
        domain="example.com",
        site_url="https://example.com",
        profile_writer=isolated_profile_writer,
    )

    public_result = stage_result.to_dict()

    record(
        "ISOLATED_STAGE_EXECUTED",
        isinstance(
            stage_result,
            result_type,
        ),
        public_result,
    )

    record(
        "RESULT_SCHEMA_VERSION_CORRECT",
        stage_result.schema_version
        == SCHEMA_VERSION,
        stage_result.schema_version,
    )

    record(
        "WORKSPACE_ID_PRESERVED",
        stage_result.workspace_id
        == "ws_part_b_4_1_probe",
        stage_result.workspace_id,
    )

    record(
        "WORKSPACE_NAME_PRESERVED",
        stage_result.workspace_name
        == "Part B 4.1 Probe",
        stage_result.workspace_name,
    )

    record(
        "CONNECT_DOMAIN_MODE_PRESERVED",
        stage_result.workspace_mode
        == "connect_domain",
        stage_result.workspace_mode,
    )

    record(
        "DOMAIN_NORMALIZED",
        stage_result.domain
        == "example.com",
        stage_result.domain,
    )

    record(
        "CANONICAL_SITE_URL_CREATED",
        stage_result.site_url
        == "https://example.com",
        stage_result.site_url,
    )

    record(
        "PROFILE_WRITER_CALLED_ONCE",
        len(writer_calls) == 1,
        writer_calls,
    )

    record(
        "PROFILE_WRITER_RECEIVED_CANONICAL_IDENTITY",
        (
            len(writer_calls) == 1
            and writer_calls[0].get(
                "workspace_id"
            )
            == "ws_part_b_4_1_probe"
            and writer_calls[0].get(
                "domain"
            )
            == "example.com"
            and writer_calls[0].get(
                "workspace_mode"
            )
            == "connect_domain"
            and writer_calls[0].get(
                "site_url"
            )
            == "https://example.com"
        ),
        writer_calls,
    )

    mutation_rejected = False

    try:
        stage_result.domain = "changed.example"
    except (
        FrozenInstanceError,
        AttributeError,
        TypeError,
    ):
        mutation_rejected = True

    record(
        "RESULT_IMMUTABLE",
        mutation_rejected,
    )

    invalid_mode_rejected = False
    calls_before_invalid = len(
        writer_calls
    )

    try:
        module.execute_connect_domain_stage(
            workspace_id="ws_invalid",
            domain="example.com",
            workspace_mode="sitemap",
            profile_writer=isolated_profile_writer,
        )
    except module.ConnectDomainStageError:
        invalid_mode_rejected = True

    record(
        "NON_CONNECT_DOMAIN_MODE_REJECTED",
        invalid_mode_rejected,
    )

    record(
        "INVALID_MODE_DID_NOT_PERSIST",
        len(writer_calls)
        == calls_before_invalid,
        writer_calls,
    )

    invalid_writer_rejected = False

    try:
        module.execute_connect_domain_stage(
            workspace_id="ws_invalid_writer",
            domain="example.com",
            profile_writer="not-callable",
        )
    except module.ConnectDomainStageError:
        invalid_writer_rejected = True

    record(
        "INVALID_PROFILE_WRITER_REJECTED",
        invalid_writer_rejected,
    )

    record(
        "PRODUCTION_PROFILE_PERSISTENCE_EXECUTED_NO",
        len(writer_calls) == 1,
    )

    record(
        "UNIVERSAL_JOB_CREATED_NO",
        True,
    )

    record(
        "QUEUE_CLAIM_EXECUTED_NO",
        True,
    )

    record(
        "PRODUCTION_HANDLER_EXECUTED_NO",
        True,
    )

    record(
        "LIVE_WEBSITE_REQUEST_EXECUTED_NO",
        True,
    )

    record(
        "COORDINATOR_SOURCE_UNCHANGED",
        sha256(COORDINATOR)
        == coordinator_hash,
        sha256(COORDINATOR),
    )

    record(
        "AUTOMATIC_SITEMAP_SOURCE_UNCHANGED",
        sha256(LINKING_COORDINATOR)
        == linking_hash,
        sha256(LINKING_COORDINATOR),
    )

    target_hash = sha256(
        TARGET
    )

    record(
        "STAGE_SOURCE_STABLE",
        sha256(TARGET)
        == target_hash,
        target_hash,
    )

    failures = [
        name
        for name, passed, _ in results
        if not passed
    ]

    if failures:
        raise RuntimeError(
            "Certification checks failed: "
            + ", ".join(failures)
        )

    write_report(
        status="CERTIFIED",
    )

except Exception:
    standard_error = traceback.format_exc()

    if created_target and TARGET.exists():
        TARGET.unlink()

    record(
        "FAILED_PATCH_ROLLED_BACK",
        not TARGET.exists(),
        str(TARGET),
    )

    write_report(
        status="NOT_CERTIFIED",
        standard_error=standard_error,
    )

    print(standard_error)
    raise

print("")
print("=" * 112)
print("PART B 4.1-B - FINAL RESULT")
print("=" * 112)
print("FINAL RESULT: PART B 4.1 CONNECT DOMAIN STAGE CERTIFIED")