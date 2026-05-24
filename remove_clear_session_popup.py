from pathlib import Path

p = Path("frontend/public/assets/js/app.js")
s = p.read_text(encoding="utf-8", errors="replace")

old = '''  const confirmed = window.confirm(
    "Clear current session?\\n\\nThis will clear:\\n- Current editor document\\n- Runtime highlights\\n- Temporary link review state\\n- Imported sitemap URLs\\n- Draft map imports\\n\\nThis will NOT disconnect the domain."
  );

  if (!confirmed) return;

'''

s = s.replace(old, "")

p.write_text(s, encoding="utf-8")
print("Removed Clear Session confirmation popup")
