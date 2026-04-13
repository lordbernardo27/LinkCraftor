"""
Phase 12 — API State Truthfulness (Upload only)

Checks:
12.1.1 Confirm the GET endpoint returns the correct merged active state for upload membership.
12.1.2 Confirm returned upload counts are accurate.
12.1.3 Confirm returned upload membership reflects actual stored backend state.

12.2.1 Confirm upload membership can coexist safely with other source fields in one active set.
12.2.2 Confirm upload active state is not suppressed incorrectly by another source field.
12.2.3 Confirm returned upload state remains source-traceable.

Usage:
    python backend/server/scripts/check_api_state_truthfulness_phase12_upload.py
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


WORKSPACE_ID = "ws_betterhealthcheck_com"
API_BASE = "http://127.0.0.1:8001"

GET_ENDPOINT_CANDIDATES = [
    "/api/site/target_pools/active_target_set",
    "/api/site/target_pools/active_target_set/get",
    "/api/site/target_pools/active_state",
    "/api/site/target_pools/state",
]

DATA_ROOT = Path(r".\backend\server\data")

UPLOAD_ID_KEYS = [
    "active_upload_ids",
    "upload_ids",
]

OTHER_SOURCE_KEYS = [
    "active_document_ids",
    "active_live_domain_urls",
    "active_imported_ids",
    "active_draft_ids",
]

LIKELY_STATE_FILE_HINTS = [
    "active",
    "target",
    "set",
    "state",
    "membership",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str


def normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            if item is None:
                continue
            s = str(item).strip()
            if s:
                out.append(s)
        return sorted(set(out))
    if isinstance(value, str):
        s = value.strip()
        return [s] if s else []
    return []


def load_json_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def maybe_json_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".json"


def score_candidate_file(path: Path, data: Dict[str, Any]) -> int:
    score = 0
    name = path.name.lower()

    for hint in LIKELY_STATE_FILE_HINTS:
        if hint in name:
            score += 3

    if WORKSPACE_ID.lower() in name:
        score += 5

    for key in UPLOAD_ID_KEYS:
        if key in data:
            score += 25

    for key in OTHER_SOURCE_KEYS:
        if key in data:
            score += 5

    if isinstance(data.get("workspaceId"), str) and data.get("workspaceId") == WORKSPACE_ID:
        score += 10

    return score


def find_backend_state_file(root: Path) -> Tuple[Optional[Path], List[Tuple[Path, int]]]:
    candidates: List[Tuple[Path, int]] = []

    if not root.exists():
        return None, candidates

    for path in root.rglob("*.json"):
        try:
            data = load_json_file(path)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        score = score_candidate_file(path, data)

        has_upload_key = any(k in data for k in UPLOAD_ID_KEYS)
        has_other_keys = any(k in data for k in OTHER_SOURCE_KEYS)

        if has_upload_key or has_other_keys or score > 0:
            candidates.append((path, score))

    candidates.sort(key=lambda x: x[1], reverse=True)

    best = candidates[0][0] if candidates else None
    return best, candidates


def http_get_json(url: str) -> Tuple[int, Dict[str, Any], str]:
    req = urllib.request.Request(url=url, method="GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        status = resp.getcode()
        body = resp.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        return status, data, body


def call_first_working_endpoint(
    api_base: str,
    workspace_id: str,
    endpoint_candidates: List[str],
) -> Tuple[str, int, Dict[str, Any], str]:
    last_error = None
    query = urllib.parse.urlencode({"workspaceId": workspace_id})

    for ep in endpoint_candidates:
        url = f"{api_base}{ep}?{query}"
        try:
            status, data, raw = http_get_json(url)
            if status == 200:
                return url, status, data, raw
            last_error = RuntimeError(f"Non-200 from {url}: {status}")
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Could not reach any GET endpoint candidate. Last error: {last_error}")


def get_first_present_key(data: Dict[str, Any], keys: List[str]) -> Tuple[Optional[str], List[str]]:
    for key in keys:
        if key in data:
            return key, normalize_list(data.get(key))
    return None, []


def get_candidate_objects(api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    objs: List[Dict[str, Any]] = []
    if isinstance(api_data, dict):
        objs.append(api_data)
    if isinstance(api_data.get("state"), dict):
        objs.append(api_data["state"])
    if isinstance(api_data.get("data"), dict):
        objs.append(api_data["data"])
    if isinstance(api_data.get("active_set"), dict):
        objs.append(api_data["active_set"])
    return objs


def read_backend_upload_membership(state: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
    return get_first_present_key(state, UPLOAD_ID_KEYS)


def read_api_upload_membership(api_data: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
    for obj in get_candidate_objects(api_data):
        key, vals = get_first_present_key(obj, UPLOAD_ID_KEYS)
        if key is not None:
            return key, vals
    return None, []


def read_backend_other_sources(state: Dict[str, Any]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for key in OTHER_SOURCE_KEYS:
        if key in state:
            out[key] = normalize_list(state.get(key))
    return out


def read_api_other_sources(api_data: Dict[str, Any]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for obj in get_candidate_objects(api_data):
        for key in OTHER_SOURCE_KEYS:
            if key in obj:
                out[key] = normalize_list(obj.get(key))
    return out


def find_count_values(api_data: Dict[str, Any]) -> Dict[str, Any]:
    found: Dict[str, Any] = {}

    def inspect(obj: Dict[str, Any]) -> None:
        for k, v in obj.items():
            if "count" in k.lower():
                found[k] = v

    for obj in get_candidate_objects(api_data):
        inspect(obj)

    return found


def check_12_1_1(api_upload_ids: List[str], backend_upload_ids: List[str]) -> CheckResult:
    ok = api_upload_ids == backend_upload_ids
    return CheckResult(
        name="12.1.1 GET returns correct merged upload membership",
        ok=ok,
        details=(
            f"API upload ids ({len(api_upload_ids)}): {api_upload_ids}\n"
            f"Backend upload ids ({len(backend_upload_ids)}): {backend_upload_ids}"
        ),
    )


def check_12_1_2(api_data: Dict[str, Any], api_upload_ids: List[str]) -> CheckResult:
    count_fields = find_count_values(api_data)
    expected = len(api_upload_ids)

    matching_fields = []
    suspicious_fields = []

    for k, v in count_fields.items():
        if isinstance(v, int) and "upload" in k.lower():
            if v == expected:
                matching_fields.append((k, v))
            else:
                suspicious_fields.append((k, v))

    ok = len(suspicious_fields) == 0

    lines = [f"Expected upload count from membership = {expected}"]
    lines.append(f"Matching upload count fields: {matching_fields}" if matching_fields else "No explicit matching upload count field found in API payload.")
    if suspicious_fields:
        lines.append(f"Suspicious upload count fields: {suspicious_fields}")

    return CheckResult(
        name="12.1.2 Returned upload counts are accurate",
        ok=ok,
        details="\n".join(lines),
    )


def check_12_1_3(
    api_upload_key: Optional[str],
    backend_upload_key: Optional[str],
    api_upload_ids: List[str],
    backend_upload_ids: List[str],
) -> CheckResult:
    same_key_family = (api_upload_key in UPLOAD_ID_KEYS) and (backend_upload_key in UPLOAD_ID_KEYS)
    same_membership = api_upload_ids == backend_upload_ids
    ok = same_key_family and same_membership

    return CheckResult(
        name="12.1.3 Returned upload membership reflects actual stored backend state",
        ok=ok,
        details=(
            f"API upload key: {api_upload_key}\n"
            f"Backend upload key: {backend_upload_key}\n"
            f"API upload ids: {api_upload_ids}\n"
            f"Backend upload ids: {backend_upload_ids}"
        ),
    )


def check_12_2_1(
    api_other: Dict[str, List[str]],
    backend_other: Dict[str, List[str]],
    api_upload_ids: List[str],
) -> CheckResult:
    backend_has_other_sources = any(len(v) > 0 for v in backend_other.values())
    upload_still_present = len(api_upload_ids) > 0

    if not backend_has_other_sources:
        return CheckResult(
            name="12.2.1 Upload membership coexists safely with other source fields",
            ok=True,
            details=(
                "No non-upload source membership found in current backend state.\n"
                "So this run does not disprove coexistence, but current stored state does not fully demonstrate it."
            ),
        )

    backend_present_keys = sorted([k for k, v in backend_other.items() if len(v) > 0])
    api_present_keys = sorted([k for k, v in api_other.items() if len(v) > 0])

    ok = upload_still_present and (api_present_keys == backend_present_keys)

    return CheckResult(
        name="12.2.1 Upload membership coexists safely with other source fields",
        ok=ok,
        details=(
            f"Backend other-source fields: {backend_other}\n"
            f"API other-source fields: {api_other}\n"
            f"API upload ids still present: {api_upload_ids}"
        ),
    )


def check_12_2_2(
    api_upload_ids: List[str],
    backend_upload_ids: List[str],
    api_other: Dict[str, List[str]],
) -> CheckResult:
    suppressed = len(backend_upload_ids) > 0 and len(api_upload_ids) == 0 and any(len(v) > 0 for v in api_other.values())
    ok = (not suppressed) and (api_upload_ids == backend_upload_ids)

    return CheckResult(
        name="12.2.2 Upload active state is not suppressed incorrectly by another source field",
        ok=ok,
        details=(
            f"Backend upload ids: {backend_upload_ids}\n"
            f"API upload ids: {api_upload_ids}\n"
            f"API other-source fields: {api_other}"
        ),
    )


def check_12_2_3(api_upload_key: Optional[str], api_data: Dict[str, Any]) -> CheckResult:
    count_fields = find_count_values(api_data)
    traceable = api_upload_key is not None or any("upload" in k.lower() for k in count_fields.keys())

    return CheckResult(
        name="12.2.3 Returned upload state remains source-traceable",
        ok=traceable,
        details=(
            f"API upload membership key: {api_upload_key}\n"
            f"API count-ish fields: {count_fields}"
        ),
    )


def main() -> int:
    print("\n===== PHASE 12 API STATE TRUTHFULNESS CHECK (UPLOAD ONLY) =====\n")

    best_file, ranked_candidates = find_backend_state_file(DATA_ROOT)

    print("--- Backend state file discovery ---")
    print(f"data_root: {DATA_ROOT.resolve()}")

    if ranked_candidates:
        print("Top candidate files:")
        for path, score in ranked_candidates[:10]:
            print(f"  score={score:>3}  {path}")
    else:
        print("No JSON candidates found under backend/server/data.")

    if best_file is None:
        print("\nERROR: Could not find a likely backend state file.")
        return 1

    backend_state = load_json_file(best_file)
    backend_upload_key, backend_upload_ids = read_backend_upload_membership(backend_state)
    backend_other = read_backend_other_sources(backend_state)

    print(f"\nChosen backend state file: {best_file}")
    print(f"backend_upload_key: {backend_upload_key}")
    print(f"backend_upload_ids: {backend_upload_ids}")
    print(f"backend_other_sources: {backend_other}")

    try:
        used_url, status, api_data, raw = call_first_working_endpoint(
            api_base=API_BASE,
            workspace_id=WORKSPACE_ID,
            endpoint_candidates=GET_ENDPOINT_CANDIDATES,
        )
    except Exception as e:
        print(f"\nERROR: GET endpoint call failed: {e}")
        return 1

    api_upload_key, api_upload_ids = read_api_upload_membership(api_data)
    api_other = read_api_other_sources(api_data)

    print("\n--- API GET snapshot ---")
    print(f"GET url: {used_url}")
    print(f"status: {status}")
    print(f"api_upload_key: {api_upload_key}")
    print(f"api_upload_ids: {api_upload_ids}")
    print(f"api_other_sources: {api_other}")

    checks = [
        check_12_1_1(api_upload_ids, backend_upload_ids),
        check_12_1_2(api_data, api_upload_ids),
        check_12_1_3(api_upload_key, backend_upload_key, api_upload_ids, backend_upload_ids),
        check_12_2_1(api_other, backend_other, api_upload_ids),
        check_12_2_2(api_upload_ids, backend_upload_ids, api_other),
        check_12_2_3(api_upload_key, api_data),
    ]

    print("\n--- Results ---")
    passed = 0
    for c in checks:
        mark = "PASS" if c.ok else "FAIL"
        if c.ok:
            passed += 1
        print(f"\n[{mark}] {c.name}")
        print(c.details)

    print("\n--- Summary ---")
    print(f"passed: {passed}/{len(checks)}")
    print(f"failed: {len(checks) - passed}/{len(checks)}")

    if passed != len(checks):
        print("\nFINAL: Phase 12 upload-only check found at least one failure or uncertainty.")
        return 2

    print("\nFINAL: Phase 12 upload-only check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())