from pathlib import Path

p = Path("backend/server/workers/universal_knowledge_worker.py")
code = p.read_text(encoding="utf-8")

old = '''        if job_type == "upload_document_batch":
            result = {
                "handled": True,
                "job_type": job_type,
                "next_jobs": ["build_uduc", "build_uucd", "build_body_store", "certify_uucd_body_store"],
                "document_count": len(payload.get("documents") or []),
            }

        elif job_type == "website_crawl_batch":
            result = {
                "handled": True,
                "job_type": job_type,
                "next_jobs": ["build_uucd", "build_body_store", "certify_uucd_body_store"],
                "url_count": len(payload.get("urls") or []),
            }

        elif job_type in {
            "build_uduc",
            "build_uucd",
            "source_lifecycle",
            "build_body_store",
            "verify_body_store",
            "certify_uucd_body_store",
        }:
            result = {
                "handled": True,
                "job_type": job_type,
                "workspace_id": workspace_id,
                "note": "Canonical stage accepted by worker contract.",
            }

        else:
            raise ValueError(f"Unsupported worker job_type: {job_type}")
'''

new = '''        stage_groups = {
            "upload_arm": {
                "upload_document_batch",
                "upload_file_route_validation",
                "format_detection",
                "format_router",
                "upload_document_extraction",
                "build_uduc",
                "build_uucd_from_uduc",
            },
            "website_arm": {
                "website_connection_batch",
                "website_crawl_batch",
                "site_page_discovery",
                "raw_html_acquisition",
                "html_cleaning",
                "article_extraction",
                "content_normalization",
                "build_website_unified_content",
                "build_uucd_from_website",
            },
            "canonical": {
                "build_uucd",
                "source_authorization",
                "source_lifecycle",
                "source_asset_versioning",
                "build_body_store",
                "verify_body_store",
                "certify_uucd_body_store",
            },
            "semantic": {
                "semantic_article_reader",
                "semantic_context_builder",
                "entity_concept_extraction",
                "phrase_neighborhood_intelligence",
                "topic_intent_intelligence",
                "section_evidence_builder",
                "semantic_relationship_graph",
                "semantic_learning_export",
                "semantic_end_to_end_certification",
            },
        }

        group = ""
        for group_name, job_types in stage_groups.items():
            if job_type in job_types:
                group = group_name
                break

        if not group:
            raise ValueError(f"Unsupported worker job_type: {job_type}")

        if group == "semantic" and payload.get("semantic_ready") is not True:
            raise ValueError("Semantic job blocked because semantic_ready is not true.")

        result = {
            "handled": True,
            "job_type": job_type,
            "stage_group": group,
            "workspace_id": workspace_id,
            "stage_index": payload.get("stage_index"),
            "stage_count": payload.get("stage_count"),
            "note": "Stage accepted by full pipeline worker contract.",
        }

        if job_type == "upload_document_batch":
            result["document_count"] = len(payload.get("documents") or [])

        if job_type in {"website_connection_batch", "website_crawl_batch"}:
            result["url_count"] = len(payload.get("urls") or [])
'''

if old not in code:
    raise SystemExit("Old worker job-type block not found.")

code = code.replace(old, new)

p.write_text(code, encoding="utf-8")
print("Expanded Universal Knowledge Worker stage handling.")
