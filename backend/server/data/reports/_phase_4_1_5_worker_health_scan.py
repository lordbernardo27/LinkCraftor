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
    / "phase_4_1_5_worker_health_scan.txt"
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
    "worker_health": re.compile(
        r"\b("
        r"worker_health|worker health|"
        r"health_status|health status"
        r")\b",
        re.IGNORECASE,
    ),

    "healthy": re.compile(
        r"\b("
        r"healthy|unhealthy|degraded|unavailable"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b("
        r"worker_heartbeat|heartbeat_at|"
        r"last_heartbeat|last_seen|heartbeat"
        r")\b",
        re.IGNORECASE,
    ),

    "stale": re.compile(
        r"\b("
        r"stale_worker|stale worker|"
        r"staleness|heartbeat timeout"
        r")\b",
        re.IGNORECASE,
    ),

    "liveness": re.compile(
        r"\b("
        r"liveness|alive|dead worker|"
        r"worker alive|worker dead"
        r")\b",
        re.IGNORECASE,
    ),

    "readiness": re.compile(
        r"\b("
        r"readiness|ready worker|worker ready|"
        r"ready_to_run|ready to run"
        r")\b",
        re.IGNORECASE,
    ),

    "status": re.compile(
        r"\b("
        r"WorkerStatus|worker_status|worker status|"
        r"ACTIVE|IDLE|BUSY|OFFLINE|FAILED"
        r")\b",
        re.IGNORECASE,
    ),

    "error_rate": re.compile(
        r"\b("
        r"error_rate|failure_rate|failure rate|"
        r"consecutive_failures|consecutive failures"
        r")\b",
        re.IGNORECASE,
    ),

    "latency": re.compile(
        r"\b("
        r"latency|response_time|response time|"
        r"processing_time|processing time"
        r")\b",
        re.IGNORECASE,
    ),

    "resource_pressure": re.compile(
        r"\b("
        r"cpu|memory|resource pressure|"
        r"resource_pressure|load average"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b("
        r"worker_capacity|max_concurrency|"
        r"available_slots|current_concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\b("
        r"worker recovery|worker_recovery|"
        r"recover_worker|restart_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b("
        r"assign_universal_worker|"
        r"UniversalWorkerAssignment|"
        r"eligible worker|assignable"
        r")\b",
        re.IGNORECASE,
    ),

    "leasing": re.compile(
        r"\b("
        r"UniversalWorkerLease|"
        r"lease_owner|lease_id|"
        r"lease_expires_at"
        r")\b",
        re.IGNORECASE,
    ),

    "state_store": re.compile(
        r"\b("
        r"runtime_state_store|Runtime State Store|"
        r"WORKERS|worker registry"
        r")\b",
        re.IGNORECASE,
    ),

    "health_endpoint": re.compile(
        r"\b("
        r"health_check|healthcheck|health endpoint|"
        r"/health|worker_health"
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
                    "health",
                    "worker",
                    "heartbeat",
                    "status",
                    "liveness",
                    "readiness",
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
                    "health",
                    "heartbeat",
                    "stale",
                    "alive",
                    "ready",
                    "worker",
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
                    "heartbeat",
                    "orchestration",
                    "state_store",
                    "health",
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
    "PHASE 4.1.5 — WORKER HEALTH READ-ONLY DISCOVERY SCAN",
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
        90
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — HEALTH-RELATED CLASSES",
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
        "SECTION 5 — HEALTH-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT HEALTH FINDINGS",
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
        items[:200]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 200:

        out.append(
            (
                "... "
                + str(
                    len(items) - 200
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
        "SECTION 9 — 4.1.5 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Worker Health authority already exist?",
        "2. Which worker health/status enums already exist?",
        "3. Are HEALTHY, DEGRADED, UNHEALTHY or UNAVAILABLE already modeled?",
        "4. Is health currently derived directly from heartbeat age?",
        "5. Is liveness currently conflated with health?",
        "6. Is readiness currently conflated with health?",
        "7. Are ACTIVE/IDLE/BUSY/OFFLINE operational states rather than health states?",
        "8. What caller-supplied health evidence already exists?",
        "9. Are error rate or consecutive failures currently tracked?",
        "10. Are latency signals currently tracked?",
        "11. Are resource-pressure signals currently tracked?",
        "12. Does capacity currently influence health anywhere?",
        "13. Does assignment currently inspect health?",
        "14. Does leasing currently inspect health?",
        "15. Does any active health function mutate worker state?",
        "16. Does any health function trigger restart/recovery?",
        "17. Does any health function access Runtime State Store?",
        "18. Should 4.1.5 classify caller-supplied health evidence only?",
        "19. Should heartbeat freshness remain entirely with 4.1.10/4.1.11?",
        "20. Should worker availability remain distinct from health?",
        "21. What exact health states should be canonical?",
        "22. What deterministic precedence should multiple health signals use?",
        "23. Should UNKNOWN/INSUFFICIENT_EVIDENCE exist?",
        "24. What exact output contract should 4.1.5 expose?",
        "25. Which recovery/remediation behavior must remain excluded?",
        "",
        (
            "NEXT: analyze findings, define the exact "
            "4.1.5 Worker Health evidence model and "
            "classification boundary, then implement."
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
    "PHASE 4.1.5 WORKER HEALTH SCAN COMPLETE"
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
