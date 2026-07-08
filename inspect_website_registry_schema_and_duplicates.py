from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict

ROOT = Path("backend/server/data")
WORKSPACE_ID = "ws_whattoexpect_com"

FILES = [
    ROOT / "website_unified_content" / f"website_unified_content_{WORKSPACE_ID}.json",
    ROOT / "clean_website_html" / f"clean_website_html_{WORKSPACE_ID}.json",
    ROOT / "raw_website_html" / f"raw_website_html_{WORKSPACE_ID}.json",
    ROOT / "site_pages_ws_whattoexpect_com.json",
    ROOT / "site_sources_ws_whattoexpect_com.json",
]

BODY_INDEX = ROOT / "universal_article_body_store" / WORKSPACE_ID / f"universal_article_body_index_{WORKSPACE_ID}.json"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e)}


def summarize_payload(payload):
    print("Payload type:", type(payload).__name__)

    if isinstance(payload, dict):
        print("Top-level keys:", list(payload.keys())[:50])

        for key, value in payload.items():
            if isinstance(value, list):
                print(f"LIST KEY: {key} | length={len(value)}")
                if value and isinstance(value[0], dict):
                    print(f"  first item keys: {list(value[0].keys())[:50]}")
                break

        dict_keys = [k for k, v in payload.items() if isinstance(v, dict)]
        print("Dict-valued keys sample:", dict_keys[:20])

        if dict_keys:
            sample_key = dict_keys[0]
            sample_val = payload[sample_key]
            print(f"First dict key: {sample_key}")
            print("First dict value keys:", list(sample_val.keys())[:50] if isinstance(sample_val, dict) else None)

    elif isinstance(payload, list):
        print("List length:", len(payload))
        if payload and isinstance(payload[0], dict):
            print("First item keys:", list(payload[0].keys())[:50])


def inspect_duplicates():
    payload = read_json(BODY_INDEX)
    bodies = payload.get("bodies", []) if isinstance(payload, dict) else []

    hashes = defaultdict(list)

    for b in bodies:
        h = b.get("content_hash")
        if h:
            hashes[h].append({
                "document_id": b.get("document_id"),
                "source_type": b.get("source_type"),
                "title": b.get("title"),
                "body_ref": b.get("body_ref"),
            })

    dupes = {h: rows for h, rows in hashes.items() if len(rows) > 1}

    print("\nDUPLICATE BODY HASHES")
    print("=" * 70)
    print("Duplicate groups:", len(dupes))

    for h, rows in list(dupes.items())[:10]:
        print("\nHASH:", h)
        for row in rows:
            print(row)


def main():
    print("WEBSITE REGISTRY SCHEMA INSPECTION")
    print("=" * 70)

    for path in FILES:
        print("\nFILE:", path)
        print("-" * 70)
        print("Exists:", path.exists())
        if not path.exists():
            continue
        print("Size:", path.stat().st_size)
        payload = read_json(path)
        summarize_payload(payload)

    inspect_duplicates()


if __name__ == "__main__":
    main()
