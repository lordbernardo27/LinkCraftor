from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

import requests

DATA_ROOT = Path("backend/server/data")
def _utc_now_iso_v1() -> str:
    return datetime.now(timezone.utc).isoformat()


USER_AGENT = "Mozilla/5.0 (LinkCraftorBot/1.0; +https://linkcraftor.com)"
MAX_HTML_BYTES = 900_000


def _safe_workspace_id_v1(workspace_id: str) -> str:
    return str(workspace_id or "").strip().replace("/", "_").replace("\\", "_")


def _site_pages_path_v1(workspace_id: str) -> Path:
    return DATA_ROOT / f"site_pages_{_safe_workspace_id_v1(workspace_id)}.json"


def _raw_html_store_dir_v1() -> Path:
    path = DATA_ROOT / "raw_website_html"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _raw_html_store_path_v1(workspace_id: str) -> Path:
    return _raw_html_store_dir_v1() / f"raw_website_html_{_safe_workspace_id_v1(workspace_id)}.json"


def _reports_dir_v1() -> Path:
    path = DATA_ROOT / "raw_html_acquisition_reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_path_v1(workspace_id: str) -> Path:
    return _reports_dir_v1() / f"raw_html_acquisition_report_{_safe_workspace_id_v1(workspace_id)}.json"


def _checkpoint_path_v1(workspace_id: str) -> Path:
    return _reports_dir_v1() / f"raw_html_acquisition_checkpoint_{_safe_workspace_id_v1(workspace_id)}.json"


def _raw_html_id_for_url_v1(url: str) -> str:
    digest = hashlib.sha256(str(url or "").strip().encode("utf-8")).hexdigest()[:16]
    return f"raw_html_{digest}"


def _load_json_v1(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json_v1(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_site_pages_v1(workspace_id: str) -> List[Dict[str, Any]]:
    path = _site_pages_path_v1(workspace_id)
    if not path.exists():
        raise FileNotFoundError(f"Site pages file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    pages = data.get("items") or data.get("pages") or data.get("urls") or []

    if isinstance(pages, dict):
        pages = list(pages.values())

    out = []
    for item in pages:
        if isinstance(item, str):
            out.append({"url": item})
        elif isinstance(item, dict):
            out.append(item)

    return out


def _extract_url_v1(page: Dict[str, Any]) -> str:
    return str(
        page.get("url")
        or page.get("loc")
        or page.get("canonical_url")
        or page.get("source_url")
        or ""
    ).strip()


def _load_raw_html_store_v1(workspace_id: str) -> Dict[str, Any]:
    path = _raw_html_store_path_v1(workspace_id)
    return _load_json_v1(
        path,
        {
            "version": "raw_website_html_store_v1",
            "workspace_id": workspace_id,
            "pages": {},
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def _save_raw_html_store_v1(workspace_id: str, store: Dict[str, Any]) -> None:
    store["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    _write_json_v1(_raw_html_store_path_v1(workspace_id), store)


def _decode_html_bytes_v1(content: bytes, content_type: str = "") -> str:
    if not isinstance(content, (bytes, bytearray)):
        return ""

    if len(content) > MAX_HTML_BYTES:
        content = content[:MAX_HTML_BYTES]

    content_type_lower = (content_type or "").lower()
    encoding = None

    if "charset=" in content_type_lower:
        encoding = content_type_lower.split("charset=", 1)[-1].split(";", 1)[0].strip()

    for enc in [encoding, "utf-8", "windows-1252", "latin-1"]:
        if not enc:
            continue
        try:
            return content.decode(enc, errors="replace")
        except Exception:
            continue

    return content.decode("utf-8", errors="replace")


def _fetch_html_v1(
    *,
    url: str,
    session: requests.Session,
    timeout: tuple[int, int] = (8, 20),
    max_retries: int = 2,
) -> Dict[str, Any]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    started = time.time()
    attempts = 0
    last_error = ""
    last_status = 0
    last_content_type = ""
    last_final_url = ""

    for attempt in range(1, int(max_retries) + 2):
        attempts = attempt

        try:
            response = session.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
            )

            last_status = int(response.status_code or 0)
            last_content_type = response.headers.get("content-type", "") or ""
            last_final_url = response.url or ""

            raw = response.content or b""
            html = _decode_html_bytes_v1(raw, last_content_type)

            is_html_like = (
                "text/html" in last_content_type.lower()
                or "application/xhtml" in last_content_type.lower()
                or "<html" in html[:500].lower()
                or "<article" in html[:5000].lower()
            )

            ok = bool(
                last_status < 400
                and html.strip()
                and is_html_like
            )

            if ok:
                return {
                    "ok": True,
                    "status_code": last_status,
                    "final_url": last_final_url,
                    "redirected": bool(last_final_url and last_final_url != url),
                    "content_type": last_content_type,
                    "html": html,
                    "html_length": len(html),
                    "byte_length": len(raw),
                    "elapsed_seconds": round(time.time() - started, 3),
                    "attempts": attempts,
                    "error": "",
                }

            last_error = (
                "non_html_or_empty_response"
                if last_status < 400
                else f"http_status_{last_status}"
            )

            if last_status not in {408, 429, 500, 502, 503, 504}:
                break

        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"

        if attempt <= int(max_retries):
            time.sleep(min(2.0, 0.5 * attempt))

    return {
        "ok": False,
        "status_code": last_status,
        "final_url": last_final_url,
        "redirected": bool(last_final_url and last_final_url != url),
        "content_type": last_content_type,
        "html": "",
        "html_length": 0,
        "byte_length": 0,
        "elapsed_seconds": round(time.time() - started, 3),
        "attempts": attempts,
        "error": last_error or "fetch_failed",
    }




def _failure_registry_path_v1(workspace_id: str) -> Path:
    path = DATA_ROOT / "raw_html_failure_registry"
    path.mkdir(parents=True, exist_ok=True)
    return path / f"raw_html_failure_registry_{_safe_workspace_id_v1(workspace_id)}.json"


def _load_failure_registry_v1(workspace_id: str) -> Dict[str, Any]:
    path = _failure_registry_path_v1(workspace_id)
    if not path.exists():
        return {"workspace_id": workspace_id, "version": "raw_html_failure_registry_v1", "failures": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    data.setdefault("workspace_id", workspace_id)
    data.setdefault("version", "raw_html_failure_registry_v1")
    data.setdefault("failures", {})
    return data


def _save_failure_registry_v1(workspace_id: str, registry: Dict[str, Any]) -> None:
    registry["workspace_id"] = workspace_id
    registry["version"] = "raw_html_failure_registry_v1"
    registry["updated_at_utc"] = _utc_now_iso_v1()
    _failure_registry_path_v1(workspace_id).write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _classify_failure_v1(status_code: int, error: str = "") -> str:
    status_code = int(status_code or 0)
    if status_code in {404, 410}:
        return "permanent"
    if status_code in {408, 429, 500, 502, 503, 504}:
        return "temporary"

    error_lower = str(error or "").lower()
    if "invalid url" in error_lower or "malformed" in error_lower or "missing url" in error_lower:
        return "permanent"
    return "temporary"


def _record_failure_v1(
    *,
    registry: Dict[str, Any],
    url: str,
    html_id: str,
    status_code: int,
    error: str,
    final_url: str = "",
    content_type: str = "",
    permanent_failure_threshold: int = 3,
) -> Dict[str, Any]:
    failures = registry.setdefault("failures", {})
    now = _utc_now_iso_v1()
    existing = failures.get(html_id, {}) if isinstance(failures.get(html_id, {}), dict) else {}

    failure_type = _classify_failure_v1(status_code, error)
    attempt_count = int(existing.get("attempt_count", 0) or 0) + 1

    temporary_failure_count = int(existing.get("temporary_failure_count", 0) or 0)
    permanent_failure_count = int(existing.get("permanent_failure_count", 0) or 0)

    if failure_type == "permanent":
        permanent_failure_count += 1
    else:
        temporary_failure_count += 1

    excluded = bool(existing.get("excluded", False))

    if permanent_failure_count >= int(permanent_failure_threshold):
        excluded = True

    history = existing.get("history", [])
    if not isinstance(history, list):
        history = []

    history.append({
        "attempt": attempt_count,
        "utc": now,
        "status_code": int(status_code or 0),
        "failure_type": failure_type,
        "error": str(error or ""),
        "final_url": str(final_url or ""),
        "content_type": str(content_type or ""),
    })

    record = {
        "url": url,
        "html_id": html_id,
        "status_code": int(status_code or 0),
        "failure_type": failure_type,
        "first_failed_utc": existing.get("first_failed_utc") or now,
        "last_failed_utc": now,
        "attempt_count": attempt_count,
        "temporary_failure_count": temporary_failure_count,
        "permanent_failure_count": permanent_failure_count,
        "excluded": excluded,
        "resolved": False,
        "reason": str(error or f"HTTP {status_code}"),
        "final_url": str(final_url or ""),
        "content_type": str(content_type or ""),
        "history": history[-20:],
    }

    failures[html_id] = record
    return record


def _clear_failure_if_success_v1(*, registry: Dict[str, Any], html_id: str) -> None:
    failures = registry.setdefault("failures", {})
    if html_id in failures:
        failures[html_id]["resolved"] = True
        failures[html_id]["resolved_at_utc"] = _utc_now_iso_v1()
        failures[html_id]["excluded"] = False

def acquire_raw_html_for_workspace_v1(
    *,
    workspace_id: str,
    dry_run: bool = False,
    resume: bool = True,
    force: bool = False,
    batch_size: int | None = None,
    limit: int | None = None,
    checkpoint_every: int = 25,
    sleep_seconds: float = 0.0,
) -> Dict[str, Any]:
    """
    Enterprise Raw HTML Acquisition Engine.

    Converts:
    Site Pages → Raw HTML Store

    Supports:
    - dry run
    - resume
    - force refresh
    - batch processing
    - checkpointing
    - fetch diagnostics
    - acquisition report
    """

    started_at = datetime.now(timezone.utc).isoformat()
    wall_start = time.time()

    pages = _load_site_pages_v1(workspace_id)
    site_pages_count = len(pages)

    store = _load_raw_html_store_v1(workspace_id)
    store.setdefault("pages", {})

    failure_registry = _load_failure_registry_v1(workspace_id)
    failure_records = failure_registry.get("failures", {}) or {}
    excluded_failure_ids = {
        html_id for html_id, record in failure_records.items()
        if isinstance(record, dict)
        and record.get("excluded") is True
        and record.get("resolved") is not True
    }

    existing_ids = set(store.get("pages", {}).keys())

    original_pages = list(pages)

    if resume and not force:
        missing_pages = []
        existing_pages = []

        excluded_pages = []

        for page in original_pages:
            url = _extract_url_v1(page)
            html_id = _raw_html_id_for_url_v1(url) if url else ""

            if html_id and html_id in existing_ids:
                existing_pages.append(page)
            elif html_id and html_id in excluded_failure_ids:
                excluded_pages.append(page)
            else:
                missing_pages.append(page)

        pages = missing_pages
    else:
        excluded_pages = []

    if limit is not None:
        pages = pages[: int(limit)]

    if batch_size is not None:
        pages = pages[: int(batch_size)]

    selected_pages_count = len(pages)
    missing_pages_count = len(pages)
    existing_pages_count = len(existing_ids)

    if dry_run:
        report = {
            "ok": True,
            "engine": "enterprise_raw_html_acquisition_engine_v1_1_failure_registry",
            "workspace_id": workspace_id,
            "dry_run": True,
            "resume": resume,
            "force": force,
            "started_at_utc": started_at,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "input": {
                "site_pages_count": site_pages_count,
                "selected_pages_count": selected_pages_count,
                "existing_raw_html_count": len(existing_ids),
                "missing_pages_selected": missing_pages_count,
                "batch_size": batch_size,
                "limit": limit,
            },
            "processing": {
                "attempted": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_existing": 0,
                "skipped_no_url": 0,
            },
            "certification": {
                "ready_to_acquire": site_pages_count > 0,
                "raw_html_complete": len(existing_ids) >= site_pages_count,
                "reason": "dry_run_only",
            },
        }

        report_path = _report_path_v1(workspace_id)
        _write_json_v1(report_path, report)
        report["report_path"] = str(report_path)
        return report

    attempted = 0
    succeeded = 0
    failed = 0
    skipped_existing = 0
    skipped_no_url = 0

    http_status_distribution: Dict[str, int] = {}
    content_type_distribution: Dict[str, int] = {}
    redirect_count = 0
    retry_attempt_total = 0
    total_fetch_seconds = 0.0
    consecutive_failures = 0
    max_consecutive_failures = 0

    temporary_failures = 0
    permanent_failures = 0
    newly_excluded = 0
    already_excluded = len(excluded_pages) if "excluded_pages" in locals() else 0
    registry_updated = False

    ledger: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    successes: List[Dict[str, Any]] = []

    session = requests.Session()

    for index, page in enumerate(pages, start=1):
        url = _extract_url_v1(page)

        if not url:
            skipped_no_url += 1
            row = {
                "index": index,
                "status": "skipped",
                "reason": "missing_url",
                "url": "",
            }
            ledger.append(row)
            errors.append(row)
            continue

        html_id = _raw_html_id_for_url_v1(url)

        if resume and not force and html_id in existing_ids:
            skipped_existing += 1
            ledger.append({
                "index": index,
                "url": url,
                "html_id": html_id,
                "status": "skipped_existing",
            })
            continue

        attempted += 1
        fetch = _fetch_html_v1(url=url, session=session)

        status_key = str(fetch.get("status_code", 0))
        http_status_distribution[status_key] = http_status_distribution.get(status_key, 0) + 1

        content_type_key = str(fetch.get("content_type") or "unknown").split(";")[0].strip().lower() or "unknown"
        content_type_distribution[content_type_key] = content_type_distribution.get(content_type_key, 0) + 1

        retry_attempt_total += int(fetch.get("attempts", 0) or 0)
        total_fetch_seconds += float(fetch.get("elapsed_seconds", 0.0) or 0.0)

        if fetch.get("redirected"):
            redirect_count += 1

        if fetch.get("ok"):
            record = {
                "html_id": html_id,
                "workspace_id": workspace_id,
                "url": url,
                "final_url": fetch.get("final_url"),
                "title": page.get("title", ""),
                "source_type": "website_crawl",
                "status_code": fetch.get("status_code"),
                "content_type": fetch.get("content_type"),
                "html": fetch.get("html"),
                "html_length": fetch.get("html_length"),
                "byte_length": fetch.get("byte_length"),
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "site_pages_record": page,
                    "acquisition_engine": "enterprise_raw_html_acquisition_engine_v1",
                    "elapsed_seconds": fetch.get("elapsed_seconds"),
                    "domain": urlparse(url).netloc,
                },
            }

            store["pages"][html_id] = record
            existing_ids.add(html_id)
            succeeded += 1
            consecutive_failures = 0

            _clear_failure_if_success_v1(
                registry=failure_registry,
                html_id=html_id,
            )
            registry_updated = True

            row = {
                "index": index,
                "url": url,
                "html_id": html_id,
                "status": "succeeded",
                "status_code": fetch.get("status_code"),
                "html_length": fetch.get("html_length"),
                "elapsed_seconds": fetch.get("elapsed_seconds"),
                "attempts": fetch.get("attempts"),
                "redirected": fetch.get("redirected"),
                "final_url": fetch.get("final_url"),
                "content_type": fetch.get("content_type"),
            }
            successes.append(row)
            ledger.append(row)

        else:
            failed += 1
            consecutive_failures += 1
            max_consecutive_failures = max(max_consecutive_failures, consecutive_failures)

            failure_record = _record_failure_v1(
                registry=failure_registry,
                url=url,
                html_id=html_id,
                status_code=int(fetch.get("status_code", 0) or 0),
                error=str(fetch.get("error", "")),
                final_url=str(fetch.get("final_url", "")),
                content_type=str(fetch.get("content_type", "")),
            )
            registry_updated = True

            if failure_record.get("failure_type") == "permanent":
                permanent_failures += 1
            else:
                temporary_failures += 1

            if failure_record.get("excluded") is True:
                newly_excluded += 1

            row = {
                "index": index,
                "url": url,
                "html_id": html_id,
                "status": "failed",
                "status_code": fetch.get("status_code"),
                "error": fetch.get("error") or "fetch_failed",
                "elapsed_seconds": fetch.get("elapsed_seconds"),
                "attempts": fetch.get("attempts"),
                "redirected": fetch.get("redirected"),
                "final_url": fetch.get("final_url"),
                "content_type": fetch.get("content_type"),
            }
            errors.append(row)
            ledger.append(row)

        processed = attempted + skipped_existing + skipped_no_url

        if checkpoint_every and processed % int(checkpoint_every) == 0:
            _save_raw_html_store_v1(workspace_id, store)

            elapsed = max(0.001, time.time() - wall_start)
            rate = processed / elapsed
            remaining = max(0, selected_pages_count - processed)
            eta_seconds = remaining / rate if rate > 0 else None

            checkpoint = {
                "engine": "enterprise_raw_html_acquisition_engine_v1_1_failure_registry",
                "workspace_id": workspace_id,
                "started_at_utc": started_at,
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
                "processed_selected_pages": processed,
                "selected_pages_count": selected_pages_count,
                "attempted": attempted,
                "succeeded": succeeded,
                "failed": failed,
                "skipped_existing": skipped_existing,
                "skipped_no_url": skipped_no_url,
                "raw_html_store_count": len(store.get("pages", {}) or {}),
                "http_status_distribution": http_status_distribution,
                "content_type_distribution": content_type_distribution,
                "redirect_count": redirect_count,
                "retry_attempt_total": retry_attempt_total,
                "max_consecutive_failures": max_consecutive_failures,
                "last_index": index,
                "last_url": url,
                "elapsed_seconds": round(elapsed, 3),
                "pages_per_second": round(rate, 4),
                "eta_seconds": round(eta_seconds, 3) if eta_seconds is not None else None,
                "recent_ledger": ledger[-25:],
            }
            _write_json_v1(_checkpoint_path_v1(workspace_id), checkpoint)

        if sleep_seconds:
            time.sleep(float(sleep_seconds))

    _save_raw_html_store_v1(workspace_id, store)

    elapsed = max(0.001, time.time() - wall_start)
    if registry_updated:
        _save_failure_registry_v1(workspace_id, failure_registry)

    raw_html_count = len(store.get("pages", {}) or {})

    average_fetch_seconds = (
        total_fetch_seconds / attempted
        if attempted > 0
        else 0.0
    )

    pages_per_minute = (
        (attempted + skipped_existing + skipped_no_url) / elapsed * 60.0
        if elapsed > 0
        else 0.0
    )

    certification = {
        "site_pages_count": site_pages_count,
        "selected_pages_count": selected_pages_count,
        "raw_html_store_count": raw_html_count,
        "selected_pages_processed_or_skipped": (
            attempted + skipped_existing + skipped_no_url
        ) == selected_pages_count,
        "zero_runtime_failures": failed == 0,
        "raw_html_complete_for_site_pages": raw_html_count >= site_pages_count,
        "ready_for_ucd_rebuild": raw_html_count > 0,
        "http_success_rate": round((succeeded / attempted) * 100.0, 2) if attempted else 0.0,
        "max_consecutive_failures": max_consecutive_failures,
        "failure_registry_enabled": True,
        "excluded_failures": already_excluded + newly_excluded,
        "engine_runtime_failures": temporary_failures,
        "expected_http_failures": permanent_failures,
    }

    report = {
        "ok": True,
        "engine": "enterprise_raw_html_acquisition_engine_v1_1_failure_registry",
        "workspace_id": workspace_id,
        "dry_run": False,
        "resume": resume,
        "force": force,
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "input": {
            "site_pages_count": site_pages_count,
            "selected_pages_count": selected_pages_count,
            "existing_raw_html_count_before": len(existing_ids) - succeeded,
            "missing_pages_selected": missing_pages_count,
            "missing_only_queue_enabled": bool(resume and not force),
            "batch_size": batch_size,
            "limit": limit,
        },
        "processing": {
            "attempted": attempted,
            "succeeded": succeeded,
            "failed": failed,
            "skipped_existing": skipped_existing,
            "skipped_no_url": skipped_no_url,
        },
        "stores": {
            "raw_html_store_count": raw_html_count,
            "raw_html_store_path": str(_raw_html_store_path_v1(workspace_id)),
        },
        "diagnostics": {
            "http_status_distribution": http_status_distribution,
            "content_type_distribution": content_type_distribution,
            "redirect_count": redirect_count,
            "retry_attempt_total": retry_attempt_total,
            "average_fetch_seconds": round(average_fetch_seconds, 3),
            "pages_per_minute": round(pages_per_minute, 3),
            "max_consecutive_failures": max_consecutive_failures,
            "temporary_failures": temporary_failures,
            "permanent_failures": permanent_failures,
            "newly_excluded": newly_excluded,
            "already_excluded": already_excluded,
            "failure_registry_count": len(failure_registry.get("failures", {}) or {}),
            "failure_registry_path": str(_failure_registry_path_v1(workspace_id)),
        },
        "certification": certification,
        "samples": {
            "successes": successes[:20],
            "errors": errors[:50],
        },
        "ledger_tail": ledger[-100:],
    }

    report_path = _report_path_v1(workspace_id)
    _write_json_v1(report_path, report)
    report["report_path"] = str(report_path)

    return report
