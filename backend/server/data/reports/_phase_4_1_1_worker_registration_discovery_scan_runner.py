from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_1_worker_registration_discovery_scan.txt"
)


# ============================================================
# FROZEN PHASE 3 PROTECTION
# ============================================================

FROZEN_QUEUE_AUTHORITIES = {
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
}


PROTECTED_JOB_AUTHORITIES = {
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
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# VERIFY FROZEN AUTHORITIES
# ============================================================

frozen_checks = []

for name, (path, expected) in {
    **FROZEN_QUEUE_AUTHORITIES,
    **PROTECTED_JOB_AUTHORITIES,
}.items():

    if not path.exists():
        frozen_checks.append(
            (name, "MISSING", expected, None)
        )
        continue

    actual = ast_sha(path)

    frozen_checks.append(
        (
            name,
            "PASS" if actual == expected else "FAIL",
            expected,
            actual,
        )
    )


# ============================================================
# SCAN CONFIGURATION
# ============================================================

ACTIVE_EXTENSIONS = {
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}


SEARCH_GROUPS = {
    "worker_identity": (
        r"\bworker_id\b",
        r"\bworker identity\b",
        r"\bworker_instance\b",
        r"\bworker_name\b",
        r"\bworker_type\b",
    ),

    "worker_registration": (
        r"\bworker registration\b",
        r"\bregister_worker\b",
        r"\bregister.*worker\b",
        r"\bworker registry\b",
        r"\bworker_registry\b",
        r"\bregistered worker\b",
    ),

    "worker_discovery": (
        r"\bworker discovery\b",
        r"\bdiscover_worker",
        r"\bdiscover.*worker\b",
        r"\bavailable workers?\b",
        r"\beligible workers?\b",
    ),

    "worker_assignment": (
        r"\bworker assignment\b",
        r"\bassign_worker\b",
        r"\bassign.*worker\b",
        r"\bselected_worker\b",
        r"\bworker selection\b",
    ),

    "worker_lease": (
        r"\blease_owner\b",
        r"\blease_id\b",
        r"\blease_started_at\b",
        r"\blease_expires_at\b",
        r"\bworker lease\b",
        r"\bacquire.*lease\b",
        r"\brelease.*lease\b",
        r"\brenew.*lease\b",
    ),

    "worker_health": (
        r"\bworker health\b",
        r"\bworker_health\b",
        r"\bhealthy worker\b",
        r"\bunhealthy worker\b",
        r"\bdegraded worker\b",
        r"\bhealth_check\b",
    ),

    "worker_recovery": (
        r"\bworker recovery\b",
        r"\brecover_worker\b",
        r"\brecover.*worker\b",
        r"\bworker failure\b",
        r"\bfailed worker\b",
    ),

    "worker_scaling": (
        r"\bworker scaling\b",
        r"\bscale_worker\b",
        r"\bscale.*worker\b",
        r"\bworker_count\b",
        r"\bdesired_worker",
        r"\bminimum_workers?\b",
        r"\bmaximum_workers?\b",
    ),

    "worker_shutdown": (
        r"\bworker shutdown\b",
        r"\bshutdown_worker\b",
        r"\bshutdown.*worker\b",
        r"\bworker stop\b",
        r"\bstop_worker\b",
    ),

    "worker_pool": (
        r"\bworker pool\b",
        r"\bworker_pool\b",
        r"\bpool_id\b",
        r"\bpool_name\b",
        r"\bworker pools\b",
    ),

    "worker_heartbeat": (
        r"\bheartbeat\b",
        r"\bheartbeats\b",
        r"\blast_seen\b",
        r"\blast_heartbeat\b",
        r"\bheartbeat_at\b",
    ),

    "worker_stale": (
        r"\bstale worker\b",
        r"\bstale_worker\b",
        r"\bworker stale\b",
        r"\bstaleness\b",
        r"\bstale threshold\b",
    ),

    "worker_drain": (
        r"\bworker drain\b",
        r"\bdrain_worker\b",
        r"\bdraining\b",
        r"\bdrained\b",
    ),

    "worker_capability": (
        r"\bworker capability\b",
        r"\bworker capabilities\b",
        r"\bworker_capabilities\b",
        r"\bcapability_id\b",
        r"\brequired_capabilities\b",
        r"\bcapabilities\b",
    ),

    "worker_capacity": (
        r"\bworker capacity\b",
        r"\bworker_capacity\b",
        r"\bmaximum concurrency\b",
        r"\bmax_concurrency\b",
        r"\bcurrent concurrency\b",
        r"\bavailable slots\b",
        r"\bcapacity slots\b",
    ),

    "runtime_registration": (
        r"\bruntime registration\b",
        r"\bruntime_registration\b",
        r"\bregister_handler\b",
        r"\bhandler registry\b",
        r"\bhandler_registry\b",
        r"\bjob_type.*handler\b",
    ),

    "worker_execution": (
        r"\bworker loop\b",
        r"\bworker_loop\b",
        r"\bexecute_job\b",
        r"\bprocess_job\b",
        r"\brun_job\b",
        r"\bdispatch_job\b",
        r"\bclaim_job\b",
        r"\bdequeue_job\b",
    ),

    "concurrency": (
        r"\bconcurrency\b",
        r"\bsemaphore\b",
        r"\bthreadpool\b",
        r"\bthread pool\b",
        r"\bprocess pool\b",
        r"\bexecutor\b",
    ),
}


compiled_groups = {
    group: tuple(
        re.compile(pattern, re.IGNORECASE)
        for pattern in patterns
    )
    for group, patterns
    in SEARCH_GROUPS.items()
}


# ============================================================
# FILE INVENTORY
# ============================================================

candidate_files = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if any(
        part in SKIP_DIRS
        for part in path.parts
    ):
        continue

    if path.suffix.lower() not in ACTIVE_EXTENSIONS:
        continue

    candidate_files.append(path)


candidate_files.sort()


# ============================================================
# CONTENT SCAN
# ============================================================

findings = []
files_with_findings = set()
group_counts = Counter()
file_group_counts = defaultdict(Counter)
parse_errors = []


for path in candidate_files:

    try:
        text = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    except Exception as exc:
        parse_errors.append(
            (
                str(path.relative_to(ROOT)),
                repr(exc),
            )
        )
        continue

    relative_path = str(
        path.relative_to(ROOT)
    )

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):

        stripped = line.strip()

        for group, patterns in compiled_groups.items():

            if not any(
                pattern.search(line)
                for pattern in patterns
            ):
                continue

            files_with_findings.add(
                relative_path
            )

            group_counts[group] += 1

            file_group_counts[
                relative_path
            ][group] += 1

            findings.append(
                {
                    "file": relative_path,
                    "line": line_number,
                    "group": group,
                    "text": stripped[:500],
                }
            )


# ============================================================
# PYTHON AST SYMBOL SCAN
# ============================================================

python_symbols = []
python_imports = []
python_classes = []
python_functions = []


for path in candidate_files:

    if path.suffix.lower() != ".py":
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
        tree = ast.parse(source)

    except Exception as exc:
        parse_errors.append(
            (
                str(path.relative_to(ROOT)),
                "AST: " + repr(exc),
            )
        )
        continue

    relative_path = str(
        path.relative_to(ROOT)
    )

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):

            name = node.name

            if any(
                token in name.lower()
                for token in (
                    "worker",
                    "lease",
                    "heartbeat",
                    "capability",
                    "pool",
                )
            ):
                python_classes.append(
                    (
                        relative_path,
                        node.lineno,
                        name,
                    )
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            name = node.name

            if any(
                token in name.lower()
                for token in (
                    "worker",
                    "lease",
                    "heartbeat",
                    "capability",
                    "pool",
                    "claim",
                    "dispatch",
                    "concurrency",
                )
            ):
                python_functions.append(
                    (
                        relative_path,
                        node.lineno,
                        name,
                    )
                )

        elif isinstance(node, ast.Assign):

            for target in node.targets:

                if not isinstance(
                    target,
                    ast.Name,
                ):
                    continue

                name = target.id

                if any(
                    token in name.lower()
                    for token in (
                        "worker",
                        "lease",
                        "heartbeat",
                        "capability",
                        "pool",
                        "concurrency",
                    )
                ):
                    python_symbols.append(
                        (
                            relative_path,
                            node.lineno,
                            name,
                        )
                    )

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            if any(
                token in module.lower()
                for token in (
                    "worker",
                    "lease",
                    "runtime_registration",
                    "orchestration",
                    "queue",
                )
            ):
                python_imports.append(
                    (
                        relative_path,
                        node.lineno,
                        module,
                    )
                )


# ============================================================
# HIGH-VALUE FILE RANKING
# ============================================================

likely_worker_authority_files = []

for relative_path in sorted(
    files_with_findings
):

    lower = relative_path.lower()
    score = 0

    for token in (
        "worker",
        "runtime",
        "orchestration",
        "queue",
        "lease",
        "handler",
    ):
        if token in lower:
            score += 1

    worker_hits = sum(
        file_group_counts[
            relative_path
        ].values()
    )

    score += min(
        worker_hits // 5,
        10,
    )

    if score >= 2:
        likely_worker_authority_files.append(
            (
                score,
                worker_hits,
                relative_path,
            )
        )


likely_worker_authority_files.sort(
    key=lambda item: (
        -item[0],
        -item[1],
        item[2],
    )
)


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.1 — WORKER REGISTRATION DISCOVERY SCAN",
    "=" * 112,
    "",
    "PURPOSE",
    "-------",
    (
        "Read-only discovery of existing worker identity, registration, "
        "pools, capabilities, assignment, leasing, heartbeats, health, "
        "recovery, scaling, shutdown, drain, capacity and execution "
        "concepts before defining canonical Phase 4.1.1 Worker Registration."
    ),
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN UPSTREAM AUTHORITY CHECK",
    "-" * 112,
    "",
]


for name, status, expected, actual in frozen_checks:

    out.extend(
        [
            f"{name}: {status}",
            "    EXPECTED: " + str(expected),
            "    ACTUAL:   " + str(actual),
            "",
        ]
    )


out.extend(
    [
        "",
        "SECTION 2 — SCAN INVENTORY",
        "-" * 112,
        "",
        (
            "Candidate files scanned: "
            + str(len(candidate_files))
        ),
        (
            "Files with worker/runtime findings: "
            + str(len(files_with_findings))
        ),
        (
            "Total findings: "
            + str(len(findings))
        ),
        (
            "Parse/read errors: "
            + str(len(parse_errors))
        ),
        "",
        "SECTION 3 — FINDING GROUP SUMMARY",
        "-" * 112,
        "",
    ]
)


for group in SEARCH_GROUPS:

    out.append(
        f"{group}: {group_counts[group]}"
    )


out.extend(
    [
        "",
        "SECTION 4 — HIGHEST-VALUE WORKER/RUNTIME FILES",
        "-" * 112,
        "",
    ]
)


for index, (
    score,
    hits,
    relative_path,
) in enumerate(
    likely_worker_authority_files[:100],
    start=1,
):

    out.append(
        (
            f"{index:03d}. "
            f"score={score} "
            f"hits={hits} "
            f"{relative_path}"
        )
    )

    for group, count in (
        file_group_counts[
            relative_path
        ].most_common()
    ):

        out.append(
            f"       {group}: {count}"
        )


out.extend(
    [
        "",
        "SECTION 5 — EXISTING WORKER-RELATED CLASSES",
        "-" * 112,
        "",
    ]
)


if python_classes:

    for file, line, name in sorted(
        python_classes
    ):
        out.append(
            f"{file}:{line}  class {name}"
        )
else:
    out.append("NONE FOUND")


out.extend(
    [
        "",
        "SECTION 6 — EXISTING WORKER-RELATED FUNCTIONS",
        "-" * 112,
        "",
    ]
)


if python_functions:

    for file, line, name in sorted(
        python_functions
    ):
        out.append(
            f"{file}:{line}  {name}()"
        )
else:
    out.append("NONE FOUND")


out.extend(
    [
        "",
        "SECTION 7 — WORKER-RELATED MODULE SYMBOLS",
        "-" * 112,
        "",
    ]
)


if python_symbols:

    for file, line, name in sorted(
        python_symbols
    ):
        out.append(
            f"{file}:{line}  {name}"
        )
else:
    out.append("NONE FOUND")


out.extend(
    [
        "",
        "SECTION 8 — RELEVANT PYTHON IMPORT RELATIONSHIPS",
        "-" * 112,
        "",
    ]
)


if python_imports:

    for file, line, module in sorted(
        python_imports
    ):
        out.append(
            f"{file}:{line} -> {module}"
        )
else:
    out.append("NONE FOUND")


out.extend(
    [
        "",
        "SECTION 9 — DIRECT FINDINGS BY AUTHORITY AREA",
        "-" * 112,
    ]
)


for group in SEARCH_GROUPS:

    out.extend(
        [
            "",
            f"[{group.upper()}]",
            "~" * 112,
        ]
    )

    group_items = [
        item
        for item in findings
        if item["group"] == group
    ]

    if not group_items:
        out.append("NO FINDINGS")
        continue

    for item in group_items[:250]:

        out.append(
            (
                f"{item['file']}:{item['line']} "
                f"| {item['text']}"
            )
        )

    if len(group_items) > 250:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(group_items) - 250
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 10 — PARSE / READ ERRORS",
        "-" * 112,
        "",
    ]
)


if parse_errors:

    for file, error in parse_errors:
        out.append(
            f"{file} | {error}"
        )
else:
    out.append("NONE")


out.extend(
    [
        "",
        "SECTION 11 — PHASE 4.1.1 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does LinkCraftor already have one or more worker identity models?",
        "2. Is worker_id currently persisted anywhere, or only transient?",
        "3. Does an existing worker registry already exist?",
        "4. Is worker registration currently mixed with Runtime Registration?",
        "5. Are workers currently generic or pipeline-specific?",
        "6. Are capabilities already declared on workers?",
        "7. Are worker pools already represented?",
        "8. Is worker assignment mixed with queue claim/dispatch logic?",
        "9. Are lease_owner / lease_id already consumed by worker code?",
        "10. Does heartbeat/liveness infrastructure already exist?",
        "11. Does Worker Health exist independently from heartbeat/staleness?",
        "12. Does worker capacity/concurrency already have implementation?",
        "13. Is legacy worker infrastructure present that must remain untouched?",
        "14. What minimum immutable identity fields should 4.1.1 own?",
        (
            "15. What belongs outside Registration because it belongs "
            "to Discovery, Health, Leasing, Pool, Capability or Capacity?"
        ),
        "",
        (
            "NEXT: analyze findings, freeze Phase 4.1.1 Worker "
            "Registration authority boundary, then implement."
        ),
    ]
)


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    "\n".join(out),
    encoding="utf-8",
)


print()
print("=" * 100)
print(
    "PHASE 4.1.1 WORKER REGISTRATION DISCOVERY SCAN COMPLETE"
)
print("=" * 100)

print(
    "Candidate files scanned:",
    len(candidate_files),
)

print(
    "Files with findings:",
    len(files_with_findings),
)

print(
    "Total findings:",
    len(findings),
)

print(
    "Parse/read errors:",
    len(parse_errors),
)

print()

print("TOP FINDING GROUPS:")

for group, count in (
    group_counts.most_common()
):
    print(
        f"  {group}: {count}"
    )

print()

print(
    "Frozen upstream authority failures:",
    sum(
        1
        for _, status, _, _
        in frozen_checks
        if status != "PASS"
    ),
)

print()
print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)
print()
print(
    "REPORT:",
    REPORT_PATH,
)
