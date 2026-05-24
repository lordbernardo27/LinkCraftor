from pathlib import Path

p = Path("frontend/public/assets/js/app.js")
s = p.read_text(encoding="utf-8")

start_marker = 'const btnClearSession = $("btnClearSession");\nbtnClearSession?.addEventListener("click", async () => {\n  clearState();'
end_marker = '\n});\n\n/* Stopwords UI */'

start = s.find(start_marker)
if start == -1:
    raise SystemExit("OLD Clear Session handler start not found")

end = s.find(end_marker, start)
if end == -1:
    raise SystemExit("OLD Clear Session handler end not found")

s = s[:start] + '/* Old duplicate Clear Session handler removed. */\n\n/* Stopwords UI */' + s[end + len(end_marker):]

p.write_text(s, encoding="utf-8")
print("Removed old duplicate Clear Session handler")
