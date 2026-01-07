# LinkCraftor/backend/app/routers/external.py
from __future__ import annotations

import csv
import gzip
import io
import json
import random
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

router = APIRouter()

# ------------------------------------------------------------
# Paths (project-root safe)
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "backend" / "data"

AUTO_PATH = DATA_DIR / "global_external_auto.json"
MANUAL_PATH = DATA_DIR / "global_external_manual.json"
BLACKLIST_PATH = DATA_DIR / "blacklist_url.json"
AUDIT_PATH = DATA_DIR / "owner_audit_log.jsonl"
SOURCES_PATH = DATA_DIR / "owner_sources.json"
SNAPSHOT_DIR = DATA_DIR / "import_snapshots"
IMPORT_RUNS_INDEX_PATH = DATA_DIR / "import_runs_index.json"


# ------------------------------------------------------------
# Tiny read-cache to speed repeated reads
# ------------------------------------------------------------
_CACHE: Dict[str, Tuple[float, Any]] = {}

# ------------------------------------------------------------
# Resolve index (fast + predictable /resolve)
# ------------------------------------------------------------
_RESOLVE_INDEX: Dict[str, Any] = {
    "manual_mtime": None,
    "auto_mtime": None,
    "manual_by_key": {},  # key -> list[dict]
    "auto_by_key": {},    # key -> list[dict]
}

# ------------------------------------------------------------
# Defaults (backend-owned sources)
# ------------------------------------------------------------
DEFAULT_SOURCES = {
    "default_source": "mayoclinic",
    "sources": {
        "mayoclinic": {
            "label": "mayoclinic",
            "domain": "mayoclinic.org",
            "defaults": {
                "include_paths": [
                    "/healthy-lifestyle/",
                    "/diseases-conditions/",
                    "/drugs-supplements/",
                    "/symptoms/",
                    "/symptoms-causes/",
                    "/diagnosis-treatment/",
                ],
                "exclude_paths": ["/news/", "/about/", "/careers/"],
                "block_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"],
                "block_lang_prefixes": [
                    "/ar/", "/zh-hans/", "/es/", "/fr/", "/de/",
                    "/pt/", "/it/", "/ru/", "/tr/", "/vi/"
                ],
                "allow_lang_prefixes": [],
                "require_host_match": True,
                "allowed_hosts": [],
            },
        }
    },
}

# ------------------------------------------------------------
# File helpers
# ------------------------------------------------------------
def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_snapshot_dir() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def _invalidate_cache(path: Path) -> None:
    try:
        _CACHE.pop(str(path), None)
    except Exception:
        pass

def _invalidate_resolve_index() -> None:
    _RESOLVE_INDEX["manual_mtime"] = None
    _RESOLVE_INDEX["auto_mtime"] = None
    _RESOLVE_INDEX["manual_by_key"] = {}
    _RESOLVE_INDEX["auto_by_key"] = {}

def _atomic_write_json(path: Path, data: Any) -> None:
    _ensure_data_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    _invalidate_cache(path)
    _invalidate_resolve_index()

def _append_import_run_index(entry: Dict[str, Any], max_keep: int = 200) -> None:
    _ensure_data_dir()

    raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
    if not isinstance(raw, dict):
        raw = {}

    # accept old schema
    runs = raw.get("runs")
    if not isinstance(runs, list):
        runs = raw.get("items")
    if not isinstance(runs, list):
        runs = []

    # newest first
    runs.insert(0, entry)

    # trim
    runs = runs[: max(1, min(int(max_keep), 2000))]

    # ✅ write both keys
    raw["runs"] = runs
    raw["items"] = runs

    _atomic_write_json(IMPORT_RUNS_INDEX_PATH, raw)


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _cached_read_json(path: Path) -> Any:
    try:
        st = path.stat()
        key = str(path)
        hit = _CACHE.get(key)
        if hit and hit[0] == st.st_mtime:
            return hit[1]
        data = _safe_read_json(path)
        _CACHE[key] = (st.st_mtime, data)
        return data
    except FileNotFoundError:
        return None
    except Exception:
        return _safe_read_json(path)

def _safe_read_list(path: Path) -> List[Dict[str, Any]]:
    raw = _cached_read_json(path)
    return raw if isinstance(raw, list) else []

def _ensure_files_exist() -> None:
    _ensure_data_dir()
    if not AUTO_PATH.exists():
        _atomic_write_json(AUTO_PATH, [])
    if not MANUAL_PATH.exists():
        _atomic_write_json(MANUAL_PATH, [])
    if not BLACKLIST_PATH.exists():
        _atomic_write_json(BLACKLIST_PATH, {"blocked_domains": [], "blocked_urls": []})
    if not SOURCES_PATH.exists():
        _atomic_write_json(SOURCES_PATH, DEFAULT_SOURCES)

    # ✅ NEW: ensure import runs index exists
    if not IMPORT_RUNS_INDEX_PATH.exists():
        _atomic_write_json(IMPORT_RUNS_INDEX_PATH, {"runs": [], "items": []})


def _make_key(phrase: str) -> str:
    return " ".join((phrase or "").strip().lower().split())

def _normalize_url(url: str) -> str:
    return (url or "").strip()

def _extract_domain(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.split("/")[0]
    u = u.split(":")[0]
    return u

def _get_mtime_safe(path: Path) -> Optional[float]:
    try:
        return path.stat().st_mtime
    except Exception:
        return None

def _normalize_url_for_storage(url: str, prefer_no_www: bool = True, drop_query: bool = True) -> str:
    """
    Normalization used for storage + dedup:
    - forces scheme (defaults to https if missing)
    - optionally removes www.
    - optionally drops ?query and #fragment
    - removes trailing slash (except '/')
    """
    u = (url or "").strip()
    if not u:
        return ""

    if "://" not in u:
        u = "https://" + u.lstrip("/")

    try:
        p = urlparse(u)
    except Exception:
        return u.strip()

    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower().strip()
    path = (p.path or "").strip() or "/"

    if prefer_no_www and netloc.startswith("www."):
        netloc = netloc[4:]

    if path != "/" and path.endswith("/"):
        path = path[:-1]

    query = "" if drop_query else (p.query or "")
    # never store fragments
    out = f"{scheme}://{netloc}{path}"
    if query:
        out += f"?{query}"
    return out

# ------------------------------------------------------------
# Sources config (backend-owned) + migration
# ------------------------------------------------------------
def _merge_unique_list(base: List[Any], extra: List[Any]) -> List[Any]:
    out: List[Any] = []
    seen = set()
    for x in (base or []):
        k = str(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    for x in (extra or []):
        k = str(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

def _migrate_owner_sources(existing: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(existing, dict):
        return DEFAULT_SOURCES

    out = dict(existing)
    if "default_source" not in out:
        out["default_source"] = DEFAULT_SOURCES.get("default_source", "mayoclinic")

    if "sources" not in out or not isinstance(out.get("sources"), dict):
        out["sources"] = {}

    sources = out["sources"]
    def_sources = DEFAULT_SOURCES.get("sources", {})

    for label, src_def in def_sources.items():
        if label not in sources or not isinstance(sources.get(label), dict):
            sources[label] = src_def
            continue

        src_existing = sources[label]
        if "defaults" not in src_existing or not isinstance(src_existing.get("defaults"), dict):
            src_existing["defaults"] = src_def.get("defaults", {})
        else:
            ex_defaults = src_existing["defaults"]
            def_defaults = src_def.get("defaults", {})

            ex_inc = ex_defaults.get("include_paths", [])
            def_inc = def_defaults.get("include_paths", [])
            if isinstance(ex_inc, list) and isinstance(def_inc, list):
                ex_defaults["include_paths"] = _merge_unique_list(ex_inc, def_inc)
            elif isinstance(def_inc, list):
                ex_defaults["include_paths"] = def_inc

            for k, v in def_defaults.items():
                if k not in ex_defaults:
                    ex_defaults[k] = v

        if "domain" not in src_existing and "domain" in src_def:
            src_existing["domain"] = src_def["domain"]
        if "label" not in src_existing and "label" in src_def:
            src_existing["label"] = src_def["label"]

        sources[label] = src_existing

    out["sources"] = sources
    return out

def _ensure_sources_file_migrated() -> None:
    _ensure_data_dir()
    if not SOURCES_PATH.exists():
        _atomic_write_json(SOURCES_PATH, DEFAULT_SOURCES)
        return

    existing = _safe_read_json(SOURCES_PATH)
    migrated = _migrate_owner_sources(existing if isinstance(existing, dict) else {})
    if migrated != existing:
        _atomic_write_json(SOURCES_PATH, migrated)

def _read_sources() -> Dict[str, Any]:
    _ensure_sources_file_migrated()
    raw = _cached_read_json(SOURCES_PATH)
    if not isinstance(raw, dict):
        return DEFAULT_SOURCES
    if "sources" not in raw or not isinstance(raw.get("sources"), dict):
        return DEFAULT_SOURCES
    if "default_source" not in raw:
        raw["default_source"] = DEFAULT_SOURCES["default_source"]
    return raw

def _get_source_config(source_label: str) -> Dict[str, Any]:
    data = _read_sources()
    src = (data.get("sources") or {}).get(source_label)
    return src if isinstance(src, dict) else {}

def _get_default_source_label() -> str:
    data = _read_sources()
    return str(data.get("default_source") or "").strip() or "mayoclinic"

def _new_import_run_id(prefix: str = "run") -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{random.randint(100000, 999999)}"

# Initialize
_ensure_files_exist()
_ensure_sources_file_migrated()

@router.get("/owner/sources")
async def owner_sources():
    data = _read_sources()
    sources = sorted(list((data.get("sources") or {}).keys()))
    return {
        "ok": True,
        "sources": sources,
        "default_source": _get_default_source_label(),
        "has_default": bool(_get_default_source_label()),
    }

# ------------------------------------------------------------
# Blacklist
# ------------------------------------------------------------
def _read_blacklist() -> Dict[str, List[str]]:
    raw = _cached_read_json(BLACKLIST_PATH)
    if not isinstance(raw, dict):
        return {"blocked_domains": [], "blocked_urls": []}
    bd = raw.get("blocked_domains") if isinstance(raw.get("blocked_domains"), list) else []
    bu = raw.get("blocked_urls") if isinstance(raw.get("blocked_urls"), list) else []
    return {"blocked_domains": bd, "blocked_urls": bu}

def _is_blocked(url: str) -> bool:
    url = _normalize_url(url)
    if not url:
        return True
    bl = _read_blacklist()
    domain = _extract_domain(url)

    blocked_urls = set(map(str, bl["blocked_urls"]))
    blocked_domains = set(map(lambda x: str(x).lower().strip(), bl["blocked_domains"]))
    return (url in blocked_urls) or (domain in blocked_domains)

# ------------------------------------------------------------
# HTTP (supports gzip)
# ------------------------------------------------------------
def _http_get_text(url: str, timeout_sec: int = 15) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "LinkCraftorControlTower/1.0 (+owner.linkcraftor.com)",
            "Accept": "text/xml,application/xml,text/plain,*/*",
            "Accept-Encoding": "gzip",
        },
        method="GET",
    )

    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read()
        enc = ""
        try:
            enc = (resp.headers.get("Content-Encoding") or "").lower().strip()
        except Exception:
            enc = ""

        is_gz = ("gzip" in enc) or url.lower().endswith(".gz")
        if is_gz:
            try:
                raw = gzip.decompress(raw)
            except Exception:
                try:
                    raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
                except Exception:
                    pass

        return raw.decode("utf-8", errors="ignore")

# ------------------------------------------------------------
# Owner audit log
# ------------------------------------------------------------
def _audit(event: str, payload: Dict[str, Any]) -> None:
    _ensure_data_dir()
    rec = {"ts": datetime.utcnow().isoformat() + "Z", "event": event, **payload}
    try:
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass

# ------------------------------------------------------------
# Sitemap discovery + filters
# ------------------------------------------------------------
def _discover_sitemaps_from_robots(domain: str) -> Dict[str, Any]:
    robots_url = f"https://{domain}/robots.txt"
    text = ""
    method_used = "robots_https"

    try:
        text = _http_get_text(robots_url)
    except Exception:
        robots_url = f"http://{domain}/robots.txt"
        method_used = "robots_http"
        try:
            text = _http_get_text(robots_url)
        except Exception:
            text = ""

    sitemaps: List[str] = []
    if text:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if sm:
                    sitemaps.append(sm)

    if not sitemaps:
        method_used = "fallback_common"
        base_https = f"https://{domain}"
        sitemaps = [
            f"{base_https}/sitemap.xml",
            f"{base_https}/sitemap-index.xml",
            f"{base_https}/sitemap_index.xml",
            f"{base_https}/sitemap/sitemap.xml",
            f"{base_https}/sitemaps/sitemap.xml",
            f"{base_https}/sitemap.xml.gz",
            f"{base_https}/sitemap-index.xml.gz",
            f"{base_https}/sitemap_index.xml.gz",
        ]

    seen = set()
    deduped: List[str] = []
    for s in sitemaps:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    return {"robots_url": robots_url, "method_used": method_used, "sitemaps_found": deduped}

def _extract_loc_urls(xml_text: str) -> List[str]:
    return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", xml_text, flags=re.IGNORECASE)

def _is_sitemap_index(xml_text: str) -> bool:
    return bool(re.search(r"<\s*sitemapindex\b", xml_text, flags=re.IGNORECASE))

def _is_probably_xml_url(u: str) -> bool:
    u2 = u.lower().split("?", 1)[0].split("#", 1)[0]
    return u2.endswith(".xml") or u2.endswith(".xml.gz") or "sitemap" in u2

def _url_has_blocked_extension(url: str, block_extensions: List[str]) -> bool:
    u = url.lower().split("?", 1)[0].split("#", 1)[0]
    for ext in (block_extensions or []):
        e = (ext or "").lower().strip()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        if u.endswith(e):
            return True
    return False

def _passes_path_filters(url: str, include_paths: List[str], exclude_paths: List[str]) -> bool:
    u = url.lower()
    inc = [p.lower().strip() for p in (include_paths or []) if p and p.strip()]
    exc = [p.lower().strip() for p in (exclude_paths or []) if p and p.strip()]

    if inc and not any(p in u for p in inc):
        return False
    for p in exc:
        if p in u:
            return False
    return True

def _host_of_url(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower().strip()
    except Exception:
        return ""

def _normalize_hosts(domain: Optional[str], allowed_hosts: List[str], sitemap_url: Optional[str]) -> List[str]:
    hosts = [str(h).lower().strip() for h in (allowed_hosts or []) if str(h).strip()]
    if hosts:
        return sorted(set(hosts))

    if domain:
        d = domain.lower().strip()
        d = re.sub(r"^https?://", "", d).strip("/")
        out = {d, "www." + d}
        if d.startswith("www."):
            out.add(d.replace("www.", "", 1))
        return sorted(out)

    if sitemap_url:
        h = _host_of_url(sitemap_url)
        return [h] if h else []

    return []

def _passes_lang_filters(url: str, allow_lang_prefixes: List[str], block_lang_prefixes: List[str]) -> bool:
    try:
        path = (urlparse(url).path or "/")
    except Exception:
        path = "/"

    allow = [p.strip() for p in (allow_lang_prefixes or []) if p and p.strip()]
    block = [p.strip() for p in (block_lang_prefixes or []) if p and p.strip()]

    if allow and not any(path.startswith(p) for p in allow):
        return False
    if block and any(path.startswith(p) for p in block):
        return False
    return True

def _passes_host_scope(url: str, allowed_hosts: List[str], require_host_match: bool) -> bool:
    if not require_host_match:
        return True
    host = _host_of_url(url)
    if not host:
        return False
    allow = set([h.lower().strip() for h in (allowed_hosts or []) if h and str(h).strip()])
    return host in allow

# ------------------------------------------------------------
# Canonical key + quality scoring
# ------------------------------------------------------------
def _canonical_key_from_url(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)

    parts = u.split("/", 1)
    path = parts[1] if len(parts) > 1 else ""
    path = path.split("?", 1)[0].split("#", 1)[0]

    raw_tokens = re.split(r"[/\-_]+", path)
    junk = set(["art", "mac", "drc", "ddc", "syc", "faq", "news", "index", "sitemap", "xml", "html"])

    tokens: List[str] = []
    for t in raw_tokens:
        t = (t or "").strip()
        if not t or t.isdigit() or t in junk:
            continue
        if re.fullmatch(r"\d{4,}", t):
            continue
        tokens.append(t)

    tokens = tokens[:10]
    return _make_key(" ".join(tokens)) or _make_key(url)

def _authority_quality_score(url: str, base: float = 1.0) -> float:
    u = (url or "").lower()
    score = float(base)

    boosts = [
        ("/diseases-conditions/", 4.0),
        ("/symptoms/", 3.0),
        ("/drugs-supplements/", 3.0),
        ("/tests-procedures/", 2.5),
        ("/healthy-lifestyle/", 2.0),
    ]
    for needle, add in boosts:
        if needle in u:
            score += add

    if "/symptoms-causes/" in u:
        score += 1.5
    if "/diagnosis-treatment/" in u:
        score += 1.2
    if "/definition/" in u:
        score += 0.8

    penalties = [
        ("/about/", 5.0),
        ("/news/", 5.0),
        ("/careers/", 5.0),
        ("/contact", 3.0),
        ("/locations", 3.0),
        ("/patient-visitor-guide", 4.0),
        ("/multimedia/", 1.5),
    ]
    for needle, sub in penalties:
        if needle in u:
            score -= sub

    try:
        path = urlparse(u).path or ""
        depth = len([p for p in path.split("/") if p])
        if depth >= 7:
            score -= 0.3
        if depth >= 10:
            score -= 0.5
    except Exception:
        pass

    if score < 0.1:
        score = 0.1
    if score > 10.0:
        score = 10.0
    return round(score, 3)

# ------------------------------------------------------------
# Snapshot helpers (Queue 5.2)
# ------------------------------------------------------------
def _snapshot_path(run_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(run_id or ""))
    return SNAPSHOT_DIR / f"auto_before_{safe}.json"

def _write_snapshot_before_commit(run_id: str) -> str:
    _ensure_snapshot_dir()
    snap_path = _snapshot_path(run_id)
    current = _safe_read_list(AUTO_PATH)
    # write snapshot WITHOUT invalidating resolve index (snapshot doesn’t affect resolve)
    _ensure_data_dir()
    snap_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(snap_path)

# ------------------------------------------------------------
# Bulk upsert authority URLs into AUTO
# ------------------------------------------------------------
def _bulk_upsert_auto_authority(
    urls: List[str],
    source_label: str,
    now: str,
    import_run_id: str,
    imported_by: str = "owner_sitemap_import",
    import_reason: str = "authority_sitemap_import",
) -> Dict[str, int]:
    dataset = _safe_read_list(AUTO_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    # normalize existing for stable dedup
    for item in dataset:
        if not isinstance(item, dict):
            continue
        raw = str(item.get("url") or "").strip()
        u = _normalize_url_for_storage(raw, prefer_no_www=True, drop_query=True)
        if not u:
            continue
        item["url"] = u
        if u not in by_url:
            by_url[u] = item
            order.append(u)

    added = 0
    updated = 0

    for raw_u in urls:
        u = _normalize_url_for_storage(raw_u, prefer_no_www=True, drop_query=True)
        if not u:
            continue
        if _is_blocked(u):
            continue

        ck = _canonical_key_from_url(u)
        score = _authority_quality_score(u, base=1.0)

        if u not in by_url:
            by_url[u] = {
                "key": ck,
                "phrase": "",
                "url": u,
                "title": "",
                "score": score,
                "source": "authority_sitemap",
                "source_label": source_label,
                "seen_count": 1,
                "first_seen": now,
                "last_seen": now,
                "phrases": [],
                "lang": "en",
                "last_event": import_reason,
                "imported_at": now,
                "import_run_id": import_run_id,
                "imported_by": imported_by,
                "import_reason": import_reason,
            }
            order.append(u)
            added += 1
        else:
            existing = by_url[u]
            if ck:
                existing["key"] = ck

            try:
                prev_score = float(existing.get("score", 1.0) or 1.0)
            except Exception:
                prev_score = 1.0
            existing["score"] = max(prev_score, score)

            existing["source"] = existing.get("source") or "authority_sitemap"
            existing["source_label"] = source_label
            existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
            existing["last_seen"] = now
            existing["first_seen"] = existing.get("first_seen") or now
            existing["last_event"] = import_reason

            existing["imported_at"] = now
            existing["import_run_id"] = import_run_id
            existing["imported_by"] = imported_by
            existing["import_reason"] = import_reason

            updated += 1

    out = [by_url[u] for u in order if u in by_url]
    _atomic_write_json(AUTO_PATH, out)
    return {"added": added, "updated": updated}

# ------------------------------------------------------------
# Models
# ------------------------------------------------------------
class ExternalCandidate(BaseModel):
    phrase: str
    url: str
    title: Optional[str] = None
    score: float = 1.0
    source: str = "backend"
    source_label: Optional[str] = None

class ManualAddRequest(BaseModel):
    phrase: str
    url: str
    title: Optional[str] = None
    score: float = 5.0
    source: str = "manual-owner"
    lang: str = "en"

class ManualUpdateRequest(BaseModel):
    url: str
    phrase: Optional[str] = None
    title: Optional[str] = None
    score: Optional[float] = None
    disabled: Optional[bool] = None
    source: Optional[str] = None
    lang: Optional[str] = None

class ManualToggleRequest(BaseModel):
    url: str
    disabled: bool = True

class ManualDeleteRequest(BaseModel):
    url: str

class SitemapFilters(BaseModel):
    include_paths: List[str] = Field(default_factory=list)
    exclude_paths: List[str] = Field(default_factory=list)
    block_extensions: List[str] = Field(default_factory=lambda: [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"])
    block_lang_prefixes: List[str] = Field(default_factory=list)
    allow_lang_prefixes: List[str] = Field(default_factory=list)
    require_host_match: bool = True
    allowed_hosts: List[str] = Field(default_factory=list)

class OwnerSitemapImportRequest(BaseModel):
    source_label: str
    domain: Optional[str] = None
    sitemap_url: Optional[str] = None
    filters: Optional[SitemapFilters] = None
    commit: bool = False

class ExternalLogEvent(BaseModel):
    event: str = "auto_apply"
    phrase: str
    url: str
    title: Optional[str] = None
    providerId: Optional[str] = None
    providerLabel: Optional[str] = None
    docCode: Optional[str] = None
    docTitle: Optional[str] = None
    lang: str = "en"
    source: str = "auto_link"
    source_label: Optional[str] = None

class OwnerRollbackRequest(BaseModel):
    import_run_id: str
    preview: bool = True

# ------------------------------------------------------------
# Resolve index helpers
# ------------------------------------------------------------
def _extra_keys_from_url(url: str) -> List[str]:
    try:
        path = (urlparse(url).path or "").strip("/")
    except Exception:
        return []

    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        return []

    section = parts[0].lower().strip()
    slug = parts[1].lower().strip()

    allowed_sections = {"diseases-conditions", "drugs-supplements", "symptoms"}
    if section not in allowed_sections:
        return []

    slug = re.sub(r"[^a-z0-9\-]+", "", slug)
    if not slug:
        return []
    return [_make_key(slug)]

def _index_rows_by_key(rows: List[Dict[str, Any]], is_manual: bool) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}

    for item in rows:
        if not isinstance(item, dict):
            continue

        url = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not url:
            continue
        if _is_blocked(url):
            continue

        item["url"] = url

        if is_manual and bool(item.get("disabled") is True):
            continue

        stored = str(item.get("key") or item.get("phrase") or "").strip()
        k = _make_key(stored)
        if k:
            out.setdefault(k, []).append(item)

        if not is_manual:
            for ek in _extra_keys_from_url(url):
                out.setdefault(ek, []).append(item)

    def _score(x: Dict[str, Any]) -> float:
        try:
            return float(x.get("score", 1.0) or 1.0)
        except Exception:
            return 1.0

    def _last_seen(x: Dict[str, Any]) -> str:
        return str(x.get("last_seen") or x.get("updated_at") or x.get("added_at") or "")

    for kk, lst in out.items():
        lst.sort(key=lambda x: (-_score(x), _last_seen(x), str(x.get("url") or "")))

    return out

def _ensure_resolve_index_uptodate() -> None:
    manual_mtime = _get_mtime_safe(MANUAL_PATH)
    auto_mtime = _get_mtime_safe(AUTO_PATH)

    if _RESOLVE_INDEX["manual_mtime"] != manual_mtime:
        manual_rows = _safe_read_list(MANUAL_PATH)
        _RESOLVE_INDEX["manual_by_key"] = _index_rows_by_key(manual_rows, is_manual=True)
        _RESOLVE_INDEX["manual_mtime"] = manual_mtime

    if _RESOLVE_INDEX["auto_mtime"] != auto_mtime:
        auto_rows = _safe_read_list(AUTO_PATH)
        _RESOLVE_INDEX["auto_by_key"] = _index_rows_by_key(auto_rows, is_manual=False)
        _RESOLVE_INDEX["auto_mtime"] = auto_mtime

# ------------------------------------------------------------
# Resolve
# ------------------------------------------------------------
@router.get("/resolve", response_model=List[ExternalCandidate])
async def external_resolve(phrase: str, lang: str = "en", source_label: Optional[str] = None):
    q = (phrase or "").strip()
    if not q:
        return []

    query_key = _make_key(q)
    _ensure_resolve_index_uptodate()

    manual_hits = _RESOLVE_INDEX["manual_by_key"].get(query_key, []) or []
    auto_hits = _RESOLVE_INDEX["auto_by_key"].get(query_key, []) or []

    hits = manual_hits if manual_hits else auto_hits

    want_label = (source_label or "").strip().lower()
    if want_label:
        hits = [
            it for it in hits
            if str((it or {}).get("source_label") or "").strip().lower() == want_label
        ]

    out: List[ExternalCandidate] = []
    for item in hits[:8]:
        if not isinstance(item, dict):
            continue
        url = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not url:
            continue
        out.append(
            ExternalCandidate(
                phrase=q,
                url=url,
                title=item.get("title") or item.get("phrase") or q,
                score=float(item.get("score", 1.0) or 1.0),
                source=str(item.get("source") or ("manual" if manual_hits else "auto")),
                source_label=(str(item.get("source_label")).strip() if item.get("source_label") else None),
            )
        )

    out.sort(key=lambda x: x.score, reverse=True)
    return out

# ------------------------------------------------------------
# Log (AUTO upsert) — normalized
# ------------------------------------------------------------
@router.post("/log")
async def external_log(payload: ExternalLogEvent = Body(...)):
    phrase = (payload.phrase or "").strip()
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)

    if not phrase or not url:
        raise HTTPException(status_code=400, detail="Missing phrase or url")
    if _is_blocked(url):
        raise HTTPException(status_code=400, detail="URL blocked by blacklist")

    dataset = _safe_read_list(AUTO_PATH)
    now = datetime.utcnow().isoformat() + "Z"

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    for it in dataset:
        if not isinstance(it, dict):
            continue
        u = _normalize_url_for_storage(str(it.get("url") or ""), prefer_no_www=True, drop_query=True)
        if not u:
            continue
        it["url"] = u
        if u not in by_url:
            by_url[u] = it
            order.append(u)

    existing = by_url.get(url)

    if not existing:
        entry = {
            "key": _make_key(phrase),
            "phrase": phrase,
            "url": url,
            "title": payload.title or phrase,
            "score": 1.0,
            "source": payload.source or "auto-log",
            "source_label": (payload.source_label or "").strip() or None,
            "seen_count": 1,
            "first_seen": now,
            "last_seen": now,
            "phrases": [phrase],
            "providerId": payload.providerId,
            "providerLabel": payload.providerLabel,
            "lang": payload.lang or "en",
            "last_event": payload.event or "auto_apply",
            "docCode": payload.docCode,
            "docTitle": payload.docTitle,
            "imported_at": now,
        }
        by_url[url] = entry
        order.append(url)
        _atomic_write_json(AUTO_PATH, [by_url[u] for u in order if u in by_url])
        return {"ok": True, "action": "added", "normalized_url": url, "path": str(AUTO_PATH)}

    existing["url"] = url
    existing["title"] = payload.title or existing.get("title") or phrase
    existing["phrase"] = existing.get("phrase") or phrase
    existing["key"] = _make_key(existing.get("phrase") or phrase)
    existing["source"] = existing.get("source") or (payload.source or "auto-log")

    existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
    existing["last_seen"] = now
    existing["first_seen"] = existing.get("first_seen") or now
    existing["last_event"] = payload.event or existing.get("last_event") or "auto_apply"

    if payload.source_label:
        existing["source_label"] = (payload.source_label or "").strip() or existing.get("source_label")

    ph = existing.get("phrases")
    if not isinstance(ph, list):
        ph = []
    if phrase and phrase not in ph:
        ph.append(phrase)
    existing["phrases"] = ph[-50:]

    existing["providerId"] = payload.providerId or existing.get("providerId")
    existing["providerLabel"] = payload.providerLabel or existing.get("providerLabel")
    existing["docCode"] = payload.docCode or existing.get("docCode")
    existing["docTitle"] = payload.docTitle or existing.get("docTitle")
    existing["lang"] = payload.lang or existing.get("lang") or "en"

    by_url[url] = existing
    _atomic_write_json(AUTO_PATH, [by_url[u] for u in order if u in by_url])
    return {"ok": True, "action": "updated", "normalized_url": url, "seen_count": existing["seen_count"], "path": str(AUTO_PATH)}

# ------------------------------------------------------------
# Import: CSV/TXT -> merge into AUTO
# ------------------------------------------------------------
@router.post("/import")
async def import_external_file(file: UploadFile = File(...), source: str = "import"):
    if not file:
        raise HTTPException(status_code=400, detail="file is required")

    name = (file.filename or "").lower()
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="ignore")

    dataset = _safe_read_list(AUTO_PATH)
    now = datetime.utcnow().isoformat() + "Z"

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    added = 0
    updated = 0
    skipped_blocked = 0
    skipped_bad = 0

    def upsert(display_phrase: str, url: str, title: Optional[str], score: float):
        nonlocal added, updated, skipped_blocked, skipped_bad

        url2 = _normalize_url_for_storage(url, prefer_no_www=True, drop_query=True)
        if not url2:
            skipped_bad += 1
            return
        if _is_blocked(url2):
            skipped_blocked += 1
            return

        phrase2 = (display_phrase or "").strip()
        title2 = (title or "").strip() if title else None
        label = phrase2 or title2 or url2
        key = _make_key(label)

        existing = by_url.get(url2)
        if not existing:
            by_url[url2] = {
                "key": key,
                "phrase": phrase2 or label,
                "url": url2,
                "title": title2 or phrase2 or url2,
                "score": float(score or 1.0),
                "source": source,
                "seen_count": 1,
                "first_seen": now,
                "last_seen": now,
                "phrases": [phrase2] if phrase2 else [],
                "lang": "en",
                "last_event": "import",
                "imported_at": now,
            }
            order.append(url2)
            added += 1
            return

        existing["url"] = url2
        existing["key"] = key
        existing["phrase"] = existing.get("phrase") or (phrase2 or label)
        existing["title"] = title2 or existing.get("title") or phrase2 or url2

        try:
            prev = float(existing.get("score", 1.0) or 1.0)
        except Exception:
            prev = 1.0
        existing["score"] = max(prev, float(score or 1.0))

        existing["source"] = existing.get("source") or source
        existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + 1
        existing["last_seen"] = now
        existing["first_seen"] = existing.get("first_seen") or now

        phrases = existing.get("phrases")
        if not isinstance(phrases, list):
            phrases = []
        if phrase2 and phrase2 not in phrases:
            phrases.append(phrase2)
        existing["phrases"] = phrases[-50:]

        updated += 1

    if name.endswith(".csv"):
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            if not isinstance(row, dict):
                continue
            phrase = (row.get("phrase") or "").strip()
            key_in = (row.get("key") or "").strip()
            url = (row.get("url") or "").strip()
            title = (row.get("title") or "").strip() or None
            try:
                score = float(row.get("score") or 1.0)
            except Exception:
                score = 1.0
            upsert(phrase or key_in, url, title, score)
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                url_part, title_part = [x.strip() for x in line.split("|", 1)]
                upsert("", url_part, title_part or None, 1.0)
            else:
                upsert("", line, None, 1.0)

    out = [by_url[u] for u in order if u in by_url]
    _atomic_write_json(AUTO_PATH, out)
    return {
        "ok": True,
        "path": str(AUTO_PATH),
        "added": added,
        "updated": updated,
        "skipped_blocked": skipped_blocked,
        "skipped_bad": skipped_bad,
    }

# ------------------------------------------------------------
# Manual dataset management
# ------------------------------------------------------------
@router.get("/manual/list")
async def manual_list(limit: int = 200):
    data = _safe_read_list(MANUAL_PATH)
    return {"ok": True, "count": len(data), "items": data[: max(1, min(limit, 2000))]}

@router.post("/manual/add")
async def manual_add(payload: ManualAddRequest = Body(...)):
    phrase = (payload.phrase or "").strip()
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    title = (payload.title or "").strip() if payload.title else None

    if not phrase or not url:
        raise HTTPException(status_code=400, detail="phrase and url are required")
    if _is_blocked(url):
        raise HTTPException(status_code=400, detail="URL blocked by blacklist")

    dataset = _safe_read_list(MANUAL_PATH)
    now = datetime.utcnow().isoformat() + "Z"
    key = _make_key(phrase)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    entry = {
        "key": key,
        "phrase": phrase,
        "url": url,
        "title": title or phrase,
        "score": float(payload.score or 5.0),
        "source": payload.source or "manual-owner",
        "lang": payload.lang or "en",
        "disabled": False,
        "last_event": "manual_add",
        "added_at": now,
    }

    if url not in by_url:
        by_url[url] = entry
        order.append(url)
        _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
        _audit("manual_add", {"url": url, "phrase": phrase, "title": entry["title"]})
        return {"ok": True, "action": "added", "path": str(MANUAL_PATH)}

    existing = by_url[url]
    existing.update(entry)
    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_add_update", {"url": url, "phrase": phrase, "title": entry["title"]})
    return {"ok": True, "action": "updated", "path": str(MANUAL_PATH)}

@router.post("/manual/update")
async def manual_update(payload: ManualUpdateRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)
    now = datetime.utcnow().isoformat() + "Z"

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    if url not in by_url:
        raise HTTPException(status_code=404, detail="manual url not found")

    existing = by_url[url]

    new_phrase = (payload.phrase if payload.phrase is not None else existing.get("phrase") or "").strip()
    new_title = (payload.title if payload.title is not None else existing.get("title")) or (new_phrase or existing.get("title"))
    new_score = float(payload.score) if payload.score is not None else float(existing.get("score", 5.0) or 5.0)
    new_disabled = bool(payload.disabled) if payload.disabled is not None else bool(existing.get("disabled", False))
    new_source = payload.source if payload.source is not None else existing.get("source", "manual-owner")
    new_lang = payload.lang if payload.lang is not None else existing.get("lang", "en")

    if not new_phrase:
        new_phrase = str(existing.get("phrase") or "").strip()

    existing.update({
        "phrase": new_phrase,
        "key": _make_key(new_phrase) if new_phrase else existing.get("key"),
        "title": new_title or new_phrase,
        "score": new_score,
        "disabled": new_disabled,
        "source": new_source,
        "lang": new_lang,
        "last_event": "manual_update",
        "updated_at": now,
    })

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_update", {"url": url, "disabled": new_disabled, "phrase": new_phrase, "title": existing.get("title")})
    return {"ok": True, "action": "updated", "path": str(MANUAL_PATH)}

@router.post("/manual/toggle")
async def manual_toggle(payload: ManualToggleRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    if url not in by_url:
        raise HTTPException(status_code=404, detail="manual url not found")

    now = datetime.utcnow().isoformat() + "Z"
    existing = by_url[url]
    existing["disabled"] = bool(payload.disabled)
    existing["last_event"] = "manual_toggle"
    existing["updated_at"] = now

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_toggle", {"url": url, "disabled": bool(payload.disabled)})
    return {"ok": True, "action": "toggled", "disabled": bool(payload.disabled)}

@router.post("/manual/delete")
async def manual_delete(payload: ManualDeleteRequest = Body(...)):
    url = _normalize_url_for_storage(payload.url, prefer_no_www=True, drop_query=True)
    if not url:
        raise HTTPException(status_code=400, detail="url is required")

    dataset = _safe_read_list(MANUAL_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in dataset:
        if not isinstance(item, dict):
            continue
        u = _normalize_url_for_storage(str(item.get("url") or ""), prefer_no_www=True, drop_query=True)
        if u and u not in by_url:
            item["url"] = u
            by_url[u] = item
            order.append(u)

    if url not in by_url:
        raise HTTPException(status_code=404, detail="manual url not found")

    by_url.pop(url, None)
    order = [u for u in order if u != url]

    _atomic_write_json(MANUAL_PATH, [by_url[u] for u in order if u in by_url])
    _audit("manual_delete", {"url": url})
    return {"ok": True, "action": "deleted", "removed": 1}

# ------------------------------------------------------------
# AUTO cleanup (GET + POST)
# ------------------------------------------------------------
@router.post("/owner/auto/cleanup")
async def owner_auto_cleanup(preview: bool = True):
    dataset = _safe_read_list(AUTO_PATH)

    by_url: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []

    changed = 0
    merged = 0

    for it in dataset:
        if not isinstance(it, dict):
            continue

        raw_url = str(it.get("url") or "").strip()
        norm = _normalize_url_for_storage(raw_url, prefer_no_www=True, drop_query=True)
        if not norm:
            continue

        if norm != raw_url:
            changed += 1

        it["url"] = norm

        if norm in by_url:
            merged += 1
            existing = by_url[norm]

            try:
                existing_score = float(existing.get("score", 1.0) or 1.0)
            except Exception:
                existing_score = 1.0
            try:
                new_score = float(it.get("score", 1.0) or 1.0)
            except Exception:
                new_score = 1.0
            existing["score"] = max(existing_score, new_score)

            ph1 = existing.get("phrases")
            if not isinstance(ph1, list):
                ph1 = []
            ph2 = it.get("phrases")
            if not isinstance(ph2, list):
                ph2 = []
            for p in ph2:
                if p and p not in ph1:
                    ph1.append(p)
            existing["phrases"] = ph1[-50:]

            existing["seen_count"] = int(existing.get("seen_count", 0) or 0) + int(it.get("seen_count", 0) or 0)
            existing["last_seen"] = max(str(existing.get("last_seen") or ""), str(it.get("last_seen") or ""))

            by_url[norm] = existing
            continue

        by_url[norm] = it
        order.append(norm)

    cleaned = [by_url[u] for u in order if u in by_url]

    result = {
        "ok": True,
        "preview": bool(preview),
        "before": len(dataset),
        "after": len(cleaned),
        "normalized_changed_count": changed,
        "duplicates_merged_count": merged,
        "path": str(AUTO_PATH),
    }

    if not preview:
        _atomic_write_json(AUTO_PATH, cleaned)
        result["written"] = True

    return result

@router.get("/owner/auto/cleanup")
async def owner_auto_cleanup_get(preview: bool = True):
    return await owner_auto_cleanup(preview=preview)

# ------------------------------------------------------------
# OWNER: Import runs (reads audit log JSONL)  ✅
# ------------------------------------------------------------
@router.get("/owner/import/runs")
async def owner_import_runs(limit: int = 20):
    limit = max(1, min(int(limit or 20), 200))
    if not AUDIT_PATH.exists():
        return {"ok": True, "count": 0, "items": [], "path": str(AUDIT_PATH)}

    items: List[Dict[str, Any]] = []
    try:
        lines = AUDIT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line in reversed(lines):
            line = (line or "").strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            ev = str(rec.get("event") or "")
            if ev not in ("owner_sitemap_commit_auto", "owner_import_rollback"):
                continue

            items.append(rec)
            if len(items) >= limit:
                break

        items.reverse()
        return {"ok": True, "count": len(items), "items": items, "path": str(AUDIT_PATH)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"import_runs_error: {type(e).__name__}: {str(e)}")

def _rebuild_import_runs_index_from_audit(max_keep: int = 200) -> Dict[str, Any]:
    """
    Rebuild import_runs_index.json from owner_audit_log.jsonl.
    Uses events that contain import_run_id (commit + rollback).
    """
    _ensure_data_dir()

    if not AUDIT_PATH.exists():
        _atomic_write_json(IMPORT_RUNS_INDEX_PATH, {"runs": []})
        return {"ok": True, "rebuilt": True, "count": 0, "path": str(IMPORT_RUNS_INDEX_PATH)}

    lines = AUDIT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    runs: List[Dict[str, Any]] = []

    for line in reversed(lines):
        line = (line or "").strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue

        ev = str(rec.get("event") or "")
        if ev not in ("owner_sitemap_commit_auto", "owner_import_rollback"):
            continue

        rid = str(rec.get("import_run_id") or "").strip()
        if not rid:
            continue

        runs.append({
            "import_run_id": rid,
            "ts": rec.get("ts"),
            "event": ev,
            "source_label": rec.get("source_label"),
            "auto_added": rec.get("auto_added"),
            "auto_updated": rec.get("auto_updated"),
            "written_count": rec.get("written_count"),
            "snapshot_path": rec.get("snapshot_path"),
            "auto_path": rec.get("auto_path"),
        })

        if len(runs) >= max_keep:
            break

    _atomic_write_json(IMPORT_RUNS_INDEX_PATH, {"runs": runs})
    return {"ok": True, "rebuilt": True, "count": len(runs), "path": str(IMPORT_RUNS_INDEX_PATH)}


@router.get("/owner/import/runs/index")
async def owner_import_runs_index(limit: int = 50, rebuild: bool = False):
    limit = max(1, min(int(limit or 50), 200))

    # If file missing, create it
    if not IMPORT_RUNS_INDEX_PATH.exists():
        _atomic_write_json(IMPORT_RUNS_INDEX_PATH, {"runs": []})

    # If user requests rebuild OR file is empty, rebuild from audit
    raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
    runs = (raw or {}).get("runs") if isinstance(raw, dict) else []
    if rebuild or not isinstance(runs, list) or len(runs) == 0:
        _rebuild_import_runs_index_from_audit(max_keep=200)
        raw = _safe_read_json(IMPORT_RUNS_INDEX_PATH)
        runs = (raw or {}).get("runs") if isinstance(raw, dict) else []
        if not isinstance(runs, list):
            runs = []

    return {
        "ok": True,
        "count": min(limit, len(runs)),
        "items": runs[:limit],
        "path": str(IMPORT_RUNS_INDEX_PATH),
    }



# ------------------------------------------------------------
# OWNER: Rollback by restoring snapshot ✅
# ------------------------------------------------------------
@router.post("/owner/import/rollback")
async def owner_import_rollback(payload: OwnerRollbackRequest = Body(...)):
    run_id = (payload.import_run_id or "").strip()
    if not run_id:
        raise HTTPException(status_code=400, detail="import_run_id is required")

    snap_path = _snapshot_path(run_id)
    if not snap_path.exists():
        raise HTTPException(status_code=404, detail=f"snapshot not found for import_run_id={run_id}")

    before_count = len(_safe_read_list(AUTO_PATH))
    snap_data = _safe_read_list(snap_path)
    after_count = len(snap_data)

    if payload.preview:
        return {
            "ok": True,
            "preview": True,
            "import_run_id": run_id,
            "auto_before_count": before_count,
            "auto_after_count": after_count,
            "snapshot_path": str(snap_path),
            "action": "would_restore_snapshot",
        }

    _atomic_write_json(AUTO_PATH, snap_data)

    _audit("owner_import_rollback", {
        "import_run_id": run_id,
        "snapshot_path": str(snap_path),
        "auto_before_count": before_count,
        "auto_after_count": after_count,
    })

    return {
        "ok": True,
        "preview": False,
        "import_run_id": run_id,
        "auto_before_count": before_count,
        "auto_after_count": after_count,
        "snapshot_path": str(snap_path),
        "action": "restored",
    }

# ------------------------------------------------------------
# OWNER: Remote sitemap import (C4)
# ------------------------------------------------------------
@router.post("/owner/sitemap/import")
async def owner_sitemap_import(payload: OwnerSitemapImportRequest = Body(...)):
    source_label = (payload.source_label or "").strip()
    if not source_label:
        raise HTTPException(status_code=400, detail="source_label is required")

    src_cfg = _get_source_config(source_label)
    if not src_cfg:
        raise HTTPException(status_code=400, detail=f"Unknown source_label: {source_label}")

    defaults = src_cfg.get("defaults") if isinstance(src_cfg.get("defaults"), dict) else {}

    domain_in = (payload.domain or "").strip()
    sitemap_url = (payload.sitemap_url or "").strip()

    if sitemap_url:
        domain = domain_in
    else:
        domain = domain_in or str(src_cfg.get("domain") or "").strip()

    if not domain and not sitemap_url:
        raise HTTPException(status_code=400, detail="Provide domain OR sitemap_url (or set domain in source config)")
    if domain_in and sitemap_url:
        raise HTTPException(status_code=400, detail="Provide only one: domain OR sitemap_url")

    if domain:
        d = domain.lower()
        d = re.sub(r"^https?://", "", d).strip("/")
        domain = d

    def _list_or_default(v, fallback):
        return v if isinstance(v, list) else fallback

    eff_include = _list_or_default(defaults.get("include_paths"), [])
    eff_exclude = _list_or_default(defaults.get("exclude_paths"), [])
    eff_block_ext = _list_or_default(defaults.get("block_extensions"), [".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp4"])
    eff_block_lang = _list_or_default(defaults.get("block_lang_prefixes"), [])
    eff_allow_lang = _list_or_default(defaults.get("allow_lang_prefixes"), [])
    eff_require_host = bool(defaults.get("require_host_match", True))
    eff_allowed_hosts = _list_or_default(defaults.get("allowed_hosts"), [])

    if payload.filters is not None:
        f = payload.filters
        if f.include_paths:
            eff_include = f.include_paths
        if f.exclude_paths:
            eff_exclude = f.exclude_paths
        if f.block_extensions:
            eff_block_ext = f.block_extensions
        if f.block_lang_prefixes:
            eff_block_lang = f.block_lang_prefixes
        if f.allow_lang_prefixes:
            eff_allow_lang = f.allow_lang_prefixes
        eff_require_host = bool(f.require_host_match)
        if f.allowed_hosts:
            eff_allowed_hosts = f.allowed_hosts

    include_paths = [p.strip() for p in (eff_include or []) if p and p.strip()]
    exclude_paths = [p.strip() for p in (eff_exclude or []) if p and p.strip()]
    block_ext = [e.strip().lower() for e in (eff_block_ext or []) if e and e.strip()]
    block_lang = [p.strip() for p in (eff_block_lang or []) if p and p.strip()]
    allow_lang = [p.strip() for p in (eff_allow_lang or []) if p and p.strip()]

    require_host_match = bool(eff_require_host)
    allowed_hosts = _normalize_hosts(domain, eff_allowed_hosts or [], sitemap_url)

    _audit("owner_sitemap_import_request", {
        "source_label": source_label,
        "domain": domain or None,
        "sitemap_url": sitemap_url or None,
        "filters_used": {
            "include_paths": include_paths,
            "exclude_paths": exclude_paths,
            "block_extensions": block_ext,
            "block_lang_prefixes": block_lang,
            "allow_lang_prefixes": allow_lang,
            "require_host_match": require_host_match,
            "allowed_hosts": allowed_hosts,
        },
        "commit": bool(payload.commit),
    })

    if domain:
        discovered = _discover_sitemaps_from_robots(domain)
    else:
        discovered = {"robots_url": None, "method_used": "direct_sitemap_url", "sitemaps_found": [sitemap_url]}

    _audit("owner_sitemap_discovered", {
        "source_label": source_label,
        "method_used": discovered.get("method_used"),
        "sitemaps_found_count": len(discovered.get("sitemaps_found") or []),
    })

    MAX_SITEMAPS_TOTAL = None
    MAX_URLS_RETURN_SAMPLE = 200
    MAX_WRITE_URLS = None

    queue: List[str] = list(discovered.get("sitemaps_found") or [])
    seen_sitemaps = set()

    sitemaps_processed = 0
    sitemap_indexes_seen = 0
    child_sitemaps_enqueued = 0

    urls_found_total = 0
    urls_after_filters = 0
    filtered_out = 0
    skipped_blocked = 0
    skipped_ext = 0
    skipped_host = 0
    skipped_lang = 0

    fetch_errors = 0
    fetch_error_samples: List[Dict[str, str]] = []

    accepted_sample: List[str] = []
    accepted_urls_all: List[str] = []
    seen_urls = set()

    def _cap_ok(cap, current):
        return (cap is None) or (current < cap)

    while queue and _cap_ok(MAX_SITEMAPS_TOTAL, sitemaps_processed):
        sm_url = _normalize_url(queue.pop(0))
        if not sm_url or not sm_url.startswith("http"):
            continue
        if sm_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sm_url)

        try:
            xml = _http_get_text(sm_url, timeout_sec=25)
        except Exception as e:
            fetch_errors += 1
            if len(fetch_error_samples) < 5:
                fetch_error_samples.append({"sitemap_url": sm_url, "error": str(e)})
            _audit("owner_sitemap_fetch_error", {
                "source_label": source_label,
                "sitemap_url": sm_url,
                "error": str(e),
            })
            continue

        sitemaps_processed += 1
        locs = _extract_loc_urls(xml)
        urls_found_total += len(locs)

        if _is_sitemap_index(xml):
            sitemap_indexes_seen += 1
            for child in locs:
                child = _normalize_url(child)
                if not child or not child.startswith("http"):
                    continue
                if child in seen_sitemaps:
                    continue
                if _is_probably_xml_url(child):
                    queue.append(child)
                    child_sitemaps_enqueued += 1
            continue

        for u in locs:
            u = _normalize_url(u)
            if not u or not u.startswith("http"):
                continue
            if u in seen_urls:
                continue
            seen_urls.add(u)

            if not _passes_host_scope(u, allowed_hosts, require_host_match):
                skipped_host += 1
                continue
            if not _passes_lang_filters(u, allow_lang, block_lang):
                skipped_lang += 1
                continue
            if _url_has_blocked_extension(u, block_ext):
                skipped_ext += 1
                continue
            if not _passes_path_filters(u, include_paths, exclude_paths):
                filtered_out += 1
                continue
            if _is_blocked(u):
                skipped_blocked += 1
                continue

            urls_after_filters += 1

            if len(accepted_sample) < MAX_URLS_RETURN_SAMPLE:
                accepted_sample.append(u)

            if _cap_ok(MAX_WRITE_URLS, len(accepted_urls_all)):
                accepted_urls_all.append(u)

    _audit("owner_sitemap_step4_recursive", {
        "source_label": source_label,
        "sitemaps_processed": sitemaps_processed,
        "urls_found_total": urls_found_total,
        "urls_after_filters": urls_after_filters,
        "filtered_out": filtered_out,
        "skipped_ext": skipped_ext,
        "skipped_blocked": skipped_blocked,
        "skipped_host": skipped_host,
        "skipped_lang": skipped_lang,
        "fetch_errors": fetch_errors,
        "cap_max_sitemaps_total": MAX_SITEMAPS_TOTAL or "unlimited",
        "cap_max_write_urls": MAX_WRITE_URLS or "unlimited",
    })

    auto_added = 0
    auto_updated = 0
    import_run_id: Optional[str] = None
    snapshot_path: Optional[str] = None

    if payload.commit:
        now = datetime.utcnow().isoformat() + "Z"
        import_run_id = _new_import_run_id("auth")

        # ✅ snapshot BEFORE writing
        snapshot_path = _write_snapshot_before_commit(import_run_id)

        stats = _bulk_upsert_auto_authority(
            accepted_urls_all,
            source_label,
            now,
            import_run_id=import_run_id,
            imported_by="owner_sitemap_import",
            import_reason="authority_sitemap_import",
        )
        auto_added = int(stats.get("added", 0) or 0)
        auto_updated = int(stats.get("updated", 0) or 0)

        _audit("owner_sitemap_commit_auto", {
            "source_label": source_label,
            "auto_added": auto_added,
            "auto_updated": auto_updated,
            "written_count": len(accepted_urls_all),
            "auto_path": str(AUTO_PATH),
            "import_run_id": import_run_id,
            "snapshot_path": snapshot_path,
        })

        _append_import_run_index({
    "import_run_id": import_run_id,
    "ts": now,
    "source_label": source_label,
    "written_count": len(accepted_urls_all),
    "auto_added": auto_added,
    "auto_updated": auto_updated,
    "snapshot_path": snapshot_path,
})



    return {
        "ok": True,
        "stage": "C4_STEP_5_COMMIT_DONE" if payload.commit else "C4_STEP_4_RECURSIVE_TRAVERSAL_DONE",
        "source_label": source_label,
        "domain": domain or None,
        "sitemap_url": sitemap_url or None,
        "filters_used": {
            "include_paths": include_paths,
            "exclude_paths": exclude_paths,
            "block_extensions": block_ext,
            "require_host_match": require_host_match,
            "allowed_hosts": allowed_hosts,
            "allow_lang_prefixes": allow_lang,
            "block_lang_prefixes": block_lang,
        },
        "import_run_id": import_run_id,
        "snapshot_path": snapshot_path,
        "robots_url": discovered.get("robots_url"),
        "method_used": discovered.get("method_used"),
        "sitemaps_seeded": len(discovered.get("sitemaps_found") or []),
        "sitemaps_processed": sitemaps_processed,
        "sitemap_indexes_seen": sitemap_indexes_seen,
        "child_sitemaps_enqueued": child_sitemaps_enqueued,
        "urls_found_total": urls_found_total,
        "urls_after_filters": urls_after_filters,
        "filtered_out": filtered_out,
        "skipped_ext": skipped_ext,
        "skipped_blocked": skipped_blocked,
        "skipped_host": skipped_host,
        "skipped_lang": skipped_lang,
        "fetch_errors": fetch_errors,
        "fetch_error_samples": fetch_error_samples,
        "accepted_sample": accepted_sample,
        "commit": bool(payload.commit),
        "auto_added": auto_added,
        "auto_updated": auto_updated,
        "auto_path": str(AUTO_PATH),
        "caps": {
            "max_sitemaps_total": MAX_SITEMAPS_TOTAL or "unlimited",
            "max_write_urls": MAX_WRITE_URLS or "unlimited",
            "max_urls_return_sample": MAX_URLS_RETURN_SAMPLE,
        },
    }
