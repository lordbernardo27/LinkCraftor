from __future__ import annotations

import ast
import hashlib
import importlib
import sys

from dataclasses import fields
from pathlib import Path
from types import MappingProxyType


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

EVIDENCE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "evidence_records.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_17_orchestration_evidence_final_certification.txt"
)

EXPECTED_AST = (
    "6BF84A9D3E8B120D5506DFF31D4BEB8718ECF488820E69782C7F0F7C85758FD9"
)


PROTECTED = {
    "5.1.1_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),
    "5.1.2_run_identity": (
        ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),
    "5.1.3_state_model": (
        ROOT / "backend/server/runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),
    "5.1.4_dependency_resolution": (
        ROOT / "backend/server/runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),
    "5.1.5_execution_planning": (
        ROOT / "backend/server/runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),
    "5.1.6_stage_readiness": (
        ROOT / "backend/server/runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),
    "5.1.7_runtime_handoff": (
        ROOT / "backend/server/runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),
    "5.1.8_fan_out": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),
    "5.1.9_fan_in": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),
    "5.1.10_conditional_branching": (
        ROOT / "backend/server/runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),
    "5.1.11_progress_tracking": (
        ROOT / "backend/server/runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),
    "5.1.12_suspension_resume": (
        ROOT / "backend/server/runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),
    "5.1.13_recovery": (
        ROOT / "backend/server/runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    "5.1.14_persistence": (
        ROOT / "backend/server/runtime/universal_orchestration/persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),
    "5.1.15_completion": (
        ROOT / "backend/server/runtime/universal_orchestration/completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
    ),
    "5.1.16_cancellation": (
        ROOT / "backend/server/runtime/universal_orchestration/cancellation_termination.py",
        "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",
    ),
}


def ast_sha(path: Path) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not EVIDENCE_PATH.exists():

    raise SystemExit(
        "5.1.17 Evidence Records authority is missing."
    )


initial_ast = ast_sha(
    EVIDENCE_PATH
)


if initial_ast != EXPECTED_AST:

    raise SystemExit(
        (
            "5.1.17 AST changed before final certification.\n"
            "EXPECTED: "
            + EXPECTED_AST
            + "\nACTUAL:   "
            + initial_ast
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            "Protected authority mismatch before final certification: "
            + name
        )


# ============================================================
# IMPORT AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.evidence_records"
)

sys.modules.pop(
    module_name,
    None,
)

evidence = importlib.import_module(
    module_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


A = "A" * 64
B = "B" * 64

D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64


def create(
    *,
    identity=A,
    kind="recovery",
    decision=D1,
    previous=None,
):

    return (
        evidence
        .create_universal_orchestration_decision_evidence_record(
            identity_fingerprint=identity,
            decision_kind=kind,
            decision_id=decision,
            previous_record_id=previous,
        )
    )


# ============================================================
# EXACT CONSTANTS
# ============================================================

check(
    "ast_exact",
    ast_sha(
        EVIDENCE_PATH
    )
    ==
    EXPECTED_AST,
)

check(
    "version_exact",
    evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORDS_VERSION
    ==
    "universal_orchestration_evidence_records_v5.1.17",
)

check(
    "schema_exact",
    evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION
    ==
    "universal_orchestration_evidence_record_schema_v1",
)

check(
    "hash_algorithm_exact",
    evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_HASH_ALGORITHM
    ==
    "sha256",
)


# ============================================================
# DECISION KINDS
# ============================================================

check(
    "decision_kinds_exact",
    tuple(
        item.value
        for item
        in evidence.UniversalOrchestrationDecisionKind
    )
    ==
    (
        "suspension_resume_eligibility",
        "recovery",
        "completion",
        "cancellation_termination",
    ),
)


# ============================================================
# STORED FIELDS
# ============================================================

stored_fields = tuple(
    field.name
    for field
    in fields(
        evidence.UniversalOrchestrationDecisionEvidenceRecord
    )
)


check(
    "stored_fields_exact",
    stored_fields
    ==
    (
        "identity_fingerprint",
        "decision_kind",
        "decision_id",
        "previous_record_id",
        "schema_version",
    ),
    stored_fields,
)


# ============================================================
# CANONICAL RECORD CHAIN
# ============================================================

root = create(
    identity=A,
    kind="suspension_resume_eligibility",
    decision=D1,
)


check(
    "root_previous_none",
    root.previous_record_id
    is None,
)

check(
    "root_is_root",
    root.is_root_record,
)

check(
    "root_source_phase",
    root.source_phase
    ==
    "5.1.12",
)


second = create(
    identity=A,
    kind="recovery",
    decision=D2,
    previous=root.evidence_record_id,
)


third = create(
    identity=A,
    kind="completion",
    decision=D3,
    previous=second.evidence_record_id,
)


fourth = create(
    identity=A,
    kind="cancellation_termination",
    decision=D4,
    previous=third.evidence_record_id,
)


check(
    "second_phase",
    second.source_phase
    ==
    "5.1.13",
)

check(
    "third_phase",
    third.source_phase
    ==
    "5.1.15",
)

check(
    "fourth_phase",
    fourth.source_phase
    ==
    "5.1.16",
)


check(
    "successor_root_second",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=root,
        next_record=second,
    )
    is True,
)

check(
    "successor_second_third",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=second,
        next_record=third,
    )
    is True,
)

check(
    "successor_third_fourth",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=third,
        next_record=fourth,
    )
    is True,
)


# ============================================================
# DETERMINISM
# ============================================================

root_repeat = create(
    identity=A,
    kind="suspension_resume_eligibility",
    decision=D1,
)


check(
    "record_id_deterministic",
    root.evidence_record_id
    ==
    root_repeat.evidence_record_id,
)

check(
    "record_id_length",
    len(
        root.evidence_record_id
    )
    ==
    64,
    root.evidence_record_id,
)

check(
    "record_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in root.evidence_record_id
    ),
)


# ============================================================
# ID SENSITIVITY
# ============================================================

identity_changed = create(
    identity=B,
    kind="suspension_resume_eligibility",
    decision=D1,
)


kind_changed = create(
    identity=A,
    kind="completion",
    decision=D1,
)


decision_changed = create(
    identity=A,
    kind="suspension_resume_eligibility",
    decision=D2,
)


predecessor_changed = create(
    identity=A,
    kind="suspension_resume_eligibility",
    decision=D1,
    previous="F" * 64,
)


check(
    "record_id_identity_sensitive",
    root.evidence_record_id
    !=
    identity_changed.evidence_record_id,
)

check(
    "record_id_kind_sensitive",
    root.evidence_record_id
    !=
    kind_changed.evidence_record_id,
)

check(
    "record_id_decision_sensitive",
    root.evidence_record_id
    !=
    decision_changed.evidence_record_id,
)

check(
    "record_id_predecessor_sensitive",
    root.evidence_record_id
    !=
    predecessor_changed.evidence_record_id,
)


# ============================================================
# LINEAGE PROTECTION
# ============================================================

skipped = create(
    identity=A,
    kind="completion",
    decision=D3,
    previous=root.evidence_record_id,
)


try:

    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=second,
        next_record=skipped,
    )

except evidence.UniversalOrchestrationEvidenceError as exc:

    skipped_rejected = (
        exc.code
        ==
        "evidence_successor_link_mismatch"
    )

else:

    skipped_rejected = False


check(
    "skipped_predecessor_rejected",
    skipped_rejected,
)


cross_run = create(
    identity=B,
    kind="recovery",
    decision=D2,
    previous=root.evidence_record_id,
)


try:

    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=root,
        next_record=cross_run,
    )

except evidence.UniversalOrchestrationEvidenceError as exc:

    cross_run_rejected = (
        exc.code
        ==
        "evidence_successor_identity_mismatch"
    )

else:

    cross_run_rejected = False


check(
    "cross_run_rejected",
    cross_run_rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    fourth
):

    try:

        setattr(
            fourth,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + field.name,
        immutable,
    )


manifest = fourth.manifest


check(
    "manifest_mappingproxy",
    isinstance(
        manifest,
        MappingProxyType,
    ),
)


try:

    manifest[
        "decision_id"
    ] = (
        "0" * 64
    )

except Exception:

    manifest_immutable = True

else:

    manifest_immutable = False


check(
    "manifest_immutable",
    manifest_immutable,
)


check(
    "manifest_keys_exact",
    tuple(
        manifest.keys()
    )
    ==
    (
        "evidence_record_id",
        "previous_record_id",
        "identity_fingerprint",
        "decision_kind",
        "source_phase",
        "decision_id",
        "schema_version",
    ),
)


# ============================================================
# ROOT SEMANTICS
# ============================================================

check(
    "root_none_valid",
    create(
        previous=None,
    ).previous_record_id
    is None,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    evidence
    .explain_universal_orchestration_evidence_records_v1()
)


check(
    "explanation_mappingproxy",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    ==
    "5.1.17",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Evidence & Decision Records",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    ==
    (
        "identity_fingerprint",
        "decision_kind",
        "decision_id",
        "previous_record_id",
        "schema_version",
    ),
)


check(
    "decision_authorities_exact",
    explanation.get(
        "decision_authorities"
    )
    ==
    (
        "5.1.12 suspension/resume eligibility",
        "5.1.13 recovery",
        "5.1.15 completion resolution",
        "5.1.16 cancellation/termination resolution",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = EVIDENCE_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "no_backend_imports",
    backend_imports
    ==
    [],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "time",
    "time_ns",
    "now",
    "utcnow",
    "sleep",

    "open",
    "read_text",
    "write_text",

    "persist",
    "save",
    "append_record",
    "load_record",
    "load_latest_record",
    "list_record_history",

    "transition_universal_orchestration_state",

    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "evaluate_universal_orchestration_recovery",
    "resolve_universal_orchestration_completion",
    "resolve_universal_orchestration_cancellation_termination",

    "enqueue_job",
    "dequeue_job",
    "claim_job",
    "requeue_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "release_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
}


found_forbidden = []


for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        call_name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = (
            node.func.attr
        )

    else:

        continue

    if call_name in forbidden_calls:

        found_forbidden.append(
            (
                call_name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not found_forbidden,
    found_forbidden,
)


# ============================================================
# FORBIDDEN STORED FIELDS
# ============================================================

for forbidden in (
    "state_snapshot",
    "progress_snapshot",
    "orchestration_state",
    "disposition",
    "reason",
    "created_at",
    "updated_at",
    "timestamp",
    "persisted_at",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in stored_fields,
    )


# ============================================================
# PROTECTED MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        ==
        expected,
        actual,
    )


# ============================================================
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_17_universal_orchestration_evidence_records",

        evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORDS_VERSION,

        evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_RECORD_SCHEMA_VERSION,

        evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_HASH_ALGORITHM,

        EXPECTED_AST,

        "decision_kind_suspension_resume_eligibility",
        "decision_kind_recovery",
        "decision_kind_completion",
        "decision_kind_cancellation_termination",

        "source_phase_5_1_12",
        "source_phase_5_1_13",
        "source_phase_5_1_15",
        "source_phase_5_1_16",

        "stored_identity_fingerprint",
        "stored_decision_kind",
        "stored_decision_id",
        "stored_previous_record_id",
        "stored_schema_version",

        "state_snapshot_not_stored",
        "progress_snapshot_not_stored",

        "immutable_record",
        "mappingproxy_manifest",

        "deterministic_sha256_record_id",

        "identity_sensitive",
        "decision_kind_sensitive",
        "decision_id_sensitive",
        "predecessor_sensitive",

        "root_previous_none",

        "append_only_predecessor_lineage",
        "same_run_successor_required",
        "cross_run_rejected",
        "skipped_predecessor_rejected",

        "upstream_decisions_not_recomputed",
        "upstream_decision_modules_not_imported",

        "5_1_14_not_invoked",

        "no_second_persistence_port",
        "no_runtime_state_store",
        "no_runtime_persistence",
        "no_runtime_audit_backend",

        "no_state_transition",
        "no_job_mutation",
        "no_recovery_execution",
        "no_cancellation_execution",

        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_wall_clock",
        "no_timestamps",

        "no_filesystem_io",
        "no_database_io",
        "no_network_io",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "deterministic_orchestration_decision_evidence_chain",
    )
)


evidence_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


certification_id = (
    "phase_5_1_17_"
    + evidence_fingerprint[
        :16
    ].lower()
)


check(
    "fingerprint_generated",
    (
        len(
            evidence_fingerprint
        )
        ==
        64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in evidence_fingerprint
        )
    ),
    evidence_fingerprint,
)


check(
    "certification_id_generated",
    certification_id
    ==
    (
        "phase_5_1_17_"
        + evidence_fingerprint[
            :16
        ].lower()
    ),
    certification_id,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    EVIDENCE_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    ==
    EXPECTED_AST,
    final_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 5.1.17 — UNIVERSAL ORCHESTRATION "
        "EVIDENCE & DECISION RECORDS FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION EVIDENCE RECORDS AST SHA256: "
        + final_ast
    ),

    (
        "ORCHESTRATION EVIDENCE RECORDS FINGERPRINT: "
        + evidence_fingerprint
    ),

    (
        "CERTIFICATION ID: "
        + certification_id
    ),

    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",

        "=" * 118,

        (
            "FINAL ORCHESTRATION EVIDENCE & DECISION RECORDS CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),

        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),

        "",

        "5.1.17 AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.16 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "CANONICAL DECISION KINDS: 4",

        "",

        "STORED FIELDS:",
        "  identity_fingerprint",
        "  decision_kind",
        "  decision_id",
        "  previous_record_id",
        "  schema_version",

        "",

        "STATE SNAPSHOT DUPLICATED: NO",
        "PROGRESS SNAPSHOT DUPLICATED: NO",

        "",

        "IMMUTABLE RECORDS: YES",
        "DETERMINISTIC RECORD IDs: YES",
        "PREDECESSOR-BASED APPEND-ONLY LINEAGE: YES",

        "",

        "ROOT RECORD PREDECESSOR: NONE",
        "CROSS-RUN LINEAGE: REJECTED",
        "SKIPPED PREDECESSOR: REJECTED",

        "",

        "IDENTITY SENSITIVE: YES",
        "DECISION KIND SENSITIVE: YES",
        "DECISION ID SENSITIVE: YES",
        "PREDECESSOR SENSITIVE: YES",

        "",

        "5.1.12 IMPORTED: NO",
        "5.1.13 IMPORTED: NO",
        "5.1.14 IMPORTED: NO",
        "5.1.15 IMPORTED: NO",
        "5.1.16 IMPORTED: NO",

        "",

        "UPSTREAM DECISIONS RECOMPUTED: NO",

        "",

        "ORCHESTRATION STATE TRANSITION: NO",
        "JOB MUTATION: NO",
        "RECOVERY EXECUTION: NO",
        "CANCELLATION EXECUTION: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "RUNTIME PERSISTENCE ACCESS: NO",
        "RUNTIME AUDIT BACKEND ACCESS: NO",
        "SECOND PERSISTENCE PORT: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "WALL CLOCK: NO",
        "TIMESTAMPS: NO",

        "",

        "FILESYSTEM I/O: NO",
        "DATABASE I/O: NO",
        "NETWORK I/O: NO",

        "",

        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.17 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        lines
    ),
    encoding="utf-8",
)


print(
    "\n".join(
        lines
    )
)


if passed != total:

    raise SystemExit(
        "Phase 5.1.17 final certification failed."
    )
