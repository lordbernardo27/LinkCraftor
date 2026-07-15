from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List
from urllib.parse import urlparse


KNOWLEDGE_PAGE_TYPES = {
    "article",
    "news_article",
    "blog_post",
    "guide",
    "tutorial",
    "documentation",
    "knowledge_base_article",
    "faq",
    "case_study",
    "white_paper",
    "research_paper",
    "medical_reference",
    "legal_reference",
    "product_review",
    "comparison_article",
    "opinion_editorial",
    "press_release",
    "encyclopedia_entry",
    "recipe",
    "educational_lesson",
    "glossary_entry",
}

DIRECTORY_PAGE_TYPES = {
    "category_page",
    "tag_page",
    "archive_page",
    "author_archive",
    "search_results",
    "topic_hub",
    "collection_page",
    "sitemap",
    "a_z_index",
    "browse_page",
}

COMMERCE_PAGE_TYPES = {
    "product_page",
    "product_category",
    "brand_page",
    "store_locator",
    "pricing_page",
    "checkout",
    "cart",
    "wishlist",
}

INTERACTIVE_PAGE_TYPES = {
    "calculator",
    "quiz",
    "tool",
    "converter",
    "wizard",
    "configurator",
    "interactive_dashboard",
}

COMMUNITY_PAGE_TYPES = {
    "forum_thread",
    "forum_index",
    "q_and_a",
    "community_discussion",
    "comments_page",
}

MEDIA_PAGE_TYPES = {
    "video_page",
    "podcast_episode",
    "gallery",
    "image_page",
    "infographic_page",
}

COMPANY_PAGE_TYPES = {
    "about_page",
    "contact_page",
    "careers_page",
    "team_page",
    "events_page",
    "webinar_page",
    "partner_page",
}

SYSTEM_PAGE_TYPES = {
    "login",
    "register",
    "account",
    "password_reset",
    "error_page",
    "maintenance_page",
    "redirect_page",
    "consent_page",
}

POLICY_PAGE_TYPES = {
    "privacy_policy",
    "terms_of_service",
    "cookie_policy",
    "accessibility_page",
    "disclaimer",
}


@dataclass
class PageClassificationResult:
    page_type: str
    page_group: str
    route: str
    confidence: float
    reasons: List[str]
    signals: Dict[str, Any]


def _plain_text(value: str) -> str:
    value = re.sub(r"(?is)<script\b[^>]*>.*?</script>", " ", str(value or ""))
    value = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", value)
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _extract_first(pattern: str, text: str) -> str:
    match = re.search(pattern, str(text or ""), re.IGNORECASE | re.DOTALL)
    return _plain_text(match.group(1)) if match else ""


def _schema_types(html_text: str) -> List[str]:
    values = re.findall(
        r'(?is)["\']@type["\']\s*:\s*["\']([^"\']+)["\']',
        str(html_text or ""),
    )
    return sorted(set(v.strip().lower() for v in values if v.strip()))


def _path_parts(url: str) -> List[str]:
    return [
        part.lower()
        for part in urlparse(str(url or "")).path.split("/")
        if part
    ]


def _count_occurrences(text: str, phrases: List[str]) -> int:
    lower = str(text or "").lower()
    return sum(lower.count(phrase.lower()) for phrase in phrases)


def _group_for_page_type(page_type: str) -> str:
    if page_type in KNOWLEDGE_PAGE_TYPES:
        return "knowledge"
    if page_type in DIRECTORY_PAGE_TYPES:
        return "directory"
    if page_type in COMMERCE_PAGE_TYPES:
        return "commerce"
    if page_type in INTERACTIVE_PAGE_TYPES:
        return "interactive"
    if page_type in COMMUNITY_PAGE_TYPES:
        return "community"
    if page_type in MEDIA_PAGE_TYPES:
        return "media"
    if page_type in COMPANY_PAGE_TYPES:
        return "company"
    if page_type in SYSTEM_PAGE_TYPES:
        return "system"
    if page_type in POLICY_PAGE_TYPES:
        return "policy"
    return "unknown"


def _route_for_group(page_group: str) -> str:
    return {
        "knowledge": "website_unified_content",
        "directory": "website_metadata_store",
        "commerce": "website_commerce_store",
        "interactive": "website_tool_store",
        "community": "website_community_store",
        "media": "website_media_store",
        "company": "website_metadata_store",
        "policy": "website_policy_store",
        "system": "ignore",
        "unknown": "manual_review",
    }.get(page_group, "manual_review")


def classify_website_page_v1(
    *,
    url: str,
    cleaned_html: str,
    title: str = "",
    h1: str = "",
    extracted_text: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Universal page-type classifier.

    This component classifies and recommends routing.
    It does not delete, exclude, or write content.
    """

    metadata = metadata or {}

    html_text = str(cleaned_html or "")
    plain = _plain_text(html_text)
    analysis_text = str(extracted_text or plain)

    detected_title = (
        str(title or "").strip()
        or _extract_first(r"<title\b[^>]*>(.*?)</title>", html_text)
    )
    detected_h1 = (
        str(h1 or "").strip()
        or _extract_first(r"<h1\b[^>]*>(.*?)</h1>", html_text)
    )

    combined = " ".join([
        detected_title,
        detected_h1,
        analysis_text[:30000],
    ]).lower()

    path_parts = _path_parts(url)
    path = "/" + "/".join(path_parts)
    schemas = _schema_types(html_text)

    link_count = len(re.findall(r"(?is)<a\b", html_text))
    paragraph_count = len(re.findall(r"(?is)<p\b", html_text))
    heading_count = len(re.findall(r"(?is)<h[1-6]\b", html_text))
    form_count = len(re.findall(r"(?is)<form\b", html_text))
    article_tag_count = len(re.findall(r"(?is)<article\b", html_text))
    product_count = len(re.findall(r"(?is)\bproduct\b", combined))
    word_count = len(analysis_text.split())

    reasons: List[str] = []
    scores: Dict[str, float] = {}

    def add(page_type: str, points: float, reason: str) -> None:
        scores[page_type] = scores.get(page_type, 0.0) + points
        reasons.append(f"{page_type}: {reason}")

    # Schema.org and structural article signals.
    schema_map = {
        "article": "article",
        "newsarticle": "news_article",
        "blogposting": "blog_post",
        "medicalwebpage": "medical_reference",
        "scholarlyarticle": "research_paper",
        "techarticle": "documentation",
        "faqpage": "faq",
        "howto": "guide",
        "recipe": "recipe",
        "product": "product_page",
        "collectionpage": "collection_page",
        "searchresultspage": "search_results",
        "qapage": "q_and_a",
        "discussionforumposting": "forum_thread",
        "videoobject": "video_page",
        "podcastepisode": "podcast_episode",
    }

    for schema_type in schemas:
        mapped = schema_map.get(schema_type)
        if mapped:
            add(mapped, 8.0, f"schema.org type {schema_type}")

    if article_tag_count > 0:
        add("article", 4.0, "article HTML element present")

    if paragraph_count >= 5 and word_count >= 300:
        add("article", 4.0, "substantial paragraph-based content")

    if paragraph_count >= 10 and word_count >= 700:
        add("article", 3.0, "long-form body structure")

    # Knowledge-type signals.
    if any(x in path_parts for x in ["blog", "blogs"]):
        add("blog_post", 4.0, "blog URL path")

    if any(x in path_parts for x in ["news", "press-release", "press-releases"]):
        add("news_article", 4.0, "news or press URL path")

    if any(x in path_parts for x in ["guide", "guides", "tutorial", "tutorials"]):
        add("guide", 4.0, "guide/tutorial URL path")

    if any(x in path_parts for x in ["docs", "documentation", "developer", "api-reference"]):
        add("documentation", 6.0, "documentation URL path")

    if any(x in path_parts for x in ["knowledge-base", "help-center", "kb"]):
        add("knowledge_base_article", 6.0, "knowledge-base URL path")

    if "frequently asked questions" in combined or re.search(r"\bfaq\b", combined):
        add("faq", 4.0, "FAQ language detected")

    if "case study" in combined:
        add("case_study", 5.0, "case-study language detected")

    if "white paper" in combined or "whitepaper" in combined:
        add("white_paper", 5.0, "white-paper language detected")

    if any(term in combined for term in [
        "abstract",
        "methodology",
        "references",
        "peer-reviewed",
    ]) and word_count >= 500:
        add("research_paper", 4.0, "research-document signals")

    if any(term in combined for term in [
        "symptoms",
        "diagnosis",
        "treatment",
        "medical review",
    ]) and word_count >= 300:
        add("medical_reference", 3.0, "medical-reference signals")

    if any(term in combined for term in [
        "legal advice",
        "statute",
        "regulation",
        "case law",
    ]) and word_count >= 300:
        add("legal_reference", 3.0, "legal-reference signals")

    if "review" in detected_title.lower() and word_count >= 300:
        add("product_review", 4.0, "review title and substantial body")

    if any(term in detected_title.lower() for term in [
        " vs ",
        " versus ",
        "comparison",
        "compare ",
    ]):
        add("comparison_article", 4.0, "comparison title")

    if any(term in path_parts for term in ["opinion", "editorial"]):
        add("opinion_editorial", 4.0, "opinion/editorial URL path")

    if any(term in path_parts for term in ["glossary", "dictionary", "definition"]):
        add("glossary_entry", 5.0, "glossary URL path")

    # Directory and listing signals.
    directory_terms = {
        "category": "category_page",
        "categories": "category_page",
        "tag": "tag_page",
        "tags": "tag_page",
        "archive": "archive_page",
        "author": "author_archive",
        "search": "search_results",
        "topics": "topic_hub",
        "topic": "topic_hub",
        "collection": "collection_page",
        "collections": "collection_page",
        "sitemap": "sitemap",
        "browse": "browse_page",
    }

    for term, page_type in directory_terms.items():
        if term in path_parts:
            add(page_type, 6.0, f"{term} URL path")

    repeated_listing_phrases = _count_occurrences(
        combined,
        [
            "recommended reading",
            "see all",
            "related topics",
            "browse all",
            "view all",
            "latest articles",
        ],
    )

    if repeated_listing_phrases >= 4 and link_count >= 30:
        add("topic_hub", 6.0, "high-volume navigational listing signals")

    if link_count >= 60 and paragraph_count <= 5:
        add("collection_page", 6.0, "many links with little paragraph content")

    if "search results" in combined:
        add("search_results", 8.0, "search-results language")

    # Commerce.
    if "product" in schemas:
        add("product_page", 8.0, "Product schema")

    if any(x in path_parts for x in ["product", "products", "shop", "store"]):
        add("product_page", 3.0, "commerce URL path")

    if any(x in path_parts for x in ["cart", "basket"]):
        add("cart", 10.0, "cart URL path")

    if "checkout" in path_parts:
        add("checkout", 10.0, "checkout URL path")

    if any(x in path_parts for x in ["wishlist", "favorites"]):
        add("wishlist", 8.0, "wishlist URL path")

    if "pricing" in path_parts or "pricing" in detected_title.lower():
        add("pricing_page", 5.0, "pricing signals")

    if product_count >= 8 and link_count >= 20:
        add("product_category", 4.0, "multiple product/listing signals")

    # Interactive.
    interactive_map = {
        "calculator": "calculator",
        "quiz": "quiz",
        "converter": "converter",
        "wizard": "wizard",
        "configurator": "configurator",
        "dashboard": "interactive_dashboard",
        "tool": "tool",
    }

    for term, page_type in interactive_map.items():
        if term in path_parts or term in detected_title.lower():
            add(page_type, 7.0, f"{term} signal")

    if form_count >= 2 and word_count < 500:
        add("tool", 3.0, "form-heavy low-text page")

    # Community.
    if any(x in path_parts for x in ["forum", "forums", "thread"]):
        add("forum_thread", 6.0, "forum URL path")

    if any(x in path_parts for x in ["community", "discussions"]):
        add("community_discussion", 5.0, "community URL path")

    if "questions and answers" in combined:
        add("q_and_a", 5.0, "Q&A language")

    # Media.
    if any(x in path_parts for x in ["video", "videos"]):
        add("video_page", 6.0, "video URL path")

    if any(x in path_parts for x in ["podcast", "podcasts"]):
        add("podcast_episode", 6.0, "podcast URL path")

    if any(x in path_parts for x in ["gallery", "galleries", "slideshow"]):
        add("gallery", 7.0, "gallery URL path")

    if "infographic" in path_parts or "infographic" in detected_title.lower():
        add("infographic_page", 6.0, "infographic signal")

    # Company.
    company_map = {
        "about": "about_page",
        "contact": "contact_page",
        "careers": "careers_page",
        "jobs": "careers_page",
        "team": "team_page",
        "events": "events_page",
        "webinar": "webinar_page",
        "partners": "partner_page",
    }

    for term, page_type in company_map.items():
        if term in path_parts:
            add(page_type, 7.0, f"{term} URL path")

    # System and policy.
    system_map = {
        "login": "login",
        "signin": "login",
        "register": "register",
        "signup": "register",
        "account": "account",
        "password-reset": "password_reset",
        "forgot-password": "password_reset",
    }

    for term, page_type in system_map.items():
        if term in path_parts:
            add(page_type, 10.0, f"{term} URL path")

    policy_map = {
        "privacy": "privacy_policy",
        "terms": "terms_of_service",
        "terms-of-use": "terms_of_service",
        "cookies": "cookie_policy",
        "cookie-policy": "cookie_policy",
        "accessibility": "accessibility_page",
        "disclaimer": "disclaimer",
    }

    for term, page_type in policy_map.items():
        if term in path_parts:
            add(page_type, 10.0, f"{term} URL path")

    if re.search(r"\b404\b|page not found|not found", combined):
        add("error_page", 10.0, "error-page content")

    if "maintenance" in combined and word_count < 200:
        add("maintenance_page", 8.0, "maintenance-page content")

    # Timeline/widget pages with almost no prose.
    timeline_tokens = len(re.findall(
        r"\b(?:week|weeks|month|months)\b",
        analysis_text,
        re.IGNORECASE,
    ))

    if timeline_tokens >= 10 and paragraph_count <= 2 and word_count < 150:
        add("interactive_dashboard", 7.0, "timeline/widget pattern")

    if not scores:
        page_type = "unknown"
        confidence = 0.20
        final_reasons = ["No decisive page-type signals"]
    else:
        ordered = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        page_type, top_score = ordered[0]
        second_score = ordered[1][1] if len(ordered) > 1 else 0.0

        margin = max(0.0, top_score - second_score)
        confidence = min(
            0.99,
            0.45 + (top_score * 0.04) + (margin * 0.025),
        )

        final_reasons = [
            reason
            for reason in reasons
            if reason.startswith(f"{page_type}:")
        ]

    page_group = _group_for_page_type(page_type)
    route = _route_for_group(page_group)

    result = PageClassificationResult(
        page_type=page_type,
        page_group=page_group,
        route=route,
        confidence=round(confidence, 4),
        reasons=final_reasons[:20],
        signals={
            "url": url,
            "title": detected_title,
            "h1": detected_h1,
            "schema_types": schemas,
            "word_count": word_count,
            "link_count": link_count,
            "paragraph_count": paragraph_count,
            "heading_count": heading_count,
            "form_count": form_count,
            "article_tag_count": article_tag_count,
            "timeline_token_count": timeline_tokens,
            "scores": dict(
                sorted(
                    scores.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[:10]
            ),
            "metadata": metadata,
        },
    )

    return asdict(result)


def explain_universal_page_type_classifier_v1() -> Dict[str, Any]:
    return {
        "engine": "universal_page_type_classifier_v1",
        "responsibility": "classify page type and recommend routing",
        "does_not_delete_content": True,
        "does_not_write_stores": True,
        "does_not_perform_article_extraction": True,
        "groups": {
            "knowledge": sorted(KNOWLEDGE_PAGE_TYPES),
            "directory": sorted(DIRECTORY_PAGE_TYPES),
            "commerce": sorted(COMMERCE_PAGE_TYPES),
            "interactive": sorted(INTERACTIVE_PAGE_TYPES),
            "community": sorted(COMMUNITY_PAGE_TYPES),
            "media": sorted(MEDIA_PAGE_TYPES),
            "company": sorted(COMPANY_PAGE_TYPES),
            "system": sorted(SYSTEM_PAGE_TYPES),
            "policy": sorted(POLICY_PAGE_TYPES),
        },
    }
