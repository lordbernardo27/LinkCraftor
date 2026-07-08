from __future__ import annotations

from backend.server.jobs.universal_knowledge_orchestrator import (
    create_pipeline_batch_jobs_v1,
    create_semantic_pipeline_jobs_if_certified_v1,
    explain_universal_knowledge_orchestrator_v1,
    get_pipeline_job_chain_v1,
    read_job_progress,
    read_job_status,
)
from backend.server.workers.universal_knowledge_worker import (
    execute_universal_knowledge_job_v1,
)


def fail(msg: str):
    raise AssertionError(msg)


def execute_all(jobs):
    results = []
    for job in jobs:
        job_payload = job.get("payload") or {}

        if job.get("job_type", "").startswith("semantic_"):
            job_payload["semantic_ready"] = True
            job["payload"] = job_payload

        result = execute_universal_knowledge_job_v1(job)
        if not result.get("ok"):
            fail(f"Job failed: {job.get('job_type')} -> {result}")
        results.append(result)
    return results


def verify_chain(workspace_id: str, chain_name: str, expected_min: int):
    chain = get_pipeline_job_chain_v1(chain_name)
    if len(chain) < expected_min:
        fail(f"{chain_name} chain too short: {len(chain)}")

    jobs = create_pipeline_batch_jobs_v1(
        workspace_id=workspace_id,
        chain_name=chain_name,
        payload={"verification": True},
    )

    if len(jobs) != len(chain):
        fail(f"{chain_name} job count mismatch")

    execute_all(jobs)

    for job in jobs:
        status = read_job_status(workspace_id, job["job_id"])
        progress = read_job_progress(workspace_id, job["job_id"])

        if status.get("status") != "completed":
            fail(f"{chain_name} job did not complete: {job['job_type']}")

        if progress.get("percent") != 100:
            fail(f"{chain_name} progress not complete: {job['job_type']}")

    return jobs


def main():
    workspace_id = "ws_phase_45a_full_pipeline"

    upload_jobs = verify_chain(
        workspace_id=workspace_id,
        chain_name="upload_document_batch",
        expected_min=10,
    )

    website_jobs = verify_chain(
        workspace_id=workspace_id,
        chain_name="website_connection_batch",
        expected_min=10,
    )

    blocked = create_semantic_pipeline_jobs_if_certified_v1(
        workspace_id=workspace_id,
        certification={"semantic_ready": False},
        payload={"verification": True},
    )

    if blocked.get("ok") is not False:
        fail("Semantic jobs should be blocked when semantic_ready=false")

    semantic = create_semantic_pipeline_jobs_if_certified_v1(
        workspace_id=workspace_id,
        certification={"semantic_ready": True},
        payload={"verification": True, "semantic_ready": True},
    )

    if semantic.get("ok") is not True:
        fail("Semantic jobs should be created when semantic_ready=true")

    execute_all(semantic["jobs"])

    explanation = explain_universal_knowledge_orchestrator_v1()

    required_job_types = [
        "upload_file_route_validation",
        "format_detection",
        "format_router",
        "upload_document_extraction",
        "build_uduc",
        "build_uucd_from_uduc",
        "site_page_discovery",
        "raw_html_acquisition",
        "html_cleaning",
        "article_extraction",
        "content_normalization",
        "build_website_unified_content",
        "build_uucd_from_website",
        "source_authorization",
        "source_lifecycle",
        "source_asset_versioning",
        "build_body_store",
        "verify_body_store",
        "certify_uucd_body_store",
        "semantic_article_reader",
        "semantic_context_builder",
        "entity_concept_extraction",
        "phrase_neighborhood_intelligence",
        "topic_intent_intelligence",
        "section_evidence_builder",
        "semantic_relationship_graph",
        "semantic_learning_export",
        "semantic_end_to_end_certification",
    ]

    supported = set(explanation.get("supported_job_types") or [])

    missing = [j for j in required_job_types if j not in supported]
    if missing:
        fail(f"Missing supported job types: {missing}")

    print("PHASE 4.5A FULL PIPELINE JOB MAP PASSED")
    print("Workspace:", workspace_id)
    print("Upload chain jobs:", len(upload_jobs))
    print("Website chain jobs:", len(website_jobs))
    print("Semantic chain jobs:", semantic.get("job_count"))
    print("Semantic blocked when not certified:", blocked.get("ok") is False)
    print("Supported job types:", len(supported))
    print("Next stage:", explanation.get("next_stage"))


if __name__ == "__main__":
    main()
