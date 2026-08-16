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
    / "phase_4_1_3_worker_assignment_scan.txt"
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

    tree = ast.parse(source)

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

    relative_parts = (
        path.relative_to(
            SERVER
        ).parts
    )

    if any(
        part in SKIP_PARTS
        for part in relative_parts
    ):
        continue

    files.append(
        path
    )


files.sort()


PATTERNS = {
    "assignment": re.compile(
        r"\b("
        r"assign_worker|assign.*worker|worker.*assign|"
        r"worker_assignment|JobWorkerAssignment"
        r")\b",
        re.IGNORECASE,
    ),

    "selection": re.compile(
        r"\b("
        r"select_worker|worker_selection|selected_worker|"
        r"choose_worker|pick_worker"
        r")\b",
        re.IGNORECASE,
    ),

    "candidate": re.compile(
        r"\b("
        r"worker_candidate|worker_candidates|candidate_worker|"
        r"eligible_worker|eligible_workers"
        r")\b",
        re.IGNORECASE,
    ),

    "round_robin": re.compile(
        r"\b("
        r"round.?robin|least.?loaded|random worker|"
        r"weighted worker|worker rotation"
        r")\b",
        re.IGNORECASE,
    ),

    "claim": re.compile(
        r"\b("
        r"claim_job|claimed_job|job claim|dequeue_job"
        r")\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b("
        r"lease_owner|lease_id|lease_started_at|"
        r"lease_expires_at|lease_job|worker lease"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch_job|dispatch.*worker|worker.*dispatch|"
        r"handler dispatch"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execute_job|run_one_job|run_one_worker_job|"
        r"worker execution"
        r")\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b("
        r"worker capability|worker_capability|"
        r"required_capabilities|capability match|"
        r"capability compatibility"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b("
        r"worker_capacity|max_concurrency|"
        r"available_slots|available slots|"
        r"current_concurrency|least_loaded"
        r")\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id"
        r")\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b("
        r"worker_health|worker health|healthy worker|"
        r"unhealthy worker"
        r")\b",
        re.IGNORECASE,
    ),

    "heartbeat_stale": re.compile(
        r"\b("
        r"worker_heartbeat|heartbeat_at|last_heartbeat|"
        r"stale_worker|stale worker"
        r")\b",
        re.IGNORECASE,
    ),

    "discovery": re.compile(
        r"\b("
        r"discover_universal_workers|"
        r"UniversalWorkerDiscovery|"
        r"DISCOVERABLE|NOT_DISCOVERABLE"
        r")\b",
        re.IGNORECASE,
    ),

    "job_identity": re.compile(
        r"\b("
        r"job_id|job_type|priority|pipeline|stage"
        r")\b",
        re.IGNORECASE,
    ),

    "persistence": re.compile(
        r"\b("
        r"save.*assignment|assignment.*save|"
        r"persist.*assignment|assignment.*persist|"
        r"worker_id.*metadata|metadata.*worker_id"
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
                "READ: " + repr(exc),
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
                "AST: " + repr(exc),
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
                    "worker",
                    "assign",
                    "candidate",
                    "selection",
                    "lease",
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
                    "worker",
                    "assign",
                    "select",
                    "candidate",
                    "claim",
                    "lease",
                    "dispatch",
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
                    "orchestration",
                    "queue",
                    "runtime_registration",
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
    "PHASE 4.1.3 — WORKER ASSIGNMENT READ-ONLY DISCOVERY SCAN",
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
        (
            "Python files scanned: "
            + str(
                len(files)
            )
        ),
        (
            "Files with findings: "
            + str(
                len(file_counts)
            )
        ),
        (
            "Total findings: "
            + str(
                len(findings)
            )
        ),
        (
            "Parse/read errors: "
            + str(
                len(parse_errors)
            )
        ),
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
        80
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — ASSIGNMENT-RELATED CLASSES",
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
        "SECTION 5 — ASSIGNMENT-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT FINDINGS",
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
        items[:175]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 175:

        out.append(
            (
                "... "
                + str(
                    len(items) - 175
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
        "SECTION 9 — 4.1.3 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical Worker Assignment authority already exist?",
        "2. Is worker selection currently coupled to dequeue/claim?",
        "3. Is assignment currently coupled to RUNNING transition?",
        "4. Is worker_id currently persisted into orchestration metadata?",
        "5. Does any existing code choose among multiple workers?",
        "6. Is any round-robin or least-loaded strategy already implemented?",
        "7. Does capability compatibility currently affect worker selection?",
        "8. Does worker capacity currently affect worker selection?",
        "9. Does worker pool identity currently affect worker selection?",
        "10. Does worker health or heartbeat freshness affect selection?",
        "11. Should 4.1.3 consume only caller-supplied eligible candidates?",
        "12. What minimal job evidence does assignment require?",
        "13. Should assignment select exactly one worker or permit NO_ASSIGNMENT?",
        "14. What deterministic tie-break belongs to 4.1.3?",
        "15. Must assignment remain separate from lease acquisition?",
        "16. Must assignment remain separate from queue claim/dequeue?",
        "17. Must assignment remain separate from dispatch/execution?",
        "18. Must assignment itself be non-persistent?",
        "19. What exact output contract should 4.1.3 expose?",
        "20. Which legacy assignment/claim components must remain untouched?",
        "",
        (
            "NEXT: analyze findings, define and freeze the "
            "4.1.3 Worker Assignment authority boundary, "
            "then implement."
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
    "PHASE 4.1.3 WORKER ASSIGNMENT SCAN COMPLETE"
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
