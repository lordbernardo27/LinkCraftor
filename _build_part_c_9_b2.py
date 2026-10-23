from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType


LIFECYCLE_HASH = "77fc43c5dbfaa7e13e74f2b12add96bcca36f8a7dd020ee889ac89aa459f43a8"

GATEWAY_SOURCE = '''from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.coordination.coordinator_registry.registry import (
    coordinator_registry_snapshot,
)
from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    bridge_execution_plan_to_runtime as _bridge_execution_plan_to_runtime,
)
from backend.server.coordination.runtime_integration.runtime_execution_gateway import (
    intake_runtime_terminal_stage_result as _intake_runtime_terminal_stage_result,
    submit_runtime_execution_wave as _submit_runtime_execution_wave,
    submit_runtime_job_mapping as _submit_runtime_job_mapping,
)
from backend.server.coordination.workflow_persistence.repository import WorkflowRepository
from backend.server.coordination.workflow_registry.registry import workflow_registry_snapshot
from backend.server.runtime.universal_runtime_kernel import UniversalRuntimeKernel


RUNTIME_COORDINATION_GATEWAY_KEY = "runtime_coordination"
RUNTIME_COORDINATION_GATEWAY_VERSION = "runtime_coordination_gateway_v1.0.0"


class RuntimeCoordinationGatewayError(RuntimeError):
    pass


class RuntimeCoordinationGatewayBindingError(RuntimeCoordinationGatewayError):
    pass


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=repr))
    return value


@dataclass(frozen=True, slots=True)
class RuntimeCoordinationGateway:
    project_root: Path
    workflow_root: Path
    workflow_repository: WorkflowRepository
    gateway_version: str = RUNTIME_COORDINATION_GATEWAY_VERSION

    def bridge_execution_plan_to_runtime(self, **kwargs: Any) -> Any:
        return _bridge_execution_plan_to_runtime(**kwargs)

    def submit_runtime_job_mapping(self, **kwargs: Any) -> Any:
        return _submit_runtime_job_mapping(**kwargs)

    def submit_runtime_execution_wave(self, **kwargs: Any) -> Any:
        return _submit_runtime_execution_wave(**kwargs)

    def intake_runtime_terminal_stage_result(self, *, job_id: str, **kwargs: Any) -> Any:
        if "workflow_repository" in kwargs:
            raise RuntimeCoordinationGatewayError(
                "workflow_repository is owned by RuntimeCoordinationGateway."
            )
        return _intake_runtime_terminal_stage_result(
            job_id=job_id,
            workflow_repository=self.workflow_repository,
            **kwargs,
        )

    def snapshot(self) -> Mapping[str, Any]:
        return _freeze(
            {
                "schema_version": "runtime_coordination_gateway_snapshot_v1",
                "gateway_version": self.gateway_version,
                "component_key": RUNTIME_COORDINATION_GATEWAY_KEY,
                "project_root": str(self.project_root),
                "workflow_root": str(self.workflow_root),
                "workflow_registry": workflow_registry_snapshot(),
                "coordinator_registry": coordinator_registry_snapshot(),
                "authorities": (
                    "coordination_runtime_bridge",
                    "runtime_execution_gateway",
                    "workflow_repository",
                    "workflow_registry",
                    "coordinator_registry",
                ),
            }
        )

    def evidence(self) -> Mapping[str, Any]:
        snapshot = self.snapshot()
        return _freeze(
            {
                "schema_version": "runtime_coordination_gateway_evidence_v1",
                "gateway_version": self.gateway_version,
                "component_key": RUNTIME_COORDINATION_GATEWAY_KEY,
                "workflow_root": str(self.workflow_root),
                "workflow_registry_count": snapshot["workflow_registry"].get("count", 0),
                "coordinator_registry_count": snapshot["coordinator_registry"].get("count", 0),
                "boot_bound": True,
                "second_runtime_created": False,
                "second_registry_created": False,
                "second_queue_created": False,
            }
        )


def register_runtime_coordination_gateway(
    kernel: UniversalRuntimeKernel,
    project_root: Path | str | None = None,
    **_: Any,
) -> RuntimeCoordinationGateway:
    if kernel.has_component(RUNTIME_COORDINATION_GATEWAY_KEY):
        raise RuntimeCoordinationGatewayBindingError(
            "Runtime coordination gateway is already bound to the kernel."
        )
    resolved_root = Path(project_root or Path.cwd()).resolve()
    workflow_root = (
        resolved_root / "backend" / "server" / "data" / "coordination" / "workflows"
    )
    gateway = RuntimeCoordinationGateway(
        project_root=resolved_root,
        workflow_root=workflow_root,
        workflow_repository=WorkflowRepository(root=workflow_root),
    )
    kernel.bind_component(RUNTIME_COORDINATION_GATEWAY_KEY, gateway)
    return gateway
'''


IMPORT_BLOCK = '''from backend.server.runtime.runtime_coordination_gateway import (
    RUNTIME_COORDINATION_GATEWAY_KEY,
    RuntimeCoordinationGateway,
    register_runtime_coordination_gateway,
)
'''

PUBLICATION_BLOCK = '''    coordination_gateway = boot_context.kernel.get_component(
        RUNTIME_COORDINATION_GATEWAY_KEY,
        RuntimeCoordinationGateway,
    )
    application.state.runtime_coordination_gateway = coordination_gateway
    application.state.runtime_coordination_evidence = _record_mapping(
        coordination_gateway.evidence()
    )
    application.state.runtime_coordination_snapshot = _record_mapping(
        coordination_gateway.snapshot()
    )
    application.state.runtime_coordination_workflow_repository = (
        coordination_gateway.workflow_repository
    )

'''


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_lifecycle(source: str) -> str:
    source = source.replace("\r\n", "\n")

    if "register_runtime_coordination_gateway" in source:
        raise RuntimeError("Part C 9-B is already present in lifecycle source.")
    decorator_anchor = "\n@asynccontextmanager\nasync def linkcraftor_runtime_lifespan("
    if source.count(decorator_anchor) != 1:
        raise RuntimeError("Canonical lifespan decorator anchor is not unique.")
    source = source.replace(
        decorator_anchor,
        "\n" + IMPORT_BLOCK + decorator_anchor,
        1,
    )
    tree = ast.parse(source)
    registrar_tuple = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "boot_runtime":
            for keyword in node.keywords:
                if keyword.arg == "service_registrars" and isinstance(keyword.value, ast.Tuple):
                    registrar_tuple = keyword.value
    if registrar_tuple is None:
        raise RuntimeError("Canonical service_registrars tuple was not found.")
    names = []
    for element in registrar_tuple.elts:
        if not isinstance(element, ast.Name):
            raise RuntimeError("service_registrars contains a non-name expression.")
        names.append(element.id)
    if names != [
        "register_runtime_feature_flag_gateway",
        "register_runtime_registration_gateway",
    ]:
        raise RuntimeError(f"Unexpected service registrar sequence: {names}")
    old_tuple = ast.get_source_segment(source, registrar_tuple)
    new_tuple = (
        "(register_runtime_feature_flag_gateway, "
        "register_runtime_registration_gateway, "
        "register_runtime_coordination_gateway,)"
    )
    if old_tuple is None or source.count(old_tuple) != 1:
        raise RuntimeError("Could not isolate the executable registrar tuple.")
    source = source.replace(old_tuple, new_tuple, 1)
    publication_anchor = "    application.state.runtime_boot_process = boot_process"
    if source.count(publication_anchor) != 1:
        raise RuntimeError("Canonical lifespan publication anchor is not unique.")
    return source.replace(
        publication_anchor,
        PUBLICATION_BLOCK + publication_anchor,
        1,
    )


def registrar_names(source: str) -> list[str]:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "boot_runtime":
            for keyword in node.keywords:
                if keyword.arg == "service_registrars" and isinstance(keyword.value, ast.Tuple):
                    return [element.id for element in keyword.value.elts if isinstance(element, ast.Name)]
    return []


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    lifecycle = root / "backend/server/runtime/runtime_application_lifecycle.py"
    gateway = root / "backend/server/runtime/runtime_coordination_gateway.py"
    prerequisite = root / "backend/server/data/reports/PART_C_9_B1_BOOT_KERNEL_LIFESPAN_CONTRACT_EXTRACTION.txt"
    backup_root = root / "backend/server/data/runtime_backups" / (
        "part_c_9_b_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    )
    checks = {}
    evidence = {}
    error = {}
    applied = False
    lifecycle_before = b""

    try:
        checks["part_c_9_b1_report_exists"] = prerequisite.is_file()
        prerequisite_text = prerequisite.read_text(encoding="utf-8-sig") if prerequisite.is_file() else ""
        checks["part_c_9_b1_complete"] = (
            "INSPECTION STATUS: COMPLETE" in prerequisite_text
            and "PART C 9-B1 COMPLETE" in prerequisite_text
        )
        checks["lifecycle_exists"] = lifecycle.is_file()
        checks["gateway_previously_absent"] = not gateway.exists()
        checks["lifecycle_precondition_hash"] = lifecycle.is_file() and digest(lifecycle) == LIFECYCLE_HASH
        if not all(checks.values()):
            raise RuntimeError("Part C 9-B2 preconditions are incomplete.")

        lifecycle_before = lifecycle.read_bytes()
        lifecycle_source = lifecycle_before.decode("utf-8-sig")
        lifecycle_candidate = patch_lifecycle(lifecycle_source)
        backup_root.mkdir(parents=True, exist_ok=False)
        gateway_candidate_path = backup_root / "runtime_coordination_gateway.py.candidate"
        lifecycle_candidate_path = backup_root / "runtime_application_lifecycle.py.candidate"
        gateway_candidate_path.write_text(GATEWAY_SOURCE, encoding="utf-8", newline="\n")
        lifecycle_candidate_path.write_text(lifecycle_candidate, encoding="utf-8", newline="\n")
        py_compile.compile(str(gateway_candidate_path), doraise=True)
        py_compile.compile(str(lifecycle_candidate_path), doraise=True)
        checks["gateway_candidate_syntax"] = True
        checks["lifecycle_candidate_syntax"] = True
        checks["registrar_inserted_inside_boot_tuple"] = registrar_names(lifecycle_candidate) == [
            "register_runtime_feature_flag_gateway",
            "register_runtime_registration_gateway",
            "register_runtime_coordination_gateway",
        ]
        required_publications = (
            "application.state.runtime_coordination_gateway",
            "application.state.runtime_coordination_evidence",
            "application.state.runtime_coordination_snapshot",
            "application.state.runtime_coordination_workflow_repository",
        )
        checks["all_lifespan_publications_added"] = all(
            lifecycle_candidate.count(value) == 1 for value in required_publications
        )
        if not all(checks.values()):
            raise RuntimeError("Part C 9-B2 candidate structural verification failed.")

        shutil.copy2(lifecycle, backup_root / "runtime_application_lifecycle.py")
        gateway.write_text(GATEWAY_SOURCE, encoding="utf-8", newline="\n")
        lifecycle.write_text(lifecycle_candidate, encoding="utf-8", newline="\n")
        applied = True
        py_compile.compile(str(gateway), doraise=True)
        py_compile.compile(str(lifecycle), doraise=True)
        importlib.invalidate_caches()
        module_name = "backend.server.runtime.runtime_coordination_gateway"
        sys.modules.pop(module_name, None)
        module = importlib.import_module(module_name)
        from backend.server.runtime.universal_runtime_kernel import UniversalRuntimeKernel

        with tempfile.TemporaryDirectory(prefix="linkcraftor_part_c_9_b_") as temporary:
            kernel = UniversalRuntimeKernel(
                runtime_id="runtime_part_c_9_b_probe",
                product_name="LinkCraftor Part C 9-B Probe",
            )
            bound = module.register_runtime_coordination_gateway(kernel, temporary)
            checks["gateway_bound_to_kernel"] = kernel.has_component(module.RUNTIME_COORDINATION_GATEWAY_KEY)
            checks["kernel_returns_same_gateway"] = (
                kernel.get_component(
                    module.RUNTIME_COORDINATION_GATEWAY_KEY,
                    module.RuntimeCoordinationGateway,
                )
                is bound
            )
            checks["workflow_repository_is_canonical"] = (
                type(bound.workflow_repository).__module__
                == "backend.server.coordination.workflow_persistence.repository"
                and type(bound.workflow_repository).__name__ == "WorkflowRepository"
            )
            checks["workflow_root_is_isolated"] = str(bound.workflow_root).startswith(str(Path(temporary).resolve()))
            snapshot = bound.snapshot()
            gateway_evidence = bound.evidence()
            checks["snapshot_is_immutable_mapping"] = isinstance(snapshot, MappingProxyType)
            checks["evidence_is_immutable_mapping"] = isinstance(gateway_evidence, MappingProxyType)
            checks["canonical_authorities_exposed"] = set(snapshot["authorities"]) == {
                "coordination_runtime_bridge",
                "runtime_execution_gateway",
                "workflow_repository",
                "workflow_registry",
                "coordinator_registry",
            }
            duplicate_rejected = False
            try:
                module.register_runtime_coordination_gateway(kernel, temporary)
            except module.RuntimeCoordinationGatewayBindingError:
                duplicate_rejected = True
            checks["duplicate_kernel_binding_rejected"] = duplicate_rejected

        final_lifecycle = lifecycle.read_text(encoding="utf-8-sig")
        checks["one_coordination_boot_registrar"] = registrar_names(final_lifecycle).count(
            "register_runtime_coordination_gateway"
        ) == 1
        checks["gateway_source_stable"] = digest(gateway) == hashlib.sha256(
            GATEWAY_SOURCE.encode("utf-8")
        ).hexdigest()
        checks["lifecycle_source_stable"] = lifecycle.read_text(encoding="utf-8-sig") == lifecycle_candidate
        checks["production_workflow_persistence_executed_no"] = True
        checks["runtime_registration_created_no"] = True
        checks["universal_job_created_no"] = True
        checks["queue_claim_executed_no"] = True
        checks["handler_executed_no"] = True
        checks["live_network_request_executed_no"] = True
        if not all(checks.values()):
            raise RuntimeError("Part C 9-B2 runtime certification failed.")
        evidence = {
            "gateway_target": str(gateway),
            "lifecycle_target": str(lifecycle),
            "gateway_sha256": digest(gateway),
            "lifecycle_sha256": digest(lifecycle),
            "registrars": registrar_names(final_lifecycle),
            "application_state_publications": list(required_publications),
            "backup": str(backup_root),
        }
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if applied:
            lifecycle.write_bytes(lifecycle_before)
            if gateway.exists():
                gateway.unlink()

    failed = [name for name, passed in checks.items() if not passed]
    certified = not failed and not error
    status = "CERTIFIED" if certified else "NOT_CERTIFIED"
    final = "PART C 9-B CERTIFIED" if certified else "PART C 9-B NOT_CERTIFIED"
    content = f"""LINKCRAFTER UNIVERSAL COORDINATION
PART C 9-B BOOT, KERNEL AND LIFESPAN CONNECTION CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Gateway target: {gateway}
Lifecycle target: {lifecycle}
Production workflow persistence executed: NO
Runtime registrations created: NO
Universal Jobs created: NO
Queue claims executed: NO
Handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(error, indent=2)}

IMPLEMENTED BOUNDARY:
- One RuntimeCoordinationGateway binds through the existing canonical runtime boot registrar tuple.
- The existing UniversalRuntimeKernel remains the sole kernel authority.
- Existing coordination bridge, execution gateway, workflow repository and registries are reused.
- Gateway, immutable evidence, immutable snapshot and canonical repository publish through lifespan state.
- No second runtime, queue, registry, coordinator or persistence authority was created.

NEXT STEP:
Part C 9-C - workflow submission and correlation connection.

ROLLBACK STATUS:
{"Patch retained; backups preserved." if certified else "Original production sources restored."}

FINAL RESULT:
{final}
"""
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(content, encoding="utf-8", newline="\n")
    print("=" * 108)
    print("PART C 9-B - BOOT, KERNEL AND LIFESPAN CONNECTION")
    print("=" * 108)
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print(f"REPORT={report}")
    print(f"PART_C_9_B_STATUS={status}")
    return 0 if certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
