"""Universal DOM article reconstruction.

Reconstructs ordered article headings and paragraphs from valid,
malformed and component-based HTML.

Changes in v1.4 (review fixes):
    * ``_node_text`` now inserts word separators at block-element
      boundaries (``<p>Hello</p><p>World</p>`` -> ``Hello World``)
      while still joining inline splits (``M<span>ost</span>`` ->
      ``Most``). Previously all block text was concatenated with no
      separator, corrupting word counts, link density and root
      scoring.
    * Removed the double entity unescape. BeautifulSoup already
      decodes entities, so ``html.unescape`` was corrupting text
      that legitimately displays ``&amp;`` / ``&lt;div&gt;``.
    * ``_remove_noise_nodes`` no longer touches nodes that were
      already destroyed when an ancestor was decomposed.
    * Generic containers that emit a text block are recorded as
      "consumed" so their descendant ``span``/``div``/``a`` nodes
      cannot emit the same text again as a duplicate block.
    * Terminal-metadata matches that occur too early in the
      document are now skipped instead of retained as content.
    * Duplicate detection is global (seen-set) instead of
      adjacent-only, catching hero/teaser text repeated later in
      the page. Identical repeated text is treated as DOM
      duplication.
    * Site-specific patterns (previously hardcoded) are moved into
      an injectable :class:`ReconstructionProfile`; the core engine
      keeps only generic patterns. A ``WHAT_TO_EXPECT_PROFILE``
      example preserves the old site-specific behavior.
    * Overly broad bare signal terms (``body``, ``text``) removed
      from ``CONTENT_SIGNAL_TERMS`` -- they matched utility classes
      such as ``modal-body`` and ``text-center``. Compound terms
      like ``article-body`` still match those class names.
    * Subtree text is memoized per node, avoiding repeated full
      text walks during candidate scoring.
    * Scoring weights and thresholds are named module constants.
    * Added ``figcaption``, ``pre``, ``dt`` and ``dd`` as explicit
      block sources. Removed dead code (``_signal_tokens``).

Known limitations (by design, not silently):
    * ``<table>`` content is not reconstructed into blocks.
    * ``<figure>`` images/media are not represented; only their
      ``<figcaption>`` text is kept.
    * Whitespace inside ``<pre>`` is collapsed like normal prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag


ENGINE_NAME = "universal_dom_article_reconstruction_engine_v1_5"
PARSER_NAME = "html5lib"


# ---------------------------------------------------------------------------
# Scoring weights and thresholds
# ---------------------------------------------------------------------------

HEADING_SCORE_WEIGHT = 45.0
PARAGRAPH_SCORE_WEIGHT = 24.0
LIST_ITEM_SCORE_WEIGHT = 4.0
BLOCKQUOTE_SCORE_WEIGHT = 12.0

ARTICLE_TAG_BONUS = 140.0
MAIN_TAG_BONUS = 120.0
SECTION_TAG_BONUS = 25.0
BODY_TAG_PENALTY = 80.0
CONTENT_SIGNAL_BONUS = 90.0

LINK_DENSITY_PENALTY_FACTOR = 1.35

MIN_ROOT_WORD_COUNT = 100
SHORT_ROOT_PENALTY = 500.0
EMPTY_STRUCTURE_PENALTY = 300.0

# Generic leaf containers must look like prose: at least this many
# words, unless they carry a heading signal.
MIN_LEAF_PARAGRAPH_WORDS = 7

# Headings recovered from signals (not <h*> tags) must be short.
MIN_SIGNAL_HEADING_WORDS = 1
MAX_SIGNAL_HEADING_WORDS = 18

# A descendant block with at least this many words makes a generic
# container non-leaf.
SUBSTANTIAL_DESCENDANT_MIN_WORDS = 3

# A terminal-metadata match before this many retained blocks is
# treated as a false positive and skipped rather than truncating.
MIN_TERMINAL_METADATA_INDEX = 15

# How many ancestor levels to inspect for navigation-list signals.
NAVIGATION_ANCESTOR_LEVELS = 4


# ---------------------------------------------------------------------------
# Tag sets
# ---------------------------------------------------------------------------

NOISE_TAGS = frozenset({
    "script",
    "style",
    "noscript",
    "template",
    "svg",
    "canvas",
    "iframe",
    "form",
    "nav",
    "footer",
})

# Inline elements whose boundaries must NOT introduce a word break.
# Everything else is treated as a block boundary in `_node_text`.
INLINE_TEXT_TAGS = frozenset({
    "a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "del",
    "dfn", "em", "font", "i", "ins", "kbd", "mark", "q", "rp", "rt",
    "rtc", "ruby", "s", "samp", "small", "span", "strong", "sub",
    "sup", "time", "u", "var", "wbr",
})

HEADING_TAG_NAMES = ("h1", "h2", "h3", "h4", "h5", "h6")

EXPLICIT_BLOCK_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "li", "blockquote",
    "figcaption", "pre", "dt", "dd",
})

GENERIC_CONTAINER_TAGS = frozenset({"div", "section", "span"})

LINKED_HEADING_TAGS = frozenset({"a"})

_CANDIDATE_BLOCK_TAGS = (
    EXPLICIT_BLOCK_TAGS
    | GENERIC_CONTAINER_TAGS
    | LINKED_HEADING_TAGS
)

# Descendant blocks that disqualify a generic container from being
# treated as a leaf paragraph.
_SUBSTANTIAL_DESCENDANT_TAGS = [
    "div", "section", "article",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "li", "blockquote",
    "figcaption", "pre", "dt", "dd",
]


# ---------------------------------------------------------------------------
# Signal terms (generic only -- site specifics belong in a profile)
# ---------------------------------------------------------------------------

NOISE_SIGNAL_TERMS = frozenset({
    "ads",
    "advertisement",
    "ad-container",
    "ad-wrapper",
    "ad-slot",
    "affiliate",
    "breadcrumb",
    "breadcrumbs",
    "cookie",
    "consent",
    "footer",
    "inline-form",
    "lightbox",
    "newsletter",
    "pagination",
    "promo",
    "recommended-products",
    "share",
    "sharing",
    "signup",
    "social",
    "sponsored",
    "subscribe",
    "video-player",
    "jw-player",
    "community-discussion",
    "comments",
})

# NOTE: bare "body" and "text" were removed intentionally. As
# single-token terms they matched utility classes such as
# `modal-body`, `card-body` and `text-center`, granting the content
# bonus to arbitrary widgets. Compound terms like `article-body`
# and `story-body` still match those class names via token matching.
CONTENT_SIGNAL_TERMS = frozenset({
    "article",
    "article-body",
    "article-content",
    "article-text",
    "content",
    "copy",
    "description",
    "entry-content",
    "main-content",
    "post-content",
    "story",
    "story-body",
    "story-text",
})

HEADING_SIGNAL_TERMS = frozenset({
    "headline",
    "heading",
    "title",
    "subheading",
    "subtitle",
})

NAVIGATION_SIGNAL_TERMS = frozenset({
    "nav",
    "navigation",
    "menu",
    "tab",
    "tabs",
    "toc",
    "table-of-contents",
    "jump",
    "jump-links",
    "section-links",
    "explore",
})


# ---------------------------------------------------------------------------
# Generic patterns
# ---------------------------------------------------------------------------

GENERIC_METADATA_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*medically reviewed(?:\s+by)?\b", re.IGNORECASE),
    re.compile(r"^\s*fact[- ]checked(?:\s+by)?\b", re.IGNORECASE),
    re.compile(
        r"^\s*reviewed\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}\s*$",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*latest update\b", re.IGNORECASE),
    re.compile(r"^\s*medical review policy\b", re.IGNORECASE),
    re.compile(r"^\s*editorial policy\b", re.IGNORECASE),
    re.compile(r"medical review board includes", re.IGNORECASE),
    re.compile(
        r"^\s*all\b.{0,160}\bmedically reviewed by a team\b",
        re.IGNORECASE,
    ),
)

# Matched with `fullmatch` -- the whole block must be the UI label.
GENERIC_UI_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*previous item\s*$", re.IGNORECASE),
    re.compile(r"^\s*next item\s*$", re.IGNORECASE),
    re.compile(r"^\s*back to top\s*$", re.IGNORECASE),
    re.compile(r"^\s*see more\s*$", re.IGNORECASE),
    re.compile(r"^\s*read more\s*$", re.IGNORECASE),
    re.compile(r"^\s*recommended products\s*$", re.IGNORECASE),
)

GENERIC_TERMINAL_METADATA_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"^\s*from the .{0,120} editorial team\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:sources?|references?|bibliography)\s*$",
        re.IGNORECASE,
    ),
    re.compile(r"^\s*about the author\s*$", re.IGNORECASE),
    re.compile(r"^\s*our editorial process\s*$", re.IGNORECASE),
    re.compile(
        r"^\s*prices and details are accurate\b",
        re.IGNORECASE,
    ),
)


# ---------------------------------------------------------------------------
# Site profiles
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReconstructionProfile:
    """Site-specific extraction rules layered on top of the generic
    engine. All fields extend (never replace) the generic sets."""

    name: str = "generic"
    noise_signal_terms: tuple[str, ...] = ()
    metadata_patterns: tuple[re.Pattern[str], ...] = ()
    ui_patterns: tuple[re.Pattern[str], ...] = ()
    terminal_metadata_patterns: tuple[re.Pattern[str], ...] = ()


GENERIC_PROFILE = ReconstructionProfile()

# Example profile. These patterns were previously hardcoded into the
# "universal" engine but target one specific publisher; they now do
# nothing unless this profile is passed in explicitly.
WHAT_TO_EXPECT_PROFILE = ReconstructionProfile(
    name="whattoexpect",
    noise_signal_terms=(
        "fact-checker-modal",
        "new-jump-links",
        "products-summary",
        "legal-disclosure",
        "products-jump-links",
        "why-trust-us-section",
        "article-feedback",
        "related-topics",
    ),
    metadata_patterns=(
        re.compile(
            r"^\s*we believe you should always know the source\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*learn more about our editorial and medical "
            r"review policies\b",
            re.IGNORECASE,
        ),
    ),
    ui_patterns=(
        re.compile(
            r"^\s*birth month group discussions\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*explore(?:\s+pregnancy)?(?:\s+week\s+\d+)?\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*track your symptoms with the my journal tool\b.*$",
            re.IGNORECASE,
        ),
    ),
    terminal_metadata_patterns=(
        re.compile(
            r"^\s*what to expect selects products\b",
            re.IGNORECASE,
        ),
    ),
)


# Internal: resolved (generic + profile) rule set threaded through
# the pipeline so patterns are merged exactly once per call.
PROFILE_BY_HOST: dict[str, ReconstructionProfile] = {
    "whattoexpect.com": WHAT_TO_EXPECT_PROFILE,
    "www.whattoexpect.com": WHAT_TO_EXPECT_PROFILE,
}


def _resolve_profile_for_url(
    url: str,
    explicit_profile: ReconstructionProfile | None,
) -> ReconstructionProfile:
    """Resolve an explicitly supplied profile first, otherwise use
    a registered hostname profile and finally the generic profile."""

    if explicit_profile is not None:
        return explicit_profile

    hostname = (
        urlparse(str(url or ""))
        .hostname
        or ""
    ).casefold().strip(".")

    return PROFILE_BY_HOST.get(
        hostname,
        GENERIC_PROFILE,
    )


@dataclass(frozen=True)
class _ResolvedRules:
    noise_signal_terms: frozenset[str]
    metadata_patterns: tuple[re.Pattern[str], ...]
    ui_patterns: tuple[re.Pattern[str], ...]
    terminal_metadata_patterns: tuple[re.Pattern[str], ...]


def _resolve_rules(
    profile: ReconstructionProfile,
) -> _ResolvedRules:
    return _ResolvedRules(
        noise_signal_terms=(
            NOISE_SIGNAL_TERMS
            | frozenset(
                str(term).casefold()
                for term in profile.noise_signal_terms
            )
        ),
        metadata_patterns=(
            GENERIC_METADATA_PATTERNS
            + tuple(profile.metadata_patterns)
        ),
        ui_patterns=(
            GENERIC_UI_PATTERNS
            + tuple(profile.ui_patterns)
        ),
        terminal_metadata_patterns=(
            GENERIC_TERMINAL_METADATA_PATTERNS
            + tuple(profile.terminal_metadata_patterns)
        ),
    )


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def _normalize_text(value: Any) -> str:
    # NOTE: no html.unescape here. BeautifulSoup already decodes
    # entities into NavigableStrings; unescaping again corrupted
    # text that legitimately displays "&amp;" or "&lt;div&gt;".
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def _node_text(
    node: Tag,
    cache: dict[int, str] | None = None,
) -> str:
    """Read visible text with correct word boundaries.

    Inline element boundaries do not break words; block element
    boundaries (and <br>) do:

        M<span>ost</span>            -> Most
        Journa<span>l</span>         -> Journal
        <p>Hello</p><p>World</p>     -> Hello World
        <li>One</li><li>Two</li>     -> One Two

    Subtree text is memoized in `cache` (keyed by id(node)) because
    candidate scoring reads overlapping subtrees repeatedly.
    """

    if cache is not None:
        cached = cache.get(id(node))
        if cached is not None:
            return cached

    parts: list[str] = []

    for descendant in node.descendants:
        if isinstance(descendant, NavigableString):
            parts.append(str(descendant))
            continue

        if isinstance(descendant, Tag):
            name = str(descendant.name or "").lower()

            if name == "br" or name not in INLINE_TEXT_TAGS:
                parts.append(" ")

    text = _normalize_text("".join(parts))

    if cache is not None:
        cache[id(node)] = text

    return text


def _clean_reconstructed_text(value: Any) -> str:
    """Remove attached interface labels without changing article
    wording or paragraph order."""

    text = _normalize_text(value)

    text = re.sub(
        r"(?:\s+(?:Read|Learn|See)\s+More)+[.!]?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    return text


def _word_count(value: str) -> int:
    return len(
        re.findall(
            r"\b[\w’'-]+\b",
            str(value or ""),
            flags=re.UNICODE,
        )
    )


# ---------------------------------------------------------------------------
# DOM signal matching
# ---------------------------------------------------------------------------

def _signal_text(node: Tag) -> str:
    values: list[str] = []

    node_id = node.get("id")
    if node_id:
        values.append(str(node_id))

    for value in node.get("class") or []:
        values.append(str(value))

    for key in (
        "role",
        "aria-label",
        "data-component",
        "data-module",
        "data-testid",
    ):
        value = node.get(key)

        if value:
            values.append(str(value))

    return " ".join(values).casefold()


def _contains_signal(
    node: Tag,
    terms: frozenset[str] | set[str],
) -> bool:
    """Match DOM identifiers safely.

    Exact identifier values are respected, while compound values
    such as article-content and your-body__body are also separated
    into meaningful tokens. Arbitrary substring matching is
    intentionally prohibited.
    """

    signal = _signal_text(node)

    if not signal:
        return False

    exact_values = {
        value
        for value in signal.split()
        if value
    }

    signal_tokens = {
        token
        for token in re.split(r"[^a-z0-9]+", signal)
        if token
    }

    for raw_term in terms:
        term = str(raw_term or "").casefold().strip()

        if not term:
            continue

        if term in exact_values:
            return True

        term_tokens = [
            token
            for token in re.split(r"[^a-z0-9]+", term)
            if token
        ]

        if (
            term_tokens
            and all(
                token in signal_tokens
                for token in term_tokens
            )
        ):
            return True

    return False


# ---------------------------------------------------------------------------
# Noise removal
# ---------------------------------------------------------------------------

def _is_noise_node(
    node: Tag,
    noise_signal_terms: frozenset[str],
) -> bool:
    if not isinstance(node, Tag) or not node.name:
        return False

    if str(node.name).lower() in NOISE_TAGS:
        return True

    return _contains_signal(node, noise_signal_terms)


def _remove_noise_nodes(
    root: Tag,
    noise_signal_terms: frozenset[str],
) -> int:
    removed = 0

    for node in list(root.find_all(True)):
        if not isinstance(node, Tag) or not node.name:
            continue

        # Skip nodes destroyed when an ancestor was decomposed.
        # Touching decomposed elements is undefined behavior in
        # bs4 and raises in newer versions.
        if getattr(node, "decomposed", False):
            continue

        if node.parent is None:
            continue

        if _is_noise_node(node, noise_signal_terms):
            node.decompose()
            removed += 1

    return removed


# ---------------------------------------------------------------------------
# Metadata / UI text filtering
# ---------------------------------------------------------------------------

def _is_metadata_or_ui(
    text: str,
    rules: _ResolvedRules,
) -> bool:
    normalized = _normalize_text(text)

    if not normalized:
        return True

    for pattern in rules.metadata_patterns:
        if pattern.search(normalized):
            return True

    for pattern in rules.ui_patterns:
        if pattern.fullmatch(normalized):
            return True

    return False


# ---------------------------------------------------------------------------
# Root candidate scoring
# ---------------------------------------------------------------------------

def _link_word_count(
    node: Tag,
    cache: dict[int, str],
) -> int:
    total = 0

    for link in node.find_all("a"):
        total += _word_count(_node_text(link, cache))

    return total


def _candidate_score(
    node: Tag,
    cache: dict[int, str],
) -> dict[str, Any]:
    text = _node_text(node, cache)
    words = _word_count(text)

    headings = len(node.find_all(list(HEADING_TAG_NAMES)))
    paragraphs = len(node.find_all("p"))
    list_items = len(node.find_all("li"))
    blockquotes = len(node.find_all("blockquote"))

    link_words = _link_word_count(node, cache)
    link_density = link_words / words if words else 1.0

    tag_name = str(node.name or "").lower()
    signal = _signal_text(node)

    score = float(words)

    score += headings * HEADING_SCORE_WEIGHT
    score += paragraphs * PARAGRAPH_SCORE_WEIGHT
    score += list_items * LIST_ITEM_SCORE_WEIGHT
    score += blockquotes * BLOCKQUOTE_SCORE_WEIGHT

    if tag_name == "article":
        score += ARTICLE_TAG_BONUS
    elif tag_name == "main":
        score += MAIN_TAG_BONUS
    elif tag_name == "section":
        score += SECTION_TAG_BONUS
    elif tag_name == "body":
        score -= BODY_TAG_PENALTY

    if _contains_signal(node, CONTENT_SIGNAL_TERMS):
        score += CONTENT_SIGNAL_BONUS

    score -= (
        link_density
        * max(words, 1)
        * LINK_DENSITY_PENALTY_FACTOR
    )

    if words < MIN_ROOT_WORD_COUNT:
        score -= SHORT_ROOT_PENALTY

    if headings == 0 and paragraphs == 0:
        score -= EMPTY_STRUCTURE_PENALTY

    return {
        "node": node,
        "tag": tag_name,
        "signal": signal,
        "word_count": words,
        "heading_count": headings,
        "paragraph_count": paragraphs,
        "list_item_count": list_items,
        "blockquote_count": blockquotes,
        "link_word_count": link_words,
        "link_density": round(link_density, 4),
        "score": round(score, 4),
    }


def _collect_root_candidates(
    soup: BeautifulSoup,
    cache: dict[int, str],
) -> list[dict[str, Any]]:
    nodes: list[Tag] = []
    seen: set[int] = set()

    def add(node: Tag | None) -> None:
        if not isinstance(node, Tag):
            return

        identity = id(node)

        if identity in seen:
            return

        seen.add(identity)
        nodes.append(node)

    add(soup.body)

    for node in soup.find_all(
        ["main", "article", "section", "div"]
    ):
        if not isinstance(node, Tag):
            continue

        tag_name = str(node.name or "").lower()

        heading_count = len(
            node.find_all(list(HEADING_TAG_NAMES))
        )

        should_consider = (
            tag_name in {"main", "article"}
            or heading_count >= 2
            or _contains_signal(node, CONTENT_SIGNAL_TERMS)
        )

        if should_consider:
            add(node)

    scored = [
        _candidate_score(node, cache)
        for node in nodes
    ]

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored


def _select_best_root(
    soup: BeautifulSoup,
    cache: dict[int, str],
) -> dict[str, Any]:
    candidates = _collect_root_candidates(soup, cache)

    # The word-count check is belt-and-suspenders: the scorer
    # already applies SHORT_ROOT_PENALTY below the threshold, but
    # requiring both keeps the eligibility rule explicit even if
    # weights are retuned.
    eligible = [
        candidate
        for candidate in candidates
        if candidate["word_count"] >= MIN_ROOT_WORD_COUNT
        and candidate["score"] > 0
    ]

    if eligible:
        selected = eligible[0]
    else:
        selected_node = soup.body or soup
        selected = _candidate_score(selected_node, cache)

    return {
        "selected": selected,
        "candidates": candidates,
    }


# ---------------------------------------------------------------------------
# Block extraction helpers
# ---------------------------------------------------------------------------

def _selected_ancestor(
    node: Tag,
    selected_tags: frozenset[str],
) -> Tag | None:
    parent = node.parent

    while isinstance(parent, Tag):
        parent_name = str(parent.name or "").lower()

        if parent_name in selected_tags:
            return parent

        parent = parent.parent

    return None


def _has_consumed_ancestor(
    node: Tag,
    consumed: set[int],
) -> bool:
    """True when an ancestor generic container already emitted its
    combined text as a block. Prevents descendant spans/divs/links
    from re-emitting the same text as duplicate blocks."""

    if not consumed:
        return False

    parent = node.parent

    while isinstance(parent, Tag):
        if id(parent) in consumed:
            return True

        parent = parent.parent

    return False


def _has_substantial_block_descendant(
    node: Tag,
    cache: dict[int, str],
) -> bool:
    """Return True when a generic container contains a more specific
    descendant block that should be emitted instead of the parent.

    This prevents:

        parent DIV containing three cards
        child card DIV
        child body DIV

    from all being written as duplicate article paragraphs.
    """

    for descendant in node.find_all(_SUBSTANTIAL_DESCENDANT_TAGS):
        if not isinstance(descendant, Tag):
            continue

        text = _node_text(descendant, cache)

        if _word_count(text) >= SUBSTANTIAL_DESCENDANT_MIN_WORDS:
            return True

    return False


def _leaf_container_text(
    node: Tag,
    cache: dict[int, str],
) -> str:
    """Extract text only from a leaf-level generic content container.

    Inline descendants such as A, STRONG and SPAN remain part of
    the paragraph. Nested block containers cause the parent to be
    skipped so their text is not duplicated.
    """

    if _has_substantial_block_descendant(node, cache):
        return ""

    text = _node_text(node, cache)
    words = _word_count(text)

    has_heading_signal = _contains_signal(
        node,
        HEADING_SIGNAL_TERMS,
    )

    if words < MIN_LEAF_PARAGRAPH_WORDS:
        if (
            has_heading_signal
            and MIN_SIGNAL_HEADING_WORDS
            <= words
            <= MAX_SIGNAL_HEADING_WORDS
        ):
            return text

        return ""

    has_content_signal = _contains_signal(
        node,
        CONTENT_SIGNAL_TERMS,
    )

    has_sentence_shape = bool(
        re.search(r"[.!?](?:\s|$)", text)
    )

    if not (has_content_signal or has_sentence_shape):
        return ""

    return text


def _is_navigation_list_item(
    node: Tag,
    cache: dict[int, str],
) -> bool:
    """Detect linked table-of-contents and tab navigation lists
    while preserving normal article bullet lists."""

    parent_list = node.find_parent(["ul", "ol"])

    if not isinstance(parent_list, Tag):
        return False

    direct_items = parent_list.find_all("li", recursive=False)

    if len(direct_items) < 3:
        return False

    item_texts = [
        _node_text(item, cache)
        for item in direct_items
        if isinstance(item, Tag)
    ]

    all_short = (
        bool(item_texts)
        and all(
            1 <= _word_count(text) <= 6
            for text in item_texts
        )
    )

    all_linked = all(
        item.find("a") is not None
        for item in direct_items
        if isinstance(item, Tag)
    )

    if all_short and all_linked:
        return True

    ancestor: Tag | None = parent_list
    levels_checked = 0

    while (
        isinstance(ancestor, Tag)
        and levels_checked < NAVIGATION_ANCESTOR_LEVELS
    ):
        if _contains_signal(ancestor, NAVIGATION_SIGNAL_TERMS):
            return True

        ancestor = ancestor.parent
        levels_checked += 1

    return False


# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------

def _postprocess_reconstructed_blocks(
    blocks: list[dict[str, Any]],
    rules: _ResolvedRules,
) -> list[dict[str, Any]]:
    """Clean reconstructed blocks and stop before terminal metadata,
    source lists or commercial-product disclosures."""

    retained: list[dict[str, Any]] = []

    for original in blocks:
        block = dict(original)

        text = _clean_reconstructed_text(block.get("text"))

        if not text:
            continue

        terminal_metadata = any(
            pattern.search(text)
            for pattern in rules.terminal_metadata_patterns
        )

        if terminal_metadata:
            if len(retained) >= MIN_TERMINAL_METADATA_INDEX:
                break

            # A terminal match near the beginning is treated as a
            # false positive: it must not truncate the article, but
            # it is still metadata-shaped text, so skip it rather
            # than retaining it as article content.
            continue

        if _is_metadata_or_ui(text, rules):
            continue

        block["text"] = text
        block["word_count"] = _word_count(text)

        retained.append(block)

    for index, block in enumerate(retained):
        block["index"] = index

    return retained


# ---------------------------------------------------------------------------
# Ordered block extraction
# ---------------------------------------------------------------------------

def _direct_text_without_nested_structures(
    node: Tag,
    cache: dict[int, str],
) -> str:
    """Read the text belonging directly to a structural node while
    excluding nested lists, tables, figures and media containers."""

    parts: list[str] = []

    excluded = {
        "ul",
        "ol",
        "table",
        "figure",
        "picture",
        "video",
        "audio",
        "iframe",
        "pre",
    }

    for child in node.contents:
        if isinstance(child, NavigableString):
            parts.append(str(child))
            continue

        if not isinstance(child, Tag):
            continue

        child_name = str(
            child.name or ""
        ).casefold()

        if child_name in excluded:
            continue

        parts.append(
            _node_text(child, cache)
        )

    return _normalize_text(
        " ".join(parts)
    )


def _extract_list_items(
    node: Tag,
    cache: dict[int, str],
) -> list[str]:
    items: list[str] = []

    for item in node.find_all(
        "li",
        recursive=False,
    ):
        if not isinstance(item, Tag):
            continue

        text = _direct_text_without_nested_structures(
            item,
            cache,
        )

        text = _clean_reconstructed_text(
            text
        )

        if (
            text
            and not _is_navigation_list_item(
                item,
                cache,
            )
        ):
            items.append(text)

    return items


def _extract_table_block(
    node: Tag,
    cache: dict[int, str],
) -> dict[str, Any] | None:
    rows: list[list[str]] = []
    headers: list[str] = []

    for row in node.find_all("tr"):
        if not isinstance(row, Tag):
            continue

        header_cells = row.find_all(
            "th",
            recursive=False,
        )

        data_cells = row.find_all(
            "td",
            recursive=False,
        )

        if header_cells and not headers:
            headers = [
                _clean_reconstructed_text(
                    _node_text(
                        cell,
                        cache,
                    )
                )
                for cell in header_cells
            ]

            headers = [
                value
                for value in headers
                if value
            ]

        if data_cells:
            values = [
                _clean_reconstructed_text(
                    _node_text(
                        cell,
                        cache,
                    )
                )
                for cell in data_cells
            ]

            if any(values):
                rows.append(values)

    if not headers and not rows:
        return None

    text_rows: list[str] = []

    if headers:
        text_rows.append(
            " | ".join(headers)
        )

    text_rows.extend(
        " | ".join(row)
        for row in rows
    )

    text = "\n".join(
        text_rows
    ).strip()

    return {
        "type": "table",
        "tag": "table",
        "text": text,
        "headers": headers,
        "rows": rows,
    }


def _extract_image_data(
    node: Tag,
) -> dict[str, Any] | None:
    src = str(
        node.get("src")
        or node.get("data-src")
        or node.get("data-lazy-src")
        or ""
    ).strip()

    srcset = str(
        node.get("srcset")
        or node.get("data-srcset")
        or ""
    ).strip()

    alt = _normalize_text(
        node.get("alt")
        or ""
    )

    title = _normalize_text(
        node.get("title")
        or ""
    )

    if not any(
        (
            src,
            srcset,
            alt,
            title,
        )
    ):
        return None

    return {
        "type": "image",
        "tag": "img",
        "text": alt or title,
        "src": src,
        "srcset": srcset,
        "alt": alt,
        "title": title,
    }


def _extract_media_data(
    node: Tag,
) -> dict[str, Any] | None:
    tag_name = str(
        node.name or ""
    ).casefold()

    src = str(
        node.get("src")
        or node.get("data-src")
        or ""
    ).strip()

    sources = []

    for source_node in node.find_all(
        "source",
    ):
        if not isinstance(source_node, Tag):
            continue

        source_value = str(
            source_node.get("src")
            or source_node.get("srcset")
            or ""
        ).strip()

        if source_value:
            sources.append(
                source_value
            )

    title = _normalize_text(
        node.get("title")
        or node.get("aria-label")
        or ""
    )

    if not src and not sources and not title:
        return None

    return {
        "type": "media",
        "tag": tag_name,
        "media_type": tag_name,
        "text": title,
        "src": src,
        "sources": sources,
        "title": title,
    }


def _derive_compatibility_views(
    content_blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    headings: list[dict[str, Any]] = []
    paragraphs: list[str] = []
    body_parts: list[str] = []

    for block in content_blocks:
        block_type = str(
            block.get("type")
            or ""
        )

        text = str(
            block.get("text")
            or ""
        ).strip()

        if block_type == "heading":
            headings.append({
                "level":
                    block.get("level"),
                "text":
                    text,
            })

        elif block_type in {
            "paragraph",
            "blockquote",
            "caption",
            "code",
            "preformatted",
        }:
            if text:
                paragraphs.append(text)

        elif block_type in {
            "unordered_list",
            "ordered_list",
        }:
            items = [
                str(item).strip()
                for item in (
                    block.get("items")
                    or []
                )
                if str(item).strip()
            ]

            if items:
                paragraphs.extend(items)

        elif block_type == "table":
            for row in (
                block.get("rows")
                or []
            ):
                row_text = " | ".join(
                    str(value).strip()
                    for value in row
                ).strip()

                if row_text:
                    paragraphs.append(
                        row_text
                    )

        if text:
            body_parts.append(text)

    return {
        "headings": headings,
        "paragraphs": paragraphs,
        "article_body":
            "\n\n".join(
                body_parts
            ).strip(),
    }


def _extract_ordered_blocks(
    root: Tag,
    rules: _ResolvedRules,
    cache: dict[int, str],
) -> dict[str, Any]:
    """Reconstruct a rich ordered article representation.

    ``content_blocks`` is canonical. Compatibility fields are
    derived from it and never reconstructed separately.
    """

    content_blocks: list[
        dict[str, Any]
    ] = []

    seen_text_keys: set[str] = set()
    consumed_nodes: set[int] = set()

    structural_tags = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "blockquote",
        "ul",
        "ol",
        "table",
        "figure",
        "img",
        "figcaption",
        "pre",
        "code",
        "video",
        "audio",
        "iframe",
        "div",
        "section",
        "span",
        "a",
        "dt",
        "dd",
    }

    def append_block(
        block: dict[str, Any],
    ) -> None:
        text = _clean_reconstructed_text(
            block.get("text")
        )

        block_type = str(
            block.get("type")
            or ""
        )

        if text and _is_metadata_or_ui(
            text,
            rules,
        ):
            return

        terminal_metadata = (
            bool(text)
            and any(
                pattern.search(text)
                for pattern
                in rules.terminal_metadata_patterns
            )
        )

        if terminal_metadata:
            if (
                len(content_blocks)
                >= MIN_TERMINAL_METADATA_INDEX
            ):
                block[
                    "_terminal_stop"
                ] = True
            return

        if text:
            normalized_key = (
                block_type
                + ":"
                + re.sub(
                    r"\s+",
                    " ",
                    text,
                ).casefold()
            )

            deduplicate = (
                block_type
                in {
                    "paragraph",
                    "heading",
                    "blockquote",
                    "caption",
                }
                and _word_count(text)
                >= 8
            )

            if (
                deduplicate
                and normalized_key
                in seen_text_keys
            ):
                return

            if deduplicate:
                seen_text_keys.add(
                    normalized_key
                )

        block = dict(block)

        block["index"] = len(
            content_blocks
        )

        block["text"] = text

        block["word_count"] = (
            _word_count(text)
            if text
            else 0
        )

        content_blocks.append(block)

    stop = False

    for node in root.descendants:
        if stop:
            break

        if not isinstance(node, Tag):
            continue

        if id(node) in consumed_nodes:
            continue

        tag_name = str(
            node.name or ""
        ).casefold()

        if tag_name not in structural_tags:
            continue

        parent = node.parent

        skip_due_to_consumed_parent = False

        while isinstance(parent, Tag):
            if id(parent) in consumed_nodes:
                skip_due_to_consumed_parent = True
                break

            parent = parent.parent

        if skip_due_to_consumed_parent:
            continue

        block: dict[str, Any] | None = None

        if tag_name in HEADING_TAG_NAMES:
            text = _node_text(
                node,
                cache,
            )

            block = {
                "type": "heading",
                "tag": tag_name,
                "level": int(
                    tag_name[1]
                ),
                "text": text,
            }

        elif tag_name == "p":
            block = {
                "type": "paragraph",
                "tag": "p",
                "level": None,
                "text": _node_text(
                    node,
                    cache,
                ),
            }

        elif tag_name == "blockquote":
            consumed_nodes.update(
                id(child)
                for child in node.find_all(
                    True,
                )
            )

            block = {
                "type": "blockquote",
                "tag": "blockquote",
                "level": None,
                "text": _node_text(
                    node,
                    cache,
                ),
            }

        elif tag_name in {
            "ul",
            "ol",
        }:
            items = _extract_list_items(
                node,
                cache,
            )

            if not items:
                continue

            consumed_nodes.update(
                id(child)
                for child in node.find_all(
                    True,
                )
            )

            block = {
                "type": (
                    "ordered_list"
                    if tag_name == "ol"
                    else "unordered_list"
                ),
                "tag": tag_name,
                "level": None,
                "items": items,
                "text": "\n".join(
                    items
                ),
            }

        elif tag_name == "table":
            block = _extract_table_block(
                node,
                cache,
            )

            if block is not None:
                consumed_nodes.update(
                    id(child)
                    for child in node.find_all(
                        True,
                    )
                )

        elif tag_name == "figure":
            image_node = node.find("img")

            image_data = (
                _extract_image_data(
                    image_node
                )
                if isinstance(
                    image_node,
                    Tag,
                )
                else None
            )

            caption_node = node.find(
                "figcaption"
            )

            caption = (
                _clean_reconstructed_text(
                    _node_text(
                        caption_node,
                        cache,
                    )
                )
                if isinstance(
                    caption_node,
                    Tag,
                )
                else ""
            )

            figure_text = caption

            if (
                image_data
                and image_data.get("alt")
                and not figure_text
            ):
                figure_text = str(
                    image_data.get("alt")
                )

            if image_data or figure_text:
                block = {
                    "type": "figure",
                    "tag": "figure",
                    "level": None,
                    "text": figure_text,
                    "image": image_data,
                    "caption": caption,
                }

                consumed_nodes.update(
                    id(child)
                    for child in node.find_all(
                        True,
                    )
                )

        elif tag_name == "img":
            image_data = _extract_image_data(
                node
            )

            if image_data:
                block = {
                    **image_data,
                    "level": None,
                }

        elif tag_name == "figcaption":
            block = {
                "type": "caption",
                "tag": "figcaption",
                "level": None,
                "text": _node_text(
                    node,
                    cache,
                ),
            }

        elif tag_name == "pre":
            text = str(
                node.get_text(
                    "\n",
                    strip=False,
                )
            ).replace(
                "\r\n",
                "\n",
            ).replace(
                "\r",
                "\n",
            ).strip()

            consumed_nodes.update(
                id(child)
                for child in node.find_all(
                    True,
                )
            )

            block = {
                "type": "preformatted",
                "tag": "pre",
                "level": None,
                "text": text,
            }

        elif tag_name == "code":
            if node.find_parent("pre"):
                continue

            block = {
                "type": "code",
                "tag": "code",
                "level": None,
                "text": _node_text(
                    node,
                    cache,
                ),
            }

        elif tag_name in {
            "video",
            "audio",
            "iframe",
        }:
            media_data = (
                _extract_media_data(
                    node
                )
            )

            if media_data:
                block = {
                    **media_data,
                    "level": None,
                }

                consumed_nodes.update(
                    id(child)
                    for child in node.find_all(
                        True,
                    )
                )

        elif tag_name in {
            "dt",
            "dd",
        }:
            block = {
                "type": "paragraph",
                "tag": tag_name,
                "level": None,
                "text": _node_text(
                    node,
                    cache,
                ),
            }

        elif tag_name == "a":
            candidate_text = _node_text(
                node,
                cache,
            )

            candidate_words = _word_count(
                candidate_text
            )

            has_heading_signal = (
                _contains_signal(
                    node,
                    HEADING_SIGNAL_TERMS,
                )
            )

            if (
                not has_heading_signal
                and isinstance(
                    node.parent,
                    Tag,
                )
            ):
                has_heading_signal = (
                    _contains_signal(
                        node.parent,
                        HEADING_SIGNAL_TERMS,
                    )
                )

            if (
                has_heading_signal
                and MIN_SIGNAL_HEADING_WORDS
                <= candidate_words
                <= MAX_SIGNAL_HEADING_WORDS
            ):
                block = {
                    "type": "heading",
                    "tag": "a",
                    "level": None,
                    "text": candidate_text,
                }

        elif tag_name in GENERIC_CONTAINER_TAGS:
            text = _leaf_container_text(
                node,
                cache,
            )

            if text:
                consumed_nodes.add(
                    id(node)
                )

                block_type = "paragraph"
                level = None

                if (
                    _contains_signal(
                        node,
                        HEADING_SIGNAL_TERMS,
                    )
                    and _word_count(text)
                    <= MAX_SIGNAL_HEADING_WORDS
                ):
                    block_type = "heading"

                block = {
                    "type": block_type,
                    "tag": tag_name,
                    "level": level,
                    "text": text,
                }

        if block is None:
            continue

        before = len(content_blocks)

        append_block(block)

        if (
            len(content_blocks)
            > before
            and content_blocks[-1].pop(
                "_terminal_stop",
                False,
            )
        ):
            stop = True

    # Re-index after all filtering.
    for index, block in enumerate(
        content_blocks
    ):
        block["index"] = index

    compatibility = (
        _derive_compatibility_views(
            content_blocks
        )
    )

    return {
        "content_blocks":
            content_blocks,
        # Temporary compatibility alias. New consumers must use
        # content_blocks; this will be removed only after all
        # downstream migrations are certified.
        "blocks":
            content_blocks,
        "headings":
            compatibility[
                "headings"
            ],
        "paragraphs":
            compatibility[
                "paragraphs"
            ],
        "article_body":
            compatibility[
                "article_body"
            ],
    }

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def reconstruct_universal_dom_article_v1(
    *,
    html_text: str,
    url: str = "",
    title: str = "",
    metadata: dict[str, Any] | None = None,
    profile: ReconstructionProfile | None = None,
) -> dict[str, Any]:
    resolved_profile = _resolve_profile_for_url(
        url,
        profile,
    )
    rules = _resolve_rules(resolved_profile)

    source_html = str(html_text or "")

    soup = BeautifulSoup(source_html, PARSER_NAME)

    removed_node_count = _remove_noise_nodes(
        soup,
        rules.noise_signal_terms,
    )

    # Subtree-text memoization. Built after noise removal so cached
    # text never includes decomposed content; the tree is not
    # mutated again after this point.
    cache: dict[int, str] = {}

    root_selection = _select_best_root(soup, cache)

    selected = root_selection["selected"]
    root = selected["node"]

    extraction = _extract_ordered_blocks(root, rules, cache)

    article_body = str(
        extraction.get("article_body") or ""
    ).strip()

    detected_title = _normalize_text(title)

    if not detected_title:
        title_tag = soup.find("title")

        if isinstance(title_tag, Tag):
            detected_title = _node_text(title_tag, cache)

    h1 = next(
        (
            heading["text"]
            for heading in extraction["headings"]
            if heading.get("level") == 1
        ),
        "",
    )

    if not detected_title:
        detected_title = h1

    candidate_summary = []

    for candidate in root_selection["candidates"][:20]:
        candidate_summary.append({
            "tag": candidate["tag"],
            "signal": candidate["signal"][:250],
            "word_count": candidate["word_count"],
            "heading_count": candidate["heading_count"],
            "paragraph_count": candidate["paragraph_count"],
            "link_density": candidate["link_density"],
            "score": candidate["score"],
        })

    return {
        "ok": bool(article_body),
        "engine": ENGINE_NAME,
        "parser": PARSER_NAME,
        "url": url,
        "title": detected_title,
        "h1": h1,
        "article_body": article_body,
        # Compatibility aliases for downstream consumers that read
        # different keys; all three are the same string.
        "content_body": article_body,
        "main_content": article_body,
        # Canonical structured reconstruction.
        "content_blocks": extraction["content_blocks"],
        # Compatibility alias for existing downstream consumers.
        "blocks": extraction["content_blocks"],
        "headings": extraction["headings"],
        "paragraphs": extraction["paragraphs"],
        "selected_root": {
            "tag": selected["tag"],
            "signal": selected["signal"],
            "word_count": selected["word_count"],
            "heading_count": selected["heading_count"],
            "paragraph_count": selected["paragraph_count"],
            "link_density": selected["link_density"],
            "score": selected["score"],
        },
        "statistics": {
            "source_html_length": len(source_html),
            "removed_node_count": removed_node_count,
            "candidate_count": len(root_selection["candidates"]),
            "block_count": len(
                extraction["content_blocks"]
            ),
            "heading_count": len(
                extraction["headings"]
            ),
            "paragraph_count": len(
                extraction["paragraphs"]
            ),
            "block_type_counts": {
                block_type: sum(
                    1
                    for block in extraction["content_blocks"]
                    if str(block.get("type") or "")
                    == block_type
                )
                for block_type in sorted({
                    str(block.get("type") or "")
                    for block in extraction["content_blocks"]
                    if str(block.get("type") or "")
                })
            },
            "article_word_count": _word_count(article_body),
            "article_length": len(article_body),
        },
        "candidate_summary": candidate_summary,
        "metadata": {
            **(metadata or {}),
            "article_reconstruction": {
                "engine": ENGINE_NAME,
                "parser": PARSER_NAME,
                "profile": resolved_profile.name,
                "selected_root_tag": selected["tag"],
                "selected_root_signal": selected["signal"],
            },
        },
    }


def explain_universal_dom_article_reconstruction_v1() -> dict[str, Any]:
    return {
        "engine": ENGINE_NAME,
        "parser": PARSER_NAME,
        "purpose": (
            "Reconstruct ordered rich article content blocks "
            "from valid, malformed and component-based HTML."
        ),
        "stages": [
            "browser-tolerant DOM repair",
            "profile-aware DOM noise removal",
            "universal root candidate scoring",
            "ordered visible content walking",
            "rich structured article reconstruction",
            "terminal metadata truncation",
        ],
        "profiles": (
            "Site-specific metadata/UI/terminal patterns are "
            "supplied via ReconstructionProfile; the core engine "
            "ships only generic patterns."
        ),
        "does_not": [
            "rewrite or reorder article wording",
            "summarize or interpret content semantically",
            "reconstruct tables or figure media (only figcaption "
            "text is kept)",
            "preserve whitespace inside <pre> blocks",
        ],
    }