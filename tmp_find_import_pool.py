import json, re
from pathlib import Path

base = Path(r"C:\Users\HP\Documents\LinkCraftor\backend\server\data")
rx = re.compile(r"https?://[^\"\s]+", re.I)

def extract_urls(x, out):
    if isinstance(x, str):
        if x.startswith("http"):
            out.add(x)
        else:
            for m in rx.findall(x):
                out.add(m)
    elif isinstance(x, dict):
        for k, v in x.items():
            if isinstance(k, str) and k.startswith("http"):
                out.add(k)
            extract_urls(v, out)
    elif isinstance(x, list):
        for it in x:
            extract_urls(it, out)

rows = []
for fp in sorted(base.glob("*.json")):
    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
    except Exception:
        try:
            obj = json.loads(fp.read_text())
        except Exception:
            continue

    urls = set()
    extract_urls(obj, urls)
    if urls:
        rows.append((len(urls), fp.name))

rows.sort(reverse=True)

print("Top URL-bearing files in data/:")
for n, name in rows[:20]:
    print(f"{n:>5}  {name}")

near = [(n, name) for n, name in rows if 70 <= n <= 95]
print("\nFiles with URL count near 82 (70-95):")
if near:
    for n, name in near:
        print(f"{n:>5}  {name}")
else:
    print("(none found)")
