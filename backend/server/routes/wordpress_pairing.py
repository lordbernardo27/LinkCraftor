from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/wordpress/pairing",
    tags=["wordpress-pairing"],
)


_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-"
    r"[0-9a-f]{4}-"
    r"4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-"
    r"[0-9a-f]{12}$",
    re.IGNORECASE,
)

_VERSION_RE = re.compile(
    r"^[A-Za-z0-9]"
    r"[A-Za-z0-9._+\-]{0,63}$"
)

_PAIRING_REQUEST_ID_RE = re.compile(
    r"^wppair_[0-9a-f]{32}$"
)


class WordPressPairingRequest(BaseModel):
    installation_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
    )

    site_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
    )

    home_url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
    )

    site_url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
    )

    blog_id: int = Field(
        ...,
        ge=1,
    )

    plugin_version: str = Field(
        ...,
        min_length=1,
        max_length=64,
    )

    wordpress_version: str = Field(
        ...,
        min_length=1,
        max_length=64,
    )

    php_version: str = Field(
        ...,
        min_length=1,
        max_length=64,
    )

    protocol_version: str = Field(
        ...,
        min_length=1,
        max_length=64,
    )

    lifecycle_status: str = Field(
        ...,
        min_length=1,
        max_length=64,
    )


def _require_uuid4(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    if not _UUID4_RE.fullmatch(
        normalized
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_wordpress_identity",
                "field": field_name,
                "message": (
                    f"{field_name} must be a valid UUIDv4."
                ),
            },
        )

    return normalized.lower()


def _require_version(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip()

    if not _VERSION_RE.fullmatch(
        normalized
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_version_value",
                "field": field_name,
                "message": (
                    f"{field_name} contains an "
                    "unsupported version value."
                ),
            },
        )

    return normalized


def _require_protocol_version(
    value: str,
) -> str:
    return _require_version(
        value,
        field_name="protocol_version",
    )


def _require_http_url(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = str(
        value or ""
    ).strip().rstrip("/")

    try:
        parsed = urlsplit(
            normalized
        )
    except Exception:
        parsed = None

    invalid = (
        parsed is None
        or parsed.scheme.lower()
        not in {
            "http",
            "https",
        }
        or not parsed.netloc
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or bool(parsed.query)
        or bool(parsed.fragment)
    )

    if invalid:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_wordpress_site_url",
                "field": field_name,
                "message": (
                    f"{field_name} must be a valid "
                    "HTTP or HTTPS base site URL "
                    "without credentials, query, "
                    "or fragment."
                ),
            },
        )

    return normalized


def _require_blog_id(
    value: int,
) -> int:
    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 1
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_wordpress_blog_id",
                "field": "blog_id",
                "message": (
                    "blog_id must be a positive integer."
                ),
            },
        )

    return value


def _new_pairing_request_id() -> str:
    pairing_request_id = (
        "wppair_"
        + uuid4().hex
    )

    if not _PAIRING_REQUEST_ID_RE.fullmatch(
        pairing_request_id
    ):
        raise RuntimeError(
            "Generated pairing request ID "
            "violated the canonical format."
        )

    return pairing_request_id


def _utc_now_iso() -> str:
    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


@router.post("/request")
def request_wordpress_pairing(
    payload: WordPressPairingRequest,
) -> dict[str, Any]:
    """
    Phase 2.2 WordPress pairing-request boundary.

    This endpoint accepts and validates the initial
    WordPress installation/site pairing request only.

    It does NOT:
    - authenticate a LinkCraftor user
    - authorize a workspace
    - select or bind a workspace
    - resolve canonical domain ownership
    - create permanent site/workspace binding
    - create connection registry state
    - issue credentials or tokens
    - call Connect Domain
    - start Connected Domain pipelines
    - start Upload Document
    - create Universal Runtime processing jobs

    Authentication begins in Phase 2.3.
    """

    installation_id = _require_uuid4(
        payload.installation_id,
        field_name="installation_id",
    )

    site_id = _require_uuid4(
        payload.site_id,
        field_name="site_id",
    )

    plugin_version = _require_version(
        payload.plugin_version,
        field_name="plugin_version",
    )

    wordpress_version = _require_version(
        payload.wordpress_version,
        field_name="wordpress_version",
    )

    php_version = _require_version(
        payload.php_version,
        field_name="php_version",
    )

    protocol_version = _require_protocol_version(
        payload.protocol_version
    )

    home_url = _require_http_url(
        payload.home_url,
        field_name="home_url",
    )

    site_url = _require_http_url(
        payload.site_url,
        field_name="site_url",
    )

    blog_id = _require_blog_id(
        payload.blog_id
    )

    lifecycle_status = str(
        payload.lifecycle_status
        or ""
    ).strip().lower()

    if lifecycle_status not in {
        "active",
        "inactive",
        "unknown",
    }:
        raise HTTPException(
            status_code=400,
            detail={
                "error":
                    "invalid_plugin_lifecycle_status",
                "field":
                    "lifecycle_status",
            },
        )

    pairing_request_id = (
        _new_pairing_request_id()
    )

    return {
        "ok": True,
        "pairing_request_id":
            pairing_request_id,
        "status":
            "pending_authentication",
        "next_step":
            "authentication",
        "source_type":
            "wordpress",
        "created_at":
            _utc_now_iso(),
        "identity": {
            "installation_id":
                installation_id,
            "site_id":
                site_id,
        },
        "site": {
            "home_url":
                home_url,
            "site_url":
                site_url,
            "blog_id":
                blog_id,
        },
        "environment": {
            "plugin_version":
                plugin_version,
            "wordpress_version":
                wordpress_version,
            "php_version":
                php_version,
            "protocol_version":
                protocol_version,
            "lifecycle_status":
                lifecycle_status,
        },
        "security_boundary": {
            "authenticated":
                False,
            "authorized":
                False,
            "workspace_selected":
                False,
            "workspace_bound":
                False,
            "domain_resolved":
                False,
            "connect_domain_started":
                False,
            "credentials_issued":
                False,
        },
    }


__all__ = [
    "router",
    "WordPressPairingRequest",
    "request_wordpress_pairing",
]