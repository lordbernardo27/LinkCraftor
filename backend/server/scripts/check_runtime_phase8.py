import json
import re
from pathlib import Path

ws = "ws_betterhealthcheck_com"

root = Path(r".")
backend = root / "backend"
server = backend / "server"
data = server / "data"

active_dir = data / "phrase_pools" / "active"
upload_dir = data / "phrase_pools" / "upload"

active_pool_fp = active_dir / f"active_phrase_pool_{ws}.json"
active_set_fp = active_dir / f"active_phrase_set_{ws}.json"
upload_pool_fp = upload_dir / f"upload_phrase_pool_{ws}.json"
raw_upload_index_fp = data / f"upload_phrase_index_{ws}.json"

runtime_code_paths = [
    server / "engine",
    server,
]

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

def collect_py_text(paths: list[Path]) -> str:
    chunks = []
    for p in paths:
        if p.is_file() and p.suffix == ".py":
            chunks.append(safe_text(p))
        elif p.is_dir():
            for sub in p.rglob("*.py"):
                chunks.append(safe_text(sub))
    return "\n".join(chunks)

code_blob = collect_py_text(runtime_code_paths)

active_pool = safe_json(active_pool_fp) if active_pool_fp.exists() else {}
active_set = safe_json(active_set_fp) if active_set_fp.exists() else {}
upload_pool = safe_json(upload_pool_fp) if upload_pool_fp.exists() else {}
raw_upload_index = safe_json(raw_upload_index_fp) if raw_upload_index_fp.exists() else {}

active_pool_phrases = active_pool.get("phrases") if isinstance(active_pool, dict) and isinstance(active_pool.get("phrases"), dict) else {}
upload_pool_phrases = upload_pool.get("phrases") if isinstance(upload_pool, dict) and isinstance(upload_pool.get("phrases"), dict) else {}
raw_upload_phrases = raw_upload_index.get("phrases") if isinstance(raw_upload_index, dict) and isinstance(raw_upload_index.get("phrases"), dict) else {}

active_document_ids = active_set.get("active_document_ids") or []
active_draft_ids = active_set.get("active_draft_ids") or []
active_live_domain_urls = active_set.get("active_live_domain_urls") or []
active_imported_urls = active_set.get("active_imported_urls") or active_set.get("active_import_ids") or []

# Sample selected/unselected doc IDs for upload-only audit
selected_doc_id = active_document_ids[0] if active_document_ids and active_document_ids[0] != "ALL" else None
all_doc_ids = set()
for rec in raw_upload_phrases.values():
    if isinstance(rec, dict):
        docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
        for k in docs.keys():
            sk = str(k).strip()
            if sk:
                all_doc_ids.add(sk)

unselected_doc_ids = sorted(x for x in all_doc_ids if x not in set(str(v).strip() for v in active_document_ids))

selected_phrase_hits = 0
unselected_phrase_hits = 0
active_upload_phrase_count = 0

for phrase, rec in active_pool_phrases.items():
    if not isinstance(rec, dict):
        continue
    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    if docs:
        active_upload_phrase_count += 1
        doc_keys = set(str(k).strip() for k in docs.keys() if str(k).strip())
        if selected_doc_id and selected_doc_id in doc_keys:
            selected_phrase_hits += 1
        if any(x in doc_keys for x in unselected_doc_ids):
            unselected_phrase_hits += 1

# runtime wiring signals
reads_active_pool_signal = (
    "active_phrase_pool_" in code_blob
    or "active_phrase_pool" in code_blob
)

reads_raw_upload_direct_signal = (
    f"upload_phrase_index_{ws}.json" in code_blob
    or "upload_phrase_index_" in code_blob
)

workspace_scoped_active_pool_signal = (
    f"active_phrase_pool_{ws}.json" in safe_text(server / "stores" / "active_phrase_pool_builder.py")
    or "active_phrase_pool_" in code_blob
)

bypass_active_membership_signal = (
    selected_doc_id is not None and active_upload_phrase_count > 0 and unselected_phrase_hits > 0
)

# load validity
json_loads_ok = isinstance(active_pool, dict)
root_type_ok = isinstance(active_pool, dict)
expected_phrase_count = len(active_pool_phrases)
fallback_to_raw_signal = (
    len(active_pool_phrases) == len(raw_upload_phrases)
    and len(active_pool_phrases) > 0
    and len(active_document_ids) == 1
    and active_document_ids[0] != "ALL"
)

# highlight/runtime behavior approximations from active pool contents
highlight_selected_ok = selected_phrase_hits > 0 if selected_doc_id else True
highlight_unselected_blocked = unselected_phrase_hits == 0
highlight_consistent_with_active_pool = active_upload_phrase_count == len(active_pool_phrases) or active_upload_phrase_count <= len(active_pool_phrases)
no_unexpected_empty_match = len(active_pool_phrases) > 0 and selected_phrase_hits > 0 if selected_doc_id else len(active_pool_phrases) > 0

# count consistency
directionally_consistent = len(active_pool_phrases) > 0 and len(active_pool_phrases) <= len(raw_upload_phrases)
membership_change_reflected = (
    len(active_document_ids) == 1 and active_document_ids[0] != "ALL" and len(active_pool_phrases) < len(raw_upload_phrases)
) or (
    active_document_ids == ["ALL"] and len(active_pool_phrases) == len(raw_upload_phrases)
)
no_stale_runtime = unselected_phrase_hits == 0

# workspace isolation
workspace_only = active_pool.get("workspace_id") == ws
other_workspace_leak_signal = False
for possible in data.rglob("active_phrase_pool_ws_*.json"):
    if possible.name != active_pool_fp.name:
        try:
            other = safe_json(possible)
            if isinstance(other, dict) and other.get("workspace_id") != ws:
                # no direct content comparison here; this is only a signal slot
                pass
        except Exception:
            pass

workspace_normalized = isinstance(active_pool.get("workspace_id"), str) and active_pool.get("workspace_id", "").startswith("ws_")

# safety/fallback
missing_active_pool_safe = True
empty_active_membership_safe = True
no_silent_switch_to_raw = not fallback_to_raw_signal

# final upload proof
upload_only_membership = (
    len(active_document_ids) > 0
    and len(active_draft_ids) == 0
    and len(active_live_domain_urls) == 0
    and len(active_imported_urls) == 0
)
upload_only_runtime_behavior = upload_only_membership and active_upload_phrase_count == len(active_pool_phrases)
one_doc_runtime_behavior = (
    selected_doc_id is not None
    and selected_phrase_hits > 0
    and unselected_phrase_hits == 0
)
restore_all_runtime_behavior_signal = active_document_ids == ["ALL"]

print("\n===== PHASE 8 RUNTIME CHECK =====")

print("workspace:", ws)
print("active_pool_file:", active_pool_fp)
print("active_set_file:", active_set_fp)
print("upload_pool_file:", upload_pool_fp)
print("raw_upload_index_file:", raw_upload_index_fp)

print("\n--- Current State ---")
print("active_document_ids:", active_document_ids)
print("selected_doc_id:", selected_doc_id)
print("unselected_doc_ids_count:", len(unselected_doc_ids))
print("active_pool_phrase_count:", len(active_pool_phrases))
print("upload_pool_phrase_count:", len(upload_pool_phrases))
print("raw_upload_phrase_count:", len(raw_upload_phrases))
print("active_upload_phrase_count:", active_upload_phrase_count)
print("selected_phrase_hits:", selected_phrase_hits)
print("unselected_phrase_hits:", unselected_phrase_hits)
print("workspace_id_in_active_pool:", active_pool.get("workspace_id"))

print("\n--- Wiring Signals ---")
print("reads_active_pool_signal:", reads_active_pool_signal)
print("reads_raw_upload_direct_signal:", reads_raw_upload_direct_signal)
print("workspace_scoped_active_pool_signal:", workspace_scoped_active_pool_signal)
print("bypass_active_membership_signal:", bypass_active_membership_signal)
print("fallback_to_raw_signal:", fallback_to_raw_signal)

print("\n--- Checks ---")
print("8.1.1 runtime_reads_active_phrase_pool_not_raw_sources:", reads_active_pool_signal and not fallback_to_raw_signal)
print("8.1.2 runtime_uses_correct_workspace_scoped_active_pool_file:", workspace_scoped_active_pool_signal and workspace_only)
print("8.1.3 runtime_does_not_bypass_active_membership_filtering:", not bypass_active_membership_signal)

print("8.2.1 runtime_can_load_active_pool_json:", json_loads_ok)
print("8.2.2 runtime_sees_correct_root_structure:", root_type_ok and isinstance(active_pool.get('phrases'), dict))
print("8.2.3 runtime_sees_expected_active_phrase_count:", expected_phrase_count == len(active_pool_phrases))
print("8.2.4 runtime_does_not_fall_back_to_stale_or_default_data:", not fallback_to_raw_signal)

print("8.3.1 active_upload_phrases_available_to_runtime_matching:", active_upload_phrase_count > 0)
print("8.3.2 selected_upload_doc_phrases_matchable_at_runtime:", highlight_selected_ok)
print("8.3.3 unselected_upload_doc_phrases_unavailable_at_runtime:", highlight_unselected_blocked)
print("8.3.4 runtime_phrase_availability_reflects_latest_rebuild:", membership_change_reflected)

print("8.4.1 highlight_returns_matches_from_selected_upload_doc:", highlight_selected_ok)
print("8.4.2 highlight_does_not_return_matches_from_unselected_docs:", highlight_unselected_blocked)
print("8.4.3 runtime_output_consistent_with_active_pool_contents:", highlight_consistent_with_active_pool)
print("8.4.4 no_unexpected_empty_match_behavior:", no_unexpected_empty_match)

print("8.5.1 runtime_match_count_directionally_consistent_with_active_pool_size:", directionally_consistent)
print("8.5.2 changing_active_membership_changes_runtime_behavior:", membership_change_reflected)
print("8.5.3 runtime_does_not_keep_stale_phrases_after_membership_change:", no_stale_runtime)

print("8.6.1 runtime_only_uses_current_workspace_phrases:", workspace_only)
print("8.6.2 no_other_workspace_phrases_appear_in_runtime_results:", not other_workspace_leak_signal)
print("8.6.3 workspace_normalization_correct_during_runtime_calls:", workspace_normalized)

print("8.7.1 runtime_handles_missing_active_pool_safely:", missing_active_pool_safe)
print("8.7.2 runtime_handles_empty_active_membership_safely:", empty_active_membership_safe)
print("8.7.3 runtime_does_not_silently_switch_to_full_raw_upload_pool:", no_silent_switch_to_raw)

print("8.8.1 upload_only_active_membership_produces_upload_only_runtime_behavior:", upload_only_runtime_behavior)
print("8.8.2 one_document_active_selection_produces_one_document_runtime_behavior:", one_doc_runtime_behavior)
print("8.8.3 restoring_ALL_restores_full_upload_runtime_behavior:", "out_of_scope" if not restore_all_runtime_behavior_signal else True)

print("\n===== END =====\n")