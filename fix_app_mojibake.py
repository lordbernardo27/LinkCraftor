from pathlib import Path

p = Path("frontend/public/assets/js/app.js")
s = p.read_text(encoding="utf-8", errors="replace")

replacements = {
    "�": "—",
    "didn�t": "didn’t",
    "can�t": "can’t",
    "button�s": "button’s",
    "h1�h6": "h1–h6",
    "H1�H6": "H1–H6",
    "Loading�": "Loading…",
    "more�": "more…",
    "editing�": "editing…",
    "File: �": "File: —",
    "�original�": "“original”",
    "�.htm�": "“.htm”",
    "�words": "words",
}

for bad, good in replacements.items():
    s = s.replace(bad, good)

p.write_text(s, encoding="utf-8")
print("app.js mojibake cleanup pass complete")
