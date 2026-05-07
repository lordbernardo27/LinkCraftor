from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from backend.server.stores.candidate_window_guard import candidate_window_guard
from backend.server.stores.phrase_strength_scorer import (
    canonical_phrase,
    score_phrase_strength,
)
from backend.server.stores.phrase_vertical_policy import (
    apply_vertical_policy_score,
    detect_vertical,
)
from backend.server.stores.smart_phrase_extractor import (
    extract_paragraphs,
    extract_smart_phrases,
)


CONNECTORS = {
    "about", "after", "before", "because", "by", "during", "for", "from",
    "in", "into", "of", "on", "than", "that", "to", "with", "without",
    "while", "whether", "rather",
}

WEAK_PRONOUN_STARTS = {
    "you", "your", "we", "our", "they", "their", "this", "that",
    "these", "those", "it", "its",
}

AUXILIARY_VERBS = {
    "am", "are", "be", "been", "being", "can", "could", "did", "do",
    "does", "had", "has", "have", "is", "may", "might", "must",
    "should", "was", "were", "will", "would",
}

ACTION_VERBS = {
    "ask", "asks", "become", "becomes", "calculate", "calculating",
    "confirm", "end", "ends", "fall", "falls", "feel", "feels",
    "find", "give", "gives", "go", "goes", "help", "helps",
    "know", "knows", "make", "makes", "mean", "means", "need",
    "needs", "show", "shows", "take", "takes", "turn", "turns",
    "use", "uses", "want", "wants",
}

WEAK_ACTION_WORDS = {"feel", "like", "make", "take", "get", "go", "come"}

QUESTION_WORDS = {"how", "what", "when", "where", "which", "who", "why"}

GENERIC_HEADS = {
    "area", "case", "goal", "idea", "method", "option", "part",
    "plan", "question", "reason", "routine", "step", "thing",
    "time", "way",
}

UNIVERSAL_ANCHOR_HEADS = {
    "account", "analytics", "assessment", "blood", "budget", "calculator",
    "campaign", "care", "cash", "course", "cycle", "date", "diet",
    "exam", "exercise", "fertility", "flow", "guide", "health",
    "income", "investment", "keyword", "learning", "lesson", "management",
    "marketing", "mucus", "ovulation", "period", "pregnancy",
    "profit", "revenue", "risk", "score", "seo", "strategy",
    "symptoms", "temperature", "tracking", "window",
}

SELECTOR_INTELLIGENCE_LAYERS = [
    "memory_feedback",
    "semantic_similarity",
    "topic_coherence",
    "cross_document_reasoning",
    "knowledge_retrieval",
    "multi_agent_reasoning",
    "hypothesis_generation",
    "multi_objective_optimization",
    "explainability",
    "qa_regression_readiness",
]


def _canonical_phrase(s: str) -> str:
    return canonical_phrase(s)


def _tokens(phrase: str) -> List[str]:
    return _canonical_phrase(phrase).split()


def _content_tokens(tokens: List[str]) -> List[str]:
    return [
        t for t in tokens
        if t not in CONNECTORS
        and t not in AUXILIARY_VERBS
        and t not in WEAK_PRONOUN_STARTS
    ]


def _has_anchor_head(tokens: List[str]) -> bool:
    if not tokens:
        return False

    head = tokens[-1]

    if head in GENERIC_HEADS:
        return False

    if head in UNIVERSAL_ANCHOR_HEADS:
        return True

    if len(tokens) >= 2:
        phrase = " ".join(tokens[-2:])
        if phrase in {
            "fertile window",
            "birth control",
            "ovulation cycle",
            "menstrual cycle",
            "basal body",
            "body temperature",
            "cervical mucus",
            "family planning",
        }:
            return True

    return False


def _is_intent_phrase(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if tokens[0] in QUESTION_WORDS:
        return True

    if tokens[0] in {"signs", "symptoms", "causes", "treatment"}:
        return True

    if tokens[0] == "best":
        return True

    return False


def _has_connector_leak(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False

    if tokens[0] in CONNECTORS or tokens[-1] in CONNECTORS:
        return True

    for i, tok in enumerate(tokens[1:-1], start=1):
        if tok not in CONNECTORS:
            continue

        left = tokens[i - 1]
        right = tokens[i + 1]

        if tok in {"of", "for", "in", "with", "during", "after", "before"}:
            if left not in ACTION_VERBS and right not in AUXILIARY_VERBS:
                continue

        return True

    return False


def _is_broken_question_fragment(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if tokens[0] in QUESTION_WORDS:
        if len(tokens) < 3:
            return True

        if len(tokens) >= 2 and tokens[1] in AUXILIARY_VERBS:
            if len(tokens) == 3:
                return True

            if tokens[-1] in {"question", "answer", "result"}:
                return True

    return False


def _is_clause_fragment(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if tokens[0] in WEAK_PRONOUN_STARTS:
        return True

    if tokens[0] in AUXILIARY_VERBS:
        return True

    if len(tokens) >= 2 and tokens[0] in ACTION_VERBS and not _is_intent_phrase(tokens):
        return True

    if len(tokens) >= 3 and tokens[1] in AUXILIARY_VERBS and not _is_intent_phrase(tokens):
        return True

    if tokens[-1] in ACTION_VERBS:
        return True

    return False


def _is_weak_generic_phrase(tokens: List[str], source_type: str = "") -> bool:
    if not tokens:
        return True

    if source_type in {"title", "heading_h1", "heading_h2", "heading_h3", "entity", "intent"}:
        return False

    if len(tokens) == 2 and tokens[-1] in GENERIC_HEADS:
        return True

    if len(tokens) <= 3 and not _has_anchor_head(tokens) and not _is_intent_phrase(tokens):
        return True

    return False


def _is_structural_fragment(phrase: str, source_type: str = "") -> bool:
    clean = _canonical_phrase(phrase)
    tokens = clean.split()

    if not clean or len(tokens) < 2:
        return True

    if len(tokens) > 8:
        return True

    if len(set(tokens)) < len(tokens):
        return True

    if _is_broken_question_fragment(tokens):
        return True

    if _has_connector_leak(tokens):
        return True

    if _is_clause_fragment(tokens):
        return True

    if _is_weak_generic_phrase(tokens, source_type=source_type):
        return True

    content = _content_tokens(tokens)

    if any(t in WEAK_ACTION_WORDS for t in tokens):
        if len(content) < 3 and not _is_intent_phrase(tokens):
            return True

    if not _is_intent_phrase(tokens) and not _has_anchor_head(tokens):
        if len(tokens) >= 3 and len(content) >= 3:
            return False
        return True

    if source_type == "sentence" and not _is_intent_phrase(tokens):
        if not _has_anchor_head(tokens) and len(content) < 3:
            return True

    return False


def _clean_selector_phrase(phrase: str, source_type: str = "") -> str:
    clean = _canonical_phrase(phrase)
    if not clean:
        return ""

    guard = candidate_window_guard(clean, source_type=source_type or "")
    if isinstance(guard, dict):
        guarded_phrase = _canonical_phrase(str(guard.get("phrase") or ""))
        if guarded_phrase:
            return guarded_phrase

    return clean


def _passes_guard(phrase: str, source_type: str = "") -> bool:
    clean = _canonical_phrase(phrase)
    if not clean:
        return False

    if _is_structural_fragment(clean, source_type=source_type):
        return False

    guard = candidate_window_guard(clean, source_type=source_type or "")
    if not isinstance(guard, dict):
        return True

    return bool(guard.get("keep"))


def _score_with_strength(
    phrase: str,
    source_type: str,
    vertical: str,
    freq: int = 1,
) -> Dict[str, Any]:
    clean = _canonical_phrase(phrase)
    if not clean:
        return {"keep": False, "score": 0.0, "reason": "empty_phrase"}

    try:
        result = score_phrase_strength(
            phrase=clean,
            source_type=source_type or "",
            vertical=vertical,
            frequency=freq,
        )
    except TypeError:
        try:
            result = score_phrase_strength(
                phrase=clean,
                source_type=source_type or "",
            )
        except Exception:
            result = {"keep": False, "score": 0.0, "reason": "score_error"}
    except Exception:
        result = {"keep": False, "score": 0.0, "reason": "score_error"}

    if not isinstance(result, dict):
        return {
            "keep": bool(result),
            "score": float(result or 0.0),
            "reason": "numeric_result",
        }

    return result


def _source_type_bonus(source_type: str) -> float:
    if source_type in {"title", "heading_h1"}:
        return 20.0
    if source_type in {"heading_h2", "heading_h3"}:
        return 15.0
    if source_type in {"entity", "intent"}:
        return 12.0
    if source_type == "list_item":
        return 8.0
    if source_type == "action_object":
        return 8.0
    if source_type == "condition_phrase":
        return 6.0
    if source_type == "noun_phrase":
        return 4.0
    return 0.0


def _final_quality_gate(row: Dict[str, Any]) -> bool:
    phrase = _canonical_phrase(str(row.get("phrase") or ""))
    source_type = str(row.get("source_type") or "")

    if not phrase:
        return False

    tokens = phrase.split()

    if len(tokens) < 2 or len(tokens) > 8:
        return False

    if len(set(tokens)) < len(tokens):
        return False

    if _is_structural_fragment(phrase, source_type=source_type):
        return False

    if not bool(row.get("keep")):
        return False

    if float(row.get("score") or 0.0) <= 0:
        return False

    return True


def _local_dedupe_phrase_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best_by_canonical: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        phrase = _canonical_phrase(str(row.get("phrase") or ""))
        canonical = _canonical_phrase(str(row.get("canonical") or phrase))

        if not phrase or not canonical:
            continue

        row["phrase"] = phrase
        row["canonical"] = canonical

        current = best_by_canonical.get(canonical)
        if current is None:
            best_by_canonical[canonical] = row
            continue

        row_score = float(row.get("score") or 0.0)
        current_score = float(current.get("score") or 0.0)

        row_quality = float(row.get("quality_score") or 0.0)
        current_quality = float(current.get("quality_score") or 0.0)

        if (row_score, row_quality, -len(phrase)) > (
            current_score,
            current_quality,
            -len(str(current.get("phrase") or "")),
        ):
            best_by_canonical[canonical] = row

    return list(best_by_canonical.values())


def _semantic_root(tokens: List[str]) -> str:
    if not tokens:
        return ""

    important = _content_tokens(tokens)
    if not important:
        important = tokens

    return " ".join(important[:2])


def _semantic_overlap(a: str, b: str) -> float:
    ta = set(_tokens(a))
    tb = set(_tokens(b))

    if not ta or not tb:
        return 0.0

    inter = len(ta & tb)
    union = len(ta | tb)

    return inter / max(1, union)


def _is_semantic_competitor(a: str, b: str) -> bool:
    a = _canonical_phrase(a)
    b = _canonical_phrase(b)

    if not a or not b:
        return False

    if a == b:
        return True

    if a in b or b in a:
        shorter = min(len(_tokens(a)), len(_tokens(b)))
        if shorter >= 2:
            return True

    if _semantic_overlap(a, b) >= 0.60:
        return True

    ra = _semantic_root(_tokens(a))
    rb = _semantic_root(_tokens(b))

    if ra and rb and ra == rb:
        return True

    return False


def _coverage_key(phrase: str) -> str:
    tokens = _content_tokens(_tokens(phrase))
    if not tokens:
        return ""

    if len(tokens) == 1:
        return tokens[0]

    return tokens[-1]


def _selector_intelligence_result(
    row: Dict[str, Any],
    *,
    selected_before: List[Dict[str, Any]],
    semantic_competitor_blocked: bool = False,
) -> Dict[str, Any]:
    phrase = str(row.get("phrase") or "")
    score = float(row.get("score") or 0.0)
    quality_score = float(row.get("quality_score") or 0.0)
    freq = int(row.get("frequency") or 1)

    semantic_diversity = 1.0
    closest_overlap = 0.0

    for existing in selected_before:
        overlap = _semantic_overlap(phrase, str(existing.get("phrase") or ""))
        closest_overlap = max(closest_overlap, overlap)
        if _is_semantic_competitor(phrase, str(existing.get("phrase") or "")):
            semantic_diversity = min(semantic_diversity, 0.25)

    coverage = 0.85 if _coverage_key(phrase) else 0.50
    runtime_usefulness = min(1.0, max(0.0, score / 120.0))
    frequency_signal = min(1.0, freq / 5.0)

    selector_score = (
        (runtime_usefulness * 0.35)
        + (float(quality_score or 0.0) * 0.25)
        + (semantic_diversity * 0.20)
        + (coverage * 0.10)
        + (frequency_signal * 0.10)
    )

    selector_score = round(max(0.0, min(1.0, selector_score)), 4)

    if semantic_competitor_blocked:
        decision = "REJECT"
        reason = "semantic_competitor_suppressed"
    else:
        decision = "ACCEPT"
        reason = "selector_accept"

    return {
        "selector_score": selector_score,
        "decision": decision,
        "reason": reason,
        "signals": {
            "runtime_usefulness": round(runtime_usefulness, 4),
            "quality_score": round(float(quality_score or 0.0), 4),
            "semantic_diversity": round(semantic_diversity, 4),
            "closest_semantic_overlap": round(closest_overlap, 4),
            "coverage": round(coverage, 4),
            "frequency_signal": round(frequency_signal, 4),
        },
        "layers": SELECTOR_INTELLIGENCE_LAYERS,
    }


def _apply_selector_intelligence(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []

    ranked = sorted(
        rows,
        key=lambda x: (
            -float(x.get("score") or 0),
            -float(x.get("quality_score") or 0),
            len(str(x.get("phrase") or "")),
            str(x.get("phrase") or ""),
        ),
    )

    for row in ranked:
        phrase = str(row.get("phrase") or "")
        blocked = any(
            _is_semantic_competitor(
                phrase,
                str(existing.get("phrase") or ""),
            )
            for existing in selected
        )

        row["selector_intelligence"] = _selector_intelligence_result(
            row,
            selected_before=selected,
            semantic_competitor_blocked=blocked,
        )

        if blocked:
            continue

        selected.append(row)

    return selected


def _dedupe_and_rank(
    candidates: List[Dict[str, Any]],
    vertical: str = "universal",
) -> List[Dict[str, Any]]:
    cleaned_phrases = [
        _clean_selector_phrase(
            str(c.get("phrase") or ""),
            str(c.get("source_type") or "unknown"),
        )
        for c in candidates
        if c.get("phrase")
    ]

    counter = Counter(p for p in cleaned_phrases if p)
    scored_rows: List[Dict[str, Any]] = []

    for c in candidates:
        original_phrase = _canonical_phrase(str(c.get("phrase") or ""))
        source_type = str(c.get("source_type") or "unknown")
        context = str(c.get("snippet") or "")

        phrase = _clean_selector_phrase(original_phrase, source_type=source_type)
        if not phrase:
            continue

        if not _passes_guard(phrase, source_type=source_type):
            continue

        freq = counter.get(phrase, 1)

        quality = _score_with_strength(
            phrase=phrase,
            source_type=source_type,
            vertical=vertical,
            freq=freq,
        )

        if not quality.get("keep"):
            continue

        raw_score = float(quality.get("score") or 0.0)
        score = raw_score * 100.0 if raw_score <= 1.0 else raw_score

        score += _source_type_bonus(source_type)

        if freq >= 2:
            score += min(freq * 1.2, 8.0)

        score = apply_vertical_policy_score(phrase, score, vertical)

        row = {
            "phrase": phrase,
            "canonical": phrase,
            "source_type": source_type,
            "score": round(float(score), 4),
            "quality_score": quality.get("score"),
            "quality_reason": quality.get("reason"),
            "keep": True,
            "section_id": c.get("section_id", ""),
            "snippet": context,
            "original_phrase": original_phrase,
            "frequency": freq,
            "extractor_intelligence": (
                c.get("extractor_intelligence")
                if isinstance(c.get("extractor_intelligence"), dict)
                else {}
            ),
        }

        guard = candidate_window_guard(phrase, source_type=source_type or "")
        if isinstance(guard, dict):
            row["quality_gate"] = guard.get("quality_gate") if isinstance(guard.get("quality_gate"), dict) else {}
        else:
            row["quality_gate"] = {}

        if _final_quality_gate(row):
            scored_rows.append(row)

    deduped = _local_dedupe_phrase_rows(scored_rows)
    intelligence_selected = _apply_selector_intelligence(deduped)

    selected = [
        {
            "phrase": row.get("phrase", ""),
            "canonical": row.get("canonical") or row.get("phrase", ""),
            "source_type": row.get("source_type", "unknown"),
            "score": round(float(row.get("score") or 0.0), 4),
            "quality_score": row.get("quality_score"),
            "quality_reason": row.get("quality_reason"),
            "section_id": row.get("section_id", ""),
            "snippet": row.get("snippet", ""),
            "original_phrase": row.get("original_phrase", ""),
            "frequency": row.get("frequency", 1),
            "extractor_intelligence": row.get("extractor_intelligence", {}),
            "quality_gate": row.get("quality_gate", {}),
            "selector_intelligence": row.get("selector_intelligence", {}),
        }
        for row in intelligence_selected
        if _final_quality_gate(row)
    ]

    ranked = sorted(
        selected,
        key=lambda x: (
            -float((x.get("selector_intelligence") or {}).get("selector_score") or 0),
            -float(x.get("score") or 0),
            len(str(x.get("phrase") or "")),
            str(x.get("phrase") or ""),
        ),
    )

    return ranked[:80]


def select_upload_phrases(
    workspace_id: str,
    doc_id: str,
    original_name: str,
    html: str,
    text: str,
) -> Dict[str, Any]:
    paragraphs = extract_paragraphs(html=html or "", text=text or "")

    candidates = extract_smart_phrases(
        text=text or "",
        html=html or "",
        title=original_name or "",
        doc_id=doc_id or "",
        max_candidates=500,
    )

    combined_text = "\n".join([
        original_name or "",
        text or "",
    ])

    vertical = detect_vertical(combined_text.lower()) or "universal"

    selected = _dedupe_and_rank(candidates, vertical=vertical)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "doc_id": doc_id,
        "vertical": vertical,
        "paragraph_count": len(paragraphs),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "selector_intelligence_summary": {
            "enabled": True,
            "layers": SELECTOR_INTELLIGENCE_LAYERS,
        },
        "phrases": selected,
    }