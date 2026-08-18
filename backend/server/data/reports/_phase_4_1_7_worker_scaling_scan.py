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
    / "phase_4_1_7_worker_scaling_scan.txt"
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
    "worker_scaling": re.compile(
        r"\b("
        r"worker_scaling|worker scaling|"
        r"scale_worker|scale workers"
        r")\b",
        re.IGNORECASE,
    ),

    "scale_up_down": re.compile(
        r"\b("
        r"scale_up|scale_down|scale up|scale down|"
        r"autoscale|autoscaling|auto scaling"
        r")\b",
        re.IGNORECASE,
    ),

    "desired_workers": re.compile(
        r"\b("
        r"desired_workers|desired worker|desired_count|"
        r"target_workers|target worker count|"
        r"worker_count"
        r")\b",
        re.IGNORECASE,
    ),

    "min_max_workers": re.compile(
        r"\b("
        r"min_workers|max_workers|minimum_workers|"
        r"maximum_workers|min worker|max worker"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b("
        r"worker_capacity|capacity|available_slots|"
        r"max_concurrency|current_concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "queue_depth": re.compile(
        r"\b("
        r"queue_depth|queue depth|backlog|"
        r"pending_jobs|pending jobs|queued_jobs"
        r")\b",
        re.IGNORECASE,
    ),

    "demand": re.compile(
        r"\b("
        r"demand|load|workload|throughput|"
        r"arrival_rate|arrival rate"
        r")\b",
        re.IGNORECASE,
    ),

    "utilization": re.compile(
        r"\b("
        r"utilization|utilisation|worker load|"
        r"load_factor|load factor"
        r")\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b("
        r"worker_health|HEALTHY|DEGRADED|UNHEALTHY|UNKNOWN"
        r")\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id|pool id"
        r")\b",
        re.IGNORECASE,
    ),

    "provision": re.compile(
        r"\b("
        r"provision|spawn worker|spawn_worker|"
        r"create worker|start worker|launch worker"
        r")\b",
        re.IGNORECASE,
    ),

    "terminate": re.compile(
        r"\b("
        r"terminate worker|terminate_worker|"
        r"kill worker|kill_worker|stop worker|"
        r"remove worker"
        r")\b",
        re.IGNORECASE,
    ),

    "shutdown_drain": re.compile(
        r"\b("
        r"shutdown_worker|worker shutdown|"
        r"drain_worker|worker drain|draining"
        r")\b",
        re.IGNORECASE,
    ),

    "cloud_scaling": re.compile(
        r"\b("
        r"autoscaling group|auto scaling group|"
        r"ec2|ecs|eks|kubernetes|pod|container|"
        r"fargate|lambda"
        r")\b",
        re.IGNORECASE,
    ),

    "resource_governance": re.compile(
        r"\b("
        r"resource governance|resource_governance|"
        r"cpu quota|memory quota|resource limit"
        r")\b",
        re.IGNORECASE,
    ),

    "backpressure": re.compile(
        r"\b("
        r"backpressure|back pressure"
        r")\b",
        re.IGNORECASE,
    ),

    "rate_limit": re.compile(
        r"\b("
        r"rate limit|rate_limit|rate limiting"
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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "scale",
                    "worker",
                    "capacity",
                    "pool",
                    "autoscal",
                    "resource",
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
                    "scale",
                    "worker",
                    "capacity",
                    "pool",
                    "provision",
                    "spawn",
                    "terminate",
                    "autoscal",
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
                    "capacity",
                    "pool",
                    "cloud",
                    "runtime",
                    "queue",
                    "resource",
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
    "PHASE 4.1.7 — WORKER SCALING READ-ONLY DISCOVERY SCAN",
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
        "SECTION 4 — SCALING-RELATED CLASSES",
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
        "SECTION 5 — SCALING-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT SCALING FINDINGS",
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
        "SECTION 9 — 4.1.7 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Universal Worker Scaling authority already exist?",
        "2. What existing code decides worker count?",
        "3. Does any active worker scaler already provision or terminate infrastructure?",
        "4. Are min_workers/max_workers modeled anywhere?",
        "5. Is desired worker count modeled anywhere?",
        "6. Is scaling driven by queue depth anywhere?",
        "7. Is scaling driven by worker utilization anywhere?",
        "8. Is scaling driven by health anywhere?",
        "9. Does Queue Backpressure already produce demand evidence useful to scaling?",
        "10. Does Queue Capacity already overlap with scaling decisions?",
        "11. Does Worker Capacity 4.1.14 need to remain the source of per-worker slot evidence?",
        "12. Does Worker Pool 4.1.9 need to remain the source of pool membership?",
        "13. Should 4.1.7 operate globally, per worker type, or per pool?",
        "14. Can scaling safely precede Worker Pool 4.1.9 in implementation?",
        "15. Should scaling consume caller-supplied current_worker_count?",
        "16. Should scaling consume caller-supplied minimum_worker_count?",
        "17. Should scaling consume caller-supplied maximum_worker_count?",
        "18. Should scaling consume caller-supplied pending_work?",
        "19. Should scaling consume caller-supplied available_capacity?",
        "20. Should health be caller-composed rather than read directly?",
        "21. What should SCALE_UP mean: one worker or target count?",
        "22. What should SCALE_DOWN mean: one worker or target count?",
        "23. Should output include desired_worker_count?",
        "24. Should output include delta?",
        "25. Should HOLD be returned when min/max boundaries forbid movement?",
        "26. Should zero demand permit scale-down to configured minimum?",
        "27. Should scale-down require caller evidence that workers are safe to remove?",
        "28. Should active leases prevent scale-down here or in Worker Drain/Shutdown?",
        "29. Should 4.1.7 ever select which worker is removed?",
        "30. Should 4.1.7 ever start/stop processes?",
        "31. Should 4.1.7 ever call cloud-provider APIs?",
        "32. What remains for Phase 10 Resource Governance?",
        "33. What deterministic scaling formula is justified by existing architecture?",
        "34. What exact immutable output contract should 4.1.7 expose?",
        "35. Which legacy scaling/provisioning components must remain untouched?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.7 Worker Scaling decision boundary "
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
    "PHASE 4.1.7 WORKER SCALING SCAN COMPLETE"
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
