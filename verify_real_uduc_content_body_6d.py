from __future__ import annotations

import json
from pathlib import Path

from backend.server.stores.upload_document_extractor import extract_upload_document_v1
from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_extraction_result,
)


def fail(msg: str):
    raise AssertionError(msg)


def find_latest_uploaded_file() -> Path:
    roots = [
        Path("backend/server/data/docs"),
        Path("backend/server/data/uploads"),
    ]

    allowed = {".docx", ".txt", ".html", ".htm", ".md", ".markdown"}

    candidates = []

    for root in roots:
        if not root.exists():
            continue

        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in allowed:
                candidates.append(p)

    if not candidates:
        fail("No real uploaded document found in backend/server/data/docs or backend/server/data/uploads")

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def infer_ids(path: Path):
    workspace_id = path.parent.name

    name = path.name
    if "__" in name:
        doc_id, original = name.split("__", 1)
    else:
        doc_id = path.stem
        original = path.name

    return workspace_id, doc_id, original


def main():
    uploaded_path = find_latest_uploaded_file()
    workspace_id, doc_id, original_filename = infer_ids(uploaded_path)

    extraction = extract_upload_document_v1(uploaded_path)

    result = build_and_write_uduc_from_extraction_result(
        extraction_result=extraction,
        workspace_id=workspace_id,
        document_id=doc_id,
        original_filename=original_filename,
        stored_filename=uploaded_path.name,
        stored_path=str(uploaded_path),
        source_metadata={
            "doc_id": doc_id,
            "filename": original_filename,
            "stored_name": uploaded_path.name,
            "stored_path": str(uploaded_path),
            "bytes": uploaded_path.stat().st_size,
        },
    )

    uduc = result["uduc"]
    content_body = uduc.get("content_body") or ""

    if not content_body.strip():
        fail("Real UDUC content_body is empty")

    print("============================================================")
    print("VERIFICATION 6D — REAL UDUC CONTENT BODY")
    print("============================================================")
    print("Uploaded file:", uploaded_path)
    print("Workspace ID:", workspace_id)
    print("Document ID:", doc_id)
    print("Original filename:", original_filename)
    print("UDUC path:", result.get("uduc_path"))
    print("Content body length:", len(content_body))
    print("============================================================")
    print("CONTENT BODY START")
    print("============================================================")
    print(content_body)
    print("============================================================")
    print("CONTENT BODY END")
    print("============================================================")


if __name__ == "__main__":
    main()
