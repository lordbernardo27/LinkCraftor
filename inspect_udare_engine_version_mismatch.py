from __future__ import annotations

import inspect
import json
from pathlib import Path


from backend.server.workers import (
    udare_reconstruction_worker
    as worker
)


RAW_STORE_PATH = Path(
    "backend/server/data/raw_website_html/"
    "raw_website_html_ws_whattoexpect_com.json"
)


store = json.loads(
    RAW_STORE_PATH.read_text(
        encoding="utf-8",
        errors="replace",
    )
)

pages = store.get("pages") or {}

if not isinstance(pages, dict) or not pages:
    raise RuntimeError(
        "Raw HTML Store pages are missing."
    )


html_id, record = next(
    iter(
        pages.items()
    )
)

source_url = str(
    record.get("source_url")
    or record.get("url")
    or record.get("canonical_url")
    or record.get("final_url")
    or ""
)

title = str(
    record.get("title")
    or record.get("page_title")
    or record.get("source_title")
    or ""
)

raw_html = str(
    record.get("raw_html")
    or record.get("html")
    or record.get("html_text")
    or record.get("source_html")
    or ""
)


if not raw_html.strip():
    raise RuntimeError(
        f"Selected raw record has no HTML: {html_id}"
    )


print()
print("=" * 100)
print("UDARE ENGINE VERSION INSPECTION")
print("=" * 100)

print()
print("WORKER EXPECTATION")
print("  UDARE_ENGINE:", worker.UDARE_ENGINE)

print()
print("DEFAULT ENGINE FUNCTION")
print(
    inspect.getsource(
        worker._default_reconstruction_engine_v1
    )
)

print()
print("RUNNING ONE DIRECT RECONSTRUCTION CALL")

result = worker._default_reconstruction_engine_v1(
    html_text=raw_html,
    source_url=source_url,
    title=title,
    metadata={
        "inspection": True,
        "html_id": html_id,
    },
)

if not isinstance(result, dict):
    raise RuntimeError(
        f"Reconstruction result is not a dict: {type(result)}"
    )


print()
print("RETURNED VALUES")
print("  ok:", result.get("ok"))
print("  engine:", repr(result.get("engine")))
print("  url:", result.get("url"))
print("  title:", result.get("title"))
print("  content_blocks:", len(result.get("content_blocks") or []))

print()
print("COMPARISON")
print(
    "  exact_match:",
    str(result.get("engine") or "")
    == worker.UDARE_ENGINE,
)

print()
print("=" * 100)
print("ENGINE VERSION INSPECTION: COMPLETE")
print("=" * 100)

print("No queue was modified.")
print("No UDARE Store write was performed.")
