from __future__ import annotations

import json
from pathlib import Path

from backend.server.jobs.universal_knowledge_orchestrator import (
    queue_path,
    read_queue,
)


WORKSPACE_ID = "ws_whattoexpect_com"
JOB_TYPE = "udare_reconstruction"

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

ARTICLES_DIR = STORE_ROOT / "articles"
REVIEWS_DIR = STORE_ROOT / "reviews"
METADATA_DIR = STORE_ROOT / "metadata"

PROGRESS_PATH = Path(
    "backend/server/data/runtime/"
    "udare_phase_4_3b_full_population/"
    "phase_4_3b_progress.json"
)


queue_rows = read_queue(
    WORKSPACE_ID,
    limit=100000,
)

udare_queue = [
    row
    for row in queue_rows
    if str(
        row.get("job_type")
        or row.get("stage")
        or ""
    ).strip()
    == JOB_TYPE
]

queued_udare = [
    row
    for row in udare_queue
    if str(
        row.get("status")
        or ""
    ).strip()
    == "queued"
]

article_files = sorted(
    ARTICLES_DIR.glob("*.html")
) if ARTICLES_DIR.is_dir() else []

review_files = sorted(
    REVIEWS_DIR.glob("*.html")
) if REVIEWS_DIR.is_dir() else []

metadata_files = sorted(
    METADATA_DIR.glob("*.json")
) if METADATA_DIR.is_dir() else []


article_document_ids = set()
review_document_ids = set()
metadata_document_ids = set()

metadata_without_article = []
metadata_without_review = []
invalid_metadata = []

for metadata_path in metadata_files:
    try:
        record = json.loads(
            metadata_path.read_text(
                encoding="utf-8",
                errors="strict",
            )
        )

        if not isinstance(record, dict):
            raise ValueError(
                "Metadata root is not an object."
            )

        document_id = str(
            record.get("document_id")
            or ""
        ).strip()

        if document_id:
            metadata_document_ids.add(
                document_id
            )

        article_relative = str(
            (
                record.get("article_document")
                or {}
            ).get("relative_path")
            or ""
        ).replace("\\", "/").strip()

        review_relative = str(
            (
                record.get("review_document")
                or {}
            ).get("relative_path")
            or ""
        ).replace("\\", "/").strip()

        if article_relative:
            article_path = (
                STORE_ROOT
                / Path(article_relative)
            )

            if article_path.is_file():
                article_document_ids.add(
                    document_id
                )
            else:
                metadata_without_article.append({
                    "metadata":
                        str(metadata_path),

                    "document_id":
                        document_id,

                    "article_path":
                        str(article_path),
                })

        else:
            metadata_without_article.append({
                "metadata":
                    str(metadata_path),

                "document_id":
                    document_id,

                "article_path":
                    "",
            })

        if review_relative:
            review_path = (
                STORE_ROOT
                / Path(review_relative)
            )

            if review_path.is_file():
                review_document_ids.add(
                    document_id
                )
            else:
                metadata_without_review.append({
                    "metadata":
                        str(metadata_path),

                    "document_id":
                        document_id,

                    "review_path":
                        str(review_path),
                })

        else:
            metadata_without_review.append({
                "metadata":
                    str(metadata_path),

                "document_id":
                    document_id,

                "review_path":
                    "",
            })

    except Exception as exc:
        invalid_metadata.append({
            "path":
                str(metadata_path),

            "error":
                f"{type(exc).__name__}: {exc}",
        })


queue_html_ids = {
    str(
        (
            row.get("payload")
            or {}
        ).get("html_id")
        or ""
    )
    for row in queued_udare
}

queue_job_ids = {
    str(
        row.get("job_id")
        or ""
    )
    for row in queued_udare
}


progress = {}

if PROGRESS_PATH.is_file():
    try:
        progress = json.loads(
            PROGRESS_PATH.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )
    except Exception as exc:
        progress = {
            "_read_error":
                f"{type(exc).__name__}: {exc}"
        }


print()
print("=" * 112)
print("PHASE 4.3B RESUME-STATE INSPECTION")
print("=" * 112)

print()
print("ACTIVE QUEUE")
print("  Path:", queue_path(WORKSPACE_ID))
print("  Total queue rows:", len(queue_rows))
print("  UDARE rows:", len(udare_queue))
print("  Queued UDARE rows:", len(queued_udare))
print("  Unique UDARE job IDs:", len(queue_job_ids))
print("  Unique queued HTML IDs:", len(queue_html_ids))

print()
print("UDARE STORE")
print("  Reader HTML files:", len(article_files))
print("  Review HTML files:", len(review_files))
print("  Metadata JSON files:", len(metadata_files))
print("  Valid metadata document IDs:", len(metadata_document_ids))
print("  Metadata with article file:", len(article_document_ids))
print("  Metadata with review file:", len(review_document_ids))

print()
print("TOTALS")
print(
    "  Reader files + queued jobs:",
    len(article_files) + len(queued_udare),
)

print(
    "  Metadata files + queued jobs:",
    len(metadata_files) + len(queued_udare),
)

print(
    "  Review files + queued jobs:",
    len(review_files) + len(queued_udare),
)

print()
print("INCONSISTENCIES")
print(
    "  Metadata without reader article:",
    len(metadata_without_article),
)

print(
    "  Metadata without review document:",
    len(metadata_without_review),
)

print(
    "  Invalid metadata files:",
    len(invalid_metadata),
)

print()
print("LAST SAVED PHASE 4.3B PROGRESS")

if progress:
    print(
        "  Batches completed:",
        progress.get("batches_completed"),
    )

    print(
        "  Total executed:",
        progress.get("total_executed"),
    )

    print(
        "  Total successful:",
        progress.get("total_successful"),
    )

    print(
        "  Total failed:",
        progress.get("total_failed"),
    )

    print(
        "  Queue remaining:",
        progress.get("queued_udare_remaining"),
    )

    print(
        "  Reader articles:",
        progress.get("reader_articles"),
    )

    print(
        "  Visual reviews:",
        progress.get("visual_reviews"),
    )

    print(
        "  Metadata records:",
        progress.get("metadata_records"),
    )

else:
    print("  No progress report found.")

if metadata_without_article:
    print()
    print("FIRST METADATA RECORDS WITHOUT ARTICLES")

    for item in metadata_without_article[:10]:
        print("  -", item)

if metadata_without_review:
    print()
    print("FIRST METADATA RECORDS WITHOUT REVIEWS")

    for item in metadata_without_review[:10]:
        print("  -", item)

if invalid_metadata:
    print()
    print("FIRST INVALID METADATA RECORDS")

    for item in invalid_metadata[:10]:
        print("  -", item)

print()
print("=" * 112)
print("RESUME-STATE INSPECTION: COMPLETE")
print("=" * 112)

print("No queue, article, review, metadata or manifest was modified.")
