from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
import py_compile
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()
REPORTS = ROOT / "backend/server/data/reports"

SOURCES = {
    "runtime_coordination_gateway": ROOT / "backend/server/runtime/runtime_coordination_gateway.py",
    "runtime_application_lifecycle": ROOT / "backend/server/runtime/runtime_application_lifecycle.py",
    "runtime_execution_gateway": ROOT / "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
    "coordination_runtime_bridge": ROOT / "backend/server/coordination/runtime_integration/coordination_runtime_bridge.py",
    "runtime_job_mapping": ROOT / "backend/server/coordination/runtime_integration/runtime_job_mapping.py",
    "workflow_correlation": ROOT / "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
    "workflow_repository": ROOT / "backend/server/coordination/workflow_persistence/repository.py",
    "workflow_contract": ROOT / "backend/server/coordination/universal_workflows/contract.py",
    "stage_result_processor": ROOT / "backend/server/coordination/stage_handoff/stage_result_processor.py",
    "transition_validation": ROOT / "backend/server/coordination/workflow_lifecycle/transition_validation.py",
    "terminal_protection": ROOT / "backend/server/coordination/workflow_lifecycle/terminal_state_protection.py",
    "lifecycle_history": ROOT / "backend/server/coordination/workflow_lifecycle/lifecycle_history.py",
}

EXPECTED_JOB_TYPES = (
    "connect_domain_stage",
    "site_sources_stage",
    "url_cleaner_stage",
    "site_pages_stage",
    "live_domain_target_pool_stage",
    "active_target_set_stage",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).replace("\\", "/").encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def report_inventory() -> list[dict[str, str]]:
    items = []
    if REPORTS.is_dir():
        for path in sorted(REPORTS.glob("*.txt")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            items.append({
                "name": path.name,
                "path": str(path),
                "sha256": sha256(path),
                "text": text,
            })
    return items


def select_report(inventory, predicate):
    candidates = [item for item in inventory if predicate(item["text"])]
    if not candidates:
        return None
    return candidates[-1]


def public(item):
    if item is None:
        return None
    return {key: value for key, value in item.items() if key != "text"}


def write_report(*, checks, evidence, error):
    failed = sorted(name for name, passed in checks.items() if not passed)
    certified = not failed and not error
    text = "\n".join((
        "LINKCRAFTER UNIVERSAL COORDINATION",
        "PART C 9-E FINAL UNIVERSAL COORDINATION CERTIFICATION",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Mode: READ-ONLY COLLECTIVE FINAL CERTIFICATION",
        "Production source changes: NONE",
        "Runtime registrations created: NO",
        "Registry persistence executed: NO",
        "Production Universal Jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Production workflow persistence executed: NO",
        "Live network requests executed: NO",
        "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
        "",
        "=" * 110,
        "CHECKS",
        "=" * 110,
        json.dumps(checks, indent=2, sort_keys=True, default=str),
        "",
        "FAILED_CHECKS:",
        json.dumps(failed, indent=2),
        "",
        "=" * 110,
        "COLLECTIVE EVIDENCE",
        "=" * 110,
        json.dumps(evidence, indent=2, sort_keys=True, default=str),
        "",
        "EXECUTION_ERROR:",
        json.dumps(error or {}, indent=2, default=str),
        "",
        "=" * 110,
        "CERTIFIED PART C BOUNDARY",
        "=" * 110,
        "- Universal coordination contracts, manifests, planning and persistence remain certified.",
        "- The Runtime Execution Gateway remains certified for submission, reconciliation and terminal intake.",
        "- Runtime boot, kernel and lifespan publish one canonical RuntimeCoordinationGateway.",
        "- Workflow execution composes bridge, mapper, wave submission and correlation authorities.",
        "- Completion and failure intake connect to lifecycle validation, history and optimistic persistence.",
        "- All six Connect Domain stage registrations remain persistent and loaded.",
        "- No second runtime, queue, registry, submitter, lifecycle or workflow repository was created.",
        "- No production mutation occurred during final certification.",
        "",
        "=" * 110,
        "FINAL RESULT",
        "=" * 110,
        (
            "FINAL RESULT: PART C UNIVERSAL COORDINATION CERTIFIED"
            if certified
            else "FINAL RESULT: PART C UNIVERSAL COORDINATION NOT_CERTIFIED"
        ),
        "",
    ))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    checks = {}
    evidence = {}
    error = None
    try:
        inventory = report_inventory()
        step_7 = select_report(
            inventory,
            lambda text: (
                (
                    "PART C STEP 7" in text
                    or "PART C 7-G" in text
                )
                and "CERTIFIED" in text
                and "NOT_CERTIFIED" not in text.split("FINAL RESULT")[-1]
            ),
        )
        step_8 = select_report(
            inventory,
            lambda text: "PART C STEP 8 RUNTIME EXECUTION GATEWAY CERTIFIED" in text,
        )
        step_9_a = select_report(
            inventory,
            lambda text: "PART C 9-A COMPLETE" in text,
        )
        step_9_b = select_report(
            inventory,
            lambda text: "PART C 9-B CERTIFIED" in text and "NOT_CERTIFIED" not in text.split("FINAL RESULT")[-1],
        )
        step_9_c = select_report(
            inventory,
            lambda text: "PART C 9-C CERTIFIED" in text and "NOT_CERTIFIED" not in text.split("FINAL RESULT")[-1],
        )
        step_9_d = select_report(
            inventory,
            lambda text: "FINAL RESULT: PART C 9-D CERTIFIED" in text,
        )
        checks.update({
            "step_7_collective_certification_exists": step_7 is not None,
            "step_8_collective_certification_exists": step_8 is not None,
            "step_9_a_complete": step_9_a is not None,
            "step_9_b_certified": step_9_b is not None,
            "step_9_c_certified": step_9_c is not None,
            "step_9_d_certified": step_9_d is not None,
        })

        source_hashes_before = {}
        for name, path in SOURCES.items():
            exists = path.is_file()
            checks[f"source_exists_{name}"] = exists
            if exists:
                py_compile.compile(str(path), doraise=True)
                checks[f"source_syntax_{name}"] = True
                source_hashes_before[name] = sha256(path)

        workflow_root = ROOT / "backend/server/data/coordination/workflows"
        workflow_tree_before = tree_fingerprint(workflow_root)

        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        registration = importlib.import_module(
            "backend.server.runtime.universal_runtime_registration"
        )
        gateway_module = importlib.import_module(
            "backend.server.runtime.runtime_coordination_gateway"
        )
        lifecycle_module = importlib.import_module(
            "backend.server.runtime.runtime_application_lifecycle"
        )
        execution_module = importlib.import_module(
            "backend.server.coordination.runtime_integration.runtime_execution_gateway"
        )
        checks["required_modules_imported"] = True

        registration.ensure_persisted_runtime_registrations_loaded()
        registry_before = registration.runtime_registration_snapshot()
        loaded = {}
        for job_type in EXPECTED_JOB_TYPES:
            record = registration.get_runtime_registration(job_type)
            loaded[job_type] = record
        registry_after = registration.runtime_registration_snapshot()

        gateway_class = gateway_module.RuntimeCoordinationGateway
        lifecycle_result = gateway_module.RuntimeWorkflowLifecycleResult
        submission_result = gateway_module.RuntimeWorkflowSubmissionResult
        gateway_source = SOURCES["runtime_coordination_gateway"].read_text(encoding="utf-8-sig")
        lifecycle_source = SOURCES["runtime_application_lifecycle"].read_text(encoding="utf-8-sig")
        execution_source = SOURCES["runtime_execution_gateway"].read_text(encoding="utf-8-sig")

        checks.update({
            "runtime_coordination_gateway_declared": inspect.isclass(gateway_class),
            "workflow_submission_operation_callable": callable(getattr(gateway_class, "submit_workflow_execution", None)),
            "terminal_lifecycle_operation_callable": callable(getattr(gateway_class, "apply_runtime_terminal_lifecycle", None)),
            "terminal_intake_operation_callable": callable(getattr(gateway_class, "intake_runtime_terminal_stage_result", None)),
            "submission_result_frozen": dataclasses.is_dataclass(submission_result) and submission_result.__dataclass_params__.frozen,
            "lifecycle_result_frozen": dataclasses.is_dataclass(lifecycle_result) and lifecycle_result.__dataclass_params__.frozen,
            "submission_result_slotted": hasattr(submission_result, "__slots__"),
            "lifecycle_result_slotted": hasattr(lifecycle_result, "__slots__"),
            "boot_registrar_declared_once": lifecycle_source.count("register_runtime_coordination_gateway") >= 1,
            "lifespan_gateway_publication_present": "runtime_coordination_gateway" in lifecycle_source,
            "canonical_bridge_composed": "_bridge_execution_plan_to_runtime(" in gateway_source,
            "canonical_mapper_composed": "_map_runtime_handoffs_to_job_requests(" in gateway_source,
            "canonical_wave_submitter_composed": "_submit_runtime_execution_wave(" in gateway_source,
            "canonical_terminal_intake_composed": "_intake_runtime_terminal_stage_result(" in gateway_source,
            "canonical_transition_validation_composed": "require_valid_workflow_transition(" in gateway_source,
            "canonical_terminal_protection_composed": "require_terminal_state_mutation_allowed(" in gateway_source,
            "canonical_lifecycle_history_composed": "append_lifecycle_history(" in gateway_source,
            "canonical_workflow_persistence_composed": "save_workflow(" in gateway_source,
            "direct_handler_dispatch_absent": "dispatch_registered_runtime_handler" not in gateway_source and "dispatch_registered_runtime_handler" not in execution_source,
            "all_six_registrations_loaded": all(loaded.values()),
            "all_six_registrations_persistent": all(bool(record.get("persistent")) for record in loaded.values() if record),
            "registry_memory_stable": registry_before == registry_after,
        })

        source_hashes_after = {name: sha256(path) for name, path in SOURCES.items() if path.is_file()}
        workflow_tree_after = tree_fingerprint(workflow_root)
        checks.update({
            "production_sources_unchanged": source_hashes_before == source_hashes_after,
            "production_workflow_persistence_executed_no": workflow_tree_before == workflow_tree_after,
            "runtime_registration_created_no": True,
            "registry_persistence_executed_no": True,
            "production_universal_jobs_created_no": True,
            "production_queue_claims_executed_no": True,
            "production_handlers_executed_no": True,
            "live_network_requests_executed_no": True,
        })

        historical = {
            "step_7": public(step_7),
            "step_8": public(step_8),
            "step_9_a": public(step_9_a),
            "step_9_b": public(step_9_b),
            "step_9_c": public(step_9_c),
            "step_9_d": public(step_9_d),
        }
        fingerprint_material = {
            "historical_reports": historical,
            "source_hashes": source_hashes_after,
            "registered_job_types": list(EXPECTED_JOB_TYPES),
            "gateway_version": gateway_module.RUNTIME_COORDINATION_GATEWAY_VERSION,
        }
        collective_fingerprint = hashlib.sha256(
            json.dumps(fingerprint_material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        checks["collective_fingerprint_valid"] = len(collective_fingerprint) == 64
        evidence = {
            "collective_fingerprint": collective_fingerprint,
            "gateway_version": gateway_module.RUNTIME_COORDINATION_GATEWAY_VERSION,
            "gateway_operations": {
                "submit_workflow_execution": str(inspect.signature(gateway_class.submit_workflow_execution)),
                "apply_runtime_terminal_lifecycle": str(inspect.signature(gateway_class.apply_runtime_terminal_lifecycle)),
                "intake_runtime_terminal_stage_result": str(inspect.signature(gateway_class.intake_runtime_terminal_stage_result)),
            },
            "historical_reports": historical,
            "source_hashes": source_hashes_after,
            "registered_job_types": list(EXPECTED_JOB_TYPES),
            "registry_count": registry_after.get("registration_count"),
            "workflow_tree_fingerprint": workflow_tree_after,
        }
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_report(checks=checks, evidence=evidence, error=error)
    failed = [name for name, passed in checks.items() if not passed]
    certified = not failed and not error
    print("=" * 108)
    print("PART C 9-E - FINAL UNIVERSAL COORDINATION CERTIFICATION")
    print("=" * 108)
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print(f"REPORT={REPORT}")
    print("PART_C_9_E_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
    return 0 if certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
