"""
LinkCraftor Autonomous Public-Web Crawler
Universal Web Seed Registration Engine

This module accepts one seed-registration request, constructs a
canonical UniversalWebSeed record, and persists it through the
certified Universal Web Seed Repository.

Responsibilities:
- validate seed-registration request fields;
- generate unique seed identities;
- normalize supported seed types;
- normalize registration metadata;
- construct canonical UniversalWebSeed records;
- persist seeds through the certified repository;
- preserve registration provenance;
- return stable registration results.

This module does not:
- validate seed crawl eligibility;
- normalize URL or domain targets;
- resolve DNS or public-network safety;
- inspect robots.txt;
- parse sitemaps or feeds;
- detect duplicate seed targets;
- insert records into the Crawl Frontier;
- schedule crawler jobs;
- execute crawler workers;
- fetch web pages.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping
from uuid import uuid4

from .seed_models import (
    UniversalWebSeed,
    UniversalWebSeedType,
    normalize_metadata,
    normalize_seed_type,
    optional_string,
)
from .seed_repository import (
    create_universal_web_seed,
)
from .session_models import (
    non_negative_integer,
    required_string,
)


UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION = (
    "universal_web_seed_registration.v1"
)


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


def generate_universal_web_seed_id() -> str:
    """
    Generate a globally unique Universal Web Seed identity.

    The timestamp supports operational inspection while UUID entropy
    prevents collisions across workers, environments, and processes.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    random_suffix = uuid4().hex[:12]

    return (
        "web_seed_"
        f"{timestamp}_"
        f"{random_suffix}"
    )


def normalize_optional_seed_id(
    seed_id: Any,
) -> str | None:
    """Normalize an optional caller-supplied seed identity."""

    if seed_id is None:
        return None

    return required_string(
        seed_id,
        field_name="seed_id",
    )


def normalize_optional_crawler_session_id(
    crawler_session_id: Any,
) -> str | None:
    """Normalize an optional crawler-session association."""

    return optional_string(
        crawler_session_id
    )


def normalize_registration_metadata(
    metadata: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """Normalize and copy registration metadata."""

    normalized = normalize_metadata(
        metadata
    )

    normalized.setdefault(
        "registration_engine",
        "universal_web_seed_registration",
    )

    normalized.setdefault(
        "eligibility_evaluated",
        False,
    )

    normalized.setdefault(
        "frontier_inserted",
        False,
    )

    normalized.setdefault(
        "target_normalized",
        False,
    )

    return normalized


def build_universal_web_seed_registration_record(
    *,
    workspace_id: str,
    seed_type: UniversalWebSeedType | str,
    original_value: str,
    crawler_session_id: str | None = None,
    priority: int = 0,
    registered_by: str = "crawler_seed_registration",
    registered_source: str = (
        "autonomous_public_web_crawler"
    ),
    metadata: Mapping[str, Any] | None = None,
    seed_id: str | None = None,
) -> UniversalWebSeed:
    """
    Build one canonical UniversalWebSeed registration record.

    This function does not persist the record. Persistence is owned by
    register_universal_web_seed().
    """

    clean_workspace_id = required_string(
        workspace_id,
        field_name="workspace_id",
    )

    clean_original_value = required_string(
        original_value,
        field_name="original_value",
    )

    clean_registered_by = required_string(
        registered_by,
        field_name="registered_by",
    )

    clean_registered_source = required_string(
        registered_source,
        field_name="registered_source",
    )

    normalized_seed_type = normalize_seed_type(
        seed_type
    )

    normalized_priority = non_negative_integer(
        priority,
        field_name="priority",
    )

    normalized_session_id = (
        normalize_optional_crawler_session_id(
            crawler_session_id
        )
    )

    normalized_metadata = (
        normalize_registration_metadata(
            metadata
        )
    )

    resolved_seed_id = (
        normalize_optional_seed_id(
            seed_id
        )
        or generate_universal_web_seed_id()
    )

    now = utc_now_iso()

    normalized_metadata.setdefault(
        "registration_requested_at",
        now,
    )

    normalized_metadata.setdefault(
        "seed_type",
        normalized_seed_type.value,
    )

    return UniversalWebSeed(
        seed_id=resolved_seed_id,
        workspace_id=clean_workspace_id,
        crawler_session_id=normalized_session_id,
        seed_type=normalized_seed_type,
        original_value=clean_original_value,
        priority=normalized_priority,
        registered_by=clean_registered_by,
        registered_source=clean_registered_source,
        registered_at=now,
        created_at=now,
        updated_at=now,
        metadata=normalized_metadata,
    )


def build_universal_web_seed_registration_result(
    *,
    seed: UniversalWebSeed,
    created: bool,
) -> Dict[str, Any]:
    """Build the stable registration result contract."""

    if not isinstance(
        seed,
        UniversalWebSeed,
    ):
        raise ValueError(
            "seed must be a UniversalWebSeed instance."
        )

    if not isinstance(created, bool):
        raise ValueError(
            "created must be a boolean."
        )

    return {
        "ok": True,
        "component": (
            "universal_web_seed_registration_engine"
        ),
        "schema_version": (
            UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION
        ),
        "status": (
            "registered"
            if created
            else "replaced"
        ),
        "created": created,
        "seed_id": seed.seed_id,
        "workspace_id": seed.workspace_id,
        "crawler_session_id": (
            seed.crawler_session_id
        ),
        "seed_type": seed.seed_type.value,
        "original_value": seed.original_value,
        "priority": seed.priority,
        "registered_by": seed.registered_by,
        "registered_source": (
            seed.registered_source
        ),
        "registered_at": seed.registered_at,
        "seed": seed.to_dict(),
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


def register_universal_web_seed(
    *,
    workspace_id: str,
    seed_type: UniversalWebSeedType | str,
    original_value: str,
    crawler_session_id: str | None = None,
    priority: int = 0,
    registered_by: str = "crawler_seed_registration",
    registered_source: str = (
        "autonomous_public_web_crawler"
    ),
    metadata: Mapping[str, Any] | None = None,
    seed_id: str | None = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Register and persist one Universal Web Seed.

    Duplicate seed identities are rejected by default. Passing
    overwrite=True replaces the existing record with the same seed_id.

    Duplicate target detection is intentionally excluded and belongs
    to the later Seed Protection component.
    """

    if not isinstance(overwrite, bool):
        raise ValueError(
            "overwrite must be a boolean."
        )

    seed = (
        build_universal_web_seed_registration_record(
            workspace_id=workspace_id,
            seed_type=seed_type,
            original_value=original_value,
            crawler_session_id=crawler_session_id,
            priority=priority,
            registered_by=registered_by,
            registered_source=registered_source,
            metadata=metadata,
            seed_id=seed_id,
        )
    )

    persisted_seed = create_universal_web_seed(
        seed,
        overwrite=overwrite,
    )

    return build_universal_web_seed_registration_result(
        seed=persisted_seed,
        created=not overwrite,
    )


def explain_universal_web_seed_registration_engine_v1(
) -> Dict[str, Any]:
    """Return the inspectable Seed Registration Engine contract."""

    return {
        "ok": True,
        "component": (
            "universal_web_seed_registration_engine"
        ),
        "schema_version": (
            UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION
        ),
        "pipeline_stage": (
            "Universal Web Seed Registry"
        ),
        "operation_scope": (
            "single seed registration"
        ),
        "identity_prefix": "web_seed_",
        "supported_seed_types": [
            seed_type.value
            for seed_type
            in UniversalWebSeedType
        ],
        "success_statuses": [
            "registered",
            "replaced",
        ],
        "responsibilities": [
            "validate seed registration request fields",
            "generate unique Universal Web Seed identities",
            "normalize supported seed types",
            "normalize registration metadata",
            "construct canonical Universal Web Seed records",
            "persist seeds through the certified repository",
            "preserve registration provenance",
            "return stable registration results",
        ],
        "excluded_responsibilities": [
            "batch seed registration",
            "seed lifecycle controls",
            "duplicate seed-target detection",
            "seed eligibility validation",
            "URL normalization",
            "domain normalization",
            "DNS resolution",
            "public-network safety validation",
            "robots.txt processing",
            "sitemap parsing",
            "feed parsing",
            "Crawl Frontier insertion",
            "crawl scheduling",
            "worker execution",
            "web page fetching",
        ],
        "duplicate_boundary": (
            "This engine protects seed identity through "
            "the repository. Duplicate target detection "
            "belongs to Seed Protection."
        ),
        "next_component": (
            "Seed Controls"
        ),
        "next_pipeline_stage": (
            "Seed Eligibility Validation"
        ),
    }


__all__ = [
    "UNIVERSAL_WEB_SEED_REGISTRATION_SCHEMA_VERSION",
    "build_universal_web_seed_registration_record",
    "build_universal_web_seed_registration_result",
    "explain_universal_web_seed_registration_engine_v1",
    "generate_universal_web_seed_id",
    "normalize_optional_crawler_session_id",
    "normalize_optional_seed_id",
    "normalize_registration_metadata",
    "register_universal_web_seed",
]
