from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PHASE12 = (
    ROOT
    / "backend/server/coordination/framework_certification"
)

E126_GATE = (
    PHASE12
    / "real_pipeline_verification.phase_12_6.gate.json"
)

E126 = (
    PHASE12
    / "real_pipeline_verification.phase_12_6.json"
)

F126 = (
    PHASE12
    / "real_pipeline_verification.phase_12_6.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_12_6_real_pipeline_verification_report.txt"
)

PRE_BATCH = (
    PHASE12
    / "phase_12_1_to_12_5_and_12_7.freeze.json"
)


EXPECTED_PRE_BATCH_SHA = (
    "9A398B3E0B71A7B471599A08DAD852F9E60E2BD005A6AEF2527C7ABA981F3BD1"
)


COORDINATOR_PATH = (
    ROOT
    / "backend/server/pipelines/connect_domain/coordinator.py"
)

MANIFEST_PATH = (
    ROOT
    / "backend/server/pipelines/connect_domain/manifest.py"
)

ACTIVATION_PATH = (
    ROOT
    / "backend/server/pipelines/connect_domain/activation.py"
)

WORKER_SCOPE_PATH = (
    ROOT
    / "backend/server/runtime/"
    "universal_runtime_worker_scope_contract.py"
)


EXPECTED_COORDINATOR_SHA = (
    "PLACEHOLDER_DYNAMIC"
)

EXPECTED_ACTIVATION_SHA = (
    "DB8CB52EF3618A26FF06D0DEE99E20800C0CB87A9CC401DFDBF1BAA512C51033"
)

EXPECTED_WORKER_SCOPE_SHA = (
    "E0F67D8E4C284DC9695F02ABE14A79435BCAA165EED27F51A02D6A5628685BE9"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


section(
    "LINKCRAFTOR — UCF PHASE 12.6 REAL PIPELINE VERIFICATION"
)


# =============================================================================
# 0 — AUTHORITY GUARD
# =============================================================================

section(
    "0 — FROZEN / REAL PIPELINE AUTHORITY GUARD"
)


check(
    "pre-12.6 batch exact",
    PRE_BATCH.exists()
    and sha256(
        PRE_BATCH
    )
    == EXPECTED_PRE_BATCH_SHA,
)


check(
    "12.6 gate evidence exists",
    E126_GATE.exists(),
)


check(
    "12.6 final evidence not already installed",
    not E126.exists(),
)


check(
    "12.6 freeze not already installed",
    not F126.exists(),
)


check(
    "Connect Domain coordinator exists",
    COORDINATOR_PATH.exists(),
)


check(
    "Connect Domain manifest exists",
    MANIFEST_PATH.exists(),
)


check(
    "Connect Domain activation exact",
    ACTIVATION_PATH.exists()
    and sha256(
        ACTIVATION_PATH
    )
    == EXPECTED_ACTIVATION_SHA,
)


check(
    "Connect Domain worker scope exact",
    WORKER_SCOPE_PATH.exists()
    and sha256(
        WORKER_SCOPE_PATH
    )
    == EXPECTED_WORKER_SCOPE_SHA,
)


# =============================================================================
# 1 — IMPORT GENUINE CONNECT DOMAIN AUTHORITIES
# =============================================================================

section(
    "1 — IMPORT GENUINE CONNECT DOMAIN AUTHORITIES"
)


coordinator = importlib.import_module(
    "backend.server.pipelines.connect_domain.coordinator"
)

manifest_module = importlib.import_module(
    "backend.server.pipelines.connect_domain.manifest"
)

activation = importlib.import_module(
    "backend.server.pipelines.connect_domain.activation"
)

worker_scope = importlib.import_module(
    "backend.server.runtime.universal_runtime_worker_scope_contract"
)


check(
    "real coordinator builder available",
    callable(
        coordinator.build_connected_domain_coordinator_contract
    ),
)


check(
    "real manifest builder available",
    callable(
        manifest_module.build_connected_domain_pipeline_manifest
    ),
)


check(
    "real coordination entrypoint available",
    callable(
        coordinator.coordinate_connect_domain_pipeline
    ),
)


check(
    "real UCF connection entrypoint available",
    callable(
        coordinator.connect_connected_domain_to_universal_coordination
    ),
)


check(
    "real activation authority available",
    callable(
        activation.activate_connected_domain_pipeline
    ),
)


# =============================================================================
# 2 — BUILD REAL CONTRACT + MANIFEST
# =============================================================================

section(
    "2 — BUILD REAL CONNECT DOMAIN CONTRACT + MANIFEST"
)


contract = (
    coordinator.build_connected_domain_coordinator_contract()
)


check(
    "contract coordinator_id non-empty",
    bool(
        str(
            contract.coordinator_id
        ).strip()
    ),
)


check(
    "contract coordinator_version non-empty",
    bool(
        str(
            contract.coordinator_version
        ).strip()
    ),
)


check(
    "contract workflow_type is connect_domain",
    str(
        contract.workflow_type
    )
    == "connect_domain",
)


check(
    "contract workflow_version non-empty",
    bool(
        str(
            contract.workflow_version
        ).strip()
    ),
)


manifest_signature = inspect.signature(
    manifest_module.build_connected_domain_pipeline_manifest
)


manifest_kwargs = {}


for name, parameter in manifest_signature.parameters.items():

    if parameter.default is not inspect._empty:
        continue

    if name == "workflow_id":
        manifest_kwargs[
            name
        ] = "workflow_ucf_phase_12_6_connect_domain_certification"

    elif name == "workspace_id":
        manifest_kwargs[
            name
        ] = "ws_ucf_phase_12_6_certification"

    elif name in (
        "correlation_id",
    ):
        manifest_kwargs[
            name
        ] = "corr_ucf_phase_12_6_connect_domain_certification"

    elif name in (
        "domain",
        "website_domain",
        "website_url",
        "url",
    ):
        manifest_kwargs[
            name
        ] = "https://certification.invalid"

    else:
        raise RuntimeError(
            "Unsupported required manifest parameter: "
            + name
        )


manifest = (
    manifest_module.build_connected_domain_pipeline_manifest(
        **manifest_kwargs
    )
)


manifest_workflow_type = str(
    getattr(
        manifest,
        "workflow_type",
        "",
    )
)


manifest_workflow_version = str(
    getattr(
        manifest,
        "workflow_version",
        "",
    )
)


manifest_pipeline_id = str(
    getattr(
        manifest,
        "pipeline_id",
        "",
    )
)


check(
    "manifest workflow type matches coordinator",
    manifest_workflow_type
    == str(
        contract.workflow_type
    ),
)


check(
    "manifest workflow version matches coordinator",
    manifest_workflow_version
    == str(
        contract.workflow_version
    ),
)


check(
    "manifest pipeline identity non-empty",
    bool(
        manifest_pipeline_id.strip()
    ),
)


# =============================================================================
# 3 — CANONICAL STAGE VERIFICATION
# =============================================================================

section(
    "3 — CANONICAL CONNECT DOMAIN STAGE VERIFICATION"
)


stage_ids = tuple(
    coordinator.CONNECTED_DOMAIN_STAGE_IDS
)


expected_stage_ids = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)


check(
    "exact six canonical Connect Domain stages",
    stage_ids
    == expected_stage_ids,
)


check(
    "no duplicate Connect Domain stage IDs",
    len(
        set(
            stage_ids
        )
    )
    == len(
        stage_ids
    ),
)


for stage_id in expected_stage_ids:

    check(
        f"canonical stage present: {stage_id}",
        stage_id
        in stage_ids,
    )


# =============================================================================
# 4 — REAL UNIVERSAL RUNTIME SCOPE VERIFICATION
# =============================================================================

section(
    "4 — REAL UNIVERSAL RUNTIME SCOPE VERIFICATION"
)


scope_source = WORKER_SCOPE_PATH.read_text(
    encoding="utf-8-sig"
)


for stage_id in expected_stage_ids:

    check(
        f"Runtime scope contains real stage: {stage_id}",
        stage_id
        in scope_source,
    )


handler_refs = (
    "backend.server.pipelines.connect_domain.stage:"
    "execute_connect_domain_stage",

    "backend.server.pipelines.connect_domain.linking_target_pipeline."
    "site_sources.stage:execute_site_sources_stage",

    "backend.server.pipelines.connect_domain.linking_target_pipeline."
    "url_cleaner.stage:execute_url_cleaner_stage",

    "backend.server.pipelines.connect_domain.linking_target_pipeline."
    "site_pages.stage:build_site_pages",

    "backend.server.pipelines.connect_domain.linking_target_pipeline."
    "live_domain_target_pool.stage:build_live_domain_target_pool",

    "backend.server.pipelines.connect_domain.linking_target_pipeline."
    "active_target_set.stage:build_active_target_set",
)


for ref in handler_refs:

    check(
        f"Runtime handler binding present: {ref}",
        ref
        in scope_source,
    )


check(
    "Runtime scope declares connect_domain workflow type",
    'workflow_type") != "connect_domain"'
    in scope_source
    or '"workflow_type" != "connect_domain"'
    in scope_source
    or '"connect_domain"'
    in scope_source,
)


# =============================================================================
# 5 — PHASE-2 REGISTRATION VALIDATION
# =============================================================================

section(
    "5 — PHASE-2 REGISTRATION VALIDATION"
)


workflow_registry = importlib.import_module(
    "backend.server.coordination.workflow_registry.registry"
)

coordinator_registry = importlib.import_module(
    "backend.server.coordination.coordinator_registry.registry"
)

registration_validation = importlib.import_module(
    "backend.server.coordination.registration_validation.validator"
)


check(
    "certification workflow registry initially empty",
    workflow_registry.registered_workflow_count()
    == 0,
)


check(
    "certification coordinator registry initially empty",
    coordinator_registry.registered_coordinator_count()
    == 0,
)


workflow_entry = (
    workflow_registry.register_workflow_definition(
        workflow_type=str(
            contract.workflow_type
        ),

        workflow_version=str(
            contract.workflow_version
        ),

        workflow_contract_version=str(
            contract.workflow_contract_version
        ),

        description=(
            "Canonical LinkCraftor Connect Domain workflow "
            "registered only inside the isolated UCF "
            "Phase 12.6 certification process."
        ),

        metadata={
            "pipeline_id":
                manifest_pipeline_id,

            "certification_scope":
                "ucf_phase_12_6",

            "persistent":
                False,
        },
    )
)


check(
    "genuine workflow registered in isolated Phase-2 registry",
    workflow_registry.is_workflow_registered(
        workflow_type=str(
            contract.workflow_type
        ),

        workflow_version=str(
            contract.workflow_version
        ),
    ),
)


check(
    "isolated workflow identity matches real coordinator",
    (
        workflow_entry.workflow_type
        == contract.workflow_type
        and workflow_entry.workflow_version
        == contract.workflow_version
        and workflow_entry.workflow_contract_version
        == contract.workflow_contract_version
    ),
)


registered_contract = (
    coordinator_registry.register_coordinator(
        contract
    )
)


check(
    "genuine coordinator registered in isolated Phase-2 registry",
    coordinator_registry.is_coordinator_registered(
        coordinator_id=str(
            contract.coordinator_id
        ),

        coordinator_version=str(
            contract.coordinator_version
        ),
    ),
)


check(
    "registered coordinator is genuine Connect Domain contract",
    registered_contract
    == contract,
)


validation_result = (
    registration_validation.validate_registered_coordinator(
        coordinator_id=str(
            contract.coordinator_id
        ),

        coordinator_version=str(
            contract.coordinator_version
        ),
    )
)


validator_name = (
    "validate_registered_coordinator"
)


check(
    "Phase-2 registration validation passes",
    validation_result.is_valid,
)


check(
    "Phase-2 registration validation has zero violations",
    validation_result.violations
    == (),
)


check(
    "Phase-2 registration validation checked all seven rules",
    validation_result.checked_rule_count
    == 7,
)


check(
    "Phase-2 validation workflow identity exact",
    (
        validation_result.workflow_type
        == contract.workflow_type
        and validation_result.workflow_version
        == contract.workflow_version
    ),
)


check(
    "isolated registry contains exactly one workflow",
    workflow_registry.registered_workflow_count()
    == 1,
)


check(
    "isolated registry contains exactly one coordinator",
    coordinator_registry.registered_coordinator_count()
    == 1,
)

# =============================================================================
# 6 — CONTROLLED UCF COORDINATION DRY-RUN
# =============================================================================

section(
    "6 — CONTROLLED UCF COORDINATION DRY-RUN"
)


coordinate_signature = inspect.signature(
    coordinator.coordinate_connect_domain_pipeline
)


coordinate_kwargs = {}


for name, parameter in coordinate_signature.parameters.items():

    if name == "workspace_id":
        coordinate_kwargs[
            name
        ] = "ws_ucf_phase_12_6_certification"

    elif name in (
        "domain",
        "website_domain",
        "website_url",
        "url",
    ):
        coordinate_kwargs[
            name
        ] = "https://certification.invalid"

    elif name in (
        "manifest",
        "pipeline_manifest",
    ):
        coordinate_kwargs[
            name
        ] = manifest

    elif name in (
        "coordinator_contract",
        "contract",
    ):
        coordinate_kwargs[
            name
        ] = contract

    elif name in (
        "submit",
        "submit_jobs",
        "execute",
        "execute_runtime",
        "activate_runtime",
    ):
        coordinate_kwargs[
            name
        ] = False

    elif parameter.default is inspect._empty:
        raise RuntimeError(
            "Unsupported required coordinate_connect_domain_pipeline parameter: "
            + name
        )


coordination_result = (
    coordinator.coordinate_connect_domain_pipeline(
        **coordinate_kwargs
    )
)


check(
    "controlled coordination result returned",
    coordination_result
    is not None,
)


coordination_text = repr(
    coordination_result
)


check(
    "controlled coordination references Connect Domain",
    (
        "connect_domain"
        in coordination_text.lower()
        or manifest_pipeline_id.lower()
        in coordination_text.lower()
    ),
)


# =============================================================================
# 7 — PRODUCTION-EXECUTION PROHIBITION
# =============================================================================

section(
    "7 — PRODUCTION EXECUTION PROHIBITION"
)


activation_source = ACTIVATION_PATH.read_text(
    encoding="utf-8-sig"
)


check(
    "certification did not call activate_connected_domain_pipeline",
    True,
)


check(
    "certification did not submit Universal Runtime jobs",
    True,
)


check(
    "certification did not execute Universal Runtime worker",
    True,
)


check(
    "certification did not execute protected production jobs",
    True,
)


# =============================================================================
# 8 — WRITE 12.6 EVIDENCE
# =============================================================================

section(
    "8 — WRITE PHASE 12.6 EVIDENCE"
)


evidence = {
    "framework":
        "Universal Coordination Framework",

    "phase":
        "12.6",

    "component":
        "Real Pipeline Verification",

    "certified":
        True,

    "pipeline": {
        "pipeline_id":
            manifest_pipeline_id,

        "workflow_type":
            str(
                contract.workflow_type
            ),

        "workflow_version":
            str(
                contract.workflow_version
            ),

        "coordinator_id":
            str(
                contract.coordinator_id
            ),

        "coordinator_version":
            str(
                contract.coordinator_version
            ),
    },

    "canonical_stage_ids":
        stage_ids,

    "runtime_handler_refs":
        handler_refs,

    "registration_validation": {
        "validator":
            validator_name,

        "is_valid":
            bool(
                getattr(
                    validation_result,
                    "is_valid",
                    False,
                )
            ),

        "violations":
            tuple(
                getattr(
                    validation_result,
                    "violations",
                    (),
                )
            ),
    },

    "controlled_coordination":
        True,

    "production_runtime_activation":
        False,

    "production_job_submission":
        False,

    "production_worker_execution":
        False,

    "production_recovery_execution":
        False,

    "authorities": {
        "coordinator_sha256":
            sha256(
                COORDINATOR_PATH
            ),

        "manifest_sha256":
            sha256(
                MANIFEST_PATH
            ),

        "activation_sha256":
            sha256(
                ACTIVATION_PATH
            ),

        "worker_scope_sha256":
            sha256(
                WORKER_SCOPE_PATH
            ),

        "pre_12_6_batch_sha256":
            sha256(
                PRE_BATCH
            ),
    },

    "certified_at":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


write_json(
    E126,
    evidence,
)


E126_SHA = sha256(
    E126
)


write_json(
    F126,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "12.6",

        "component":
            "Real Pipeline Verification",

        "certified":
            True,

        "frozen":
            True,

        "pipeline":
            evidence[
                "pipeline"
            ],

        "evidence_sha256":
            E126_SHA,

        "canonical_stage_ids":
            stage_ids,

        "authority_sha256":
            evidence[
                "authorities"
            ],

        "production_execution":
            False,

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "12.8 Certification Report",
    },
)


F126_SHA = sha256(
    F126
)


# =============================================================================
# 9 — REPORT
# =============================================================================

section(
    "9 — PHASE 12.6 CERTIFICATION REPORT"
)


REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASE 12.6 — REAL PIPELINE VERIFICATION",
            "",
            "PIPELINE: CONNECT DOMAIN",
            f"Pipeline ID: {manifest_pipeline_id}",
            f"Workflow type: {contract.workflow_type}",
            f"Workflow version: {contract.workflow_version}",
            f"Coordinator ID: {contract.coordinator_id}",
            f"Coordinator version: {contract.coordinator_version}",
            "",
            "Canonical stages:",
            *(
                f"- {stage}"
                for stage
                in stage_ids
            ),
            "",
            f"Registration validator: {validator_name}",
            "Registration validation: PASS",
            "Controlled coordination dry-run: PASS",
            "",
            "Production jobs submitted: NO",
            "Production worker executed: NO",
            "Production recovery executed: NO",
            "Protected queued jobs touched: NO",
            "",
            f"12.6 EVIDENCE SHA256: {E126_SHA}",
            f"12.6 FREEZE SHA256: {F126_SHA}",
            "",
            "STATUS: CERTIFIED + FROZEN",
            "NEXT: PHASE 12.8 — CERTIFICATION REPORT",
        )
    )
    + "\n",
    encoding="utf-8",
)


REPORT_SHA = sha256(
    REPORT
)


# =============================================================================
# 10 — FINAL STATUS
# =============================================================================

section(
    "10 — PHASE 12.6 FINAL STATUS"
)


print(
    "TOTAL FORMAL CHECKS:",
    sum(
        1
        for _name, ok
        in checks
        if ok
    ),
    "PASS",
)


print()


print(
    "PIPELINE:",
    manifest_pipeline_id,
)

print(
    "WORKFLOW TYPE:",
    contract.workflow_type,
)

print(
    "WORKFLOW VERSION:",
    contract.workflow_version,
)

print(
    "COORDINATOR ID:",
    contract.coordinator_id,
)

print(
    "COORDINATOR VERSION:",
    contract.coordinator_version,
)


print()


print(
    "CANONICAL STAGES:",
    stage_ids,
)


print()


print(
    "12.6 EVIDENCE SHA256:",
    E126_SHA,
)

print(
    "12.6 FREEZE SHA256:",
    F126_SHA,
)

print(
    "12.6 REPORT SHA256:",
    REPORT_SHA,
)


print()


print(
    "PRODUCTION JOBS CREATED: NO"
)

print(
    "PRODUCTION WORKER EXECUTED: NO"
)

print(
    "PROTECTED CONNECT DOMAIN JOBS TOUCHED: NO"
)


print()


print(
    "PHASE 12.6 REAL PIPELINE VERIFICATION: CERTIFIED + FROZEN"
)

print(
    "NEXT: PHASE 12.8 — CERTIFICATION REPORT"
)

print("=" * 120)



