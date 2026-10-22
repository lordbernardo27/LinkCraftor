"""Immutable stage boundary for the canonical URL Cleaner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Mapping

from .cleaner import (
    _normalize_domain,
    clean_urls,
)


URL_CLEANER_STAGE_SCHEMA_VERSION = "url_cleaner_stage_v1"

Cleaner = Callable[..., Any]


class UrlCleanerStageError(ValueError):
    """Raised when URL Cleaner stage execution fails closed."""


@dataclass(frozen=True, slots=True)
class UrlRejectionEvidence:
    url: str
    reason: str
    canonical: str
    confidence: str
    tracking_stripped: bool


@dataclass(frozen=True, slots=True)
class UrlCleanerStageResult:
    schema_version: str
    workspace_id: str
    domain: str
    input_count: int
    cleaned_urls: tuple[str, ...]
    explicit_urls: tuple[str, ...]
    uncertain_urls: tuple[str, ...]
    rejected: tuple[UrlRejectionEvidence, ...]
    rejection_reason_counts: tuple[tuple[str, int], ...]

    @property
    def cleaned_count(self) -> int:
        return len(self.cleaned_urls)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "workspace_id": self.workspace_id,
            "domain": self.domain,
            "input_count": self.input_count,
            "cleaned_urls": list(
                self.cleaned_urls
            ),
            "cleaned_count": self.cleaned_count,
            "explicit_urls": list(
                self.explicit_urls
            ),
            "uncertain_urls": list(
                self.uncertain_urls
            ),
            "rejected": [
                asdict(item)
                for item in self.rejected
            ],
            "rejected_count": self.rejected_count,
            "rejection_reason_counts": dict(
                self.rejection_reason_counts
            ),
        }


def _value(
    item: Any,
    name: str,
    default: Any,
) -> Any:
    if isinstance(item, Mapping):
        return item.get(
            name,
            default,
        )

    return getattr(
        item,
        name,
        default,
    )


def execute_url_cleaner_stage(
    *,
    workspace_id: str,
    domain: str,
    source_urls: Iterable[Any],
    exclude_informational: bool = True,
    exclude_taxonomy: bool = True,
    cleaner: Cleaner = clean_urls,
) -> UrlCleanerStageResult:
    """Clean raw Site Sources URLs without executing downstream stages."""

    normalized_workspace_id = str(
        workspace_id or ""
    ).strip()

    if not normalized_workspace_id:
        raise UrlCleanerStageError(
            "workspace_id is required."
        )

    normalized_domain = _normalize_domain(
        domain
    )

    if not normalized_domain:
        raise UrlCleanerStageError(
            "A valid domain is required."
        )

    if isinstance(
        source_urls,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise UrlCleanerStageError(
            "source_urls must be an iterable of URL values."
        )

    try:
        raw_urls = tuple(
            source_urls
        )
    except TypeError as exc:
        raise UrlCleanerStageError(
            "source_urls must be iterable."
        ) from exc

    if not raw_urls:
        raise UrlCleanerStageError(
            "At least one source URL is required."
        )

    if not callable(cleaner):
        raise UrlCleanerStageError(
            "cleaner must be callable."
        )

    try:
        result = cleaner(
            raw_urls,
            normalized_domain,
            exclude_informational=bool(
                exclude_informational
            ),
            exclude_taxonomy=bool(
                exclude_taxonomy
            ),
        )
    except Exception as exc:
        raise UrlCleanerStageError(
            "URL Cleaner execution failed: "
            + type(exc).__name__
            + ": "
            + str(exc)
        ) from exc

    cleaned_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "urls",
            (),
        )
        if str(value).strip()
    )

    explicit_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "explicit_urls",
            (),
        )
        if str(value).strip()
    )

    uncertain_urls = tuple(
        str(value).strip()
        for value in getattr(
            result,
            "uncertain_urls",
            (),
        )
        if str(value).strip()
    )

    rejected = tuple(
        UrlRejectionEvidence(
            url=str(
                _value(
                    item,
                    "url",
                    "",
                )
            ),
            reason=str(
                _value(
                    item,
                    "reason",
                    "",
                )
            ),
            canonical=str(
                _value(
                    item,
                    "canonical",
                    "",
                )
            ),
            confidence=str(
                _value(
                    item,
                    "confidence",
                    "",
                )
            ),
            tracking_stripped=bool(
                _value(
                    item,
                    "tracking_stripped",
                    False,
                )
            ),
        )
        for item in getattr(
            result,
            "rejected",
            (),
        )
    )

    reason_counts = tuple(
        sorted(
            (
                str(reason),
                int(count),
            )
            for reason, count in dict(
                getattr(
                    result,
                    "reason_counts",
                    {},
                )
            ).items()
        )
    )

    input_count = int(
        getattr(
            result,
            "input_count",
            len(raw_urls),
        )
    )

    if input_count != len(raw_urls):
        raise UrlCleanerStageError(
            "Canonical cleaner returned an invalid input count."
        )

    if len(set(cleaned_urls)) != len(cleaned_urls):
        raise UrlCleanerStageError(
            "Canonical cleaner returned duplicate URLs."
        )

    if (
        len(cleaned_urls)
        + len(rejected)
        != input_count
    ):
        raise UrlCleanerStageError(
            "URL Cleaner accounting invariant failed."
        )

    return UrlCleanerStageResult(
        schema_version=URL_CLEANER_STAGE_SCHEMA_VERSION,
        workspace_id=normalized_workspace_id,
        domain=normalized_domain,
        input_count=input_count,
        cleaned_urls=cleaned_urls,
        explicit_urls=explicit_urls,
        uncertain_urls=uncertain_urls,
        rejected=rejected,
        rejection_reason_counts=reason_counts,
    )


__all__ = [
    "URL_CLEANER_STAGE_SCHEMA_VERSION",
    "UrlCleanerStageError",
    "UrlCleanerStageResult",
    "UrlRejectionEvidence",
    "execute_url_cleaner_stage",
]
