from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


WORKSPACE_ID = "ws_whattoexpect_com"

STORE_ROOT = Path(
    "backend/server/data/udare_store"
) / WORKSPACE_ID

ARTICLES_DIR = STORE_ROOT / "articles"
REVIEWS_DIR = STORE_ROOT / "reviews"
METADATA_DIR = STORE_ROOT / "metadata"
INDEX_PATH = STORE_ROOT / "index.html"
MANIFEST_PATH = STORE_ROOT / "manifest.json"

REPORT_PATH = Path(
    "backend/server/data/runtime/"
    "udare_manifest_phase_4_3a5/"
    "udare_manifest_phase_4_3a5_report.json"
)

EXPECTED_COUNT = 5

MANIFEST_SCHEMA = "udare_store_manifest_v1"
STORE_VERSION = "udare_store_v1"


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8",
            errors="strict",
        )
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"JSON file is not an object: {path}"
        )

    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def write_json_atomic(
    path: Path,
    value: Dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(path)


if not STORE_ROOT.is_dir():
    raise RuntimeError(
        f"UDARE Store does not exist: {STORE_ROOT}"
    )

if not ARTICLES_DIR.is_dir():
    raise RuntimeError(
        f"UDARE articles directory is missing: {ARTICLES_DIR}"
    )

if not REVIEWS_DIR.is_dir():
    raise RuntimeError(
        f"UDARE reviews directory is missing: {REVIEWS_DIR}"
    )

if not METADATA_DIR.is_dir():
    raise RuntimeError(
        f"UDARE metadata directory is missing: {METADATA_DIR}"
    )

if not INDEX_PATH.is_file():
    raise RuntimeError(
        f"UDARE clickable index is missing: {INDEX_PATH}"
    )


metadata_files = sorted(
    METADATA_DIR.glob("*.json")
)

if len(metadata_files) != EXPECTED_COUNT:
    raise RuntimeError(
        "Expected five metadata records before full population, "
        f"found {len(metadata_files)}."
    )


records: List[Dict[str, Any]] = []

document_ids: set[str] = set()
html_ids: set[str] = set()
article_paths: set[str] = set()
review_paths: set[str] = set()

engines: set[str] = set()

total_words = 0
total_article_bytes = 0
total_review_bytes = 0
total_images = 0


for metadata_path in metadata_files:
    metadata = load_json(
        metadata_path
    )

    document_id = str(
        metadata.get("document_id")
        or ""
    ).strip()

    html_id = str(
        metadata.get("html_id")
        or ""
    ).strip()

    source_url = str(
        metadata.get("source_url")
        or ""
    ).strip()

    title = str(
        metadata.get("title")
        or metadata.get("h1")
        or ""
    ).strip()

    engine = str(
        metadata.get("udare_engine")
        or ""
    ).strip()

    article_document = (
        metadata.get("article_document")
        or {}
    )

    review_document = (
        metadata.get("review_document")
        or {}
    )

    content_integrity = (
        metadata.get("content_integrity")
        or {}
    )

    if not isinstance(article_document, dict):
        raise RuntimeError(
            f"Invalid article_document in {metadata_path}"
        )

    if not isinstance(review_document, dict):
        raise RuntimeError(
            f"Invalid review_document in {metadata_path}"
        )

    if not isinstance(content_integrity, dict):
        content_integrity = {}

    article_relative_path = str(
        article_document.get("relative_path")
        or ""
    ).replace("\\", "/").strip()

    review_relative_path = str(
        review_document.get("relative_path")
        or ""
    ).replace("\\", "/").strip()

    if not document_id:
        raise RuntimeError(
            f"Missing document_id in {metadata_path}"
        )

    if not html_id:
        raise RuntimeError(
            f"Missing html_id in {metadata_path}"
        )

    if not source_url:
        raise RuntimeError(
            f"Missing source_url in {metadata_path}"
        )

    if not article_relative_path:
        raise RuntimeError(
            f"Missing article path in {metadata_path}"
        )

    if not review_relative_path:
        raise RuntimeError(
            f"Missing review path in {metadata_path}"
        )

    article_path = (
        STORE_ROOT
        / Path(article_relative_path)
    )

    review_path = (
        STORE_ROOT
        / Path(review_relative_path)
    )

    if not article_path.is_file():
        raise RuntimeError(
            f"Missing reader article: {article_path}"
        )

    if not review_path.is_file():
        raise RuntimeError(
            f"Missing review document: {review_path}"
        )

    article_sha256 = sha256_file(
        article_path
    )

    review_sha256 = sha256_file(
        review_path
    )

    expected_article_sha256 = str(
        article_document.get("sha256")
        or ""
    ).strip()

    expected_review_sha256 = str(
        review_document.get("sha256")
        or ""
    ).strip()

    if (
        expected_article_sha256
        and article_sha256
        != expected_article_sha256
    ):
        raise RuntimeError(
            "Reader article SHA256 mismatch: "
            f"{article_path}"
        )

    if (
        expected_review_sha256
        and review_sha256
        != expected_review_sha256
    ):
        raise RuntimeError(
            "Review document SHA256 mismatch: "
            f"{review_path}"
        )

    if document_id in document_ids:
        raise RuntimeError(
            f"Duplicate document_id: {document_id}"
        )

    if html_id in html_ids:
        raise RuntimeError(
            f"Duplicate html_id: {html_id}"
        )

    if article_relative_path in article_paths:
        raise RuntimeError(
            f"Duplicate article path: {article_relative_path}"
        )

    if review_relative_path in review_paths:
        raise RuntimeError(
            f"Duplicate review path: {review_relative_path}"
        )

    document_ids.add(document_id)
    html_ids.add(html_id)
    article_paths.add(article_relative_path)
    review_paths.add(review_relative_path)

    if engine:
        engines.add(engine)

    word_count = int(
        content_integrity.get(
            "reader_body_word_count"
        )
        or 0
    )

    image_count = int(
        review_document.get(
            "image_count"
        )
        or 0
    )

    article_bytes = article_path.stat().st_size
    review_bytes = review_path.stat().st_size

    total_words += word_count
    total_images += image_count
    total_article_bytes += article_bytes
    total_review_bytes += review_bytes

    records.append({
        "document_id":
            document_id,

        "html_id":
            html_id,

        "source_url":
            source_url,

        "title":
            title,

        "h1":
            str(
                metadata.get("h1")
                or ""
            ),

        "udare_engine":
            engine,

        "reconstruction_status":
            str(
                metadata.get(
                    "reconstruction_status"
                )
                or ""
            ),

        "persistence_status":
            str(
                metadata.get(
                    "persistence_status"
                )
                or ""
            ),

        "article_document": {
            "format":
                str(
                    article_document.get(
                        "format"
                    )
                    or ""
                ),

            "relative_path":
                article_relative_path,

            "sha256":
                article_sha256,

            "byte_length":
                article_bytes,
        },

        "review_document": {
            "format":
                str(
                    review_document.get(
                        "format"
                    )
                    or ""
                ),

            "relative_path":
                review_relative_path,

            "sha256":
                review_sha256,

            "byte_length":
                review_bytes,

            "image_count":
                image_count,
        },

        "metadata": {
            "relative_path":
                metadata_path.relative_to(
                    STORE_ROOT
                ).as_posix(),

            "sha256":
                sha256_file(
                    metadata_path
                ),
        },

        "content_integrity": {
            "reader_body_word_count":
                word_count,

            "content_block_count":
                int(
                    content_integrity.get(
                        "content_block_count"
                    )
                    or 0
                ),
        },

        "created_at_utc":
            str(
                metadata.get(
                    "created_at_utc"
                )
                or ""
            ),

        "updated_at_utc":
            str(
                metadata.get(
                    "updated_at_utc"
                )
                or ""
            ),
    })


records.sort(
    key=lambda record: (
        str(
            record.get("title")
            or ""
        ).casefold(),
        str(
            record.get("document_id")
            or ""
        ),
    )
)


generated_at = utc_now()

manifest = {
    "schema_version":
        MANIFEST_SCHEMA,

    "store_version":
        STORE_VERSION,

    "workspace_id":
        WORKSPACE_ID,

    "generated_at_utc":
        generated_at,

    "record_count":
        len(records),

    "counts": {
        "reader_articles":
            len(article_paths),

        "visual_review_documents":
            len(review_paths),

        "metadata_records":
            len(metadata_files),

        "index_files":
            1,
    },

    "content_totals": {
        "reader_body_words":
            total_words,

        "retained_images":
            total_images,

        "reader_article_bytes":
            total_article_bytes,

        "visual_review_bytes":
            total_review_bytes,
    },

    "engines":
        sorted(engines),

    "canonical_downstream_source": {
        "field":
            "article_document.relative_path",

        "format":
            "udare_article_reader_document_v1",

        "purpose":
            (
                "Website Article Integrity, Article Validation, "
                "WUC, UUCD and semantic processing."
            ),
    },

    "audit_source": {
        "field":
            "review_document.relative_path",

        "format":
            "udare_visual_review_document_v1",

        "purpose":
            (
                "Human visual inspection, image review, "
                "certification and debugging."
            ),
    },

    "index": {
        "relative_path":
            "index.html",

        "sha256":
            sha256_file(
                INDEX_PATH
            ),
    },

    "records":
        records,
}


write_json_atomic(
    MANIFEST_PATH,
    manifest,
)


verified = load_json(
    MANIFEST_PATH
)

verified_records = (
    verified.get("records")
    or []
)

verified_counts = (
    verified.get("counts")
    or {}
)


checks = {
    "manifest_exists":
        MANIFEST_PATH.is_file(),

    "manifest_schema_correct":
        verified.get(
            "schema_version"
        )
        == MANIFEST_SCHEMA,

    "workspace_correct":
        verified.get(
            "workspace_id"
        )
        == WORKSPACE_ID,

    "record_count_5":
        verified.get(
            "record_count"
        )
        == EXPECTED_COUNT,

    "records_list_count_5":
        isinstance(
            verified_records,
            list,
        )
        and len(
            verified_records
        )
        == EXPECTED_COUNT,

    "reader_article_count_5":
        verified_counts.get(
            "reader_articles"
        )
        == EXPECTED_COUNT,

    "review_document_count_5":
        verified_counts.get(
            "visual_review_documents"
        )
        == EXPECTED_COUNT,

    "metadata_count_5":
        verified_counts.get(
            "metadata_records"
        )
        == EXPECTED_COUNT,

    "all_reader_paths_exist":
        all(
            (
                STORE_ROOT
                / Path(
                    record[
                        "article_document"
                    ][
                        "relative_path"
                    ]
                )
            ).is_file()

            for record
            in verified_records
        ),

    "all_review_paths_exist":
        all(
            (
                STORE_ROOT
                / Path(
                    record[
                        "review_document"
                    ][
                        "relative_path"
                    ]
                )
            ).is_file()

            for record
            in verified_records
        ),

    "all_metadata_paths_exist":
        all(
            (
                STORE_ROOT
                / Path(
                    record[
                        "metadata"
                    ][
                        "relative_path"
                    ]
                )
            ).is_file()

            for record
            in verified_records
        ),

    "canonical_downstream_source_is_reader":
        (
            verified.get(
                "canonical_downstream_source"
            )
            or {}
        ).get(
            "field"
        )
        == "article_document.relative_path",

    "audit_source_is_review":
        (
            verified.get(
                "audit_source"
            )
            or {}
        ).get(
            "field"
        )
        == "review_document.relative_path",
}


failed = [
    name
    for name, passed in checks.items()
    if not passed
]


report = {
    "schema_version":
        "udare_manifest_phase_4_3a5_report_v1",

    "workspace_id":
        WORKSPACE_ID,

    "manifest_path":
        str(MANIFEST_PATH),

    "record_count":
        len(records),

    "checks":
        checks,

    "failed_checks":
        failed,

    "queue_runner_invoked":
        False,

    "worker_invoked":
        False,

    "reconstruction_invoked":
        False,

    "decision":
        (
            "READY_FOR_PHASE_4_3B_FULL_POPULATION"
            if not failed
            else "BLOCKED"
        ),
}


write_json_atomic(
    REPORT_PATH,
    report,
)


print()
print("=" * 112)
print(
    "PHASE 4.3A.5 — CANONICAL UDARE MANIFEST"
)
print("=" * 112)

print(
    "Manifest:",
    MANIFEST_PATH,
)

print(
    "Records:",
    len(records),
)

print(
    "Reader articles:",
    len(article_paths),
)

print(
    "Visual reviews:",
    len(review_paths),
)

print(
    "Metadata records:",
    len(metadata_files),
)

print(
    "Engines:",
    sorted(engines),
)

print()
print("CHECKS")

for name, passed in checks.items():
    print(
        f"  {name}:",
        "PASS" if passed else "FAIL",
    )

print()
print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 4.3A.5 DECISION:",
    report["decision"],
)
print("=" * 112)

print("No queue runner or worker was invoked.")
print("No article was reconstructed.")

raise SystemExit(
    0 if not failed else 1
)
