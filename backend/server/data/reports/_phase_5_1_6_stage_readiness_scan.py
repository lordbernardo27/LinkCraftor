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
    / "phase_5_1_6_stage_readiness_scan.txt"
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
# FOCUSED TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",
    SERVER / "runtime/universal_orchestration/dependency_resolution.py",
    SERVER / "runtime/universal_orchestration/execution_planning.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/status.py",
    SERVER / "runtime/universal_jobs/lineage.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_worker/registration.py",
    SERVER / "runtime/universal_worker/discovery.py",
    SERVER / "runtime/universal_worker/assignment.py",
    SERVER / "runtime/universal_worker/leasing.py",
    SERVER / "runtime/universal_worker/health.py",
    SERVER / "runtime/universal_worker/capacity.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


PATTERNS = {
    "ready": re.compile(
        r"\b("
        r"ready|readiness|is_ready|ready_to_"
        r")\b",
        re.IGNORECASE,
    ),

    "blocked": re.compile(
        r"\b("
        r"blocked|blocking|block_reason|blocked_by"
        r")\b",
        re.IGNORECASE,
    ),

    "waiting": re.compile(
        r"\b("
        r"waiting|wait|pending_dependency|pending_dependencies"
        r")\b",
        re.IGNORECASE,
    ),

    "eligible": re.compile(
        r"\b("
        r"eligible|eligibility|is_eligible"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_resolution": re.compile(
        r"\b("
        r"all_dependencies_satisfied|"
        r"has_unresolved_dependencies|"
        r"has_terminal_dependency_failure|"
        r"has_missing_dependency_evidence|"
        r"satisfied_dependency_ids|"
        r"unresolved_dependency_ids|"
        r"terminal_unsatisfied_dependency_ids|"
        r"missing_dependency_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\b("
        r"UniversalJobStatus|job_status|status"
        r")\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|succeeded|failed|cancelled|"
        r"dead_letter|expired"
        r")\b",
        re.IGNORECASE,
    ),

    "execution_plan": re.compile(
        r"\b("
        r"execution_plan|execution_waves|"
        r"topological_order|root_job_ids|"
        r"leaf_job_ids"
        r")\b",
        re.IGNORECASE,
    ),

    "queue_readiness": re.compile(
        r"\b("
        r"queue_ready|queue_readiness|"
        r"scheduling_ready|schedule_ready"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_readiness": re.compile(
        r"\b("
        r"worker_ready|worker_readiness|"
        r"worker_available|capacity_available|"
        r"has_available_capacity"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease|leased|lease_owner|lease_id"
        r")\b",
        re.IGNORECASE,
    ),

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|claim|dequeue"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|handler|execute|execution"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"orchestration_state|transition_state|"
        r"state_transition"
        r")\b",
        re.IGNORECASE,
    ),

    "retry": re.compile(
        r"\b("
        r"retry|attempt|maximum_attempts"
        r")\b",
        re.IGNORECASE,
    ),

    "schedule": re.compile(
        r"\b("
        r"scheduled_at|schedule|scheduler"
        r")\b",
        re.IGNORECASE,
    ),

    "suspended": re.compile(
        r"\b("
        r"suspended|paused|resume"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

file_counts = Counter()

classes = []

functions = []

fields = []

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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "ready",
                    "readiness",
                    "eligible",
                    "blocked",
                    "waiting",
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
                    "ready",
                    "readiness",
                    "eligible",
                    "blocked",
                    "waiting",
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
                        "ready",
                        "readiness",
                        "eligible",
                        "blocked",
                        "waiting",
                    )
                ):

                    fields.append(
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
                    "dependency",
                    "planning",
                    "queue",
                    "worker",
                    "orchestration",
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
        "PHASE 5.1.6 — STAGE READINESS "
        "EVALUATION READ-ONLY DISCOVERY"
    ),
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
        "SECTION 3 — READINESS FINDING COUNTS",
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
        "SECTION 6 — RELEVANT FUNCTIONS",
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
        "SECTION 7 — DECLARED READINESS FIELDS",
        "-" * 118,
        "",
    ]
)


if fields:

    for relative, line, name in sorted(
        fields
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
        "SECTION 8 — RELEVANT IMPORTS",
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
        "SECTION 9 — READINESS FINDINGS",
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

    for _, relative, line, text in items:

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 10 — ERRORS / MISSING TARGETS",
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
        "SECTION 11 — 5.1.6 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Does a canonical Runtime Orchestration readiness authority already exist?",
        "2. Is READY already defined as a Universal Job status? Expected NO.",
        "3. Is BLOCKED already defined as a Universal Job status? Expected NO.",
        "4. Is WAITING already defined as a Universal Job status? Expected NO.",
        "5. Are READY/BLOCKED/WAITING orchestration decisions rather than persisted job statuses?",
        "6. Should readiness consume a frozen 5.1.4 Dependency Resolution object?",
        "7. Should readiness consume the frozen 5.1.5 Execution Plan?",
        "8. Must readiness verify both inputs belong to the same orchestration identity?",
        "9. Must readiness verify the target job exists in the execution plan?",
        "10. Must readiness verify the 5.1.4 target_job matches the planned target job?",
        "11. Is all_dependencies_satisfied=True sufficient for READY?",
        "12. Should a zero-dependency job be structurally READY?",
        "13. Should unresolved dependency evidence produce WAITING?",
        "14. Should missing dependency evidence produce WAITING?",
        "15. Should terminally-unsatisfied dependency evidence produce BLOCKED?",
        "16. Should terminal dependency failure outrank unresolved/missing evidence?",
        "17. If terminal failure and unresolved evidence coexist, should classification be BLOCKED?",
        "18. If unresolved and missing coexist without terminal failure, should classification be WAITING?",
        "19. Should READY require no unresolved, no missing, and no terminally-unsatisfied dependencies?",
        "20. Should 5.1.6 inspect target_job.status itself?",
        "21. Should target job already SUCCEEDED/FAILED/CANCELLED/etc. be classified by readiness at all?",
        "22. Should terminal target jobs be rejected as non-actionable readiness subjects?",
        "23. Should SUSPENDED target jobs be handled here or deferred to 5.1.12?",
        "24. Should RUNNING/LEASED jobs be considered already beyond readiness?",
        "25. Should CREATED/QUEUED/SCHEDULED be eligible readiness subjects?",
        "26. Should job priority influence readiness? Expected NO.",
        "27. Should queue priority influence readiness? Expected NO.",
        "28. Should created_at influence readiness? Expected NO.",
        "29. Should worker availability influence readiness? Expected NO.",
        "30. Should worker capacity influence readiness? Expected NO.",
        "31. Should worker capability influence readiness? Expected NO.",
        "32. Should queue capacity/backpressure influence readiness? Expected NO.",
        "33. Should lease availability influence readiness? Expected NO.",
        "34. Should scheduled_at timing influence readiness? Expected NO unless explicitly designed elsewhere.",
        "35. Should retries/attempt counts influence readiness? Expected NO.",
        "36. Should readiness perform queue enqueue? Expected NO.",
        "37. Should readiness assign workers? Expected NO.",
        "38. Should readiness acquire leases? Expected NO.",
        "39. Should readiness dispatch handlers? Expected NO.",
        "40. Should readiness execute jobs? Expected NO.",
        "41. Should readiness transition 5.1.3 state? Expected NO.",
        "42. Should readiness coordinate fan-out? Expected NO.",
        "43. Should readiness coordinate fan-in? Expected NO.",
        "44. Should readiness perform handoff? Expected NO.",
        "45. Should readiness evaluate conditional branches? Expected NO.",
        "46. Should readiness access Runtime State Store? Expected NO.",
        "47. Should readiness persist results? Expected NO.",
        "48. Should readiness import Universal Coordination Framework? Expected NO.",
        "49. Should readiness invoke pipeline coordinators? Expected NO.",
        "50. Should readiness output be immutable?",
        "51. Should readiness classification be an enum?",
        "52. Is the canonical vocabulary READY / WAITING / BLOCKED?",
        "53. Should exact reason codes be exposed?",
        "54. Should satisfied/unresolved/terminal/missing dependency IDs remain derived from 5.1.4 rather than copied?",
        "55. Should the readiness object store dependency_resolution directly?",
        "56. Should the readiness object store execution_plan directly?",
        "57. Should target job be derived through dependency_resolution?",
        "58. Should identity be derived rather than duplicated?",
        "59. What exact stored fields belong in the readiness object?",
        "60. What exact precedence rules define READY / WAITING / BLOCKED?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.6 Stage Readiness Evaluation boundary "
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
    "PHASE 5.1.6 STAGE READINESS DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Target files:",
    len(
        TARGETS
    ),
)

print(
    "Files with readiness findings:",
    len(
        file_counts
    ),
)

print(
    "Total readiness findings:",
    len(
        findings
    ),
)

print(
    "Errors / missing targets:",
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
