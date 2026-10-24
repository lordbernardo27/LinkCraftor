"""Read-only Part D collective verification; only report artifacts may be written.

Usage: python _part_d_12_c_final_pipeline_coordination_certification.py ROOT REPORT
Does not install, patch, activate, register, submit or execute production stages.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import os
import re
import sys
import traceback
from collections.abc import Mapping
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import FunctionType, MappingProxyType, SimpleNamespace
from typing import Any

sys.dont_write_bytecode = True

REPORT_NAME = "PART_D_12_C_FINAL_CONNECTED_DOMAIN_PIPELINE_COORDINATION_CERTIFICATION.txt"
STAGES = (
    "connect_domain", "site_sources", "url_cleaner", "site_pages",
    "live_domain_target_pool", "active_target_set",
)
JOBS = tuple(stage + "_stage" for stage in STAGES)

CERTIFIED_GATEWAY_SHA256 = "9c381cfb5ef773b45488bd548ee4361c55984f9b6ea60e558755390b8177338d"
CERTIFIED_GATEWAY_AST_SHA256 = "082dcbbe37e3c801732a63f75828852cfc7c5efb66d09d8ff48d4a3bde3b81b2"
REVIEWED_REGISTRAR = '''def register_runtime_coordination_gateway(
    composition: Any,
    project_root: Path | str | None = None,
    **_: Any,
) -> RuntimeCoordinationGateway:
    kernel = composition.kernel
    if kernel.has_component(RUNTIME_COORDINATION_GATEWAY_KEY):
        raise RuntimeCoordinationGatewayBindingError(
            "Runtime coordination gateway is already bound to the kernel."
        )
    resolved_root = Path(project_root or composition.project_root).resolve()
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
ORIGINAL_REGISTRAR = (
    REVIEWED_REGISTRAR.replace("composition: Any,", "kernel: UniversalRuntimeKernel,", 1)
    .replace("    kernel = composition.kernel\n", "", 1)
    .replace("project_root or composition.project_root", "project_root or Path.cwd()", 1)
)

HISTORICAL = {
    "part_c": (
        "PART_C_9_E_FINAL_UNIVERSAL_COORDINATION_CERTIFICATION.txt",
        "CERTIFICATION STATUS", "CERTIFIED",
        "PART C UNIVERSAL COORDINATION CERTIFIED",
    ),
    "step_10": (
        "PART_D_10_B_CONNECTED_DOMAIN_PIPELINE_COORDINATOR_CERTIFICATION.txt",
        "CERTIFICATION STATUS", "CERTIFIED",
        "PART D STEP 10 CONNECTED DOMAIN PIPELINE COORDINATOR CERTIFIED",
    ),
    "step_11": (
        "PART_D_11_B_COORDINATOR_UNIVERSAL_COORDINATION_CONNECTION_CERTIFICATION.txt",
        "CERTIFICATION STATUS", "CERTIFIED",
        "PART D STEP 11 COORDINATOR CONNECTED TO UNIVERSAL COORDINATION FRAMEWORK",
    ),
    "step_12_a": (
        "PART_D_12_A_CORRECTED_CONNECTED_DOMAIN_MANIFEST_BOUNDARY_CLOSURE.txt",
        "INSPECTION STATUS", "COMPLETE", "PART D 12-A COMPLETE",
    ),
    "step_12_b1": (
        "PART_D_12_B1_MANIFEST_IMPLEMENTATION_CONTRACT_EXTRACTION.txt",
        "EXTRACTION STATUS", "COMPLETE", "PART D 12-B1 COMPLETE",
    ),
    "runnable_handoff": (
        "PART_D_12_B1_RUNNABLE_PLANNING_HANDOFF.txt",
        "HANDOFF STATUS", "COMPLETE", "PART D 12-B1 RUNNABLE HANDOFF COMPLETE",
    ),
    "step_12_b": (
        "PART_D_12_B_CONNECTED_DOMAIN_PIPELINE_MANIFEST_CERTIFICATION.txt",
        "CERTIFICATION STATUS", "CERTIFIED",
        "PART D 12-B CONNECTED DOMAIN PIPELINE MANIFEST CERTIFIED",
    ),
}

SOURCE_PATHS = {
    "coordinator": "backend/server/pipelines/connect_domain/coordinator.py",
    "manifest": "backend/server/pipelines/connect_domain/manifest.py",
    "runtime_coordination_gateway": "backend/server/runtime/runtime_coordination_gateway.py",
    "runtime_execution_gateway": "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
    "runtime_application_lifecycle": "backend/server/runtime/runtime_application_lifecycle.py",
    "runtime_registration": "backend/server/runtime/universal_runtime_registration.py",
    "coordinator_contract": "backend/server/coordination/pipeline_coordinators/contract.py",
}


def plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return plain(value.value)
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((plain(item) for item in value), key=repr)
    if dataclasses.is_dataclass(value) and not inspect.isclass(value):
        return {field.name: plain(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if callable(getattr(value, "to_public_dict", None)):
        return plain(value.to_public_dict())
    return value


def canonical(value: Any) -> str:
    return json.dumps(plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def section(text: str, name: str, *, optional: bool = False) -> Any:
    match = re.search(r"(?m)^" + re.escape(name) + r":?[ \t]*\n(?:=+[ \t]*\n)?", text)
    if not match:
        if optional:
            return None
        raise ValueError("Report JSON section is absent: " + name)
    result, _ = json.JSONDecoder().raw_decode(text[match.end():].lstrip())
    return result


def report_valid(text: str, header: str, status: str, final: str) -> bool:
    final_line = next((line.strip() for line in reversed(text.splitlines()) if line.strip()), "")
    final_line = re.sub(r"^(?:FINAL RESULT:\s*)+", "", final_line)
    checks = section(text, "CHECKS")
    return bool(
        re.search(r"(?m)^" + re.escape(header) + r":\s*" + re.escape(status) + r"\s*$", text)
        and final_line == final
        and isinstance(checks, dict) and checks
        and all(value is True for value in checks.values())
        and section(text, "FAILED_CHECKS") == []
        and section(text, "EXECUTION_ERROR", optional=True) in (None, {})
    )


def immutable_result(value: Any) -> bool:
    cls = type(value)
    return bool(
        dataclasses.is_dataclass(value)
        and getattr(getattr(cls, "__dataclass_params__", None), "frozen", False)
        and hasattr(cls, "__slots__")
    )


def ast_shape(value: Any) -> Any:
    """Stable across Python 3.12/3.13 AST pretty-printer formatting changes."""
    if isinstance(value, ast.AST):
        return {"node": type(value).__name__, "fields": {key: ast_shape(item) for key, item in ast.iter_fields(value)}}
    if isinstance(value, list):
        return [ast_shape(item) for item in value]
    if value is Ellipsis:
        return {"literal": "Ellipsis"}
    return value


def reviewed_gateway_delta(source: str, historical_hash: str) -> tuple[bool, Mapping[str, Any]]:
    """Allow only the reviewed registrar change; all other Python AST must match Part C."""
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "register_runtime_coordination_gateway"]
    expected_function = ast.parse(REVIEWED_REGISTRAR).body[0]
    signature_match = len(functions) == 1 and ast_shape(functions[0]) == ast_shape(expected_function)
    if signature_match:
        index = tree.body.index(functions[0])
        tree.body[index] = ast.parse(ORIGINAL_REGISTRAR).body[0]
    reversed_ast_hash = digest(ast_shape(tree))
    valid = bool(
        historical_hash == CERTIFIED_GATEWAY_SHA256 and signature_match
        and reversed_ast_hash == CERTIFIED_GATEWAY_AST_SHA256
    )
    return valid, {
        "reviewed_registrar_exact_ast_match": signature_match,
        "historical_gateway_sha256": historical_hash,
        "certified_gateway_ast_sha256": CERTIFIED_GATEWAY_AST_SHA256,
        "gateway_ast_after_reversing_reviewed_change": reversed_ast_hash,
        "all_other_gateway_code_preserved": valid,
        "reviewed_changes": [
            "Registrar receives composition rather than a bare kernel.",
            "Kernel resolves from composition.kernel.",
            "Default project root resolves from composition.project_root.",
        ],
    }


def test_composition_binding(module: Any) -> Mapping[str, bool]:
    """Exercise real registrar bytecode with in-memory kernel/repository dependencies only."""
    class KernelProbe:
        def __init__(self) -> None:
            self.components: dict[str, Any] = {}

        def has_component(self, key: str) -> bool:
            return key in self.components

        def bind_component(self, key: str, value: Any) -> None:
            if key in self.components:
                raise RuntimeError("Duplicate isolated binding")
            self.components[key] = value

    class RepositoryProbe:
        def __init__(self, *, root: Any) -> None:
            self.root = Path(root).resolve()

    original = module.register_runtime_coordination_gateway
    globals_copy = dict(original.__globals__)
    globals_copy["WorkflowRepository"] = RepositoryProbe
    registrar = FunctionType(original.__code__, globals_copy, original.__name__, original.__defaults__, original.__closure__)
    registrar.__kwdefaults__ = original.__kwdefaults__
    # A virtual path only: no TemporaryDirectory/gettempdir probe may write under the guard.
    probe_root = (Path(sys.executable).resolve().parent / "__virtual_linkcraftor_12c_binding_probe__").resolve()
    kernel = KernelProbe()
    composition = SimpleNamespace(kernel=kernel, project_root=probe_root)
    bound = registrar(composition)
    expected_workflows = probe_root / "backend/server/data/coordination/workflows"
    correct_binding = bool(
        kernel.components.get(module.RUNTIME_COORDINATION_GATEWAY_KEY) is bound
        and isinstance(bound, module.RuntimeCoordinationGateway)
        and bound.project_root == probe_root
        and bound.workflow_root == expected_workflows
        and isinstance(bound.workflow_repository, RepositoryProbe)
        and bound.workflow_repository.root == expected_workflows
    )
    duplicate_rejected = False
    try:
        registrar(composition)
    except module.RuntimeCoordinationGatewayBindingError:
        duplicate_rejected = True
    override = probe_root / "explicit_override"
    overridden = registrar(SimpleNamespace(kernel=KernelProbe(), project_root=probe_root), project_root=override)
    return {
        "composition_registration_isolated_test_passed": correct_binding,
        "duplicate_isolated_gateway_binding_rejected": duplicate_rejected,
        "explicit_registration_project_root_preserved": overridden.project_root == override,
    }


class ReadOnlyGuard:
    """Deny external side effects while imported project code is inspected."""

    def __init__(self, report: Path) -> None:
        self.report = report.resolve()
        self.allowed_report_paths = {self.report}
        self.report_writing = False
        self.denied: list[dict[str, str]] = []
        self.active = True

    def reject(self, kind: str, detail: Any) -> None:
        self.denied.append({"kind": kind, "detail": str(detail)})
        raise RuntimeError("Read-only verification denied " + kind + ": " + str(detail))

    def audit(self, event: str, args: tuple[Any, ...]) -> None:
        if not self.active:
            return
        if event == "open":
            path, mode, flags = args
            writes = bool(
                isinstance(mode, str) and any(token in mode for token in "wax+")
                or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if writes:
                allowed = bool(
                    self.report_writing and isinstance(path, (str, bytes, os.PathLike))
                    and Path(os.fsdecode(path)).resolve() in self.allowed_report_paths
                )
                if not allowed:
                    self.reject("file_write", path)
        elif event in {
            "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink",
            "os.truncate", "os.chmod", "os.utime", "os.setxattr", "shutil.copyfile",
            "socket.connect", "socket.bind", "socket.getaddrinfo", "socket.sendto",
            "subprocess.Popen", "os.system", "sqlite3.connect", "winreg.SetValue",
        }:
            self.reject(event, args[:2])

    def profile(self, frame: Any, event: str, arg: Any) -> None:
        if event != "call" or not self.active:
            return
        module = str(frame.f_globals.get("__name__", ""))
        name = frame.f_code.co_name
        if not module.startswith("backend.server."):
            return
        forbidden = {
            "submit_universal_job", "dispatch_registered_runtime_handler",
            "register_runtime_handler", "unregister_runtime_handler", "register_coordinator",
            "save_workflow", "save_jobs", "create_job", "claim_next_job",
            "submit_runtime_job_mapping", "submit_runtime_execution_wave",
        }
        if name in forbidden or (
            module.startswith("backend.server.pipelines.connect_domain") and name.startswith("execute_")
        ) or (module.startswith("backend.server.runtime") and name.startswith("claim_")):
            self.reject("production_call", module + ":" + name)


class IsolatedGateway:
    """Record the coordinator handoff only; do not call a runtime gateway."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def submit_workflow_execution(self, **kwargs: Any) -> Mapping[str, Any]:
        self.calls.append(kwargs)
        return MappingProxyType({
            "verification_only": True, "submitted": False,
            "workflow_id": kwargs["context"].workflow_id,
        })


def main(root: Path, report: Path) -> int:
    reports = root / "backend/server/data/reports"
    if report.resolve() != (reports / REPORT_NAME).resolve() or not reports.is_dir():
        print("Report must use the canonical reports directory and 12-C filename.", file=sys.stderr)
        return 2
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    names = ["historical_" + key + "_valid" for key in HISTORICAL]
    names += ["source_exists_" + key for key in SOURCE_PATHS]
    names += ["source_syntax_" + key for key in SOURCE_PATHS]
    names += [
        "historical_source_hash_lineage_valid", "coordinator_matches_step_11_and_12_b",
        "manifest_matches_step_12_b", "framework_source_integrity_verified",
        "reviewed_gateway_change_verified", "composition_registration_isolated_test_passed",
        "duplicate_isolated_gateway_binding_rejected", "explicit_registration_project_root_preserved",
        "required_modules_imported", "all_six_registrations_loaded_and_persistent",
        "coordinator_contract_valid", "coordinator_contract_frozen_slotted",
        "canonical_runtime_policy_and_execution_model", "contract_job_types_complete",
        "coordination_intent_deterministic", "workspace_and_domain_preserved",
        "manifest_result_frozen_slotted", "manifest_stage_order_and_job_types_correct",
        "six_canonical_stage_references_valid", "five_dependency_edges_correct",
        "six_execution_waves_correct", "only_initial_stage_runnable",
        "canonical_planning_certification_passed", "manifest_deterministic",
        "manifest_snapshot_immutable", "connection_accepts_real_manifest",
        "isolated_gateway_called_once", "connection_identities_preserved",
        "connection_result_frozen_slotted", "connection_serialization_complete",
        "no_real_runtime_submission", "canonical_gateway_boundary_retained",
        "production_sources_unchanged", "historical_reports_unchanged",
        "runtime_registry_memory_unchanged", "runtime_registry_file_unchanged",
        "no_forbidden_side_effects_attempted", "collective_fingerprint_valid",
    ]
    checks = dict.fromkeys(names, None)
    evidence: dict[str, Any] = {}
    error: dict[str, str] = {}
    guard = ReadOnlyGuard(report)
    sys.addaudithook(guard.audit)
    previous_profile = sys.getprofile()
    source_hashes: dict[str, str] = {}
    history_hashes: dict[str, str] = {}

    try:
        texts: dict[str, str] = {}
        for key, (filename, header, status, final) in HISTORICAL.items():
            path = reports / filename
            if not path.is_file():
                raise FileNotFoundError("Required historical report is absent: " + str(path))
            texts[key] = read(path)
            checks["historical_" + key + "_valid"] = report_valid(texts[key], header, status, final)
            history_hashes[key] = file_hash(path)
        evidence["historical_reports"] = {
            key: {"name": config[0], "sha256": history_hashes[key]}
            for key, config in HISTORICAL.items()
        }

        for key, relative in SOURCE_PATHS.items():
            path = root / relative
            checks["source_exists_" + key] = path.is_file()
            if not path.is_file():
                raise FileNotFoundError("Required production source is absent: " + str(path))
            compile(read(path), str(path), "exec")
            checks["source_syntax_" + key] = True
            source_hashes[key] = file_hash(path)
        evidence["source_hashes"] = dict(source_hashes)

        e10 = section(texts["step_10"], "EVIDENCE")
        e11 = section(texts["step_11"], "EVIDENCE")
        e12 = section(texts["step_12_b"], "EVIDENCE")
        ec = section(texts["part_c"], "COLLECTIVE EVIDENCE")
        checks["historical_source_hash_lineage_valid"] = bool(
            e10.get("retained_sha256") and e11.get("original_sha256") == e10["retained_sha256"]
        )
        checks["coordinator_matches_step_11_and_12_b"] = (
            source_hashes["coordinator"] == e11.get("retained_sha256") == e12.get("coordinator_sha256")
        )
        checks["manifest_matches_step_12_b"] = source_hashes["manifest"] == e12.get("manifest_sha256")
        framework_keys = ("runtime_coordination_gateway", "runtime_execution_gateway", "runtime_application_lifecycle")
        evidence["integrity_expected"] = {
            "coordinator": e11.get("retained_sha256"),
            "manifest": e12.get("manifest_sha256"),
            **{key: ec.get("source_hashes", {}).get(key) for key in framework_keys},
        }
        raw_framework_matches = {
            key: source_hashes[key] == ec.get("source_hashes", {}).get(key) for key in framework_keys
        }
        evidence["framework_raw_hash_matches_part_c"] = raw_framework_matches
        if raw_framework_matches["runtime_coordination_gateway"]:
            checks["reviewed_gateway_change_verified"] = True
            evidence["reviewed_gateway_change"] = {"status": "Original certified gateway bytes unchanged"}
        else:
            valid_delta, delta_evidence = reviewed_gateway_delta(
                read(root / SOURCE_PATHS["runtime_coordination_gateway"]),
                ec.get("source_hashes", {}).get("runtime_coordination_gateway", ""),
            )
            checks["reviewed_gateway_change_verified"] = valid_delta
            evidence["reviewed_gateway_change"] = dict(delta_evidence)
        checks["framework_source_integrity_verified"] = bool(
            raw_framework_matches["runtime_execution_gateway"]
            and raw_framework_matches["runtime_application_lifecycle"]
            and checks["reviewed_gateway_change_verified"]
        )
        if not all(checks["historical_" + key + "_valid"] for key in HISTORICAL) or not all(
            checks[name] for name in (
                "historical_source_hash_lineage_valid",
                "coordinator_matches_step_11_and_12_b", "manifest_matches_step_12_b",
                "framework_source_integrity_verified",
            )
        ):
            raise RuntimeError("Historical certification or installed-source integrity gate failed; no runtime checks executed.")

        coordinator = importlib.import_module("backend.server.pipelines.connect_domain.coordinator")
        manifest_module = importlib.import_module("backend.server.pipelines.connect_domain.manifest")
        registration = importlib.import_module("backend.server.runtime.universal_runtime_registration")
        contracts = importlib.import_module("backend.server.coordination.pipeline_coordinators.contract")
        gateway_module = importlib.import_module("backend.server.runtime.runtime_coordination_gateway")
        checks["required_modules_imported"] = True

        registration.ensure_persisted_runtime_registrations_loaded()
        registry_before = canonical(registration.runtime_registration_snapshot())
        snapshot = json.loads(registry_before)
        registry_path_text = str(snapshot.get("persistent_registry_path") or "").strip()
        registry_path = Path(registry_path_text) if registry_path_text else None
        if registry_path is not None and not registry_path.is_absolute():
            registry_path = root / registry_path
        registry_file_before = file_hash(registry_path) if registry_path is not None and registry_path.is_file() else None
        # All disk/network writes are denied even if the registry does not publish its path.
        checks["runtime_registry_file_unchanged"] = registry_path is None

        sys.setprofile(guard.profile)
        checks.update(test_composition_binding(gateway_module))
        loaded = {job: plain(registration.get_runtime_registration(job)) for job in JOBS}
        checks["all_six_registrations_loaded_and_persistent"] = all(
            isinstance(loaded[job], Mapping) and loaded[job].get("persistent") is True
            and loaded[job].get("job_type") == job and loaded[job].get("stage") == stage
            for stage, job in zip(STAGES, JOBS)
        )

        contract = coordinator.build_connected_domain_coordinator_contract()
        checks["coordinator_contract_valid"] = contracts.validate_pipeline_coordinator_contract(contract).is_valid
        checks["coordinator_contract_frozen_slotted"] = immutable_result(contract)
        checks["canonical_runtime_policy_and_execution_model"] = (
            getattr(contract.execution_model, "name", "") == "ASYNCHRONOUS"
            and getattr(contract.runtime_policy, "name", "") == "UNIVERSAL_RUNTIME_REQUIRED"
        )
        checks["contract_job_types_complete"] = tuple(contract.stage_job_types) == JOBS

        arguments = {
            "workspace_id": "ws_part_d_12_c_probe", "workspace_name": "Part D 12-C Probe",
            "domain": "Example.COM", "workflow_id": "workflow_part_d_12_c_probe",
            "correlation_id": "correlation_part_d_12_c_probe",
        }
        intent = coordinator.coordinate_connect_domain_pipeline(**arguments)
        repeated_intent = coordinator.coordinate_connect_domain_pipeline(**arguments)
        checks["coordination_intent_deterministic"] = canonical(intent.to_dict()) == canonical(repeated_intent.to_dict())
        checks["workspace_and_domain_preserved"] = (
            intent.workspace_id == arguments["workspace_id"] and intent.domain == "example.com"
            and intent.site_url == "https://example.com"
        )

        manifest = manifest_module.build_connected_domain_pipeline_manifest(workflow_id=intent.workflow_id)
        repeated_manifest = manifest_module.build_connected_domain_pipeline_manifest(workflow_id=intent.workflow_id)
        checks["manifest_result_frozen_slotted"] = immutable_result(manifest)
        checks["manifest_stage_order_and_job_types_correct"] = manifest.stage_ids == STAGES and manifest.stage_job_types == JOBS
        checks["six_canonical_stage_references_valid"] = (
            tuple(manifest.stage_references) == STAGES and all(
                reference.validate().is_valid and reference.uses_universal_runtime
                and reference.runtime_lookup_key == job
                for reference, job in zip(manifest.stage_references.values(), JOBS)
            )
        )
        checks["five_dependency_edges_correct"] = {
            edge.to_tuple() for edge in manifest.dependency_graph.edges
        } == set(zip(STAGES, STAGES[1:]))
        checks["six_execution_waves_correct"] = (
            manifest.execution_plan.wave_count == 6
            and tuple(wave.stage_ids for wave in manifest.execution_plan.waves) == tuple((stage,) for stage in STAGES)
            and tuple(wave.wave_index for wave in manifest.execution_plan.waves) == tuple(range(1, 7))
            and manifest.execution_plan.planned_stage_ids == STAGES
        )
        checks["only_initial_stage_runnable"] = manifest.planning_resolutions[0].runnable_stage_ids == ("connect_domain",)
        checks["canonical_planning_certification_passed"] = (
            manifest.planning_certification.is_certified and manifest.planning_certification.failed_check_count == 0
        )
        checks["manifest_deterministic"] = canonical(manifest.to_dict()) == canonical(repeated_manifest.to_dict())
        manifest_snapshot = manifest_module.connected_domain_manifest_snapshot(manifest)
        try:
            manifest_snapshot["mutation_probe"] = True
        except TypeError:
            checks["manifest_snapshot_immutable"] = True

        isolated_gateway = IsolatedGateway()
        connection = coordinator.connect_connected_domain_to_universal_coordination(
            runtime_gateway=isolated_gateway, execution_plan=manifest.execution_plan,
            stage_references=manifest.stage_references, **arguments,
        )
        checks["connection_accepts_real_manifest"] = (
            connection.execution_plan is manifest.execution_plan
            and tuple(connection.stage_references) == STAGES
        )
        checks["isolated_gateway_called_once"] = len(isolated_gateway.calls) == 1
        checks["connection_identities_preserved"] = (
            connection.intent.workflow_id == connection.handoff_context.workflow_id == intent.workflow_id
            and connection.intent.workspace_id == connection.handoff_context.workspace_id == intent.workspace_id
            and connection.intent.correlation_id == connection.handoff_context.correlation_id == intent.correlation_id
        )
        checks["connection_result_frozen_slotted"] = immutable_result(connection)
        serialized_connection = plain(connection.to_dict())
        checks["connection_serialization_complete"] = bool(canonical(serialized_connection)) and (
            serialized_connection.get("schema_version") == "connected_domain_universal_coordination_v1"
        )
        checks["no_real_runtime_submission"] = connection.runtime_submission.get("submitted") is False
        checks["canonical_gateway_boundary_retained"] = (
            callable(getattr(gateway_module.RuntimeCoordinationGateway, "submit_workflow_execution", None))
            and connection.evidence.get("runtime_gateway") == "submit_workflow_execution"
        )

        checks["runtime_registry_memory_unchanged"] = registry_before == canonical(registration.runtime_registration_snapshot())
        if registry_path is not None:
            registry_file_after = file_hash(registry_path) if registry_path.is_file() else None
            checks["runtime_registry_file_unchanged"] = registry_file_before == registry_file_after
        checks["production_sources_unchanged"] = all(
            source_hashes[key] == file_hash(root / relative) for key, relative in SOURCE_PATHS.items()
        )
        checks["historical_reports_unchanged"] = all(
            history_hashes[key] == file_hash(reports / config[0]) for key, config in HISTORICAL.items()
        )
        checks["no_forbidden_side_effects_attempted"] = not guard.denied
        evidence.update({
            "historical_reports": {key: {"name": config[0], "sha256": history_hashes[key]} for key, config in HISTORICAL.items()},
            "source_hashes": source_hashes,
            "registered_job_types": JOBS,
            "registration_fingerprints": {job: loaded[job].get("registration_fingerprint") for job in JOBS},
            "manifest_identity_fingerprint": manifest.identity_fingerprint(),
            "manifest_content_fingerprint": manifest.content_fingerprint(),
            "dependency_edges": tuple(edge.to_tuple() for edge in manifest.dependency_graph.edges),
            "execution_plan": plain(manifest.execution_plan.to_dict()),
            "coordinator_contract": plain(contract),
            "isolated_gateway_call_count": len(isolated_gateway.calls),
            "production_submission_performed": False,
            "connection_result": serialized_connection,
            "registry_file_published": registry_path_text or None,
            "scope": "Part D collective architecture certification; activation and end-to-end execution remain Part E.",
            "denied_operations": list(guard.denied),
        })
        evidence["collective_fingerprint"] = digest(evidence)
        checks["collective_fingerprint_valid"] = len(evidence["collective_fingerprint"]) == 64
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
    finally:
        sys.setprofile(previous_profile)

    evidence["denied_operations"] = list(guard.denied)
    failed = sorted(name for name, passed in checks.items() if passed is False)
    not_run = sorted(name for name, passed in checks.items() if passed is None)
    certified = not failed and not not_run and not error and not guard.denied
    status = "CERTIFIED" if certified else "NOT_CERTIFIED"
    lines = [
        "LINKCRAFTOR PIPELINE COORDINATION", "PART D 12-C FINAL CONNECTED DOMAIN PIPELINE COORDINATION CERTIFICATION", "",
        "Generated: " + datetime.now(timezone.utc).isoformat(),
        "Mode: READ-ONLY COLLECTIVE FINAL CERTIFICATION",
        "Production source changes: " + ("NONE" if checks["production_sources_unchanged"] else "NOT VERIFIED"),
        "Registry persistence executed: " + ("NO" if certified else "NOT VERIFIED"),
        "Production workflow persistence executed: " + ("NO" if certified else "NOT VERIFIED"),
        "Production Universal Jobs created: " + ("NO" if certified else "NOT VERIFIED"),
        "Production queue claims executed: " + ("NO" if certified else "NOT VERIFIED"),
        "Production handlers executed: " + ("NO" if certified else "NOT VERIFIED"),
        "Live network requests executed: " + ("NO" if certified else "NOT VERIFIED"),
        "Connection verification: REAL COORDINATOR AND MANIFEST / ISOLATED GATEWAY DOUBLE",
        "Protection: DISK MUTATIONS, NETWORK AND PRODUCTION EXECUTION CALLS DENIED",
        "Allowed writes: THIS REPORT AND ANY PREVIOUS-REPORT BACKUP ONLY",
        "Production activation: NOT PERFORMED", "End-to-end pipeline execution: NOT PERFORMED",
        "CERTIFICATION STATUS: " + status, "", "=" * 110, "CHECKS", "=" * 110,
        json.dumps(checks, indent=2, sort_keys=True), "", "FAILED_CHECKS:", json.dumps(failed, indent=2),
        "", "NOT_RUN_CHECKS:", json.dumps(not_run, indent=2),
        "", "=" * 110, "COLLECTIVE EVIDENCE", "=" * 110,
        json.dumps(plain(evidence), indent=2, sort_keys=True), "", "EXECUTION_ERROR:", json.dumps(error, indent=2),
        "", "=" * 110, "CERTIFICATION BOUNDARY", "=" * 110,
        "- Scope: Step 10 coordinator, Step 11 connection and Step 12 manifest collective verification.",
        "- The real manifest/coordinator connection is exercised only after integrity gates pass.",
        "- A changed gateway is accepted only for the exact reviewed registrar adapter with all other code preserved.",
        "- Registrar tests use its real bytecode with isolated in-memory dependencies, not a production kernel or repository.",
        "- No production runtime submission, queue claim or stage handler is exercised.",
        "- This report does not certify pipeline activation, data handoffs or end-to-end execution.",
        "- Those remain Part E: Step 13 collective validation/activation and Step 14 end-to-end certification.",
        "", "=" * 110, "FINAL RESULT", "=" * 110,
        "FINAL RESULT: PART D CONNECTED DOMAIN PIPELINE COORDINATION " + status, "",
    ]
    guard.report_writing = True
    try:
        if report.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = report.with_name(report.name + ".before_" + stamp)
            guard.allowed_report_paths.add(backup.resolve())
            with backup.open("xb") as handle:
                handle.write(report.read_bytes())
        report.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    finally:
        guard.report_writing = False
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed is True else "NOT_RUN" if passed is None else "FAIL"))
    print("CHECKS_PASSED=" + str(sum(value is True for value in checks.values())))
    print("FAILED_CHECK_COUNT=" + str(len(failed)))
    print("NOT_RUN_CHECK_COUNT=" + str(len(not_run)))
    print("REPORT=" + str(report))
    print("PART_D_12_C_STATUS=" + status)
    print("PART_D_STATUS=" + status)
    return 0 if certified else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python _part_d_12_c_final_pipeline_coordination_certification.py ROOT REPORT")
    raise SystemExit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
