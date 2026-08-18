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
    / "phase_4_1_12_worker_drain_scan.txt"
)


# ============================================================
# PROTECTED FROZEN AUTHORITIES
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

    "3.1.15_queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
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
# SEARCH SURFACE
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
    "worker_drain": re.compile(
        r"\b("
        r"worker_drain|worker drain|"
        r"drain_worker|drain worker"
        r")\b",
        re.IGNORECASE,
    ),

    "draining": re.compile(
        r"\bDRAINING\b|\bdraining\b",
        re.IGNORECASE,
    ),

    "drained": re.compile(
        r"\bDRAINED\b|\bdrained\b",
        re.IGNORECASE,
    ),

    "drain_requested": re.compile(
        r"\b("
        r"drain_requested|drain requested|"
        r"request_drain|begin_drain|"
        r"start_drain"
        r")\b",
        re.IGNORECASE,
    ),

    "drain_complete": re.compile(
        r"\b("
        r"drain_complete|drain complete|"
        r"drain_completed|drain finished|"
        r"drain_finished"
        r")\b",
        re.IGNORECASE,
    ),

    "admission": re.compile(
        r"\b("
        r"admission|admit|accept_new_work|"
        r"accepting_new_work|new work|"
        r"new_assignment|new assignments"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_assignment": re.compile(
        r"\b("
        r"worker_assignment|worker assignment|"
        r"assign_worker|assigned worker|"
        r"ASSIGNED"
        r")\b",
        re.IGNORECASE,
    ),

    "active_work": re.compile(
        r"\b("
        r"active_work|active work|"
        r"active_work_count|in_flight|"
        r"inflight|running_work"
        r")\b",
        re.IGNORECASE,
    ),

    "active_lease": re.compile(
        r"\b("
        r"active_lease|active lease|"
        r"active_lease_count|lease_count|"
        r"lease_owner|lease_id"
        r")\b",
        re.IGNORECASE,
    ),

    "shutdown": re.compile(
        r"\b("
        r"worker_shutdown|worker shutdown|"
        r"shutdown_requested|shutdown ready|"
        r"shutdown_ready"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_lifecycle": re.compile(
        r"\b("
        r"RuntimeLifecycle|RuntimeLifecyclePhase|"
        r"runtime lifecycle|lifecycle phase"
        r")\b",
        re.IGNORECASE,
    ),

    "queue_drain": re.compile(
        r"\b("
        r"queue_drain|queue drain|"
        r"drain_queue|drain queue"
        r")\b",
        re.IGNORECASE,
    ),

    "graceful_shutdown": re.compile(
        r"\b("
        r"graceful_shutdown|graceful shutdown|"
        r"graceful_stop|graceful stop"
        r")\b",
        re.IGNORECASE,
    ),

    "stop_accepting": re.compile(
        r"\b("
        r"stop_accepting|stop accepting|"
        r"reject_new|reject new|"
        r"no_new_work|no new work"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id|"
        r"pool membership"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_scaling": re.compile(
        r"\b("
        r"worker_scaling|worker scaling|"
        r"scale_down|scale down|"
        r"scaling"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_health": re.compile(
        r"\b("
        r"worker_health|worker health|"
        r"HEALTHY|DEGRADED|UNHEALTHY"
        r")\b",
        re.IGNORECASE,
    ),

    "stale_worker": re.compile(
        r"\b("
        r"stale_worker|stale worker|"
        r"worker_stale|worker stale"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_recovery": re.compile(
        r"\b("
        r"worker_recovery|worker recovery|"
        r"RECOVERABLE|recover_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_capacity": re.compile(
        r"\b("
        r"worker_capacity|worker capacity|"
        r"available_slots|max_concurrency|"
        r"capacity"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_capability": re.compile(
        r"\b("
        r"worker_capability|worker capability|"
        r"capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|"
        r"Runtime State Store|write_json|"
        r"save_state"
        r")\b",
        re.IGNORECASE,
    ),

    "orchestration": re.compile(
        r"\b("
        r"orchestration|orchestrator"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

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
                + repr(exc),
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
                + repr(exc),
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

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "drain",
                    "shutdown",
                    "lifecycle",
                    "worker",
                    "admission",
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
                    "drain",
                    "shutdown",
                    "stop_accept",
                    "admission",
                    "worker",
                    "graceful",
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

            lower = module.lower()

            if any(
                token in lower
                for token in (
                    "worker",
                    "shutdown",
                    "lifecycle",
                    "queue",
                    "orchestration",
                    "state_store",
                )
            ):

                imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )


file_counts = Counter(
    filename
    for _, filename, _, _
    in findings
)


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.12 — WORKER DRAIN READ-ONLY DISCOVERY SCAN",
    "=" * 112,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 112,
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
        "-" * 112,
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
        "-" * 112,
        "",
    ]
)


for index, (
    filename,
    hits,
) in enumerate(
    file_counts.most_common(
        120
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — DRAIN/SHUTDOWN/LIFECYCLE CLASSES",
        "-" * 112,
        "",
    ]
)


if classes:

    for filename, line, name in sorted(
        classes
    ):

        out.append(
            f"{filename}:{line} class {name}"
        )

else:

    out.append(
        "NONE FOUND"
    )


out.extend(
    [
        "",
        "SECTION 5 — DRAIN/SHUTDOWN/LIFECYCLE FUNCTIONS",
        "-" * 112,
        "",
    ]
)


if functions:

    for filename, line, name in sorted(
        functions
    ):

        out.append(
            f"{filename}:{line} {name}()"
        )

else:

    out.append(
        "NONE FOUND"
    )


out.extend(
    [
        "",
        "SECTION 6 — RELEVANT IMPORT RELATIONSHIPS",
        "-" * 112,
        "",
    ]
)


if imports:

    for filename, line, module in sorted(
        imports
    ):

        out.append(
            f"{filename}:{line} -> {module}"
        )

else:

    out.append(
        "NONE FOUND"
    )


out.extend(
    [
        "",
        "SECTION 7 — DIRECT WORKER DRAIN FINDINGS",
        "-" * 112,
    ]
)


for group in PATTERNS:

    out.extend(
        [
            "",
            "[" + group.upper() + "]",
            "~" * 112,
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
        items[:300]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 300:

        out.append(
            (
                "... "
                + str(
                    len(items) - 300
                )
                + " additional findings omitted"
            )
        )


out.extend(
    [
        "",
        "SECTION 8 — PARSE / READ ERRORS",
        "-" * 112,
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
        "SECTION 9 — 4.1.12 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical individual Worker Drain authority already exist?",
        "2. Does the runtime-wide lifecycle already use DRAINING?",
        "3. Does any code already define a DRAINED worker state?",
        "4. Does any code already define drain_requested?",
        "5. Does any code already define drain_complete?",
        "6. Does any code already prevent new Worker Assignment during drain?",
        "7. Does any code already prevent new Worker Leasing during drain?",
        "8. Does any code allow existing work to complete during drain?",
        "9. Is drain currently tied directly to Worker Shutdown?",
        "10. Is drain currently tied directly to Scaling scale-down?",
        "11. Is drain currently tied directly to Worker Pool membership removal?",
        "12. Is drain currently tied directly to Health?",
        "13. Is drain currently tied directly to Stale Worker Detection?",
        "14. Is drain currently tied directly to Recovery?",
        "15. Is any queue-level drain mechanism present?",
        "16. Is any runtime-wide graceful shutdown mechanism present?",
        "17. Does runtime lifecycle DRAINING mean whole-runtime rather than worker-level drain?",
        "18. Should 4.1.12 remain explicitly worker-scoped?",
        "19. Should canonical drain states be ACTIVE / DRAINING / DRAINED?",
        "20. Should drain_requested=false mean ACTIVE?",
        "21. Should drain_requested=true + active work > 0 mean DRAINING?",
        "22. Should drain_requested=true + active leases > 0 mean DRAINING?",
        "23. Should zero active work + zero active leases mean DRAINED?",
        "24. Should DRAINED require drain_requested=true?",
        "25. Should active_work_count be caller-supplied?",
        "26. Should active_lease_count be caller-supplied?",
        "27. Should 4.1.12 prevent new assignment itself or only produce eligibility evidence?",
        "28. Should Assignment later consume drain evidence rather than import Drain directly?",
        "29. Should Leasing later consume drain evidence rather than import Drain directly?",
        "30. Should Worker Shutdown consume DRAINED/drain_complete evidence?",
        "31. Should Worker Drain ever release active leases?",
        "32. Should Worker Drain ever cancel/requeue running work?",
        "33. Should Worker Drain ever terminate a worker?",
        "34. Should Worker Drain ever remove Worker Pool membership?",
        "35. Should Worker Drain ever mutate Worker Registration?",
        "36. Should Worker Drain ever modify Worker Health?",
        "37. Should Worker Drain ever invoke Worker Recovery?",
        "38. Should Worker Drain ever perform Scaling?",
        "39. Should Worker Drain persist state itself?",
        "40. Should Worker Drain access Runtime State Store directly?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.12 Worker Drain boundary before implementation."
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
print("=" * 96)
print(
    "PHASE 4.1.12 WORKER DRAIN SCAN COMPLETE"
)
print("=" * 96)

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
