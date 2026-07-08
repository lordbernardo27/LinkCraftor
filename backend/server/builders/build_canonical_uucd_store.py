import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone


WORKSPACE_ID = "ws_whattoexpect_com"
SCHEMA_VERSION = "uucd.v1"

ROOT = Path("backend/server")

UUCD_DIR = ROOT / "data" / "universal_unified_content_documents"
UUCD_PATH = UUCD_DIR / f"universal_unified_content_documents_{WORKSPACE_ID}.json"

OLD_UCD_DIR = ROOT / "data" / "unified_content_documents"
OLD_UCD_PATH = OLD_UCD_DIR / f"unified_content_documents_{WORKSPACE_ID}.json"

QUARANTINE_DIR = ROOT / "_quarantine" / "old_ucd_store"

SEARCH_DIRS = [
    ROOT / "data",
    ROOT / "stores",
    ROOT / "artifacts",
    ROOT / "uploads",
    ROOT / "documents",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def stable_hash(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "\n".join(str(x) for x in value if x is not None).strip()
    return str(value).strip()


def extract_records(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("documents", "items", "records", "data", "pages"):
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return []


def guess_source_type(record, fallback="unknown"):
    source_type = (
        record.get("source_type")
        or record.get("type")
        or record.get("document_type")
        or record.get("kind")
        or fallback
    )

    source_type = str(source_type).lower().strip()

    if source_type in {"crawled_web_page", "web_page", "website", "url", "page"}:
        return "crawled_web_page"

    if source_type in {"docx", "uploaded_docx", "uploaded_document", "document"}:
        return "uploaded_document"

    url = record.get("url") or record.get("canonical_url")
    if url:
        return "crawled_web_page"

    filename = str(record.get("filename") or record.get("file_name") or record.get("source_name") or "").lower()
    if filename.endswith(".docx"):
        return "uploaded_document"

    if "documents.json" in str(fallback).lower():
        return "uploaded_document"

    return source_type or "unknown"


def normalize_record(record, source_hint="unknown"):
    if not isinstance(record, dict):
        return None

    source_type = guess_source_type(record, source_hint)

    url = normalize_text(record.get("canonical_url") or record.get("url") or record.get("page_url"))
    title = normalize_text(
        record.get("title")
        or record.get("page_title")
        or record.get("document_title")
        or record.get("filename")
        or record.get("file_name")
        or url
        or "Untitled Document"
    )

    text = normalize_text(
        record.get("text")
        or record.get("content")
        or record.get("body")
        or record.get("article_text")
        or record.get("clean_text")
        or record.get("markdown")
    )

    source_name = normalize_text(
        record.get("source_name")
        or record.get("filename")
        or record.get("file_name")
        or record.get("domain")
        or "whattoexpect.com"
    )

    dedupe_basis = "|".join([
        WORKSPACE_ID,
        source_type,
        url.lower(),
        title.lower(),
        stable_hash(text),
    ])

    existing_id = normalize_text(record.get("document_id") or record.get("id"))

    RESERVED_DOCUMENT_IDS = {
        "active_document",
        "current_document",
        "document",
        "default",
        "temp",
        "temporary",
        "unknown",
        "none",
        "null",
    }

    if existing_id and existing_id.lower() not in RESERVED_DOCUMENT_IDS:
        document_id = existing_id
    else:
        document_id = f"uucd_{stable_hash(dedupe_basis)[:24]}"

    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    metadata.update({
        "migrated_from": source_hint,
        "original_document_id": existing_id or None,
        "content_hash": stable_hash(text),
        "canonical_url": url or None,
    })

    return {
        "document_id": document_id,
        "schema_version": SCHEMA_VERSION,
        "workspace_id": WORKSPACE_ID,
        "source_type": source_type,
        "source_name": source_name,
        "title": title,
        "canonical_url": url or None,
        "text": text,
        "metadata": metadata,
        "created_at": record.get("created_at") or now_iso(),
        "updated_at": now_iso(),
    }


def collect_candidate_json_files():
    candidates = []

    for base in SEARCH_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            p = str(path).replace("\\", "/").lower()

            if "universal_unified_content_documents" in p:
                continue
            if "_quarantine" in p:
                continue

            name = path.name.lower()

            likely = any(token in name for token in [
                WORKSPACE_ID.lower(),
                "crawled",
                "crawl",
                "website",
                "web_page",
                "webpage",
                "uploaded",
                "docx",
                "document",
                "unified_content_documents",
            ])

            if likely:
                candidates.append(path)

    return sorted(set(candidates))


def load_all_candidates():
    normalized = []
    source_files = []

    for path in collect_candidate_json_files():
        try:
            payload = read_json(path)
            records = extract_records(payload)
            if not records:
                continue

            accepted = 0
            for rec in records:
                item = normalize_record(rec, source_hint=str(path))
                if not item:
                    continue

                has_text = bool(item.get("text"))
                has_url = bool(item.get("canonical_url"))
                is_docx = item.get("source_type") == "uploaded_document"

                if has_text or has_url or is_docx:
                    normalized.append(item)
                    accepted += 1

            if accepted:
                source_files.append({
                    "path": str(path),
                    "records_seen": len(records),
                    "records_accepted": accepted,
                })

        except Exception as exc:
            source_files.append({
                "path": str(path),
                "error": str(exc),
            })

    return normalized, source_files


def dedupe_records(records):
    unique = {}
    duplicate_count = 0
    duplicate_examples = []

    for record in records:
        source_type = record.get("source_type")
        url = (record.get("canonical_url") or "").strip().lower()
        title = (record.get("title") or "").strip().lower()
        content_hash = record.get("metadata", {}).get("content_hash") or stable_hash(record.get("text", ""))

        if url:
            key = f"url::{source_type}::{url}"
        elif content_hash:
            key = f"hash::{source_type}::{content_hash}"
        else:
            key = f"title::{source_type}::{title}"

        if key in unique:
            duplicate_count += 1
            if len(duplicate_examples) < 20:
                duplicate_examples.append({
                    "kept_document_id": unique[key].get("document_id"),
                    "dropped_document_id": record.get("document_id"),
                    "dedupe_key": key,
                    "title": record.get("title"),
                })

            kept = unique[key]
            if len(record.get("text", "")) > len(kept.get("text", "")):
                unique[key] = record
            continue

        unique[key] = record

    return list(unique.values()), duplicate_count, duplicate_examples


def quarantine_old_ucd_store():
    if not OLD_UCD_PATH.exists():
        return {
            "old_ucd_found": False,
            "quarantined": False,
            "old_path": str(OLD_UCD_PATH),
        }

    target = QUARANTINE_DIR / OLD_UCD_PATH.name
    shutil.copy2(OLD_UCD_PATH, target)

    marker = QUARANTINE_DIR / "QUARANTINE_MARKER.json"
    write_json(marker, {
        "workspace_id": WORKSPACE_ID,
        "reason": "Old UCD store is deprecated after UUCD canonical migration.",
        "old_path": str(OLD_UCD_PATH),
        "quarantine_copy": str(target),
        "quarantined_at": now_iso(),
    })

    return {
        "old_ucd_found": True,
        "quarantined": True,
        "old_path": str(OLD_UCD_PATH),
        "quarantine_copy": str(target),
    }


def main():
    UUCD_DIR.mkdir(parents=True, exist_ok=True)

    records, source_files = load_all_candidates()
    unique_records, duplicate_count, duplicate_examples = dedupe_records(records)

    website_count = sum(1 for r in unique_records if r.get("source_type") == "crawled_web_page")
    uploaded_count = sum(1 for r in unique_records if r.get("source_type") == "uploaded_document")

    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": WORKSPACE_ID,
        "store_type": "universal_unified_content_documents",
        "canonical": True,
        "generated_at": now_iso(),
        "counts": {
            "candidate_records_before_dedupe": len(records),
            "duplicates_removed": duplicate_count,
            "documents_after_dedupe": len(unique_records),
            "website_documents": website_count,
            "uploaded_documents": uploaded_count,
        },
        "source_files": source_files,
        "duplicate_examples": duplicate_examples,
        "documents": unique_records,
    }

    write_json(UUCD_PATH, payload)

    quarantine_result = quarantine_old_ucd_store()

    print("UUCD STORE BUILD COMPLETE")
    print("uucd_path =", UUCD_PATH)
    print("candidate_records_before_dedupe =", len(records))
    print("duplicates_removed =", duplicate_count)
    print("documents_after_dedupe =", len(unique_records))
    print("website_documents =", website_count)
    print("uploaded_documents =", uploaded_count)
    print("old_ucd_quarantine =", quarantine_result)


if __name__ == "__main__":
    main()


