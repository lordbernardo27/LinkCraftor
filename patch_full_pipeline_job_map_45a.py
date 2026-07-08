from pathlib import Path

p = Path("backend/server/jobs/universal_knowledge_orchestrator.py")
code = p.read_text(encoding="utf-8")

old = '''SUPPORTED_JOB_TYPES = {
    "upload_document_batch",
    "website_crawl_batch",
    "build_uduc",
    "build_uucd",
    "source_lifecycle",
    "build_body_store",
    "verify_body_store",
    "certify_uucd_body_store",
}
'''

new = '''SUPPORTED_JOB_TYPES = {
    # Upload arm
    "upload_document_batch",
    "upload_file_route_validation",
    "format_detection",
    "format_router",
    "upload_document_extraction",
    "build_uduc",
    "build_uucd_from_uduc",

    # Website arm
    "website_connection_batch",
    "website_crawl_batch",
    "site_page_discovery",
    "raw_html_acquisition",
    "html_cleaning",
    "article_extraction",
    "content_normalization",
    "build_website_unified_content",
    "build_uucd_from_website",

    # Universal canonical layer
    "build_uucd",
    "source_authorization",
    "source_lifecycle",
    "source_asset_versioning",
    "build_body_store",
    "verify_body_store",
    "certify_uucd_body_store",

    # Semantic pipeline 4.6.1–4.6.9
    "semantic_article_reader",
    "semantic_context_builder",
    "entity_concept_extraction",
    "phrase_neighborhood_intelligence",
    "topic_intent_intelligence",
    "section_evidence_builder",
    "semantic_relationship_graph",
    "semantic_learning_export",
    "semantic_end_to_end_certification",
}
'''

if old not in code:
    raise SystemExit("SUPPORTED_JOB_TYPES block not found.")

code = code.replace(old, new)

extra = r'''

PIPELINE_JOB_CHAIN = {
    "upload_document_batch": [
        "upload_file_route_validation",
        "format_detection",
        "format_router",
        "upload_document_extraction",
        "build_uduc",
        "build_uucd_from_uduc",
        "source_authorization",
        "source_lifecycle",
        "source_asset_versioning",
        "build_body_store",
        "verify_body_store",
        "certify_uucd_body_store",
    ],
    "website_connection_batch": [
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
    ],
    "semantic_pipeline": [
        "semantic_article_reader",
        "semantic_context_builder",
        "entity_concept_extraction",
        "phrase_neighborhood_intelligence",
        "topic_intent_intelligence",
        "section_evidence_builder",
        "semantic_relationship_graph",
        "semantic_learning_export",
        "semantic_end_to_end_certification",
    ],
}


def get_pipeline_job_chain_v1(chain_name: str) -> List[str]:
    return list(PIPELINE_JOB_CHAIN.get(chain_name, []))


def create_pipeline_batch_jobs_v1(
    *,
    workspace_id: str,
    chain_name: str,
    payload: Dict[str, Any] | None = None,
    parent_job_id: str = "",
    batch_id: str = "",
) -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    chain = get_pipeline_job_chain_v1(chain_name)

    if not chain:
        raise ValueError(f"Unknown pipeline chain: {chain_name}")

    for idx, job_type in enumerate(chain, start=1):
        stage_payload = {
            **(payload or {}),
            "chain_name": chain_name,
            "stage_index": idx,
            "stage_count": len(chain),
            "requires_previous_stage": idx > 1,
        }

        job = create_universal_knowledge_job(
            workspace_id=workspace_id,
            job_type=job_type,
            payload=stage_payload,
            parent_job_id=parent_job_id,
            batch_id=batch_id or f"{safe_id(workspace_id)}_{chain_name}",
        )

        jobs.append(job)

    return jobs


def create_semantic_pipeline_jobs_if_certified_v1(
    *,
    workspace_id: str,
    certification: Dict[str, Any],
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if certification.get("semantic_ready") is not True:
        return {
            "ok": False,
            "semantic_ready": False,
            "jobs": [],
            "reason": "Certification is not semantic_ready=true.",
        }

    jobs = create_pipeline_batch_jobs_v1(
        workspace_id=workspace_id,
        chain_name="semantic_pipeline",
        payload=payload or {},
        batch_id=f"{safe_id(workspace_id)}_semantic_pipeline",
    )

    return {
        "ok": True,
        "semantic_ready": True,
        "jobs": jobs,
        "job_count": len(jobs),
    }
'''

if "PIPELINE_JOB_CHAIN" not in code:
    code = code.replace(
        "\ndef explain_universal_knowledge_orchestrator_v1() -> Dict[str, Any]:",
        extra + "\n\ndef explain_universal_knowledge_orchestrator_v1() -> Dict[str, Any]:"
    )

old_explain = '''        "next_stage": "Worker execution + Job Status API",
    }
'''

new_explain = '''        "pipeline_chains": {
            "upload_document_batch": get_pipeline_job_chain_v1("upload_document_batch"),
            "website_connection_batch": get_pipeline_job_chain_v1("website_connection_batch"),
            "semantic_pipeline": get_pipeline_job_chain_v1("semantic_pipeline"),
        },
        "semantic_gate": "Semantic jobs are created only when certification.semantic_ready is true.",
        "next_stage": "Job Status API + real stage adapters",
    }
'''

code = code.replace(old_explain, new_explain)

p.write_text(code, encoding="utf-8")
print("Expanded Universal Knowledge Orchestrator job map.")
