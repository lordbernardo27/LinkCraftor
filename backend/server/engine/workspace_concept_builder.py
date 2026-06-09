from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from backend.server.engine.workspace_concept_store import (
    normalize_concept_text,
    save_workspace_concepts,
)


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    ws = str(workspace_id or "default").strip()
    return ws if ws else "default"


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _tokens(text: Any) -> List[str]:
    stop = {
        "a","an","and","are","as","at","be","by","for","from",
        "how","in","into","is","it","of","on","or","the","to",
        "what","when","where","why","with","your","you","this",
        "that","these","those"
    }
    return [
        t for t in re.findall(r"[a-z0-9]+", normalize_concept_text(text))
        if len(t) >= 3 and t not in stop
    ]


def _phrase_from_item(item: Any) -> str:
    if isinstance(item, dict):
        return normalize_concept_text(
            item.get("phrase")
            or item.get("phrase_text")
            or item.get("text")
            or item.get("label")
            or ""
        )
    return normalize_concept_text(item)


def _topic_cluster_tokens(text: str) -> set:
    toks = set(_tokens(text))

    # Generic cluster anchors:
    # These are not final niche rules; they are runtime topic-cluster hints.
    # Later this list should be generated from workspace frequency.
    cluster_groups = [
        {"ovulation", "fertile", "fertility", "cycle", "luteal", "follicular"},
        {"cervical", "mucus"},
        {"birth", "control", "contraception", "hormonal"},
        {"period", "menstrual", "cycle"},
        {"pregnancy", "pregnant", "conceive", "conception"},
    ]

    out = set(toks)
    for group in cluster_groups:
        if toks & group:
            out |= group

    return out


def _is_safe_alias_pair(concept: str, alias: str) -> bool:
    ct = set(_tokens(concept))
    at = set(_tokens(alias))

    if not ct or not at:
        return False

    overlap = ct & at
    cluster_overlap = _topic_cluster_tokens(concept) & _topic_cluster_tokens(alias)

    # Negative intent mismatch:
    # "avoid pregnancy" usually means prevention/contraception,
    # while "avoid during pregnancy" means safety restriction while pregnant.
    c = normalize_concept_text(concept)
    a = normalize_concept_text(alias)

    if "avoid during pregnancy" in c and "avoid pregnancy" in a:
        return False

    weak_bridge_tokens = {
        "avoid", "patterns", "pattern", "period", "more", "helpful",
        "reliable", "after", "before", "during", "pregnancy"
    }

    # Reject one-token generic matches.
    if len(overlap) == 1 and list(overlap)[0] in weak_bridge_tokens:
        return False

    # Require at least 2 shared tokens OR strong cluster agreement OR containment.
    if len(overlap) >= 2:
        return True

    # Same topic cluster, with at least one direct shared token or strong cluster signal.
    if len(cluster_overlap) >= 2 and (overlap or len(cluster_overlap) >= 4):
        return True

    c = normalize_concept_text(concept)
    a = normalize_concept_text(alias)

    if c in a or a in c:
        return True

    return False


def _add_alias(concepts: Dict[str, set], concept: str, alias: str) -> None:
    concept = normalize_concept_text(concept)
    alias = normalize_concept_text(alias)

    if not concept or not alias:
        return

    if not _is_safe_alias_pair(concept, alias):
        return

    concepts[concept].add(alias)
    concepts[concept].add(concept)


def build_workspace_concepts(workspace_id: str, max_concepts: int = 500) -> Dict[str, Any]:
    ws = _safe_ws(workspace_id)
    data_dir = _data_dir()

    site_pages_fp = data_dir / f"site_pages_{ws}.json"
    active_phrase_fp = data_dir / "phrase_pools" / "active" / f"active_phrase_pool_{ws}.json"
    live_pool_fp = data_dir / "target_pools" / "live_domain" / f"live_domain_target_pool_{ws}.json"

    site_pages = _read_json(site_pages_fp, {}).get("pages", {})
    active_phrase_obj = _read_json(active_phrase_fp, {})
    live_pool = _read_json(live_pool_fp, {}).get("items", [])

    concepts: Dict[str, set] = defaultdict(set)

    # 1. Build concepts from site page titles/H1/URL slugs.
    if isinstance(site_pages, dict):
        for url, rec in site_pages.items():
            if not isinstance(rec, dict):
                continue

            title = normalize_concept_text(rec.get("title") or rec.get("h1") or "")
            h1 = normalize_concept_text(rec.get("h1") or "")
            slug = normalize_concept_text(str(url or "").split("/")[-2] if str(url or "").endswith("/") else str(url or "").split("/")[-1])
            slug = re.sub(r"[-_]+", " ", slug)

            base = title or h1 or slug
            if not base:
                continue

            _add_alias(concepts, base, title)
            _add_alias(concepts, base, h1)
            _add_alias(concepts, base, slug)

    # 2. Add active article phrases as possible aliases to title concepts using overlap.
    raw_phrases = active_phrase_obj.get("phrases", {}) if isinstance(active_phrase_obj, dict) else {}
    if isinstance(raw_phrases, dict):
        active_phrases = [_phrase_from_item(v) for v in raw_phrases.values()]
    elif isinstance(raw_phrases, list):
        active_phrases = [_phrase_from_item(v) for v in raw_phrases]
    else:
        active_phrases = []

    concept_keys = list(concepts.keys())

    for phrase in active_phrases:
        pt = set(_tokens(phrase))
        if not pt:
            continue

        for concept in concept_keys:
            ct = set(_tokens(concept))
            if not ct:
                continue

            overlap = pt & ct
            ratio = len(overlap) / max(1, min(len(pt), len(ct)))

            if ratio >= 0.60:
                _add_alias(concepts, concept, phrase)

    # 3. Add live target-pool matched phrases/aliases.
    if isinstance(live_pool, list):
        for item in live_pool:
            if not isinstance(item, dict):
                continue

            title = normalize_concept_text(item.get("title") or item.get("h1") or item.get("label") or "")
            if not title:
                continue

            for alias in (item.get("matched_phrases") or []) + (item.get("aliases") or []):
                _add_alias(concepts, title, alias)

    # 4. Convert to JSON-safe format.
    concept_payload = {}
    for concept, aliases in list(concepts.items())[:max_concepts]:
        clean_aliases = sorted(a for a in aliases if a)
        if len(clean_aliases) < 2:
            continue
        concept_payload[concept] = {
            "concept": concept,
            "aliases": clean_aliases[:50],
            "alias_count": len(clean_aliases),
            "source": "workspace_auto_concept_builder_v1",
        }

    out = {
        "workspace_id": ws,
        "type": "workspace_concepts",
        "concept_count": len(concept_payload),
        "concepts": concept_payload,
        "metadata": {
            "source": "site_pages + active_phrase_pool + live_domain_target_pool",
            "version": "workspace_concepts_v1",
        },
    }

    return save_workspace_concepts(ws, out)
