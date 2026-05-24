from pathlib import Path

p = Path("frontend/public/index.html")
s = p.read_text(encoding="utf-8", errors="replace")

replacements = {
    "â€”": "—",
    "â€™": "’",
    "â€¦": "…",
    "â–¾": "▾",
    "â–®": "▮",
    "â†¶": "↶",
    "â†·": "↷",
    "â†”": "↔",
    "â˜·": "☷",
    "â˜°": "☰",
    "â˜‘": "☑",
    "â›“": "⛓",
    "â–£": "▣",
    "â‰¡": "≡",
    "â›¶": "⛶",
    "â—€": "◀",
    "â–¶": "▶",
    "âœ“": "✓",
    "âœ•": "✕",
    "ðŸ””": "🔔",
    "ðŸ”—": "🔗",
    "ðŸ›¡": "🛡",
    "ðŸ“": "📁",
    "â±": "⏱",
    "â—": "●",
}

for bad, good in replacements.items():
    s = s.replace(bad, good)

p.write_text(s, encoding="utf-8")
print("index.html mojibake pass complete")
