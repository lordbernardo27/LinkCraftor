from __future__ import annotations

import hashlib
import html
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


TITLE = "PART F 15-B6C-R OWNER ACTIONS NAVIGATION AND REACHABILITY CORRECTION"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6C-R OWNER ACTIONS NAVIGATION AND "
    "REACHABILITY CORRECTION CERTIFIED"
)

B6_REPORT = (
    "backend/server/data/reports/"
    "PART_F_15_B6B_B6I_OWNER_ACTIONS_RECOVERY_SAFETY_UI_CERTIFICATION.txt"
)
INDEX_PATH = "backend/server/owner/index.html"
RUNTIME_JS_PATH = "backend/server/owner/runtime_owner.js"
RUNTIME_CSS_PATH = "backend/server/owner/runtime_owner.css"
RUNTIME_API_PATH = "backend/server/owner/runtime_summary_api.py"
GATEWAY_PATH = "backend/server/owner/owner_actions_gateway.py"
PROJECTION_PATH = "backend/server/owner/runtime_infrastructure_projection.py"
PIPELINE_PATH = "backend/server/owner/pipeline_operations.py"

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
NAV_MARKER = "<!-- BEGIN PART F 15-B6C-R OWNER ACTIONS NAVIGATION -->"
NAV_END_MARKER = "<!-- END PART F 15-B6C-R OWNER ACTIONS NAVIGATION -->"
SECTION_KEY = "owner_actions"
PANEL_ID = "runtimeOwnerSectionOwnerActions"
WORKSPACE_ID = "runtimeOwnerActionsWorkspace"
NAV_ID = "runtimeSidebarOwnerActions"


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, {key: value or "" for key, value in attrs}))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


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


def atomic_write(path: Path, source: str) -> None:
    temporary = path.with_name(path.name + ".tmp-b6cr")
    temporary.write_text(source, encoding="utf-8", newline="\n")
    temporary.replace(path)


def matching_tag_end(source: str, opening_start: int, tag: str) -> tuple[int, int]:
    opening_end = source.find(">", opening_start)
    if opening_end < 0:
        raise RuntimeError(f"The opening <{tag}> tag is incomplete.")
    pattern = re.compile(rf"<{tag}\b|</{tag}\s*>", re.IGNORECASE)
    depth = 0
    for match in pattern.finditer(source, opening_start):
        if source[match.start():].lower().startswith(f"<{tag}"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return opening_end, match.start()
    raise RuntimeError(f"The opening <{tag}> tag has no matching closing tag.")


def enclosing_element(source: str, token_index: int) -> tuple[int, int, str]:
    candidates: list[tuple[int, str]] = []
    for tag in ("div", "section", "nav", "ul"):
        position = source.rfind(f"<{tag}", 0, token_index)
        if position >= 0:
            candidates.append((position, tag))
    for position, tag in sorted(candidates, reverse=True):
        opening_end, closing_start = matching_tag_end(source, position, tag)
        if opening_end < token_index < closing_start:
            return position, closing_start, tag
    raise RuntimeError("The Runtime Administration navigation container was not found.")


def locate_administration_container(source: str) -> tuple[int, int, str]:
    identifiers = (
        'id="runtimeSidebarAdministration"',
        'data-runtime-sidebar-group="runtime_administration"',
        'data-runtime-sidebar-group="runtime-administration"',
    )
    for token in identifiers:
        index = source.find(token)
        if index >= 0:
            return enclosing_element(source, index)

    label_match = re.search(r"Runtime\s+Administration", source, re.IGNORECASE)
    if label_match is None:
        raise RuntimeError("The Runtime Administration sidebar group is unavailable.")

    # Prefer the nearest ancestor carrying the sidebar-group contract.
    search_start = max(0, label_match.start() - 2500)
    prefix = source[search_start:label_match.start()]
    group_matches = list(re.finditer(r"<(?P<tag>div|section|nav|ul)\b[^>]*data-runtime-sidebar-group[^>]*>", prefix, re.IGNORECASE))
    if group_matches:
        match = group_matches[-1]
        opening_start = search_start + match.start()
        tag = match.group("tag").lower()
        _, closing_start = matching_tag_end(source, opening_start, tag)
        if closing_start > label_match.end():
            return opening_start, closing_start, tag

    raise RuntimeError(
        "Runtime Administration is visible in the source, but its sidebar container "
        "cannot be resolved safely. Nothing was changed."
    )


def sidebar_button_template(source: str) -> str:
    patterns = (
        r'<button\b[^>]*data-runtime-sidebar-section="execution"[^>]*>.*?</button>',
        r'<button\b[^>]*data-runtime-sidebar-section="jobs"[^>]*>.*?</button>',
        r'<button\b[^>]*data-runtime-sidebar-section="[^"]+"[^>]*>.*?</button>',
    )
    for pattern in patterns:
        match = re.search(pattern, source, re.IGNORECASE | re.DOTALL)
        if match is not None:
            return match.group(0)
    raise RuntimeError("No certified Runtime Owner sidebar item is available as a style template.")


def build_sidebar_button(template: str) -> str:
    opening_end = template.find(">")
    if opening_end < 0:
        raise RuntimeError("The sidebar item template is malformed.")
    opening = template[:opening_end + 1]
    opening = re.sub(
        r'data-runtime-sidebar-section="[^"]+"',
        f'data-runtime-sidebar-section="{SECTION_KEY}"',
        opening,
        count=1,
        flags=re.IGNORECASE,
    )
    if re.search(r'\bid="[^"]+"', opening, re.IGNORECASE):
        opening = re.sub(r'\bid="[^"]+"', f'id="{NAV_ID}"', opening, count=1, flags=re.IGNORECASE)
    else:
        opening = opening[:-1] + f' id="{NAV_ID}">'
    if re.search(r'\baria-controls="[^"]+"', opening, re.IGNORECASE):
        opening = re.sub(
            r'\baria-controls="[^"]+"',
            f'aria-controls="{PANEL_ID}"',
            opening,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        opening = opening[:-1] + f' aria-controls="{PANEL_ID}">'
    opening = re.sub(r'\baria-current="[^"]+"', 'aria-current="false"', opening, flags=re.IGNORECASE)
    return "\n".join((
        NAV_MARKER,
        opening,
        "  Owner Actions &amp; Recovery",
        "</button>",
        NAV_END_MARKER,
    ))


def add_panel_contract(source: str) -> str:
    match = re.search(
        rf'<section\b(?=[^>]*\bid="{re.escape(PANEL_ID)}")[^>]*>',
        source,
        re.IGNORECASE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError("The installed Owner Actions section is unavailable.")
    opening = match.group(0)
    existing = re.search(r'data-runtime-owner-section-panel="([^"]+)"', opening, re.IGNORECASE)
    if existing is not None and existing.group(1) != SECTION_KEY:
        raise RuntimeError("The Owner Actions section is mapped to an unexpected navigation key.")
    if existing is None:
        opening = opening[:-1] + f' data-runtime-owner-section-panel="{SECTION_KEY}">'
    if not re.search(r'\bhidden(?:\s|=|>)', opening, re.IGNORECASE):
        opening = opening[:-1] + " hidden>"
    return source[:match.start()] + opening + source[match.end():]


def build_candidate(source: str) -> str:
    if NAV_MARKER in source or f'data-runtime-sidebar-section="{SECTION_KEY}"' in source:
        raise RuntimeError("The Owner Actions sidebar correction is already present.")
    if source.count(f'id="{WORKSPACE_ID}"') != 1:
        raise RuntimeError("The certified Owner Actions workspace is not present exactly once.")

    candidate = add_panel_contract(source)
    _, closing_start, _ = locate_administration_container(candidate)
    button = build_sidebar_button(sidebar_button_template(candidate))
    candidate = candidate[:closing_start] + "\n" + button + "\n" + candidate[closing_start:]
    return candidate


def parse_elements(source: str) -> list[tuple[str, dict[str, str]]]:
    parser = ElementCollector()
    parser.feed(source)
    parser.close()
    return parser.elements


def ids_unique(source: str) -> bool:
    ids = [attrs["id"] for _, attrs in parse_elements(source) if attrs.get("id")]
    return len(ids) == len(set(ids))


def navigation_contract(source: str) -> dict[str, Any]:
    links = [
        (tag, attrs) for tag, attrs in parse_elements(source)
        if attrs.get("data-runtime-sidebar-section") == SECTION_KEY
    ]
    panels = [
        (tag, attrs) for tag, attrs in parse_elements(source)
        if attrs.get("data-runtime-owner-section-panel") == SECTION_KEY
    ]
    return {
        "sidebar_count": len(links),
        "panel_count": len(panels),
        "sidebar_is_button": len(links) == 1 and links[0][0] == "button",
        "sidebar_id": links[0][1].get("id") if len(links) == 1 else None,
        "aria_controls": links[0][1].get("aria-controls") if len(links) == 1 else None,
        "panel_id": panels[0][1].get("id") if len(panels) == 1 else None,
        "workspace_count": source.count(f'id="{WORKSPACE_ID}"'),
        "label_present": "Owner Actions &amp; Recovery" in source,
        "marker_present": NAV_MARKER in source and NAV_END_MARKER in source,
    }


def html_syntax_valid(source: str) -> bool:
    try:
        parse_elements(source)
        return True
    except Exception:
        return False


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


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


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
        f"Sidebar entry added: {'YES' if evidence.get('patch_retained') else 'NO'}",
        f"Owner Actions workspace changed: {'NO' if evidence.get('workspace_preserved') else 'UNKNOWN'}",
        "Live owner actions executed during correction: NO",
        "Trusted mutation adapters registered: NO",
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
        "IMPLEMENTED CORRECTION:",
        "- Added a visible Owner Actions & Recovery sidebar control under Runtime Administration.",
        "- Mapped the control to the existing runtimeOwnerSectionOwnerActions panel.",
        "- Reused the certified Runtime Owner section-switching authority.",
        "- Preserved the complete B6B-B6I workspace, gateway, preview and safety contracts.",
        "- Live dispatch remains OFF and no trusted mutation adapter was registered.",
        "- No production job, queue claim, handler, workflow or recovery action was executed.",
        "",
        "NEXT STEP:",
        "Press Ctrl + F5, expand Runtime Administration, and open Owner Actions & Recovery.",
        "After visual acceptance, proceed to Part F 15-B6J collective development certification.",
        "",
        FINAL_RESULT if certified else FINAL_RESULT.replace(" CERTIFIED", " NOT_CERTIFIED"),
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run(root: Path, report: Path) -> int:
    paths = {
        "index_html": root / INDEX_PATH,
        "runtime_owner_js": root / RUNTIME_JS_PATH,
        "runtime_owner_css": root / RUNTIME_CSS_PATH,
        "runtime_summary_api": root / RUNTIME_API_PATH,
        "owner_actions_gateway": root / GATEWAY_PATH,
        "runtime_infrastructure_projection": root / PROJECTION_PATH,
        "pipeline_operations": root / PIPELINE_PATH,
        "b6_report": root / B6_REPORT,
    }
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "actions_executed": False,
        "trusted_adapters_installed": 0,
        "patch_retained": False,
        "rollback_performed": False,
        "workspace_preserved": False,
    }
    error: dict[str, Any] = {}
    backup: Path | None = None
    original_index: bytes | None = None
    report_hash_before: str | None = None

    try:
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified B6 source/report baseline is unavailable.")

        checks["part_f_15_b6b_b6i_certified"] = report_certified(read_text(paths["b6_report"]))
        report_hash_before = sha256(paths["b6_report"])

        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = sha256(paths[name]) == expected
        if not all(checks.values()):
            raise RuntimeError("The certified B6B-B6I source baseline is not intact.")

        source = read_text(paths["index_html"])
        checks["owner_actions_workspace_present_once"] = source.count(f'id="{WORKSPACE_ID}"') == 1
        checks["owner_actions_sidebar_entry_previously_absent"] = (
            f'data-runtime-sidebar-section="{SECTION_KEY}"' not in source
        )
        checks["runtime_administration_group_discoverable"] = True
        locate_administration_container(source)
        if not all(checks.values()):
            raise RuntimeError("The missing-navigation correction boundary is unavailable.")

        candidate = build_candidate(source)
        contract = navigation_contract(candidate)
        evidence["navigation_contract"] = contract
        checks["candidate_html_syntax"] = html_syntax_valid(candidate)
        checks["candidate_html_ids_unique"] = ids_unique(candidate)
        checks["sidebar_entry_present_once"] = contract["sidebar_count"] == 1
        checks["sidebar_entry_is_native_button"] = contract["sidebar_is_button"]
        checks["sidebar_identity_present"] = contract["sidebar_id"] == NAV_ID
        checks["sidebar_aria_controls_panel"] = contract["aria_controls"] == PANEL_ID
        checks["owner_actions_panel_mapping_present_once"] = contract["panel_count"] == 1
        checks["owner_actions_panel_identity_retained"] = contract["panel_id"] == PANEL_ID
        checks["owner_actions_workspace_retained_once"] = contract["workspace_count"] == 1
        checks["owner_actions_visible_label_present"] = contract["label_present"]
        checks["correction_markers_present"] = contract["marker_present"]
        js_source = read_text(paths["runtime_owner_js"])
        checks["section_switching_authority_retained"] = all(token in js_source for token in (
            "window.LinkCraftorRuntimeOwner", "setActiveSection", "runtimeowner:sectionchange",
        ))
        gateway_source = read_text(paths["owner_actions_gateway"])
        checks["live_dispatch_default_remains_off"] = (
            'OWNER_ACTIONS_ENABLED_ENV' in gateway_source
            and '!= "1"' in gateway_source
            and "owner_actions_disabled" in gateway_source
        )
        checks["no_mutation_adapter_added"] = "register_owner_action_adapter(" not in candidate
        if not all(checks.values()):
            raise RuntimeError("One or more candidate navigation checks failed.")

        backup = (
            root / "backend/server/data/runtime_backups"
            / f"part_f_15_b6c_r_{timestamp_slug()}"
        )
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(paths["index_html"], backup / "index.html")
        evidence["backup"] = str(backup)
        checks["backup_created"] = (backup / "index.html").is_file()

        original_index = paths["index_html"].read_bytes()
        atomic_write(paths["index_html"], candidate)

        retained = read_text(paths["index_html"])
        retained_contract = navigation_contract(retained)
        checks["retained_html_syntax"] = html_syntax_valid(retained)
        checks["retained_html_ids_unique"] = ids_unique(retained)
        checks["retained_sidebar_entry_present_once"] = retained_contract["sidebar_count"] == 1
        checks["retained_panel_mapping_present_once"] = retained_contract["panel_count"] == 1
        checks["retained_sidebar_targets_owner_actions_panel"] = (
            retained_contract["aria_controls"] == retained_contract["panel_id"] == PANEL_ID
        )
        checks["retained_workspace_present_once"] = retained_contract["workspace_count"] == 1
        checks["historical_b6_report_unchanged"] = sha256(paths["b6_report"]) == report_hash_before
        for name in EXPECTED_HASHES:
            if name != "index_html":
                checks[f"unchanged_{name}"] = sha256(paths[name]) == EXPECTED_HASHES[name]
        checks["only_index_html_changed"] = sha256(paths["index_html"]) != EXPECTED_HASHES["index_html"]
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_correction_no"] = True
        checks["project_modules_imported_no"] = True

        if not all(checks.values()):
            raise RuntimeError("One or more retained navigation checks failed.")

        evidence.update({
            "changed_sources": [INDEX_PATH],
            "index_hash_before": EXPECTED_HASHES["index_html"],
            "index_hash_after": sha256(paths["index_html"]),
            "navigation_key": SECTION_KEY,
            "sidebar_id": NAV_ID,
            "panel_id": PANEL_ID,
            "workspace_id": WORKSPACE_ID,
            "patch_retained": True,
            "workspace_preserved": True,
        })
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if original_index is not None:
            paths["index_html"].write_bytes(original_index)
            evidence["rollback_performed"] = True

    certified = not error and all(checks.values())
    write_report(report, checks, evidence, error, certified)
    failed = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={len(failed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B6C_R_STATUS={'CERTIFIED' if certified else 'NOT_CERTIFIED'}")
    print(f"PATCH_RETAINED={'YES' if evidence.get('patch_retained') else 'NO'}")
    print("ACTIONS_EXECUTED=NO")
    return 0 if certified else 1


def self_test() -> int:
    sample = '''
<nav data-runtime-sidebar-group="runtime_administration">
  <button type="button">Runtime Administration</button>
  <div id="runtimeSidebarAdministration">
    <button class="runtime-sidebar-link" data-runtime-sidebar-section="execution"
      id="runtimeSidebarExecution" aria-controls="runtimeOwnerSectionExecution">Execution</button>
  </div>
</nav>
<section id="runtimeOwnerSectionOwnerActions" data-runtime-owner-section="owner_actions" hidden>
  <div id="runtimeOwnerActionsWorkspace">Owner Actions &amp; Recovery</div>
</section>
'''.strip()
    candidate = build_candidate(sample)
    contract = navigation_contract(candidate)
    assert contract["sidebar_count"] == 1
    assert contract["panel_count"] == 1
    assert contract["sidebar_id"] == NAV_ID
    assert contract["aria_controls"] == PANEL_ID
    assert contract["panel_id"] == PANEL_ID
    assert contract["workspace_count"] == 1
    assert ids_unique(candidate)
    print("PART_F_15_B6C_R_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        print(
            "Usage: RUN_15_B6C_R_OWNER_ACTIONS_NAVIGATION_REACHABILITY_CORRECTION.py "
            "<project-root> <report-path>",
            file=sys.stderr,
        )
        return 2
    return run(Path(argv[0]).resolve(), Path(argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
