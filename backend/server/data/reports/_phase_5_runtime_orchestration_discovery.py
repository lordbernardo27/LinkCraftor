from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

SERVER = (
    ROOT
    / "backend"
    / "server"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_runtime_orchestration_discovery.txt"
)


# ============================================================
# FROZEN PHASE 4 AUTHORITIES
# ============================================================

PROTECTED = {
    "4.1.1_worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),
    "4.1.2_worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),
    "4.1.3_worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),
    "4.1.4_worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),
    "4.1.5_worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),
    "4.1.6_worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),
    "4.1.7_worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),
    "4.1.8_worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),
    "4.1.9_worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),
    "4.1.10_worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),
    "4.1.11_stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),
    "4.1.12_worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),
    "4.1.13_worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
    ),
    "4.1.14_worker_capacity": (
        ROOT / "backend/server/runtime/universal_worker/capacity.py",
        "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),

    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
    ),

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),

    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
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
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# PROTECTION CHECK
# ============================================================

protected_results = []


for name, (
    path,
    expected,
) in PROTECTED.items():

    if not path.exists():

        protected_results.append(
            (
                name,
                "MISSING",
                expected,
                None,
            )
        )

        continue

    try:

        actual = ast_sha(
            path
        )

    except Exception as exc:

        protected_results.append(
            (
                name,
                "ERROR",
                expected,
                repr(
                    exc
                ),
            )
        )

        continue

    protected_results.append(
        (
            name,
            (
                "PASS"
                if actual == expected
                else "FAIL"
            ),
            expected,
            actual,
        )
    )


# ============================================================
# SCAN FILES
# ============================================================

SKIP_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "data",
    "reports",
    "tests",
    "test",
    "fixtures",
    "snapshots",
}


files = []


for path in SERVER.rglob(
    "*.py"
):

    parts = path.relative_to(
        SERVER
    ).parts

    if any(
        part in SKIP_PARTS
        for part in parts
    ):

        continue

    files.append(
        path
    )


files.sort()


PATTERNS = {
    "orchestration": re.compile(
        r"\b("
        r"orchestration|orchestrator|orchestrate"
        r")\b",
        re.IGNORECASE,
    ),

    "workflow": re.compile(
        r"\b("
        r"workflow|workflow_id|workflow_run"
        r")\b",
        re.IGNORECASE,
    ),

    "state_machine": re.compile(
        r"\b("
        r"state_machine|state machine|transition"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency": re.compile(
        r"\b("
        r"dependency|dependencies|dependency_graph|"
        r"dependency graph"
        r")\b",
        re.IGNORECASE,
    ),

    "scheduler": re.compile(
        r"\b("
        r"scheduler|scheduling|scheduled"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|dispatcher|dispatched"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execution|execute|executor"
        r")\b",
        re.IGNORECASE,
    ),

    "handoff": re.compile(
        r"\b("
        r"handoff|hand-off|stage_handoff"
        r")\b",
        re.IGNORECASE,
    ),

    "fanout": re.compile(
        r"\b("
        r"fan_out|fan-out|fanout"
        r")\b",
        re.IGNORECASE,
    ),

    "fanin": re.compile(
        r"\b("
        r"fan_in|fan-in|fanin"
        r")\b",
        re.IGNORECASE,
    ),

    "pause_resume": re.compile(
        r"\b("
        r"pause|resume|suspend|suspended"
        r")\b",
        re.IGNORECASE,
    ),

    "checkpoint": re.compile(
        r"\b("
        r"checkpoint|checkpoint_reference"
        r")\b",
        re.IGNORECASE,
    ),

    "parent_job": re.compile(
        r"\bparent_job_id\b",
        re.IGNORECASE,
    ),

    "dependency_jobs": re.compile(
        r"\bdependency_job_ids\b",
        re.IGNORECASE,
    ),

    "pipeline_run": re.compile(
        r"\bpipeline_run_id\b",
        re.IGNORECASE,
    ),

    "batch": re.compile(
        r"\bbatch_id\b",
        re.IGNORECASE,
    ),

    "runtime_registration": re.compile(
        r"\b("
        r"runtime_registration|register_runtime|"
        r"runtime handler|runtime_handler"
        r")\b",
        re.IGNORECASE,
    ),

    "coordinator": re.compile(
        r"\b("
        r"coordinator|coordination"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\bqueue\b",
        re.IGNORECASE,
    ),

    "worker": re.compile(
        r"\bworker\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\brecovery\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|state store"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

file_counts = Counter()

classes = []

functions = []

imports = []

parse_errors = []


for path in files:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    try:

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

    except Exception as exc:

        parse_errors.append(
            (
                relative,
                "READ: "
                + repr(
                    exc
                ),
            )
        )

        continue

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        for group, pattern in (
            PATTERNS.items()
        ):

            if pattern.search(
                line
            ):

                counts[
                    group
                ] += 1

                file_counts[
                    relative
                ] += 1

                findings.append(
                    (
                        group,
                        relative,
                        line_number,
                        line.strip()[:500],
                    )
                )

    try:

        tree = ast.parse(
            source
        )

    except Exception as exc:

        parse_errors.append(
            (
                relative,
                "AST: "
                + repr(
                    exc
                ),
            )
        )

        continue

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ClassDef,
        ):

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "orchestr",
                    "workflow",
                    "scheduler",
                    "dependency",
                    "execution",
                    "dispatch",
                    "coordination",
                    "state",
                )
            ):

                classes.append(
                    (
                        relative,
                        node.lineno,
                        node.name,
                    )
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "orchestr",
                    "workflow",
                    "schedule",
                    "dependency",
                    "dispatch",
                    "execute",
                    "handoff",
                    "resume",
                    "pause",
                    "transition",
                )
            ):

                functions.append(
                    (
                        relative,
                        node.lineno,
                        node.name,
                    )
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            module = (
                node.module
                or ""
            )

            lower = (
                module.lower()
            )

            if any(
                token in lower
                for token in (
                    "orchestration",
                    "coordination",
                    "runtime",
                    "queue",
                    "worker",
                    "jobs",
                )
            ):

                imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 5 — RUNTIME ORCHESTRATION READ-ONLY DISCOVERY",
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
    "",
]


for name, status, expected, actual in (
    protected_results
):

    out.extend(
        [
            f"{name}: {status}",
            f"    EXPECTED: {expected}",
            f"    ACTUAL:   {actual}",
            "",
        ]
    )


out.extend(
    [
        "",
        "SECTION 2 — SCAN SUMMARY",
        "-" * 118,
        "",
        f"Python files scanned: {len(files)}",
        f"Files with findings: {len(file_counts)}",
        f"Total findings: {len(findings)}",
        f"Parse/read errors: {len(parse_errors)}",
        "",
    ]
)


for group in PATTERNS:

    out.append(
        f"{group}: {counts[group]}"
    )


out.extend(
    [
        "",
        "SECTION 3 — HIGHEST-VALUE FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    hits,
) in enumerate(
    file_counts.most_common(
        200
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — RELEVANT CLASSES",
        "-" * 118,
        "",
    ]
)


for filename, line, name in sorted(
    classes
):

    out.append(
        f"{filename}:{line} class {name}"
    )


out.extend(
    [
        "",
        "SECTION 5 — RELEVANT FUNCTIONS",
        "-" * 118,
        "",
    ]
)


for filename, line, name in sorted(
    functions
):

    out.append(
        f"{filename}:{line} {name}()"
    )


out.extend(
    [
        "",
        "SECTION 6 — RELEVANT IMPORTS",
        "-" * 118,
        "",
    ]
)


for filename, line, module in sorted(
    imports
):

    out.append(
        f"{filename}:{line} -> {module}"
    )


out.extend(
    [
        "",
        "SECTION 7 — FINDINGS BY CATEGORY",
        "-" * 118,
    ]
)


for group in PATTERNS:

    out.extend(
        [
            "",
            "[" + group.upper() + "]",
            "~" * 118,
        ]
    )

    items = [
        item
        for item in findings
        if item[0] == group
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for _, filename, line, text in (
        items[:500]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 500:

        out.append(
            (
                "... "
                + str(
                    len(items) - 500
                )
                + " additional findings omitted"
            )
        )


out.extend(
    [
        "",
        "SECTION 8 — PARSE / READ ERRORS",
        "-" * 118,
        "",
    ]
)


if parse_errors:

    for filename, error in (
        parse_errors
    ):

        out.append(
            f"{filename} | {error}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 9 — PHASE 5 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. What canonical runtime-orchestration authority already exists?",
        "2. What does backend/server/orchestration currently own?",
        "3. What does universal_runtime_worker_v1 currently orchestrate?",
        "4. Does runtime_scheduler own runtime orchestration or only scheduling?",
        "5. Are parent_job_id/dependency_job_ids already actively consumed?",
        "6. Is pipeline_run_id used as runtime orchestration identity?",
        "7. Is batch_id orchestration evidence or only grouping metadata?",
        "8. Is checkpoint_reference consumed anywhere canonically?",
        "9. Are workflow state transitions already implemented?",
        "10. Is there a dependency graph authority?",
        "11. Is there deterministic execution planning?",
        "12. Is fan-out implemented anywhere?",
        "13. Is fan-in/join implemented anywhere?",
        "14. Are conditions or branch decisions implemented anywhere?",
        "15. Are runtime stage handoffs implemented anywhere?",
        "16. Is pause/resume runtime-level or coordinator-level today?",
        "17. Is orchestration recovery distinct from Worker Recovery?",
        "18. Is orchestration persistence distinct from Runtime State Store?",
        "19. Does existing orchestration directly execute pipeline business logic?",
        "20. Does existing orchestration use Runtime Registration handlers?",
        "21. Does it bypass Runtime Registration?",
        "22. Does existing runtime worker contain orchestration responsibilities that should later be separated?",
        "23. Which orchestration surfaces are legacy versus canonical?",
        "24. Which authorities must remain untouched during Phase 5?",
        "25. How must Phase 5 remain separate from the later Universal Coordination Framework?",
        "26. How must Phase 5 remain separate from pipeline coordinators?",
        "27. How must Phase 5 remain separate from Runtime Registration?",
        "28. How must Phase 5 remain separate from Stage Handlers?",
        "29. How must Phase 5 remain separate from Phase 6 Execution Engine?",
        "30. What exact Phase 5 subphases should be frozen before implementation?",
        "",
        "NEXT: analyze findings, define the canonical Phase 5 boundary, then build the Phase 5 subphase checklist before any production implementation.",
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        out
    ),
    encoding="utf-8",
)


print()
print("=" * 100)
print(
    "PHASE 5 RUNTIME ORCHESTRATION DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Python files scanned:",
    len(files),
)

print(
    "Files with findings:",
    len(file_counts),
)

print(
    "Total findings:",
    len(findings),
)

print(
    "Parse/read errors:",
    len(parse_errors),
)

print(
    "Frozen authority failures:",
    sum(
        1
        for _, status, _, _
        in protected_results
        if status != "PASS"
    ),
)

print()

for group, count in (
    counts.most_common()
):

    print(
        f"{group}: {count}"
    )

print()
print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
