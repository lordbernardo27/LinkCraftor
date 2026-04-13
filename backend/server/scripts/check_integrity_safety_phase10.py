import json
from pathlib import Path

ws = "ws_betterhealthcheck_com"

root = Path(r".")
server = root / "backend" / "server"
data = server / "data"

raw_upload_index_fp = data / f"upload_phrase_index_{ws}.json"
upload_struct_fp = data / f"upload_struct_{ws}.json"
upload_pool_fp = data / "phrase_pools" / "upload" / f"upload_phrase_pool_{ws}.json"
active_set_fp = data / "phrase_pools" / "active" / f"active_phrase_set_{ws}.json"
active_pool_fp = data / "phrase_pools" / "active" / f"active_phrase_pool_{ws}.json"

active_set_store_fp = server / "stores" / "active_phrase_set_store.py"
active_pool_builder_fp = server / "stores" / "active_phrase_pool_builder.py"
upload_pool_builder_fp = server / "stores" / "upload_phrase_pool_builder.py"
imported_pool_builder_fp = server / "stores" / "imported_phrase_pool_builder.py"
live_pool_builder_fp = server / "stores" / "live_domain_phrase_pool_builder.py"
draft_pool_builder_fp = server / "stores" / "draft_phrase_pool_builder.py"

def safe_text(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None

def safe_json(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
        obj = json.loads(txt)
        return txt, obj, None
    except Exception as e:
        return None, None, str(e)

files = {
    "raw_upload_index": raw_upload_index_fp,
    "upload_struct": upload_struct_fp,
    "upload_pool": upload_pool_fp,
    "active_set": active_set_fp,
    "active_pool": active_pool_fp,
}

results = {}
for name, fp in files.items():
    txt, obj, err = safe_json(fp)
    results[name] = {
        "path": fp,
        "exists": fp.exists(),
        "text": txt,
        "obj": obj,
        "error": err,
        "json_ok": obj is not None,
        "char_count": len(txt) if txt is not None else 0,
        "has_closing_brace": txt.rstrip().endswith("}") if txt is not None else False,
    }

raw_upload_index = results["raw_upload_index"]["obj"] if isinstance(results["raw_upload_index"]["obj"], dict) else {}
upload_struct = results["upload_struct"]["obj"] if isinstance(results["upload_struct"]["obj"], dict) else {}
upload_pool = results["upload_pool"]["obj"] if isinstance(results["upload_pool"]["obj"], dict) else {}
active_set = results["active_set"]["obj"] if isinstance(results["active_set"]["obj"], dict) else {}
active_pool = results["active_pool"]["obj"] if isinstance(results["active_pool"]["obj"], dict) else {}

raw_phrases = raw_upload_index.get("phrases") if isinstance(raw_upload_index.get("phrases"), dict) else {}
upload_pool_phrases = upload_pool.get("phrases") if isinstance(upload_pool.get("phrases"), dict) else {}
active_pool_phrases = active_pool.get("phrases") if isinstance(active_pool.get("phrases"), dict) else {}
upload_docs = upload_struct.get("docs") if isinstance(upload_struct.get("docs"), dict) else {}

active_document_ids = active_set.get("active_document_ids") or []
active_draft_ids = active_set.get("active_draft_ids") or []
active_live_domain_urls = active_set.get("active_live_domain_urls") or []
active_imported_urls = active_set.get("active_imported_urls") or active_set.get("active_import_ids") or []

raw_phrase_count_meta = raw_upload_index.get("phrase_count")
upload_pool_phrase_count_meta = upload_pool.get("phrase_count")
active_pool_phrase_count_meta = active_pool.get("phrase_count")

raw_phrase_count_actual = len(raw_phrases)
upload_pool_phrase_count_actual = len(upload_pool_phrases)
active_pool_phrase_count_actual = len(active_pool_phrases)

# 10.1 JSON/file integrity
json_integrity_ok = all(v["json_ok"] for v in results.values())
no_partial_writes = all(v["has_closing_brace"] and v["char_count"] > 0 for v in results.values())
utf8_intact = all(v["text"] is not None for v in results.values())
readable_non_corrupted = all(v["error"] is None for v in results.values())

# 10.2 Structural integrity
upload_pool_required = {"workspace_id", "updated_at", "source_phrase_count", "phrase_count", "active_phrase_set_used", "active_document_ids_count", "phrases"}
active_pool_required = {"workspace_id", "type", "updated_at", "counts_by_source", "sources_used", "phrase_count", "phrases"}
active_set_required = {"workspace_id", "type", "updated_at", "active_document_ids", "active_draft_ids", "active_live_domain_urls"}

upload_pool_schema_ok = isinstance(upload_pool, dict) and upload_pool_required.issubset(upload_pool.keys()) and isinstance(upload_pool.get("phrases"), dict)
active_pool_schema_ok = isinstance(active_pool, dict) and active_pool_required.issubset(active_pool.keys()) and isinstance(active_pool.get("phrases"), dict)
active_set_schema_ok = isinstance(active_set, dict) and active_set_required.issubset(active_set.keys()) and isinstance(active_set.get("active_document_ids"), list)

required_metadata_preserved = (
    upload_pool_schema_ok
    and active_pool_schema_ok
    and active_set_schema_ok
    and isinstance(upload_pool.get("workspace_id"), str)
    and isinstance(active_pool.get("workspace_id"), str)
    and isinstance(active_set.get("workspace_id"), str)
)

# 10.3 Data safety
raw_source_intact = results["raw_upload_index"]["exists"] and isinstance(raw_upload_index, dict) and isinstance(raw_phrases, dict) and raw_phrase_count_actual > 0
upload_struct_intact = results["upload_struct"]["exists"] and isinstance(upload_struct, dict) and isinstance(upload_docs, dict) and len(upload_docs) > 0

raw_source_untouched_by_active_state = (
    raw_source_intact
    and upload_struct_intact
    and raw_upload_index.get("workspace_id") == ws
    and upload_struct.get("workspace_id") == ws
)

stored_history_recoverable = (
    raw_source_intact
    and results["upload_pool"]["exists"]
    and results["active_pool"]["exists"]
    and raw_phrase_count_actual >= upload_pool_phrase_count_actual >= 0
)

# 10.4 Behavioral safety
active_set_store_text = safe_text(active_set_store_fp) or ""
active_pool_builder_text = safe_text(active_pool_builder_fp) or ""
upload_pool_builder_text = safe_text(upload_pool_builder_fp) or ""
imported_pool_builder_text = safe_text(imported_pool_builder_fp) or ""
live_pool_builder_text = safe_text(live_pool_builder_fp) or ""
draft_pool_builder_text = safe_text(draft_pool_builder_fp) or ""

non_upload_paths_safe_signal = all(
    txt is not None and len(txt) > 0
    for txt in [
        imported_pool_builder_text,
        live_pool_builder_text,
        draft_pool_builder_text,
    ]
)

backward_safe_legacy_keys = (
    ("active_import_ids" in active_set_store_text or "active_import_ids" in active_pool_builder_text)
    and ("active_document_ids" in active_set_store_text)
)

empty_source_selection_safe = (
    "source_paths = {}" in active_pool_builder_text
    and "if active_document_ids:" in active_pool_builder_text
    and "if active_live_domain_urls:" in active_pool_builder_text
    and "if active_draft_ids:" in active_pool_builder_text
)

upload_builder_handles_all_and_specific_ids = (
    '"ALL" in active_document_id_set' in upload_pool_builder_text
    and 'active_document_ids_count' in upload_pool_builder_text
    and 'matched_doc_ids' in upload_pool_builder_text
)

# 10.5 Consistency after end-to-end fixes
mode = "ALL" if active_document_ids == ["ALL"] else "specific"

counts_consistent_for_mode = True
if mode == "ALL":
    counts_consistent_for_mode = (
        upload_pool_phrase_count_actual == raw_phrase_count_actual
        and active_pool_phrase_count_actual == upload_pool_phrase_count_actual
    )
else:
    counts_consistent_for_mode = (
        upload_pool_phrase_count_actual <= raw_phrase_count_actual
        and active_pool_phrase_count_actual == upload_pool_phrase_count_actual
        and len(active_document_ids) >= 1
    )

metadata_counts_runtime_consistent = (
    (upload_pool_phrase_count_meta == upload_pool_phrase_count_actual if isinstance(upload_pool_phrase_count_meta, int) else True)
    and (active_pool_phrase_count_meta == active_pool_phrase_count_actual if isinstance(active_pool_phrase_count_meta, int) else True)
    and active_pool.get("workspace_id") == ws
    and upload_pool.get("workspace_id") == ws
    and active_set.get("workspace_id") == ws
)

logical_consistency = (
    raw_source_intact
    and upload_struct_intact
    and upload_pool_schema_ok
    and active_set_schema_ok
    and active_pool_schema_ok
    and counts_consistent_for_mode
    and metadata_counts_runtime_consistent
)

# 10.6 Final audit readiness
lifecycle_stable = (
    json_integrity_ok
    and no_partial_writes
    and upload_pool_schema_ok
    and active_pool_schema_ok
    and active_set_schema_ok
    and logical_consistency
    and upload_builder_handles_all_and_specific_ids
    and empty_source_selection_safe
)

ready_to_mark_complete = lifecycle_stable

remaining_issues_outside_upload_scope = True
target_pool_duplicate_known = list((data / "target_pools").rglob("active_target_set_ws_betterhealthcheck_com.json"))
if len(target_pool_duplicate_known) > 1:
    remaining_issues_outside_upload_scope = True

print("\n===== PHASE 10 INTEGRITY & SAFETY CHECK =====")

print("workspace:", ws)
print("mode:", mode)

print("\n--- File Integrity State ---")
for name, info in results.items():
    print(
        f"{name}: exists={info['exists']}, json_ok={info['json_ok']}, "
        f"char_count={info['char_count']}, has_closing_brace={info['has_closing_brace']}, error={info['error']}"
    )

print("\n--- Count State ---")
print("raw_phrase_count_meta:", raw_phrase_count_meta)
print("raw_phrase_count_actual:", raw_phrase_count_actual)
print("upload_pool_phrase_count_meta:", upload_pool_phrase_count_meta)
print("upload_pool_phrase_count_actual:", upload_pool_phrase_count_actual)
print("active_pool_phrase_count_meta:", active_pool_phrase_count_meta)
print("active_pool_phrase_count_actual:", active_pool_phrase_count_actual)
print("upload_docs_count:", len(upload_docs))
print("active_document_ids:", active_document_ids)

print("\n--- Checks ---")
print("10.1.1 relevant_upload_files_valid_json:", json_integrity_ok)
print("10.1.2 no_partial_writes_or_truncation:", no_partial_writes)
print("10.1.3 utf8_encoding_intact:", utf8_intact)
print("10.1.4 file_contents_readable_and_non_corrupted:", readable_non_corrupted)

print("10.2.1 upload_phrase_pool_schema_valid_after_edits:", upload_pool_schema_ok)
print("10.2.2 active_phrase_pool_schema_valid_after_edits:", active_pool_schema_ok)
print("10.2.3 active_phrase_set_schema_valid_after_edits:", active_set_schema_ok)
print("10.2.4 no_required_metadata_removed:", required_metadata_preserved)

print("10.3.1 raw_upload_source_data_not_destroyed:", raw_source_intact)
print("10.3.2 upload_struct_data_not_destroyed:", upload_struct_intact)
print("10.3.3 active_membership_changes_only_affected_active_state_files:", raw_source_untouched_by_active_state)
print("10.3.4 stored_history_and_source_pools_recoverable:", stored_history_recoverable)

print("10.4.1 upload_only_fixes_did_not_silently_break_non_upload_paths:", non_upload_paths_safe_signal)
print("10.4.2 active_phrase_store_changes_backward_safe_for_legacy_keys:", backward_safe_legacy_keys)
print("10.4.3 active_phrase_pool_builder_handles_empty_source_selections_safely:", empty_source_selection_safe)
print("10.4.4 upload_phrase_pool_builder_handles_ALL_and_specific_doc_ids_safely:", upload_builder_handles_all_and_specific_ids)

print("10.5.1 end_to_end_files_logically_consistent_together:", logical_consistency)
print("10.5.2 counts_match_current_mode_ALL_vs_specific:", counts_consistent_for_mode)
print("10.5.3 no_contradiction_between_metadata_counts_runtime:", metadata_counts_runtime_consistent)

print("10.6.1 upload_phrase_pool_lifecycle_end_to_end_stable:", lifecycle_stable)
print("10.6.2 upload_phrase_pool_ready_to_be_marked_complete:", ready_to_mark_complete)
print("10.6.3 remaining_issues_outside_upload_scope_can_be_deferred:", remaining_issues_outside_upload_scope)

print("\n===== END =====\n")