from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

future = "from __future__ import annotations"
uduc_import = "from backend.server.stores.uploaded_document_unified_content import build_and_write_uduc_from_extraction_result"

lines = code.splitlines()

# remove duplicate future/import lines
lines = [line for line in lines if line.strip() not in {future, uduc_import}]

# rebuild file with future import first
new_lines = [
    future,
    uduc_import,
    "",
] + lines

p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("Fixed import order in universal_knowledge_worker.py")
