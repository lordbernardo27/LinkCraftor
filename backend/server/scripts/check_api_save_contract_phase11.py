from pathlib import Path
import re

root = Path(r".")
server = root / "backend" / "server"

files_route_fp = server / "routes" / "files.py"
app_js_fp = root / "frontend" / "public" / "assets" / "js" / "app.js"
active_set_store_fp = server / "stores" / "active_phrase_set_store.py"

def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

files_route_text = safe_text(files_route_fp)
app_js_text = safe_text(app_js_fp)
active_set_store_text = safe_text(active_set_store_fp)

combined = "\n".join([files_route_text, app_js_text, active_set_store_text])

def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.I | re.M) is not None

def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.I | re.M))

# 11.1 Source-specific save payloads
doc_payload_signal = (
    has(r"active_document_ids", app_js_text)
    and not has(r"active_upload_ids", app_js_text)
)

draft_payload_signal = has(r"active_draft_ids", app_js_text)

imported_payload_signal = (
    has(r"active_imported_urls", app_js_text)
    or has(r"active_import_ids", app_js_text)
)

live_payload_signal = has(r"active_live_domain_urls", app_js_text)

# Save contract / merge-safe behavior in backend
save_endpoint_exists = has(r"save_active_phrase_set|active_phrase_set|active_document_ids", files_route_text + active_set_store_text)

preserve_omitted_fields_signal = (
    has(r"base\s*=\s*_default_obj", active_set_store_text)
    and has(r"for key in\s*\(", active_set_store_text)
)

update_only_supplied_fields_signal = (
    has(r"raw\s*=\s*obj\.get\(key\)\s*or\s*\[\]", active_set_store_text)
    or has(r"obj\.get\(key\)", active_set_store_text)
)

# Stronger merge-safe signal from route layer:
# route should load current object, then only replace provided keys
route_loads_current_state = (
    has(r"load_active_phrase_set", files_route_text)
    or has(r"_active_phrase_set_path", files_route_text)
    or has(r"obj\s*=", files_route_text)
)

route_handles_document_only = has(r"active_document_ids", files_route_text)
route_handles_draft_only = has(r"active_draft_ids", files_route_text)
route_handles_live_only = has(r"active_live_domain_urls", files_route_text)
route_handles_import_only = (
    has(r"active_imported_urls", files_route_text)
    or has(r"active_import_ids", files_route_text)
)

one_source_does_not_wipe_others_signal = (
    route_loads_current_state
    and route_handles_document_only
    and route_handles_draft_only
    and route_handles_live_only
    and route_handles_import_only
)

print("\n===== PHASE 11 API SAVE CONTRACT CHECK =====")

print("\n--- File Paths ---")
print("files_route_fp:", files_route_fp)
print("app_js_fp:", app_js_fp)
print("active_set_store_fp:", active_set_store_fp)

print("\n--- Signal Counts ---")
print("active_document_ids count:", count(r"active_document_ids", combined))
print("active_draft_ids count:", count(r"active_draft_ids", combined))
print("active_live_domain_urls count:", count(r"active_live_domain_urls", combined))
print("active_imported_urls count:", count(r"active_imported_urls", combined))
print("active_import_ids count:", count(r"active_import_ids", combined))
print("active_upload_ids count:", count(r"active_upload_ids", combined))

print("\n--- Checks ---")
print("11.1.1 documents_callers_send_only_active_document_ids:", doc_payload_signal)
print("11.1.2 drafts_callers_send_only_active_draft_ids:", draft_payload_signal)
print("11.1.3 imported_callers_send_only_active_imported_urls:", imported_payload_signal)
print("11.1.4 live_domain_callers_send_only_active_live_domain_urls:", live_payload_signal)

print("11.2.1 save_endpoints_preserve_omitted_fields:", preserve_omitted_fields_signal)
print("11.2.2 save_endpoints_update_only_supplied_fields:", update_only_supplied_fields_signal)
print("11.2.3 one_source_save_does_not_wipe_other_active_memberships:", one_source_does_not_wipe_others_signal)

print("\n===== END =====\n")