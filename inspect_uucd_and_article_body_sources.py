import json
from pathlib import Path
from collections import Counter

WORKSPACE_ID = "ws_whattoexpect_com"
ROOT = Path("backend/server")

UUCD_PATH = ROOT / "data/universal_unified_content_documents" / f"universal_unified_content_documents_{WORKSPACE_ID}.json"

BODY_KEYS = [
    "text",
    "content",
    "body",
    "article_body",
    "clean_text",
    "markdown",
    "raw_text",
    "extracted_text",
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def body_length(doc):
    best = ("", 0)
    for key in BODY_KEYS:
        value = doc.get(key)
        if isinstance(value, str) and len(value.strip()) > best[1]:
            best = (key, len(value.strip()))
    return best

def main():
    if not UUCD_PATH.exists():
        raise FileNotFoundError(f"Missing UUCD store: {UUCD_PATH}")

    data = read_json(UUCD_PATH)
    docs = data.get("documents", [])

    print("=" * 90)
    print("UUCD DEEP INSPECTION")
    print("=" * 90)

    print("uucd_path =", UUCD_PATH)
    print("schema_version =", data.get("schema_version"))
    print("workspace_id =", data.get("workspace_id"))
    print("canonical =", data.get("canonical"))
    print("total_documents =", len(docs))
    print("counts =", data.get("counts"))
    print("source_authorization =", data.get("source_authorization"))

    print("\nSOURCE COUNTS")
    print(dict(Counter(d.get("source_type") for d in docs)))

    print("\nBODY FIELD SCAN")
    found_by_key = Counter()
    empty_docs = []
    usable_docs = []

    for doc in docs:
        key, length = body_length(doc)
        if length > 0:
            found_by_key[key] += 1
            usable_docs.append((doc, key, length))
        else:
            empty_docs.append(doc)

    print("usable_body_documents =", len(usable_docs))
    print("empty_body_documents =", len(empty_docs))
    print("body_fields_found =", dict(found_by_key))

    print("\nEMPTY BODY COUNTS BY SOURCE TYPE")
    print(dict(Counter(d.get("source_type") for d in empty_docs)))

    print("\nUSABLE BODY COUNTS BY SOURCE TYPE")
    print(dict(Counter(d.get("source_type") for d, _, _ in usable_docs)))

    print("\nSAMPLE EMPTY DOCUMENTS")
    for d in empty_docs[:10]:
        print("-" * 60)
        print("document_id =", d.get("document_id"))
        print("source_type =", d.get("source_type"))
        print("source_name =", d.get("source_name"))
        print("title =", d.get("title"))
        print("canonical_url =", d.get("canonical_url"))
        print("metadata.migrated_from =", d.get("metadata", {}).get("migrated_from"))

    print("\nSAMPLE USABLE BODY DOCUMENTS")
    for d, key, length in usable_docs[:10]:
        print("-" * 60)
        print("document_id =", d.get("document_id"))
        print("source_type =", d.get("source_type"))
        print("source_name =", d.get("source_name"))
        print("title =", d.get("title"))
        print("body_key =", key)
        print("body_length =", length)

    print("\nDECISION")
    if empty_docs:
        print("UUCD has document records, but some article bodies are missing.")
    else:
        print("UUCD has article bodies for all documents.")

if __name__ == "__main__":
    main()
