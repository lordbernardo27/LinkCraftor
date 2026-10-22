"""Automatic website-source discovery for the Connected Domain pipeline."""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
from urllib.parse import urlsplit

from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
    _normalize_domain,
)


SITE_SOURCES_STAGE_SCHEMA_VERSION = "site_sources_stage_v1"
DEFAULT_MAXIMUM_SITEMAPS = 250
DEFAULT_MAXIMUM_CANDIDATES = 64

HttpGetter = Callable[[str], tuple[int, Any, str]]
SitemapExpander = Callable[..., tuple[Iterable[Any], Iterable[Any]]]
SiteSourcesWriter = Callable[[str, dict[str, Any]], Any]


class SiteSourcesStageError(RuntimeError):
    """Raised when automatic website-source discovery cannot complete."""


@dataclass(frozen=True, slots=True)
class SiteSourcesStageResult:
    schema_version: str
    workspace_id: str
    domain: str
    sitemap_used: str
    sitemap_candidates: tuple[str, ...]
    discovered_urls: tuple[str, ...]
    error_messages: tuple[str, ...]
    persisted: bool

    @property
    def discovered_count(self) -> int:
        return len(self.discovered_urls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "domain": self.domain,
            "sitemap_used": self.sitemap_used,
            "sitemap_candidates": list(
                self.sitemap_candidates
            ),
            "discovered_urls": list(
                self.discovered_urls
            ),
            "discovered_count": self.discovered_count,
            "error_messages": list(
                self.error_messages
            ),
            "persisted": self.persisted,
        }


def _canonical_authorities(
) -> tuple[HttpGetter, SitemapExpander, SiteSourcesWriter]:
    module = importlib.import_module(
        "backend.server.routes.site_reader"
    )

    http_get = getattr(
        module,
        "_http_get",
        None,
    )

    sitemap_expander = getattr(
        module,
        "_fetch_and_expand_sitemaps",
        None,
    )

    site_sources_writer = getattr(
        module,
        "save_site_sources",
        None,
    )

    authorities = (
        http_get,
        sitemap_expander,
        site_sources_writer,
    )

    if not all(
        callable(authority)
        for authority in authorities
    ):
        raise SiteSourcesStageError(
            "Canonical Site Sources authorities are unavailable."
        )

    return authorities


def _error_text(value: Any) -> str:
    if isinstance(value, str):
        return value

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    except Exception:
        return str(value)


def _deduplicate_strings(
    values: Iterable[Any],
) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []

    for value in values:
        normalized = str(
            value or ""
        ).strip()

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        ordered.append(normalized)

    return tuple(ordered)


def _standard_sitemap_candidates(
    domain: str,
) -> tuple[str, ...]:
    return (
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://{domain}/sitemap-index.xml",
        f"https://{domain}/wp-sitemap.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap-index.xml",
        f"https://www.{domain}/wp-sitemap.xml",
    )


def _valid_discovered_sitemap_url(
    value: str,
) -> bool:
    try:
        parsed = urlsplit(value)
    except Exception:
        return False

    return (
        parsed.scheme.lower() in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
    )


def execute_site_sources_stage(
    *,
    workspace_id: str,
    domain: str,
    http_get: HttpGetter | None = None,
    sitemap_expander: SitemapExpander | None = None,
    site_sources_writer: SiteSourcesWriter | None = None,
    maximum_sitemaps: int = DEFAULT_MAXIMUM_SITEMAPS,
    maximum_candidates: int = DEFAULT_MAXIMUM_CANDIDATES,
) -> SiteSourcesStageResult:
    """Discover and persist raw website-provided source URLs only."""

    normalized_workspace_id = str(
        workspace_id or ""
    ).strip()

    if not normalized_workspace_id:
        raise SiteSourcesStageError(
            "workspace_id is required."
        )

    try:
        normalized_domain = _normalize_domain(
            domain
        )
    except Exception as exc:
        raise SiteSourcesStageError(
            "A valid domain is required."
        ) from exc

    if not normalized_domain:
        raise SiteSourcesStageError(
            "A valid domain is required."
        )

    if (
        isinstance(maximum_sitemaps, bool)
        or not isinstance(maximum_sitemaps, int)
        or maximum_sitemaps < 1
        or maximum_sitemaps > 1000
    ):
        raise SiteSourcesStageError(
            "maximum_sitemaps must be between 1 and 1000."
        )

    if (
        isinstance(maximum_candidates, bool)
        or not isinstance(maximum_candidates, int)
        or maximum_candidates < 1
        or maximum_candidates > 256
    ):
        raise SiteSourcesStageError(
            "maximum_candidates must be between 1 and 256."
        )

    if (
        http_get is None
        or sitemap_expander is None
        or site_sources_writer is None
    ):
        (
            canonical_http_get,
            canonical_expander,
            canonical_writer,
        ) = _canonical_authorities()

        http_get = (
            http_get
            if http_get is not None
            else canonical_http_get
        )

        sitemap_expander = (
            sitemap_expander
            if sitemap_expander is not None
            else canonical_expander
        )

        site_sources_writer = (
            site_sources_writer
            if site_sources_writer is not None
            else canonical_writer
        )

    if not callable(http_get):
        raise SiteSourcesStageError(
            "http_get must be callable."
        )

    if not callable(sitemap_expander):
        raise SiteSourcesStageError(
            "sitemap_expander must be callable."
        )

    if not callable(site_sources_writer):
        raise SiteSourcesStageError(
            "site_sources_writer must be callable."
        )

    candidates = list(
        _standard_sitemap_candidates(
            normalized_domain
        )
    )

    errors: list[str] = []

    robots_urls = (
        f"https://{normalized_domain}/robots.txt",
        f"https://www.{normalized_domain}/robots.txt",
    )

    for robots_url in robots_urls:
        try:
            status_code, content, _ = http_get(
                robots_url
            )

            if status_code >= 400 or not content:
                continue

            if isinstance(
                content,
                (
                    bytes,
                    bytearray,
                ),
            ):
                robots_text = bytes(content).decode(
                    "utf-8",
                    errors="replace",
                )
            else:
                robots_text = str(content)

            for raw_line in robots_text.splitlines():
                line = raw_line.strip()

                if not line.lower().startswith(
                    "sitemap:"
                ):
                    continue

                discovered = line.split(
                    ":",
                    1,
                )[1].strip()

                if (
                    discovered
                    and _valid_discovered_sitemap_url(
                        discovered
                    )
                    and discovered not in candidates
                    and len(candidates)
                    < maximum_candidates
                ):
                    candidates.append(
                        discovered
                    )

        except Exception as exc:
            errors.append(
                "robots_fetch_error:"
                + robots_url
                + ":"
                + type(exc).__name__
                + ":"
                + str(exc)
            )

    discovered_urls: tuple[str, ...] = ()
    sitemap_used = ""

    for sitemap_url in candidates[
        :maximum_candidates
    ]:
        try:
            expanded_urls, expansion_errors = (
                sitemap_expander(
                    sitemap_url,
                    max_sitemaps=maximum_sitemaps,
                )
            )

            errors.extend(
                _error_text(error)
                for error in (
                    expansion_errors or ()
                )
            )

            normalized_urls = _deduplicate_strings(
                expanded_urls or ()
            )

            if normalized_urls:
                discovered_urls = normalized_urls
                sitemap_used = sitemap_url
                break

        except Exception as exc:
            errors.append(
                "sitemap_expansion_error:"
                + sitemap_url
                + ":"
                + type(exc).__name__
                + ":"
                + str(exc)
            )

    if not discovered_urls:
        raise SiteSourcesStageError(
            "No website-provided sitemap URLs were discovered."
        )

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    payload = {
        "schema_version": SITE_SOURCES_STAGE_SCHEMA_VERSION,
        "workspace_id": normalized_workspace_id,
        "domain": normalized_domain,
        "updated_at": timestamp,
        "sources": [
            {
                "source_type": "connected_domain",
                "domain": normalized_domain,
                "sitemap_url": sitemap_used,
                "sitemap_urls": list(
                    discovered_urls
                ),
                "sitemap_urls_count": len(
                    discovered_urls
                ),
            }
        ],
        "errors": list(errors),
    }

    try:
        site_sources_writer(
            normalized_workspace_id,
            payload,
        )
    except Exception as exc:
        raise SiteSourcesStageError(
            "Site Sources persistence failed: "
            + type(exc).__name__
            + ": "
            + str(exc)
        ) from exc

    return SiteSourcesStageResult(
        schema_version=SITE_SOURCES_STAGE_SCHEMA_VERSION,
        workspace_id=normalized_workspace_id,
        domain=normalized_domain,
        sitemap_used=sitemap_used,
        sitemap_candidates=tuple(
            candidates[:maximum_candidates]
        ),
        discovered_urls=discovered_urls,
        error_messages=tuple(errors),
        persisted=True,
    )


__all__ = [
    "SITE_SOURCES_STAGE_SCHEMA_VERSION",
    "SiteSourcesStageError",
    "SiteSourcesStageResult",
    "execute_site_sources_stage",
]
