from fastapi import HTTPException

from backend.server.routes.wordpress_pairing import (
    WordPressPairingRequest,
    request_wordpress_pairing,
    _require_http_url,
    _require_uuid4,
    _require_version,
)


def pass_check(name):
    print(f"{name}: PASS")


def fail_check(name, detail=""):
    print(
        f"{name}: FAIL"
        + (
            f" -> {detail}"
            if detail
            else ""
        )
    )
    raise SystemExit(1)


print(
    "=== 2.2.6 PENDING PAIRING RESPONSE CONTRACT ==="
)

payload = WordPressPairingRequest(
    installation_id=(
        "550e8400-e29b-41d4-a716-446655440000"
    ),
    site_id=(
        "123e4567-e89b-42d3-a456-426614174000"
    ),
    home_url="https://example.com",
    site_url="https://example.com",
    blog_id=1,
    plugin_version="1.0.0",
    wordpress_version="6.8.1",
    php_version="8.4.0",
    protocol_version="1.0",
    lifecycle_status="active",
)

response = request_wordpress_pairing(
    payload
)

required = {
    "ok": True,
    "status": "pending_authentication",
    "next_step": "authentication",
    "source_type": "wordpress",
}

for key, expected in required.items():
    if response.get(key) == expected:
        pass_check(
            f"RESPONSE_{key.upper()}"
        )
    else:
        fail_check(
            f"RESPONSE_{key.upper()}",
            repr(response.get(key)),
        )

pairing_id = response.get(
    "pairing_request_id"
)

if (
    isinstance(pairing_id, str)
    and pairing_id.startswith(
        "wppair_"
    )
    and len(pairing_id) == 39
):
    pass_check(
        "RESPONSE_PAIRING_REQUEST_ID"
    )
else:
    fail_check(
        "RESPONSE_PAIRING_REQUEST_ID",
        repr(pairing_id),
    )

security = response.get(
    "security_boundary"
)

if not isinstance(
    security,
    dict,
):
    fail_check(
        "RESPONSE_SECURITY_BOUNDARY"
    )

pass_check(
    "RESPONSE_SECURITY_BOUNDARY"
)

for key in (
    "authenticated",
    "authorized",
    "workspace_selected",
    "workspace_bound",
    "domain_resolved",
    "connect_domain_started",
    "credentials_issued",
):
    if security.get(key) is False:
        pass_check(
            f"BOUNDARY_{key.upper()}_FALSE"
        )
    else:
        fail_check(
            f"BOUNDARY_{key.upper()}_FALSE"
        )

for forbidden in (
    "workspace_id",
    "access_token",
    "refresh_token",
    "connection_id",
    "domain_id",
):
    if forbidden not in response:
        pass_check(
            f"FORBIDDEN_{forbidden.upper()}_ABSENT"
        )
    else:
        fail_check(
            f"FORBIDDEN_{forbidden.upper()}_ABSENT"
        )

print(
    "2.2.6_PENDING_PAIRING_RESPONSE_CONTRACT: CERTIFIED"
)


print()
print(
    "=== 2.2.9 BACKEND ERROR / FAILURE CONTRACT ==="
)


def expect_400(
    name,
    fn,
    expected_error,
):
    try:
        fn()

    except HTTPException as exc:
        detail = exc.detail

        if (
            exc.status_code == 400
            and isinstance(
                detail,
                dict,
            )
            and detail.get(
                "error"
            ) == expected_error
        ):
            pass_check(name)
            return

        fail_check(
            name,
            repr(detail),
        )

    fail_check(
        name,
        "request was not rejected",
    )


expect_400(
    "BAD_IDENTITY_CONTROLLED_400",
    lambda: _require_uuid4(
        "bad-id",
        field_name="site_id",
    ),
    "invalid_wordpress_identity",
)

expect_400(
    "BAD_URL_CONTROLLED_400",
    lambda: _require_http_url(
        "ftp://example.com",
        field_name="site_url",
    ),
    "invalid_wordpress_site_url",
)

expect_400(
    "BAD_VERSION_CONTROLLED_400",
    lambda: _require_version(
        "1.0 bad",
        field_name="plugin_version",
    ),
    "invalid_version_value",
)

print(
    "2.2.9_BACKEND_ERROR_FAILURE_CONTRACT: CERTIFIED"
)