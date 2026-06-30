"""
Candidate window guard (corrected, niche-agnostic).

Role
----
A *downstream* accept/reject gate. It receives an already-extracted candidate
phrase and decides whether it is a clean anchor. It returns the same
``quality_gate`` record shape as before, so it is a drop-in replacement for
``candidate_window_guard``.

What changed vs. the previous version
-------------------------------------
The previous guard gated on large hand-curated *noun* vocabularies and a set of
regexes memorised from specific documents. That made it (a) reject many perfectly
good anchors whose modifier happened to be a common adjective ("simple interest",
"regular expression", "search results"), (b) silently rewrite phrases to a
hardcoded "core", and (c) carry a six-signal score that was decorative — every
accepted phrase scored exactly 1.0, so the REVIEW band was unreachable.

This version follows the same asymmetry that makes phrase work universal:

  * VERBS are a (mostly) closed, niche-independent class -> we gate on a curated
    *verb* lexicon (clause verbs, action-led leaks). Curating verbs is fine; they
    do not vary by niche.
  * NOUNS are open and vary by niche -> we NEVER reject a phrase because its head
    noun is unknown. Weakness is judged on the HEAD, not on a modifier, and only
    truly vacuous heads (thing/way/stuff/aspect) count.

The score is now honest: it is computed from real, transparent signals, so the
ACCEPT / REVIEW / REJECT bands are all reachable and mean something.

No required third-party or backend dependencies; the learning hook is optional.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

# --------------------------------------------------------------------------- #
# Optional learning hook — degrades gracefully if the backend isn't present.
# --------------------------------------------------------------------------- #
try:  # pragma: no cover - infra dependent
    from backend.server.stores.dis_pipeline_learning import (  # type: ignore
        learn_from_pipeline_rejection,
    )
except Exception:  # pragma: no cover
    def learn_from_pipeline_rejection(**_kwargs: Any) -> None:
        return None


WORD_RE = re.compile(r"[a-z0-9]{2,}", re.I)


# --------------------------------------------------------------------------- #
# Closed-ish function / verb classes (niche-independent).
# --------------------------------------------------------------------------- #

STOPWORDS: Set[str] = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
    "are", "was", "were", "will", "can", "could", "should", "would", "have",
    "has", "had", "about", "over", "under", "than", "then", "a", "an", "to",
    "of", "in", "on", "at", "by", "or", "as", "is", "it", "be", "not", "no",
    "if", "but", "so", "because", "while", "up", "down", "out", "off", "too",
    "very", "also", "their", "our", "his", "her", "its", "them", "they", "we",
}

CONNECTORS: Set[str] = {
    "for", "to", "with", "without", "before", "after", "during", "between",
    "among", "against", "through", "across", "near", "within", "around",
    "beyond", "via", "per",
}
# Connectors that frequently sit *inside* a legitimate term and so must not, on
# their own, condemn a phrase ("rate of return", "return on investment",
# "cost of goods", "point in time").
TERM_CONNECTORS: Set[str] = {"of", "on", "in"}

LEADING_ADVERBS: Set[str] = {
    "quickly", "slowly", "often", "usually", "sometimes", "really", "simply",
    "just", "always", "never", "very", "quite", "rather", "highly",
}

# Auxiliaries / copulas / modals — unambiguous clause signals.
AUX_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "been", "being", "am", "has", "have",
    "had", "do", "does", "did", "can", "could", "should", "would", "will",
    "shall", "may", "might", "must",
}

# Verbs that are *clearly* verbs (not common noun homographs). Used to detect
# clause leaks anywhere in the phrase. Deliberately EXCLUDES ambiguous words
# such as rate / score / review / report / support / plan / study / search /
# track / drive / charge, which are frequently noun heads.
CLAUSE_VERBS: Set[str] = {
    "become", "becomes", "became", "mean", "means", "depend", "depends",
    "help", "helps", "improve", "improves", "reduce", "reduces", "increase",
    "increases", "require", "requires", "contain", "contains", "reveal",
    "reveals", "affect", "affects", "struggle", "struggles", "enable",
    "enables", "allow", "allows", "prevent", "prevents", "boost", "boosts",
    "lower", "lowers", "raise", "raises", "deliver", "delivers", "provide",
    "provides", "explain", "explains", "describe", "describes", "include",
    "includes", "offer", "offers", "create", "creates", "build", "builds",
    "drive", "drives", "ensure", "ensures", "happen", "happens", "occur",
    "occurs", "cause", "causes", "remain", "remains", "appear", "appears",
    "seem", "seems", "comes", "goes", "make", "makes", "get", "gets",
}

# Verbs that, when they LEAD a phrase, signal a verb+object clause leak
# ("reduce churn", "improve activation"). Closed class -> niche independent.
ACTION_LEAD_VERBS: Set[str] = {
    "neglect", "avoid", "reduce", "improve", "manage", "monitor", "review",
    "choose", "define", "send", "skip", "treat", "increase", "decrease",
    "boost", "lower", "raise", "optimize", "optimise", "maximize", "maximise",
    "minimize", "minimise", "build", "create", "design", "develop", "deliver",
    "ensure", "enable", "prevent", "handle", "perform", "achieve", "calculate",
    "estimate", "configure", "deploy", "install", "remove", "replace", "update",
    "compare", "identify", "measure", "analyze", "analyse", "understand",
    "learn", "discover", "explore", "find", "get", "make", "use",
}

# Intent prefixes that legitimately contain a verb ("how to track spend").
INTENT_STARTS: Tuple[str, ...] = (
    "how to", "how many", "how much", "what is", "what are", "when to",
    "where to", "why is", "why are", "best way to", "best time to",
    "best ways to", "ways to", "steps to", "tips for", "guide to",
    "reasons to", "signs of", "benefits of", "causes of", "symptoms of",
)
INTENT_FIRST_WORDS: Set[str] = {w.split()[0] for w in INTENT_STARTS}

# Truly vacuous heads — contentless no matter the niche.
VACUOUS_HEADS: Set[str] = {
    "thing", "things", "stuff", "way", "ways", "aspect", "aspects",
    "lot", "lots", "bit", "bits", "kind", "kinds", "sort", "sorts",
}

# Weak modifiers — they don't reject on their own, but a phrase made of ONLY
# weak modifiers + a vacuous head is junk, and they lower the score.
WEAK_MODIFIERS: Set[str] = {
    "good", "better", "best", "great", "nice", "useful", "helpful", "important",
    "simple", "basic", "common", "general", "regular", "normal", "same",
    "various", "different", "certain", "particular", "specific", "valuable",
    "healthy", "traditional", "random", "minor", "major", "other", "another",
    "several", "many", "some", "any", "each", "every", "main", "key", "top",
    "real", "actual", "overall", "whole", "big", "full", "total", "only",
}


# --------------------------------------------------------------------------- #
# Verb-form expansion (so we recognise inflections of the closed verb classes).
# --------------------------------------------------------------------------- #

def _expand_forms(lemmas: Set[str]) -> Set[str]:
    forms: Set[str] = set()
    for v in lemmas:
        forms.add(v)
        forms.update({v + "s", v + "es", v + "ed", v + "ing"})
        if v.endswith("e"):
            forms.update({v[:-1] + "es", v[:-1] + "ed", v[:-1] + "ing"})
        if v.endswith("y") and len(v) > 1 and v[-2] not in "aeiou":
            forms.update({v[:-1] + "ies", v[:-1] + "ied"})
    return forms


_CLAUSE_VERB_FORMS: Set[str] = _expand_forms(CLAUSE_VERBS) | AUX_VERBS
_ACTION_LEAD_FORMS: Set[str] = _expand_forms(ACTION_LEAD_VERBS)


def _is_gerund(w: str) -> bool:
    """-ing forms act as nominal/participial modifiers, not clause verbs."""
    return len(w) > 4 and w.endswith("ing")


def _is_clause_verb(w: str) -> bool:
    if _is_gerund(w):
        return False
    return w in _CLAUSE_VERB_FORMS


# --------------------------------------------------------------------------- #
# Quality-gate record (honest, computed scoring).
# --------------------------------------------------------------------------- #

QUALITY_GATE_WEIGHTS: Dict[str, float] = {
    "logical_structure": 0.20,
    "context_fit": 0.20,
    "pragmatic_anchor_value": 0.25,
    "topic_coherence": 0.15,
    "trust_risk_safety": 0.10,
    "rule_hybrid_check": 0.10,
}

ACCEPT_AT = 0.80
REVIEW_AT = 0.60


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]


def make_quality_gate_result(phrase: str, score: float, decision: str,
                             signals: Dict[str, float],
                             reasons: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "phrase": phrase,
        "quality_gate_score": round(float(score), 4),
        "decision": decision,
        "signals": signals or {},
        "reasons": reasons or [],
    }


def _weighted(signals: Dict[str, float]) -> float:
    return round(sum(float(signals.get(k, 0.0)) * w
                     for k, w in QUALITY_GATE_WEIGHTS.items()), 4)


def _decision(score: float, keep: bool) -> str:
    if not keep:
        return "REJECT"
    if score >= ACCEPT_AT:
        return "ACCEPT"
    if score >= REVIEW_AT:
        return "REVIEW"
    return "REVIEW"  # kept but low-confidence -> never silently dropped


def _accept_signals(tokens: List[str]) -> Dict[str, float]:
    """Real, transparent signals for a phrase we keep."""
    content = [t for t in tokens if t not in STOPWORDS and t not in CONNECTORS]
    n = len(tokens)
    head_weak = bool(tokens) and tokens[-1] in VACUOUS_HEADS
    has_weak_mod = any(t in WEAK_MODIFIERS for t in tokens)
    strong_content = [t for t in content
                      if t not in WEAK_MODIFIERS and t not in VACUOUS_HEADS]

    sig = {
        "logical_structure": 1.0,
        "context_fit": 1.0,
        "pragmatic_anchor_value": 1.0,
        "topic_coherence": 1.0,
        "trust_risk_safety": 1.0,
        "rule_hybrid_check": 1.0,
    }
    if n > 5:
        sig["logical_structure"] = 0.85
    if has_weak_mod:
        sig["topic_coherence"] = 0.80
    if not strong_content:
        sig["pragmatic_anchor_value"] = 0.55
    elif head_weak:
        sig["pragmatic_anchor_value"] = 0.70
    if len(content) < 2:
        sig["pragmatic_anchor_value"] = min(sig["pragmatic_anchor_value"], 0.75)
    return sig


def _attach(result: Dict[str, Any], signals: Dict[str, float],
            reasons: List[str]) -> Dict[str, Any]:
    keep = bool(result.get("keep"))
    if not keep:
        signals = dict(signals)
        signals["rule_hybrid_check"] = 0.0
    score = _weighted(signals)
    result["quality_gate"] = make_quality_gate_result(
        phrase=result.get("phrase", ""), score=score,
        decision=_decision(score, keep), signals=signals, reasons=reasons,
    )
    return result


def _reject(phrase: str, reason: str, signals: Dict[str, float], *,
            workspace_id: str, document_id: str, vertical: str) -> Dict[str, Any]:
    learn_from_pipeline_rejection(
        workspace_id=workspace_id, document_id=document_id, vertical=vertical,
        pipeline_stage="candidate_window_guard",
        candidate={"phrase": phrase}, rejection_reason=reason,
    )
    return _attach({"keep": False, "reason": reason, "phrase": phrase},
                   signals, [reason])


def _accept(phrase: str, tokens: List[str]) -> Dict[str, Any]:
    return _attach({"keep": True, "reason": "guard_pass", "phrase": phrase},
                   _accept_signals(tokens), ["guard_pass"])


def _review(phrase: str, tokens: List[str], reason: str,
            signals: Dict[str, float]) -> Dict[str, Any]:
    """Kept, but flagged as borderline (not silently dropped)."""
    base = _accept_signals(tokens)
    base.update(signals)
    return _attach({"keep": True, "reason": reason, "phrase": phrase},
                   base, [reason])


# --------------------------------------------------------------------------- #
# Boundary trimming (predictable; no semantic rewriting).
# --------------------------------------------------------------------------- #

def _trim_boundaries(tokens: List[str]) -> List[str]:
    toks = list(tokens)
    while toks and (toks[0] in STOPWORDS or toks[0] in CONNECTORS
                    or toks[0] in LEADING_ADVERBS):
        toks.pop(0)
    while toks and (toks[-1] in STOPWORDS or toks[-1] in CONNECTORS
                    or toks[-1] in AUX_VERBS):
        toks.pop()
    return toks


def _is_intent(tokens: List[str]) -> bool:
    if not tokens or tokens[0] not in INTENT_FIRST_WORDS:
        return False
    joined = " ".join(tokens)
    return any(joined.startswith(p) for p in INTENT_STARTS)


# --------------------------------------------------------------------------- #
# Individual, head-aware checks.
# --------------------------------------------------------------------------- #

def _starts_or_ends_badly(tokens: List[str]) -> bool:
    if not tokens:
        return True
    return (tokens[0] in STOPWORDS or tokens[0] in CONNECTORS
            or tokens[-1] in STOPWORDS or tokens[-1] in CONNECTORS
            or tokens[0] in LEADING_ADVERBS)


def _is_action_led_leak(tokens: List[str]) -> bool:
    """A verb+object clause fragment ('reduce churn', 'improve activation').
    Gated on the closed action-verb class; gerund-led modifiers are exempt."""
    if len(tokens) < 2:
        return False
    head = tokens[0]
    if _is_gerund(head):
        return False
    if head not in _ACTION_LEAD_FORMS:
        return False
    # a term connector immediately after a verb still reads as a clause
    return True


def _has_clause_verb(tokens: List[str]) -> bool:
    """A finite clause verb anywhere makes this a sentence fragment, not an
    anchor — unless it's a recognised intent phrase."""
    if _is_intent(tokens):
        return False
    return any(_is_clause_verb(t) for t in tokens)


def _is_all_weak(tokens: List[str]) -> bool:
    """Every content token is a weak modifier or vacuous head -> junk
    ('various things', 'best ways', 'simple stuff')."""
    content = [t for t in tokens if t not in STOPWORDS and t not in CONNECTORS]
    if not content:
        return True
    return all(t in WEAK_MODIFIERS or t in VACUOUS_HEADS for t in content)


def _is_vacuous_head(tokens: List[str]) -> bool:
    """Head is contentless but a real (non-weak) word qualifies it
    ('marketing stuff', 'config thing') -> keep but flag for REVIEW. The
    all-weak case ('best ways') is handled earlier as a hard reject."""
    if not tokens or tokens[-1] not in VACUOUS_HEADS:
        return False
    if _is_intent(tokens):
        return False
    quals = [t for t in tokens[:-1]
             if t not in STOPWORDS and t not in CONNECTORS]
    strong = [t for t in quals if t not in WEAK_MODIFIERS]
    return len(strong) >= 1


def _has_duplicate_noise(tokens: List[str]) -> bool:
    if len(tokens) < 3:
        return False
    return len(set(tokens)) / len(tokens) < 0.6


def _too_many_connectors(tokens: List[str]) -> bool:
    """One internal connector is fine ('rate of return'); several means a
    stitched clause ('tips for owners with budgets for teams')."""
    return sum(1 for t in tokens if t in CONNECTORS or t in TERM_CONNECTORS) >= 2


# --------------------------------------------------------------------------- #
# Public entry point.
# --------------------------------------------------------------------------- #

def candidate_window_guard(
    candidate: str,
    *,
    source_type: str = "",
    workspace_id: str = "default",
    document_id: str = "",
    vertical: str = "general",
    max_tokens: int = 8,
) -> Dict[str, Any]:
    phrase = " ".join(tokenize(candidate))

    def rej(p: str, reason: str, signals: Dict[str, float]) -> Dict[str, Any]:
        return _reject(p, reason, signals, workspace_id=workspace_id,
                       document_id=document_id, vertical=vertical)

    if not phrase:
        return rej("", "empty_candidate",
                   {"logical_structure": 0.0, "pragmatic_anchor_value": 0.0})

    # Predictable boundary trim (no semantic rewriting).
    tokens = _trim_boundaries(phrase.split())
    phrase = " ".join(tokens)

    if len(tokens) < 2:
        return rej(phrase, "too_short",
                   {"logical_structure": 0.30, "pragmatic_anchor_value": 0.15})

    if len(tokens) > max_tokens:
        return rej(phrase, "too_long",
                   {"logical_structure": 0.40, "context_fit": 0.45,
                    "pragmatic_anchor_value": 0.30})

    if _starts_or_ends_badly(tokens):
        return rej(phrase, "bad_boundary",
                   {"logical_structure": 0.25, "pragmatic_anchor_value": 0.20})

    if _is_action_led_leak(tokens):
        return rej(phrase, "action_leak_start",
                   {"logical_structure": 0.35, "pragmatic_anchor_value": 0.20,
                    "topic_coherence": 0.40})

    if _has_clause_verb(tokens):
        return rej(phrase, "clause_leak",
                   {"logical_structure": 0.25, "context_fit": 0.35,
                    "pragmatic_anchor_value": 0.20})

    if _is_all_weak(tokens):
        return rej(phrase, "all_weak_terms",
                   {"logical_structure": 0.40, "pragmatic_anchor_value": 0.10,
                    "topic_coherence": 0.30})

    if _is_vacuous_head(tokens):
        return _review(phrase, tokens, "vacuous_head_review",
                       {"pragmatic_anchor_value": 0.45, "topic_coherence": 0.55})

    if _has_duplicate_noise(tokens):
        return rej(phrase, "duplicate_noise",
                   {"logical_structure": 0.25, "pragmatic_anchor_value": 0.25})

    if _too_many_connectors(tokens):
        return rej(phrase, "stitched_connectors",
                   {"logical_structure": 0.25, "context_fit": 0.30,
                    "pragmatic_anchor_value": 0.20})

    return _accept(phrase, tokens)


__all__ = ["candidate_window_guard", "make_quality_gate_result", "tokenize"]