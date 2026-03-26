# backend/server/engine/extract_rb2.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re
import html as _html


# ============================================================
# RB2 Document Extraction Contract — v1 (FROZEN)
# - headings: H1–H4 with paraStart/paraEnd mapping
# - paragraphs: scan units (p, list items, table rows)
# - joinedText: "\n\n" separator
# - charStart/charEnd: offsets in joinedText
# - headingCtx per paragraph (nearest active H1–H4)
# - norm + tokens per paragraph
# ============================================================

_VERSION = "rb2.extract.v1"

_ws = re.compile(r"\s+")
_nbsp = re.compile(r"\u00A0|&nbsp;?", re.IGNORECASE)

# normalize “smart” punctuation minimally (non-destructive)
_SMART = {
    "\u2018": "'", "\u2019": "'",  # single quotes
    "\u201C": '"', "\u201D": '"',  # double quotes
    "\u2013": "-", "\u2014": "-",  # en/em dashes
    "\u2212": "-",                 # minus sign
}

def _norm_minimal(s: str) -> str:
    """Lowercase, trim, collapse whitespace, normalize smart quotes/hyphens. No punctuation stripping."""
    if s is None:
        s = ""
    s = str(s)
    # html entities -> text (e.g. &amp;)
    s = _html.unescape(s)
    # nbsp -> space
    s = _nbsp.sub(" ", s)
    # normalize smart punctuation
    if s:
        s = "".join(_SMART.get(ch, ch) for ch in s)
    # collapse whitespace
    s = _ws.sub(" ", s).strip().lower()
    return s

def _clean_text(s: str) -> str:
    """Display-safe plain text for paragraphs/headings (keeps punctuation, keeps case as-is)."""
    if s is None:
        s = ""
    s = str(s)
    s = _html.unescape(s)
    s = _nbsp.sub(" ", s)
    if s:
        s = "".join(_SMART.get(ch, ch) for ch in s)
    # collapse whitespace but preserve casing
    s = _ws.sub(" ", s).strip()
    return s

def _tokens_from_norm(norm: str) -> List[str]:
    if not norm:
        return []
    # split on whitespace; do NOT remove stopwords here (frozen)
    return [t for t in norm.split(" ") if t]

def _strip_list_prefix(text: str) -> str:
    """
    Remove deterministic list prefixes like:
    - "•", "-", "*", "1.", "1)", "(1)"
    Contract: markers removed from `text`.
    """
    t = text.strip()
    t = re.sub(r"^(?:[\u2022\-\*•]+)\s+", "", t)          # bullets
    t = re.sub(r"^(?:\(?\d+\)?[.)])\s+", "", t)           # 1.  1)  (1)
    t = re.sub(r"^(?:[a-zA-Z][.)])\s+", "", t)            # a) a.
    return t.strip()


# ------------------------------
# HTML extraction (preferred)
# ------------------------------

def extract_rb2_contract_from_html(doc_id: str, html: str) -> Dict[str, Any]:
    """
    Convert HTML to RB2 extraction contract.
    Paragraph units:
      - <p> blocks
      - <li> list items (each item is a paragraph)
      - <tr> table rows => one paragraph joined by " | " of cell texts
    Headings:
      - <h1>..<h4>
    """
    html = html or ""
    # Try BeautifulSoup if available; fall back to minimal parser otherwise.
    soup = None
    try:
        from bs4 import BeautifulSoup  # type: ignore
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        soup = None

    if soup is None:
        # Minimal fallback: strip tags for a single paragraph blob (still deterministic),
        # but headings and table/list fidelity require bs4.
        # We keep the contract valid but less rich.
        text = _clean_text(re.sub(r"<[^>]+>", " ", html))
        return extract_rb2_contract_from_plaintext(doc_id, text)

    # Walk the DOM in document order, collecting headings + paragraph units.
    # We treat <p>, <li>, and <tr> as paragraph units.
    paragraphs_text: List[str] = []
    paragraph_heading_ctx: List[Dict[str, Optional[str]]] = []

    # Track active heading texts (original casing)
    active: Dict[int, Optional[str]] = {1: None, 2: None, 3: None, 4: None}

    headings: List[Dict[str, Any]] = []
    # We'll store heading positions (paraStart set later when we see the first paragraph after it)
    pending_heading_indices: List[int] = []

    def current_heading_ctx() -> Dict[str, Optional[str]]:
        return {
            "h1": active[1],
            "h2": active[2],
            "h3": active[3],
            "h4": active[4],
        }

    def register_heading(level: int, text_raw: str) -> None:
        nonlocal headings, pending_heading_indices
        text = _clean_text(text_raw)
        if not text:
            return
        # update active stack:
        active[level] = text
        for lv in range(level + 1, 5):
            active[lv] = None

        headings.append({
            "level": int(level),
            "text": text,
            "norm": _norm_minimal(text),
            # paraStart/paraEnd filled later
            "paraStart": None,
            "paraEnd": None,
        })
        pending_heading_indices.append(len(headings) - 1)

    def register_paragraph(text_raw: str, is_list_item: bool = False) -> None:
        nonlocal paragraphs_text, paragraph_heading_ctx, pending_heading_indices
        text = _clean_text(text_raw)
        if is_list_item:
            text = _strip_list_prefix(text)
        if not text:
            return

        # When we add the first paragraph after headings, set paraStart for any pending headings
        para_i = len(paragraphs_text)
        for hi in pending_heading_indices:
            if headings[hi].get("paraStart") is None:
                headings[hi]["paraStart"] = para_i
        # Once a paragraph is registered, those headings are no longer "pending"
        pending_heading_indices = [hi for hi in pending_heading_indices if headings[hi].get("paraStart") is None]

        paragraphs_text.append(text)
        paragraph_heading_ctx.append(current_heading_ctx())

    # We need document-order traversal. BeautifulSoup doesn't guarantee .descendants order with filtering,
    # so we use .find_all(True) and rely on the parse tree order.
    for el in soup.find_all(True):
        tag = (el.name or "").lower()

        # Headings
        if tag in ("h1", "h2", "h3", "h4"):
            lvl = int(tag[1])
            register_heading(lvl, el.get_text(" ", strip=True))
            continue

        # Paragraphs
        if tag == "p":
            register_paragraph(el.get_text(" ", strip=True))
            continue

        # List items => paragraphs
        if tag == "li":
            register_paragraph(el.get_text(" ", strip=True), is_list_item=True)
            continue

        # Tables: each row => one paragraph joined by " | "
        if tag == "tr":
            # gather cell texts from direct or nested cells
            cells = el.find_all(["th", "td"])
            parts = []
            for c in cells:
                ct = _clean_text(c.get_text(" ", strip=True))
                if ct:
                    parts.append(ct)
            if parts:
                register_paragraph(" | ".join(parts))
            continue

    # Finalize heading ranges: paraEnd for each heading
    # Rule: a heading applies from its paraStart to the paragraph before the next heading of same or higher level.
    # We do this deterministically in one pass.
    _finalize_heading_ranges(headings=headings, para_count=len(paragraphs_text))

    # docH1 is the first H1 if present; else None
    doc_h1_text = None
    for h in headings:
        if h.get("level") == 1 and h.get("text"):
            doc_h1_text = h["text"]
            break

    # Build joinedText and char ranges
    joined_text, ranges = _build_joined_and_ranges(paragraphs_text)

    # Build paragraph objects
    paragraphs: List[Dict[str, Any]] = []
    for i, text in enumerate(paragraphs_text):
        norm = _norm_minimal(text)
        tokens = _tokens_from_norm(norm)
        char_start, char_end = ranges[i]
        paragraphs.append({
            "i": i,
            "text": text,
            "norm": norm,
            "tokens": tokens,
            "charStart": char_start,
            "charEnd": char_end,
            "headingCtx": paragraph_heading_ctx[i],
        })

    return {
        "docId": str(doc_id),
        "headings": headings,
        "docH1": {"text": doc_h1_text or "", "norm": _norm_minimal(doc_h1_text or "")},
        "paragraphs": paragraphs,
        "joinedText": joined_text,
        "version": _VERSION,
    }


def extract_rb2_contract_from_plaintext(doc_id: str, text: str) -> Dict[str, Any]:
    """
    Fallback extractor from plaintext (no real headings).
    Paragraphs are split on blank lines.
    """
    raw = text or ""
    raw = _html.unescape(raw)
    raw = _nbsp.sub(" ", raw)

    # Paragraph split: blank lines -> paragraph boundary
    blocks = [b.strip() for b in re.split(r"\n\s*\n+", raw) if b.strip()]
    if not blocks:
        blocks = [raw.strip()] if raw.strip() else []

    # No headings detected
    headings: List[Dict[str, Any]] = []
    doc_h1_text = ""

    joined_text, ranges = _build_joined_and_ranges([_clean_text(b) for b in blocks])

    paragraphs: List[Dict[str, Any]] = []
    for i, b in enumerate(blocks):
        t = _clean_text(b)
        n = _norm_minimal(t)
        paragraphs.append({
            "i": i,
            "text": t,
            "norm": n,
            "tokens": _tokens_from_norm(n),
            "charStart": ranges[i][0],
            "charEnd": ranges[i][1],
            "headingCtx": {"h1": None, "h2": None, "h3": None, "h4": None},
        })

    return {
        "docId": str(doc_id),
        "headings": headings,
        "docH1": {"text": doc_h1_text, "norm": _norm_minimal(doc_h1_text)},
        "paragraphs": paragraphs,
        "joinedText": joined_text,
        "version": _VERSION,
    }


# ------------------------------
# Helpers
# ------------------------------

def _build_joined_and_ranges(paras: List[str]) -> Tuple[str, List[Tuple[int, int]]]:
    """
    joinedText = para0 + "\n\n" + para1 + ...
    ranges[i] = (charStart, charEnd) in joinedText (charEnd exclusive)
    """
    ranges: List[Tuple[int, int]] = []
    parts: List[str] = []
    offset = 0
    for i, p in enumerate(paras):
        if i > 0:
            parts.append("\n\n")
            offset += 2
        start = offset
        parts.append(p)
        offset += len(p)
        end = offset
        ranges.append((start, end))
    return "".join(parts), ranges


def _finalize_heading_ranges(headings: List[Dict[str, Any]], para_count: int) -> None:
    """
    Fill paraEnd for each heading with a paraStart.
    If a heading has no paraStart (no paragraphs after it), set paraStart=paraEnd=para_count (empty range).
    """
    # 1) Ensure every heading has paraStart and a default paraEnd
    for h in headings:
        if h.get("paraStart") is None:
            # no paragraph under heading
            h["paraStart"] = para_count
            h["paraEnd"] = para_count
        else:
            # paraStart can be 0, so do NOT use `or`
            h["paraEnd"] = (para_count - 1) if para_count > 0 else 0

    # 2) Tighten based on next heading of same-or-higher level
    for idx, h in enumerate(headings):
        level = int(h.get("level") or 1)

        start = int(h["paraStart"])  # safe now
        end = int(h["paraEnd"])

        # find next heading with level <= current level
        next_start: Optional[int] = None
        for j in range(idx + 1, len(headings)):
            hj = headings[j]
            lvl_j = int(hj.get("level") or 1)
            if lvl_j <= level:
                ns = int(hj["paraStart"])  # safe now
                next_start = ns
                break

        if next_start is not None:
            # heading's range ends before the next same-or-higher heading begins
            if para_count > 0:
                end = max(start, next_start - 1)
            else:
                end = start

        h["paraStart"] = start
        h["paraEnd"] = end



# ------------------------------
# Small self-test (optional)
# ------------------------------
if __name__ == "__main__":
    demo_html = """
    <h1>Pregnancy Due Date</h1>
    <p>Most people use a due date calculator.</p>
    <h2>Methods</h2>
    <ul>
      <li>Last menstrual period (LMP)</li>
      <li>Conception date</li>
    </ul>
    <table>
      <tr><th>Cycle length</th><th>Effect</th></tr>
      <tr><td>24 days</td><td>Earlier ovulation</td></tr>
    </table>
    """
    out = extract_rb2_contract_from_html("doc_demo", demo_html)
    import json
    print(json.dumps(out, indent=2))
