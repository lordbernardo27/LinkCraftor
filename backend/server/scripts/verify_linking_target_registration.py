from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_universal_knowledge_job,
    read_universal_runtime_registration,
)
from backend.server.pipelines.connect_domain.job_types import (
    LINKING_TARGET_PIPELINE_BATCH,
)
from backend.server.pipelines.connect_domain.linking_target_pipeline.runtime_registration import (
    ensure_linking_target_pipeline_registration,
)


def main() -> None:
    registration = ensure_linking_target_pipeline_registration()

    if not isinstance(registration, dict):
        raise RuntimeError(
            "Registration did not return a dictionary."
        )

    stored = read_universal_runtime_registration(
        LINKING_TARGET_PIPELINE_BATCH
    )

    if not isinstance(stored, dict) or not stored:
        raise RuntimeError(
            "Runtime registration was not stored."
        )

    job = create_universal_knowledge_job(
        workspace_id="ws_runtime_registration_verification",
        job_type=LINKING_TARGET_PIPELINE_BATCH,
        pipeline="linking_target_pipeline",
        stage=LINKING_TARGET_PIPELINE_BATCH,
        payload={
            "workspace_id": "ws_runtime_registration_verification",
            "domain": "example.com",
            "verification_only": True,
        },
        enqueue=False,
    )

    if job.get("job_type") != LINKING_TARGET_PIPELINE_BATCH:
        raise RuntimeError(
            "Registered job type was not accepted."
        )

    if job.get("status") != "registered":
        raise RuntimeError(
            "Verification job was unexpectedly queued."
        )

    print(
        "LINKING_TARGET_PIPELINE_RUNTIME_REGISTRATION_VERIFIED"
    )
    print(
        f"JOB_TYPE={LINKING_TARGET_PIPELINE_BATCH}"
    )
    print(
        f"STATUS={job.get('status')}"
    )


if __name__ == "__main__":
    main()
