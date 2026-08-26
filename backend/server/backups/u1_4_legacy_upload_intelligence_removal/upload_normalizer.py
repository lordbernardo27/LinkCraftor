from __future__ import annotations

import html as html_lib
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List


def _ext_of(path: str) -> str:
    return Path(path or "").suffix.lower().strip()


def _read_text_loose(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="utf-8", errors="ignore")


def _paragraphs_from_text(text: str) -> List[str]:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
    return blocks


def _text_to_html(text: str) -> str:
    blocks = _paragraphs_from_text(text)
    if not blocks:
        return ""
    return "\n".join(f"<p>{html_lib.escape(block)}</p>" for block in blocks)


def _markdown_to_html(md: str) -> str:
    blocks = _paragraphs_from_text(md)
    if not blocks:
        return ""
    return "\n".join(f"<p>{html_lib.escape(block)}</p>" for block in blocks)


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path, "r") as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")

    paragraphs = re.findall(r"<w:p[\s\S]*?</w:p>", xml)
    blocks: List[str] = []

    for para in paragraphs:
        para = re.sub(r"<w:tab[^>]*/>", " ", para)
        para = re.sub(r"<w:br[^>]*/>", "\n", para)

        text_parts = re.findall(r"<w:t[^>]*>([\s\S]*?)</w:t>", para)
        text = "".join(text_parts)
        text = html_lib.unescape(text)

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        if text:
            blocks.append(text)

    return "\n\n".join(blocks).strip()


def normalize_upload(path: str) -> Dict[str, Any]:
    fp = Path(path)

    if not fp.exists():
        return {
            "ok": False,
            "reason": "file not found",
            "path": str(fp),
        }

    ext = _ext_of(str(fp))

    try:
        if ext in {".html", ".htm"}:
            html = _read_text_loose(fp)
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()

            return {
                "ok": True,
                "format": "html",
                "path": str(fp),
                "html": html,
                "text": text,
                "paragraphs": _paragraphs_from_text(text),
            }

        if ext == ".md":
            raw = _read_text_loose(fp)
            html = _markdown_to_html(raw)
            text = re.sub(r"\s+", " ", raw).strip()

            return {
                "ok": True,
                "format": "md",
                "path": str(fp),
                "html": html,
                "text": text,
                "paragraphs": _paragraphs_from_text(raw),
            }

        if ext == ".txt":
            raw = _read_text_loose(fp)
            html = _text_to_html(raw)
            text = re.sub(r"\s+", " ", raw).strip()

            return {
                "ok": True,
                "format": "txt",
                "path": str(fp),
                "html": html,
                "text": text,
                "paragraphs": _paragraphs_from_text(raw),
            }

        if ext == ".docx":
            raw = _extract_docx_text(fp)
            html = _text_to_html(raw)
            text = re.sub(r"\s+", " ", raw).strip()

            return {
                "ok": True,
                "format": "docx",
                "path": str(fp),
                "html": html,
                "text": text,
                "paragraphs": _paragraphs_from_text(raw),
            }

        return {
            "ok": False,
            "reason": f"unsupported extension: {ext or 'none'}",
            "path": str(fp),
        }

    except Exception as e:
        return {
            "ok": False,
            "reason": f"normalize failed: {e}",
            "path": str(fp),
        }