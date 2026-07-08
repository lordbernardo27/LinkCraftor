from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

backup = p.with_suffix(".py.bak_uduc_to_uucd")
backup.write_text(code, encoding="utf-8")

future = "from __future__ import annotations"
uduc_import = "from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result"
uucd_import = "from backend.server.stores.universal_unified_content_document_convergence import build_and_write_uucd_from_uduc_v1"

lines = code.splitlines()
lines = [line for line in lines if line.strip() not in {future, uduc_import, uucd_import}]

code = "\n".join([future, uduc_import, uucd_import, ""] + lines) + "\n"

old = '''        written = build_and_write_uduc_from_extraction_result(
            workspace_id=workspace_id,
            document_id=document_id,
            extraction_result=extraction_result,
        )

        results.append({
            "ok": True,
            "document_id": document_id,
            "filename": filename,
            "uduc_path": written.get("path") or written.get("output_path"),
        })
'''

new = '''        written = build_and_write_uduc_from_extraction_result(
            workspace_id=workspace_id,
            document_id=document_id,
            extraction_result=extraction_result,
        )

        uduc_payload = written.get("uduc") or written.get("document") or extraction_result
        uucd_written = build_and_write_uucd_from_uduc_v1(uduc_payload)

        results.append({
            "ok": True,
            "document_id": document_id,
            "filename": filename,
            "uduc_path": written.get("path") or written.get("output_path"),
            "uucd_path": uucd_written.get("uucd_path"),
            "uucd_written": bool(uucd_written.get("ok")),
        })
'''

if old not in code:
    raise SystemExit("Could not find UDUC write block to extend into UUCD.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")

print("Patched worker: UDUC now immediately writes UUCD.")
print("Backup:", backup)
