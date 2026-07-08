from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")
code = p.read_text(encoding="utf-8")

backup = p.with_suffix(".py.bak_live_uduc")
backup.write_text(code, encoding="utf-8")

import_line = "from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result\n"

if import_line not in code:
    code = import_line + code

helper = r'''

def _write_uduc_for_upload_batch_job(job):
    from pathlib import Path
    import zipfile
    import xml.etree.ElementTree as ET

    payload = job.get("payload") or {}
    workspace_id = job.get("workspace_id") or payload.get("workspace_id") or "default"

    docs = payload.get("documents") or []
    if not docs and payload.get("document_id"):
        docs = [payload]

    results = []

    for doc in docs:
        document_id = doc.get("document_id") or doc.get("doc_id")
        filename = doc.get("filename") or doc.get("original_name") or doc.get("stored_name") or document_id
        stored_path = doc.get("stored_path")

        if not document_id:
            results.append({"ok": False, "reason": "missing_document_id"})
            continue

        if not stored_path:
            docs_dir = Path("backend/server/data/docs") / workspace_id
            matches = list(docs_dir.glob(f"{document_id}__*"))
            if matches:
                stored_path = str(matches[0])

        if not stored_path or not Path(stored_path).exists():
            results.append({"ok": False, "document_id": document_id, "reason": "missing_stored_path"})
            continue

        fp = Path(stored_path)
        raw_text = ""

        try:
            raw_text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            raw_text = ""

        if not raw_text.strip() and fp.suffix.lower() == ".docx":
            try:
                with zipfile.ZipFile(fp) as z:
                    xml = z.read("word/document.xml")
                root = ET.fromstring(xml)
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                raw_text = " ".join(t.text for t in root.findall(".//w:t", ns) if t.text).strip()
            except Exception:
                raw_text = ""

        if not raw_text.strip():
            results.append({"ok": False, "document_id": document_id, "reason": "empty_extracted_text"})
            continue

        extraction_result = {
            "workspace_id": workspace_id,
            "document_id": document_id,
            "title": Path(str(filename)).stem,
            "original_name": filename,
            "filename": filename,
            "content_body": raw_text,
            "text": raw_text,
            "headings": [],
            "metadata": {
                "source_type": "uploaded_document",
                "stored_path": stored_path,
                "source_pipeline": "live_upload_orchestration",
            },
        }

        written = build_and_write_uduc_from_extraction_result(
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

    return results
'''

if "_write_uduc_for_upload_batch_job" not in code:
    code += helper

old = '''        if job_type == "upload_document_batch":
            result["document_count"] = len(payload.get("documents") or [])
'''

new = '''        if job_type == "upload_document_batch":
            result["document_count"] = len(payload.get("documents") or [])
            result["uduc_write_results"] = _write_uduc_for_upload_batch_job(job)
'''

if old not in code:
    raise SystemExit("Could not find exact upload_document_batch result block.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
print("Patched universal_knowledge_worker.py to write UDUC during upload_document_batch.")
print("Backup created:", backup)
