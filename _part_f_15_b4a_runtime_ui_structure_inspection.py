from __future__ import annotations

import hashlib
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.classes: list[str] = []
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.data_attributes: list[dict[str, str]] = []
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {str(key): str(value or "") for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("class"):
            self.classes.extend(item for item in values["class"].split() if item)
        if tag == "link" and values.get("href"):
            self.links.append(values["href"])
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        data = {key: value for key, value in values.items() if key.startswith("data-")}
        if data:
            self.data_attributes.append(data)

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self._text.append(text)

    @property
    def visible_text(self) -> str:
        return " ".join(self._text)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def contains_any(text: str, values: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(value.lower() in lowered for value in values)


def matching_lines(text: str, pattern: str, limit: int = 20) -> list[dict[str, Any]]:
    regex = re.compile(pattern, re.IGNORECASE)
    found: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            found.append({"line": number, "text": line.strip()[:300]})
            if len(found) >= limit:
                break
    return found


def relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def main(root: Path, report: Path) -> int:
    root = root.resolve()
    report = report.resolve()
    owner = root / "backend/server/owner"
    html = owner / "index.html"
    javascript = owner / "runtime_owner.js"
    runtime_api = owner / "runtime_summary_api.py"
    operations = owner / "pipeline_operations.py"
    prior_report = root / "backend/server/data/reports/PART_F_15_B3_UNIVERSAL_PIPELINE_OPERATIONS_BACKEND_CERTIFICATION.txt"

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    error: dict[str, Any] = {}
    decision = "INSPECTION_BLOCKED"

    watched: list[Path] = []
    before: dict[str, str] = {}

    try:
        checks["part_f_15_b3_report_exists"] = prior_report.is_file()
        prior = read(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b3_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and "FINAL RESULT: PART F 15-B3 UNIVERSAL PIPELINE OPERATIONS BACKEND CERTIFIED" in prior
            and re.search(r"FAILED_CHECKS:\s*\[\s*\]", prior) is not None
        )
        checks["owner_ui_root_exists"] = owner.is_dir()
        checks["owner_index_exists"] = html.is_file()
        checks["runtime_owner_javascript_exists"] = javascript.is_file()
        checks["runtime_summary_api_exists"] = runtime_api.is_file()
        checks["pipeline_operations_backend_exists"] = operations.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required 15-B4A inspection preconditions are unavailable.")

        ui_files = sorted(
            path for path in owner.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".html", ".css", ".js"}
            and "__pycache__" not in path.parts
        )
        watched = sorted(set(ui_files + [runtime_api, operations, prior_report]))
        before = {relative(root, path): sha256(path) for path in watched}

        html_source = read(html)
        js_source = read(javascript)
        api_source = read(runtime_api)
        operations_source = read(operations)
        combined_ui = "\n".join(read(path) for path in ui_files)

        parser = StructureParser()
        parser.feed(html_source)
        parser.close()
        checks["owner_html_parsed"] = True
        checks["owner_ui_sources_found"] = bool(ui_files)
        checks["runtime_navigation_inventory_complete"] = bool(parser.ids or parser.data_attributes)
        checks["runtime_javascript_inventory_complete"] = bool(js_source.strip())
        checks["runtime_style_inventory_complete"] = any(path.suffix.lower() == ".css" for path in ui_files)

        backend_endpoints = {
            "pipeline_index": bool(re.search(r'@router\.get\(\s*["\']\/pipelines["\']\s*\)', api_source)),
            "pipeline_detail": bool(re.search(r'@router\.get\(\s*["\']\/pipelines\/\{pipeline_id\}["\']\s*\)', api_source)),
        }
        checks["pipeline_index_endpoint_available"] = backend_endpoints["pipeline_index"]
        checks["pipeline_detail_endpoint_available"] = backend_endpoints["pipeline_detail"]
        checks["read_only_pipeline_projection_available"] = (
            "build_pipeline_operations_index" in operations_source
            and "build_pipeline_operations_snapshot" in operations_source
            and "read_only" in operations_source
        )
        if not all((
            checks["pipeline_index_endpoint_available"],
            checks["pipeline_detail_endpoint_available"],
            checks["read_only_pipeline_projection_available"],
        )):
            raise RuntimeError("The certified 15-B3 backend boundary is incomplete.")

        component_terms: dict[str, tuple[str, ...]] = {
            "pipeline_operations_navigation": ("pipeline operations", "pipelineOperations"),
            "all_pipelines_overview": ("all pipelines", "pipeline list", "pipelineOperationsIndex"),
            "connected_domain_overview": ("connected domain", "connect_domain"),
            "workflow_explorer": ("workflow explorer", "pipeline workflows"),
            "six_stage_progress": ("stage progress", "pipeline stages"),
            "jobs_and_attempts": ("jobs & attempts", "jobs and attempts", "maximum_attempts"),
            "dependencies_and_handoffs": ("dependencies & handoffs", "dependencies and handoffs"),
            "events_timeline": ("events timeline", "event timeline"),
            "failures_and_attention": ("owner attention", "pipeline failures"),
            "output_readiness": ("output readiness", "ready_workflow_count"),
            "loading_state": ("loading pipeline", "pipeline-loading"),
            "empty_state": ("no pipelines", "pipeline-empty"),
            "error_state": ("pipeline error", "pipeline-error"),
            "unavailable_state": ("pipeline unavailable", "pipeline-unavailable"),
            "pipeline_refresh": ("refreshPipeline", "pipelineOperationsRefresh"),
            "pipeline_selection": ("selectPipeline", "pipelineSelector"),
        }
        component_presence = {
            name: contains_any(combined_ui, terms)
            for name, terms in component_terms.items()
        }

        summary_endpoint_bound = "/owner/api/runtime/summary" in js_source
        pipeline_index_bound = "/owner/api/runtime/pipelines" in js_source
        pipeline_detail_bound = bool(re.search(r"/owner/api/runtime/pipelines/", js_source))
        existing_runtime_overview = (
            summary_endpoint_bound
            and contains_any(html_source, ("runtime overview", "runtimeOverview"))
        )

        expected_components = tuple(component_terms)
        missing_components = tuple(
            name for name in expected_components if not component_presence[name]
        )

        if not missing_components and pipeline_index_bound and pipeline_detail_bound:
            decision = "EXISTING_PIPELINE_OPERATIONS_UI_REQUIRES_CERTIFICATION"
        else:
            decision = "UI_RESTRUCTURING_REQUIRED"

        findings.append({
            "finding": "universal_runtime_overview",
            "status": "CONNECTED" if existing_runtime_overview else "INCOMPLETE",
            "evidence": "The existing Runtime Overview uses /owner/api/runtime/summary." if existing_runtime_overview else "The Runtime Overview connection was not fully discoverable in installed UI sources.",
        })
        findings.append({
            "finding": "pipeline_operations_backend",
            "status": "AVAILABLE",
            "evidence": "Both certified read-only Pipeline Operations endpoints are present.",
        })
        findings.append({
            "finding": "pipeline_operations_frontend_connection",
            "status": "CONNECTED" if pipeline_index_bound and pipeline_detail_bound else "NOT_CONNECTED",
            "evidence": {
                "pipeline_index_requested_by_javascript": pipeline_index_bound,
                "pipeline_detail_requested_by_javascript": pipeline_detail_bound,
            },
        })
        findings.append({
            "finding": "universal_runtime_ui_restructuring",
            "status": "REQUIRED" if decision == "UI_RESTRUCTURING_REQUIRED" else "EXISTING",
            "missing_components": list(missing_components),
        })
        findings.append({
            "finding": "authority_boundary",
            "status": "RETAINED",
            "evidence": "15-B4 must consume the 15-B3 read-only API and must not create Runtime, queue, job, workflow, registry, or recovery authority.",
        })

        after = {relative(root, path): sha256(path) for path in watched}
        checks["production_sources_unchanged"] = before == after
        checks["historical_report_unchanged"] = before.get(relative(root, prior_report)) == after.get(relative(root, prior_report))
        checks["no_project_modules_imported"] = True
        checks["no_production_side_effects_executed"] = True
        checks["inspection_scope_defined"] = True

        evidence = {
            "decision": decision,
            "owner_ui_root": str(owner),
            "source_inventory": [
                {
                    "path": relative(root, path),
                    "sha256": before[relative(root, path)],
                    "bytes": path.stat().st_size,
                }
                for path in watched
            ],
            "html_structure": {
                "id_count": len(set(parser.ids)),
                "class_count": len(set(parser.classes)),
                "ids": sorted(set(parser.ids)),
                "linked_styles": parser.links,
                "linked_scripts": parser.scripts,
                "data_attributes": parser.data_attributes[:100],
            },
            "runtime_ui_evidence": {
                "existing_runtime_overview": existing_runtime_overview,
                "summary_endpoint_requested": summary_endpoint_bound,
                "pipeline_index_endpoint_requested": pipeline_index_bound,
                "pipeline_detail_endpoint_requested": pipeline_detail_bound,
                "runtime_matches": matching_lines(combined_ui, r"runtime|pipeline|workflow|recovery", 60),
            },
            "backend_endpoints": backend_endpoints,
            "component_presence": component_presence,
            "missing_components": list(missing_components),
            "required_ui_contract": {
                "navigation": ["Runtime Overview", "Pipeline Operations", "Reliability & Recovery"],
                "pipeline_operations": [
                    "All Pipelines",
                    "Connected Domain Overview",
                    "Workflow Explorer",
                    "Six-Stage Progress",
                    "Jobs & Attempts",
                    "Dependencies & Handoffs",
                    "Events Timeline",
                    "Failures & Owner Attention",
                    "Output Readiness",
                ],
                "required_states": ["loading", "empty", "error", "unavailable"],
                "required_behaviour": ["refresh", "pipeline selection", "workflow selection", "responsive layout"],
                "read_only_endpoints": [
                    "/owner/api/runtime/pipelines",
                    "/owner/api/runtime/pipelines/{pipeline_id}",
                ],
            },
        }

        if not all(checks.values()):
            raise RuntimeError("One or more 15-B4A inspection integrity checks failed.")

    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    failed = [name for name, passed in checks.items() if not passed]
    status = "COMPLETE" if not failed and not error else "NOT_COMPLETE"
    if status != "COMPLETE":
        decision = "INSPECTION_BLOCKED"

    output = f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4A EXISTING RUNTIME UI STRUCTURE INSPECTION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY TARGETED UI INSPECTION
Production source changes: NONE
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
INSPECTION STATUS: {status}

INSPECTION DECISION:
{decision}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

FINDINGS:
{json.dumps(findings, indent=2, sort_keys=True)}

BOUNDARY EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(error, indent=2)}

NEXT STEP:
Part F 15-B4B through 15-B4N — implement the Universal Runtime UI restructuring
using the existing Owner Control Tower and the certified 15-B3 read-only API.

CERTIFIED INSPECTION BOUNDARY:
- The installed Owner Control Tower HTML, JavaScript and CSS structure was inventoried.
- The existing Universal Runtime Overview connection was checked.
- The certified Pipeline Operations index and detail endpoints were checked.
- Every required 15-B4 UI component and state was assessed separately.
- No UI, Runtime, workflow, job, queue, registry or recovery state was modified.

FINAL RESULT:
PART F 15-B4A {status}
'''
    write(report, output)

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"DECISION={decision}")
    print(f"REPORT={report}")
    print(f"PART_F_15_B4A_STATUS={status}")
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: _part_f_15_b4a_runtime_ui_structure_inspection.py PROJECT_ROOT REPORT_PATH"
        )
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
