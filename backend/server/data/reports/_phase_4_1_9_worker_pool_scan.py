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
    / "phase_4_1_9_worker_pool_scan.txt"
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
    "worker_pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|"
        r"workerpool|pool of workers"
        r")\b",
        re.IGNORECASE,
    ),

    "pool_id": re.compile(
        r"\b("
        r"pool_id|worker_pool_id|pool id|"
        r"worker pool id"
        r")\b",
        re.IGNORECASE,
    ),

    "pool_membership": re.compile(
        r"\b("
        r"pool membership|pool_membership|"
        r"worker membership|worker_membership|"
        r"member worker|worker member"
        r")\b",
        re.IGNORECASE,
    ),

    "default_pool": re.compile(
        r"\b("
        r"default_pool|default pool|"
        r"shared_pool|shared pool"
        r")\b",
        re.IGNORECASE,
    ),

    "dedicated_pool": re.compile(
        r"\b("
        r"dedicated_pool|dedicated pool|"
        r"isolated_pool|isolated pool|"
        r"private pool"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_group": re.compile(
        r"\b("
        r"worker_group|worker group|"
        r"worker_group_id|group of workers"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_type": re.compile(
        r"\b("
        r"worker_type|worker type"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_registration": re.compile(
        r"\b("
        r"worker_registration|worker registration|"
        r"register_worker|register worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_discovery": re.compile(
        r"\b("
        r"worker_discovery|worker discovery|"
        r"discover_worker|discover worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_assignment": re.compile(
        r"\b("
        r"worker_assignment|worker assignment|"
        r"assign_worker|assign worker|"
        r"assign_universal_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_capacity": re.compile(
        r"\b("
        r"worker_capacity|worker capacity|"
        r"available_slots|max_concurrency|"
        r"current_concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_capability": re.compile(
        r"\b("
        r"worker_capability|worker capability|"
        r"capabilities|capability set"
        r")\b",
        re.IGNORECASE,
    ),

    "workspace": re.compile(
        r"\b("
        r"workspace_id|workspace id|tenant_id|"
        r"tenant id"
        r")\b",
        re.IGNORECASE,
    ),

    "product": re.compile(
        r"\b("
        r"product_id|product id"
        r")\b",
        re.IGNORECASE,
    ),

    "queue_partition": re.compile(
        r"\b("
        r"queue_partition|queue partition|"
        r"partition_id|partition id"
        r")\b",
        re.IGNORECASE,
    ),

    "routing": re.compile(
        r"\b("
        r"routing|route worker|worker route|"
        r"routing_key|route_key"
        r")\b",
        re.IGNORECASE,
    ),

    "isolation": re.compile(
        r"\b("
        r"isolation|isolated|dedicated|shared"
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

    "shutdown": re.compile(
        r"\b("
        r"worker_shutdown|worker shutdown|"
        r"shutdown_worker|shutdown worker"
        r")\b",
        re.IGNORECASE,
    ),

    "drain": re.compile(
        r"\b("
        r"worker_drain|worker drain|"
        r"drain_worker|draining|drained"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b("
        r"heartbeat|last_heartbeat|heartbeat_at"
        r")\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b("
        r"worker_health|HEALTHY|DEGRADED|"
        r"UNHEALTHY|UNKNOWN"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_state": re.compile(
        r"\b("
        r"Runtime State Store|state_store|"
        r"runtime_state"
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
                    "pool",
                    "worker",
                    "membership",
                    "group",
                    "isolation",
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
                    "pool",
                    "worker",
                    "membership",
                    "group",
                    "assign",
                    "isolation",
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
                    "pool",
                    "queue",
                    "runtime",
                    "assignment",
                    "routing",
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
    "PHASE 4.1.9 — WORKER POOL INFRASTRUCTURE READ-ONLY DISCOVERY SCAN",
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
        "SECTION 4 — POOL-RELATED CLASSES",
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
        "SECTION 5 — POOL-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT WORKER POOL FINDINGS",
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
        "SECTION 9 — 4.1.9 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Universal Worker Pool authority already exist?",
        "2. Does any active production code already define pool_id?",
        "3. Does Worker Registration currently include pool membership?",
        "4. Does Worker Discovery filter workers by pool?",
        "5. Does Worker Assignment select a worker pool before selecting a worker?",
        "6. Does Queue Routing or Queue Partitioning already imply worker pools?",
        "7. Is any pool concept currently tied to worker_type?",
        "8. Is any pool concept tied to workspace_id or tenant_id?",
        "9. Is any pool concept tied to product_id?",
        "10. Is any pool concept tied to pipeline or stage?",
        "11. Is there an existing shared/default worker-group concept?",
        "12. Is there an existing dedicated/isolated worker-group concept?",
        "13. Should 4.1.9 define logical pools only?",
        "14. Should 4.1.9 own pool identity and immutable pool metadata?",
        "15. Should worker membership be represented separately from pool definition?",
        "16. Should membership be caller-supplied evidence or managed by a stateful authority?",
        "17. Should a worker be allowed in more than one pool simultaneously?",
        "18. Should one worker have exactly one primary pool?",
        "19. Should a default pool always exist?",
        "20. Should pool type include SHARED / DEDICATED / SYSTEM?",
        "21. Should worker_type constrain pool membership?",
        "22. Should workspace isolation be encoded in pool definition or external policy?",
        "23. Should product isolation be encoded in pool definition or external policy?",
        "24. Should Assignment 4.1.3 remain worker-selection only after caller supplies an eligible pool?",
        "25. Should Scaling 4.1.7 later operate per pool via caller-composed evidence?",
        "26. Should Shutdown 4.1.8 know anything about pool membership?",
        "27. Should Drain 4.1.12 later remove eligibility without removing pool membership?",
        "28. Should Capability 4.1.13 determine pool compatibility or only worker execution ability?",
        "29. Should Capacity 4.1.14 aggregate per pool outside 4.1.9?",
        "30. Should Heartbeats 4.1.10 contain pool identity?",
        "31. Should pool membership ever be inferred from worker_type automatically?",
        "32. Should pool identity be stable and caller-supplied?",
        "33. What validation is required for pool_id?",
        "34. What validation is required for membership identity?",
        "35. Should 4.1.9 perform registration/discovery/assignment itself?",
        "36. Should 4.1.9 provision or terminate workers?",
        "37. Should 4.1.9 mutate Queue Infrastructure?",
        "38. Should 4.1.9 persist pool state itself?",
        "39. What exact pure/stateful boundary is justified by existing architecture?",
        "40. What immutable contracts should 4.1.9 expose?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.9 Worker Pool Infrastructure boundary "
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
    "PHASE 4.1.9 WORKER POOL INFRASTRUCTURE SCAN COMPLETE"
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
