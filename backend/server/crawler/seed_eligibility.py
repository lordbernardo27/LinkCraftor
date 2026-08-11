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
import http.client
import ipaddress
import socket
import ssl
from typing import Any, Callable, Dict, Mapping, Tuple
from urllib.parse import urlsplit, urlunsplit

from .seed_models import (
    UniversalWebSeed,
    UniversalWebSeedStatus,
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



STATIC_ELIGIBILITY_STAGE_ORDER = (
    "seed_state",
    "target_extraction",
    "target_normalization",
    "scheme_validation",
    "hostname_validation",
    "port_validation",
    "seed_type_validation",
    "network_validation_required",
)


ALLOWED_STATIC_ELIGIBILITY_TRANSITIONS = {
    "seed_state": (
        "target_extraction",
    ),
    "target_extraction": (
        "target_normalization",
    ),
    "target_normalization": (
        "scheme_validation",
    ),
    "scheme_validation": (
        "hostname_validation",
    ),
    "hostname_validation": (
        "port_validation",
    ),
    "port_validation": (
        "seed_type_validation",
    ),
    "seed_type_validation": (
        "network_validation_required",
    ),
    "network_validation_required": (),
}


def validate_static_eligibility_transition(
    *,
    current_stage: str,
    next_stage: str,
) -> bool:
    """
    Validate one canonical static eligibility stage transition.

    This validator protects the ordering of offline eligibility checks.
    """

    clean_current = required_string(
        current_stage,
        field_name="current_stage",
    )

    clean_next = required_string(
        next_stage,
        field_name="next_stage",
    )

    if clean_current not in ALLOWED_STATIC_ELIGIBILITY_TRANSITIONS:
        raise ValueError(
            "Unsupported static eligibility stage: "
            f"{clean_current}"
        )

    allowed = ALLOWED_STATIC_ELIGIBILITY_TRANSITIONS[
        clean_current
    ]

    if clean_next not in allowed:
        raise ValueError(
            "Invalid static eligibility transition: "
            f"{clean_current} -> {clean_next}"
        )

    return True


def normalize_seed_hostname(
    hostname: str,
) -> str:
    """Normalize a seed hostname without performing DNS resolution."""

    clean_hostname = required_string(
        hostname,
        field_name="hostname",
    ).strip().lower().rstrip(".")

    if any(
        character.isspace()
        for character in clean_hostname
    ):
        raise ValueError(
            "Seed hostname cannot contain whitespace."
        )

    try:
        clean_hostname = clean_hostname.encode(
            "idna"
        ).decode(
            "ascii"
        )
    except UnicodeError as exc:
        raise ValueError(
            "Seed hostname could not be normalized with IDNA."
        ) from exc

    if not clean_hostname:
        raise ValueError(
            "Seed hostname cannot be empty."
        )

    return clean_hostname


def _seed_target_with_default_scheme(
    value: str,
) -> str:
    """
    Ensure a URL-like seed target has a scheme.

    Scheme-less public-web seeds default to HTTPS.
    """

    clean_value = required_string(
        value,
        field_name="original_value",
    ).strip()

    if "://" not in clean_value:
        return f"https://{clean_value}"

    return clean_value


def normalize_static_seed_target(
    *,
    seed_type: UniversalWebSeedType | str,
    original_value: str,
) -> str:
    """
    Normalize one seed target using offline rules only.

    No DNS, HTTP, robots, redirect, or network-safety activity occurs.
    """

    normalized_type = normalize_seed_type(
        seed_type
    )

    candidate = _seed_target_with_default_scheme(
        original_value
    )

    parsed = urlsplit(
        candidate
    )

    scheme = (
        parsed.scheme or ""
    ).lower()

    if scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Seed target must use HTTP or HTTPS."
        )

    if parsed.username is not None:
        raise ValueError(
            "Seed targets containing URL usernames are not supported."
        )

    if parsed.password is not None:
        raise ValueError(
            "Seed targets containing URL passwords are not supported."
        )

    if not parsed.hostname:
        raise ValueError(
            "Seed target does not contain a hostname."
        )

    hostname = normalize_seed_hostname(
        parsed.hostname
    )

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(
            "Seed target contains an invalid port."
        ) from exc

    if (
        scheme == "http"
        and port == 80
    ):
        port = None

    if (
        scheme == "https"
        and port == 443
    ):
        port = None

    if ":" in hostname:
        host_for_netloc = (
            f"[{hostname}]"
        )
    else:
        host_for_netloc = hostname

    if port is not None:
        netloc = (
            f"{host_for_netloc}:{port}"
        )
    else:
        netloc = host_for_netloc

    if (
        normalized_type
        == UniversalWebSeedType.DOMAIN
    ):
        path = "/"
        query = ""
    else:
        path = parsed.path or "/"
        query = parsed.query or ""

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            query,
            "",
        )
    )


def validate_seed_control_state(
    seed: UniversalWebSeed,
) -> SeedEligibilityEvidence:
    """Validate whether the registry seed is active."""

    if not isinstance(
        seed,
        UniversalWebSeed,
    ):
        raise ValueError(
            "seed must be a UniversalWebSeed record."
        )

    active = (
        seed.enabled
        and seed.status
        == UniversalWebSeedStatus.REGISTERED
    )

    if active:
        return SeedEligibilityEvidence(
            check="seed_state",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.ELIGIBLE
            ),
            details={
                "enabled": seed.enabled,
                "status": seed.status.value,
                "active": True,
            },
        )

    return SeedEligibilityEvidence(
        check="seed_state",
        passed=False,
        reason_code=(
            SeedEligibilityReasonCode.SEED_NOT_ACTIVE
        ),
        details={
            "enabled": seed.enabled,
            "status": seed.status.value,
            "active": False,
        },
    )


def validate_seed_scheme(
    normalized_target: str,
) -> SeedEligibilityEvidence:
    """Validate the normalized target scheme."""

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    scheme = (
        parsed.scheme or ""
    ).lower()

    passed = scheme in {
        "http",
        "https",
    }

    return SeedEligibilityEvidence(
        check="scheme_validation",
        passed=passed,
        reason_code=(
            SeedEligibilityReasonCode.ELIGIBLE
            if passed
            else SeedEligibilityReasonCode.INVALID_SCHEME
        ),
        details={
            "scheme": scheme,
        },
    )


def validate_seed_hostname(
    normalized_target: str,
) -> SeedEligibilityEvidence:
    """Validate target hostname syntax without resolving DNS."""

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    hostname = parsed.hostname

    try:
        if hostname is None:
            raise ValueError(
                "hostname missing"
            )

        normalized_hostname = (
            normalize_seed_hostname(
                hostname
            )
        )

        passed = True

    except ValueError:
        normalized_hostname = None
        passed = False

    return SeedEligibilityEvidence(
        check="hostname_validation",
        passed=passed,
        reason_code=(
            SeedEligibilityReasonCode.ELIGIBLE
            if passed
            else SeedEligibilityReasonCode.INVALID_HOSTNAME
        ),
        details={
            "hostname": normalized_hostname,
        },
    )


def validate_seed_port(
    normalized_target: str,
) -> SeedEligibilityEvidence:
    """Validate the target port without connecting to it."""

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    try:
        port = parsed.port
        passed = True
    except ValueError:
        port = None
        passed = False

    return SeedEligibilityEvidence(
        check="port_validation",
        passed=passed,
        reason_code=(
            SeedEligibilityReasonCode.ELIGIBLE
            if passed
            else SeedEligibilityReasonCode.INVALID_PORT
        ),
        details={
            "port": port,
        },
    )


def validate_seed_type_static(
    *,
    seed_type: UniversalWebSeedType | str,
    normalized_target: str,
) -> SeedEligibilityEvidence:
    """Perform static seed-type-specific validation."""

    normalized_type = normalize_seed_type(
        seed_type
    )

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    reason_code = (
        SeedEligibilityReasonCode.ELIGIBLE
    )

    passed = True

    if (
        normalized_type
        == UniversalWebSeedType.SITEMAP
        and not parsed.path
    ):
        passed = False
        reason_code = (
            SeedEligibilityReasonCode.INVALID_SITEMAP_TARGET
        )

    elif (
        normalized_type
        == UniversalWebSeedType.RSS_FEED
        and not parsed.path
    ):
        passed = False
        reason_code = (
            SeedEligibilityReasonCode.INVALID_FEED_TARGET
        )

    return SeedEligibilityEvidence(
        check="seed_type_validation",
        passed=passed,
        reason_code=reason_code,
        details={
            "seed_type": normalized_type.value,
            "path": parsed.path,
        },
    )


def build_static_seed_eligibility_result(
    seed: UniversalWebSeed,
) -> SeedEligibilityResult:
    """
    Run the complete offline Seed Eligibility Validation sequence.

    A statically valid seed returns REVIEW / NETWORK_CHECK_REQUIRED
    because DNS, network safety, reachability, redirects, and robots
    have not yet been evaluated.
    """

    if not isinstance(
        seed,
        UniversalWebSeed,
    ):
        raise ValueError(
            "seed must be a UniversalWebSeed record."
        )

    evidence = []

    state_evidence = validate_seed_control_state(
        seed
    )

    evidence.append(
        state_evidence
    )

    if not state_evidence.passed:
        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.SEED_NOT_ACTIVE
            ),
            normalized_target=None,
            evidence=tuple(
                evidence
            ),
        )

    validate_static_eligibility_transition(
        current_stage="seed_state",
        next_stage="target_extraction",
    )

    original_value = required_string(
        seed.original_value,
        field_name="original_value",
    )

    evidence.append(
        SeedEligibilityEvidence(
            check="target_extraction",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.ELIGIBLE
            ),
            details={
                "original_value": original_value,
            },
        )
    )

    validate_static_eligibility_transition(
        current_stage="target_extraction",
        next_stage="target_normalization",
    )

    try:
        normalized_target = (
            normalize_static_seed_target(
                seed_type=seed.seed_type,
                original_value=original_value,
            )
        )
    except ValueError as exc:
        evidence.append(
            SeedEligibilityEvidence(
                check="target_normalization",
                passed=False,
                reason_code=(
                    SeedEligibilityReasonCode.INVALID_TARGET
                ),
                details={
                    "error": str(exc),
                },
            )
        )

        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.INVALID_TARGET
            ),
            normalized_target=None,
            evidence=tuple(
                evidence
            ),
        )

    evidence.append(
        SeedEligibilityEvidence(
            check="target_normalization",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.ELIGIBLE
            ),
            details={
                "normalized_target": normalized_target,
            },
        )
    )

    validate_static_eligibility_transition(
        current_stage="target_normalization",
        next_stage="scheme_validation",
    )

    scheme_evidence = validate_seed_scheme(
        normalized_target
    )

    evidence.append(
        scheme_evidence
    )

    if not scheme_evidence.passed:
        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.INVALID_SCHEME
            ),
            normalized_target=normalized_target,
            evidence=tuple(
                evidence
            ),
        )

    validate_static_eligibility_transition(
        current_stage="scheme_validation",
        next_stage="hostname_validation",
    )

    hostname_evidence = validate_seed_hostname(
        normalized_target
    )

    evidence.append(
        hostname_evidence
    )

    if not hostname_evidence.passed:
        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.INVALID_HOSTNAME
            ),
            normalized_target=normalized_target,
            evidence=tuple(
                evidence
            ),
        )

    validate_static_eligibility_transition(
        current_stage="hostname_validation",
        next_stage="port_validation",
    )

    port_evidence = validate_seed_port(
        normalized_target
    )

    evidence.append(
        port_evidence
    )

    if not port_evidence.passed:
        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.INVALID_PORT
            ),
            normalized_target=normalized_target,
            evidence=tuple(
                evidence
            ),
        )

    validate_static_eligibility_transition(
        current_stage="port_validation",
        next_stage="seed_type_validation",
    )

    type_evidence = validate_seed_type_static(
        seed_type=seed.seed_type,
        normalized_target=normalized_target,
    )

    evidence.append(
        type_evidence
    )

    if not type_evidence.passed:
        return SeedEligibilityResult(
            seed_id=seed.seed_id,
            workspace_id=seed.workspace_id,
            seed_type=seed.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                type_evidence.reason_code
            ),
            normalized_target=normalized_target,
            evidence=tuple(
                evidence
            ),
        )

    validate_static_eligibility_transition(
        current_stage="seed_type_validation",
        next_stage="network_validation_required",
    )

    evidence.append(
        SeedEligibilityEvidence(
            check="network_validation_required",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
            ),
            details={
                "dns_checked": False,
                "network_safety_checked": False,
                "reachability_checked": False,
                "redirects_checked": False,
                "robots_checked": False,
            },
        )
    )

    return SeedEligibilityResult(
        seed_id=seed.seed_id,
        workspace_id=seed.workspace_id,
        seed_type=seed.seed_type,
        decision=(
            SeedEligibilityDecision.REVIEW
        ),
        reason_code=(
            SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        ),
        normalized_target=normalized_target,
        evidence=tuple(
            evidence
        ),
    )



DNSResolver = Callable[
    [
        str,
        int | None,
        int,
        int,
    ],
    list[
        tuple[
            int,
            int,
            int,
            str,
            tuple,
        ]
    ],
]


def hostname_from_normalized_target(
    normalized_target: str,
) -> str:
    """Extract and normalize the hostname from a static target."""

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    if not parsed.hostname:
        raise ValueError(
            "Normalized seed target does not contain a hostname."
        )

    return normalize_seed_hostname(
        parsed.hostname
    )


def resolve_seed_hostname(
    hostname: str,
    *,
    resolver: Callable[..., Any] = socket.getaddrinfo,
) -> Tuple[str, ...]:
    """
    Resolve one hostname to deterministic unique IP addresses.

    This function performs DNS resolution only. It does not classify
    the returned addresses as public, private, loopback, or otherwise.
    """

    clean_hostname = normalize_seed_hostname(
        hostname
    )

    try:
        records = resolver(
            clean_hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )
    except (
        socket.gaierror,
        OSError,
    ) as exc:
        raise ValueError(
            "DNS resolution failed for seed hostname: "
            f"{clean_hostname}"
        ) from exc

    addresses = []

    for record in records:
        if (
            not isinstance(record, tuple)
            or len(record) < 5
        ):
            continue

        sockaddr = record[4]

        if (
            not isinstance(sockaddr, tuple)
            or not sockaddr
        ):
            continue

        address = str(
            sockaddr[0]
        ).strip()

        if (
            address
            and address not in addresses
        ):
            addresses.append(
                address
            )

    if not addresses:
        raise ValueError(
            "DNS resolution returned no usable IP addresses for "
            f"{clean_hostname}"
        )

    return tuple(
        sorted(addresses)
    )


def validate_seed_dns_resolution(
    normalized_target: str,
    *,
    resolver: Callable[..., Any] = socket.getaddrinfo,
) -> SeedEligibilityEvidence:
    """Resolve the seed hostname and return structured DNS evidence."""

    try:
        hostname = hostname_from_normalized_target(
            normalized_target
        )

        addresses = resolve_seed_hostname(
            hostname,
            resolver=resolver,
        )

    except ValueError as exc:
        return SeedEligibilityEvidence(
            check="dns_resolution",
            passed=False,
            reason_code=(
                SeedEligibilityReasonCode.DNS_RESOLUTION_FAILED
            ),
            details={
                "error": str(exc),
                "addresses": [],
            },
        )

    return SeedEligibilityEvidence(
        check="dns_resolution",
        passed=True,
        reason_code=(
            SeedEligibilityReasonCode.ELIGIBLE
        ),
        details={
            "hostname": hostname,
            "addresses": list(
                addresses
            ),
            "address_count": len(
                addresses
            ),
        },
    )


def build_dns_checked_seed_eligibility_result(
    seed: UniversalWebSeed,
    *,
    resolver: Callable[..., Any] = socket.getaddrinfo,
) -> SeedEligibilityResult:
    """
    Run static validation followed by DNS resolution.

    Successful DNS resolution still returns REVIEW because the resolved
    addresses must next pass Public-Network / SSRF Safety validation.
    """

    static_result = (
        build_static_seed_eligibility_result(
            seed
        )
    )

    if (
        static_result.decision
        != SeedEligibilityDecision.REVIEW
        or static_result.reason_code
        != SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        or not static_result.normalized_target
    ):
        return static_result

    evidence = list(
        static_result.evidence
    )

    dns_evidence = (
        validate_seed_dns_resolution(
            static_result.normalized_target,
            resolver=resolver,
        )
    )

    evidence.append(
        dns_evidence
    )

    if not dns_evidence.passed:
        return SeedEligibilityResult(
            seed_id=static_result.seed_id,
            workspace_id=static_result.workspace_id,
            seed_type=static_result.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.DNS_RESOLUTION_FAILED
            ),
            normalized_target=(
                static_result.normalized_target
            ),
            evidence=tuple(
                evidence
            ),
        )

    evidence.append(
        SeedEligibilityEvidence(
            check="public_network_safety_required",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
            ),
            details={
                "dns_checked": True,
                "network_safety_checked": False,
                "resolved_addresses": (
                    dns_evidence.details.get(
                        "addresses",
                        [],
                    )
                ),
            },
        )
    )

    return SeedEligibilityResult(
        seed_id=static_result.seed_id,
        workspace_id=static_result.workspace_id,
        seed_type=static_result.seed_type,
        decision=(
            SeedEligibilityDecision.REVIEW
        ),
        reason_code=(
            SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        ),
        normalized_target=(
            static_result.normalized_target
        ),
        evidence=tuple(
            evidence
        ),
    )



def classify_seed_network_address(
    address: str,
) -> Dict[str, Any]:
    """
    Classify one DNS-resolved IP address for outbound crawler safety.

    Fail closed. Only globally routable unicast addresses are accepted.
    """

    raw_address = required_string(
        address,
        field_name="address",
    )

    try:
        ip = ipaddress.ip_address(
            raw_address
        )
    except ValueError as exc:
        raise ValueError(
            "Resolved DNS address is not a valid IPv4 or IPv6 address: "
            f"{raw_address}"
        ) from exc

    reasons = []

    if ip.is_unspecified:
        reasons.append(
            "unspecified"
        )

    if ip.is_loopback:
        reasons.append(
            "loopback"
        )

    if ip.is_link_local:
        reasons.append(
            "link_local"
        )

    if ip.is_multicast:
        reasons.append(
            "multicast"
        )

    if ip.is_private:
        reasons.append(
            "private_or_non_global"
        )

    if ip.is_reserved:
        reasons.append(
            "reserved"
        )

    if not ip.is_global:
        reasons.append(
            "not_global"
        )

    reasons = list(
        dict.fromkeys(
            reasons
        )
    )

    is_safe = (
        ip.is_global
        and not ip.is_unspecified
        and not ip.is_loopback
        and not ip.is_link_local
        and not ip.is_multicast
        and not ip.is_private
        and not ip.is_reserved
    )

    return {
        "address": str(ip),
        "version": ip.version,
        "is_safe": is_safe,
        "is_global": ip.is_global,
        "is_private": ip.is_private,
        "is_loopback": ip.is_loopback,
        "is_link_local": ip.is_link_local,
        "is_multicast": ip.is_multicast,
        "is_reserved": ip.is_reserved,
        "is_unspecified": ip.is_unspecified,
        "reasons": reasons,
    }


def validate_seed_public_network_safety(
    addresses: Tuple[str, ...] | list[str],
) -> SeedEligibilityEvidence:
    """
    Require every DNS-resolved address to be globally routable.

    Mixed public/private DNS answers fail closed.
    """

    if not addresses:
        return SeedEligibilityEvidence(
            check="public_network_safety",
            passed=False,
            reason_code=(
                SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET
            ),
            details={
                "error": "No resolved addresses were supplied.",
                "addresses": [],
                "unsafe_addresses": [],
            },
        )

    classifications = []

    try:
        for address in addresses:
            classifications.append(
                classify_seed_network_address(
                    address
                )
            )
    except ValueError as exc:
        return SeedEligibilityEvidence(
            check="public_network_safety",
            passed=False,
            reason_code=(
                SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET
            ),
            details={
                "error": str(exc),
                "addresses": list(
                    addresses
                ),
                "unsafe_addresses": list(
                    addresses
                ),
            },
        )

    unsafe = [
        item
        for item in classifications
        if not item["is_safe"]
    ]

    if unsafe:
        return SeedEligibilityEvidence(
            check="public_network_safety",
            passed=False,
            reason_code=(
                SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET
            ),
            details={
                "address_count": len(
                    classifications
                ),
                "safe_address_count": (
                    len(classifications)
                    - len(unsafe)
                ),
                "unsafe_address_count": len(
                    unsafe
                ),
                "addresses": classifications,
                "unsafe_addresses": [
                    item["address"]
                    for item in unsafe
                ],
            },
        )

    return SeedEligibilityEvidence(
        check="public_network_safety",
        passed=True,
        reason_code=(
            SeedEligibilityReasonCode.ELIGIBLE
        ),
        details={
            "address_count": len(
                classifications
            ),
            "safe_address_count": len(
                classifications
            ),
            "unsafe_address_count": 0,
            "addresses": classifications,
            "unsafe_addresses": [],
        },
    )


def build_network_safe_seed_eligibility_result(
    seed: UniversalWebSeed,
    *,
    resolver: Callable[..., Any] = socket.getaddrinfo,
) -> SeedEligibilityResult:
    """
    Run static validation, DNS resolution, then network-safety validation.

    Successful network safety still cannot grant final eligibility.
    Target Reachability is the next required stage.
    """

    dns_result = (
        build_dns_checked_seed_eligibility_result(
            seed,
            resolver=resolver,
        )
    )

    if (
        dns_result.decision
        != SeedEligibilityDecision.REVIEW
        or dns_result.reason_code
        != SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        or not dns_result.normalized_target
    ):
        return dns_result

    evidence = list(
        dns_result.evidence
    )

    dns_evidence = next(
        (
            item
            for item in reversed(
                evidence
            )
            if item.check
            == "dns_resolution"
        ),
        None,
    )

    if (
        dns_evidence is None
        or not dns_evidence.passed
    ):
        return SeedEligibilityResult(
            seed_id=dns_result.seed_id,
            workspace_id=dns_result.workspace_id,
            seed_type=dns_result.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.DNS_RESOLUTION_FAILED
            ),
            normalized_target=(
                dns_result.normalized_target
            ),
            evidence=tuple(
                evidence
            ),
        )

    resolved_addresses = tuple(
        str(address)
        for address in dns_evidence.details.get(
            "addresses",
            [],
        )
    )

    safety_evidence = (
        validate_seed_public_network_safety(
            resolved_addresses
        )
    )

    evidence.append(
        safety_evidence
    )

    if not safety_evidence.passed:
        return SeedEligibilityResult(
            seed_id=dns_result.seed_id,
            workspace_id=dns_result.workspace_id,
            seed_type=dns_result.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET
            ),
            normalized_target=(
                dns_result.normalized_target
            ),
            evidence=tuple(
                evidence
            ),
        )

    evidence.append(
        SeedEligibilityEvidence(
            check="target_reachability_required",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
            ),
            details={
                "dns_checked": True,
                "public_network_safety_checked": True,
                "reachability_checked": False,
                "resolved_addresses": list(
                    resolved_addresses
                ),
            },
        )
    )

    return SeedEligibilityResult(
        seed_id=dns_result.seed_id,
        workspace_id=dns_result.workspace_id,
        seed_type=dns_result.seed_type,
        decision=(
            SeedEligibilityDecision.REVIEW
        ),
        reason_code=(
            SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        ),
        normalized_target=(
            dns_result.normalized_target
        ),
        evidence=tuple(
            evidence
        ),
    )



DEFAULT_REACHABILITY_TIMEOUT_SECONDS = 8.0

DEFAULT_REACHABILITY_USER_AGENT = (
    "LinkCraftor-AutonomousCrawler/1.0"
)


def _target_request_path(
    normalized_target: str,
) -> str:
    """Build the HTTP request target path and query."""

    parsed = urlsplit(
        required_string(
            normalized_target,
            field_name="normalized_target",
        )
    )

    path = parsed.path or "/"

    if parsed.query:
        return (
            f"{path}?{parsed.query}"
        )

    return path


def _target_host_header(
    *,
    hostname: str,
    scheme: str,
    port: int,
) -> str:
    """Build a correct HTTP Host header."""

    host = normalize_seed_hostname(
        hostname
    )

    if ":" in host:
        host = f"[{host}]"

    default_port = (
        443
        if scheme == "https"
        else 80
    )

    if port == default_port:
        return host

    return f"{host}:{port}"


def probe_seed_target_reachability(
    normalized_target: str,
    *,
    address: str,
    timeout_seconds: float = (
        DEFAULT_REACHABILITY_TIMEOUT_SECONDS
    ),
    user_agent: str = (
        DEFAULT_REACHABILITY_USER_AGENT
    ),
) -> Dict[str, Any]:
    """
    Probe one already-approved IP address for HTTP reachability.

    The TCP connection is pinned to the supplied numeric IP address.
    The original hostname remains responsible for the Host header and
    HTTPS TLS/SNI verification.

    Redirects are never followed here.
    """

    target = required_string(
        normalized_target,
        field_name="normalized_target",
    )

    clean_address = required_string(
        address,
        field_name="address",
    )

    try:
        ip = ipaddress.ip_address(
            clean_address
        )
    except ValueError as exc:
        raise ValueError(
            "Reachability address must be a valid "
            "IPv4 or IPv6 address."
        ) from exc

    if not isinstance(
        timeout_seconds,
        (
            int,
            float,
        ),
    ):
        raise ValueError(
            "timeout_seconds must be numeric."
        )

    timeout = float(
        timeout_seconds
    )

    if timeout <= 0:
        raise ValueError(
            "timeout_seconds must be greater than zero."
        )

    parsed = urlsplit(
        target
    )

    scheme = (
        parsed.scheme or ""
    ).lower()

    if scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Reachability probe supports only HTTP and HTTPS."
        )

    if not parsed.hostname:
        raise ValueError(
            "Reachability target does not contain a hostname."
        )

    hostname = normalize_seed_hostname(
        parsed.hostname
    )

    try:
        explicit_port = parsed.port
    except ValueError as exc:
        raise ValueError(
            "Reachability target contains an invalid port."
        ) from exc

    port = (
        explicit_port
        if explicit_port is not None
        else (
            443
            if scheme == "https"
            else 80
        )
    )

    request_path = _target_request_path(
        target
    )

    host_header = _target_host_header(
        hostname=hostname,
        scheme=scheme,
        port=port,
    )

    headers = {
        "Host": host_header,
        "User-Agent": required_string(
            user_agent,
            field_name="user_agent",
        ),
        "Accept": "*/*",
        "Connection": "close",
    }

    def execute(
        method: str,
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> Dict[str, Any]:

        request_headers = dict(
            headers
        )

        if extra_headers:
            request_headers.update(
                dict(extra_headers)
            )

        raw_socket = None
        transport_socket = None
        connection = None

        try:
            raw_socket = socket.create_connection(
                (
                    str(ip),
                    port,
                ),
                timeout=timeout,
            )

            raw_socket.settimeout(
                timeout
            )

            if scheme == "https":
                context = ssl.create_default_context()

                transport_socket = (
                    context.wrap_socket(
                        raw_socket,
                        server_hostname=hostname,
                    )
                )

                raw_socket = None

            else:
                transport_socket = raw_socket
                raw_socket = None

            connection = http.client.HTTPConnection(
                hostname,
                port,
                timeout=timeout,
            )

            connection.sock = (
                transport_socket
            )

            transport_socket = None

            connection.request(
                method,
                request_path,
                headers=request_headers,
            )

            response = connection.getresponse()

            status = int(
                response.status
            )

            reason = str(
                response.reason or ""
            )

            response_headers = {
                str(key).lower(): str(value)
                for key, value
                in response.getheaders()
            }

            location = response_headers.get(
                "location"
            )

            response.close()

            return {
                "reachable": (
                    100 <= status <= 599
                ),
                "method": method,
                "status": status,
                "reason": reason,
                "address": str(ip),
                "hostname": hostname,
                "port": port,
                "scheme": scheme,
                "request_path": request_path,
                "redirect_detected": (
                    300 <= status <= 399
                    and bool(location)
                ),
                "location": location,
                "headers": response_headers,
            }

        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

            if transport_socket is not None:
                try:
                    transport_socket.close()
                except Exception:
                    pass

            if raw_socket is not None:
                try:
                    raw_socket.close()
                except Exception:
                    pass

    try:
        result = execute(
            "HEAD"
        )

        # Some valid web servers deliberately do not implement HEAD.
        # In that narrow case, perform a tiny GET without following
        # redirects and request only the first byte.
        if result["status"] in {
            405,
            501,
        }:
            result = execute(
                "GET",
                extra_headers={
                    "Range": "bytes=0-0",
                },
            )

            result[
                "head_fallback_used"
            ] = True

        else:
            result[
                "head_fallback_used"
            ] = False

        return result

    except (
        OSError,
        TimeoutError,
        ssl.SSLError,
        http.client.HTTPException,
    ) as exc:
        return {
            "reachable": False,
            "method": None,
            "status": None,
            "reason": None,
            "address": str(ip),
            "hostname": hostname,
            "port": port,
            "scheme": scheme,
            "request_path": request_path,
            "redirect_detected": False,
            "location": None,
            "headers": {},
            "head_fallback_used": False,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def validate_seed_target_reachability(
    normalized_target: str,
    *,
    addresses: Tuple[str, ...] | list[str],
    probe: Callable[..., Mapping[str, Any]] = (
        probe_seed_target_reachability
    ),
    timeout_seconds: float = (
        DEFAULT_REACHABILITY_TIMEOUT_SECONDS
    ),
) -> SeedEligibilityEvidence:
    """
    Determine whether at least one already-approved IP is reachable.

    Every supplied address is assumed to have already passed the
    Public-Network / SSRF Safety stage.
    """

    if not addresses:
        return SeedEligibilityEvidence(
            check="target_reachability",
            passed=False,
            reason_code=(
                SeedEligibilityReasonCode.UNREACHABLE_TARGET
            ),
            details={
                "error": (
                    "No safety-approved addresses "
                    "were supplied."
                ),
                "attempts": [],
            },
        )

    attempts = []

    for address in addresses:
        try:
            result = dict(
                probe(
                    normalized_target,
                    address=str(address),
                    timeout_seconds=timeout_seconds,
                )
            )

        except Exception as exc:
            result = {
                "reachable": False,
                "address": str(address),
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }

        attempts.append(
            result
        )

        if result.get(
            "reachable"
        ) is True:

            return SeedEligibilityEvidence(
                check="target_reachability",
                passed=True,
                reason_code=(
                    SeedEligibilityReasonCode.ELIGIBLE
                ),
                details={
                    "reachable_address": (
                        result.get(
                            "address"
                        )
                    ),
                    "status": (
                        result.get(
                            "status"
                        )
                    ),
                    "method": (
                        result.get(
                            "method"
                        )
                    ),
                    "redirect_detected": bool(
                        result.get(
                            "redirect_detected"
                        )
                    ),
                    "location": (
                        result.get(
                            "location"
                        )
                    ),
                    "attempt_count": len(
                        attempts
                    ),
                    "attempts": attempts,
                },
            )

    return SeedEligibilityEvidence(
        check="target_reachability",
        passed=False,
        reason_code=(
            SeedEligibilityReasonCode.UNREACHABLE_TARGET
        ),
        details={
            "attempt_count": len(
                attempts
            ),
            "attempts": attempts,
        },
    )


def build_reachable_seed_eligibility_result(
    seed: UniversalWebSeed,
    *,
    resolver: Callable[..., Any] = socket.getaddrinfo,
    probe: Callable[..., Mapping[str, Any]] = (
        probe_seed_target_reachability
    ),
    timeout_seconds: float = (
        DEFAULT_REACHABILITY_TIMEOUT_SECONDS
    ),
) -> SeedEligibilityResult:
    """
    Run static, DNS, network-safety, and reachability validation.

    A reachable target still remains REVIEW because redirects must
    next be processed by the dedicated Redirect Safety stage.
    """

    network_result = (
        build_network_safe_seed_eligibility_result(
            seed,
            resolver=resolver,
        )
    )

    if (
        network_result.decision
        != SeedEligibilityDecision.REVIEW
        or network_result.reason_code
        != SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        or not network_result.normalized_target
    ):
        return network_result

    evidence = list(
        network_result.evidence
    )

    dns_evidence = next(
        (
            item
            for item in reversed(
                evidence
            )
            if item.check
            == "dns_resolution"
        ),
        None,
    )

    safety_evidence = next(
        (
            item
            for item in reversed(
                evidence
            )
            if item.check
            == "public_network_safety"
        ),
        None,
    )

    if (
        dns_evidence is None
        or safety_evidence is None
        or not dns_evidence.passed
        or not safety_evidence.passed
    ):
        return SeedEligibilityResult(
            seed_id=network_result.seed_id,
            workspace_id=(
                network_result.workspace_id
            ),
            seed_type=network_result.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.UNSAFE_NETWORK_TARGET
            ),
            normalized_target=(
                network_result.normalized_target
            ),
            evidence=tuple(
                evidence
            ),
        )

    addresses = tuple(
        str(address)
        for address
        in dns_evidence.details.get(
            "addresses",
            [],
        )
    )

    reachability_evidence = (
        validate_seed_target_reachability(
            network_result.normalized_target,
            addresses=addresses,
            probe=probe,
            timeout_seconds=timeout_seconds,
        )
    )

    evidence.append(
        reachability_evidence
    )

    if not reachability_evidence.passed:
        return SeedEligibilityResult(
            seed_id=network_result.seed_id,
            workspace_id=(
                network_result.workspace_id
            ),
            seed_type=network_result.seed_type,
            decision=(
                SeedEligibilityDecision.INELIGIBLE
            ),
            reason_code=(
                SeedEligibilityReasonCode.UNREACHABLE_TARGET
            ),
            normalized_target=(
                network_result.normalized_target
            ),
            evidence=tuple(
                evidence
            ),
        )

    evidence.append(
        SeedEligibilityEvidence(
            check="redirect_safety_required",
            passed=True,
            reason_code=(
                SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
            ),
            details={
                "reachability_checked": True,
                "redirect_safety_checked": False,
                "status": (
                    reachability_evidence.details.get(
                        "status"
                    )
                ),
                "redirect_detected": bool(
                    reachability_evidence.details.get(
                        "redirect_detected"
                    )
                ),
                "location": (
                    reachability_evidence.details.get(
                        "location"
                    )
                ),
            },
        )
    )

    return SeedEligibilityResult(
        seed_id=network_result.seed_id,
        workspace_id=(
            network_result.workspace_id
        ),
        seed_type=network_result.seed_type,
        decision=(
            SeedEligibilityDecision.REVIEW
        ),
        reason_code=(
            SeedEligibilityReasonCode.NETWORK_CHECK_REQUIRED
        ),
        normalized_target=(
            network_result.normalized_target
        ),
        evidence=tuple(
            evidence
        ),
    )


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
            "validate seed control state",
            "extract seed targets",
            "normalize seed targets using offline rules",
            "validate HTTP and HTTPS schemes",
            "validate hostnames",
            "validate ports",
            "apply seed-type static validation",
            "enforce static eligibility stage transitions",
            "return network-check-required review results",
            "resolve normalized seed hostnames through DNS",
            "collect deterministic unique DNS address evidence",
            "reject seeds whose hostnames cannot be resolved",
            "preserve public-network safety as a later decision",
            "classify DNS-resolved IPv4 and IPv6 addresses",
            "reject loopback, private, link-local, multicast, reserved, unspecified, and non-global addresses",
            "fail closed when DNS returns mixed public and unsafe addresses",
            "preserve target reachability as a later decision",
            "probe safety-approved IP addresses for HTTP or HTTPS reachability",
            "pin outbound reachability connections to safety-approved numeric IP addresses",
            "preserve hostname Host headers and HTTPS TLS/SNI verification",
            "prevent automatic redirect following during reachability checks",
            "fall back from unsupported HEAD requests to minimal ranged GET requests",
            "reject targets when no safety-approved address is reachable",
            "preserve redirect safety as the next eligibility decision",
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

    "ALLOWED_STATIC_ELIGIBILITY_TRANSITIONS",
    "STATIC_ELIGIBILITY_STAGE_ORDER",
    "build_static_seed_eligibility_result",
    "normalize_seed_hostname",
    "normalize_static_seed_target",
    "validate_seed_control_state",
    "validate_seed_hostname",
    "validate_seed_port",
    "validate_seed_scheme",
    "validate_seed_type_static",
    "validate_static_eligibility_transition",
    "build_dns_checked_seed_eligibility_result",
    "hostname_from_normalized_target",
    "resolve_seed_hostname",
    "validate_seed_dns_resolution",
    "build_network_safe_seed_eligibility_result",
    "classify_seed_network_address",
    "validate_seed_public_network_safety",
    "DEFAULT_REACHABILITY_TIMEOUT_SECONDS",
    "DEFAULT_REACHABILITY_USER_AGENT",
    "build_reachable_seed_eligibility_result",
    "probe_seed_target_reachability",
    "validate_seed_target_reachability",]
