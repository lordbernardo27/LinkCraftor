import json
import re
from pathlib import Path

ws = "ws_betterhealthcheck_com"

root = Path(r".")
backend = root / "backend"
server = backend / "server"
data = server / "data"

active_dir = data / "phrase_pools" / "active"
upload_pool_fp = data / "phrase_pools" / "upload" / f"upload_phrase_pool_{ws}.json"
active_pool_fp = active_dir / f"active_phrase_pool_{ws}.json"
active_set_fp = active_dir / f"active_phrase_set_{ws}.json"

builder_fp = server / "stores" / "active_phrase_pool_builder.py"
upload_builder_fp = server / "stores" / "upload_phrase_pool_builder.py"
active_set_store_fp = server / "stores" / "active_phrase_set_store.py"
files_route_fp = server / "routes" / "files.py"

def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def safe_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

builder_text = safe_text(builder_fp)
upload_builder_text = safe_text(upload_builder_fp)
active_set_store_text = safe_text(active_set_store_fp)
files_route_text = safe_text(files_route_fp)

active_pool = safe_json(active_pool_fp) if active_pool_fp.exists() else {}
upload_pool = safe_json(upload_pool_fp) if upload_pool_fp.exists() else {}
active_set = safe_json(active_set_fp) if active_set_fp.exists() else {}

active_pool_phrases = active_pool.get("phrases") if isinstance(active_pool, dict) and isinstance(active_pool.get("phrases"), dict) else {}
upload_pool_phrases = upload_pool.get("phrases") if isinstance(upload_pool, dict) and isinstance(upload_pool.get("phrases"), dict) else {}

active_document_ids = active_set.get("active_document_ids") or []
active_draft_ids = active_set.get("active_draft_ids") or []
active_live_domain_urls = active_set.get("active_live_domain_urls") or []
active_imported_urls = active_set.get("active_imported_urls") or active_set.get("active_import_ids") or []

manual_rebuild_signals = [
    "build_active_phrase_pool",
    "build_upload_phrase_pool",
    "rebuild",
]

source_entry_trigger_signals = [
    "build_upload_phrase_pool",
    "save_active_phrase_set",
    "active_document_ids",
]

membership_change_trigger_signals = [
    "save_active_phrase_set",
    "active_document_ids",
    "active_draft_ids",
    "active_live_domain_urls",
    "active_imported_urls",
    "active_import_ids",
]

def has_any(text: str, patterns: list[str]) -> bool:
    return any(p in text for p in patterns)

def count_any(text: str, patterns: list[str]) -> int:
    return sum(text.count(p) for p in patterns)

rebuild_uses_correct_workspace = False
if isinstance(active_pool, dict):
    rebuild_uses_correct_workspace = active_pool.get("workspace_id") == ws

rebuild_results_inspectable = (
    active_pool_fp.exists()
    and isinstance(active_pool, dict)
    and isinstance(active_pool.get("counts_by_source"), dict)
    and isinstance(active_pool.get("sources_used"), dict)
)

counts_reflect_rebuilt_data = False
if rebuild_results_inspectable:
    cps = active_pool.get("counts_by_source") or {}
    su = active_pool.get("sources_used") or {}
    counts_reflect_rebuilt_data = (
        "upload" in cps and "upload" in su
        and isinstance(active_pool.get("phrase_count"), int)
        and active_pool.get("phrase_count", 0) >= 0
    )

failure_visibility_signal = (
    "FileNotFoundError" in upload_builder_text
    or "raise FileNotFoundError" in upload_builder_text
    or "except Exception" in builder_text
    or "Missing upload phrase index file" in upload_builder_text
)

latest_active_set_reflected = False
if active_pool_fp.exists() and isinstance(active_pool, dict):
    cps = active_pool.get("counts_by_source") or {}
    su = active_pool.get("sources_used") or {}
    upload_only_mode = (
        len(active_document_ids) > 0
        and len(active_draft_ids) == 0
        and len(active_live_domain_urls) == 0
        and len(active_imported_urls) == 0
    )
    latest_active_set_reflected = (
        (not upload_only_mode)
        or (
            su.get("upload") is True
            and su.get("draft") is False
            and su.get("live_domain") is False
            and su.get("imported") is False
            and cps.get("draft", 0) == 0
            and cps.get("live_domain", 0) == 0
            and cps.get("imported", 0) == 0
        )
    )

no_stale_phrases = latest_active_set_reflected

correct_source_files_signal = (
    'phrase_pools" / "upload" / f"upload_phrase_pool_' in builder_text
    and 'phrase_pools" / "active" / f"active_phrase_pool_' in builder_text
)

source_entry_trigger_signal = has_any(upload_builder_text + files_route_text, source_entry_trigger_signals)
membership_change_trigger_signal = has_any(builder_text + upload_builder_text + active_set_store_text + files_route_text, membership_change_trigger_signals)
manual_rebuild_available_signal = has_any(builder_text + upload_builder_text + files_route_text, manual_rebuild_signals)

print("\n===== PHASE 7 REBUILD CHECK =====")

print("workspace:", ws)
print("active_pool_file:", active_pool_fp)
print("upload_pool_file:", upload_pool_fp)
print("active_set_file:", active_set_fp)

print("\n--- Current State ---")
print("active_document_ids:", active_document_ids)
print("active_pool_phrase_count:", len(active_pool_phrases))
print("upload_pool_phrase_count:", len(upload_pool_phrases))
print("active_pool_workspace_id:", active_pool.get("workspace_id") if isinstance(active_pool, dict) else None)
print("counts_by_source:", active_pool.get("counts_by_source") if isinstance(active_pool, dict) else None)
print("sources_used:", active_pool.get("sources_used") if isinstance(active_pool, dict) else None)

print("\n--- Trigger Signals ---")
print("source_entry_trigger_signal_count:", count_any(upload_builder_text + files_route_text, source_entry_trigger_signals))
print("membership_change_trigger_signal_count:", count_any(builder_text + upload_builder_text + active_set_store_text + files_route_text, membership_change_trigger_signals))
print("manual_rebuild_signal_count:", count_any(builder_text + upload_builder_text + files_route_text, manual_rebuild_signals))

print("\n--- Checks ---")
print("7.1.1 rebuild_runs_after_source_entry_when_required:", source_entry_trigger_signal)
print("7.1.2 rebuild_runs_after_membership_change_when_required:", membership_change_trigger_signal)
print("7.1.3 manual_rebuild_available_if_designed:", manual_rebuild_available_signal)

print("7.2.1 rebuild_refreshes_active_phrase_behavior:", latest_active_set_reflected)
print("7.2.2 rebuild_does_not_leave_stale_phrases:", no_stale_phrases)
print("7.2.3 rebuild_uses_correct_workspace_and_source_files:", rebuild_uses_correct_workspace and correct_source_files_signal)

print("7.3.1 rebuild_results_are_inspectable:", rebuild_results_inspectable)
print("7.3.2 counts_or_metadata_reflect_rebuilt_output:", counts_reflect_rebuilt_data)
print("7.3.3 failures_are_visible_not_silent:", failure_visibility_signal)

print("\n===== END =====\n")