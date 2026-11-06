from fastapi import HTTPException

from backend.server.routes.wordpress_pairing import (
    _PAIRING_REQUEST_ID_RE,
    _new_pairing_request_id,
    _require_blog_id,
    _require_http_url,
    _require_protocol_version,
    _require_uuid4,
    _require_version,
)


VALID_INSTALLATION_ID = (
    "550e8400-e29b-41d4-a716-446655440000"
)

VALID_SITE_ID = (
    "123e4567-e89b-42d3-a456-426614174000"
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


def expect_http_400(
    name,
    fn,
    expected_error,
    expected_field,
):
    try:
        fn()

    except HTTPException as exc:
        detail = exc.detail

        ok = (
            exc.status_code == 400
            and isinstance(
                detail,
                dict,
            )
            and detail.get(
                "error"
            ) == expected_error
            and detail.get(
                "field"
            ) == expected_field
        )

        if ok:
            pass_check(name)
            return

        fail_check(
            name,
            (
                f"status={exc.status_code}, "
                f"detail={detail!r}"
            ),
        )

    except Exception as exc:
        fail_check(
            name,
            (
                f"unexpected "
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        )

    fail_check(
        name,
        "invalid input was accepted",
    )


print(
    "=== 2.2.2 STRICT IDENTITY VALIDATION ==="
)

normalized = _require_uuid4(
    VALID_INSTALLATION_ID.upper(),
    field_name="installation_id",
)

if normalized == VALID_INSTALLATION_ID:
    pass_check(
        "INSTALLATION_UUID4_VALID"
    )
else:
    fail_check(
        "INSTALLATION_UUID4_VALID"
    )

if (
    _require_uuid4(
        VALID_SITE_ID,
        field_name="site_id",
    )
    == VALID_SITE_ID
):
    pass_check(
        "SITE_UUID4_VALID"
    )
else:
    fail_check(
        "SITE_UUID4_VALID"
    )

expect_http_400(
    "INSTALLATION_EMPTY_REJECTED",
    lambda: _require_uuid4(
        "",
        field_name="installation_id",
    ),
    "invalid_wordpress_identity",
    "installation_id",
)

expect_http_400(
    "INSTALLATION_RANDOM_REJECTED",
    lambda: _require_uuid4(
        "not-a-uuid",
        field_name="installation_id",
    ),
    "invalid_wordpress_identity",
    "installation_id",
)

expect_http_400(
    "INSTALLATION_UUID1_REJECTED",
    lambda: _require_uuid4(
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        field_name="installation_id",
    ),
    "invalid_wordpress_identity",
    "installation_id",
)

expect_http_400(
    "SITE_MALFORMED_REJECTED",
    lambda: _require_uuid4(
        "1234",
        field_name="site_id",
    ),
    "invalid_wordpress_identity",
    "site_id",
)

print(
    "2.2.2_STRICT_IDENTITY_VALIDATION: CERTIFIED"
)


print()
print(
    "=== 2.2.3 PROTOCOL / VERSION VALIDATION ==="
)

valid_versions = {
    "plugin_version":
        "1.0.0",
    "wordpress_version":
        "6.8.1",
    "php_version":
        "8.4.0",
}

for field_name, value in valid_versions.items():
    returned = _require_version(
        value,
        field_name=field_name,
    )

    if returned != value:
        fail_check(
            f"{field_name.upper()}_VALID"
        )

    pass_check(
        f"{field_name.upper()}_VALID"
    )

protocol = _require_protocol_version(
    "1.0"
)

if protocol == "1.0":
    pass_check(
        "PROTOCOL_VERSION_VALID"
    )
else:
    fail_check(
        "PROTOCOL_VERSION_VALID"
    )

expect_http_400(
    "EMPTY_PLUGIN_VERSION_REJECTED",
    lambda: _require_version(
        "",
        field_name="plugin_version",
    ),
    "invalid_version_value",
    "plugin_version",
)

expect_http_400(
    "VERSION_WHITESPACE_REJECTED",
    lambda: _require_version(
        "1.0 bad",
        field_name="wordpress_version",
    ),
    "invalid_version_value",
    "wordpress_version",
)

expect_http_400(
    "VERSION_CONTROL_CHARS_REJECTED",
    lambda: _require_version(
        "8.4\nmalicious",
        field_name="php_version",
    ),
    "invalid_version_value",
    "php_version",
)

expect_http_400(
    "PROTOCOL_EMPTY_REJECTED",
    lambda: _require_protocol_version(
        ""
    ),
    "invalid_version_value",
    "protocol_version",
)

print(
    "2.2.3_PROTOCOL_VERSION_VALIDATION: CERTIFIED"
)


print()
print(
    "=== 2.2.4 URL / SITE METADATA VALIDATION ==="
)

home = _require_http_url(
    "https://Example.com/",
    field_name="home_url",
)

if home == "https://Example.com":
    pass_check(
        "HOME_URL_VALID"
    )
else:
    fail_check(
        "HOME_URL_VALID"
    )

site = _require_http_url(
    "https://example.com/wp/",
    field_name="site_url",
)

if site == "https://example.com/wp":
    pass_check(
        "SITE_URL_PATH_VALID"
    )
else:
    fail_check(
        "SITE_URL_PATH_VALID"
    )

http_url = _require_http_url(
    "http://example.com/",
    field_name="home_url",
)

if http_url == "http://example.com":
    pass_check(
        "HTTP_SCHEME_VALID"
    )
else:
    fail_check(
        "HTTP_SCHEME_VALID"
    )

expect_http_400(
    "FTP_SCHEME_REJECTED",
    lambda: _require_http_url(
        "ftp://example.com",
        field_name="home_url",
    ),
    "invalid_wordpress_site_url",
    "home_url",
)

expect_http_400(
    "URL_CREDENTIALS_REJECTED",
    lambda: _require_http_url(
        "https://user:pass@example.com",
        field_name="site_url",
    ),
    "invalid_wordpress_site_url",
    "site_url",
)

expect_http_400(
    "URL_QUERY_REJECTED",
    lambda: _require_http_url(
        "https://example.com/?x=1",
        field_name="home_url",
    ),
    "invalid_wordpress_site_url",
    "home_url",
)

expect_http_400(
    "URL_FRAGMENT_REJECTED",
    lambda: _require_http_url(
        "https://example.com/#section",
        field_name="site_url",
    ),
    "invalid_wordpress_site_url",
    "site_url",
)

expect_http_400(
    "URL_HOST_MISSING_REJECTED",
    lambda: _require_http_url(
        "https:///missing-host",
        field_name="site_url",
    ),
    "invalid_wordpress_site_url",
    "site_url",
)

if _require_blog_id(1) == 1:
    pass_check(
        "BLOG_ID_ONE_VALID"
    )
else:
    fail_check(
        "BLOG_ID_ONE_VALID"
    )

if _require_blog_id(999) == 999:
    pass_check(
        "BLOG_ID_POSITIVE_VALID"
    )
else:
    fail_check(
        "BLOG_ID_POSITIVE_VALID"
    )

expect_http_400(
    "BLOG_ID_ZERO_REJECTED",
    lambda: _require_blog_id(
        0
    ),
    "invalid_wordpress_blog_id",
    "blog_id",
)

expect_http_400(
    "BLOG_ID_NEGATIVE_REJECTED",
    lambda: _require_blog_id(
        -5
    ),
    "invalid_wordpress_blog_id",
    "blog_id",
)

expect_http_400(
    "BLOG_ID_BOOL_REJECTED",
    lambda: _require_blog_id(
        True
    ),
    "invalid_wordpress_blog_id",
    "blog_id",
)

print(
    "2.2.4_URL_SITE_METADATA_VALIDATION: CERTIFIED"
)


print()
print(
    "=== 2.2.5 PAIRING REQUEST IDENTIFIER ==="
)

generated = [
    _new_pairing_request_id()
    for _ in range(100)
]

if all(
    _PAIRING_REQUEST_ID_RE.fullmatch(
        value
    )
    for value in generated
):
    pass_check(
        "PAIRING_ID_FORMAT_100_OF_100"
    )
else:
    fail_check(
        "PAIRING_ID_FORMAT_100_OF_100"
    )

if len(
    set(
        generated
    )
) == 100:
    pass_check(
        "PAIRING_ID_UNIQUENESS_100_OF_100"
    )
else:
    fail_check(
        "PAIRING_ID_UNIQUENESS_100_OF_100"
    )

if all(
    value.startswith(
        "wppair_"
    )
    for value in generated
):
    pass_check(
        "PAIRING_ID_NAMESPACE_PREFIX"
    )
else:
    fail_check(
        "PAIRING_ID_NAMESPACE_PREFIX"
    )

print(
    "2.2.5_PAIRING_REQUEST_IDENTIFIER: CERTIFIED"
)


print()
print(
    "=== COMBINED RESULT ==="
)

print(
    "2.2.2_TO_2.2.5: CERTIFIED"
)