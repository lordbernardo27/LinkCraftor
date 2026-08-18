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
    / "phase_4_1_10_worker_heartbeat_scan.txt"
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
    "worker_heartbeat": re.compile(
        r"\b("
        r"worker_heartbeat|worker heartbeat|"
        r"heartbeat_worker|heartbeat worker"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\bheartbeat\b",
        re.IGNORECASE,
    ),

    "heartbeat_at": re.compile(
        r"\b("
        r"heartbeat_at|last_heartbeat|"
        r"last_heartbeat_at|heartbeat_time|"
        r"heartbeat_timestamp"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_interval": re.compile(
        r"\b("
        r"heartbeat_interval|heartbeat interval|"
        r"heartbeat_period|heartbeat_frequency"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_sequence": re.compile(
        r"\b("
        r"heartbeat_sequence|heartbeat sequence|"
        r"heartbeat_seq|sequence_number|"
        r"heartbeat_counter"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_freshness": re.compile(
        r"\b("
        r"heartbeat_freshness|heartbeat freshness|"
        r"heartbeat_age|heartbeat age|"
        r"fresh heartbeat|fresh_heartbeat"
        r")\b",
        re.IGNORECASE,
    ),

    "stale_worker": re.compile(
        r"\b("
        r"stale_worker|stale worker|"
        r"worker_stale|worker stale|"
        r"stale heartbeat|stale_heartbeat"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_liveness": re.compile(
        r"\b("
        r"worker_liveness|worker liveness|"
        r"liveness|alive|is_alive"
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
        r"recover_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease_owner|lease_id|lease_started_at|"
        r"lease_expires_at|lease state|lease_state"
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
        r"drain_worker|draining|drained"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_capacity": re.compile(
        r"\b("
        r"worker_capacity|worker capacity|"
        r"available_slots|max_concurrency"
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

    "status_update": re.compile(
        r"\b("
        r"status update|status_update|"
        r"worker status|worker_status"
        r")\b",
        re.IGNORECASE,
    ),

    "timestamp": re.compile(
        r"\b("
        r"datetime\.now|datetime\.utcnow|"
        r"time\.time|monotonic|timezone\.utc"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"persist|persistence|save heartbeat|"
        r"heartbeat store|heartbeat_store|"
        r"state_store|Runtime State Store"
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

    "network": re.compile(
        r"\b("
        r"requests\.|httpx\.|aiohttp|"
        r"socket\.|websocket"
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
                    "heartbeat",
                    "worker",
                    "liveness",
                    "stale",
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
                    "heartbeat",
                    "worker",
                    "liveness",
                    "stale",
                    "alive",
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
                    "runtime",
                    "health",
                    "recovery",
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
    "PHASE 4.1.10 — WORKER HEARTBEATS READ-ONLY DISCOVERY SCAN",
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
        "SECTION 4 — HEARTBEAT-RELATED CLASSES",
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
        "SECTION 5 — HEARTBEAT-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT HEARTBEAT FINDINGS",
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
        "SECTION 9 — 4.1.10 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Universal Worker Heartbeat authority already exist?",
        "2. Does active production code currently emit worker heartbeats?",
        "3. Does any worker heartbeat contract already exist?",
        "4. What worker identity is attached to heartbeat evidence?",
        "5. Is worker_id alone used anywhere, or worker_id + worker_instance_id?",
        "6. Are heartbeat timestamps currently caller-supplied or generated internally?",
        "7. Is there an existing heartbeat sequence/counter?",
        "8. Is there an existing heartbeat interval contract?",
        "9. Is there an existing duplicate-heartbeat rule?",
        "10. Is there an existing out-of-order heartbeat rule?",
        "11. Is there any existing freshness calculation?",
        "12. Is stale-worker detection already implemented anywhere?",
        "13. Does any existing heartbeat code classify Worker Health?",
        "14. Does any existing heartbeat code trigger Worker Recovery?",
        "15. Does any existing heartbeat code release leases?",
        "16. Does any existing heartbeat code requeue jobs?",
        "17. Does any existing heartbeat code alter Worker Registration?",
        "18. Does any existing heartbeat code alter Worker Pool membership?",
        "19. Does any heartbeat state persist in Runtime State Store?",
        "20. Is heartbeat production tied to a background thread or async loop?",
        "21. Is heartbeat publication network-based anywhere?",
        "22. Should 4.1.10 define heartbeat evidence only?",
        "23. Should heartbeat timestamps be timezone-aware UTC?",
        "24. Should timestamps be caller-supplied for deterministic purity?",
        "25. Should heartbeat evidence include a strictly increasing sequence?",
        "26. Should duplicate sequence numbers be invalid?",
        "27. Should lower sequence numbers be invalid/out-of-order?",
        "28. Should sequence ordering be validated only when prior heartbeat is supplied?",
        "29. Should heartbeat interval be part of heartbeat evidence or external configuration?",
        "30. Should heartbeat payload include worker_type?",
        "31. Should heartbeat consume immutable Worker Registration identity?",
        "32. Should heartbeat include pool_id?",
        "33. Should heartbeat include Worker Health?",
        "34. Should heartbeat include capacity/capability data?",
        "35. Should heartbeat freshness belong exclusively to 4.1.11?",
        "36. Should missing heartbeat mean anything inside 4.1.10?",
        "37. Should 4.1.10 ever mark a worker stale?",
        "38. Should 4.1.10 ever mark a worker unhealthy?",
        "39. Should 4.1.10 ever initiate recovery?",
        "40. Should 4.1.10 ever mutate Runtime State Store directly?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.10 Worker Heartbeat evidence boundary "
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
    "PHASE 4.1.10 WORKER HEARTBEAT SCAN COMPLETE"
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
