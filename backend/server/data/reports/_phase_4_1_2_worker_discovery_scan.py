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
    / "phase_4_1_2_worker_discovery_scan.txt"
)


# ============================================================
# PROTECTED FROZEN AUTHORITIES
# ============================================================

PROTECTED = {
    "4.1.1_worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
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

    actual = ast_sha(path)

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
# DISCOVERY SEARCH SURFACE
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


for path in SERVER.rglob("*.py"):

    parts = path.relative_to(
        SERVER
    ).parts

    if any(
        part in SKIP_PARTS
        for part in parts
    ):
        continue

    files.append(path)


files.sort()


PATTERNS = {
    "discover_worker": re.compile(
        r"\b(discover_worker|discover_workers|worker discovery|worker_discovery)\b",
        re.IGNORECASE,
    ),

    "list_workers": re.compile(
        r"\b(list_workers|inspect_workers|get_workers|read_workers|workers)\b",
        re.IGNORECASE,
    ),

    "available_worker": re.compile(
        r"\b(available_worker|available workers|worker_available|worker availability)\b",
        re.IGNORECASE,
    ),

    "eligible_worker": re.compile(
        r"\b(eligible_worker|eligible workers|worker_eligible)\b",
        re.IGNORECASE,
    ),

    "enabled_disabled": re.compile(
        r"\b(enabled|disabled|is_enabled|active|inactive)\b",
        re.IGNORECASE,
    ),

    "worker_identity": re.compile(
        r"\b(worker_id|worker_instance_id|worker_type)\b",
        re.IGNORECASE,
    ),

    "worker_state": re.compile(
        r"\b(worker state|worker_state|worker status|worker_status|idle|busy)\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b(worker health|worker_health|healthy|unhealthy|degraded)\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b(worker heartbeat|worker_heartbeat|last_heartbeat|heartbeat_at|last_seen)\b",
        re.IGNORECASE,
    ),

    "stale": re.compile(
        r"\b(stale worker|stale_worker|worker stale|staleness)\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b(max_concurrency|current_concurrency|worker_capacity|available slots)\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b(worker capability|worker_capability|required_capabilities|capability)\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b(worker pool|worker_pool|pool_id)\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b(assign_worker|worker assignment|selected_worker|worker selection)\b",
        re.IGNORECASE,
    ),

    "state_store": re.compile(
        r"\b(Runtime State Store|runtime_state_store|WORKERS|worker store|worker registry)\b",
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
        path.relative_to(ROOT)
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

            if not pattern.search(line):
                continue

            counts[group] += 1

            findings.append(
                (
                    group,
                    relative,
                    line_number,
                    line.strip()[:450],
                )
            )

    try:

        tree = ast.parse(source)

    except Exception as exc:

        parse_errors.append(
            (
                relative,
                "AST: " + repr(exc),
            )
        )

        continue

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.ClassDef,
        ):

            lower = node.name.lower()

            if any(
                token in lower
                for token in (
                    "worker",
                    "discovery",
                    "registry",
                    "availability",
                    "candidate",
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
                    "worker",
                    "discover",
                    "available",
                    "eligible",
                    "candidate",
                    "registry",
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
                    "state_store",
                    "orchestration",
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
    relative
    for _, relative, _, _
    in findings
)


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.2 — WORKER DISCOVERY READ-ONLY DISCOVERY SCAN",
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
    file_counts.most_common(75),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — DISCOVERY-RELATED CLASSES",
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
        "SECTION 5 — DISCOVERY-RELATED FUNCTIONS",
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
        "SECTION 7 — DIRECT DISCOVERY FINDINGS",
        "-" * 112,
    ]
)


for group in PATTERNS:

    out.extend(
        [
            "",
            f"[{group.upper()}]",
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
        items[:150]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 150:

        out.append(
            (
                "... "
                + str(
                    len(items) - 150
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

    for filename, error in parse_errors:

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
        "SECTION 9 — 4.1.2 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does any canonical worker discovery authority already exist?",
        "2. Does any code currently enumerate registered workers?",
        "3. Is worker discovery currently persistence-backed?",
        "4. Is enabled/disabled worker state already modeled?",
        "5. Is health currently used as a discovery filter?",
        "6. Is heartbeat freshness currently used as a discovery filter?",
        "7. Is worker capacity currently used as a discovery filter?",
        "8. Are capabilities currently used as a discovery filter?",
        "9. Are pools currently used as a discovery filter?",
        "10. Is discoverability currently mixed with worker assignment?",
        "11. Is discoverability currently mixed with heartbeat/state storage?",
        "12. What should 4.1.2 accept as caller-supplied evidence?",
        "13. What exact output should 4.1.2 return?",
        "14. What ordering should discovery results use?",
        "15. What later-phase responsibilities must remain excluded?",
        "",
        (
            "NEXT: analyze discovery findings, define the exact "
            "4.1.2 authority boundary, then implement."
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
    "PHASE 4.1.2 WORKER DISCOVERY SCAN COMPLETE"
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
