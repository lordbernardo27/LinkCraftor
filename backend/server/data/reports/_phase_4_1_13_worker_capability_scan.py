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
    / "phase_4_1_13_worker_capability_scan.txt"
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

    "4.1.11_stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),

    "4.1.12_worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
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
    "worker_capability": re.compile(
        r"\b("
        r"worker_capability|worker capability|"
        r"worker_capabilities|worker capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "capability": re.compile(
        r"\b("
        r"capability|capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "supported_job_type": re.compile(
        r"\b("
        r"supported_job_type|supported job type|"
        r"supported_job_types|supported job types"
        r")\b",
        re.IGNORECASE,
    ),

    "supported_stage": re.compile(
        r"\b("
        r"supported_stage|supported stage|"
        r"supported_stages|supported stages"
        r")\b",
        re.IGNORECASE,
    ),

    "supported_pipeline": re.compile(
        r"\b("
        r"supported_pipeline|supported pipeline|"
        r"supported_pipelines|supported pipelines"
        r")\b",
        re.IGNORECASE,
    ),

    "worker_type": re.compile(
        r"\bworker_type\b|\bworker type\b",
        re.IGNORECASE,
    ),

    "service_registry": re.compile(
        r"\b("
        r"service_registry|service registry|"
        r"ServiceRegistry|ServiceDefinition|"
        r"service capability|service capabilities"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_registration": re.compile(
        r"\b("
        r"runtime_registration|runtime registration|"
        r"register_handler|handler_registry|"
        r"job_type.*handler|handler.*job_type"
        r")\b",
        re.IGNORECASE,
    ),

    "handler": re.compile(
        r"\b("
        r"handler|handlers"
        r")\b",
        re.IGNORECASE,
    ),

    "job_type": re.compile(
        r"\bjob_type\b|\bjob type\b",
        re.IGNORECASE,
    ),

    "pipeline_stage": re.compile(
        r"\b("
        r"pipeline|stage"
        r")\b",
        re.IGNORECASE,
    ),

    "assignment": re.compile(
        r"\b("
        r"worker_assignment|worker assignment|"
        r"assignable|eligible worker|eligible_workers"
        r")\b",
        re.IGNORECASE,
    ),

    "capacity": re.compile(
        r"\b("
        r"worker_capacity|worker capacity|"
        r"capacity|available_slots|max_concurrency"
        r")\b",
        re.IGNORECASE,
    ),

    "pool": re.compile(
        r"\b("
        r"worker_pool|worker pool|pool_id"
        r")\b",
        re.IGNORECASE,
    ),

    "registration": re.compile(
        r"\b("
        r"worker_registration|worker registration|"
        r"UniversalWorkerRegistration"
        r")\b",
        re.IGNORECASE,
    ),

    "dispatch": re.compile(
        r"\b("
        r"dispatch|dispatcher|dispatch_job"
        r")\b",
        re.IGNORECASE,
    ),

    "execution": re.compile(
        r"\b("
        r"execute|execution|executor"
        r")\b",
        re.IGNORECASE,
    ),

    "routing": re.compile(
        r"\b("
        r"routing|router|route_job"
        r")\b",
        re.IGNORECASE,
    ),

    "metadata_capability": re.compile(
        r"\b("
        r"metadata.*capabilit|"
        r"capabilit.*metadata"
        r")\b",
        re.IGNORECASE,
    ),

    "feature_support": re.compile(
        r"\b("
        r"supported_feature|supported features|"
        r"feature_support|feature support"
        r")\b",
        re.IGNORECASE,
    ),

    "runtime_service": re.compile(
        r"\b("
        r"runtime_service|runtime service|"
        r"RuntimeService"
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
                    "capability",
                    "service",
                    "worker",
                    "handler",
                    "registry",
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
                    "capability",
                    "support",
                    "worker",
                    "handler",
                    "registry",
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
                    "registration",
                    "service",
                    "handler",
                    "dispatch",
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


# ============================================================
# REPORT
# ============================================================

out = [
    "PHASE 4.1.13 — WORKER CAPABILITY MANAGEMENT READ-ONLY DISCOVERY SCAN",
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
        150
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={hits} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — CAPABILITY/REGISTRY CLASSES",
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
        "SECTION 5 — CAPABILITY/REGISTRY FUNCTIONS",
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
        "SECTION 7 — DIRECT CAPABILITY FINDINGS",
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
        items[:350]
    ):

        out.append(
            f"{filename}:{line} | {text}"
        )

    if len(items) > 350:

        out.append(
            (
                "... "
                + str(
                    len(items) - 350
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
        "SECTION 9 — 4.1.13 ARCHITECTURE QUESTIONS",
        "-" * 112,
        "",
        "1. Does a canonical individual Worker Capability authority already exist?",
        "2. Are capabilities already stored on UniversalWorkerRegistration?",
        "3. Does existing worker_type currently imply capability?",
        "4. Are worker capabilities represented anywhere as strings/tokens?",
        "5. Are worker capabilities represented as job types?",
        "6. Are worker capabilities represented as pipeline/stage pairs?",
        "7. Does any runtime service registry already define capabilities?",
        "8. Are those service capabilities worker-level or service-level?",
        "9. Does Runtime Registration map job_type to handlers?",
        "10. Must 4.1.13 remain separate from Runtime Registration?",
        "11. Does Assignment currently inspect capability?",
        "12. Should Assignment continue to receive caller-supplied eligible workers?",
        "13. Should capability matching occur before Assignment?",
        "14. Does Worker Pool imply capability today?",
        "15. Should Pool membership remain independent from capability?",
        "16. Does worker_type imply exactly one capability?",
        "17. Should worker_type remain identity/classification rather than executable capability?",
        "18. Should one worker support multiple capabilities?",
        "19. Should capabilities be immutable evidence snapshots?",
        "20. Should capability names be canonical normalized tokens?",
        "21. Should duplicate capability entries be rejected or deduplicated?",
        "22. Should capability ordering be deterministic?",
        "23. Should empty capability collection be valid?",
        "24. Should a worker with zero capabilities be representable?",
        "25. Should 4.1.13 expose supports_capability(capability)?",
        "26. Should 4.1.13 expose required-capability matching?",
        "27. Should matching be ALL-required or ANY-required?",
        "28. Should one capability result prove compatibility only, not assignment?",
        "29. Should capability evidence include worker_id and worker_instance_id?",
        "30. Should capability evidence include worker_type?",
        "31. Should capability evidence include capacity? (expected NO)",
        "32. Should capability evidence include health? (expected NO)",
        "33. Should capability evidence include drain state? (expected NO)",
        "34. Should capability evidence include pool_id? (expected NO unless discovery proves otherwise)",
        "35. Should capability management mutate registration? (expected NO)",
        "36. Should capability management register runtime handlers? (expected NO)",
        "37. Should capability management dispatch or execute jobs? (expected NO)",
        "38. Should capability management persist state itself? (expected NO)",
        "39. Should capability management access Runtime State Store? (expected NO)",
        "40. Should capability management perform filesystem/network I/O? (expected NO)",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "4.1.13 Worker Capability Management boundary "
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
    "PHASE 4.1.13 WORKER CAPABILITY MANAGEMENT SCAN COMPLETE"
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
