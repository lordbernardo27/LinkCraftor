from pathlib import Path
import re

p = Path("backend/server/stores/uploaded_document_unified_content.py")
code = p.read_text(encoding="utf-8")

# 1. Add structure field to dataclass
code = code.replace(
'''    content_body: str

    metadata: Dict[str, Any] = field(default_factory=dict)
''',
'''    content_body: str

    structure: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
'''
)

# 2. Add helper functions before build_uduc_from_upload_extraction_result
insert_after = '''def _read_upload_index_hit(workspace_id: str, document_id: str) -> Dict[str, Any]:
    candidates = [
        Path("backend/server/data/docs") / workspace_id / "index.json",
        Path("backend/server/data/uploads") / workspace_id / "index.json",
    ]

    for fp in candidates:
        if not fp.exists():
            continue

        try:
            raw = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue

        rows = raw if isinstance(raw, list) else raw.get("items", []) if isinstance(raw, dict) else []

        for row in rows:
            if isinstance(row, dict) and str(row.get("doc_id") or row.get("document_id") or "").strip() == document_id:
                return row

    return {}
'''

helpers = r'''

def _paragraphs_from_content_body(content_body: str) -> List[Dict[str, Any]]:
    raw = str(content_body or "")
    blocks = [b.strip() for b in re.split(r"\n\s*\n+", raw) if b.strip()]

    if not blocks and raw.strip():
        blocks = [raw.strip()]

    return [
        {
            "index": i,
            "text": block,
            "char_count": len(block),
            "word_count": len([w for w in re.split(r"\s+", block) if w.strip()]),
        }
        for i, block in enumerate(blocks, start=1)
    ]


def _build_heading_map(headings: List[str], content_body: str) -> List[Dict[str, Any]]:
    body = str(content_body or "")
    out: List[Dict[str, Any]] = []

    for i, heading in enumerate(headings, start=1):
        h = str(heading or "").strip()
        if not h:
            continue

        char_position = body.find(h)

        out.append(
            {
                "index": i,
                "heading": h,
                "level": None,
                "char_position": char_position if char_position >= 0 else None,
            }
        )

    return out


def _build_uduc_structure(content_body: str, headings: List[str]) -> Dict[str, Any]:
    paragraphs = _paragraphs_from_content_body(content_body)
    heading_map = _build_heading_map(headings, content_body)

    document_order: List[Dict[str, Any]] = []

    for h in heading_map:
        document_order.append(
            {
                "type": "heading",
                "index": h.get("index"),
                "text": h.get("heading"),
                "char_position": h.get("char_position"),
            }
        )

    for p in paragraphs:
        document_order.append(
            {
                "type": "paragraph",
                "index": p.get("index"),
                "text_preview": str(p.get("text") or "")[:160],
                "word_count": p.get("word_count"),
            }
        )

    return {
        "paragraphs": paragraphs,
        "heading_map": heading_map,
        "section_count": len(heading_map),
        "paragraph_count": len(paragraphs),
        "document_order": document_order,
        "structure_version": "uduc_structure_v1",
        "boundary": {
            "preserves_content_body": True,
            "modifies_content_body": False,
            "performs_cleaning": False,
            "performs_semantic_analysis": False,
        },
    }
'''

if helpers.strip() not in code:
    code = code.replace(insert_after, insert_after + helpers)

# 3. Build structure after content_body
code = code.replace(
'''    content_body = str(er.get("content_body") or er.get("text") or "").strip()

    extension = str(meta.get("extension") or Path(original_name).suffix.lower() or "").strip()
''',
'''    content_body = str(er.get("content_body") or er.get("text") or "").strip()
    structure = _build_uduc_structure(content_body, headings)

    extension = str(meta.get("extension") or Path(original_name).suffix.lower() or "").strip()
'''
)

# 4. Add structure to return object
code = code.replace(
'''        headings=headings,
        content_body=content_body,
        metadata=merged_metadata,
''',
'''        headings=headings,
        content_body=content_body,
        structure=structure,
        metadata=merged_metadata,
'''
)

p.write_text(code, encoding="utf-8")
print("Updated UDUC with structure preservation.")
