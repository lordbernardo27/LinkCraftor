from pathlib import Path

p = Path("backend/server/stores/uploaded_document_unified_content.py")
code = p.read_text(encoding="utf-8")

old = '''    return {
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

new = '''    word_count = len([w for w in re.split(r"\\s+", str(content_body or "")) if w.strip()])

    return {
        "paragraphs": paragraphs,
        "heading_map": heading_map,
        "section_count": len(heading_map),
        "paragraph_count": len(paragraphs),
        "document_order": document_order,

        "first_heading": headings[0] if headings else "",
        "last_heading": headings[-1] if headings else "",
        "first_paragraph": paragraphs[0]["text"] if paragraphs else "",
        "last_paragraph": paragraphs[-1]["text"] if paragraphs else "",
        "estimated_word_count": word_count,
        "estimated_character_count": len(str(content_body or "")),

        "structure_version": "uduc_structure_v1_1",
        "boundary": {
            "preserves_content_body": True,
            "modifies_content_body": False,
            "performs_cleaning": False,
            "performs_semantic_analysis": False,
        },
    }
'''

if old not in code:
    raise SystemExit("Could not find old structure return block.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
print("Added final UDUC structure enhancements.")
