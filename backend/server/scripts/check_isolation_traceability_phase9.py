import json
import re
from pathlib import Path

ws = "ws_betterhealthcheck_com"

root = Path(r".")
server = root / "backend" / "server"
data = server / "data"

upload_pool_fp = data / "phrase_pools" / "upload" / f"upload_phrase_pool_{ws}.json"
active_pool_fp = data / "phrase_pools" / "active" / f"active_phrase_pool_{ws}.json"
active_set_fp = data / "phrase_pools" / "active" / f"active_phrase_set_{ws}.json"
raw_upload_index_fp = data / f"upload_phrase_index_{ws}.json"
upload_struct_fp = data / f"upload_struct_{ws}.json"

def safe_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

upload_pool = safe_json(upload_pool_fp) if upload_pool_fp.exists() else {}
active_pool = safe_json(active_pool_fp) if active_pool_fp.exists() else {}
active_set = safe_json(active_set_fp) if active_set_fp.exists() else {}
raw_upload_index = safe_json(raw_upload_index_fp) if raw_upload_index_fp.exists() else {}
upload_struct = safe_json(upload_struct_fp) if upload_struct_fp.exists() else {}

upload_phrases = upload_pool.get("phrases") if isinstance(upload_pool, dict) and isinstance(upload_pool.get("phrases"), dict) else {}
active_phrases = active_pool.get("phrases") if isinstance(active_pool, dict) and isinstance(active_pool.get("phrases"), dict) else {}
raw_upload_phrases = raw_upload_index.get("phrases") if isinstance(raw_upload_index, dict) and isinstance(raw_upload_index.get("phrases"), dict) else {}
upload_docs = upload_struct.get("docs") if isinstance(upload_struct, dict) and isinstance(upload_struct.get("docs"), dict) else {}

active_document_ids = active_set.get("active_document_ids") or []

# 9.1 Workspace isolation
upload_workspace_ok = isinstance(upload_pool, dict) and upload_pool.get("workspace_id") == ws
active_workspace_ok = isinstance(active_pool, dict) and active_pool.get("workspace_id") == ws

runtime_leak_signal = False
for phrase, rec in active_phrases.items():
    if not isinstance(rec, dict):
        continue
    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    for doc_id in docs.keys():
        s = str(doc_id).strip()
        if s and s not in upload_docs:
            runtime_leak_signal = True
            break
    if runtime_leak_signal:
        break

# 9.2 Source traceability
active_traceable = 0
active_untraceable = 0
filtered_traceable = 0
filtered_untraceable = 0
merged_traceable = 0
merged_untraceable = 0
source_metadata_usable_count = 0

for phrase, rec in upload_phrases.items():
    if not isinstance(rec, dict):
        continue
    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    if docs:
        filtered_traceable += 1
    else:
        filtered_untraceable += 1

for phrase, rec in active_phrases.items():
    if not isinstance(rec, dict):
        continue
    docs = rec.get("docs") if isinstance(rec.get("docs"), dict) else {}
    if docs:
        active_traceable += 1
        merged_traceable += 1
    else:
        active_untraceable += 1
        merged_untraceable += 1

    if any(k in rec for k in ["docs", "source_type", "source", "pool_sources"]):
        source_metadata_usable_count += 1

# 9.3 File/path traceability
relevant_files = [
    upload_pool_fp,
    active_pool_fp,
    active_set_fp,
    raw_upload_index_fp,
    upload_struct_fp,
]

existing_relevant_files = [p for p in relevant_files if p.exists()]
name_pattern_ok = all(
    p.name.endswith(f"{ws}.json") or p.name == f"upload_struct_{ws}.json"
    for p in existing_relevant_files
)

search_paths = list(data.rglob(f"*{ws}*.json"))
conflicting_duplicates = []
seen_names = {}

for p in search_paths:
    name = p.name
    if name not in seen_names:
        seen_names[name] = [p]
    else:
        seen_names[name].append(p)

for name, paths in seen_names.items():
    if len(paths) > 1:
        conflicting_duplicates.append((name, [str(x) for x in paths]))

bad_ws_ws = [str(p) for p in data.rglob("*ws_ws_*")]
bad_non_normalized = []
for p in data.rglob("*.json"):
    name = p.name
    if "betterhealthcheck_com" in name and "ws_betterhealthcheck_com" not in name and "workspace_ws_betterhealthcheck_com.json" != name:
        if not name.startswith("workspace_"):
            bad_non_normalized.append(str(p))

# 9.4 Metadata integrity
workspace_ids = {}
for p in existing_relevant_files:
    obj = safe_json(p)
    if isinstance(obj, dict):
        workspace_ids[str(p)] = obj.get("workspace_id")

workspace_ids_ok = all(v == ws for v in workspace_ids.values() if v is not None)

raw_phrase_count = raw_upload_index.get("phrase_count") if isinstance(raw_upload_index, dict) else None
upload_phrase_count = upload_pool.get("phrase_count") if isinstance(upload_pool, dict) else None
active_phrase_count = active_pool.get("phrase_count") if isinstance(active_pool, dict) else None

counts_metadata_consistent = True
if isinstance(upload_phrase_count, int) and isinstance(upload_phrases, dict):
    counts_metadata_consistent = counts_metadata_consistent and (upload_phrase_count == len(upload_phrases))
if isinstance(active_phrase_count, int) and isinstance(active_phrases, dict):
    counts_metadata_consistent = counts_metadata_consistent and (active_phrase_count == len(active_phrases))
if isinstance(raw_phrase_count, int) and isinstance(raw_upload_phrases, dict):
    counts_metadata_consistent = counts_metadata_consistent and (raw_phrase_count == len(raw_upload_phrases))

# 9.5 Debuggability
can_inspect_upload_pool = upload_pool_fp.exists() and isinstance(upload_pool, dict) and isinstance(upload_phrases, dict)
can_inspect_active_pool = active_pool_fp.exists() and isinstance(active_pool, dict) and isinstance(active_phrases, dict)
can_inspect_active_set = active_set_fp.exists() and isinstance(active_set, dict) and isinstance(active_document_ids, list)

inspection_sufficient = (
    can_inspect_upload_pool
    and can_inspect_active_pool
    and can_inspect_active_set
    and isinstance(upload_phrase_count, int)
    and isinstance(active_phrase_count, int)
    and "counts_by_source" in active_pool
    and "sources_used" in active_pool
)

print("\n===== PHASE 9 ISOLATION & TRACEABILITY CHECK =====")

print("workspace:", ws)

print("\n--- File State ---")
print("upload_pool_file:", upload_pool_fp)
print("active_pool_file:", active_pool_fp)
print("active_set_file:", active_set_fp)
print("raw_upload_index_file:", raw_upload_index_fp)
print("upload_struct_file:", upload_struct_fp)

print("\n--- Current Counts ---")
print("raw_upload_phrase_count:", raw_phrase_count)
print("upload_pool_phrase_count:", upload_phrase_count)
print("active_pool_phrase_count:", active_phrase_count)
print("upload_docs_count:", len(upload_docs))
print("active_document_ids:", active_document_ids)

print("\n--- Traceability Stats ---")
print("filtered_traceable:", filtered_traceable)
print("filtered_untraceable:", filtered_untraceable)
print("active_traceable:", active_traceable)
print("active_untraceable:", active_untraceable)
print("source_metadata_usable_count:", source_metadata_usable_count)

print("\n--- Metadata ---")
print("workspace_ids:", workspace_ids)
print("bad_ws_ws_files:", bad_ws_ws)
print("bad_non_normalized_files:", bad_non_normalized)
print("conflicting_duplicates:", conflicting_duplicates)

print("\n--- Checks ---")
print("9.1.1 upload_pool_isolated_to_correct_workspace:", upload_workspace_ok)
print("9.1.2 active_pool_isolated_to_correct_workspace:", active_workspace_ok)
print("9.1.3 runtime_does_not_leak_across_workspaces:", not runtime_leak_signal)

print("9.2.1 each_active_upload_phrase_has_traceable_doc_linkage:", active_traceable > 0 and active_untraceable == 0)
print("9.2.2 traceability_survives_filtering_into_upload_pool:", filtered_traceable > 0 and filtered_untraceable == 0)
print("9.2.3 traceability_survives_merging_into_active_pool:", merged_traceable > 0 and merged_untraceable == 0)

print("9.3.1 relevant_files_follow_workspace_scoped_naming:", name_pattern_ok)
print("9.3.2 no_duplicate_conflicting_files_exist:", len(conflicting_duplicates) == 0)
print("9.3.3 no_ws_ws_or_non_normalized_artifacts_remain:", len(bad_ws_ws) == 0 and len(bad_non_normalized) == 0)

print("9.4.1 workspace_ids_inside_files_match_expected_ws:", workspace_ids_ok)
print("9.4.2 source_metadata_remains_usable:", source_metadata_usable_count > 0)
print("9.4.3 counts_and_metadata_do_not_contradict_each_other:", counts_metadata_consistent)

print("9.5.1 upload_pool_inspection_possible:", can_inspect_upload_pool)
print("9.5.2 active_pool_inspection_possible:", can_inspect_active_pool)
print("9.5.3 active_membership_state_inspection_possible:", can_inspect_active_set)
print("9.5.4 inspection_sufficient_to_explain_runtime_outcomes:", inspection_sufficient)

print("\n===== END =====\n")