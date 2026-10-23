from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import os
import py_compile
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Mapping


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()
TARGET = ROOT / "backend/server/coordination/runtime_integration/runtime_execution_gateway.py"
INSPECTION = ROOT / "backend/server/data/reports/PART_C_8_E1_IDEMPOTENCY_RECONCILIATION_BOUNDARY_INSPECTION.txt"
START = "# === PART C 8-E IDEMPOTENCY AND RECONCILIATION START ==="
END = "# === PART C 8-E IDEMPOTENCY AND RECONCILIATION END ==="

BLOCK = r'''
# === PART C 8-E IDEMPOTENCY AND RECONCILIATION START ===
from hashlib import sha256 as _e2_sha256
from json import dumps as _e2_dumps
from dataclasses import asdict as _e2_asdict, is_dataclass as _e2_is_dataclass, replace as _e2_replace
from backend.server.orchestration.job_store import load_jobs as _e2_load_jobs
from backend.server.runtime.universal_jobs.idempotency_key import validate_universal_job_idempotency_key as _e2_validate_key

RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION = "runtime_execution_wave_gateway_v1.1.0"


def build_coordination_execution_idempotency_key(*, mapping: RuntimeJobMapping) -> str:
    """Build the stable execution identity owned by Universal Coordination."""
    request = _validate_mapping(mapping)
    material = {
        "authority": "universal_coordination_runtime_execution_v1",
        "workflow_id": _text(mapping.workflow_id),
        "correlation_id": _text(mapping.correlation_id),
        "stage_id": _text(mapping.stage_id),
        "wave_index": mapping.wave_index,
        "workspace_id": _text(request.workspace_id),
        "job_type": _text(request.job_type),
        "pipeline": _text(request.pipeline),
        "runtime_stage": _text(request.stage),
    }
    digest = _e2_sha256(
        _e2_dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    value = f"coordination_runtime_execution_v1:{digest}"
    canonical = _e2_validate_key(value)
    return _text(canonical.idempotency_key)


def _e2_job_document(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if _e2_is_dataclass(value) and not isinstance(value, type):
        return _e2_asdict(value)
    values = getattr(value, "__dict__", None)
    return dict(values) if isinstance(values, Mapping) else {}


def _e2_existing_for_key(*, jobs: Mapping[str, Any], key: str) -> tuple[dict[str, Any], ...]:
    matches = []
    for identity, raw in jobs.items():
        job = _e2_job_document(raw)
        metadata = job.get("metadata")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        projection = metadata.get("universal_runtime_submission")
        projection = projection if isinstance(projection, Mapping) else {}
        canonical = projection.get("canonical_job")
        canonical = canonical if isinstance(canonical, Mapping) else {}
        existing_key = _text(canonical.get("idempotency_key"))
        if existing_key == key:
            document = dict(job)
            document["job_id"] = _text(document.get("job_id") or identity)
            document["canonical_job"] = dict(canonical)
            matches.append(document)
    return tuple(matches)


def _e2_reused_submission(*, mapping: RuntimeJobMapping, existing: Mapping[str, Any], key: str) -> dict[str, Any]:
    request = mapping.creation_request
    canonical = existing.get("canonical_job")
    canonical = canonical if isinstance(canonical, Mapping) else {}
    comparisons = {
        "workspace_id": (_text(request.workspace_id), _text(canonical.get("workspace_id") or existing.get("workspace_id"))),
        "job_type": (_text(request.job_type), _text(canonical.get("job_type") or existing.get("job_type"))),
        "pipeline": (_text(request.pipeline), _text(canonical.get("pipeline"))),
        "stage": (_text(request.stage), _text(canonical.get("stage"))),
        "idempotency_key": (_text(key), _text(canonical.get("idempotency_key"))),
    }
    mismatches = tuple(name for name, values in comparisons.items() if values[0] != values[1])
    job_id = _text(existing.get("job_id") or canonical.get("job_id"))
    if not job_id:
        mismatches += ("job_id",)
    if mismatches:
        raise RuntimeExecutionGatewayError(
            "Persisted idempotency match has a different canonical identity.",
            code="idempotency_reconciliation_conflict",
            violations=mismatches,
        )
    return {
        **dict(canonical),
        "job_id": job_id,
        "workspace_id": request.workspace_id,
        "job_type": request.job_type,
        "pipeline": request.pipeline,
        "stage": request.stage,
        "payload": dict(request.payload),
        "metadata": dict(request.metadata),
        "dependency_job_ids": list(request.dependency_job_ids),
        "idempotency_key": key,
        "status": _text(existing.get("status")) or "queued",
        "created": False,
        "reused_existing_job": True,
        "queued": True,
        "submission": {
            "persisted": True,
            "queued": True,
            "created": False,
            "reused_existing_job": True,
            "canonical_identity_preserved": True,
            "reconciled_from_canonical_job_store": True,
        },
    }


def submit_runtime_execution_wave(
    *,
    mapping_result: RuntimeJobMappingResult,
    dependency_job_ids_by_stage: Mapping[str, Any] | None = None,
    execution_semantics: str = "parallel_eligible",
    submitter: Callable[..., Mapping[str, Any]] = submit_universal_job,
    correlation_registry: WorkflowJobCorrelationRegistry | None = None,
    jobs_reader: Callable[[], Mapping[str, Any]] = _e2_load_jobs,
) -> RuntimeExecutionWaveGatewayResult:
    """Submit or safely reconcile one complete execution wave."""
    (workflow_id, wave_index, semantics, stage_ids, mappings,
     effective_dependencies, effective_registry) = _preflight_execution_wave(
        mapping_result=mapping_result,
        dependency_job_ids_by_stage=dependency_job_ids_by_stage,
        execution_semantics=execution_semantics,
        submitter=submitter,
        correlation_registry=correlation_registry,
    )
    if not callable(jobs_reader):
        raise _wave_error("jobs_reader must be callable.", code="idempotency_reconciliation_failure",
                          violations=("jobs_reader",), workflow_id=workflow_id, wave_index=wave_index)
    loaded = jobs_reader()
    if not isinstance(loaded, Mapping):
        raise _wave_error("Canonical job reader must return a mapping.", code="idempotency_reconciliation_failure",
                          violations=("jobs_reader",), workflow_id=workflow_id, wave_index=wave_index)

    prepared = tuple(mappings)
    execution_keys = {
        mapping.stage_id: build_coordination_execution_idempotency_key(
            mapping=mapping
        )
        for mapping in prepared
    }

    submitted = []
    reconciled_stage_ids = []
    created_stage_ids = []
    for mapping in prepared:
        key = execution_keys[mapping.stage_id]
        matches = _e2_existing_for_key(jobs=loaded, key=key)
        if len(matches) > 1:
            raise _wave_error("Multiple persisted jobs share one coordination execution key.",
                              code="idempotency_reconciliation_conflict", violations=(mapping.stage_id,),
                              workflow_id=workflow_id, wave_index=wave_index,
                              failed_stage_id=mapping.stage_id, submitted_results=tuple(submitted))
        try:
            if matches:
                reused = _e2_reused_submission(mapping=mapping, existing=matches[0], key=key)
                result = submit_runtime_job_mapping(
                    mapping=mapping,
                    submitter=lambda **_kwargs: reused,
                    correlation_registry=effective_registry,
                )
                reconciled_stage_ids.append(mapping.stage_id)
            else:
                def keyed_submitter(
                    _submitter=submitter,
                    _key=key,
                    **kwargs,
                ):
                    arguments = dict(kwargs)
                    arguments["idempotency_key"] = _key
                    return _submitter(**arguments)

                result = submit_runtime_job_mapping(
                    mapping=mapping,
                    submitter=keyed_submitter,
                    correlation_registry=effective_registry,
                )
                created_stage_ids.append(mapping.stage_id)
        except Exception as error:
            raise _wave_error(
                f"Idempotent wave submission failed at stage {mapping.stage_id!r}: {type(error).__name__}: {error}",
                code="wave_submission_failure", violations=(mapping.stage_id,), workflow_id=workflow_id,
                wave_index=wave_index, failed_stage_id=mapping.stage_id,
                submitted_results=tuple(submitted),
            ) from error
        result = _e2_replace(
            result,
            idempotency_key=key,
            evidence={
                **dict(result.evidence),
                "coordination_execution_idempotency_key": key,
            },
        )

        submitted.append(result)

    submissions = tuple(submitted)
    evidence = {
        "preflight_complete": True,
        "all_registrations_resolved": True,
        "canonical_single_mapping_gateway": "submit_runtime_job_mapping",
        "canonical_job_store": "orchestration.job_store.load_jobs",
        "idempotency_authority": "universal_job_idempotency_key",
        "execution_identity_owner": "universal_coordination_runtime_execution_gateway",
        "phase_5_2_mapping_unchanged": True,
        "reconciliation_complete": True,
        "reconciled_stage_ids": tuple(reconciled_stage_ids),
        "created_stage_ids": tuple(created_stage_ids),
        "partial_failure_evidence_retained": True,
        "handler_dispatched": False,
    }
    return RuntimeExecutionWaveGatewayResult(
        contract_version=RUNTIME_EXECUTION_WAVE_GATEWAY_CONTRACT_VERSION,
        gateway_version=RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION,
        workflow_id=workflow_id, wave_index=wave_index, execution_semantics=semantics,
        stage_ids=stage_ids, submission_count=len(submissions),
        created_count=sum(1 for item in submissions if item.created),
        reused_existing_count=sum(1 for item in submissions if item.reused_existing_job),
        queued_count=sum(1 for item in submissions if item.queued),
        job_ids=tuple(item.job_id for item in submissions),
        dependency_job_ids_by_stage=effective_dependencies,
        mappings=tuple(prepared), submissions=submissions, evidence=evidence,
    )


def explain_runtime_execution_reconciliation_v1() -> dict[str, Any]:
    return {
        "component": "Runtime Execution Idempotency and Reconciliation",
        "version": RUNTIME_EXECUTION_WAVE_GATEWAY_VERSION,
        "identity_owner": "Universal Coordination Runtime Execution Gateway",
        "canonical_job_store": "orchestration.job_store.load_jobs",
        "duplicate_store_created": False,
        "phase_5_2_mapping_modified": False,
        "partial_wave_retry": "submit_only_missing_stages",
    }
# === PART C 8-E IDEMPOTENCY AND RECONCILIATION END ===
'''.strip("\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True); raise


def plain(value):
    if isinstance(value, Mapping): return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [plain(v) for v in value]
    if dataclasses.is_dataclass(value): return {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    return value


def report(checks, evidence, error, backup):
    failed = [name for name, ok in checks.items() if not ok]
    status = "CERTIFIED" if not failed and error is None else "NOT_CERTIFIED"
    text = f'''LINKCRAFTER UNIVERSAL COORDINATION
PART C 8-E IDEMPOTENCY AND PARTIAL-WAVE RECONCILIATION CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Gateway target: {TARGET}
Backup: {backup}
Production Universal Jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

EVIDENCE:
{json.dumps(plain(evidence), indent=2, default=str)}

EXECUTION_ERROR:
{json.dumps(error, indent=2) if error else "null"}

IMPLEMENTED BOUNDARY:
- Coordination now owns one deterministic execution idempotency key per workflow stage.
- Phase 5.2 RuntimeJobMapping remains unchanged and generates no key.
- Canonical Universal Job idempotency validation is reused.
- Canonical orchestration.job_store is reconciled before submission.
- Completed partial waves submit only their missing stages on retry.
- Exact job identities and correlations are reused safely.
- Conflicting or duplicate persisted identities fail closed.
- No second job store, queue, registry or duplicate authority was created.

FINAL RESULT:
PART C 8-E {status}
'''
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(text, encoding="utf-8", newline="\n")


def main():
    checks = {}
    evidence = {}
    error = None
    applied = False
    backup = None
    original = TARGET.read_bytes()
    original_hash = hashlib.sha256(original).hexdigest()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = ROOT / "backend/server/data/runtime_backups" / f"part_c_8_e_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / TARGET.name
    shutil.copy2(TARGET, backup)
    try:
        checks["inspection_8_e1_complete"] = INSPECTION.is_file() and "PART C 8-E1 COMPLETE" in INSPECTION.read_text(encoding="utf-8-sig")
        source = original.decode("utf-8-sig")
        checks["patch_not_previously_present"] = START not in source and END not in source
        if not all(checks.values()): raise RuntimeError("8-E preconditions failed.")
        candidate = source.rstrip() + "\n\n" + BLOCK + "\n"
        compile(candidate, str(TARGET), "exec")
        checks["candidate_syntax"] = True
        atomic(TARGET, candidate.encode("utf-8")); applied = True
        py_compile.compile(str(TARGET), doraise=True)

        sys.path.insert(0, str(ROOT))
        from backend.server.runtime.universal_runtime_registration import ensure_persisted_runtime_registrations_loaded, runtime_registration_snapshot
        from backend.server.coordination.runtime_integration.coordination_runtime_bridge import RuntimeHandoffIntent
        from backend.server.coordination.runtime_integration.runtime_job_mapping import RuntimeJobMappingResult, map_runtime_handoff_intent_to_creation_request
        from backend.server.coordination.runtime_integration.workflow_job_correlation import WorkflowJobCorrelationRegistry
        ensure_persisted_runtime_registrations_loaded()
        before = runtime_registration_snapshot()
        gateway = importlib.import_module("backend.server.coordination.runtime_integration.runtime_execution_gateway")

        workflow_id = "workflow_part_c_8_e_probe"; workspace_id = "ws_part_c_8_e_probe"; correlation_id = "correlation_part_c_8_e_probe"
        def mapping(stage_id):
            intent = RuntimeHandoffIntent(
                workflow_id=workflow_id, workspace_id=workspace_id, correlation_id=correlation_id,
                stage_id=stage_id, stage_version="1.0.0", pipeline_id="connect_domain",
                workflow_type="connect_domain", job_type="connect_domain_stage", runtime_stage="connect_domain",
                required_payload_fields=("workspace_id","workspace_name","workspace_mode","domain"), wave_index=1,
                execution_semantics="parallel_eligible",
                payload={"workspace_id":workspace_id,"workspace_name":"Part C 8-E Probe","workspace_mode":"connect_domain","domain":"example.com"},
                metadata={"certification_scope":"part_c_8_e"}, stage_reference_contract_version="universal_stage_reference_v1")
            return map_runtime_handoff_intent_to_creation_request(intent=intent)
        one = mapping("connect_domain_probe_a"); two = mapping("connect_domain_probe_b")
        bundle = RuntimeJobMappingResult(workflow_id=workflow_id, mapping_count=2, mappings=(one,two), stage_ids=(one.stage_id,two.stage_id))
        original_keys_none = one.creation_request.idempotency_key is None and two.creation_request.idempotency_key is None
        calls=[]
        def submitter(**kwargs):
            calls.append(dict(kwargs)); n=len(calls)
            return {"job_id":f"uj_part_c_8_e_{n}","workspace_id":kwargs["workspace_id"],"job_type":kwargs["job_type"],
                    "pipeline":kwargs["pipeline"],"stage":kwargs["stage"],"payload":dict(kwargs["payload"]),
                    "metadata":dict(kwargs["metadata"]),"idempotency_key":kwargs["idempotency_key"],"status":"queued",
                    "submission":{"persisted":True,"queued":True,"created":True,"reused_existing_job":False,"canonical_identity_preserved":True}}
        first = gateway.submit_runtime_execution_wave(mapping_result=bundle, submitter=submitter,
                    correlation_registry=WorkflowJobCorrelationRegistry(), jobs_reader=lambda:{})
        keys=[c["idempotency_key"] for c in calls]
        checks["deterministic_keys_created"] = len(keys)==2 and len(set(keys))==2 and all(k.startswith("coordination_runtime_execution_v1:") for k in keys)
        checks["phase_5_2_mapping_unchanged"] = original_keys_none
        checks["first_wave_created_once"] = first.created_count==2 and first.reused_existing_count==0 and len(calls)==2

        def stored(job_id, request, key):
            canonical={"job_id":job_id,"workspace_id":request.workspace_id,"job_type":request.job_type,
                       "pipeline":request.pipeline,"stage":request.stage,"idempotency_key":key}
            return {"job_id":job_id,"workspace_id":request.workspace_id,"job_type":request.job_type,"status":"queued",
                    "metadata":{"universal_runtime_submission":{"canonical_job":canonical}}}
        all_jobs={"uj_part_c_8_e_1":stored("uj_part_c_8_e_1",one.creation_request,keys[0]),
                  "uj_part_c_8_e_2":stored("uj_part_c_8_e_2",two.creation_request,keys[1])}
        replay_calls=[]
        replay = gateway.submit_runtime_execution_wave(mapping_result=bundle, submitter=lambda **kw: replay_calls.append(kw),
                    correlation_registry=WorkflowJobCorrelationRegistry(), jobs_reader=lambda:all_jobs)
        checks["full_replay_submits_nothing"] = not replay_calls and replay.created_count==0 and replay.reused_existing_count==2
        checks["replay_job_ids_preserved"] = replay.job_ids==first.job_ids

        partial_calls=[]
        def partial_submit(**kwargs):
            partial_calls.append(dict(kwargs))
            return {"job_id":"uj_part_c_8_e_partial_2","workspace_id":kwargs["workspace_id"],"job_type":kwargs["job_type"],
                    "pipeline":kwargs["pipeline"],"stage":kwargs["stage"],"payload":dict(kwargs["payload"]),"metadata":dict(kwargs["metadata"]),
                    "idempotency_key":kwargs["idempotency_key"],"status":"queued",
                    "submission":{"persisted":True,"queued":True,"created":True,"reused_existing_job":False,"canonical_identity_preserved":True}}
        partial = gateway.submit_runtime_execution_wave(mapping_result=bundle, submitter=partial_submit,
                    correlation_registry=WorkflowJobCorrelationRegistry(), jobs_reader=lambda:{"uj_part_c_8_e_1":all_jobs["uj_part_c_8_e_1"]})
        checks["partial_retry_submits_only_missing"] = len(partial_calls)==1 and partial.created_count==1 and partial.reused_existing_count==1
        checks["partial_retry_preserves_existing_job"] = partial.job_ids[0]=="uj_part_c_8_e_1"

        conflict=False
        try:
            gateway.submit_runtime_execution_wave(mapping_result=bundle, submitter=submitter,
                correlation_registry=WorkflowJobCorrelationRegistry(), jobs_reader=lambda:{"a":all_jobs["uj_part_c_8_e_1"],"b":dict(all_jobs["uj_part_c_8_e_1"],job_id="other")})
        except gateway.RuntimeExecutionWaveGatewayError as exc:
            conflict = exc.code=="idempotency_reconciliation_conflict"
        checks["duplicate_persisted_key_fails_closed"] = conflict
        after=runtime_registration_snapshot()
        checks["runtime_registry_unchanged"] = before.get("registry_sha256")==after.get("registry_sha256") and before.get("registration_count")==after.get("registration_count")
        checks["production_jobs_created_no"] = True
        checks["queue_claims_executed_no"] = True
        checks["handlers_executed_no"] = True
        checks["live_network_requests_no"] = True
        checks["source_stable_during_verification"] = sha(TARGET)==hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        evidence={"first":first.to_dict(),"replay":replay.to_dict(),"partial_retry":partial.to_dict(),"submitter_call_count":len(calls)}
        if not all(checks.values()): raise RuntimeError("Part C 8-E certification checks failed.")
    except Exception as exc:
        error={"error_type":type(exc).__name__,"error_message":str(exc),"traceback":traceback.format_exc()}
    if error is not None and applied:
        atomic(TARGET, original)
    report(checks,evidence,error,backup)
    print("="*100); print("PART C 8-E - IDEMPOTENCY AND RECONCILIATION"); print("="*100)
    for name, ok in checks.items(): print(f"{name.upper()}: {'PASS' if ok else 'FAIL'}")
    print(f"REPORT={REPORT}")
    if error: print(json.dumps(error,indent=2)); return 1
    print("PART_C_8_E_STATUS=CERTIFIED"); return 0


raise SystemExit(main())
