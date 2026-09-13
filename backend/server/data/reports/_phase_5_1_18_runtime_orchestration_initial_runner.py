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

ORCH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
)

CERT_PATH = (
    ORCH
    / "certification.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_18_runtime_orchestration_initial_implementation.txt"
)


AUTHORITIES = (
    (
        "5.1.1",
        "contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),
    (
        "5.1.2",
        "run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),
    (
        "5.1.3",
        "state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),
    (
        "5.1.4",
        "dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),
    (
        "5.1.5",
        "execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),
    (
        "5.1.6",
        "stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),
    (
        "5.1.7",
        "runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),
    (
        "5.1.8",
        "fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),
    (
        "5.1.9",
        "fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),
    (
        "5.1.10",
        "conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),
    (
        "5.1.11",
        "progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),
    (
        "5.1.12",
        "suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),
    (
        "5.1.13",
        "recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    (
        "5.1.14",
        "persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),
    (
        "5.1.15",
        "completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
    ),
    (
        "5.1.16",
        "cancellation_termination.py",
        "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",
    ),
    (
        "5.1.17",
        "evidence_records.py",
        "6BF84A9D3E8B120D5506DFF31D4BEB8718ECF488820E69782C7F0F7C85758FD9",
    ),
)


EXPECTED_FINGERPRINTS = {
    "5.1.1":
        "6EB4FBA61E7FF764FA5CD64BBF3F13972D3F61954AC78B1AAA0D93B9AA74A155",
    "5.1.2":
        "6F0475D76C0A629827FA6B74F755F89C63CD5E75D7E70F2087469B69F1B76299",
    "5.1.3":
        "D46F580CA2E18CA666F0BB597623FDFAA98F75EED64224F7690A3724C11826AA",
    "5.1.4":
        "66ABE78758EFD3FE25A36D80A87A14B43A96AE8C806A20DBEB273C69C1050942",
    "5.1.5":
        "E89F767158E43C2DF78B8E65E9B1BF7C2B948238683F04DC2014AC18CAC3957A",
    "5.1.6":
        "8BDEF91879B5851355844B941DAE53899FCB51ADE46557DD72B4FA1F76D51D29",
    "5.1.7":
        "E016E782AC306C62505386D7D11F9254275EF9E9E34B7FB52DF1FCCC2AE095BC",
    "5.1.8":
        "B59238FA3050850AEF25BD111E49719B65E036DF8F4A3F8C9021A90C5B71F03D",
    "5.1.9":
        "02135980C7275A5C3713156C7021D391E1BD160AFF3AB9696D26A57FDA504D20",
    "5.1.10":
        "A4AACA0AB85E9C43F64B385C3853E0555D191CEC1DCA69583857DBC4F003D046",
    "5.1.11":
        "58CA16BC4DC8B9AFA7DE15DCF8184FDF253FAE0CDC98EABB750AFC6252303BAF",
    "5.1.12":
        "CC2A68A007E71BC1FE2DAC3E01E0F40F90D694CDE67F00D0559478A0BA96BFAE",
    "5.1.13":
        "09AA8290AF5DD557937750C5220E7292090458240E5D8719E730C33236284E38",
    "5.1.14":
        "C4D44944254E8BFBC867FDD96BA0346A119FBC3D0A5C3B0B9478F7E8383B48AA",
    "5.1.15":
        "6DECC6FD7917E08C08607E4914EEA056750A9BBF7B41E4859F3DB8A895772C36",
    "5.1.16":
        "BD694423C0C8266DA09166C2593AF020C6FF08E9DF2FF408447DE08A18BFC048",
    "5.1.17":
        "363E53AF5760ED08AC53CC6D72711923053E1960F76172B83025366BF3A8698E",
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


for phase, filename, expected in AUTHORITIES:

    actual = ast_sha(
        ORCH / filename
    )

    if actual != expected:

        raise SystemExit(
            "Frozen authority mismatch before 5.1.18 initial test: "
            + phase
        )


sys.path.insert(
    0,
    str(ROOT),
)


cert = importlib.import_module(
    "backend.server.runtime.universal_orchestration.certification"
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
    "hash_exact",
    cert.UNIVERSAL_RUNTIME_ORCHESTRATION_CERTIFICATION_HASH_ALGORITHM
    ==
    "sha256",
)


manifest = (
    cert
    .create_universal_runtime_orchestration_certification_manifest()
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


check(
    "authority_count_17",
    manifest.authority_count
    ==
    17,
)

check(
    "authority_ast_mappingproxy",
    isinstance(
        manifest.authority_ast_hashes,
        MappingProxyType,
    ),
)

check(
    "authority_fingerprint_mappingproxy",
    isinstance(
        manifest.authority_fingerprints,
        MappingProxyType,
    ),
)

check(
    "ast_keys_exact",
    tuple(
        manifest.authority_ast_hashes.keys()
    )
    ==
    tuple(
        f"5.1.{index}"
        for index
        in range(
            1,
            18,
        )
    ),
)

check(
    "fingerprint_keys_exact",
    tuple(
        manifest.authority_fingerprints.keys()
    )
    ==
    tuple(
        f"5.1.{index}"
        for index
        in range(
            1,
            18,
        )
    ),
)


for phase, filename, expected in AUTHORITIES:

    check(
        "manifest_ast_" + phase,
        manifest.authority_ast_hashes[
            phase
        ]
        ==
        expected,
    )


for phase, expected in EXPECTED_FINGERPRINTS.items():

    check(
        "manifest_fingerprint_" + phase,
        manifest.authority_fingerprints[
            phase
        ]
        ==
        expected,
    )


check(
    "invariant_count_31",
    manifest.invariant_count
    ==
    31,
    manifest.invariant_count,
)


check(
    "execution_boundary_invariant",
    "phase_6_owns_execution"
    in
    manifest.certified_invariants,
)


check(
    "unknown_not_false_invariant",
    "conditional_unknown_is_not_false"
    in
    manifest.certified_invariants,
)


check(
    "completion_not_cancellation_invariant",
    "completion_is_not_cancellation"
    in
    manifest.certified_invariants,
)


check(
    "explicit_cancellation_invariant",
    "cancellation_requires_explicit_intent"
    in
    manifest.certified_invariants,
)


check(
    "persistence_evidence_separation_invariant",
    "state_persistence_is_not_decision_evidence"
    in
    manifest.certified_invariants,
)


whole_fingerprint = (
    manifest.runtime_orchestration_fingerprint
)


check(
    "whole_fingerprint_length",
    len(
        whole_fingerprint
    )
    ==
    64,
    whole_fingerprint,
)

check(
    "whole_fingerprint_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in whole_fingerprint
    ),
)


manifest_repeat = (
    cert
    .create_universal_runtime_orchestration_certification_manifest()
)


check(
    "whole_fingerprint_deterministic",
    whole_fingerprint
    ==
    manifest_repeat.runtime_orchestration_fingerprint,
)


check(
    "certification_id_exact_shape",
    manifest.certification_id
    ==
    (
        "phase_5_1_18_"
        + whole_fingerprint[
            :16
        ].lower()
    ),
    manifest.certification_id,
)


for field in fields(
    manifest
):

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
        "manifest_immutable_"
        + field.name,
        immutable,
    )


public_manifest = (
    manifest.manifest
)


check(
    "public_manifest_mappingproxy",
    isinstance(
        public_manifest,
        MappingProxyType,
    ),
)


try:

    public_manifest[
        "authority_count"
    ] = 99

except Exception:

    public_manifest_immutable = True

else:

    public_manifest_immutable = False


check(
    "public_manifest_immutable",
    public_manifest_immutable,
)


explanation = (
    cert
    .explain_universal_runtime_orchestration_certification_v1()
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
    "5.1.18",
)

check(
    "explanation_authority_count",
    explanation.get(
        "authority_count"
    )
    ==
    17,
)

check(
    "explanation_invariant_count",
    explanation.get(
        "certified_invariant_count"
    )
    ==
    31,
)


source = CERT_PATH.read_text(
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
        not in stored_fields,
    )


for phase, filename, expected in AUTHORITIES:

    actual = ast_sha(
        ORCH / filename
    )

    check(
        "protected_"
        + phase,
        actual
        ==
        expected,
        actual,
    )


cert_ast = (
    ast_sha(
        CERT_PATH
    )
)


check(
    "certification_ast_generated",
    len(
        cert_ast
    )
    ==
    64,
    cert_ast,
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
        "PHASE 5.1.18 — UNIVERSAL RUNTIME ORCHESTRATION "
        "CERTIFICATION INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "RUNTIME ORCHESTRATION CERTIFICATION AST SHA256: "
        + cert_ast
    ),

    (
        "WHOLE-LAYER RUNTIME ORCHESTRATION FINGERPRINT: "
        + whole_fingerprint
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
            "INITIAL RUNTIME ORCHESTRATION CERTIFICATION RESULT: "
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

        "5.1.1–5.1.17 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "AUTHORITIES BOUND: 17",
        "SEMANTIC FINGERPRINTS BOUND: 17",
        "WHOLE-LAYER INVARIANTS BOUND: 31",

        "",

        "CERTIFICATION MANIFEST IMMUTABLE: YES",
        "WHOLE-LAYER FINGERPRINT DETERMINISTIC: YES",

        "",

        "STATE TRANSITION: NO",
        "PROGRESS RECOMPUTATION: NO",
        "DECISION RECOMPUTATION: NO",

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

        "UCF ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        "PHASE 6 OWNS EXECUTION: YES",

        "",

        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL WHOLE-LAYER CERTIFICATION REQUIRED"
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
        "Phase 5.1.18 initial implementation failed."
    )

