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
    / "phase_5_1_4_dependency_resolution_scan.txt"
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
# TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",
    SERVER / "runtime/universal_orchestration/run_identity.py",
    SERVER / "runtime/universal_orchestration/state_model.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/lineage.py",
    SERVER / "runtime/universal_jobs/status.py",

    SERVER / "runtime/universal_queue/certification.py",

    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_registration.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


PATTERNS = {
    "dependency_job_ids": re.compile(
        r"\bdependency_job_ids\b",
        re.IGNORECASE,
    ),

    "dependencies": re.compile(
        r"\b("
        r"dependency|dependencies|depends_on|dependent"
        r")\b",
        re.IGNORECASE,
    ),

    "parent_job_id": re.compile(
        r"\bparent_job_id\b",
        re.IGNORECASE,
    ),

    "job_status": re.compile(
        r"\b("
        r"UniversalJobStatus|job_status|status"
        r")\b",
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

    "dead_letter": re.compile(
        r"\b("
        r"dead_letter|dead-letter|deadletter"
        r")\b",
        re.IGNORECASE,
    ),

    "expired": re.compile(
        r"\bexpired\b",
        re.IGNORECASE,
    ),

    "terminal": re.compile(
        r"\b("
        r"terminal|terminal_status|is_terminal"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_satisfied": re.compile(
        r"\b("
        r"dependency_satisfied|dependencies_satisfied|"
        r"all_dependencies_satisfied|satisfied_dependencies"
        r")\b",
        re.IGNORECASE,
    ),

    "dependency_blocked": re.compile(
        r"\b("
        r"dependency_blocked|blocked_by_dependency|"
        r"unresolved_dependencies|pending_dependencies"
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

    "queue": re.compile(
        r"\b("
        r"queue|queued|enqueue|claim"
        r")\b",
        re.IGNORECASE,
    ),

    "cycle": re.compile(
        r"\b("
        r"cycle|cyclic|circular"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

file_counts = Counter()

classes = []

functions = []

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
                    "dependency",
                    "lineage",
                    "job",
                    "status",
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

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "dependency",
                    "lineage",
                    "terminal",
                    "ready",
                    "status",
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
                        "dependency",
                        "parent_job",
                        "status",
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
                    "jobs",
                    "lineage",
                    "status",
                    "orchestration",
                    "coordination",
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
        "PHASE 5.1.4 — DEPENDENCY RESOLUTION "
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
        "SECTION 3 — DEPENDENCY FINDING COUNTS",
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
        "SECTION 7 — DECLARED DEPENDENCY FIELDS",
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
        "SECTION 9 — DEPENDENCY FINDINGS",
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
        "SECTION 11 — 5.1.4 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Where is dependency_job_ids canonically defined today?",
        "2. Is dependency_job_ids stored as immutable Universal Job lineage evidence?",
        "3. Does any existing authority actively resolve dependency satisfaction?",
        "4. Does any existing authority wait on dependencies?",
        "5. Does any existing authority mutate dependency_job_ids after job creation?",
        "6. Are duplicate dependency IDs already rejected by Universal Job validation?",
        "7. Is self-dependency already rejected?",
        "8. Is dependency order semantically meaningful or only canonicalized?",
        "9. Are dependencies required to belong to the same workspace?",
        "10. Are dependencies required to belong to the same pipeline?",
        "11. May a dependency reference a job outside the 5.1.1 orchestration contract?",
        "12. Should 5.1.4 reject dependency IDs outside contract.job_ids?",
        "13. Is parent_job_id dependency semantics or lineage only?",
        "14. Must parent_job_id remain separate from dependency_job_ids?",
        "15. Which Universal Job statuses count as dependency-satisfied?",
        "16. Is SUCCEEDED the only dependency-satisfied terminal status?",
        "17. Does FAILED represent terminal dependency failure?",
        "18. Does CANCELLED represent terminal dependency failure?",
        "19. Does DEAD_LETTER represent terminal dependency failure?",
        "20. Does EXPIRED represent terminal dependency failure?",
        "21. Should nonterminal dependency statuses remain unresolved?",
        "22. Should CREATED / QUEUED / SCHEDULED / LEASED / RUNNING / SUSPENDED all remain unresolved?",
        "23. Should 5.1.4 distinguish unresolved from terminally-unsatisfied dependencies?",
        "24. Should 5.1.4 expose satisfied_dependency_ids?",
        "25. Should 5.1.4 expose unresolved_dependency_ids?",
        "26. Should 5.1.4 expose failed_dependency_ids?",
        "27. Should cancelled/dead-letter/expired be separately represented or grouped as terminal-unsatisfied?",
        "28. Should 5.1.4 expose an all_dependencies_satisfied derived boolean?",
        "29. Should 5.1.4 expose has_terminal_dependency_failure?",
        "30. Should a job with zero dependencies resolve immediately as all_dependencies_satisfied=True?",
        "31. Should 5.1.4 detect missing dependency evidence?",
        "32. How should a dependency ID with no supplied job snapshot be classified?",
        "33. Should missing evidence be unresolved rather than failed?",
        "34. Should 5.1.4 perform graph cycle detection?",
        "35. If cycle detection is needed, is it local per resolution request or a later graph authority?",
        "36. Should 5.1.4 read Runtime State Store directly? Expected NO.",
        "37. Should dependency job snapshots be caller supplied? Expected YES.",
        "38. Should 5.1.4 query job persistence directly? Expected NO.",
        "39. Should 5.1.4 mutate Universal Jobs? Expected NO.",
        "40. Should 5.1.4 transition orchestration state? Expected NO.",
        "41. Should 5.1.4 determine READY/BLOCKED? Expected NO, defer to 5.1.6.",
        "42. Should 5.1.4 determine execution order? Expected NO, defer to 5.1.5.",
        "43. Should 5.1.4 enqueue/claim jobs? Expected NO.",
        "44. Should 5.1.4 dispatch handlers? Expected NO.",
        "45. Should 5.1.4 execute jobs? Expected NO.",
        "46. Should 5.1.4 import Universal Coordination Framework? Expected NO.",
        "47. Should 5.1.4 invoke pipeline coordinators? Expected NO.",
        "48. What exact immutable evidence object should dependency resolution return?",
        "49. Which fields belong in that object versus derived properties?",
        "50. What exact dependency-status classification is canonical for 5.1.4?",
        "",
        (
            "NEXT: analyze findings and freeze the exact "
            "5.1.4 Dependency Resolution boundary "
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
    "PHASE 5.1.4 DEPENDENCY RESOLUTION DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Target files:",
    len(
        TARGETS
    ),
)

print(
    "Files with dependency findings:",
    len(
        file_counts
    ),
)

print(
    "Total dependency findings:",
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
