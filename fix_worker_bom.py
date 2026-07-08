from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")

code = p.read_text(encoding="utf-8-sig")
code = code.replace("\ufeff", "")

p.write_text(code, encoding="utf-8")

print("Removed hidden BOM/non-printable character from universal_knowledge_worker.py")
