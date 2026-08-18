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
    / "phase_5_1_2_orchestration_run_identity_scan.txt"
)


# ============================================================
# PROTECTED AUTHORITIES
# ============================================================

PROTECTED = {
    "5.1.1_orchestration_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),

    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),

    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),

    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),

    "worker_stale": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),

    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),

    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
    ),

    "worker_capacity": (
        ROOT / "backend/server/runtime/universal_worker/capacity.py",
        "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
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
        canonical.encode(
            "utf-8"
        )
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
                repr(
                    exc
                ),
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
# TARGETS
# ============================================================

TARGETS = (
    SERVER / "runtime/universal_orchestration/contract.py",

    SERVER / "runtime/universal_jobs/contract.py",
    SERVER / "runtime/universal_jobs/lineage.py",
    SERVER / "runtime/universal_jobs/creation.py",

    SERVER / "runtime/universal_runtime_registration.py",
    SERVER / "runtime/universal_runtime_worker_v1.py",
    SERVER / "runtime/universal_runtime_infrastructure.py",

    SERVER / "orchestration/models.py",
    SERVER / "orchestration/service.py",
    SERVER / "orchestration/queue.py",
    SERVER / "orchestration/job_store.py",

    SERVER / "coordination/universal_workflows/contract.py",
    SERVER / "coordination/universal_stages/contract.py",
    SERVER / "coordination/universal_stages/result_contract.py",
)


PATTERNS = {
    "orchestration_run_id": re.compile(
        r"\borchestration_run_id\b",
        re.IGNORECASE,
    ),

    "run_id": re.compile(
        r"\brun_id\b",
        re.IGNORECASE,
    ),

    "pipeline_run_id": re.compile(
        r"\bpipeline_run_id\b",
        re.IGNORECASE,
    ),

    "workflow_id": re.compile(
        r"\bworkflow_id\b",
        re.IGNORECASE,
    ),

    "job_id": re.compile(
        r"\bjob_id\b",
        re.IGNORECASE,
    ),

    "batch_id": re.compile(
        r"\bbatch_id\b",
        re.IGNORECASE,
    ),

    "correlation_id": re.compile(
        r"\bcorrelation_id\b",
        re.IGNORECASE,
    ),

    "execution_id": re.compile(
        r"\bexecution_id\b",
        re.IGNORECASE,
    ),

    "request_id": re.compile(
        r"\brequest_id\b",
        re.IGNORECASE,
    ),

    "parent": re.compile(
        r"\b("
        r"parent_job_id|parent_workflow_id|parent_run_id"
        r")\b",
        re.IGNORECASE,
    ),

    "identity": re.compile(
        r"\b("
        r"identity|identifier|canonical.*id|stable.*id"
        r")\b",
        re.IGNORECASE,
    ),

    "uuid": re.compile(
        r"\b("
        r"uuid|uuid4|uuid5"
        r")\b",
        re.IGNORECASE,
    ),

    "timestamp_identity": re.compile(
        r"\b("
        r"time_ns|timestamp.*id|datetime.*id"
        r")\b",
        re.IGNORECASE,
    ),
}


findings = []

counts = Counter()

file_counts = Counter()

classes = []

functions = []

declared_fields = []

imports = []

errors = []


for path in TARGETS:

    relative = str(
        path.relative_to(
            ROOT
        )
    )

    if not path.exists():

        errors.append(
            (
                relative,
                "MISSING",
            )
        )

        continue

    try:

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        tree = ast.parse(
            source
        )

    except Exception as exc:

        errors.append(
            (
                relative,
                repr(
                    exc
                ),
            )
        )

        continue

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        for category, pattern in (
            PATTERNS.items()
        ):

            if pattern.search(
                line
            ):

                counts[
                    category
                ] += 1

                file_counts[
                    relative
                ] += 1

                findings.append(
                    (
                        category,
                        relative,
                        line_number,
                        line.strip()[:500],
                    )
                )

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
                    "identity",
                    "run",
                    "workflow",
                    "job",
                    "lineage",
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
                    "identity",
                    "run",
                    "workflow",
                    "job_id",
                    "pipeline_run",
                    "correlation",
                    "uuid",
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
            ast.AnnAssign,
        ):

            if isinstance(
                node.target,
                ast.Name,
            ):

                field_name = (
                    node.target.id
                )

                if (
                    field_name.endswith(
                        "_id"
                    )
                    or
                    "identity"
                    in field_name.lower()
                ):

                    declared_fields.append(
                        (
                            relative,
                            node.lineno,
                            field_name,
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

            if any(
                token in module.lower()
                for token in (
                    "uuid",
                    "runtime",
                    "orchestration",
                    "coordination",
                    "jobs",
                )
            ):

                imports.append(
                    (
                        relative,
                        node.lineno,
                        module,
                    )
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                if any(
                    token in alias.name.lower()
                    for token in (
                        "uuid",
                        "runtime",
                        "orchestration",
                        "coordination",
                    )
                ):

                    imports.append(
                        (
                            relative,
                            node.lineno,
                            alias.name,
                        )
                    )


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.2 — ORCHESTRATION RUN "
        "IDENTITY READ-ONLY DISCOVERY"
    ),
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
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
        "SECTION 2 — TARGET FILES",
        "-" * 118,
        "",
    ]
)


for path in TARGETS:

    out.append(
        str(
            path.relative_to(
                ROOT
            )
        )
        + (
            " — FOUND"
            if path.exists()
            else " — MISSING"
        )
    )


out.extend(
    [
        "",
        "SECTION 3 — IDENTITY FINDING COUNTS",
        "-" * 118,
        "",
    ]
)


for category in PATTERNS:

    out.append(
        (
            category
            + ": "
            + str(
                counts[
                    category
                ]
            )
        )
    )


out.extend(
    [
        "",
        "SECTION 4 — HIGHEST-VALUE FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    file_counts.most_common(),
    start=1,
):

    out.append(
        (
            f"{index:03d}. "
            f"hits={count} "
            + filename
        )
    )


out.extend(
    [
        "",
        "SECTION 5 — RELEVANT CLASSES",
        "-" * 118,
        "",
    ]
)


if classes:

    for relative, line, name in sorted(
        classes
    ):

        out.append(
            f"{relative}:{line} class {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 6 — RELEVANT FUNCTIONS",
        "-" * 118,
        "",
    ]
)


if functions:

    for relative, line, name in sorted(
        functions
    ):

        out.append(
            f"{relative}:{line} {name}()"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 7 — DECLARED IDENTITY FIELDS",
        "-" * 118,
        "",
    ]
)


if declared_fields:

    for relative, line, name in sorted(
        declared_fields
    ):

        out.append(
            f"{relative}:{line} {name}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 8 — RELEVANT IMPORTS",
        "-" * 118,
        "",
    ]
)


if imports:

    for relative, line, module in sorted(
        imports
    ):

        out.append(
            f"{relative}:{line} -> {module}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 9 — IDENTITY FINDINGS",
        "-" * 118,
    ]
)


for category in PATTERNS:

    out.extend(
        [
            "",
            "[" + category.upper() + "]",
            "~" * 118,
        ]
    )

    items = [
        item
        for item in findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )

        continue

    for _, relative, line, text in items:

        out.append(
            f"{relative}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 10 — ERRORS",
        "-" * 118,
        "",
    ]
)


if errors:

    for relative, error in errors:

        out.append(
            f"{relative} | {error}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 11 — 5.1.2 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",
        "1. Does orchestration_run_id already exist anywhere canonically?",
        "2. Does generic run_id already have another meaning?",
        "3. What exactly does Universal Job pipeline_run_id mean today?",
        "4. Is pipeline_run_id job lineage/grouping evidence or orchestration identity?",
        "5. Is pipeline_run_id caller supplied or generated internally?",
        "6. May multiple Universal Jobs share one pipeline_run_id?",
        "7. May one orchestration contain jobs with different pipeline_run_id values?",
        "8. Should 5.1.2 reuse pipeline_run_id or define orchestration_run_id separately?",
        "9. What exactly does workflow_id mean in Universal Coordination Framework?",
        "10. Must orchestration_run_id remain distinct from workflow_id?",
        "11. Is batch_id grouping evidence only?",
        "12. Must orchestration_run_id remain distinct from batch_id?",
        "13. Must orchestration_run_id remain distinct from job_id?",
        "14. Is correlation_id already defined as cross-layer tracing rather than identity?",
        "15. Does an existing execution_id conflict with the proposed authority?",
        "16. Does an existing request_id conflict with the proposed authority?",
        "17. Should 5.1.2 generate IDs itself or validate caller-supplied IDs?",
        "18. Would internal UUID generation violate deterministic/pure authority design?",
        "19. Should identity creation be caller supplied to avoid wall-clock/randomness?",
        "20. What exact token normalization should orchestration_run_id use?",
        "21. Should an identity bind workspace_id?",
        "22. Should an identity bind pipeline?",
        "23. Should an identity bind a 5.1.1 Orchestration Contract?",
        "24. Should run identity contain job_ids? Or reference only the contract identity?",
        "25. Can the same 5.1.1 contract participate in multiple runs?",
        "26. Should two runs over the same contract be independently identifiable?",
        "27. Should run identity contain lifecycle state? Expected NO.",
        "28. Should run identity contain timestamps? Expected NO unless evidence proves otherwise.",
        "29. Should run identity contain worker/lease evidence? Expected NO.",
        "30. Should run identity perform persistence? Expected NO.",
        "31. Should run identity access Runtime State Store? Expected NO.",
        "32. Should run identity import Runtime Registration? Expected NO.",
        "33. Should run identity import Universal Coordination Framework? Expected NO.",
        "34. Should run identity perform queue/dispatch/execution? Expected NO.",
        "35. What minimum immutable fields define one canonical runtime orchestration run identity?",
        "",
        (
            "NEXT: analyze findings and freeze the "
            "5.1.2 Orchestration Run Identity boundary "
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
print("=" * 100)
print(
    "PHASE 5.1.2 ORCHESTRATION RUN IDENTITY DISCOVERY COMPLETE"
)
print("=" * 100)

print(
    "Target files:",
    len(
        TARGETS
    ),
)

print(
    "Files with identity findings:",
    len(
        file_counts
    ),
)

print(
    "Total identity findings:",
    len(
        findings
    ),
)

print(
    "Errors:",
    len(
        errors
    ),
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

for category, count in (
    counts.most_common()
):

    print(
        f"{category}: {count}"
    )

print()
print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
