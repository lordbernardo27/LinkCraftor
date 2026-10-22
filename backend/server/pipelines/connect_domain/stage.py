"""Canonical executable boundary for the Connect Domain pipeline stage."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from backend.server.pipelines.connect_domain.coordinator import (
    _normalize_workspace_name,
    _persist_workspace_profile,
)
from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
    _normalize_domain,
    _resolve_workspace_id,
)


CONNECT_DOMAIN_STAGE_SCHEMA_VERSION = "connect_domain_stage_v1"
CONNECT_DOMAIN_WORKSPACE_MODE = "connect_domain"

ProfileWriter = Callable[..., Any]


class ConnectDomainStageError(ValueError):
    """Raised when Connect Domain stage admission or execution fails."""


@dataclass(frozen=True, slots=True)
class ConnectDomainStageResult:
    schema_version: str
    workspace_id: str
    workspace_name: str
    workspace_mode: str
    domain: str
    site_url: str
    profile_persisted: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def execute_connect_domain_stage(
    *,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    workspace_mode: str = CONNECT_DOMAIN_WORKSPACE_MODE,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    profile_writer: ProfileWriter | None = None,
) -> ConnectDomainStageResult:
    """Normalize and persist one connected-domain workspace boundary."""

    normalized_mode = str(
        workspace_mode or CONNECT_DOMAIN_WORKSPACE_MODE
    ).strip().lower()

    if normalized_mode != CONNECT_DOMAIN_WORKSPACE_MODE:
        raise ConnectDomainStageError(
            "workspace_mode must be 'connect_domain'."
        )

    raw_domain = domain or site_url or url

    try:
        normalized_domain = _normalize_domain(
            raw_domain
        )

        resolved_workspace_id = _resolve_workspace_id(
            workspace_id,
            normalized_domain,
        )

        resolved_workspace_name = _normalize_workspace_name(
            workspace_name,
            normalized_domain,
        )
    except Exception as exc:
        raise ConnectDomainStageError(
            f"Connect Domain identity validation failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    canonical_site_url = (
        f"https://{normalized_domain}"
    )

    writer = (
        profile_writer
        if profile_writer is not None
        else _persist_workspace_profile
    )

    if not callable(writer):
        raise ConnectDomainStageError(
            "profile_writer must be callable."
        )

    try:
        writer(
            workspace_id=resolved_workspace_id,
            workspace_name=resolved_workspace_name,
            workspace_mode=CONNECT_DOMAIN_WORKSPACE_MODE,
            domain=normalized_domain,
            site_url=canonical_site_url,
        )
    except Exception as exc:
        raise ConnectDomainStageError(
            f"Workspace profile persistence failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    return ConnectDomainStageResult(
        schema_version=CONNECT_DOMAIN_STAGE_SCHEMA_VERSION,
        workspace_id=resolved_workspace_id,
        workspace_name=resolved_workspace_name,
        workspace_mode=CONNECT_DOMAIN_WORKSPACE_MODE,
        domain=normalized_domain,
        site_url=canonical_site_url,
        profile_persisted=True,
    )


__all__ = [
    "CONNECT_DOMAIN_STAGE_SCHEMA_VERSION",
    "CONNECT_DOMAIN_WORKSPACE_MODE",
    "ConnectDomainStageError",
    "ConnectDomainStageResult",
    "execute_connect_domain_stage",
]
