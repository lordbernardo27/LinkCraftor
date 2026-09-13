from __future__ import annotations

import ast
import hashlib
import importlib
import sys

from dataclasses import fields
from pathlib import Path
from types import MappingProxyType


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

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
    / "phase_5_1_17_orchestration_evidence_regression.txt"
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
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


if ast_sha(EVIDENCE_PATH) != EXPECTED_AST:
    raise SystemExit(
        "5.1.17 AST changed before adversarial regression."
    )


for name, (path, expected) in PROTECTED.items():
    actual = ast_sha(path)

    if actual != expected:
        raise SystemExit(
            "Protected authority mismatch before regression: "
            + name
        )


sys.path.insert(0, str(ROOT))

module_name = (
    "backend.server.runtime."
    "universal_orchestration.evidence_records"
)

sys.modules.pop(module_name, None)

evidence = importlib.import_module(module_name)


checks = []


def check(name, condition, detail=""):
    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


A = "A" * 64
B = "B" * 64
C = "C" * 64

D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64
D5 = "5" * 64


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
# 1. EXACT AUTHORITY CONTRACT
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(EVIDENCE_PATH) == EXPECTED_AST,
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
    "hash_exact",
    evidence.UNIVERSAL_ORCHESTRATION_EVIDENCE_HASH_ALGORITHM
    ==
    "sha256",
)

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
# 2. STORED FIELDS EXACT
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


for forbidden in (
    "state_snapshot",
    "progress_snapshot",
    "orchestration_state",
    "disposition",
    "reason",
    "target_terminal_state",
    "request_id",
    "request_source",
    "created_at",
    "updated_at",
    "timestamp",
    "persisted_at",
    "worker_id",
    "lease_id",
):
    check(
        "forbidden_stored_field_" + forbidden,
        forbidden not in stored_fields,
    )


# ============================================================
# 3. SHA256 NORMALIZATION ATTACKS
# ============================================================

valid_lower = "a" * 64
valid_spaced = "  " + ("b" * 64) + "  "

record_lower = create(
    identity=valid_lower,
    decision=("c" * 64),
)

check(
    "lower_identity_normalized",
    record_lower.identity_fingerprint
    ==
    ("A" * 64),
)

check(
    "lower_decision_normalized",
    record_lower.decision_id
    ==
    ("C" * 64),
)


record_spaced = create(
    identity=valid_spaced,
    decision=("  " + ("d" * 64) + "  "),
)

check(
    "spaced_identity_trimmed",
    record_spaced.identity_fingerprint
    ==
    ("B" * 64),
)

check(
    "spaced_decision_trimmed",
    record_spaced.decision_id
    ==
    ("D" * 64),
)


bad_hashes = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    " ",
    "abc",
    "0x" + ("A" * 64),
    "G" * 64,
    "Z" * 64,
    "A" * 1,
    "A" * 31,
    "A" * 32,
    "A" * 63,
    "A" * 65,
    "A" * 128,
    (),
    [],
    {},
    object(),
)


for index, bad in enumerate(
    bad_hashes,
    start=1,
):
    try:
        create(
            identity=bad,
            decision=D1,
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_evidence_identity_fingerprint"
        )
    else:
        rejected = False

    check(
        f"invalid_identity_{index}",
        rejected,
    )


for index, bad in enumerate(
    bad_hashes,
    start=1,
):
    try:
        create(
            identity=A,
            decision=bad,
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_evidence_decision_id"
        )
    else:
        rejected = False

    check(
        f"invalid_decision_{index}",
        rejected,
    )


# ============================================================
# 4. PREDECESSOR NORMALIZATION
# ============================================================

previous_lower = "e" * 64

pred_record = create(
    identity=A,
    kind="recovery",
    decision=D1,
    previous=previous_lower,
)

check(
    "previous_normalized_upper",
    pred_record.previous_record_id
    ==
    ("E" * 64),
)


for index, bad in enumerate(
    bad_hashes,
    start=1,
):
    try:
        create(
            identity=A,
            decision=D1,
            previous=bad,
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_evidence_previous_record_id"
        )
    else:
        rejected = False

    check(
        f"invalid_previous_{index}",
        rejected,
    )


# ============================================================
# 5. DECISION KIND NORMALIZATION
# ============================================================

for raw, expected in (
    (
        " suspension_resume_eligibility ",
        evidence.UniversalOrchestrationDecisionKind.SUSPENSION_RESUME_ELIGIBILITY,
    ),
    (
        " RECOVERY ",
        evidence.UniversalOrchestrationDecisionKind.RECOVERY,
    ),
    (
        " Completion ",
        evidence.UniversalOrchestrationDecisionKind.COMPLETION,
    ),
    (
        " CANCELLATION_TERMINATION ",
        evidence.UniversalOrchestrationDecisionKind.CANCELLATION_TERMINATION,
    ),
):
    candidate = create(
        kind=raw,
    )

    check(
        "kind_normalized_" + expected.value,
        candidate.decision_kind
        is expected,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        " ",
        "suspension",
        "resume",
        "eligibility",
        "recover",
        "completed",
        "cancel",
        "termination",
        "5.1.12",
        "5.1.13",
        "5.1.15",
        "5.1.16",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):
    try:
        create(
            kind=bad,
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_evidence_decision_kind"
        )
    else:
        rejected = False

    check(
        f"invalid_kind_{index}",
        rejected,
    )


# ============================================================
# 6. SOURCE PHASE MAPPING
# ============================================================

phase_matrix = (
    (
        "suspension_resume_eligibility",
        "5.1.12",
    ),
    (
        "recovery",
        "5.1.13",
    ),
    (
        "completion",
        "5.1.15",
    ),
    (
        "cancellation_termination",
        "5.1.16",
    ),
)


for kind, phase in phase_matrix:
    candidate = create(
        kind=kind,
    )

    check(
        "source_phase_" + kind,
        candidate.source_phase
        ==
        phase,
    )


# ============================================================
# 7. DETERMINISM
# ============================================================

root_ids = tuple(
    create(
        identity=A,
        kind="recovery",
        decision=D1,
    ).evidence_record_id
    for _
    in range(50)
)

check(
    "root_deterministic_50",
    len(set(root_ids))
    == 1,
)

check(
    "root_id_length",
    len(root_ids[0])
    == 64,
    root_ids[0],
)

check(
    "root_id_upper_hex",
    all(
        char in "0123456789ABCDEF"
        for char
        in root_ids[0]
    ),
)


# ============================================================
# 8. RECORD-ID SENSITIVITY
# ============================================================

baseline = create(
    identity=A,
    kind="recovery",
    decision=D1,
)

identity_changed = create(
    identity=B,
    kind="recovery",
    decision=D1,
)

kind_changed = create(
    identity=A,
    kind="completion",
    decision=D1,
)

decision_changed = create(
    identity=A,
    kind="recovery",
    decision=D2,
)

predecessor_changed = create(
    identity=A,
    kind="recovery",
    decision=D1,
    previous=("F" * 64),
)


check(
    "id_identity_sensitive",
    baseline.evidence_record_id
    !=
    identity_changed.evidence_record_id,
)

check(
    "id_kind_sensitive",
    baseline.evidence_record_id
    !=
    kind_changed.evidence_record_id,
)

check(
    "id_decision_sensitive",
    baseline.evidence_record_id
    !=
    decision_changed.evidence_record_id,
)

check(
    "id_predecessor_sensitive",
    baseline.evidence_record_id
    !=
    predecessor_changed.evidence_record_id,
)


# ============================================================
# 9. LONG APPEND-ONLY CHAIN
# ============================================================

chain = []

previous_id = None

chain_inputs = (
    (
        "suspension_resume_eligibility",
        D1,
    ),
    (
        "recovery",
        D2,
    ),
    (
        "completion",
        D3,
    ),
    (
        "cancellation_termination",
        D4,
    ),
    (
        "recovery",
        D5,
    ),
    (
        "completion",
        "6" * 64,
    ),
    (
        "suspension_resume_eligibility",
        "7" * 64,
    ),
    (
        "cancellation_termination",
        "8" * 64,
    ),
)


for kind, decision in chain_inputs:
    record = create(
        identity=A,
        kind=kind,
        decision=decision,
        previous=previous_id,
    )

    chain.append(
        record
    )

    previous_id = (
        record.evidence_record_id
    )


check(
    "chain_length_exact",
    len(chain)
    ==
    8,
)


for index in range(
    1,
    len(chain),
):
    check(
        f"chain_successor_{index}",
        evidence
        .validate_universal_orchestration_evidence_successor(
            previous_record=chain[index - 1],
            next_record=chain[index],
        )
        is True,
    )


check(
    "chain_first_is_root",
    chain[0].is_root_record,
)

check(
    "chain_rest_nonroot",
    all(
        not item.is_root_record
        for item
        in chain[1:]
    ),
)


# ============================================================
# 10. SKIPPED PREDECESSOR ATTACKS
# ============================================================

for previous_index in range(
    len(chain) - 2
):
    later_index = (
        previous_index + 2
    )

    try:
        evidence.validate_universal_orchestration_evidence_successor(
            previous_record=chain[previous_index],
            next_record=chain[later_index],
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "evidence_successor_link_mismatch"
        )
    else:
        rejected = False

    check(
        (
            "skipped_predecessor_"
            + str(previous_index)
            + "_"
            + str(later_index)
        ),
        rejected,
    )


# ============================================================
# 11. CROSS-RUN ATTACKS
# ============================================================

foreign = create(
    identity=B,
    kind="recovery",
    decision=D2,
    previous=chain[0].evidence_record_id,
)


try:
    evidence.validate_universal_orchestration_evidence_successor(
        previous_record=chain[0],
        next_record=foreign,
    )
except evidence.UniversalOrchestrationEvidenceError as exc:
    rejected = (
        exc.code
        ==
        "evidence_successor_identity_mismatch"
    )
else:
    rejected = False


check(
    "cross_run_successor_rejected",
    rejected,
)


foreign_root = create(
    identity=C,
    kind="completion",
    decision=D3,
)


try:
    evidence.validate_universal_orchestration_evidence_successor(
        previous_record=foreign_root,
        next_record=chain[1],
    )
except evidence.UniversalOrchestrationEvidenceError as exc:
    rejected = (
        exc.code
        ==
        "evidence_successor_identity_mismatch"
    )
else:
    rejected = False


check(
    "reverse_cross_run_rejected",
    rejected,
)


# ============================================================
# 12. INVALID SUCCESSOR OBJECTS
# ============================================================

bad_objects = (
    None,
    True,
    False,
    0,
    1,
    "",
    (),
    [],
    {},
    object(),
)


for index, bad in enumerate(
    bad_objects,
    start=1,
):
    try:
        evidence.validate_universal_orchestration_evidence_successor(
            previous_record=bad,
            next_record=chain[1],
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_previous_evidence_record"
        )
    else:
        rejected = False

    check(
        f"invalid_previous_object_{index}",
        rejected,
    )


for index, bad in enumerate(
    bad_objects,
    start=1,
):
    try:
        evidence.validate_universal_orchestration_evidence_successor(
            previous_record=chain[0],
            next_record=bad,
        )
    except evidence.UniversalOrchestrationEvidenceError as exc:
        rejected = (
            exc.code
            ==
            "invalid_next_evidence_record"
        )
    else:
        rejected = False

    check(
        f"invalid_next_object_{index}",
        rejected,
    )


# ============================================================
# 13. IMMUTABILITY
# ============================================================

for field in fields(
    chain[3]
):
    try:
        setattr(
            chain[3],
            field.name,
            None,
        )
    except Exception:
        immutable = True
    else:
        immutable = False

    check(
        "record_immutable_" + field.name,
        immutable,
    )


manifest = chain[3].manifest


check(
    "manifest_mappingproxy",
    isinstance(
        manifest,
        MappingProxyType,
    ),
)


try:
    manifest["decision_id"] = "0" * 64
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
# 14. MANIFEST CONSISTENCY
# ============================================================

for index, record in enumerate(
    chain,
    start=1,
):
    manifest = record.manifest

    check(
        f"manifest_id_{index}",
        manifest[
            "evidence_record_id"
        ]
        ==
        record.evidence_record_id,
    )

    check(
        f"manifest_previous_{index}",
        manifest[
            "previous_record_id"
        ]
        ==
        record.previous_record_id,
    )

    check(
        f"manifest_identity_{index}",
        manifest[
            "identity_fingerprint"
        ]
        ==
        record.identity_fingerprint,
    )

    check(
        f"manifest_kind_{index}",
        manifest[
            "decision_kind"
        ]
        ==
        record.decision_kind.value,
    )

    check(
        f"manifest_phase_{index}",
        manifest[
            "source_phase"
        ]
        ==
        record.source_phase,
    )

    check(
        f"manifest_decision_{index}",
        manifest[
            "decision_id"
        ]
        ==
        record.decision_id,
    )


# ============================================================
# 15. EXPLANATION CONTRACT
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
    explanation.get("phase")
    ==
    "5.1.17",
)

check(
    "component_exact",
    explanation.get("component")
    ==
    "Universal Orchestration Evidence & Decision Records",
)

check(
    "stored_fields_explanation_exact",
    explanation.get("stored_fields")
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
    "decision_kinds_explanation_exact",
    explanation.get("decision_kinds")
    ==
    (
        "suspension_resume_eligibility",
        "recovery",
        "completion",
        "cancellation_termination",
    ),
)


required_authorities = (
    "5.1.12 suspension/resume eligibility",
    "5.1.13 recovery",
    "5.1.15 completion resolution",
    "5.1.16 cancellation/termination resolution",
)


check(
    "decision_authorities_exact",
    explanation.get(
        "decision_authorities"
    )
    ==
    required_authorities,
)


# ============================================================
# 16. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not recompute suspension/resume eligibility",
    "does not recompute recovery",
    "does not recompute completion",
    "does not recompute cancellation/termination",
    "does not transition orchestration state",
    "does not mutate jobs",
    "does not execute recovery",
    "does not execute cancellation",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not manipulate workers",
    "does not manipulate leases",
    "does not dispatch handlers",
    "does not execute jobs",
    "does not duplicate state_snapshot",
    "does not duplicate progress_snapshot",
    "does not invoke 5.1.14 persistence port",
    "does not access Runtime State Store",
    "does not import Runtime Audit infrastructure",
    "does not implement an audit-log backend",
    "does not define a second persistence port",
    "does not use wall clock",
    "does not generate timestamps",
    "does not perform filesystem I/O",
    "does not perform database I/O",
    "does not perform network I/O",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
)


prohibitions = tuple(
    explanation.get("prohibitions")
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):
    check(
        f"prohibition_{index}",
        item
        in prohibitions,
        item,
    )


# ============================================================
# 17. IMPORT BOUNDARY
# ============================================================

source = EVIDENCE_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)


backend_imports = []


for node in ast.walk(tree):
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
# 18. FORBIDDEN IMPORTS
# ============================================================

all_imports = []


for node in ast.walk(tree):
    if isinstance(
        node,
        ast.Import,
    ):
        for alias in node.names:
            all_imports.append(
                alias.name
            )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):
        if node.module:
            all_imports.append(
                node.module
            )


for forbidden in (
    "time",
    "datetime",
    "uuid",
    "random",
    "asyncio",
    "threading",
    "multiprocessing",
    "os",
    "subprocess",
    "socket",
    "sqlite3",
    "backend.server.runtime.runtime_state_store",
    "backend.server.runtime.runtime_persistence",
    "backend.server.runtime.runtime_schema.audit",
    "backend.server.runtime.universal_orchestration.suspension_resume_eligibility",
    "backend.server.runtime.universal_orchestration.recovery",
    "backend.server.runtime.universal_orchestration.persistence_interface",
    "backend.server.runtime.universal_orchestration.completion_resolution",
    "backend.server.runtime.universal_orchestration.cancellation_termination",
    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",
    "backend.server.coordination",
    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):
    matches = tuple(
        item
        for item
        in all_imports
        if (
            item == forbidden
            or
            item.startswith(
                forbidden + "."
            )
        )
    )

    check(
        "forbidden_import_absent_"
        + forbidden.replace(".", "_"),
        not matches,
        matches,
    )


# ============================================================
# 19. FORBIDDEN CALLS
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


found_forbidden_calls = []


for node in ast.walk(tree):
    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    if isinstance(
        node.func,
        ast.Name,
    ):
        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        name = node.func.attr

    else:
        continue

    if name in forbidden_calls:
        found_forbidden_calls.append(
            (
                name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 20. FORBIDDEN ATTRIBUTES
# ============================================================

attributes = tuple(
    node.attr
    for node
    in ast.walk(tree)
    if isinstance(
        node,
        ast.Attribute,
    )
)


for forbidden_attr in (
    "created_at",
    "updated_at",
    "timestamp",
    "persisted_at",
    "state_snapshot",
    "progress_snapshot",
    "orchestration_state",
    "status_evidence",
    "worker_id",
    "lease_id",
    "attempt_count",
    "checkpoint_reference",
):
    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attributes,
    )


# ============================================================
# 21. NO PORT / BACKEND SYMBOLS
# ============================================================

names = {
    node.id
    for node
    in ast.walk(tree)
    if isinstance(
        node,
        ast.Name,
    )
}

defined_names = {
    node.name
    for node
    in ast.walk(tree)
    if isinstance(
        node,
        (
            ast.ClassDef,
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}


for forbidden_symbol in (
    "Protocol",
    "runtime_checkable",
    "PersistencePort",
    "AuditPort",
    "RuntimeStateStore",
    "RuntimePersistence",
    "AuditLog",
    "AuditRecord",
):
    check(
        "forbidden_symbol_absent_"
        + forbidden_symbol,
        (
            forbidden_symbol
            not in names
            and
            forbidden_symbol
            not in defined_names
        ),
    )


# ============================================================
# 22. PROTECTED AUTHORITIES
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():
    actual = ast_sha(path)

    check(
        "protected_" + name,
        actual == expected,
        actual,
    )


# ============================================================
# 23. FINAL AST
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

total = len(checks)


failures = tuple(
    (
        name,
        detail,
    )
    for name, ok, detail
    in checks
    if not ok
)


lines = [
    (
        "PHASE 5.1.17 — UNIVERSAL ORCHESTRATION "
        "EVIDENCE & DECISION RECORDS ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION EVIDENCE RECORDS AST SHA256: "
        + final_ast
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
            "   " + detail
        )


if failures:
    lines.extend(
        [
            "",
            "FAILURE SUMMARY",
            "-" * 118,
        ]
    )

    for name, detail in failures:
        lines.append(
            "FAIL: " + name
        )

        if detail:
            lines.append(
                "   " + detail
            )


lines.extend(
    [
        "",
        "=" * 118,

        (
            "ADVERSARIAL ORCHESTRATION EVIDENCE & DECISION RECORDS REGRESSION: "
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

        "5.1.17 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.16 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "CANONICAL DECISION KINDS: 4",
        "IMMUTABLE RECORDS: YES",
        "DETERMINISTIC RECORD IDS: YES",
        "PREDECESSOR-BASED APPEND-ONLY LINEAGE: YES",

        "",

        "ROOT RECORD PREDECESSOR: NONE",
        "CROSS-RUN LINEAGE: REJECTED",
        "SKIPPED PREDECESSOR: REJECTED",

        "",

        "IDENTITY-FINGERPRINT SENSITIVE: YES",
        "DECISION-KIND SENSITIVE: YES",
        "DECISION-ID SENSITIVE: YES",
        "PREDECESSOR SENSITIVE: YES",

        "",

        "STATE SNAPSHOT STORED: NO",
        "PROGRESS SNAPSHOT STORED: NO",
        "TIMESTAMPS STORED: NO",

        "",

        "5.1.12 IMPORTED: NO",
        "5.1.13 IMPORTED: NO",
        "5.1.14 IMPORTED: NO",
        "5.1.15 IMPORTED: NO",
        "5.1.16 IMPORTED: NO",

        "",

        "UPSTREAM DECISIONS RECOMPUTED: NO",
        "ORCHESTRATION STATE TRANSITION: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "RUNTIME PERSISTENCE ACCESS: NO",
        "RUNTIME AUDIT INFRASTRUCTURE ACCESS: NO",
        "SECOND PERSISTENCE PORT: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "WALL CLOCK: NO",
        "FILESYSTEM I/O: NO",
        "DATABASE I/O: NO",
        "NETWORK I/O: NO",

        "",

        (
            "STATUS: REGRESSION PASS — FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED — INVESTIGATE BEFORE PATCHING PRODUCTION"
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:
    raise SystemExit(
        "Phase 5.1.17 adversarial regression failed."
    )
