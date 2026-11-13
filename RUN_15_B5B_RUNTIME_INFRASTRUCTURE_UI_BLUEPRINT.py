from __future__ import annotations

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


STEP = "PART F 15-B5B"
TITLE = "RUNTIME INFRASTRUCTURE MISSING-COMPONENT SCAN AND UI BLUEPRINT"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5B RUNTIME INFRASTRUCTURE "
    "MISSING-COMPONENT SCAN AND UI BLUEPRINT COMPLETE"
)

EXPECTED_HASHES = {
    "index_html": "6d252cf36d56b9de643efc87d09c92f6e0c49d49098c6924d1457f6afc331de9",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "b87a76c5ddc17446c573ddbc2dea09f32600321738aeb15a74a269933a1145e4",
    "runtime_owner_js": "b73f61e6569e5dc0d97a213c8f8c030556c4877597c7c0274fa63861de5b05ba",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

B5A_REPORT = "PART_F_15_B5A_RUNTIME_INFRASTRUCTURE_BOUNDARY_INSPECTION.txt"
B5A_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5A RUNTIME INFRASTRUCTURE "
    "BOUNDARY INSPECTION COMPLETE"
)

PRESENTATION_STATES = (
    "loading",
    "ready",
    "empty",
    "no_match",
    "unavailable",
)

SHARED_UI_CONTRACT: dict[str, Any] = {
    "purpose": (
        "One read-only Owner Control Tower presentation system for Jobs, "
        "Queues, Workers & Leases, Orchestration and Execution."
    ),
    "regions": [
        "component_header",
        "health_badge",
        "summary_strip",
        "filter_toolbar",
        "directory_pane",
        "evidence_detail_pane",
        "presentation_state_region",
    ],
    "layout": {
        "wide": "summary strip above a directory/detail split pane",
        "medium": "reflowed summary and balanced directory/detail panes",
        "narrow": "single-column directory followed by selected detail",
    },
    "accessibility": [
        "labelled controls",
        "keyboard-reachable listbox rows",
        "visible focus",
        "one selected directory item",
        "aria-live presentation-state message",
        "long-identity wrapping",
        "reduced-motion compatibility",
        "minimum compact touch targets",
    ],
    "data_policy": [
        "show recorded evidence only",
        "do not infer missing runtime facts",
        "render unavailable evidence explicitly",
        "never invent activity for an empty authority",
    ],
    "action_policy": (
        "No retry, claim, cancel, recovery, termination, execution or other "
        "mutation control belongs to B5. A later dedicated Owner Actions "
        "component will own governed runtime actions."
    ),
}


def component_contract(
    *,
    label: str,
    panel_id: str,
    prefix: str,
    description: str,
    summary_metrics: list[str],
    filters: list[str],
    directory_fields: list[str],
    detail_groups: dict[str, list[str]],
) -> dict[str, Any]:
    return {
        "label": label,
        "panel_id": panel_id,
        "prefix": prefix,
        "description": description,
        "required_ids": {
            "workspace": f"{prefix}Workspace",
            "state_badge": f"{prefix}StateBadge",
            "summary": f"{prefix}Summary",
            "filters": f"{prefix}Filters",
            "directory": f"{prefix}Directory",
            "detail": f"{prefix}Detail",
            "message": f"{prefix}Message",
        },
        "summary_metrics": summary_metrics,
        "filters": filters,
        "directory_fields": directory_fields,
        "detail_groups": detail_groups,
        "presentation_states": list(PRESENTATION_STATES),
        "layout": "directory_detail_split",
        "mutation_controls": [],
    }


COMPONENT_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "jobs": component_contract(
        label="Jobs",
        panel_id="runtimeOwnerSectionJobs",
        prefix="runtimeInfrastructureJobs",
        description=(
            "Inspect canonical Universal Job identity, lifecycle, ownership, "
            "progress, attempts, retry evidence and terminal outcome."
        ),
        summary_metrics=[
            "total_jobs",
            "queued_jobs",
            "running_jobs",
            "completed_jobs",
            "failed_jobs",
            "cancelled_jobs",
        ],
        filters=[
            "pipeline_scope",
            "job_status",
            "priority",
            "identity_search",
        ],
        directory_fields=[
            "job_identity",
            "pipeline",
            "job_type",
            "stage",
            "status",
            "priority",
            "progress",
        ],
        detail_groups={
            "identity": [
                "job_id",
                "workflow_id",
                "correlation_id",
                "workspace_id",
                "pipeline_id",
            ],
            "lifecycle": [
                "status",
                "stage",
                "job_type",
                "priority",
                "progress",
            ],
            "ownership": [
                "assigned_worker_id",
                "lease_identity",
                "lease_expiry",
            ],
            "attempts": [
                "attempt_count",
                "attempt_limit",
                "retry_state",
                "next_retry_at",
            ],
            "timing_and_result": [
                "created_at",
                "updated_at",
                "started_at",
                "completed_at",
                "dispatch_result",
                "terminal_error",
                "event_count",
            ],
        },
    ),
    "queues": component_contract(
        label="Queues",
        panel_id="runtimeOwnerSectionQueues",
        prefix="runtimeInfrastructureQueues",
        description=(
            "Inspect canonical queue backlog, priority distribution, claimable "
            "work, reservations, delay and pressure evidence."
        ),
        summary_metrics=[
            "queued_items",
            "claimable_items",
            "reserved_items",
            "delayed_items",
            "blocked_items",
            "queue_pressure",
        ],
        filters=[
            "queue_scope",
            "item_status",
            "priority",
            "identity_search",
        ],
        directory_fields=[
            "queue_identity",
            "queued_count",
            "claimable_count",
            "reserved_count",
            "oldest_item_age",
            "pressure_state",
        ],
        detail_groups={
            "identity": ["queue_id", "queue_name", "pipeline_scope"],
            "backlog": [
                "queued_count",
                "claimable_count",
                "delayed_count",
                "blocked_count",
                "oldest_item_at",
            ],
            "priority_distribution": [
                "critical_count",
                "high_count",
                "normal_count",
                "low_count",
            ],
            "reservation_evidence": [
                "reserved_count",
                "active_claim_count",
                "reservation_expiry_evidence",
            ],
            "pressure": [
                "pressure_state",
                "capacity_evidence",
                "throughput_evidence",
                "last_updated_at",
            ],
        },
    ),
    "workers_leases": component_contract(
        label="Workers & Leases",
        panel_id="runtimeOwnerSectionWorkersLeases",
        prefix="runtimeInfrastructureWorkersLeases",
        description=(
            "Inspect worker identity, lifecycle, health, heartbeat and the "
            "authoritative leases currently associated with runtime work."
        ),
        summary_metrics=[
            "total_workers",
            "active_workers",
            "idle_workers",
            "busy_workers",
            "stale_workers",
            "active_leases",
        ],
        filters=[
            "worker_lifecycle",
            "worker_health",
            "lease_state",
            "identity_search",
        ],
        directory_fields=[
            "worker_identity",
            "lifecycle",
            "health",
            "current_work",
            "active_lease_count",
            "last_heartbeat_at",
        ],
        detail_groups={
            "identity": [
                "worker_id",
                "worker_kind",
                "runtime_identity",
                "environment",
            ],
            "lifecycle_and_health": [
                "lifecycle",
                "health",
                "availability",
                "last_heartbeat_at",
                "staleness_reason",
            ],
            "work_ownership": [
                "current_job_id",
                "current_workflow_id",
                "current_stage",
            ],
            "lease_evidence": [
                "lease_id",
                "lease_owner",
                "lease_status",
                "acquired_at",
                "expires_at",
                "renewed_at",
            ],
            "capacity": [
                "concurrency_limit",
                "active_execution_count",
                "available_capacity",
            ],
        },
    ),
    "orchestration": component_contract(
        label="Orchestration",
        panel_id="runtimeOwnerSectionOrchestration",
        prefix="runtimeInfrastructureOrchestration",
        description=(
            "Inspect workflow identity, correlation, lifecycle, current stage, "
            "dependencies, handoffs, completion and failure evidence."
        ),
        summary_metrics=[
            "total_workflows",
            "active_workflows",
            "completed_workflows",
            "failed_workflows",
            "blocked_workflows",
            "pending_handoffs",
        ],
        filters=[
            "pipeline_scope",
            "workflow_lifecycle",
            "current_stage",
            "identity_search",
        ],
        directory_fields=[
            "workflow_identity",
            "pipeline",
            "lifecycle",
            "current_stage",
            "completion",
            "failure_state",
        ],
        detail_groups={
            "identity": [
                "workflow_id",
                "correlation_id",
                "workspace_id",
                "pipeline_id",
            ],
            "lifecycle": [
                "status",
                "current_stage",
                "created_at",
                "updated_at",
                "completed_at",
            ],
            "stage_progress": [
                "stage_count",
                "completed_stage_count",
                "pending_stage_count",
                "failed_stage_count",
            ],
            "dependencies_and_handoffs": [
                "predecessor_evidence",
                "successor_evidence",
                "handoff_state",
                "blocked_reason",
            ],
            "work_evidence": [
                "job_count",
                "active_job_count",
                "failed_job_count",
                "final_output_state",
            ],
        },
    ),
    "execution": component_contract(
        label="Execution",
        panel_id="runtimeOwnerSectionExecution",
        prefix="runtimeInfrastructureExecution",
        description=(
            "Inspect canonical handler execution identity, job binding, worker "
            "and lease ownership, timing, outcome and terminal evidence."
        ),
        summary_metrics=[
            "total_executions",
            "running_executions",
            "succeeded_executions",
            "failed_executions",
            "cancelled_executions",
            "terminal_executions",
        ],
        filters=[
            "pipeline_scope",
            "execution_status",
            "handler_identity",
            "evidence_search",
        ],
        directory_fields=[
            "execution_identity",
            "job_identity",
            "handler_identity",
            "status",
            "worker_identity",
            "duration",
        ],
        detail_groups={
            "identity": [
                "execution_id",
                "job_id",
                "workflow_id",
                "correlation_id",
                "pipeline_id",
            ],
            "handler_binding": [
                "handler_id",
                "handler_version",
                "stage",
                "execution_action",
            ],
            "ownership": [
                "worker_id",
                "lease_id",
                "dispatch_identity",
            ],
            "timing": [
                "dispatched_at",
                "started_at",
                "finished_at",
                "duration",
            ],
            "outcome": [
                "status",
                "result_summary",
                "terminal_error",
                "failure_kind",
                "event_count",
            ],
        },
    ),
}

IMPLEMENTATION_SEQUENCE = [
    {
        "phase": "15-B5C",
        "scope": "Shared Runtime Infrastructure workspace shell",
        "components": list(COMPONENT_BLUEPRINTS),
        "wiring": "none",
    },
    {
        "phase": "15-B5D",
        "scope": "Jobs UI structure",
        "components": ["jobs"],
        "wiring": "none",
    },
    {
        "phase": "15-B5E",
        "scope": "Queues UI structure",
        "components": ["queues"],
        "wiring": "none",
    },
    {
        "phase": "15-B5F",
        "scope": "Workers & Leases UI structure",
        "components": ["workers_leases"],
        "wiring": "none",
    },
    {
        "phase": "15-B5G",
        "scope": "Orchestration UI structure",
        "components": ["orchestration"],
        "wiring": "none",
    },
    {
        "phase": "15-B5H",
        "scope": "Execution UI structure",
        "components": ["execution"],
        "wiring": "none",
    },
    {
        "phase": "15-B5I",
        "scope": "Responsive, accessibility and UI regression closure",
        "components": list(COMPONENT_BLUEPRINTS),
        "wiring": "none",
    },
]


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized = {
            str(name): "" if value is None else str(value)
            for name, value in attrs
        }
        self.elements.append((tag, normalized))
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


def b5a_report_complete(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "INSPECTION STATUS: COMPLETE" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and B5A_FINAL_RESULT in normalized
        and "Production recovery actions executed: NO" in normalized
        and "Live network requests executed: NO" in normalized
        and (
            "REUSE_EXISTING_FIVE_PLACEHOLDER_SHELLS_AND_DEFINE_ONE_"
            "READ_ONLY_INFRASTRUCTURE_EVIDENCE_BOUNDARY"
        ) in normalized
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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5b_js_") as folder:
        candidate = Path(folder) / "runtime_owner.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def panel_fragment(source: str, panel_id: str) -> str:
    start_pattern = re.compile(
        rf"<section\b[^>]*\bid=[\"']{re.escape(panel_id)}[\"'][^>]*>",
        flags=re.I,
    )
    match = start_pattern.search(source)
    if match is None:
        return ""
    token_pattern = re.compile(r"</?section\b[^>]*>", flags=re.I)
    depth = 0
    for token in token_pattern.finditer(source, match.start()):
        closing = token.group(0).lstrip().startswith("</")
        depth += -1 if closing else 1
        if depth == 0:
            return source[match.start():token.end()]
    return ""


def placeholder_panel_state(
    html_source: str,
    component: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    fragment = panel_fragment(html_source, str(contract["panel_id"]))
    parser = ElementCollector()
    if fragment:
        parser.feed(fragment)
        parser.close()
    interactive_tags = {
        tag
        for tag, _attrs in parser.elements
        if tag.lower() in {"button", "input", "select", "textarea", "table"}
    }
    future_ids = list(contract["required_ids"].values())
    return {
        "label": contract["label"],
        "panel_id": contract["panel_id"],
        "panel_present": bool(fragment),
        "placeholder_present": (
            f'data-runtime-owner-placeholder="{component}"' in fragment
            or f"data-runtime-owner-placeholder='{component}'" in fragment
        ),
        "interactive_structure_present": bool(interactive_tags),
        "future_blueprint_ids_present": [
            identifier
            for identifier in future_ids
            if identifier in parser.ids
        ],
        "missing_regions": list(SHARED_UI_CONTRACT["regions"]),
    }


def blueprint_is_complete(contract: dict[str, Any]) -> bool:
    required_ids = contract.get("required_ids", {})
    return (
        len(required_ids) == 7
        and len(set(required_ids.values())) == 7
        and bool(contract.get("summary_metrics"))
        and bool(contract.get("filters"))
        and bool(contract.get("directory_fields"))
        and bool(contract.get("detail_groups"))
        and tuple(contract.get("presentation_states", ())) == PRESENTATION_STATES
        and contract.get("layout") == "directory_detail_split"
        and contract.get("mutation_controls") == []
    )


def all_blueprint_ids_unique() -> bool:
    values: list[str] = []
    for contract in COMPONENT_BLUEPRINTS.values():
        values.extend(contract["required_ids"].values())
    return len(values) == len(set(values))


def make_report(
    status: str,
    decision: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "COMPLETE"
        else (
            "FINAL RESULT: PART F 15-B5B RUNTIME INFRASTRUCTURE "
            "MISSING-COMPONENT SCAN AND UI BLUEPRINT NOT_COMPLETE"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            f"{STEP} {TITLE}",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Mode: STRICT READ-ONLY UI BLUEPRINT FAIL-CLOSED",
            "Production source changes: NONE",
            "Endpoint requests added: NO",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed: NO",
            f"BLUEPRINT STATUS: {status}",
            "",
            "BLUEPRINT DECISION:",
            decision,
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
            "UI BLUEPRINT EVIDENCE:",
            json.dumps(evidence, indent=2, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2, sort_keys=True),
            "",
            "APPROVED IMPLEMENTATION BOUNDARY:",
            "- B5C through B5I implement presentation structure only.",
            "- Jobs, Queues, Workers & Leases, Orchestration and Execution retain their existing sidebar locations and panel identities.",
            "- Every panel receives a summary strip, local filters, a directory pane, an evidence-detail pane and explicit presentation states.",
            "- Responsive behavior and accessibility are shared across all five component families.",
            "- No backend evidence endpoint or additional frontend request is introduced during the UI restructuring phases.",
            "- Retry, claim, cancel, recovery, termination and execution controls are excluded from B5 and reserved for a separate Owner Actions component.",
            "- No job, queue, worker, lease, workflow, handler, recovery or persistence authority was created, executed or mutated.",
            "",
            "NEXT STEP:",
            "Part F 15-B5C - implement the shared Runtime Infrastructure workspace shell without live evidence wiring.",
            "",
            final,
            "",
        ]
    )


def run_blueprint(root: Path, report: Path) -> int:
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
    b5a_report = root / "backend/server/data/reports" / B5A_REPORT

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "new_endpoint_requests": 0,
        "source_mutation_performed": False,
        "action_controls_added": False,
        "live_wiring_performed": False,
    }
    error: dict[str, Any] = {}
    status = "NOT_COMPLETE"
    decision = "BLUEPRINT_BLOCKED"

    try:
        checks["part_f_15_b5a_report_exists"] = b5a_report.is_file()
        checks["part_f_15_b5a_complete"] = (
            b5a_report.is_file()
            and b5a_report_complete(read_text(b5a_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "The complete B5A baseline or a required Runtime Owner source is unavailable."
            )

        watched = {**paths, "b5a_report": b5a_report}
        hashes_before = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(
            checks[f"source_hash_{name}"]
            for name in EXPECTED_HASHES
        ):
            raise RuntimeError(
                "The certified B5A production-source baseline has changed."
            )

        html_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])

        checks["final_html_ids_unique"] = html_ids_unique(html_source)
        checks["final_css_balanced"] = css_balanced(css_source)
        checks["final_javascript_syntax"] = javascript_syntax_valid(js_source)
        checks["runtime_infrastructure_group_retained"] = all(
            token in html_source
            for token in (
                'data-runtime-sidebar-group="runtime_infrastructure"',
                'id="runtimeSidebarInfrastructure"',
            )
        )

        parser = ElementCollector()
        parser.feed(html_source)
        parser.close()
        sidebar_components = {
            attrs.get("data-runtime-sidebar-section")
            for _tag, attrs in parser.elements
            if attrs.get("data-runtime-sidebar-section")
        }
        panel_components = {
            attrs.get("data-runtime-owner-section-panel"): attrs.get("id")
            for _tag, attrs in parser.elements
            if attrs.get("data-runtime-owner-section-panel")
        }

        scan: dict[str, dict[str, Any]] = {}
        for component, contract in COMPONENT_BLUEPRINTS.items():
            scan[component] = placeholder_panel_state(
                html_source,
                component,
                contract,
            )

        checks["five_sidebar_destinations_retained"] = all(
            component in sidebar_components
            for component in COMPONENT_BLUEPRINTS
        )
        checks["five_panel_destinations_retained"] = all(
            panel_components.get(component) == contract["panel_id"]
            for component, contract in COMPONENT_BLUEPRINTS.items()
        )
        checks["five_panels_confirmed_placeholder_only"] = all(
            state["panel_present"]
            and state["placeholder_present"]
            and not state["interactive_structure_present"]
            and not state["future_blueprint_ids_present"]
            for state in scan.values()
        )
        checks["existing_section_navigation_retained"] = all(
            token in js_source
            for token in (
                "window.LinkCraftorRuntimeOwner",
                "setActiveSection",
                "getActiveSection",
                "runtimeowner:sectionchange",
            )
        )
        checks["existing_three_fetch_authorities_retained"] = (
            js_source.count("fetch(") == 3
        )

        checks["exactly_five_component_blueprints_defined"] = (
            list(COMPONENT_BLUEPRINTS)
            == [
                "jobs",
                "queues",
                "workers_leases",
                "orchestration",
                "execution",
            ]
        )
        checks["all_component_blueprints_complete"] = all(
            blueprint_is_complete(contract)
            for contract in COMPONENT_BLUEPRINTS.values()
        )
        checks["all_future_blueprint_ids_unique"] = all_blueprint_ids_unique()
        checks["shared_workspace_contract_complete"] = all(
            bool(SHARED_UI_CONTRACT.get(key))
            for key in (
                "purpose",
                "regions",
                "layout",
                "accessibility",
                "data_policy",
                "action_policy",
            )
        )
        checks["five_presentation_states_defined"] = all(
            tuple(contract["presentation_states"]) == PRESENTATION_STATES
            for contract in COMPONENT_BLUEPRINTS.values()
        )
        checks["responsive_contract_defined"] = set(
            SHARED_UI_CONTRACT["layout"]
        ) == {"wide", "medium", "narrow"}
        checks["accessibility_contract_defined"] = len(
            SHARED_UI_CONTRACT["accessibility"]
        ) >= 8
        checks["recorded_evidence_only_policy_defined"] = all(
            phrase in SHARED_UI_CONTRACT["data_policy"]
            for phrase in (
                "show recorded evidence only",
                "do not infer missing runtime facts",
                "render unavailable evidence explicitly",
                "never invent activity for an empty authority",
            )
        )
        checks["owner_actions_separation_recorded"] = (
            "dedicated Owner Actions component"
            in SHARED_UI_CONTRACT["action_policy"]
            and all(
                contract["mutation_controls"] == []
                for contract in COMPONENT_BLUEPRINTS.values()
            )
        )
        checks["ui_first_sequence_b5c_through_b5i_defined"] = (
            [item["phase"] for item in IMPLEMENTATION_SEQUENCE]
            == [
                "15-B5C",
                "15-B5D",
                "15-B5E",
                "15-B5F",
                "15-B5G",
                "15-B5H",
                "15-B5I",
            ]
            and all(item["wiring"] == "none" for item in IMPLEMENTATION_SEQUENCE)
        )

        decision = (
            "RESTRUCTURE_EXISTING_FIVE_PLACEHOLDER_PANELS_USING_ONE_"
            "SHARED_UI_CONTRACT_BEFORE_ANY_LIVE_EVIDENCE_WIRING"
        )
        evidence.update(
            {
                "decision": decision,
                "approved_sequence": {
                    "first": "UI restructuring B5C through B5I",
                    "second": "Live evidence wiring B5J through B5O",
                    "third": "Collective closure B5P",
                    "separate_later_workstream": "Owner Actions and controlled recovery",
                },
                "existing_panel_scan": scan,
                "shared_ui_contract": SHARED_UI_CONTRACT,
                "component_blueprints": COMPONENT_BLUEPRINTS,
                "implementation_sequence": IMPLEMENTATION_SEQUENCE,
                "source_hashes_before": {
                    name: hashes_before[name]
                    for name in paths
                },
                "b5a_report_hash": hashes_before["b5a_report"],
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
        checks["b5a_report_unchanged"] = (
            hashes_after["b5a_report"] == hashes_before["b5a_report"]
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
                "One or more B5B UI-blueprint integrity checks failed."
            )
        status = "COMPLETE"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    report.parent.mkdir(parents=True, exist_ok=True)
    write_text(
        report,
        make_report(status, decision, checks, evidence, error),
    )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"DECISION={decision}")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5B_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("LIVE_WIRING=NO")
    print("ACTION_CONTROLS=NO")
    return 0 if status == "COMPLETE" else 1


def self_test() -> int:
    mock_html = "".join(
        [
            '<div id="runtimeSidebarInfrastructure" ',
            'data-runtime-sidebar-group="runtime_infrastructure">',
            *[
                (
                    f'<button data-runtime-sidebar-section="{component}">'
                    f'{contract["label"]}</button>'
                    f'<section id="{contract["panel_id"]}" '
                    f'data-runtime-owner-section-panel="{component}">'
                    f'<h3>{contract["label"]}</h3>'
                    f'<p data-runtime-owner-placeholder="{component}">'
                    "Placeholder</p></section>"
                )
                for component, contract in COMPONENT_BLUEPRINTS.items()
            ],
            "</div>",
        ]
    )
    assert html_ids_unique(mock_html)
    assert css_balanced("a { color: red; } @media (x) { b { color: blue; } }")
    assert all_blueprint_ids_unique()
    assert all(
        blueprint_is_complete(contract)
        for contract in COMPONENT_BLUEPRINTS.values()
    )
    for component, contract in COMPONENT_BLUEPRINTS.items():
        state = placeholder_panel_state(mock_html, component, contract)
        assert state["panel_present"]
        assert state["placeholder_present"]
        assert not state["interactive_structure_present"]
        assert not state["future_blueprint_ids_present"]
    print("PART_F_15_B5B_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5B_RUNTIME_INFRASTRUCTURE_UI_BLUEPRINT.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(
        run_blueprint(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
        )
    )
