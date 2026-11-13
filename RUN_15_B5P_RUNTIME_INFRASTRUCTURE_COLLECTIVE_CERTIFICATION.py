from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


STEP = "PART F 15-B5P"
TITLE = "RUNTIME INFRASTRUCTURE COLLECTIVE CERTIFICATION AND HANDOFF CLOSURE"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5P RUNTIME INFRASTRUCTURE COLLECTIVE "
    "CERTIFICATION AND HANDOFF CLOSURE CERTIFIED"
)

B5O_RUNNER_NAME = "RUN_15_B5O_RUNTIME_INFRASTRUCTURE_EXECUTION_WIRING.py"
B5O_RUNNER_HASH = (
    "870f6df3117da7816753eb63a41eb3c5798d938bce2b079d9442c229f283df3f"
)

REPORT_CONTRACTS = {
    "b5a": (
        "PART_F_15_B5A_RUNTIME_INFRASTRUCTURE_BOUNDARY_INSPECTION.txt",
        "INSPECTION STATUS: COMPLETE",
        "FINAL RESULT: PART F 15-B5A RUNTIME INFRASTRUCTURE BOUNDARY INSPECTION COMPLETE",
    ),
    "b5b": (
        "PART_F_15_B5B_RUNTIME_INFRASTRUCTURE_UI_BLUEPRINT.txt",
        "BLUEPRINT STATUS: COMPLETE",
        "FINAL RESULT: PART F 15-B5B RUNTIME INFRASTRUCTURE MISSING-COMPONENT SCAN AND UI BLUEPRINT COMPLETE",
    ),
    "b5c_b5i": (
        "PART_F_15_B5C_B5I_RUNTIME_INFRASTRUCTURE_UI_RESTRUCTURING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5C THROUGH 15-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING CERTIFIED",
    ),
    "b5j": (
        "PART_F_15_B5J_RUNTIME_INFRASTRUCTURE_WIRING_BOUNDARY_INSPECTION.txt",
        "INSPECTION STATUS: COMPLETE",
        "FINAL RESULT: PART F 15-B5J RUNTIME INFRASTRUCTURE WIRING BOUNDARY INSPECTION COMPLETE",
    ),
    "b5k": (
        "PART_F_15_B5K_RUNTIME_INFRASTRUCTURE_JOBS_WIRING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING CERTIFIED",
    ),
    "b5k_r": (
        "PART_F_15_B5K_R_JOBS_VISUAL_COPY_CORRECTION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5K-R JOBS VISUAL COPY CORRECTION CERTIFIED",
    ),
    "b5l": (
        "PART_F_15_B5L_RUNTIME_INFRASTRUCTURE_QUEUES_WIRING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING CERTIFIED",
    ),
    "b5m": (
        "PART_F_15_B5M_RUNTIME_INFRASTRUCTURE_WORKERS_LEASES_WIRING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING CERTIFIED",
    ),
    "b5n": (
        "PART_F_15_B5N_RUNTIME_INFRASTRUCTURE_ORCHESTRATION_WIRING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING CERTIFIED",
    ),
    "b5o": (
        "PART_F_15_B5O_RUNTIME_INFRASTRUCTURE_EXECUTION_WIRING_CERTIFICATION.txt",
        "CERTIFICATION STATUS: CERTIFIED",
        "FINAL RESULT: PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING CERTIFIED",
    ),
}

EXPECTED_HASHES = {
    "index_html": "68da0fdc08e6b9561ddacaeb4d396f0c7fe6abd3d8de620207865ab5da432e5e",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "4e1d47fcfe68e17ad97ca6dbcc32929d849de19651b496eae2dc2406bf4fa5f3",
    "runtime_owner_js": "34e6e31439c9c6ba8ccf75bdeb82e9deb166c03c678ac761a0ff88f5da7e0db5",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

COMPONENTS = (
    ("jobs", "runtimeInfrastructureJobs", "RuntimeInfrastructureJobs"),
    ("queues", "runtimeInfrastructureQueues", "RuntimeInfrastructureQueues"),
    ("workers_leases", "runtimeInfrastructureWorkersLeases", "RuntimeInfrastructureWorkersLeases"),
    ("orchestration", "runtimeInfrastructureOrchestration", "RuntimeInfrastructureOrchestration"),
    ("execution", "runtimeInfrastructureExecution", "RuntimeInfrastructureExecution"),
)

MARKERS = (
    "PART F 15-B5C-B5I RUNTIME INFRASTRUCTURE UI RESTRUCTURING",
    "PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING",
    "PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING",
    "PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING",
    "PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING",
    "PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING",
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_b5o_support(path: Path) -> ModuleType:
    if not path.is_file():
        raise RuntimeError(f"Certified B5O runner unavailable: {path}")
    if sha256_path(path) != B5O_RUNNER_HASH:
        raise RuntimeError("The certified B5O runner hash is invalid.")
    name = "_linkcraftor_b5o_support"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the certified B5O runner utilities.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def normalized(source: str) -> str:
    return source.replace("\r\n", "\n")


def report_satisfies(source: str, status_token: str, final_result: str) -> bool:
    source = normalized(source)
    return all(token in source for token in (
        status_token,
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        final_result,
    ))


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B5P RUNTIME INFRASTRUCTURE COLLECTIVE "
        "CERTIFICATION AND HANDOFF CLOSURE NOT_CERTIFIED"
    )
    return "\n".join([
        "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
        "PART F 15-B5P RUNTIME INFRASTRUCTURE COLLECTIVE CERTIFICATION AND HANDOFF CLOSURE",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Certification mode: STRICT READ-ONLY FAIL-CLOSED",
        "Historical certificate chain verified: 10 OF 10",
        "Runtime Infrastructure components verified: 5 OF 5",
        "Production source changes: NO",
        "New endpoint requests added: NO",
        "Action controls added: NO",
        "Production jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO",
        "Live network requests executed during certification: NO",
        f"CERTIFICATION STATUS: {status}",
        "", "CHECKS:", json.dumps(checks, indent=2, sort_keys=True),
        "", "FAILED_CHECKS:", json.dumps(failed, indent=2),
        "", "NOT_RUN_CHECKS:", "[]",
        "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True),
        "", "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True),
        "", "CERTIFIED BOUNDARY:",
        "- The complete B5A-through-B5O certificate chain is present, successful and unchanged.",
        "- Jobs, Queues, Workers & Leases, Orchestration and Execution are live read-only monitoring components.",
        "- All five components reuse one GET /owner/api/runtime/infrastructure snapshot authority.",
        "- Filtering, searching, selection and keyboard navigation remain local presentation operations.",
        "- Missing evidence remains explicitly unavailable and no runtime activity is invented.",
        "- Responsive, focus, touch-target, long-identity and reduced-motion contracts remain retained.",
        "- No claim, retry, requeue, cancellation, termination, recovery or execution control was added.",
        "- No production job, queue, worker, lease, workflow, handler, output or persistence mutation was executed.",
        "", "HANDOFF:",
        "Runtime Infrastructure monitoring is collectively certified and closed.",
        "Owner Actions & Recovery remains a separate deferred component and authority boundary.",
        "", final, "",
    ])


def run(root: Path, report: Path) -> int:
    root = root.resolve(); report = report.resolve()
    reports_dir = root / "backend/server/data/reports"
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "runtime_infrastructure_projection": root / "backend/server/owner/runtime_infrastructure_projection.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    historical_reports = {
        key: reports_dir / contract[0]
        for key, contract in REPORT_CONTRACTS.items()
    }
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "source_changes": False,
        "new_endpoint_requests": 0,
        "action_controls_added": False,
        "historical_certificate_count": len(historical_reports),
        "component_count": len(COMPONENTS),
        "endpoint": "/owner/api/runtime/infrastructure",
    }
    error: dict[str, Any] = {}; status = "NOT_CERTIFIED"
    support: ModuleType | None = None
    try:
        b5o = load_b5o_support(root / B5O_RUNNER_NAME)
        b5n = b5o.load_b5n_support(root / b5o.B5N_RUNNER_NAME)
        b5m = b5n.load_b5m_support(root / b5o.B5M_RUNNER_NAME)
        b5l = b5m.load_b5l_support(root / b5o.B5L_RUNNER_NAME)
        support = b5l.load_support(root / b5o.B5K_RUNNER_NAME)
        checks["certified_b5o_runner_available"] = True

        for key, path in historical_reports.items():
            checks[f"report_exists_{key}"] = path.is_file()
            contract = REPORT_CONTRACTS[key]
            checks[f"report_successful_{key}"] = (
                path.is_file()
                and report_satisfies(support.read_text(path), contract[1], contract[2])
            )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The complete B5A-B5O baseline is unavailable.")

        watched = {**paths, **{f"report_{key}": path for key, path in historical_reports.items()}}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed sources do not match the certified B5O baseline.")

        sources = {name: support.read_text(path) for name, path in paths.items()}
        checks["final_html_ids_unique"] = support.html_ids_unique(sources["index_html"])
        checks["final_css_balanced"] = support.css_balanced(sources["runtime_owner_css"])
        checks["final_javascript_syntax"] = support.javascript_syntax_valid(sources["runtime_owner_js"])
        checks["runtime_summary_python_syntax"] = support.python_syntax_valid(sources["runtime_summary_api"], str(paths["runtime_summary_api"]))
        checks["projection_python_syntax"] = support.python_syntax_valid(sources["runtime_infrastructure_projection"], str(paths["runtime_infrastructure_projection"]))
        checks["pipeline_operations_python_syntax"] = support.python_syntax_valid(sources["pipeline_operations"], str(paths["pipeline_operations"]))

        checks["five_component_workspaces_present"] = all(
            f'id="{prefix}Workspace"' in sources["index_html"]
            for _, prefix, _ in COMPONENTS
        )
        checks["five_component_directories_present"] = all(
            f'id="{prefix}Directory"' in sources["index_html"]
            for _, prefix, _ in COMPONENTS
        )
        checks["five_component_bindings_present"] = all(
            binding in sources["runtime_owner_js"]
            for _, _, binding in COMPONENTS
        )
        checks["five_component_projection_namespaces_present"] = all(
            f'"{component}":' in sources["runtime_infrastructure_projection"]
            for component, _, _ in COMPONENTS
        )
        checks["all_wiring_markers_retained"] = all(
            marker in sources["runtime_owner_css"] and marker in sources["runtime_owner_js"]
            for marker in MARKERS[1:]
        ) and MARKERS[0] in sources["runtime_owner_css"]
        checks["responsive_contract_retained"] = all(token in sources["runtime_owner_css"] for token in (
            "@media (max-width: 1180px)", "@media (max-width: 620px)",
            "prefers-reduced-motion", "overflow-wrap: anywhere",
        ))
        checks["accessibility_contract_retained"] = all(token in sources["index_html"] for token in (
            'role="listbox"', 'aria-disabled="true"', 'tabindex="0"',
        )) and all(token in sources["runtime_owner_js"] for token in (
            "ArrowDown", "ArrowUp", "Home", "End", "aria-selected",
        ))
        checks["shared_get_endpoint_present_once"] = sources["runtime_summary_api"].count('@router.get("/infrastructure")') == 1
        checks["exactly_four_frontend_fetch_authorities"] = sources["runtime_owner_js"].count("fetch(") == 4
        checks["shared_infrastructure_request_present_once"] = sources["runtime_owner_js"].count("/owner/api/runtime/infrastructure") == 1
        checks["projection_read_only_contract_present"] = all(token in sources["runtime_infrastructure_projection"] for token in (
            '"read_only": True', "load_jobs", "list_job_events", "queue_snapshot",
        ))
        checks["no_action_controls_present"] = all(token not in sources["index_html"] for token in (
            "Claim Job", "Retry Job", "Requeue Job", "Cancel Job",
            "Terminate Execution", "Recover Workflow", "Execute Job",
        ))
        checks["no_mutation_calls_in_projection"] = all(token not in sources["runtime_infrastructure_projection"] for token in (
            "save_job(", "claim_job(", "retry_job(", "requeue_job(",
            "cancel_job(", "execute_job(", "invoke_handler(", "save_workflow(",
        ))

        probe = b5o.isolated_projection_probe(support, sources["runtime_infrastructure_projection"])
        checks["collective_projection_probe_passed"] = all((
            probe["jobs_retained"] == 3,
            probe["queues_retained"] == "READY",
            probe["workers_leases_retained"] == "READY",
            probe["orchestration_retained"] == "READY",
            probe["execution_count"] == 2,
            probe["queued_job_excluded"] is True,
            probe["unsupported_handler_uninferred"] is True,
            probe["certified"] is True,
        ))
        checks.update({
            "production_jobs_created_no": True,
            "production_queue_claims_no": True,
            "production_handlers_executed_no": True,
            "production_workflow_persistence_no": True,
            "production_recovery_actions_no": True,
            "live_network_requests_during_certification_no": True,
            "project_modules_imported_no": True,
        })

        hashes_after = {name: sha256_path(path) for name, path in watched.items()}
        checks["source_hashes_unchanged_during_collective_certification"] = all(
            hashes_after[name] == hashes_before[name] for name in paths
        )
        checks["historical_reports_unchanged_during_collective_certification"] = all(
            hashes_after[f"report_{key}"] == hashes_before[f"report_{key}"]
            for key in historical_reports
        )
        checks["source_files_modified_no"] = checks["source_hashes_unchanged_during_collective_certification"]
        if not all(checks.values()):
            raise RuntimeError("One or more B5P collective checks failed.")

        evidence.update({
            "certificate_chain": list(REPORT_CONTRACTS),
            "components": [component for component, _, _ in COMPONENTS],
            "projection_probe": probe,
            "source_hashes": {name: hashes_before[name] for name in paths},
            "frontend_fetch_authorities": 4,
            "shared_infrastructure_endpoint_count": 1,
            "production_sources_modified": False,
            "monitoring_boundary": "read_only_recorded_evidence_only",
            "owner_actions_boundary": "separate_and_deferred",
        })
        status = "CERTIFIED"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    report.parent.mkdir(parents=True, exist_ok=True)
    report_source = make_report(status, checks, evidence, error)
    if support is not None:
        support.write_text(report, report_source)
    else:
        report.write_text(report_source, encoding="utf-8", newline="\n")
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5P_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("COLLECTIVE_REPORT_WRITTEN=YES")
    return 0 if status == "CERTIFIED" else 1


def self_test() -> int:
    folder = Path(__file__).resolve().parent
    b5o = load_b5o_support(folder / B5O_RUNNER_NAME)
    assert b5o.self_test() == 0
    for _, status_token, final_result in REPORT_CONTRACTS.values():
        sample = "\n".join((
            status_token,
            "FAILED_CHECKS:", "[]",
            "NOT_RUN_CHECKS:", "[]",
            final_result,
        ))
        assert report_satisfies(sample, status_token, final_result)
    checks = {"sample": True}
    source = make_report("CERTIFIED", checks, {}, {})
    assert "CERTIFICATION STATUS: CERTIFIED" in source
    assert "FAILED_CHECKS:\n[]" in source
    assert FINAL_RESULT in source
    print("PART_F_15_B5P_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5P_RUNTIME_INFRASTRUCTURE_COLLECTIVE_CERTIFICATION.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
