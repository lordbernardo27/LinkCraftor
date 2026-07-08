import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


WORKSPACE_ID = "ws_whattoexpect_com"

ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data" / "universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"

OUT_DIR = ROOT / "data" / "source_lifecycle_registry"
OUT_PATH = OUT_DIR / f"source_lifecycle_registry_{WORKSPACE_ID}.json"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def stable_hash(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def normalize_domain(url: str):
    if not url:
        return None
    value = url.lower().strip()
    value = value.replace("https://", "").replace("http://", "")
    return value.split("/")[0].replace("www.", "")


def source_id_for_doc(doc):
    source_type = doc.get("source_type")

    if source_type == "crawled_web_page":
        domain = normalize_domain(doc.get("canonical_url")) or doc.get("source_name") or "unknown_domain"
        return f"source_website_{stable_hash(domain)[:16]}"

    if source_type == "uploaded_document":
        basis = doc.get("source_name") or doc.get("title") or doc.get("document_id")
        return f"source_upload_{stable_hash(basis)[:16]}"

    basis = doc.get("source_name") or doc.get("document_id") or "unknown"
    return f"source_unknown_{stable_hash(basis)[:16]}"


def source_name_for_doc(doc):
    if doc.get("source_type") == "crawled_web_page":
        return normalize_domain(doc.get("canonical_url")) or doc.get("source_name") or "unknown website"
    return doc.get("source_name") or doc.get("title") or "unknown uploaded document"


def build_registry():
    if not UUCD_PATH.exists():
        raise FileNotFoundError(f"UUCD store missing: {UUCD_PATH}")

    uucd = read_json(UUCD_PATH)
    docs = uucd.get("documents", [])

    grouped = defaultdict(list)

    for doc in docs:
        sid = source_id_for_doc(doc)
        grouped[sid].append(doc)

    sources = []

    for source_id, source_docs in sorted(grouped.items()):
        first = source_docs[0]
        source_type = first.get("source_type")

        if source_type == "crawled_web_page":
            lifecycle_type = "website_connection"
            connection_status = "active"
        elif source_type == "uploaded_document":
            lifecycle_type = "uploaded_document"
            connection_status = "active"
        else:
            lifecycle_type = "unknown"
            connection_status = "active"

        content_hashes = [
            d.get("metadata", {}).get("content_hash") or stable_hash(d.get("text", ""))
            for d in source_docs
        ]

        snapshot_hash = stable_hash("|".join(sorted(content_hashes)))

        sources.append({
            "source_id": source_id,
            "workspace_id": WORKSPACE_ID,
            "source_type": source_type,
            "lifecycle_type": lifecycle_type,
            "source_name": source_name_for_doc(first),

            "connection_status": connection_status,
            "uucd_status": "retained",
            "learning_status": "usable",

            "latest_snapshot_id": f"snapshot_{snapshot_hash[:24]}",
            "latest_snapshot_hash": snapshot_hash,
            "latest_snapshot_at": now_iso(),

            "document_count": len(source_docs),
            "document_ids": [d.get("document_id") for d in source_docs],

            "policy": {
                "disconnect_behavior": "stop_future_sync_keep_processed_snapshot",
                "editor_delete_behavior": "remove_from_editor_keep_processed_snapshot",
                "update_behavior": "create_new_snapshot_compare_changes",
                "purge_behavior": "delete_uucd_and_semantic_learning_only_when_explicitly_requested"
            },

            "events": [
                {
                    "event_type": "snapshot_created",
                    "event_at": now_iso(),
                    "reason": "Initial lifecycle registry generated from canonical UUCD store.",
                    "snapshot_id": f"snapshot_{snapshot_hash[:24]}",
                    "document_count": len(source_docs)
                }
            ]
        })

    payload = {
        "schema_version": "source_lifecycle_registry.v1",
        "workspace_id": WORKSPACE_ID,
        "registry_type": "source_lifecycle_and_knowledge_snapshots",
        "generated_at": now_iso(),
        "uucd_path": str(UUCD_PATH),
        "counts": {
            "sources": len(sources),
            "documents_tracked": sum(s["document_count"] for s in sources),
            "website_sources": sum(1 for s in sources if s["source_type"] == "crawled_web_page"),
            "uploaded_document_sources": sum(1 for s in sources if s["source_type"] == "uploaded_document"),
        },
        "rules": {
            "disconnect_does_not_delete_knowledge": True,
            "editor_delete_does_not_delete_knowledge": True,
            "updates_create_new_snapshots": True,
            "permanent_delete_requires_explicit_purge": True
        },
        "sources": sources
    }

    write_json(OUT_PATH, payload)

    print("SOURCE LIFECYCLE SNAPSHOT REGISTRY BUILT")
    print("registry_path =", OUT_PATH)
    print("sources =", payload["counts"]["sources"])
    print("documents_tracked =", payload["counts"]["documents_tracked"])
    print("website_sources =", payload["counts"]["website_sources"])
    print("uploaded_document_sources =", payload["counts"]["uploaded_document_sources"])


if __name__ == "__main__":
    build_registry()
