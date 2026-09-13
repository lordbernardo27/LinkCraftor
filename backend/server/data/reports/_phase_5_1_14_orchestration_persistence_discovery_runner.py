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
    SERVER
    / "data"
    / "reports"
    / "phase_5_1_14_orchestration_persistence_discovery.txt"
)


# ============================================================
# FROZEN AUTHORITIES
# ============================================================

PROTECTED = {
    "5.1.1_contract": (
        SERVER / "runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "5.1.2_run_identity": (
        SERVER / "runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),

    "5.1.3_state_model": (
        SERVER / "runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),

    "5.1.4_dependency_resolution": (
        SERVER / "runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),

    "5.1.5_execution_planning": (
        SERVER / "runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),

    "5.1.6_stage_readiness": (
        SERVER / "runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),

    "5.1.7_runtime_handoff": (
        SERVER / "runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),

    "5.1.8_fan_out": (
        SERVER / "runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),

    "5.1.9_fan_in": (
        SERVER / "runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),

    "5.1.10_conditional_branching": (
        SERVER / "runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),

    "5.1.11_progress_tracking": (
        SERVER / "runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),

    "5.1.12_suspension_resume": (
        SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),

    "5.1.13_recovery": (
        SERVER / "runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),

    "job_contract": (
        SERVER / "runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "queue_certification": (
        SERVER / "runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "runtime_registration": (
        SERVER / "runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_worker": (
        SERVER / "runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        SERVER / "runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
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
# SEARCH CONFIGURATION
# ============================================================

SEARCH_ROOTS = (
    SERVER / "runtime",
    SERVER / "orchestration",
    SERVER / "coordination",
    SERVER / "jobs",
    SERVER / "stores",
    SERVER / "persistence",
)


SKIP_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


PATTERNS = {
    "persistence": re.compile(
        r"\b("
        r"persist|persistence|persistent|save|saved"
        r")\b",
        re.IGNORECASE,
    ),

    "state_store": re.compile(
        r"\b("
        r"state.?store|runtime.?state.?store|store.?registry|"
        r"repository|backend"
        r")\b",
        re.IGNORECASE,
    ),

    "snapshot": re.compile(
        r"\b("
        r"snapshot|snapshot_id|snapshot_version"
        r")\b",
        re.IGNORECASE,
    ),

    "serialization": re.compile(
        r"\b("
        r"serialize|serialization|deserialize|json|canonical"
        r")\b",
        re.IGNORECASE,
    ),

    "load_restore": re.compile(
        r"\b("
        r"load|loaded|restore|restored|rehydrate|rehydration"
        r")\b",
        re.IGNORECASE,
    ),

    "write_read": re.compile(
        r"\b("
        r"write|read|put|get|upsert|insert|update|delete"
        r")\b",
        re.IGNORECASE,
    ),

    "identity": re.compile(
        r"\b("
        r"identity|identity_fingerprint|orchestration_run_id|run_id"
        r")\b",
        re.IGNORECASE,
    ),

    "version": re.compile(
        r"\b("
        r"schema_version|version|revision|generation|etag"
        r")\b",
        re.IGNORECASE,
    ),

    "integrity": re.compile(
        r"\b("
        r"fingerprint|checksum|hash|integrity|conflict|compare.?and.?swap"
        r")\b",
        re.IGNORECASE,
    ),

    "state": re.compile(
        r"\b("
        r"orchestration state|CREATED|ACTIVE|WAITING|SUSPENDED|"
        r"RECOVERING|SUCCEEDED|FAILED|CANCELLED"
        r")\b",
        re.IGNORECASE,
    ),

    "progress": re.compile(
        r"\b("
        r"progress_snapshot|status_evidence|progress"
        r")\b",
        re.IGNORECASE,
    ),

    "recovery": re.compile(
        r"\b("
        r"recovery|recovery_decision|recovering"
        r")\b",
        re.IGNORECASE,
    ),

    "transaction": re.compile(
        r"\b("
        r"transaction|atomic|commit|rollback|concurrency|lock"
        r")\b",
        re.IGNORECASE,
    ),

    "io": re.compile(
        r"\b("
        r"filesystem|file|database|db|sql|redis|s3|dynamodb"
        r")\b",
        re.IGNORECASE,
    ),
}


repo_findings = []
repo_counts = Counter()
repo_file_counts = Counter()
python_files_scanned = 0
errors = []


for search_root in SEARCH_ROOTS:

    if not search_root.exists():
        continue

    for path in search_root.rglob(
        "*.py"
    ):

        if any(
            part.lower() in SKIP_PARTS
            for part in path.parts
        ):
            continue

        python_files_scanned += 1

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

            errors.append(
                (
                    relative,
                    repr(exc),
                )
            )
            continue

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            for category, pattern in PATTERNS.items():

                if pattern.search(
                    line
                ):

                    repo_counts[
                        category
                    ] += 1

                    repo_file_counts[
                        relative
                    ] += 1

                    repo_findings.append(
                        (
                            category,
                            relative,
                            line_number,
                            line.strip()[:600],
                        )
                    )

        try:

            ast.parse(
                source
            )

        except SyntaxError as exc:

            errors.append(
                (
                    relative,
                    (
                        "SYNTAX_ERROR "
                        f"line={exc.lineno} "
                        f"msg={exc.msg}"
                    ),
                )
            )


# ============================================================
# HIGH-VALUE FILE NAME DISCOVERY
# ============================================================

high_value_files = []


for search_root in SEARCH_ROOTS:

    if not search_root.exists():
        continue

    for path in search_root.rglob(
        "*.py"
    ):

        lower = path.name.lower()

        if any(
            token in lower
            for token in (
                "persist",
                "state",
                "store",
                "snapshot",
                "serial",
                "repository",
                "history",
                "checkpoint",
            )
        ):

            high_value_files.append(
                str(
                    path.relative_to(
                        ROOT
                    )
                )
            )


high_value_files = sorted(
    set(
        high_value_files
    )
)


# ============================================================
# REPORT
# ============================================================

out = [
    (
        "PHASE 5.1.14 — UNIVERSAL ORCHESTRATION "
        "PERSISTENCE INTERFACE READ-ONLY DISCOVERY"
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
        "SECTION 2 — REPOSITORY SEARCH COUNTS",
        "-" * 118,
        "",
        f"Python files scanned: {python_files_scanned}",
        f"Files with findings: {len(repo_file_counts)}",
        f"Total findings: {len(repo_findings)}",
        f"Errors / parse issues: {len(errors)}",
        "",
    ]
)


for category in PATTERNS:

    out.append(
        (
            category
            + ": "
            + str(
                repo_counts[
                    category
                ]
            )
        )
    )


out.extend(
    [
        "",
        "SECTION 3 — HIGH-VALUE PERSISTENCE / STATE FILES",
        "-" * 118,
        "",
    ]
)


if high_value_files:

    for index, filename in enumerate(
        high_value_files,
        start=1,
    ):

        out.append(
            f"{index:03d}. {filename}"
        )

else:

    out.append(
        "NONE"
    )


out.extend(
    [
        "",
        "SECTION 4 — HIGHEST-HIT FILES",
        "-" * 118,
        "",
    ]
)


for index, (
    filename,
    count,
) in enumerate(
    repo_file_counts.most_common(
        150
    ),
    start=1,
):

    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 5 — REPOSITORY FINDINGS",
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
        for item in repo_findings
        if item[0] == category
    ]

    if not items:

        out.append(
            "NONE"
        )
        continue

    for _, relative, line, text in items[:800]:

        out.append(
            f"{relative}:{line} | {text}"
        )

    if len(items) > 800:

        out.append(
            (
                "... TRUNCATED: "
                + str(
                    len(items) - 800
                )
                + " additional findings"
            )
        )


out.extend(
    [
        "",
        "SECTION 6 — ERRORS / PARSE ISSUES",
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
        "SECTION 7 — 5.1.14 ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Runtime State Store already exist?",
        "2. Is it an interface, registry, concrete backend, or combination?",
        "3. Does existing runtime code already define save/load semantics?",
        "4. Does existing orchestration code already persist runs or snapshots?",
        "5. Which persistence mechanisms are legacy and must not become 5.1.14 authority?",

        "6. Should 5.1.14 be an interface/contract rather than a storage backend?",
        "7. Should 5.1.14 itself perform filesystem/database/network I/O?",
        "8. Expected: probably NO; concrete persistence backend remains separate.",
        "9. Should it define persistence records that another backend consumes?",
        "10. Should it define save/load request contracts?",

        "11. Which orchestration artifacts belong in a canonical persisted record?",
        "12. 5.1.1 contract identity?",
        "13. 5.1.2 run identity?",
        "14. 5.1.3 state snapshot?",
        "15. 5.1.5 execution-plan identity/topology reference?",
        "16. 5.1.10 conditional decisions?",
        "17. 5.1.11 progress snapshot?",
        "18. 5.1.12 suspension/resume eligibility?",
        "19. 5.1.13 recovery decision?",
        "20. Or should some remain recomputable and therefore not persisted?",

        "21. Should 5.1.14 persist authoritative inputs, derived outputs, or both?",
        "22. Should progress snapshots be stored as immutable versions?",
        "23. Should state snapshots be immutable versions?",
        "24. Should the current/latest pointer be separate from historical snapshots?",

        "25. How should orchestration identity key persisted records?",
        "26. orchestration_run_id?",
        "27. identity_fingerprint?",
        "28. workspace + pipeline + run ID?",
        "29. Should identity_fingerprint be mandatory for integrity?",

        "30. Should persisted records carry schema_version?",
        "31. Should they carry content fingerprint/checksum?",
        "32. Should deterministic persistence_record_id be generated?",
        "33. Should identical canonical evidence create identical record IDs?",
        "34. Or should every persistence write be uniquely versioned?",

        "35. Should 5.1.14 define optimistic concurrency?",
        "36. expected_revision?",
        "37. previous_record_id?",
        "38. compare-and-swap semantics?",
        "39. Or is concurrency enforcement owned by the concrete Runtime State Store?",

        "40. Should 5.1.14 define append-only persistence?",
        "41. Should orchestration history be immutable?",
        "42. Should state replacement be prohibited?",
        "43. Should latest-state pointer updates be backend responsibility?",

        "44. Should persistence include timestamps?",
        "45. If so, should caller/backend supply them rather than 5.1.14 use wall clock?",
        "46. Should deterministic orchestration snapshots avoid time entirely?",

        "47. Should 5.1.14 serialize to JSON itself?",
        "48. Or should it expose JSON-native canonical records only?",
        "49. Should serialization policy belong Runtime Schema Management?",
        "50. Should 5.1.14 import runtime-schema serializers?",

        "51. Should restore/rehydration live inside 5.1.14?",
        "52. Should 5.1.14 validate a persisted record before rehydration?",
        "53. Should it actually rebuild 5.1.3/5.1.11 objects?",
        "54. Or should rehydration execution belong later runtime integration?",

        "55. Should 5.1.14 ever mutate orchestration state? Expected NO.",
        "56. Should it recompute progress? Expected NO.",
        "57. Should it reevaluate conditions? Expected NO.",
        "58. Should it rerun recovery? Expected NO.",
        "59. Should it decide completion? Expected NO; 5.1.15.",
        "60. Should it decide termination? Expected NO; 5.1.16.",
        "61. Should it record permanent evidence/audit semantics? Expected 5.1.17.",

        "62. Should 5.1.14 directly invoke Runtime State Store?",
        "63. Or only define the port/interface Runtime State Store must implement?",
        "64. Should concrete backend registration happen outside 5.1.14?",
        "65. Should AWS/DynamoDB/S3/database choices remain infrastructure-level?",

        "66. What exact operations should a persistence port expose?",
        "67. save_record?",
        "68. load_latest?",
        "69. load_by_record_id?",
        "70. list_history?",
        "71. compare_and_swap?",
        "72. delete? Probably NO for immutable orchestration history.",

        "73. Should terminal orchestration records remain immutable?",
        "74. Should cancelled/failed/succeeded history ever be overwritten? Expected NO.",
        "75. Should recovery produce a new persisted record rather than modify an old one?",

        "76. Should 5.1.14 include persistence disposition enums?",
        "77. READY_TO_PERSIST?",
        "78. INVALID?",
        "79. CONFLICT?",
        "80. Or should this phase purely define canonical persistence records and a port?",

        "81. Should storage failure classification belong 5.1.14?",
        "82. Or infrastructure/observability/reliability phases?",
        "83. Should retrying failed database writes be outside Runtime Orchestration?",

        "84. Should persistence interface import queue/worker/runtime lifecycle? Expected NO.",
        "85. Should it invoke Universal Coordination Framework? Expected NO.",
        "86. Should it invoke pipeline coordinators? Expected NO.",

        "87. Which 5.1.1–5.1.13 objects are safe to reference directly without circular dependencies?",
        "88. Should a persistence envelope store object fingerprints rather than whole derived objects?",
        "89. Can later 5.1.17 evidence records compose with 5.1.14 instead of duplicating storage?",

        "90. What is the smallest deterministic persistence interface that preserves enough state for restart/recovery without owning the storage engine?",

        "",
        (
            "NEXT: analyze these findings and freeze the exact "
            "5.1.14 Orchestration Persistence Interface boundary "
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
    "PHASE 5.1.14 ORCHESTRATION PERSISTENCE "
    "INTERFACE DISCOVERY COMPLETE"
)

print("=" * 100)

print(
    "Python files scanned:",
    python_files_scanned,
)

print(
    "Files with findings:",
    len(
        repo_file_counts
    ),
)

print(
    "Total findings:",
    len(
        repo_findings
    ),
)

print(
    "Errors / parse issues:",
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

for category in PATTERNS:

    print(
        f"{category}: "
        f"{repo_counts[category]}"
    )

print()

print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)

print(
    "REPORT:",
    REPORT_PATH,
)
