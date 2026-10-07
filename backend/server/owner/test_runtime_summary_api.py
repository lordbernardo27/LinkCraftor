import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.server.owner.runtime_summary_api import (
    RUNTIME_SUMMARY_ENDPOINT,
    install_runtime_owner_summary_provider,
    router,
    certify_runtime_summary_api_v1,
)


def build_sample_provider():

    def provider():

        return {

            "health": {
                "runtime_health":
                    "HEALTHY",

                "health_reasons":
                    [],

                "authoritative_health_source":
                    "runtime_observability",
            },

            "architecture": {
                "architecture_name":
                    "Universal Runtime",

                "architecture_registry_version":
                    "test",

                "owner_section_count":
                    14,
            },

            "activity": {
                "active_jobs": 5,
                "queued_jobs": 3,
                "running_executions": 2,
                "active_workers": 4,
                "active_leases": 2,
            },

            "work_state": {
                "active_orchestrations": 2,
                "failed_work": 1,
                "recovering_work": 1,
            },

            "infrastructure": {
                "queue_pressure":
                    "NORMAL",

                "resource_pressure":
                    "NORMAL",

                "persistence_health":
                    "HEALTHY",
            },

            "security_api_alert_attention": {
                "security_health":
                    "ENFORCED",

                "api_health":
                    "HEALTHY",

                "runtime_alerts":
                    {},

                "error_summary":
                    {},

                "owner_attention_required":
                    False,

                "owner_attention_sources":
                    [],
            },
        }

    return provider


def test_component_certification():

    result = certify_runtime_summary_api_v1()

    assert result["certified"] is True

    assert (
        result["endpoint"]
        == RUNTIME_SUMMARY_ENDPOINT
    )

    assert (
        result["mode"]
        == "read_only_owner_runtime_api"
    )


def test_provider_missing_fails_closed():

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        RUNTIME_SUMMARY_ENDPOINT
    )

    assert response.status_code == 503

    payload = response.json()

    assert (
        payload["detail"]["error"]
        ==
        "runtime_owner_summary_provider_unavailable"
    )


def test_live_provider_route():

    app = FastAPI()

    app.include_router(router)

    install_runtime_owner_summary_provider(
        app,
        build_sample_provider(),
    )

    client = TestClient(app)

    response = client.get(
        RUNTIME_SUMMARY_ENDPOINT
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["read_only"] is True

    assert (
        payload["health"][
            "runtime_health"
        ]
        == "HEALTHY"
    )

    assert (
        payload["architecture"][
            "owner_section_count"
        ]
        == 14
    )

    assert (
        payload["activity"][
            "active_jobs"
        ]
        == 5
    )

    assert (
        payload["work_state"][
            "active_orchestrations"
        ]
        == 2
    )

    assert (
        payload["infrastructure"][
            "persistence_health"
        ]
        == "HEALTHY"
    )

    assert (
        payload[
            "security_api_alert_attention"
        ][
            "api_health"
        ]
        == "HEALTHY"
    )


def run():

    test_component_certification()

    test_provider_missing_fails_closed()

    test_live_provider_route()

    print(
        "RUNTIME OWNER PHASE 2.18 SUMMARY API TEST: PASS"
    )


if __name__ == "__main__":
    run()
