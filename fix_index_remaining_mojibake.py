from pathlib import Path

p = Path("frontend/public/index.html")
s = p.read_text(encoding="utf-8", errors="replace")

s = s.replace('ðŸ›', '🏛')
s = s.replace('â±', '⏱')

p.write_text(s, encoding="utf-8")
print("fixed remaining index.html mojibake")
