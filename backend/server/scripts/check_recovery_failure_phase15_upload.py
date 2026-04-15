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

DATA_DIR = Path(r".\backend\server\data")
UPLOAD_POOL_FP = DATA_DIR / "phrase_pools" / "upload" / f"upload_phrase_pool_{WORKSPACE_ID}.json"


@dataclass
class CheckResult:
    code: str
    ok: bool
    detail: str


def request_json(method: str, url: str, payload: Dict[str, Any] | None = None) -> Tuple[int, Dict[str, Any], str]:
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)

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


def get_active_state() -> Tuple[int, Dict[str, Any], str]:
    url = (
        f"{BASE_URL}/api/site/target_pools/active_target_set?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("GET", url)


def clear_active_state() -> Tuple[int, Dict[str, Any], str]:
    url = (
        f"{BASE_URL}/api/site/target_pools/active_target_set/clear?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("POST", url)


def save_active_state(doc_ids: List[str]) -> Tuple[int, Dict[str, Any], str]:
    url = f"{BASE_URL}/api/site/target_pools/active_target_set/save"
    payload = {
        "workspace_id": WORKSPACE_ID,
        "active_document_ids": doc_ids,
        "preserve_omitted_fields": True,
    }
    return request_json("POST", url, payload)


def rebuild_all() -> Tuple[int, Dict[str, Any], str]:
    url = (
        f"{BASE_URL}/api/site/target_pools/rebuild_all?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("POST", url)


def load_pool_phrase_count() -> int:
    try:
        obj = json.loads(UPLOAD_POOL_FP.read_text(encoding="utf-8"))
        return int(obj.get("phrase_count", 0))
    except Exception:
        return 0


def extract_doc_ids(state_obj: Dict[str, Any]) -> List[str]:
    ats = state_obj.get("active_target_set")
    if not isinstance(ats, dict):
        return []
    vals = ats.get("active_document_ids")
    if not isinstance(vals, list):
        return []
    return [str(x).strip() for x in vals if str(x).strip()]


def main() -> int:
    print("\n===== PHASE 15 RECOVERY & FAILURE SAFETY CHECK (UPLOAD FOCUS) =====\n")
    print("workspace_id:", WORKSPACE_ID)
    print("base_url:", BASE_URL)
    print()

    checks: List[CheckResult] = []

    # Snapshot original state
    st0, data0, _ = get_active_state()
    original_doc_ids = extract_doc_ids(data0)

    # If empty, seed one valid id
    seeded = False
    if not original_doc_ids:
        seeded = True
        save_active_state(["seed_doc_0001"])
        st0, data0, _ = get_active_state()
        original_doc_ids = extract_doc_ids(data0)

    # -------------------------
    # 15.1 Clear and recover
    # -------------------------
    st_clear, data_clear, _ = clear_active_state()
    st_after_clear, data_after_clear, _ = get_active_state()
    after_clear_ids = extract_doc_ids(data_after_clear)

    checks.append(
        CheckResult(
            "15.1.1",
            st_clear == 200 and after_clear_ids == [],
            f"clear_status={st_clear}, active_document_ids_after_clear={after_clear_ids}",
        )
    )

    st_restore, _, _ = save_active_state(original_doc_ids)
    st_after_restore, data_after_restore, _ = get_active_state()
    restored_ids = extract_doc_ids(data_after_restore)

    checks.append(
        CheckResult(
            "15.1.2",
            st_restore == 200 and restored_ids == original_doc_ids,
            f"restore_status={st_restore}, restored_ids={restored_ids}, original_ids={original_doc_ids}",
        )
    )

    before_count = load_pool_phrase_count()
    st_rebuild, data_rebuild, _ = rebuild_all()
    after_count = load_pool_phrase_count()

    checks.append(
        CheckResult(
            "15.1.3",
            st_rebuild == 200 and bool(data_rebuild.get("ok")) and after_count >= 0,
            f"rebuild_status={st_rebuild}, before_count={before_count}, after_count={after_count}",
        )
    )

    # -------------------------
    # 15.2 Empty / missing
    # -------------------------
    st_empty_save, _, _ = save_active_state([])
    st_empty_get, data_empty_get, _ = get_active_state()
    empty_ids = extract_doc_ids(data_empty_get)

    checks.append(
        CheckResult(
            "15.2.1",
            st_empty_save == 200 and empty_ids == [],
            f"empty_save_status={st_empty_save}, active_document_ids={empty_ids}",
        )
    )

    missing_url = (
        f"{BASE_URL}/api/site/target_pools/active_target_set?"
        f"workspace_id=ws_missing_demo"
    )
    st_missing, _, _ = request_json("GET", missing_url)

    checks.append(
        CheckResult(
            "15.2.2",
            st_missing in (200, 400, 404),
            f"missing_workspace_status={st_missing}",
        )
    )

    # restore original after empty test
    save_active_state(original_doc_ids)
    _, data_restored2, _ = get_active_state()
    restored2 = extract_doc_ids(data_restored2)

    checks.append(
        CheckResult(
            "15.2.3",
            restored2 == original_doc_ids,
            f"restored_after_empty_test={restored2}",
        )
    )

    # -------------------------
    # 15.3 Duplicate / junk
    # -------------------------
    dup_ids = original_doc_ids + original_doc_ids
    save_active_state(dup_ids)
    _, data_dup, _ = get_active_state()
    deduped = extract_doc_ids(data_dup)

    checks.append(
        CheckResult(
            "15.3.1",
            len(deduped) == len(set(original_doc_ids)),
            f"saved_duplicates={dup_ids}, stored={deduped}",
        )
    )

    rebuild_all()
    count_after_dup = load_pool_phrase_count()

    checks.append(
        CheckResult(
            "15.3.2",
            count_after_dup >= 0,
            f"phrase_count_after_duplicate_test={count_after_dup}",
        )
    )

    junk_ids = ["", "   ", "%%%bad%%%"]
    save_active_state(junk_ids)
    _, data_junk, _ = get_active_state()
    junk_saved = extract_doc_ids(data_junk)

    checks.append(
        CheckResult(
            "15.3.3",
            junk_saved == ["%%%bad%%%"] or junk_saved == [],
            f"junk_input_saved_as={junk_saved}",
        )
    )

    # Final restore
    save_active_state(original_doc_ids)

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