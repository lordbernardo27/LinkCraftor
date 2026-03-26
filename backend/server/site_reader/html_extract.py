# backend/server/site_reader/html_extract.py
from __future__ import annotations

import re
from html import unescape
from typing import List, Tuple


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Remove script/style/noscript (and their contents)
_DROP_BLOCKS_RE = re.compile(
    r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"
)

# Very light heading capture
_H1_RE = re.compile(r"(?is)<h1[^>]*>(.*?)</h1>")
_H2_RE = re.compile(r"(?is)<h2[^>]*>(.*?)</h2>")
_H3_RE = re.compile(r"(?is)<h3[^>]*>(.*?)</h3>")


def _clean_html_fragment(s: str) -> str:
    """Strip tags, unescape entities, collapse whitespace."""
    if not s:
        return ""
    s = _DROP_BLOCKS_RE.sub(" ", s)
    s = _TAG_RE.sub(" ", s)
    s = unescape(s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def extract_headings_and_body(html: str) -> Tuple[str, List[str], List[str], str]:
    """
    Extract: first H1, all H2, all H3, and overall body text (plain).
    No external libraries.
    """
    raw = html or ""
    # remove dropped blocks early
    scrubbed = _DROP_BLOCKS_RE.sub(" ", raw)

    h1s = [_clean_html_fragment(m) for m in _H1_RE.findall(scrubbed)]
    h2s = [_clean_html_fragment(m) for m in _H2_RE.findall(scrubbed)]
    h3s = [_clean_html_fragment(m) for m in _H3_RE.findall(scrubbed)]

    h1 = next((x for x in h1s if x), "")
    h2 = [x for x in h2s if x]
    h3 = [x for x in h3s if x]

    body_text = _clean_html_fragment(scrubbed)

    # prevent absurd payloads
    if len(body_text) > 20000:
        body_text = body_text[:20000].rstrip()

    return h1, h2, h3, body_text
