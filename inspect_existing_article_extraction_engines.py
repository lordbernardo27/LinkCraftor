from pathlib import Path
import re

FILES = [
    "backend/server/engine/article_body_extractor.py",
    "backend/server/stores/article_body_cleaning_engine.py",
    "backend/server/stores/article_cleaning_pipeline.py",
    "backend/server/stores/main_content_extraction_engine.py",
    "backend/server/stores/website_source_pipeline_orchestrator.py",
    "backend/server/stores/website_unified_content_store.py",
    "backend/server/stores/validated_article_uucd_bridge.py",
    "backend/server/stores/validated_article_ucd_bridge.py",
    "backend/server/stores/website_article_integrity_checker.py",
    "backend/server/stores/semantic_article_certification.py",
]

TERMS = [
    "def ",
    "class ",
    "article_body",
    "body_text",
    "main_content",
    "clean",
    "boilerplate",
    "nav",
    "footer",
    "header",
    "sidebar",
    "recommended",
    "related",
    "certify",
    "validate",
    "write",
    "store",
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
        if any(term.lower() in lower for term in TERMS[2:]):
            print(f"{i}: {line[:220]}")

    print("\nFIRST 120 LINES")
    for i, line in enumerate(lines[:120], start=1):
        print(f"{i}: {line}")
