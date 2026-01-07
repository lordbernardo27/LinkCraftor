# LinkCraftor/backend/server/external_dataset.py
# ---------------------------------------------------------
# Simple JSON-backed Global External URL Dataset.
#
# Purpose:
# - Store "known good" external article URLs (NOT search pages)
# - Map many phrases -> a canonical semantic key -> best URL
# - Let /api/external/log gradually grow this dataset over time
#
# JSON shape:
# {
#   "version": 1,
#   "urls": {
#     "https://example.com/article": {
#       "url": "...",
#       "canonical_key": "cervical mucus",
#       "phrases": ["white cervical mucus"],
#       "origins": ["manual_seed", "auto_log"],
#       "providers": ["pubmed", "acog"],
#       "stats": { "seen": 3, "avg_confidence": 0.91, "last_confidence": 0.94 },
#       "created_at": "2025-01-01T00:00:00Z",
#       "updated_at": "2025-01-02T00:00:00Z"
#     }
#   }
# }

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import datetime

from .external_scoring import (
    ExternalConfidenceResult,
    phrase_to_semantic_key,
)

# --- NEW: point legacy server dataset module to the unified auto dataset ---
from pathlib import Path

# external_dataset.py is at backend/server/external_dataset.py
# project root is 2 levels up from /backend/server
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "backend" / "data" / "global_external_auto.json"


# ---------------------------------------------------------
# 1) Seed URLs – small starter set (optional)
# ---------------------------------------------------------
# These are starter examples. Replace with real article URLs later.
SEED_URLS = [
    {
        "url": "https://medlineplus.gov/pregnancy.html",
        "phrase": "pregnancy",
        "provider": "medlineplus",
    },
    {
        "url": "https://medlineplus.gov/ency/article/001911.htm",
        "phrase": "ovulation",
        "provider": "medlineplus",
    },
]


# ---------------------------------------------------------
# 2) Core load/save helpers
# ---------------------------------------------------------

from datetime import datetime

def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_data_dir() -> None:
    # Make sure backend/data exists
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_global_dataset() -> Dict[str, Any]:
    """
    Load JSON from disk. If the file does not exist,
    create a fresh structure and seed it with SEED_URLS.
    """
    ensure_data_dir()

    if not DATA_FILE.exists():
        data: Dict[str, Any] = {"version": 1, "urls": {}}
        now = _now_iso()

        for seed in SEED_URLS:
            url = str(seed.get("url") or "").strip()
            phrase = str(seed.get("phrase") or "").strip()
            provider = str(seed.get("provider") or "manual_seed").strip()

            if not url or not phrase:
                continue

            canonical_key = phrase_to_semantic_key(phrase)

            # NOTE: you are using URL as the key here (kept as-is)
            data["urls"][url] = {
                "url": url,
                "canonical_key": canonical_key,
                "phrases": [phrase],
                "origins": ["manual_seed"],
                "providers": [provider],
                "stats": {
                    "seen": 1,
                    "avg_confidence": 0.95,
                    "last_confidence": 0.95,
                },
                "created_at": now,
                "updated_at": now,
            }

        save_global_dataset(data)
        return data

    # File exists – load it safely
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"version": 1, "urls": {}}
        save_global_dataset(data)
        return data

    # Ensure basic shape
    if not isinstance(data, dict):
        data = {"version": 1, "urls": {}}

    if "urls" not in data or not isinstance(data["urls"], dict):
        data["urls"] = {}

    if "version" not in data:
        data["version"] = 1

    return data


def save_global_dataset(data: Dict[str, Any]) -> None:
    ensure_data_dir()
    tmp_file = DATA_FILE.with_suffix(".tmp")
    with tmp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp_file.replace(DATA_FILE)



# ---------------------------------------------------------
# 3) Read helpers
# ---------------------------------------------------------

def get_cluster_phrases_for_url(url: str) -> List[str]:
    """
    Return all phrases that already map to this URL.
    """
    if not url:
        return []
    data = load_global_dataset()
    entry = data.get("urls", {}).get(url)
    if not isinstance(entry, dict):
        return []

    phrases = entry.get("phrases") or []
    if not isinstance(phrases, list):
        return []

    # Ensure unique, stable order
    seen = set()
    out: List[str] = []
    for p in phrases:
        ps = str(p).strip()
        if ps and ps not in seen:
            seen.add(ps)
            out.append(ps)
    return out


def find_best_url_for_canonical_key(canonical_key: str) -> Optional[Dict[str, Any]]:
    """
    Given a canonical_key (semantic phrase like 'cervical mucus'),
    find the best URL entry from the Global External URL Dataset.

    Heuristic:
    - Prefer higher avg_confidence
    - Small bonus for more "seen" counts (capped)
    """
    ck = str(canonical_key or "").strip()
    if not ck:
        return None

    data = load_global_dataset()
    urls = data.get("urls", {})
    if not isinstance(urls, dict):
        return None

    best_entry: Optional[Dict[str, Any]] = None
    best_score = -1.0

    ck_lower = ck.lower()

    for entry in urls.values():
        if not isinstance(entry, dict):
            continue

        entry_ck = str(entry.get("canonical_key") or "").strip().lower()
        if entry_ck != ck_lower:
            continue

        stats = entry.get("stats") or {}
        if not isinstance(stats, dict):
            stats = {}

        avg_conf = float(stats.get("avg_confidence") or 0.0)
        seen = int(stats.get("seen") or 0)

        score = avg_conf + (min(seen, 10) * 0.01)

        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry


# ---------------------------------------------------------
# 4) Write helper – upsert from confidence result
# ---------------------------------------------------------

def upsert_from_confidence(result: ExternalConfidenceResult) -> None:
    """
    Given an ExternalConfidenceResult, update the Global External URL Dataset.
    - If result.should_store is False → do nothing.
    - Deduplicate by URL (URL is the primary key).
    - Append new phrase / origin / provider as needed.
    """
    if not result or not getattr(result, "should_store", False):
        return

    url = str(getattr(result, "url", "") or "").strip()
    if not url:
        return

    phrase = str(getattr(result, "phrase", "") or "").strip()
    canonical_key = str(getattr(result, "canonical_key", "") or "").strip()
    origin = str(getattr(result, "origin", "") or "").strip()
    provider_id = str(getattr(result, "provider_id", "") or "").strip()

    confidence = float(getattr(result, "confidence", 0.0) or 0.0)

    data = load_global_dataset()
    urls = data.setdefault("urls", {})
    if not isinstance(urls, dict):
        data["urls"] = {}
        urls = data["urls"]

    now = _now_iso()
    entry = urls.get(url)

    if not isinstance(entry, dict):
        # New URL
        urls[url] = {
            "url": url,
            "canonical_key": canonical_key,
            "phrases": [phrase] if phrase else [],
            "origins": [origin] if origin else [],
            "providers": [provider_id] if provider_id else [],
            "stats": {
                "seen": 1,
                "avg_confidence": confidence,
                "last_confidence": confidence,
            },
            "created_at": now,
            "updated_at": now,
        }
        save_global_dataset(data)
        return

    # Update existing
    phrases = entry.get("phrases") or []
    origins = entry.get("origins") or []
    providers = entry.get("providers") or []
    stats = entry.get("stats") or {}

    if not isinstance(phrases, list): phrases = []
    if not isinstance(origins, list): origins = []
    if not isinstance(providers, list): providers = []
    if not isinstance(stats, dict): stats = {}

    if phrase and phrase not in phrases:
        phrases.append(phrase)

    if origin and origin not in origins:
        origins.append(origin)

    if provider_id and provider_id not in providers:
        providers.append(provider_id)

    prev_seen = int(stats.get("seen") or 0)
    seen = prev_seen + 1

    last_conf = confidence
    prev_avg = float(stats.get("avg_confidence") or 0.0)
    avg_conf = ((prev_avg * prev_seen) + last_conf) / max(seen, 1)

    # Only set canonical_key if missing (don’t overwrite good keys accidentally)
    if canonical_key and not str(entry.get("canonical_key") or "").strip():
        entry["canonical_key"] = canonical_key

    entry["phrases"] = phrases
    entry["origins"] = origins
    entry["providers"] = providers
    entry["stats"] = {
        "seen": seen,
        "avg_confidence": avg_conf,
        "last_confidence": last_conf,
    }
    entry["updated_at"] = now

    urls[url] = entry
    save_global_dataset(data)
