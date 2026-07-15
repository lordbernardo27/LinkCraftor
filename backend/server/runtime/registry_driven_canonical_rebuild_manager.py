from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from backend.server.jobs.universal_knowledge_orchestrator import create_universal_knowledge_job
from backend.server.stores.universal_article_body_store import build_universal_article_body_store_from_uucd_payload_v2
from backend.server.stores.uucd_body_store_certification import certify_uucd_body_store_v1
from backend.server.workers.universal_knowledge_worker import execute_universal_knowledge_job_v1


ROOT = Path("backend/server/data")
UUCD_DIR = ROOT / "universal_unified_content_documents"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def safe_id(value: str, fallback: str = "doc") -> str:
    raw = str(value or fallback).strip() or fallback
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in raw)[:140]


def body_value(row: Dict[str, Any]) -> str:
    return str(
        row.get("content_body")
        or row.get("body_text")
        or row.get("article_text")
        or row.get("text")
        or row.get("content")
        or row.get("body")
        or ""
    ).strip()


def extract_rows(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ["documents", "items", "pages", "records", "articles", "bodies"]:
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]

        # Common dict-of-records format
        dict_rows = []
        for v in payload.values():
            if isinstance(v, dict):
                dict_rows.append(v)
        if dict_rows:
            return dict_rows

        if payload:
            return [payload]

    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]

    return []


def normalize_website_doc(row: Dict[str, Any], workspace_id: str, index: int) -> Dict[str, Any] | None:
    text = body_value(row)
    if not text:
        return None

    url = (
        row.get("canonical_url")
        or row.get("url")
        or row.get("source_url")
        or row.get("page_url")
        or row.get("href")
        or ""
    )

    raw_id = (
        row.get("document_id")
        or row.get("doc_id")
        or row.get("page_id")
        or row.get("id")
        or url
        or f"website_doc_{index}"
    )

    doc_id = safe_id(str(raw_id), f"website_doc_{index}")

    return {
        "schema_version": "universal_unified_content_document_v1",
        "pipeline_version": "registry_driven_rebuild_manager_v1",
        "workspace_id": workspace_id,
        "document_id": doc_id,
        "source_type": "website",
        "source_format": "html",
        "source_identity": {
            "canonical_url": url,
            "source": "website_registry",
        },
        "title": row.get("title") or row.get("page_title") or row.get("h1") or doc_id,
        "h1": row.get("h1") or "",
        "headings": row.get("headings") or [],
        "canonical_url": url,
        "content_body": text,
        "structure": row.get("structure") or {},
        "metadata": {
            **(row.get("metadata") or {}),
            "registry_rebuild": True,
            "source_registry": "website",
        },
    }


def normalize_upload_doc(row: Dict[str, Any], workspace_id: str, index: int) -> Dict[str, Any] | None:
    text = body_value(row)
    if not text:
        return None

    filename = (
        row.get("filename")
        or row.get("original_filename")
        or row.get("name")
        or row.get("title")
        or f"upload_doc_{index}"
    )

    raw_id = (
        row.get("document_id")
        or row.get("doc_id")
        or row.get("id")
        or filename
        or f"upload_doc_{index}"
    )

    doc_id = safe_id(str(raw_id), f"upload_doc_{index}")

    forbidden_names = {"index", "work_index"}
    if doc_id.lower() in forbidden_names:
        return None

    return {
        "schema_version": "universal_unified_content_document_v1",
        "pipeline_version": "registry_driven_rebuild_manager_v1",
        "workspace_id": workspace_id,
        "document_id": doc_id,
        "source_type": "uploaded_document",
        "source_format": str(row.get("source_format") or row.get("extension") or Path(str(filename)).suffix.lower().lstrip(".") or "unknown"),
        "source_identity": {
            "original_filename": filename,
            "source": "upload_registry",
        },
        "title": row.get("title") or Path(str(filename)).stem,
        "h1": row.get("h1") or "",
        "headings": row.get("headings") or [],
        "content_body": text,
        "structure": row.get("structure") or {},
        "metadata": {
            **(row.get("metadata") or {}),
            "registry_rebuild": True,
            "source_registry": "upload",
        },
    }


def collect_website_registry_docs(workspace_id: str) -> List[Dict[str, Any]]:
    candidates = [
        ROOT / "website_unified_content" / f"website_unified_content_{workspace_id}.json",
        ROOT / "raw_website_html" / f"raw_website_html_{workspace_id}.json",
        ROOT / "raw_website_html" / f"raw_website_html_{workspace_id}.json",
    ]

    docs: List[Dict[str, Any]] = []
    seen_ids = set()

    for path in candidates:
        payload = read_json(path)
        if payload is None:
            continue

        rows = extract_rows(payload)
        for i, row in enumerate(rows, start=1):
            doc = normalize_website_doc(row, workspace_id, i)
            if not doc:
                continue
            if doc["document_id"] in seen_ids:
                continue
            seen_ids.add(doc["document_id"])
            docs.append(doc)

        if docs:
            break

    return docs


def collect_upload_registry_docs(workspace_id: str) -> List[Dict[str, Any]]:
    candidates = [
        ROOT / "workspaces" / workspace_id / "saved_sessions",
        ROOT / "uploaded_document_unified_content" / workspace_id,
        ROOT / "docs" / workspace_id,
    ]

    docs: List[Dict[str, Any]] = []
    seen_ids = set()

    for base in candidates:
        if not base.exists():
            continue

        files = []
        if base.is_file():
            files = [base]
        else:
            files = list(base.rglob("documents.json")) + list(base.rglob("*.json"))

        for path in files:
            if path.name.lower() in {"index.json", "work_index.json"}:
                continue

            payload = read_json(path)
            rows = extract_rows(payload)

            for i, row in enumerate(rows, start=1):
                doc = normalize_upload_doc(row, workspace_id, len(docs) + i)
                if not doc:
                    continue
                if doc["document_id"] in seen_ids:
                    continue
                seen_ids.add(doc["document_id"])
                docs.append(doc)

    return docs


def execute_rebuild_jobs(workspace_id: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for doc in docs:
        job_type = "article_extraction" if doc["source_type"] == "website" else "upload_document_extraction"
        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type=job_type,
            payload={
                "document_id": doc["document_id"],
                "source_type": doc["source_type"],
                "registry_rebuild": True,
            },
        )
        results.append(execute_universal_knowledge_job_v1(job))
    return results


def build_registry_driven_rebuild(workspace_id: str) -> Dict[str, Any]:
    website_docs = collect_website_registry_docs(workspace_id)
    upload_docs = collect_upload_registry_docs(workspace_id)

    all_docs = website_docs + upload_docs

    job_results = execute_rebuild_jobs(workspace_id, all_docs)

    uucd_payload = {
        "schema_version": "uucd_collection_v1",
        "pipeline_version": "registry_driven_rebuild_manager_v1",
        "workspace_id": workspace_id,
        "documents": all_docs,
    }

    uucd_path = write_json(
        UUCD_DIR / f"universal_unified_content_documents_{workspace_id}.json",
        uucd_payload,
    )

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
            {
                "asset_id": f"asset_{doc['document_id']}",
                "document_id": doc["document_id"],
                "source_type": doc["source_type"],
            }
            for doc in all_docs
        ],
    }

    authorization_payload = {
        "schema_version": "source_authorization_v1",
        "workspace_id": workspace_id,
        "counts": {"unauthorized_documents_quarantined": 0},
    }

    cert_result = certify_uucd_body_store_v1(
        workspace_id=workspace_id,
        uucd_payload=uucd_payload,
        body_index=body_result["index"],
        lifecycle_registry=lifecycle_registry,
        asset_version_registry=asset_registry,
        authorization_payload=authorization_payload,
    )

    cert = cert_result.get("certification", {})

    report = {
        "ok": True,
        "workspace_id": workspace_id,
        "website_documents_found": len(website_docs),
        "uploaded_documents_found": len(upload_docs),
        "total_uucd_documents": len(all_docs),
        "jobs_run": len(job_results),
        "bodies_written": body_result.get("bodies_written"),
        "duplicate_hashes": body_result.get("duplicate_hashes"),
        "certified": cert.get("certified"),
        "semantic_ready": cert.get("semantic_ready"),
        "certification_level": cert.get("certification_level"),
        "certification_problems": cert.get("problems", []),
        "uucd_path": str(uucd_path),
        "body_index_path": body_result.get("body_index_path"),
        "certification_path": cert_result.get("certification_path"),
    }

    write_json(
        ROOT / "runtime" / "automatic_rebuild_reports" / workspace_id / "registry_driven_rebuild_report.json",
        report,
    )

    return report


if __name__ == "__main__":
    workspace_id = "ws_whattoexpect_com"
    result = build_registry_driven_rebuild(workspace_id)

    print("REGISTRY-DRIVEN CANONICAL REBUILD COMPLETE")
    print("Workspace:", result["workspace_id"])
    print("Website documents found:", result["website_documents_found"])
    print("Uploaded documents found:", result["uploaded_documents_found"])
    print("Total UUCD documents:", result["total_uucd_documents"])
    print("Jobs run:", result["jobs_run"])
    print("Bodies written:", result["bodies_written"])
    print("Duplicate hashes:", result["duplicate_hashes"])
    print("Certified:", result["certified"])
    print("Semantic ready:", result["semantic_ready"])
    print("Certification level:", result["certification_level"])
    print("Problems:", result["certification_problems"][:10])
    print("UUCD path:", result["uucd_path"])
    print("Body index:", result["body_index_path"])
    print("Certification:", result["certification_path"])
