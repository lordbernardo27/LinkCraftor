from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


UNIVERSAL_ARTICLE_BODY_STORE_SCHEMA_VERSION = "universal_article_body_store_v2"

DATA_ROOT = Path("backend/server/data")
BODY_STORE_ROOT = DATA_ROOT / "universal_article_body_store"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value: str | None, fallback: str = "unknown") -> str:
    raw = str(value or fallback).strip() or fallback
    return "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in raw)[:160]


def _stable_hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return path


def body_store_dir(workspace_id: str) -> Path:
    return BODY_STORE_ROOT / _safe_id(workspace_id, "default")


def body_files_dir(workspace_id: str) -> Path:
    return body_store_dir(workspace_id) / "bodies"


def body_index_path(workspace_id: str) -> Path:
    ws = _safe_id(workspace_id, "default")
    return body_store_dir(ws) / f"universal_article_body_index_{ws}.json"


def _extract_documents_from_uucd_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get("documents"), list):
        return [d for d in payload["documents"] if isinstance(d, dict)]

    if payload.get("schema_version") == "universal_unified_content_document_v1":
        return [payload]

    if "content_body" in payload and "document_id" in payload:
        return [payload]

    return []


def _load_existing_index(workspace_id: str) -> Dict[str, Any]:
    path = body_index_path(workspace_id)
    return _read_json(path, {
        "schema_version": UNIVERSAL_ARTICLE_BODY_STORE_SCHEMA_VERSION,
        "workspace_id": _safe_id(workspace_id, "default"),
        "store_type": "universal_article_body_store",
        "canonical": True,
        "all_sources_share_one_body_store": True,
        "semantic_reader_loads_body_from_body_ref": True,
        "bodies": [],
        "duplicate_hashes": [],
        "missing_bodies": [],
        "counts": {},
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    })


def build_universal_article_body_store_from_uucd_payload_v2(
    *,
    workspace_id: str,
    uucd_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a source-agnostic Universal Article Body Store from UUCD payload.

    Boundary:
    - Does not extract.
    - Does not clean.
    - Does not rewrite content_body.
    - Does not perform phrase extraction.
    - Does not perform semantic analysis.
    """

    ws = _safe_id(workspace_id, "default")
    docs = _extract_documents_from_uucd_payload(uucd_payload)

    index = _load_existing_index(ws)
    body_dir = body_files_dir(ws)
    body_dir.mkdir(parents=True, exist_ok=True)

    bodies_by_doc = {
        b.get("document_id"): b
        for b in index.get("bodies", [])
        if isinstance(b, dict) and b.get("document_id")
    }

    missing: List[Dict[str, Any]] = []
    hash_to_docs: Dict[str, List[str]] = {}

    for doc in docs:
        document_id = _safe_id(doc.get("document_id"), "unknown_document")
        source_type = str(doc.get("source_type") or "unknown").strip() or "unknown"
        source_format = str(doc.get("source_format") or "").strip()
        content_body = str(doc.get("content_body") or "")

        if not content_body.strip():
            missing.append({
                "document_id": document_id,
                "workspace_id": ws,
                "source_type": source_type,
                "reason": "missing_or_empty_content_body",
            })
            continue

        content_hash = _stable_hash(content_body)
        body_ref = body_dir / f"{document_id}.txt"

        previous = bodies_by_doc.get(document_id)
        previous_hash = previous.get("content_hash") if previous else ""

        if previous_hash != content_hash or not body_ref.exists():
            body_ref.write_text(content_body, encoding="utf-8")

        record = {
            "document_id": document_id,
            "uucd_document_id": document_id,
            "workspace_id": ws,
            "source_type": source_type,
            "source_format": source_format,
            "title": doc.get("title") or "",
            "body_ref": str(body_ref),
            "body_length": len(content_body),
            "content_hash": content_hash,
            "body_status": "available",
            "metadata": {
                "uucd_schema_version": doc.get("schema_version"),
                "uucd_pipeline_version": doc.get("pipeline_version"),
                "source_identity": doc.get("source_identity") or {},
                "created_from": "UUCD.content_body",
                "content_body_modified": False,
            },
            "created_at": previous.get("created_at") if previous else _now_iso(),
            "updated_at": _now_iso(),
        }

        bodies_by_doc[document_id] = record
        hash_to_docs.setdefault(content_hash, []).append(document_id)

        doc["content_ref"] = str(body_ref)
        doc["content_hash"] = content_hash
        doc["body_status"] = "available"
        doc.setdefault("metadata", {})["content_ref"] = str(body_ref)
        doc.setdefault("metadata", {})["content_hash"] = content_hash
        doc.setdefault("metadata", {})["body_length"] = len(content_body)

    duplicate_hashes = [
        {
            "content_hash": h,
            "document_ids": sorted(ids),
            "duplicate_count": len(ids),
        }
        for h, ids in hash_to_docs.items()
        if len(ids) > 1
    ]

    bodies = sorted(bodies_by_doc.values(), key=lambda r: (r.get("source_type", ""), r.get("document_id", "")))

    source_counts: Dict[str, int] = {}
    for b in bodies:
        st = b.get("source_type") or "unknown"
        source_counts[st] = source_counts.get(st, 0) + 1

    index.update({
        "schema_version": UNIVERSAL_ARTICLE_BODY_STORE_SCHEMA_VERSION,
        "workspace_id": ws,
        "store_type": "universal_article_body_store",
        "canonical": True,
        "all_sources_share_one_body_store": True,
        "semantic_reader_loads_body_from_body_ref": True,
        "supported_source_types": sorted(set(["website", "uploaded_document", "future_pdf", "future_api", "future_database"] + list(source_counts.keys()))),
        "bodies": bodies,
        "missing_bodies": missing,
        "duplicate_hashes": duplicate_hashes,
        "counts": {
            "total_bodies": len(bodies),
            "missing_bodies": len(missing),
            "duplicate_hashes": len(duplicate_hashes),
            "by_source_type": source_counts,
        },
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "modifies_content_body": False,
        },
        "updated_at": _now_iso(),
    })

    index_path = _write_json(body_index_path(ws), index)

    return {
        "ok": True,
        "workspace_id": ws,
        "body_index_path": str(index_path),
        "body_store_dir": str(body_store_dir(ws)),
        "bodies_written": len(bodies),
        "missing_bodies": len(missing),
        "duplicate_hashes": len(duplicate_hashes),
        "index": index,
        "uucd_payload": uucd_payload,
    }


def build_universal_article_body_store_from_uucd_file_v2(
    *,
    workspace_id: str,
    uucd_path: str | Path,
    write_back_uucd: bool = True,
) -> Dict[str, Any]:
    path = Path(uucd_path)
    payload = _read_json(path, {})

    result = build_universal_article_body_store_from_uucd_payload_v2(
        workspace_id=workspace_id,
        uucd_payload=payload,
    )

    if write_back_uucd:
        _write_json(path, result["uucd_payload"])

    result["uucd_path"] = str(path)
    return result


def read_universal_article_body_index_v2(workspace_id: str) -> Dict[str, Any]:
    return _read_json(body_index_path(workspace_id), {})


def explain_universal_article_body_store_v2() -> Dict[str, Any]:
    return {
        "stage": "Verification 6G",
        "component": "Universal Article Body Store",
        "schema_version": UNIVERSAL_ARTICLE_BODY_STORE_SCHEMA_VERSION,
        "responsibility": "Store source-agnostic article bodies from UUCD.content_body.",
        "canonical_body_field": "content_body",
        "outputs": [
            "body_ref",
            "body_length",
            "content_hash",
            "source_type",
            "document_id mapping",
            "UUCD mapping",
            "duplicate body hash protection",
        ],
        "future_source_placeholders": [
            "future_pdf",
            "future_api",
            "future_database",
        ],
        "boundary": {
            "performs_extraction": False,
            "performs_cleaning": False,
            "performs_phrase_extraction": False,
            "performs_semantic_analysis": False,
            "modifies_content_body": False,
        },
        "next_stage": "Verification 6H — Universal Article Body Store Verification",
    }
