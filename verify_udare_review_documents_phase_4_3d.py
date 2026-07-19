from __future__ import annotations

import json
import re
from pathlib import Path


WORKSPACE_ID = "ws_whattoexpect_com"

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

ARTICLES_DIR = (
    STORE_ROOT
    / "articles"
)

REVIEWS_DIR = (
    STORE_ROOT
    / "reviews"
)

METADATA_DIR = (
    STORE_ROOT
    / "metadata"
)

INDEX_PATH = (
    STORE_ROOT
    / "index.html"
)

WORKER_PATH = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)


article_files = sorted(
    ARTICLES_DIR.glob(
        "*.html"
    )
)

review_files = sorted(
    REVIEWS_DIR.glob(
        "*.html"
    )
)

metadata_files = sorted(
    METADATA_DIR.glob(
        "*.json"
    )
)

index_text = INDEX_PATH.read_text(
    encoding="utf-8",
    errors="strict",
)

worker_text = WORKER_PATH.read_text(
    encoding="utf-8",
    errors="strict",
)


metadata_records = [
    json.loads(
        path.read_text(
            encoding="utf-8",
            errors="strict",
        )
    )

    for path
    in metadata_files
]


review_links = re.findall(
    r'class="review-button"\s+href="([^"]+)"',
    index_text,
    flags=re.MULTILINE,
)


resolved_review_links = [
    STORE_ROOT
    / Path(
        link
    )

    for link
    in review_links
]


review_markers_ok = all(
    (
        "UDARE Visual Review"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and "Article Identity"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and "Extracted Heading Sequence"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and "Manual Review Checklist"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and "Image Evidence"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and "Reconstructed Article Body"
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
        and 'class="article-body"'
        in path.read_text(
            encoding="utf-8",
            errors="strict",
        )
    )

    for path
    in review_files
)


metadata_review_paths = [
    str(
        (
            record.get(
                "review_document"
            )
            or {}
        ).get(
            "relative_path"
        )
        or ""
    )

    for record
    in metadata_records
]


checks = {
    "reader_article_count_5":
        len(
            article_files
        )
        == 5,

    "review_document_count_5":
        len(
            review_files
        )
        == 5,

    "metadata_count_5":
        len(
            metadata_files
        )
        == 5,

    "all_metadata_has_review_document":
        len(
            metadata_review_paths
        )
        == 5
        and all(
            metadata_review_paths
        ),

    "all_review_metadata_paths_exist":
        all(
            (
                STORE_ROOT
                / Path(
                    relative_path
                )
            ).is_file()

            for relative_path
            in metadata_review_paths
        ),

    "review_documents_have_required_format":
        review_markers_ok,

    "index_review_links_5":
        len(
            review_links
        )
        == 5,

    "all_index_review_links_exist":
        len(
            resolved_review_links
        )
        == 5
        and all(
            path.is_file()

            for path
            in resolved_review_links
        ),

    "index_has_open_article":
        "Open Article"
        in index_text,

    "index_has_open_review":
        "Open Review"
        in index_text,

    "worker_review_import_present":
        (
            "from backend.server.stores."
            "udare_review_document_builder "
            "import build_udare_review_document_v1"
        )
        in worker_text,

    "worker_review_call_present":
        "build_udare_review_document_v1("
        in worker_text,

    "worker_review_before_index":
        worker_text.find(
            "build_udare_review_document_v1("
        )
        < worker_text.find(
            "build_udare_store_index_v1("
        ),
}


failed = [
    name

    for name, passed
    in checks.items()

    if not passed
]


print()
print("=" * 112)
print(
    "PHASE 4.3D — UDARE VISUAL REVIEW VERIFICATION"
)
print("=" * 112)

print(
    "Reader articles:",
    len(
        article_files
    ),
)

print(
    "Visual review documents:",
    len(
        review_files
    ),
)

print(
    "Metadata records:",
    len(
        metadata_files
    ),
)

print(
    "Index review links:",
    len(
        review_links
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
print("=" * 112)

if failed:
    print(
        "PHASE 4.3D — UDARE VISUAL REVIEWS: FAIL"
    )

    print(
        "Failed checks:",
        ", ".join(
            failed
        ),
    )

else:
    print(
        "PHASE 4.3D — UDARE VISUAL REVIEWS: PASS"
    )

print("=" * 112)

print(
    "No queue runner or reconstruction was executed."
)

raise SystemExit(
    0
    if not failed
    else 1
)
