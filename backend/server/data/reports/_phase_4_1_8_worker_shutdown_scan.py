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
    / "phase_4_1_8_worker_shutdown_scan.txt"
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
    "worker_shutdown": re.compile(
        r"\b("
        r"worker_shutdown|worker shutdown|"
        r"shutdown_worker|shutdown worker"
        r")\b",
        re.IGNORECASE,
    ),

    "shutdown": re.compile(
        r"\b("
        r"shutdown|shutting down|shut down"
        r")\b",
        re.IGNORECASE,
    ),

    "graceful_shutdown": re.compile(
        r"\b("
        r"graceful shutdown|graceful_shutdown|"
        r"graceful stop|graceful_stop"
        r")\b",
        re.IGNORECASE,
    ),

    "terminate": re.compile(
        r"\b("
        r"terminate|termination|terminated|"
        r"terminate_worker|kill_worker|kill worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_stop": re.compile(
        r"\b("
        r"stop_worker|stop worker|"
        r"worker_stop|worker stop"
        r")\b",
        re.IGNORECASE,
    ),

    "exit": re.compile(
        r"\b("
        r"worker exit|worker_exit|exit event|"
        r"exit_event|exit_requested|"
        r"shutdown_requested"
        r")\b",
        re.IGNORECASE,
    ),

    "signal": re.compile(
        r"\b("
        r"SIGTERM|SIGINT|signal\.signal|"
        r"signal handler|signal_handler"
        r")\b",
        re.IGNORECASE,
    ),

    "drain": re.compile(
        r"\b("
        r"drain|draining|drained|"
        r"worker_drain|drain_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "active_work": re.compile(
        r"\b("
        r"active_job|active job|current_job|"
        r"current job|in_flight|in-flight|"
        r"running_job|running job"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease_owner|lease_id|lease_expires_at|"
        r"active lease|release lease|"
        r"release_universal_worker_lease"
        r")\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b("
        r"assignment|assign worker|"
        r"assign_universal_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "requeue": re.compile(
        r"\b("
        r"requeue|re-queue|enqueue again|"
        r"return.*queue"
        r")\b",
        re.IGNORECASE,
    ),

    "cancel": re.compile(
        r"\b("
        r"cancel job|cancel_job|CANCELLED|"
        r"cancelled_at"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_registration": re.compile(
        r"\b("
        r"worker registration|"
        r"worker_registration|"
        r"register_worker|deregister|"
        r"unregister"
        r")\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|"
        r"pool membership|pool_membership"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b("
        r"heartbeat|last_heartbeat|"
        r"heartbeat_at"
        r")\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b("
        r"worker_health|HEALTHY|"
        r"DEGRADED|UNHEALTHY|UNKNOWN"
        r")\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\b("
        r"worker_recovery|worker recovery|"
        r"recover_worker|recover worker"
        r")\b",
        re.IGNORECASE,
    ),

    "scaling": re.compile(
        r"\b("
        r"worker_scaling|worker scaling|"
        r"SCALE_UP|SCALE_DOWN"
        r")\b",
        re.IGNORECASE,
    ),

    "process": re.compile(
        r"\b("
        r"subprocess|Popen|Process\(|"
        r"multiprocessing|process\.terminate|"
        r"process\.kill"
        r")\b",
        re.IGNORECASE,
    ),

    "thread_executor": re.compile(
        r"\b("
        r"ThreadPoolExecutor|"
        r"ProcessPoolExecutor|executor.shutdown"
        r")\b",
        re.IGNORECASE,
    ),

    "state_store": re.compile(
        r"\b("
        r"state_store|Runtime State Store|"
        r"get_runtime_state_store_registry"
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

                counts[group] += 1

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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "shutdown",
                    "drain",
                    "worker",
                    "terminate",
                    "lifecycle",
                    "stop",
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
                    "shutdown",
                    "drain",
                    "worker",
                    "terminate",
                    "kill",
                    "stop",
                    "exit",
                    "signal",
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
                    "worker",
                    "shutdown",
                    "runtime",
                    "queue",
                    "lease",
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
    "PHASE 4.1.8 — WORKER SHUTDOWN READ-ONLY DISCOVERY SCAN",
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
        "SECTION 4 — SHUTDOWN-RELATED CLASSES",
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
        "SECTION 5 — SHUTDOWN-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT SHUTDOWN FINDINGS",
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
        "SECTION 9 — 4.1.8 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Universal Worker Shutdown authority already exist?",
        "2. What existing code currently stops or terminates workers?",
        "3. Is shutdown currently a signal, process operation, state transition, or combination?",
        "4. Does any active code model graceful worker shutdown?",
        "5. Does any active code model shutdown_requested separately from shutdown_complete?",
        "6. Is shutdown coupled directly to process termination anywhere?",
        "7. Is shutdown coupled to SIGTERM/SIGINT handling anywhere?",
        "8. Is shutdown coupled to active job ownership anywhere?",
        "9. Is shutdown coupled to lease release anywhere?",
        "10. Is shutdown coupled to job requeue anywhere?",
        "11. Is shutdown coupled to job cancellation anywhere?",
        "12. Is shutdown coupled to worker deregistration anywhere?",
        "13. Is shutdown coupled to Worker Pool removal anywhere?",
        "14. Is shutdown coupled to heartbeat deletion anywhere?",
        "15. Is shutdown coupled to Worker Health status anywhere?",
        "16. Is shutdown coupled to Worker Recovery anywhere?",
        "17. Is shutdown coupled to Worker Scaling anywhere?",
        "18. What semantics must remain owned by 4.1.12 Worker Drain?",
        "19. Should shutdown consume caller-supplied drain_complete evidence?",
        "20. Should shutdown consume caller-supplied active_work_count?",
        "21. Should shutdown consume caller-supplied active_lease_count?",
        "22. Should shutdown consume caller-supplied shutdown_requested?",
        "23. Should shutdown distinguish REQUESTED / BLOCKED / READY?",
        "24. Should shutdown ever issue the OS/process termination itself?",
        "25. Should shutdown ever release a lease?",
        "26. Should shutdown ever cancel or requeue a job?",
        "27. Should shutdown ever select work for recovery?",
        "28. Should shutdown ever deregister the worker?",
        "29. Should shutdown ever remove Worker Pool membership?",
        "30. Should shutdown ever remove heartbeat state?",
        "31. Is forced shutdown part of 4.1.8 or a later reliability/emergency authority?",
        "32. What should happen when shutdown is requested but active work remains?",
        "33. What should happen when shutdown is requested and drain is complete?",
        "34. What should happen when shutdown has not been requested?",
        "35. Should an unhealthy worker automatically imply shutdown?",
        "36. Should a scale-down decision automatically imply shutdown?",
        "37. Should shutdown output be immutable permission/state evidence only?",
        "38. What exact deterministic precedence is justified?",
        "39. What exact immutable output contract should 4.1.8 expose?",
        "40. Which legacy shutdown/process-control components must remain untouched?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.8 Worker Shutdown decision boundary "
            "before implementation."
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(out),
    encoding="utf-8",
)


print()
print("=" * 96)
print(
    "PHASE 4.1.8 WORKER SHUTDOWN SCAN COMPLETE"
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
