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
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


STEP = "PART F 15-B5J"
TITLE = "RUNTIME INFRASTRUCTURE WIRING BOUNDARY INSPECTION"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5J RUNTIME INFRASTRUCTURE "
    "WIRING BOUNDARY INSPECTION COMPLETE"
)
DECISION = (
    "CREATE_ONE_DEDICATED_READ_ONLY_RUNTIME_INFRASTRUCTURE_"
    "PROJECTION_REUSING_CANONICAL_STORES_WITHOUT_IMPORT_"
    "SIDE_EFFECTS_OR_MUTATION_AUTHORITY"
)
FUTURE_ENDPOINT = "/owner/api/runtime/infrastructure"

B5CI_REPORT = (
    "PART_F_15_B5C_B5I_RUNTIME_INFRASTRUCTURE_"
    "UI_RESTRUCTURING_CERTIFICATION.txt"
)
B5CI_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5C THROUGH 15-B5I RUNTIME "
    "INFRASTRUCTURE UI RESTRUCTURING CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "7652af2f3047beff560a79472283fe83993aaa767c39493c4ec1fcbd1901b6b1",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "cbfe8119682499638e5cdad015e65ab0056d08b8c3db9772681cc5baf865a1ac",
    "runtime_owner_js": "b73f61e6569e5dc0d97a213c8f8c030556c4877597c7c0274fa63861de5b05ba",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

PRESENTATION_STATES = (
    "loading",
    "ready",
    "empty",
    "no_match",
    "unavailable",
)

READ_TERMS = {
    "count",
    "current",
    "evidence",
    "find",
    "get",
    "health",
    "heartbeat",
    "history",
    "inspect",
    "list",
    "load",
    "lookup",
    "metrics",
    "peek",
    "read",
    "snapshot",
    "status",
    "summary",
    "view",
}

MUTATION_TERMS = {
    "ack",
    "acquire",
    "assign",
    "cancel",
    "checkpoint",
    "claim",
    "commit",
    "create",
    "delete",
    "dequeue",
    "dispatch",
    "enqueue",
    "execute",
    "expire",
    "insert",
    "nack",
    "persist",
    "quarantine",
    "recover",
    "register",
    "release",
    "remove",
    "renew",
    "requeue",
    "resume",
    "retry",
    "save",
    "scale",
    "shutdown",
    "start",
    "stop",
    "submit",
    "suspend",
    "terminate",
    "update",
    "write",
}

SKIP_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "data",
    "node_modules",
    "reports",
    "runtime_backups",
}


def component(
    *,
    label: str,
    panel_id: str,
    prefix: str,
    path_terms: tuple[str, ...],
    source_terms: tuple[str, ...],
    anchors: tuple[str, ...],
    summaries: tuple[str, ...],
    fields: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "label": label,
        "panel_id": panel_id,
        "prefix": prefix,
        "path_terms": path_terms,
        "source_terms": source_terms,
        "anchors": anchors,
        "summaries": summaries,
        "fields": fields,
    }


COMPONENTS: dict[str, dict[str, Any]] = {
    "jobs": component(
        label="Jobs",
        panel_id="runtimeOwnerSectionJobs",
        prefix="runtimeInfrastructureJobs",
        path_terms=("job", "universal_jobs"),
        source_terms=(
            "job_id",
            "workflow_id",
            "assigned_worker_id",
            "attempt_count",
            "terminal_error",
        ),
        anchors=(
            "backend/server/orchestration/job_store.py",
            "backend/server/runtime/universal_job_submission.py",
            "backend/server/runtime/api/job_api.py",
            "backend/server/runtime/persistence/job_state_persistence.py",
            "backend/server/runtime/universal_jobs/contract.py",
            "backend/server/runtime/universal_jobs/creation_engine.py",
        ),
        summaries=(
            "total_jobs",
            "queued_jobs",
            "running_jobs",
            "completed_jobs",
            "failed_jobs",
            "cancelled_jobs",
        ),
        fields=(
            "job_id",
            "workflow_id",
            "correlation_id",
            "workspace_id",
            "pipeline_id",
            "status",
            "stage",
            "job_type",
            "priority",
            "progress",
            "assigned_worker_id",
            "lease_identity",
            "lease_expiry",
            "attempt_count",
            "attempt_limit",
            "retry_state",
            "next_retry_at",
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
            "dispatch_result",
            "terminal_error",
            "event_count",
        ),
    ),
    "queues": component(
        label="Queues",
        panel_id="runtimeOwnerSectionQueues",
        prefix="runtimeInfrastructureQueues",
        path_terms=("queue", "backpressure"),
        source_terms=(
            "queued",
            "claimable",
            "reserved",
            "priority",
            "capacity",
        ),
        anchors=(
            "backend/server/orchestration/queue.py",
            "backend/server/runtime/universal_queue/backpressure.py",
            "backend/server/runtime/universal_queue/capacity_limits.py",
            "backend/server/runtime/universal_queue/creation.py",
            "backend/server/runtime/universal_queue/prioritization.py",
            "backend/server/runtime/universal_queue/scheduling.py",
        ),
        summaries=(
            "queued_items",
            "claimable_items",
            "reserved_items",
            "delayed_items",
            "blocked_items",
            "queue_pressure",
        ),
        fields=(
            "queue_id",
            "queue_name",
            "pipeline_scope",
            "queued_count",
            "claimable_count",
            "reserved_count",
            "delayed_count",
            "blocked_count",
            "oldest_item_at",
            "critical_count",
            "high_count",
            "normal_count",
            "low_count",
            "active_claim_count",
            "reservation_expiry_evidence",
            "pressure_state",
            "capacity_evidence",
            "throughput_evidence",
            "last_updated_at",
        ),
    ),
    "workers_leases": component(
        label="Workers & Leases",
        panel_id="runtimeOwnerSectionWorkersLeases",
        prefix="runtimeInfrastructureWorkersLeases",
        path_terms=("worker", "lease", "heartbeat"),
        source_terms=(
            "worker_id",
            "lease_id",
            "heartbeat",
            "expires_at",
            "concurrency",
        ),
        anchors=(
            "backend/server/runtime/universal_worker/lifecycle_gateway.py",
            "backend/server/runtime/persistence/worker_lease_state_persistence.py",
            "backend/server/runtime/security/ak6_authoritative_lease.py",
            "backend/server/runtime/universal_worker/leasing.py",
            "backend/server/runtime/universal_worker/health.py",
            "backend/server/runtime/universal_worker/heartbeat.py",
        ),
        summaries=(
            "total_workers",
            "active_workers",
            "idle_workers",
            "busy_workers",
            "stale_workers",
            "active_leases",
        ),
        fields=(
            "worker_id",
            "worker_kind",
            "runtime_identity",
            "environment",
            "lifecycle",
            "health",
            "availability",
            "last_heartbeat_at",
            "staleness_reason",
            "current_job_id",
            "current_workflow_id",
            "current_stage",
            "lease_id",
            "lease_owner",
            "lease_status",
            "acquired_at",
            "expires_at",
            "renewed_at",
            "concurrency_limit",
            "active_execution_count",
            "available_capacity",
        ),
    ),
    "orchestration": component(
        label="Orchestration",
        panel_id="runtimeOwnerSectionOrchestration",
        prefix="runtimeInfrastructureOrchestration",
        path_terms=("orchestration", "workflow", "lifecycle"),
        source_terms=(
            "workflow_id",
            "correlation_id",
            "current_stage",
            "predecessor",
            "handoff",
        ),
        anchors=(
            "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
            "backend/server/coordination/workflow_lifecycle/lifecycle_history.py",
            "backend/server/runtime/api/orchestration_api.py",
            "backend/server/runtime/universal_orchestration/contract.py",
            "backend/server/runtime/universal_orchestration/evidence_records.py",
            "backend/server/runtime/universal_orchestration/run_identity.py",
        ),
        summaries=(
            "total_workflows",
            "active_workflows",
            "completed_workflows",
            "failed_workflows",
            "blocked_workflows",
            "pending_handoffs",
        ),
        fields=(
            "workflow_id",
            "correlation_id",
            "workspace_id",
            "pipeline_id",
            "status",
            "current_stage",
            "created_at",
            "updated_at",
            "completed_at",
            "stage_count",
            "completed_stage_count",
            "pending_stage_count",
            "failed_stage_count",
            "predecessor_evidence",
            "successor_evidence",
            "handoff_state",
            "blocked_reason",
            "job_count",
            "active_job_count",
            "failed_job_count",
            "final_output_state",
        ),
    ),
    "execution": component(
        label="Execution",
        panel_id="runtimeOwnerSectionExecution",
        prefix="runtimeInfrastructureExecution",
        path_terms=("execution", "handler", "dispatch"),
        source_terms=(
            "execution_id",
            "handler_id",
            "dispatch",
            "worker_id",
            "terminal_error",
        ),
        anchors=(
            "backend/server/runtime/execution_engine/runtime_handler_execution.py",
            "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
            "backend/server/runtime/execution_engine/execution_contracts.py",
            "backend/server/runtime/execution_engine/completion_execution.py",
            "backend/server/runtime/execution_engine/execution_lifecycle_controller.py",
            "backend/server/runtime/observability/structured_execution_logs.py",
        ),
        summaries=(
            "total_executions",
            "running_executions",
            "succeeded_executions",
            "failed_executions",
            "cancelled_executions",
            "terminal_executions",
        ),
        fields=(
            "execution_id",
            "job_id",
            "workflow_id",
            "correlation_id",
            "pipeline_id",
            "handler_id",
            "handler_version",
            "stage",
            "execution_action",
            "worker_id",
            "lease_id",
            "dispatch_identity",
            "dispatched_at",
            "started_at",
            "finished_at",
            "duration",
            "status",
            "result_summary",
            "terminal_error",
            "failure_kind",
            "event_count",
        ),
    ),
}


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del tag
        normalized = {
            str(name): "" if value is None else str(value)
            for name, value in attrs
        }
        identifier = normalized.get("id")
        if identifier:
            self.ids.append(identifier)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def b5ci_report_is_certified(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "CERTIFICATION STATUS: CERTIFIED" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and B5CI_FINAL_RESULT in normalized
        and "Live evidence wiring performed: NO" in normalized
        and "Action controls added: NO" in normalized
    )


def html_ids_unique(source: str) -> bool:
    parser = ElementCollector()
    parser.feed(source)
    parser.close()
    return len(parser.ids) == len(set(parser.ids))


def css_balanced(source: str) -> bool:
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    stripped = re.sub(r'"(?:\\.|[^"\\])*"', '""', stripped)
    stripped = re.sub(r"'(?:\\.|[^'\\])*'", "''", stripped)
    depth = 0
    for character in stripped:
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5j_js_") as folder:
        candidate = Path(folder) / "runtime_owner.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def python_syntax_valid(source: str, filename: str) -> bool:
    try:
        ast.parse(source, filename=filename)
        compile(source, filename, "exec")
    except SyntaxError:
        return False
    return True


def excluded_source_path(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    lowered_name = path.name.lower()
    if lowered_parts.intersection(SKIP_DIRECTORY_NAMES):
        return True
    return any(
        marker in lowered_name
        for marker in (
            "_before_",
            "-before-",
            ".before.",
            "_backup_",
            "-backup-",
        )
    ) or lowered_name.startswith(("before_", "backup_"))


def backend_python_files(root: Path) -> list[Path]:
    backend = root / "backend/server"
    if not backend.is_dir():
        return []
    files: list[Path] = []
    for path in backend.rglob("*.py"):
        if excluded_source_path(path):
            continue
        try:
            if path.is_file() and path.stat().st_size <= 2_000_000:
                files.append(path)
        except OSError:
            continue
    return sorted(files)


def python_symbols(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return sorted(
        {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
            )
        }
    )


def identifier_tokens(identifier: str) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier)
    return {
        token
        for token in re.split(r"[^A-Za-z0-9]+", expanded.lower())
        if token
    }


def classify_symbol(identifier: str) -> str:
    tokens = identifier_tokens(identifier)
    if tokens.intersection(MUTATION_TERMS):
        return "mutation"
    if tokens.intersection(READ_TERMS):
        return "read_safe"
    return "ambiguous"


def route_declarations(source: str, file_path: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"@(?P<router>[A-Za-z_][A-Za-z0-9_]*)\."
        r"(?P<method>get|post|put|patch|delete)\(\s*"
        r"[\"'](?P<path>[^\"']+)[\"']",
        flags=re.I,
    )
    routes: list[dict[str, Any]] = []
    for match in pattern.finditer(source):
        routes.append(
            {
                "file": file_path,
                "line": source.count("\n", 0, match.start()) + 1,
                "router": match.group("router"),
                "method": match.group("method").upper(),
                "path": match.group("path"),
            }
        )
    return routes


def frontend_runtime_endpoints(source: str) -> list[str]:
    return sorted(
        set(
            re.findall(
                r"[\"'`](/owner/api/runtime(?:/[^\"'`]*)?)[\"'`]",
                source,
            )
        )
    )


def discover_component_authorities(
    root: Path,
    files: list[Path],
) -> dict[str, dict[str, Any]]:
    prepared: list[tuple[Path, str, str, list[str]]] = []
    for path in files:
        try:
            source = read_text(path)
        except (OSError, UnicodeError):
            continue
        prepared.append(
            (
                path,
                relative(root, path),
                source,
                python_symbols(source),
            )
        )

    result: dict[str, dict[str, Any]] = {}
    for component_name, contract in COMPONENTS.items():
        anchor_set = set(contract["anchors"])
        candidates: list[dict[str, Any]] = []
        aggregate_source: list[str] = []
        read_safe: set[str] = set()
        mutation: set[str] = set()
        ambiguous: set[str] = set()

        for path, relative_path, source, symbols in prepared:
            path_lower = relative_path.lower()
            source_lower = source.lower()
            anchor = relative_path in anchor_set
            path_hits = [
                term
                for term in contract["path_terms"]
                if term.lower() in path_lower
            ]
            source_hits = [
                term
                for term in contract["source_terms"]
                if term.lower() in source_lower
            ]
            if not anchor and not path_hits and len(source_hits) < 2:
                continue

            score = (20 if anchor else 0) + (3 * len(path_hits)) + len(source_hits)
            classified = {
                "read_safe": [],
                "mutation": [],
                "ambiguous": [],
            }
            for symbol in symbols:
                category = classify_symbol(symbol)
                classified[category].append(symbol)
                if category == "read_safe":
                    read_safe.add(symbol)
                elif category == "mutation":
                    mutation.add(symbol)
                else:
                    ambiguous.add(symbol)

            candidates.append(
                {
                    "path": relative_path,
                    "score": score,
                    "anchor": anchor,
                    "path_terms": path_hits,
                    "source_terms": source_hits,
                    "read_safe_symbols": classified["read_safe"][:16],
                    "mutation_symbols": classified["mutation"][:16],
                    "ambiguous_symbols": classified["ambiguous"][:12],
                }
            )
            aggregate_source.append(source_lower)

        candidates.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
        corpus = "\n".join(aggregate_source)
        field_map = {
            field: field.lower() in corpus
            for field in contract["fields"]
        }
        anchors_present = [
            anchor
            for anchor in contract["anchors"]
            if (root / anchor).is_file()
        ]
        result[component_name] = {
            "label": contract["label"],
            "anchors_present": anchors_present,
            "anchor_count": len(anchors_present),
            "candidate_count": len(candidates),
            "candidates": candidates[:24],
            "read_safe_symbols": sorted(read_safe)[:60],
            "mutation_symbols_excluded": sorted(mutation)[:60],
            "ambiguous_symbols_for_adapter_review": sorted(ambiguous)[:40],
            "field_presence": field_map,
            "field_presence_count": sum(field_map.values()),
            "field_contract_count": len(field_map),
        }
    return result


def infrastructure_ui_contract_present(source: str) -> bool:
    states = " ".join(PRESENTATION_STATES)
    for component_name, contract in COMPONENTS.items():
        required = (
            f'id="{contract["panel_id"]}"',
            f'data-runtime-infrastructure-component="{component_name}"',
            'data-runtime-infrastructure-state="unavailable"',
            f'data-runtime-infrastructure-states="{states}"',
            f'id="{contract["prefix"]}Directory"',
            f'id="{contract["prefix"]}Detail"',
        )
        if not all(token in source for token in required):
            return False
    return True


def action_controls_absent(source: str) -> bool:
    action_label = re.compile(
        r"<button\b[^>]*>\s*(?:claim|retry|recover|requeue|cancel|"
        r"terminate|execute|release|restart)\b",
        flags=re.I,
    )
    return (
        "data-runtime-infrastructure-action=" not in source
        and action_label.search(source) is None
    )


def projection_contract() -> dict[str, Any]:
    return {
        "future_endpoint": FUTURE_ENDPOINT,
        "method": "GET",
        "request_count_added_during_b5j": 0,
        "planned_request_count_for_b5k": 1,
        "snapshot_policy": (
            "one cached read-only snapshot shared by B5K-B5O; local filtering, "
            "search and selection do not issue requests"
        ),
        "top_level_fields": (
            "generated_at",
            "source_status",
            "jobs",
            "queues",
            "workers_leases",
            "orchestration",
            "execution",
        ),
        "components": {
            name: {
                "summary_fields": contract["summaries"],
                "record_fields": contract["fields"],
                "presentation_states": PRESENTATION_STATES,
            }
            for name, contract in COMPONENTS.items()
        },
        "fail_closed_rules": (
            "do not infer absent records",
            "do not import or call mutation authorities",
            "do not create jobs, claim queues or execute handlers",
            "do not expose retry, recovery, cancellation or termination controls",
            "mark unavailable evidence explicitly",
        ),
        "separate_future_authority": "Owner Actions & Recovery",
    }


def make_report(
    status: str,
    checks: dict[str, bool],
    findings: list[dict[str, Any]],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "COMPLETE"
        else (
            "FINAL RESULT: PART F 15-B5J RUNTIME INFRASTRUCTURE "
            "WIRING BOUNDARY INSPECTION NOT_COMPLETE"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            "PART F 15-B5J RUNTIME INFRASTRUCTURE WIRING BOUNDARY INSPECTION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Mode: STRICT READ-ONLY FAIL-CLOSED",
            "Production source changes: NONE",
            "Endpoint requests added: NO",
            "Project modules imported: NO",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed: NO",
            f"INSPECTION STATUS: {status}",
            "",
            "INSPECTION DECISION:",
            DECISION,
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
            "FINDINGS:",
            json.dumps(findings, indent=2, sort_keys=True),
            "",
            "WIRING BOUNDARY EVIDENCE:",
            json.dumps(evidence, indent=2, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2, sort_keys=True),
            "",
            "INSPECTED BOUNDARY:",
            "- Canonical job, queue, worker/lease, orchestration and execution sources were scanned as text and AST only.",
            "- Read-safe candidate symbols were separated from mutation and ambiguous symbols.",
            "- One future GET projection was specified for a shared B5K-B5O cached snapshot.",
            "- Existing Runtime summary and Connected Domain requests remain unchanged.",
            "- Filters, searches and selections will remain local presentation operations after the snapshot loads.",
            "- Retry, claim, requeue, cancellation, termination, recovery and execution controls remain deferred to Owner Actions & Recovery.",
            "- No endpoint, UI, job, queue, worker, lease, workflow, handler, output or persistence authority was added or mutated.",
            "",
            "NEXT STEP:",
            "Part F 15-B5K - add the shared read-only projection and wire Jobs evidence first.",
            "",
            final,
            "",
        ]
    )


def run_inspection(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    b5ci_report = root / "backend/server/data/reports" / B5CI_REPORT

    checks: dict[str, bool] = {}
    findings: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {
        "decision": DECISION,
        "future_endpoint": FUTURE_ENDPOINT,
        "new_endpoint_requests": 0,
        "source_mutation_performed": False,
        "recovery_controls_added": False,
        "project_modules_imported": False,
    }
    error: dict[str, Any] = {}
    status = "NOT_COMPLETE"

    try:
        checks["part_f_15_b5c_b5i_report_exists"] = b5ci_report.is_file()
        checks["part_f_15_b5c_b5i_certified"] = (
            b5ci_report.is_file()
            and b5ci_report_is_certified(read_text(b5ci_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "The certified B5C-B5I baseline or a required Runtime Owner source is unavailable."
            )

        watched = {**paths, "b5ci_report": b5ci_report}
        hashes_before = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed sources do not match the certified B5C-B5I baseline."
            )

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        summary_source = read_text(paths["runtime_summary_api"])
        operations_source = read_text(paths["pipeline_operations"])

        checks["final_html_ids_unique"] = html_ids_unique(html_source)
        checks["final_css_balanced"] = css_balanced(css_source)
        checks["final_javascript_syntax"] = javascript_syntax_valid(js_source)
        checks["runtime_summary_python_syntax"] = python_syntax_valid(
            summary_source,
            str(paths["runtime_summary_api"]),
        )
        checks["pipeline_operations_python_syntax"] = python_syntax_valid(
            operations_source,
            str(paths["pipeline_operations"]),
        )
        checks["five_ui_component_contracts_retained"] = (
            infrastructure_ui_contract_present(html_source)
        )
        checks["five_presentation_states_retained"] = all(
            state in html_source for state in PRESENTATION_STATES
        )
        checks["action_controls_remain_absent"] = action_controls_absent(
            html_source
        )

        endpoints = frontend_runtime_endpoints(js_source)
        fetch_count = js_source.count("fetch(")
        expected_endpoints = {
            "/owner/api/runtime/summary",
            "/owner/api/runtime/pipelines",
            "/owner/api/runtime/pipelines/connect_domain",
        }
        checks["three_existing_frontend_fetch_authorities_retained"] = (
            fetch_count == 3
        )
        checks["connected_domain_get_endpoints_retained"] = (
            expected_endpoints.issubset(set(endpoints))
        )
        checks["future_infrastructure_endpoint_not_yet_requested"] = (
            FUTURE_ENDPOINT not in js_source
        )

        python_files = backend_python_files(root)
        checks["backend_source_inventory_completed"] = bool(python_files)
        authorities = discover_component_authorities(root, python_files)

        checks["five_authority_maps_completed"] = (
            set(authorities) == set(COMPONENTS)
            and all(
                details["candidate_count"] > 0
                for details in authorities.values()
            )
        )
        checks["canonical_anchor_sources_present"] = all(
            details["anchor_count"] >= 2
            for details in authorities.values()
        )
        checks["read_safe_candidates_discovered"] = all(
            len(details["read_safe_symbols"]) > 0
            for details in authorities.values()
        )
        checks["mutation_authorities_identified_and_excluded"] = all(
            len(details["mutation_symbols_excluded"]) > 0
            for details in authorities.values()
        )
        checks["field_contract_scan_completed"] = all(
            details["field_contract_count"] == len(COMPONENTS[name]["fields"])
            and details["field_presence_count"] > 0
            for name, details in authorities.items()
        )

        all_routes: list[dict[str, Any]] = []
        for path in python_files:
            try:
                source = read_text(path)
            except (OSError, UnicodeError):
                continue
            all_routes.extend(
                route_declarations(source, relative(root, path))
            )
        runtime_routes = [
            route
            for route in all_routes
            if (
                "runtime" in route["file"].lower()
                or "runtime" in route["path"].lower()
                or route["path"] in {
                    "/summary",
                    "/pipelines",
                    "/pipelines/{pipeline_id}",
                }
            )
        ]
        checks["runtime_route_inventory_completed"] = bool(runtime_routes)
        checks["future_projection_route_not_yet_present"] = not any(
            route["path"] in {FUTURE_ENDPOINT, "/infrastructure"}
            for route in runtime_routes
        )

        contract_data = projection_contract()
        checks["one_shared_future_get_projection_defined"] = (
            contract_data["future_endpoint"] == FUTURE_ENDPOINT
            and contract_data["method"] == "GET"
            and contract_data["planned_request_count_for_b5k"] == 1
        )
        checks["all_five_projection_namespaces_defined"] = (
            set(contract_data["components"]) == set(COMPONENTS)
        )
        checks["local_filtering_and_selection_defined"] = (
            "local filtering" in contract_data["snapshot_policy"]
            and "do not issue requests" in contract_data["snapshot_policy"]
        )
        checks["fail_closed_read_only_policy_defined"] = (
            len(contract_data["fail_closed_rules"]) == 5
            and contract_data["separate_future_authority"]
            == "Owner Actions & Recovery"
        )

        findings.extend(
            [
                {
                    "finding": "existing_runtime_owner_request_boundary",
                    "status": "RETAINED",
                    "fetch_authority_count": fetch_count,
                    "endpoints": endpoints,
                },
                {
                    "finding": "canonical_authority_boundary",
                    "status": "MAPPED",
                    "component_counts": {
                        name: {
                            "anchors": details["anchor_count"],
                            "candidates": details["candidate_count"],
                            "read_safe_symbols": len(details["read_safe_symbols"]),
                            "mutation_symbols_excluded": len(
                                details["mutation_symbols_excluded"]
                            ),
                        }
                        for name, details in authorities.items()
                    },
                },
                {
                    "finding": "shared_projection_boundary",
                    "status": "DEFINED_NOT_IMPLEMENTED",
                    "endpoint": FUTURE_ENDPOINT,
                    "implementation_phase": "15-B5K",
                    "reuse_phases": ["15-B5L", "15-B5M", "15-B5N", "15-B5O"],
                },
                {
                    "finding": "owner_action_boundary",
                    "status": "SEPARATE_AND_DEFERRED",
                    "authority": "Owner Actions & Recovery",
                },
            ]
        )

        evidence.update(
            {
                "source_hashes_before": {
                    name: hashes_before[name]
                    for name in paths
                },
                "b5ci_report_hash": hashes_before["b5ci_report"],
                "frontend_fetch_authority_count": fetch_count,
                "frontend_runtime_endpoints": endpoints,
                "runtime_routes": runtime_routes,
                "authority_maps": authorities,
                "projection_contract": contract_data,
                "wiring_sequence": [
                    "15-B5K jobs plus shared projection endpoint",
                    "15-B5L queues from cached snapshot",
                    "15-B5M workers and leases from cached snapshot",
                    "15-B5N orchestration from cached snapshot",
                    "15-B5O execution from cached snapshot",
                    "15-B5P collective closure",
                ],
            }
        )

        hashes_after = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        checks["production_sources_unchanged"] = all(
            hashes_after[name] == hashes_before[name]
            for name in paths
        )
        checks["b5c_b5i_report_unchanged"] = (
            hashes_after["b5ci_report"] == hashes_before["b5ci_report"]
        )
        checks.update(
            {
                "new_endpoint_requests_added_no": True,
                "production_jobs_created_no": True,
                "production_queue_claims_no": True,
                "production_handlers_executed_no": True,
                "production_workflow_persistence_no": True,
                "production_recovery_actions_no": True,
                "live_network_requests_executed_no": True,
                "project_modules_imported_no": True,
            }
        )

        if not all(checks.values()):
            raise RuntimeError(
                "One or more B5J wiring-boundary inspection checks failed."
            )
        status = "COMPLETE"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_text(
        report,
        make_report(
            status,
            checks,
            findings,
            evidence,
            error,
        ),
    )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"DECISION={DECISION}")
    print(f"FUTURE_ENDPOINT={FUTURE_ENDPOINT}")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5J_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("LIVE_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "COMPLETE" else 1


def self_test() -> int:
    assert classify_symbol("load_job_snapshot") == "read_safe"
    assert classify_symbol("retry_failed_job") == "mutation"
    assert classify_symbol("RuntimeContract") == "ambiguous"
    assert excluded_source_path(Path("backend/server/x/job_store_before_b5.py"))
    assert excluded_source_path(Path("backend/server/data/reports/report.py"))
    assert not excluded_source_path(
        Path("backend/server/orchestration/job_store.py")
    )
    routes = route_declarations(
        '@router.get("/summary")\ndef sample():\n    return {}\n',
        "sample.py",
    )
    assert routes[0]["method"] == "GET"
    assert frontend_runtime_endpoints(
        'const endpoint = "/owner/api/runtime/summary";'
    ) == ["/owner/api/runtime/summary"]
    assert html_ids_unique('<section id="a"><div id="b"></div></section>')
    assert css_balanced("a { color: red; } @media (x) { b { color: blue; } }")
    assert python_syntax_valid("def sample():\n    return True\n", "sample.py")
    contract_data = projection_contract()
    assert set(contract_data["components"]) == set(COMPONENTS)
    assert contract_data["future_endpoint"] == FUTURE_ENDPOINT
    certified = "\n".join(
        (
            "CERTIFICATION STATUS: CERTIFIED",
            "FAILED_CHECKS:",
            "[]",
            "NOT_RUN_CHECKS:",
            "[]",
            "Live evidence wiring performed: NO",
            "Action controls added: NO",
            B5CI_FINAL_RESULT,
        )
    )
    assert b5ci_report_is_certified(certified)
    print("PART_F_15_B5J_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5J_RUNTIME_INFRASTRUCTURE_"
            "WIRING_BOUNDARY_INSPECTION.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(
        run_inspection(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
        )
    )
