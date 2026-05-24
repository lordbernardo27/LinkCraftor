from pathlib import Path

p = Path("frontend/public/assets/js/app.js")
lines = p.read_text(encoding="utf-8", errors="replace").splitlines()

# Remove the extra stray line.
# Your inspection showed it at line 2467 (1-based).
del lines[2467 - 1]

p.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Removed extra closing brace")
