from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

BACKEND_SERVER = (
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
    / "phase_4_1_1_worker_registration_discovery_scan.txt"
)


# ============================================================
# FROZEN UPSTREAM PROTECTION
# ============================================================

PROTECTED = {
    "3.1.1 creation": (
        ROOT / "backend/server/runtime/universal_queue/creation.py",
        "5ED908A9AFB9D102915EC1A2C8DA1D4B97D8A6CC2FDDCE3CB2EDF4E6159590BD",
    ),

    "3.1.2 scheduling": (
        ROOT / "backend/server/runtime/universal_queue/scheduling.py",
        "61563B1AA20A9C419A7B9BADC7AC9A7632835E2C8FC04AF42A9A86860B6CA0AC",
    ),

    "3.1.3 prioritization": (
        ROOT / "backend/server/runtime/universal_queue/prioritization.py",
        "C3C34C37CB6D30B5BCB22C07B2E26F825F97D7E76DEEDC6476954522B8211680",
    ),

    "3.1.4 routing": (
        ROOT / "backend/server/runtime/universal_queue/routing.py",
        "99AEEA931EC1DC4533CEE7A4E0BC07EA01FF120792A3BCC92C41CE9C253E6502",
    ),

    "3.1.5 balancing": (
        ROOT / "backend/server/runtime/universal_queue/balancing.py",
        "6811E385C802B743411534DBEE00BB65C51A59353A6491327EBFB230AB506CD5",
    ),

    "3.1.6 partitioning": (
        ROOT / "backend/server/runtime/universal_queue/partitioning.py",
        "E01247DECCAD5734B57CAE832D916727AE6D0F8AC02871E5F7CE631DE28B0575",
    ),

    "3.1.7 recovery": (
        ROOT / "backend/server/runtime/universal_queue/recovery.py",
        "D7AA19721DEFB1D40A24A22EBA04BDA776216520CFB31B9FAA1309242F1CF650",
    ),

    "3.1.8 dead_letter": (
        ROOT / "backend/server/runtime/universal_queue/dead_letter.py",
        "0628EBEF79EB8F2F7E0D9CF55D84B93FD5B66AAA36702D25699AF3E4DCC6D1B4",
    ),

    "3.1.9 cleanup": (
        ROOT / "backend/server/runtime/universal_queue/cleanup.py",
        "406EC0488C01742FAF8B551335157B315B04A4D4276D4A6E6CD121D4B7FF329F",
    ),

    "3.1.10 backpressure": (
        ROOT / "backend/server/runtime/universal_queue/backpressure.py",
        "AA8A1C29D832AF8BFA01703734D40CBB7C0D9F75D6DA67D407D398AE296BEE16",
    ),

    "3.1.11 capacity": (
        ROOT / "backend/server/runtime/universal_queue/capacity_limits.py",
        "AFB3ADC980D432F329FD76E471EDB8DA571E2ED00708F37B04D888BFB178E8A5",
    ),

    "3.1.12 fairness": (
        ROOT / "backend/server/runtime/universal_queue/fairness.py",
        "905AB94AC692D343489CD6840A7AFDEE166A0BA6832366BCB9D4F9841BDEB0B1",
    ),

    "3.1.13 rate_limiting": (
        ROOT / "backend/server/runtime/universal_queue/rate_limiting.py",
        "879EF24F1FA0DC36D2F92619C64085913DC4F38A9E0CDF001B92FAE7DC32E598",
    ),

    "3.1.14 deduplication": (
        ROOT / "backend/server/runtime/universal_queue/deduplication.py",
        "F55FD3543558FEAC3C3D681C9CD8500F9EBE685CA349F298625C28C934962930",
    ),

    "3.1.15 certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_status": (
        ROOT / "backend/server/runtime/universal_jobs/status.py",
        "4636EF770005A6CCC84A37596622880C2244D4C12FFDEDAAC02078C20AA29EEE",
    ),

    "job_attempts": (
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",
        "2662BC9A968D3F37B9072FA9551A70681E5CE9BEB78E65DAF6550580893DEE24",
    ),
}


def ast_sha(path: Path) -> str:

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
# FAST WORKER DISCOVERY SURFACE
# ============================================================

SKIP_PARTS = {
    "__pycache__",
    "data",
    "reports",
    "tests",
    "test",
    "fixtures",
    "snapshots",
    "node_modules",
    ".git",
    ".venv",
}


python_files = []


for path in BACKEND_SERVER.rglob("*.py"):

    relative_parts = (
        path.relative_to(
            BACKEND_SERVER
        ).parts
    )

    if any(
        part in SKIP_PARTS
        for part in relative_parts
    ):
        continue

    python_files.append(path)


python_files.sort()


PATTERNS = {
    "worker_identity": re.compile(
        r"\b(worker_id|worker_name|worker_type|worker_instance)\b",
        re.IGNORECASE,
    ),

    "registration": re.compile(
        r"\b(register_worker|worker_registry|worker registration|registered worker)\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b(assign_worker|worker assignment|worker selection|selected_worker)\b",
        re.IGNORECASE,
    ),

    "lease": re.compile(
        r"\b(lease_owner|lease_id|lease_started_at|lease_expires_at|acquire_lease|renew_lease|release_lease)\b",
        re.IGNORECASE,
    ),

    "heartbeat": re.compile(
        r"\b(heartbeat|last_heartbeat|heartbeat_at|last_seen)\b",
        re.IGNORECASE,
    ),

    "health": re.compile(
        r"\b(worker_health|worker health|health_check|unhealthy worker|healthy worker)\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\b(worker recovery|recover_worker|worker failure|failed worker)\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b(worker_pool|worker pool|pool_id|pool_name)\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b(worker_capabilities|worker capabilities|required_capabilities|capability_id)\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b(worker_capacity|max_concurrency|maximum concurrency|current concurrency|available slots)\b",
        re.IGNORECASE,
    ),

    "drain_shutdown": re.compile(
        r"\b(drain_worker|draining|drained|shutdown_worker|worker shutdown|stop_worker)\b",
        re.IGNORECASE,
    ),

    "worker_execution": re.compile(
        r"\b(claim_job|dequeue_job|dispatch_job|execute_job|process_job|run_job|worker_loop)\b",
        re.IGNORECASE,
    ),

    "runtime_registration": re.compile(
        r"\b(runtime_registration|register_handler|handler_registry)\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

classes = []

functions = []

module_symbols = []

imports = []

parse_errors = []


for path in python_files:

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

    # Text findings
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
                    line.strip()[:400],
                )
            )

    # AST findings
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

            name = node.name.lower()

            if any(
                token in name
                for token in (
                    "worker",
                    "lease",
                    "heartbeat",
                    "pool",
                    "capability",
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

            name = node.name.lower()

            if any(
                token in name
                for token in (
                    "worker",
                    "lease",
                    "heartbeat",
                    "claim",
                    "dispatch",
                    "pool",
                    "capability",
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
            ast.Assign,
        ):

            for target in node.targets:

                if not isinstance(
                    target,
                    ast.Name,
                ):
                    continue

                name = target.id.lower()

                if any(
                    token in name
                    for token in (
                        "worker",
                        "lease",
                        "heartbeat",
                        "pool",
                        "capability",
                    )
                ):

                    module_symbols.append(
                        (
                            relative,
                            node.lineno,
                            target.id,
                        )
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            module = node.module or ""

            lower = module.lower()

            if any(
                token in lower
                for token in (
                    "worker",
                    "runtime_registration",
                    "orchestration",
                    "universal_queue",
                )
            ):

                imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )


# ============================================================
# RANK IMPORTANT FILES
# ============================================================

file_counts = Counter(
    relative
    for _, relative, _, _
    in findings
)


important_files = file_counts.most_common(
    75
)


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.1 — WORKER REGISTRATION FAST DISCOVERY SCAN",
    "=" * 108,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN UPSTREAM AUTHORITY CHECK",
    "-" * 108,
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
        "-" * 108,
        "",
        (
            "Python files scanned: "
            + str(len(python_files))
        ),
        (
            "Files with findings: "
            + str(len(file_counts))
        ),
        (
            "Total direct findings: "
            + str(len(findings))
        ),
        (
            "AST/read errors: "
            + str(len(parse_errors))
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
        "-" * 108,
        "",
    ]
)


for index, (
    filename,
    hit_count,
) in enumerate(
    important_files,
    start=1,
):

    out.append(
        (
            f"{index:03d}. "
            f"hits={hit_count} "
            f"{filename}"
        )
    )


out.extend(
    [
        "",
        "SECTION 4 — WORKER-RELATED CLASSES",
        "-" * 108,
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
        "SECTION 5 — WORKER-RELATED FUNCTIONS",
        "-" * 108,
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
        "SECTION 6 — WORKER-RELATED MODULE SYMBOLS",
        "-" * 108,
        "",
    ]
)


if module_symbols:

    for filename, line, name in sorted(
        module_symbols
    ):

        out.append(
            f"{filename}:{line} {name}"
        )

else:

    out.append(
        "NONE FOUND"
    )


out.extend(
    [
        "",
        "SECTION 7 — RELEVANT IMPORT RELATIONSHIPS",
        "-" * 108,
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
        "SECTION 8 — DIRECT FINDINGS",
        "-" * 108,
        "",
    ]
)


for group in PATTERNS:

    out.extend(
        [
            "",
            f"[{group.upper()}]",
            "~" * 108,
        ]
    )

    group_items = [
        item
        for item in findings
        if item[0] == group
    ]

    if not group_items:

        out.append(
            "NONE"
        )

        continue

    for _, filename, line, text in (
        group_items[:150]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(group_items) > 150:

        out.append(
            (
                "... "
                + str(
                    len(group_items) - 150
                )
                + " additional findings omitted"
            )
        )


out.extend(
    [
        "",
        "SECTION 9 — PARSE / READ ERRORS",
        "-" * 108,
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
        "SECTION 10 — ARCHITECTURE QUESTIONS",
        "-" * 108,
        "",
        "1. Is there an existing canonical worker identity?",
        "2. Is there already a worker registry?",
        "3. Is worker registration mixed with Runtime Registration?",
        "4. Is worker assignment mixed with claim/dispatch?",
        "5. Are Universal Job lease fields consumed by worker logic?",
        "6. Do heartbeat and health authorities already exist?",
        "7. Are worker pools or capabilities already modeled?",
        "8. Is worker capacity/concurrency already modeled?",
        "9. Which legacy worker components must remain untouched?",
        "10. What minimum immutable identity belongs to 4.1.1?",
        "",
        (
            "NEXT: define and freeze the 4.1.1 Worker "
            "Registration boundary before production implementation."
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(out),
    encoding="utf-8",
)


print()
print("=" * 92)
print(
    "PHASE 4.1.1 FAST DISCOVERY SCAN COMPLETE"
)
print("=" * 92)

print(
    "Python files scanned:",
    len(python_files),
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
    "AST/read errors:",
    len(parse_errors),
)

print(
    "Frozen upstream failures:",
    sum(
        1
        for _, status, _, _
        in protected_results
        if status != "PASS"
    ),
)

print()

for group, count in counts.most_common():

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
