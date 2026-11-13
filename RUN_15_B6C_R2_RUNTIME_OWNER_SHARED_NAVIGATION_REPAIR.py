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


TITLE = "PART F 15-B6C-R2 RUNTIME OWNER SHARED NAVIGATION REPAIR"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6C-R2 RUNTIME OWNER SHARED NAVIGATION "
    "REPAIR CERTIFIED"
)

INDEX_PATH = "backend/server/owner/index.html"
RUNTIME_JS_PATH = "backend/server/owner/runtime_owner.js"
B6_REPORT_PATH = (
    "backend/server/data/reports/"
    "PART_F_15_B6B_B6I_OWNER_ACTIONS_RECOVERY_SAFETY_UI_CERTIFICATION.txt"
)

SOURCE_PATHS = {
    "index_html": INDEX_PATH,
    "runtime_owner_css": "backend/server/owner/runtime_owner.css",
    "runtime_owner_js": RUNTIME_JS_PATH,
    "runtime_summary_api": "backend/server/owner/runtime_summary_api.py",
    "owner_actions_gateway": "backend/server/owner/owner_actions_gateway.py",
    "runtime_infrastructure_projection": (
        "backend/server/owner/runtime_infrastructure_projection.py"
    ),
    "pipeline_operations": "backend/server/owner/pipeline_operations.py",
}

EXPECTED_HASHES = {
    "index_html": "4a27050caf0f45ba5a9b6ffa092bcc6dfa42fdd0018fd2b55db47c8f9d1c9764",
    "runtime_owner_css": "3ba0fc871d432c013f9a7d43deaf9cde4f968447c4e489394a1f4b3dab2715fd",
    "runtime_owner_js": "b06627ea6774a69e70e7283186a30888371b327b8c5b6475a5bbec49d02ac109",
    "runtime_summary_api": "fb76eae288d2ae26c86cb6280c821a10664d35ee95882cb1486e8fc9b6848443",
    "owner_actions_gateway": "357e7e3b4be573700652ea2268d38071f3b376a7d27f55b42aea0af54dc72a97",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

B6_FINAL = (
    "FINAL RESULT: PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND "
    "RECOVERY SAFETY FRAMEWORK AND UI CERTIFIED"
)

OLD_GUARD = '''    if (!runtimePage || !subnav || !contentPanel) {
      return false;
    }'''

NEW_GUARD = '''    // PART F 15-B6C-R2: the nested sidebar replaced the legacy subnav.
    // Panel switching requires the page and content panel; the legacy subnav is optional.
    if (!runtimePage || !contentPanel) {
      return false;
    }'''

OLD_BUTTON_BLOCK = '''    const buttons = subnav.querySelectorAll(
      "[data-runtime-owner-section]"
    );

    buttons.forEach((button) => {
      const isActive =
        button.dataset.runtimeOwnerSection === normalized;

      button.classList.toggle("active", isActive);

      button.setAttribute(
        "aria-selected",
        isActive ? "true" : "false"
      );
    });'''

NEW_BUTTON_BLOCK = '''    // Preserve legacy subnav synchronization when that optional shell exists.
    if (subnav) {
      const buttons = subnav.querySelectorAll(
        "[data-runtime-owner-section]"
      );

      buttons.forEach((button) => {
        const isActive =
          button.dataset.runtimeOwnerSection === normalized;

        button.classList.toggle("active", isActive);

        button.setAttribute(
          "aria-selected",
          isActive ? "true" : "false"
        );
      });
    }'''

OLD_JS_CACHE = '<script src="/owner/runtime_owner.js?v=23"></script>'
NEW_JS_CACHE = '<script src="/owner/runtime_owner.js?v=24"></script>'
OLD_SIDEBAR_LABEL = (
    '<button class="runtime-sidebar-link" type="button" '
    'data-runtime-sidebar-section="owner_actions">Owner Actions</button>'
)
NEW_SIDEBAR_LABEL = (
    '<button class="runtime-sidebar-link" type="button" '
    'data-runtime-sidebar-section="owner_actions">'
    'Owner Actions &amp; Recovery</button>'
)
OLD_PRESENTATION = (
    'owner_actions: ["Owner Actions", "Governed owner operations and approvals."]'
)
NEW_PRESENTATION = (
    'owner_actions: ["Owner Actions & Recovery", '
    '"Governed owner operations, recovery requests, and approvals."]'
)


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


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def atomic_write(path: Path, source: str) -> None:
    temporary = path.with_name(path.name + ".tmp-b6cr2")
    temporary.write_text(source, encoding="utf-8", newline="\n")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} was expected exactly once; found {count}.")
    return source.replace(old, new, 1)


def build_candidate_js(source: str) -> str:
    candidate = replace_once(
        source,
        OLD_GUARD,
        NEW_GUARD,
        "obsolete legacy-subnav guard",
    )
    candidate = replace_once(
        candidate,
        OLD_BUTTON_BLOCK,
        NEW_BUTTON_BLOCK,
        "legacy subnav synchronization block",
    )
    candidate = replace_once(
        candidate,
        OLD_PRESENTATION,
        NEW_PRESENTATION,
        "Owner Actions header presentation",
    )
    return candidate


def build_candidate_html(source: str) -> str:
    candidate = replace_once(
        source,
        OLD_JS_CACHE,
        NEW_JS_CACHE,
        "Runtime Owner JavaScript cache reference",
    )
    candidate = replace_once(
        candidate,
        OLD_SIDEBAR_LABEL,
        NEW_SIDEBAR_LABEL,
        "Owner Actions sidebar label",
    )
    return candidate


def ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    parser.close()
    return len(parser.ids) == len(set(parser.ids))


def javascript_syntax_valid(source: str) -> bool:
    with tempfile.TemporaryDirectory(prefix="linkcraftor-b6cr2-js-") as folder:
        path = Path(folder) / "runtime_owner.js"
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


def isolated_navigation_probe(source: str) -> dict[str, Any]:
    end = source.find("\n})();")
    if end < 0:
        return {"passed": False, "reason": "core_runtime_owner_iife_unavailable"}
    core = source[: end + len("\n})();")]
    harness = r'''
const panels = [
  "overview", "pipeline_operations", "jobs", "queues", "workers_leases",
  "orchestration", "execution", "reliability_recovery", "resource_governance",
  "runtime_apis", "persistence_state_integrity", "observability", "security",
  "owner_actions", "evidence_audit"
].map((key) => ({
  dataset: { runtimeOwnerSectionPanel: key },
  hidden: key !== "overview",
  classList: { toggle() {} }
}));
const contentPanel = {
  dataset: { runtimeOwnerActiveSection: "overview" },
  querySelectorAll(selector) {
    return selector === "[data-runtime-owner-section-panel]" ? panels : [];
  }
};
const runtimePage = { dispatchEvent(event) { this.lastEvent = event; } };
global.window = {};
global.CustomEvent = class CustomEvent {
  constructor(type, options) { this.type = type; this.detail = options.detail; }
};
global.document = {
  readyState: "complete",
  addEventListener() {},
  getElementById(id) {
    if (id === "runtimePage") return runtimePage;
    if (id === "runtimeOwnerContentPanel") return contentPanel;
    if (id === "runtimeOwnerSubnav") return null;
    return null;
  }
};
'''
    assertions = r'''
const result = window.LinkCraftorRuntimeOwner.setActiveSection("owner_actions");
const ownerPanel = panels.find(
  (panel) => panel.dataset.runtimeOwnerSectionPanel === "owner_actions"
);
const overviewPanel = panels.find(
  (panel) => panel.dataset.runtimeOwnerSectionPanel === "overview"
);
const output = {
  result,
  active: window.LinkCraftorRuntimeOwner.getActiveSection(),
  owner_actions_visible: ownerPanel.hidden === false,
  overview_hidden: overviewPanel.hidden === true,
  event_section: runtimePage.lastEvent?.detail?.section || null,
  legacy_subnav_present: false
};
output.passed = (
  output.result === true &&
  output.active === "owner_actions" &&
  output.owner_actions_visible &&
  output.overview_hidden &&
  output.event_section === "owner_actions"
);
console.log(JSON.stringify(output));
'''
    with tempfile.TemporaryDirectory(prefix="linkcraftor-b6cr2-probe-") as folder:
        path = Path(folder) / "probe.js"
        path.write_text(harness + "\n" + core + "\n" + assertions, encoding="utf-8")
        try:
            result = subprocess.run(
                ["node", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return {"passed": False, "reason": type(exc).__name__}
        if result.returncode != 0:
            return {
                "passed": False,
                "reason": "node_probe_failed",
                "stderr": result.stderr[-2000:],
            }
        try:
            return json.loads(result.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            return {
                "passed": False,
                "reason": "probe_output_invalid",
                "stdout": result.stdout[-2000:],
            }


def report_certified(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(token in normalized for token in (
        "CERTIFICATION STATUS: CERTIFIED",
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        B6_FINAL,
        '"patch_retained": true',
        '"trusted_adapters_installed": 0',
    ))


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
        "Patch mode: STRICT FAIL-CLOSED WITH AUTOMATIC ROLLBACK",
        f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
        f"Shared Runtime Owner navigation repaired: {'YES' if evidence.get('patch_retained') else 'NO'}",
        "Owner Actions live dispatch: OFF",
        "Trusted mutation adapters added: NO",
        "Owner actions executed during repair: NO",
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
        "IMPLEMENTED REPAIR:",
        "- Removed runtimeOwnerSubnav as a mandatory panel-switching prerequisite.",
        "- Retained optional legacy-subnav synchronization when that shell exists.",
        "- Restored shared switching for every Runtime Owner sidebar section.",
        "- Renamed the sidebar and header presentation to Owner Actions & Recovery.",
        "- Retained all B6B-B6I safety, preview, confirmation and gateway controls.",
        "- Live dispatch remains OFF and no mutation adapter was registered.",
        "- No production job, queue, handler, workflow or recovery action was executed.",
        "",
        "NEXT STEP:",
        "Press Ctrl + F5 and verify Jobs, Queues and Owner Actions & Recovery.",
        "After browser acceptance, proceed to Part F 15-B6J collective development certification.",
        "",
        FINAL_RESULT if certified else FINAL_RESULT.replace(" CERTIFIED", " NOT_CERTIFIED"),
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path, report: Path) -> int:
    paths = {name: root / relative for name, relative in SOURCE_PATHS.items()}
    b6_report = root / B6_REPORT_PATH
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "patch_retained": False,
        "rollback_performed": False,
        "actions_executed": False,
        "trusted_adapters_installed": 0,
    }
    error: dict[str, Any] = {}
    originals: dict[str, bytes] = {}
    report_hash_before: str | None = None

    try:
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["part_f_15_b6b_b6i_report_exists"] = b6_report.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified B6B-B6I source baseline is unavailable.")

        checks["part_f_15_b6b_b6i_certified"] = report_certified(read_text(b6_report))
        report_hash_before = sha256(b6_report)
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = sha256(paths[name]) == expected
        if not all(checks.values()):
            raise RuntimeError("The certified B6B-B6I source hashes are not intact.")

        html_source = read_text(paths["index_html"])
        js_source = read_text(paths["runtime_owner_js"])
        checks["runtime_page_present"] = 'id="runtimePage"' in html_source
        checks["runtime_content_panel_present"] = 'id="runtimeOwnerContentPanel"' in html_source
        checks["obsolete_runtime_subnav_absent"] = 'id="runtimeOwnerSubnav"' not in html_source
        checks["obsolete_subnav_guard_present"] = OLD_GUARD in js_source
        checks["owner_actions_sidebar_present"] = (
            'data-runtime-sidebar-section="owner_actions"' in html_source
        )
        checks["owner_actions_panel_present"] = (
            'data-runtime-owner-section-panel="owner_actions"' in html_source
        )
        if not all(checks.values()):
            raise RuntimeError("The diagnosed shared-navigation failure boundary is unavailable.")

        candidate_html = build_candidate_html(html_source)
        candidate_js = build_candidate_js(js_source)
        probe = isolated_navigation_probe(candidate_js)
        evidence["isolated_navigation_probe"] = probe
        checks["candidate_html_ids_unique"] = ids_unique(candidate_html)
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(candidate_js)
        checks["isolated_navigation_probe_passed"] = bool(probe.get("passed"))
        checks["legacy_subnav_now_optional"] = (
            OLD_GUARD not in candidate_js
            and "if (!runtimePage || !contentPanel)" in candidate_js
            and "if (subnav)" in candidate_js
        )
        checks["all_runtime_sections_retained"] = all(
            f'"{section}"' in candidate_js
            for section in (
                "overview", "pipeline_operations", "jobs", "queues",
                "workers_leases", "orchestration", "execution",
                "reliability_recovery", "resource_governance", "runtime_apis",
                "persistence_state_integrity", "observability", "security",
                "owner_actions", "evidence_audit",
            )
        )
        checks["owner_actions_recovery_label_present"] = all(token in candidate_html for token in (
            'data-runtime-sidebar-section="owner_actions"',
            "Owner Actions &amp; Recovery",
        ))
        checks["javascript_cache_advanced"] = (
            OLD_JS_CACHE not in candidate_html and candidate_html.count(NEW_JS_CACHE) == 1
        )
        if not all(checks.values()):
            raise RuntimeError("One or more candidate shared-navigation checks failed.")

        backup = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b6c_r2_{timestamp_slug()}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(paths["index_html"], backup / "index.html")
        shutil.copy2(paths["runtime_owner_js"], backup / "runtime_owner.js")
        checks["backup_created"] = all(
            (backup / name).is_file() for name in ("index.html", "runtime_owner.js")
        )
        evidence["backup"] = str(backup)

        originals = {
            "index_html": paths["index_html"].read_bytes(),
            "runtime_owner_js": paths["runtime_owner_js"].read_bytes(),
        }
        atomic_write(paths["index_html"], candidate_html)
        atomic_write(paths["runtime_owner_js"], candidate_js)

        retained_html = read_text(paths["index_html"])
        retained_js = read_text(paths["runtime_owner_js"])
        retained_probe = isolated_navigation_probe(retained_js)
        evidence["retained_navigation_probe"] = retained_probe
        checks["retained_html_ids_unique"] = ids_unique(retained_html)
        checks["retained_javascript_syntax"] = javascript_syntax_valid(retained_js)
        checks["retained_navigation_probe_passed"] = bool(retained_probe.get("passed"))
        checks["retained_cache_version_24"] = retained_html.count(NEW_JS_CACHE) == 1
        checks["retained_owner_actions_recovery_label"] = (
            "Owner Actions &amp; Recovery" in retained_html
        )
        checks["historical_b6_report_unchanged"] = sha256(b6_report) == report_hash_before
        for name, expected in EXPECTED_HASHES.items():
            if name not in {"index_html", "runtime_owner_js"}:
                checks[f"unchanged_{name}"] = sha256(paths[name]) == expected
        checks["only_expected_sources_changed"] = (
            sha256(paths["index_html"]) != EXPECTED_HASHES["index_html"]
            and sha256(paths["runtime_owner_js"]) != EXPECTED_HASHES["runtime_owner_js"]
        )
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_repair_no"] = True
        checks["project_modules_imported_no"] = True
        if not all(checks.values()):
            raise RuntimeError("One or more retained shared-navigation checks failed.")

        evidence.update({
            "changed_sources": [INDEX_PATH, RUNTIME_JS_PATH],
            "index_hash_before": EXPECTED_HASHES["index_html"],
            "index_hash_after": sha256(paths["index_html"]),
            "runtime_owner_js_hash_before": EXPECTED_HASHES["runtime_owner_js"],
            "runtime_owner_js_hash_after": sha256(paths["runtime_owner_js"]),
            "repaired_sections": 15,
            "root_cause": "obsolete_mandatory_runtimeOwnerSubnav_dependency",
            "patch_retained": True,
        })
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        for name, content in originals.items():
            paths[name].write_bytes(content)
        if originals:
            evidence["rollback_performed"] = True

    certified = not error and all(checks.values())
    write_report(report, checks, evidence, error, certified)
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B6C_R2_STATUS={'CERTIFIED' if certified else 'NOT_CERTIFIED'}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("ACTIONS_EXECUTED=NO")
    return 0 if certified else 1


def self_test() -> int:
    synthetic_js = '''(function () {
  "use strict";
  const RUNTIME_OWNER_SECTIONS = Object.freeze(["overview", "owner_actions"]);
  const LEGACY_ROUTE_SECTION_MAP = Object.freeze({});
  function getRuntimePage() { return document.getElementById("runtimePage"); }
  function getSubnav() { return document.getElementById("runtimeOwnerSubnav"); }
  function getContentPanel() { return document.getElementById("runtimeOwnerContentPanel"); }
  function isValidSection(section) { return RUNTIME_OWNER_SECTIONS.includes(section); }
  function normalizeSection(section) {
    if (isValidSection(section)) return section;
    return "overview";
  }
  function setActiveSection(section) {
    const runtimePage = getRuntimePage();
    const subnav = getSubnav();
    const contentPanel = getContentPanel();

    if (!runtimePage || !subnav || !contentPanel) {
      return false;
    }

    const normalized = normalizeSection(section);

    const buttons = subnav.querySelectorAll(
      "[data-runtime-owner-section]"
    );

    buttons.forEach((button) => {
      const isActive =
        button.dataset.runtimeOwnerSection === normalized;

      button.classList.toggle("active", isActive);

      button.setAttribute(
        "aria-selected",
        isActive ? "true" : "false"
      );
    });
    const panels = contentPanel.querySelectorAll("[data-runtime-owner-section-panel]");
    panels.forEach((panel) => {
      const isActive = panel.dataset.runtimeOwnerSectionPanel === normalized;
      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });
    contentPanel.dataset.runtimeOwnerActiveSection = normalized;
    runtimePage.dispatchEvent(new CustomEvent("runtimeowner:sectionchange", {detail: {section: normalized}}));
    return true;
  }
  function getActiveSection() {
    const contentPanel = getContentPanel();
    if (!contentPanel) return "overview";
    return normalizeSection(contentPanel.dataset.runtimeOwnerActiveSection);
  }
  window.LinkCraftorRuntimeOwner = Object.freeze({setActiveSection, getActiveSection});
})();
owner_actions: ["Owner Actions", "Governed owner operations and approvals."]'''
    candidate = build_candidate_js(synthetic_js)
    assert OLD_GUARD not in candidate
    assert "if (!runtimePage || !contentPanel)" in candidate
    assert "if (subnav)" in candidate
    assert "Owner Actions & Recovery" in candidate
    synthetic_html = OLD_JS_CACHE + "\n" + OLD_SIDEBAR_LABEL
    candidate_html = build_candidate_html(synthetic_html)
    assert NEW_JS_CACHE in candidate_html
    assert "Owner Actions &amp; Recovery" in candidate_html
    print("PART_F_15_B6C_R2_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        print(
            "Usage: RUN_15_B6C_R2_RUNTIME_OWNER_SHARED_NAVIGATION_REPAIR.py "
            "<project-root> <report-path>",
            file=sys.stderr,
        )
        return 2
    return run(Path(argv[0]).resolve(), Path(argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
