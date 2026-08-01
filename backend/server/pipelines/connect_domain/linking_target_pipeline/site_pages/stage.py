"""
Canonical Site Pages stage.

Responsibility:
- receive accepted URL Cleaner verdicts
- create one Site Page record per accepted canonical URL
- preserve URL, canonical identity, domain, workspace and Cleaner confidence
- return normalized Site Pages records for persistence and downstream handoff

Prohibited:
- no HTML fetching
- no body extraction
- no page-content classification
- no clustering
- no target scoring
- no runtime coordination
- no queue or worker logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


SITE_PAGE_STATUS_READY = "ready"

VALID_CLEANER_CONFIDENCE = {
    "explicit",
    "uncertain",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _read_value(
    record: Any,
    name: str,
    default: Any = "",
) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)

    return getattr(record, name, default)


def _canonical_fallback(url: str) -> str:
    parsed = urlparse(url)

    host = (
        parsed.hostname
        or ""
    ).lower().removeprefix("www.")

    path = (
        parsed.path
        or "/"
    ).rstrip("/") or "/"

    canonical = f"https://{host}{path}"

    if parsed.query:
        canonical += f"?{parsed.query}"

    return canonical


@dataclass(frozen=True)
class SitePageRecord:
    url: str
    canonical_url: str
    domain: str
    workspace_id: str
    cleaner_confidence: str
    status: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "url": self.url,
            "canonical_url": self.canonical_url,
            "domain": self.domain,
            "workspace_id": self.workspace_id,
            "cleaner_confidence": self.cleaner_confidence,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class SitePagesResult:
    workspace_id: str
    domain: str
    pages: list[SitePageRecord] = field(
        default_factory=list
    )
    input_count: int = 0
    created_count: int = 0
    rejected_count: int = 0
    rejection_reason_counts: dict[str, int] = field(
        default_factory=dict
    )
    generated_at: str = field(
        default_factory=_utc_now
    )

    def page_dicts(self) -> list[dict[str, str]]:
        return [
            page.to_dict()
            for page in self.pages
        ]

    def to_payload(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "domain": self.domain,
            "generated_at": self.generated_at,
            "input_count": self.input_count,
            "created_count": self.created_count,
            "rejected_count": self.rejected_count,
            "rejection_reason_counts": dict(
                self.rejection_reason_counts
            ),
            "pages": self.page_dicts(),
        }


def build_site_pages(
    cleaner_records: Iterable[Any],
    *,
    workspace_id: str,
    domain: str,
) -> SitePagesResult:
    normalized_workspace_id = str(
        workspace_id
        or ""
    ).strip()

    normalized_domain = _normalize_domain(domain)

    if not normalized_workspace_id:
        raise ValueError(
            "workspace_id is required"
        )

    if not normalized_domain:
        raise ValueError(
            "domain is required"
        )

    records = list(cleaner_records or [])

    result = SitePagesResult(
        workspace_id=normalized_workspace_id,
        domain=normalized_domain,
        input_count=len(records),
    )

    seen_canonical_urls: set[str] = set()

    def reject(reason: str) -> None:
        result.rejected_count += 1
        result.rejection_reason_counts[reason] = (
            result.rejection_reason_counts.get(
                reason,
                0,
            )
            + 1
        )

    for cleaner_record in records:
        accepted = bool(
            _read_value(
                cleaner_record,
                "accepted",
                True,
            )
        )

        if not accepted:
            reject(
                "cleaner_record_not_accepted"
            )
            continue

        url = str(
            _read_value(
                cleaner_record,
                "url",
                "",
            )
            or ""
        ).strip()

        if not url:
            reject("missing_url")
            continue

        parsed = urlparse(url)

        host = _normalize_domain(
            parsed.hostname
            or ""
        )

        if not host:
            reject("invalid_url")
            continue

        if host != normalized_domain:
            reject("domain_mismatch")
            continue

        canonical_url = str(
            _read_value(
                cleaner_record,
                "canonical",
                "",
            )
            or _read_value(
                cleaner_record,
                "canonical_url",
                "",
            )
            or ""
        ).strip()

        if not canonical_url:
            canonical_url = (
                _canonical_fallback(url)
            )

        confidence = str(
            _read_value(
                cleaner_record,
                "confidence",
                "",
            )
            or _read_value(
                cleaner_record,
                "cleaner_confidence",
                "",
            )
            or ""
        ).strip().lower()

        if confidence not in (
            VALID_CLEANER_CONFIDENCE
        ):
            reject(
                "invalid_cleaner_confidence"
            )
            continue

        if canonical_url in seen_canonical_urls:
            reject(
                "duplicate_canonical_url"
            )
            continue

        seen_canonical_urls.add(
            canonical_url
        )

        result.pages.append(
            SitePageRecord(
                url=url,
                canonical_url=canonical_url,
                domain=normalized_domain,
                workspace_id=(
                    normalized_workspace_id
                ),
                cleaner_confidence=confidence,
                status=SITE_PAGE_STATUS_READY,
                created_at=result.generated_at,
            )
        )

    result.created_count = len(
        result.pages
    )

    reconciled = (
        result.created_count
        + result.rejected_count
    )

    if reconciled != result.input_count:
        raise RuntimeError(
            "Site Pages count reconciliation failed: "
            f"input={result.input_count}, "
            f"created={result.created_count}, "
            f"rejected={result.rejected_count}"
        )

    return result
