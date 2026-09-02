from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


CERTIFICATION_SCHEMA_VERSION = "uucd_body_store_certification_v1"

DATA_ROOT = Path("backend/server/data")
CERT_DIR = DATA_ROOT / "uucd_body_store_certifications"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_ws(workspace_id: str) -> str:
    raw = str(workspace_id or "default").strip() or "default"
    return raw.replace("/", "_").replace("\\", "_").replace(" ", "_")


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


def certification_path(workspace_id: str) -> Path:
    ws = _safe_ws(workspace_id)
    return CERT_DIR / ws / f"uucd_body_store_certification_{ws}.json"


def _extract_uucd_documents(uucd: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(uucd.get("documents"), list):
        return [d for d in uucd["documents"] if isinstance(d, dict)]

    if uucd.get("schema_version") == "universal_unified_content_document_v1":
        return [uucd]

    if "document_id" in uucd and "content_body" in uucd:
        return [uucd]

    return []


def _bool_result(ok: bool, problems: List[str]) -> Dict[str, Any]:
    return {
        "ok": bool(ok),
        "problems": problems,
    }


def certify_uucd_body_store_v1(
    *,
    workspace_id: str,
    uucd_payload: Dict[str, Any],
    body_index: Dict[str, Any],
    lifecycle_registry: Dict[str, Any] | None = None,
    asset_version_registry: Dict[str, Any] | None = None,
    authorization_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    ws = _safe_ws(workspace_id)

    docs = _extract_uucd_documents(uucd_payload)
    bodies = body_index.get("bodies") if isinstance(body_index.get("bodies"), list) else []

    problems: List[str] = []

    doc_ids = [d.get("document_id") for d in docs if d.get("document_id")]
    body_doc_ids = [b.get("document_id") for b in bodies if b.get("document_id")]

    doc_id_set = set(doc_ids)
    body_doc_id_set = set(body_doc_ids)

    doc_source_counts = Counter(str(d.get("source_type") or "unknown") for d in docs)
    body_source_counts = Counter(str(b.get("source_type") or "unknown") for b in bodies)

    duplicate_doc_ids = [doc_id for doc_id, count in Counter(doc_ids).items() if count > 1]
    duplicate_body_doc_ids = [doc_id for doc_id, count in Counter(body_doc_ids).items() if count > 1]

    missing_body_doc_ids = sorted(doc_id_set - body_doc_id_set)
    orphan_body_doc_ids = sorted(body_doc_id_set - doc_id_set)

    if not docs:
        problems.append("UUCD has zero documents")

    if duplicate_doc_ids:
        problems.append(f"Duplicate UUCD document_ids: {duplicate_doc_ids[:20]}")

    if duplicate_body_doc_ids:
        problems.append(f"Duplicate body store document_ids: {duplicate_body_doc_ids[:20]}")

    if missing_body_doc_ids:
        problems.append(f"UUCD documents missing body records: {missing_body_doc_ids[:20]}")

    if orphan_body_doc_ids:
        problems.append(f"Body records not found in UUCD: {orphan_body_doc_ids[:20]}")

    empty_body_files: List[str] = []
    missing_body_files: List[str] = []
    mismatched_body_hashes: List[str] = []

    for body in bodies:
        doc_id = body.get("document_id")
        ref = Path(str(body.get("body_ref") or ""))

        if not ref.exists():
            missing_body_files.append(str(doc_id))
            continue

        text = ref.read_text(encoding="utf-8", errors="ignore")

        if not text.strip():
            empty_body_files.append(str(doc_id))

        if body.get("body_length") is not None and int(body.get("body_length") or 0) != len(text):
            mismatched_body_hashes.append(str(doc_id))

    if missing_body_files:
        problems.append(f"Missing body files: {missing_body_files[:20]}")

    if empty_body_files:
        problems.append(f"Empty body files: {empty_body_files[:20]}")

    if mismatched_body_hashes:
        problems.append(f"Body length mismatches: {mismatched_body_hashes[:20]}")

    duplicate_hashes = body_index.get("duplicate_hashes") or []
    duplicate_hash_ok = len(duplicate_hashes) == 0

    if duplicate_hashes:
        problems.append(f"Duplicate body hashes detected: {len(duplicate_hashes)}")

    lifecycle_ok = True
    lifecycle_problems: List[str] = []

    if lifecycle_registry:
        lifecycle_sources = lifecycle_registry.get("sources", {})
        lifecycle_events = lifecycle_registry.get("events", [])

        if not isinstance(lifecycle_sources, dict):
            lifecycle_ok = False
            lifecycle_problems.append("Lifecycle registry sources is not a dict")

        if not isinstance(lifecycle_events, list):
            lifecycle_ok = False
            lifecycle_problems.append("Lifecycle registry events is not a list")
    else:
        lifecycle_ok = False
        lifecycle_problems.append("Lifecycle registry not supplied")

    asset_ok = True
    asset_problems: List[str] = []

    if asset_version_registry:
        assets = asset_version_registry.get("assets") or asset_version_registry.get("versions") or []

        if not isinstance(assets, list):
            asset_ok = False
            asset_problems.append("Asset version registry assets/versions is not a list")
    else:
        asset_ok = False
        asset_problems.append("Asset version registry not supplied")

    authorization_ok = True
    authorization_problems: List[str] = []

    if authorization_payload:
        quarantined = (
            authorization_payload.get("unauthorized_documents_quarantined")
            or authorization_payload.get("counts", {}).get("unauthorized_documents_quarantined")
            or 0
        )

        if int(quarantined or 0) > 0:
            authorization_ok = False
            authorization_problems.append(f"Unauthorized documents quarantined: {quarantined}")

    verification = {
        "uucd": _bool_result(
            bool(docs) and not duplicate_doc_ids,
            [
                *([f"Duplicate UUCD document_ids: {duplicate_doc_ids[:20]}"] if duplicate_doc_ids else []),
                *(["UUCD has zero documents"] if not docs else []),
            ],
        ),
        "body_store": _bool_result(
            bool(bodies)
            and not missing_body_doc_ids
            and not orphan_body_doc_ids
            and not missing_body_files
            and not empty_body_files,
            [
                *([f"UUCD documents missing body records: {missing_body_doc_ids[:20]}"] if missing_body_doc_ids else []),
                *([f"Body records not found in UUCD: {orphan_body_doc_ids[:20]}"] if orphan_body_doc_ids else []),
                *([f"Missing body files: {missing_body_files[:20]}"] if missing_body_files else []),
                *([f"Empty body files: {empty_body_files[:20]}"] if empty_body_files else []),
            ],
        ),
        "authorization": _bool_result(authorization_ok, authorization_problems),
        "lifecycle": _bool_result(lifecycle_ok, lifecycle_problems),
        "version_registry": _bool_result(asset_ok, asset_problems),
        "duplicates": _bool_result(duplicate_hash_ok, [f"Duplicate body hashes detected: {len(duplicate_hashes)}"] if duplicate_hashes else []),
    }

    all_ok = all(v.get("ok") for v in verification.values())

    certification_level = "gold" if all_ok else "blocked"

    certification = {
        "schema_version": CERTIFICATION_SCHEMA_VERSION,
        "workspace_id": ws,
        "certified": all_ok,
        "semantic_ready": all_ok,
        "certification_level": certification_level,
        "verification": verification,
        "counts": {
            "uucd_documents": len(docs),
            "body_records": len(bodies),
            "website_documents": doc_source_counts.get("website", 0) + doc_source_counts.get("crawled_web_page", 0),
            "uploaded_documents": doc_source_counts.get("uploaded_document", 0),
            "body_records_by_source_type": dict(body_source_counts),
            "uucd_documents_by_source_type": dict(doc_source_counts),
            "missing_body_records": len(missing_body_doc_ids),
            "orphan_body_records": len(orphan_body_doc_ids),
            "duplicate_hashes": len(duplicate_hashes),
        },
        "problems": problems + lifecycle_problems + asset_problems + authorization_problems,
        "next_stage": "Phase 4.6.1 Semantic Article Reader" if all_ok else "Resolve certification blockers before Phase 4.6.1",
        "certified_at": _now_iso(),
    }

    path = _write_json(certification_path(ws), certification)

    return {
        "ok": True,
        "certification_path": str(path),
        "certification": certification,
    }


def explain_uucd_body_store_certification_v1() -> Dict[str, Any]:
    return {
        "stage": "Verification 6I",
        "component": "UUCD / Body Store Certification",
        "schema_version": CERTIFICATION_SCHEMA_VERSION,
        "responsibility": "Aggregate UUCD, body store, authorization, lifecycle, version, duplicate, and readiness checks into one semantic-readiness decision.",
        "output_decision_fields": [
            "certified",
            "semantic_ready",
            "certification_level",
            "next_stage",
        ],
        "next_stage_when_certified": "Phase 4.6.1 Semantic Article Reader",
    }
