from pathlib import Path

p = Path("backend/server/runtime/automatic_canonical_rebuild_runner.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

backup = p.with_suffix(".py.bak_filter_upload_docs_early")
backup.write_text(code, encoding="utf-8")

marker = '''    upload_job_results = create_and_run_jobs(workspace_id, upload_docs, "uploaded_document")
'''

insert = '''    # Remove internal metadata/index files before creating jobs.
    upload_docs = [
        d for d in upload_docs
        if str(d.get("document_id") or "").lower() not in {"index", "work_index"}
        and str(d.get("filename") or "").lower() not in {"index.json", "work_index.json"}
        and str(d.get("title") or "").lower() not in {"index", "work index"}
    ]

    upload_job_results = create_and_run_jobs(workspace_id, upload_docs, "uploaded_document")
'''

if marker not in code:
    raise SystemExit("Could not find upload_job_results line.")

code = code.replace(marker, insert)

p.write_text(code, encoding="utf-8")

print("Patched rebuild runner to stop scheduling index/work_index extraction jobs.")
print("Backup:", backup)
