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
    / "phase_4_1_11_stale_worker_detection_scan.txt"
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
    "stale_worker": re.compile(
        r"\b("
        r"stale_worker|stale worker|"
        r"worker_stale|worker stale"
        r")\b",
        re.IGNORECASE,
    ),

    "stale": re.compile(
        r"\bstale\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b("
        r"heartbeat|heartbeat_at|"
        r"last_heartbeat|last_heartbeat_at"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_age": re.compile(
        r"\b("
        r"heartbeat_age|heartbeat age|"
        r"age_since_heartbeat|"
        r"seconds_since_heartbeat"
        r")\b",
        re.IGNORECASE,
    ),

    "freshness": re.compile(
        r"\b("
        r"freshness|fresh heartbeat|"
        r"heartbeat_freshness|fresh_heartbeat"
        r")\b",
        re.IGNORECASE,
    ),

    "stale_threshold": re.compile(
        r"\b("
        r"stale_threshold|stale threshold|"
        r"heartbeat_timeout|heartbeat timeout|"
        r"heartbeat_ttl|heartbeat ttl|"
        r"worker_timeout|worker timeout"
        r")\b",
        re.IGNORECASE,
    ),

    "liveness": re.compile(
        r"\b("
        r"liveness|worker_liveness|"
        r"worker liveness|is_alive|alive"
        r")\b",
        re.IGNORECASE,
    ),

    "last_seen": re.compile(
        r"\b("
        r"last_seen|last seen|"
        r"last_seen_at|seen_at"
        r")\b",
        re.IGNORECASE,
    ),

    "expiry": re.compile(
        r"\b("
        r"expired|expiry|expires_at|"
        r"timeout|timed out|timed_out"
        r")\b",
        re.IGNORECASE,
    ),

    "evaluation_time": re.compile(
        r"\b("
        r"evaluation_time|evaluated_at|"
        r"evaluation_at|now_iso|"
        r"datetime\.now|datetime\.utcnow|"
        r"time\.time"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_status": re.compile(
        r"\b("
        r"worker_status|worker status|"
        r"WorkerStatus|record_worker_status|"
        r"get_latest_worker_statuses"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_health": re.compile(
        r"\b("
        r"worker_health|worker health|"
        r"HEALTHY|DEGRADED|UNHEALTHY|UNKNOWN"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_recovery": re.compile(
        r"\b("
        r"worker_recovery|worker recovery|"
        r"RECOVERABLE|NOT_RECOVERABLE"
        r")\b",
        re.IGNORECASE,
    ),

    "lease_expiry": re.compile(
        r"\b("
        r"lease_expires_at|lease expired|"
        r"lease_expiry|lease expiry|"
        r"EXPIRED"
        r")\b",
        re.IGNORECASE,
    ),

    "job_failure": re.compile(
        r"\b("
        r"job failed|job_failed|FAILED|"
        r"failure|mark_job_failed"
        r")\b",
        re.IGNORECASE,
    ),

    "requeue": re.compile(
        r"\b("
        r"requeue|re-queue|requeued"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_registration": re.compile(
        r"\b("
        r"worker_registration|worker registration|"
        r"worker_id|worker_instance_id"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_shutdown": re.compile(
        r"\b("
        r"worker_shutdown|worker shutdown|"
        r"shutdown_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_drain": re.compile(
        r"\b("
        r"worker_drain|worker drain|"
        r"drain_worker|DRAINING|DRAINED"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|state_store|"
        r"Runtime State Store|write_json|"
        r"read_json"
        r")\b",
        re.IGNORECASE,
    ),

    "thread_loop": re.compile(
        r"\b("
        r"while True|threading|Thread\(|"
        r"asyncio\.create_task|sleep\("
        r")",
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

            lower = (
                node.name.lower()
            )

            if any(
                token in lower
                for token in (
                    "stale",
                    "heartbeat",
                    "liveness",
                    "workerstatus",
                    "worker_status",
                    "timeout",
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
                    "stale",
                    "heartbeat",
                    "liveness",
                    "alive",
                    "timeout",
                    "worker_status",
                    "last_seen",
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
                    "heartbeat",
                    "worker",
                    "health",
                    "recovery",
                    "lease",
                    "state_store",
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


file_counts = Counter(
    filename
    for _, filename, _, _
    in findings
)


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.11 — STALE WORKER DETECTION READ-ONLY DISCOVERY SCAN",
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
        "SECTION 4 — STALE/LIVENESS-RELATED CLASSES",
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
        "SECTION 5 — STALE/LIVENESS-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT STALE WORKER FINDINGS",
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
        "SECTION 9 — 4.1.11 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Stale Worker Detection authority already exist?",
        "2. Is stale-worker classification already implemented in active production code?",
        "3. Is heartbeat age already calculated anywhere?",
        "4. Is heartbeat freshness already calculated anywhere?",
        "5. Does an existing stale threshold exist?",
        "6. Does an existing heartbeat timeout/TTL exist?",
        "7. Is worker liveness currently inferred from legacy heartbeat files?",
        "8. Is worker liveness currently inferred from orchestration WorkerHeartbeat?",
        "9. Is worker liveness currently inferred from TMS WorkerStatus?",
        "10. Does any code mark workers stale after a timeout?",
        "11. Does any code mark workers offline after a timeout?",
        "12. Does any code equate stale with unhealthy?",
        "13. Does any code equate stale with failed?",
        "14. Does any code equate stale worker with expired lease?",
        "15. Does stale-worker logic currently trigger recovery?",
        "16. Does stale-worker logic currently requeue jobs?",
        "17. Does stale-worker logic currently release leases?",
        "18. Does stale-worker logic currently deregister workers?",
        "19. Does stale-worker logic currently remove Worker Pool membership?",
        "20. Does stale-worker logic currently trigger Worker Shutdown?",
        "21. Should 4.1.11 consume canonical 4.1.10 heartbeat evidence?",
        "22. Should evaluation time be caller-supplied?",
        "23. Should stale threshold be caller-supplied?",
        "24. Should stale threshold be expressed in seconds?",
        "25. Should threshold require a positive value?",
        "26. What should equality mean: ACTIVE or STALE?",
        "27. Should age < threshold mean ACTIVE?",
        "28. Should age == threshold mean STALE?",
        "29. Should age > threshold mean STALE?",
        "30. Should heartbeat_at later than evaluation time be rejected?",
        "31. Should a missing heartbeat be representable inside 4.1.11?",
        "32. If heartbeat evidence is missing, should result be UNKNOWN rather than STALE?",
        "33. Should 4.1.11 classify only ACTIVE / STALE when heartbeat exists?",
        "34. Should stale result include calculated age_seconds?",
        "35. Should result echo threshold_seconds and evaluated_at?",
        "36. Should 4.1.11 read the wall clock itself?",
        "37. Should 4.1.11 persist stale state?",
        "38. Should 4.1.11 mutate Worker Health?",
        "39. Should 4.1.11 initiate Worker Recovery?",
        "40. Should 4.1.11 ever mutate leases/jobs/registration/pools?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.11 Stale Worker Detection boundary "
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
    "PHASE 4.1.11 STALE WORKER DETECTION SCAN COMPLETE"
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
