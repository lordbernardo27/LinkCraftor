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
    / "phase_4_1_14_worker_capacity_scan.txt"
)


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

    "4.1.12_worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),

    "4.1.13_worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
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
    "worker_capacity": re.compile(
        r"\b("
        r"worker_capacity|worker capacity|"
        r"worker_capacities|worker capacities"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\bcapacity\b",
        re.IGNORECASE,
    ),

    "available_capacity": re.compile(
        r"\b("
        r"available_capacity|available capacity"
        r")\b",
        re.IGNORECASE,
    ),

    "available_slots": re.compile(
        r"\b("
        r"available_slots|available slots"
        r")\b",
        re.IGNORECASE,
    ),

    "max_concurrency": re.compile(
        r"\b("
        r"max_concurrency|maximum concurrency|"
        r"max concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "concurrency": re.compile(
        r"\bconcurrency\b",
        re.IGNORECASE,
    ),

    "active_work": re.compile(
        r"\b("
        r"active_work|active work|"
        r"active_work_count|running_work|"
        r"running work"
        r")\b",
        re.IGNORECASE,
    ),

    "active_lease": re.compile(
        r"\b("
        r"active_lease|active lease|"
        r"active_lease_count|lease_count"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_load": re.compile(
        r"\b("
        r"worker_load|worker load|"
        r"current_load|current load"
        r")\b",
        re.IGNORECASE,
    ),

    "load": re.compile(
        r"\bload\b",
        re.IGNORECASE,
    ),

    "utilization": re.compile(
        r"\b("
        r"utilization|utilisation"
        r")\b",
        re.IGNORECASE,
    ),

    "in_flight": re.compile(
        r"\b("
        r"in_flight|in-flight|inflight"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_scaling": re.compile(
        r"\b("
        r"worker_scaling|worker scaling|"
        r"scale_up|scale_down|"
        r"scaling"
        r")\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b("
        r"worker_assignment|worker assignment|"
        r"eligible_workers|eligible worker|assignable"
        r")\b",
        re.IGNORECASE,
    ),

    "leasing": re.compile(
        r"\b("
        r"worker_leasing|worker leasing|"
        r"lease_owner|lease_id|leased"
        r")\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id"
        r")\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b("
        r"worker_capability|worker capability|"
        r"capability|capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "drain": re.compile(
        r"\b("
        r"worker_drain|worker drain|"
        r"draining|drained|drain_requested"
        r")\b",
        re.IGNORECASE,
    ),

    "backpressure": re.compile(
        r"\bbackpressure\b",
        re.IGNORECASE,
    ),

    "queue_capacity": re.compile(
        r"\b("
        r"queue_capacity|queue capacity|"
        r"capacity_limit|capacity limit"
        r")\b",
        re.IGNORECASE,
    ),

    "semaphore": re.compile(
        r"\b("
        r"semaphore|boundedsemaphore"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_count": re.compile(
        r"\b("
        r"worker_count|worker count|"
        r"current_worker_count"
        r")\b",
        re.IGNORECASE,
    ),

    "resource": re.compile(
        r"\b("
        r"cpu|memory|resource|resources|"
        r"gpu"
        r")\b",
        re.IGNORECASE,
    ),

    "parallelism": re.compile(
        r"\bparallelism\b",
        re.IGNORECASE,
    ),

    "throughput": re.compile(
        r"\bthroughput\b",
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
                    "capacity",
                    "worker",
                    "load",
                    "concurrency",
                    "resource",
                    "scaling",
                    "pool",
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
                    "capacity",
                    "load",
                    "concurrency",
                    "worker",
                    "slot",
                    "resource",
                    "scale",
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
                    "queue",
                    "scaling",
                    "resource",
                    "orchestration",
                    "runtime",
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


out = [
    "PHASE 4.1.14 — WORKER CAPACITY MANAGEMENT READ-ONLY DISCOVERY SCAN",
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
        175
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — CAPACITY/LOAD CLASSES",
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
        "SECTION 5 — CAPACITY/LOAD FUNCTIONS",
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
        "SECTION 7 — DIRECT CAPACITY FINDINGS",
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
        items[:400]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 400:

        out.append(
            (
                "... "
                + str(
                    len(items) - 400
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
        "SECTION 9 — 4.1.14 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical individual Worker Capacity authority already exist?",
        "2. Is capacity currently stored on UniversalWorkerRegistration?",
        "3. Does Worker Capability currently contain capacity? (expected NO)",
        "4. Does Worker Pool currently define per-worker capacity?",
        "5. Does Worker Scaling already consume caller-supplied available_capacity?",
        "6. If so, what exactly does Scaling assume available_capacity means?",
        "7. Is available_capacity currently calculated anywhere canonically?",
        "8. Are max_concurrency/current_work concepts already present?",
        "9. Are active leases used as a proxy for active work anywhere?",
        "10. Should active_work_count and active_lease_count remain distinct?",
        "11. Should Worker Capacity own maximum concurrent work?",
        "12. Should Worker Capacity own current active work count?",
        "13. Should available slots be derived as max_concurrency - active_work_count?",
        "14. Should active lease count constrain available capacity independently?",
        "15. Should max_concurrency=0 be valid?",
        "16. Should active_work_count=0 be valid?",
        "17. Should current active work above max_concurrency be rejected as contradictory evidence?",
        "18. Should available capacity ever be negative? (expected NO)",
        "19. Should Capacity emit SATURATED / AVAILABLE states or numeric evidence only?",
        "20. Should a worker with max_concurrency=0 be representable?",
        "21. Should Capacity include worker identity?",
        "22. Should Capacity include worker_type?",
        "23. Should Capacity include capability tokens? (expected NO)",
        "24. Should Capacity include pool membership? (expected NO)",
        "25. Should Capacity include health? (expected NO)",
        "26. Should Capacity include stale state? (expected NO)",
        "27. Should Capacity include drain state? (expected NO)",
        "28. Should Capacity itself exclude draining workers? (expected NO)",
        "29. Should Capacity itself assign workers? (expected NO)",
        "30. Should Capacity itself lease jobs? (expected NO)",
        "31. Should Capacity itself scale workers? (expected NO)",
        "32. Should Scaling consume caller-composed Capacity evidence later?",
        "33. Should Assignment continue to receive caller-supplied eligible workers?",
        "34. Should Capacity matching occur before Assignment?",
        "35. Should active work represent running jobs only or all owned work?",
        "36. Should leased-but-not-running work consume a capacity slot?",
        "37. Is there repository evidence supporting that decision?",
        "38. Should Capacity expose has_available_capacity?",
        "39. Should Capacity expose available_capacity integer?",
        "40. Should Capacity expose utilization ratio? Or leave that to observability?",
        "41. Should Capacity expose saturation only as derived property?",
        "42. Should CPU/memory/GPU resource accounting be part of 4.1.14? (expected NO unless scan proves otherwise)",
        "43. Should 4.1.14 be generic work-slot capacity rather than resource scheduling?",
        "44. Should Capacity state be immutable caller-supplied evidence?",
        "45. Should Capacity maintain history? (expected NO)",
        "46. Should Capacity use wall clock? (expected NO)",
        "47. Should Capacity access Runtime State Store? (expected NO)",
        "48. Should Capacity persist state itself? (expected NO)",
        "49. Should Capacity perform filesystem/network I/O? (expected NO)",
        "50. What exact evidence should later Worker Infrastructure Certification protect?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.14 Worker Capacity Management boundary "
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
print("=" * 96)
print(
    "PHASE 4.1.14 WORKER CAPACITY MANAGEMENT SCAN COMPLETE"
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
