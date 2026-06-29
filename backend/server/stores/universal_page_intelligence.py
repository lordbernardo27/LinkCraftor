"""
Universal Page Intelligence

Phase 4.5.1
URL Pattern Intelligence

Purpose:
Predict page type from URL structure before any HTML analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from urllib.parse import urlparse
from typing import Dict, Any


@dataclass
class URLPatternResult:
    url: str
    path: str
    predicted_page_type: str
    confidence: float
    matched_rule: str


_RULES = [
    ("ARTICLE", []),
    ("CATEGORY", ["category", "categories"]),
    ("DIRECTORY", ["directory", "directories", "brands", "authors"]),
    ("PRODUCT", ["product", "products", "shop"]),
    ("SERVICE", ["service", "services"]),
    ("AUTHOR", ["author", "authors"]),
    ("TAG", ["tag", "tags"]),
    ("SEARCH_RESULTS", ["search"]),
    ("LOGIN", ["login", "signin", "sign-in", "account"]),
    ("ERROR", ["404"]),
    ("PAGINATION", ["page"]),
]


def classify_url_pattern_v1(url: str) -> URLPatternResult:
    parsed = urlparse(url)
    path = parsed.path.lower().strip("/")

    if path == "":
        return URLPatternResult(
            url=url,
            path="/",
            predicted_page_type="HOME",
            confidence=1.0,
            matched_rule="root_path",
        )

    segments = [s for s in path.split("/") if s]

    for page_type, keywords in _RULES:
        for segment in segments:
            if segment in keywords:
                return URLPatternResult(
                    url=url,
                    path=parsed.path,
                    predicted_page_type=page_type,
                    confidence=0.95,
                    matched_rule=segment,
                )

    if len(segments) == 1 and "-" in segments[0]:
        return URLPatternResult(
            url=url,
            path=parsed.path,
            predicted_page_type="ARTICLE",
            confidence=0.80,
            matched_rule="hyphenated_slug",
        )

    return URLPatternResult(
        url=url,
        path=parsed.path,
        predicted_page_type="UNKNOWN",
        confidence=0.50,
        matched_rule="fallback",
    )


def serialize_url_pattern_result(result: URLPatternResult) -> Dict[str, Any]:
    return asdict(result)





@dataclass
class HTMLStructureResult:
    paragraph_count: int
    heading_count: int
    h1_count: int
    h2_count: int
    h3_count: int
    list_count: int
    table_count: int
    form_count: int
    nav_count: int
    footer_count: int
    link_count: int
    card_like_count: int
    pagination_like_count: int
    body_text_length: int
    navigation_density: float
    footer_ratio: float
    structural_confidence: float


def _count_regex_v1(pattern: str, text: str) -> int:
    import re
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL))


def _strip_tags_for_structure_v1(html: str) -> str:
    import re
    import html as html_lib

    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", html)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = html_lib.unescape(cleaned)
    return " ".join(cleaned.split())


def analyze_html_structure_v1(html: str) -> HTMLStructureResult:
    safe_html = html or ""

    paragraph_count = _count_regex_v1(r"<p\b", safe_html)
    h1_count = _count_regex_v1(r"<h1\b", safe_html)
    h2_count = _count_regex_v1(r"<h2\b", safe_html)
    h3_count = _count_regex_v1(r"<h3\b", safe_html)
    heading_count = _count_regex_v1(r"<h[1-6]\b", safe_html)

    list_count = _count_regex_v1(r"<(ul|ol)\b", safe_html)
    table_count = _count_regex_v1(r"<table\b", safe_html)
    form_count = _count_regex_v1(r"<form\b", safe_html)
    nav_count = _count_regex_v1(r"<nav\b", safe_html)
    footer_count = _count_regex_v1(r"<footer\b", safe_html)
    link_count = _count_regex_v1(r"<a\b", safe_html)

    card_like_count = _count_regex_v1(r'class=["\'][^"\']*(card|grid|tile|item)[^"\']*["\']', safe_html)
    pagination_like_count = _count_regex_v1(r'(pagination|page-numbers|next-page|prev-page|load-more)', safe_html)

    body_text = _strip_tags_for_structure_v1(safe_html)
    body_text_length = len(body_text)

    nav_text_length = 0
    footer_text_length = 0

    import re

    for m in re.finditer(r"(?is)<nav\b.*?</nav>", safe_html):
        nav_text_length += len(_strip_tags_for_structure_v1(m.group(0)))

    for m in re.finditer(r"(?is)<footer\b.*?</footer>", safe_html):
        footer_text_length += len(_strip_tags_for_structure_v1(m.group(0)))

    navigation_density = round(nav_text_length / body_text_length, 4) if body_text_length else 0.0
    footer_ratio = round(footer_text_length / body_text_length, 4) if body_text_length else 0.0

    signal_count = sum([
        paragraph_count > 0,
        heading_count > 0,
        list_count > 0,
        table_count > 0,
        form_count > 0,
        nav_count > 0,
        link_count > 0,
        body_text_length > 0,
    ])

    structural_confidence = round(min(1.0, signal_count / 5), 2)

    return HTMLStructureResult(
        paragraph_count=paragraph_count,
        heading_count=heading_count,
        h1_count=h1_count,
        h2_count=h2_count,
        h3_count=h3_count,
        list_count=list_count,
        table_count=table_count,
        form_count=form_count,
        nav_count=nav_count,
        footer_count=footer_count,
        link_count=link_count,
        card_like_count=card_like_count,
        pagination_like_count=pagination_like_count,
        body_text_length=body_text_length,
        navigation_density=navigation_density,
        footer_ratio=footer_ratio,
        structural_confidence=structural_confidence,
    )


def serialize_html_structure_result(result: HTMLStructureResult) -> Dict[str, Any]:
    return asdict(result)


def explain_html_structure_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.2",
        "module": "universal_page_intelligence.py",
        "status": "created",
        "responsibility": "Analyze HTML structure using niche-independent DOM signals.",
        "signals": [
            "paragraph_count",
            "heading_count",
            "heading_hierarchy",
            "list_count",
            "table_count",
            "form_count",
            "navigation_density",
            "footer_ratio",
            "card_like_count",
            "pagination_like_count",
            "body_text_length",
        ],
    }





@dataclass
class ContentQualityResult:
    word_count: int
    sentence_count: int
    unique_word_count: int
    lexical_diversity: float
    avg_sentence_length: float
    heading_depth_score: float
    text_to_link_ratio: float
    paragraph_density: float
    repeated_boilerplate_score: float
    semantic_richness_score: float
    quality_score: float
    quality_label: str


def _extract_visible_text_for_quality_v1(html: str) -> str:
    return _strip_tags_for_structure_v1(html or "")


def _split_sentences_v1(text: str) -> list[str]:
    import re
    parts = re.split(r"[.!?]+", text or "")
    return [p.strip() for p in parts if p.strip()]


def _tokenize_words_v1(text: str) -> list[str]:
    import re
    return re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text.lower())


def _calculate_repeated_boilerplate_score_v1(text: str) -> float:
    lines = [line.strip().lower() for line in (text or "").splitlines() if line.strip()]

    if len(lines) < 3:
        return 0.0

    seen = {}
    for line in lines:
        seen[line] = seen.get(line, 0) + 1

    repeated = sum(count for count in seen.values() if count > 1)
    return round(min(1.0, repeated / max(1, len(lines))), 4)


def analyze_content_quality_v1(html: str, structure: HTMLStructureResult | None = None) -> ContentQualityResult:
    safe_html = html or ""
    visible_text = _extract_visible_text_for_quality_v1(safe_html)

    words = _tokenize_words_v1(visible_text)
    sentences = _split_sentences_v1(visible_text)

    word_count = len(words)
    sentence_count = len(sentences)
    unique_word_count = len(set(words))

    lexical_diversity = round(unique_word_count / word_count, 4) if word_count else 0.0
    avg_sentence_length = round(word_count / sentence_count, 2) if sentence_count else 0.0

    if structure is None:
        structure = analyze_html_structure_v1(safe_html)

    heading_depth_score = 0.0
    if structure.h1_count:
        heading_depth_score += 0.3
    if structure.h2_count:
        heading_depth_score += 0.3
    if structure.h3_count:
        heading_depth_score += 0.2
    if structure.heading_count >= 3:
        heading_depth_score += 0.2
    heading_depth_score = round(min(1.0, heading_depth_score), 4)

    text_to_link_ratio = round(word_count / max(1, structure.link_count), 4)
    paragraph_density = round(structure.paragraph_count / max(1, word_count / 100), 4)

    repeated_boilerplate_score = _calculate_repeated_boilerplate_score_v1(visible_text)

    richness_components = [
        min(1.0, word_count / 700),
        min(1.0, unique_word_count / 300),
        min(1.0, sentence_count / 35),
        heading_depth_score,
        min(1.0, structure.paragraph_count / 8),
    ]
    semantic_richness_score = round(sum(richness_components) / len(richness_components), 4)

    quality_components = [
        min(1.0, word_count / 500),
        min(1.0, lexical_diversity),
        min(1.0, text_to_link_ratio / 50),
        min(1.0, paragraph_density / 2),
        semantic_richness_score,
        1.0 - repeated_boilerplate_score,
    ]

    quality_score = round(sum(quality_components) / len(quality_components), 4)

    if quality_score >= 0.75:
        quality_label = "HIGH"
    elif quality_score >= 0.50:
        quality_label = "MEDIUM"
    elif quality_score >= 0.25:
        quality_label = "LOW"
    else:
        quality_label = "VERY_LOW"

    return ContentQualityResult(
        word_count=word_count,
        sentence_count=sentence_count,
        unique_word_count=unique_word_count,
        lexical_diversity=lexical_diversity,
        avg_sentence_length=avg_sentence_length,
        heading_depth_score=heading_depth_score,
        text_to_link_ratio=text_to_link_ratio,
        paragraph_density=paragraph_density,
        repeated_boilerplate_score=repeated_boilerplate_score,
        semantic_richness_score=semantic_richness_score,
        quality_score=quality_score,
        quality_label=quality_label,
    )


def serialize_content_quality_result(result: ContentQualityResult) -> Dict[str, Any]:
    return asdict(result)


def explain_content_quality_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.3",
        "module": "universal_page_intelligence.py",
        "status": "created",
        "responsibility": "Measure content quality using niche-independent textual and structural signals.",
        "signals": [
            "word_count",
            "sentence_count",
            "unique_word_count",
            "lexical_diversity",
            "avg_sentence_length",
            "heading_depth_score",
            "text_to_link_ratio",
            "paragraph_density",
            "repeated_boilerplate_score",
            "semantic_richness_score",
            "quality_score",
            "quality_label",
        ],
    }





@dataclass
class PageIntentResult:
    url: str
    final_page_type: str
    confidence: float
    route_action: str
    evidence: Dict[str, Any]


_ROUTE_ACTIONS = {
    "ARTICLE": "article_body_extractor",
    "CATEGORY": "category_extractor",
    "DIRECTORY": "directory_extractor",
    "LANDING_PAGE": "landing_page_extractor",
    "PRODUCT": "product_extractor",
    "SERVICE": "service_extractor",
    "AUTHOR": "author_intelligence",
    "TAG": "tag_extractor",
    "HOME": "home_page_extractor",
    "SEARCH_RESULTS": "ignore",
    "LOGIN": "ignore",
    "ERROR": "ignore",
    "PAGINATION": "pagination_handler",
    "UNKNOWN": "manual_review",
}


def _score_page_intent_candidates_v1(
    url_result: URLPatternResult,
    structure: HTMLStructureResult,
    quality: ContentQualityResult,
) -> Dict[str, float]:
    scores: Dict[str, float] = {
        "ARTICLE": 0.0,
        "CATEGORY": 0.0,
        "DIRECTORY": 0.0,
        "LANDING_PAGE": 0.0,
        "PRODUCT": 0.0,
        "SERVICE": 0.0,
        "AUTHOR": 0.0,
        "TAG": 0.0,
        "HOME": 0.0,
        "SEARCH_RESULTS": 0.0,
        "LOGIN": 0.0,
        "ERROR": 0.0,
        "PAGINATION": 0.0,
        "UNKNOWN": 0.0,
    }

    scores[url_result.predicted_page_type] += url_result.confidence * 0.45

    article_strength = 0.0

    if structure.paragraph_count >= 2:
        article_strength += 0.12

    if structure.paragraph_count >= 4:
        article_strength += 0.08

    if structure.heading_count >= 1:
        article_strength += 0.10

    if structure.h1_count == 1:
        article_strength += 0.05

    if quality.word_count >= 80:
        article_strength += 0.08

    if quality.word_count >= 200:
        article_strength += 0.07

    if quality.word_count >= 500:
        article_strength += 0.05

    if quality.quality_label == "MEDIUM":
        article_strength += 0.05

    elif quality.quality_label == "HIGH":
        article_strength += 0.10

    scores["ARTICLE"] += article_strength

    if structure.card_like_count >= 3 or structure.pagination_like_count >= 1:
        scores["CATEGORY"] += 0.25
        scores["DIRECTORY"] += 0.20

    if structure.form_count >= 1 and quality.word_count < 300:
        scores["LOGIN"] += 0.25
        scores["SEARCH_RESULTS"] += 0.20

    if structure.table_count >= 1 and structure.paragraph_count <= 3:
        scores["DIRECTORY"] += 0.20

    if structure.link_count >= 20 and quality.word_count < 500:
        scores["CATEGORY"] += 0.25
        scores["DIRECTORY"] += 0.25

    if quality.quality_label in {"HIGH", "MEDIUM"} and quality.word_count >= 400:
        scores["ARTICLE"] += 0.25

    if structure.h1_count >= 1 and structure.paragraph_count <= 2 and quality.word_count <= 250:
        scores["LANDING_PAGE"] += 0.20

    if structure.pagination_like_count >= 1:
        scores["PAGINATION"] += 0.25

    return scores


def classify_page_intent_v1(url: str, html: str) -> PageIntentResult:
    url_result = classify_url_pattern_v1(url)
    structure = analyze_html_structure_v1(html)
    quality = analyze_content_quality_v1(html, structure)

    scores = _score_page_intent_candidates_v1(url_result, structure, quality)

    final_page_type = max(scores, key=scores.get)
    confidence = round(min(1.0, scores[final_page_type]), 4)

    if confidence < 0.35:
        final_page_type = "UNKNOWN"
        confidence = 0.35

    route_action = _ROUTE_ACTIONS.get(final_page_type, "manual_review")

    return PageIntentResult(
        url=url,
        final_page_type=final_page_type,
        confidence=confidence,
        route_action=route_action,
        evidence={
            "url_pattern": serialize_url_pattern_result(url_result),
            "html_structure": serialize_html_structure_result(structure),
            "content_quality": serialize_content_quality_result(quality),
            "candidate_scores": scores,
        },
    )


def serialize_page_intent_result(result: PageIntentResult) -> Dict[str, Any]:
    return asdict(result)


def explain_page_intent_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.4",
        "module": "universal_page_intelligence.py",
        "status": "created",
        "responsibility": "Combine URL, HTML structure, and content quality signals to predict page intent.",
        "inputs": [
            "URL Pattern Intelligence",
            "HTML Structure Intelligence",
            "Content Quality Intelligence",
        ],
        "outputs": [
            "final_page_type",
            "confidence",
            "route_action",
            "evidence",
        ],
        "supported_page_types": list(_ROUTE_ACTIONS.keys()),
    }





@dataclass
class IntelligentRouteResult:
    url: str
    page_type: str
    route_action: str
    should_process: bool
    should_ignore: bool
    confidence: float
    reason: str
    evidence: Dict[str, Any]


_IGNORE_ACTIONS = {"ignore"}


def route_page_intelligently_v1(url: str, html: str) -> IntelligentRouteResult:
    intent = classify_page_intent_v1(url, html)

    should_ignore = intent.route_action in _IGNORE_ACTIONS
    should_process = not should_ignore and intent.final_page_type != "UNKNOWN"

    if should_ignore:
        reason = f"Page type {intent.final_page_type} is configured to be ignored."
    elif intent.final_page_type == "UNKNOWN":
        reason = "Page type could not be classified confidently and requires manual review."
    else:
        reason = f"Page routed to {intent.route_action}."

    return IntelligentRouteResult(
        url=url,
        page_type=intent.final_page_type,
        route_action=intent.route_action,
        should_process=should_process,
        should_ignore=should_ignore,
        confidence=intent.confidence,
        reason=reason,
        evidence=serialize_page_intent_result(intent),
    )


def serialize_intelligent_route_result(result: IntelligentRouteResult) -> Dict[str, Any]:
    return asdict(result)


def explain_intelligent_router_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.5",
        "module": "universal_page_intelligence.py",
        "status": "created",
        "responsibility": "Route classified pages to the correct downstream extractor or ignore handler.",
        "routing_targets": _ROUTE_ACTIONS,
        "ignore_actions": sorted(_IGNORE_ACTIONS),
        "outputs": [
            "page_type",
            "route_action",
            "should_process",
            "should_ignore",
            "confidence",
            "reason",
            "evidence",
        ],
    }





from dataclasses import field


@dataclass
class UnifiedContentDocument:
    source_type: str
    page_type: str
    source_identifier: str

    title: str
    primary_content: str
    headings: List[str]

    metadata: Dict[str, Any] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)
    routing: Dict[str, Any] = field(default_factory=dict)
    semantic_features: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


def build_unified_content_document_v1(
    *,
    source_type: str,
    page_type: str,
    source_identifier: str,
    title: str,
    primary_content: str,
    headings: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
    quality: Dict[str, Any] | None = None,
    routing: Dict[str, Any] | None = None,
    semantic_features: Dict[str, Any] | None = None,
    diagnostics: Dict[str, Any] | None = None,
) -> UnifiedContentDocument:

    return UnifiedContentDocument(
        source_type=source_type,
        page_type=page_type,
        source_identifier=source_identifier,
        title=title,
        primary_content=primary_content,
        headings=headings or [],
        metadata=metadata or {},
        quality=quality or {},
        routing=routing or {},
        semantic_features=semantic_features or {},
        diagnostics=diagnostics or {},
    )


def serialize_unified_content_document_v1(
    document: UnifiedContentDocument,
) -> Dict[str, Any]:
    return asdict(document)


def explain_unified_content_contract_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.6",
        "status": "created",
        "contract": "UnifiedContentDocument",
        "purpose": (
            "Provide a single canonical content format consumed by all "
            "downstream semantic, graph, reasoning and linking engines."
        ),
        "supported_sources": [
            "website_article",
            "category_page",
            "directory_page",
            "product_page",
            "service_page",
            "author_page",
            "html_upload",
            "markdown_upload",
            "txt_upload",
            "docx_upload",
        ],
        "required_fields": [
            "source_type",
            "page_type",
            "source_identifier",
            "title",
            "primary_content",
            "headings",
            "metadata",
            "quality",
            "routing",
            "semantic_features",
            "diagnostics",
        ],
    }


def explain_url_pattern_intelligence_v1() -> Dict[str, Any]:
    return {
        "phase": "4.5.1",
        "module": "universal_page_intelligence.py",
        "status": "created",
        "responsibility": "Predict page type from URL structure.",
        "supported_page_types": [
            "ARTICLE",
            "CATEGORY",
            "DIRECTORY",
            "PRODUCT",
            "SERVICE",
            "AUTHOR",
            "TAG",
            "HOME",
            "SEARCH_RESULTS",
            "LOGIN",
            "ERROR",
            "PAGINATION",
            "UNKNOWN",
        ],
    }
