from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
    r"\backend\server\data\reports"
    r"\_phase_5_1_4_dependency_resolution_initial_runner.py"
)

source = path.read_text(
    encoding="utf-8-sig"
)

old = '''    return job_contract.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        status=status,
        dependency_job_ids=tuple(
            dependencies
        ),
    )
'''

new = '''    return job_contract.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        status=status,
        dependency_job_ids=tuple(
            dependencies
        ),
        created_at="2026-05-21T03:49:30.579317+00:00",
    )
'''

count = source.count(
    old
)

if count != 1:
    raise SystemExit(
        (
            "Expected exactly one make_job fixture block "
            f"to patch; found {count}."
        )
    )

patched = source.replace(
    old,
    new,
    1,
)

path.write_text(
    patched,
    encoding="utf-8",
)

print(
    "PATCHED: 5.1.4 test fixture now supplies "
    "deterministic created_at."
)

print(
    "PRODUCTION DEPENDENCY RESOLUTION MODIFIED: NO"
)
