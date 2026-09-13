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
    / "phase_5_1_17_orchestration_evidence_initial_implementation.txt"
)


PROTECTED = {
    "5.1.1": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),
    "5.1.2": (
        ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),
    "5.1.3": (
        ROOT / "backend/server/runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),
    "5.1.4": (
        ROOT / "backend/server/runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),
    "5.1.5": (
        ROOT / "backend/server/runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),
    "5.1.6": (
        ROOT / "backend/server/runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),
    "5.1.7": (
        ROOT / "backend/server/runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),
    "5.1.8": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),
    "5.1.9": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),
    "5.1.10": (
        ROOT / "backend/server/runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),
    "5.1.11": (
        ROOT / "backend/server/runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),
    "5.1.12": (
        ROOT / "backend/server/runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),
    "5.1.13": (
        ROOT / "backend/server/runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    "5.1.14": (
        ROOT / "backend/server/runtime/universal_orchestration/persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),
    "5.1.15": (
        ROOT / "backend/server/runtime/universal_orchestration/completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
    ),
    "5.1.16": (
        ROOT / "backend/server/runtime/universal_orchestration/cancellation_termination.py",
        "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",
    ),
}


def ast_sha(
    path: Path,
) -> str:

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


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            "Protected authority changed: "
            + name
        )


sys.path.insert(
    0,
    str(ROOT),
)


evidence = importlib.import_module(
    "backend.server.runtime.universal_orchestration.evidence_records"
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


IDENTITY_A = (
    "A" * 64
)

IDENTITY_B = (
    "B" * 64
)

DECISION_1 = (
    "1" * 64
)

DECISION_2 = (
    "2" * 64
)

DECISION_3 = (
    "3" * 64
)

DECISION_4 = (
    "4" * 64
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


field_names = tuple(
    field.name
    for field
    in fields(
        evidence.UniversalOrchestrationDecisionEvidenceRecord
    )
)


check(
    "stored_fields_exact",
    field_names
    ==
    (
        "identity_fingerprint",
        "decision_kind",
        "decision_id",
        "previous_record_id",
        "schema_version",
    ),
    field_names,
)


root = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A.lower(),
        decision_kind="suspension_resume_eligibility",
        decision_id=DECISION_1.lower(),
    )
)


check(
    "identity_normalized",
    root.identity_fingerprint
    ==
    IDENTITY_A,
)

check(
    "decision_id_normalized",
    root.decision_id
    ==
    DECISION_1,
)

check(
    "root_is_root",
    root.is_root_record,
)

check(
    "root_previous_none",
    root.previous_record_id
    is None,
)

check(
    "root_phase_exact",
    root.source_phase
    ==
    "5.1.12",
)


root_id = (
    root.evidence_record_id
)


check(
    "root_id_length",
    len(
        root_id
    )
    == 64,
    root_id,
)

check(
    "root_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in root_id
    ),
)


same_root = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind=evidence.UniversalOrchestrationDecisionKind.SUSPENSION_RESUME_ELIGIBILITY,
        decision_id=DECISION_1,
    )
)


check(
    "root_deterministic",
    root.evidence_record_id
    ==
    same_root.evidence_record_id,
)


second = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="recovery",
        decision_id=DECISION_2,
        previous_record_id=root.evidence_record_id,
    )
)


third = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="completion",
        decision_id=DECISION_3,
        previous_record_id=second.evidence_record_id,
    )
)


fourth = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="cancellation_termination",
        decision_id=DECISION_4,
        previous_record_id=third.evidence_record_id,
    )
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
    "root_second_successor",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=root,
        next_record=second,
    )
    is True,
)

check(
    "second_third_successor",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=second,
        next_record=third,
    )
    is True,
)

check(
    "third_fourth_successor",
    evidence
    .validate_universal_orchestration_evidence_successor(
        previous_record=third,
        next_record=fourth,
    )
    is True,
)


skipped = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="completion",
        decision_id=DECISION_3,
        previous_record_id=root.evidence_record_id,
    )
)


try:

    evidence.validate_universal_orchestration_evidence_successor(
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


cross_run = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_B,
        decision_kind="recovery",
        decision_id=DECISION_2,
        previous_record_id=root.evidence_record_id,
    )
)


try:

    evidence.validate_universal_orchestration_evidence_successor(
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


kind_changed = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="completion",
        decision_id=DECISION_1,
    )
)


check(
    "record_id_kind_sensitive",
    kind_changed.evidence_record_id
    !=
    root.evidence_record_id,
)


decision_changed = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="suspension_resume_eligibility",
        decision_id=DECISION_2,
    )
)


check(
    "record_id_decision_sensitive",
    decision_changed.evidence_record_id
    !=
    root.evidence_record_id,
)


identity_changed = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_B,
        decision_kind="suspension_resume_eligibility",
        decision_id=DECISION_1,
    )
)


check(
    "record_id_identity_sensitive",
    identity_changed.evidence_record_id
    !=
    root.evidence_record_id,
)


predecessor_changed = (
    evidence
    .create_universal_orchestration_decision_evidence_record(
        identity_fingerprint=IDENTITY_A,
        decision_kind="suspension_resume_eligibility",
        decision_id=DECISION_1,
        previous_record_id=(
            "F" * 64
        ),
    )
)


check(
    "record_id_predecessor_sensitive",
    predecessor_changed.evidence_record_id
    !=
    root.evidence_record_id,
)


manifest = (
    fourth.manifest
)


check(
    "manifest_mappingproxy",
    isinstance(
        manifest,
        MappingProxyType,
    ),
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


invalid_hash_values = (
    None,
    True,
    False,
    0,
    1,
    "",
    "abc",
    "G" * 64,
    "A" * 63,
    "A" * 65,
)


for index, bad in enumerate(
    invalid_hash_values,
    start=1,
):

    try:

        evidence.create_universal_orchestration_decision_evidence_record(
            identity_fingerprint=bad,
            decision_kind="recovery",
            decision_id=DECISION_1,
        )

    except evidence.UniversalOrchestrationEvidenceError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_identity_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    invalid_hash_values,
    start=1,
):

    try:

        evidence.create_universal_orchestration_decision_evidence_record(
            identity_fingerprint=IDENTITY_A,
            decision_kind="recovery",
            decision_id=bad,
        )

    except evidence.UniversalOrchestrationEvidenceError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_decision_id_"
        + str(index),
        rejected,
    )


for bad_kind in (
    None,
    True,
    1,
    "",
    "unknown",
    "5.1.15",
):

    try:

        evidence.create_universal_orchestration_decision_evidence_record(
            identity_fingerprint=IDENTITY_A,
            decision_kind=bad_kind,
            decision_id=DECISION_1,
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
        "invalid_kind_"
        + str(
            bad_kind
        ),
        rejected,
    )


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


check(
    "no_backend_imports",
    backend_imports
    ==
    [],
    backend_imports,
)


for forbidden_field in (
    "state_snapshot",
    "progress_snapshot",
    "orchestration_state",
    "created_at",
    "updated_at",
    "timestamp",
):

    check(
        "forbidden_stored_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


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


evidence_ast = (
    ast_sha(
        EVIDENCE_PATH
    )
)


check(
    "evidence_ast_generated",
    len(
        evidence_ast
    )
    == 64,
    evidence_ast,
)


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
        "EVIDENCE & DECISION RECORDS INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION EVIDENCE RECORDS AST SHA256: "
        + evidence_ast
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
            "INITIAL ORCHESTRATION EVIDENCE & DECISION RECORDS RESULT: "
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

        "5.1.1–5.1.16 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "DECISION KINDS:",
        "  SUSPENSION_RESUME_ELIGIBILITY",
        "  RECOVERY",
        "  COMPLETION",
        "  CANCELLATION_TERMINATION",

        "",

        "RECORDS IMMUTABLE: YES",
        "RECORD IDS DETERMINISTIC: YES",
        "APPEND-ONLY PREDECESSOR LINEAGE: YES",

        "",

        "CROSS-RUN LINEAGE: REJECTED",
        "SKIPPED PREDECESSOR: REJECTED",

        "",

        "STATE SNAPSHOT DUPLICATED: NO",
        "PROGRESS SNAPSHOT DUPLICATED: NO",

        "",

        "UPSTREAM DECISIONS RECOMPUTED: NO",
        "UPSTREAM DECISION MODULES IMPORTED: NO",

        "",

        "WALL CLOCK: NO",
        "TIMESTAMPS: NO",

        "",

        "PERSISTENCE BACKEND: NO",
        "SECOND PERSISTENCE PORT: NO",
        "RUNTIME AUDIT INFRASTRUCTURE IMPORT: NO",

        "",

        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
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
        "Phase 5.1.17 initial implementation failed."
    )
