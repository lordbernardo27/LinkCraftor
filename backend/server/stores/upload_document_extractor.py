"""
Universal Upload Document Extractor

Phase 4.4 responsibility:
- Extract readable body content from uploaded documents.
- Normalize uploaded source content before semantic processing.
- Keep uploaded document extraction separate from website article extraction.

This module will support:
- TXT
- Markdown
- HTML
- DOCX
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class UploadExtractionResult:
    source_path: str
    source_type: str
    title: str
    text: str
    headings: List[str]
    metadata: Dict[str, Any]
    extraction_status: str
    extraction_confidence: float
    created_at: str


SUPPORTED_UPLOAD_EXTENSIONS = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}


def detect_upload_source_type(path: str | Path) -> str:
    p = Path(path)
    return SUPPORTED_UPLOAD_EXTENSIONS.get(p.suffix.lower(), "unsupported")


def build_empty_upload_result(
    path: str | Path,
    *,
    status: str = "pending",
    confidence: float = 0.0,
) -> UploadExtractionResult:
    p = Path(path)
    source_type = detect_upload_source_type(p)

    return UploadExtractionResult(
        source_path=str(p),
        source_type=source_type,
        title=p.stem,
        text="",
        headings=[],
        metadata={
            "filename": p.name,
            "extension": p.suffix.lower(),
            "phase": "4.4",
            "extractor": "upload_document_extractor",
        },
        extraction_status=status,
        extraction_confidence=confidence,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def serialize_upload_extraction_result(result: UploadExtractionResult) -> Dict[str, Any]:
    return asdict(result)



def _normalize_upload_text_v1(text: str) -> str:
    lines = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = " ".join(raw_line.strip().split())
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def extract_txt_upload_v1(path: str | Path) -> UploadExtractionResult:
    p = Path(path)

    if not p.exists():
        result = build_empty_upload_result(p, status="missing_file", confidence=0.0)
        result.metadata["error"] = "File does not exist."
        return result

    if p.suffix.lower() != ".txt":
        result = build_empty_upload_result(p, status="unsupported_extension", confidence=0.0)
        result.metadata["error"] = "TXT extractor only accepts .txt files."
        return result

    try:
        raw_text = p.read_text(encoding="utf-8", errors="ignore")
        normalized_text = _normalize_upload_text_v1(raw_text)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["raw_char_count"] = len(raw_text)
            result.metadata["normalized_char_count"] = 0
            return result

        result = UploadExtractionResult(
            source_path=str(p),
            source_type="txt",
            title=p.stem,
            text=normalized_text,
            headings=[],
            metadata={
                "filename": p.name,
                "extension": p.suffix.lower(),
                "phase": "4.4.2",
                "extractor": "extract_txt_upload_v1",
                "raw_char_count": len(raw_text),
                "normalized_char_count": len(normalized_text),
                "line_count": len(normalized_text.splitlines()),
            },
            extraction_status="success",
            extraction_confidence=0.95,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return result

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result



def _clean_markdown_line_prefix_v1(line: str) -> str:
    # Handles UTF-8 BOM and mojibake BOM seen as ??? before Markdown headings.
    return str(line or "").replace("\ufeff", "").replace("???", "").strip()


def _extract_markdown_headings_v1(text: str) -> List[str]:
    headings: List[str] = []
    for line in text.splitlines():
        stripped = _clean_markdown_line_prefix_v1(line)
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                headings.append(heading)
    return headings


def _strip_markdown_syntax_v1(text: str) -> str:
    cleaned_lines: List[str] = []

    for line in text.splitlines():
        stripped = _clean_markdown_line_prefix_v1(line)

        if not stripped:
            continue

        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()

        if stripped.startswith(">"):
            stripped = stripped.lstrip(">").strip()

        for token in ["**", "__", "`", "*"]:
            stripped = stripped.replace(token, "")

        if stripped.startswith("- "):
            stripped = stripped[2:].strip()

        if stripped.startswith("* "):
            stripped = stripped[2:].strip()

        cleaned_lines.append(stripped)

    return _normalize_upload_text_v1("\n".join(cleaned_lines))


def extract_markdown_upload_v1(path: str | Path) -> UploadExtractionResult:
    p = Path(path)

    if not p.exists():
        result = build_empty_upload_result(p, status="missing_file", confidence=0.0)
        result.metadata["error"] = "File does not exist."
        return result

    if p.suffix.lower() not in {".md", ".markdown"}:
        result = build_empty_upload_result(p, status="unsupported_extension", confidence=0.0)
        result.metadata["error"] = "Markdown extractor only accepts .md or .markdown files."
        return result

    try:
        raw_text = p.read_text(encoding="utf-8", errors="ignore")
        headings = _extract_markdown_headings_v1(raw_text)
        normalized_text = _strip_markdown_syntax_v1(raw_text)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["raw_char_count"] = len(raw_text)
            result.metadata["normalized_char_count"] = 0
            result.metadata["heading_count"] = len(headings)
            return result

        result = UploadExtractionResult(
            source_path=str(p),
            source_type="markdown",
            title=headings[0] if headings else p.stem,
            text=normalized_text,
            headings=headings,
            metadata={
                "filename": p.name,
                "extension": p.suffix.lower(),
                "phase": "4.4.3",
                "extractor": "extract_markdown_upload_v1",
                "raw_char_count": len(raw_text),
                "normalized_char_count": len(normalized_text),
                "line_count": len(normalized_text.splitlines()),
                "heading_count": len(headings),
            },
            extraction_status="success",
            extraction_confidence=0.93,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return result

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result





def _strip_html_tags_v1(html: str) -> str:
    import re

    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    cleaned = re.sub(r"(?is)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"(?is)</p\s*>", "\n", cleaned)
    cleaned = re.sub(r"(?is)</div\s*>", "\n", cleaned)
    cleaned = re.sub(r"(?is)</h[1-6]\s*>", "\n", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)

    import html as html_lib
    cleaned = html_lib.unescape(cleaned)

    return _normalize_upload_text_v1(cleaned)


def _extract_html_title_v1(html: str, fallback: str) -> str:
    import re
    import html as html_lib

    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if m:
        title = _normalize_upload_text_v1(html_lib.unescape(m.group(1)))
        if title:
            return title

    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    if h1:
        title = _strip_html_tags_v1(h1.group(1))
        if title:
            return title

    return fallback


def _extract_html_headings_v1(html: str) -> List[str]:
    import re

    headings: List[str] = []
    for m in re.finditer(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>", html):
        heading = _strip_html_tags_v1(m.group(1))
        if heading:
            headings.append(heading)
    return headings


def extract_html_upload_v1(path: str | Path) -> UploadExtractionResult:
    p = Path(path)

    if not p.exists():
        result = build_empty_upload_result(p, status="missing_file", confidence=0.0)
        result.metadata["error"] = "File does not exist."
        return result

    if p.suffix.lower() not in {".html", ".htm"}:
        result = build_empty_upload_result(p, status="unsupported_extension", confidence=0.0)
        result.metadata["error"] = "HTML extractor only accepts .html or .htm files."
        return result

    try:
        raw_html = p.read_text(encoding="utf-8", errors="ignore")
        title = _extract_html_title_v1(raw_html, p.stem)
        headings = _extract_html_headings_v1(raw_html)
        normalized_text = _strip_html_tags_v1(raw_html)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["raw_char_count"] = len(raw_html)
            result.metadata["normalized_char_count"] = 0
            result.metadata["heading_count"] = len(headings)
            return result

        result = UploadExtractionResult(
            source_path=str(p),
            source_type="html",
            title=title,
            text=normalized_text,
            headings=headings,
            metadata={
                "filename": p.name,
                "extension": p.suffix.lower(),
                "phase": "4.4.4",
                "extractor": "extract_html_upload_v1",
                "raw_char_count": len(raw_html),
                "normalized_char_count": len(normalized_text),
                "line_count": len(normalized_text.splitlines()),
                "heading_count": len(headings),
            },
            extraction_status="success",
            extraction_confidence=0.9,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return result

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result





def _extract_docx_paragraphs_v1(path: str | Path) -> List[str]:
    from zipfile import ZipFile
    import re
    import html as html_lib

    p = Path(path)

    with ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

    paragraphs: List[str] = []

    for paragraph_xml in re.findall(r"(?is)<w:p\b.*?</w:p>", xml):
        texts = re.findall(r"(?is)<w:t[^>]*>(.*?)</w:t>", paragraph_xml)
        paragraph = "".join(html_lib.unescape(t) for t in texts)
        paragraph = _normalize_upload_text_v1(paragraph)
        if paragraph:
            paragraphs.append(paragraph)

    return paragraphs


def _extract_docx_headings_v1(paragraphs: List[str]) -> List[str]:
    headings: List[str] = []

    for paragraph in paragraphs:
        words = paragraph.split()

        if len(words) <= 12 and len(paragraph) <= 90:
            if paragraph[:1].isupper() and not paragraph.endswith("."):
                headings.append(paragraph)

    return headings[:25]


def extract_docx_upload_v1(path: str | Path) -> UploadExtractionResult:
    p = Path(path)

    if not p.exists():
        result = build_empty_upload_result(p, status="missing_file", confidence=0.0)
        result.metadata["error"] = "File does not exist."
        return result

    if p.suffix.lower() != ".docx":
        result = build_empty_upload_result(p, status="unsupported_extension", confidence=0.0)
        result.metadata["error"] = "DOCX extractor only accepts .docx files."
        return result

    try:
        paragraphs = _extract_docx_paragraphs_v1(p)
        normalized_text = _normalize_upload_text_v1("\n".join(paragraphs))
        headings = _extract_docx_headings_v1(paragraphs)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["paragraph_count"] = len(paragraphs)
            result.metadata["heading_count"] = len(headings)
            return result

        result = UploadExtractionResult(
            source_path=str(p),
            source_type="docx",
            title=headings[0] if headings else p.stem,
            text=normalized_text,
            headings=headings,
            metadata={
                "filename": p.name,
                "extension": p.suffix.lower(),
                "phase": "4.4.5",
                "extractor": "extract_docx_upload_v1",
                "normalized_char_count": len(normalized_text),
                "line_count": len(normalized_text.splitlines()),
                "paragraph_count": len(paragraphs),
                "heading_count": len(headings),
                "method": "zipfile_word_document_xml",
            },
            extraction_status="success",
            extraction_confidence=0.88,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return result

    except KeyError:
        result = build_empty_upload_result(p, status="invalid_docx", confidence=0.0)
        result.metadata["error"] = "word/document.xml not found in DOCX archive."
        return result

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result





def extract_upload_document_v1(path: str | Path) -> UploadExtractionResult:
    p = Path(path)
    source_type = detect_upload_source_type(p)

    if source_type == "txt":
        return extract_txt_upload_v1(p)

    if source_type == "markdown":
        return extract_markdown_upload_v1(p)

    if source_type == "html":
        return extract_html_upload_v1(p)

    if source_type == "docx":
        return extract_docx_upload_v1(p)

    result = build_empty_upload_result(p, status="unsupported_source_type", confidence=0.0)
    result.metadata["error"] = "Unsupported uploaded document type."
    result.metadata["supported_extensions"] = sorted(SUPPORTED_UPLOAD_EXTENSIONS.keys())
    return result


def extract_upload_documents_batch_v1(paths: List[str | Path]) -> List[UploadExtractionResult]:
    results: List[UploadExtractionResult] = []

    for path in paths:
        results.append(extract_upload_document_v1(path))

    return results





def write_upload_extraction_artifact_v1(
    result: UploadExtractionResult,
    output_dir: str | Path = "backend/server/data/upload_extractions",
) -> Path:
    import json
    import hashlib

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_key = hashlib.sha256(result.source_path.encode("utf-8")).hexdigest()[:16]
    safe_type = result.source_type.replace("/", "_").replace("\\", "_")
    filename = f"{safe_type}_{source_key}.json"
    out_path = out_dir / filename

    payload = serialize_upload_extraction_result(result)
    payload["artifact_type"] = "upload_extraction_result"
    payload["artifact_version"] = "v1"
    payload["written_at"] = datetime.now(timezone.utc).isoformat()

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def write_upload_extraction_batch_artifacts_v1(
    results: List[UploadExtractionResult],
    output_dir: str | Path = "backend/server/data/upload_extractions",
) -> List[Path]:
    paths: List[Path] = []

    for result in results:
        paths.append(write_upload_extraction_artifact_v1(result, output_dir=output_dir))

    return paths


def explain_upload_document_extractor_v1() -> Dict[str, Any]:
    return {
        "phase": "4.4.1",
        "module": "upload_document_extractor.py",
        "status": "created",
        "responsibility": "Provide the foundation module for uploaded document extraction.",
        "supported_extensions": sorted(SUPPORTED_UPLOAD_EXTENSIONS.keys()),
        "current_capabilities": [
            "Detect upload source type from file extension",
            "Extract readable text from TXT uploads",
            "Extract headings and readable text from Markdown uploads",
            "Extract title, headings, and readable text from HTML uploads",
            "Extract readable text from DOCX uploads using document.xml",
            "Route uploaded files to the correct extractor automatically",
            "Batch-extract multiple uploaded documents",
            "Write upload extraction artifacts as JSON",
            "Write batch upload extraction artifacts",
            "Create empty normalized extraction result",
            "Serialize extraction result for downstream artifact writing",
            "Keep uploaded document extraction separate from website article extraction",
        ],
        "next_steps": [
            "4.4.2 TXT Extraction Engine completed",
            "4.4.3 Markdown Extraction Engine completed",
            "4.4.4 HTML Extraction Engine completed",
            "4.4.5 DOCX Extraction Engine completed",
            "4.4.6 Smart Extractor Integration completed",
            "4.4.7 Upload Artifact Writer completed",
            "4.4.8 End-to-End Upload Verification",
        ],
    }
