from pathlib import Path

p = Path("frontend/public/index.html")
lines = p.read_text(encoding="utf-8", errors="replace").splitlines()

# Line numbers are 1-based from your inspection.
lines[1117 - 1] = '      <div class="kpi-icon purple">🏛</div>'
lines[1135 - 1] = '      <div class="kpi-icon cyan">⏱</div>'

p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("fixed index.html by exact line numbers")
