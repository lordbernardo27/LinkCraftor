from pathlib import Path

p = Path("backend/server/runtime/automatic_canonical_rebuild_runner.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

backup = p.with_suffix(".py.bak_skip_internal_indexes")
backup.write_text(code, encoding="utf-8")

old = '''    for doc in upload_docs:
        write_json(UDUC_DIR / workspace_id / f"{doc['document_id']}.json", doc)
'''

new = '''    # Skip internal metadata/index files. They are not user documents.
    upload_docs = [
        d for d in upload_docs
        if str(d.get("document_id") or "").lower() not in {"index", "work_index"}
        and not str(d.get("filename") or "").lower() in {"index.json", "work_index.json"}
        and not str(d.get("title") or "").lower() in {"index", "work index"}
    ]

    for doc in upload_docs:
        write_json(UDUC_DIR / workspace_id / f"{doc['document_id']}.json", doc)
'''

if old not in code:
    raise SystemExit("Could not find upload_docs write block.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")

print("Patched rebuild runner to skip index.json and work_index.json.")
print("Backup:", backup)
