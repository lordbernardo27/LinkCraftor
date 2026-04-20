# backend/server/scripts/check_imported_phase1_workspace_entry.py

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


WORKSPACE_KEYS = {"workspace_id", "workspaceId", "ws", "ws_id"}


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
    return ws.lower() in str(fp).lower()


def looks_like_imported_file(fp: Path) -> bool:
    s = str(fp).lower()
    n = fp.name.lower()
    return "imported" in s and n.endswith(".json")


def extract_workspace_fields(data: Any) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []

    if not isinstance(data, dict):
        return found

    for key in WORKSPACE_KEYS:
        value = data.get(key)
        if isinstance(value, str):
            found.append((key, value))

    meta = data.get("meta")
    if isinstance(meta, dict):
        for key in WORKSPACE_KEYS:
            value = meta.get(key)
            if isinstance(value, str):
                found.append((f"meta.{key}", value))

    return found


def has_workspace_assignment(data: Any, workspace_id: str) -> bool:
    for _, value in extract_workspace_fields(data):
        if value == workspace_id:
            return True
    return False


def find_imported_candidates(data_dir: Path, workspace_id: str) -> tuple[list[Path], list[Path]]:
    all_json = collect_json_files(data_dir)

    imported_candidates: list[Path] = []
    for fp in all_json:
        if looks_like_imported_file(fp) and path_mentions_workspace(fp, workspace_id):
            imported_candidates.append(fp)

    source_candidates: list[Path] = []
    output_candidates: list[Path] = []

    for fp in imported_candidates:
        try:
            data = load_json(fp)
        except Exception:
            continue

        if not has_workspace_assignment(data, workspace_id):
            continue

        name = fp.name.lower()
        path_text = str(fp).lower()

        if (
            "phrase_pool" in name
            or "phrase_index" in name
            or "phrase_pools" in path_text
            or ("phrases" in name and "imported" in name)
        ):
            output_candidates.append(fp)
        else:
            source_candidates.append(fp)

    return sorted(source_candidates), sorted(output_candidates)


def inspect_workspace_fields(fp: Path, workspace_id: str) -> tuple[bool, str]:
    try:
        data = load_json(fp)
    except Exception as e:
        return False, f"could not read JSON: {e}"

    fields = extract_workspace_fields(data)
    if not fields:
        return False, "no explicit workspace field found"

    detail = ", ".join(f"{k}={v!r}" for k, v in fields)
    ok = any(v == workspace_id for _, v in fields)
    return ok, detail


def check_foreign_workspace_leak(fp: Path, workspace_id: str) -> tuple[bool, str]:
    try:
        data = load_json(fp)
    except Exception as e:
        return False, f"could not read JSON: {e}"

    fields = extract_workspace_fields(data)
    if not fields:
        return False, "no explicit workspace field found for leak check"

    foreign = [(k, v) for k, v in fields if v != workspace_id]

    if foreign:
        detail = ", ".join(f"{k}={v!r}" for k, v in foreign)
        return False, f"foreign workspace field(s) found: {detail}"

    detail = ", ".join(f"{k}={v!r}" for k, v in fields)
    return True, f"workspace fields isolated correctly: {detail}"


def main() -> int:
    workspace_id = "ws_betterhealthcheck_com"

    base_dir = Path(__file__).resolve().parents[1]  # backend/server
    data_dir = base_dir / "data"

    print("===== IMPORTED PHRASE POOL — PHASE 1 WORKSPACE ENTRY CHECK =====\n")
    print(f"workspace_id: {workspace_id}")
    print(f"base_dir: {base_dir}\n")

    all_ok = True

    source_candidates, output_candidates = find_imported_candidates(data_dir, workspace_id)

    # 1.1.1
    check_111_ok = len(source_candidates) > 0
    if check_111_ok:
        details = []
        for fp in source_candidates:
            ok, detail = inspect_workspace_fields(fp, workspace_id)
            details.append(f"{fp.name} [{detail}]")
            check_111_ok = check_111_ok and ok
        detail_111 = "; ".join(details)
    else:
        detail_111 = "no imported source candidate found for workspace"
    print_result("1.1.1", "Confirm imported source is assigned to correct ws_* workspace ID", check_111_ok, detail_111)
    all_ok &= check_111_ok

    # 1.1.2
    normalized = normalize_workspace_id(workspace_id)
    check_112_ok = workspace_id == normalized and is_valid_workspace_id(workspace_id)
    detail_112 = f"normalized={normalized}"
    print_result("1.1.2", "Confirm workspace naming is normalized consistently", check_112_ok, detail_112)
    all_ok &= check_112_ok

    # 1.1.3
    bad_paths = [str(fp) for fp in collect_json_files(data_dir) if contains_bad_ws_duplication(str(fp))]
    bad_paths = sorted(set(bad_paths))
    check_113_ok = len(bad_paths) == 0
    detail_113 = "no bad ws_ws_* paths found" if check_113_ok else f"bad paths: {bad_paths}"
    print_result("1.1.3", "Confirm no ws_ws_* duplication or bad path naming exists", check_113_ok, detail_113)
    all_ok &= check_113_ok

    # 1.2.1
    leak_ok = True
    leak_details: list[str] = []

    if not source_candidates:
        leak_ok = False
        leak_details.append("no imported source candidate available for leak check")
    else:
        for fp in source_candidates:
            ok, detail = check_foreign_workspace_leak(fp, workspace_id)
            if not ok:
                leak_ok = False
            leak_details.append(f"{fp.name}: {detail}")

    detail_121 = "; ".join(leak_details) if leak_details else "no imported source candidate available for leak check"
    print_result("1.2.1", "Confirm imported source does not leak into another workspace", leak_ok, detail_121)
    all_ok &= leak_ok

    # 1.2.2
    scoped_issues: list[str] = []
    files_to_check = source_candidates + output_candidates

    if not files_to_check:
        scoped_issues.append("no imported workspace files discovered")

    for fp in files_to_check:
        if not path_mentions_workspace(fp, workspace_id):
            scoped_issues.append(f"unscoped:{fp}")

    check_122_ok = len(scoped_issues) == 0
    detail_122 = "all discovered imported files are workspace-scoped" if check_122_ok else "; ".join(scoped_issues)
    print_result("1.2.2", "Confirm imported phrase files are workspace-scoped", check_122_ok, detail_122)
    all_ok &= check_122_ok

    # 1.2.3
    rebuild_issues: list[str] = []

    if not output_candidates:
        rebuild_issues.append("no imported output candidate found for workspace")
    else:
        for fp in output_candidates:
            if not path_mentions_workspace(fp, workspace_id):
                rebuild_issues.append(f"output not workspace-scoped: {fp}")
                continue

            ok, detail = inspect_workspace_fields(fp, workspace_id)
            if not ok:
                rebuild_issues.append(f"{fp.name}: {detail}")

    check_123_ok = len(rebuild_issues) == 0
    detail_123 = "discovered imported outputs appear isolated to intended workspace" if check_123_ok else "; ".join(rebuild_issues)
    print_result("1.2.3", "Confirm rebuilds only affect intended workspace", check_123_ok, detail_123)
    all_ok &= check_123_ok

    print("\n===== DISCOVERED FILES =====")
    print(f"source_candidates_count: {len(source_candidates)}")
    for fp in source_candidates:
        print(f"  SOURCE  {fp}")

    print(f"output_candidates_count: {len(output_candidates)}")
    for fp in output_candidates:
        print(f"  OUTPUT  {fp}")

    print("\n===== SUMMARY =====")
    print(f"overall: {'PASS' if all_ok else 'FAIL'}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())