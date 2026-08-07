"""
LinkCraftor Autonomous Public-Web Crawler
Universal Web Seed Protection

This module protects the Universal Web Seed Registry against duplicate
and conflicting seed targets.

Responsibilities:
- build comparison-only canonical seed targets;
- generate deterministic target fingerprints;
- inspect seeds against other records in the same workspace;
- identify exact duplicates;
- identify canonical duplicates;
- identify domain duplicates;
- identify seed-type conflicts;
- identify non-blocking related-domain relationships;
- apply disabled and archived-record policies;
- persist protection evidence through the certified seed repository;
- return stable protection results.

This module does not:
- register seeds;
- control seed lifecycle;
- delete or merge seed records;
- perform full crawl-pipeline URL normalization;
- resolve DNS;
- inspect public-network safety;
- fetch URLs;
- resolve redirects;
- inspect canonical tags;
- evaluate robots.txt;
- parse sitemaps or feeds;
- determine seed eligibility;
- insert URLs into the Crawl Frontier.
"""

from __future__ import annotations

import hashlib
import ipaddress
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

from .seed_models import (
    UniversalWebSeed,
    UniversalWebSeedStatus,
    UniversalWebSeedType,
    normalize_seed_type,
)
from .seed_repository import (
    list_universal_web_seeds,
    require_universal_web_seed,
    update_universal_web_seed,
)
from .session_models import required_string


UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION = (
    "universal_web_seed_protection.v1"
)


class SeedComparisonFamily(str, Enum):
    """Canonical Seed Protection comparison families."""

    WEB_PAGE_TARGET = "web_page_target"
    DOMAIN_TARGET = "domain_target"
    SITEMAP_TARGET = "sitemap_target"
    FEED_TARGET = "feed_target"


class SeedProtectionClassification(str, Enum):
    """Canonical duplicate and conflict classifications."""

    NO_CONFLICT = "no_conflict"
    EXACT_DUPLICATE = "exact_duplicate"
    CANONICAL_DUPLICATE = "canonical_duplicate"
    DOMAIN_DUPLICATE = "domain_duplicate"
    TYPE_CONFLICT = "type_conflict"
    RELATED_DOMAIN = "related_domain"
    POSSIBLE_EQUIVALENCE = "possible_equivalence"


class SeedProtectionDecision(str, Enum):
    """Canonical Seed Protection decisions."""

    ALLOW = "allow"
    BLOCK_DUPLICATE = "block_duplicate"
    BLOCK_TYPE_CONFLICT = "block_type_conflict"
    REVIEW = "review"


COMPARISON_FAMILY_BY_SEED_TYPE = {
    UniversalWebSeedType.URL: (
        SeedComparisonFamily.WEB_PAGE_TARGET
    ),
    UniversalWebSeedType.DOMAIN: (
        SeedComparisonFamily.DOMAIN_TARGET
    ),
    UniversalWebSeedType.SITEMAP: (
        SeedComparisonFamily.SITEMAP_TARGET
    ),
    UniversalWebSeedType.RSS_FEED: (
        SeedComparisonFamily.FEED_TARGET
    ),
}


BLOCKING_DUPLICATE_CLASSIFICATIONS = {
    SeedProtectionClassification.EXACT_DUPLICATE,
    SeedProtectionClassification.CANONICAL_DUPLICATE,
    SeedProtectionClassification.DOMAIN_DUPLICATE,
}


URL_RESOURCE_FAMILIES = {
    SeedComparisonFamily.WEB_PAGE_TARGET,
    SeedComparisonFamily.SITEMAP_TARGET,
    SeedComparisonFamily.FEED_TARGET,
}


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def normalize_hostname(
    hostname: str,
    *,
    strip_www: bool = False,
) -> str:
    """Normalize a hostname for comparison."""

    clean_hostname = required_string(
        hostname,
        field_name="hostname",
    ).strip().lower().rstrip(".")

    try:
        clean_hostname = clean_hostname.encode(
            "idna"
        ).decode(
            "ascii"
        )
    except UnicodeError as exc:
        raise ValueError(
            "Hostname could not be normalized with IDNA."
        ) from exc

    if (
        strip_www
        and clean_hostname.startswith("www.")
        and len(clean_hostname) > 4
    ):
        clean_hostname = clean_hostname[4:]

    return clean_hostname


def parse_url_like_value(
    value: str,
    *,
    default_scheme: str = "https",
):
    """
    Parse a URL-like target.

    Scheme-less values are parsed by temporarily adding the requested
    default scheme. This performs no network activity.
    """

    clean_value = required_string(
        value,
        field_name="target_value",
    )

    candidate = clean_value

    if "://" not in candidate:
        candidate = (
            f"{default_scheme}://{candidate}"
        )

    parsed = urlsplit(
        candidate
    )

    if not parsed.hostname:
        raise ValueError(
            "Seed target does not contain a valid hostname."
        )

    return parsed


def normalized_port(
    *,
    scheme: str,
    port: int | None,
) -> int | None:
    """Remove a default HTTP or HTTPS port."""

    if port is None:
        return None

    if scheme == "http" and port == 80:
        return None

    if scheme == "https" and port == 443:
        return None

    return port


def normalize_url_path(
    path: str,
) -> str:
    """Normalize a URL path for comparison."""

    normalized = path or "/"

    if (
        normalized != "/"
        and normalized.endswith("/")
    ):
        normalized = normalized.rstrip("/")

        if not normalized:
            normalized = "/"

    return normalized


def normalize_url_query(
    query: str,
) -> str:
    """Sort query parameters deterministically."""

    if not query:
        return ""

    query_items = parse_qsl(
        query,
        keep_blank_values=True,
        strict_parsing=False,
    )

    query_items.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return urlencode(
        query_items,
        doseq=True,
    )


def build_normalized_netloc(
    *,
    hostname: str,
    port: int | None,
) -> str:
    """Build a comparison-safe URL network location."""

    try:
        ip_value = ipaddress.ip_address(
            hostname
        )
    except ValueError:
        host_text = hostname
    else:
        if ip_value.version == 6:
            host_text = f"[{hostname}]"
        else:
            host_text = hostname

    if port is None:
        return host_text

    return f"{host_text}:{port}"


def normalize_url_resource_target(
    value: str,
) -> str:
    """Normalize a URL-like resource for comparison only."""

    parsed = parse_url_like_value(
        value
    )

    scheme = parsed.scheme.lower()

    if scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Seed URL comparison supports only HTTP "
            "and HTTPS schemes."
        )

    hostname = normalize_hostname(
        parsed.hostname or "",
        strip_www=False,
    )

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(
            "Seed target contains an invalid port."
        ) from exc

    port = normalized_port(
        scheme=scheme,
        port=port,
    )

    netloc = build_normalized_netloc(
        hostname=hostname,
        port=port,
    )

    path = normalize_url_path(
        parsed.path
    )

    query = normalize_url_query(
        parsed.query
    )

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            query,
            "",
        )
    )


def normalize_domain_target(
    value: str,
) -> str:
    """Normalize a domain seed target for comparison only."""

    parsed = parse_url_like_value(
        value
    )

    return normalize_hostname(
        parsed.hostname or "",
        strip_www=True,
    )


def comparison_family_for_seed_type(
    seed_type: UniversalWebSeedType | str,
) -> SeedComparisonFamily:
    """Return the comparison family for one seed type."""

    normalized_type = normalize_seed_type(
        seed_type
    )

    return COMPARISON_FAMILY_BY_SEED_TYPE[
        normalized_type
    ]


def build_seed_comparison_target(
    *,
    seed_type: UniversalWebSeedType | str,
    original_value: str,
) -> Dict[str, str]:
    """
    Build a canonical comparison representation.

    This function does not update or persist the seed record.
    """

    normalized_type = normalize_seed_type(
        seed_type
    )

    clean_original_value = required_string(
        original_value,
        field_name="original_value",
    )

    comparison_family = (
        comparison_family_for_seed_type(
            normalized_type
        )
    )

    if normalized_type == UniversalWebSeedType.DOMAIN:
        comparison_target = normalize_domain_target(
            clean_original_value
        )
    else:
        comparison_target = (
            normalize_url_resource_target(
                clean_original_value
            )
        )

    return {
        "seed_type": normalized_type.value,
        "comparison_family": (
            comparison_family.value
        ),
        "comparison_target": comparison_target,
    }


def generate_seed_target_fingerprint(
    *,
    workspace_id: str,
    comparison_family: SeedComparisonFamily | str,
    comparison_target: str,
) -> str:
    """Generate a deterministic workspace-scoped SHA-256 fingerprint."""

    clean_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    if isinstance(
        comparison_family,
        SeedComparisonFamily,
    ):
        normalized_family = comparison_family
    else:
        try:
            normalized_family = SeedComparisonFamily(
                comparison_family
            )
        except ValueError as exc:
            raise ValueError(
                "Unsupported seed comparison family: "
                f"{comparison_family}"
            ) from exc

    clean_target = required_string(
        comparison_target,
        field_name="comparison_target",
    )

    fingerprint_source = "|".join(
        [
            clean_workspace_id,
            normalized_family.value,
            clean_target,
        ]
    )

    digest = hashlib.sha256(
        fingerprint_source.encode(
            "utf-8"
        )
    ).hexdigest()

    return f"sha256:{digest}"


def hostname_from_comparison_target(
    *,
    comparison_family: SeedComparisonFamily,
    comparison_target: str,
) -> str:
    """Extract the normalized host represented by a comparison target."""

    if (
        comparison_family
        == SeedComparisonFamily.DOMAIN_TARGET
    ):
        return normalize_hostname(
            comparison_target,
            strip_www=True,
        )

    parsed = urlsplit(
        comparison_target
    )

    if not parsed.hostname:
        raise ValueError(
            "Comparison target does not contain a hostname."
        )

    return normalize_hostname(
        parsed.hostname,
        strip_www=True,
    )


def same_resource_across_url_families(
    *,
    candidate_family: SeedComparisonFamily,
    candidate_target: str,
    existing_family: SeedComparisonFamily,
    existing_target: str,
) -> bool:
    """Return whether two URL-family targets identify the same resource."""

    return (
        candidate_family in URL_RESOURCE_FAMILIES
        and existing_family in URL_RESOURCE_FAMILIES
        and candidate_target == existing_target
    )


def hosts_are_related(
    candidate_host: str,
    existing_host: str,
) -> bool:
    """Return whether two hosts are equal or nested within one another."""

    candidate = normalize_hostname(
        candidate_host,
        strip_www=True,
    )

    existing = normalize_hostname(
        existing_host,
        strip_www=True,
    )

    return (
        candidate == existing
        or candidate.endswith(
            "." + existing
        )
        or existing.endswith(
            "." + candidate
        )
    )


def classify_seed_match(
    *,
    candidate_seed: UniversalWebSeed,
    candidate_family: SeedComparisonFamily,
    candidate_target: str,
    candidate_fingerprint: str,
    existing_seed: UniversalWebSeed,
    existing_family: SeedComparisonFamily,
    existing_target: str,
    existing_fingerprint: str,
) -> SeedProtectionClassification:
    """Classify one candidate-to-existing seed relationship."""

    if candidate_seed.seed_id == existing_seed.seed_id:
        return SeedProtectionClassification.NO_CONFLICT

    same_original = (
        candidate_seed.original_value.strip()
        == existing_seed.original_value.strip()
    )

    same_type = (
        candidate_seed.seed_type
        == existing_seed.seed_type
    )

    same_family = (
        candidate_family
        == existing_family
    )

    same_target = (
        candidate_target
        == existing_target
    )

    same_fingerprint = (
        candidate_fingerprint
        == existing_fingerprint
    )

    if (
        same_type
        and same_target
        and same_original
    ):
        if (
            candidate_family
            == SeedComparisonFamily.DOMAIN_TARGET
        ):
            return (
                SeedProtectionClassification.DOMAIN_DUPLICATE
            )

        return (
            SeedProtectionClassification.EXACT_DUPLICATE
        )

    if (
        same_type
        and same_family
        and same_target
        and same_fingerprint
    ):
        if (
            candidate_family
            == SeedComparisonFamily.DOMAIN_TARGET
        ):
            return (
                SeedProtectionClassification.DOMAIN_DUPLICATE
            )

        return (
            SeedProtectionClassification.CANONICAL_DUPLICATE
        )

    if same_resource_across_url_families(
        candidate_family=candidate_family,
        candidate_target=candidate_target,
        existing_family=existing_family,
        existing_target=existing_target,
    ):
        return (
            SeedProtectionClassification.TYPE_CONFLICT
        )

    candidate_host = hostname_from_comparison_target(
        comparison_family=candidate_family,
        comparison_target=candidate_target,
    )

    existing_host = hostname_from_comparison_target(
        comparison_family=existing_family,
        comparison_target=existing_target,
    )

    if hosts_are_related(
        candidate_host,
        existing_host,
    ):
        return (
            SeedProtectionClassification.RELATED_DOMAIN
        )

    return SeedProtectionClassification.NO_CONFLICT


def classification_reason_code(
    classification: SeedProtectionClassification,
) -> str:
    """Return the stable reason code for one classification."""

    reason_codes = {
        SeedProtectionClassification.NO_CONFLICT: (
            "no_conflicting_seed_target"
        ),
        SeedProtectionClassification.EXACT_DUPLICATE: (
            "same_original_target_same_seed_type"
        ),
        SeedProtectionClassification.CANONICAL_DUPLICATE: (
            "same_canonical_target_same_seed_type"
        ),
        SeedProtectionClassification.DOMAIN_DUPLICATE: (
            "same_comparison_domain"
        ),
        SeedProtectionClassification.TYPE_CONFLICT: (
            "same_canonical_resource_different_seed_type"
        ),
        SeedProtectionClassification.RELATED_DOMAIN: (
            "related_hostname_distinct_seed_target"
        ),
        SeedProtectionClassification.POSSIBLE_EQUIVALENCE: (
            "possible_target_equivalence_requires_review"
        ),
    }

    return reason_codes[
        classification
    ]


def classification_is_blocking(
    classification: SeedProtectionClassification,
) -> bool:
    """Return whether the classification normally blocks."""

    return (
        classification
        in BLOCKING_DUPLICATE_CLASSIFICATIONS
        or classification
        == SeedProtectionClassification.TYPE_CONFLICT
    )


def build_seed_match_record(
    *,
    existing_seed: UniversalWebSeed,
    comparison_family: SeedComparisonFamily,
    comparison_target: str,
    target_fingerprint: str,
    classification: SeedProtectionClassification,
) -> Dict[str, Any]:
    """Build one stable protection match record."""

    blocking = classification_is_blocking(
        classification
    )

    review_required = False

    if (
        existing_seed.status
        == UniversalWebSeedStatus.ARCHIVED
        and classification
        in (
            BLOCKING_DUPLICATE_CLASSIFICATIONS
            | {
                SeedProtectionClassification.TYPE_CONFLICT,
            }
        )
    ):
        blocking = False
        review_required = True

    return {
        "seed_id": existing_seed.seed_id,
        "seed_type": existing_seed.seed_type.value,
        "status": existing_seed.status.value,
        "enabled": existing_seed.enabled,
        "original_value": existing_seed.original_value,
        "comparison_family": comparison_family.value,
        "comparison_target": comparison_target,
        "target_fingerprint": target_fingerprint,
        "classification": classification.value,
        "blocking": blocking,
        "review_required": review_required,
        "reason_code": classification_reason_code(
            classification
        ),
    }


def decide_seed_protection(
    matches: List[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Determine the final Seed Protection decision."""

    blocking_type_conflicts = [
        match
        for match in matches
        if (
            match.get("classification")
            == SeedProtectionClassification.TYPE_CONFLICT.value
            and match.get("blocking") is True
        )
    ]

    if blocking_type_conflicts:
        return {
            "decision": (
                SeedProtectionDecision
                .BLOCK_TYPE_CONFLICT.value
            ),
            "blocking": True,
            "review_required": False,
            "reason_code": (
                "blocking_seed_type_conflict_found"
            ),
        }

    blocking_duplicates = [
        match
        for match in matches
        if (
            match.get("classification")
            in {
                classification.value
                for classification
                in BLOCKING_DUPLICATE_CLASSIFICATIONS
            }
            and match.get("blocking") is True
        )
    ]

    if blocking_duplicates:
        return {
            "decision": (
                SeedProtectionDecision
                .BLOCK_DUPLICATE.value
            ),
            "blocking": True,
            "review_required": False,
            "reason_code": (
                "blocking_duplicate_seed_target_found"
            ),
        }

    review_matches = [
        match
        for match in matches
        if match.get("review_required") is True
    ]

    if review_matches:
        return {
            "decision": (
                SeedProtectionDecision.REVIEW.value
            ),
            "blocking": False,
            "review_required": True,
            "reason_code": (
                "archived_or_uncertain_match_requires_review"
            ),
        }

    return {
        "decision": (
            SeedProtectionDecision.ALLOW.value
        ),
        "blocking": False,
        "review_required": False,
        "reason_code": (
            "no_conflicting_seed_target"
        ),
    }


def inspect_seed_protection(
    *,
    workspace_id: str,
    seed_id: str,
) -> Dict[str, Any]:
    """
    Inspect one seed against all other workspace seeds.

    This operation is read-only and does not persist protection evidence.
    """

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    candidate_comparison = (
        build_seed_comparison_target(
            seed_type=seed.seed_type,
            original_value=seed.original_value,
        )
    )

    candidate_family = SeedComparisonFamily(
        candidate_comparison[
            "comparison_family"
        ]
    )

    candidate_target = candidate_comparison[
        "comparison_target"
    ]

    candidate_fingerprint = (
        generate_seed_target_fingerprint(
            workspace_id=seed.workspace_id,
            comparison_family=candidate_family,
            comparison_target=candidate_target,
        )
    )

    workspace_seeds = list_universal_web_seeds(
        workspace_id=seed.workspace_id
    )

    matches: List[Dict[str, Any]] = []

    for existing_seed in workspace_seeds:
        if existing_seed.seed_id == seed.seed_id:
            continue

        existing_comparison = (
            build_seed_comparison_target(
                seed_type=existing_seed.seed_type,
                original_value=(
                    existing_seed.original_value
                ),
            )
        )

        existing_family = SeedComparisonFamily(
            existing_comparison[
                "comparison_family"
            ]
        )

        existing_target = existing_comparison[
            "comparison_target"
        ]

        existing_fingerprint = (
            generate_seed_target_fingerprint(
                workspace_id=(
                    existing_seed.workspace_id
                ),
                comparison_family=existing_family,
                comparison_target=existing_target,
            )
        )

        classification = classify_seed_match(
            candidate_seed=seed,
            candidate_family=candidate_family,
            candidate_target=candidate_target,
            candidate_fingerprint=(
                candidate_fingerprint
            ),
            existing_seed=existing_seed,
            existing_family=existing_family,
            existing_target=existing_target,
            existing_fingerprint=(
                existing_fingerprint
            ),
        )

        if (
            classification
            == SeedProtectionClassification.NO_CONFLICT
        ):
            continue

        matches.append(
            build_seed_match_record(
                existing_seed=existing_seed,
                comparison_family=existing_family,
                comparison_target=existing_target,
                target_fingerprint=(
                    existing_fingerprint
                ),
                classification=classification,
            )
        )

    matches.sort(
        key=lambda match: (
            0
            if match.get("blocking") is True
            else 1,
            str(
                match.get("classification", "")
            ),
            str(
                match.get("seed_id", "")
            ),
        )
    )

    decision = decide_seed_protection(
        matches
    )

    evaluated_at = utc_now_iso()

    return {
        "ok": True,
        "component": (
            "universal_web_seed_protection"
        ),
        "schema_version": (
            UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION
        ),
        "operation": "inspect",
        "protected": True,
        "persisted": False,
        "seed_id": seed.seed_id,
        "workspace_id": seed.workspace_id,
        "seed_type": seed.seed_type.value,
        "decision": decision["decision"],
        "blocking": decision["blocking"],
        "review_required": (
            decision["review_required"]
        ),
        "comparison_family": (
            candidate_family.value
        ),
        "comparison_target": candidate_target,
        "target_fingerprint": (
            candidate_fingerprint
        ),
        "match_count": len(matches),
        "matches": matches,
        "reason_code": decision["reason_code"],
        "evaluated_at": evaluated_at,
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


def build_seed_protection_metadata(
    result: Mapping[str, Any],
) -> Dict[str, Any]:
    """Build the protection evidence persisted on a seed."""

    if not isinstance(result, Mapping):
        raise ValueError(
            "Seed Protection result must be a mapping."
        )

    required_fields = (
        "schema_version",
        "evaluated_at",
        "decision",
        "blocking",
        "review_required",
        "comparison_family",
        "comparison_target",
        "target_fingerprint",
        "match_count",
        "matches",
        "reason_code",
    )

    for field_name in required_fields:
        if field_name not in result:
            raise ValueError(
                "Seed Protection result is missing "
                f"required field: {field_name}"
            )

    return {
        "schema_version": result[
            "schema_version"
        ],
        "evaluated": True,
        "evaluated_at": result[
            "evaluated_at"
        ],
        "decision": result[
            "decision"
        ],
        "blocking": result[
            "blocking"
        ],
        "review_required": result[
            "review_required"
        ],
        "comparison_family": result[
            "comparison_family"
        ],
        "comparison_target": result[
            "comparison_target"
        ],
        "target_fingerprint": result[
            "target_fingerprint"
        ],
        "match_count": result[
            "match_count"
        ],
        "matches": [
            dict(match)
            for match in result[
                "matches"
            ]
        ],
        "reason_code": result[
            "reason_code"
        ],
    }


def protect_universal_web_seed(
    *,
    workspace_id: str,
    seed_id: str,
) -> Dict[str, Any]:
    """
    Inspect one seed and persist its protection evidence.

    This operation does not delete, merge, archive, enable, disable, or
    otherwise alter seed lifecycle state.
    """

    inspection = inspect_seed_protection(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    seed = require_universal_web_seed(
        workspace_id=workspace_id,
        seed_id=seed_id,
    )

    protection_metadata = (
        build_seed_protection_metadata(
            inspection
        )
    )

    seed.metadata[
        "seed_protection"
    ] = protection_metadata

    seed.metadata[
        "protection_evaluated"
    ] = True

    seed.metadata[
        "protection_decision"
    ] = inspection[
        "decision"
    ]

    seed.metadata[
        "protection_blocking"
    ] = inspection[
        "blocking"
    ]

    seed.updated_at = inspection[
        "evaluated_at"
    ]

    persisted_seed = update_universal_web_seed(
        seed
    )

    result = dict(
        inspection
    )

    result["operation"] = "protect"
    result["persisted"] = True
    result["seed"] = persisted_seed.to_dict()

    return result


def explain_universal_web_seed_protection_v1(
) -> Dict[str, Any]:
    """Return the inspectable Seed Protection contract."""

    return {
        "ok": True,
        "component": (
            "universal_web_seed_protection"
        ),
        "schema_version": (
            UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "comparison_scope": "workspace",
        "canonicalization_scope": (
            "comparison-only"
        ),
        "fingerprint_algorithm": "sha256",
        "comparison_families": [
            family.value
            for family
            in SeedComparisonFamily
        ],
        "classifications": [
            classification.value
            for classification
            in SeedProtectionClassification
        ],
        "decisions": [
            decision.value
            for decision
            in SeedProtectionDecision
        ],
        "public_operations": [
            "build_seed_comparison_target",
            "generate_seed_target_fingerprint",
            "inspect_seed_protection",
            "protect_universal_web_seed",
            "explain_universal_web_seed_protection_v1",
        ],
        "status_policy": {
            "registered": (
                "Equivalent registered seeds may block."
            ),
            "disabled": (
                "Equivalent disabled seeds may block."
            ),
            "archived": (
                "Equivalent archived seeds require review."
            ),
        },
        "responsibilities": [
            "build comparison-only canonical seed targets",
            "generate workspace-scoped target fingerprints",
            "inspect workspace seed targets",
            "exclude candidate self-matches",
            "detect exact duplicate seed targets",
            "detect canonical duplicate seed targets",
            "detect duplicate domain seed targets",
            "detect seed-type conflicts",
            "identify non-blocking related domains",
            "apply disabled and archived seed policies",
            "persist seed protection evidence",
            "return stable Seed Protection decisions",
        ],
        "excluded_responsibilities": [
            "seed registration",
            "seed lifecycle controls",
            "physical seed deletion",
            "automatic seed merging",
            "full crawl-pipeline URL normalization",
            "URL reachability validation",
            "DNS resolution",
            "private-network safety validation",
            "robots.txt evaluation",
            "HTTP fetching",
            "redirect resolution",
            "canonical-tag inspection",
            "sitemap parsing",
            "feed parsing",
            "seed eligibility validation",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page fetching",
        ],
        "next_component": (
            "Universal Web Seed Registry Certification"
        ),
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


__all__ = [
    "BLOCKING_DUPLICATE_CLASSIFICATIONS",
    "COMPARISON_FAMILY_BY_SEED_TYPE",
    "SeedComparisonFamily",
    "SeedProtectionClassification",
    "SeedProtectionDecision",
    "UNIVERSAL_WEB_SEED_PROTECTION_SCHEMA_VERSION",
    "build_seed_comparison_target",
    "build_seed_match_record",
    "build_seed_protection_metadata",
    "classify_seed_match",
    "comparison_family_for_seed_type",
    "decide_seed_protection",
    "explain_universal_web_seed_protection_v1",
    "generate_seed_target_fingerprint",
    "hostname_from_comparison_target",
    "hosts_are_related",
    "inspect_seed_protection",
    "normalize_domain_target",
    "normalize_hostname",
    "normalize_url_path",
    "normalize_url_query",
    "normalize_url_resource_target",
    "protect_universal_web_seed",
]
