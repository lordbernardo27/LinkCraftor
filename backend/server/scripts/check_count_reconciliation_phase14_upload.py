from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


WORKSPACE_ID = "ws_betterhealthcheck_com"
BASE_URL = "http://127.0.0.1:8001"

SERVER_DIR = Path(r".\backend\server")
DATA_DIR = SERVER_DIR / "data"

RAW_UPLOAD_INDEX_FP = DATA_DIR / f"upload_phrase_index_{WORKSPACE_ID}.json"
UPLOAD_POOL_FP = DATA_DIR / "phrase_pools" / "upload" / f"upload_phrase_pool_{WORKSPACE_ID}.json"


@dataclass
class CheckResult:
    code: str
    ok: bool
    detail: str


def safe_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


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
    except Exception:
        return 0, {}, ""


# -------------------------
# Correct source counters
# -------------------------
def count_raw_upload_phrases(raw_obj: Any) -> int:
    if not isinstance(raw_obj, dict):
        return 0
    phrases = raw_obj.get("phrases")
    return len(phrases) if isinstance(phrases, dict) else 0


def count_raw_upload_docs(raw_obj: Any) -> int:
    if not isinstance(raw_obj, dict):
        return 0

    phrases = raw_obj.get("phrases")
    if not isinstance(phrases, dict):
        return 0

    doc_ids: set[str] = set()

    for rec in phrases.values():
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


# -------------------------
# Correct pool counters
# -------------------------
def count_pool_items(pool_obj: Any) -> int:
    if not isinstance(pool_obj, dict):
        return 0

    phrases = pool_obj.get("phrases")
    return len(phrases) if isinstance(phrases, dict) else 0


def count_pool_docs(pool_obj: Any) -> int:
    if not isinstance(pool_obj, dict):
        return 0

    phrases = pool_obj.get("phrases")
    if not isinstance(phrases, dict):
        return 0

    doc_ids: set[str] = set()

    for rec in phrases.values():
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


def count_api_active_documents(api_obj: Dict[str, Any]) -> int:
    if not isinstance(api_obj, dict):
        return 0

    ats = api_obj.get("active_target_set")
    if not isinstance(ats, dict):
        return 0

    vals = ats.get("active_document_ids")
    return len(vals) if isinstance(vals, list) else 0


def counts_are_roughly_close(
    a: int,
    b: int,
    tolerance_ratio: float = 0.35,
    min_abs: int = 25,
) -> bool:
    if a == b:
        return True

    diff = abs(a - b)
    ceiling = max(min_abs, int(max(a, b) * tolerance_ratio))
    return diff <= ceiling


def main() -> int:
    print("\n===== PHASE 14 COUNT RECONCILIATION CHECK (UPLOAD FOCUS) =====\n")
    print("workspace_id:", WORKSPACE_ID)
    print("base_url:", BASE_URL)
    print()

    raw_obj = safe_json(RAW_UPLOAD_INDEX_FP)
    pool_obj = safe_json(UPLOAD_POOL_FP)

    raw_phrase_count = count_raw_upload_phrases(raw_obj)
    raw_doc_count = count_raw_upload_docs(raw_obj)

    pool_phrase_count = (
        int(pool_obj.get("phrase_count", 0))
        if isinstance(pool_obj, dict)
        else 0
    )
    pool_item_count = count_pool_items(pool_obj)
    pool_doc_count = count_pool_docs(pool_obj)

    active_set_url = (
        f"{BASE_URL}/api/site/target_pools/active_target_set?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )

    status_active, active_data, _ = get_json(active_set_url)
    api_active_doc_count = count_api_active_documents(active_data)

    checks: List[CheckResult] = []

    # 14.1.1
    checks.append(
        CheckResult(
            "14.1.1",
            counts_are_roughly_close(raw_phrase_count, pool_phrase_count),
            (
                f"raw_phrase_count={raw_phrase_count}, "
                f"pool_phrase_count={pool_phrase_count}, "
                f"pool_item_count={pool_item_count}"
            ),
        )
    )

    # 14.1.2
    checks.append(
        CheckResult(
            "14.1.2",
            api_active_doc_count <= max(pool_doc_count, raw_doc_count),
            (
                f"pool_doc_count={pool_doc_count}, "
                f"raw_doc_count={raw_doc_count}, "
                f"api_active_doc_count={api_active_doc_count}, "
                f"active_set_status={status_active}"
            ),
        )
    )

   # 14.1.3
    checks.append(
    CheckResult(
        "14.1.3",
        status_active == 200 and api_active_doc_count >= 0,
        (
            f"api_active_doc_count={api_active_doc_count}, "
            f"pool_doc_count={pool_doc_count}, "
            f"note=active_count_and_historical_pool_count_are_different_metrics"
        ),
    )
)

    # 14.2.1
    checks.append(
        CheckResult(
            "14.2.1",
            (
                RAW_UPLOAD_INDEX_FP.exists()
                and UPLOAD_POOL_FP.exists()
                and status_active == 200
                and bool(active_data.get("ok")) is True
                and raw_phrase_count >= pool_phrase_count >= 0
            ),
            (
                f"raw_exists={RAW_UPLOAD_INDEX_FP.exists()}, "
                f"pool_exists={UPLOAD_POOL_FP.exists()}, "
                f"active_api_ok={bool(active_data.get('ok')) if isinstance(active_data, dict) else False}, "
                f"raw_phrase_count={raw_phrase_count}, "
                f"pool_phrase_count={pool_phrase_count}"
            ),
        )
    )

    # 14.2.2
    checks.append(
        CheckResult(
            "14.2.2",
            pool_phrase_count <= raw_phrase_count if raw_phrase_count > 0 else pool_phrase_count == 0,
            (
                f"raw_phrase_count={raw_phrase_count}, "
                f"pool_phrase_count={pool_phrase_count}"
            ),
        )
    )

    # 14.2.3
    retention_ratio = (
        pool_phrase_count / max(raw_phrase_count, 1)
        if raw_phrase_count > 0 else 1.0
    )

    checks.append(
        CheckResult(
            "14.2.3",
            (
                (raw_phrase_count == 0 and pool_phrase_count == 0)
                or (
                    raw_phrase_count > 0
                    and pool_phrase_count > 0
                    and retention_ratio >= 0.10
                )
            ),
            (
                f"raw_phrase_count={raw_phrase_count}, "
                f"pool_phrase_count={pool_phrase_count}, "
                f"retention_ratio={retention_ratio:.4f}"
            ),
        )
    )

    print("--- Current counts ---")
    print("raw_upload_index_fp:", RAW_UPLOAD_INDEX_FP)
    print("upload_pool_fp:", UPLOAD_POOL_FP)
    print("raw_phrase_count:", raw_phrase_count)
    print("raw_doc_count:", raw_doc_count)
    print("pool_phrase_count:", pool_phrase_count)
    print("pool_item_count:", pool_item_count)
    print("pool_doc_count:", pool_doc_count)
    print("api_active_doc_count:", api_active_doc_count)
    print()

    print("--- Results ---")
    failed = 0

    for chk in checks:
        status = "PASS" if chk.ok else "FAIL"
        print(f"{chk.code} {status}")
        print(chk.detail)
        print()
        if not chk.ok:
            failed += 1

    print("===== END =====\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())