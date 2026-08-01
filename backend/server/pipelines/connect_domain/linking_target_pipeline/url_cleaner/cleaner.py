"""
Universal Article URL Cleaner.

Canonical responsibility:
- receive the complete Site Sources URL inventory
- retain explicit and uncertain content-candidate URLs
- reject definite tools, profiles, generated results and technical URLs
- strip tracking parameters
- canonicalize URL identity for duplicate detection
- remain pure: no filesystem, network, route or store access

Policy:
The Cleaner rejects definite non-content URLs using URL evidence only.
Remaining same-domain content candidates are preserved because URL shape
alone cannot reliably distinguish every article from every section page.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)

CONFIDENCE_EXPLICIT = "explicit"
CONFIDENCE_UNCERTAIN = "uncertain"


EDITORIAL_PATH_RE = re.compile(
    r"/("
    r"article|articles|guide|guides|how-to|howto|"
    r"blog|blogs|post|posts|tutorial|tutorials|"
    r"news|insights|research|resources|learn|academy|"
    r"story|stories|review|reviews"
    r")(/|$)",
    re.IGNORECASE,
)

MEDIA_FILE_RE = re.compile(
    r"\.(jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|"
    r"ppt|pptx|xls|xlsx|zip|rar|7z|tar|gz|mp3|mp4|"
    r"m4a|wav|mov|avi|webm|woff|woff2|ttf|otf|eot)"
    r"(\?|$)",
    re.IGNORECASE,
)

TRACKING_PARAM_RE = re.compile(
    r"^("
    r"utm_.*|gclid|gbraid|wbraid|fbclid|msclkid|"
    r"yclid|ttclid|igshid|_ga|_gl|ref|ref_src|"
    r"referrer|source|campaign|adgroup|adid|"
    r"affiliate|aff|aff_id|srsltid|mc_cid|mc_eid|"
    r"_hsenc|_hsmi"
    r")$",
    re.IGNORECASE,
)

ASSET_PATH_RE = re.compile(
    r"/(images|img|uploads|media|assets|static|gcms)(/|$)",
    re.IGNORECASE,
)

ASSET_SUBDOMAIN_LABELS = {
    "images",
    "img",
    "cdn",
    "static",
    "assets",
    "media",
}

SEARCH_RE = re.compile(
    r"/search(/|$)|[?&](s|q|query|search)=",
    re.IGNORECASE,
)

TAXONOMY_RE = re.compile(
    r"/(tag|tags|category|categories|archive|archives)(/|$)",
    re.IGNORECASE,
)

IDENTITY_RE = re.compile(
    r"/("
    r"author|authors|byline|contributors?|profile|profiles|"
    r"reviewer|reviewers|member|members|user|users|"
    r"community|forums?|groups?"
    r")(/|$)",
    re.IGNORECASE,
)

PAGINATION_PATH_RE = re.compile(
    r"/page/\d+/?$",
    re.IGNORECASE,
)

PAGINATION_QUERY_RE = re.compile(
    r"[?&](paged|page)=\d+",
    re.IGNORECASE,
)

TRANSACTIONAL_RE = re.compile(
    r"/("
    r"login|logout|register|signup|sign-in|account|"
    r"my-account|cart|checkout|orders|wishlist"
    r")(/|$)",
    re.IGNORECASE,
)

API_RE = re.compile(
    r"/(api|graphql|rest|ajax|admin|wp-admin|wp-json)(/|$)",
    re.IGNORECASE,
)

FEED_RE = re.compile(
    r"/(feed|rss|atom)/?$",
    re.IGNORECASE,
)

INFORMATIONAL_RE = re.compile(
    r"/("
    r"privacy|privacy-policy|terms|terms-and-conditions|"
    r"cookie|cookie-policy|contact|about|faq|help|support|"
    r"advertise|newsletter|disclaimer|editorial-policy|"
    r"affiliate-disclosure"
    r")(/|$)",
    re.IGNORECASE,
)

TOOL_AND_RESULT_RE = re.compile(
    r"/("
    r"calculator|calculators|generator|generators|"
    r"quiz|quizzes|tool|tools|finder|finders|"
    r"directory|directories|lookup|results?"
    r")(/|$)",
    re.IGNORECASE,
)

GENERIC_TERMINAL_SLUGS = {
    "home",
    "index",
    "overview",
    "all",
    "browse",
    "topics",
    "topic",
    "resources",
    "resource",
    "products",
    "product",
    "services",
    "service",
    "features",
    "feature",
    "categories",
    "category",
    "registry",
    "milestones",
    "grooming",
    "movement",
    "strollers",
}

NON_WORD_RE = re.compile(
    r"[^a-z0-9]+",
    re.IGNORECASE,
)


def _normalize_domain(value: str) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .removeprefix("http://")
        .removeprefix("https://")
        .split("/", 1)[0]
        .removeprefix("www.")
        .rstrip(".")
    )


def _safe_hostname(parsed) -> str | None:
    try:
        host = (
            parsed.hostname
            or ""
        ).lower().rstrip(".")
    except ValueError:
        return None

    return host or None


def _port_is_valid(parsed) -> bool:
    try:
        parsed.port
        return True
    except ValueError:
        return False


def _is_same_site(
    host: str,
    domain: str,
) -> bool:
    normalized_host = _normalize_domain(host)
    normalized_domain = _normalize_domain(domain)

    if not normalized_host or not normalized_domain:
        return False

    return (
        normalized_host == normalized_domain
        or normalized_host.endswith(
            "." + normalized_domain
        )
    )


def _is_asset_subdomain(
    host: str,
    domain: str,
) -> bool:
    normalized_host = _normalize_domain(host)
    normalized_domain = _normalize_domain(domain)

    if normalized_host == normalized_domain:
        return False

    suffix = "." + normalized_domain

    if not normalized_host.endswith(suffix):
        return False

    relative_host = normalized_host[
        : -len(suffix)
    ].rstrip(".")

    if not relative_host:
        return False

    labels = {
        label
        for label in relative_host.split(".")
        if label
    }

    return bool(
        labels & ASSET_SUBDOMAIN_LABELS
    )


def strip_tracking_params(
    url: str,
) -> tuple[str, bool]:
    parsed = urlparse(url)

    if not parsed.query:
        return url, False

    pairs = parse_qsl(
        parsed.query,
        keep_blank_values=True,
    )

    kept_pairs = [
        (key, value)
        for key, value in pairs
        if not TRACKING_PARAM_RE.fullmatch(key)
    ]

    if len(kept_pairs) == len(pairs):
        return url, False

    cleaned_url = urlunparse(
        parsed._replace(
            query=urlencode(
                kept_pairs,
                doseq=True,
            ),
            fragment="",
        )
    )

    return cleaned_url, True


def canonical_form(url: str) -> str:
    parsed = urlparse(url)

    host = (
        _safe_hostname(parsed)
        or ""
    ).removeprefix("www.")

    path = (
        parsed.path
        or "/"
    ).rstrip("/") or "/"

    query = urlencode(
        sorted(
            parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
        ),
        doseq=True,
    )

    return urlunparse(
        (
            "https",
            host,
            path,
            "",
            query,
            "",
        )
    )


def _path_segments(path: str) -> list[str]:
    return [
        segment
        for segment in path.strip("/").split("/")
        if segment
    ]


def _terminal_slug(path: str) -> str:
    segments = _path_segments(path)

    if not segments:
        return ""

    slug = segments[-1].lower()

    for extension in (
        ".aspx",
        ".html",
        ".htm",
        ".php",
    ):
        if slug.endswith(extension):
            slug = slug[: -len(extension)]
            break

    return slug.strip("-_")


def _slug_tokens(slug: str) -> list[str]:
    return [
        token
        for token in NON_WORD_RE.split(slug)
        if token
    ]


def _looks_like_structural_article(
    path: str,
) -> bool:
    """
    Require meaningful terminal-page evidence.

    This deliberately rejects ambiguous one-segment and shallow hub URLs.
    """
    segments = _path_segments(path)

    if len(segments) < 2:
        return False

    terminal = _terminal_slug(path)

    if not terminal:
        return False

    if terminal in GENERIC_TERMINAL_SLUGS:
        return False

    tokens = _slug_tokens(terminal)

    if len(tokens) < 2:
        return False

    if all(token.isdigit() for token in tokens):
        return False

    return True


@dataclass(frozen=True)
class UrlVerdict:
    accepted: bool
    reason: str
    url: str = ""
    canonical: str = ""
    confidence: str = ""
    tracking_stripped: bool = False


@dataclass
class CleanResult:
    accepted: list[UrlVerdict] = field(
        default_factory=list
    )
    rejected: list[dict] = field(
        default_factory=list
    )
    reason_counts: dict[str, int] = field(
        default_factory=dict
    )
    input_count: int = 0

    @property
    def urls(self) -> list[str]:
        return [
            verdict.url
            for verdict in self.accepted
        ]

    @property
    def explicit_urls(self) -> list[str]:
        return [
            verdict.url
            for verdict in self.accepted
            if verdict.confidence
            == CONFIDENCE_EXPLICIT
        ]

    @property
    def uncertain_urls(self) -> list[str]:
        return [
            verdict.url
            for verdict in self.accepted
            if verdict.confidence
            == CONFIDENCE_UNCERTAIN
        ]

    @property
    def explicit_count(self) -> int:
        return len(self.explicit_urls)

    @property
    def uncertain_count(self) -> int:
        return len(self.uncertain_urls)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)


def classify_url(
    raw_url,
    domain: str,
    *,
    exclude_informational: bool = True,
    exclude_taxonomy: bool = True,
) -> UrlVerdict:
    original_url = str(
        raw_url
        or ""
    ).strip()

    if not original_url:
        return UrlVerdict(
            False,
            "blank_url",
            original_url,
        )

    try:
        parsed = urlparse(original_url)
    except ValueError:
        return UrlVerdict(
            False,
            "invalid_url",
            original_url,
        )

    scheme = (
        parsed.scheme
        or ""
    ).lower()

    host = _safe_hostname(parsed)

    if (
        scheme not in {"http", "https"}
        or not host
        or not _port_is_valid(parsed)
    ):
        return UrlVerdict(
            False,
            "invalid_url",
            original_url,
        )

    if not _is_same_site(host, domain):
        return UrlVerdict(
            False,
            "non_domain_url",
            original_url,
        )

    cleaned_url, tracking_stripped = (
        strip_tracking_params(original_url)
    )

    parsed = urlparse(cleaned_url)

    path = parsed.path or "/"
    path_lower = path.lower()
    normalized_path = path.rstrip("/") or "/"
    lower_url = cleaned_url.lower()
    canonical = canonical_form(cleaned_url)

    def reject(reason: str) -> UrlVerdict:
        return UrlVerdict(
            accepted=False,
            reason=reason,
            url=cleaned_url,
            canonical=canonical,
            tracking_stripped=tracking_stripped,
        )

    if normalized_path == "/":
        return reject("homepage_root")

    if MEDIA_FILE_RE.search(lower_url):
        return reject(
            "media_file_or_download"
        )

    if (
        ASSET_PATH_RE.search(path_lower)
        or _is_asset_subdomain(
            host,
            domain,
        )
    ):
        return reject("image_media_cdn")

    if SEARCH_RE.search(lower_url):
        return reject("search_page")

    if (
        exclude_taxonomy
        and TAXONOMY_RE.search(path_lower)
    ):
        return reject("taxonomy_archive")

    if IDENTITY_RE.search(path_lower):
        return reject(
            "identity_community_page"
        )

    if (
        PAGINATION_PATH_RE.search(path_lower)
        or PAGINATION_QUERY_RE.search(
            lower_url
        )
    ):
        return reject("pagination")

    if TRANSACTIONAL_RE.search(path_lower):
        return reject(
            "private_transactional_page"
        )

    if (
        API_RE.search(path_lower)
        or "xmlrpc.php" in path_lower
    ):
        return reject("api_admin_system")

    if (
        FEED_RE.search(path_lower)
        or path_lower.endswith(
            (".rss", ".atom")
        )
    ):
        return reject("feed_rss_atom")

    if (
        exclude_informational
        and INFORMATIONAL_RE.search(
            path_lower
        )
    ):
        return reject(
            "legal_support_brand_page"
        )

    if TOOL_AND_RESULT_RE.search(path_lower):
        return reject(
            "tool_or_generated_result_page"
        )

    if EDITORIAL_PATH_RE.search(path_lower):
        return UrlVerdict(
            accepted=True,
            reason="accepted_explicit_article",
            url=cleaned_url,
            canonical=canonical,
            confidence=CONFIDENCE_EXPLICIT,
            tracking_stripped=tracking_stripped,
        )

    return UrlVerdict(
        accepted=True,
        reason="accepted_uncertain_content_candidate",
        url=cleaned_url,
        canonical=canonical,
        confidence=CONFIDENCE_UNCERTAIN,
        tracking_stripped=tracking_stripped,
    )


def clean_urls(
    all_urls,
    domain: str,
    *,
    exclude_informational: bool = True,
    exclude_taxonomy: bool = True,
) -> CleanResult:
    input_urls = list(all_urls or [])

    result = CleanResult(
        input_count=len(input_urls)
    )

    seen_canonical_urls: set[str] = set()

    for raw_url in input_urls:
        verdict = classify_url(
            raw_url,
            domain,
            exclude_informational=(
                exclude_informational
            ),
            exclude_taxonomy=exclude_taxonomy,
        )

        if verdict.accepted:
            if (
                verdict.canonical
                in seen_canonical_urls
            ):
                verdict = UrlVerdict(
                    accepted=False,
                    reason="duplicate_url",
                    url=verdict.url,
                    canonical=verdict.canonical,
                    tracking_stripped=(
                        verdict.tracking_stripped
                    ),
                )
            else:
                seen_canonical_urls.add(
                    verdict.canonical
                )

        if verdict.accepted:
            result.accepted.append(verdict)
            continue

        result.rejected.append(
            {
                "url": (
                    verdict.url
                    or str(raw_url or "")
                ),
                "reason": verdict.reason,
            }
        )

        result.reason_counts[
            verdict.reason
        ] = (
            result.reason_counts.get(
                verdict.reason,
                0,
            )
            + 1
        )

    reconciled = (
        len(result.accepted)
        + len(result.rejected)
    )

    if reconciled != result.input_count:
        raise RuntimeError(
            "URL Cleaner count reconciliation failed: "
            f"input={result.input_count}, "
            f"accepted={len(result.accepted)}, "
            f"rejected={len(result.rejected)}"
        )

    return result
