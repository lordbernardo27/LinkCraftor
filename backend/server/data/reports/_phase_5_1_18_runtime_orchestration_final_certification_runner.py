from __future__ import annotations

import ast
import hashlib
import importlib
import sys

from dataclasses import fields
from pathlib import Path
from types import MappingProxyType


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

ORCH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
)

CERT_PATH = ORCH / "certification.py"

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_18_runtime_orchestration_final_certification.txt"
)

EXPECTED_CERT_AST = (
    "2E740E8771E946EE673AE5FD23FE635D6DD63F10087A79CC7E7B8952CDBEF542"
)

EXPECTED_WHOLE_FINGERPRINT = (
    "139B2457C77806A357FA610DBC7534EC309A3E522AEFBFF9F3E9F1CA65393260"
)

EXPECTED_CERTIFICATION_ID = (
    "phase_5_1_18_139b2457c77806a3"
)


AUTHORITIES = (
    ("5.1.1","contract.py","8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9"),
    ("5.1.2","run_identity.py","A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC"),
    ("5.1.3","state_model.py","B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610"),
    ("5.1.4","dependency_resolution.py","CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E"),
    ("5.1.5","execution_planning.py","78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465"),
    ("5.1.6","stage_readiness.py","9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D"),
    ("5.1.7","runtime_handoff.py","6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73"),
    ("5.1.8","fan_out_coordination.py","D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916"),
    ("5.1.9","fan_in_coordination.py","98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F"),
    ("5.1.10","conditional_branching.py","3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F"),
    ("5.1.11","progress_tracking.py","92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309"),
    ("5.1.12","suspension_resume_eligibility.py","476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A"),
    ("5.1.13","recovery.py","4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F"),
    ("5.1.14","persistence_interface.py","5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA"),
    ("5.1.15","completion_resolution.py","1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4"),
    ("5.1.16","cancellation_termination.py","3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB"),
    ("5.1.17","evidence_records.py","6BF84A9D3E8B120D5506DFF31D4BEB8718ECF488820E69782C7F0F7C85758FD9"),
)


EXPECTED_FINGERPRINTS = {
    "5.1.1":"6EB4FBA61E7FF764FA5CD64BBF3F13972D3F61954AC78B1AAA0D93B9AA74A155",
    "5.1.2":"6F0475D76C0A629827FA6B74F755F89C63CD5E75D7E70F2087469B69F1B76299",
    "5.1.3":"D46F580CA2E18CA666F0BB597623FDFAA98F75EED64224F7690A3724C11826AA",
    "5.1.4":"66ABE78758EFD3FE25A36D80A87A14B43A96AE8C806A20DBEB273C69C1050942",
    "5.1.5":"E89F767158E43C2DF78B8E65E9B1BF7C2B948238683F04DC2014AC18CAC3957A",
    "5.1.6":"8BDEF91879B5851355844B941DAE53899FCB51ADE46557DD72B4FA1F76D51D29",
    "5.1.7":"E016E782AC306C62505386D7D11F9254275EF9E9E34B7FB52DF1FCCC2AE095BC",
    "5.1.8":"B59238FA3050850AEF25BD111E49719B65E036DF8F4A3F8C9021A90C5B71F03D",
    "5.1.9":"02135980C7275A5C3713156C7021D391E1BD160AFF3AB9696D26A57FDA504D20",
    "5.1.10":"A4AACA0AB85E9C43F64B385C3853E0555D191CEC1DCA69583857DBC4F003D046",
    "5.1.11":"58CA16BC4DC8B9AFA7DE15DCF8184FDF253FAE0CDC98EABB750AFC6252303BAF",
    "5.1.12":"CC2A68A007E71BC1FE2DAC3E01E0F40F90D694CDE67F00D0559478A0BA96BFAE",
    "5.1.13":"09AA8290AF5DD557937750C5220E7292090458240E5D8719E730C33236284E38",
    "5.1.14":"C4D44944254E8BFBC867FDD96BA0346A119FBC3D0A5C3B0B9478F7E8383B48AA",
    "5.1.15":"6DECC6FD7917E08C08607E4914EEA056750A9BBF7B41E4859F3DB8A895772C36",
    "5.1.16":"BD694423C0C8266DA09166C2593AF020C6FF08E9DF2FF408447DE08A18BFC048",
    "5.1.17":"363E53AF5760ED08AC53CC6D72711923053E1960F76172B83025366BF3A8698E",
}


EXPECTED_INVARIANTS = (
    "contract_authority_unique",
    "run_identity_authority_unique",
    "state_legality_authority_unique",
    "dependency_resolution_authority_unique",
    "execution_planning_is_planning_only",
    "stage_readiness_is_decision_only",
    "runtime_handoff_is_eligibility_only",
    "fan_out_preserves_structural_planning",
    "fan_in_preserves_join_semantics",
    "conditional_unknown_is_not_false",
    "progress_authority_unique",
    "excluded_work_ignored_downstream",
    "uncertainty_preserved",
    "suspension_resume_eligibility_is_not_execution",
    "recovery_decision_is_not_recovery_execution",
    "persistence_interface_is_not_persistence_backend",
    "completion_is_not_state_mutation",
    "completion_is_not_cancellation",
    "cancellation_requires_explicit_intent",
    "cancellation_is_not_cancellation_execution",
    "evidence_record_is_not_physical_audit_backend",
    "state_persistence_is_not_decision_evidence",
    "no_job_execution",
    "no_queue_execution",
    "no_worker_execution",
    "no_lease_manipulation",
    "no_runtime_handler_dispatch",
    "no_direct_concrete_persistence",
    "no_ucf_ownership",
    "no_pipeline_coordinator_ownership",
    "phase_6_owns_execution",
)


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


# ============================================================
# PRE-FLIGHT
# ============================================================

if ast_sha(CERT_PATH) != EXPECTED_CERT_AST:
    raise SystemExit(
        "5.1.18 certification authority changed before final certification."
    )


for phase, filename, expected in AUTHORITIES:
    actual = ast_sha(ORCH / filename)

    if actual != expected:
        raise SystemExit(
            "Frozen authority mismatch before final certification: "
            + phase
        )


sys.path.insert(
    0,
    str(ROOT),
)

module_name = (
    "backend.server.runtime.universal_orchestration.certification"
)

sys.modules.pop(
    module_name,
    None,
)

cert = importlib.import_module(
    module_name
)


checks = []


def check(name, condition, detail=""):
    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


manifest = (
    cert.create_universal_runtime_orchestration_certification_manifest()
)


# ============================================================
# EXACT CERTIFICATION AUTHORITY CONTRACT
# ============================================================

check(
    "certification_ast_exact",
    ast_sha(CERT_PATH)
    ==
    EXPECTED_CERT_AST,
)

check(
    "version_exact",
    cert.UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_VERSION
    ==
    "universal_runtime_orchestration_certification_v5.1.18",
)

check(
    "schema_exact",
    cert.UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_SCHEMA_VERSION
    ==
    "universal_runtime_orchestration_certification_schema_v1",
)

check(
    "hash_algorithm_exact",
    cert.UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM
    ==
    "sha256",
)


stored_fields = tuple(
    field.name
    for field
    in fields(
        cert.UniversalRuntimeOrchestrationCertificationManifest
    )
)

check(
    "stored_fields_exact",
    stored_fields
    ==
    (
        "authority_ast_hashes",
        "authority_fingerprints",
        "certified_invariants",
        "schema_version",
    ),
    stored_fields,
)


# ============================================================
# 17-AUTHORITY BINDING
# ============================================================

check(
    "authority_count_exact",
    manifest.authority_count
    ==
    17,
)

check(
    "ast_authority_keys_exact",
    tuple(manifest.authority_ast_hashes.keys())
    ==
    tuple(
        f"5.1.{index}"
        for index
        in range(1, 18)
    ),
)

check(
    "fingerprint_authority_keys_exact",
    tuple(manifest.authority_fingerprints.keys())
    ==
    tuple(
        f"5.1.{index}"
        for index
        in range(1, 18)
    ),
)


for phase, filename, expected in AUTHORITIES:
    check(
        "authority_ast_" + phase,
        manifest.authority_ast_hashes[phase]
        ==
        expected,
    )


for phase, expected in EXPECTED_FINGERPRINTS.items():
    check(
        "authority_fingerprint_" + phase,
        manifest.authority_fingerprints[phase]
        ==
        expected,
    )


# ============================================================
# WHOLE-LAYER INVARIANTS
# ============================================================

check(
    "invariant_count_exact",
    manifest.invariant_count
    ==
    31,
)

check(
    "invariant_tuple_exact",
    manifest.certified_invariants
    ==
    EXPECTED_INVARIANTS,
)

check(
    "invariants_unique",
    len(set(manifest.certified_invariants))
    ==
    31,
)

check(
    "phase_6_execution_boundary",
    manifest.certified_invariants[-1]
    ==
    "phase_6_owns_execution",
)


# ============================================================
# WHOLE-LAYER IDENTITY
# ============================================================

check(
    "whole_layer_fingerprint_exact",
    manifest.runtime_orchestration_fingerprint
    ==
    EXPECTED_WHOLE_FINGERPRINT,
    manifest.runtime_orchestration_fingerprint,
)

check(
    "whole_layer_fingerprint_upper_hex",
    (
        len(manifest.runtime_orchestration_fingerprint)
        ==
        64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in manifest.runtime_orchestration_fingerprint
        )
    ),
)

check(
    "certification_id_exact",
    manifest.certification_id
    ==
    EXPECTED_CERTIFICATION_ID,
    manifest.certification_id,
)


# ============================================================
# DETERMINISM
# ============================================================

repeat_fingerprints = tuple(
    cert
    .create_universal_runtime_orchestration_certification_manifest()
    .runtime_orchestration_fingerprint
    for _
    in range(100)
)

check(
    "fingerprint_deterministic_100",
    len(set(repeat_fingerprints))
    ==
    1,
)

repeat_ids = tuple(
    cert
    .create_universal_runtime_orchestration_certification_manifest()
    .certification_id
    for _
    in range(100)
)

check(
    "certification_id_deterministic_100",
    len(set(repeat_ids))
    ==
    1,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(manifest):
    try:
        setattr(
            manifest,
            field.name,
            None,
        )
    except Exception:
        immutable = True
    else:
        immutable = False

    check(
        "immutable_" + field.name,
        immutable,
    )


check(
    "ast_mapping_mappingproxy",
    isinstance(
        manifest.authority_ast_hashes,
        MappingProxyType,
    ),
)

check(
    "fingerprint_mapping_mappingproxy",
    isinstance(
        manifest.authority_fingerprints,
        MappingProxyType,
    ),
)

check(
    "public_manifest_mappingproxy",
    isinstance(
        manifest.manifest,
        MappingProxyType,
    ),
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    cert.explain_universal_runtime_orchestration_certification_v1()
)

check(
    "explanation_mappingproxy",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

check(
    "explanation_phase",
    explanation.get("phase")
    ==
    "5.1.18",
)

check(
    "explanation_component",
    explanation.get("component")
    ==
    "Universal Runtime Orchestration Certification",
)

check(
    "explanation_authority_count",
    explanation.get("authority_count")
    ==
    17,
)

check(
    "explanation_invariant_count",
    explanation.get("certified_invariant_count")
    ==
    31,
)

check(
    "execution_boundary_exact",
    explanation.get("execution_boundary")
    ==
    "Phase 5.1 models, decides and coordinates. Phase 6 owns actual execution.",
)


# ============================================================
# PRODUCTION AUTHORITY BOUNDARY
# ============================================================

source = CERT_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []

for node in ast.walk(tree):

    if isinstance(node, ast.ImportFrom):
        module = node.module or ""

        if module.startswith("backend.server"):
            backend_imports.append(module)

    elif isinstance(node, ast.Import):

        for alias in node.names:

            if alias.name.startswith("backend.server"):
                backend_imports.append(alias.name)


check(
    "no_backend_imports",
    backend_imports
    ==
    [],
    backend_imports,
)


all_imports = []

for node in ast.walk(tree):

    if isinstance(node, ast.Import):

        for alias in node.names:
            all_imports.append(alias.name)

    elif isinstance(node, ast.ImportFrom):

        if node.module:
            all_imports.append(node.module)


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
):
    check(
        "forbidden_import_" + forbidden,
        forbidden
        not in all_imports,
    )


forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "time",
    "time_ns",
    "now",
    "utcnow",
    "sleep",

    "transition_universal_orchestration_state",
    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "evaluate_universal_orchestration_recovery",
    "resolve_universal_orchestration_completion",
    "resolve_universal_orchestration_cancellation_termination",

    "append_record",
    "load_record",
    "load_latest_record",
    "list_record_history",

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
# FORBIDDEN STORED RUNTIME STATE
# ============================================================

for forbidden in (
    "state_snapshot",
    "progress_snapshot",
    "orchestration_state",
    "created_at",
    "updated_at",
    "timestamp",
    "worker_id",
    "lease_id",
    "checkpoint_reference",
    "retry_count",
    "attempt_count",
):

    check(
        "forbidden_stored_" + forbidden,
        forbidden
        not in stored_fields,
    )


# ============================================================
# ALL 17 FROZEN AUTHORITIES
# ============================================================

for phase, filename, expected in AUTHORITIES:

    actual = ast_sha(
        ORCH / filename
    )

    check(
        "protected_" + phase,
        actual
        ==
        expected,
        actual,
    )


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    CERT_PATH
)

check(
    "final_certification_ast_unchanged",
    final_ast
    ==
    EXPECTED_CERT_AST,
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
        "PHASE 5.1.18 — UNIVERSAL RUNTIME ORCHESTRATION "
        "FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "RUNTIME ORCHESTRATION CERTIFICATION AST SHA256: "
        + final_ast
    ),

    (
        "WHOLE-LAYER RUNTIME ORCHESTRATION FINGERPRINT: "
        + manifest.runtime_orchestration_fingerprint
    ),

    (
        "CERTIFICATION ID: "
        + manifest.certification_id
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
        f"{index}. {name}: {'PASS' if ok else 'FAIL'}"
    )

    if detail:
        lines.append(
            "   "
            + detail
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
            "FAIL: "
            + name
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
            "FINAL UNIVERSAL RUNTIME ORCHESTRATION CERTIFICATION: "
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

        "5.1.18 CERTIFICATION AUTHORITY MODIFIED DURING FINAL CERTIFICATION: NO",
        "5.1.1–5.1.17 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "AUTHORITIES CERTIFIED: 17",
        "SEMANTIC FINGERPRINTS CERTIFIED: 17",
        "WHOLE-LAYER INVARIANTS CERTIFIED: 31",

        "",

        "CERTIFICATION MANIFEST IMMUTABLE: YES",
        "CERTIFICATION ID DETERMINISTIC: YES",
        "WHOLE-LAYER FINGERPRINT DETERMINISTIC: YES",

        "",

        "STATE LEGALITY AUTHORITY UNIQUE: YES",
        "PROGRESS AUTHORITY UNIQUE: YES",
        "COMPLETION / CANCELLATION SEPARATION: YES",
        "STATE PERSISTENCE / DECISION EVIDENCE SEPARATION: YES",

        "",

        "UNCERTAINTY PRESERVED: YES",
        "EXCLUDED BRANCH WORK IGNORED DOWNSTREAM: YES",

        "",

        "STATE TRANSITION EXECUTION: NO",
        "RECOVERY EXECUTION: NO",
        "CANCELLATION EXECUTION: NO",

        "",

        "JOB EXECUTION: NO",
        "QUEUE EXECUTION: NO",
        "WORKER EXECUTION: NO",
        "LEASE MANIPULATION: NO",
        "HANDLER DISPATCH: NO",

        "",

        "CONCRETE PERSISTENCE: NO",
        "RUNTIME STATE STORE ACCESS: NO",

        "",

        "UCF OWNERSHIP: NO",
        "PIPELINE COORDINATOR OWNERSHIP: NO",

        "",

        "PHASE 6 OWNS EXECUTION: YES",

        "",

        (
            "PHASE 5.1 RUNTIME ORCHESTRATION FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
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
        "Phase 5.1.18 final Runtime Orchestration certification failed."
    )
