import json
from pathlib import Path
from collections import Counter

WORKSPACE_ID = "ws_whattoexpect_com"

ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
LIFECYCLE_PATH = ROOT / "data/source_lifecycle_registry" / f"source_lifecycle_registry_{WORKSPACE_ID}.json"
ASSET_PATH = ROOT / "data/source_asset_versions" / f"source_asset_versions_{WORKSPACE_ID}.json"

def load(path):
    if not path.exists():
        print("MISSING:", path)
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def text_stats(docs):
    lengths = [len(d.get("text", "") or "") for d in docs]
    empty = [d for d in docs if not (d.get("text", "") or "").strip()]
    short = [d for d in docs if 0 < len(d.get("text", "") or "") < 300]

    return {
        "min_text_length": min(lengths) if lengths else 0,
        "max_text_length": max(lengths) if lengths else 0,
        "empty_text_documents": len(empty),
        "short_text_documents_under_300_chars": len(short),
    }

def main():
    print("=" * 90)
    print("PHASE 4.6 READINESS SCAN")
    print("=" * 90)

    uucd = load(UUCD_PATH)
    lifecycle = load(LIFECYCLE_PATH)
    assets = load(ASSET_PATH)

    if not uucd:
        return

    docs = uucd.get("documents", [])

    print("\n[1] UUCD STORE")
    print("path =", UUCD_PATH)
    print("schema_version =", uucd.get("schema_version"))
    print("workspace_id =", uucd.get("workspace_id"))
    print("canonical =", uucd.get("canonical"))
    print("total_documents =", len(docs))
    print("counts =", uucd.get("counts"))
    print("source_authorization =", uucd.get("source_authorization"))

    print("\n[2] UUCD SOURCE COUNTS")
    print(dict(Counter(d.get("source_type") for d in docs)))

    print("\n[3] TEXT BODY READINESS")
    stats = text_stats(docs)
    print(stats)

    print("\n[4] SAMPLE WEBSITE DOCUMENTS")
    website_docs = [d for d in docs if d.get("source_type") == "crawled_web_page"]
    for d in website_docs[:3]:
        print("-" * 60)
        print("document_id =", d.get("document_id"))
        print("title =", d.get("title"))
        print("canonical_url =", d.get("canonical_url"))
        print("text_length =", len(d.get("text", "") or ""))

    print("\n[5] SAMPLE UPLOADED DOCUMENTS")
    upload_docs = [d for d in docs if d.get("source_type") == "uploaded_document"]
    for d in upload_docs[:8]:
        print("-" * 60)
        print("document_id =", d.get("document_id"))
        print("source_name =", d.get("source_name"))
        print("title =", d.get("title"))
        print("text_length =", len(d.get("text", "") or ""))

    if lifecycle:
        print("\n[6] SOURCE LIFECYCLE REGISTRY")
        print("path =", LIFECYCLE_PATH)
        print("schema_version =", lifecycle.get("schema_version"))
        print("counts =", lifecycle.get("counts"))
        print("rules =", lifecycle.get("rules"))

        print("\n[7] LIFECYCLE SOURCES")
        for s in lifecycle.get("sources", []):
            print("-" * 60)
            print("source_id =", s.get("source_id"))
            print("source_name =", s.get("source_name"))
            print("source_type =", s.get("source_type"))
            print("document_count =", s.get("document_count"))
            print("connection_status =", s.get("connection_status"))
            print("uucd_status =", s.get("uucd_status"))
            print("learning_status =", s.get("learning_status"))

    if assets:
        print("\n[8] SOURCE ASSET VERSION REGISTRY")
        print("path =", ASSET_PATH)
        print("schema_version =", assets.get("schema_version"))
        print("counts =", assets.get("counts"))
        print("rules =", assets.get("rules"))

        print("\n[9] VERSIONED ASSETS")
        for a in assets.get("assets", []):
            print("-" * 60)
            print("asset_id =", a.get("asset_id"))
            print("source_name =", a.get("source_name"))
            print("source_type =", a.get("source_type"))
            print("current_version =", a.get("current_version"))
            print("current_snapshot_id =", a.get("current_snapshot_id"))
            print("snapshots =", len(a.get("snapshots", [])))

    print("\n[10] READINESS DECISION")
    problems = []

    if uucd.get("canonical") is not True:
        problems.append("UUCD is not marked canonical")

    if not docs:
        problems.append("UUCD has zero documents")

    if stats["empty_text_documents"] > 0:
        problems.append(f"{stats['empty_text_documents']} documents have empty text")

    if lifecycle and lifecycle.get("counts", {}).get("documents_tracked") != len(docs):
        problems.append("Lifecycle registry document count does not match UUCD")

    if assets and assets.get("counts", {}).get("documents_tracked") != len(docs):
        problems.append("Asset registry document count does not match UUCD")

    if problems:
        print("NOT READY")
        for p in problems:
            print("-", p)
    else:
        print("READY FOR PHASE 4.6.1 — SEMANTIC ARTICLE READER")

if __name__ == "__main__":
    main()
