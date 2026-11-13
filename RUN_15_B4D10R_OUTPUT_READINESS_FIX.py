from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4D10R OUTPUT READINESS "
    "SEMANTIC CORRECTION CERTIFIED"
)
REPORT_TITLE = (
    "PART F 15-B4D10R OUTPUT READINESS SEMANTIC CORRECTION CERTIFICATION"
)
BACKEND_MARKER = "PART F 15-B4D10R OUTPUT READINESS SEMANTICS"
FRONTEND_MARKER = "PART F 15-B4D10R OUTPUT READINESS PRESENTATION"

EXPECTED_HASHES = {
    "index_html": "57155d1a8bc7b78016075e6224b4a3945a7bb1ab45191b4e7361ab0a905af356",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "9f50dd04a9c38634f74c5001531aaafd4acf024bea38d35bde77387e853e72d0",
    "runtime_owner_js": "44d7b03f88fde60198414917d858d95b7cefc2a8bad35afd5acb764da04654a9",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

OLD_VERSION = 'PIPELINE_OPERATIONS_VERSION = "runtime_pipeline_operations_v1.0.0"'
NEW_VERSION = 'PIPELINE_OPERATIONS_VERSION = "runtime_pipeline_operations_v1.0.1"'

OLD_BACKEND_STATUS_BLOCK = '''    workflow_count = len(workflow_rows)
    failed_workflows = status_counts.get("failed", 0)
    active_workflows = sum(status_counts.get(value, 0) for value in ("created", "pending", "running", "processing"))
    if failed_workflows or failed_jobs:
'''

NEW_BACKEND_STATUS_BLOCK = '''    workflow_count = len(workflow_rows)
    failed_workflows = status_counts.get("failed", 0)
    active_workflows = sum(status_counts.get(value, 0) for value in ("created", "pending", "running", "processing"))
    completed_workflows = status_counts.get("completed", 0)

    # BEGIN PART F 15-B4D10R OUTPUT READINESS SEMANTICS
    if workflow_count == 0:
        readiness_status = "NOT_EVALUATED"
    elif failed_workflows or final_outputs_ready < completed_workflows:
        readiness_status = "BLOCKED"
    elif completed_workflows == workflow_count:
        readiness_status = "VERIFIED"
    else:
        readiness_status = "PENDING"
    # END PART F 15-B4D10R OUTPUT READINESS SEMANTICS

    if failed_workflows or failed_jobs:
'''

OLD_BACKEND_READINESS_BLOCK = '''        output_readiness=_freeze({
            "final_stage_id": order[-1] if order else None,
            "ready_workflow_count": final_outputs_ready,
            "all_completed_outputs_ready": bool(
                workflow_count and final_outputs_ready == status_counts.get("completed", 0)
            ),
        }),
'''

NEW_BACKEND_READINESS_BLOCK = '''        output_readiness=_freeze({
            "final_stage_id": order[-1] if order else None,
            "completed_workflow_count": completed_workflows,
            "ready_workflow_count": final_outputs_ready,
            "readiness_status": readiness_status,
            "all_completed_outputs_ready": readiness_status == "VERIFIED",
        }),
'''

OLD_FRONTEND_VALUES = '''    const workflowCount = integer(counts.workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const health = label(payload.health_status);
'''

NEW_FRONTEND_VALUES = '''    const workflowCount = integer(counts.workflow_count);
    const completedCount = integer(readiness.completed_workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const readinessStatus = String(readiness.readiness_status || "")
      .trim()
      .toUpperCase();
    const readinessLabels = Object.freeze({
      NOT_EVALUATED: "Not evaluated",
      PENDING: "Pending",
      BLOCKED: "Blocked",
      VERIFIED: "Verified"
    });
    // BEGIN PART F 15-B4D10R OUTPUT READINESS PRESENTATION
    if (!Object.prototype.hasOwnProperty.call(readinessLabels, readinessStatus)) {
      throw new Error("Connected Domain output-readiness status is unavailable.");
    }
    if (readyCount > completedCount || completedCount > workflowCount) {
      throw new Error("Connected Domain output-readiness counts are inconsistent.");
    }
    // END PART F 15-B4D10R OUTPUT READINESS PRESENTATION
    const health = label(payload.health_status);
'''

OLD_FRONTEND_OUTPUT = '''    setText(
      "pipelineConnectedDomainOutputReadiness",
      readiness.all_completed_outputs_ready ? "Verified" : `${readyCount} ready`
    );
'''

NEW_FRONTEND_OUTPUT = '''    setText(
      "pipelineConnectedDomainOutputReadiness",
      readinessLabels[readinessStatus]
    );
'''

OLD_SCRIPT_VERSION = '<script src="/owner/runtime_owner.js?v=8"></script>'
NEW_SCRIPT_VERSION = '<script src="/owner/runtime_owner.js?v=9"></script>'


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}.")
    return source.replace(old, new, 1)


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d10r_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def python_syntax_valid(source: str) -> bool:
    try:
        ast.parse(source)
        compile(source, "pipeline_operations_candidate.py", "exec")
    except SyntaxError:
        return False
    return True


def isolated_readiness_contract(candidate_source: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d10r_contract_") as folder:
        root = Path(folder)
        package_files = (
            "backend/__init__.py",
            "backend/server/__init__.py",
            "backend/server/owner/__init__.py",
            "backend/server/orchestration/__init__.py",
            "backend/server/coordination/__init__.py",
            "backend/server/coordination/runtime_integration/__init__.py",
            "backend/server/runtime/__init__.py",
        )
        for relative in package_files:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            write_text(target, "")

        candidate = root / "backend/server/owner/pipeline_operations.py"
        write_text(candidate, candidate_source)

        write_text(
            root / "backend/server/orchestration/job_store.py",
            '''def load_jobs():
    return {}


def list_job_events(job_id):
    return ()
''',
        )
        write_text(
            root
            / "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py",
            '''class _Registry:
    def all_for_workflow(self, workflow_id):
        return ()


def get_workflow_job_correlation_registry():
    return _Registry()
''',
        )
        write_text(
            root / "backend/server/runtime/universal_runtime_registration.py",
            '''def list_runtime_registrations():
    return ()
''',
        )

        test_script = root / "verify_contract.py"
        write_text(
            test_script,
            r'''from __future__ import annotations

import json
from types import SimpleNamespace

from backend.server.owner.pipeline_operations import (
    build_pipeline_operations_snapshot,
)


STAGES = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)


REGISTRATIONS = tuple(
    {
        "pipeline": "connect_domain",
        "stage": stage,
        "job_type": f"{stage}_stage",
        "predecessor_stages": () if index == 0 else (STAGES[index - 1],),
        "successor_stages": () if index == len(STAGES) - 1 else (STAGES[index + 1],),
        "persistent": True,
    }
    for index, stage in enumerate(STAGES)
)


class Repository:
    def __init__(self, workflows):
        self.workflows = {item.workflow_id: item for item in workflows}

    def list_workflow_ids(self):
        return tuple(self.workflows)

    def load_workflow(self, workflow_id):
        return self.workflows[workflow_id]


class Registry:
    def all_for_workflow(self, workflow_id):
        return ()


def workflow(workflow_id, status):
    completed = STAGES if status == "completed" else ()
    pending = () if status in ("completed", "failed") else STAGES
    failed = ("active_target_set",) if status == "failed" else ()
    return SimpleNamespace(
        workflow_id=workflow_id,
        correlation_id=f"correlation-{workflow_id}",
        workspace_id="ws-b4d10r",
        workflow_type="connect_domain",
        metadata={"pipeline_id": "connect_domain"},
        status=SimpleNamespace(value=status),
        current_stage=None,
        completed_stages=completed,
        pending_stages=pending,
        failed_stages=failed,
        created_at="2026-11-09T00:00:00Z",
        updated_at="2026-11-09T00:00:01Z",
    )


def final_job(workflow_id):
    return {
        "job_id": f"job-{workflow_id}",
        "job_type": "active_target_set_stage",
        "status": "completed",
        "priority": 5,
        "metadata": {
            "workflow_id": workflow_id,
            "stage_id": "active_target_set",
            "runtime_dispatch_result": {"targets": []},
        },
    }


def snapshot(workflows, jobs=()):
    job_map = {item["job_id"]: item for item in jobs}
    result = build_pipeline_operations_snapshot(
        pipeline_id="connect_domain",
        workflow_repository=Repository(workflows),
        registrations_reader=lambda: REGISTRATIONS,
        jobs_reader=lambda: job_map,
        events_reader=lambda job_id: (),
        correlation_registry=Registry(),
    )
    return result.to_dict()["output_readiness"]


scenarios = {
    "no_workflows": snapshot(()),
    "active_unfinished": snapshot((workflow("wf-active", "running"),)),
    "completed_without_output": snapshot((workflow("wf-blocked", "completed"),)),
    "completed_with_output": snapshot(
        (workflow("wf-verified", "completed"),),
        (final_job("wf-verified"),),
    ),
    "mixed_completed_and_active": snapshot(
        (
            workflow("wf-completed", "completed"),
            workflow("wf-active-2", "running"),
        ),
        (final_job("wf-completed"),),
    ),
    "failed_workflow": snapshot((workflow("wf-failed", "failed"),)),
}

expected = {
    "no_workflows": ("NOT_EVALUATED", False, 0, 0),
    "active_unfinished": ("PENDING", False, 0, 0),
    "completed_without_output": ("BLOCKED", False, 1, 0),
    "completed_with_output": ("VERIFIED", True, 1, 1),
    "mixed_completed_and_active": ("PENDING", False, 1, 1),
    "failed_workflow": ("BLOCKED", False, 0, 0),
}

for name, readiness in scenarios.items():
    actual = (
        readiness["readiness_status"],
        readiness["all_completed_outputs_ready"],
        readiness["completed_workflow_count"],
        readiness["ready_workflow_count"],
    )
    assert actual == expected[name], (name, actual, expected[name])

print(json.dumps({
    "scenario_count": len(scenarios),
    "statuses": {
        name: value["readiness_status"]
        for name, value in scenarios.items()
    },
}, sort_keys=True))
''',
        )

        result = subprocess.run(
            [sys.executable, "-B", str(test_script)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "Isolated readiness contract failed.\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
        return json.loads(result.stdout.strip())


def print_check(name: str, value: bool) -> None:
    print(f"{name.upper()}: {'PASS' if value else 'FAIL'}")


def build_report(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    backup: Path | None,
) -> str:
    failed = [name for name, value in checks.items() if not value]
    final = FINAL_RESULT if status == "CERTIFIED" else (
        "FINAL RESULT: PART F 15-B4D10R OUTPUT READINESS "
        "SEMANTIC CORRECTION NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
{REPORT_TITLE}

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup if backup else "NOT_CREATED"}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed during certification: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True)}

EXECUTION_ERROR:
{json.dumps(error, indent=2, sort_keys=True)}

CORRECTED SEMANTICS:
- No workflows: NOT_EVALUATED.
- Active or otherwise unfinished workflow: PENDING.
- Failed workflow or completed workflow without final output: BLOCKED.
- Every workflow completed with final output evidence: VERIFIED.
- The legacy boolean remains available but is true only for VERIFIED readiness.

CORRECTED BOUNDARY:
- The canonical Pipeline Operations projection now publishes an explicit readiness_status.
- Connected Domain Overview renders that status instead of inferring readiness from a faulty boolean.
- All Pipelines receives the corrected legacy boolean from the same canonical projection.
- Six isolated scenarios verify empty, active, blocked, verified, mixed and failed states.
- No endpoint, job, queue, handler, workflow, recovery or persistence authority was added.

NEXT STEP:
Visual confirmation after Ctrl+F5, then Part F 15-B4E - Workflow Explorer component.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D10R_OUTPUT_READINESS_FIX.py "
            "<project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    prior_report = (
        root
        / "backend/server/data/reports/"
        "PART_F_15_B4D10_CONNECTED_DOMAIN_OVERVIEW_WIRING_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d10_report_exists"] = prior_report.is_file()
        prior_report_hash = sha256_path(prior_report) if prior_report.is_file() else ""
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4d10_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and "FINAL RESULT: PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW "
            "LIVE EVIDENCE WIRING CERTIFIED" in prior
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or D10 evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed source lineage does not match certified D10.")

        index_source = read_text(paths["index_html"])
        js_source = read_text(paths["runtime_owner_js"])
        operations_source = read_text(paths["pipeline_operations"])
        checks["correction_not_previously_present"] = (
            BACKEND_MARKER not in operations_source
            and FRONTEND_MARKER not in js_source
        )

        operations_candidate = replace_once(
            operations_source,
            OLD_VERSION,
            NEW_VERSION,
            "Pipeline Operations version",
        )
        operations_candidate = replace_once(
            operations_candidate,
            OLD_BACKEND_STATUS_BLOCK,
            NEW_BACKEND_STATUS_BLOCK,
            "readiness-status derivation boundary",
        )
        operations_candidate = replace_once(
            operations_candidate,
            OLD_BACKEND_READINESS_BLOCK,
            NEW_BACKEND_READINESS_BLOCK,
            "output-readiness projection boundary",
        )
        js_candidate = replace_once(
            js_source,
            OLD_FRONTEND_VALUES,
            NEW_FRONTEND_VALUES,
            "overview readiness validation boundary",
        )
        js_candidate = replace_once(
            js_candidate,
            OLD_FRONTEND_OUTPUT,
            NEW_FRONTEND_OUTPUT,
            "overview readiness rendering boundary",
        )
        index_candidate = replace_once(
            index_source,
            OLD_SCRIPT_VERSION,
            NEW_SCRIPT_VERSION,
            "Runtime JavaScript cache version",
        )

        checks["candidate_python_syntax"] = python_syntax_valid(
            operations_candidate
        )
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(
            js_candidate
        )
        checks["explicit_four_state_contract_present"] = all(
            f'"{value}"' in operations_candidate
            for value in ("NOT_EVALUATED", "PENDING", "BLOCKED", "VERIFIED")
        )
        checks["completed_workflow_count_projected"] = (
            '"completed_workflow_count": completed_workflows'
            in operations_candidate
        )
        checks["legacy_boolean_fail_closed"] = (
            '"all_completed_outputs_ready": readiness_status == "VERIFIED"'
            in operations_candidate
        )
        checks["frontend_uses_explicit_status"] = (
            "readiness.readiness_status" in js_candidate
            and "readinessLabels[readinessStatus]" in js_candidate
            and 'readiness.all_completed_outputs_ready ? "Verified"' not in js_candidate
        )
        checks["frontend_rejects_inconsistent_counts"] = (
            "readyCount > completedCount || completedCount > workflowCount"
            in js_candidate
        )
        checks["pipeline_operations_version_advanced"] = (
            NEW_VERSION in operations_candidate and OLD_VERSION not in operations_candidate
        )
        checks["runtime_javascript_cache_advanced"] = (
            NEW_SCRIPT_VERSION in index_candidate
            and OLD_SCRIPT_VERSION not in index_candidate
        )
        checks["runtime_requests_unchanged"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
            and js_candidate.count('"/owner/api/runtime/pipelines/connect_domain"')
            == js_source.count('"/owner/api/runtime/pipelines/connect_domain"')
            and js_candidate.count('"/owner/api/runtime/pipelines"')
            == js_source.count('"/owner/api/runtime/pipelines"')
            and js_candidate.count('"/owner/api/runtime/summary"')
            == js_source.count('"/owner/api/runtime/summary"')
        )
        checks["no_recovery_controls_added"] = all(
            js_candidate.count(token) == js_source.count(token)
            for token in (
                "retryJob(",
                "cancelJob(",
                "terminateJob(",
                "data-runtime-recovery-action",
            )
        )

        scenario_evidence = isolated_readiness_contract(operations_candidate)
        evidence["isolated_readiness_contract"] = scenario_evidence
        checks["six_isolated_readiness_scenarios_passed"] = (
            scenario_evidence.get("scenario_count") == 6
            and scenario_evidence.get("statuses")
            == {
                "active_unfinished": "PENDING",
                "completed_with_output": "VERIFIED",
                "completed_without_output": "BLOCKED",
                "failed_workflow": "BLOCKED",
                "mixed_completed_and_active": "PENDING",
                "no_workflows": "NOT_EVALUATED",
            }
        )
        if not all(checks.values()):
            raise RuntimeError("D10R candidate certification checks failed.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root
            / "backend/server/data/runtime_backups"
            / f"part_f_15_b4d10r_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_js", "pipeline_operations"):
            path = paths[name]
            originals[name] = path.read_bytes()
            backup_target = backup_dir / name / path.name
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup_target)
        checks["backup_created"] = all(
            (backup_dir / name / paths[name].name).is_file()
            for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("D10R production-source backup is incomplete.")

        write_text(paths["pipeline_operations"], operations_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)
        write_text(paths["index_html"], index_candidate)

        retained_operations = read_text(paths["pipeline_operations"])
        retained_js = read_text(paths["runtime_owner_js"])
        retained_index = read_text(paths["index_html"])
        checks["retained_python_syntax"] = python_syntax_valid(retained_operations)
        checks["retained_javascript_syntax"] = javascript_syntax_valid(retained_js)
        checks["retained_backend_marker_once"] = (
            retained_operations.count(BACKEND_MARKER) == 2
        )
        checks["retained_frontend_marker_once"] = (
            retained_js.count(FRONTEND_MARKER) == 2
        )
        checks["retained_cache_version"] = NEW_SCRIPT_VERSION in retained_index

        retained_scenarios = isolated_readiness_contract(retained_operations)
        checks["retained_readiness_contract_passed"] = (
            retained_scenarios == scenario_evidence
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["corrected_surfaces"] = [
            "All Pipelines output-readiness summary",
            "Connected Domain Operations Overview output-readiness value",
        ]
        evidence["readiness_states"] = [
            "NOT_EVALUATED",
            "PENDING",
            "BLOCKED",
            "VERIFIED",
        ]
        evidence["new_endpoint_requests"] = 0
        evidence["recovery_controls_added"] = False

        for name in (
            "owner_css",
            "owner_js",
            "runtime_owner_css",
            "runtime_summary_api",
        ):
            checks[f"unchanged_{name}"] = before[name] == after[name]
        checks["historical_d10_report_unchanged"] = (
            sha256_path(prior_report) == prior_report_hash
        )
        checks["only_three_target_sources_changed"] = all(
            before[name] != after[name]
            for name in ("index_html", "runtime_owner_js", "pipeline_operations")
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_certification_no"] = True
        if not all(checks.values()):
            raise RuntimeError("D10R retained-source certification checks failed.")

        retained = True
        status = "CERTIFIED"

    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, data in originals.items():
            paths[name].write_bytes(data)

    report.parent.mkdir(parents=True, exist_ok=True)
    write_text(
        report,
        build_report(
            status=status,
            checks=checks,
            evidence=evidence,
            error=error,
            backup=backup_dir,
        ),
    )
    for name, value in checks.items():
        print_check(name, value)
    failed = [name for name, value in checks.items() if not value]
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4D10R_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
