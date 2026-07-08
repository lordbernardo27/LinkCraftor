from pathlib import Path

FILES = [
    "backend/server/stores/upload_document_extractor.py",
    "backend/server/stores/upload_intel_store_v2.py",
    "backend/server/stores/upload_phrase_pool_builder.py",
    "backend/server/stores/upload_phrase_selector.py",
    "backend/server/stores/upload_document_store.py",
    "backend/server/engine/extract_rb2.py",
    "backend/server/engine/semantic_workspace_learner.py",
    "backend/server/routes/files.py",
    "backend/server/routes/rb2_run.py",
    "backend/server/orchestration/worker.py",
]

TERMS = [
    "upload",
    "document",
    "docx",
    "pdf",
    "txt",
    "extract",
    "clean_text",
    "text",
    "store",
    "workspace",
    "semantic",
    "phrase",
    "entity",
    "body",
]

for file in FILES:
    path = Path(file)
    print("=" * 100)
    print("FILE:", file)
    print("=" * 100)

    if not path.exists():
        print("MISSING")
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    print("total_lines =", len(lines))

    print("\nFUNCTIONS / CLASSES")
    for i, line in enumerate(lines, start=1):
        s = line.strip()
        if s.startswith("def ") or s.startswith("class "):
            print(f"{i}: {s}")

    print("\nIMPORTANT TERM HITS")
    for i, line in enumerate(lines, start=1):
        lower = line.lower()
        if any(term in lower for term in TERMS):
            print(f"{i}: {line[:220]}")

    print("\nFIRST 100 LINES")
    for i, line in enumerate(lines[:100], start=1):
        print(f"{i}: {line}")
