import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


WORKSPACE_ID = "ws_whattoexpect_com"

ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data" / "universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
LIFECYCLE_PATH = ROOT / "data" / "source_lifecycle_registry" / f"source_lifecycle_registry_{WORKSPACE_ID}.json"

OUT_DIR = ROOT / "data" / "source_asset_versions"
OUT_PATH = OUT_DIR / f"source_asset_versions_{WORKSPACE_ID}.json"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def stable_hash(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def main():
    if not UUCD_PATH.exists():
        raise FileNotFoundError(f"Missing UUCD store: {UUCD_PATH}")

    if not LIFECYCLE_PATH.exists():
        raise FileNotFoundError(f"Missing lifecycle registry: {LIFECYCLE_PATH}")

    uucd = read_json(UUCD_PATH)
    lifecycle = read_json(LIFECYCLE_PATH)

    docs_by_id = {
        d.get("document_id"): d
        for d in uucd.get("documents", [])
        if d.get("document_id")
    }

    assets = []

    for source in lifecycle.get("sources", []):
        document_ids = source.get("document_ids", [])
        source_docs = [docs_by_id[d] for d in document_ids if d in docs_by_id]

        document_fingerprints = []
        for doc in source_docs:
            content_hash = doc.get("metadata", {}).get("content_hash") or stable_hash(doc.get("text", ""))
            document_fingerprints.append({
                "document_id": doc.get("document_id"),
                "title": doc.get("title"),
                "canonical_url": doc.get("canonical_url"),
                "content_hash": content_hash,
                "text_length": len(doc.get("text", "") or ""),
                "source_type": doc.get("source_type")
            })

        version_basis = json.dumps(document_fingerprints, sort_keys=True, ensure_ascii=False)
        version_hash = stable_hash(version_basis)
        snapshot_id = f"snapshot_{version_hash[:24]}"

        asset = {
            "asset_id": f"asset_{source.get('source_id')}",
            "source_id": source.get("source_id"),
            "workspace_id": WORKSPACE_ID,

            "source_type": source.get("source_type"),
            "lifecycle_type": source.get("lifecycle_type"),
            "source_name": source.get("source_name"),

            "connection_status": source.get("connection_status"),
            "uucd_status": source.get("uucd_status"),
            "learning_status": source.get("learning_status"),

            "current_version": 1,
            "current_snapshot_id": snapshot_id,
            "current_snapshot_hash": version_hash,

            "snapshots": [
                {
                    "snapshot_id": snapshot_id,
                    "version": 1,
                    "snapshot_hash": version_hash,
                    "created_at": now_iso(),
                    "status": "current",
                    "change_type": "initial_snapshot",
                    "document_count": len(source_docs),
                    "document_fingerprints": document_fingerprints,
                    "change_summary": {
                        "added_documents": len(source_docs),
                        "removed_documents": 0,
                        "changed_documents": 0,
                        "unchanged_documents": 0
                    }
                }
            ],

            "version_policy": {
                "on_reconnect": "compare_current_source_against_latest_snapshot",
                "on_upload_new_version": "create_new_snapshot_and_compare_document_hashes",
                "on_editor_delete": "keep_asset_and_snapshot_mark_source_deleted_from_editor",
                "on_disconnect": "keep_asset_and_snapshot_mark_source_disconnected",
                "on_explicit_purge": "remove_asset_snapshots_uucd_documents_and_semantic_learning",
                "semantic_reprocessing": "only_reprocess_new_or_changed_documents"
            },

            "events": [
                {
                    "event_type": "asset_version_registry_created",
                    "event_at": now_iso(),
                    "snapshot_id": snapshot_id,
                    "version": 1,
                    "reason": "Initial source asset version registry generated from lifecycle registry and canonical UUCD store."
                }
            ]
        }

        assets.append(asset)

    payload = {
        "schema_version": "source_asset_versions.v1",
        "workspace_id": WORKSPACE_ID,
        "registry_type": "source_asset_version_registry",
        "generated_at": now_iso(),
        "inputs": {
            "uucd_path": str(UUCD_PATH),
            "lifecycle_registry_path": str(LIFECYCLE_PATH)
        },
        "counts": {
            "assets": len(assets),
            "snapshots": sum(len(a.get("snapshots", [])) for a in assets),
            "documents_tracked": sum(
                s.get("document_count", 0)
                for a in assets
                for s in a.get("snapshots", [])
                if s.get("status") == "current"
            ),
            "website_assets": sum(1 for a in assets if a.get("source_type") == "crawled_web_page"),
            "uploaded_document_assets": sum(1 for a in assets if a.get("source_type") == "uploaded_document"),
        },
        "rules": {
            "sources_are_versioned_assets": True,
            "snapshots_are_immutable": True,
            "current_snapshot_is_explicit": True,
            "changed_documents_are_detected_by_hash": True,
            "semantic_pipeline_should_process_only_current_usable_snapshots": True,
            "old_snapshots_can_be_used_for_comparison_or_rollback": True
        },
        "assets": assets
    }

    write_json(OUT_PATH, payload)

    print("SOURCE ASSET VERSION REGISTRY BUILT")
    print("asset_registry_path =", OUT_PATH)
    print("assets =", payload["counts"]["assets"])
    print("snapshots =", payload["counts"]["snapshots"])
    print("documents_tracked =", payload["counts"]["documents_tracked"])
    print("website_assets =", payload["counts"]["website_assets"])
    print("uploaded_document_assets =", payload["counts"]["uploaded_document_assets"])


if __name__ == "__main__":
    main()
