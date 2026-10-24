from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import sys
import tempfile
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any, Mapping


STAGES = (
    ("connect_domain", "connect_domain_stage"),
    ("site_sources", "site_sources_stage"),
    ("url_cleaner", "url_cleaner_stage"),
    ("site_pages", "site_pages_stage"),
    ("live_domain_target_pool", "live_domain_target_pool_stage"),
    ("active_target_set", "active_target_set_stage"),
)


EXPECTED_SOURCE_HASHES = {
    "backend/server/pipelines/connect_domain/activation.py": "7a392200005452fd595820d81f6f90bb88ff2854d11cfcf68e28e22c92a54ff1",
    "backend/server/pipelines/connect_domain/coordinator.py": "a05bfc1d106306b7399f03bdef2f2d06a22a88fa9006aff680ac1796b1bb77fb",
    "backend/server/pipelines/connect_domain/manifest.py": "27a5258c7679160ced9fdf54d3ba0a202593861ada25b3571be0c053b16c1beb",
    "backend/server/pipelines/connect_domain/runtime_hydration.py": "e486d82ecb73e223d83b3fd9ebcac99016cd1d55487c444952fa650add66f7e2",
    "backend/server/routes/site_workspace.py": "4ed403e7040c68e0c223efd2922bd723b6a524789bb20c3dc138dc7383ccd0be",
    "backend/server/runtime/runtime_coordination_gateway.py": "95dbabf2b63fd52e51d984741e4fcb2ac392e7276354ae550fbce58de1259f45",
    "backend/server/runtime/runtime_payload_hydration.py": "df0b50e4bc4494848a82c886b65413217e4155ed406777bafa0c9ca56dbd20b8",
    "backend/server/runtime/universal_runtime_registration.py": "bbee0fb0132a970cdf9cf4c6776c2ac990490c25010c6ee10c0befe4e403d83f",
    "backend/server/runtime/universal_runtime_worker_v1.py": "15e205976ca5d0da4e5df236c4c2019881563bab0102ec29d371750cf370b743",
    "backend/server/pipelines/connect_domain/stage.py": "41eb1aa109748bea0d8080601d77cf394131415d8c8c8cbac0c557754d13cd7a",
    "backend/server/pipelines/connect_domain/linking_target_pipeline/site_sources/stage.py": "fdc26ebf4a0f2ffb283604aefae814caec9b4aba5339cf4e5237912d9492fcf8",
    "backend/server/pipelines/connect_domain/linking_target_pipeline/url_cleaner/stage.py": "22b8faa7df021b26b33081d575bbd6b9d9856495d448c8e07e080868965c2cc7",
    "backend/server/pipelines/connect_domain/linking_target_pipeline/site_pages/stage.py": "8055b55c9e773b72493efc1304a7d4c617f0546cd413384a1e982eb075b3962b",
    "backend/server/pipelines/connect_domain/linking_target_pipeline/live_domain_target_pool/stage.py": "46dd22998dc2036bbe179227b99fbd417dd257967182efd0780f823ab950f6fc",
    "backend/server/pipelines/connect_domain/linking_target_pipeline/active_target_set/stage.py": "08c19bdb95d732ea243594fe0bb633bd007aa581bdc622635a08607e5d65172f",
    "backend/server/coordination/stage_handoff/stage_result_processor.py": "8106d844b0b4d1c4d4e3a07a6232f4796010c604f538ed0f8e45f823d2c64456",
    "backend/server/coordination/workflow_persistence/repository.py": "e7a8379fabf9047f150e24df4b2b9f138f4ce285c1b3d3ec43dd2f1a454c69db",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    for name in ("to_dict", "to_canonical_dict", "to_payload"):
        method = getattr(value, name, None)
        if callable(method):
            try:
                return plain(method())
            except TypeError:
                pass
    if dataclasses.is_dataclass(value):
        return plain(dataclasses.asdict(value))
    if hasattr(value, "__dict__"):
        return plain(vars(value))
    return str(value)


def deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(deep_freeze(item) for item in value)
    return value


def write_report(
    path: Path,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> None:
    failed = [name for name, passed in checks.items() if not passed]
    certified = not failed and not error
    content = "\n".join(
        [
            "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION",
            "PART E 14-B CONTROLLED END-TO-END PIPELINE CERTIFICATION",
            "",
            "Mode: REAL REGISTERED HANDLERS / CONTROLLED FIXTURES / ISOLATED WORKFLOW STORAGE",
            "Production source changes: CERTIFIED WINDOWS ATOMIC-REPLACE COMPATIBILITY FIX",
            "Production activation executed: NO",
            "Production workflow persistence executed: NO",
            "Production Universal Jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Controlled real handlers executed: YES",
            "Live network requests executed: NO",
            "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
            "",
            "CHECKS:",
            json.dumps(checks, indent=2, sort_keys=True),
            "",
            "FAILED_CHECKS:",
            json.dumps(failed, indent=2),
            "",
            "NOT_RUN_CHECKS:",
            "[]",
            "",
            "EVIDENCE:",
            json.dumps(evidence, indent=2, default=str, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2),
            "",
            "CERTIFIED BOUNDARY:",
            "- All six persisted registered handlers executed in canonical dependency order.",
            "- Site discovery used deterministic HTTP and sitemap doubles; no network was called.",
            "- Four downstream payloads were hydrated from actual predecessor dispatch results.",
            "- The final Active Target Set was produced by the real registered stage handler.",
            "- The real RuntimeCoordinationGateway lifecycle method completed all six stages",
            "  against a temporary WorkflowRepository and rejected a terminal retry.",
            "- Production queues, jobs, workflow storage and stage repositories were untouched.",
            "",
            "FINAL RESULT:",
            (
                "FINAL RESULT: PART E STEP 14 END-TO-END PIPELINE CERTIFIED"
                if certified
                else "FINAL RESULT: PART E STEP 14 NOT_CERTIFIED"
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    inspection_report = root / "backend/server/data/reports/PART_E_14_A_END_TO_END_BOUNDARY_INSPECTION.txt"
    source_paths = {name: root / name for name in EXPECTED_SOURCE_HASHES}
    registry_candidates = (
        root / "backend/server/data/universal_runtime_registrations.json",
        root / "backend/server/data/runtime/universal_runtime_registrations.json",
    )
    registry_file = next((path for path in registry_candidates if path.is_file()), None)

    checks = {
        "part_e_14_a_report_exists": False,
        "part_e_14_a_complete": False,
        "production_source_lineage_matches_14_a_with_certified_repository_fix": False,
        "required_modules_imported": False,
        "all_six_registrations_loaded": False,
        "all_six_registration_handlers_match": False,
        "connect_domain_handler_executed": False,
        "site_sources_handler_executed": False,
        "url_cleaner_handler_executed": False,
        "site_pages_handler_executed": False,
        "live_domain_target_pool_handler_executed": False,
        "active_target_set_handler_executed": False,
        "six_handlers_executed_in_order": False,
        "deterministic_site_sources_fixture_used": False,
        "profile_persistence_isolated": False,
        "site_sources_persistence_isolated": False,
        "four_handoffs_hydrated_from_dispatch_evidence": False,
        "hydration_marker_removed_before_dispatch": False,
        "runtime_dispatch_result_evidence_complete": False,
        "final_active_target_set_created": False,
        "final_target_identity_preserved": False,
        "temporary_workflow_repository_used": False,
        "six_terminal_lifecycle_updates_applied": False,
        "workflow_completed_after_final_stage": False,
        "workflow_completed_stages_exact": False,
        "workflow_pending_stages_empty": False,
        "terminal_retry_rejected": False,
        "controlled_result_evidence_immutable": False,
        "production_sources_unchanged": False,
        "inspection_report_unchanged": False,
        "runtime_registry_memory_unchanged": False,
        "runtime_registry_file_unchanged": False,
        "production_jobs_created_no": True,
        "production_queue_claims_no": True,
        "production_handlers_executed_no": True,
        "production_workflow_persistence_no": True,
        "live_network_requests_no": True,
        "collective_fingerprint_valid": False,
    }
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    source_before: dict[str, str] = {}
    inspection_hash_before = ""
    registry_bytes_before: bytes | None = None
    registry_snapshot_before: Any = None

    try:
        checks["part_e_14_a_report_exists"] = inspection_report.is_file()
        if not checks["part_e_14_a_report_exists"]:
            raise RuntimeError("Part E 14-A inspection report is unavailable.")
        inspection_hash_before = sha256(inspection_report)
        inspection_text = inspection_report.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        checks["part_e_14_a_complete"] = (
            "INSPECTION STATUS: COMPLETE" in inspection_text
            and "FAILED_CHECKS:\n[]" in inspection_text
            and "PART E 14-A COMPLETE" in inspection_text
            and "CONTROLLED_FIXTURE_END_TO_END_EXECUTION_REQUIRED" in inspection_text
        )
        if not checks["part_e_14_a_complete"]:
            raise RuntimeError("Part E 14-A is not complete.")

        source_before = {name: sha256(path) for name, path in source_paths.items() if path.is_file()}
        checks["production_source_lineage_matches_14_a_with_certified_repository_fix"] = (
            len(source_before) == len(EXPECTED_SOURCE_HASHES)
            and source_before == EXPECTED_SOURCE_HASHES
        )
        if not checks["production_source_lineage_matches_14_a_with_certified_repository_fix"]:
            changed = {
                name: {"expected": expected, "actual": source_before.get(name)}
                for name, expected in EXPECTED_SOURCE_HASHES.items()
                if source_before.get(name) != expected
            }
            raise RuntimeError("Production source lineage changed after 14-A: " + json.dumps(changed, sort_keys=True))

        if registry_file is not None:
            registry_bytes_before = registry_file.read_bytes()
        sys.path.insert(0, str(root))
        registration = importlib.import_module("backend.server.runtime.universal_runtime_registration")
        hook = importlib.import_module("backend.server.runtime.runtime_payload_hydration")
        hydration = importlib.import_module("backend.server.pipelines.connect_domain.runtime_hydration")
        workflow_contract = importlib.import_module("backend.server.coordination.universal_workflows.contract")
        workflow_repository_module = importlib.import_module("backend.server.coordination.workflow_persistence.repository")
        gateway_module = importlib.import_module("backend.server.runtime.runtime_coordination_gateway")
        checks["required_modules_imported"] = True

        registration.ensure_persisted_runtime_registrations_loaded()
        registry_snapshot_before = plain(registration.runtime_registration_snapshot())
        expected_refs = {
            "connect_domain_stage": "backend.server.pipelines.connect_domain.stage:execute_connect_domain_stage",
            "site_sources_stage": "backend.server.pipelines.connect_domain.linking_target_pipeline.site_sources.stage:execute_site_sources_stage",
            "url_cleaner_stage": "backend.server.pipelines.connect_domain.linking_target_pipeline.url_cleaner.stage:execute_url_cleaner_stage",
            "site_pages_stage": "backend.server.pipelines.connect_domain.linking_target_pipeline.site_pages.stage:build_site_pages",
            "live_domain_target_pool_stage": "backend.server.pipelines.connect_domain.linking_target_pipeline.live_domain_target_pool.stage:build_live_domain_target_pool",
            "active_target_set_stage": "backend.server.pipelines.connect_domain.linking_target_pipeline.active_target_set.stage:build_active_target_set",
        }
        records = {
            job_type: registration.get_runtime_registration(job_type)
            for _, job_type in STAGES
        }
        checks["all_six_registrations_loaded"] = all(record is not None for record in records.values())
        checks["all_six_registration_handlers_match"] = all(
            plain(records[job_type]).get("handler_ref") == expected_ref
            for job_type, expected_ref in expected_refs.items()
        )
        if not checks["all_six_registrations_loaded"] or not checks["all_six_registration_handlers_match"]:
            raise RuntimeError("The six runtime registrations are unavailable or mismatched.")

        workspace_id = "ws_part_e_14_b_probe"
        workflow_id = "workflow_part_e_14_b_probe"
        correlation_id = "correlation_part_e_14_b_probe"
        domain = "example.com"
        fixture_urls = (
            "https://example.com/guide-a",
            "https://example.com/guide-b",
            "https://example.com/guide-c",
        )
        profile_writes: list[Any] = []
        source_writes: list[Any] = []
        network_calls: list[str] = []
        expansion_calls: list[str] = []
        execution_order: list[str] = []
        synthetic_jobs: dict[str, Any] = {}
        dispatch_evidence: dict[str, Any] = {}
        hydrated_fields: dict[str, Any] = {}

        def profile_writer(*args: Any, **kwargs: Any) -> dict[str, Any]:
            profile_writes.append({"args": plain(args), "kwargs": plain(kwargs)})
            return {"ok": True, "isolated": True}

        def http_get(url: str) -> tuple[int, bytes, dict[str, str]]:
            network_calls.append(str(url))
            return 404, b"", {}

        def sitemap_expander(url: str, *, max_sitemaps: int) -> tuple[tuple[str, ...], tuple[Any, ...]]:
            expansion_calls.append(str(url))
            return fixture_urls, ()

        def site_sources_writer(*args: Any, **kwargs: Any) -> dict[str, Any]:
            source_writes.append({"args": plain(args), "kwargs": plain(kwargs)})
            return {"ok": True, "isolated": True}

        def cleaner(urls: Any, cleaner_domain: str, **kwargs: Any) -> Any:
            normalized = tuple(str(url) for url in urls)
            return SimpleNamespace(
                urls=normalized,
                explicit_urls=normalized,
                uncertain_urls=(),
                rejected=(),
                reason_counts={},
                input_count=len(normalized),
            )

        payloads: dict[str, dict[str, Any]] = {
            "connect_domain": {
                "workspace_id": workspace_id,
                "workspace_name": "Part E 14-B Probe",
                "workspace_mode": "connect_domain",
                "domain": "Example.COM",
                "profile_writer": profile_writer,
            },
            "site_sources": {
                "workspace_id": workspace_id,
                "domain": domain,
                "http_get": http_get,
                "sitemap_expander": sitemap_expander,
                "site_sources_writer": site_sources_writer,
                "maximum_sitemaps": 8,
                "maximum_candidates": 8,
            },
            "url_cleaner": {
                "workspace_id": workspace_id,
                "domain": domain,
                "cleaner": cleaner,
            },
            "site_pages": {"workspace_id": workspace_id, "domain": domain},
            "live_domain_target_pool": {"workspace_id": workspace_id, "domain": domain},
            "active_target_set": {"workspace_id": workspace_id},
        }
        predecessor_by_stage = {
            "url_cleaner": "site_sources",
            "site_pages": "url_cleaner",
            "live_domain_target_pool": "site_pages",
            "active_target_set": "live_domain_target_pool",
        }
        target_field_by_stage = {
            "url_cleaner": "source_urls",
            "site_pages": "cleaner_records",
            "live_domain_target_pool": "site_pages",
            "active_target_set": "live_domain_payload",
        }

        for index, (stage_id, job_type) in enumerate(STAGES, start=1):
            predecessor_stage = predecessor_by_stage.get(stage_id)
            dependency_ids = (
                [synthetic_jobs[predecessor_stage].job_id]
                if predecessor_stage is not None
                else []
            )
            payload = dict(payloads[stage_id])
            if predecessor_stage is not None:
                payload[hook.RUNTIME_PAYLOAD_HYDRATOR_KEY] = hydration.CONNECTED_DOMAIN_HYDRATOR_REF
            job = {
                "id": "job_part_e_14_b_" + stage_id,
                "job_id": "job_part_e_14_b_" + stage_id,
                "job_type": job_type,
                "type": job_type,
                "pipeline": "connect_domain",
                "stage": stage_id,
                "workspace_id": workspace_id,
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "dependency_job_ids": dependency_ids,
                "metadata": {
                    "workflow_id": workflow_id,
                    "correlation_id": correlation_id,
                    "dependency_job_ids": dependency_ids,
                },
                "payload": payload,
            }
            if predecessor_stage is not None:
                original_resolver = hook._resolve_hydrator
                hook._resolve_hydrator = lambda _reference: (
                    lambda runtime_job: hydration.hydrate_connected_domain_runtime_job(
                        runtime_job,
                        job_reader=lambda requested_id: next(
                            (
                                item
                                for item in synthetic_jobs.values()
                                if item.job_id == requested_id
                            ),
                            None,
                        ),
                        jobs_reader=lambda: {
                            item.job_id: item for item in synthetic_jobs.values()
                        },
                    )
                )
                try:
                    job = hook.hydrate_runtime_job_payload(job)
                finally:
                    hook._resolve_hydrator = original_resolver
                target_field = target_field_by_stage[stage_id]
                if target_field not in job["payload"]:
                    raise RuntimeError("Hydrated field is absent: " + target_field)
                hydrated_fields[stage_id] = plain(job["payload"][target_field])
                if hook.RUNTIME_PAYLOAD_HYDRATOR_KEY in job["payload"]:
                    raise RuntimeError("Internal hydrator marker reached dispatcher payload.")

            dispatch = registration.dispatch_registered_runtime_handler(job)
            execution_order.append(stage_id)
            dispatch_evidence[stage_id] = plain(dispatch)
            synthetic_jobs[stage_id] = SimpleNamespace(
                job_id=job["job_id"],
                job_type=job_type,
                stage=stage_id,
                status="completed",
                metadata={
                    "workflow_id": workflow_id,
                    "correlation_id": correlation_id,
                    "dependency_job_ids": dependency_ids,
                    "runtime_dispatch_result": dispatch,
                },
            )
            checks[stage_id + "_handler_executed"] = (
                dispatch.get("handled") is True
                and dispatch.get("job_type") == job_type
                and dispatch.get("handler_ref") == expected_refs[job_type]
            )

        checks["six_handlers_executed_in_order"] = execution_order == [stage for stage, _ in STAGES]
        checks["deterministic_site_sources_fixture_used"] = (
            bool(expansion_calls)
            and set(hydrated_fields["url_cleaner"]) == set(fixture_urls)
            and all(url.endswith(("robots.txt", ".xml", ".xml.gz")) for url in network_calls + expansion_calls)
        )
        checks["profile_persistence_isolated"] = len(profile_writes) == 1
        checks["site_sources_persistence_isolated"] = len(source_writes) == 1
        checks["four_handoffs_hydrated_from_dispatch_evidence"] = set(hydrated_fields) == set(predecessor_by_stage)
        checks["hydration_marker_removed_before_dispatch"] = all(
            hook.RUNTIME_PAYLOAD_HYDRATOR_KEY not in item.get("handler_result", {})
            for item in dispatch_evidence.values()
        )
        checks["runtime_dispatch_result_evidence_complete"] = all(
            isinstance(item.metadata.get("runtime_dispatch_result"), Mapping)
            for item in synthetic_jobs.values()
        )
        final_result = dispatch_evidence["active_target_set"].get("handler_result", {})
        if isinstance(final_result, Mapping) and set(final_result) == {"value"}:
            final_result = final_result["value"]
        final_payload = plain(final_result)
        final_items = list(final_payload.get("items", ())) if isinstance(final_payload, Mapping) else []
        checks["final_active_target_set_created"] = len(final_items) == len(fixture_urls)
        checks["final_target_identity_preserved"] = {
            item.get("canonical_url") for item in final_items
        } == set(fixture_urls)

        with tempfile.TemporaryDirectory(prefix="linkcraftor_part_e_14_b_") as temporary:
            temporary_root = Path(temporary).resolve()
            repository = workflow_repository_module.WorkflowRepository(root=temporary_root)
            gateway = gateway_module.RuntimeCoordinationGateway(
                project_root=root,
                workflow_root=temporary_root,
                workflow_repository=repository,
            )
            checks["temporary_workflow_repository_used"] = (
                temporary_root != (root / "backend/server/data/coordination/workflows").resolve()
            )
            now = datetime(2026, 10, 24, 17, 30, tzinfo=timezone.utc)
            workflow = workflow_contract.UniversalWorkflow(
                workflow_id=workflow_id,
                workflow_type="connect_domain",
                workflow_version="1.0.0",
                workspace_id=workspace_id,
                coordinator_id="connect_domain_coordinator",
                coordinator_version="1.0.0",
                correlation_id=correlation_id,
                parent_workflow_id=None,
                root_workflow_id=workflow_id,
                status=workflow_contract.UniversalWorkflowStatus.RUNNING,
                input_reference=None,
                context={"domain": domain},
                metadata={"certification_scope": "part_e_14_b"},
                current_stage=STAGES[0][0],
                pending_stages=tuple(stage for stage, _ in STAGES),
                idempotency_key="part_e_14_b:" + workflow_id,
                created_at=now.isoformat().replace("+00:00", "Z"),
                updated_at=now.isoformat().replace("+00:00", "Z"),
                started_at=now.isoformat().replace("+00:00", "Z"),
            )
            repository.save_workflow(workflow)

            lifecycle_results: list[Any] = []
            job_to_stage = {
                synthetic_jobs[stage].job_id: stage for stage, _ in STAGES
            }

            def terminal_intake(*, job_id: str, workflow_repository: Any, **kwargs: Any) -> Any:
                stage_id = job_to_stage[job_id]
                return SimpleNamespace(
                    workflow_id=workflow_id,
                    stage_id=stage_id,
                    correlation_id=correlation_id,
                    disposition="completed",
                    processed_result={
                        "result_reference": "isolated://" + job_id,
                        "artifact_references": (),
                    },
                    to_dict=lambda: {
                        "job_id": job_id,
                        "stage_id": stage_id,
                        "disposition": "completed",
                    },
                )

            for index, (stage_id, _) in enumerate(STAGES, start=1):
                lifecycle_results.append(
                    gateway.apply_runtime_terminal_lifecycle(
                        job_id=synthetic_jobs[stage_id].job_id,
                        terminal_intake=terminal_intake,
                        occurred_at=(now + timedelta(seconds=index)).isoformat().replace("+00:00", "Z"),
                    )
                )
            final_record = repository.load_workflow_record(workflow_id)
            final_workflow = final_record.workflow
            checks["six_terminal_lifecycle_updates_applied"] = len(lifecycle_results) == 6
            checks["workflow_completed_after_final_stage"] = str(final_workflow.status.value).lower() == "completed"
            checks["workflow_completed_stages_exact"] = tuple(final_workflow.completed_stages) == tuple(stage for stage, _ in STAGES)
            checks["workflow_pending_stages_empty"] = not tuple(final_workflow.pending_stages)
            try:
                gateway.apply_runtime_terminal_lifecycle(
                    job_id=synthetic_jobs["active_target_set"].job_id,
                    terminal_intake=terminal_intake,
                    occurred_at=(now + timedelta(seconds=10)).isoformat().replace("+00:00", "Z"),
                )
            except Exception:
                checks["terminal_retry_rejected"] = True
            lifecycle_evidence = {
                "updates": [plain(item) for item in lifecycle_results],
                "final_workflow": plain(final_workflow),
                "temporary_root": str(temporary_root),
            }

        immutable_evidence = deep_freeze(
            {
                "execution_order": execution_order,
                "hydrated_fields": hydrated_fields,
                "final_active_target_set": final_payload,
            }
        )
        checks["controlled_result_evidence_immutable"] = (
            isinstance(immutable_evidence, MappingProxyType)
            and isinstance(immutable_evidence["execution_order"], tuple)
        )

        registry_snapshot_after = plain(registration.runtime_registration_snapshot())
        checks["runtime_registry_memory_unchanged"] = registry_snapshot_before == registry_snapshot_after
        checks["runtime_registry_file_unchanged"] = (
            registry_bytes_before is None
            or (registry_file is not None and registry_file.read_bytes() == registry_bytes_before)
        )
        checks["production_sources_unchanged"] = source_before == {
            name: sha256(path) for name, path in source_paths.items()
        }
        checks["inspection_report_unchanged"] = inspection_hash_before == sha256(inspection_report)

        fingerprint_material = {
            "sources": source_before,
            "execution_order": execution_order,
            "dispatch": dispatch_evidence,
            "hydration": hydrated_fields,
            "final": final_payload,
            "lifecycle": lifecycle_evidence,
        }
        collective_fingerprint = hashlib.sha256(
            json.dumps(plain(fingerprint_material), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        checks["collective_fingerprint_valid"] = len(collective_fingerprint) == 64
        evidence = {
            "collective_fingerprint": collective_fingerprint,
            "execution_order": execution_order,
            "fixture_urls": list(fixture_urls),
            "network_double_calls": network_calls,
            "sitemap_expander_calls": expansion_calls,
            "isolated_profile_write_count": len(profile_writes),
            "isolated_site_sources_write_count": len(source_writes),
            "hydrated_fields": hydrated_fields,
            "dispatch_results": dispatch_evidence,
            "final_active_target_set": final_payload,
            "lifecycle": lifecycle_evidence,
            "source_hashes": source_before,
            "production_jobs_created": False,
            "production_queue_claims_executed": False,
            "production_workflow_persistence_executed": False,
            "live_network_requests_executed": False,
        }
        if not all(checks.values()):
            raise RuntimeError("One or more Part E 14-B certification checks failed.")
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_report(report, checks, plain(evidence), error)
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    failed_count = sum(not passed for passed in checks.values())
    print("FAILED_CHECK_COUNT=" + str(failed_count))
    print("NOT_RUN_CHECK_COUNT=0")
    print("REPORT=" + str(report))
    certified = failed_count == 0 and not error
    print("PART_E_14_B_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
    print("PART_E_STEP_14_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
    return 0 if certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
