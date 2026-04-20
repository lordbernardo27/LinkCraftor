# backend/server/scripts/check_imported_phase1_workspace_entry.py

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def load_json(fp: Path) -> Any:
    return json.loads(fp.read_text(encoding="utf-8"))


def normalize_workspace_id(raw: str) -> str:
    s = (raw or "").strip().lower()
    s = s.replace("-", "_").replace(".", "_").replace(" ", "_")
    s = re.sub(r"_+", "_", s)
    if not s.startswith("ws_"):
        s = f"ws_{s}"
    return s


def is_valid_workspace_id(ws: str) -> bool:
    return bool(re.fullmatch(r"ws_[a-z0-9_]+", ws or ""))


def contains_bad_ws_duplication(text: str) -> bool:
    return "ws_ws_" in (text or "").lower()


def print_result(code: str, label: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"{code} {label} — {status}{suffix}")


def collect_json_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*.json") if p.is_file()]


def path_mentions_workspace(fp: Path, ws: str) -> bool:
    text = str(fp).lower()
    return ws.lower() in text


def any_other_workspace_mentions(text: str, target_ws: str) -> list[str]:
    hits = sorted(set(re.findall(r"ws_[a-z0-9_]+", text.lower())))
    return [x for x in hits if x != target_ws.lower()]


def main() -> int:
    # ---- CONFIG ----
    workspace_id = "ws_betterhealthcheck_com"

    base_dir = Path(__file__).resolve().parents[1]  # backend/server
    data_dir = base_dir / "data"

    # Adjust these if your imported source/output paths differ
    imported_source_dir = data_dir / "imported"
    imported_pool_dir = data_dir / "phrase_pools" / "imported"

    imported_source_fp = imported_source_dir / f"imported_sources_{workspace_id}.json"
    imported_phrase_pool_fp = imported_pool_dir / f"imported_phrase_pool_{workspace_id}.json"
    imported_phrase_index_fp = data_dir / f"imported_phrase_index_{workspace_id}.json"

    # Optional rebuild-related files to inspect if they exist
    active_phrase_set_fp = data_dir / f"active_phrase_set_{workspace_id}.json"
    active_target_set_fp = data_dir / "target_pools" / f"active_target_set_{workspace_id}.json"

    print("===== IMPORTED PHRASE POOL — PHASE 1 WORKSPACE ENTRY CHECK =====\n")
    print(f"workspace_id: {workspace_id}")
    print(f"base_dir: {base_dir}")
    print()

    all_ok = True

    # ---------------------------------------------------------
    # 1.1.1 Confirm imported source is assigned to correct ws_* workspace ID
    # ---------------------------------------------------------
    check_111_ok = False
    check_111_detail = ""

    if not imported_source_fp.exists():
        check_111_detail = f"missing source file: {imported_source_fp}"
    else:
        try:
            source_data = load_json(imported_source_fp)
            file_ws = source_data.get("workspace_id") if isinstance(source_data, dict) else None
            if file_ws == workspace_id:
                check_111_ok = True
                check_111_detail = f"workspace_id={file_ws}"
            else:
                check_111_detail = f"stored workspace_id={file_ws!r}, expected={workspace_id!r}"
        except Exception as e:
            check_111_detail = f"could not read source JSON: {e}"

    print_result("1.1.1", "Confirm imported source is assigned to correct ws_* workspace ID", check_111_ok, check_111_detail)
    all_ok &= check_111_ok

    # ---------------------------------------------------------
    # 1.1.2 Confirm workspace naming is normalized consistently
    # ---------------------------------------------------------
    normalized = normalize_workspace_id(workspace_id)
    check_112_ok = workspace_id == normalized and is_valid_workspace_id(workspace_id)
    detail_112 = f"normalized={normalized}"
    print_result("1.1.2", "Confirm workspace naming is normalized consistently", check_112_ok, detail_112)
    all_ok &= check_112_ok

    # ---------------------------------------------------------
    # 1.1.3 Confirm no ws_ws_* duplication or bad path naming exists
    # ---------------------------------------------------------
    candidate_paths = [
        imported_source_fp,
        imported_phrase_pool_fp,
        imported_phrase_index_fp,
        active_phrase_set_fp,
        active_target_set_fp,
    ]

    bad_paths: list[str] = []
    for fp in candidate_paths:
        if contains_bad_ws_duplication(str(fp)):
            bad_paths.append(str(fp))

    # also inspect all json files under data for ws_ws_ in path
    for fp in collect_json_files(data_dir):
        if contains_bad_ws_duplication(str(fp)):
            bad_paths.append(str(fp))

    bad_paths = sorted(set(bad_paths))
    check_113_ok = len(bad_paths) == 0
    detail_113 = "no bad ws_ws_* paths found" if check_113_ok else f"bad paths: {bad_paths}"
    print_result("1.1.3", "Confirm no ws_ws_* duplication or bad path naming exists", check_113_ok, detail_113)
    all_ok &= check_113_ok

    # ---------------------------------------------------------
    # 1.2.1 Confirm imported source does not leak into another workspace
    # ---------------------------------------------------------
    leak_hits: list[str] = []

    if imported_source_fp.exists():
        try:
            text = imported_source_fp.read_text(encoding="utf-8", errors="replace")
            other_ws = any_other_workspace_mentions(text, workspace_id)
            if other_ws:
                leak_hits.extend(other_ws)
        except Exception as e:
            leak_hits.append(f"read_error:{e}")

    check_121_ok = len(leak_hits) == 0
    detail_121 = "no foreign workspace ids found in imported source" if check_121_ok else f"foreign workspace ids found: {sorted(set(leak_hits))}"
    print_result("1.2.1", "Confirm imported source does not leak into another workspace", check_121_ok, detail_121)
    all_ok &= check_121_ok

    # ---------------------------------------------------------
    # 1.2.2 Confirm imported phrase files are workspace-scoped
    # ---------------------------------------------------------
    required_workspace_scoped = [
        imported_source_fp,
        imported_phrase_pool_fp,
        imported_phrase_index_fp,
    ]

    missing_or_unscoped: list[str] = []
    for fp in required_workspace_scoped:
        if not fp.exists():
            missing_or_unscoped.append(f"missing:{fp}")
            continue
        if not path_mentions_workspace(fp, workspace_id):
            missing_or_unscoped.append(f"unscoped:{fp}")

    check_122_ok = len(missing_or_unscoped) == 0
    detail_122 = "all required imported files are workspace-scoped" if check_122_ok else "; ".join(missing_or_unscoped)
    print_result("1.2.2", "Confirm imported phrase files are workspace-scoped", check_122_ok, detail_122)
    all_ok &= check_122_ok

    # ---------------------------------------------------------
    # 1.2.3 Confirm rebuilds only affect intended workspace
    # ---------------------------------------------------------
    # Heuristic check:
    # - imported output files for target workspace exist
    # - no recently named imported output for another workspace is mixed into these filenames
    # - output JSON metadata, if present, points to same workspace
    rebuild_issues: list[str] = []

    rebuild_outputs = [
        imported_phrase_pool_fp,
        imported_phrase_index_fp,
    ]

    for fp in rebuild_outputs:
        if not fp.exists():
            rebuild_issues.append(f"missing rebuild output: {fp}")
            continue

        if not path_mentions_workspace(fp, workspace_id):
            rebuild_issues.append(f"output not workspace-scoped: {fp}")

        try:
            data = load_json(fp)
            if isinstance(data, dict):
                stored_ws = data.get("workspace_id")
                if stored_ws is not None and stored_ws != workspace_id:
                    rebuild_issues.append(
                        f"{fp.name} workspace_id={stored_ws!r} expected={workspace_id!r}"
                    )

                # inspect common metadata containers too
                meta = data.get("meta")
                if isinstance(meta, dict):
                    meta_ws = meta.get("workspace_id")
                    if meta_ws is not None and meta_ws != workspace_id:
                        rebuild_issues.append(
                            f"{fp.name} meta.workspace_id={meta_ws!r} expected={workspace_id!r}"
                        )
        except Exception as e:
            rebuild_issues.append(f"could not inspect {fp.name}: {e}")

    # Also scan imported pool directory for conflicting output files from other workspaces
    if imported_pool_dir.exists():
        conflict_files = []
        for fp in imported_pool_dir.glob("imported_phrase_pool_*.json"):
            m = re.search(r"imported_phrase_pool_(ws_[a-z0-9_]+)\.json$", fp.name.lower())
            if m:
                seen_ws = m.group(1)
                if seen_ws != workspace_id.lower():
                    conflict_files.append(fp.name)
        # This is informational; not automatically failure unless user wants strict single-workspace dir.
        # Since your rule says rebuilds should only affect intended workspace, flag if suspicious files are mixed.
        if conflict_files:
            rebuild_issues.append(f"other workspace pool files present in imported pool dir: {conflict_files}")

    check_123_ok = len(rebuild_issues) == 0
    detail_123 = "rebuild outputs appear isolated to intended workspace" if check_123_ok else "; ".join(rebuild_issues)
    print_result("1.2.3", "Confirm rebuilds only affect intended workspace", check_123_ok, detail_123)
    all_ok &= check_123_ok

    print("\n===== SUMMARY =====")
    print(f"overall: {'PASS' if all_ok else 'FAIL'}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())