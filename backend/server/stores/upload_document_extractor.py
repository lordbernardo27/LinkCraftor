"""
Universal Upload Document Extractor

Phase 4.4 responsibility:
- Extract readable body content from uploaded documents.
- Normalize uploaded source content before semantic processing.
- Keep uploaded document extraction separate from website article extraction.

Supports: TXT, Markdown, HTML, DOCX.

CONTRACT (fixed in this version):
- Extracted `text` preserves PARAGRAPH BOUNDARIES as blank lines ("\n\n").
  Downstream (UDUC `_paragraphs_from_content_body`) splits paragraphs on
  blank lines; the previous normalizer removed every blank line, so every
  document collapsed into a single paragraph downstream.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Anchor all filesystem defaults to the package (backend/server), matching
# files.py, instead of relying on the process CWD.
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/server
DEFAULT_EXTRACTION_ARTIFACT_DIR = BASE_DIR / "data" / "upload_extractions"


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


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def _normalize_upload_text_v2(text: str) -> str:
    """Normalize whitespace WITHOUT destroying paragraph structure.

    - Line endings unified to \n.
    - Runs of spaces/tabs inside a line collapsed to single spaces.
    - Lines stripped.
    - One-or-more blank lines between content collapse to exactly ONE blank
      line (a paragraph boundary), never zero.

    The previous v1 dropped every empty line, which meant the output could
    never contain "\n\n" — and UDUC's paragraph splitter (which splits on
    blank lines) therefore saw every document as a single paragraph.
    """
    unified = str(text or "").replace("\r\n", "\n").replace("\r", "\n")

    blocks: List[str] = []
    current: List[str] = []

    for raw_line in unified.split("\n"):
        line = " ".join(raw_line.strip().split())
        if line:
            current.append(line)
        elif current:
            blocks.append("\n".join(current))
            current = []

    if current:
        blocks.append("\n".join(current))

    return "\n\n".join(blocks).strip()


# Kept as an alias so any external caller of the old name keeps working,
# but now with paragraph-preserving behavior.
_normalize_upload_text_v1 = _normalize_upload_text_v2


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

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
        normalized_text = _normalize_upload_text_v2(raw_text)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["raw_char_count"] = len(raw_text)
            result.metadata["normalized_char_count"] = 0
            return result

        return UploadExtractionResult(
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
                "paragraph_count": normalized_text.count("\n\n") + 1,
            },
            extraction_status="success",
            extraction_confidence=0.95,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

# BOM / UTF-8-BOM-as-cp1252 mojibake, only meaningful at line start.
_LINE_PREFIX_JUNK_RE = re.compile(r"^(?:\ufeff|ï»¿)+")

_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_MD_ORDERED_LIST_RE = re.compile(r"^\d{1,3}[.)]\s+")
_MD_HR_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})\s*$")
_MD_STAR_OR_CODE_RE = re.compile(
    r"(\*\*|\*|`)(.+?)\1"
)

_MD_UNDERSCORE_EMPHASIS_RE = re.compile(
    r"(?<!\w)(__|_)(.+?)\1(?!\w)"
)


def _clean_markdown_line_prefix_v2(line: str) -> str:
    """Strip BOM / mojibake-BOM at the START of a line only.

    FIX: v1 did a blanket ``.replace("???", "")`` across the whole line,
    which deleted legitimate question marks from body text
    ("Wait, what??? ..." -> "Wait, what ..."). Only the line-leading
    byte-order-mark junk is actually mojibake.
    """
    return _LINE_PREFIX_JUNK_RE.sub("", str(line or "")).strip()


# Backward-compat alias (old name, safe behavior).
_clean_markdown_line_prefix_v1 = _clean_markdown_line_prefix_v2


def _strip_md_inline_v1(text: str) -> str:
    out = _MD_IMAGE_RE.sub(lambda m: m.group(1), text)   # ![alt](src) -> alt
    out = _MD_LINK_RE.sub(lambda m: m.group(1), out)     # [text](url) -> text

    # Strip real Markdown emphasis/code delimiters while preserving
    # underscores that are part of ordinary tokens such as user_id,
    # product_name, API_RESPONSE_CODE, and similar identifiers.
    prev = None

    while prev != out:  # nested emphasis: **bold *italic***
        prev = out

        out = _MD_STAR_OR_CODE_RE.sub(
            lambda m: m.group(2),
            out,
        )

        out = _MD_UNDERSCORE_EMPHASIS_RE.sub(
            lambda m: m.group(2),
            out,
        )

    return out


def _extract_markdown_headings_v1(text: str) -> List[str]:
    headings: List[str] = []
    in_fence = False
    for line in str(text or "").splitlines():
        stripped = _clean_markdown_line_prefix_v2(line)
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("#"):
            heading = _strip_md_inline_v1(stripped.lstrip("#").strip())
            if heading:
                headings.append(heading)
    return headings


def _strip_markdown_syntax_v2(text: str) -> str:
    cleaned_lines: List[str] = []
    in_fence = False

    for line in str(text or "").splitlines():
        stripped = _clean_markdown_line_prefix_v2(line)

        # Fenced code blocks: drop the fence lines, keep the code content
        # verbatim (it is still readable body content).
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            cleaned_lines.append(stripped)
            continue

        if not stripped:
            cleaned_lines.append("")  # preserve paragraph boundary
            continue

        if _MD_HR_RE.match(stripped):  # --- / *** / ___ rules
            cleaned_lines.append("")
            continue

        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()

        if stripped.startswith(">"):
            stripped = stripped.lstrip(">").strip()

        if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("+ "):
            stripped = stripped[2:].strip()
        else:
            stripped = _MD_ORDERED_LIST_RE.sub("", stripped)  # "1. item"

        stripped = _strip_md_inline_v1(stripped)

        cleaned_lines.append(stripped)

    return _normalize_upload_text_v2("\n".join(cleaned_lines))


# Backward-compat alias.
_strip_markdown_syntax_v1 = _strip_markdown_syntax_v2


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
        normalized_text = _strip_markdown_syntax_v2(raw_text)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["raw_char_count"] = len(raw_text)
            result.metadata["normalized_char_count"] = 0
            result.metadata["heading_count"] = len(headings)
            return result

        return UploadExtractionResult(
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
                "paragraph_count": normalized_text.count("\n\n") + 1,
            },
            extraction_status="success",
            extraction_confidence=0.93,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_HTML_COMMENT_RE = re.compile(r"(?s)<!--.*?-->")


def _strip_html_tags_v1(html: str) -> str:
    import html as html_lib

    cleaned = _HTML_COMMENT_RE.sub(" ", str(html or ""))  # FIX: comments first
    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", cleaned)
    cleaned = re.sub(r"(?is)<br\s*/?>", "\n", cleaned)
    # Block-level closers become PARAGRAPH boundaries (blank line), so the
    # downstream paragraph splitter sees real blocks.
    cleaned = re.sub(r"(?is)</p\s*>", "\n\n", cleaned)
    cleaned = re.sub(r"(?is)</div\s*>", "\n\n", cleaned)
    cleaned = re.sub(r"(?is)</h[1-6]\s*>", "\n\n", cleaned)
    cleaned = re.sub(r"(?is)</li\s*>", "\n", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)

    cleaned = html_lib.unescape(cleaned)

    return _normalize_upload_text_v2(cleaned)


def _extract_html_title_v1(html: str, fallback: str) -> str:
    import html as html_lib

    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", str(html or ""))
    if m:
        title = _normalize_upload_text_v2(html_lib.unescape(m.group(1)))
        if title:
            return title

    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", str(html or ""))
    if h1:
        title = _strip_html_tags_v1(h1.group(1))
        if title:
            return title

    return fallback


def _extract_html_headings_v1(html: str) -> List[str]:
    headings: List[str] = []
    for m in re.finditer(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>", str(html or "")):
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

        return UploadExtractionResult(
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
                "paragraph_count": normalized_text.count("\n\n") + 1,
            },
            extraction_status="success",
            extraction_confidence=0.9,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

_DOCX_P_RE = re.compile(r"(?is)<w:p\b.*?</w:p>")
_DOCX_T_RE = re.compile(r"(?is)<w:t(?:\s[^>]*)?>(.*?)</w:t>")
_DOCX_BR_TAB_RE = re.compile(r"(?is)<w:(?:br|cr)\s*/?>|<w:tab\s*/?>")
_DOCX_PSTYLE_RE = re.compile(r'(?is)<w:pStyle\s[^>]*w:val="([^"]+)"')

# Word style IDs that mark real headings (locale-independent IDs, not
# display names).
_DOCX_HEADING_STYLE_RE = re.compile(r"(?i)^(?:heading|berschrift|titre|titolo)?\s*(\d)$|^(title|heading\d)$")


def _docx_style_is_heading(style_id: str) -> bool:
    s = (style_id or "").strip().lower()
    if not s:
        return False
    if s == "title":
        return True
    return bool(re.match(r"^heading[1-6]$", s))


def _extract_docx_paragraphs_v2(path: str | Path) -> List[Dict[str, Any]]:
    """Extract paragraphs WITH their style ids from word/document.xml.

    FIXES vs v1:
    - <w:br/>, <w:cr/> become line breaks and <w:tab/> becomes a space
      inside a paragraph (previously 'line one<w:br/>line two' extracted
      as 'line oneline two').
    - The paragraph style id (<w:pStyle w:val="Heading1"/>) is captured so
      heading detection can be STYLE-BASED, consistent with the strict
      style-based approach used elsewhere in the system (files.py).
    """
    from zipfile import ZipFile
    import html as html_lib

    p = Path(path)

    with ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")

    paragraphs: List[Dict[str, Any]] = []

    for paragraph_xml in _DOCX_P_RE.findall(xml):
        style_m = _DOCX_PSTYLE_RE.search(paragraph_xml)
        style_id = style_m.group(1).strip() if style_m else ""

        # Convert breaks/tabs to whitespace BEFORE pulling runs, so the
        # boundary survives run concatenation.
        pxml = _DOCX_BR_TAB_RE.sub(
            lambda m: "\n" if "tab" not in m.group(0).lower() else " ",
            paragraph_xml,
        )

        parts: List[str] = []
        pos = 0
        # Walk the paragraph xml preserving order of text runs and the
        # injected \n markers between them.
        for m in _DOCX_T_RE.finditer(pxml):
            gap = pxml[pos:m.start()]
            if "\n" in gap:
                parts.append("\n")
            elif " " in gap:
                parts.append(" ")
            parts.append(html_lib.unescape(m.group(1)))
            pos = m.end()

        trailing_gap = pxml[pos:]
        if "\n" in trailing_gap:
            parts.append("\n")
        elif " " in trailing_gap:
            parts.append(" ")

        text = "".join(parts)
        # Normalize within the paragraph but keep internal line breaks.
        lines = [" ".join(l.split()) for l in text.split("\n")]
        text = "\n".join(l for l in lines if l).strip()

        if text:
            paragraphs.append({"text": text, "style_id": style_id})

    return paragraphs


def _extract_docx_paragraphs_v1(path: str | Path) -> List[str]:
    """Backward-compat: plain-text paragraph list."""
    return [p["text"] for p in _extract_docx_paragraphs_v2(path)]


def _extract_docx_headings_v2(paragraphs: List[Dict[str, Any]]) -> tuple[List[str], str]:
    """Style-based heading extraction with heuristic fallback.

    Returns (headings, method). Style-based results are preferred; the old
    guess-by-shape heuristic only applies when the document has NO heading
    styles at all, and is labeled as such so downstream can trust
    `method == 'style_based'` results more.
    """
    styled = [
        p["text"]
        for p in paragraphs
        if _docx_style_is_heading(p.get("style_id") or "")
    ]
    if styled:
        return styled[:25], "style_based"

    heuristic: List[str] = []
    for p in paragraphs:
        text = p["text"]
        words = text.split()
        if len(words) <= 12 and len(text) <= 90:
            if text[:1].isupper() and not text.endswith("."):
                heuristic.append(text)

    return heuristic[:25], "heuristic_fallback"


def _extract_docx_headings_v1(paragraphs: List[str]) -> List[str]:
    """Backward-compat wrapper over the old heuristic signature."""
    wrapped = [{"text": t, "style_id": ""} for t in paragraphs]
    headings, _ = _extract_docx_headings_v2(wrapped)
    return headings


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
        paragraphs = _extract_docx_paragraphs_v2(p)
        # Paragraphs joined with a BLANK line: each Word paragraph is a
        # paragraph boundary downstream.
        normalized_text = _normalize_upload_text_v2(
            "\n\n".join(par["text"] for par in paragraphs)
        )
        headings, heading_method = _extract_docx_headings_v2(paragraphs)

        if not normalized_text:
            result = build_empty_upload_result(p, status="empty_text", confidence=0.0)
            result.metadata["paragraph_count"] = len(paragraphs)
            result.metadata["heading_count"] = len(headings)
            return result

        confidence = 0.92 if heading_method == "style_based" else 0.88

        return UploadExtractionResult(
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
                "heading_method": heading_method,
                "method": "zipfile_word_document_xml_v2",
            },
            extraction_status="success",
            extraction_confidence=confidence,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    except KeyError:
        result = build_empty_upload_result(p, status="invalid_docx", confidence=0.0)
        result.metadata["error"] = "word/document.xml not found in DOCX archive."
        return result

    except Exception as exc:
        result = build_empty_upload_result(p, status="extraction_error", confidence=0.0)
        result.metadata["error"] = str(exc)
        return result


# ---------------------------------------------------------------------------
# Router / batch / artifacts
# ---------------------------------------------------------------------------

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
    return [extract_upload_document_v1(path) for path in paths]


def write_upload_extraction_artifact_v1(
    result: UploadExtractionResult,
    output_dir: str | Path | None = None,
) -> Path:
    import json
    import hashlib

    # FIX: default anchored to the package instead of a CWD-relative
    # "backend/server/data/..." string.
    out_dir = Path(output_dir) if output_dir is not None else DEFAULT_EXTRACTION_ARTIFACT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    source_key = hashlib.sha256(result.source_path.encode("utf-8")).hexdigest()[:16]
    safe_type = result.source_type.replace("/", "_").replace("\\", "_")
    filename = f"{safe_type}_{source_key}.json"
    out_path = out_dir / filename

    payload = serialize_upload_extraction_result(result)
    payload["artifact_type"] = "upload_extraction_result"
    payload["artifact_version"] = "v1"
    payload["written_at"] = datetime.now(timezone.utc).isoformat()

    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out_path)
    return out_path


def write_upload_extraction_batch_artifacts_v1(
    results: List[UploadExtractionResult],
    output_dir: str | Path | None = None,
) -> List[Path]:
    return [
        write_upload_extraction_artifact_v1(result, output_dir=output_dir)
        for result in results
    ]


def explain_upload_document_extractor_v1() -> Dict[str, Any]:
    return {
        "phase": "4.4.1",
        "module": "upload_document_extractor.py",
        "status": "created",
        "responsibility": "Provide the foundation module for uploaded document extraction.",
        "supported_extensions": sorted(SUPPORTED_UPLOAD_EXTENSIONS.keys()),
        "contract": {
            "paragraph_boundaries": "blank lines (\\n\\n) in extracted text",
            "docx_headings": "style-based (Heading1-6/Title), heuristic fallback",
            "paths": "anchored to backend/server, not process CWD",
        },
        "current_capabilities": [
            "Detect upload source type from file extension",
            "Extract readable text from TXT uploads (paragraphs preserved)",
            "Extract headings and readable text from Markdown uploads",
            "Extract title, headings, and readable text from HTML uploads",
            "Extract readable text from DOCX uploads using document.xml",
            "Style-based DOCX heading detection with heuristic fallback",
            "Route uploaded files to the correct extractor automatically",
            "Batch-extract multiple uploaded documents",
            "Write upload extraction artifacts as JSON (atomic writes)",
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