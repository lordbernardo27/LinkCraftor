"""
LinkCraftor Autonomous Public-Web Crawler
Seed Eligibility Validation

This module defines the canonical Seed Eligibility Validation contract.

Pipeline position:

Universal Web Seed Registry
    ->
Seed Eligibility Validation
    ->
Crawl Frontier

Patch 1 responsibilities:
- define eligibility decisions;
- define eligibility reason codes;
- define immutable eligibility evidence;
- define immutable eligibility results;
- validate eligibility contract fields;
- serialize eligibility evidence and results;
- expose the inspectable Seed Eligibility contract.

This patch does not:
- resolve DNS;
- perform public-network or SSRF safety checks;
- fetch URLs;
- resolve redirects;
- retrieve or evaluate robots.txt;
- parse sitemaps;
- parse feeds;
- determine live network eligibility;
- persist eligibility results;
- insert seeds into the Crawl Frontier;
- schedule crawl work;
- execute crawler workers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .seed_models import (
    UniversalWebSeedType,
    normalize_seed_type,
)
from .session_models import required_string


SEED_ELIGIBILITY_SCHEMA_VERSION = (
    "seed_eligibility_validation.v1"
)


class SeedEligibilityDecision(str, Enum):
    """Canonical Seed Eligibility Validation decisions."""

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    REVIEW = "review"


class SeedEligibilityReasonCode(str, Enum):
    """Canonical reason codes used by eligibility results."""

    ELIGIBLE = "eligible"

    SEED_NOT_ACTIVE = "seed_not_active"
    UNSUPPORTED_SEED_TYPE = "unsupported_seed_type"

    INVALID_TARGET = "invalid_target"
    INVALID_SCHEME = "invalid_scheme"
    INVALID_HOSTNAME = "invalid_hostname"
    INVALID_PORT = "invalid_port"

    DNS_RESOLUTION_FAILED = "dns_resolution_failed"
    PRIVATE_NETWORK_TARGET = "private_network_target"
    LOOPBACK_TARGET = "loopback_target"
    LINK_LOCAL_TARGET = "link_local_target"
    UNSAFE_NETWORK_TARGET = "unsafe_network_target"

    UNREACHABLE_TARGET = "unreachable_target"
    UNSAFE_REDIRECT = "unsafe_redirect"
    REDIRECT_LIMIT_EXCEEDED = "redirect_limit_exceeded"

    ROBOTS_DISALLOWED = "robots_disallowed"
    ROBOTS_UNAVAILABLE = "robots_unavailable"

    INVALID_SITEMAP_TARGET = "invalid_sitemap_target"
    INVALID_FEED_TARGET = "invalid_feed_target"

    NETWORK_CHECK_REQUIRED = "network_check_required"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


def normalize_eligibility_decision(
    value: SeedEligibilityDecision | str,
) -> SeedEligibilityDecision:
    """Normalize and validate an eligibility decision."""

    if isinstance(
        value,
        SeedEligibilityDecision,
    ):
        return value

    try:
        return SeedEligibilityDecision(
            required_string(
                value,
                field_name="decision",
            ).lower()
        )
    except ValueError as exc:
        raise ValueError(
            "Unsupported seed eligibility decision: "
            f"{value}"
        ) from exc


def normalize_eligibility_reason_code(
    value: SeedEligibilityReasonCode | str,
) -> SeedEligibilityReasonCode:
    """Normalize and validate an eligibility reason code."""

    if isinstance(
        value,
        SeedEligibilityReasonCode,
    ):
        return value

    try:
        return SeedEligibilityReasonCode(
            required_string(
                value,
                field_name="reason_code",
            ).lower()
        )
    except ValueError as exc:
        raise ValueError(
            "Unsupported seed eligibility reason code: "
            f"{value}"
        ) from exc


def normalize_details(
    value: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """Return a detached details mapping."""

    if value is None:
        return {}

    if not isinstance(
        value,
        Mapping,
    ):
        raise ValueError(
            "details must be a mapping."
        )

    return dict(value)


@dataclass(frozen=True)
class SeedEligibilityEvidence:
    """
    Immutable evidence emitted by one eligibility check.

    Evidence records describe what was checked without granting
    downstream Crawl Frontier authority.
    """

    check: str
    passed: bool
    reason_code: SeedEligibilityReasonCode
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        clean_check = required_string(
            self.check,
            field_name="check",
        )

        if not isinstance(
            self.passed,
            bool,
        ):
            raise ValueError(
                "passed must be a boolean."
            )

        clean_reason = (
            normalize_eligibility_reason_code(
                self.reason_code
            )
        )

        clean_details = normalize_details(
            self.details
        )

        object.__setattr__(
            self,
            "check",
            clean_check,
        )
        object.__setattr__(
            self,
            "reason_code",
            clean_reason,
        )
        object.__setattr__(
            self,
            "details",
            clean_details,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize eligibility evidence."""

        return {
            "check": self.check,
            "passed": self.passed,
            "reason_code": self.reason_code.value,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class SeedEligibilityResult:
    """
    Immutable Seed Eligibility Validation result.

    This result authorizes or rejects eligibility only.
    It does not insert the seed into the Crawl Frontier.
    """

    seed_id: str
    workspace_id: str
    seed_type: UniversalWebSeedType
    decision: SeedEligibilityDecision
    reason_code: SeedEligibilityReasonCode

    normalized_target: str | None = None

    evidence: Tuple[
        SeedEligibilityEvidence,
        ...,
    ] = ()

    schema_version: str = (
        SEED_ELIGIBILITY_SCHEMA_VERSION
    )

    def __post_init__(self) -> None:
        clean_seed_id = required_string(
            self.seed_id,
            field_name="seed_id",
        )

        clean_workspace_id = required_string(
            self.workspace_id,
            field_name="workspace_id",
        )

        clean_seed_type = normalize_seed_type(
            self.seed_type
        )

        clean_decision = (
            normalize_eligibility_decision(
                self.decision
            )
        )

        clean_reason = (
            normalize_eligibility_reason_code(
                self.reason_code
            )
        )

        if (
            self.normalized_target is not None
            and not isinstance(
                self.normalized_target,
                str,
            )
        ):
            raise ValueError(
                "normalized_target must be a string "
                "or None."
            )

        clean_target = (
            self.normalized_target.strip()
            if isinstance(
                self.normalized_target,
                str,
            )
            else None
        )

        if clean_target == "":
            clean_target = None

        clean_evidence = tuple(
            self.evidence
        )

        for item in clean_evidence:
            if not isinstance(
                item,
                SeedEligibilityEvidence,
            ):
                raise ValueError(
                    "evidence must contain only "
                    "SeedEligibilityEvidence records."
                )

        if (
            self.schema_version
            != SEED_ELIGIBILITY_SCHEMA_VERSION
        ):
            raise ValueError(
                "Unsupported Seed Eligibility "
                "schema version: "
                f"{self.schema_version}"
            )

        object.__setattr__(
            self,
            "seed_id",
            clean_seed_id,
        )
        object.__setattr__(
            self,
            "workspace_id",
            clean_workspace_id,
        )
        object.__setattr__(
            self,
            "seed_type",
            clean_seed_type,
        )
        object.__setattr__(
            self,
            "decision",
            clean_decision,
        )
        object.__setattr__(
            self,
            "reason_code",
            clean_reason,
        )
        object.__setattr__(
            self,
            "normalized_target",
            clean_target,
        )
        object.__setattr__(
            self,
            "evidence",
            clean_evidence,
        )

    @property
    def is_eligible(self) -> bool:
        """Return whether this result grants eligibility."""

        return (
            self.decision
            == SeedEligibilityDecision.ELIGIBLE
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the eligibility result."""

        return {
            "schema_version": self.schema_version,
            "seed_id": self.seed_id,
            "workspace_id": self.workspace_id,
            "seed_type": self.seed_type.value,
            "decision": self.decision.value,
            "reason_code": self.reason_code.value,
            "normalized_target": (
                self.normalized_target
            ),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "is_eligible": self.is_eligible,
        }


def explain_seed_eligibility_validation_v1(
) -> Dict[str, Any]:
    """Return the inspectable Seed Eligibility contract."""

    return {
        "ok": True,
        "component": (
            "seed_eligibility_validation"
        ),
        "schema_version": (
            SEED_ELIGIBILITY_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Seed Eligibility Validation"
        ),
        "previous_pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "next_pipeline_stage": (
            "Crawl Frontier"
        ),
        "decisions": [
            decision.value
            for decision
            in SeedEligibilityDecision
        ],
        "reason_codes": [
            reason.value
            for reason
            in SeedEligibilityReasonCode
        ],
        "contracts": [
            "SeedEligibilityEvidence",
            "SeedEligibilityResult",
        ],
        "responsibilities": [
            "define seed eligibility decisions",
            "define seed eligibility reason codes",
            "define immutable eligibility evidence",
            "define immutable eligibility results",
            "validate eligibility contract fields",
            "serialize eligibility evidence and results",
        ],
        "future_validation_capabilities": [
            "seed control-state validation",
            "seed target normalization",
            "scheme and hostname validation",
            "DNS resolution",
            "public-network and SSRF safety validation",
            "target reachability validation",
            "redirect safety validation",
            "robots.txt evaluation",
            "seed-type-specific validation",
            "final eligibility decision",
        ],
        "excluded_responsibilities": [
            "Universal Web Seed registration",
            "Seed Protection duplicate detection",
            "seed lifecycle controls",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page acquisition",
            "HTML parsing",
            "page classification",
            "Raw HTML persistence",
            "left-arm handoff",
        ],
        "frontier_authority": False,
    }


__all__ = [
    "SEED_ELIGIBILITY_SCHEMA_VERSION",
    "SeedEligibilityDecision",
    "SeedEligibilityEvidence",
    "SeedEligibilityReasonCode",
    "SeedEligibilityResult",
    "explain_seed_eligibility_validation_v1",
    "normalize_eligibility_decision",
    "normalize_eligibility_reason_code",
]
