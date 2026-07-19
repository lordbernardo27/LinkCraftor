from __future__ import annotations

import json
import re
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

INDEX_PATH = (
    STORE_ROOT
    / "index.html"
)

ARTICLES_DIR = (
    STORE_ROOT
    / "articles"
)

METADATA_DIR = (
    STORE_ROOT
    / "metadata"
)

WORKER_PATH = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)


if not INDEX_PATH.is_file():
    raise RuntimeError(
        f"Index does not exist: {INDEX_PATH}"
    )


index_text = INDEX_PATH.read_text(
    encoding="utf-8",
    errors="strict",
)

metadata_files = sorted(
    METADATA_DIR.glob(
        "*.json"
    )
)

article_files = sorted(
    ARTICLES_DIR.glob(
        "*.html"
    )
)


hrefs = re.findall(
    r'class="open-button"\s+href="([^"]+)"',
    index_text,
    flags=re.MULTILINE,
)


resolved_links = [
    (
        STORE_ROOT
        / Path(
            href
        )
    )

    for href
    in hrefs
]


worker_text = WORKER_PATH.read_text(
    encoding="utf-8",
    errors="strict",
)


checks = {
    "index_exists":
        INDEX_PATH.is_file(),

    "index_is_html_document":
        index_text.lstrip().casefold().startswith(
            "<!doctype html>"
        ),

    "metadata_count_5":
        len(
            metadata_files
        )
        == 5,

    "article_count_5":
        len(
            article_files
        )
        == 5,

    "index_article_links_5":
        len(
            hrefs
        )
        == 5,

    "all_index_links_exist":
        len(
            resolved_links
        )
        == 5
        and all(
            path.is_file()

            for path
            in resolved_links
        ),

    "search_control_present":
        'id="search-input"'
        in index_text,

    "sort_control_present":
        'id="sort-select"'
        in index_text,

    "search_javascript_present":
        "searchInput.addEventListener"
        in index_text,

    "sort_javascript_present":
        "sortSelect.addEventListener"
        in index_text,

    "statistics_present":
        "Average Words"
        in index_text
        and "Largest Article"
        in index_text
        and "Smallest Article"
        in index_text,

    "worker_import_present":
        (
            "from backend.server.stores."
            "udare_store_index_builder "
            "import build_udare_store_index_v1"
        )
        in worker_text,

    "worker_call_present":
        (
            "build_udare_store_index_v1("
            in worker_text
            and "index_result"
            in worker_text
        ),
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


print()
print("=" * 108)
print(
    "PHASE 4.3C — UDARE CLICKABLE INDEX VERIFICATION"
)
print("=" * 108)

print(
    "UDARE Store:",
    STORE_ROOT,
)

print(
    "Index:",
    INDEX_PATH,
)

print(
    "Metadata records:",
    len(
        metadata_files
    ),
)

print(
    "HTML articles:",
    len(
        article_files
    ),
)

print(
    "Clickable article links:",
    len(
        hrefs
    ),
)

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print("=" * 108)

if failed:
    print(
        "PHASE 4.3C — UDARE CLICKABLE INDEX: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "PHASE 4.3C — UDARE CLICKABLE INDEX: PASS"
    )

print("=" * 108)

print(
    "No queue runner or worker was executed."
)

print(
    "No reconstruction was performed."
)

raise SystemExit(
    0
    if not failed
    else 1
)
