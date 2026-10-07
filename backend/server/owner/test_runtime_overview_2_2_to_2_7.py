from pathlib import Path

from backend.server.owner.runtime_architecture_version_read_model import (
    build_runtime_architecture_version_read_model,
    certify_runtime_architecture_version_read_model_v1,
)

from backend.server.owner.runtime_activity_read_model import (
    build_runtime_activity_read_model,
    certify_runtime_activity_read_model_v1,
)


def test_architecture_version():
    runtime_root = Path(
        "backend/server/runtime"
    )

    model = (
        build_runtime_architecture_version_read_model(
            runtime_root=runtime_root
        )
    )

    payload = model.to_dict()

    assert (
        payload["architecture_name"]
        == "Universal Runtime"
    )

    assert (
        payload["owner_section_count"]
        == 14
    )

    assert (
        payload["subsystem_version_count"]
        > 0
    )

    certification = (
        certify_runtime_architecture_version_read_model_v1(
            runtime_root=runtime_root
        )
    )

    assert certification["certified"] is True


def test_activity_model():
    model = build_runtime_activity_read_model(
        jobs=(
            {"status": "RUNNING"},
            {"status": "PENDING"},
            {"status": "COMPLETE"},
            {"active": True},
            {"queued": True},
        ),

        executions=(
            {"status": "RUNNING"},
            {"status": "COMPLETE"},
            {"running": True},
        ),

        workers=(
            {"status": "ACTIVE"},
            {"status": "IDLE"},
            {"status": "LOST"},
            {"active": True},
        ),

        leases=(
            {"status": "ACTIVE"},
            {"active": True},
            {"status": "ACTIVE", "expired": True},
            {"status": "RELEASED"},
        ),
    )

    payload = model.to_dict()

    assert payload["active_jobs"] == 2
    assert payload["queued_jobs"] == 2

    assert (
        payload["running_executions"]
        == 2
    )

    assert payload["active_workers"] == 3
    assert payload["active_leases"] == 2

    certification = (
        certify_runtime_activity_read_model_v1()
    )

    assert certification["certified"] is True


def run():
    test_architecture_version()
    test_activity_model()

    print(
        "RUNTIME OWNER OVERVIEW 2.2-2.7 TEST: PASS"
    )


if __name__ == "__main__":
    run()
