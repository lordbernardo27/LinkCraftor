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
    / "phase_5_1_3_orchestration_state_model_scan.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

PROTECTED = {
    "5.1.1_orchestration_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "5.1.2_run_identity": (
        ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),

    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),

    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),

    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),

    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),

    "worker_stale": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),

    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),

    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
    ),

    "worker_capacity": (
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

    "runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
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
                repr(exc),
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
# TARGET FILES
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/status.py",
    SERVER / "runtime/universal_jobs/transitions.py",
    SERVER / "runtime/universal_jobs/lifecycle.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_worker/health.py",
    SERVER / "runtime/universal_worker/stale.py",
    SERVER / "runtime/universal_worker/drain.py",
    SERVER / "runtime/universal_worker/shutdown.py",

    SERVER / "runtime/runtime_lifecycle_manager.py",
    SERVER / "runtime/runtime_shutdown_process.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


PATTERNS = {
    "status": re.compile(
        r"\bstatus\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\bstate\b",
        re.IGNORECASE,
    ),

    "transition": re.compile(
        r"\b("
        r"transition|transitions|transition_to|"
        r"allowed_transition|valid_transition"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|is_terminal|terminal_status"
        r")\b",
        re.IGNORECASE,
    ),

    "created": re.compile(
        r"\bcreated\b",
        re.IGNORECASE,
    ),

    "queued": re.compile(
        r"\bqueued\b",
        re.IGNORECASE,
    ),

    "scheduled": re.compile(
        r"\bscheduled\b",
        re.IGNORECASE,
    ),

    "active": re.compile(
        r"\bactive\b",
        re.IGNORECASE,
    ),

    "running": re.compile(
        r"\brunning\b",
        re.IGNORECASE,
    ),

    "waiting": re.compile(
        r"\bwaiting\b",
        re.IGNORECASE,
    ),

    "blocked": re.compile(
        r"\bblocked\b",
        re.IGNORECASE,
    ),

    "paused": re.compile(
        r"\b("
        r"paused|pause|suspended|suspend"
        r")\b",
        re.IGNORECASE,
    ),

    "completing": re.compile(
        r"\bcompleting\b",
        re.IGNORECASE,
    ),

    "succeeded": re.compile(
        r"\b("
        r"succeeded|success|completed"
        r")\b",
        re.IGNORECASE,
    ),

    "failed": re.compile(
        r"\bfailed\b",
        re.IGNORECASE,
    ),

    "cancelled": re.compile(
        r"\b("
        r"cancelled|canceled"
        r")\b",
        re.IGNORECASE,
    ),

    "expired": re.compile(
        r"\bexpired\b",
        re.IGNORECASE,
    ),

    "dead_letter": re.compile(
        r"\b("
        r"dead_letter|dead-letter|deadletter"
        r")\b",
        re.IGNORECASE,
    ),

    "workflow_status": re.compile(
        r"\bUniversalWorkflowStatus\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\bUniversalJobStatus\b",
        re.IGNORECASE,
    ),

    "orchestration_status": re.compile(
        r"\b("
        r"orchestration_status|OrchestrationStatus|"
        r"orchestration state|orchestration_state"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency": re.compile(
        r"\b("
        r"dependency|dependencies|dependency_job_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\b("
        r"ready|readiness|eligible"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execute|execution|dispatch|handler"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

file_counts = Counter()

classes = []

functions = []

enum_members = []

declared_fields = []

imports = []

errors = []


for path in TARGETS:

    relative = str(
        path.relative_to(ROOT)
    )

    if not path.exists():

        errors.append(
            (
                relative,
                "MISSING",
            )
        )

        continue

    try:

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        tree = ast.parse(
            source
        )

    except Exception as exc:

        errors.append(
            (
                relative,
                repr(exc),
            )
        )

        continue

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        for category, pattern in PATTERNS.items():

            if pattern.search(
                line
            ):

                counts[
                    category
                ] += 1

                file_counts[
                    relative
                ] += 1

                findings.append(
                    (
                        category,
                        relative,
                        line_number,
                        line.strip()[:500],
                    )
                )

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ClassDef,
        ):

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "status",
                    "state",
                    "transition",
                    "lifecycle",
                )
            ):

                classes.append(
                    (
                        relative,
                        node.lineno,
                        node.name,
                    )
                )

            base_names = []

            for base in node.bases:

                if isinstance(
                    base,
                    ast.Name,
                ):

                    base_names.append(
                        base.id
                    )

                elif isinstance(
                    base,
                    ast.Attribute,
                ):

                    base_names.append(
                        base.attr
                    )

            if any(
                base in (
                    "Enum",
                    "StrEnum",
                    "IntEnum",
                )
                for base in base_names
            ):

                for item in node.body:

                    if isinstance(
                        item,
                        ast.Assign,
                    ):

                        for target in item.targets:

                            if isinstance(
                                target,
                                ast.Name,
                            ):

                                enum_members.append(
                                    (
                                        relative,
                                        item.lineno,
                                        node.name,
                                        target.id,
                                    )
                                )

                    elif isinstance(
                        item,
                        ast.AnnAssign,
                    ):

                        if isinstance(
                            item.target,
                            ast.Name,
                        ):

                            enum_members.append(
                                (
                                    relative,
                                    item.lineno,
                                    node.name,
                                    item.target.id,
                                )
                            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "status",
                    "state",
                    "transition",
                    "terminal",
                    "lifecycle",
                    "pause",
                    "resume",
                    "complete",
                    "cancel",
                    "fail",
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
            ast.AnnAssign,
        ):

            if isinstance(
                node.target,
                ast.Name,
            ):

                name = (
                    node.target.id
                )

                if any(
                    token in name.lower()
                    for token in (
                        "status",
                        "state",
                    )
                ):

                    declared_fields.append(
                        (
                            relative,
                            node.lineno,
                            name,
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

            if any(
                token in module.lower()
                for token in (
                    "status",
                    "state",
                    "lifecycle",
                    "orchestration",
                    "coordination",
                    "runtime",
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
    (
        "PHASE 5.1.3 — ORCHESTRATION STATE MODEL "
        "READ-ONLY DISCOVERY"
    ),
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
    "",
]


for name, status, expected, actual in protected_results:

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
        "SECTION 2 — TARGET FILES",
        "-" * 118,
        "",
    ]
)


for path in TARGETS:

    out.append(
        str(
            path.relative_to(ROOT)
        )
        + (
            " — FOUND"
            if path.exists()
            else " — MISSING"
        )
    )


out.extend(
    [
        "",
        "SECTION 3 — STATE FINDING COUNTS",
        "-" * 118,
        "",
    ]
)


for category in PATTERNS:

    out.append(
        (
            category
            + ": "
            + str(
                counts[
                    category
                ]
            )
        )
    )


out.extend(
    [
        "",
        "SECTION 4 — HIGHEST-VALUE FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    file_counts.most_common(),
    start=1,
):

    out.append(
        (
            f"{index:03d}. "
            f"hits={count} "
            + filename
        )
    )


out.extend(
    [
        "",
        "SECTION 5 — RELEVANT CLASSES",
        "-" * 118,
        "",
    ]
)


if classes:

    for relative, line, name in sorted(
        classes
    ):

        out.append(
            f"{relative}:{line} class {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 6 — ENUM MEMBERS",
        "-" * 118,
        "",
    ]
)


if enum_members:

    for (
        relative,
        line,
        class_name,
        member,
    ) in sorted(
        enum_members
    ):

        out.append(
            (
                f"{relative}:{line} "
                f"{class_name}.{member}"
            )
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 7 — RELEVANT FUNCTIONS",
        "-" * 118,
        "",
    ]
)


if functions:

    for relative, line, name in sorted(
        functions
    ):

        out.append(
            f"{relative}:{line} {name}()"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 8 — DECLARED STATE FIELDS",
        "-" * 118,
        "",
    ]
)


if declared_fields:

    for relative, line, name in sorted(
        declared_fields
    ):

        out.append(
            f"{relative}:{line} {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 9 — RELEVANT IMPORTS",
        "-" * 118,
        "",
    ]
)


if imports:

    for relative, line, module in sorted(
        imports
    ):

        out.append(
            f"{relative}:{line} -> {module}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 10 — STATE FINDINGS",
        "-" * 118,
    ]
)


for category in PATTERNS:

    out.extend(
        [
            "",
            "[" + category.upper() + "]",
            "~" * 118,
        ]
    )

    items = [
        item
        for item in findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for (
        _,
        relative,
        line,
        text,
    ) in items:

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 11 — ERRORS / MISSING TARGETS",
        "-" * 118,
        "",
    ]
)


if errors:

    for relative, error in errors:

        out.append(
            f"{relative} | {error}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 12 — 5.1.3 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Does a canonical Runtime Orchestration state model already exist?",
        "2. What are the exact Universal Job statuses?",
        "3. Which Universal Job statuses describe one job rather than an orchestration run?",
        "4. What statuses exist on legacy OrchestrationJob?",
        "5. Are legacy OrchestrationJob statuses operational queue/worker statuses?",
        "6. What statuses exist on UniversalWorkflow?",
        "7. Are UniversalWorkflow states higher-layer coordination states?",
        "8. Must 5.1.3 define a separate UniversalOrchestrationState enum?",
        "9. Should CREATED exist for an identified run before orchestration begins?",
        "10. Should ACTIVE exist as the generic progressing state?",
        "11. Should WAITING exist?",
        "12. If WAITING exists, is it generic waiting evidence rather than dependency resolution?",
        "13. Should BLOCKED exist here or belong solely to 5.1.6 readiness?",
        "14. Should PAUSED/SUSPENDED exist here?",
        "15. Should pause/resume execution itself remain outside 5.1.3?",
        "16. Should COMPLETING exist or should completion be resolved only in 5.1.15?",
        "17. Should SUCCEEDED be a terminal orchestration state?",
        "18. Should FAILED be a terminal orchestration state?",
        "19. Should CANCELLED be a terminal orchestration state?",
        "20. Should EXPIRED exist for orchestration runs?",
        "21. Should DEAD_LETTER exist? Expected likely NO because DLQ is job/queue semantics.",
        "22. Which states are terminal?",
        "23. Which state is the initial state?",
        "24. Are self-transitions allowed?",
        "25. Are terminal states immutable?",
        "26. Is CREATED -> SUCCEEDED ever legal?",
        "27. Is CREATED -> FAILED legal?",
        "28. Is CREATED -> CANCELLED legal?",
        "29. Is ACTIVE -> WAITING legal?",
        "30. Is WAITING -> ACTIVE legal?",
        "31. Is ACTIVE -> PAUSED legal?",
        "32. Is PAUSED -> ACTIVE legal?",
        "33. Can WAITING -> PAUSED occur?",
        "34. Can PAUSED -> WAITING occur?",
        "35. Must success/failure/cancellation decisions remain external evidence supplied to this state model?",
        "36. Should 5.1.3 transition state or only validate transition legality?",
        "37. Should state transition produce a new immutable snapshot rather than mutate prior state?",
        "38. Should 5.1.3 include orchestration_run identity directly?",
        "39. Should lifecycle state bind to a 5.1.2 Run Identity?",
        "40. Should state contain timestamps? Expected NO.",
        "41. Should state contain dependency evidence? Expected NO.",
        "42. Should state contain readiness evidence? Expected NO.",
        "43. Should state contain execution-plan evidence? Expected NO.",
        "44. Should state contain worker/lease evidence? Expected NO.",
        "45. Should state contain queue status? Expected NO.",
        "46. Should state persistence be deferred to 5.1.14?",
        "47. Should completion determination remain deferred to 5.1.15?",
        "48. Should cancellation/termination determination remain deferred to 5.1.16?",
        "49. Should suspension/resume eligibility remain deferred to 5.1.12?",
        "50. What exact immutable fields define one orchestration state snapshot?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.3 Orchestration State Model boundary "
            "before implementation."
        ),
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
    "PHASE 5.1.3 ORCHESTRATION STATE MODEL DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Target files:",
    len(
        TARGETS
    ),
)

print(
    "Files with state findings:",
    len(
        file_counts
    ),
)

print(
    "Total state findings:",
    len(
        findings
    ),
)

print(
    "Errors/missing targets:",
    len(
        errors
    ),
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

for category, count in (
    counts.most_common()
):

    print(
        f"{category}: {count}"
    )

print()
print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
