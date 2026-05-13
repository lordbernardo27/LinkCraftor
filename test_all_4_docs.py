import json
import requests
from pathlib import Path

ws = "ws_betterhealthcheck_com"
url = "http://127.0.0.1:8001/api/engine/run"

data = json.loads(
    Path("backend/server/data/upload_struct_ws_betterhealthcheck_com.json")
    .read_text(encoding="utf-8")
)

for doc_id, doc in data.get("docs", {}).items():
    article = " ".join(
        p.get("text", "")
        for p in doc.get("paragraphs", [])
        if p.get("text")
    )

    payload = {
        "workspaceId": ws,
        "docId": doc_id,
        "text": article,
        "phase": "prepublish",
    }

    r = requests.post(url, json=payload, timeout=30)
    result = r.json()

    print("\n==============================")
    print(doc.get("original_name"))
    print("doc_id:", doc_id)
    print("ok:", result.get("ok"))
    print("selection:", result.get("meta", {}).get("selection_stats"))
    print("density:", result.get("meta", {}).get("density_stats"))
    print("internal_strong_count:", len(result.get("internal_strong", [])))
    print("top_highlights:", [x.get("phrase") for x in result.get("internal_strong", [])[:15]])
