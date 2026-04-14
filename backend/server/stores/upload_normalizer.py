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
    lines = (md or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: List[str] = []
    para_buf: List[str] = []

    def flush_para() -> None:
        nonlocal para_buf
        if para_buf:
            text = " ".join(x.strip() for x in para_buf if x.strip()).strip()
            if text:
                out.append(f"<p>{html_lib.escape(text)}</p>")
            para_buf = []

    for raw in lines:
        line = raw.strip()

        if not line:
            flush_para()
            continue

        if line.startswith("### "):
            flush_para()
            out.append(f"<h3>{html_lib.escape(line[4:].strip())}</h3>")
            continue

        if line.startswith("## "):
            flush_para()
            out.append(f"<h2>{html_lib.escape(line[3:].strip())}</h2>")
            continue

        if line.startswith("# "):
            flush_para()
            out.append(f"<h1>{html_lib.escape(line[2:].strip())}</h1>")
            continue

        if line.startswith(("- ", "* ")):
            flush_para()
            out.append(f"<li>{html_lib.escape(line[2:].strip())}</li>")
            continue

        para_buf.append(line)

    flush_para()

    if any(x.startswith("<li>") for x in out):
        grouped: List[str] = []
        li_buf: List[str] = []
        for item in out:
            if item.startswith("<li>"):
                li_buf.append(item)
            else:
                if li_buf:
                    grouped.append("<ul>\n" + "\n".join(li_buf) + "\n</ul>")
                    li_buf = []
                grouped.append(item)
        if li_buf:
            grouped.append("<ul>\n" + "\n".join(li_buf) + "\n</ul>")
        out = grouped

    return "\n".join(out)


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path, "r") as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")

    xml = re.sub(r"</w:p>", "\n\n", xml)
    xml = re.sub(r"</w:tr>", "\n", xml)
    xml = re.sub(r"<w:tab[^>]*/>", " ", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    xml = re.sub(r"\n{3,}", "\n\n", xml)
    xml = re.sub(r"[ \t]+", " ", xml)
    return xml.strip()


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