from backend.server.owner.runtime_work_state_read_model import (
    build_runtime_work_state_read_model,
    certify_runtime_work_state_read_model_v1,
)

from backend.server.owner.runtime_infrastructure_health_read_model import (
    build_runtime_infrastructure_health_read_model,
    certify_runtime_infrastructure_health_read_model_v1,
)


def run():

    work = build_runtime_work_state_read_model(

        orchestrations=(
            {"status": "RUNNING"},
            {"status": "COMPLETE"},
            {"active": True},
        ),

        jobs=(
            {"status": "FAILED"},
            {"status": "RETRYING"},
        ),

        executions=(
            {"status": "CRASHED"},
            {"status": "RECOVERING"},
        ),
    ).to_dict()

    assert work["active_orchestrations"] == 2
    assert work["failed_work"] == 2
    assert work["recovering_work"] == 2


    infrastructure = (
        build_runtime_infrastructure_health_read_model(

            resource_handoff={
                "runtime_capacity_status": "ELEVATED",
                "worker_capacity_status": "AVAILABLE",
                "queue_capacity_status": "AVAILABLE",
                "pressure_status": "ELEVATED",
                "owner_attention_required": True,
            },

            persistence_handoff={
                "persistence_health": "HEALTHY",
                "owner_attention_required": False,
            },
        ).to_dict()
    )

    assert infrastructure["queue_pressure"] == "ELEVATED"
    assert infrastructure["resource_pressure"] == "ELEVATED"
    assert infrastructure["persistence_health"] == "HEALTHY"


    assert (
        certify_runtime_work_state_read_model_v1()[
            "certified"
        ]
        is True
    )

    assert (
        certify_runtime_infrastructure_health_read_model_v1()[
            "certified"
        ]
        is True
    )

    print(
        "RUNTIME OWNER OVERVIEW 2.8-2.13 TEST: PASS"
    )


if __name__ == "__main__":
    run()
