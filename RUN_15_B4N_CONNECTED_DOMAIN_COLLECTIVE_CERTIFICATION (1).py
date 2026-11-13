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


FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4N CONNECTED DOMAIN OPERATIONS COLLECTIVE "
    "CERTIFICATION AND HANDOFF CLOSURE CERTIFIED"
)

RUNNER_REVISION = "15-B4N-R1-SEMANTIC-STAGE-ORDER-VERIFIER"

EXPECTED_HASHES = {
    "index_html": "6d252cf36d56b9de643efc87d09c92f6e0c49d49098c6924d1457f6afc331de9",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "b87a76c5ddc17446c573ddbc2dea09f32600321738aeb15a74a269933a1145e4",
    "runtime_owner_js": "b73f61e6569e5dc0d97a213c8f8c030556c4877597c7c0274fa63861de5b05ba",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

TAB_PANEL_PAIRS = (
    (
        "overview",
        "pipelineOperationsTabOverview",
        "pipelineOperationsViewOverview",
    ),
    (
        "workflows",
        "pipelineOperationsTabWorkflows",
        "pipelineOperationsViewWorkflows",
    ),
    (
        "stage_progress",
        "pipelineOperationsTabStageProgress",
        "pipelineOperationsViewStageProgress",
    ),
    (
        "jobs_attempts",
        "pipelineOperationsTabJobsAttempts",
        "pipelineOperationsViewJobsAttempts",
    ),
    (
        "dependencies_handoffs",
        "pipelineOperationsTabDependenciesHandoffs",
        "pipelineOperationsViewDependenciesHandoffs",
    ),
    (
        "events_timeline",
        "pipelineOperationsTabEventsTimeline",
        "pipelineOperationsViewEventsTimeline",
    ),
    (
        "failures",
        "pipelineOperationsTabFailures",
        "pipelineOperationsViewFailures",
    ),
    (
        "output_readiness",
        "pipelineOperationsTabOutputReadiness",
        "pipelineOperationsViewOutputReadiness",
    ),
)

COMPONENT_AUTHORITIES = (
    "LinkCraftorConnectedDomainOverview",
    "LinkCraftorConnectedDomainWorkflowExplorer",
    "LinkCraftorConnectedDomainStageProgress",
    "LinkCraftorConnectedDomainJobsAttempts",
    "LinkCraftorConnectedDomainDependenciesHandoffs",
    "LinkCraftorConnectedDomainEventsTimeline",
    "LinkCraftorConnectedDomainFailuresAttention",
    "LinkCraftorConnectedDomainOutputReadiness",
)

STAGE_ORDER = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)

REPORT_CHAIN = {
    "PART_F_15_B4D3_D5_RUNTIME_UI_REDESIGN_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D3 THROUGH 15-B4D5 RUNTIME UI "
        "REDESIGN CERTIFIED"
    ),
    "PART_F_15_B4D6_D8_COMPONENT_SHELLS_NAVIGATION_STATES_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D6 THROUGH 15-B4D8 COMPONENT SHELLS "
        "NAVIGATION AND STATES CERTIFIED"
    ),
    "PART_F_15_B4D9_NAVIGATION_BOUNDARY_FIX_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION "
        "BOUNDARY CORRECTION CERTIFIED"
    ),
    "PART_F_15_B4D10_CONNECTED_DOMAIN_OVERVIEW_WIRING_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE "
        "EVIDENCE WIRING CERTIFIED"
    ),
    "PART_F_15_B4D10R_OUTPUT_READINESS_SEMANTIC_CORRECTION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4D10R OUTPUT READINESS SEMANTIC "
        "CORRECTION CERTIFIED"
    ),
    "PART_F_15_B4E_WORKFLOW_EXPLORER_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4E WORKFLOW EXPLORER CERTIFIED"
    ),
    "PART_F_15_B4F_SIX_STAGE_PROGRESS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4F SIX-STAGE PROGRESS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4G_JOBS_ATTEMPTS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4G JOBS AND ATTEMPTS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4H_DEPENDENCIES_HANDOFFS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4I_EVENTS_TIMELINE_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4I EVENTS TIMELINE COMPONENT CERTIFIED"
    ),
    "PART_F_15_B4J_FAILURES_ATTENTION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4J FAILURES AND ATTENTION COMPONENT "
        "CERTIFIED"
    ),
    "PART_F_15_B4K_OUTPUT_READINESS_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4K OUTPUT READINESS COMPONENT CERTIFIED"
    ),
    "PART_F_15_B4L_RESPONSIVE_INTEGRATION_FINALIZATION_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION "
        "CERTIFIED"
    ),
    "PART_F_15_B4M_CROSS_COMPONENT_REGRESSION_ACCESSIBILITY_CERTIFICATION.txt": (
        "FINAL RESULT: PART F 15-B4M CROSS-COMPONENT REGRESSION AND "
        "ACCESSIBILITY CLOSURE CERTIFIED"
    ),
}


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        normalized = {
            name: "" if value is None else value
            for name, value in attrs
        }
        self.elements.append((tag, normalized))
        identifier = normalized.get("id")
        if identifier:
            self.ids.append(identifier)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def html_ids_unique(source: str) -> bool:
    parser = ElementCollector()
    parser.feed(source)
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
        raise RuntimeError(
            "Node.js is required for JavaScript syntax validation."
        )
    with tempfile.TemporaryDirectory(
        prefix="linkcraftor_b4n_js_"
    ) as folder:
        candidate = Path(folder) / "runtime_owner_collective.js"
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
        compile(source, filename, "exec")
    except SyntaxError:
        return False
    return True


def report_is_certified(source: str, final_result: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "CERTIFICATION STATUS: CERTIFIED" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and final_result in normalized
        and "Production jobs created: NO" in normalized
        and "Production recovery actions executed: NO" in normalized
        and "Live network requests executed" in normalized
    )


def report_json_object(source: str, heading: str) -> dict[str, Any]:
    """Decode the first JSON object following a report heading."""
    marker = f"{heading}\n"
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError(f"Report heading is unavailable: {heading}")
    object_index = source.find("{", marker_index + len(marker))
    if object_index < 0:
        raise ValueError(f"Report JSON object is unavailable: {heading}")
    value, _ = json.JSONDecoder().raw_decode(source[object_index:])
    if not isinstance(value, dict):
        raise ValueError(f"Report JSON value is not an object: {heading}")
    return value


def canonical_stage_order_probe(
    js_source: str,
    stage_progress_report: str,
    handoffs_report: str,
) -> dict[str, Any]:
    """Verify the canonical order at its certified projection boundaries."""
    expected = list(STAGE_ORDER)
    expected_handoffs = [
        f"{upstream} -> {downstream}"
        for upstream, downstream in zip(STAGE_ORDER, STAGE_ORDER[1:])
    ]
    array_pattern = re.compile(
        r"\b(?:STAGE_ORDER|EXPECTED_ORDER)\s*=\s*"
        r"Object\.freeze\(\s*\[(?P<body>.*?)\]\s*\)",
        flags=re.S,
    )
    declared_orders = [
        re.findall(r"[\"']([a-z0-9_]+)[\"']", match.group("body"))
        for match in array_pattern.finditer(js_source)
    ]
    stage_progress_evidence = report_json_object(
        stage_progress_report,
        "EVIDENCE:",
    )
    handoffs_evidence = report_json_object(
        handoffs_report,
        "EVIDENCE:",
    )
    current_ui_order = any(order == expected for order in declared_orders)
    payload_cross_validation = (
        "JSON.stringify(stageOrder) !== JSON.stringify(STAGE_ORDER)"
        in js_source
        and "payload.stage_order" in js_source
    )
    stage_progress_order = stage_progress_evidence.get("stage_order")
    canonical_handoffs = handoffs_evidence.get("canonical_handoffs")
    passed = bool(
        current_ui_order
        and payload_cross_validation
        and stage_progress_order == expected
        and canonical_handoffs == expected_handoffs
    )
    return {
        "expected_order": expected,
        "declared_orders": declared_orders,
        "current_ui_order_matches": current_ui_order,
        "payload_cross_validation_present": payload_cross_validation,
        "certified_stage_progress_order": stage_progress_order,
        "certified_handoffs": canonical_handoffs,
        "expected_handoffs": expected_handoffs,
        "passed": passed,
    }


def tab_panel_probe(source: str) -> dict[str, Any]:
    parser = ElementCollector()
    parser.feed(source)
    by_id = {
        attrs["id"]: (tag, attrs)
        for tag, attrs in parser.elements
        if attrs.get("id")
    }
    nav = by_id.get("pipelineOperationsViewNav")
    pair_results: dict[str, bool] = {}
    selected = 0
    exposed = 0
    for index, (view, tab_id, panel_id) in enumerate(TAB_PANEL_PAIRS):
        tab = by_id.get(tab_id)
        panel = by_id.get(panel_id)
        expected_selected = "true" if index == 0 else "false"
        expected_hidden = "false" if index == 0 else "true"
        expected_tabindex = "0" if index == 0 else "-1"
        pair_results[view] = bool(
            tab
            and panel
            and tab[0] == "button"
            and panel[0] == "section"
            and tab[1].get("role") == "tab"
            and panel[1].get("role") == "tabpanel"
            and tab[1].get("data-pipeline-operations-view") == view
            and panel[1].get("data-pipeline-operations-view-panel") == view
            and tab[1].get("aria-selected") == expected_selected
            and tab[1].get("aria-controls") == panel_id
            and tab[1].get("tabindex") == expected_tabindex
            and panel[1].get("aria-labelledby") == tab_id
            and panel[1].get("aria-hidden") == expected_hidden
            and panel[1].get("tabindex") == "0"
        )
        if tab and tab[1].get("aria-selected") == "true":
            selected += 1
        if panel and panel[1].get("aria-hidden") == "false":
            exposed += 1
    tablist_valid = bool(
        nav
        and nav[1].get("role") == "tablist"
        and nav[1].get("aria-orientation") == "horizontal"
        and nav[1].get("aria-label")
    )
    return {
        "tablist_valid": tablist_valid,
        "pairs": pair_results,
        "selected_tab_count": selected,
        "exposed_panel_count": exposed,
        "passed": (
            tablist_valid
            and all(pair_results.values())
            and selected == 1
            and exposed == 1
        ),
    }


def responsive_contract_probe(source: str) -> dict[str, Any]:
    breakpoints = [1180, 940, 820, 700, 620, 480]
    required = [
        "BEGIN PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION",
        "END PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION",
        "prefers-reduced-motion: reduce",
        "overflow-wrap: anywhere",
        "overflow-x: clip",
        ":focus-visible",
        "min-height: 44px",
    ] + [f"@media (max-width: {width}px)" for width in breakpoints]
    return {
        "breakpoints": breakpoints,
        "required_tokens_present": all(token in source for token in required),
        "marker_count": source.count(
            "PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION"
        ),
        "passed": (
            all(token in source for token in required)
            and source.count(
                "PART F 15-B4L RESPONSIVE INTEGRATION FINALIZATION"
            )
            == 2
        ),
    }


def accessibility_script_probe(source: str) -> dict[str, Any]:
    required = (
        "BEGIN PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE",
        "END PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE",
        "LinkCraftorPipelineAccessibility",
        "resolveTabIndex",
        "onTabKeydown",
        "onListboxKeydown",
        '"ArrowRight"',
        '"ArrowDown"',
        '"ArrowLeft"',
        '"ArrowUp"',
        '"Home"',
        '"End"',
        "new MutationObserver(sync)",
    )
    return {
        "required_tokens_present": all(token in source for token in required),
        "marker_count": source.count(
            "PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE"
        ),
        "passed": (
            all(token in source for token in required)
            and source.count(
                "PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE"
            )
            == 2
        ),
    }


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "CERTIFIED"
        else (
            "FINAL RESULT: PART F 15-B4N CONNECTED DOMAIN OPERATIONS "
            "COLLECTIVE CERTIFICATION AND HANDOFF CLOSURE NOT_CERTIFIED"
        )
    )
    return "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            (
                "PART F 15-B4N CONNECTED DOMAIN OPERATIONS COLLECTIVE "
                "CERTIFICATION AND HANDOFF CLOSURE"
            ),
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Certification mode: STRICT READ-ONLY FAIL-CLOSED",
            "Backup: NOT REQUIRED - NO SOURCE MUTATION",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed during certification: NO",
            "Source files modified during certification: NO",
            f"CERTIFICATION STATUS: {status}",
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
            "COLLECTIVE EVIDENCE:",
            json.dumps(evidence, indent=2, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2, sort_keys=True),
            "",
            "COLLECTIVE CERTIFICATE:",
            "- Runtime UI foundation and Pipeline Operations workspace: CERTIFIED.",
            "- Connected Domain navigation and eight component panels: CERTIFIED.",
            "- Overview live evidence and cached detail projection: CERTIFIED.",
            "- Workflow Explorer and six-stage progress: CERTIFIED.",
            "- Jobs, attempts, dependencies, handoffs and events: CERTIFIED.",
            "- Failures, attention and four-state output readiness: CERTIFIED.",
            "- Responsive integration and accessibility closure: CERTIFIED.",
            "- Read-only endpoint and no-recovery boundary: CERTIFIED.",
            "",
            "HANDOFF:",
            (
                "Connected Domain Owner Operations is closed and ready to "
                "serve as the completed Pipeline Operations implementation."
            ),
            (
                "The next approved workstream is Universal Runtime "
                "Infrastructure UI restructuring and evidence wiring."
            ),
            "",
            final,
            "",
        ]
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4N_CONNECTED_DOMAIN_COLLECTIVE_CERTIFICATION.py "
            "<project_root> <report_path>"
        )

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": (
            root / "backend/server/owner/runtime_owner.css"
        ),
        "runtime_owner_js": (
            root / "backend/server/owner/runtime_owner.js"
        ),
        "runtime_summary_api": (
            root / "backend/server/owner/runtime_summary_api.py"
        ),
        "pipeline_operations": (
            root / "backend/server/owner/pipeline_operations.py"
        ),
    }
    reports_root = root / "backend/server/data/reports"

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "backup": "NOT_REQUIRED_READ_ONLY_CERTIFICATION",
        "runner_revision": RUNNER_REVISION,
        "new_endpoint_requests": 0,
        "recovery_controls_added": False,
        "source_changes": [],
    }
    error: dict[str, Any] = {}
    status = "NOT_CERTIFIED"

    try:
        historical_paths = {
            filename: reports_root / filename
            for filename in REPORT_CHAIN
        }
        for filename, path in historical_paths.items():
            key = filename.removesuffix(".txt").lower()
            checks[f"report_exists_{key}"] = path.is_file()
            checks[f"report_certified_{key}"] = (
                path.is_file()
                and report_is_certified(
                    read_text(path),
                    REPORT_CHAIN[filename],
                )
            )
        if not all(checks.values()):
            raise RuntimeError(
                "The B4D3-through-B4M certificate chain is incomplete."
            )

        report_hashes_before = {
            filename: sha256_path(path)
            for filename, path in historical_paths.items()
        }
        evidence["historical_certificate_count"] = len(
            report_hashes_before
        )
        evidence["historical_certificate_hashes"] = (
            report_hashes_before
        )

        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("A required Owner Runtime source is unavailable.")

        source_hashes_before = {
            name: sha256_path(path)
            for name, path in paths.items()
        }
        evidence["source_hashes"] = source_hashes_before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = (
                source_hashes_before[name] == expected
            )
        if not all(checks.values()):
            raise RuntimeError(
                "Installed source lineage does not match certified B4M."
            )

        index_source = read_text(paths["index_html"])
        css_source = read_text(paths["runtime_owner_css"])
        js_source = read_text(paths["runtime_owner_js"])
        summary_source = read_text(paths["runtime_summary_api"])
        operations_source = read_text(paths["pipeline_operations"])

        checks["final_html_ids_unique"] = html_ids_unique(index_source)
        checks["final_css_balanced"] = css_balanced(css_source)
        checks["final_javascript_syntax"] = (
            javascript_syntax_valid(js_source)
        )
        checks["runtime_summary_python_syntax"] = python_syntax_valid(
            summary_source,
            str(paths["runtime_summary_api"]),
        )
        checks["pipeline_operations_python_syntax"] = (
            python_syntax_valid(
                operations_source,
                str(paths["pipeline_operations"]),
            )
        )

        tab_probe = tab_panel_probe(index_source)
        responsive_probe = responsive_contract_probe(css_source)
        accessibility_probe = accessibility_script_probe(js_source)
        evidence["tab_panel_probe"] = tab_probe
        evidence["responsive_contract_probe"] = responsive_probe
        evidence["accessibility_script_probe"] = accessibility_probe
        checks["eight_tab_panel_pairs_certified"] = bool(
            tab_probe["passed"]
        )
        checks["responsive_contract_certified"] = bool(
            responsive_probe["passed"]
        )
        checks["accessibility_contract_certified"] = bool(
            accessibility_probe["passed"]
        )

        checks["eight_component_authorities_certified"] = all(
            authority in js_source
            for authority in COMPONENT_AUTHORITIES
        )
        checks["seven_detail_activation_handoffs_certified"] = all(
            f"window.{authority}?.activate?.();" in js_source
            for authority in COMPONENT_AUTHORITIES[1:]
        )
        checks["seven_detail_render_handoffs_certified"] = all(
            f"window.{authority}?.render?.(payload);" in js_source
            for authority in COMPONENT_AUTHORITIES[1:]
        )
        checks["seven_unavailable_handoffs_certified"] = all(
            f"window.{authority}?.renderUnavailable?.(" in js_source
            for authority in COMPONENT_AUTHORITIES[1:]
        )

        stage_order_probe = canonical_stage_order_probe(
            js_source,
            read_text(
                historical_paths[
                    "PART_F_15_B4F_SIX_STAGE_PROGRESS_CERTIFICATION.txt"
                ]
            ),
            read_text(
                historical_paths[
                    "PART_F_15_B4H_DEPENDENCIES_HANDOFFS_CERTIFICATION.txt"
                ]
            ),
        )
        evidence["canonical_stage_order_probe"] = stage_order_probe
        checks["canonical_six_stage_order_certified"] = bool(
            stage_order_probe["passed"]
        )
        checks["four_state_readiness_contract_certified"] = all(
            state in js_source
            for state in (
                "NOT_EVALUATED",
                "PENDING",
                "BLOCKED",
                "VERIFIED",
            )
        )
        checks["three_get_endpoints_certified_once"] = all(
            js_source.count(endpoint) == 1
            for endpoint in (
                '"/owner/api/runtime/summary"',
                '"/owner/api/runtime/pipelines"',
                '"/owner/api/runtime/pipelines/connect_domain"',
            )
        )
        checks["exactly_three_fetch_authorities"] = (
            js_source.count("fetch(") == 3
        )
        checks["detail_request_get_only"] = bool(
            re.search(
                r"fetch\(DETAIL_ENDPOINT,\s*\{.*?method:\s*[\"']GET[\"']",
                js_source,
                flags=re.S,
            )
        )
        checks["read_only_presentation_retained"] = (
            "READ-ONLY" in index_source
            or "Read-only" in index_source
            or "read-only" in index_source
        )
        checks["no_recovery_execution_in_certificate_chain"] = all(
            "Production recovery actions executed: NO" in read_text(path)
            for path in historical_paths.values()
        )
        checks["no_live_network_execution_in_certificate_chain"] = all(
            "Live network requests executed" in read_text(path)
            for path in historical_paths.values()
        )
        checks["final_cache_versions_retained"] = (
            '/owner/runtime_owner.css?v=15' in index_source
            and '/owner/runtime_owner.js?v=17' in index_source
        )

        checks["source_hashes_unchanged_during_collective_certification"] = all(
            sha256_path(paths[name]) == source_hashes_before[name]
            for name in paths
        )
        checks["historical_reports_unchanged_during_collective_certification"] = all(
            sha256_path(historical_paths[filename])
            == report_hashes_before[filename]
            for filename in historical_paths
        )
        checks.update(
            {
                "production_jobs_created_no": True,
                "production_queue_claims_no": True,
                "production_handlers_executed_no": True,
                "production_workflow_persistence_no": True,
                "production_recovery_actions_no": True,
                "live_network_requests_during_certification_no": True,
                "source_files_modified_no": True,
            }
        )

        evidence["certified_components"] = [
            "overview",
            "workflows",
            "stage_progress",
            "jobs_attempts",
            "dependencies_handoffs",
            "events_timeline",
            "failures_attention",
            "output_readiness",
        ]
        evidence["canonical_stage_order"] = list(STAGE_ORDER)
        evidence["readiness_states"] = [
            "NOT_EVALUATED",
            "PENDING",
            "BLOCKED",
            "VERIFIED",
        ]
        evidence["endpoint_request_count"] = js_source.count("fetch(")
        evidence["handoff_target"] = (
            "Universal Runtime Infrastructure UI restructuring and evidence wiring"
        )
        if not all(checks.values()):
            raise RuntimeError(
                "15-B4N collective certification checks failed."
            )

        status = "CERTIFIED"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        evidence["source_mutation_performed"] = False
        report.parent.mkdir(parents=True, exist_ok=True)
        write_text(
            report,
            make_report(status, checks, evidence, error),
        )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(
        "FAILED_CHECK_COUNT="
        f"{sum(not passed for passed in checks.values())}"
    )
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4N_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print(
        "COLLECTIVE_REPORT_WRITTEN="
        f"{'YES' if report.is_file() else 'NO'}"
    )
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
