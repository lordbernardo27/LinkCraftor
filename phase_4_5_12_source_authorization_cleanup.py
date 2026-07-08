import json
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ID = "ws_whattoexpect_com"
ALLOWED_WEBSITE_DOMAINS = {"whattoexpect.com"}

ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"
QUARANTINE_DIR = ROOT / "_quarantine/unauthorized_uucd_sources"
QUARANTINE_PATH = QUARANTINE_DIR / f"unauthorized_sources_{WORKSPACE_ID}.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def domain_from_url(url):
    if not url:
        return None
    value = url.lower().strip()
    value = value.replace("https://", "").replace("http://", "")
    return value.split("/")[0].replace("www.", "")

def is_authorized(doc):
    source_type = doc.get("source_type")

    if source_type == "uploaded_document":
        return True

    if source_type == "crawled_web_page":
        domain = domain_from_url(doc.get("canonical_url")) or str(doc.get("source_name", "")).lower()
        return domain in ALLOWED_WEBSITE_DOMAINS

    return False

def main():
    if not UUCD_PATH.exists():
        raise FileNotFoundError(f"Missing UUCD store: {UUCD_PATH}")

    data = read_json(UUCD_PATH)
    docs = data.get("documents", [])

    kept = []
    removed = []

    for doc in docs:
        if is_authorized(doc):
            kept.append(doc)
        else:
            removed.append(doc)

    if removed:
        write_json(QUARANTINE_PATH, {
            "schema_version": "unauthorized_uucd_quarantine.v1",
            "workspace_id": WORKSPACE_ID,
            "quarantined_at": now_iso(),
            "reason": "Document source is not authorized for this workspace.",
            "allowed_website_domains": sorted(ALLOWED_WEBSITE_DOMAINS),
            "removed_count": len(removed),
            "documents": removed,
        })

    data["documents"] = kept
    data["generated_at"] = now_iso()
    data["counts"]["documents_after_dedupe"] = len(kept)
    data["counts"]["website_documents"] = sum(1 for d in kept if d.get("source_type") == "crawled_web_page")
    data["counts"]["uploaded_documents"] = sum(1 for d in kept if d.get("source_type") == "uploaded_document")
    data["counts"]["unauthorized_documents_quarantined"] = len(removed)
    data["source_authorization"] = {
        "enabled": True,
        "allowed_website_domains": sorted(ALLOWED_WEBSITE_DOMAINS),
        "uploaded_documents_allowed": True,
        "unauthorized_documents_quarantined": len(removed),
        "quarantine_path": str(QUARANTINE_PATH) if removed else None
    }

    write_json(UUCD_PATH, data)

    print("PHASE 4.5.12 SOURCE AUTHORIZATION CLEANUP COMPLETE")
    print("kept_documents =", len(kept))
    print("removed_unauthorized_documents =", len(removed))
    print("website_documents =", data["counts"]["website_documents"])
    print("uploaded_documents =", data["counts"]["uploaded_documents"])
    print("quarantine_path =", QUARANTINE_PATH if removed else None)

if __name__ == "__main__":
    main()
