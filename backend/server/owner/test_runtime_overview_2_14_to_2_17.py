from backend.server.owner.runtime_security_api_alert_attention_read_model import (
    build_runtime_security_api_alert_attention_read_model,
    certify_runtime_security_api_alert_attention_read_model_v1,
)


def run():

    model = (
        build_runtime_security_api_alert_attention_read_model(

            runtime_api_handoff={
                "api_health_status":
                    "HEALTHY",

                "security_integration_status":
                    "ENFORCED",

                "owner_attention_required":
                    False,
            },

            observability_handoff={
                "alert_summary": {
                    "active": 3,
                    "warning": 2,
                    "critical": 1,
                },

                "error_summary": {
                    "critical": 1,
                    "error": 2,
                },

                "owner_attention_required":
                    False,
            },

            resource_handoff={
                "owner_attention_required":
                    False,
            },

            persistence_handoff={
                "owner_attention_required":
                    True,
            },
        )
    )

    payload = model.to_dict()

    assert (
        payload["security_health"]
        == "ENFORCED"
    )

    assert (
        payload["api_health"]
        == "HEALTHY"
    )

    assert (
        payload["runtime_alerts"][
            "active"
        ]
        == 3
    )

    assert (
        payload["error_summary"][
            "critical"
        ]
        == 1
    )

    assert (
        payload[
            "owner_attention_required"
        ]
        is True
    )

    assert (
        payload[
            "owner_attention_sources"
        ]
        == ["persistence"]
    )

    certification = (
        certify_runtime_security_api_alert_attention_read_model_v1()
    )

    assert certification["certified"] is True

    print(
        "RUNTIME OWNER OVERVIEW 2.14-2.17 TEST: PASS"
    )


if __name__ == "__main__":
    run()
