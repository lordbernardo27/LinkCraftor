from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AuthorityDomainItem:
    phrase: str
    title: str
    vertical: str
    confidence: float
    source: str  # "global_external_auto" | "global_external_manual"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "phrase": self.phrase,
            "title": self.title,
            "vertical": self.vertical,
            "confidence": self.confidence,
            "source": self.source,
        }


# ----------------------------
# small utils
# ----------------------------
def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        if v != v:  # NaN
            return default
        return v
    except Exception:
        return default


def _norm_text(s: Any) -> str:
    return " ".join(str(s or "").strip().split())


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _pick_first(meta: Dict[str, Any], keys: List[str]) -> Optional[Any]:
    for k in keys:
        if k in meta and meta.get(k) is not None:
            return meta.get(k)
    return None


def _unwrap_known_containers(obj: Any) -> Any:
    """
    Some files are wrapped like:
      { "items": [...] } or { "data": [...] } or { "phrases": {...} }
    We unwrap one level if we recognize a common container key.
    """
    if isinstance(obj, dict):
        for k in ("items", "data", "rows", "records", "entries", "phrases", "map", "dict"):
            v = obj.get(k)
            if isinstance(v, (list, dict)) and len(v) > 0:
                return v
    return obj


def _iter_entries(obj: Any) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Accepts flexible formats:

    A) Dict keyed by phrase:
       { "pregnancy due date": {"title": "...", "vertical": "...", "confidence": 0.8}, ... }

    B) List of objects:
       [ {"phrase":"...", "title":"...", "vertical":"...", "confidence":0.8}, ... ]

    Also supports container wrappers like {items:[...]} or {phrases:{...}}.
    """
    obj = _unwrap_known_containers(obj)

    out: List[Tuple[str, Dict[str, Any]]] = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                out.append((str(k), v))
            else:
                # value might itself be numeric/confidence etc.
                out.append((str(k), {"confidence": v}))
        return out

    if isinstance(obj, list):
        for it in obj:
            if not isinstance(it, dict):
                continue
            phrase = (
                it.get("phrase")
                or it.get("key")
                or it.get("anchor")
                or it.get("term")
                or it.get("text")
                or ""
            )
            out.append((str(phrase), it))
        return out

    return out


def load_authority_domain_pool(project_root: Path) -> List[AuthorityDomainItem]:
    """
    Loads + merges:
      backend/data/global_external_auto.json
      backend/data/global_external_manual.json

    Uses only:
      phrase, title, vertical, confidence
    Ignores URL entirely.
    """
    data_dir = project_root / "backend" / "data"

    sources = [
        ("global_external_auto", data_dir / "global_external_auto.json"),
        ("global_external_manual", data_dir / "global_external_manual.json"),
    ]

    merged: Dict[str, AuthorityDomainItem] = {}

    TITLE_KEYS = ["title", "topic", "name", "label", "paper_title", "page_title", "source_title"]
    VERTICAL_KEYS = ["vertical", "niche", "category", "domain", "industry", "field"]
    CONF_KEYS = ["confidence", "confidence_ratio", "conf", "score", "weight", "prob", "p", "rank_score"]

    for source_name, fp in sources:
        raw = _read_json(fp)
        if raw is None:
            continue

        for phrase_raw, meta in _iter_entries(raw):
            phrase_norm = _norm_text(phrase_raw).lower()
            if not phrase_norm:
                continue

            meta = meta if isinstance(meta, dict) else {}

            # title / vertical / confidence (with flexible keys)
            title_raw = _pick_first(meta, TITLE_KEYS)
            vertical_raw = _pick_first(meta, VERTICAL_KEYS)
            conf_raw = _pick_first(meta, CONF_KEYS)

            title = _norm_text(title_raw)
            vertical = _norm_text(vertical_raw) or "general"

            # confidence could be stored 0..100 or 0..1; normalize safely
            conf = _safe_float(conf_raw, 0.0)
            if conf > 1.0 and conf <= 100.0:
                conf = conf / 100.0
            conf = _clamp01(conf)

            if not title:
                # last-resort fallback
                title = _norm_text(meta.get("title_text")) or phrase_raw.strip() or phrase_norm

            item = AuthorityDomainItem(
                phrase=phrase_norm,
                title=title,
                vertical=vertical,
                confidence=conf,
                source=source_name,
            )

            # De-dupe by phrase: highest confidence wins (no "manual always wins")
            prev = merged.get(phrase_norm)
            if prev is None or item.confidence > prev.confidence:
                merged[phrase_norm] = item

    out = sorted(merged.values(), key=lambda x: (-x.confidence, x.phrase))
    return out