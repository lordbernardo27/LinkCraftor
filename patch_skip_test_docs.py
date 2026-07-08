from pathlib import Path

p = Path("backend/server/runtime/automatic_canonical_rebuild_runner.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

backup = p.with_suffix(".py.bak_skip_test_docs")
backup.write_text(code, encoding="utf-8")

old = '''        and str(d.get("title") or "").lower() not in {"index", "work index"}
    ]
'''

new = '''        and str(d.get("title") or "").lower() not in {"index", "work index"}
        and "__test" not in str(d.get("document_id") or "").lower()
        and "__test2" not in str(d.get("document_id") or "").lower()
        and "__wrap_test" not in str(d.get("document_id") or "").lower()
        and "__tmp_upload_test" not in str(d.get("document_id") or "").lower()
        and "__ui_store_test" not in str(d.get("document_id") or "").lower()
    ]
'''

if old not in code:
    raise SystemExit("Could not find filter block to extend.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")

print("Patched rebuild runner to skip test documents.")
print("Backup:", backup)
