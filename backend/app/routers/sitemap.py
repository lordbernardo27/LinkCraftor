import logging
import re
from typing import List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
import xml.etree.ElementTree as ET

log = logging.getLogger("linkcraftor.sitemap")

router = APIRouter()

# ---------- Models ----------

class SitemapScanRequest(BaseModel):
    """
    Ask the backend to:
    1) Fetch a sitemap (XML or plain-text list)
    2) Extract up to max_urls URLs
    3) Fetch each page and return small text snippets
    """
    sitemap_url: HttpUrl = Field(..., description="URL to XML/TXT sitemap (or URL list)")
    max_urls: int = Field(30, ge=1, le=200, description="Maximum pages to fetch & summarize")


class PageSnippet(BaseModel):
    url: HttpUrl
    title: str = ""
    h1: str = ""
    snippet: str = ""  # short cleaned text from the page body


class SitemapScanResponse(BaseModel):
    pages: List[PageSnippet]


# ---------- Tiny HTML helpers (no heavy BeautifulSoup) ----------

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
H1_RE    = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TAG_RE   = re.compile(r"<[^>]+>")
WS_RE    = re.compile(r"\s+")


def _clean_html_text(html: str, limit_words: int = 60) -> str:
    """Strip tags and squash whitespace; keep first N words."""
    if not html:
        return ""
    text = TAG_RE.sub(" ", html)
    text = WS_RE.sub(" ", text).strip()
    parts = text.split(" ")
    if len(parts) > limit_words:
        parts = parts[:limit_words]
    return " ".join(parts)


def _extract_meta(html: str) -> tuple[str, str, str]:
    """Extract <title>, first <h1>, and a short text snippet from page HTML."""
    if not html:
        return "", "", ""

    title = ""
    h1 = ""

    m = TITLE_RE.search(html)
    if m:
        title = WS_RE.sub(" ", m.group(1)).strip()

    m = H1_RE.search(html)
    if m:
        h1 = WS_RE.sub(" ", m.group(1)).strip()

    snippet = _clean_html_text(html, limit_words=60)
    return title, h1, snippet


# ---------- Sitemap text → list of URLs ----------

def _parse_sitemap(text: str) -> List[str]:
    """
    Very tolerant parser:
    - If it looks like XML <urlset> or <sitemapindex>, parse <loc> tags
    - Otherwise, treat each non-empty line that starts with http(s) as a URL
    """
    text = text or ""
    urls: List[str] = []

    if "<urlset" in text or "<sitemapindex" in text:
        try:
            root = ET.fromstring(text)
            ns = ""
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"

            for loc in root.iter(f"{ns}loc"):
                u = (loc.text or "").strip()
                if u:
                    urls.append(u)
        except Exception as e:
            log.warning("Failed to parse XML sitemap: %s", e)
    else:
        # Plain-text list (one URL per line)
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("http://") or line.startswith("https://"):
                urls.append(line)

    return urls


# ---------- Endpoint: /sitemap/scan ----------

@router.post("/scan", response_model=SitemapScanResponse)
async def sitemap_scan(body: SitemapScanRequest):
    """
    1) Fetch the sitemap URL
    2) Extract URLs
    3) Fetch each page
    4) Return basic page snippets
    """
    # 1) Fetch sitemap
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(str(body.sitemap_url))
    except Exception as e:
        log.error("Failed to fetch sitemap %s: %s", body.sitemap_url, e)
        raise HTTPException(status_code=502, detail="Failed to fetch sitemap")

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Upstream error {resp.status_code} when fetching sitemap",
        )

    text = resp.text
    urls = _parse_sitemap(text)
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs found in sitemap")

    urls = urls[: body.max_urls]

    # 2) Fetch each page and build snippets
    pages: List[PageSnippet] = []

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for u in urls:
            html = ""
            try:
                page_resp = await client.get(u)
                if page_resp.status_code < 400:
                    html = page_resp.text
                else:
                    log.warning("Page %s returned status %s", u, page_resp.status_code)
            except Exception as e:
                log.warning("Failed to fetch page %s: %s", u, e)

            title, h1, snippet = _extract_meta(html)
            pages.append(PageSnippet(url=u, title=title, h1=h1, snippet=snippet))

    return SitemapScanResponse(pages=pages)
