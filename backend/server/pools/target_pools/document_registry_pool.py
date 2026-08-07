from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.server.utils.text_normalization import fix_mojibake_text


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _docs_root() -> Path:
    return _data_dir() / "docs"


def _ws_safe(ws: str) -> str:
    raw = (ws or "default").strip()
    if not raw:
        return "default"
    if raw.lower() == "default":
        return "default"
    if raw.lower().startswith("ws_"):
        return raw

    s = raw.lower()
    s = s.replace(".", "_").replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "workspace"
    return f"ws_{s}"[:80]


def _ws_docs_dir(ws: str) -> Path:
    return _docs_root() / _ws_safe(ws)


def _index_path(ws: str) -> Path:
    return _ws_docs_dir(ws) / "index.json"


def _pool_path(ws: str) -> Path:
    return (
        _data_dir()
        / "target_pools"
        / "document_registry"
        / f"document_registry_{_ws_safe(ws)}.json"
    )


def _clean_text(s: str) -> str:
    s = str(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\ufeff", " ")
    s = fix_mojibake_text(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _norm_title(s: str) -> str:
    s = _clean_text(s).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _filename_to_title(name: str) -> str:
    name = Path(str(name or "")).stem
    name = fix_mojibake_text(name)
    name = re.sub(r"[_\-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:200]


def _extract_h1_from_html(text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text or "", flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    return _clean_text(m.group(1))[:200]


def _extract_first_heading(text: str) -> str:
    m = re.search(
        r"<h([1-6])[^>]*>(.*?)</h\1>",
        text or "",
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        return _clean_text(m.group(2))[:200]

    for line in (text or "").splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("#"):
            t = re.sub(r"^#+\s*", "", t).strip()
            return _clean_text(t)[:200]

    return ""


def _extract_first_meaningful_line(text: str) -> str:
    for line in (text or "").splitlines():
        t = _clean_text(line)
        if not t:
            continue
        if len(t) < 3:
            continue
        return t[:200]
    return ""


def _is_test_or_demo_title(title: str) -> bool:
    t = (title or "").lower().strip()

    if len(t) < 5:
        return True

    bad_patterns = [
        "doc one",
        "doc1",
        "docpool",
        "test",
        "sample",
        "demo",
        "example",
    ]

    for p in bad_patterns:
        if p in t:
            return True

    return False


def _classify_page_type(title: str, title_source: str, rec: Dict[str, Any]) -> str:
    text = f"{title} {title_source} {rec.get('filename') or ''}".lower()

    if any(x in text for x in ["guide", "how to", "what is", "explained", "complete"]):
        return "guide_article"

    if any(x in text for x in ["calculator", "tool", "checker", "estimator"]):
        return "tool_page"

    if any(x in text for x in ["review", "comparison", "vs", "best"]):
        return "commercial_article"

    if any(x in text for x in ["policy", "terms", "privacy", "about", "contact"]):
        return "utility_page"

    return "editor_document"


def _registry_priority_bucket(title: str, title_source: str, is_placeholder_url: bool) -> str:
    # Document Registry Pool is purely for cross-document linking.
    # All valid uploaded documents should be treated equally.
    return "cross_document_target"


def _semantic_intent_signals(title: str, page_type_hint: str) -> Dict[str, Any]:
    t = _norm_title(title)
    tokens = [x for x in t.split() if len(x) > 2]

    return {
        "normalized_title": t,
        "token_count": len(tokens),
        "page_type_hint": page_type_hint,
        "has_question_intent": any(x in t for x in ["how", "what", "why", "when", "where"]),
        "has_tool_intent": any(x in t for x in ["calculator", "checker", "tool", "estimator"]),
        "has_guide_intent": any(x in t for x in ["guide", "complete", "explained"]),
    }


def _registry_priority_signals(
    title: str,
    title_source: str,
    page_type_hint: str,
    is_placeholder_url: bool,
) -> Dict[str, Any]:
    return {
        "title_source": title_source,
        "page_type_hint": page_type_hint,
        "is_placeholder_url": is_placeholder_url,
        "h1_or_heading_based": title_source in {"h1", "first_heading", "docx:Title"},
        "filename_based": title_source == "filename",
        "cross_document_eligible": bool(title),
    }


def _pick_title(rec: Dict[str, Any], file_text: str) -> Dict[str, str]:
    # 1) Prefer indexed H1 from upload pipeline
    indexed_h1 = _clean_text(rec.get("h1") or "")
    if indexed_h1:
        return {
            "title": indexed_h1[:200],
            "title_source": str(rec.get("h1_source") or "h1"),
        }

    # 2) Try parsing html-ish content
    h1 = _extract_h1_from_html(file_text)
    if h1:
        return {"title": h1, "title_source": "h1"}

    heading = _extract_first_heading(file_text)
    if heading:
        return {"title": heading, "title_source": "first_heading"}

    # 3) Filename from index metadata
    meta_title = _clean_text(rec.get("filename") or rec.get("title") or rec.get("name") or "")
    if meta_title:
        return {"title": meta_title[:200], "title_source": "filename"}

    # 4) Stored filename
    stored_name = rec.get("stored_name") or rec.get("storedName") or ""
    file_name_title = _filename_to_title(stored_name)
    if file_name_title:
        return {"title": file_name_title, "title_source": "filename"}

    # 5) First meaningful line
    first_line = _extract_first_meaningful_line(file_text)
    if first_line:
        return {"title": first_line, "title_source": "first_meaningful_line"}

    return {"title": "", "title_source": ""}


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _uploaded_at_key(rec: Dict[str, Any]) -> str:
    return str(rec.get("uploaded_at") or "")


def build_document_registry_pool(workspace_id: str) -> Dict[str, Any]:
    ws = _ws_safe(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    idx_fp = _index_path(ws)
    if not idx_fp.exists():
        raise FileNotFoundError(f"Missing docs index: {idx_fp}")

    rows = _safe_read_json(idx_fp)
    if not isinstance(rows, list):
        rows = []

    # Document Registry is an upstream target source.
    # It emits every valid uploaded workspace document.
    # Active Target Set membership is derived downstream.

    docs_dir = _ws_docs_dir(ws)

    documents_seen = 0
    documents_written = 0
    missing_title = 0
    duplicate_titles_collapsed = 0
    test_titles_removed = 0
    invalid_records_rejected = 0
    rejected_examples: List[Dict[str, Any]] = []
    rejection_reasons: Dict[str, int] = {}
    duplicate_suppression_audit: List[Dict[str, Any]] = []

    def _track_rejection(reason: str, rec: Any = None, title: str = "") -> None:
        nonlocal invalid_records_rejected
        invalid_records_rejected += 1
        rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

        if len(rejected_examples) < 10:
            if isinstance(rec, dict):
                rejected_examples.append({
                    "reason": reason,
                    "document_id": str(rec.get("doc_id") or rec.get("docId") or ""),
                    "title": title or str(rec.get("title") or rec.get("filename") or ""),
                })
            else:
                rejected_examples.append({
                    "reason": reason,
                    "record_type": type(rec).__name__,
                    "title": title,
                })

    deduped: Dict[str, Dict[str, Any]] = {}

    for rec in rows:
        if not isinstance(rec, dict):
            _track_rejection("invalid_record_type", rec)
            continue

        documents_seen += 1

        document_id = str(rec.get("doc_id") or rec.get("docId") or "").strip()
        if not document_id:
            missing_title += 1
            _track_rejection("missing_document_id", rec)
            continue

        stored_name = str(rec.get("stored_name") or rec.get("storedName") or "").strip()
        file_text = ""
        if stored_name:
            file_fp = docs_dir / stored_name
            if file_fp.exists():
                file_text = _safe_read_text(file_fp)

        picked = _pick_title(rec, file_text)
        title = (picked.get("title") or "").strip()
        title_source = (picked.get("title_source") or "").strip()

        if not title:
            missing_title += 1
            _track_rejection("missing_title", rec)
            continue

        if _is_test_or_demo_title(title):
            test_titles_removed += 1
            _track_rejection("test_or_demo_title", rec, title)
            continue

        norm = _norm_title(title)
        if not norm:
            missing_title += 1
            _track_rejection("empty_normalized_title", rec, title)
            continue

        target_path = f"/documents/{document_id}"
        published_url = _clean_text(
            rec.get("published_url")
            or rec.get("publishedUrl")
            or rec.get("url")
            or rec.get("canonical_url")
            or rec.get("canonicalUrl")
            or ""
        )
        final_url = published_url or target_path
        is_placeholder_url = not bool(published_url)
        page_type_hint = _classify_page_type(title, title_source, rec)
        priority_bucket = _registry_priority_bucket(title, title_source, is_placeholder_url)
        registry_priority_signals = _registry_priority_signals(
            title,
            title_source,
            page_type_hint,
            is_placeholder_url,
        )
        semantic_intent_signals = _semantic_intent_signals(title, page_type_hint)

        candidate = {
            "document_id": document_id,
            "workspace_id": ws,
            "url": final_url,
            "path": target_path,
            "published_url": published_url,
            "placeholder_url": target_path,
            "is_placeholder_url": is_placeholder_url,
            "label": title,
            "h1": title,
            "title": title,
            "title_source": title_source,
            "link_target": final_url,
            "source_type": "document_registry",
            "source_origin": "uploaded_editor_documents",
            "priority_bucket": priority_bucket,
            "page_type_hint": page_type_hint,
            "cross_document_linking": True,
            "uses_h1_heading_targets": True,
            "registry_priority_signals": registry_priority_signals,
            "semantic_intent_signals": semantic_intent_signals,
            "metadata": {
                "builder_version": "document_registry_pool_v2",
                "document_id": document_id,
                "workspace_id": ws,
                "document_title": title,
                "title_source": title_source,
                "upload_source": "document_registry",
                "content_type": str(rec.get("content_type") or rec.get("contentType") or ""),
                "document_status": str(rec.get("status") or rec.get("document_status") or "uploaded"),
                "publish_readiness": str(rec.get("publish_readiness") or rec.get("publishReadiness") or "editor_document"),
                "planned_content": False,
                "future_content": False,
                "uploaded_at": _uploaded_at_key(rec),
                "created_at": str(rec.get("created_at") or rec.get("createdAt") or ""),
                "updated_at": str(rec.get("updated_at") or rec.get("updatedAt") or ""),
                "registry_timestamps_available": bool(
                    rec.get("uploaded_at")
                    or rec.get("created_at")
                    or rec.get("createdAt")
                    or rec.get("updated_at")
                    or rec.get("updatedAt")
                ),
                "metadata_diagnostics": {
                    "has_document_id": bool(document_id),
                    "has_title": bool(title),
                    "has_published_url": bool(published_url),
                    "title_source": title_source,
                    "is_placeholder_url": is_placeholder_url,
                },
                "published_url": published_url,
                "placeholder_url": target_path,
                "is_placeholder_url": is_placeholder_url,
                "cross_document_linking": True,
                "uses_h1_heading_targets": True,
            },
            "generated_by": "document_registry_pool",
            "_uploaded_at": _uploaded_at_key(rec),
        }

        # Document Registry must dedupe by document_id, not title.
        # Different uploaded documents may share similar titles/headings, but each document_id is a valid cross-document target.
        dedupe_key = document_id

        existing = deduped.get(dedupe_key)
        if existing is None:
            deduped[dedupe_key] = candidate
        else:
            duplicate_titles_collapsed += 1
            duplicate_suppression_audit.append({
                "dedupe_key": dedupe_key,
                "normalized_title": norm,
                "kept_document_id": candidate["document_id"] if candidate["_uploaded_at"] >= existing["_uploaded_at"] else existing["document_id"],
                "suppressed_document_id": existing["document_id"] if candidate["_uploaded_at"] >= existing["_uploaded_at"] else candidate["document_id"],
                "reason": "duplicate_document_id_keep_newest",
            })
            # Keep newest duplicate copy of the same document_id
            if candidate["_uploaded_at"] >= existing["_uploaded_at"]:
                deduped[dedupe_key] = candidate

    items: List[Dict[str, str]] = []
    for _, item in deduped.items():
        items.append(
            {
                "document_id": item["document_id"],
                "workspace_id": item["workspace_id"],
                "url": item["url"],
                "path": item["path"],
                "label": item["label"],
                "h1": item["h1"],
                "title": item["title"],
                "title_source": item["title_source"],
                "link_target": item["link_target"],
                "source_type": item["source_type"],
                "source_origin": item["source_origin"],
                "priority_bucket": item["priority_bucket"],
                "page_type_hint": item["page_type_hint"],
                "cross_document_linking": item["cross_document_linking"],
                "uses_h1_heading_targets": item["uses_h1_heading_targets"],
                "registry_priority_signals": item["registry_priority_signals"],
                "semantic_intent_signals": item["semantic_intent_signals"],
                "metadata": item["metadata"],
                "generated_by": item["generated_by"],
            }
        )

    items.sort(key=lambda x: x["title"].lower())
    documents_written = len(items)

    page_type_counts: Dict[str, int] = {}
    priority_bucket_counts: Dict[str, int] = {}

    for item in items:
        pt = str(item.get("page_type_hint") or "unknown")
        pb = str(item.get("priority_bucket") or "unknown")
        page_type_counts[pt] = page_type_counts.get(pt, 0) + 1
        priority_bucket_counts[pb] = priority_bucket_counts.get(pb, 0) + 1

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "document_registry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "documents_seen": documents_seen,
            "documents_written": documents_written,
            "missing_title": missing_title,
            "duplicate_titles_collapsed": duplicate_titles_collapsed,
            "test_titles_removed": test_titles_removed,
            "page_type_counts": page_type_counts,
            "priority_bucket_counts": priority_bucket_counts,
            "invalid_records_rejected": invalid_records_rejected,
            "rejection_reasons": rejection_reasons,
            "rejected_examples": rejected_examples,
            "duplicate_suppression_audit_count": len(duplicate_suppression_audit),
        },
        "audit": {
            "rejection_reasons": rejection_reasons,
            "rejected_examples": rejected_examples,
            "duplicate_suppression_audit": duplicate_suppression_audit[:25],
            "counts_diagnostics": {
                "documents_seen": documents_seen,
                "documents_written": documents_written,
                "invalid_records_rejected": invalid_records_rejected,
                "duplicate_titles_collapsed": duplicate_titles_collapsed,
            },
            "rebuild_diagnostics": {
                "workspace_id": ws,
                "source_index": str(idx_fp),
                "output_path": str(_pool_path(ws)),
            },
        },
        "source": f"docs/{ws}/index.json",
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    return out