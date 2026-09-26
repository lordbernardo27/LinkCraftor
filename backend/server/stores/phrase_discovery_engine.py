"""
Phrase Discovery Engine (LinkCraftor)
=====================================

Niche-neutral discovery layer that revisits an uploaded document AFTER the
Smart Phrase Extractor and proposes additional LITERAL phrase candidates the
extractor missed.

Canonical position in the architecture::

    Smart Phrase Extractor ──┬──────────────────────────────┐
                             ▼                              ▼
                     Extracted Phrases          Phrase Discovery Engine   <- this module
                                                  (6 internal components)
                             └──────────────┬───────────────┘
                                            ▼
                                      Phrase Merger → Candidate Window Guard →
                                      Phrase Strength Scorer → Selection → Density

Hard boundaries (enforced in code, not just documented)
-------------------------------------------------------
* Every emitted phrase is an exact character slice of the document's visible
  text (title / headings / list items / paragraphs), re-verified with a
  word-boundary-aware literal search against the ORIGINAL inputs.
* No synonyms, paraphrases, determiner-stripping or any synthetic phrase.
* No URL search, source selection, domain ranking or link-target logic.
* No final quality decision: ``discovery_signal`` is an internal ordering
  hint only (``advisory_only: True``). Candidate Window Guard remains the
  structural authority, Phrase Strength Scorer the quality authority.
* No highlight selection / density logic.
* ``vertical`` is accepted for contract compatibility but never used for logic.

Design
------
All six components share ONE document model built once per call:

1. Document segmentation that mirrors the extractor's own segmentation
   (``title_0``, ``heading_hN_k``, ``list_item_k``, ``p{pi}_s{si}``), so
   discovery section IDs line up 1:1 with extractor section IDs.
2. Offset-preserving tokenisation of each sentence.
3. POS tags from the extractor's own tagger (``pos_tag`` +
   ``_nominalize_tags``: NLTK when available, else the extractor's heuristic
   tagger) plus a small, closed-class refinement pass (modal+verb, participial
   modifiers, "-s/-ed before a determiner" verbs). No second NLP stack.
4. Maximal noun-phrase chunking using the extractor's ``_np_eligible`` /
   ``_head_is_noun_like`` rules. The key fix for the earlier weak fragments
   ("Modern cloud", "improve application", "infrastructure can") is that
   spans are only ever cut at *constituent boundaries*: the right edge of a
   span is always the right edge of its NP chunk (so a compound is never
   truncated before its head), verbs/auxiliaries never enter a nominal span,
   and there are no free token windows.
5. A document concept inventory (heads and compound cores with sentence /
   section / heading / title / extractor support) that every component uses as
   document-local evidence. No niche dictionaries.

Closed-class word lists used here (relation connectors, evidence markers,
normative nouns such as "standard"/"guideline"/"regulation", institution nouns
such as "agency"/"institute") are generic English function/discourse
vocabulary that occurs identically across all niches. They are SIGNALS for
where to look; they are never emitted on their own and never gate the head
noun of a phrase.
"""

from __future__ import annotations

import html as html_lib
import logging
import re
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # Reuse the Smart Phrase Extractor's linguistic infrastructure.
    from backend.server.stores import smart_phrase_extractor as _spe  # type: ignore
except Exception:  # pragma: no cover - relative / standalone fallbacks
    try:
        from . import smart_phrase_extractor as _spe  # type: ignore
    except Exception:
        import smart_phrase_extractor as _spe  # type: ignore

logger = logging.getLogger(__name__)

__all__ = ["discover_phrases", "DISCOVERY_COMPONENTS", "ENGINE_VERSION"]

ENGINE_VERSION = "phrase_discovery_engine/1.0"
POSITION_BASIS = "phrase_discovery_surface_v1"

SEMANTIC = "semantic_discovery"
RELATIONSHIP = "relationship_discovery"
CONTENT_CONTEXT = "content_context_discovery"
LONG_TAIL = "long_tail_discovery"
PATTERN = "pattern_discovery"
EXTERNAL_AUTHORITY = "external_authority_discovery"

DISCOVERY_COMPONENTS: Tuple[str, ...] = (
    SEMANTIC, RELATIONSHIP, CONTENT_CONTEXT, LONG_TAIL, PATTERN, EXTERNAL_AUTHORITY,
)

# ---------------------------------------------------------------------------
# Shared linguistic resources (re-exported from the extractor: one stack).
# ---------------------------------------------------------------------------

FUNCTION_WORDS = _spe.FUNCTION_WORDS
LEADING_BAN = _spe.LEADING_BAN
TRAILING_BAN = _spe.TRAILING_BAN
AUX_VERBS = _spe.AUX_VERBS
PRONOUNS = _spe.PRONOUNS
DETERMINERS = _spe.DETERMINERS
PREPOSITIONS = _spe.PREPOSITIONS
CONJUNCTIONS = _spe.CONJUNCTIONS
PARTICLES_DEGREE = _spe.PARTICLES_DEGREE
GENERIC_WEAK_HEADS = _spe.GENERIC_WEAK_HEADS
STRIP_INTERIOR = _spe.STRIP_INTERIOR
COMPARATIVES = _spe.COMPARATIVES
ALL_VERB_LEMMAS = _spe.ALL_VERB_LEMMAS

# ---------------------------------------------------------------------------
# Closed-class, niche-neutral structural vocabulary.
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[^\W_]+(?:['\u2019\-.][^\W_]+)*", re.UNICODE)
_JOINABLE_GAP_RE = re.compile(r"^\s*(?:[&/]\s*)?$")
_BULLET_RE = re.compile(r"^\s*(?:[-*\u2022\u2013]|\d{1,3}[.)])\s+")
_MD_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+")
_STAT_RE = re.compile(
    r"\d(?:[\d,.]*\d)?\s?(?:%|percent\b|per\s?cent\b)"
    r"|\b\d+(?:\.\d+)?\s?(?:million|billion|trillion|thousand)\b",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"\b(?:1[89]|20)\d{2}\b")

_MAX_NP_TOKENS = 8
_OPEN_PUNCT = frozenset("([{\"'\u201c\u2018\u00ab")
_CLOSE_PUNCT = frozenset(".,;:!?)]}\"'\u201d\u2019\u00bb\u2026")
_MAX_INTENT_TOKENS = 10

_MODALS = frozenset({"can", "could", "will", "would", "shall", "should",
                     "may", "might", "must"})
_DO_AUX = frozenset({"do", "does", "did"})
_ARTICLES = frozenset({"a", "an", "the"})
_POSSESSIVE_DETS = frozenset({"my", "your", "his", "her", "its", "our", "their"})
_PERSONAL_PRONOUNS = frozenset(PRONOUNS - DETERMINERS)
_QUANTIFIERS = frozenset({
    "several", "various", "numerous", "certain", "other", "same", "few",
    "multiple", "many", "much", "own", "such", "any", "each", "every", "some",
    "all", "both", "either", "neither", "enough",
})
_OF = frozenset({"of"})
# Clause-introducing / discourse words the extractor's closed lists omit.
_CLAUSE_WORDS = frozenset({"when", "where", "why", "how", "whenever", "wherever",
                           "whereby", "thus", "hence", "whilst", "once", "whether",
                           "what", "which", "who", "whom", "not"})
_CLAUSE_SPLIT = frozenset(CONJUNCTIONS | _CLAUSE_WORDS | {"which", "that", "who", "to"})
# Preposition-like closed-class words missing from the extractor's list.
_EXTRA_PREPOSITIONS = frozenset({"unlike", "despite", "including", "regarding", "concerning",
                                 "versus", "vs", "amid", "amongst", "excluding", "towards",
                                 "alongside", "beneath", "throughout"})
_BE_FORMS = frozenset({"is", "are", "was", "were", "be", "been", "being"})
_CATENATIVE = frozenset({"help", "helps", "let", "lets", "make", "makes", "see", "watch", "hear"})
_TIME_NOUNS = frozenset({"time", "times", "now", "today", "day", "days", "night", "week",
                         "weeks", "month", "months", "year", "years", "hour", "hours",
                         "minute", "minutes", "moment", "while"})
_GERUND_CLAUSE_TRIGGERS = frozenset({
    "by", "for", "in", "of", "through", "without", "while", "when", "after",
    "before", "from", "on", "about", "at", "to", "via", "into", "upon",
    "besides", "despite", "including", "toward", "towards",
})
_ACRONYM_EXCLUDE = frozenset({"I", "A", "OK", "AM", "PM", "II", "III", "IV"})
_CALENDAR_WORDS = frozenset({
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "monday", "tuesday",
    "wednesday", "thursday", "friday", "saturday", "sunday",
})
_ENTITY_CONNECTORS = frozenset({"of", "for", "and", "the", "on", "in", "de",
                                "du", "des", "da", "van", "von", "der"})
_INITIAL_SKIP = frozenset({"of", "and", "for", "the", "in", "on", "to", "a",
                           "an", "&", "at", "by", "with"})

_NOMINALIZATION_SUFFIXES = ("tion", "sion", "ment", "ance", "ence", "ity",
                            "ness", "age", "ure", "sis", "ism", "ship",
                            "ency", "ancy")
_RELATIONAL_NOUN_STEMS = frozenset({
    "risk", "cause", "effect", "impact", "benefit", "role", "source", "lack",
    "loss", "need", "use", "access", "demand", "cost", "difference",
    "relationship", "link", "ratio", "balance", "increase", "decrease",
    "reduction", "rise", "decline", "growth", "exposure", "resistance",
    "response", "contribution", "dependence", "dependency", "influence",
    "consequence", "outcome", "result", "solution", "alternative", "approach",
    "prevention", "protection", "requirement", "component", "part", "member",
    "change", "shift", "gap", "barrier", "threat", "limit", "shortage",
    "supply", "value", "effectiveness", "quality", "level", "rate", "share",
})
_FRAME_PREPS = frozenset({"of", "for", "to", "in", "on", "between", "against",
                          "with", "from", "among", "toward", "towards", "into",
                          "over", "within", "without", "across", "through"})
# Prepositions that usually attach INSIDE a noun phrase (long-tail / context
# expansions). Verb-attaching ones ("with", "during", "over", ...) are excluded.
_PP_PREPS = frozenset({"for", "in", "on", "from", "to", "without", "between",
                       "against", "under", "within"})
_OBJECT_PP_PREPS = frozenset({"of", "between", "against"})
# Only unambiguous adjective endings (-ive/-al/-ent/-ic also form many nouns:
# directive, withdrawal, unemployment, clinic).
_ADJ_SUFFIXES = ("ical", "ous", "ful", "able", "ible", "less", "etic", "atic")
_QUANTITY_HEADS = frozenset({"percent", "percentage", "cent", "%"})

# Relation connectors: (tokens, family, kind, (left_role, right_role)).
#   kind "verbal": first token must be tagged VERB in context.
#   kind "fixed":  multiword/closed connector, matched literally.
#   kind "nominal": connector begins with a noun (handled by nominal frames).
def _rel(tokens: str, family: str, kind: str, roles: Tuple[str, str]):
    return (tuple(tokens.split()), family, kind, roles)


_CE, _EC = ("cause", "effect"), ("effect", "cause")
_RELATION_MARKERS = tuple(sorted([
    _rel("leads to", "cause_effect", "fixed", _CE), _rel("lead to", "cause_effect", "fixed", _CE),
    _rel("led to", "cause_effect", "fixed", _CE), _rel("results in", "cause_effect", "fixed", _CE),
    _rel("result in", "cause_effect", "fixed", _CE), _rel("resulted in", "cause_effect", "fixed", _CE),
    _rel("contributes to", "cause_effect", "fixed", _CE), _rel("contribute to", "cause_effect", "fixed", _CE),
    _rel("caused by", "cause_effect", "fixed", _EC), _rel("due to", "cause_effect", "fixed", _EC),
    _rel("because of", "cause_effect", "fixed", _EC), _rel("causes", "cause_effect", "verbal", _CE),
    _rel("cause", "cause_effect", "verbal", _CE), _rel("caused", "cause_effect", "verbal", _CE),
    _rel("triggers", "cause_effect", "verbal", _CE), _rel("affects", "cause_effect", "verbal", _CE),
    _rel("affect", "cause_effect", "verbal", _CE), _rel("influences", "cause_effect", "verbal", _CE),
    _rel("if", "condition", "fixed", ("consequence", "condition")),
    _rel("unless", "condition", "fixed", ("consequence", "condition")),
    _rel("in case of", "condition", "fixed", ("consequence", "condition")),
    _rel("than", "comparison", "fixed", ("item_a", "item_b")),
    _rel("compared to", "comparison", "fixed", ("item_a", "item_b")),
    _rel("compared with", "comparison", "fixed", ("item_a", "item_b")),
    _rel("unlike", "comparison", "fixed", ("item_a", "item_b")),
    _rel("whereas", "comparison", "fixed", ("item_a", "item_b")),
    _rel("requires", "dependency", "verbal", ("dependent", "requirement")),
    _rel("require", "dependency", "verbal", ("dependent", "requirement")),
    _rel("depends on", "dependency", "fixed", ("dependent", "requirement")),
    _rel("depend on", "dependency", "fixed", ("dependent", "requirement")),
    _rel("relies on", "dependency", "fixed", ("dependent", "requirement")),
    _rel("rely on", "dependency", "fixed", ("dependent", "requirement")),
    _rel("needed for", "dependency", "fixed", ("requirement", "dependent")),
    _rel("required for", "dependency", "fixed", ("requirement", "dependent")),
    _rel("essential for", "dependency", "fixed", ("requirement", "dependent")),
    _rel("consists of", "part_whole", "fixed", ("whole", "part")),
    _rel("composed of", "part_whole", "fixed", ("whole", "part")),
    _rel("made up of", "part_whole", "fixed", ("whole", "part")),
    _rel("includes", "part_whole", "verbal", ("whole", "part")),
    _rel("include", "part_whole", "verbal", ("whole", "part")),
    _rel("contains", "part_whole", "verbal", ("whole", "part")),
    _rel("part of", "part_whole", "nominal", ("part", "whole")),
    _rel("improves", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("improve", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("reduces", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("reduce", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("increases", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("increase", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("prevents", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("prevent", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("enables", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("helps", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("protects", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("lowers", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("boosts", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("supports", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("allows", "feature_benefit", "verbal", ("feature", "benefit")),
    _rel("solves", "problem_solution", "verbal", ("solution", "problem")),
    _rel("addresses", "problem_solution", "verbal", ("solution", "problem")),
    _rel("resolves", "problem_solution", "verbal", ("solution", "problem")),
    _rel("mitigates", "problem_solution", "verbal", ("solution", "problem")),
    _rel("fixes", "problem_solution", "verbal", ("solution", "problem")),
    _rel("produces", "process_outcome", "verbal", ("process", "outcome")),
    _rel("generates", "process_outcome", "verbal", ("process", "outcome")),
    _rel("yields", "process_outcome", "verbal", ("process", "outcome")),
    _rel("creates", "process_outcome", "verbal", ("process", "outcome")),
    _rel("associated with", "risk_association", "fixed", ("entity", "associated")),
    _rel("linked to", "risk_association", "fixed", ("entity", "associated")),
    _rel("correlated with", "risk_association", "fixed", ("entity", "associated")),
    _rel("risk of", "risk_association", "nominal", ("entity", "risk")),
], key=lambda m: -len(m[0])))

_CONTRAST_NEXT = (("instead", "of"), ("rather", "than"), ("as", "opposed", "to"),
                  ("unlike",), ("despite",), ("except",), ("in", "contrast", "to"))
_CONTRAST_CLAUSE = frozenset({"however", "but", "although", "though", "whereas", "yet"})
_DEFINITION_NEXT = (("also", "known", "as"), ("known", "as"), ("referred", "to", "as"),
                    ("is", "called"), ("are", "called"), ("also", "called"),
                    ("termed",), ("so-called",))
_DEFINITION_PREV = (("is", "defined", "as"), ("are", "defined", "as"), ("defined", "as"),
                    ("refers", "to"), ("refer", "to"), ("stands", "for"))

# Generic institution / normative vocabulary for External Authority signals.
_INSTITUTION_HEADS = frozenset({
    "organization", "organisation", "association", "institute", "institution",
    "agency", "department", "ministry", "commission", "council", "board",
    "bureau", "authority", "administration", "university", "college",
    "society", "foundation", "federation", "committee", "centre", "center",
    "office", "court", "tribunal", "parliament", "congress", "senate",
    "assembly", "union", "alliance", "consortium", "academy", "laboratory",
    "registry", "observatory", "fund", "bank", "service", "services",
    "school", "hospital", "police", "army", "navy", "network", "forum",
})
_NORMATIVE_CATEGORY = {
    "standard": "standards", "guideline": "guidelines", "guidance": "official_guidance",
    "regulation": "regulations", "law": "laws", "act": "laws", "statute": "laws",
    "rule": "regulations", "directive": "regulations", "ordinance": "regulations",
    "code": "regulations", "protocol": "named_protocols", "framework": "standards",
    "specification": "technical_specifications", "spec": "technical_specifications",
    "policy": "official_guidance", "requirement": "regulations",
    "recommendation": "recommendations", "criterion": "formal_criteria",
    "criteria": "formal_criteria", "classification": "official_classifications",
    "certification": "standards", "convention": "laws", "treaty": "laws",
    "charter": "laws", "amendment": "laws", "mandate": "regulations",
    "provision": "regulations", "threshold": "thresholds_limits",
    "limit": "thresholds_limits", "definition": "definitions",
    "benchmark": "standards", "program": "government_programs",
    "programme": "government_programs", "initiative": "government_programs",
    "scheme": "government_programs", "warning": "safety_warnings",
    "advisory": "official_guidance", "diagnosis": "formal_criteria",
}
_LIMIT_STEMS = frozenset({"limit", "threshold", "range", "target", "minimum",
                          "maximum", "cap", "ceiling", "ratio", "quota",
                          "allowance", "dose", "dosage", "rate", "level"})
_REFERENCE_WORDS = frozenset({
    "section", "article", "rule", "chapter", "title", "part", "clause",
    "schedule", "annex", "appendix", "form", "regulation", "standard",
    "class", "category", "grade", "stage", "type", "version", "phase",
    "tier", "directive", "act", "bill", "amendment", "paragraph",
    "subsection", "level",
})
_EVIDENCE_WORDS = frozenset({
    "study", "studies", "research", "researchers", "trial", "trials",
    "survey", "surveys", "evidence", "findings", "meta-analysis", "census",
    "statistics", "percent", "percentage", "peer-reviewed", "published",
    "experiment", "experiments", "estimated", "reported",
})
_EVIDENCE_MULTI = (("according", "to"), ("found", "that"), ("showed", "that"),
                   ("suggests", "that"), ("shows", "that"), ("estimated", "that"))
_SCIENCE_WORDS = frozenset({"study", "studies", "trial", "trials", "experiment",
                            "experiments", "meta-analysis", "peer-reviewed",
                            "researchers", "research"})
_SAFETY_WORDS = frozenset({
    "warning", "warnings", "warn", "warns", "caution", "hazard", "hazards",
    "hazardous", "danger", "dangerous", "unsafe", "safety", "toxic", "risk",
    "risks", "avoid", "never", "prohibited", "illegal", "banned", "penalty",
    "penalties", "liability", "liable", "recall", "recalled", "fatal",
    "harmful", "emergency",
})
_SAFETY_MULTI = (("must", "not"), ("should", "not"), ("do", "not"), ("never", "use"))
_NORMATIVE_WORDS = frozenset({
    "must", "required", "requires", "mandatory", "shall", "prohibited",
    "permitted", "compliance", "comply", "complies", "regulated", "regulatory",
    "statutory", "official", "officially", "certified", "accredited",
    "approved", "mandated", "legal", "legally", "federal", "national",
    "international", "government", "governmental", "recommended",
    "recommends", "recommendation", "recommendations",
})
_SOURCE_INTRODUCERS = (("according", "to"), ("published", "by"), ("issued", "by"),
                       ("developed", "by"), ("recommended", "by"), ("set", "by"),
                       ("defined", "by"), ("reported", "by"), ("approved", "by"),
                       ("regulated", "by"), ("endorsed", "by"), ("maintained", "by"))

_INTENT_EXTRA = (("how", "do"), ("how", "does"), ("how", "can"), ("how", "should"),
                 ("what", "does"), ("which",), ("why", "do"), ("why", "does"),
                 ("when", "should"), ("is", "it"), ("can", "you"))
_INTENT_STARTS = tuple(sorted(
    {tuple(p.split()) for p in _spe.INTENT_STARTS} | set(_INTENT_EXTRA),
    key=lambda t: -len(t),
))


# ---------------------------------------------------------------------------
# Small text utilities (kept from the Phase-2 foundation, corrected).
# ---------------------------------------------------------------------------

def _normalize_span_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _html_to_visible_text(value: Any) -> str:
    raw = html_lib.unescape(str(value or ""))
    raw = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return _normalize_span_text(raw)


def _low(token_text: str) -> str:
    return token_text.lower().replace("\u2019", "'")


def _lows_of(text: str) -> List[str]:
    return [_low(m.group(0)) for m in _TOKEN_RE.finditer(str(text or ""))]


def _stem(word: str) -> str:
    """Tiny, niche-neutral plural folding used only for grouping evidence."""
    w = _low(word)
    if w.endswith("'s"):
        w = w[:-2]
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith(("sses", "shes", "ches", "xes")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        return w[:-1]
    return w


def _nodet_key(lows: Sequence[str]) -> str:
    """Key with interior determiners removed — mirrors the extractor's own
    interior-determiner stripping so extractor overlap is detected correctly."""
    toks = list(lows)
    if len(toks) > 2:
        toks = [toks[0]] + [t for t in toks[1:-1] if t not in STRIP_INTERIOR] + [toks[-1]]
    return " ".join(toks)


def _boundary_regex(needle_cf: str) -> "re.Pattern[str]":
    """Literal match that cannot start/end inside a word or hyphenated word."""
    return re.compile(
        r"(?<![^\W_])(?<![^\W_][\-'\u2019])" + re.escape(needle_cf)
        + r"(?![^\W_])(?![\-'\u2019][^\W_])"
    )


def _verify_literal_span(phrase: str, *, text: str = "", html: str = "",
                         title: str = "") -> bool:
    """True only when ``phrase`` occurs literally (case-insensitive, whitespace
    normalised, WORD-BOUNDARY aware) in the title, text or visible HTML.

    Discovery-stage eligibility only; not a Guard/Scorer decision.
    (The earlier version used a bare substring test, so "art" matched "start".)
    """
    needle = _normalize_span_text(phrase)
    if not needle:
        return False
    rx = _boundary_regex(needle.casefold())
    for part in (_normalize_span_text(title), _normalize_span_text(text),
                 _html_to_visible_text(html)):
        if part and rx.search(part.casefold()):
            return True
    return False


def _find_literal_positions(phrase: str, *, surface: str) -> Dict[str, Any]:
    """Word-boundary-aware occurrence recovery against the discovery surface.

    ``first_position`` may legitimately be 0 (the earlier ``... or -1`` bug is
    gone because we never coerce falsy values)."""
    needle = _normalize_span_text(phrase)
    if not needle or not surface:
        return {"first_position": -1, "all_positions": [], "occurrence_count": 0}
    positions = [m.start() for m in _boundary_regex(needle.casefold()).finditer(surface.casefold())]
    return {
        "first_position": positions[0] if positions else -1,
        "all_positions": positions,
        "occurrence_count": len(positions),
    }


def _new_component_diagnostics(component: str) -> Dict[str, Any]:
    return {
        "component": str(component or "").strip(),
        "proposed": 0,
        "literal_verified": 0,
        "rejected_nonliteral": 0,
        "exact_span_failures": 0,
        "exact_span_failure_examples": [],
        "rejected_structural": 0,
        "overlap_with_extractor": 0,
        "duplicate_within_component": 0,
        "reinspected_existing": 0,
        "truncated_by_limit": 0,
        "net_new": 0,
        "emitted": 0,
        "capability_counts": {},
        "errors": [],
    }


def _build_discovery_candidate(*, phrase: str, component: str, capability: str = "",
                               section_id: str = "", doc_id: str = "", snippet: str = "",
                               intelligence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The ONE canonical output shape shared by all six components."""
    comp = str(component or "").strip()
    return {
        "phrase": str(phrase or ""),
        "source_type": "phrase_discovery",
        "section_id": str(section_id or "").strip(),
        "doc_id": str(doc_id or "").strip(),
        "snippet": str(snippet or ""),
        "provenance": {
            "origin": "phrase_discovery",
            "component": comp,
            "capability": str(capability or ""),
            "engine_version": ENGINE_VERSION,
        },
        "discovery_intelligence": {"component": comp, **dict(intelligence or {})},
    }


# ---------------------------------------------------------------------------
# Document model (built ONCE per call and shared by every component).
# ---------------------------------------------------------------------------

class _Token:
    __slots__ = ("i", "text", "low", "ls", "le", "tag", "cap", "acronym", "numeric")

    def __init__(self, i: int, text: str, ls: int, le: int) -> None:
        self.i, self.text, self.ls, self.le = i, text, ls, le
        self.low = _low(text)
        self.tag = "X"
        letters = [c for c in text if c.isalpha()]
        self.cap = bool(letters) and text[0].isupper()
        core = letters[:-1] if (len(letters) >= 3 and letters[-1] == "s") else letters
        self.acronym = (len(core) >= 2 and all(c.isupper() for c in core)
                        and text not in _ACRONYM_EXCLUDE)
        self.numeric = any(c.isdigit() for c in text)


class _Sentence:
    __slots__ = ("index", "block", "local", "text", "start", "end", "tokens",
                 "lows", "role", "level", "section_id", "section", "np_units",
                 "np_of_units", "singles", "by_start", "by_end", "_signals")

    def __init__(self) -> None:
        self._signals = None


class _Block:
    __slots__ = ("index", "kind", "start", "end", "sentences")


class _Section:
    __slots__ = ("index", "heading", "level", "parent", "stems", "sentences")


class _Span:
    """A literal token span inside one sentence."""
    __slots__ = ("sent", "s", "e", "kind", "lows", "key", "content",
                 "head_key", "core_key")

    def __init__(self, sent: _Sentence, s: int, e: int, kind: str) -> None:
        self.sent, self.s, self.e, self.kind = sent, s, e, kind
        self.lows = tuple(t.low for t in sent.tokens[s:e])
        self.key = " ".join(self.lows)
        self.content = tuple(w for w in self.lows
                             if w not in FUNCTION_WORDS and w not in _QUANTIFIERS)
        self.head_key = _stem(self.lows[-1]) if self.lows else ""
        if len(self.content) >= 2 and self.content[-1] == self.lows[-1]:
            self.core_key = self.content[-2] + " " + _stem(self.content[-1])
        else:
            self.core_key = self.head_key

    @property
    def length(self) -> int:
        return self.e - self.s


def _refine_tags(lows: List[str], tags: List[str],
                 boundary_after: Optional[List[bool]] = None,
                 role: str = "body", caps: Optional[List[bool]] = None) -> List[str]:
    """Closed-class context refinements on top of the extractor's tagger.

    ``boundary_after[i]`` is True when token i ends the sentence or is followed
    by punctuation (a clause boundary)."""
    n = len(lows)
    out = list(tags)
    if boundary_after is None or len(boundary_after) != n:
        boundary_after = [i == n - 1 for i in range(n)]
    for i, w in enumerate(lows):
        if w.endswith("n't") or w == "cannot":
            out[i] = "AUX"
        elif w in _EXTRA_PREPOSITIONS:
            out[i] = "ADP"
        elif i > 0 and lows[i - 1] in _BE_FORMS and (w.endswith("ed") or w.endswith("en")) and len(w) > 4 \
                and not (i + 1 < n and tags[i + 1] == "NOUN"):
            out[i] = "VERB"   # passive participle ("is caused by", "are certified against")
    for i in range(n):
        w, t = lows[i], out[i]
        if t in ("DET", "ADP", "CONJ", "PRON", "AUX", "NUM"):
            continue
        j = i - 1
        while j >= 0 and (lows[j] == "not" or lows[j] in PARTICLES_DEGREE
                          or _spe._is_adverb_ly(lows[j])):
            j -= 1
        prev = lows[j] if j >= 0 else None
        prev_tag = out[j] if j >= 0 else None
        nxt = lows[i + 1] if i + 1 < n else None
        nxt_tag = out[i + 1] if i + 1 < n else None
        # modal / do-support + verb ("can mitigate", "does reduce")
        if prev is not None and prev_tag == "AUX" and j > 0 and (
                prev in _MODALS or prev.endswith("n't")):
            if not _spe._is_gerund(w):
                out[i] = "VERB"
                continue
        if prev in _DO_AUX and prev_tag == "AUX" and j > 0 and (
                w in ALL_VERB_LEMMAS or w.endswith(("ize", "ify"))):
            out[i] = "VERB"
            continue
        # infinitive "to" + known/morphological verb
        if i > 0 and lows[i - 1] == "to" and (w in ALL_VERB_LEMMAS or w.endswith(("ize", "ify"))):
            out[i] = "VERB"
            continue
        prev_imm_tag = out[i - 1] if i > 0 else None
        # Restore a post-nominal participle demoted by nominalization.
        # Generic pattern: "liquid used in systems", "methods developed for testing".
        if t == "NOUN" and (w.endswith("ed") or w.endswith("en")) and len(w) >= 4 \
                and i > 0 and out[i - 1] in ("NOUN", "ADJ") \
                and nxt_tag == "ADP" and not boundary_after[i]:
            out[i] = "VERB"
            continue
        # noun + X-s / X-ed + determiner  => finite verb ("infrastructure mitigates the")
        if (prev_imm_tag in ("NOUN", "NUM") and nxt is not None
                and (nxt in _ARTICLES or nxt in _POSSESSIVE_DETS or nxt in ("this", "these"))):
            if (w.endswith("s") and not w.endswith(("ss", "us", "is", "'s")) and len(w) > 3) \
                    or (w.endswith("ed") and len(w) > 4):
                out[i] = "VERB"
                continue
        if prev_imm_tag in ("NOUN", "NUM") and w.endswith(("izes", "ifies", "ized", "ified")) \
                and nxt_tag in ("NOUN", "ADJ", "DET"):
            out[i] = "VERB"
            continue
        # clause-final bare verb lemma after a nominal, once the clause already
        # has its finite verb => it is the NP head ("supports ... application design")
        if (t == "VERB" and (w in ALL_VERB_LEMMAS or not w.endswith(("s", "ed", "ing")))
                and not _spe._is_gerund(w) and i > 1
                and out[i - 1] in ("NOUN", "ADJ") and lows[i - 1] not in FUNCTION_WORDS
                and (boundary_after[i] or (nxt is not None and (nxt in PREPOSITIONS or nxt in CONJUNCTIONS)))
                and any(out[q] == "VERB" and lows[q] not in AUX_VERBS for q in range(0, i - 1))):
            out[i] = "NOUN"
            continue
        # participial modifier before a noun ("distributed systems", "track returned merchandise") => ADJ
        if t == "VERB" and (w.endswith("ed") or w.endswith("en")) and len(w) > 4 \
                and (nxt_tag in ("NOUN", "ADJ") or (nxt is not None and _spe._is_gerund(nxt))) \
                and (i == 0 or boundary_after[i - 1] or out[i - 1] in ("DET", "ADP", "CONJ", "ADJ", "NUM", "VERB")
                     or lows[i - 1] in PREPOSITIONS) and (i == 0 or lows[i - 1] not in AUX_VERBS):
            out[i] = "ADJ"
    return _refine_clauses(lows, out, boundary_after, role, caps or [False] * n)


def _closed_class_tag(w: str, tag: str) -> str:
    """Closed classes are fully reliable; tagger output is not."""
    if w in _MODALS or w in AUX_VERBS or w.endswith("n't"):
        return "AUX"
    if tag == "AUX":
        return "NOUN"          # e.g. NLTK tagging "overnight" as MD
    if w == "to" or w in _EXTRA_PREPOSITIONS:
        return "ADP"
    if w in DETERMINERS and tag not in ("PRON",):
        return "DET"
    if w in CONJUNCTIONS:
        return "CONJ"
    if w in PREPOSITIONS and w not in ("like", "up", "down", "out", "off", "over"):
        return "ADP"
    if w in _PERSONAL_PRONOUNS:
        return "PRON"
    return tag


_CLAUSE_PUNCT_RE = re.compile(r"[,;:!?.\u2014\u2013]|\s-\s")


def clause_boundaries(text: str, spans: Sequence[Tuple[int, int]]) -> List[bool]:
    """Per token: True when a CLAUSE boundary follows it (sentence end or
    , ; : ! ? . dashes). Brackets, slashes and hyphens are not clause breaks
    ("401(k) plan", "and/or"). Shared with the Smart Phrase Extractor."""
    n = len(spans)
    return [i == n - 1 or bool(_CLAUSE_PUNCT_RE.search(text[spans[i][1]:spans[i + 1][0]]))
            for i in range(n)]


def _is_bare_lemma_verb(w: str) -> bool:
    return w in ALL_VERB_LEMMAS and not _spe._is_gerund(w) and w not in _spe._ING_ED_NOUNS


def _refine_clauses(lows: List[str], out: List[str], boundary_after: List[bool], role: str,
                    caps: List[bool]) -> List[str]:
    """Clause-scoped refinements using only closed-class evidence.

    * A bare verb lemma inside a noun compound ("Load rating determines",
      "safe live load capacity", "Free return shipping improves") is a noun
      when the clause already has a real verb anchor elsewhere.
    * "to X and|the|a" => X is an infinitive verb; a word coordinated with it
      ("to hear and manipulate individual sounds") is a verb too.
    * A verbless body clause almost always hides an unknown finite verb; its
      first -s/-ed word right after a nominal is marked as that verb, so it
      breaks the noun run instead of gluing subject and object together.
    """
    n = len(lows)
    clauses: List[List[int]] = [[]]
    for i in range(n):
        if lows[i] in _CLAUSE_SPLIT and clauses[-1]:
            clauses.append([])
        clauses[-1].append(i)
        if boundary_after[i] and i < n - 1:
            clauses.append([])
    # infinitives / coordinated verbs
    for i in range(1, n - 1):
        if lows[i - 1] == "to" and out[i] == "NOUN" and not boundary_after[i] and \
                (lows[i + 1] in ("and", "or") or lows[i + 1] in _ARTICLES or lows[i + 1] in _POSSESSIVE_DETS):
            out[i] = "VERB"
    for i in range(2, n - 1):
        if lows[i - 1] in ("and", "or") and out[i - 2] == "VERB" and out[i] == "NOUN" \
                and not _spe._is_gerund(lows[i]) and out[i + 1] in ("ADJ", "NOUN", "DET") \
                and i >= 3 and lows[i - 3] == "to":
            out[i] = "VERB"
    for clause in clauses:
        if not clause:
            continue
        def is_anchor(q: int) -> bool:
            w = lows[q]
            if out[q] == "AUX" and w in AUX_VERBS:
                return True
            return out[q] == "VERB" and not _is_bare_lemma_verb(w) and not _spe._is_gerund(w)
        # Plural nominal head before an independent bare verb:
        # "interest rates cause", "investment returns depend", "water flows shape".
        for q in clause[:-1]:
            if out[q] == "VERB" and _is_plural_like(lows[q]) and lows[q] not in _CATENATIVE and q > clause[0] \
                    and out[q - 1] in ("NOUN", "ADJ", "NUM") and _is_bare_lemma_verb(lows[q + 1]):
                out[q] = "NOUN"
        # Plural nominal subject + catenative bare verb + bare complement verb:
        # restore the catenative when a tagger has treated it as a noun.
        # Generic shape: "security controls help reduce", "systems help prevent".
        for q in clause[1:-1]:
            if out[q] in ("NOUN", "VERB") and lows[q] in _CATENATIVE                     and out[q - 1] in ("NOUN", "ADJ", "NUM")                     and _is_plural_like(lows[q - 1])                     and _is_bare_lemma_verb(lows[q + 1]):
                out[q] = "VERB"
                if out[q + 1] == "NOUN" and _is_bare_lemma_verb(lows[q + 1]):
                    out[q + 1] = "VERB"
        anchors = [q for q in clause if is_anchor(q)]
        imperative = bool(clause) and out[clause[0]] == "VERB" and _is_bare_lemma_verb(lows[clause[0]])
        for q in clause:
            if out[q] != "VERB" or not _is_bare_lemma_verb(lows[q]) or q + 1 >= n:
                continue
            if q > 0 and (lows[q - 1] == "to" or lows[q - 1] in _MODALS or lows[q - 1] in _DO_AUX):
                continue
            if lows[q] in _CATENATIVE or (q > 0 and _is_plural_like(lows[q - 1])):
                continue   # "feeders help owners", "teams use ..." — left to clause resolution
            nxt_ok = (out[q + 1] == "NOUN" or (out[q + 1] == "ADP" and lows[q + 1] != "to")) \
                and not boundary_after[q]
            if not nxt_ok:
                continue
            if q > 0 and out[q - 1] in ("NOUN", "ADJ") and lows[q - 1] not in FUNCTION_WORDS \
                    and not _is_plural_like(lows[q - 1]):
                out[q] = "NOUN"   # singular subjects never take a bare verb: "remote work policy"
                continue
            if q > 0 and out[q - 1] == "VERB" and _is_bare_lemma_verb(lows[q - 1]) \
                    and lows[q - 1] not in _CATENATIVE and q + 2 <= n:
                out[q] = "NOUN"   # "use return authorization numbers"
                continue
            prev_nominal = q > 0 and out[q - 1] in ("NOUN", "ADJ", "DET", "NUM") and lows[q - 1] != "to"
            later_anchor = any(a > q + 1 for a in anchors)
            earlier_anchor = any(a < q for a in anchors)
            if (later_anchor and ((q == clause[0] and not imperative) or prev_nominal)) or (earlier_anchor and prev_nominal) \
                    or (imperative and q != clause[0] and prev_nominal):
                out[q] = "NOUN"
        if role not in ("body", "list_item") or len(clause) < 2:
            continue
        _resolve_clause_verb(lows, out, clause, boundary_after, caps)
    # Final reduced-participle restoration after clause resolution.
    # Generic: "liquid used in systems", "methods developed for testing".
    for i, w in enumerate(lows):
        if out[i] == "NOUN" and _spe._is_inflected_verb(w) and w.endswith(("ed", "en")) and len(w) >= 4 \
                and i > 0 and i + 1 < n and out[i - 1] in ("NOUN", "ADJ") \
                and out[i + 1] == "ADP" and not boundary_after[i]:
            out[i] = "VERB"
    return out


def _is_plural_like(w: str) -> bool:
    return (w in ("they", "we", "you", "i", "people")
            or (w.endswith("s") and not w.endswith(("ss", "us", "is", "'s")) and len(w) > 3))


_PREP_TO_COLLOCATIONS = frozenset({
    "leads", "lead", "led", "contributes", "contribute", "contributed", "due", "according",
    "similar", "related", "prior", "thanks", "compared", "access", "exposure", "addition",
    "close", "next", "linked", "applies", "apply", "refers", "refer", "belongs", "belong",
    "responds", "respond", "equal", "relative", "subject", "vulnerable", "sensitive",
    "resistant", "adjacent", "attributable", "exposed", "committed", "devoted", "limited",
})


def _resolve_clause_verb(lows: List[str], out: List[str], clause: List[int],
                         boundary_after: List[bool], caps: Optional[List[bool]] = None) -> None:
    """One finite verb per clause (tagger-agnostic safeguard).

    Every VERB-tagged token and every hidden-verb candidate is scored from
    morphology and closed-class context; the winner is the clause verb.
    Remaining VERB tags that sit inside noun compounds (subject heads, object
    modifiers) are demoted, which repairs noisy taggers ("ecosystems/VBZ face",
    "improves/NNS crust/VBP") without any domain vocabulary."""
    n = len(lows)
    aux_pos = next((q for q in clause if out[q] == "AUX" and lows[q] in AUX_VERBS), None)
    if aux_pos is not None:
        main = None  # an auxiliary already anchors the clause
    else:
        scores: Dict[int, float] = {}
        for q in clause:
            w = lows[q]
            if w in FUNCTION_WORDS or _spe._is_gerund(w) or out[q] in ("DET", "ADP", "CONJ", "PRON", "NUM"):
                continue
            if q > 0 and (lows[q - 1] == "to" or lows[q - 1] in _MODALS or lows[q - 1] in _DO_AUX):
                continue
            if q > 0 and (out[q - 1] in ("DET", "ADP") or lows[q - 1] in _POSSESSIVE_DETS
                          or lows[q - 1] in DETERMINERS):
                continue   # "the department", "of labor": never a finite verb
            if caps and q > 0 and caps[q]:
                continue   # mid-sentence capital: part of a name, not a verb
            # Preserve a resolved plural nominal head before an independent bare verb.
            # Generic structural shape: plural nominal head + bare finite verb.
            if out[q] == "NOUN" and q > clause[0] and _is_plural_like(w)                     and out[q - 1] in ("NOUN", "ADJ", "NUM") and q + 1 < n                     and _is_bare_lemma_verb(lows[q + 1]):
                continue
            if out[q] == "ADJ" and (w.endswith("ed") or w.endswith("en")) and q + 1 < n \
                    and out[q + 1] in ("NOUN", "ADJ") and not boundary_after[q]:
                continue   # participial modifier ("reduced calcification rates")
            pq = q - 1   # subject side, looking past adverbs ("season usually peaks")
            while pq > clause[0] and (out[pq] == "ADV" or _spe._is_adverb_ly(lows[pq])
                                      or lows[pq] in PARTICLES_DEGREE):
                pq -= 1
            prev = lows[pq] if pq >= 0 else ""
            prev_tag = out[pq] if pq >= 0 else ""
            nxt = lows[q + 1] if q + 1 < n else ""
            nxt_tag = out[q + 1] if q + 1 < n else ""
            adj_modifies = nxt_tag == "ADJ" and q + 2 < n and out[q + 2] in ("NOUN", "ADJ") \
                and not boundary_after[q + 1]
            strong = bool(nxt) and not boundary_after[q] and (
                nxt_tag in ("DET", "ADP", "ADV", "PRON") or adj_modifies or nxt in COMPARATIVES
                or _spe._is_adverb_ly(nxt) or _spe._is_gerund(nxt)
                or (len(nxt) > 5 and nxt.endswith(_ADJ_SUFFIXES)))
            suffixed = (w.endswith("s") and not w.endswith(("ss", "us", "is", "'s")) and len(w) > 3) or \
                (w.endswith("ed") and len(w) > 4)
            plural_prev = _is_plural_like(prev)
            score = 0.0
            if out[q] == "VERB":
                score += 1.5
            if _spe._is_inflected_verb(w):
                score += 3.0
            elif w in ALL_VERB_LEMMAS and not suffixed:
                score += 0.5
            if q == clause[0]:
                score -= 1.0 if out[q] != "VERB" else 0.0
            if not suffixed and plural_prev:
                score += 1.0
            if out[q] == "ADJ" and not suffixed and plural_prev and q + 1 < n and out[q + 1] in ("ADP", "DET", "ADV"):
                score += 1.5   # adjective with no noun to modify, after a plural subject: a verb ("requirements vary by")
            if suffixed and q > 0 and prev_tag in ("NOUN", "ADJ", "NUM") and not plural_prev:
                score += 1.0
                # Unknown finite -s/-ed verb between a singular nominal subject and its object.
                # Generic pattern: "fluid transfers pressure", "device measures temperature".
                if nxt_tag in ("NOUN", "ADJ", "DET") and not boundary_after[q]:
                    score += 2.0
            if not suffixed and q > 0 and prev_tag in ("NOUN", "NUM") and not plural_prev \
                    and prev not in _PERSONAL_PRONOUNS:
                score -= 2.0   # a singular noun never takes a bare verb ("blossom season usually")
            if strong:
                score += 1.0
            elif nxt_tag == "NOUN" and q > 0 and out[q - 1] in ("NOUN", "ADJ") and not plural_prev and not suffixed:
                score -= 1.0   # sandwiched between nominals: compound-like
            if q + 1 >= n or boundary_after[q]:
                score -= 2.0   # finite verbs rarely end a clause ("meal schedules.")
            if suffixed and nxt in ALL_VERB_LEMMAS and not boundary_after[q]:
                score -= 1.0   # plural subject before a base verb ("flows shape", "frames support")
            if score > 0:
                scores[q] = score
        after_conj = clause[0] > 0 and lows[clause[0] - 1] in ("and", "or") or lows[clause[0]] in ("and", "or")
        threshold = 3.0 if after_conj else 1.5
        strong_scores = {q: v for q, v in scores.items() if v >= threshold}
        if not strong_scores:
            # Verbless body clause: accept the best weak candidate, preferring
            # -s/-ed forms after a singular nominal ("Labor oversees state ...").
            has_verb = any(out[q] == "VERB" and not _spe._is_gerund(lows[q]) for q in clause)
            if after_conj or has_verb or len(clause) < 4:
                return
            weak = {q: v for q, v in scores.items() if v >= 1.0}
            if not weak:
                return
            strong_scores = weak
        main = max(strong_scores, key=lambda q: (strong_scores[q], -q))
        inflected = sorted(q for q in strong_scores if _spe._is_inflected_verb(lows[q]) and q < main)
        if inflected and _spe._is_inflected_verb(lows[main]):
            first = inflected[0]
            if all(out[k] in ("NOUN", "ADJ", "DET", "NUM") for k in range(first + 1, main)):
                main = first   # "improves conversion rates for": the later -s word is in the object
        out[main] = "VERB"
        if main > 0 and main - 1 >= clause[0] and lows[main - 1] not in COMPARATIVES \
                and not _spe._is_adverb_ly(lows[main - 1]) and lows[main - 1] not in FUNCTION_WORDS and (
                    out[main - 1] == "ADJ" or (out[main - 1] == "VERB" and _spe._is_gerund(lows[main - 1]))):
            out[main - 1] = "NOUN"   # subject head before the verb ("wheat flour/JJ ferments", "proofing improves")
    # "leads to foundation damage": prepositional "to" + VERB-tagged noun
    for q in clause:
        if lows[q] in _PREP_TO_COLLOCATIONS and q + 2 < n and lows[q + 1] == "to" and \
                out[q + 2] == "VERB" and not _spe._is_gerund(lows[q + 2]) and \
                q + 3 < n and out[q + 3] in ("NOUN", "ADJ"):
            out[q + 2] = "NOUN"
    for q in clause:
        if q == main or out[q] != "VERB" or _spe._is_gerund(lows[q]) or lows[q] in _CATENATIVE:
            continue
        if q > 0 and (lows[q - 1] in ("to", "and", "or") or lows[q - 1] in _MODALS
                      or lows[q - 1] in _DO_AUX or lows[q - 1] in AUX_VERBS):
            continue
        prev_tag = out[q - 1] if q > 0 else ""
        nxt_tag = out[q + 1] if q + 1 < n else ""
        if main is not None and q == main - 1 and prev_tag in ("NOUN", "ADJ", "NUM"):
            out[q] = "NOUN"          # subject head before the verb ("reef ecosystems face")
        elif main is not None and q == main + 1 and lows[main] in _CATENATIVE                 and _is_bare_lemma_verb(lows[q]):
            continue            # preserve catenative bare-verb complement
        elif main is not None and q == main + 1 and nxt_tag == "NOUN":
            out[q] = "NOUN"          # object modifier after the verb ("improves crust color")
        elif prev_tag in ("NOUN", "ADJ", "NUM") and nxt_tag == "NOUN" and main is not None:
            out[q] = "NOUN"          # inside a compound elsewhere in the clause
        elif prev_tag in ("NOUN", "ADJ", "NUM") and (nxt_tag in ("ADP", "CONJ", "") or q + 1 >= n
                                                      or boundary_after[q]) \
                and lows[q].endswith("s") and not lows[q].endswith(("ss", "us", "is", "'s")) \
                and (main is not None and q > main):
            out[q] = "NOUN"          # one finite verb per clause: "improves conversion rates for"
        elif main is None and aux_pos is not None and q < aux_pos and prev_tag in ("NOUN", "ADJ", "NUM") \
                and not _is_plural_like(lows[q - 1]) and nxt_tag in ("ADP", "NOUN") and lows[q + 1] != "to":
            out[q] = "NOUN"          # subject noun before the auxiliary: "contribution limit for ... was"


class _ExtractorIndex:
    """Normalised view of the Smart Phrase Extractor candidates."""

    def __init__(self, candidates: List[Dict[str, Any]], model: "_DocumentModel") -> None:
        self.keys: Dict[str, str] = {}
        self.nodet: Dict[str, str] = {}
        self.cores: Dict[str, int] = {}
        self.heads: Dict[str, int] = {}
        self.literal_seqs: List[Tuple[Tuple[str, ...], str, Dict[str, Any]]] = []
        self.nonliteral: List[str] = []
        self.total = len(candidates)
        for cand in candidates:
            phrase = _normalize_span_text(cand.get("phrase", ""))
            lows = tuple(_lows_of(phrase))
            if not lows:
                continue
            key = " ".join(lows)
            if key in self.keys:
                continue
            self.keys[key] = phrase
            self.nodet.setdefault(_nodet_key(lows), phrase)
            content = [w for w in lows if w not in FUNCTION_WORDS]
            if content:
                hk = _stem(content[-1])
                self.heads[hk] = self.heads.get(hk, 0) + 1
                if len(content) >= 2:
                    ck = content[-2] + " " + hk
                    self.cores[ck] = self.cores.get(ck, 0) + 1
            if model.verify_literal(phrase):
                self.literal_seqs.append((lows, phrase, cand))
            else:
                self.nonliteral.append(phrase)

    def is_known(self, lows: Sequence[str]) -> bool:
        key = " ".join(lows)
        return key in self.keys or _nodet_key(lows) in self.nodet or key in self.nodet

    def contained_in(self, lows: Sequence[str], limit: int = 5) -> List[str]:
        out: List[str] = []
        L = len(lows)
        for seq, phrase, _ in self.literal_seqs:
            n = len(seq)
            if n >= L:
                continue
            for k in range(L - n + 1):
                if tuple(lows[k:k + n]) == seq:
                    out.append(phrase)
                    break
            if len(out) >= limit:
                break
        return out


class _DocumentModel:
    def __init__(self, *, text: str, html: str, title: str,
                 extractor_candidates: List[Dict[str, Any]]) -> None:
        self.text, self.html, self.title = text, html, title
        self.blocks: List[_Block] = []
        self.sentences: List[_Sentence] = []
        self.sections: List[_Section] = []
        self.surface = ""
        self.structure_mode = "empty"
        self._search_cf = [p.casefold() for p in (
            _normalize_span_text(title), _normalize_span_text(text),
            _html_to_visible_text(html)) if p]
        self._verify_cache: Dict[str, bool] = {}
        self._pos_cache: Dict[str, Dict[str, Any]] = {}
        self._build_structure()
        self._analyse_sentences()
        self._build_sections()
        self.extractor = _ExtractorIndex(extractor_candidates, self)
        self._build_concepts()
        self._build_entities()

    # ------------------------------------------------------------ structure
    @staticmethod
    def _clean(value: str, from_html: bool) -> str:
        return _normalize_span_text(html_lib.unescape(value) if from_html else value)

    @staticmethod
    def _looks_like_heading(line: str, si: int, n_sents: int, pi: int, n_paras: int) -> bool:
        s = line.strip()
        if not s or s[-1] in ".!?;,:\"'":
            return False
        toks = _TOKEN_RE.findall(s)
        if not (1 <= len(toks) <= 12):
            return False
        first_alpha = next((c for c in s if c.isalpha()), "")
        if not first_alpha or not first_alpha.isupper():
            return False
        return si == 0 and (n_sents > 1 or pi + 1 < n_paras)

    def _build_structure(self) -> None:
        items: List[Dict[str, Any]] = []
        title = _normalize_span_text(self.title)
        if title:
            items.append({"kind": "title", "sents": [(title, "title_0", "title", 0)]})
        html = self.html or ""
        html_has_paras = False
        if html.strip():
            heads, lis, paras = [], [], []
            for m in _spe.H_RE.finditer(html):
                txt = _spe.strip_tags(m.group(2))
                if txt:
                    heads.append((m.start(), int(m.group(1)), txt))
            for m in _spe.LI_RE.finditer(html):
                txt = _spe.strip_tags(m.group(1))
                if txt:
                    lis.append((m.start(), m.end(), txt))
            for m in _spe.P_RE.finditer(html):
                txt = _spe.strip_tags(m.group(1))
                if txt:
                    paras.append((m.start(), m.end(), txt))
            ordered: List[Tuple[int, Dict[str, Any]]] = []
            for k, (pos, lvl, txt) in enumerate(heads):
                sid = f"heading_h{lvl}_{k}"
                ordered.append((pos, {"kind": "heading",
                                      "sents": [(self._clean(txt, True), sid, "heading", lvl)]}))
            nh = len(heads)
            for j, (pos, _end, txt) in enumerate(lis):
                sid = f"list_item_{nh + j}"
                sents = [(self._clean(s, True), sid, "list_item", 0)
                         for s in _spe.split_sentences(txt)]
                ordered.append((pos, {"kind": "list_item", "sents": [x for x in sents if x[0]]}))
            for pi, (pos, end, txt) in enumerate(paras):
                if any(ls <= pos and end <= le for ls, le, _ in lis):
                    continue  # <p> nested in <li>: the list item already carries it
                sents = [(self._clean(s, True), f"p{pi}_s{si}", "body", 0)
                         for si, s in enumerate(_spe.split_sentences(txt))]
                ordered.append((pos, {"kind": "paragraph", "sents": [x for x in sents if x[0]]}))
            ordered.sort(key=lambda x: x[0])
            items.extend(b for _, b in ordered)
            html_has_paras = bool(paras)
            self.structure_mode = "html" if html_has_paras else ("html_structure" if ordered else "empty")
        if not html_has_paras and (self.text or "").strip():
            # Mirrors extract_paragraphs(html=..., text=...) exactly.
            paras = _spe.extract_paragraphs(html=html, text=self.text)
            n_paras = len(paras)
            for pi, para in enumerate(paras):
                raw = _spe.split_sentences(para)
                lines = {ln.strip() for ln in para.split("\n") if ln.strip()}
                sents = []
                for si, s in enumerate(raw):
                    clean = self._clean(s, False)
                    if not clean:
                        continue
                    role, level = "body", 0
                    md = _MD_HEADING_RE.match(s)
                    if md:
                        role, level = "heading", len(md.group(1))
                    elif _BULLET_RE.match(s) and s.strip() in lines:
                        role = "list_item"
                    elif s.strip() in lines and self._looks_like_heading(s, si, len(raw), pi, n_paras):
                        role, level = "heading", 2
                    sents.append((clean, f"p{pi}_s{si}", role, level))
                if sents:
                    items.append({"kind": "paragraph", "sents": sents})
            self.structure_mode = ("html_structure+text_body"
                                   if self.structure_mode == "html_structure" else "text")

        parts: List[str] = []
        pos = 0
        for item in items:
            if not item["sents"]:
                continue
            if parts:
                parts.append("\n\n")
                pos += 2
            blk = _Block()
            blk.index, blk.kind, blk.start, blk.sentences = len(self.blocks), item["kind"], pos, []
            for li, (stext, sid, role, level) in enumerate(item["sents"]):
                if li > 0:
                    parts.append(" ")
                    pos += 1
                sent = _Sentence()
                sent.index, sent.block, sent.local = len(self.sentences), blk.index, li
                sent.text, sent.start = stext, pos
                sent.role, sent.level, sent.section_id = role, level, sid
                parts.append(stext)
                pos += len(stext)
                sent.end = pos
                blk.sentences.append(sent.index)
                self.sentences.append(sent)
            blk.end = pos
            self.blocks.append(blk)
        self.surface = "".join(parts)

    # ------------------------------------------------------------ tokens/tags
    def _analyse_sentences(self) -> None:
        self._first_index: Dict[str, List[Tuple[int, int]]] = {}
        for sent in self.sentences:
            toks = [_Token(i, m.group(0), m.start(), m.end())
                    for i, m in enumerate(_TOKEN_RE.finditer(sent.text))]
            sent.tokens = toks
            sent.lows = [t.low for t in toks]
            if toks:
                # Surface-cased tokens give NLTK (when present) far better tags;
                # lexicon-based passes then run on lowercase forms.
                raw = _spe.pos_tag([t.text for t in toks])
                nlp = _spe._get_spacy()
                if nlp is not None:
                    doc = nlp(sent.text)
                    spacy_toks = [st for st in doc if _TOKEN_RE.fullmatch(st.text)]
                    aligned = []
                    alignment_ok = True
                    for tok in toks:
                        parts = [st for st in spacy_toks
                                 if st.idx >= tok.ls and st.idx + len(st.text) <= tok.le]
                        if not parts:
                            alignment_ok = False
                            break
                        joined = "".join(st.text for st in parts)
                        target = re.sub(r"[-\u2010-\u2015]", "", tok.text)
                        if joined != target:
                            alignment_ok = False
                            break
                        head = parts[-1]
                        aligned.append((tok.text,
                                        _spe._coarsen_ptb(head.tag_) if head.tag_
                                        else _spe._spacy_coarse(head)))
                    if alignment_ok and len(aligned) == len(toks):
                        raw = aligned
                raw = [(low, _closed_class_tag(low, tag)) for low, (_, tag) in zip(sent.lows, raw)]
                tagged = _spe._nominalize_tags(raw)
                bnd = clause_boundaries(sent.text, [(t.ls, t.le) for t in toks])
                caps = [q > 0 and t.cap and not t.acronym for q, t in enumerate(toks)] \
                    if sent.role == "body" and not self._title_case_sentence(sent) else None
                tags = _refine_tags(sent.lows, [t for _, t in tagged], bnd, sent.role, caps)
                for tok, tag in zip(toks, tags):
                    tok.tag = tag
            for k, w in enumerate(sent.lows):
                self._first_index.setdefault(w, []).append((sent.index, k))
            self._build_units(sent)

    def joinable(self, sent: _Sentence, a: int, b: int) -> bool:
        gap = sent.text[sent.tokens[a].le:sent.tokens[b].ls]
        return bool(_JOINABLE_GAP_RE.match(gap))

    def gap(self, sent: _Sentence, a: int, b: int) -> str:
        return sent.text[sent.tokens[a].le:sent.tokens[b].ls]

    @staticmethod
    def head_tag(tok: _Token) -> Optional[str]:
        return None if tok.tag == "X" else tok.tag

    def _eligible(self, sent: _Sentence, k: int) -> bool:
        t = sent.tokens[k]
        w = t.low
        if w.endswith("n't") or w in _MODALS or w in _CLAUSE_WORDS:
            return False
        if not _spe._np_eligible(w, t.tag):
            return False
        if t.tag == "ADV" and w in PARTICLES_DEGREE:
            return False
        return True

    def _clausal_gerund(self, sent: _Sentence, a: int, b: int) -> bool:
        w = sent.tokens[a].low
        return (_spe._is_gerund(w) and w not in _spe._ING_ED_NOUNS and b - a >= 2 and a > 0
                and sent.tokens[a - 1].low in _GERUND_CLAUSE_TRIGGERS
                and self.joinable(sent, a - 1, a))

    def _trim(self, sent: _Sentence, a: int, b: int) -> Tuple[int, int]:
        toks = sent.tokens
        while a < b:
            t = toks[a]
            w = t.low
            if (w in LEADING_BAN or w in _QUANTIFIERS or w == "of"
                    or (t.tag == "VERB" and not _spe._is_gerund(w))
                    or (t.tag == "ADV" and not _spe._is_adverb_ly(w))
                    or self._clausal_gerund(sent, a, b)):
                a += 1
                continue
            break
        while b > a:
            t = toks[b - 1]
            w = t.low
            if (w in TRAILING_BAN or w in AUX_VERBS or w in PARTICLES_DEGREE
                    or _spe._is_adverb_ly(w) or w == "of"
                    or not _spe._head_is_noun_like(w, self.head_tag(t))):
                b -= 1
                continue
            break
        return a, b

    def is_clause_verb(self, tok: _Token) -> bool:
        return (tok.tag == "VERB" and not _spe._is_gerund(tok.low)
                and tok.low not in _spe._ING_ED_NOUNS)

    def coherent(self, sent: _Sentence, s: int, e: int, *,
                 allow_preps: Iterable[str] = (), allow_single: bool = False,
                 max_tokens: int = _MAX_NP_TOKENS, allow_articles: bool = False,
                 allow_conj: Iterable[str] = (), free_positions: Iterable[int] = (),
                 allow_leading_function: bool = False) -> bool:
        """Structural coherence of a literal span (discovery eligibility only)."""
        toks = sent.tokens
        n = e - s
        if n < 1 or n > max_tokens or s < 0 or e > len(toks):
            return False
        if n == 1 and not allow_single:
            return False
        preps, conj, free = set(allow_preps), set(allow_conj), set(free_positions)
        first, last = toks[s], toks[e - 1]
        if first.low in LEADING_BAN and not allow_leading_function and s not in free:
            return False
        if last.low in TRAILING_BAN or last.low in AUX_VERBS:
            return False
        if not _spe._head_is_noun_like(last.low, self.head_tag(last)):
            return False
        for k in range(s, e):
            t = toks[k]
            w = t.low
            if k > s and not self.joinable(sent, k - 1, k):
                return False
            if k in free:
                continue
            if w.endswith("n't") or w in _PERSONAL_PRONOUNS:
                return False
            if w in AUX_VERBS or w in _MODALS or w in _CLAUSE_WORDS:
                return False
            if s < k < e - 1:
                if w in PREPOSITIONS and w not in preps:
                    return False
                if w in CONJUNCTIONS and w not in conj:
                    return False
                if w in DETERMINERS and not (allow_articles and (w in _ARTICLES or w in _POSSESSIVE_DETS)):
                    return False
                if self.is_clause_verb(t):
                    return False
        content = [t for t in toks[s:e] if t.low not in FUNCTION_WORDS and t.low not in _QUANTIFIERS]
        if n >= 2 and len(content) < 2:
            return False
        if n == 1 and not content:
            return False
        if all(t.low in GENERIC_WEAK_HEADS or t.low in FUNCTION_WORDS for t in toks[s:e]):
            return False
        return True

    def _build_units(self, sent: _Sentence) -> None:
        toks = sent.tokens
        n = len(toks)
        runs: List[List[int]] = []
        cur: List[int] = []
        for k in range(n):
            if self._eligible(sent, k):
                if cur and not self.joinable(sent, k - 1, k):
                    runs.append(cur)
                    cur = []
                cur.append(k)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        sent.np_units, sent.np_of_units, sent.singles = [], [], []
        for run in runs:
            s0, e0 = run[0], run[-1] + 1
            parts: List[Tuple[int, int]] = []
            start = s0
            for k in range(s0, e0):
                if toks[k].low == "of":
                    parts.append((start, k))
                    start = k + 1
            parts.append((start, e0))
            trimmed: List[Optional[Tuple[int, int]]] = []
            for a, b in parts:
                ta, tb = self._trim(sent, a, b) if b > a else (a, a)
                trimmed.append((ta, tb) if tb > ta else None)
            for p in trimmed:
                if p is None:
                    continue
                a, b = p
                if b - a == 1:
                    if self.coherent(sent, a, b, allow_single=True):
                        sent.singles.append(_Span(sent, a, b, "single"))
                elif self.coherent(sent, a, b):
                    sent.np_units.append(_Span(sent, a, b, "np"))
            for i in range(len(trimmed) - 1):
                A, B = trimmed[i], trimmed[i + 1]
                if not A or not B:
                    continue
                if A[1] != parts[i][1] or B[0] != parts[i + 1][0] or A[1] - A[0] > 4:
                    continue
                if self.coherent(sent, A[0], B[1], allow_preps=_OF):
                    sent.np_of_units.append(_Span(sent, A[0], B[1], "np_of"))
        sent.by_start, sent.by_end = {}, {}
        for sp in sent.np_of_units + sent.np_units + sent.singles:
            sent.by_start.setdefault(sp.s, []).append(sp)
            sent.by_end.setdefault(sp.e, []).append(sp)

    # ------------------------------------------------------------ sections
    def _build_sections(self) -> None:
        root = _Section()
        root.index, root.heading, root.level, root.parent = 0, None, 0, None
        root.stems, root.sentences = [], []
        self.sections = [root]
        stack = [root]
        for sent in self.sentences:
            if sent.role == "title":
                root.heading = sent.index
                root.stems = self._content_stems(sent)
                sent.section = 0
                root.sentences.append(sent.index)
                continue
            if sent.role == "heading":
                level = sent.level or 2
                while len(stack) > 1 and stack[-1].level >= level:
                    stack.pop()
                sec = _Section()
                sec.index, sec.heading, sec.level = len(self.sections), sent.index, level
                sec.parent, sec.stems, sec.sentences = stack[-1].index, self._content_stems(sent), []
                self.sections.append(sec)
                stack.append(sec)
            sec = stack[-1]
            sent.section = sec.index
            sec.sentences.append(sent.index)

    @staticmethod
    def _content_stems(sent: _Sentence) -> List[str]:
        out: List[str] = []
        for t in sent.tokens:
            if t.low not in FUNCTION_WORDS and len(t.low) >= 3 and not t.numeric:
                st = _stem(t.low)
                if st not in out:
                    out.append(st)
        return out

    def heading_text(self, section_index: int) -> str:
        sec = self.sections[section_index]
        return self.sentences[sec.heading].text if sec.heading is not None else ""

    # ------------------------------------------------------------ concepts
    def _build_concepts(self) -> None:
        self.concepts: Dict[str, Dict[str, Any]] = {}
        self.heads: Dict[str, Dict[str, Any]] = {}
        for sent in self.sentences:
            for sp in sent.np_units + sent.singles:
                for index, key in ((self.concepts, sp.core_key), (self.heads, sp.head_key)):
                    rec = index.setdefault(key, {"key": key, "sentences": {}, "sections": {},
                                                 "blocks": {}, "roles": {}, "variants": {},
                                                 "occurrences": 0})
                    rec["sentences"][sent.index] = True
                    rec["sections"][sent.section] = True
                    rec["blocks"][sent.block] = True
                    rec["roles"][sent.role] = True
                    rec["occurrences"] += 1
                    if sp.kind == "np":
                        rec["variants"].setdefault(sp.key, sp)

    def _support(self, rec: Optional[Dict[str, Any]], extractor_hit: bool) -> Dict[str, Any]:
        if not rec:
            return {"salient": False, "strength": 0.0, "sentence_count": 0}
        sc = len(rec["sentences"])
        in_title = "title" in rec["roles"]
        in_heading = "heading" in rec["roles"]
        strength = (min(1.0, sc / 4.0) * 0.45 + 0.2 * in_title + 0.15 * in_heading
                    + 0.2 * extractor_hit)
        return {
            "salient": sc >= 2 or in_title or in_heading,
            "strength": round(min(1.0, strength), 4),
            "sentence_count": sc,
            "section_count": len(rec["sections"]),
            "in_title": in_title,
            "in_heading": in_heading,
            "extractor_support": extractor_hit,
        }

    def concept_support(self, core_key: str) -> Dict[str, Any]:
        return self._support(self.concepts.get(core_key),
                             core_key in self.extractor.cores or core_key in self.extractor.heads)

    def head_support(self, head_key: str) -> Dict[str, Any]:
        sup = self._support(self.heads.get(head_key), head_key in self.extractor.heads)
        if head_key in GENERIC_WEAK_HEADS or len(head_key) < 3 or any(c.isdigit() for c in head_key):
            sup["salient"] = False
        return sup

    def span_salient(self, sp: _Span) -> bool:
        return self.concept_support(sp.core_key)["salient"] or self.head_support(sp.head_key)["salient"]

    # ------------------------------------------------------------ entities
    def _title_case_sentence(self, sent: _Sentence) -> bool:
        content = [t for t in sent.tokens if t.low not in FUNCTION_WORDS and any(c.isalpha() for c in t.text)]
        if len(content) < 2:
            return False
        ratio = sum(1 for t in content if t.cap) / len(content)
        return ratio >= (0.6 if sent.role in ("title", "heading", "list_item") else 0.85)

    def _build_entities(self) -> None:
        self.entities: List[Dict[str, Any]] = []
        # Words that also occur in lowercase elsewhere are ordinary words when
        # they are capitalised only because they start a sentence ("Unlike").
        lowercase_words = {t.low for s_ in self.sentences for t in s_.tokens
                           if t.text.islower()}
        marker_words = {m[0] for m in _CONTRAST_NEXT + _DEFINITION_NEXT + _DEFINITION_PREV
                        + _SOURCE_INTRODUCERS + _EVIDENCE_MULTI} | _CONTRAST_CLAUSE | _CLAUSE_WORDS
        mid_caps: Dict[str, int] = {}
        raw: List[Dict[str, Any]] = []
        for sent in self.sentences:
            toks = sent.tokens
            n = len(toks)
            titleish = sent.role in ("title", "heading") or self._title_case_sentence(sent)
            k = 0
            while k < n:
                t = toks[k]
                if not (t.cap or t.acronym) or t.low in FUNCTION_WORDS:
                    k += 1
                    continue
                if k == 0 and not t.acronym and (t.low in lowercase_words or t.low in marker_words):
                    k += 1
                    continue
                s, e, j = k, k + 1, k + 1
                while j < n and self.joinable(sent, j - 1, j):
                    tj = toks[j]
                    if (tj.cap or tj.acronym) and tj.low not in FUNCTION_WORDS:
                        e, j = j + 1, j + 1
                    elif tj.numeric and not tj.cap:
                        e, j = j + 1, j + 1
                        break
                    elif (tj.low in _ENTITY_CONNECTORS and j + 1 < n and self.joinable(sent, j, j + 1)
                          and (toks[j + 1].cap or toks[j + 1].acronym)
                          and toks[j + 1].low not in FUNCTION_WORDS):
                        j += 1
                    else:
                        break
                # "and" may only join capitalised words inside ONE institutional
                # name ("Institute of Standards and Technology"), never two names.
                for q in range(s + 1, e - 1):
                    if toks[q].low == "and":
                        inner = [x.low for x in toks[s:e]]
                        joins_name = any(w in ("of", "for") for w in inner[:q - s]) or \
                            any(w in _INSTITUTION_HEADS for w in inner)
                        if not joins_name:
                            e = q
                            break
                k = max(e, k + 1)
                span_toks = toks[s:e]
                has_acronym = any(x.acronym for x in span_toks)
                if titleish:
                    # Title-cased text: capitalisation carries no entity signal;
                    # keep only acronym(+identifier) spans.
                    for q in range(s, e):
                        if toks[q].acronym:
                            qe = q + 1
                            if qe < e and toks[qe].numeric:
                                qe += 1
                            raw.append({"sent": sent, "s": q, "e": qe, "titleish": True})
                    continue
                if s == 0 and e - s == 1 and not has_acronym:
                    continue  # sentence-initial capital only
                if e - s == 1 and span_toks[0].low in _CALENDAR_WORDS:
                    continue
                raw.append({"sent": sent, "s": s, "e": e, "titleish": False})
                if s > 0 and e - s == 1 and not has_acronym:
                    key = span_toks[0].low
                    mid_caps[key] = mid_caps.get(key, 0) + 1
        counts: Dict[str, int] = {}
        for r in raw:
            r["key"] = " ".join(t.low for t in r["sent"].tokens[r["s"]:r["e"]])
            counts[r["key"]] = counts.get(r["key"], 0) + 1
        seen: Dict[Tuple[int, int, int], bool] = {}
        for r in raw:
            sent, s, e = r["sent"], r["s"], r["e"]
            toks = sent.tokens[s:e]
            single = e - s == 1
            acr = any(t.acronym for t in toks)
            if single and not acr and mid_caps.get(toks[0].low, 0) < 2:
                continue
            if (sent.index, s, e) in seen:
                continue
            seen[(sent.index, s, e)] = True
            lows = [t.low for t in toks]
            stems = [_stem(w) for w in lows]
            if any(w in _INSTITUTION_HEADS for w in lows):
                category = "named_institutions"
            elif any(st in _NORMATIVE_CATEGORY for st in stems):
                cat = _NORMATIVE_CATEGORY[next(st for st in stems if st in _NORMATIVE_CATEGORY)]
                category = {"standards": "named_standards", "regulations": "regulations",
                            "laws": "laws"}.get(cat, cat)
            elif acr and toks[-1].numeric:
                category = "named_standards"
            elif lows[0] in _REFERENCE_WORDS and toks[-1].numeric:
                category = "official_classifications"
            else:
                category = "recognized_entities"
            self.entities.append({"sent": sent, "s": s, "e": e, "category": category,
                                  "acronym": acr, "single": single,
                                  "frequency": counts.get(r["key"], 1)})
        self.acronym_expansions = self._find_acronym_expansions()
        self._entities_by_sentence: Dict[int, List[Dict[str, Any]]] = {}
        for ent in self.entities:
            self._entities_by_sentence.setdefault(ent["sent"].index, []).append(ent)

    def _initials(self, toks: Sequence[_Token]) -> List[str]:
        out: List[str] = []
        for t in toks:
            if t.low in _INITIAL_SKIP:
                continue
            for piece in re.split(r"[-\u2019']", t.text):
                if piece:
                    out.append(piece[0].lower())
        return out

    def _find_acronym_expansions(self) -> List[Dict[str, Any]]:
        """'Service Level Agreement (SLA)' / 'SLA (Service Level Agreement)' —
        validated by matching initials, which is language- and niche-neutral."""
        found: List[Dict[str, Any]] = []
        for sent in self.sentences:
            toks = sent.tokens
            for k, t in enumerate(toks):
                if not t.acronym:
                    continue
                letters = [c.lower() for c in t.text if c.isalpha()]
                if len(letters) >= 3 and t.text.endswith("s") and t.text[-1].islower():
                    letters = letters[:-1]
                L = len(letters)
                if L < 2:
                    continue
                # Expansion (ACRO)
                if k > 0 and self.gap(sent, k - 1, k).strip() == "(" and (
                        k + 1 >= len(toks) or self.gap(sent, k, k + 1).strip().startswith(")")
                        or sent.text[t.le:t.le + 1] == ")"):
                    for s in range(k - 1, max(-1, k - 1 - (L + 4)), -1):
                        if s < k - 1 and not self.joinable(sent, s, s + 1):
                            break
                        if toks[s].low in _INITIAL_SKIP:
                            continue
                        if self._initials(toks[s:k]) == letters:
                            found.append({"sent": sent, "s": s, "e": k, "acronym": t.text,
                                          "acronym_index": k})
                            break
                # ACRO (Expansion)
                if k + 1 < len(toks) and self.gap(sent, k, k + 1).strip() == "(":
                    for e in range(k + 2, min(len(toks), k + 2 + L + 4) + 1):
                        if e - 1 > k + 1 and not self.joinable(sent, e - 2, e - 1):
                            break
                        if toks[e - 1].low in _INITIAL_SKIP:
                            continue
                        if self._initials(toks[k + 1:e]) == letters:
                            found.append({"sent": sent, "s": k + 1, "e": e, "acronym": t.text,
                                          "acronym_index": k})
                            break
        return found

    # ------------------------------------------------------------ signals
    def signals(self, sent: _Sentence) -> Dict[str, Any]:
        if sent._signals is not None:
            return sent._signals
        lows = sent.lows
        joined = " " + " ".join(lows) + " "

        def multi(markers: Sequence[Tuple[str, ...]]) -> List[str]:
            return [" ".join(m) for m in markers if " " + " ".join(m) + " " in joined]

        evidence = sorted({w for w in lows if w in _EVIDENCE_WORDS}) + multi(_EVIDENCE_MULTI)
        safety = sorted({w for w in lows if w in _SAFETY_WORDS}) + multi(_SAFETY_MULTI)
        normative = sorted({w for w in lows if w in _NORMATIVE_WORDS})
        statistic = bool(_STAT_RE.search(sent.text))
        dated = bool(_YEAR_RE.search(sent.text))
        sent._signals = {
            "evidence": evidence, "safety": safety, "normative": normative,
            "statistic": statistic, "dated": dated,
            "science": any(w in _SCIENCE_WORDS for w in lows),
            "any_claim": bool(evidence) or statistic,
            "any_authority": bool(evidence or safety or normative or statistic),
        }
        return sent._signals

    # ------------------------------------------------------------ spans
    def span(self, sent: _Sentence, s: int, e: int, kind: str) -> _Span:
        return _Span(sent, s, e, kind)

    def span_text(self, sp: _Span) -> str:
        return sp.sent.text[sp.sent.tokens[sp.s].ls:sp.sent.tokens[sp.e - 1].le]

    def abs_bounds(self, sp: _Span) -> Tuple[int, int]:
        base = sp.sent.start
        return base + sp.sent.tokens[sp.s].ls, base + sp.sent.tokens[sp.e - 1].le

    def verify_literal(self, phrase: str) -> bool:
        needle = _normalize_span_text(phrase).casefold()
        if not needle:
            return False
        hit = self._verify_cache.get(needle)
        if hit is None:
            rx = _boundary_regex(needle)
            hit = any(rx.search(p) for p in self._search_cf)
            self._verify_cache[needle] = hit
        return hit

    def positions(self, phrase: str) -> Dict[str, Any]:
        key = phrase.casefold()
        if key not in self._pos_cache:
            self._pos_cache[key] = _find_literal_positions(phrase, surface=self.surface)
        return self._pos_cache[key]

    def token_occurrences(self, lows: Sequence[str]) -> List[Tuple[_Sentence, int, int]]:
        out: List[Tuple[_Sentence, int, int]] = []
        if not lows:
            return out
        L = len(lows)
        target = list(lows)
        for si, k in self._first_index.get(lows[0], ()):
            sent = self.sentences[si]
            if sent.lows[k:k + L] == target:
                out.append((sent, k, k + L))
        return out

    def units(self, sent: _Sentence) -> List[_Span]:
        return sorted(sent.np_of_units + sent.np_units, key=lambda u: (u.s, -u.e))

    def unit_starting_at(self, sent: _Sentence, pos: int,
                         kinds: Sequence[str] = ("np_of", "np", "single")) -> Optional[_Span]:
        for kind in kinds:
            for sp in sent.by_start.get(pos, ()):
                if sp.kind == kind:
                    return sp
        return None

    def unit_ending_at(self, sent: _Sentence, pos: int,
                       kinds: Sequence[str] = ("np", "single", "np_of")) -> Optional[_Span]:
        for kind in kinds:
            for sp in sent.by_end.get(pos, ()):
                if sp.kind == kind:
                    return sp
        return None

    def right_maximal(self, sp: _Span) -> bool:
        toks = sp.sent.tokens
        if sp.e >= len(toks):
            return True
        nxt = toks[sp.e]
        return not (self._eligible(sp.sent, sp.e) and nxt.low != "of"
                    and self.joinable(sp.sent, sp.e - 1, sp.e)
                    and _spe._head_is_noun_like(nxt.low, self.head_tag(nxt)))

    def cuts_entity(self, sp: _Span) -> bool:
        """True if the span starts or ends strictly INSIDE a multi-token named
        entity ("National Institute of Standards" inside "National Institute of
        Standards and Technology")."""
        for ent in self._entities_by_sentence.get(sp.sent.index, ()):
            es, ee = ent["s"], ent["e"]
            if ee - es < 2 or (sp.s <= es and sp.e >= ee) or sp.e <= es or sp.s >= ee:
                continue
            if es < sp.e < ee or es < sp.s < ee:
                return True
        return False

    def truncated_coordination(self, sent: _Sentence, e: int) -> bool:
        """True when the span ending at ``e`` is the first conjunct of a
        coordination ("between a landlord | and a tenant")."""
        toks = sent.tokens
        if e >= len(toks) or toks[e].low not in ("and", "or") or not self.joinable(sent, e - 1, e):
            return False
        j = e + 1
        if j < len(toks) and (toks[j].low in _ARTICLES or toks[j].low in _POSSESSIVE_DETS):
            j += 1
        return j < len(toks) and self.unit_starting_at(sent, j, ("np_of", "np", "single")) is not None

    def is_verb_object(self, sent: _Sentence, head_start: int) -> bool:
        q = head_start - 1
        toks = sent.tokens
        while q >= 0 and (toks[q].low in _ARTICLES or toks[q].low in _POSSESSIVE_DETS
                          or toks[q].low in _QUANTIFIERS or toks[q].tag == "NUM"):
            q -= 1
        return q >= 0 and self.is_clause_verb(toks[q]) and self.joinable(sent, q, q + 1)

    def pp_complement(self, sent: _Sentence, head_end: int, head_start: int,
                      preps: Iterable[str], max_b: int = 4,
                      nominal_head: bool = False) -> Optional[Tuple[_Span, str]]:
        """Shared NP + PREP + NP attachment used by Relationship, Content
        Context, Long-tail and Pattern discovery (one implementation).

        ``nominal_head`` is True for relational nouns ("risk of", "demand for"),
        whose PP attaches to the noun even in object position. Otherwise a PP
        after a verb's object is assumed verb-attached unless the preposition is
        strongly nominal ("of", "between", "against")."""
        toks = sent.tokens
        k = head_end
        if k >= len(toks) or toks[k].low not in preps or not self.joinable(sent, k - 1, k):
            return None
        prep = toks[k].low
        if not nominal_head and prep not in _OBJECT_PP_PREPS and self.is_verb_object(sent, head_start):
            return None
        if toks[head_end - 1].low in _QUANTITY_HEADS or toks[head_end - 1].numeric and \
                all(t.numeric for t in toks[head_start:head_end]):
            return None
        j = k + 1
        article = j < len(toks) and toks[j].low in _ARTICLES and self.joinable(sent, k, j)
        if article:
            j += 1
        B = self.unit_starting_at(sent, j, kinds=("np", "single"))
        if B is None or B.length > max_b or B.e - head_start > _MAX_NP_TOKENS:
            return None
        if toks[B.e - 1].numeric and B.length == 1:
            return None  # "over 16 (to 20 weeks)" — numeric complement is truncated
        if prep == "to" and B.length < 2 and not article:
            return None  # likely an infinitive ("ability to hear")
        if B.length == 1 and toks[B.s].low in _TIME_NOUNS:
            return None  # adverbial time PP ("over time"), not part of the concept
        if head_end - head_start == 1 and head_start > 0:
            prev = toks[head_start - 1]
            if not (prev.low in DETERMINERS or not self.joinable(sent, head_start - 1, head_start)):
                return None  # bare noun inside a larger construction ("time to value for")
        if self.truncated_coordination(sent, B.e):
            return None
        sp = _Span(sent, head_start, B.e, "np_pp")
        if not self.coherent(sent, sp.s, sp.e, allow_preps={prep}, allow_articles=True):
            return None
        if not self.right_maximal(sp):
            return None
        return sp, prep

    def completeness_profile(self, sp: _Span) -> Dict[str, Any]:
        head = sp.sent.tokens[sp.e - 1]
        rmax = self.right_maximal(sp)
        confirmed_noun = head.tag in ("NOUN", "NUM")
        signal = 0.4 + 0.2 * rmax + 0.2 * (len(sp.content) >= 2) + 0.2 * confirmed_noun
        return {"right_edge_maximal": rmax, "left_edge_clean": sp.lows[0] not in LEADING_BAN,
                "head_token": head.text, "head_tag": head.tag,
                "content_tokens": len(sp.content), "signal": round(signal, 4)}


# ---------------------------------------------------------------------------
# Component runner: exact-span verification, extractor comparison, provenance.
# ---------------------------------------------------------------------------

class _ComponentRun:
    """Single choke point through which EVERY component emits. It guarantees
    literalness, position recovery, provenance and extractor comparison, so no
    component can bypass the hard rules."""

    def __init__(self, model: _DocumentModel, name: str, diag: Dict[str, Any],
                 limit: int, document_id: str) -> None:
        self.model, self.name, self.diag = model, name, diag
        self.limit, self.document_id = limit, document_id
        self.by_key: Dict[str, Dict[str, Any]] = {}
        self.out: List[Dict[str, Any]] = []

    def _cap(self, capability: str) -> Dict[str, int]:
        return self.diag["capability_counts"].setdefault(capability, {"proposed": 0, "emitted": 0})

    def propose(self, sp: Optional[_Span], capability: str, signal: float,
                intel: Optional[Dict[str, Any]] = None, *, mode: str = "discovery",
                allow_single: bool = False) -> Optional[Dict[str, Any]]:
        if sp is None:
            return None
        d = self.diag
        d["proposed"] += 1
        self._cap(capability)["proposed"] += 1
        if sp.e <= sp.s or (sp.length == 1 and not allow_single):
            d["rejected_structural"] += 1
            return None
        phrase = self.model.span_text(sp)
        a, b = self.model.abs_bounds(sp)
        stext = sp.sent.text
        ls_, le_ = sp.sent.tokens[sp.s].ls, sp.sent.tokens[sp.e - 1].le
        before = stext[ls_ - 1] if ls_ > 0 else " "
        after = stext[le_] if le_ < len(stext) else " "
        glued = not (before.isspace() or before in _OPEN_PUNCT) or \
            not (after.isspace() or after in _CLOSE_PUNCT)
        if glued:  # e.g. "401" cut out of "401(k)", "cloud" out of "cloud/edge"
            d["rejected_structural"] += 1
            return None
        if self.model.cuts_entity(sp):  # never truncate a proper name
            d["rejected_structural"] += 1
            d["rejected_entity_truncation"] = d.get("rejected_entity_truncation", 0) + 1
            return None
        ok = (bool(phrase) and phrase == phrase.strip()
              and phrase[0].isalnum() and phrase[-1].isalnum()
              and self.model.surface[a:b] == phrase
              and " ".join(_lows_of(phrase)) == sp.key
              and self.model.verify_literal(phrase))
        if not ok:
            d["rejected_nonliteral"] += 1
            d["exact_span_failures"] += 1
            if len(d["exact_span_failure_examples"]) < 10:
                d["exact_span_failure_examples"].append(phrase)
            return None
        d["literal_verified"] += 1
        known = self.model.extractor.is_known(sp.lows)
        if mode == "reinspection" and not known:
            mode = "discovery"
        if known and mode != "reinspection":
            d["overlap_with_extractor"] += 1
            return None
        existing = self.by_key.get(sp.key)
        if existing is not None:
            d["duplicate_within_component"] += 1
            ei = existing["discovery_intelligence"]
            ei["supporting_occurrences"] += 1
            if capability not in ei["capabilities"]:
                ei["capabilities"].append(capability)
            ei["discovery_signal"] = max(ei["discovery_signal"], round(float(signal), 4))
            return None
        if len(self.out) >= self.limit:
            d["truncated_by_limit"] += 1
            return None
        sent = sp.sent
        pos = self.model.positions(phrase)
        related = self.model.extractor.contained_in(sp.lows)
        relation = ("reinspection" if mode == "reinspection"
                    else ("expands_extractor_phrase" if related else "net_new"))
        info: Dict[str, Any] = {
            "capability": capability,
            "capabilities": [capability],
            "canonical_phrase": sp.key,
            "token_count": sp.length,
            "structure": sp.kind,
            "discovery_signal": round(max(0.0, min(1.0, float(signal))), 4),
            "advisory_only": True,
            "extractor_relation": relation,
            "related_extractor_phrases": related,
            "literal_span_verified": True,
            "span": {
                "start": a, "end": b,
                "snippet_start": sent.tokens[sp.s].ls, "snippet_end": sent.tokens[sp.e - 1].le,
                "block_index": sent.block, "block_kind": self.model.blocks[sent.block].kind,
                "sentence_index": sent.index, "sentence_role": sent.role,
                "section_index": sent.section,
            },
            "heading_context": self.model.heading_text(sent.section),
            "first_position": pos["first_position"],
            "all_positions": pos["all_positions"],
            "occurrence_count": pos["occurrence_count"],
            "position_source": "title" if sent.role == "title" else "body",
            "position_basis": POSITION_BASIS,
            "supporting_occurrences": 1,
        }
        info.update(intel or {})
        cand = _build_discovery_candidate(
            phrase=phrase, component=self.name, capability=capability,
            section_id=sent.section_id, doc_id=self.document_id, snippet=sent.text,
            intelligence=info)
        self.by_key[sp.key] = cand
        self.out.append(cand)
        self._cap(capability)["emitted"] += 1
        if mode == "reinspection":
            d["reinspected_existing"] += 1
        return cand


# ===========================================================================
# 1. SEMANTIC DISCOVERY
# ===========================================================================

def semantic_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Concept Detection → Semantic Span Search → Extractor-Miss Comparison →
    Semantic Completeness → Semantic Salience → Exact-Span Verification.

    Span proposals are MAXIMAL noun-phrase constituents only, so a compound is
    never cut before its head ("Modern cloud" cannot be proposed when the text
    says "Modern cloud infrastructure") and no verb ever enters a span
    ("improve application", "infrastructure can" cannot be proposed)."""
    d = run.diag
    seeds: Dict[str, Dict[str, Any]] = {}
    for key in model.concepts:
        sup = model.concept_support(key)
        if sup["salient"] and " " in key:
            seeds["core:" + key] = {"concept": key, "type": "compound_core", **sup}
    for key in model.heads:
        sup = model.head_support(key)
        if sup["salient"]:
            seeds["head:" + key] = {"concept": key, "type": "head", **sup}
    ordered = sorted(seeds.values(), key=lambda x: (-x["strength"], x["concept"]))
    d["concept_seed_count"] = len(ordered)
    d["concept_seeds"] = [{k: v for k, v in s.items()} for s in ordered[:30]]

    proposals = 0
    low_salience = 0
    for sent in model.sentences:
        for sp in sent.np_units:
            csup = model.concept_support(sp.core_key)
            hsup = model.head_support(sp.head_key)
            if not (csup["salient"] or hsup["salient"]):
                continue
            proposals += 1
            comp = model.completeness_profile(sp)
            if not comp["right_edge_maximal"]:
                d["rejected_structural"] += 1
                continue
            best = csup if csup["strength"] >= hsup["strength"] else hsup
            salience = min(1.0, best["strength"] + 0.1 * (len(sp.content) >= 3))
            if salience < 0.25:
                low_salience += 1
                continue
            run.propose(sp, "semantic_span_search", 0.5 * salience + 0.5 * comp["signal"], {
                "seed_concept": sp.core_key if csup["salient"] else sp.head_key,
                "seed_type": "compound_core" if csup["salient"] else "head",
                "semantic_salience": round(salience, 4),
                "semantic_completeness": comp,
                "concept_support": best,
            })
    # Recurring compound core shared by several modified variants
    # ("modern cloud infrastructure" + "distributed cloud infrastructure"
    #  → "cloud infrastructure" as its own literal span).
    for key, rec in model.concepts.items():
        if " " not in key:
            continue
        variants = [sp for sp in rec["variants"].values() if len(sp.content) > 2]
        if len({v.key for v in variants}) < 2:
            continue
        for v in variants:
            toks = v.sent.tokens
            if v.e - 2 >= v.s and toks[v.e - 2].low == key.split(" ")[0]:
                core = model.span(v.sent, v.e - 2, v.e, "core")
                if model.coherent(v.sent, core.s, core.e):
                    proposals += 1
                    run.propose(core, "recurring_concept_core", 0.6, {
                        "seed_concept": key, "variant_count": len({x.key for x in variants}),
                        "concept_support": model.concept_support(key)})
                    break
    d["semantic_span_proposal_count"] = proposals
    d["rejected_low_salience"] = low_salience


# ===========================================================================
# 2. RELATIONSHIP DISCOVERY
# ===========================================================================

def _find_relation_markers(model: _DocumentModel, sent: _Sentence) -> List[Tuple[int, int, tuple]]:
    lows, toks = sent.lows, sent.tokens
    out: List[Tuple[int, int, tuple]] = []
    k = 0
    while k < len(lows):
        hit = None
        for marker in _RELATION_MARKERS:
            mt = marker[0]
            L = len(mt)
            if tuple(lows[k:k + L]) != mt:
                continue
            if marker[2] == "verbal" and toks[k].tag != "VERB":
                continue
            if any(not model.joinable(sent, q - 1, q) for q in range(k + 1, k + L)):
                continue
            hit = marker
            break
        if hit:
            out.append((k, k + len(hit[0]), hit))
            k += len(hit[0])
        else:
            k += 1
    return out


def _left_argument(model: _DocumentModel, sent: _Sentence, cs: int, family: str) -> Optional[_Span]:
    toks = sent.tokens
    best: Optional[_Span] = None
    for u in list(model.units(sent)) + list(sent.singles):
        if u.e > cs or cs - u.e > 3:
            continue
        ok = True
        for q in range(u.e, cs):
            w, t = toks[q].low, toks[q].tag
            if w in AUX_VERBS or w in _MODALS or w in ("not", "that", "which", "who") \
                    or w in PARTICLES_DEGREE or _spe._is_adverb_ly(w):
                continue
            if family == "comparison" and (w in COMPARATIVES or t == "ADJ" or w in ("more", "less", "much", "far")):
                continue
            ok = False
            break
        if ok and (best is None or u.e > best.e or (u.e == best.e and u.length > best.length)):
            best = u
    return best


def _right_argument(model: _DocumentModel, sent: _Sentence, ce: int) -> Optional[_Span]:
    toks = sent.tokens
    q = ce
    while q < len(toks) and q - ce < 3 and (
            toks[q].low in _ARTICLES or toks[q].low in _POSSESSIVE_DETS
            or toks[q].low in ("this", "these", "those") or toks[q].low in PARTICLES_DEGREE
            or _spe._is_adverb_ly(toks[q].low) or toks[q].low in _QUANTIFIERS):
        q += 1
    return model.unit_starting_at(sent, q, kinds=("np_of", "np"))


def _is_relational_noun(word: str) -> bool:
    return _stem(word) in _RELATIONAL_NOUN_STEMS or (len(word) >= 6 and word.endswith(_NOMINALIZATION_SUFFIXES))


def relationship_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Relationship Identification, Relational Span Discovery, Multi-Concept
    Phrase Detection, Connector/Relation Analysis, Existing-Candidate
    Comparison, Exact-Span Verification.

    Connectors are only SIGNALS: emitted phrases are always nominal spans
    (relation arguments, nominal relation frames like "risk of X", coordinated
    or compared concepts). A connector is never emitted on its own."""
    d = run.diag
    d.update(relations_identified=0, relation_family_counts={}, connector_only_blocked=0)
    for sent in model.sentences:
        toks = sent.tokens
        n = len(toks)
        marker_positions = set()
        # --- connector-driven relations
        for cs, ce, marker in _find_relation_markers(model, sent):
            family, kind, roles = marker[1], marker[2], marker[3]
            marker_positions.update(range(cs, ce))
            d["relations_identified"] += 1
            d["relation_family_counts"][family] = d["relation_family_counts"].get(family, 0) + 1
            connector = sent.text[toks[cs].ls:toks[ce - 1].le]
            left = None if kind == "nominal" else _left_argument(model, sent, cs, family)
            right = _right_argument(model, sent, ce)
            for arg, role, partner in ((left, roles[0], right), (right, roles[1], left)):
                if arg is None:
                    continue
                if not arg.content or all(w in {m for m in marker[0]} for w in arg.lows):
                    d["connector_only_blocked"] += 1
                    continue
                sal = model.span_salient(arg)
                run.propose(arg, "relational_argument", 0.5 + 0.2 * sal + 0.1 * (len(arg.content) >= 3), {
                    "relation_family": family, "relation_role": role, "connector": connector,
                    "partner_phrase": model.span_text(partner) if partner else "",
                    "argument_salient": sal}, allow_single=(arg.kind == "single"))
        # --- nominal relation frames ("risk of heart disease", "demand for skilled workers")
        for A in sent.np_units + sent.singles:
            if A.length > 3 or not _is_relational_noun(toks[A.e - 1].low):
                continue
            res = model.pp_complement(sent, A.e, A.s, _FRAME_PREPS, nominal_head=True)
            if res is None:
                continue
            sp, prep = res
            B_start = A.e + 1 + (1 if toks[A.e + 1].low in _ARTICLES else 0)
            B = model.span(sent, B_start, sp.e, "np")
            run.propose(model.span(sent, sp.s, sp.e, "relational_frame"), "relational_nominal_frame",
                        0.55 + 0.15 * model.span_salient(B) + 0.1 * model.span_salient(A), {
                            "relation_family": "nominal_relation", "relation_head": toks[A.e - 1].text,
                            "connector": toks[A.e].text, "concepts": [model.span_text(A), model.span_text(B)]})
        # --- multi-concept: coordination / comparison spans
        for k in range(1, n - 1):
            w = toks[k].low
            if w in ("and", "or"):
                if not (model.joinable(sent, k - 1, k) and model.joinable(sent, k, k + 1)):
                    continue
                L = model.unit_ending_at(sent, k, kinds=("np", "single"))
                R = model.unit_starting_at(sent, k + 1, kinds=("np", "single"))
                shared_modifier = False
                if L is None and R is not None and R.length >= 2:
                    lt = toks[k - 1]
                    if lt.low not in FUNCTION_WORDS and lt.tag in ("ADJ", "NOUN") and \
                            (k - 2 < 0 or not model._eligible(sent, k - 2) or not model.joinable(sent, k - 2, k - 1)):
                        L, shared_modifier = model.span(sent, k - 1, k, "modifier"), True
                if L is None or R is None or L.length > 3 or R.length > 3:
                    continue
                if L.s > 0 and model._eligible(sent, L.s - 1) and model.joinable(sent, L.s - 1, L.s):
                    continue
                gate = (sent.role in ("title", "heading", "list_item") or shared_modifier
                        or L.head_key == R.head_key
                        or (model.span_salient(L) and model.span_salient(R)))
                if not gate:
                    continue
                sp = model.span(sent, L.s, R.e, "coordination")
                if not model.coherent(sent, sp.s, sp.e, allow_conj={w}) or not model.right_maximal(sp):
                    continue
                run.propose(sp, "multi_concept_coordination", 0.5 + 0.2 * shared_modifier, {
                    "relation_family": "coordination", "connector": toks[k].text,
                    "concepts": [model.span_text(L), model.span_text(R)],
                    "shared_modifier_coordination": shared_modifier})
            elif w in ("vs", "versus", "vs."):
                L = model.unit_ending_at(sent, k, kinds=("np", "single"))
                R = model.unit_starting_at(sent, k + 1, kinds=("np", "single"))
                if L is None or R is None or L.length > 4 or R.length > 4:
                    continue
                if not re.match(r"^\s+$", model.gap(sent, k - 1, k)) or \
                        not re.match(r"^\.?\s+$", model.gap(sent, k, k + 1)):
                    continue
                sp = model.span(sent, L.s, R.e, "comparison")
                if sp.length <= 9:
                    run.propose(sp, "comparison_span", 0.65, {
                        "relation_family": "comparison", "connector": toks[k].text,
                        "concepts": [model.span_text(L), model.span_text(R)]})
        # --- lexicon-free subject–verb–object relations between salient concepts
        for k in range(1, n - 1):
            t = toks[k]
            if k in marker_positions or not model.is_clause_verb(t) or t.low in AUX_VERBS:
                continue
            L = _left_argument(model, sent, k, "svo")
            R = _right_argument(model, sent, k + 1)
            if L is None or R is None:
                continue
            if not (model.span_salient(L) and model.span_salient(R)):
                continue
            for arg, role, partner in ((L, "subject", R), (R, "object", L)):
                run.propose(arg, "relational_argument", 0.5, {
                    "relation_family": "entity_action", "relation_role": role,
                    "connector": t.text, "partner_phrase": model.span_text(partner),
                    "argument_salient": True})


# ===========================================================================
# 3. CONTENT CONTEXT DISCOVERY
# ===========================================================================

def _definitional_spans(model: _DocumentModel, sent: _Sentence) -> List[Tuple[_Span, str]]:
    out: List[Tuple[_Span, str]] = []
    lows, toks = sent.lows, sent.tokens
    n = len(lows)
    # "X is/are a|an|the ..." at sentence start
    for u in model.units(sent):
        if all(lows[q] in _ARTICLES for q in range(0, u.s)) and u.e + 1 < n \
                and lows[u.e] in ("is", "are") and lows[u.e + 1] in ("a", "an", "the", "one", "defined"):
            out.append((u, "definiendum"))
            j = u.e + 2
            while j < n and lows[j] in ("a", "an", "the", "type", "kind", "form", "of", "set"):
                j += 1
            nxt = model.unit_starting_at(sent, j, kinds=("np_of", "np"))
            if nxt is not None:
                out.append((nxt, "definiens"))
            break
    for markers, role in ((_DEFINITION_NEXT, "defined_term"), (_DEFINITION_PREV, "definiendum")):
        for m in markers:
            L = len(m)
            for k in range(n - L + 1):
                if tuple(lows[k:k + L]) != m:
                    continue
                if role == "defined_term":
                    j = k + L
                    while j < n and lows[j] in _ARTICLES:
                        j += 1
                    u = model.unit_starting_at(sent, j, kinds=("np_of", "np", "single"))
                    if u is not None and (u.length >= 2 or toks[u.s].cap):
                        out.append((u, role))
                else:
                    u = model.unit_ending_at(sent, k, kinds=("np_of", "np"))
                    if u is not None:
                        out.append((u, role))
    return out


def content_context_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Sentence / Paragraph / Section / Heading / Article-level context,
    Contextual Span Expansion, Contrast & Qualification, Miss Comparison,
    Exact-Span Verification."""
    d = run.diag
    d.update(sections_analysed=len(model.sections), definitional_hits=0, contrast_hits=0)
    title_stems = set(model.sections[0].stems)

    # Sentence context: definitions, appositive acronym expansions, contrast.
    for sent in model.sentences:
        for sp, role in _definitional_spans(model, sent):
            d["definitional_hits"] += 1
            run.propose(sp, "sentence_context_definition", 0.7, {
                "context_type": "definition", "definition_role": role}, allow_single=sp.length == 1 and sp.sent.tokens[sp.s].cap)
        lows, toks = sent.lows, sent.tokens
        n = len(lows)
        for m in _CONTRAST_NEXT:
            L = len(m)
            for k in range(n - L + 1):
                if tuple(lows[k:k + L]) == m:
                    j = k + L
                    while j < n and lows[j] in _ARTICLES:
                        j += 1
                    u = model.unit_starting_at(sent, j, kinds=("np_of", "np"))
                    if u is not None:
                        d["contrast_hits"] += 1
                        run.propose(u, "contrast_qualification", 0.6, {
                            "context_type": "contrast", "qualifier": " ".join(m)})
                    if m == ("unlike",):
                        # "Unlike X, Y ..." → Y is the contrasted concept
                        after = [q for q in range(j, n) if "," in model.gap(sent, q - 1, q)] if j < n else []
                        if after:
                            y = model.unit_starting_at(sent, after[0], kinds=("np_of", "np"))
                            if y is not None:
                                run.propose(y, "contrast_qualification", 0.6, {
                                    "context_type": "contrast", "qualifier": "unlike", "contrast_side": "main"})
        for k, w in enumerate(lows):
            if w in _CONTRAST_CLAUSE:
                for u in model.units(sent):
                    if k < u.s <= k + 4:
                        d["contrast_hits"] += 1
                        run.propose(u, "contrast_qualification", 0.5, {
                            "context_type": "contrast_clause", "qualifier": toks[k].text})
                        break
    for exp in model.acronym_expansions:
        sp = model.span(exp["sent"], exp["s"], exp["e"], "acronym_expansion")
        if model.coherent(sp.sent, sp.s, sp.e, allow_preps={"of", "for", "and", "in", "on", "to"},
                          allow_conj={"and"}, allow_articles=True, max_tokens=12):
            run.propose(sp, "sentence_context_appositive", 0.75, {
                "context_type": "acronym_definition", "acronym": exp["acronym"]})

    # Paragraph context: concept repeated within one paragraph → most specific form.
    for blk in model.blocks:
        if blk.kind != "paragraph" or len(blk.sentences) < 2:
            continue
        local: Dict[str, Dict[int, bool]] = {}
        best: Dict[str, _Span] = {}
        for si in blk.sentences:
            for sp in model.sentences[si].np_units + model.sentences[si].singles:
                local.setdefault(sp.head_key, {})[si] = True
                if sp.kind == "np" and (sp.head_key not in best or sp.length > best[sp.head_key].length):
                    best[sp.head_key] = sp
        for hk, sents in local.items():
            if len(sents) >= 2 and hk in best and hk not in GENERIC_WEAK_HEADS:
                run.propose(best[hk], "paragraph_context_topic", 0.55, {
                    "context_type": "paragraph_topic", "topic_head": hk,
                    "paragraph_mentions": len(sents)})

    # Heading-aware + section context + contextual expansion.
    for sec in model.sections:
        if sec.heading is None or not sec.stems:
            continue
        stems = set(sec.stems)
        emitted_here = 0
        section_heads: Dict[str, Dict[int, bool]] = {}
        for si in sec.sentences:
            sent = model.sentences[si]
            for sp in sent.np_units:
                section_heads.setdefault(sp.head_key, {})[si] = True
        for si in sec.sentences:
            sent = model.sentences[si]
            if si == sec.heading:
                continue
            toks = sent.tokens
            for sp in model.units(sent):
                overlap = sorted({_stem(w) for w in sp.content} & stems)
                if not overlap or len(sp.content) < 2 or emitted_here >= 20:
                    continue
                if run.propose(sp, "heading_aware_discovery", 0.5 + 0.1 * min(3, len(overlap)), {
                        "context_type": "heading_overlap", "heading_overlap": overlap}):
                    emitted_here += 1
                # contextual expansion: NP + prep + NP where the PP matches heading/title context
                if sp.kind == "np":
                    res = model.pp_complement(sent, sp.e, sp.s, _PP_PREPS)
                    if res is not None:
                        ex, prep = res
                        tail = {_stem(w) for w in ex.lows[sp.length + 1:] if w not in FUNCTION_WORDS}
                        if tail & (stems | title_stems):
                            run.propose(ex, "contextual_span_expansion", 0.55, {
                                "context_type": "heading_pp_expansion", "preposition": prep})
        # section-specific topics: head repeated in this section, rare elsewhere
        for hk, sents in section_heads.items():
            if len(sents) < 2 or hk in GENERIC_WEAK_HEADS:
                continue
            rec = model.heads.get(hk)
            if rec and len([s for s in rec["sections"] if s != sec.index]) > 1:
                continue
            best_sp = None
            for si in sents:
                for sp in model.sentences[si].np_units:
                    if sp.head_key == hk and (best_sp is None or sp.length > best_sp.length):
                        best_sp = sp
            if best_sp is not None:
                run.propose(best_sp, "section_context_topic", 0.55, {
                    "context_type": "section_topic", "topic_head": hk, "section_mentions": len(sents)})

    # Article-level: title concepts that recur across sections → most specific variant per section.
    if title_stems:
        for key, rec in model.heads.items():
            if key not in title_stems or len(rec["sections"]) < 2:
                continue
            per_section: Dict[int, _Span] = {}
            for sp in rec["variants"].values():
                sec_i = sp.sent.section
                if sec_i not in per_section or sp.length > per_section[sec_i].length:
                    per_section[sec_i] = sp
            for sp in per_section.values():
                run.propose(sp, "article_level_context", 0.6, {
                    "context_type": "title_concept_across_sections", "title_concept": key,
                    "section_count": len(rec["sections"])})


# ===========================================================================
# 4. LONG-TAIL DISCOVERY
# ===========================================================================

def _intent_span(model: _DocumentModel, sent: _Sentence, k: int) -> Optional[Tuple[_Span, Tuple[str, ...]]]:
    lows, toks = sent.lows, sent.tokens
    n = len(lows)
    prefix = next((p for p in _INTENT_STARTS if tuple(lows[k:k + len(p)]) == p), None)
    if prefix is None:
        return None
    question = sent.text.rstrip().endswith("?") or sent.role in ("heading", "title")
    j = k + len(prefix)
    verbs, free = 0, set(range(k, j))
    while j < n and j - k < _MAX_INTENT_TOKENS:
        w, t = lows[j], toks[j]
        if not model.joinable(sent, j - 1, j):
            return None
        if w in _ARTICLES or w in _POSSESSIVE_DETS:
            free.add(j)
            j += 1
            continue
        if question and w in ("you", "i", "we") and verbs == 0:
            free.add(j)
            j += 1
            continue
        if verbs < 2 and (t.tag == "VERB" or w in ALL_VERB_LEMMAS) and not model.unit_starting_at(sent, j, ("np",)):
            free.add(j)
            verbs += 1
            j += 1
            continue
        break
    head = model.unit_starting_at(sent, j, kinds=("np", "single"))
    if head is None:
        return None
    end = head.e
    if end < n and lows[end] in _PP_PREPS and model.joinable(sent, end - 1, end):
        q = end + 1
        if q < n and lows[q] in _ARTICLES:
            free.add(q)
            q += 1
        tail = model.unit_starting_at(sent, q, kinds=("np", "single"))
        if tail is not None and tail.e - k <= _MAX_INTENT_TOKENS:
            free.add(end)
            end = tail.e
    if end - k > _MAX_INTENT_TOKENS or end - k < 3:
        return None
    if not model.coherent(sent, k, end, max_tokens=_MAX_INTENT_TOKENS, allow_articles=True,
                          free_positions=free, allow_leading_function=True):
        return None
    return model.span(sent, k, end, "intent"), prefix


def long_tail_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Existing-Candidate Expansion, Multi-Word Specificity, Modifier
    Preservation, Compound Concepts, Intent-Rich Phrases, Overlapping-Candidate
    Recovery, Heading/Title Long-Tail — all constrained to constituent spans
    (maximal NP, NP-of-NP, one NP+PP), never free n-grams."""
    d = run.diag
    d.update(expansion_sources=0, pp_attachments=0, overlap_unions=0)

    def label(sp: _Span) -> str:
        toks = sp.sent.tokens[sp.s:sp.e]
        if any(t.numeric or "-" in t.text or t.tag == "ADJ" or _spe._is_adverb_ly(t.low) for t in toks[:-1]):
            return "modifier_preserving"
        if sum(1 for t in toks if t.tag == "NOUN" and t.low not in FUNCTION_WORDS) >= 3:
            return "compound_concept"
        return "multi_word_specificity"

    # 6.1 existing-candidate expansion (+ one PP attachment)
    for lows, phrase, _cand in model.extractor.literal_seqs:
        for sent, s, e in model.token_occurrences(lows):
            d["expansion_sources"] += 1
            for u in model.units(sent):
                if u.s <= s and e <= u.e and (u.e - u.s) > (e - s):
                    run.propose(u, "existing_candidate_expansion", 0.6 + 0.05 * min(3, u.length - (e - s)), {
                        "expanded_from": phrase, "specificity_type": label(u)})
            base = model.unit_ending_at(sent, e, kinds=("np", "single"))
            if base is None or base.s > s:
                continue
            res = model.pp_complement(sent, base.e, base.s, _PP_PREPS)
            if res is not None:
                d["pp_attachments"] += 1
                run.propose(res[0], "existing_candidate_expansion", 0.55, {
                    "expanded_from": phrase, "specificity_type": "prepositional_attachment",
                    "preposition": res[1]})

    # 6.2–6.4 maximal multi-word constituents (>=3 content tokens, or NP-of-NP)
    for sent in model.sentences:
        for u in model.units(sent):
            if len(u.content) >= 3 or (u.kind == "np_of" and len(u.content) >= 2):
                run.propose(u, label(u) if u.kind == "np" else "compound_concept",
                            0.45 + 0.1 * model.span_salient(u), {"specificity_type": label(u),
                                                                  "content_tokens": len(u.content)})

    # 6.5 intent-rich phrases (headings/title anywhere, body at sentence start)
    for sent in model.sentences:
        positions = range(len(sent.tokens)) if sent.role in ("title", "heading", "list_item") else [0]
        for k in positions:
            if k > 0 and not re.search(r"[:\-\u2013\u2014(]\s*$", model.gap(sent, k - 1, k)) \
                    and sent.role not in ("title", "heading"):
                continue
            res = _intent_span(model, sent, k)
            if res:
                sp, prefix = res
                run.propose(sp, "intent_rich_phrase", 0.65, {"intent_prefix": " ".join(prefix)})

    # 6.6 overlapping / adjacent extractor candidates → coherent union span
    for sent in model.sentences:
        occ: List[Tuple[int, int, str]] = []
        for lows, phrase, _ in model.extractor.literal_seqs:
            if lows[0] not in sent.lows:
                continue
            for occ_sent, s, e in model.token_occurrences(lows):
                if occ_sent is sent:
                    occ.append((s, e, phrase))
        occ.sort()
        for i in range(len(occ)):
            for j in range(i + 1, min(len(occ), i + 6)):
                a, b = occ[i], occ[j]
                if b[0] > a[1] or b[1] <= a[1] or b[0] <= a[0]:
                    continue
                s, e = a[0], b[1]
                if e - s > _MAX_NP_TOKENS:
                    continue
                if model.coherent(sent, s, e, allow_preps=_OF):
                    sp = model.span(sent, s, e, "overlap_union")
                    if model.right_maximal(sp):
                        d["overlap_unions"] += 1
                        run.propose(sp, "overlapping_candidate_recovery", 0.55, {
                            "recovered_from": [a[2], b[2]]})

    # 6.7 heading / title long-tail (whole heading when it is one constituent)
    for sent in model.sentences:
        if sent.role not in ("title", "heading"):
            continue
        n = len(sent.tokens)
        if 3 <= n <= _MAX_INTENT_TOKENS:
            preps = {w for w in sent.lows if w in PREPOSITIONS}
            if len(preps) <= 1 and model.coherent(sent, 0, n, allow_preps=preps, allow_articles=True,
                                                   max_tokens=_MAX_INTENT_TOKENS, allow_conj={"and", "or"}):
                run.propose(model.span(sent, 0, n, "heading_whole"), "heading_title_long_tail", 0.6,
                            {"heading_level": sent.level})
        for u in model.units(sent):
            if u.kind == "np":
                res = model.pp_complement(sent, u.e, u.s, _PP_PREPS)
                if res is not None:
                    run.propose(res[0], "heading_title_long_tail", 0.55, {"heading_level": sent.level})


# ===========================================================================
# 5. PATTERN DISCOVERY
# ===========================================================================

def _list_groups(model: _DocumentModel) -> List[List[_Sentence]]:
    groups: List[List[_Sentence]] = []
    cur: List[_Sentence] = []
    last_block = -2
    for sent in model.sentences:
        if sent.role == "list_item":
            if sent.local == 0 or model.blocks[sent.block].kind == "paragraph":
                contiguous = cur and (sent.block == last_block + 1 or sent.block == last_block)
                if not contiguous and cur:
                    groups.append(cur)
                    cur = []
                cur.append(sent)
            last_block = sent.block
        else:
            if cur and sent.block != last_block:
                groups.append(cur)
                cur = []
    if cur:
        groups.append(cur)
    return [g for g in groups if len(g) >= 2]


def _label_span(model: _DocumentModel, sent: _Sentence) -> Optional[_Span]:
    toks = sent.tokens
    for k in range(1, min(len(toks), 9)):
        g = model.gap(sent, k - 1, k)
        if re.search(r"[:\u2013\u2014]|\s-\s", g):
            s = 0
            while s < k and toks[s].low in _ARTICLES:
                s += 1
            if s < k and model.coherent(sent, s, k, allow_preps={"of", "for", "and"}, allow_conj={"and"},
                                        allow_single=True):
                return model.span(sent, s, k, "label")
            return None
    return None


def pattern_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Lexical / Syntactic / Section-List / Semantic-Family / Parallel-Phrase
    pattern detection, Pattern Support Evaluation and Pattern-Guided Rescan.

    Patterns are learned from THIS document only. A pattern needs at least two
    distinct literal instances in at least two different sentences (lists and
    enumerations: at least three parallel items) before it may guide a rescan."""
    d = run.diag
    patterns: List[Dict[str, Any]] = []

    def register(ptype: str, key: str, instances: int, sentences: int, accepted: bool, **extra: Any) -> str:
        pid = f"{ptype}:{key}"
        patterns.append({"pattern_id": pid, "type": ptype, "key": key, "instances": instances,
                         "sentences": sentences, "accepted": accepted, **extra})
        return pid

    all_np = [sp for s in model.sentences for sp in s.np_units]

    # 7.1 lexical head family ("* storage") and 7.1b modifier family ("cloud *")
    for ptype, keyfn in (("lexical_head_family", lambda sp: sp.head_key),
                         ("lexical_modifier_family", lambda sp: _stem(sp.content[0]) if len(sp.content) >= 2 else "")):
        fam: Dict[str, Dict[str, _Span]] = {}
        fam_sents: Dict[str, Dict[int, bool]] = {}
        for sp in all_np:
            key = keyfn(sp)
            if not key or key in GENERIC_WEAK_HEADS or len(key) < 3:
                continue
            fam.setdefault(key, {}).setdefault(sp.key, sp)
            fam_sents.setdefault(key, {})[sp.sent.index] = True
        for key, members in fam.items():
            distinct, n_sents = len(members), len(fam_sents[key])
            known_member = any(model.extractor.is_known(m.lows) for m in members.values())
            accepted = n_sents >= 2 and (distinct >= 3 or (distinct >= 2 and known_member))
            if distinct < 2:
                continue
            pid = register(ptype, key, distinct, n_sents, accepted)
            if not accepted:
                continue
            for m in members.values():  # pattern-guided rescan: every literal member
                run.propose(m, ptype, 0.45 + 0.05 * min(4, distinct), {
                    "pattern_id": pid, "pattern_support": {"instances": distinct, "sentences": n_sents}})

    # 7.2 syntactic frames: (head, preposition) with >=2 distinct complements
    frames: Dict[Tuple[str, str], Dict[str, _Span]] = {}
    frame_sents: Dict[Tuple[str, str], Dict[int, bool]] = {}
    for sent in model.sentences:
        toks = sent.tokens
        for A in sent.np_units + sent.singles:
            res = model.pp_complement(sent, A.e, A.s, _FRAME_PREPS)
            if res is None:
                continue
            sp, prep = res
            fk = (A.head_key, prep)
            frames.setdefault(fk, {}).setdefault(sp.key, sp)
            frame_sents.setdefault(fk, {})[sent.index] = True
    for fk, members in frames.items():
        distinct, n_sents = len(members), len(frame_sents[fk])
        if distinct < 2:
            continue
        accepted = n_sents >= 2 and fk[0] not in GENERIC_WEAK_HEADS
        pid = register("syntactic_frame", f"{fk[0]} {fk[1]} *", distinct, n_sents, accepted)
        if accepted:
            for m in members.values():
                run.propose(m, "syntactic_frame", 0.55, {"pattern_id": pid,
                                                        "pattern_support": {"instances": distinct, "sentences": n_sents}})

    # 7.3 section / list patterns
    for gi, group in enumerate(_list_groups(model)):
        labels = [(s, _label_span(model, s)) for s in group]
        labelled = [(s, sp) for s, sp in labels if sp is not None]
        if len(labelled) >= 2:
            pid = register("list_label_pattern", f"list{gi}", len(labelled), len(labelled), True)
            for s, sp in labelled:
                run.propose(sp, "section_list_pattern", 0.6, {"pattern_id": pid, "list_size": len(group)},
                            allow_single=sp.length == 1 and len(sp.content) == 1 and len(sp.lows[0]) >= 4)
        # Establish an action-list frame from independently supported sibling items first.
        action_anchors = []
        for s in group:
            toks = s.tokens
            if toks and (toks[0].tag == "VERB" or toks[0].low in ALL_VERB_LEMMAS) and toks[0].low not in AUX_VERBS:
                action_anchors.append(s)
        action_frame = len(action_anchors) >= 2 and any(s.tokens and s.tokens[0].tag == "VERB" for s in action_anchors) and len(action_anchors) * 2 >= len(group)
        verb_first = []
        if action_frame:
            for s in group:
                toks = s.tokens
                if not toks or len(toks) < 2 or len(toks) > 7 or toks[0].low in AUX_VERBS:
                    continue
                direct_action = toks[0].tag == "VERB" or toks[0].low in ALL_VERB_LEMMAS
                suffix_ok = model.coherent(s, 1, len(toks), allow_articles=True, free_positions=set(), max_tokens=6)
                if direct_action or suffix_ok:
                    sp = model.span(s, 0, len(toks), "action")
                    if model.coherent(s, 0, len(toks), allow_articles=True, free_positions={0}, max_tokens=7) or suffix_ok:
                        verb_first.append(sp)
        if len(verb_first) >= 2:
            pid = register("parallel_action_list", f"list{gi}", len(verb_first), len(verb_first), True)
            for sp in verb_first:
                run.propose(sp, "parallel_phrase_pattern", 0.6, {"pattern_id": pid, "list_size": len(group)})
        leading = [model.unit_starting_at(s, 0, kinds=("np_of", "np")) for s in group]
        leading = [sp for sp in leading if sp is not None]
        if len(leading) >= 2:
            pid = register("list_leading_np", f"list{gi}", len(leading), len(leading), True)
            for sp in leading:
                run.propose(sp, "section_list_pattern", 0.5, {"pattern_id": pid, "list_size": len(group)})
    # paragraph "Label: ..." pattern across the document
    body_labels = [(s, _label_span(model, s)) for s in model.sentences if s.role == "body"]
    body_labels = [(s, sp) for s, sp in body_labels if sp is not None and sp.length >= 2]
    if len(body_labels) >= 2:
        pid = register("paragraph_label_pattern", "doc", len(body_labels), len(body_labels), True)
        for s, sp in body_labels:
            run.propose(sp, "section_list_pattern", 0.55, {"pattern_id": pid})
    # sibling headings sharing a leading structure ("Step 1: X", "Step 2: Y")
    by_parent: Dict[Tuple[int, int], List[_Sentence]] = {}
    for sec in model.sections[1:]:
        by_parent.setdefault((sec.parent, sec.level), []).append(model.sentences[sec.heading])
    for (parent, level), heads in by_parent.items():
        if len(heads) < 2:
            continue
        with_label = [(h, _label_span(model, h)) for h in heads]
        tails = []
        for h, lab in with_label:
            if lab is None:
                continue
            k = lab.e
            while k < len(h.tokens) and h.tokens[k].low in _ARTICLES:
                k += 1
            u = model.unit_starting_at(h, k, kinds=("np_of", "np"))
            if u is not None:
                tails.append(u)
        if len(tails) >= 2:
            pid = register("sibling_heading_pattern", f"{parent}:{level}", len(tails), len(tails), True)
            for u in tails:
                run.propose(u, "section_list_pattern", 0.6, {"pattern_id": pid})

    # 7.5 parallel enumerations "A, B, and C" → 7.4 semantic family → rescan
    families: List[List[_Span]] = []
    for sent in model.sentences:
        segs = sorted(sent.np_units + sent.singles, key=lambda u: u.s)
        chain: List[_Span] = []
        commas = 0
        for u in segs:
            if not chain:
                chain = [u]
                commas = 0
                continue
            prev = chain[-1]
            between = sent.lows[prev.e:u.s]
            gap_text = sent.text[sent.tokens[prev.e - 1].le:sent.tokens[u.s].ls]
            gap_clean = re.sub(r"\b(and|or)\b", "", gap_text)
            if len(between) <= 1 and all(w in ("and", "or") for w in between) and \
                    re.match(r"^[\s,]*$", gap_clean) and ("," in gap_text or between):
                chain.append(u)
                commas += gap_text.count(",")
            else:
                if len(chain) >= 3 and commas >= 1:
                    families.append(chain)
                chain = [u]
                commas = 0
        if len(chain) >= 3 and commas >= 1:
            families.append(chain)
    for fi, fam in enumerate(families):
        pid = register("parallel_enumeration", f"enum{fi}", len(fam), 1, True,
                       members=[model.span_text(u) for u in fam])
        for u in fam:
            if u.length >= 2:
                run.propose(u, "parallel_phrase_pattern", 0.55, {"pattern_id": pid, "family_size": len(fam)})
        # semantic family rescan: member embedded in a longer maximal NP elsewhere
        member_seqs = {u.lows for u in fam}
        for sent in model.sentences:
            for w in model.units(sent):
                if w.sent is fam[0].sent and any(w.s <= u.s and u.e <= w.e for u in fam):
                    continue
                for seq in member_seqs:
                    L = len(seq)
                    if w.length > L and any(w.lows[q:q + L] == seq for q in range(w.length - L + 1)):
                        run.propose(w, "semantic_family_rescan", 0.5, {
                            "pattern_id": pid, "family_member": " ".join(seq)})
                        break

    d["patterns"] = patterns[:200]
    d["patterns_detected"] = len(patterns)
    d["patterns_accepted"] = sum(1 for p in patterns if p["accepted"])
    d["patterns_rejected_insufficient_support"] = sum(1 for p in patterns if not p["accepted"])


# ===========================================================================
# 6. EXTERNAL AUTHORITY DISCOVERY  (phrases only — ZERO URL/source resolution)
# ===========================================================================

def _normative_category(sp: _Span) -> Optional[str]:
    for w in reversed(sp.lows):
        st = _stem(w)
        if st in _NORMATIVE_CATEGORY:
            return _NORMATIVE_CATEGORY[st]
        if w in _NORMATIVE_CATEGORY:
            return _NORMATIVE_CATEGORY[w]
    return None


def external_authority_discovery(model: _DocumentModel, run: _ComponentRun) -> None:
    """Authority-Worthy Concept Detection, Claim-Linked Phrases, Named
    Authorities/Institutions, Standards/Guidelines/Regulations,
    Evidence-Sensitive Topics, Existing-Candidate Authority Reinspection.

    Emits literal phrases with authority *signals* only. It never searches,
    fetches, ranks or selects sources/URLs/domains."""
    d = run.diag
    d.update(url_resolution_performed=False, authority_category_counts={})

    def emit(sp: _Span, capability: str, categories: List[str], signal: float,
             extra: Optional[Dict[str, Any]] = None, *, allow_single: bool = False, mode: str = "discovery") -> None:
        cats = sorted(set(c for c in categories if c))
        res = run.propose(sp, capability, signal, {
            "authority_categories": cats, "authority_signals": model.signals(sp.sent),
            "url_resolution": "none", **(extra or {})}, allow_single=allow_single, mode=mode)
        if res is not None:
            for c in cats:
                d["authority_category_counts"][c] = d["authority_category_counts"].get(c, 0) + 1

    # 8.3 named authorities / institutions / named standards
    for ent in model.entities:
        sent = ent["sent"]
        sig = model.signals(sent)
        sp = model.span(sent, ent["s"], ent["e"], "entity")
        cat = ent["category"]
        cap_tokens = sum(1 for t in sent.tokens[ent["s"]:ent["e"]] if t.cap or t.acronym)
        if cat == "recognized_entities" and cap_tokens < 2 and not (
                sig["any_authority"] or ent["frequency"] >= 2 or ent["acronym"]):
            continue
        if ent["single"] and ent["acronym"] and ent["frequency"] < 2 and not any(
                x["acronym_index"] == ent["s"] and x["sent"] is sent for x in model.acronym_expansions):
            continue
        emit(sp, "named_authority_detection", [cat], 0.7 if cat != "recognized_entities" else 0.5,
             {"entity_frequency": ent["frequency"], "acronym": ent["acronym"]},
             allow_single=ent["single"])
    for exp in model.acronym_expansions:
        sp = model.span(exp["sent"], exp["s"], exp["e"], "acronym_expansion")
        if not model.coherent(sp.sent, sp.s, sp.e, allow_preps={"of", "for", "and", "in", "on", "to"},
                              allow_conj={"and"}, allow_articles=True, max_tokens=12):
            continue
        cat = "named_institutions" if any(w in _INSTITUTION_HEADS for w in sp.lows) else (
            _normative_category(sp) or "recognized_entities")
        emit(sp, "named_authority_detection", [cat, "definitions"], 0.75, {"acronym": exp["acronym"]})

    for sent in model.sentences:
        sig = model.signals(sent)
        toks = sent.tokens
        lows = sent.lows
        n = len(toks)
        # 8.4 standards / guidelines / regulations / formal references
        for u in model.units(sent):
            cat = _normative_category(u)
            if cat and len(u.content) >= 2:
                emit(u, "standard_guideline_regulation", [cat], 0.65 + 0.1 * sig["any_authority"],
                     {"normative_head": next((w for w in reversed(u.lows)
                                              if _stem(w) in _NORMATIVE_CATEGORY or w in _NORMATIVE_CATEGORY), "")})
        for k in range(n - 1):
            if lows[k] in _REFERENCE_WORDS and toks[k].cap and toks[k + 1].numeric and model.joinable(sent, k, k + 1):
                sp = model.span(sent, k, k + 2, "reference")
                if model.coherent(sent, sp.s, sp.e):
                    emit(sp, "standard_guideline_regulation", ["official_classifications"], 0.6,
                         {"reference_word": toks[k].text})
        # source introducers ("according to X", "published by X")
        for m in _SOURCE_INTRODUCERS:
            L = len(m)
            for k in range(n - L + 1):
                if tuple(lows[k:k + L]) != m:
                    continue
                j = k + L
                while j < n and lows[j] in _ARTICLES:
                    j += 1
                u = model.unit_starting_at(sent, j, kinds=("np_of", "np", "single"))
                if u is not None and (toks[u.s].cap or toks[u.s].acronym or u.length >= 2):
                    emit(u, "claim_linked_phrase", ["research_findings" if sig["science"] else "official_guidance"],
                         0.7, {"claim_role": "cited_source", "introducer": " ".join(m)},
                         allow_single=toks[u.s].acronym or toks[u.s].cap)
        # 8.2 claim-linked topics & thresholds
        if sig["any_claim"]:
            cats = []
            if sig["statistic"]:
                cats.append("statistics")
            if sig["science"]:
                cats += ["research_findings", "scientific_claims"]
            if sig["evidence"] and not cats:
                cats.append("research_findings")
            emitted = 0
            for u in model.units(sent):
                if emitted >= 3:
                    break
                if model.span_salient(u) or len(u.content) >= 3:
                    emit(u, "claim_linked_phrase", cats, 0.55 + 0.1 * model.span_salient(u),
                         {"claim_role": "claim_topic"})
                    emitted += 1
        if re.search(r"\d", sent.text):
            for u in model.units(sent):
                if any(_stem(w) in _LIMIT_STEMS for w in u.content) and len(u.content) >= 2:
                    emit(u, "claim_linked_phrase", ["thresholds_limits"], 0.6, {"claim_role": "threshold"})
        # 8.5 evidence-sensitive topics (safety / normative modality)
        if sig["safety"] or sig["normative"]:
            cats = (["safety_warnings"] if sig["safety"] else []) + \
                   (["official_guidance", "recommendations"] if sig["normative"] else [])
            emitted = 0
            for u in model.units(sent):
                if emitted >= 3:
                    break
                if model.span_salient(u):
                    emit(u, "evidence_sensitive_topic", cats, 0.55,
                         {"sensitivity_markers": sig["safety"] + sig["normative"]})
                    emitted += 1
        # definitions are reference-worthy
        for sp, role in _definitional_spans(model, sent):
            if role in ("definiendum", "defined_term") and sp.length >= 2:
                emit(sp, "authority_worthy_concept", ["definitions"], 0.55, {"definition_role": role})

    # 8.6 existing-candidate authority reinspection: re-flag extractor phrases
    # that coincide EXACTLY with a coherent constituent and carry an authority
    # signal. Extractor fragments ("sessions improve vocabulary") are never re-emitted.
    entity_bounds = {(e["sent"].index, e["s"], e["e"]) for e in model.entities}
    for lows, phrase, _ in model.extractor.literal_seqs:
        norm = any(_stem(w) in _NORMATIVE_CATEGORY for w in lows)
        inst = any(w in _INSTITUTION_HEADS for w in lows)
        for sent, s, e in model.token_occurrences(lows)[:3]:
            unit = next((u for u in sent.np_of_units + sent.np_units if u.s == s and u.e == e), None)
            is_entity = (sent.index, s, e) in entity_bounds
            if unit is None and not is_entity:
                continue
            sig = model.signals(sent)
            sp = model.span(sent, s, e, "reinspection")
            if not (norm or inst or is_entity or (sig["any_authority"] and model.span_salient(sp))):
                continue
            cats = []
            if inst:
                cats.append("named_institutions")
            if norm:
                cats.append(_normative_category(sp) or "standards")
            if is_entity and not inst:
                cats.append("recognized_entities")
            if sig["statistic"]:
                cats.append("statistics")
            if sig["science"]:
                cats.append("research_findings")
            if sig["safety"]:
                cats.append("safety_warnings")
            if sig["normative"] and not norm:
                cats.append("official_guidance")
            emit(sp, "existing_candidate_authority_reinspection", cats or ["official_guidance"],
                 0.5, {"reinspected_extractor_phrase": phrase}, mode="reinspection")
            break


# ---------------------------------------------------------------------------
# Canonical public entry point.
# ---------------------------------------------------------------------------

_COMPONENT_FUNCS: Dict[str, Callable[[_DocumentModel, _ComponentRun], None]] = {
    SEMANTIC: semantic_discovery,
    RELATIONSHIP: relationship_discovery,
    CONTENT_CONTEXT: content_context_discovery,
    LONG_TAIL: long_tail_discovery,
    PATTERN: pattern_discovery,
    EXTERNAL_AUTHORITY: external_authority_discovery,
}


def discover_phrases(
    *,
    text: str = "",
    html: str = "",
    title: str = "",
    extractor_candidates: Optional[List[Dict[str, Any]]] = None,
    document_id: str = "",
    workspace_id: str = "default",
    vertical: str = "general",
    max_candidates: int = 500,
    components: Optional[Sequence[str]] = None,
    diagnostics: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Canonical Phrase Discovery entry point.

    Returns discovery candidates in the shared schema (``source_type ==
    "phrase_discovery"``). Never calls Guard/Scorer/Selection/Density and never
    resolves URLs.

    Optional, backward-compatible keyword arguments:
      * ``components``: subset of DISCOVERY_COMPONENTS (isolated testing).
      * ``diagnostics``: a dict the engine fills with engine and per-component
        diagnostics (the return type stays a plain list).
    """
    if extractor_candidates is None:
        clean_extractor: List[Dict[str, Any]] = []
    elif not isinstance(extractor_candidates, list):
        raise TypeError("extractor_candidates must be a list.")
    else:
        clean_extractor = [dict(c) for c in extractor_candidates if isinstance(c, dict)]
    selected = list(DISCOVERY_COMPONENTS) if components is None else [c for c in DISCOVERY_COMPONENTS if c in set(components)]
    unknown = sorted(set(components or ()) - set(DISCOVERY_COMPONENTS))
    if unknown:
        raise ValueError(f"Unknown discovery components: {unknown}")
    clean_text, clean_html, clean_title = str(text or ""), str(html or ""), str(title or "")
    clean_doc = str(document_id or "").strip()
    try:
        safe_max = max(1, min(int(max_candidates or 500), 5000))
    except (TypeError, ValueError):
        safe_max = 500

    diag_out: Dict[str, Any] = {
        "engine_version": ENGINE_VERSION,
        "workspace_id": str(workspace_id or "default").strip() or "default",
        "vertical": str(vertical or "general").strip() or "general",
        "vertical_used_for_logic": False,
        "components_run": selected,
        "components": {c: _new_component_diagnostics(c) for c in selected},
    }
    if not (clean_text.strip() or clean_html.strip() or clean_title.strip()):
        diag_out["empty_document"] = True
        if diagnostics is not None:
            diagnostics.update(diag_out)
        return []

    model = _DocumentModel(text=clean_text, html=clean_html, title=clean_title,
                           extractor_candidates=clean_extractor)
    diag_out.update({
        "tagger_backend": "nltk" if _spe._have_nltk() else "heuristic",
        "structure_mode": model.structure_mode,
        "blocks": len(model.blocks), "sentences": len(model.sentences),
        "sections": len(model.sections),
        "extractor_candidates": model.extractor.total,
        "extractor_literal_candidates": len(model.extractor.literal_seqs),
        "extractor_nonliteral_candidates": len(model.extractor.nonliteral),
        "extractor_nonliteral_examples": model.extractor.nonliteral[:10],
    })

    per_component: Dict[str, List[Dict[str, Any]]] = {}
    for name in selected:
        d = diag_out["components"][name]
        run = _ComponentRun(model, name, d, safe_max, clean_doc)
        try:
            _COMPONENT_FUNCS[name](model, run)
        except Exception as exc:  # isolate component failures
            logger.exception("Phrase discovery component %s failed", name)
            d["errors"].append(f"{type(exc).__name__}: {exc}")
        d["net_new"] = sum(1 for c in run.out if c["discovery_intelligence"]["extractor_relation"] != "reinspection")
        denom = max(1, d["literal_verified"] - d["overlap_with_extractor"])
        d["duplicate_rate"] = round(d["duplicate_within_component"] / denom, 4)
        d["summary"] = {k: d[k] for k in ("proposed", "literal_verified", "exact_span_failures",
                                          "overlap_with_extractor", "duplicate_within_component",
                                          "duplicate_rate", "net_new", "reinspected_existing")}
        per_component[name] = sorted(run.out, key=lambda c: (
            -c["discovery_intelligence"]["discovery_signal"],
            c["discovery_intelligence"]["span"]["start"], c["phrase"].casefold()))

    # Cross-component support (information for Phrase Merger; no dedupe here).
    support: Dict[str, List[str]] = {}
    for name in selected:
        for c in per_component[name]:
            lst = support.setdefault(c["discovery_intelligence"]["canonical_phrase"], [])
            if name not in lst:
                lst.append(name)
    total = 0
    for name in selected:
        for c in per_component[name]:
            comps = support[c["discovery_intelligence"]["canonical_phrase"]]
            c["discovery_intelligence"]["cross_component_support"] = [x for x in comps if x != name]
            total += 1

    # Fair budget: round-robin across components so none can starve the others.
    merged: List[Dict[str, Any]] = []
    queues = [list(per_component[n]) for n in selected]
    while len(merged) < safe_max and any(queues):
        for q in queues:
            if q and len(merged) < safe_max:
                merged.append(q.pop(0))
    order = {n: i for i, n in enumerate(selected)}
    merged.sort(key=lambda c: (c["discovery_intelligence"]["span"]["start"],
                               order[c["provenance"]["component"]], c["phrase"]))
    for name in selected:
        d = diag_out["components"][name]
        d["emitted"] = sum(1 for c in merged if c["provenance"]["component"] == name)
    diag_out["total_before_budget"] = total
    diag_out["total_emitted"] = len(merged)
    diag_out["cross_component_shared_phrases"] = sum(1 for v in support.values() if len(v) > 1)
    if diagnostics is not None:
        diagnostics.update(diag_out)
    return merged


if __name__ == "__main__":  # pragma: no cover
    import json
    demo_text = ("Modern cloud infrastructure provides scalable computing resources. "
                 "Distributed cloud infrastructure can improve application reliability.")
    diag: Dict[str, Any] = {}
    extracted = _spe.extract_smart_phrases(text=demo_text, doc_id="demo")
    for c in discover_phrases(text=demo_text, extractor_candidates=extracted,
                              document_id="demo", diagnostics=diag):
        print(f'{c["provenance"]["component"]:<30} {c["provenance"]["capability"]:<32} {c["phrase"]}')
    print(json.dumps({k: v["summary"] for k, v in diag["components"].items()}, indent=1))


