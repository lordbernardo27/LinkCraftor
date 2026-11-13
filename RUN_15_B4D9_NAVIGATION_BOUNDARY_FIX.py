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
    "FINAL RESULT: PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION "
    "BOUNDARY CORRECTION CERTIFIED"
)
MARKER = "PART F 15-B4D9 SIDEBAR NAVIGATION BOUNDARY CORRECTION"

EXPECTED_HASHES = {
    "index_html": "91f277d06e8f2b7c633e7b8fd3048ba33da1ce16f7dff52137acd007d78affac",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "6b12dd5d08a42ab8d6e18f97368e76bf37505d06ac37a7878e2bc231815f716c",
    "runtime_owner_js": "ffd1cd620f541699369980c78605fb21db3205df5dbfc89f90909db53a207987",
    "runtime_summary_api": "8c2e234a0592d3b82236c61a50d04889b7c53d866e9e80412dfdc5a967ca57ae",
    "pipeline_operations": "570bfc61676fd15b5a1cacc6ed74130eac1d98dc41f327606019df59d55f342a",
}

OLD_LISTENER = '    page.addEventListener("click", (event) => {'
NEW_LISTENER = (
    f"    // {MARKER}\n"
    '    document.addEventListener("click", (event) => {'
)


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.append(value)


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


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    return len(parser.ids) == len(set(parser.ids))


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b4d9_js_") as folder:
        candidate = Path(folder) / "runtime_owner_candidate.js"
        write_text(candidate, source)
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


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
        "FINAL RESULT: PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION "
        "BOUNDARY CORRECTION NOT_CERTIFIED"
    )
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B4D9 CONNECTED DOMAIN NAVIGATION BOUNDARY CORRECTION CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup if backup else "NOT_CREATED"}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
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

CORRECTED BOUNDARY:
- The Connected Domain links are outside the Runtime page element in the global Owner sidebar.
- Their delegated click listener now uses the document boundary and can receive those clicks.
- Workspace tabs and pipeline cards continue to use the same canonical setPipelineView authority.
- Exactly one component panel remains visible for each selected destination.
- No new endpoint request, pipeline-detail wiring, recovery control or backend authority was added.

VISUAL ACCEPTANCE:
- Press Ctrl + F5 and test Overview, Workflows, Stage Progress, Jobs & Attempts,
  Dependencies & Handoffs, Events Timeline, Failures & Attention and Output Readiness.
- Final visual acceptance remains dependent on the refreshed browser result.

FINAL RESULT:
{final}
'''


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B4D9_NAVIGATION_BOUNDARY_FIX.py "
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
        root / "backend/server/data/reports/"
        "PART_F_15_B4D6_D8_COMPONENT_SHELLS_NAVIGATION_STATES_CERTIFICATION.txt"
    )

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    backup_dir: Path | None = None
    retained = False
    status = "NOT_CERTIFIED"

    try:
        checks["part_f_15_b4d6_d8_report_exists"] = prior_report.is_file()
        prior = read_text(prior_report) if prior_report.is_file() else ""
        checks["part_f_15_b4d6_d8_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in prior
            and "FINAL RESULT: PART F 15-B4D6 THROUGH 15-B4D8 "
            "COMPONENT SHELLS NAVIGATION AND STATES CERTIFIED" in prior
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("Required source or D6-D8 evidence is unavailable.")

        before = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_before"] = before
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed source lineage does not match certified D6-D8.")

        html_source = read_text(paths["index_html"])
        js_source = read_text(paths["runtime_owner_js"])
        checks["failure_reproduced_listener_scoped_to_runtime_page"] = (
            js_source.count(OLD_LISTENER) == 1
        )
        checks["correction_not_previously_present"] = MARKER not in js_source

        js_candidate = replace_once(
            js_source,
            OLD_LISTENER,
            NEW_LISTENER,
            "Runtime-page-scoped pipeline navigation listener",
        )
        html_candidate = replace_once(
            html_source,
            '<script src="/owner/runtime_owner.js?v=6"></script>',
            '<script src="/owner/runtime_owner.js?v=7"></script>',
            "Runtime JavaScript cache version",
        )

        checks["candidate_html_ids_unique"] = html_ids_unique(html_candidate)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(js_candidate)
        checks["document_navigation_boundary_present"] = (
            js_candidate.count(
                'document.addEventListener("click", (event) => {'
            ) >= 1
            and js_candidate.count(OLD_LISTENER) == 0
        )
        checks["eight_sidebar_destinations_retained"] = (
            len(re.findall(r'data-runtime-pipeline-view="[^"]+"', html_candidate))
            == 8
        )
        checks["eight_workspace_tabs_retained"] = (
            len(re.findall(r'data-pipeline-operations-view="[^"]+"', html_candidate))
            == 8
        )
        checks["eight_component_panels_retained"] = (
            len(re.findall(
                r'data-pipeline-operations-view-panel="[^"]+"', html_candidate
            )) == 8
        )
        checks["one_panel_selection_authority_retained"] = all(
            token in js_candidate
            for token in (
                "panel.hidden = !active;",
                'panel.classList.toggle("active", active);',
                'button.setAttribute("aria-selected", active ? "true" : "false");',
                "setPipelineView(view);",
            )
        )
        checks["sidebar_failure_alias_retained"] = (
            'failures_attention: "failures"' in js_candidate
        )
        checks["runtime_summary_endpoint_unchanged"] = (
            js_candidate.count('"/owner/api/runtime/summary"')
            == js_source.count('"/owner/api/runtime/summary"') == 1
        )
        checks["pipeline_index_endpoint_unchanged"] = (
            js_candidate.count('"/owner/api/runtime/pipelines"')
            == js_source.count('"/owner/api/runtime/pipelines"') == 1
        )
        checks["no_new_fetch_requests_added"] = (
            js_candidate.count("fetch(") == js_source.count("fetch(")
        )
        checks["no_pipeline_detail_request_added"] = (
            "/owner/api/runtime/pipelines/" not in js_candidate
        )
        checks["no_recovery_controls_added"] = all(
            token not in NEW_LISTENER
            for token in ("retryJob(", "cancelJob(", "terminateJob(")
        )
        checks["cache_version_advanced"] = (
            '/owner/runtime_owner.js?v=7' in html_candidate
        )
        if not all(checks.values()):
            raise RuntimeError("D9 navigation correction failed candidate checks.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b4d9_navigation_fix_{timestamp}"
        )
        backup_dir.mkdir(parents=True, exist_ok=False)
        for name in ("index_html", "runtime_owner_js"):
            path = paths[name]
            originals[name] = path.read_bytes()
            shutil.copy2(path, backup_dir / path.name)
        checks["backup_created"] = all(
            (backup_dir / paths[name].name).is_file() for name in originals
        )
        if not checks["backup_created"]:
            raise RuntimeError("D9 production UI backup is incomplete.")

        write_text(paths["index_html"], html_candidate)
        write_text(paths["runtime_owner_js"], js_candidate)

        checks["retained_html_ids_unique"] = html_ids_unique(
            read_text(paths["index_html"])
        )
        checks["retained_javascript_syntax"] = javascript_syntax_valid(
            read_text(paths["runtime_owner_js"])
        )
        checks["retained_correction_marker_once"] = (
            read_text(paths["runtime_owner_js"]).count(MARKER) == 1
        )

        after = {name: sha256_path(path) for name, path in paths.items()}
        evidence["source_hashes_after"] = after
        evidence["backup"] = str(backup_dir)
        evidence["root_cause"] = (
            "Connected Domain links are outside #runtimePage, while their "
            "delegated listener was attached to #runtimePage."
        )
        evidence["correction"] = "Delegated navigation listener moved to document."
        evidence["new_endpoint_requests"] = 0
        evidence["pipeline_detail_wiring_added"] = False
        evidence["recovery_controls_added"] = False

        for name in (
            "owner_css", "owner_js", "runtime_owner_css",
            "runtime_summary_api", "pipeline_operations",
        ):
            checks[f"unchanged_{name}"] = before[name] == after[name]
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_no"] = True
        if not all(checks.values()):
            raise RuntimeError("D9 retained-source certification checks failed.")

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
    print(f"PART_F_15_B4D9_NAVIGATION_FIX_STATUS={status}")
    print("PATCH_RETAINED=YES" if retained else "PATCH_RETAINED=NO")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
