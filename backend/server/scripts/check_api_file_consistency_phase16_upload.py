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
ACTIVE_FP = DATA_DIR / "target_pools" / f"active_target_set_{WORKSPACE_ID}.json"
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


def safe_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def api_get_active():
    url = (
        f"{BASE_URL}/api/site/target_pools/active_target_set?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("GET", url)


def api_rebuild():
    url = (
        f"{BASE_URL}/api/site/target_pools/rebuild_all?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("POST", url)


def api_preview():
    # If this route does not exist, checker will mark safe fail.
    url = (
        f"{BASE_URL}/api/site/target_pools/upload/preview?"
        f"workspace_id={urllib.parse.quote(WORKSPACE_ID)}"
    )
    return request_json("GET", url)


def active_ids_from_obj(obj: Dict[str, Any]) -> List[str]:
    ats = obj.get("active_target_set")
    if not isinstance(ats, dict):
        return []
    vals = ats.get("active_document_ids")
    if not isinstance(vals, list):
        return []
    return [str(x).strip() for x in vals if str(x).strip()]


def active_ids_from_file(obj: Dict[str, Any]) -> List[str]:
    if not isinstance(obj, dict):
        return []
    vals = obj.get("active_document_ids")
    if not isinstance(vals, list):
        return []
    return [str(x).strip() for x in vals if str(x).strip()]


def pool_phrase_count(obj: Dict[str, Any]) -> int:
    if not isinstance(obj, dict):
        return 0
    return int(obj.get("phrase_count", 0))


def preview_count(obj: Dict[str, Any]) -> int:
    if not isinstance(obj, dict):
        return 0

    for key in ("count", "phrase_count", "items_count"):
        val = obj.get(key)
        if isinstance(val, int):
            return val

    items = obj.get("items")
    if isinstance(items, list):
        return len(items)
    if isinstance(items, dict):
        return len(items)

    phrases = obj.get("phrases")
    if isinstance(phrases, dict):
        return len(phrases)

    return 0


def main() -> int:
    print("\n===== PHASE 16 API ↔ FILE CONSISTENCY CHECK (UPLOAD FOCUS) =====\n")
    print("workspace_id:", WORKSPACE_ID)
    print("base_url:", BASE_URL)
    print()

    checks: List[CheckResult] = []

    active_file = safe_json(ACTIVE_FP)
    upload_file = safe_json(UPLOAD_POOL_FP)

    st_active, data_active, _ = api_get_active()
    st_rebuild, data_rebuild, _ = api_rebuild()
    st_preview, data_preview, _ = api_preview()

    file_active_ids = active_ids_from_file(active_file)
    api_active_ids = active_ids_from_obj(data_active)

    file_pool_count = pool_phrase_count(upload_file)

    rebuild_upload = {}
    if isinstance(data_rebuild, dict):
        rebuild_upload = (data_rebuild.get("results") or {}).get("upload") or {}

    rebuild_count = 0
    if isinstance(rebuild_upload, dict):
        rebuild_count = int(((rebuild_upload.get("counts") or {}).get("phrase_count", 0)))

    preview_phrase_count = preview_count(data_preview)

    # 16.1.1
    checks.append(
        CheckResult(
            "16.1.1",
            st_active == 200 and file_active_ids == api_active_ids,
            f"file_active_ids={file_active_ids}, api_active_ids={api_active_ids}, status={st_active}",
        )
    )

    # 16.1.2
    checks.append(
        CheckResult(
            "16.1.2",
            st_rebuild == 200 and rebuild_count == file_pool_count,
            f"rebuild_count={rebuild_count}, file_pool_count={file_pool_count}, status={st_rebuild}",
        )
    )

    # 16.1.3
    checks.append(
        CheckResult(
            "16.1.3",
            st_preview == 200 and preview_phrase_count == file_pool_count,
            f"preview_status={st_preview}, preview_phrase_count={preview_phrase_count}, file_pool_count={file_pool_count}",
        )
    )

    # 16.2.1
    checks.append(
        CheckResult(
            "16.2.1",
            (file_active_ids == api_active_ids) and (rebuild_count == file_pool_count),
            f"active_match={file_active_ids == api_active_ids}, rebuild_match={rebuild_count == file_pool_count}",
        )
    )

    # 16.2.2
    checks.append(
        CheckResult(
            "16.2.2",
            not (st_rebuild == 200 and rebuild_count != file_pool_count),
            f"rebuild_status={st_rebuild}, rebuild_count={rebuild_count}, file_pool_count={file_pool_count}",
        )
    )

    # 16.2.3
    checks.append(
        CheckResult(
            "16.2.3",
            st_active == 200 and st_rebuild == 200,
            f"active_status={st_active}, rebuild_status={st_rebuild}, preview_status={st_preview}",
        )
    )

    print("--- Current values ---")
    print("active_file:", ACTIVE_FP)
    print("upload_pool_file:", UPLOAD_POOL_FP)
    print("file_active_ids:", file_active_ids)
    print("api_active_ids:", api_active_ids)
    print("file_pool_count:", file_pool_count)
    print("rebuild_count:", rebuild_count)
    print("preview_phrase_count:", preview_phrase_count)
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