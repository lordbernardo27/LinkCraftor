from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple, Set

# Conservative stopwords for URL phrase generation
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "if", "in", "into", "is", "it",
    "of", "on", "or", "our", "out", "so", "than", "that", "the", "their", "then", "there", "these", "this",
    "to", "too", "up", "was", "we", "were", "what", "when", "where", "which", "who", "why", "with", "you", "your",
}

# Tokens we never want from URLs
_URL_JUNK_TOKENS = {
    "amp", "utm", "ref", "src", "fbclid", "gclid", "share", "index", "html", "php",
}

# Common non-post path segments to ignore
_DROP_SEGMENTS = {
    "blog", "blogs", "post", "posts", "article", "articles", "news", "insights",
    "category", "categories", "tag", "tags", "author", "authors", "page",
}

# Stronger blacklist to avoid generic/low-signal outputs
_GENERIC_BAD_PHRASES = {
    "things", "avoid", "high", "low", "how to", "what is", "things to", "things to avoid",
}

# Tokens that are too generic to be part of a Strong phrase (especially at ends)
_GENERIC_TOKENS = {
    "thing", "things", "avoid", "guide", "tips", "help", "best", "top", "ways", "what", "how",
}

# Single-token Strong allowlist (seed list; expand later)
# We keep this conservative: real entities/terms should be here.
_SINGLE_TOKEN_ALLOW = {
    "amlodipine", "lisinopril", "losartan", "metformin", "ibuprofen", "pregnancy", "ovulation",
}

# Glue words that frequently create awkward slug phrases (we avoid them inside phrases)
_GLUE_WORDS = {"on", "to", "for", "with", "in", "at", "by", "from", "of", "and", "or"}

_multi_space = re.compile(r"\s+")
_non_word = re.compile(r"[^a-z0-9]+")

# Runtime-populated protected phrase set.
# Keep empty by default so this module stays safe to import.
PROTECTED_SET: Set[str] = set()


def set_protected_phrase_set(values: Set[str] | List[str] | Tuple[str, ...]) -> None:
    """
    Optional runtime hook for callers to inject protected phrases.
    Example sources later:
      - imported phrase pool
      - live-domain phrase pool
      - draft topics / aliases
      - entity seeds / heading phrases
    """
    global PROTECTED_SET
    clean: Set[str] = set()
    for v in values or []:
        n = _norm_phrase(str(v or ""))
        if n:
            clean.add(n)
    PROTECTED_SET = clean


def clear_protected_phrase_set() -> None:
    """
    Explicit reset helper so each page/job can start from a clean protected set.
    """
    global PROTECTED_SET
    PROTECTED_SET = set()


def _norm_phrase(s: str) -> str:
    s = (s or "").strip().lower()
    s = _multi_space.sub(" ", s)
    return s


def _tokenize_slug(slug: str) -> List[str]:
    raw = (slug or "").strip().lower()
    raw = raw.replace("_", "-")
    parts = [p for p in raw.split("-") if p]
    out: List[str] = []
    for t in parts:
        t = _non_word.sub("", t)
        if not t:
            continue
        if t in _URL_JUNK_TOKENS:
            continue
        if t.isdigit():
            continue
        if len(t) < 2:
            continue
        out.append(t)
    return out


def _pick_slug_segment(path: str) -> str:
    """
    Take the last meaningful segment in the path, excluding common non-post segments.
    """
    segs = [s for s in (path or "").split("/") if s.strip()]
    if not segs:
        return ""
    meaningful = [s for s in segs if s.strip().lower() not in _DROP_SEGMENTS]
    if not meaningful:
        meaningful = segs
    return meaningful[-1].strip()

def _collect_norms(*groups: List[Dict[str, Any]]) -> Set[str]:
    """
    Collect normalized phrases from generated records.
    Includes both record.norm and normalized aliases.
    Filters out weak cores so PROTECTED_SET stays strong.
    """
    out: Set[str] = set()

    for group in groups:
        for rec in group or []:
            norm = _norm_phrase(str(rec.get("norm") or ""))
            if norm:
                toks = norm.split()

                # keep only stronger cores
                if len(toks) >= 3 and norm not in {"pregnancy", "due date"}:
                    out.add(norm)

            for alias in rec.get("aliases") or []:
                an = _norm_phrase(str(alias or ""))
                if an:
                    toks = an.split()

                    # keep only stronger alias cores
                    if len(toks) >= 3 and an not in {"pregnancy", "due date"}:
                        out.add(an)

    return out


def survives_protected_core(phrase: str, protected_set: Set[str]) -> bool:
    """
    Phrase survives if:
      - exact protected match, or
      - contains a protected core as a contiguous token span,
        with no weak boundary token immediately adjacent.

    Important:
    - token-based matching, not raw substring matching
    - safe default: if protected_set is empty, return True so existing
      generation does not silently collapse until caller wires the set
    """
    p = _norm_phrase(phrase)
    if not p:
        return False

    if not protected_set:
        return True

    toks = p.split()

    for core in protected_set:
        core_norm = _norm_phrase(core)
        if not core_norm:
            continue

        core_toks = core_norm.split()

        # exact match
        if p == core_norm:
            return True

        # token-level contiguous match
        max_i = len(toks) - len(core_toks) + 1
        for i in range(max_i):
            if toks[i:i + len(core_toks)] == core_toks:
                left = toks[:i]
                right = toks[i + len(core_toks):]

                # reject phrases that are shorter or equal to the core
                if len(toks) <= len(core_toks):
                    continue

                # reject weak immediate boundary around the core
                if left and left[-1] in _STOPWORDS:
                    continue
                if right and right[0] in _STOPWORDS:
                    continue

                return True

    return False


def generate_strong_phrases_from_url(url: str) -> List[Dict[str, Any]]:
    """
    URL → Strong phrase candidates (generator only).
    Returns list of phrase records:
      { phrase, norm, bucket, type, confidence, aliases[] }
    """
    u = (url or "").strip()
    if not u:
        return []

    if "://" not in u:
        u = "https://" + u

    parsed = urlparse(u)
    path = parsed.path or ""
    slug = _pick_slug_segment(path)
    tokens = _tokenize_slug(slug)
    if not tokens:
        return []

    # contiguous n-grams 2..5
    candidates: List[Tuple[str, List[str]]] = []
    n_max = min(5, len(tokens))
    for n in range(2, n_max + 1):
        for i in range(0, len(tokens) - n + 1):
            window = tokens[i:i + n]
            candidates.append((" ".join(window), window))

    # Single token: allow only if it looks like an entity (conservative v1)
    for t in tokens:
        if t in _STOPWORDS or t in _URL_JUNK_TOKENS:
            continue
        if len(t) >= 6:
            candidates.append((t, [t]))

    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for phrase, _toks in candidates:
        norm = _norm_phrase(phrase)
        if not norm:
            continue
        if norm in seen:
            continue

        words = norm.split()
        if not words:
            continue

        if words[0] in _GENERIC_TOKENS or words[-1] in _GENERIC_TOKENS:
            continue

        if len(words) == 2 and words[0] in {"high", "low"}:
            continue

        if len(words) == 1 and words[0] not in _SINGLE_TOKEN_ALLOW:
            continue

        if any(w in _GLUE_WORDS for w in words[1:-1]):
            continue

        if words[0] in _STOPWORDS or words[-1] in _STOPWORDS:
            continue

        stop_count = sum(1 for w in words if w in _STOPWORDS)
        if (stop_count / len(words)) > 0.40:
            continue

        if norm in _GENERIC_BAD_PHRASES:
            continue

        if all(w in _STOPWORDS for w in words):
            continue

        if len(words) == 1:
            conf = 0.75
        elif len(words) == 5:
            conf = 0.85
        else:
            conf = 0.90

        rec = {
            "phrase": phrase,
            "norm": norm,
            "bucket": "internal_strong",
            "type": "live_url_slug",
            "confidence": float(conf),
            "aliases": [],
        }
        out.append(rec)
        seen.add(norm)

    out.sort(
        key=lambda r: (r.get("confidence", 0.0), len(str(r.get("norm", "")).split())),
        reverse=True,
    )
    return out


def generate_strong_phrases_from_h1(h1: str) -> List[Dict[str, Any]]:
    """
    H1 → Strong phrase candidates (generator only).
    - Does NOT highlight the raw H1.
    - Generates qualified topic phrases from the H1.
    Returns phrase records:
      { phrase, norm, bucket, type, confidence, aliases[] }
    """
    raw = (h1 or "").strip()
    if not raw:
        return []

    s = raw.replace("—", ":").replace("–", ":").replace("|", ":").replace("•", ":")
    s = _multi_space.sub(" ", s).strip()

    parts = [p.strip() for p in s.split(":") if p.strip()]
    main = parts[0] if parts else s

    main_clean = main.strip(" -–—:;,.")
    main_norm = _norm_phrase(main_clean)

    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def _add_phrase(display: str, conf: float, aliases: List[str] | None = None) -> None:
        d = (display or "").strip()
        if not d:
            return
        n = _norm_phrase(d)
        if not n or n in seen:
            return

        words = n.split()
        if not words:
            return

        if words[0] in _STOPWORDS or words[-1] in _STOPWORDS:
            return
        if words[0] in _GENERIC_TOKENS or words[-1] in _GENERIC_TOKENS:
            return
        if len(words) > 7:
            return
        if any(w in _GLUE_WORDS for w in words[1:-1]):
            return
        if len(words) == 1 and words[0] in _GENERIC_BAD_PHRASES:
            return

        rec = {
            "phrase": d,
            "norm": n,
            "bucket": "internal_strong",
            "type": "live_h1",
            "confidence": float(conf),
            "aliases": [],
        }

        if aliases:
            clean_aliases = []
            seen_aliases: Set[str] = set()
            for a in aliases:
                a2 = (a or "").strip()
                if not a2:
                    continue
                an = _norm_phrase(a2)
                if not an or an == n or an in seen_aliases:
                    continue
                clean_aliases.append(a2)
                seen_aliases.add(an)
            rec["aliases"] = clean_aliases[:8]

        out.append(rec)
        seen.add(n)

    if main_norm:
        _add_phrase(main_clean, 0.95)

    if len(parts) >= 2 and main_norm:
        tail = ":".join(parts[1:]).strip()
        tail = tail.replace(" and ", ", ")
        bits = [b.strip(" -–—:;,.") for b in tail.split(",") if b.strip()]
        for b in bits:
            b_norm = _norm_phrase(b)
            if not b_norm:
                continue
            phrase = f"{main_clean} {b}".strip()
            _add_phrase(phrase, 0.90)

    out.sort(
        key=lambda r: (r.get("confidence", 0.0), len(str(r.get("norm", "")).split())),
        reverse=True,
    )
    return out


def generate_optional_phrases_from_headings(
    headings: List[str],
    heading_level: str = "h2",
) -> List[Dict[str, Any]]:
    """
    H2/H3 headings → Semantic/Optional phrase candidates.

    Key behavior:
    - More permissive than Strong.
    - Keeps the heading (cleaned) AND generates normalized aliases:
        "How amlodipine works" -> "amlodipine works"
        "When to see a doctor" -> "see a doctor"
        "Risk factors for hypertension" -> "risk factors hypertension"
    Output:
      { phrase, norm, bucket="semantic_optional", type="heading_h2|heading_h3", confidence, aliases[] }
    """
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    typ = "heading_h2" if heading_level.lower() == "h2" else "heading_h3"
    base_conf = 0.78 if typ == "heading_h2" else 0.74

    _lead_drop = {"how", "when", "why", "what", "which", "who", "where"}
    _drop_words = {"to"}

    def _clean(s: str) -> str:
        s = (s or "").strip()
        s = s.replace("—", ":").replace("–", ":").replace("|", ":").replace("•", ":")
        s = _multi_space.sub(" ", s).strip()
        return s.strip(" -–—:;,.").strip()

    def _strip_parenthetical(s: str) -> str:
        return re.sub(r"\([^)]*\)", "", s).strip()

    def _make_core_variant(display: str) -> str:
        d = _norm_phrase(display)
        words = d.split()
        if not words:
            return ""

        if words[0] in _lead_drop:
            words = words[1:]
            if words and words[0] in _drop_words:
                words = words[1:]

        words = [w for w in words if w not in _GLUE_WORDS]
        core = " ".join(words).strip()
        return core

    def _add(display: str, conf: float, aliases: List[str]) -> None:
        d = _clean(display)
        if not d:
            return

        n = _norm_phrase(d)
        if not n or n in seen:
            return

        words = n.split()
        if not words:
            return

        if len(words) < 2:
            return
        if len(words) > 10:
            return

        if all(w in _STOPWORDS for w in words):
            return

        rec = {
            "phrase": d,
            "norm": n,
            "bucket": "semantic_optional",
            "type": typ,
            "confidence": float(conf),
            "aliases": [],
        }

        clean_aliases = []
        seen_a = set()
        for a in (aliases or []):
            a2 = _clean(a)
            an = _norm_phrase(a2)
            if not a2 or not an or an == n:
                continue
            if an in seen_a:
                continue
            clean_aliases.append(a2)
            seen_a.add(an)

        rec["aliases"] = clean_aliases[:10]
        out.append(rec)
        seen.add(n)

    for h in headings or []:
        raw = _clean(h)
        if not raw:
            continue

        base_display = _strip_parenthetical(raw)
        aliases: List[str] = []

        if base_display != raw:
            aliases.append(base_display)

        core = _make_core_variant(base_display)
        if core and core != _norm_phrase(base_display):
            aliases.append(core)

        if ":" in base_display:
            parts = [p.strip() for p in base_display.split(":") if p.strip()]
            if len(parts) >= 2:
                combo = _clean(parts[0] + " " + parts[1])
                if combo:
                    aliases.append(combo)

        _add(base_display, base_conf, aliases)

    out.sort(
        key=lambda r: (r.get("confidence", 0.0), len(str(r.get("norm", "")).split())),
        reverse=True,
    )
    return out


def generate_optional_phrases_from_body(text: str, max_phrases: int = 120) -> List[Dict[str, Any]]:
    """
    BODY TEXT → Semantic/Optional phrase candidates (clean, sentence-bounded).

    Key fix vs previous:
    - We DO NOT delete stopwords before n-gramming (that created false adjacency → junk phrases).
    - Instead, we keep the full token stream and only accept windows that contain ONLY content tokens.
    - Still: sentence-bounded, 2–3 words only, verb/glue filtered.

    New protected-core behavior:
    - If PROTECTED_SET is populated, windows must also survive the protected-core gate.
    - If PROTECTED_SET is empty, existing generation behavior is preserved.
    """
    raw = (text or "").strip()
    if not raw:
        return []

    SENT_SPLIT = re.compile(r"(?:[.!?]+|[\r\n]+)+\s*")

    WORD_RE = re.compile(r"[a-z0-9]+")
    STOP = _STOPWORDS

    BAD_TOKENS = {
        "is", "are", "was", "were", "be", "been", "being",
        "include", "includes", "including",
        "use", "used", "using",
        "increase", "increases", "increased",
        "vary", "varies", "varied",
        "discuss", "discusses", "discussed",
        "require", "requires", "required",
        "need", "needs", "needed",
        "seek", "seeks", "seeking",
        "options", "option",
        "common", "often", "sometimes", "many", "most", "some",
    }

    BAD_STARTERS = {
        "common", "often", "sometimes", "many", "most", "some",
        "this", "that", "these", "those", "article", "people",
    }

    HEAD_NOUNS = {"risk", "treatment", "therapy", "care", "diagnosis", "management", "options"}

    BAD_BIGRAMS = {
        ("options", "seek"),
        ("need", "more"),
        ("more", "one"),
        ("works", "common"),
        ("common", "side"),
        ("side", "effects"),
    }
    BAD_TRIGRAMS = {
        ("need", "more", "one"),
        ("works", "common", "side"),
        ("options", "seek", "urgent"),
    }

    def _words(s: str) -> List[str]:
        return WORD_RE.findall((s or "").lower())

    def _is_content_token(w: str) -> bool:
        if not w:
            return False
        if w in STOP:
            return False
        if w in _GLUE_WORDS:
            return False
        if w in BAD_TOKENS:
            return False
        if len(w) < 3:
            return False
        if w.isdigit():
            return False
        return True

    def _good_window(ws: List[str]) -> bool:
        if len(ws) < 2 or len(ws) > 3:
            return False

        if not all(_is_content_token(w) for w in ws):
            return False

        if ws[0] in BAD_STARTERS:
            return False

        if len(ws) == 2 and tuple(ws) in BAD_BIGRAMS:
            return False
        if len(ws) == 3 and tuple(ws) in BAD_TRIGRAMS:
            return False

        if ws[-1] in HEAD_NOUNS:
            if not any(len(w) >= 5 for w in ws[:-1]):
                return False

        return True

    sentences = [s.strip() for s in SENT_SPLIT.split(raw) if s.strip()]
    if not sentences:
        sentences = [raw]

    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []

    for sent in sentences:
        toks = _words(sent)
        if len(toks) < 2:
            continue

        # build n-grams from the ORIGINAL token stream (no collapsing)
        for n in (3, 2):  # prefer 3-grams first, then 2-grams
            for i in range(0, len(toks) - n + 1):
                window = toks[i:i + n]

                if not _good_window(window):
                    continue

                phrase_str = " ".join(window)

                # PROTECTED CORE GATE
                if not survives_protected_core(phrase_str, PROTECTED_SET):
                    continue

                norm = _norm_phrase(phrase_str)
                if not norm or norm in seen:
                    continue

                conf = 0.64 if n == 3 else 0.60
                out.append({
                    "phrase": phrase_str,
                    "norm": norm,
                    "bucket": "semantic_optional",
                    "type": "body_phrase",
                    "confidence": float(conf),
                    "aliases": [],
                })
                seen.add(norm)

                if len(out) >= max_phrases:
                    break

            if len(out) >= max_phrases:
                break

        if len(out) >= max_phrases:
            break

    out.sort(
        key=lambda r: (
            len(str(r.get("norm", "")).split()),
            float(r.get("confidence", 0.0)),
        ),
        reverse=True,
    )
    return out[:max_phrases]


def generate_phrase_bundle_for_page(
    *,
    url: str,
    h1: str,
    h2_headings: List[str] | None = None,
    h3_headings: List[str] | None = None,
    body_text: str = "",
    max_body_phrases: int = 120,
    extra_protected_values: Set[str] | List[str] | Tuple[str, ...] | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    One-call orchestrator for a page.

    This is the wiring you were missing:
    1. Generate strong URL phrases
    2. Generate strong H1 phrases
    3. Generate optional H2/H3 heading phrases
    4. Build protected phrase set from those outputs
    5. Generate body phrases using the protected-core gate
    """

    url_phrases = generate_strong_phrases_from_url(url)
    h1_phrases = generate_strong_phrases_from_h1(h1)
    h2_phrases = generate_optional_phrases_from_headings(h2_headings or [], heading_level="h2")
    h3_phrases = generate_optional_phrases_from_headings(h3_headings or [], heading_level="h3")

    protected_values = _collect_norms(url_phrases, h1_phrases, h2_phrases, h3_phrases)

    for v in extra_protected_values or []:
        n = _norm_phrase(str(v or ""))
        if n:
            protected_values.add(n)

    # Ensure protected set is always active for this generation
    set_protected_phrase_set(protected_values)

    print("DEBUG PROTECTED_SET SIZE:", len(PROTECTED_SET))
    print("DEBUG SAMPLE:", list(PROTECTED_SET)[:10])

    # DEBUG (optional)
    # print("PROTECTED_SET SIZE:", len(PROTECTED_SET))

    body_phrases = generate_optional_phrases_from_body(
        body_text,
        max_phrases=max_body_phrases,
    )

    return {
        "url_phrases": url_phrases,
        "h1_phrases": h1_phrases,
        "h2_phrases": h2_phrases,
        "h3_phrases": h3_phrases,
        "body_phrases": body_phrases,
    }