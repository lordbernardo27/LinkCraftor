from backend.server.owner.runtime_health_read_model import (
    RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION,
    RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION,
    build_runtime_owner_health_read_model,
    certify_runtime_owner_health_read_model_v1,
)


def run():
    certification = (
        certify_runtime_owner_health_read_model_v1()
    )

    assert certification["certified"] is True
    assert certification["authority"] == "runtime_observability"
    assert certification["mode"] == "read_only_projection"

    model = build_runtime_owner_health_read_model(
        observability_handoff={
            "runtime_health": "HEALTHY",
            "health_reasons": [],
        },
        persistence_handoff={
            "persistence_health": "HEALTHY",
        },
        resource_handoff={
            "pressure_status": "NORMAL",
        },
        runtime_api_handoff={
            "api_health_status": "HEALTHY",
        },
    )

    payload = model.to_dict()

    assert payload["runtime_health"] == "HEALTHY"

    assert (
        payload["authoritative_health_source"]
        == "runtime_observability"
    )

    assert (
        payload["supporting_health"][
            "persistence_health"
        ]
        == "HEALTHY"
    )

    assert (
        payload["supporting_health"][
            "resource_pressure_status"
        ]
        == "NORMAL"
    )

    assert (
        payload["supporting_health"][
            "runtime_api_health"
        ]
        == "HEALTHY"
    )

    assert (
        payload["version"]
        == RUNTIME_OWNER_HEALTH_READ_MODEL_VERSION
    )

    assert (
        payload["schema_version"]
        == RUNTIME_OWNER_HEALTH_READ_MODEL_SCHEMA_VERSION
    )

    print("RUNTIME OWNER HEALTH READ MODEL TEST: PASS")


if __name__ == "__main__":
    run()
