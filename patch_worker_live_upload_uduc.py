from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")
code = p.read_text(encoding="utf-8")

import_line = "from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result\n"

if import_line not in code:
    marker = "from backend.server.jobs.universal_knowledge_orchestrator import"
    pos = code.find(marker)
    if pos < 0:
        raise SystemExit("Could not find worker import marker.")
    line_end = code.find("\n", pos)
    code = code[:line_end+1] + import_line + code[line_end+1:]

helper = r'''


def _write_uduc_for_live_upload_job_v1(job):
    payload = job.get("payload") or {}
    workspace_id = job.get("workspace_id") or payload.get("workspace_id") or "default"
    document_id = payload.get("document_id") or payload.get("doc_id")
    filename = payload.get("filename") or payload.get("stored_name") or document_id
    stored_path = payload.get("stored_path")

    if not document_id:
        return {"ok": False, "reason": "missing_document_id"}

    if not stored_path:
        docs_dir = Path("backend/server/data/docs") / workspace_id
        matches = list(docs_dir.glob(f"{document_id}__*"))
        if matches:
            stored_path = str(matches[0])

    if not stored_path or not Path(stored_path).exists():
        return {"ok": False, "reason": "missing_stored_path", "stored_path": stored_path}

    fp = Path(stored_path)

    try:
        raw_text = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        raw_text = ""

    if not raw_text.strip():
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(fp) as z:
                xml = z.read("word/document.xml")
            root = ET.fromstring(xml)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            parts = []
            for t in root.findall(".//w:t", ns):
                if t.text:
                    parts.append(t.text)
            raw_text = " ".join(parts).strip()
        except Exception:
            raw_text = ""

    if not raw_text.strip():
        return {"ok": False, "reason": "empty_extracted_text", "stored_path": stored_path}

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

    result = build_and_write_uduc_from_extraction_result(
        workspace_id=workspace_id,
        document_id=document_id,
        extraction_result=extraction_result,
    )

    return {
        "ok": True,
        "document_id": document_id,
        "uduc_path": result.get("path") or result.get("output_path"),
    }
'''

if "_write_uduc_for_live_upload_job_v1" not in code:
    code += helper

old = '''    if job_type == "upload_document_batch":
        return _complete(job, {"next_jobs": ["build_uduc", "build_uucd", "build_body_store", "certify_uucd_body_store"]})
'''

new = '''    if job_type == "upload_document_batch":
        uduc_result = _write_uduc_for_live_upload_job_v1(job)
        return _complete(job, {
            "uduc_written": uduc_result,
            "next_jobs": ["build_uduc", "build_uucd", "build_body_store", "certify_uucd_body_store"],
        })
'''

if old not in code:
    raise SystemExit("Could not find upload_document_batch worker block.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
print("Patched worker to write UDUC during live upload orchestration.")
