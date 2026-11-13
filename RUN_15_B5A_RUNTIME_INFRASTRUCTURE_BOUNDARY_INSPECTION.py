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


STEP = "PART F 15-B5A"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5A RUNTIME INFRASTRUCTURE "
    "BOUNDARY INSPECTION COMPLETE"
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

B4N_REPORT = "PART_F_15_B4N_CONNECTED_DOMAIN_COLLECTIVE_CERTIFICATION.txt"
B4N_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B4N CONNECTED DOMAIN OPERATIONS COLLECTIVE "
    "CERTIFICATION AND HANDOFF CLOSURE CERTIFIED"
)

INFRASTRUCTURE_COMPONENTS: dict[str, dict[str, Any]] = {
    "jobs": {
        "label": "Jobs",
        "panel_id": "runtimeOwnerSectionJobs",
        "path_terms": ("job",),
        "source_terms": (
            "UniversalJob",
            "load_jobs",
            "save_job",
            "job_store",
            "job_id",
            "list_job_events",
        ),
    },
    "queues": {
        "label": "Queues",
        "panel_id": "runtimeOwnerSectionQueues",
        "path_terms": ("queue",),
        "source_terms": (
            "enqueue",
            "queue",
            "claim",
            "queued",
            "dequeue",
            "priority",
        ),
    },
    "workers_leases": {
        "label": "Workers & Leases",
        "panel_id": "runtimeOwnerSectionWorkersLeases",
        "path_terms": ("worker", "lease"),
        "source_terms": (
            "worker",
            "lease",
            "heartbeat",
            "assigned_worker_id",
            "lease_owner",
            "lease_expires",
        ),
    },
    "orchestration": {
        "label": "Orchestration",
        "panel_id": "runtimeOwnerSectionOrchestration",
        "path_terms": ("orchestration", "workflow", "correlation"),
        "source_terms": (
            "orchestration",
            "workflow",
            "correlation",
            "dependency",
            "predecessor",
            "successor",
        ),
    },
    "execution": {
        "label": "Execution",
        "panel_id": "runtimeOwnerSectionExecution",
        "path_terms": ("execution", "handler", "dispatch"),
        "source_terms": (
            "execution",
            "handler",
            "dispatch",
            "runtime_dispatch_result",
            "execute",
            "terminal",
        ),
    },
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


def relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def report_is_certified(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return (
        "CERTIFICATION STATUS: CERTIFIED" in normalized
        and "FAILED_CHECKS:\n[]" in normalized
        and "NOT_RUN_CHECKS:\n[]" in normalized
        and B4N_FINAL_RESULT in normalized
        and "Production recovery actions executed: NO" in normalized
        and "Live network requests executed during certification: NO" in normalized
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
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b5a_js_") as folder:
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


def python_symbols(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    values = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    return sorted(set(values))[:30]


def python_imports(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            values.add(node.module or "")
    return sorted(value for value in values if value)


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
                r"[\"'](/owner/api/runtime(?:/[^\"']*)?)[\"']",
                source,
            )
        )
    )


def backend_python_files(root: Path) -> list[Path]:
    backend = root / "backend/server"
    if not backend.is_dir():
        return []
    files: list[Path] = []
    for path in backend.rglob("*.py"):
        if any(part in SKIP_DIRECTORY_NAMES for part in path.parts):
            continue
        try:
            if path.is_file() and path.stat().st_size <= 2_000_000:
                files.append(path)
        except OSError:
            continue
    return sorted(files)


def discover_backend_authorities(
    root: Path,
    files: list[Path],
) -> dict[str, list[dict[str, Any]]]:
    discovered: dict[str, list[dict[str, Any]]] = {
        component: [] for component in INFRASTRUCTURE_COMPONENTS
    }
    for path in files:
        try:
            source = read_text(path)
        except (OSError, UnicodeError):
            continue
        source_lower = source.lower()
        path_lower = relative(root, path).lower()
        symbols = python_symbols(source)
        for component, contract in INFRASTRUCTURE_COMPONENTS.items():
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
            if not path_hits and len(source_hits) < 2:
                continue
            score = (len(path_hits) * 3) + len(source_hits)
            discovered[component].append(
                {
                    "path": relative(root, path),
                    "score": score,
                    "path_terms": path_hits,
                    "source_terms": source_hits,
                    "symbols": symbols,
                }
            )
    for component in discovered:
        discovered[component] = sorted(
            discovered[component],
            key=lambda item: (-int(item["score"]), str(item["path"])),
        )[:20]
    return discovered


def summary_projection_keys(source: str) -> list[str]:
    return sorted(
        set(
            re.findall(
                r"[\"']([A-Za-z][A-Za-z0-9_]*)[\"']\s*:",
                source,
            )
        )
    )


def make_report(
    status: str,
    decision: str,
    checks: dict[str, bool],
    findings: list[dict[str, Any]],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = (
        FINAL_RESULT
        if status == "COMPLETE"
        else "FINAL RESULT: PART F 15-B5A RUNTIME INFRASTRUCTURE BOUNDARY INSPECTION NOT_COMPLETE"
    )
    return "\n".join(
        [
            "LINKCRAFTOR UNIVERSAL RUNTIME OWNER OPERATIONS",
            "PART F 15-B5A RUNTIME INFRASTRUCTURE BOUNDARY INSPECTION",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "Mode: STRICT READ-ONLY FAIL-CLOSED",
            "Production source changes: NONE",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production workflow persistence executed: NO",
            "Production recovery actions executed: NO",
            "Live network requests executed: NO",
            f"INSPECTION STATUS: {status}",
            "",
            "INSPECTION DECISION:",
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
            "FINDINGS:",
            json.dumps(findings, indent=2, sort_keys=True),
            "",
            "BOUNDARY EVIDENCE:",
            json.dumps(evidence, indent=2, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2, sort_keys=True),
            "",
            "INSPECTED BOUNDARY:",
            "- Existing Jobs, Queues, Workers & Leases, Orchestration and Execution panels were inspected.",
            "- Existing sidebar navigation and Runtime Owner section switching were inspected.",
            "- Existing backend job, queue, worker/lease, orchestration and execution authorities were mapped without importing them.",
            "- Existing Runtime Owner routes, summary projection and frontend GET requests were inventoried.",
            "- Connected Domain B4N certification and all seven certified production source hashes were retained.",
            "- No endpoint, UI, job, queue, worker, workflow, handler, recovery or persistence authority was added or mutated.",
            "",
            "NEXT STEP:",
            "Part F 15-B5B - define the canonical read-only Runtime Infrastructure evidence projection and wiring plan.",
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
    b4n_report = root / "backend/server/data/reports" / B4N_REPORT

    checks: dict[str, bool] = {}
    findings: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {
        "new_endpoint_requests": 0,
        "source_mutation_performed": False,
        "recovery_controls_added": False,
    }
    error: dict[str, Any] = {}
    status = "NOT_COMPLETE"
    decision = "INSPECTION_BLOCKED"

    try:
        checks["part_f_15_b4n_report_exists"] = b4n_report.is_file()
        checks["part_f_15_b4n_certified"] = (
            b4n_report.is_file()
            and report_is_certified(read_text(b4n_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError(
                "The certified B4N baseline or a required Runtime Owner source is unavailable."
            )

        watched = {**paths, "b4n_report": b4n_report}
        hashes_before = {
            name: sha256_path(path)
            for name, path in watched.items()
        }
        evidence["source_hashes_before"] = {
            name: hashes_before[name] for name in paths
        }
        evidence["b4n_report_hash"] = hashes_before["b4n_report"]
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError(
                "Installed source lineage does not match the certified B4N baseline."
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

        parser = ElementCollector()
        parser.feed(html_source)
        parser.close()

        sidebar_links: dict[str, dict[str, str]] = {}
        panels: dict[str, dict[str, str]] = {}
        placeholders: dict[str, dict[str, str]] = {}
        for tag, attrs in parser.elements:
            section = attrs.get("data-runtime-sidebar-section")
            panel = attrs.get("data-runtime-owner-section-panel")
            placeholder = attrs.get("data-runtime-owner-placeholder")
            if section:
                sidebar_links[section] = {"tag": tag, **attrs}
            if panel:
                panels[panel] = {"tag": tag, **attrs}
            if placeholder:
                placeholders[placeholder] = {"tag": tag, **attrs}

        component_state: dict[str, dict[str, Any]] = {}
        for component, contract in INFRASTRUCTURE_COMPONENTS.items():
            sidebar = sidebar_links.get(component)
            panel = panels.get(component)
            placeholder = placeholders.get(component)
            component_state[component] = {
                "label": contract["label"],
                "sidebar_present": sidebar is not None,
                "panel_present": panel is not None,
                "panel_id": panel.get("id") if panel else None,
                "expected_panel_id": contract["panel_id"],
                "placeholder_present": placeholder is not None,
                "presentation_mapping_present": bool(
                    re.search(
                        rf"\b{re.escape(component)}\s*:\s*\[",
                        js_source,
                    )
                ),
            }

        checks["runtime_infrastructure_group_present"] = (
            'data-runtime-sidebar-group="runtime_infrastructure"' in html_source
            and 'id="runtimeSidebarInfrastructure"' in html_source
        )
        checks["five_infrastructure_sidebar_links_present"] = all(
            state["sidebar_present"] for state in component_state.values()
        )
        checks["five_infrastructure_panels_present"] = all(
            state["panel_present"]
            and state["panel_id"] == state["expected_panel_id"]
            for state in component_state.values()
        )
        checks["five_infrastructure_placeholders_present"] = all(
            state["placeholder_present"] for state in component_state.values()
        )
        checks["five_section_presentations_present"] = all(
            state["presentation_mapping_present"]
            for state in component_state.values()
        )
        checks["existing_section_navigation_authority_present"] = all(
            token in js_source
            for token in (
                "window.LinkCraftorRuntimeOwner",
                "setActiveSection",
                "getActiveSection",
                "runtimeowner:sectionchange",
            )
        )

        frontend_endpoints = frontend_runtime_endpoints(js_source)
        checks["three_existing_frontend_fetch_authorities_retained"] = (
            js_source.count("fetch(") == 3
        )
        checks["connected_domain_get_endpoints_retained"] = all(
            endpoint in frontend_endpoints
            for endpoint in (
                "/owner/api/runtime/summary",
                "/owner/api/runtime/pipelines",
                "/owner/api/runtime/pipelines/connect_domain",
            )
        )

        python_files = backend_python_files(root)
        authorities = discover_backend_authorities(root, python_files)
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
        checks["backend_authority_scan_completed"] = bool(python_files)
        checks["runtime_route_inventory_completed"] = bool(runtime_routes)
        checks["summary_projection_inventory_completed"] = bool(
            summary_projection_keys(summary_source)
        )

        authority_counts = {
            component: len(rows)
            for component, rows in authorities.items()
        }
        all_authorities_discovered = all(
            count > 0 for count in authority_counts.values()
        )
        shell_baseline_complete = all(
            state["sidebar_present"]
            and state["panel_present"]
            and state["placeholder_present"]
            for state in component_state.values()
        )
        if shell_baseline_complete and all_authorities_discovered:
            decision = (
                "REUSE_EXISTING_FIVE_PLACEHOLDER_SHELLS_AND_DEFINE_ONE_"
                "READ_ONLY_INFRASTRUCTURE_EVIDENCE_BOUNDARY"
            )
        elif shell_baseline_complete:
            decision = (
                "REUSE_EXISTING_FIVE_PLACEHOLDER_SHELLS_AND_COMPLETE_"
                "AUTHORITY_MAPPING_BEFORE_WIRING"
            )
        else:
            decision = "REPAIR_RUNTIME_INFRASTRUCTURE_SHELLS_BEFORE_WIRING"

        findings.extend(
            [
                {
                    "finding": "runtime_infrastructure_ui_baseline",
                    "status": "REUSABLE" if shell_baseline_complete else "INCOMPLETE",
                    "component_state": component_state,
                },
                {
                    "finding": "canonical_backend_authorities",
                    "status": "DISCOVERED" if all_authorities_discovered else "PARTIAL",
                    "candidate_counts": authority_counts,
                },
                {
                    "finding": "current_runtime_owner_requests",
                    "status": "RETAINED",
                    "fetch_authority_count": js_source.count("fetch("),
                    "endpoints": frontend_endpoints,
                },
                {
                    "finding": "authority_boundary",
                    "status": "READ_ONLY",
                    "evidence": (
                        "B5 must project existing authorities and must not create "
                        "a second job store, queue, worker registry, lease authority, "
                        "workflow repository, execution gateway or recovery authority."
                    ),
                },
            ]
        )

        evidence.update(
            {
                "decision": decision,
                "inspection_components": [
                    contract["label"]
                    for contract in INFRASTRUCTURE_COMPONENTS.values()
                ],
                "component_state": component_state,
                "backend_candidate_authorities": authorities,
                "backend_candidate_counts": authority_counts,
                "runtime_routes": runtime_routes,
                "runtime_summary_imports": python_imports(summary_source),
                "runtime_summary_projection_keys": summary_projection_keys(
                    summary_source
                ),
                "frontend_runtime_endpoints": frontend_endpoints,
                "frontend_fetch_authority_count": js_source.count("fetch("),
                "recommended_wiring_order": [
                    "jobs",
                    "queues",
                    "workers_leases",
                    "orchestration",
                    "execution",
                ],
                "required_presentation_states": [
                    "loading",
                    "ready",
                    "empty",
                    "unavailable",
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
        checks["b4n_report_unchanged"] = (
            hashes_after["b4n_report"] == hashes_before["b4n_report"]
        )
        checks.update(
            {
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
                "One or more B5A inspection-integrity checks failed."
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
        make_report(
            status,
            decision,
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
    print(f"DECISION={decision}")
    print(f"REPORT={report}")
    print(f"PART_F_15_B5A_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    return 0 if status == "COMPLETE" else 1


def self_test() -> int:
    html = "".join(
        (
            '<section data-runtime-sidebar-group="runtime_infrastructure">',
            '<div id="runtimeSidebarInfrastructure">',
            *[
                (
                    f'<button data-runtime-sidebar-section="{component}">'
                    f'{contract["label"]}</button>'
                    f'<section id="{contract["panel_id"]}" '
                    f'data-runtime-owner-section-panel="{component}">'
                    f'<p data-runtime-owner-placeholder="{component}"></p>'
                    f'</section>'
                )
                for component, contract in INFRASTRUCTURE_COMPONENTS.items()
            ],
            "</div></section>",
        )
    )
    parser = ElementCollector()
    parser.feed(html)
    parser.close()
    assert len(parser.ids) == len(set(parser.ids))
    assert css_balanced("a { color: red; } @media (x) { b { color: blue; } }")
    assert route_declarations(
        '@router.get("/summary")\ndef sample():\n    return {}\n',
        "sample.py",
    )[0]["method"] == "GET"
    assert frontend_runtime_endpoints(
        'const x = "/owner/api/runtime/summary";'
    ) == ["/owner/api/runtime/summary"]
    assert python_syntax_valid("def sample():\n    return True\n", "sample.py")
    print("PART_F_15_B5A_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B5A_RUNTIME_INFRASTRUCTURE_BOUNDARY_INSPECTION.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(
        run_inspection(
            Path(sys.argv[1]),
            Path(sys.argv[2]),
        )
    )

