from backend.server.routes.wordpress_pairing_guard import (
    enforce_pairing_no_authorization,
)


def pass_check(name):
    print(f"{name}: PASS")


def expect_failure(
    name,
    response,
):
    try:
        enforce_pairing_no_authorization(
            response
        )
    except RuntimeError:
        pass_check(name)
        return

    raise SystemExit(
        f"{name}: FAIL"
    )


print(
    "=== 2.2.10 NO-AUTHORIZATION GUARD ==="
)


base = {
    "ok": True,
    "pairing_request_id":
        "wppair_"
        + ("a" * 32),
    "status":
        "pending_authentication",
    "next_step":
        "authentication",
    "source_type":
        "wordpress",
    "security_boundary": {
        "authenticated": False,
        "authorized": False,
        "workspace_selected": False,
        "workspace_bound": False,
        "domain_resolved": False,
        "connect_domain_started": False,
        "credentials_issued": False,
    },
}


result = enforce_pairing_no_authorization(
    dict(base)
)

if result["status"] == "pending_authentication":
    pass_check(
        "VALID_PENDING_RESPONSE_ACCEPTED"
    )
else:
    raise SystemExit(
        "VALID_PENDING_RESPONSE_ACCEPTED: FAIL"
    )


for field in (
    "workspace_id",
    "connection_id",
    "domain_id",
    "access_token",
    "refresh_token",
    "authorization_grant",
    "connect_domain_result",
    "runtime_job_id",
):
    bad = {
        **base,
        field: "forbidden",
    }

    expect_failure(
        "FORBIDDEN_"
        + field.upper()
        + "_REJECTED",
        bad,
    )


for flag in (
    "authenticated",
    "authorized",
    "workspace_selected",
    "workspace_bound",
    "domain_resolved",
    "connect_domain_started",
    "credentials_issued",
):
    bad = {
        **base,
        "security_boundary": {
            **base[
                "security_boundary"
            ],
            flag: True,
        },
    }

    expect_failure(
        "PREMATURE_"
        + flag.upper()
        + "_REJECTED",
        bad,
    )


bad_status = {
    **base,
    "status": "connected",
}

expect_failure(
    "CONNECTED_STATE_REJECTED",
    bad_status,
)


bad_next = {
    **base,
    "next_step": "authorization",
}

expect_failure(
    "AUTHORIZATION_NEXT_STEP_REJECTED",
    bad_next,
)


print()
print(
    "2.2.10_NO_AUTHORIZATION_GUARD: CERTIFIED"
)