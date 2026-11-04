from __future__ import annotations

"""Fail-closed, workflow-specific Universal Worker scope validator.

This contract validates canonical job identity. It does not grant
permission to enable a worker or authorize production queue claims.
"""

from backend.server.orchestration.job_store import load_jobs

WORKSPACE_ID = "ws_whattoexpect_com"
WORKFLOW_ID = "workflow_connect_domain_a3ab8627c22ea34444e0aef30128889a"

STAGES = (
    (
        "connect_domain_stage",
        "uj_7e5ae92f76c9e9b54dd7a5f5eea3cf2d",
        "backend.server.pipelines.connect_domain.stage:execute_connect_domain_stage",
        "37be4b5bb33b093a4196a638dc5f39688fb9add34fc32c0861195d03f9e50b15",
    ),
    (
        "site_sources_stage",
        "uj_c1b0d2f3cf847e1b2fd222bb720020bf",
        "backend.server.pipelines.connect_domain.linking_target_pipeline.site_sources.stage:execute_site_sources_stage",
        "fa7375428c09585fca9df596c4951f045cf14f42bbde5f20c16b8f57980fe4b7",
    ),
    (
        "url_cleaner_stage",
        "uj_1858eb6f8fca4738ce429a5183238c00",
        "backend.server.pipelines.connect_domain.linking_target_pipeline.url_cleaner.stage:execute_url_cleaner_stage",
        "f2eab9a9f2010f9dad622c4a63cddfa6e3503114183067a0d60e0930a67a8691",
    ),
    (
        "site_pages_stage",
        "uj_b1e0348f76f7cc1aa857892682f06e21",
        "backend.server.pipelines.connect_domain.linking_target_pipeline.site_pages.stage:build_site_pages",
        "3c8af8a433127c0f48e69cc9f09b347c7c505599b23472b9a64f14d965d54a2f",
    ),
    (
        "live_domain_target_pool_stage",
        "uj_e37a125059dd06476520073b468096c6",
        "backend.server.pipelines.connect_domain.linking_target_pipeline.live_domain_target_pool.stage:build_live_domain_target_pool",
        "3295d72b36cde6a3c6e61c124d8fa5c219a8c9653cd05b182c9fee9659d2fa55",
    ),
    (
        "active_target_set_stage",
        "uj_76898e356c348e8a19874501a7566f05",
        "backend.server.pipelines.connect_domain.linking_target_pipeline.active_target_set.stage:build_active_target_set",
        "e42d6cc5fcf52450f65301d09c6a178444f028737aec6a1f9675eede0e2518ce",
    ),
)

EXPECTED_SCOPE = frozenset(item[1] for item in STAGES)

LEGACY_IDS = frozenset({
    "job_cdb701f231234155",
    "job_84b9c7e8e743442b",
    "job_c8508708b80f4a95",
    "job_f704ea81bc7c45a7",
    "job_c6f37a857ea54264",
})

def validate_trusted_worker_scope(
    requested_scope: frozenset[str],
) -> frozenset[str]:
    if not isinstance(requested_scope, frozenset):
        raise TypeError("Trusted scope must be a frozenset.")

    if requested_scope != EXPECTED_SCOPE:
        raise ValueError(
            "Trusted worker scope does not match the six "
            "canonical Connected Domain job IDs."
        )

    if len(requested_scope) != 6:
        raise ValueError("Exactly six canonical jobs required.")

    if not requested_scope.isdisjoint(LEGACY_IDS):
        raise ValueError("Legacy jobs cannot enter worker scope.")

    jobs = load_jobs()

    for order, item in enumerate(STAGES, 1):
        stage, job_id, handler, fingerprint = item

        job = jobs.get(job_id)
        if job is None:
            raise ValueError("Canonical stage job missing: " + job_id)

        if job.job_id != job_id:
            raise ValueError("Canonical job identity mismatch.")

        if job.workspace_id != WORKSPACE_ID:
            raise ValueError("Canonical workspace mismatch.")

        if job.job_type != stage:
            raise ValueError("Canonical stage type mismatch.")

        metadata = job.metadata
        if not isinstance(metadata, dict):
            raise ValueError("Canonical stage metadata invalid.")

        reference = metadata.get("stage_reference")
        if not isinstance(reference, dict):
            raise ValueError("Canonical stage reference missing.")

        if reference.get("pipeline_stage_order") != order:
            raise ValueError("Canonical stage order mismatch.")

        if reference.get("handler_ref") != handler:
            raise ValueError("Canonical handler reference mismatch.")

        if reference.get("registration_fingerprint") != fingerprint:
            raise ValueError("Stage registration fingerprint mismatch.")

        if reference.get("registration_persistent") is not True:
            raise ValueError("Stage persistence certification missing.")

        coordination = metadata.get("coordination")
        if not isinstance(coordination, dict):
            raise ValueError("Workflow coordination evidence missing.")

        if coordination.get("workflow_id") != WORKFLOW_ID:
            raise ValueError("Canonical workflow identity mismatch.")

        if coordination.get("workflow_type") != "connect_domain":
            raise ValueError("Canonical workflow type mismatch.")

    return EXPECTED_SCOPE
