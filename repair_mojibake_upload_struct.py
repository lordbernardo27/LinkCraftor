import json
from pathlib import Path

p = Path("backend/server/data/upload_struct_ws_betterhealthcheck_com.json")
data = json.loads(p.read_text(encoding="utf-8"))

changed = 0

def repair_text(s: str) -> str:
    if "â" not in s and "Ã" not in s and "Â" not in s:
        return s
    try:
        return s.encode("cp1252", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        return s

for doc in data.get("docs", {}).values():
    for par in doc.get("paragraphs", []):
        old = str(par.get("text", ""))
        new = repair_text(old)
        if new != old:
            par["text"] = new
            changed += 1

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("fixed_paragraphs=", changed)
