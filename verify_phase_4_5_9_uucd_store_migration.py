import json
from pathlib import Path
from collections import Counter


WORKSPACE_ID = "ws_whattoexpect_com"

UUCD_PATH = Path(
    "backend/server/data/universal_unified_content_documents/"
    f"universal_unified_content_documents_{WORKSPACE_ID}.json"
)

OLD_UCD_PATH = Path(
    "backend/server/data/unified_content_documents/"
    f"unified_content_documents_{WORKSPACE_ID}.json"
)

QUARANTINE_PATH = Path(
    "backend/server/_quarantine/old_ucd_store/"
    f"unified_content_documents_{WORKSPACE_ID}.json"
)


def fail(msg):
    raise AssertionError(msg)


def main():
    if not UUCD_PATH.exists():
        fail(f"UUCD store missing: {UUCD_PATH}")

    payload = json.loads(UUCD_PATH.read_text(encoding="utf-8"))
    docs = payload.get("documents", [])

    if not isinstance(docs, list):
        fail("UUCD documents must be a list")

    if not docs:
        fail("UUCD store has zero documents")

    required = ["document_id", "schema_version", "workspace_id", "source_type", "title", "metadata"]

    missing = []
    for idx, doc in enumerate(docs):
        for field in required:
            if field not in doc or doc.get(field) in ("", None):
                missing.append((idx, field, doc.get("title")))

    if missing:
        fail(f"Documents missing required fields: {missing[:20]}")

    bad_workspace = [d.get("document_id") for d in docs if d.get("workspace_id") != WORKSPACE_ID]
    if bad_workspace:
        fail(f"Documents with wrong workspace_id: {bad_workspace[:20]}")

    ids = [d.get("document_id") for d in docs]
    duplicate_ids = [doc_id for doc_id, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        fail(f"Duplicate document_id values found: {duplicate_ids[:20]}")

    urls = [
        (d.get("source_type"), d.get("canonical_url"))
        for d in docs
        if d.get("canonical_url")
    ]
    duplicate_urls = [
        key for key, count in Counter(urls).items()
        if count > 1
    ]
    if duplicate_urls:
        fail(f"Duplicate canonical URLs found: {duplicate_urls[:20]}")

    source_counts = Counter(d.get("source_type") for d in docs)

    if OLD_UCD_PATH.exists() and not QUARANTINE_PATH.exists():
        fail("Old UCD store still exists but no quarantine copy was created")

    print("PHASE 4.5.9 UUCD MIGRATION VERIFICATION PASSED")
    print("uucd_path =", UUCD_PATH)
    print("total_documents =", len(docs))
    print("source_counts =", dict(source_counts))
    print("duplicates_removed =", payload.get("counts", {}).get("duplicates_removed"))
    print("old_ucd_exists =", OLD_UCD_PATH.exists())
    print("old_ucd_quarantine_copy_exists =", QUARANTINE_PATH.exists())


if __name__ == "__main__":
    main()
