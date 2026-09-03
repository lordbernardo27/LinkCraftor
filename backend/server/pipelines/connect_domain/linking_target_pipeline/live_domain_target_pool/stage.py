"""
Canonical Live Domain Target Pool stage.

Responsibility:
- receive certified Site Page records
- create one basic live-domain target per Site Page
- preserve Site Page and Cleaner identities
- create deterministic target identities
- return targets for downstream clustering

Prohibited:
- no HTML acquisition
- no content extraction
- no phrase matching
- no target scoring
- no topic or section clustering
- no enrichment
- no Active Target Set filtering
- no queue, worker, job, or coordinator logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


SOURCE_TYPE_LIVE_DOMAIN = "live_domain"
TARGET_STATUS_AVAILABLE = "available"
SITE_PAGE_STATUS_READY = "ready"

VALID_CLEANER_CONFIDENCE = {
    "explicit",
    "uncertain",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_value(
    record: Any,
    name: str,
    default: Any = "",
) -> Any:
    if isinstance(record, Mapping):
        return record.get(name, default)

    return getattr(record, name, default)


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


def _target_id(
    workspace_id: str,
    canonical_url: str,
) -> str:
    identity = (
        f"{workspace_id}\n{canonical_url}"
    ).encode("utf-8")

    digest = hashlib.sha256(
        identity
    ).hexdigest()[:32]

    return f"ldt_{digest}"


@dataclass(frozen=True)
class LiveDomainTargetRecord:
    target_id: str
    url: str
    canonical_url: str
    domain: str
    workspace_id: str
    source_type: str
    site_page_status: str
    cleaner_confidence: str
    target_status: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "target_id": self.target_id,
            "url": self.url,
            "canonical_url": self.canonical_url,
            "domain": self.domain,
            "workspace_id": self.workspace_id,
            "source_type": self.source_type,
            "site_page_status": self.site_page_status,
            "cleaner_confidence": self.cleaner_confidence,
            "target_status": self.target_status,
            "created_at": self.created_at,
        }


@dataclass
class LiveDomainTargetPoolResult:
    workspace_id: str
    domain: str
    targets: list[LiveDomainTargetRecord] = field(
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

    def target_dicts(self) -> list[dict[str, str]]:
        return [
            target.to_dict()
            for target in self.targets
        ]

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": "live_domain_target_pool_v1",
            "type": "live_domain_target_pool",
            "version": "1.0",
            "workspace_id": self.workspace_id,
            "domain": self.domain,
            "generated_at": self.generated_at,
            "input_count": self.input_count,
            "created_count": self.created_count,
            "rejected_count": self.rejected_count,
            "rejection_reason_counts": dict(
                self.rejection_reason_counts
            ),
            "items": self.target_dicts(),
        }


def build_live_domain_target_pool(
    site_pages: Iterable[Any],
    *,
    workspace_id: str,
    domain: str,
) -> LiveDomainTargetPoolResult:
    normalized_workspace_id = str(
        workspace_id
        or ""
    ).strip()

    normalized_domain = _normalize_domain(
        domain
    )

    if not normalized_workspace_id:
        raise ValueError(
            "workspace_id is required"
        )

    if not normalized_domain:
        raise ValueError(
            "domain is required"
        )

    records = list(site_pages or [])

    result = LiveDomainTargetPoolResult(
        workspace_id=normalized_workspace_id,
        domain=normalized_domain,
        input_count=len(records),
    )

    seen_canonical_urls: set[str] = set()
    seen_target_ids: set[str] = set()

    def reject(reason: str) -> None:
        result.rejected_count += 1
        result.rejection_reason_counts[reason] = (
            result.rejection_reason_counts.get(
                reason,
                0,
            )
            + 1
        )

    for site_page in records:
        url = str(
            _read_value(
                site_page,
                "url",
                "",
            )
            or ""
        ).strip()

        canonical_url = str(
            _read_value(
                site_page,
                "canonical_url",
                "",
            )
            or ""
        ).strip()

        record_workspace_id = str(
            _read_value(
                site_page,
                "workspace_id",
                "",
            )
            or ""
        ).strip()

        record_domain = _normalize_domain(
            _read_value(
                site_page,
                "domain",
                "",
            )
        )

        site_page_status = str(
            _read_value(
                site_page,
                "status",
                "",
            )
            or ""
        ).strip().lower()

        confidence = str(
            _read_value(
                site_page,
                "cleaner_confidence",
                "",
            )
            or ""
        ).strip().lower()

        if not url:
            reject("missing_url")
            continue

        if not canonical_url:
            reject("missing_canonical_url")
            continue

        parsed = urlparse(url)

        if not parsed.scheme or not parsed.hostname:
            reject("invalid_url")
            continue

        if record_workspace_id != normalized_workspace_id:
            reject("workspace_mismatch")
            continue

        if record_domain != normalized_domain:
            reject("domain_mismatch")
            continue

        if site_page_status != SITE_PAGE_STATUS_READY:
            reject("site_page_not_ready")
            continue

        if confidence not in VALID_CLEANER_CONFIDENCE:
            reject("invalid_cleaner_confidence")
            continue

        if canonical_url in seen_canonical_urls:
            reject("duplicate_canonical_url")
            continue

        target_id = _target_id(
            normalized_workspace_id,
            canonical_url,
        )

        if target_id in seen_target_ids:
            reject("duplicate_target_id")
            continue

        seen_canonical_urls.add(
            canonical_url
        )
        seen_target_ids.add(
            target_id
        )

        result.targets.append(
            LiveDomainTargetRecord(
                target_id=target_id,
                url=url,
                canonical_url=canonical_url,
                domain=normalized_domain,
                workspace_id=normalized_workspace_id,
                source_type=SOURCE_TYPE_LIVE_DOMAIN,
                site_page_status=site_page_status,
                cleaner_confidence=confidence,
                target_status=TARGET_STATUS_AVAILABLE,
                created_at=result.generated_at,
            )
        )

    result.created_count = len(
        result.targets
    )

    if (
        result.created_count
        + result.rejected_count
        != result.input_count
    ):
        raise RuntimeError(
            "Live Domain Target Pool count "
            "reconciliation failed"
        )

    return result
