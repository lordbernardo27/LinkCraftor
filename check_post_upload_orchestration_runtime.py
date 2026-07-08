from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server/data")

PATHS = {
    "job_ledger": ROOT / "jobs" / "universal_knowledge" / WORKSPACE_ID / f"job_ledger_{WORKSPACE_ID}.jsonl",
    "job_status_dir": ROOT / "job_status" / "universal_knowledge" / WORKSPACE_ID,
    "job_progress_dir": ROOT / "job_progress" / "universal_knowledge" / WORKSPACE_ID,
    "docs_dir": ROOT / "docs" / WORKSPACE_ID,
    "uduc_dir": ROOT / "uploaded_document_unified_content" / WORKSPACE_ID,
    "uucd": ROOT / "universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json",
    "body_index": ROOT / "universal_article_body_store" / WORKSPACE_ID / f"universal_article_body_index_{WORKSPACE_ID}.json",
    "body_dir": ROOT / "universal_article_body_store" / WORKSPACE_ID / "bodies",
    "cert": ROOT / "uucd_body_store_certifications" / WORKSPACE_ID / f"uucd_body_store_certification_{WORKSPACE_ID}.json",
}


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e), "__path__": str(path)}


def read_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"__raw__": line[:300]})
    return rows


def count_files(path: Path, suffixes=None):
    if not path.exists():
        return 0
    files = [p for p in path.rglob("*") if p.is_file()]
    if suffixes:
        files = [p for p in files if p.suffix.lower() in suffixes]
    return len(files)


def latest_files(path: Path, limit=10):
    if not path.exists():
        return []
    files = [p for p in path.rglob("*") if p.is_file()]
    files = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "path": str(p),
            "size": p.stat().st_size,
            "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
        }
        for p in files[:limit]
    ]


def body_text(doc):
    return str(
        doc.get("content_body")
        or doc.get("body_text")
        or doc.get("article_text")
        or doc.get("text")
        or ""
    ).strip()


def main():
    print("POST-UPLOAD ORCHESTRATION RUNTIME CHECK")
    print("=" * 70)
    print("Workspace:", WORKSPACE_ID)

    print("\n1. PATH EXISTENCE")
    print("-" * 70)
    for name, path in PATHS.items():
        print(f"{name}: exists={path.exists()} | {path}")

    print("\n2. LATEST UPLOADED DOC FILES")
    print("-" * 70)
    print("docs files:", count_files(PATHS["docs_dir"]))
    for row in latest_files(PATHS["docs_dir"], 10):
        print(row)

    print("\n3. JOB LEDGER")
    print("-" * 70)
    ledger = read_jsonl(PATHS["job_ledger"])
    print("ledger_exists:", PATHS["job_ledger"].exists())
    print("ledger_rows:", len(ledger))
    print("latest_10_jobs:")
    for row in ledger[-10:]:
        print({
            "job_id": row.get("job_id"),
            "job_type": row.get("job_type"),
            "status": row.get("status"),
            "trigger": (row.get("payload") or {}).get("trigger"),
            "document_id": (row.get("payload") or {}).get("document_id"),
            "filename": (row.get("payload") or {}).get("filename"),
            "created_at": row.get("created_at"),
        })

    print("\n4. JOB STATUS FILES")
    print("-" * 70)
    print("status_files:", count_files(PATHS["job_status_dir"], {".json"}))
    for row in latest_files(PATHS["job_status_dir"], 10):
        payload = read_json(Path(row["path"]), {})
        print({
            "path": row["path"],
            "job_id": payload.get("job_id"),
            "job_type": payload.get("job_type"),
            "status": payload.get("status"),
            "message": payload.get("message"),
            "updated_at": payload.get("updated_at"),
        })

    print("\n5. JOB PROGRESS FILES")
    print("-" * 70)
    print("progress_files:", count_files(PATHS["job_progress_dir"], {".json"}))
    for row in latest_files(PATHS["job_progress_dir"], 10):
        payload = read_json(Path(row["path"]), {})
        print({
            "path": row["path"],
            "job_id": payload.get("job_id"),
            "percent": payload.get("percent"),
            "message": payload.get("message"),
        })

    print("\n6. UDUC")
    print("-" * 70)
    print("uduc_files:", count_files(PATHS["uduc_dir"], {".json"}))
    for row in latest_files(PATHS["uduc_dir"], 10):
        payload = read_json(Path(row["path"]), {})
        print({
            "path": row["path"],
            "document_id": payload.get("document_id"),
            "source_type": payload.get("source_type"),
            "title": payload.get("title"),
            "content_body_length": len(str(payload.get("content_body") or "")),
        })

    print("\n7. UUCD")
    print("-" * 70)
    uucd = read_json(PATHS["uucd"], {}) or {}
    docs = uucd.get("documents") or []
    print("uucd_exists:", PATHS["uucd"].exists())
    print("uucd_document_count:", len(docs))
    print("uucd_docs_with_body:", sum(1 for d in docs if isinstance(d, dict) and body_text(d)))
    print("uucd_by_source_type:")
    counts = {}
    for d in docs:
        st = str(d.get("source_type") or "unknown")
        counts[st] = counts.get(st, 0) + 1
    print(counts)
    print("latest/sample docs:")
    for d in docs[-10:]:
        print({
            "document_id": d.get("document_id"),
            "source_type": d.get("source_type"),
            "title": d.get("title"),
            "content_body_length": len(body_text(d)),
            "content_ref": d.get("content_ref") or (d.get("metadata") or {}).get("content_ref"),
        })

    print("\n8. BODY STORE")
    print("-" * 70)
    body_index = read_json(PATHS["body_index"], {}) or {}
    bodies = body_index.get("bodies") or []
    print("body_index_exists:", PATHS["body_index"].exists())
    print("body_records:", len(bodies))
    print("body_files:", count_files(PATHS["body_dir"], {".txt"}))
    print("duplicate_hashes:", len(body_index.get("duplicate_hashes") or []))
    for b in bodies[-10:]:
        ref = Path(str(b.get("body_ref") or ""))
        print({
            "document_id": b.get("document_id"),
            "source_type": b.get("source_type"),
            "body_length": b.get("body_length"),
            "body_ref_exists": ref.exists(),
            "body_ref": str(ref),
        })

    print("\n9. CERTIFICATION")
    print("-" * 70)
    cert = read_json(PATHS["cert"], {}) or {}
    print("cert_exists:", PATHS["cert"].exists())
    print("certified:", cert.get("certified"))
    print("semantic_ready:", cert.get("semantic_ready"))
    print("certification_level:", cert.get("certification_level"))
    print("problems:", cert.get("problems", [])[:20])
    print("counts:", cert.get("counts"))

    print("\n10. DECISION")
    print("-" * 70)
    latest_upload_jobs = [
        r for r in ledger
        if (r.get("payload") or {}).get("trigger") == "live_upload_route"
        or r.get("job_type") == "upload_document_batch"
    ]
    print("live_upload_orchestration_jobs_found:", len(latest_upload_jobs))
    print("expected_after_3_uploads: at least 3 recent upload-triggered jobs")
    print("If jobs exist but UDUC/UUCD/Body Store did not change, the route is wired but worker stage is not doing real canonical writes yet.")


if __name__ == "__main__":
    main()
