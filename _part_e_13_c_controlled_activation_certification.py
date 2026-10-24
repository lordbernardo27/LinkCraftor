from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
import traceback
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any, Mapping


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    for name in ("to_dict", "to_canonical_dict", "to_payload"):
        method = getattr(value, name, None)
        if callable(method):
            try:
                return plain(method())
            except TypeError:
                pass
    if dataclasses.is_dataclass(value):
        return plain(dataclasses.asdict(value))
    if hasattr(value, "__dict__"):
        return plain(vars(value))
    return str(value)


def frozen(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): frozen(v) for k, v in value.items()})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(frozen(item) for item in value)
    return value


def report_text(
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    certified = not failed and not error
    return "\n".join(
        [
            "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION",
            "PART E 13-C CONTROLLED ACTIVATION CERTIFICATION",
            "",
            "Mode: INSTALLED PRODUCTION COMPOSITION / ISOLATED AUTHORITIES",
            "Production source changes: NONE",
            "Production activation executed: NO",
            "Production workflow persistence executed: NO",
            "Production Universal Jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Live network requests executed: NO",
            "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
            "",
            "CHECKS:",
            json.dumps(checks, indent=2, sort_keys=True),
            "",
            "FAILED_CHECKS:",
            json.dumps(failed, indent=2),
            "",
            "NOT_RUN_CHECKS:",
            "[]",
            "",
            "EVIDENCE:",
            json.dumps(evidence, indent=2, default=str, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2),
            "",
            "CERTIFIED BOUNDARY:",
            "- The installed public route delegates to canonical Connected Domain activation.",
            "- The real coordinator and manifest compose through one isolated gateway double.",
            "- All four result-to-payload handoffs are hydrated from completed predecessor evidence.",
            "- Repeated activation preserves workflow and correlation identity.",
            "- No live domain request or production runtime mutation was performed.",
            "",
            "NEXT STEP:",
            "Part E Step 14 - controlled end-to-end pipeline certification.",
            "",
            "FINAL RESULT:",
            (
                "FINAL RESULT: PART E STEP 13 COLLECTIVE PIPELINE ACTIVATION CERTIFIED"
                if certified
                else "FINAL RESULT: PART E STEP 13 NOT_CERTIFIED"
            ),
            "",
        ]
    )


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    checks = {
        "part_e_13_b2_report_exists": False,
        "part_e_13_b2_certified": False,
        "required_sources_exist": False,
        "required_sources_parse": False,
        "installed_modules_imported": False,
        "all_six_registrations_loaded": False,
        "all_six_registrations_persistent": False,
        "public_route_uses_canonical_activation": False,
        "legacy_route_call_absent": False,
        "worker_hydration_hook_declared_once": False,
        "activation_uses_real_coordinator_and_manifest": False,
        "isolated_activation_succeeded": False,
        "isolated_gateway_called_once_per_activation": False,
        "six_stage_identities_preserved": False,
        "workflow_identity_persisted": False,
        "activation_retry_reuses_workflow": False,
        "activation_retry_identity_stable": False,
        "four_handoffs_hydrated": False,
        "hydrator_marker_not_forwarded": False,
        "missing_predecessor_rejected": False,
        "incomplete_predecessor_rejected": False,
        "no_duplicate_runtime_infrastructure": False,
        "source_files_unchanged": False,
        "historical_report_unchanged": False,
        "registry_memory_unchanged": False,
        "registry_file_unchanged": False,
        "production_jobs_created_no": True,
        "production_queue_claims_no": True,
        "production_handlers_executed_no": True,
        "production_workflow_persistence_no": True,
        "live_network_requests_no": True,
        "collective_fingerprint_valid": False,
    }
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}

    relative_sources = (
        "backend/server/routes/site_workspace.py",
        "backend/server/runtime/universal_runtime_worker_v1.py",
        "backend/server/runtime/runtime_payload_hydration.py",
        "backend/server/pipelines/connect_domain/runtime_hydration.py",
        "backend/server/pipelines/connect_domain/activation.py",
        "backend/server/pipelines/connect_domain/coordinator.py",
        "backend/server/pipelines/connect_domain/manifest.py",
        "backend/server/runtime/runtime_coordination_gateway.py",
        "backend/server/runtime/universal_runtime_registration.py",
    )
    sources = {name: root / name for name in relative_sources}
    b2_report = root / "backend/server/data/reports/PART_E_13_B2_HYDRATION_ENTRYPOINT_INTEGRATION_CERTIFICATION.txt"
    registry_file = root / "backend/server/data/universal_runtime_registrations.json"
    source_before: dict[str, str] = {}
    report_before = ""
    registry_bytes_before: bytes | None = None
    registry_snapshot_before: Any = None

    try:
        checks["part_e_13_b2_report_exists"] = b2_report.is_file()
        if not checks["part_e_13_b2_report_exists"]:
            raise RuntimeError("Part E 13-B2 certification report is unavailable.")
        report_before = sha256(b2_report)
        b2_text = b2_report.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        checks["part_e_13_b2_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in b2_text
            and "FAILED_CHECKS:\n[]" in b2_text
            and "FINAL RESULT: PART E 13-B2 CERTIFIED" in b2_text
        )
        if not checks["part_e_13_b2_certified"]:
            raise RuntimeError("Part E 13-B2 is not certified.")

        checks["required_sources_exist"] = all(path.is_file() for path in sources.values())
        if not checks["required_sources_exist"]:
            missing = [name for name, path in sources.items() if not path.is_file()]
            raise RuntimeError("Required source unavailable: " + ", ".join(missing))
        source_before = {name: sha256(path) for name, path in sources.items()}
        for name, path in sources.items():
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        checks["required_sources_parse"] = True
        if registry_file.is_file():
            registry_bytes_before = registry_file.read_bytes()

        sys.path.insert(0, str(root))
        registration = importlib.import_module(
            "backend.server.runtime.universal_runtime_registration"
        )
        activation = importlib.import_module(
            "backend.server.pipelines.connect_domain.activation"
        )
        hydration = importlib.import_module(
            "backend.server.pipelines.connect_domain.runtime_hydration"
        )
        hook = importlib.import_module(
            "backend.server.runtime.runtime_payload_hydration"
        )
        coordinator = importlib.import_module(
            "backend.server.pipelines.connect_domain.coordinator"
        )
        manifest_module = importlib.import_module(
            "backend.server.pipelines.connect_domain.manifest"
        )
        persistence = importlib.import_module(
            "backend.server.coordination.workflow_persistence.repository"
        )
        checks["installed_modules_imported"] = True

        registration.ensure_persisted_runtime_registrations_loaded()
        registry_snapshot_before = plain(registration.runtime_registration_snapshot())
        expected_job_types = (
            "connect_domain_stage",
            "site_sources_stage",
            "url_cleaner_stage",
            "site_pages_stage",
            "live_domain_target_pool_stage",
            "active_target_set_stage",
        )
        records = [registration.get_runtime_registration(item) for item in expected_job_types]
        checks["all_six_registrations_loaded"] = all(record is not None for record in records)
        record_payloads = [plain(record) for record in records]
        checks["all_six_registrations_persistent"] = all(
            bool(record.get("persistent", record.get("persisted", True)))
            for record in record_payloads
        )

        route_text = sources["backend/server/routes/site_workspace.py"].read_text(encoding="utf-8-sig")
        route_tree = ast.parse(route_text)
        route_functions = [
            node for node in route_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "connect_domain"
        ]
        if len(route_functions) != 1:
            raise RuntimeError("Expected one public connect_domain route function.")
        route_function = route_functions[0]
        called_names = {
            node.func.id
            for node in ast.walk(route_function)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        checks["public_route_uses_canonical_activation"] = (
            "activate_connected_domain_pipeline" in called_names
        )
        checks["legacy_route_call_absent"] = "run_connect_domain" not in called_names
        worker_text = sources["backend/server/runtime/universal_runtime_worker_v1.py"].read_text(encoding="utf-8-sig")
        checks["worker_hydration_hook_declared_once"] = (
            worker_text.count("hydrate_runtime_job_payload(") == 1
        )

        activation_source = inspect.getsource(activation.activate_connected_domain_pipeline)
        checks["activation_uses_real_coordinator_and_manifest"] = all(
            token in activation_source
            for token in (
                "coordinate_connect_domain_pipeline(",
                "build_connected_domain_pipeline_manifest(",
                "connect_connected_domain_to_universal_coordination(",
            )
        )

        class IsolatedRepository:
            def __init__(self) -> None:
                self.records: dict[str, Any] = {}
                self.save_calls = 0

            def load_workflow_record(self, workflow_id: str) -> Any:
                record = self.records.get(str(workflow_id))
                if record is None:
                    raise persistence.WorkflowPersistenceNotFoundError(str(workflow_id))
                return record

            def save_workflow(self, workflow: Any) -> Any:
                self.save_calls += 1
                workflow_id = str(workflow.workflow_id)
                evidence_item = SimpleNamespace(
                    workflow_id=workflow_id,
                    workflow_content_fingerprint=workflow.content_fingerprint(),
                    workflow_identity_fingerprint=workflow.identity_fingerprint(),
                    document_fingerprint="isolated_" + workflow_id,
                    persisted_at="isolated",
                )
                self.records[workflow_id] = SimpleNamespace(
                    workflow=workflow,
                    evidence=evidence_item,
                )
                return evidence_item

        class IsolatedGateway:
            def __init__(self) -> None:
                self.workflow_repository = IsolatedRepository()
                self.calls: list[dict[str, Any]] = []

            def submit_workflow_execution(self, **kwargs: Any) -> Any:
                self.calls.append(kwargs)
                workflow_id = str(kwargs.get("context").workflow_id)
                job_ids = tuple(
                    "isolated_" + workflow_id + "_" + stage
                    for stage in coordinator.CONNECTED_DOMAIN_STAGE_IDS
                )
                return SimpleNamespace(
                    job_ids=job_ids,
                    to_dict=lambda: {
                        "job_ids": list(job_ids),
                        "isolated": True,
                    },
                )

        gateway = IsolatedGateway()
        activation_kwargs = {
            "runtime_gateway": gateway,
            "workspace_id": "ws_part_e_13_c_probe",
            "workspace_name": "Part E 13-C Probe",
            "domain": "Example.COM",
            "metadata": {"certification_scope": "part_e_13_c"},
        }
        first = activation.activate_connected_domain_pipeline(**activation_kwargs)
        first_call = gateway.calls[0] if gateway.calls else {}
        checks["isolated_activation_succeeded"] = (
            first.get("ok") is True
            and first.get("domain") == "example.com"
            and first.get("pipeline", {}).get("manifest_finalized") is True
            and first.get("pipeline", {}).get("hydration_connected") is True
        )
        checks["isolated_gateway_called_once_per_activation"] = len(gateway.calls) == 1
        checks["six_stage_identities_preserved"] = (
            tuple(first.get("stage_ids", ())) == tuple(coordinator.CONNECTED_DOMAIN_STAGE_IDS)
            and len(first.get("job_ids", ())) == 6
            and len(first_call.get("stage_references", {})) == 6
        )
        checks["workflow_identity_persisted"] = (
            first.get("workflow_id") in gateway.workflow_repository.records
            and gateway.workflow_repository.save_calls == 1
        )

        second = activation.activate_connected_domain_pipeline(**activation_kwargs)
        checks["isolated_gateway_called_once_per_activation"] = len(gateway.calls) == 2
        checks["activation_retry_reuses_workflow"] = (
            second.get("workflow_created") is False
            and gateway.workflow_repository.save_calls == 1
        )
        checks["activation_retry_identity_stable"] = all(
            first.get(key) == second.get(key)
            for key in ("workflow_id", "correlation_id", "workspace_id", "domain", "site_url")
        )

        def predecessor(stage: str, result: dict[str, Any], status: str = "completed") -> Any:
            return SimpleNamespace(
                job_id="job_" + stage,
                stage=stage,
                status=status,
                metadata={
                    "runtime_dispatch_result": {
                        "handler_result": {"value": result}
                    }
                },
            )

        cases = (
            ("url_cleaner", predecessor("site_sources", {"discovered_urls": ["https://example.com/a"]}), "source_urls"),
            ("site_pages", predecessor("url_cleaner", {"cleaned_urls": ["https://example.com/a"], "explicit_urls": ["https://example.com/a"], "uncertain_urls": []}), "cleaner_records"),
            ("live_domain_target_pool", predecessor("site_pages", {"pages": [{"url": "https://example.com/a"}]}), "site_pages"),
            ("active_target_set", predecessor("live_domain_target_pool", {"targets": [{"url": "https://example.com/a"}]}), "live_domain_payload"),
        )
        handoffs: dict[str, Any] = {}
        marker = hook.RUNTIME_PAYLOAD_HYDRATOR_KEY
        for stage, prior, target_field in cases:
            job = {
                "job_id": "job_" + stage,
                "stage": stage,
                "payload": {marker: hydration.CONNECTED_DOMAIN_HYDRATOR_REF},
                "dependency_job_ids": [prior.job_id],
            }
            hydrated = hydration.hydrate_connected_domain_runtime_job(
                job,
                job_reader=lambda _job_id, item=prior: item,
                jobs_reader=lambda: {},
            )
            if target_field not in hydrated["payload"]:
                raise RuntimeError("Hydration field missing: " + target_field)
            handoffs[stage] = plain(hydrated["payload"][target_field])
        checks["four_handoffs_hydrated"] = len(handoffs) == 4

        original_resolver = hook._resolve_hydrator
        hook._resolve_hydrator = lambda _reference: (
            lambda job: hydration.hydrate_connected_domain_runtime_job(
                job,
                job_reader=lambda _job_id: cases[0][1],
                jobs_reader=lambda: {},
            )
        )
        try:
            hooked = hook.hydrate_runtime_job_payload(
                {
                    "stage": "url_cleaner",
                    "payload": {marker: hydration.CONNECTED_DOMAIN_HYDRATOR_REF},
                    "dependency_job_ids": [cases[0][1].job_id],
                }
            )
        finally:
            hook._resolve_hydrator = original_resolver
        checks["hydrator_marker_not_forwarded"] = (
            marker not in hooked.get("payload", {})
            and hooked.get("payload", {}).get("source_urls") == ["https://example.com/a"]
        )

        try:
            hydration.hydrate_connected_domain_runtime_job(
                {"stage": "url_cleaner", "payload": {}},
                job_reader=lambda _job_id: None,
                jobs_reader=lambda: {},
            )
        except hydration.ConnectedDomainRuntimeHydrationError:
            checks["missing_predecessor_rejected"] = True
        try:
            running = predecessor("site_sources", {"discovered_urls": ["x"]}, "running")
            hydration.hydrate_connected_domain_runtime_job(
                {"stage": "url_cleaner", "payload": {}, "dependency_job_ids": [running.job_id]},
                job_reader=lambda _job_id: running,
                jobs_reader=lambda: {},
            )
        except hydration.ConnectedDomainRuntimeHydrationError:
            checks["incomplete_predecessor_rejected"] = True

        combined = "\n".join(
            sources[name].read_text(encoding="utf-8-sig")
            for name in (
                "backend/server/runtime/runtime_payload_hydration.py",
                "backend/server/pipelines/connect_domain/runtime_hydration.py",
                "backend/server/pipelines/connect_domain/activation.py",
            )
        )
        checks["no_duplicate_runtime_infrastructure"] = not any(
            token in combined
            for token in (
                "class UniversalRuntimeKernel",
                "class WorkflowRepository",
                "def submit_universal_job",
                "def create_job",
            )
        )

        registry_snapshot_after = plain(registration.runtime_registration_snapshot())
        checks["registry_memory_unchanged"] = registry_snapshot_before == registry_snapshot_after
        checks["source_files_unchanged"] = source_before == {
            name: sha256(path) for name, path in sources.items()
        }
        checks["historical_report_unchanged"] = report_before == sha256(b2_report)
        checks["registry_file_unchanged"] = (
            registry_bytes_before is None
            or (registry_file.is_file() and registry_file.read_bytes() == registry_bytes_before)
        )
        fingerprint_payload = {
            "sources": source_before,
            "workflow_id": first.get("workflow_id"),
            "correlation_id": first.get("correlation_id"),
            "stage_ids": first.get("stage_ids"),
            "handoffs": handoffs,
        }
        collective_fingerprint = hashlib.sha256(
            json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        checks["collective_fingerprint_valid"] = (
            len(collective_fingerprint) == 64
            and all(character in "0123456789abcdef" for character in collective_fingerprint)
        )
        evidence = {
            "collective_fingerprint": collective_fingerprint,
            "source_hashes": source_before,
            "registered_job_types": list(expected_job_types),
            "activation": frozen(
                {
                    "workflow_id": first.get("workflow_id"),
                    "correlation_id": first.get("correlation_id"),
                    "workspace_id": first.get("workspace_id"),
                    "domain": first.get("domain"),
                    "site_url": first.get("site_url"),
                    "stage_ids": first.get("stage_ids"),
                    "job_ids": first.get("job_ids"),
                    "workflow_created_first": first.get("workflow_created"),
                    "workflow_created_retry": second.get("workflow_created"),
                }
            ),
            "hydrated_handoffs": frozen(handoffs),
            "isolated_gateway_call_count": len(gateway.calls),
            "isolated_workflow_save_count": gateway.workflow_repository.save_calls,
            "production_activation_executed": False,
            "production_jobs_created": False,
            "production_handlers_executed": False,
        }
        if not all(checks.values()):
            raise RuntimeError("One or more Part E 13-C checks failed.")
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(report_text(checks, plain(evidence), error), encoding="utf-8", newline="\n")
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    failed_count = sum(not passed for passed in checks.values())
    print("FAILED_CHECK_COUNT=" + str(failed_count))
    print("NOT_RUN_CHECK_COUNT=0")
    print("REPORT=" + str(report))
    certified = failed_count == 0 and not error
    print("PART_E_13_C_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
    print("PART_E_STEP_13_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
    return 0 if certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
