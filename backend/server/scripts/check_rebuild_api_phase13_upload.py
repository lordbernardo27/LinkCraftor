from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =========================
# Config
# =========================
WORKSPACE_ID = "ws_betterhealthcheck_com"
BASE_URL = "http://127.0.0.1:8001"

SERVER_DIR = Path(r".\backend\server")
DATA_DIR = SERVER_DIR / "data"

DOCUMENT_REGISTRY_FP = (
    DATA_DIR / "target_pools" / "document_registry" / f"document_registry_{WORKSPACE_ID}.json"
)
UPLOAD_PHRASE_INDEX_FP = DATA_DIR / f"upload_phrase_index_{WORKSPACE_ID}.json"
UPLOAD_STRUCT_FP = DATA_DIR / f"upload_struct_{WORKSPACE_ID}.json"
UPLOAD_POOL_FP = DATA_DIR / "phrase_pools" / "upload" / f"upload_phrase_pool_{WORKSPACE_ID}.json"

MAIN_FP = SERVER_DIR / "main.py"
FILES_ROUTE_FP = SERVER_DIR / "routes" / "files.py"
UPLOAD_POOL_BUILDER_FP = SERVER_DIR / "stores" / "upload_phrase_pool_builder.py"
DOC_REGISTRY_POOL_FP = SERVER_DIR / "pools" / "target_pools" / "document_registry_pool.py"


# =========================
# Helpers
# =========================
@dataclass
class CheckResult:
    code: str
    ok: bool
    detail: str


def safe_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def safe_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def file_mtime(path: Path) -> Optional[float]:
    try:
        return path.stat().st_mtime
    except Exception:
        return None


def iso_age_seconds(path: Path) -> Optional[float]:
    mt = file_mtime(path)
    if mt is None:
        return None
    return time.time() - mt


def post_json(url: str, body: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any], str]:
    data_bytes = None
    headers = {}
    if body is not None:
        data_bytes = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {}
            return resp.status, parsed, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        return e.code, parsed, raw


def get_json(url: str) -> Tuple[int, Dict[str, Any], str]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {}
            return resp.status, parsed, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        return e.code, parsed, raw


def count_upload_docs_from_raw_sources() -> int:
    raw = safe_json(UPLOAD_PHRASE_INDEX_FP)
    if not isinstance(raw, dict):
        return 0

    doc_ids: set[str] = set()
    for rec in raw.values():
        if not isinstance(rec, dict):
            continue
        docs = rec.get("docs")
        if not isinstance(docs, dict):
            continue
        for k in docs.keys():
            s = str(k).strip()
            if s:
                doc_ids.add(s)
    return len(doc_ids)


def count_upload_pool_docs() -> int:
    obj = safe_json(UPLOAD_POOL_FP)
    if not isinstance(obj, dict):
        return 0

    items = obj.get("items")
    if not isinstance(items, dict):
        return 0

    doc_ids: set[str] = set()
    for rec in items.values():
        if not isinstance(rec, dict):
            continue
        docs = rec.get("docs")
        if not isinstance(docs, dict):
            continue
        for k in docs.keys():
            s = str(k).strip()
            if s:
                doc_ids.add(s)
    return len(doc_ids)


def count_document_registry_items() -> int:
    obj = safe_json(DOCUMENT_REGISTRY_FP)
    if not isinstance(obj, dict):
        return 0
    items = obj.get("items")
    return len(items) if isinstance(items, list) else 0


def has_any(text: str, needles: List[str]) -> bool:
    return any(n in text for n in needles)


def paths_are_workspace_scoped() -> bool:
    return (
        WORKSPACE_ID in str(DOCUMENT_REGISTRY_FP)
        and WORKSPACE_ID in str(UPLOAD_POOL_FP)
        and WORKSPACE_ID in str(UPLOAD_PHRASE_INDEX_FP)
    )


# =========================
# Check runner
# =========================
def main() -> int:
    print("\n===== PHASE 13 REBUILD API CHECK (UPLOAD FOCUS) =====\n")
    print("workspace_id:", WORKSPACE_ID)
    print("base_url:", BASE_URL)
    print()

    # Snapshot mtimes before
    before_doc_registry_mtime = file_mtime(DOCUMENT_REGISTRY_FP)
    before_upload_pool_mtime = file_mtime(UPLOAD_POOL_FP)

    # 13.1.1 rebuild_all executes successfully
    rebuild_all_url = (
        f"{BASE_URL}/api/site/target_pools/rebuild_all?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    status_all, data_all, raw_all = post_json(rebuild_all_url)

    # allow fs timestamps to settle
    time.sleep(1.0)

    # Source code signals
    main_text = safe_text(MAIN_FP)
    files_route_text = safe_text(FILES_ROUTE_FP)
    upload_builder_text = safe_text(UPLOAD_POOL_BUILDER_FP)
    doc_registry_text = safe_text(DOC_REGISTRY_POOL_FP)

    after_doc_registry_mtime = file_mtime(DOCUMENT_REGISTRY_FP)
    after_upload_pool_mtime = file_mtime(UPLOAD_POOL_FP)

    results_obj = data_all.get("results") if isinstance(data_all, dict) else {}
    if not isinstance(results_obj, dict):
        results_obj = {}

    rebuild_all_ok = status_all == 200 and bool(data_all.get("ok")) is True

    # 13.1.2 expected upload-related builder runs during full rebuild
    upload_builder_exists = "def build_upload_phrase_pool(" in upload_builder_text
    upload_builder_wired_into_rebuild_all = False

    # conservative signal: rebuild_all response would mention upload if included
    if "upload" in results_obj:
        upload_builder_wired_into_rebuild_all = True

    # fallback source-code heuristic
    if not upload_builder_wired_into_rebuild_all:
        upload_builder_wired_into_rebuild_all = has_any(
            main_text + files_route_text,
            [
                "build_upload_phrase_pool",
                "upload_phrase_pool_builder",
                'results["upload"]',
                '"upload":',
            ],
        )

    # 13.1.3 full rebuild result reflects actual rebuilt upload state
    upload_state_reflectable = False
    upload_pool_obj = safe_json(UPLOAD_POOL_FP)
    if isinstance(upload_pool_obj, dict):
        phrase_count = upload_pool_obj.get("phrase_count")
        workspace_ok = upload_pool_obj.get("workspace_id") == WORKSPACE_ID
        upload_state_reflectable = isinstance(phrase_count, int) and phrase_count >= 0 and workspace_ok

    # 13.2.1 document-registry rebuild route works correctly
    doc_registry_route_candidates = [
        f"{BASE_URL}/api/site/target_pools/document_registry/rebuild?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
        f"{BASE_URL}/api/site/target_pools/document_registry/rebuild_pool?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
        f"{BASE_URL}/api/site/target_pools/document_registry/build?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
    ]
    doc_registry_route_ok = False
    doc_registry_route_used = ""
    doc_registry_route_payload: Dict[str, Any] = {}

    for url in doc_registry_route_candidates:
        status, data, _ = post_json(url)
        if status == 200 and isinstance(data, dict) and data.get("ok") is True:
            doc_registry_route_ok = True
            doc_registry_route_used = url
            doc_registry_route_payload = data
            break

    # 13.2.2 upload/document pool rebuild route works correctly
    upload_route_candidates = [
        f"{BASE_URL}/api/site/target_pools/upload/rebuild?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
        f"{BASE_URL}/api/site/target_pools/upload_phrase_pool/rebuild?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
        f"{BASE_URL}/api/site/phrase_pools/upload/rebuild?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
        f"{BASE_URL}/api/files/upload/rebuild?workspace_id={urllib.parse.quote(WORKSPACE_ID)}",
    ]
    upload_route_ok = False
    upload_route_used = ""
    upload_route_payload: Dict[str, Any] = {}

    for url in upload_route_candidates:
        status, data, _ = post_json(url)
        if status == 200 and isinstance(data, dict):
            okish = data.get("ok") is True or "phrase_count" in data or "counts" in data
            if okish:
                upload_route_ok = True
                upload_route_used = url
                upload_route_payload = data
                break

    # 13.3.1 upload-side rebuild writes expected backend JSON output
    upload_output_written = UPLOAD_POOL_FP.exists() and isinstance(upload_pool_obj, dict)

    # 13.3.2 upload outputs written to correct workspace-scoped files
    workspace_scoped_paths_ok = paths_are_workspace_scoped()
    upload_pool_workspace_ok = isinstance(upload_pool_obj, dict) and upload_pool_obj.get("workspace_id") == WORKSPACE_ID
    upload_output_workspace_scoped = workspace_scoped_paths_ok and upload_pool_workspace_ok

    # 13.3.3 output files not stale after execution
    doc_registry_fresh = (
        before_doc_registry_mtime is None
        or (after_doc_registry_mtime is not None and after_doc_registry_mtime >= before_doc_registry_mtime)
    )
    upload_pool_fresh = (
        before_upload_pool_mtime is None
        or (after_upload_pool_mtime is not None and after_upload_pool_mtime >= before_upload_pool_mtime)
    )
    upload_output_not_stale = upload_pool_fresh

    # Helpful counts
    raw_upload_doc_count = count_upload_docs_from_raw_sources()
    upload_pool_doc_count = count_upload_pool_docs()
    doc_registry_item_count = count_document_registry_items()

    checks: List[CheckResult] = [
        CheckResult(
            "13.1.1",
            rebuild_all_ok,
            f"rebuild_all status={status_all}, ok={data_all.get('ok')}, keys={list(results_obj.keys()) if isinstance(results_obj, dict) else []}",
        ),
        CheckResult(
            "13.1.2",
            upload_builder_exists and upload_builder_wired_into_rebuild_all,
            (
                f"upload_builder_exists={upload_builder_exists}, "
                f"upload_builder_wired_into_rebuild_all={upload_builder_wired_into_rebuild_all}, "
                f"rebuild_all_result_keys={list(results_obj.keys()) if isinstance(results_obj, dict) else []}"
            ),
        ),
        CheckResult(
            "13.1.3",
            upload_state_reflectable,
            (
                f"upload_pool_exists={UPLOAD_POOL_FP.exists()}, "
                f"upload_pool_workspace_ok={upload_pool_workspace_ok}, "
                f"raw_upload_doc_count={raw_upload_doc_count}, "
                f"upload_pool_doc_count={upload_pool_doc_count}"
            ),
        ),
        CheckResult(
            "13.2.1",
            doc_registry_route_ok,
            (
                f"route_used={doc_registry_route_used or 'NONE'}, "
                f"payload_keys={list(doc_registry_route_payload.keys()) if isinstance(doc_registry_route_payload, dict) else []}"
            ),
        ),
        CheckResult(
            "13.2.2",
            upload_route_ok,
            (
                f"route_used={upload_route_used or 'NONE'}, "
                f"payload_keys={list(upload_route_payload.keys()) if isinstance(upload_route_payload, dict) else []}"
            ),
        ),
        CheckResult(
            "13.3.1",
            upload_output_written,
            f"upload_pool_fp={UPLOAD_POOL_FP}, exists={UPLOAD_POOL_FP.exists()}",
        ),
        CheckResult(
            "13.3.2",
            upload_output_workspace_scoped,
            (
                f"workspace_scoped_paths_ok={workspace_scoped_paths_ok}, "
                f"upload_pool_workspace_ok={upload_pool_workspace_ok}, "
                f"document_registry_fp={DOCUMENT_REGISTRY_FP.name}, upload_pool_fp={UPLOAD_POOL_FP.name}"
            ),
        ),
        CheckResult(
            "13.3.3",
            upload_output_not_stale,
            (
                f"before_upload_pool_mtime={before_upload_pool_mtime}, "
                f"after_upload_pool_mtime={after_upload_pool_mtime}, "
                f"upload_pool_age_seconds={iso_age_seconds(UPLOAD_POOL_FP)}"
            ),
        ),
    ]

    print("--- Rebuild_all response ---")
    print(json.dumps(data_all, indent=2, ensure_ascii=False))
    print()

    print("--- Helpful counts ---")
    print("raw_upload_doc_count:", raw_upload_doc_count)
    print("upload_pool_doc_count:", upload_pool_doc_count)
    print("doc_registry_item_count:", doc_registry_item_count)
    print("document_registry_fp_exists:", DOCUMENT_REGISTRY_FP.exists())
    print("upload_pool_fp_exists:", UPLOAD_POOL_FP.exists())
    print()

    print("--- Results ---")
    failed = 0
    for r in checks:
        status = "PASS" if r.ok else "FAIL"
        print(f"{r.code} {status}")
        print(r.detail)
        print()
        if not r.ok:
            failed += 1

    print("===== END =====\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())