from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.stores.universal_article_body_store import build_universal_article_body_store_from_uucd_payload_v2
from backend.server.stores.uucd_body_store_certification import certify_uucd_body_store_v1
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


ROOT = Path("backend/server/data")
DOCS_DIR = ROOT / "docs"
RAW_HTML_DIR = ROOT / "raw_website_html"
UDUC_DIR = ROOT / "uploaded_document_unified_content"
UUCD_DIR = ROOT / "universal_unified_content_documents"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def safe_id(value: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in str(value or "unknown"))[:120]


def collect_uploaded_documents(workspace_id: str) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not DOCS_DIR.exists():
        return docs

    allowed = {".txt", ".md", ".html", ".htm", ".json"}

    for fp in DOCS_DIR.rglob("*"):
        if not fp.is_file() or fp.suffix.lower() not in allowed:
            continue

        text = read_text(fp).strip()
        if not text:
            continue

        doc_id = safe_id(fp.stem)

        docs.append({
            "schema_version": "uploaded_document_unified_content_v1",
            "workspace_id": workspace_id,
            "document_id": doc_id,
            "source_type": "uploaded_document",
            "source_format": fp.suffix.lower().lstrip("."),
            "original_filename": fp.name,
            "stored_path": str(fp),
            "title": fp.stem.replace("_", " ").replace("-", " ").strip(),
            "h1": fp.stem.replace("_", " ").replace("-", " ").strip(),
            "headings": [],
            "content_body": text,
            "structure": {
                "paragraph_count": max(1, len([b for b in text.split("\n\n") if b.strip()])),
                "estimated_character_count": len(text),
                "source": "automatic_rebuild_runner",
            },
            "metadata": {
                "rebuilt_from": str(fp),
                "automatic_rebuild": True,
            },
        })

    return docs


def collect_website_documents(workspace_id: str) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    candidates = []

    for folder in [RAW_HTML_DIR]:
        if folder.exists():
            candidates.extend([p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm", ".txt"}])

    seen = set()

    for fp in candidates:
        if str(fp) in seen:
            continue
        seen.add(str(fp))

        text = read_text(fp).strip()
        if not text:
            continue

        doc_id = safe_id(fp.stem)

        docs.append({
            "schema_version": "website_unified_content_v1",
            "workspace_id": workspace_id,
            "document_id": doc_id,
            "source_type": "website",
            "source_format": "html" if fp.suffix.lower() in {".html", ".htm"} else "txt",
            "source_identity": {
                "source_file": str(fp),
            },
            "title": fp.stem.replace("_", " ").replace("-", " ").strip(),
            "h1": fp.stem.replace("_", " ").replace("-", " ").strip(),
            "headings": [],
            "content_body": text,
            "structure": {
                "paragraph_count": max(1, len([b for b in text.split("\n\n") if b.strip()])),
                "estimated_character_count": len(text),
                "source": "automatic_rebuild_runner",
            },
            "metadata": {
                "rebuilt_from": str(fp),
                "automatic_rebuild": True,
            },
        })

    return docs


def create_and_run_jobs(workspace_id: str, docs: List[Dict[str, Any]], source_type: str) -> List[Dict[str, Any]]:
    results = []

    for doc in docs:
        job_type = "upload_document_extraction" if source_type == "uploaded_document" else "article_extraction"

        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type=job_type,
            payload={
                "document_id": doc["document_id"],
                "source_type": source_type,
                "title": doc.get("title"),
                "automatic_rebuild": True,
            },
        )

        results.append(execute_universal_knowledge_job_v1(job))

    return results


def build_uucd_collection(workspace_id: str, upload_docs: List[Dict[str, Any]], website_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    docs = []

    for doc in website_docs:
        docs.append({
            "schema_version": "universal_unified_content_document_v1",
            "pipeline_version": "automatic_rebuild_runner_v1",
            "workspace_id": workspace_id,
            "document_id": doc["document_id"],
            "source_type": "website",
            "source_format": doc.get("source_format", "html"),
            "source_identity": doc.get("source_identity", {}),
            "title": doc.get("title", ""),
            "h1": doc.get("h1", ""),
            "headings": doc.get("headings", []),
            "content_body": doc.get("content_body", ""),
            "structure": doc.get("structure", {}),
            "metadata": doc.get("metadata", {}),
        })

    for doc in upload_docs:
        docs.append({
            "schema_version": "universal_unified_content_document_v1",
            "pipeline_version": "automatic_rebuild_runner_v1",
            "workspace_id": workspace_id,
            "document_id": doc["document_id"],
            "source_type": "uploaded_document",
            "source_format": doc.get("source_format", ""),
            "source_identity": {
                "original_filename": doc.get("original_filename", ""),
                "stored_path": doc.get("stored_path", ""),
            },
            "title": doc.get("title", ""),
            "h1": doc.get("h1", ""),
            "headings": doc.get("headings", []),
            "content_body": doc.get("content_body", ""),
            "structure": doc.get("structure", {}),
            "metadata": doc.get("metadata", {}),
        })

    return {
        "schema_version": "uucd_collection_v1",
        "pipeline_version": "automatic_rebuild_runner_v1",
        "workspace_id": workspace_id,
        "documents": docs,
    }


def run_automatic_canonical_rebuild(workspace_id: str) -> Dict[str, Any]:
    UDUC_DIR.mkdir(parents=True, exist_ok=True)
    UUCD_DIR.mkdir(parents=True, exist_ok=True)

    upload_docs = collect_uploaded_documents(workspace_id)
    website_docs = collect_website_documents(workspace_id)

    # Remove internal metadata/index files before creating jobs.
    upload_docs = [
        d for d in upload_docs
        if str(d.get("document_id") or "").lower() not in {"index", "work_index"}
        and str(d.get("filename") or "").lower() not in {"index.json", "work_index.json"}
        and str(d.get("title") or "").lower() not in {"index", "work index"}
        and "__test" not in str(d.get("document_id") or "").lower()
        and "__test2" not in str(d.get("document_id") or "").lower()
        and "__wrap_test" not in str(d.get("document_id") or "").lower()
        and "__tmp_upload_test" not in str(d.get("document_id") or "").lower()
        and "__ui_store_test" not in str(d.get("document_id") or "").lower()
    ]

    upload_job_results = create_and_run_jobs(workspace_id, upload_docs, "uploaded_document")
    website_job_results = create_and_run_jobs(workspace_id, website_docs, "website")

    # Skip internal metadata/index files. They are not user documents.
    upload_docs = [
        d for d in upload_docs
        if str(d.get("document_id") or "").lower() not in {"index", "work_index"}
        and not str(d.get("filename") or "").lower() in {"index.json", "work_index.json"}
        and not str(d.get("title") or "").lower() in {"index", "work index"}
    ]

    for doc in upload_docs:
        write_json(UDUC_DIR / workspace_id / f"{doc['document_id']}.json", doc)

    uucd_payload = build_uucd_collection(workspace_id, upload_docs, website_docs)
    uucd_path = write_json(UUCD_DIR / f"universal_unified_content_documents_{workspace_id}.json", uucd_payload)

    body_result = build_universal_article_body_store_from_uucd_payload_v2(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
    )

    lifecycle_registry = {
        "schema_version": "source_lifecycle_control_v1",
        "workspace_id": workspace_id,
        "sources": {},
        "events": [],
    }

    asset_registry = {
        "schema_version": "source_asset_versions_v1",
        "workspace_id": workspace_id,
        "assets": [
            {"asset_id": f"asset_{d['document_id']}", "document_id": d["document_id"]}
            for d in uucd_payload["documents"]
        ],
    }

    authorization_payload = {
        "schema_version": "source_authorization_v1",
        "workspace_id": workspace_id,
        "counts": {
            "unauthorized_documents_quarantined": 0,
        },
    }

    cert_result = certify_uucd_body_store_v1(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
        body_index=body_result["index"],
        lifecycle_registry=lifecycle_registry,
        asset_version_registry=asset_registry,
        authorization_payload=authorization_payload,
    )

    report = {
        "ok": True,
        "workspace_id": workspace_id,
        "uploaded_documents_found": len(upload_docs),
        "website_documents_found": len(website_docs),
        "total_uucd_documents": len(uucd_payload["documents"]),
        "upload_jobs_run": len(upload_job_results),
        "website_jobs_run": len(website_job_results),
        "uucd_path": str(uucd_path),
        "body_index_path": body_result.get("body_index_path"),
        "bodies_written": body_result.get("bodies_written"),
        "certification_path": cert_result.get("certification_path"),
        "certified": cert_result.get("certification", {}).get("certified"),
        "semantic_ready": cert_result.get("certification", {}).get("semantic_ready"),
    }

    write_json(ROOT / "runtime" / "automatic_rebuild_reports" / workspace_id / "automatic_canonical_rebuild_report.json", report)

    return report


if __name__ == "__main__":
    workspace_id = "ws_whattoexpect_com"
    result = run_automatic_canonical_rebuild(workspace_id)

    print("AUTOMATIC CANONICAL REBUILD COMPLETE")
    print("Workspace:", result["workspace_id"])
    print("Uploaded documents found:", result["uploaded_documents_found"])
    print("Website documents found:", result["website_documents_found"])
    print("Total UUCD documents:", result["total_uucd_documents"])
    print("Bodies written:", result["bodies_written"])
    print("Certified:", result["certified"])
    print("Semantic ready:", result["semantic_ready"])
    print("UUCD path:", result["uucd_path"])
    print("Body index:", result["body_index_path"])
    print("Certification:", result["certification_path"])
