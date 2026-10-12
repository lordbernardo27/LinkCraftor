from pathlib import Path
from docx import Document
from backend.server.pipelines.upload_document.uploaded_document_to_highlight_pipeline.coordinator import run_uploaded_document_to_highlight_pipeline

doc_id = "536f826368bf4c48b42cbca307eb0b2d"
workspace_id = "ws_whattoexpect_com"
path = Path(r"backend\server\data\docs\ws_whattoexpect_com\536f826368bf4c48b42cbca307eb0b2d__health_medicine_article_1_hypertension.docx")

doc = Document(path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
title = paragraphs[0] if paragraphs else "Understanding High Blood Pressure: Causes, Risks, and Practical Management"
text = "\n\n".join(paragraphs[1:] if len(paragraphs) > 1 else paragraphs)

result = run_uploaded_document_to_highlight_pipeline(
    workspace_id=workspace_id,
    document_id=doc_id,
    extraction_result={
        "title": title,
        "text": text,
        "html": "",
    },
)

selected = result["highlight_selection"]["selected"]

print("")
print("========== ARTICLE 1 — FIRST 20 SELECTOR PHRASES ==========")
print("TOTAL_SELECTED =", len(selected))
for i, item in enumerate(selected[:20], 1):
    print(f"{i:02d}. {item.get('phrase')}")
print("===========================================================")
