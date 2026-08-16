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
    / "phase_4_1_6_worker_recovery_scan.txt"
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

    "3.1.15_queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_attempts": (
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",
        "2662BC9A968D3F37B9072FA9551A70681E5CE9BEB78E65DAF6550580893DEE24",
    ),

    "queue_recovery": (
        ROOT / "backend/server/runtime/universal_queue/recovery.py",
        "D7AA19721DEFB1D40A24A22EBA04BDA776216520CFB31B9FAA1309242F1CF650",
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
    "worker_recovery": re.compile(
        r"\b("
        r"worker_recovery|worker recovery|"
        r"recover_worker|recover worker"
        r")\b",
        re.IGNORECASE,
    ),

    "queue_recovery": re.compile(
        r"\b("
        r"queue_recovery|queue recovery|"
        r"recover_queue|recover.*queue"
        r")\b",
        re.IGNORECASE,
    ),

    "requeue": re.compile(
        r"\b("
        r"requeue|re-queue|enqueue again|"
        r"return.*queue|queue.*restore"
        r")\b",
        re.IGNORECASE,
    ),

    "retry": re.compile(
        r"\b("
        r"retry|attempts|maximum_attempts|"
        r"max_attempts|retry_policy"
        r")\b",
        re.IGNORECASE,
    ),

    "lease_expiry": re.compile(
        r"\b("
        r"lease_expires_at|expired_lease|"
        r"lease expired|lease expiration|"
        r"UniversalWorkerLeaseState.EXPIRED"
        r")\b",
        re.IGNORECASE,
    ),

    "lease_release": re.compile(
        r"\b("
        r"release.*lease|lease.*release|"
        r"clear.*lease|lease_owner.*None"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_stale": re.compile(
        r"\b("
        r"heartbeat|stale worker|stale_worker|"
        r"last_heartbeat|heartbeat_at|"
        r"last_seen"
        r")\b",
        re.IGNORECASE,
    ),

    "health_failure": re.compile(
        r"\b("
        r"UNHEALTHY|worker health|worker_health|"
        r"critical_failure_present|"
        r"health_check_passed"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_failure": re.compile(
        r"\b("
        r"worker failed|worker_failure|"
        r"failed worker|worker crashed|"
        r"worker crash|worker disappeared|"
        r"orphaned worker|orphaned job"
        r")\b",
        re.IGNORECASE,
    ),

    "running_leased": re.compile(
        r"\b("
        r"LEASED|RUNNING|"
        r"UniversalJobStatus.LEASED|"
        r"UniversalJobStatus.RUNNING"
        r")\b",
        re.IGNORECASE,
    ),

    "claim": re.compile(
        r"\b("
        r"claim_job|dequeue_job|claimed_job|"
        r"claim.*lease|lease.*claim"
        r")\b",
        re.IGNORECASE,
    ),

    "failure_transition": re.compile(
        r"\b("
        r"FAILED|mark.*failed|fail_job|"
        r"failed_at|error_code|error_message"
        r")\b",
        re.IGNORECASE,
    ),

    "dead_letter": re.compile(
        r"\b("
        r"dead.?letter|DEAD_LETTER|dlq"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execute_job|run_one_job|"
        r"dispatch_job|runtime handler|"
        r"dispatch_registered_runtime_handler"
        r")\b",
        re.IGNORECASE,
    ),

    "ownership": re.compile(
        r"\b("
        r"lease_owner|worker_id|"
        r"worker_instance_id|ownership|owner"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"save_job|update_job|persist|"
        r"state_store|Runtime State Store|"
        r"job_store"
        r")\b",
        re.IGNORECASE,
    ),

    "restart_shutdown": re.compile(
        r"\b("
        r"restart_worker|restart worker|"
        r"shutdown_worker|shutdown worker|"
        r"terminate_worker|kill worker"
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
                    "recover",
                    "retry",
                    "lease",
                    "worker",
                    "failure",
                    "orphan",
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
                    "recover",
                    "retry",
                    "requeue",
                    "lease",
                    "worker",
                    "fail",
                    "orphan",
                    "restart",
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
                    "queue",
                    "recovery",
                    "lease",
                    "job",
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
    "PHASE 4.1.6 — WORKER RECOVERY READ-ONLY DISCOVERY SCAN",
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
        100
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — RECOVERY-RELATED CLASSES",
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
        "SECTION 5 — RECOVERY-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT RECOVERY FINDINGS",
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
        items[:250]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 250:

        out.append(
            (
                "... "
                + str(
                    len(items) - 250
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
        "SECTION 9 — 4.1.6 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Universal Worker Recovery authority already exist?",
        "2. What active code currently recovers worker-owned jobs?",
        "3. Is any existing recovery tied specifically to Queue Recovery?",
        "4. Is worker recovery currently coupled directly to requeue?",
        "5. Is worker recovery currently coupled to retry attempts?",
        "6. Is worker recovery currently coupled to FAILED status?",
        "7. Is worker recovery currently coupled to DEAD_LETTER?",
        "8. Is expired lease evidence currently enough to trigger recovery?",
        "9. Is UNHEALTHY health evidence currently enough to trigger recovery?",
        "10. Is missing heartbeat/stale evidence currently enough to trigger recovery?",
        "11. Which code currently clears lease_owner/lease_id?",
        "12. Which code currently changes LEASED/RUNNING jobs after worker loss?",
        "13. Which code currently increments attempts during recovery?",
        "14. Which code currently decides whether another attempt is permitted?",
        "15. Are retryability and recoverability distinct in current architecture?",
        "16. Is job idempotency considered during recovery anywhere?",
        "17. Is duplicate-execution prevention considered during recovery?",
        "18. Does any active recovery code restart or terminate the worker itself?",
        "19. Does any recovery authority mutate queue membership directly?",
        "20. Does any recovery authority access Runtime State Store?",
        "21. Should 4.1.6 produce recovery disposition/evidence rather than mutate jobs?",
        "22. What caller-supplied facts are minimally required?",
        "23. Should recovery distinguish RECOVERABLE / NOT_RECOVERABLE / NO_ACTION?",
        "24. Should ownership-loss evidence be required before permitting recovery?",
        "25. Should active unexpired lease block recovery?",
        "26. Should an expired lease alone permit recovery or only signal ownership loss?",
        "27. Should health classification influence recovery directly or only as caller evidence?",
        "28. What must remain owned by Universal Job Attempts?",
        "29. What must remain owned by Queue Recovery?",
        "30. What must remain owned by Phase 9 Reliability & Recovery?",
        "31. What exact immutable output contract should 4.1.6 expose?",
        "32. Which legacy recovery components must remain untouched?",
        "",
        (
            "NEXT: analyze evidence and freeze the "
            "4.1.6 Worker Recovery decision boundary "
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
    "PHASE 4.1.6 WORKER RECOVERY SCAN COMPLETE"
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
