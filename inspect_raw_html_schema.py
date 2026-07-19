import json
from pathlib import Path

p = Path("backend/server/data/raw_website_html/raw_website_html_ws_whattoexpect_com.json")

obj = json.loads(
    p.read_text(
        encoding="utf-8",
        errors="replace",
    )
)

print("=" * 80)
print("ROOT TYPE")
print("=" * 80)
print(type(obj))

if isinstance(obj, dict):
    print()
    print("TOP LEVEL KEYS")
    print("-" * 80)
    for k in obj.keys():
        print(k)

elif isinstance(obj, list):
    print()
    print("LIST LENGTH:", len(obj))
    if obj:
        print()
        print("FIRST RECORD KEYS")
        print("-" * 80)
        for k in obj[0].keys():
            print(k)

print("=" * 80)
