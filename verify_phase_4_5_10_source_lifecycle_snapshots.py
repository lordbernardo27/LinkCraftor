import json
from pathlib import Path
from collections import Counter


WORKSPACE_ID = "ws_whattoexpect_com"

UUCD_PATH = Path(
    "backend/server/data/universal_unified_content_documents/"
    f"universal_unified_content_documents_{WORKSPACE_ID}.json"
)

REGISTRY_PATH = Path(
    "backend/server/data/source_lifecycle_registry/"
    f"source_lifecycle_registry_{WORKSPACE_ID}.json"
)


def fail(msg):
    raise AssertionError(msg)


def main():
    if not UUCD_PATH.exists():
        fail(f"UUCD store missing: {UUCD_PATH}")

    if not REGISTRY_PATH.exists():
        fail(f"Source lifecycle registry missing: {REGISTRY_PATH}")

    uucd = json.loads(UUCD_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    docs = uucd.get("documents", [])
    sources = registry.get("sources", [])

    if not docs:
        fail("UUCD has zero documents")

    if not sources:
        fail("Lifecycle registry has zero sources")

    required_source_fields = [
        "source_id",
        "workspace_id",
        "source_type",
        "connection_status",
        "uucd_status",
        "learning_status",
        "latest_snapshot_id",
        "latest_snapshot_hash",
        "document_count",
        "document_ids",
        "policy",
        "events",
    ]

    missing = []
    for source in sources:
        for field in required_source_fields:
            if field not in source or source.get(field) in ("", None, []):
                missing.append((source.get("source_id"), field))

    if missing:
        fail(f"Sources missing required fields: {missing[:20]}")

    bad_workspace = [
        s.get("source_id") for s in sources
        if s.get("workspace_id") != WORKSPACE_ID
    ]
    if bad_workspace:
        fail(f"Sources with wrong workspace_id: {bad_workspace[:20]}")

    source_ids = [s.get("source_id") for s in sources]
    duplicate_source_ids = [
        sid for sid, count in Counter(source_ids).items()
        if count > 1
    ]
    if duplicate_source_ids:
        fail(f"Duplicate source_id values: {duplicate_source_ids[:20]}")

    allowed_connection = {"active", "disconnected", "deleted_from_editor", "purged"}
    allowed_uucd = {"retained", "superseded", "removed"}
    allowed_learning = {"usable", "frozen", "purged"}

    for source in sources:
        if source.get("connection_status") not in allowed_connection:
            fail(f"Bad connection_status: {source}")
        if source.get("uucd_status") not in allowed_uucd:
            fail(f"Bad uucd_status: {source}")
        if source.get("learning_status") not in allowed_learning:
            fail(f"Bad learning_status: {source}")

    tracked_doc_ids = set()
    for source in sources:
        tracked_doc_ids.update(source.get("document_ids", []))

    uucd_doc_ids = {d.get("document_id") for d in docs}

    missing_from_registry = uucd_doc_ids - tracked_doc_ids
    if missing_from_registry:
        fail(f"UUCD documents not tracked in lifecycle registry: {list(missing_from_registry)[:20]}")

    print("PHASE 4.5.10 SOURCE LIFECYCLE SNAPSHOT VERIFICATION PASSED")
    print("registry_path =", REGISTRY_PATH)
    print("sources =", len(sources))
    print("documents_tracked =", len(tracked_doc_ids))
    print("uucd_documents =", len(uucd_doc_ids))
    print("registry_counts =", registry.get("counts", {}))
    print("rules =", registry.get("rules", {}))


if __name__ == "__main__":
    main()
