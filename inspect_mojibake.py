from pathlib import Path

paths = [
    Path("frontend/public/index.html"),
    Path("frontend/public/assets/js/app.js"),
]

patterns = ["�", "â", "Â", "Ã", "ð", "Ÿ", "?", "✅", "❌"]

for p in paths:
    print("\n====", p, "====")
    if not p.exists():
        print("MISSING")
        continue

    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    hits = []
    for i, line in enumerate(lines, 1):
        if any(x in line for x in ["�", "â", "Â", "Ã", "ð", "Ÿ"]):
            hits.append((i, line[:220]))

    print("mojibake_line_count:", len(hits))
    for i, line in hits[:80]:
        print(f"{i}: {line}")
