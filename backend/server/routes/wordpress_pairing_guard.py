from __future__ import annotations

from typing import Any


FORBIDDEN_PAIRING_RESPONSE_FIELDS = frozenset(
    {
        "workspace_id",
        "workspace",
        "workspace_binding",
        "connection_id",
        "domain_id",
        "canonical_domain_id",
        "access_token",
        "refresh_token",
        "credential",
        "credentials",
        "authorization",
        "authorization_grant",
        "connect_domain_result",
        "runtime_job_id",
    }
)


REQUIRED_FALSE_SECURITY_FLAGS = frozenset(
    {
        "authenticated",
        "authorized",
        "workspace_selected",
        "workspace_bound",
        "domain_resolved",
        "connect_domain_started",
        "credentials_issued",
    }
)


def enforce_pairing_no_authorization(
    response: dict[str, Any],
) -> dict[str, Any]:
    """
    Enforce the Phase 2.2 fail-closed boundary.

    Pairing Request may establish only a pending authentication
    state. It must not carry authorization, workspace binding,
    domain resolution, credentials, Connect Domain results, or
    runtime execution state.
    """

    if not isinstance(response, dict):
        raise RuntimeError(
            "Pairing response must be a dictionary."
        )

    if response.get("ok") is not True:
        raise RuntimeError(
            "Only a successful pairing response may pass "
            "the no-authorization guard."
        )

    if (
        response.get("status")
        != "pending_authentication"
    ):
        raise RuntimeError(
            "Pairing response attempted to leave "
            "pending_authentication."
        )

    if (
        response.get("next_step")
        != "authentication"
    ):
        raise RuntimeError(
            "Pairing response next step must be authentication."
        )

    present_forbidden = sorted(
        key
        for key in FORBIDDEN_PAIRING_RESPONSE_FIELDS
        if key in response
    )

    if present_forbidden:
        raise RuntimeError(
            "Forbidden pairing response fields detected: "
            + ", ".join(
                present_forbidden
            )
        )

    security = response.get(
        "security_boundary"
    )

    if not isinstance(
        security,
        dict,
    ):
        raise RuntimeError(
            "Pairing response security boundary is missing."
        )

    violated_flags = sorted(
        key
        for key in REQUIRED_FALSE_SECURITY_FLAGS
        if security.get(key) is not False
    )

    if violated_flags:
        raise RuntimeError(
            "Pairing response attempted premature security "
            "state transition: "
            + ", ".join(
                violated_flags
            )
        )

    return response


__all__ = [
    "FORBIDDEN_PAIRING_RESPONSE_FIELDS",
    "REQUIRED_FALSE_SECURITY_FLAGS",
    "enforce_pairing_no_authorization",
]