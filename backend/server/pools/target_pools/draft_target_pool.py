# backend/server/pools/target_pools/draft_target_pool.py

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    server_dir = here.parents[2]  # .../backend/server
    return server_dir / "data"


def _pool_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / "draft" / f"draft_target_pool_{ws}.json"


# Draft import can be CSV or TXT. We will read *topics* from them.
def _draft_csv_path(ws: str) -> Path:
    return _data_dir() / f"draft_targets_{ws}.csv"


def _draft_txt_path(ws: str) -> Path:
    return _data_dir() / f"draft_targets_{ws}.txt"


def _site_sources_path(ws: str) -> Path:
    return _data_dir() / f"site_sources_{ws}.json"


def _active_target_set_path(ws: str) -> Path:
    return _data_dir() / "target_pools" / f"active_target_set_{ws}.json"


def _fix_mojibake_text(s: str) -> str:
    s = str(s or "")
    if not s:
        return ""

    # ASCII-safe mojibake fixer.
    # Avoids storing broken characters directly in source code.
    replacements = {
        "\u00e2\u20ac\u2122": "'",
        "\u00e2\u20ac\u02dc": "'",
        "\u00e2\u20ac\u0153": '"',
        "\u00e2\u20ac\u009d": '"',
        "\u00e2\u20ac\u201c": "-",
        "\u00e2\u20ac\u201d": "-",
        "\u00e2\u20ac\u00a6": "...",
        "\u00e2\u0080\u0099": "'",
        "\u00e2\u0080\u0098": "'",
        "\u00e2\u0080\u009c": '"',
        "\u00e2\u0080\u009d": '"',
        "\u00e2\u0080\u0093": "-",
        "\u00e2\u0080\u0094": "-",
        "\u00e2\u0080\u00a6": "...",
        "\u00c2\u00a0": " ",
        "\u00c2": "",
        "\ufffd": "",
    }

    for bad, good in replacements.items():
        s = s.replace(bad, good)

    return re.sub(r"\s+", " ", s).strip()


def _clean(s: str) -> str:
    s = str(s or "").strip().strip("\ufeff").strip()
    s = _fix_mojibake_text(s)
    return s


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _domain_from_sources_or_ws(ws: str) -> str:
    """
    Prefer site_sources_<ws>.json -> sources[0].domain
    Fallback: ws_betterhealthcheck_com -> betterhealthcheck.com
    """
    fp = _site_sources_path(ws)
    if fp.exists():
        try:
            obj = json.loads(fp.read_text(encoding="utf-8"))
            arr = obj.get("sources") or []
            if isinstance(arr, list) and arr:
                dom = str((arr[0] or {}).get("domain") or "").strip().lower()
                dom = dom[4:] if dom.startswith("www.") else dom
                if dom:
                    return dom
        except Exception:
            pass

    s = ws
    if s.startswith("ws_"):
        s = s[3:]
    return s.replace("_", ".").strip(".").lower()


_slug_re = re.compile(r"[^a-z0-9]+")


def _slugify(topic: str) -> str:
    t = _clean(topic).lower()
    t = _slug_re.sub("-", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    return t or "draft"


def _apply_strong_intent_balance(scores: Dict[str, int], text: str) -> Dict[str, int]:
    # Strong intent should beat weaker secondary wording.
    if any(x in text for x in [" vs ", " versus ", "compare", "comparison"]):
        scores["comparison"] += 3

    if text.startswith("how to ") or " how to " in text:
        scores["how_to"] += 3

    if any(x in text for x in ["guide", "checklist", "step-by-step", "steps"]):
        scores["guide"] += 2

    if any(x in text for x in ["explained", "understanding", "what is"]):
        scores["explainer"] += 2

    # Avoid over-classifying every "plan" as guide unless it has practical intent.
    if "plan" in text and any(x in text for x in ["practical", "step", "checklist", "routine"]):
        scores["guide"] += 2

    return scores


def _classify_page_type_hint(title: str) -> str:
    text = _clean(title).lower()

    scores = {
        "how_to": 0,
        "guide": 0,
        "explainer": 0,
        "comparison": 0,
        "listicle": 0,
        "general_article": 1,
    }

    if text.startswith("how to ") or " how to " in text:
        scores["how_to"] += 4
    if any(x in text for x in ["guide", "checklist", "plan", "steps", "strategy"]):
        scores["guide"] += 3
    if any(x in text for x in ["what is", "understanding", "explained", "why ", "causes"]):
        scores["explainer"] += 3
    if any(x in text for x in [" vs ", " versus ", "compare", "comparison"]):
        scores["comparison"] += 4
    if re.search(r"\b\d+\b", text) or any(x in text for x in ["ideas", "tips", "ways", "best"]):
        scores["listicle"] += 2

    scores = _apply_strong_intent_balance(scores, text)
    return max(scores.items(), key=lambda kv: kv[1])[0]


def _classify_priority_bucket(title: str, page_type_hint: str) -> str:
    text = _clean(title).lower()

    score = 0

    if page_type_hint in {"how_to", "guide", "comparison"}:
        score += 3
    elif page_type_hint in {"explainer", "listicle"}:
        score += 2
    else:
        score += 1

    if any(x in text for x in ["safe", "pregnancy", "fertility", "newborn", "breastfeeding", "miscarriage"]):
        score += 2

    if any(x in text for x in ["needs", "should", "avoid", "when to worry", "practical", "support"]):
        score += 1

    if len(text.split()) >= 7:
        score += 1

    if score >= 6:
        return "critical"
    if score >= 4:
        return "strong"
    if score >= 2:
        return "supporting"
    return "long_tail"


def _build_draft_priority_signals(title: str, page_type_hint: str) -> Dict[str, Any]:
    text = _clean(title).lower()
    wc = len(text.split())

    return {
        "has_practical_intent": any(
            x in text for x in [
                "practical",
                "guide",
                "steps",
                "how to",
                "plan",
                "routine",
                "strategy",
            ]
        ),

        "has_risk_intent": any(
            x in text for x in [
                "risk",
                "danger",
                "miscarriage",
                "warning",
                "safe",
                "when to worry",
            ]
        ),

        "has_comparison_intent": any(
            x in text for x in [
                " vs ",
                " versus ",
                "compare",
                "comparison",
            ]
        ),

        "has_explainer_intent": page_type_hint == "explainer",

        "word_count_signal":
            "short" if wc <= 4 else
            "medium" if wc <= 8 else
            "long"
    }


def _build_draft_priority_signals(title: str, page_type_hint: str) -> Dict[str, Any]:
    text = _clean(title).lower()
    wc = len(text.split())

    return {
        "has_practical_intent": any(
            x in text for x in [
                "practical",
                "guide",
                "steps",
                "how to",
                "plan",
                "routine",
                "strategy",
            ]
        ),

        "has_risk_intent": any(
            x in text for x in [
                "risk",
                "danger",
                "miscarriage",
                "warning",
                "safe",
                "when to worry",
            ]
        ),

        "has_comparison_intent": any(
            x in text for x in [
                " vs ",
                " versus ",
                "compare",
                "comparison",
            ]
        ),

        "has_explainer_intent": page_type_hint == "explainer",

        "word_count_signal":
            "short" if wc <= 4 else
            "medium" if wc <= 8 else
            "long"
    }


def _read_topics_from_csv(fp: Path) -> List[str]:
    """
    CSV supported formats:
      - Title
      - Title,URL  (URL ignored)
    Header row optional: Title,URL or Topic,URL
    """
    out: List[str] = []
    with fp.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue

            c0 = _clean(row[0]) if len(row) >= 1 else ""
            c1 = _clean(row[1]) if len(row) >= 2 else ""

            if i == 0 and c0.lower() in {"title", "topic"}:
                continue
            if i == 0 and c0.lower() in {"title", "topic"} and c1.lower() in {"url", "link"}:
                continue

            if c0:
                out.append(c0)
    return out


def _read_topics_from_txt(fp: Path) -> List[str]:
    """
    TXT supported formats:
      - One topic per line
      - Or "Title,URL" per line (URL ignored)
    """
    out: List[str] = []
    for line in fp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            parsed = next(csv.reader([line]))
            c0 = _clean(parsed[0]) if parsed else ""
        except Exception:
            c0 = _clean(line)

        if c0.lower() in {"title", "topic"}:
            continue
        if c0:
            out.append(c0)

    return out


def build_draft_target_pool(
    workspace_id: str,
    *,
    drafts_path: str = "/drafts",
) -> Dict[str, Any]:
    """
    Draft Target Pool (Option A):
      - reads draft topics (topics only) from CSV/TXT
      - generates placeholder URL for each topic during build:
          https://{domain}{drafts_path}/{slug}
      - writes items: {draft_topic_id, topic, url}
      - if active_target_set_<ws>.json exists, only keeps active draft ids
    """
    ws = _clean(workspace_id)
    if not ws:
        raise ValueError("workspace_id is required")

    csv_fp = _draft_csv_path(ws)
    txt_fp = _draft_txt_path(ws)

    source_used = ""
    topics: List[str] = []

    if csv_fp.exists():
        topics = _read_topics_from_csv(csv_fp)
        source_used = str(csv_fp)
    elif txt_fp.exists():
        topics = _read_topics_from_txt(txt_fp)
        source_used = str(txt_fp)
    else:
        raise FileNotFoundError(
            f"No draft input found. Expected one of: {csv_fp.name}, {txt_fp.name}"
        )

    seen: set[str] = set()
    uniq: List[str] = []
    rejection_audit: Dict[str, int] = {
        "empty_title": 0,
        "duplicate_title": 0,
        "too_short_title": 0,
    }
    rejected_examples: List[Dict[str, str]] = []

    def _reject(reason: str, value: str) -> None:
        rejection_audit[reason] = rejection_audit.get(reason, 0) + 1
        if len(rejected_examples) < 10:
            rejected_examples.append({
                "reason": reason,
                "value": str(value or ""),
            })

    for t in topics:
        cleaned_topic = _clean(t)
        k = cleaned_topic.lower()

        if not k:
            _reject("empty_title", t)
            continue

        if len(k) < 3:
            _reject("too_short_title", t)
            continue

        if k in seen:
            _reject("duplicate_title", t)
            continue

        seen.add(k)
        uniq.append(cleaned_topic)

    domain = _domain_from_sources_or_ws(ws)
    base = f"https://{domain}".rstrip("/")
    dp = "/" + str(drafts_path or "/drafts").lstrip("/")
    dp = dp.rstrip("/")

    active_fp = _active_target_set_path(ws)
    active_obj = _safe_read_json(active_fp) if active_fp.exists() else None
    active_draft_ids: List[str] = []

    if isinstance(active_obj, dict):
        raw_ids = active_obj.get("active_draft_ids") or []
        if isinstance(raw_ids, list):
            active_draft_ids = [str(x).strip() for x in raw_ids if str(x).strip()]

    active_draft_id_set = set(active_draft_ids)

    items: List[Dict[str, Any]] = []
    topics_seen = 0
    items_kept_after_active_filter = 0
    page_type_counts: Dict[str, int] = {}
    priority_bucket_counts: Dict[str, int] = {}
    future_content_count = 0
    planned_content_count = 0

    for i, topic in enumerate(uniq, start=1):
        topics_seen += 1
        draft_topic_id = f"draft_{i:04d}"

        # Safety: only filter drafts when active_draft_ids is explicitly populated.
        # If the active file exists but active_draft_ids is empty, do NOT wipe the draft pool.
        if active_draft_id_set and draft_topic_id not in active_draft_id_set:
            continue

        clean_topic = _clean(topic)
        slug = _slugify(clean_topic)
        page_type_hint = _classify_page_type_hint(clean_topic)
        priority_bucket = _classify_priority_bucket(clean_topic, page_type_hint)
        draft_priority_signals = _build_draft_priority_signals(
            clean_topic,
            page_type_hint,
        )
        path = f"{dp}/{slug}"
        url = f"{base}{path}"
        page_type_counts[page_type_hint] = page_type_counts.get(page_type_hint, 0) + 1
        priority_bucket_counts[priority_bucket] = priority_bucket_counts.get(priority_bucket, 0) + 1
        future_content_count += 1
        planned_content_count += 1

        items.append(
            {
                "draft_topic_id": draft_topic_id,
                "draft_id": draft_topic_id,
                "draft_status": "planned",
                "publish_readiness": "planned",
                "document_id": None,
                "topic": clean_topic,
                "label": clean_topic,
                "title": clean_topic,
                "h1": clean_topic,
                "title_source": "draft_topic",
                "title_fallback_used": False,
                "placeholder_generated": True,
                "page_type_hint": page_type_hint,
                "priority_bucket": priority_bucket,
                "draft_priority_signals": draft_priority_signals,
                "future_content": True,
                "planned_content": True,
                "source_type": "draft",
                "source_origin": "draft_pool",
                "path": path,
                "url": url,
                "planned_url": url,
                "placeholder_url": url,
                "published_url": None,
                "metadata": {
                    "draft_topic_id": draft_topic_id,
                    "domain": domain,
                    "drafts_path": dp,
                    "slug": slug,
                    "generated_by": "draft_target_pool_builder",
                },
            }
        )
        items_kept_after_active_filter += 1

    out: Dict[str, Any] = {
        "workspace_id": ws,
        "type": "draft",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source_used,
        "drafts_path": dp,
        "domain": domain,
        "active_target_set_used": active_fp.exists(),
        "active_draft_ids_count": len(active_draft_ids),
        "counts": {
            "topics_read": len(topics),
            "topics_deduped": len(uniq),
            "topics_seen": topics_seen,
            "items_written": len(items),
            "items_kept_after_active_filter": items_kept_after_active_filter,
            "rejected_total": sum(rejection_audit.values()),
            "page_type_counts": page_type_counts,
            "priority_bucket_counts": priority_bucket_counts,
            "future_content_count": future_content_count,
            "planned_content_count": planned_content_count,
        },
        "rejection_audit": rejection_audit,
        "rejected_examples": rejected_examples,
        "items": items,
    }

    out_fp = _pool_path(ws)
    out_fp.parent.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out