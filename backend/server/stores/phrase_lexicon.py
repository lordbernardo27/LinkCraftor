"""
phrase_lexicon.py — the single source of truth for phrase vocabulary + canonicalization.

WHY THIS FILE EXISTS
--------------------
Before this, five files each defined their own `canonical_phrase` and their own
sets of heads/modifiers/verbs/stopwords. They disagreed, and disagreement is
where quality leaked (good phrases dropped by one stage, bad ones preserved
because the stage that would catch them wasn't on that path).

RULE: every stage imports from here. No stage defines its own phrase vocabulary
or its own canonicalizer ever again.

Domain vocab is a *soft booster*, never the deciding factor. The deciding factor
is structure (POS) in the extractor. These sets only nudge usefulness scoring and
let known compounds bypass the generic checks. That is what lets the system
generalise across niches it has thin vocab for (legal/travel/ecommerce).
"""

from __future__ import annotations

import re
from typing import List, Set, Tuple

# ---------------------------------------------------------------------------
# Canonicalization — exactly one implementation
# ---------------------------------------------------------------------------

_WS_RE = re.compile(r"\s+")
_LIST_MARKER_RE = re.compile(r"^\s*(?:\d+[.)]\s+|[\u2022\u2013\u2014\-]\s+)")
_WRAP_PUNCT_RE = re.compile(r"^[\"'\u201c\u201d\u2018\u2019(\[{]+|[\"'\u201c\u201d\u2018\u2019)\]}:;,.!?]+$")

# Conversational wrappers that should be stripped from the FRONT of a phrase.
# (Previously only one of five canonicalizers did this, causing dedupe misses.)
_LEAD_WRAPPER_RE = re.compile(
    r"^(?:"
    r"(?:many |you may |you might |often )?"
    r"(?:people|users|readers|customers|clients|students|parents|patients|"
    r"business owners|teams|professionals|creators)?\s*"
    r"(?:often )?(?:ask|wonder|be asking)\s+"
    r")",
    re.IGNORECASE,
)


def canonical_phrase(text: str) -> str:
    """The one canonical form. Lowercase, smart-quotes normalised, list markers
    and wrapping punctuation stripped, whitespace collapsed, lead wrappers removed."""
    s = (text or "").strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = s.replace("\u00a0", " ")
    s = _LIST_MARKER_RE.sub("", s)
    s = _WRAP_PUNCT_RE.sub("", s)
    s = _LEAD_WRAPPER_RE.sub("", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


_WORD_RE = re.compile(r"[a-z0-9][a-z0-9'-]*", re.I)


def tokenize(text: str) -> List[str]:
    """Tokenize, with the one tokenization fix that matters: split glued
    negations like 'cannot' so they're caught as the function words they are."""
    raw = [t.lower() for t in _WORD_RE.findall(text or "")]
    out: List[str] = []
    for t in raw:
        if t == "cannot":
            out.extend(["can", "not"])
        else:
            out.append(t)
    return out


def phrase_key(phrase: str) -> str:
    return " ".join(tokenize(canonical_phrase(phrase)))


# ---------------------------------------------------------------------------
# Closed-class words (function words) — used for boundary trimming
# ---------------------------------------------------------------------------

DETERMINERS: Set[str] = {
    "a", "an", "the", "this", "that", "these", "those", "my", "your", "his",
    "her", "its", "our", "their", "some", "any", "each", "every", "no",
    "another", "such", "much", "many", "more", "most", "all", "both", "either",
    "neither", "which", "what", "whose",
}

PREPOSITIONS: Set[str] = {
    "about", "above", "across", "after", "against", "along", "among", "around",
    "as", "at", "before", "behind", "below", "beneath", "beside", "between",
    "beyond", "by", "down", "during", "except", "for", "from", "in", "inside",
    "into", "near", "of", "off", "on", "onto", "out", "outside", "over", "per",
    "since", "than", "through", "throughout", "to", "toward", "towards",
    "under", "until", "up", "upon", "via", "with", "within", "without", "like",
}

CONJUNCTIONS: Set[str] = {
    "and", "or", "but", "nor", "so", "yet", "because", "although", "though",
    "while", "whereas", "unless", "until", "whether", "if", "then",
}

PRONOUNS: Set[str] = {
    "i", "me", "my", "mine", "myself", "you", "yours", "yourself", "he", "him",
    "his", "she", "her", "hers", "we", "us", "our", "ours", "they", "them",
    "their", "theirs", "it", "its", "itself", "who", "whom", "whose", "anyone",
    "someone", "everyone", "everybody", "somebody", "anybody", "nobody",
    "something", "anything", "everything", "nothing", "one", "ones",
}

AUX_VERBS: Set[str] = {
    "is", "are", "was", "were", "be", "being", "been", "am", "can", "could",
    "will", "would", "shall", "should", "may", "might", "must", "has", "have",
    "had", "do", "does", "did", "ought", "not",  # 'not' here so 'can not' fully trims
}

# Adverbs / discourse particles that should never anchor a phrase end.
# Expanded (vs the original) so the *heuristic fallback* hardens against
# leaks like 'together imagine' when real POS is unavailable.
PARTICLES_DEGREE: Set[str] = {
    "not", "very", "too", "also", "just", "only", "even", "still", "quite",
    "rather", "really", "almost", "always", "never", "often", "sometimes",
    "usually", "generally", "typically", "currently", "recently", "soon",
    "later", "now", "today", "tomorrow", "yesterday", "here", "there",
    "however", "therefore", "meanwhile", "instead", "anyway", "actually",
    "basically", "simply", "clearly", "finally", "first", "firstly",
    "second", "secondly", "lastly", "overall", "especially", "particularly",
    "together", "apart", "away", "back", "forward", "ahead", "again",
    "perhaps", "maybe", "indeed", "thus", "hence", "moreover",
}

FUNCTION_WORDS: Set[str] = (
    DETERMINERS | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | AUX_VERBS | PARTICLES_DEGREE
)

# ---------------------------------------------------------------------------
# Verbs — used by the heuristic fallback only. With real POS these are advisory.
# ---------------------------------------------------------------------------

# Verbs that legitimately HEAD an action anchor ("calculate due date").
ACTION_VERBS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check", "measure",
    "estimate", "build", "create", "fix", "improve", "optimize", "reduce",
    "increase", "manage", "treat", "prevent", "diagnose", "review", "audit",
    "forecast", "plan", "write", "design", "analyze", "monitor", "test",
    "rank", "score", "publish", "import", "export", "sync", "validate",
    "protect", "convert", "identify", "select", "schedule", "generate",
}

# Lexical verbs that, mid-phrase, signal a glued-together clause.
# Expanded materially so the heuristic fallback catches the verbs that leaked
# before (pay, lead, detect, imagine, etc.).
LEXICAL_VERBS: Set[str] = {
    "runs", "run", "falls", "fall", "lands", "land", "becomes", "become",
    "means", "mean", "depends", "depend", "explains", "explain", "turns",
    "turn", "makes", "make", "shows", "show", "happens", "happen", "rises",
    "rise", "stays", "stay", "offers", "offer", "works", "work", "holds",
    "hold", "starts", "start", "ends", "end", "uses", "use", "gives", "give",
    "gets", "get", "goes", "go", "comes", "come", "takes", "take", "needs",
    "need", "wants", "want", "knows", "know", "says", "say", "tells", "tell",
    "grows", "grow", "affects", "affect", "changes", "change", "watch", "look",
    "see", "let", "keep", "try", "learn", "read", "note", "avoid", "consider",
    "remember", "ensure", "pick", "set", "add", "put", "ask", "call", "send",
    "follow", "apply", "enter", "click", "tap", "visit", "open", "close",
    "save", "share", "control", "controls", "controlled",
    # verbs that previously leaked as fake nouns:
    "pay", "pays", "paid", "lead", "leads", "led", "detect", "detects",
    "detected", "imagine", "imagines", "imagined", "feel", "feels", "felt",
    "find", "finds", "found", "lean", "leans", "shoot", "shoots", "derail",
    "ruin", "wreck", "confuse", "frustrate", "wonder", "wonders",
    # common verbs whose 3sg form taggers sometimes mislabel as a plural noun:
    "deserve", "deserves", "deserved", "involve", "involves", "require",
    "requires", "describe", "describes", "indicate", "indicates", "suggest",
    "suggests", "remain", "remains", "appear", "appears", "seem", "seems",
    "occur", "occurs", "arrive", "arrives", "decline", "declines", "vary",
    "varies", "lead", "leads", "pay", "pays", "matter", "matters",
}


def _verb_forms(lemmas: Set[str]) -> Set[str]:
    forms: Set[str] = set()
    for v in lemmas:
        forms.add(v)
        forms.update({v + "s", v + "es", v + "ed", v + "ing"})
        if v.endswith("e"):
            forms.update({v[:-1] + "es", v[:-1] + "ed", v[:-1] + "ing"})
        if v.endswith("y"):
            forms.add(v[:-1] + "ies")
    return forms


VERB_FORMS: Set[str] = _verb_forms(ACTION_VERBS | LEXICAL_VERBS | {
    "help", "allow", "provide", "support", "include", "require", "reveal",
    "contain", "mention", "combine", "understand", "request", "invite",
    "connect", "complete", "summarize", "interpret", "guide", "unlock",
})
GERUND_FORMS: Set[str] = {v for v in VERB_FORMS if v.endswith("ing")}
FINITE_VERB_FORMS: Set[str] = VERB_FORMS - GERUND_FORMS

# -ing/-ed words that are really nouns/adjectives (allowed inside an NP).
ING_ED_NOUNS: Set[str] = {
    "marketing", "branding", "onboarding", "training", "ranking", "rankings",
    "pricing", "billing", "listing", "listings", "meeting", "meetings",
    "setting", "settings", "building", "buildings", "reporting", "advertising",
    "engineering", "accounting", "funding", "spending", "earnings", "savings",
    "tracking", "planning", "screening", "linking", "booking", "shipping",
    "parking", "cleaning", "coaching", "consulting", "hosting", "streaming",
    "messaging", "packaging", "staffing", "lending", "trading", "investing",
    "budgeting", "forecasting", "scheduling", "advanced", "automated",
    "integrated", "detailed", "dedicated", "related", "recommended",
    "estimated", "extended", "timed", "recorded",
}

# ---------------------------------------------------------------------------
# Heads & modifiers — the usefulness booster vocabulary (seeded across niches)
# ---------------------------------------------------------------------------

GENERIC_WEAK_HEADS: Set[str] = {
    "thing", "things", "stuff", "way", "ways", "part", "parts", "case",
    "cases", "point", "points", "area", "areas", "lot", "bit", "kind",
    "kinds", "sort", "sorts", "one", "ones", "matter", "fact", "facts",
    "idea", "ideas", "reason", "reasons", "answer", "answers", "friend", "friends", "length", "result",
    "results", "example", "examples",  # weak as a *bare* head
}

# Strong concept heads — a phrase ending here is a real anchor.
STRONG_HEADS: Set[str] = {
    # SaaS / SEO / tech
    "software", "tool", "tools", "platform", "system", "systems", "strategy",
    "workflow", "automation", "integration", "pipeline", "dashboard", "api",
    "app", "application", "plugin", "extension", "database", "storage",
    "security", "keyword", "keywords", "content", "backlink", "backlinks",
    "audit", "optimization", "conversion", "page", "pages", "traffic",
    "ranking", "rankings", "analytics", "cluster", "clusters", "schema",
    # finance / legal
    "rate", "rates", "forecast", "tax", "taxes", "investment", "lease",
    "agreement", "contract", "property", "mortgage", "insurance", "calculator",
    "policy", "compliance", "revenue", "budget", "portfolio", "loan", "loans",
    "invoice", "invoices", "deduction", "deductions", "liability",
    # ecommerce / travel
    "checkout", "subscription", "pricing", "menu", "reservation", "restaurant",
    "hotel", "rental", "product", "products", "customer", "customers",
    "itinerary", "booking", "flight", "flights", "destination", "package",
    "inventory", "fulfillment", "shipping", "cart",
    # education
    "course", "courses", "lesson", "lessons", "training", "curriculum",
    "syllabus", "assignment", "exam", "exams", "grade", "grades",
    # health / fertility
    "symptoms", "causes", "treatment", "medication", "dosage", "therapy",
    "diagnosis", "condition", "ovulation", "fertility", "pregnancy", "period",
    "periods", "cycle", "cycles", "mucus", "temperature", "conception",
    "trimester", "phase", "phases", "window", "calculator", "kit", "kits",
    "predictor", "hormone", "hormones",
    # universal anchors
    "checklist", "service", "services", "report", "analysis", "assessment",
    "plan", "plans", "template", "framework", "model", "engine", "module",
    "feature", "features", "component", "guide", "benefits", "estimate",
    "schedule", "routine", "process", "method", "methods", "comparison",
    "management", "prevention", "solution", "length", "date", "patterns",
}

# Heads that are okay only when well-qualified.
GENERIC_BUT_ALLOWED_HEADS: Set[str] = {
    "time", "day", "days", "option", "options", "care", "score", "trend",
    "trends", "signal", "signals", "category", "categories", "step", "steps",
}

# Modifier words that, in front of a head, signal a real concept.
STRONG_MODIFIERS: Set[str] = {
    "pricing", "landing", "checkout", "subscription", "onboarding",
    "management", "marketing", "analytics", "email", "project", "technical",
    "conversion", "setup", "customer", "saas", "enterprise", "security",
    "billing", "internal", "external", "keyword", "content", "product",
    "support", "usage", "search", "brand", "branded", "trial", "demo",
    "cash", "flow", "blood", "pressure", "cervical", "fertile", "fertility",
    "ovulation", "luteal", "follicular", "menstrual", "basal", "hormonal",
    "birth", "real", "credit", "interest", "rental", "machine", "supply",
    "social", "remote", "legal", "medical", "clinical", "commercial",
    "digital", "online", "mobile", "annual", "monthly", "quarterly",
}

# ---------------------------------------------------------------------------
# Known compounds — bypass generic checks (these are *always* good anchors)
# ---------------------------------------------------------------------------

VALID_ORDERED_PAIRS: Set[Tuple[str, str]] = {
    ("cash", "flow"), ("blood", "pressure"), ("internal", "linking"),
    ("external", "linking"), ("search", "intent"), ("supply", "chain"),
    ("remote", "work"), ("content", "marketing"), ("email", "marketing"),
    ("social", "media"), ("machine", "learning"), ("artificial", "intelligence"),
    ("real", "estate"), ("credit", "card"), ("credit", "cards"),
    ("interest", "rate"), ("interest", "rates"), ("rental", "agreement"),
    ("lease", "agreement"), ("category", "pages"), ("product", "pages"),
    ("side", "effects"), ("risk", "management"), ("customer", "service"),
    ("data", "security"), ("keyword", "research"), ("conversion", "rate"),
    ("study", "plan"), ("learning", "platform"), ("progress", "tracking"),
    ("fertile", "window"), ("cycle", "length"), ("follicular", "phase"),
    ("luteal", "phase"), ("cervical", "mucus"), ("menstrual", "period"),
    ("basal", "body"), ("body", "temperature"), ("birth", "control"),
    ("fertility", "tracking"), ("ovulation", "predictor"),
    ("ovulation", "calculator"), ("expected", "ovulation"),
    ("irregular", "periods"), ("due", "date"), ("egg", "white"),
}

CANONICAL_ANCHOR_PHRASES: Set[str] = {
    "cash flow", "cash flow management", "blood pressure", "internal linking",
    "search intent", "category pages", "product pages", "rental agreement",
    "lease agreement", "side effects", "supply chain", "remote work",
    "content marketing", "email marketing", "machine learning",
    "risk management", "customer service", "data security", "keyword research",
    "conversion rate", "fertile window", "cycle length", "follicular phase",
    "luteal phase", "cervical mucus", "cervical mucus tracking",
    "egg white cervical mucus", "ovulation predictor kits", "expected ovulation",
    "irregular periods", "birth control", "hormonal birth control",
    "fertility tracking", "basal body temperature", "fertility awareness",
    "fertility awareness methods", "ovulation calculator",
}


def has_valid_ordered_pair(tokens: List[str]) -> bool:
    return any(pair in VALID_ORDERED_PAIRS for pair in zip(tokens, tokens[1:]))


def contains_canonical_anchor(tokens: List[str]) -> str:
    phrase = " ".join(tokens)
    for core in sorted(CANONICAL_ANCHOR_PHRASES, key=lambda x: len(x.split()), reverse=True):
        if core == phrase or f" {core} " in f" {phrase} " or phrase.startswith(core + " ") or phrase.endswith(" " + core):
            return core
    return ""


def is_exact_canonical_anchor(tokens: List[str]) -> bool:
    return " ".join(tokens) in CANONICAL_ANCHOR_PHRASES

WEAK_NON_ANCHOR_MODIFIERS = {
    "best", "working", "official", "estimated", "known", "early",
    "right", "new", "many", "next", "formal",
}

# Weak generic heads that should not survive unless part of a canonical/ordered anchor.
EXTRA_WEAK_GENERIC_HEADS = {
    "method", "methods", "routine", "routines", "approach", "approaches",
    "plan", "plans", "version", "versions", "average", "number", "numbers",
    "evaluation", "evaluations", "situation", "situations", "month", "months",
    "skill", "skills", "option", "options", "moment", "moments",
    "phrase", "phrases", "search", "searches", "instruction", "instructions",
    "takeaway", "takeaways", "bar", "layer", "layers", "rhythm",
    "data", "sign", "signs", "biology", "tenths", "experience", "anchor", "range",
}

NARRATIVE_FRAGMENT_WORDS = {
    "different", "playbook", "convert", "rough", "trickier", "recent",
    "history", "april", "stretches", "same", "subtraction", "rule",
    "single", "exact", "raw", "spans", "several",
}
