from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json
import re


TARGET_POOL_DIR = Path("backend/server/data/target_pools")


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _norm_text(text: Any) -> str:
    text = str(text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s\-\/:\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_phrase(text: Any) -> str:
    text = _norm_text(text)
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_slug(url: Any) -> str:
    url = str(url or "").strip()
    if not url:
        return ""

    clean = url.split("?")[0].split("#")[0].rstrip("/")
    slug = clean.split("/")[-1]
    return _normalize_phrase(slug)


def _token_set(text: Any) -> set:
    return {
        t for t in _normalize_phrase(text).split()
        if t
    }


def _safe_read_json(path: Path) -> Any:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _is_probably_valid_url(url: Any) -> bool:
    url = str(url or "").strip()
    if not url:
        return False

    if url.startswith("http://") or url.startswith("https://"):
        return True

    if url.startswith("/"):
        return True

    return False


def _looks_like_internal_id(text: Any) -> bool:
    text = str(text or "").strip().lower()
    if not text:
        return True

    compact = text.replace("-", "").replace("_", "")

    if re.fullmatch(r"[a-f0-9]{12,}", compact):
        return True

    if re.fullmatch(r"[0-9]{8,}", compact):
        return True

    if re.fullmatch(r"[a-z0-9\-_]{20,}", text) and len(text.split()) <= 1:
        return True

    return False


def _is_valid_semantic_slug(slug: Any) -> bool:
    slug = _normalize_phrase(slug)

    if not slug:
        return False

    if _looks_like_internal_id(slug):
        return False

    tokens = slug.split()

    if len(tokens) < 2:
        return False

    alpha_count = sum(1 for c in slug if c.isalpha())
    if alpha_count < 4:
        return False

    return True

def _empty_candidate_groups() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "live_domain": [],
        "imported": [],
        "draft": [],
        "document_registry": [],
        "active": [],
        "unknown": [],
    }


def _detect_source_group(
    source_file: Path,
) -> str:

    p = str(source_file).lower()

    if "live_domain" in p:
        return "live_domain"

    if "imported" in p:
        return "imported"

    if "draft" in p:
        return "draft"

    if "document" in p:
        return "document_registry"

    if "active" in p:
        return "active"

    return "unknown"


def _safe_source_dedupe_key(
    rec: Dict[str, Any],
) -> str:

    return (
        f"{rec['source_type']}::"
        f"{rec['url'].strip().lower()}"
    )


def load_source_separated_candidates_v2(
    workspace_id: str,
) -> Dict[str, Any]:

    candidate_groups = (
        _empty_candidate_groups()
    )

    scanned_files = []

    seen = set()

    for path in _workspace_pool_files(
        workspace_id
    ):

        scanned_files.append(str(path))

        data = _safe_read_json(path)

        if not data:
            continue

        source_group = (
            _detect_source_group(path)
        )

        items: List[Any] = []

        if isinstance(data, dict):

            if isinstance(
                data.get("targets"),
                list,
            ):
                items.extend(data["targets"])

            if isinstance(
                data.get("items"),
                list,
            ):
                items.extend(data["items"])

            if isinstance(
                data.get("urls"),
                list,
            ):
                items.extend(data["urls"])

        elif isinstance(data, list):
            items.extend(data)

        for item in items:

            if not isinstance(item, dict):
                continue

            rec = _extract_candidate_record(
                item,
                path,
            )

            if not rec:
                continue

            dedupe_key = (
                _safe_source_dedupe_key(
                    rec
                )
            )

            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)

            candidate_groups[
                source_group
            ].append(rec)

    selection_view = []

    for group_name, rows in (
        candidate_groups.items()
    ):

        for rec in rows:

            selection_view.append({

                "source_group":
                    group_name,

                "source_type":
                    rec["source_type"],

                "url":
                    rec["url"],

                "title":
                    rec["title"],

                "slug":
                    rec["slug"],

                "normalized_title":
                    rec["normalized_title"],
            })

    return {

        "workspace_id":
            workspace_id,

        "generated_at":
            _now_iso(),

        "candidate_groups":
            candidate_groups,

        "selection_view":
            selection_view,

        "selection_candidate_count":
            len(selection_view),

        "scanned_files":
            scanned_files,

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.7.5.4_source_separated_candidates",
    }


def _workspace_pool_files(
    workspace_id: str,
) -> List[Path]:

    matches = []

    for path in TARGET_POOL_DIR.rglob("*.json"):

        p = str(path).lower()

        if workspace_id.lower() not in p:
            continue

        matches.append(path)

    return sorted(matches)


def _extract_candidate_record(
    item: Dict[str, Any],
    source_file: Path,
) -> Optional[Dict[str, Any]]:

    url = str(
        item.get("url")
        or item.get("target_url")
        or item.get("source_url")
        or item.get("href")
        or ""
    ).strip()

    if not _is_probably_valid_url(url):
        return None

    title = str(
        item.get("title")
        or item.get("target_title")
        or item.get("label")
        or item.get("slug_label")
        or item.get("url_label")
        or item.get("name")
        or ""
    ).strip()

    slug = _extract_slug(url)

    if not _is_valid_semantic_slug(slug):
        return None

    normalized_title = _normalize_phrase(title or slug)

    if not normalized_title:
        normalized_title = slug

    if _looks_like_internal_id(normalized_title):
        return None

    return {
        "url": url,
        "title": title,
        "normalized_title": normalized_title,
        "slug": slug,
        "source_file": str(source_file),
        "source_type": source_file.parent.name,
    }


from backend.server.engine.intelligence_target_resolver import (
    resolve_intelligent_targets,
)


CANONICAL_SOURCE_PRIORITY = {
    "live_domain": 100,
    "imported": 80,
    "document_registry": 60,
    "draft": 40,
    "active": 20,
    "unknown": 5,
}


def _canonical_source_priority(
    source_group: str,
) -> int:

    return CANONICAL_SOURCE_PRIORITY.get(
        str(source_group or "").strip().lower(),
        0,
    )


def build_canonical_orchestration_bridge_v2(
    workspace_id: str,
    phrase: str,
    limit: int = 25,
) -> Dict[str, Any]:

    phrase = _normalize_phrase(phrase)

    if not phrase:
        return {
            "workspace_id": workspace_id,
            "phrase": "",
            "canonical_candidates": [],
            "candidate_count": 0,
            "generated_at": _now_iso(),
        }

    resolved = resolve_intelligent_targets(
        workspace_id=workspace_id,
        anchor_phrase=phrase,
        limit=max(limit, 10),
    )

    canonical_candidates = []

    for row in resolved:

        source_type = str(
            row.get("source_type") or "unknown"
        ).strip().lower()

        priority_score = (
            _canonical_source_priority(
                source_type
            )
        )

        runtime_score = float(
            row.get(
                "runtime_normalized_score",
                0,
            ) or 0
        )

        resolver_confidence = float(
            row.get(
                "resolver_confidence",
                0,
            ) or 0
        )

        base_canonical_score = (
            (
                runtime_score * 0.45
            )
            +
            (
                resolver_confidence * 0.25
            )
            +
            (
                priority_score / 100 * 0.30
            )
        )

        governance_multiplier = (
            _canonical_url_governance_multiplier(
                row
            )
        )

        canonical_score = round(
            base_canonical_score
            * governance_multiplier,
            6,
        )

        governance_reason = (
            _canonical_url_penalty_reason(
                row
            )
        )

        canonical_candidates.append({

            "phrase":
                phrase,

            "url":
                row.get("url"),

            "title":
                row.get("title"),

            "source_type":
                source_type,

            "canonical_score":
                canonical_score,

            "base_canonical_score":
                round(base_canonical_score, 6),

            "governance_multiplier":
                governance_multiplier,

            "governance_reason":
                governance_reason,

            "runtime_normalized_score":
                runtime_score,

            "resolver_confidence":
                resolver_confidence,

            "priority_score":
                priority_score,

            "semantic_route_score":
                row.get(
                    "semantic_route_score"
                ),

            "authority_score":
                row.get(
                    "authority_score"
                ),

            "topic_graph_score":
                row.get(
                    "topic_graph_score"
                ),

            "rb2_weight_score":
                row.get(
                    "rb2_weight_score"
                ),

            "path_score":
                row.get(
                    "path_score"
                ),

            "slug":
                _extract_slug(
                    row.get("url")
                ),

            "normalized_title":
                _normalize_phrase(
                    row.get("title")
                ),

            "resolver_reason":
                row.get(
                    "resolver_reason"
                ),
        })

    canonical_candidates.sort(
        key=lambda x: (
            x["canonical_score"],
            x["priority_score"],
            x["runtime_normalized_score"],
        ),
        reverse=True,
    )

    return {

        "workspace_id":
            workspace_id,

        "phrase":
            phrase,

        "candidate_count":
            len(canonical_candidates),

        "canonical_candidates":
            canonical_candidates,

        "generated_at":
            _now_iso(),

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.7.5.4_canonical_orchestration_bridge_v2",
    }


INTERNAL_URL_PREFIXES = (
    "/documents/",
    "/uploads/",
    "/tmp/",
    "/internal/",
    "/preview/",
)


def _is_internal_noncanonical_url(
    url: Any,
) -> bool:

    url = str(url or "").strip().lower()

    if not url:
        return True

    for prefix in INTERNAL_URL_PREFIXES:
        if url.startswith(prefix):
            return True

    slug = _extract_slug(url)

    if _looks_like_internal_id(slug):
        return True

    return False


def _canonical_url_governance_multiplier(
    row: Dict[str, Any],
) -> float:

    url = row.get("url", "")
    source_type = str(
        row.get("source_type") or ""
    ).strip().lower()

    # Published/live URLs should dominate canonical SEO selection.
    if source_type == "live_domain":
        return 1.35

    # Imported URLs are usually external/published references.
    if source_type == "imported":
        return 1.15

    # Drafts are useful but should not dominate published URLs.
    if source_type == "draft":
        return 0.82

    # Internal document registry should almost never be canonical SEO.
    if source_type == "document_registry":
        return 0.28

    if _is_internal_noncanonical_url(url):
        return 0.20

    return 1.0


def _canonical_url_penalty_reason(
    row: Dict[str, Any],
) -> str:

    url = row.get("url", "")
    source_type = str(
        row.get("source_type") or ""
    ).strip().lower()

    if source_type == "live_domain":
        return "published_live_domain_priority"

    if source_type == "imported":
        return "imported_published_reference_priority"

    if source_type == "draft":
        return "draft_candidate_lower_than_published"

    if source_type == "document_registry":
        return "internal_document_registry_not_seo_canonical"

    if _is_internal_noncanonical_url(url):
        return "internal_noncanonical_url_penalty"

    return "standard_canonical_candidate"


def resolve_canonical_winner_v2(
    workspace_id: str,
    phrase: str,
    limit: int = 25,
) -> Dict[str, Any]:

    orchestration = (
        build_canonical_orchestration_bridge_v2(
            workspace_id=workspace_id,
            phrase=phrase,
            limit=limit,
        )
    )

    candidates = list(
        orchestration.get(
            "canonical_candidates",
            []
        )
    )

    if not candidates:

        return {

            "workspace_id":
                workspace_id,

            "phrase":
                phrase,

            "canonical_winner":
                None,

            "alternate_candidates":
                [],

            "candidate_count":
                0,

            "resolution_reason":
                "no_candidates_found",

            "generated_at":
                _now_iso(),

            "runtime_effect":
                "read_only_no_runtime_injection",

            "layer":
                "1.7.5.4_canonical_winner_resolver_v2",
        }

    winner = candidates[0]

    alternates = []

    for alt in candidates[1:]:

        rejection_reasons = []

        if (
            alt["canonical_score"]
            < winner["canonical_score"]
        ):
            rejection_reasons.append(
                "lower_canonical_score"
            )

        if (
            alt["priority_score"]
            < winner["priority_score"]
        ):
            rejection_reasons.append(
                "lower_source_priority"
            )

        if (
            alt["governance_multiplier"]
            < winner["governance_multiplier"]
        ):
            rejection_reasons.append(
                "canonical_governance_penalty"
            )

        if (
            alt["source_type"]
            == "document_registry"
        ):
            rejection_reasons.append(
                "internal_registry_not_public_canonical"
            )

        alternates.append({

            "url":
                alt["url"],

            "title":
                alt["title"],

            "source_type":
                alt["source_type"],

            "canonical_score":
                alt["canonical_score"],

            "governance_reason":
                alt.get(
                    "governance_reason"
                ),

            "rejection_reasons":
                rejection_reasons,
        })

    resolution_reason = (
        winner.get(
            "governance_reason"
        )
        or
        "highest_canonical_score"
    )

    canonical_winner = {

        "phrase":
            phrase,

        "url":
            winner["url"],

        "title":
            winner["title"],

        "source_type":
            winner["source_type"],

        "canonical_score":
            winner["canonical_score"],

        "base_canonical_score":
            winner[
                "base_canonical_score"
            ],

        "governance_multiplier":
            winner[
                "governance_multiplier"
            ],

        "governance_reason":
            winner[
                "governance_reason"
            ],

        "resolver_reason":
            winner.get(
                "resolver_reason"
            ),

        "slug":
            winner.get(
                "slug"
            ),

        "normalized_title":
            winner.get(
                "normalized_title"
            ),
    }

    return {

        "workspace_id":
            workspace_id,

        "phrase":
            phrase,

        "canonical_winner":
            canonical_winner,

        "alternate_candidates":
            alternates,

        "candidate_count":
            len(candidates),

        "resolution_reason":
            resolution_reason,

        "generated_at":
            _now_iso(),

        "runtime_effect":
            "read_only_no_runtime_injection",

        "layer":
            "1.7.5.4_canonical_winner_resolver_v2",
    }


def explain_sitemap_confidence_v2(
    workspace_id: str,
    phrase: str,
    limit: int = 25,
) -> Dict[str, Any]:

    resolved = resolve_canonical_winner_v2(
        workspace_id=workspace_id,
        phrase=phrase,
        limit=limit,
    )

    winner = resolved.get("canonical_winner")

    if not winner:
        return {
            "workspace_id": workspace_id,
            "phrase": phrase,
            "sitemap_confidence": 0.0,
            "confidence_level": "none",
            "confidence_reason": "no_canonical_winner_found",
            "winner": None,
            "signals": {},
            "generated_at": _now_iso(),
            "runtime_effect": "read_only_no_runtime_injection",
            "layer": "1.7.5.5_sitemap_confidence_explanation_v2",
        }

    canonical_score = float(
        winner.get("canonical_score") or 0
    )

    governance_multiplier = float(
        winner.get("governance_multiplier") or 0
    )

    source_type = str(
        winner.get("source_type") or "unknown"
    ).lower()

    slug = str(
        winner.get("slug") or ""
    )

    normalized_title = str(
        winner.get("normalized_title") or ""
    )

    slug_tokens = set(slug.split())
    title_tokens = set(normalized_title.split())

    title_slug_overlap = 0.0

    if slug_tokens and title_tokens:
        title_slug_overlap = round(
            len(slug_tokens & title_tokens)
            / max(len(slug_tokens | title_tokens), 1),
            4,
        )

    source_bonus = {
        "live_domain": 0.25,
        "imported": 0.18,
        "draft": 0.08,
        "document_registry": -0.25,
    }.get(source_type, 0.0)

    confidence = (
        (canonical_score * 0.55)
        + (title_slug_overlap * 0.25)
        + source_bonus
        + min(governance_multiplier / 10, 0.15)
    )

    confidence = round(
        max(0.0, min(confidence, 1.0)),
        4,
    )

    if confidence >= 0.75:
        level = "high"
    elif confidence >= 0.45:
        level = "medium"
    elif confidence > 0:
        level = "low"
    else:
        level = "none"

    return {
        "workspace_id": workspace_id,
        "phrase": phrase,
        "sitemap_confidence": confidence,
        "confidence_level": level,
        "confidence_reason": "sitemap_confidence_explained_from_existing_signals",
        "winner": winner,
        "signals": {
            "canonical_score": canonical_score,
            "governance_multiplier": governance_multiplier,
            "source_type": source_type,
            "source_bonus": source_bonus,
            "title_slug_overlap": title_slug_overlap,
            "slug": slug,
            "normalized_title": normalized_title,
        },
        "generated_at": _now_iso(),
        "runtime_effect": "read_only_no_runtime_injection",
        "layer": "1.7.5.5_sitemap_confidence_explanation_v2",
    }

