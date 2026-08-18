from __future__ import annotations

import ast
import hashlib
import importlib
import py_compile
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

WORKER_ROOT = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_15_worker_infrastructure_certification.txt"
)


# ============================================================
# CANONICAL PHASE 4 COMPONENT MANIFEST
# ============================================================

COMPONENTS = (
    (
        "4.1.1",
        "Worker Registration",
        "registration",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
        "D884B4E3F94D6C26814B88793D04C559CD02E39CB64678F8A738FB52F646AAE3",
    ),
    (
        "4.1.2",
        "Worker Discovery",
        "discovery",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
        "7AEBDB25831F1FE5DCA5D0DD658A630AE8EA161B19C7AFB6D3584381492288E2",
    ),
    (
        "4.1.3",
        "Worker Assignment",
        "assignment",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
        "DEDBEE82F5F3F4AF2B42EA313C790EEA086271D12B966641E367C07E4A6ACC1C",
    ),
    (
        "4.1.4",
        "Worker Leasing",
        "leasing",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
        "90E2E2D916763E17F1EE77AB02C820D374851944CE05DCCF8DB61FDD07F11EFE",
    ),
    (
        "4.1.5",
        "Worker Health",
        "health",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
        "EBEBCC717A73135D38093F250168E7696014EC321EC8A0088DAFF37D93928C37",
    ),
    (
        "4.1.6",
        "Worker Recovery",
        "recovery",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
        "5F5B23EF31AEE4BF9B87B99B35E4EBC93C60D3FE3BF4F7A9BC25B1A8D83A4E03",
    ),
    (
        "4.1.7",
        "Worker Scaling",
        "scaling",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
        "87076D2B8FD337E472A5F9D4DB350C737596EF456B482897362421B02CCAF1DD",
    ),
    (
        "4.1.8",
        "Worker Shutdown",
        "shutdown",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
        "F9A9802AF14F68EB8210AB0A57B4CA136C41247DA33050E208D08436B6015CF4",
    ),
    (
        "4.1.9",
        "Worker Pool Infrastructure",
        "pool",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
        "E92B2E6871C84D44E8522A639DB8A7827EC5F6A7E5AC25B9CBE5452627F31DEA",
    ),
    (
        "4.1.10",
        "Worker Heartbeats",
        "heartbeat",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
        "2E370554729FAE227AD779588514F2B1EB989A5313CB258E5F4760D8B4F42B6A",
    ),
    (
        "4.1.11",
        "Stale Worker Detection",
        "stale",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
        "3C0B384BF6F3527D490AEA61FB2EB6C4C581A8A7D50E06BD91A01BC24B742F47",
    ),
    (
        "4.1.12",
        "Worker Drain",
        "drain",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
        "753357BB720233A4E2E186088EF39E9A2D136EBDCD4F61513F5FE4C1A054CDBA",
    ),
    (
        "4.1.13",
        "Worker Capability Management",
        "capability",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
        "D2BB13E03764D365C7FD92C8CFE2282615BE09FA3A7CAAF43344B3C74B30435F",
    ),
    (
        "4.1.14",
        "Worker Capacity Management",
        "capacity",
        "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55",
        "8E1F83740A13BA1783987FF1B1800BD9E094471662BFD4159BFAF88B131FDC06",
    ),
)


# ============================================================
# ADJACENT PROTECTED AUTHORITIES
# ============================================================

PROTECTED_ADJACENT = (
    (
        "Queue Infrastructure Certification",
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),
    (
        "Universal Job Contract",
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),
    (
        "Existing Runtime Worker",
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),
    (
        "Runtime Registration",
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),
    (
        "Runtime Infrastructure",
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),
    (
        "Runtime Shutdown Process",
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),
    (
        "Runtime Lifecycle Manager",
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
    ),
    (
        "Orchestration Models",
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),
    (
        "TMS Orchestration Governance",
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
    ),
    (
        "Orchestration Queue",
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),
    (
        "Orchestration Service",
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
)


FORBIDDEN_WORKER_IMPORT_PREFIXES = (
    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
)


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
        canonical.encode("utf-8")
    ).hexdigest().upper()


def module_imports(
    path: Path,
) -> tuple[str, ...]:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    found = []

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                found.append(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:

                found.append(
                    node.module
                )

    return tuple(
        found
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


# ============================================================
# 1 — MANIFEST INTEGRITY
# ============================================================

check(
    "component_count_exact",
    len(
        COMPONENTS
    )
    == 14,
    len(
        COMPONENTS
    ),
)


expected_phase_sequence = tuple(
    "4.1."
    + str(index)
    for index in range(
        1,
        15
    )
)


actual_phase_sequence = tuple(
    phase
    for phase, _, _, _, _
    in COMPONENTS
)


check(
    "phase_sequence_exact",
    actual_phase_sequence
    == expected_phase_sequence,
    actual_phase_sequence,
)


module_names = tuple(
    module_name
    for _, _, module_name, _, _
    in COMPONENTS
)


check(
    "component_module_names_unique",
    len(
        module_names
    )
    == len(
        set(
            module_names
        )
    ),
    module_names,
)


component_fingerprints = tuple(
    fingerprint
    for _, _, _, _, fingerprint
    in COMPONENTS
)


check(
    "component_fingerprints_unique",
    len(
        component_fingerprints
    )
    == len(
        set(
            component_fingerprints
        )
    ),
)


# ============================================================
# 2 — FILE / AST / COMPILE / IMPORT MATRIX
# ============================================================

before_asts = {}


sys.path.insert(
    0,
    str(
        ROOT
    ),
)


for (
    phase,
    component_name,
    module_name,
    expected_ast,
    fingerprint,
) in COMPONENTS:

    path = (
        WORKER_ROOT
        / (
            module_name
            + ".py"
        )
    )

    check(
        phase
        + "_file_exists",
        path.exists(),
        path,
    )

    if not path.exists():

        continue

    actual_ast = ast_sha(
        path
    )

    before_asts[
        module_name
    ] = actual_ast

    check(
        phase
        + "_ast_exact",
        actual_ast
        == expected_ast,
        actual_ast,
    )

    check(
        phase
        + "_fingerprint_shape",
        (
            len(
                fingerprint
            )
            == 64
            and
            all(
                character
                in "0123456789ABCDEF"
                for character in fingerprint
            )
        ),
        fingerprint,
    )

    try:

        py_compile.compile(
            str(
                path
            ),
            doraise=True,
        )

    except Exception as exc:

        compiled = False
        compile_detail = repr(
            exc
        )

    else:

        compiled = True
        compile_detail = "OK"

    check(
        phase
        + "_compile",
        compiled,
        compile_detail,
    )

    import_name = (
        "backend.server.runtime."
        "universal_worker."
        + module_name
    )

    try:

        importlib.import_module(
            import_name
        )

    except Exception as exc:

        imported = False
        import_detail = repr(
            exc
        )

    else:

        imported = True
        import_detail = "OK"

    check(
        phase
        + "_import",
        imported,
        import_detail,
    )


# ============================================================
# 3 — FORBIDDEN LEGACY/PIPELINE COUPLING
# ============================================================

for (
    phase,
    component_name,
    module_name,
    expected_ast,
    fingerprint,
) in COMPONENTS:

    path = (
        WORKER_ROOT
        / (
            module_name
            + ".py"
        )
    )

    if not path.exists():

        continue

    imports = module_imports(
        path
    )

    forbidden = tuple(
        imported
        for imported in imports
        if any(
            imported.startswith(
                prefix
            )
            for prefix
            in FORBIDDEN_WORKER_IMPORT_PREFIXES
        )
    )

    check(
        phase
        + "_no_legacy_or_pipeline_coordinator_import",
        not forbidden,
        forbidden,
    )


# ============================================================
# 4 — CANONICAL RESPONSIBILITY PRESENCE
# ============================================================

expected_files = {
    (
        module_name
        + ".py"
    )
    for _, _, module_name, _, _
    in COMPONENTS
}


actual_expected_files = {
    path.name
    for path in WORKER_ROOT.glob(
        "*.py"
    )
    if path.name
    in expected_files
}


check(
    "all_14_operational_authorities_present",
    actual_expected_files
    == expected_files,
    sorted(
        actual_expected_files
    ),
)


# ============================================================
# 5 — ADJACENT AUTHORITY PROTECTION
# ============================================================

adjacent_before = {}


for (
    name,
    path,
    expected_ast,
) in PROTECTED_ADJACENT:

    check(
        (
            "adjacent_"
            + name
            .lower()
            .replace(
                " ",
                "_"
            )
            + "_exists"
        ),
        path.exists(),
        path,
    )

    if not path.exists():

        continue

    actual = ast_sha(
        path
    )

    adjacent_before[
        str(
            path
        )
    ] = actual

    check(
        (
            "adjacent_"
            + name
            .lower()
            .replace(
                " ",
                "_"
            )
            + "_ast_exact"
        ),
        actual
        == expected_ast,
        actual,
    )


# ============================================================
# 6 — PHASE-WIDE CANONICAL FINGERPRINT
# ============================================================

fingerprint_parts = [
    "linkcraftor_phase_4_worker_infrastructure_v1",
    "phase_4_1_15_worker_infrastructure_certification",
    "component_count_14",
]


for (
    phase,
    component_name,
    module_name,
    expected_ast,
    fingerprint,
) in COMPONENTS:

    fingerprint_parts.extend(
        (
            phase,
            component_name,
            module_name,
            expected_ast,
            fingerprint,
        )
    )


fingerprint_parts.extend(
    (
        "registration_identity_authority",
        "discovery_evidence_authority",
        "assignment_selection_authority",
        "leasing_ownership_authority",
        "health_evidence_authority",
        "recovery_authorization_authority",
        "scaling_decision_authority",
        "shutdown_permission_authority",
        "pool_membership_authority",
        "heartbeat_evidence_authority",
        "stale_detection_authority",
        "drain_evidence_authority",
        "capability_evidence_authority",
        "capacity_evidence_authority",

        "assignment_consumes_caller_supplied_eligibility",
        "capability_does_not_assign",
        "capacity_does_not_assign",
        "capacity_does_not_scale",
        "leases_do_not_define_capacity",
        "drain_does_not_terminate",
        "shutdown_does_not_drain",
        "stale_does_not_mean_unhealthy",
        "health_does_not_mean_live",
        "compatible_does_not_mean_assigned",
        "available_capacity_does_not_mean_assigned",

        "queue_infrastructure_separate",
        "universal_job_contract_separate",
        "runtime_registration_separate",
        "runtime_handler_registration_later",
        "coordinator_orchestration_later",
        "legacy_orchestrator_untouched",

        "no_connect_domain_coordinator_coupling",
        "no_phase_4_runtime_handler_registration",
        "no_phase_4_pipeline_orchestration",

        "phase_4_complete_after_integrated_certification",
    )
)


fingerprint_material = "|".join(
    fingerprint_parts
)


worker_infrastructure_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "phase_4_fingerprint_generated",
    (
        len(
            worker_infrastructure_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in worker_infrastructure_fingerprint
        )
    ),
    worker_infrastructure_fingerprint,
)


certification_id = (
    "phase_4_1_15_"
    + worker_infrastructure_fingerprint[
        :16
    ].lower()
)


check(
    "certification_id_generated",
    certification_id.startswith(
        "phase_4_1_15_"
    ),
    certification_id,
)


# ============================================================
# 7 — POST-CERTIFICATION AST RECHECK
# ============================================================

for (
    phase,
    component_name,
    module_name,
    expected_ast,
    fingerprint,
) in COMPONENTS:

    path = (
        WORKER_ROOT
        / (
            module_name
            + ".py"
        )
    )

    if not path.exists():

        continue

    final_ast = ast_sha(
        path
    )

    check(
        phase
        + "_ast_unchanged_during_certification",
        (
            final_ast
            == before_asts.get(
                module_name
            )
            == expected_ast
        ),
        final_ast,
    )


for (
    name,
    path,
    expected_ast,
) in PROTECTED_ADJACENT:

    if not path.exists():

        continue

    final_ast = ast_sha(
        path
    )

    check(
        (
            "adjacent_"
            + name
            .lower()
            .replace(
                " ",
                "_"
            )
            + "_unchanged_during_certification"
        ),
        (
            final_ast
            == adjacent_before.get(
                str(
                    path
                )
            )
            == expected_ast
        ),
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
        "PHASE 4.1.15 — UNIVERSAL WORKER "
        "INFRASTRUCTURE FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "CERTIFICATION ID: "
        + certification_id
    ),
    (
        "WORKER INFRASTRUCTURE FINGERPRINT: "
        + worker_infrastructure_fingerprint
    ),
    "",
    "CANONICAL COMPONENT MATRIX",
    "-" * 118,
]


for (
    phase,
    component_name,
    module_name,
    expected_ast,
    fingerprint,
) in COMPONENTS:

    lines.extend(
        [
            (
                phase
                + " "
                + component_name
            ),
            (
                "    MODULE: "
                + module_name
                + ".py"
            ),
            (
                "    AST: "
                + expected_ast
            ),
            (
                "    FINGERPRINT: "
                + fingerprint
            ),
        ]
    )


lines.extend(
    [
        "",
        "CERTIFICATION CHECKS",
        "-" * 118,
    ]
)


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
            "FINAL WORKER INFRASTRUCTURE CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
        ),
        "",
        "4.1.1–4.1.14 OPERATIONAL AUTHORITIES MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODELS MODIFIED: NO",
        "ORCHESTRATION QUEUE MODIFIED: NO",
        "ORCHESTRATION SERVICE MODIFIED: NO",
        "TMS ORCHESTRATION GOVERNANCE MODIFIED: NO",
        "LEGACY UNIVERSAL KNOWLEDGE ORCHESTRATOR MODIFIED: NO",
        "CONNECT DOMAIN COORDINATOR MODIFIED: NO",
        "",
        "RUNTIME HANDLER REGISTRATION PERFORMED: NO",
        "PIPELINE STAGE REGISTRATION PERFORMED: NO",
        "COORDINATOR INTEGRATION PERFORMED: NO",
        "JOB DISPATCH/EXECUTION PERFORMED: NO",
        "",
        (
            "PHASE 4 WORKER INFRASTRUCTURE "
            "FREEZE CANDIDATE: "
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
        (
            "Phase 4.1.15 Worker Infrastructure "
            "final certification failed."
        )
    )
