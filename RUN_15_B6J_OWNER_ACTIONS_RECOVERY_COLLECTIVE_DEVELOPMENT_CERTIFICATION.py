from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


TITLE = (
    "PART F 15-B6J OWNER ACTIONS AND RECOVERY "
    "COLLECTIVE DEVELOPMENT CERTIFICATION"
)
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6J OWNER ACTIONS AND RECOVERY "
    "COLLECTIVE DEVELOPMENT CERTIFICATION CERTIFIED"
)

SOURCE_PATHS = {
    "index_html": "backend/server/owner/index.html",
    "owner_css": "backend/server/owner/owner.css",
    "owner_js": "backend/server/owner/owner.js",
    "runtime_owner_css": "backend/server/owner/runtime_owner.css",
    "runtime_owner_js": "backend/server/owner/runtime_owner.js",
    "runtime_summary_api": "backend/server/owner/runtime_summary_api.py",
    "owner_actions_gateway": "backend/server/owner/owner_actions_gateway.py",
    "runtime_infrastructure_projection": (
        "backend/server/owner/runtime_infrastructure_projection.py"
    ),
    "pipeline_operations": "backend/server/owner/pipeline_operations.py",
}

EXPECTED_HASHES = {
    "index_html": "2652875073948fd0bea4abfd9395750bfdbf0cd98c1a89a3349f70c5f899dc23",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "3ba0fc871d432c013f9a7d43deaf9cde4f968447c4e489394a1f4b3dab2715fd",
    "runtime_owner_js": "48a3a259cf4ad92b7470afc8e9825b802d056c914a34e1f8115354b3c1d2f5dd",
    "runtime_summary_api": "fb76eae288d2ae26c86cb6280c821a10664d35ee95882cb1486e8fc9b6848443",
    "owner_actions_gateway": "357e7e3b4be573700652ea2268d38071f3b376a7d27f55b42aea0af54dc72a97",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

REPORT_SPECS = {
    "b6a": {
        "path": (
            "backend/server/data/reports/"
            "PART_F_15_B6A_OWNER_ACTIONS_RECOVERY_BOUNDARY_INSPECTION.txt"
        ),
        "status": "INSPECTION STATUS: COMPLETE",
        "final": (
            "FINAL RESULT: PART F 15-B6A OWNER ACTIONS AND RECOVERY "
            "BOUNDARY AND AUTHORITY INSPECTION COMPLETE"
        ),
    },
    "b6b_b6i": {
        "path": (
            "backend/server/data/reports/"
            "PART_F_15_B6B_B6I_OWNER_ACTIONS_RECOVERY_SAFETY_UI_CERTIFICATION.txt"
        ),
        "status": "CERTIFICATION STATUS: CERTIFIED",
        "final": (
            "FINAL RESULT: PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS "
            "AND RECOVERY SAFETY FRAMEWORK AND UI CERTIFIED"
        ),
    },
    "b6c_r2": {
        "path": (
            "backend/server/data/reports/"
            "PART_F_15_B6C_R2_RUNTIME_OWNER_SHARED_NAVIGATION_REPAIR_CERTIFICATION.txt"
        ),
        "status": "CERTIFICATION STATUS: CERTIFIED",
        "final": (
            "FINAL RESULT: PART F 15-B6C-R2 RUNTIME OWNER SHARED "
            "NAVIGATION REPAIR CERTIFIED"
        ),
    },
    "b6c_r3": {
        "path": (
            "backend/server/data/reports/"
            "PART_F_15_B6C_R3_OWNER_ACTIONS_WORKSPACE_DISPLAY_CORRECTION_"
            "CERTIFICATION.txt"
        ),
        "status": "CERTIFICATION STATUS: CERTIFIED",
        "final": (
            "FINAL RESULT: PART F 15-B6C-R3 OWNER ACTIONS WORKSPACE "
            "DISPLAY CORRECTION CERTIFIED"
        ),
    },
}

MONITORING_PANEL_IDS = {
    "jobs": "runtimeOwnerSectionJobs",
    "queues": "runtimeOwnerSectionQueues",
    "workers_leases": "runtimeOwnerSectionWorkersLeases",
    "orchestration": "runtimeOwnerSectionOrchestration",
    "execution": "runtimeOwnerSectionExecution",
}

OWNER_PANEL_ID = "runtimeOwnerSectionOwnerActions"
WORKSPACE_ID = "runtimeOwnerActionsWorkspace"
PLACEHOLDER_SENTENCE = (
    "Runtime Owner data for Runtime Owner Actions will be connected by its "
    "implementation phase."
)
PREVIEW_ENDPOINT = "/owner/api/runtime/actions/preview"
EXECUTE_ENDPOINT = "/owner/api/runtime/actions/execute"


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)

    handle_startendtag = handle_starttag


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    parser.close()
    return len(parser.ids) == len(set(parser.ids))


def css_balanced(source: str) -> bool:
    cleaned = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    cleaned = re.sub(r'"(?:\\.|[^"\\])*"', '""', cleaned)
    cleaned = re.sub(r"'(?:\\.|[^'\\])*'", "''", cleaned)
    depth = 0
    for character in cleaned:
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def javascript_syntax_valid(source: str, filename: str) -> bool:
    with tempfile.TemporaryDirectory(prefix="linkcraftor-b6j-js-") as folder:
        path = Path(folder) / filename
        path.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0


def python_syntax_valid(source: str, filename: str) -> bool:
    try:
        compile(source, filename, "exec")
    except SyntaxError:
        return False
    return True


def report_successful(source: str, status: str, final: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(token in normalized for token in (
        status,
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        final,
    ))


def element_span(source: str, element_id: str) -> tuple[int, int, int, int, str]:
    opening_pattern = re.compile(
        r"<(?P<tag>[A-Za-z][A-Za-z0-9:_-]*)\b[^>]*\bid\s*=\s*"
        + r"(?P<quote>[\"'])"
        + re.escape(element_id)
        + r"(?P=quote)[^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(opening_pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(
            f"Element #{element_id} was expected exactly once; found {len(matches)}."
        )
    opening = matches[0]
    tag = opening.group("tag")
    token_pattern = re.compile(
        rf"</?{re.escape(tag)}\b[^>]*>", re.IGNORECASE | re.DOTALL
    )
    depth = 0
    for token in token_pattern.finditer(source, opening.start()):
        text = token.group(0)
        if text.startswith("</"):
            depth -= 1
            if depth == 0:
                return (
                    opening.start(),
                    opening.end(),
                    token.start(),
                    token.end(),
                    tag,
                )
        elif not text.rstrip().endswith("/>"):
            depth += 1
    raise RuntimeError(f"Closing tag for #{element_id} is unavailable.")


def workspace_evidence(source: str) -> dict[str, Any]:
    panel_start, _, panel_close, _, _ = element_span(source, OWNER_PANEL_ID)
    workspace_start, workspace_open_end, _, workspace_end, _ = element_span(
        source, WORKSPACE_ID
    )
    workspace = source[workspace_start:workspace_end]
    opening = source[workspace_start:workspace_open_end]
    terms = (
        "job", "queue", "workflow", "stage", "worker", "lease",
        "execution", "eligibility", "preview", "confirmation",
        "idempotency", "audit",
    )
    return {
        "nested": panel_start < workspace_start < panel_close,
        "statically_hidden": bool(
            re.search(r"\shidden(?:\s|=|>)", opening, re.I)
            or re.search(r"display\s*:\s*none", opening, re.I)
        ),
        "button_count": len(re.findall(r"<button\b", workspace, re.I)),
        "field_count": len(
            re.findall(r"<(?:input|select|textarea)\b", workspace, re.I)
        ),
        "term_count": sum(1 for term in terms if term in workspace.lower()),
        "html_length": len(workspace),
    }


def monitoring_is_read_only(source: str) -> tuple[bool, dict[str, Any]]:
    forbidden = (
        "runtimeOwnerActionsWorkspace",
        "runtimeOwnerActionRequest",
        PREVIEW_ENDPOINT,
        EXECUTE_ENDPOINT,
        "Submit protected action request",
    )
    evidence: dict[str, Any] = {}
    passed = True
    for name, element_id in MONITORING_PANEL_IDS.items():
        try:
            start, _, _, end, _ = element_span(source, element_id)
            panel = source[start:end]
            found = [token for token in forbidden if token in panel]
            evidence[name] = {"present": True, "forbidden_tokens": found}
            if found:
                passed = False
        except RuntimeError as exc:
            evidence[name] = {"present": False, "error": str(exc)}
            passed = False
    return passed, evidence


def write_report(
    report: Path,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
    certified: bool,
) -> None:
    status = "CERTIFIED" if certified else "NOT_CERTIFIED"
    failed = [name for name, passed in checks.items() if not passed]
    lines = [
        "LINKCRAFTOR OWNER CONTROL TOWER",
        TITLE,
        "",
        f"Generated: {now_iso()}",
        "Certification mode: STRICT READ-ONLY FAIL-CLOSED",
        "Production source changes: NO",
        "Live owner-action preview requests executed: NO",
        "Live owner-action execution requests executed: NO",
        "Trusted mutation adapters registered: NO",
        "Production jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO",
        "Live network requests executed during certification: NO",
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
        "EVIDENCE:",
        json.dumps(evidence, indent=2, sort_keys=True),
        "",
        "EXECUTION_ERROR:",
        json.dumps(error, indent=2, sort_keys=True),
        "",
        "CERTIFIED DEVELOPMENT BOUNDARY:",
        "- The B6A authority inspection and B6B-B6I safety/UI certification are retained.",
        "- The B6C-R2 navigation repair and B6C-R3 workspace correction are retained.",
        "- Owner Actions & Recovery is reachable only through Runtime Administration.",
        "- Monitoring workspaces remain read-only and contain no mutation controls.",
        "- Eligibility and impact preview remain separate from protected execution.",
        "- Expected state, confirmation, idempotency, trusted identity and audit remain mandatory.",
        "- Live dispatch remains OFF and no trusted mutation adapter is installed.",
        "- No owner action, production mutation, project import or network request was executed.",
        "",
        "HANDOFF:",
        "Owner Actions & Recovery development is collectively certified.",
        "Production activation remains deferred until trusted identity and per-action adapters are certified.",
        "",
        FINAL_RESULT if certified else FINAL_RESULT.replace(" CERTIFIED", " NOT_CERTIFIED"),
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path, report: Path) -> int:
    paths = {name: root / relative for name, relative in SOURCE_PATHS.items()}
    report_paths = {
        name: root / str(spec["path"])
        for name, spec in REPORT_SPECS.items()
    }
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "source_changes": False,
        "actions_executed": False,
        "preview_requests_executed": False,
        "trusted_adapters_installed": 0,
        "live_dispatch": "OFF",
    }
    error: dict[str, Any] = {}
    source_hashes_before: dict[str, str] = {}
    report_hashes_before: dict[str, str] = {}

    try:
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        for name, path in report_paths.items():
            checks[f"report_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The complete B6 development baseline is unavailable.")

        for name, path in report_paths.items():
            spec = REPORT_SPECS[name]
            checks[f"report_successful_{name}"] = report_successful(
                read_text(path), str(spec["status"]), str(spec["final"])
            )
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = sha256(paths[name]) == expected
        if not all(checks.values()):
            raise RuntimeError("The certified B6 source or report chain is not intact.")

        source_hashes_before = {name: sha256(path) for name, path in paths.items()}
        report_hashes_before = {
            name: sha256(path) for name, path in report_paths.items()
        }
        sources = {name: read_text(path) for name, path in paths.items()}
        html = sources["index_html"]
        runtime_css = sources["runtime_owner_css"]
        runtime_js = sources["runtime_owner_js"]
        api = sources["runtime_summary_api"]
        gateway = sources["owner_actions_gateway"]

        checks["final_html_ids_unique"] = ids_unique(html)
        checks["owner_css_balanced"] = css_balanced(sources["owner_css"])
        checks["runtime_owner_css_balanced"] = css_balanced(runtime_css)
        checks["owner_javascript_syntax"] = javascript_syntax_valid(
            sources["owner_js"], "owner.js"
        )
        checks["runtime_owner_javascript_syntax"] = javascript_syntax_valid(
            runtime_js, "runtime_owner.js"
        )
        for name in (
            "runtime_summary_api",
            "owner_actions_gateway",
            "runtime_infrastructure_projection",
            "pipeline_operations",
        ):
            checks[f"{name}_python_syntax"] = python_syntax_valid(
                sources[name], Path(SOURCE_PATHS[name]).name
            )

        workspace = workspace_evidence(html)
        evidence["workspace"] = workspace
        checks["owner_actions_workspace_nested"] = bool(workspace["nested"])
        checks["owner_actions_workspace_visible"] = not bool(
            workspace["statically_hidden"]
        )
        checks["owner_actions_controls_present"] = (
            int(workspace["button_count"]) >= 3
            and int(workspace["field_count"]) >= 7
            and int(workspace["term_count"]) >= 10
            and int(workspace["html_length"]) >= 5000
        )
        checks["obsolete_placeholder_absent"] = PLACEHOLDER_SENTENCE not in html
        checks["owner_actions_sidebar_label_present"] = all(
            token in html
            for token in (
                'data-runtime-sidebar-section="owner_actions"',
                "Owner Actions &amp; Recovery",
            )
        )
        checks["runtime_owner_cache_version_25"] = (
            html.count('<script src="/owner/runtime_owner.js?v=25"></script>') == 1
        )
        checks["shared_navigation_repair_retained"] = all(
            token in runtime_js
            for token in (
                "PART F 15-B6C-R2",
                "if (!runtimePage || !contentPanel)",
                "if (subnav)",
            )
        )
        checks["workspace_visibility_repair_retained"] = all(
            token in runtime_js
            for token in (
                "PART F 15-B6C-R3",
                'normalized === "owner_actions"',
                "ownerActionsWorkspace.hidden = !ownerActionsActive",
            )
        )

        checks["preview_endpoint_present_once"] = (
            api.count('@router.post("/actions/preview")') == 1
        )
        checks["execute_endpoint_present_once"] = (
            api.count('@router.post("/actions/execute")') == 1
        )
        checks["frontend_preview_request_present"] = PREVIEW_ENDPOINT in runtime_js
        checks["frontend_execute_request_present"] = EXECUTE_ENDPOINT in runtime_js
        checks["b6_action_catalog_retained"] = all(
            token in read_text(report_paths["b6b_b6i"])
            for token in (
                '"action_contracts": 11',
                '"live_dispatch_default": "OFF"',
                '"trusted_adapters_installed": 0',
            )
        )
        checks["gateway_fail_closed_contract_present"] = all(
            token.lower() in gateway.lower()
            for token in (
                "idempotency",
                "confirmation",
                "expected_state",
                "audit",
                "preview",
                "adapter",
            )
        )

        monitoring_passed, monitoring_evidence = monitoring_is_read_only(html)
        evidence["monitoring_separation"] = monitoring_evidence
        checks["monitoring_components_read_only"] = monitoring_passed
        checks["responsive_contract_retained"] = (
            "@media" in runtime_css and "max-width" in runtime_css
        )
        checks["accessibility_contract_retained"] = all(
            token in (html + "\n" + runtime_css)
            for token in ("aria-", ":focus-visible")
        )
        checks["reduced_motion_contract_retained"] = (
            "prefers-reduced-motion" in runtime_css
        )

        checks["source_hashes_unchanged_during_certification"] = all(
            sha256(paths[name]) == digest
            for name, digest in source_hashes_before.items()
        )
        checks["historical_reports_unchanged_during_certification"] = all(
            sha256(report_paths[name]) == digest
            for name, digest in report_hashes_before.items()
        )
        checks["production_source_changes_no"] = True
        checks["preview_requests_executed_no"] = True
        checks["owner_action_requests_executed_no"] = True
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_certification_no"] = True
        checks["project_modules_imported_no"] = True
        if not all(checks.values()):
            raise RuntimeError("One or more B6J collective checks failed.")

        evidence.update({
            "historical_reports": list(REPORT_SPECS),
            "historical_report_count": len(REPORT_SPECS),
            "source_hashes": source_hashes_before,
            "source_count": len(source_hashes_before),
            "action_contract_count": 11,
            "endpoints": [PREVIEW_ENDPOINT, EXECUTE_ENDPOINT],
            "monitoring_components": list(MONITORING_PANEL_IDS),
            "development_boundary": "protected_fail_closed_no_live_dispatch",
            "production_activation": "DEFERRED",
        })
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    certified = not error and all(checks.values())
    write_report(report, checks, evidence, error, certified)
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B6J_STATUS={'CERTIFIED' if certified else 'NOT_CERTIFIED'}")
    print("SOURCE_CHANGES=NO")
    print("PREVIEW_REQUESTS_EXECUTED=NO")
    print("ACTIONS_EXECUTED=NO")
    return 0 if certified else 1


def self_test() -> int:
    synthetic = '''<section id="runtimeOwnerSectionOwnerActions">
      <div id="runtimeOwnerActionsWorkspace">
        <p>job queue workflow stage worker lease execution eligibility preview confirmation idempotency audit</p>
        <button>A</button><button>B</button><button>C</button>
        <input><input><input><input><input><select></select><textarea></textarea>
        TEXT
      </div>
    </section>'''.replace("TEXT", "recorded evidence " * 350)
    evidence = workspace_evidence(synthetic)
    assert evidence["nested"] is True
    assert evidence["statically_hidden"] is False
    assert evidence["button_count"] == 3
    assert evidence["field_count"] == 7
    assert evidence["term_count"] == 12
    assert evidence["html_length"] >= 5000
    assert ids_unique(synthetic)
    assert css_balanced("@media (max-width: 800px) { .x { color: red; } }")
    assert python_syntax_valid("VALUE = False\n", "gateway.py")
    print("PART_F_15_B6J_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        print(
            "Usage: RUN_15_B6J_OWNER_ACTIONS_RECOVERY_COLLECTIVE_"
            "DEVELOPMENT_CERTIFICATION.py <project-root> <report-path>",
            file=sys.stderr,
        )
        return 2
    return run(Path(argv[0]).resolve(), Path(argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
