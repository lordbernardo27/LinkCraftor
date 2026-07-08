from pathlib import Path

p = Path("backend/server/routes/files.py")
code = p.read_text(encoding="utf-8")

import_line = "from backend.server.runtime.live_route_orchestration_hooks import enqueue_and_run_upload_ingestion_job_v1\n"

if import_line not in code:
    marker = "from fastapi.responses import FileResponse\n"
    if marker not in code:
        raise SystemExit("Could not find files.py import marker.")
    code = code.replace(marker, marker + import_line)

old = "_append_to_docs_index(ws_norm, meta)"
new = '''_append_to_docs_index(ws_norm, meta)

        try:
            orchestration_result = enqueue_and_run_upload_ingestion_job_v1(
                workspace_id=ws_norm,
                upload_meta=meta,
            )
            meta["universal_knowledge_orchestration"] = orchestration_result
            processing_job_id = orchestration_result.get("job_id") or processing_job_id
        except Exception as e:
            meta["universal_knowledge_orchestration"] = {
                "ok": False,
                "error": f"upload_orchestration_failed:{str(e)[:160]}",
            }'''

if old not in code:
    raise SystemExit("Could not find _append_to_docs_index(ws_norm, meta) insertion point.")

if "enqueue_and_run_upload_ingestion_job_v1(" not in code:
    code = code.replace(old, new, 1)

p.write_text(code, encoding="utf-8")
print("Patched files.py upload route.")
