from __future__ import annotations

import ast
import hashlib
import re

from collections import Counter
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
SERVER = ROOT / "backend" / "server"

REPORT_PATH = (
    SERVER
    / "data"
    / "reports"
    / "phase_5_1_17_orchestration_evidence_discovery.txt"
)


PROTECTED = {
    "5.1.1": (
        SERVER / "runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),
    "5.1.2": (
        SERVER / "runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),
    "5.1.3": (
        SERVER / "runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),
    "5.1.4": (
        SERVER / "runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),
    "5.1.5": (
        SERVER / "runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),
    "5.1.6": (
        SERVER / "runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),
    "5.1.7": (
        SERVER / "runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),
    "5.1.8": (
        SERVER / "runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),
    "5.1.9": (
        SERVER / "runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),
    "5.1.10": (
        SERVER / "runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),
    "5.1.11": (
        SERVER / "runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),
    "5.1.12": (
        SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),
    "5.1.13": (
        SERVER / "runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    "5.1.14": (
        SERVER / "runtime/universal_orchestration/persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
    ),
    "5.1.15": (
        SERVER / "runtime/universal_orchestration/completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
    ),
    "5.1.16": (
        SERVER / "runtime/universal_orchestration/cancellation_termination.py",
        "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB",
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


protected = []

for name, (path, expected) in PROTECTED.items():

    if not path.exists():
        protected.append((name, "MISSING", expected, None))
        continue

    try:
        actual = ast_sha(path)
    except Exception as exc:
        protected.append((name, "ERROR", expected, repr(exc)))
        continue

    protected.append(
        (
            name,
            "PASS" if actual == expected else "FAIL",
            expected,
            actual,
        )
    )


SEARCH_ROOTS = (
    SERVER / "runtime",
    SERVER / "orchestration",
    SERVER / "coordination",
    SERVER / "evidence",
    SERVER / "audit",
)

PATTERNS = {
    "evidence": re.compile(
        r"\b(evidence|evidentiary|proof)\b",
        re.I,
    ),
    "decision": re.compile(
        r"\b(decision|decision_id|disposition|reason)\b",
        re.I,
    ),
    "audit": re.compile(
        r"\b(audit|audit_log|audit_record|audit_trail)\b",
        re.I,
    ),
    "record": re.compile(
        r"\b(record|event|ledger|history|journal)\b",
        re.I,
    ),
    "immutable": re.compile(
        r"\b(immutable|append.only|tamper|fingerprint|hash)\b",
        re.I,
    ),
    "persistence": re.compile(
        r"\b(persist|persistence|state_store|save|append_record)\b",
        re.I,
    ),
    "clock": re.compile(
        r"\b(timestamp|created_at|occurred_at|time|clock|utcnow)\b",
        re.I,
    ),
    "eligibility": re.compile(
        r"\b(suspension|resume|eligibility|recovery)\b",
        re.I,
    ),
    "completion": re.compile(
        r"\b(completion|succeeded|failed)\b",
        re.I,
    ),
    "cancellation": re.compile(
        r"\b(cancel|cancelled|cancellation|termination)\b",
        re.I,
    ),
}


counts = Counter()
files = Counter()
findings = []
errors = []
scanned = 0


for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for path in root.rglob("*.py"):

        if "__pycache__" in path.parts:
            continue

        scanned += 1

        rel = str(path.relative_to(ROOT))

        try:
            source = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )
        except Exception as exc:
            errors.append((rel, repr(exc)))
            continue

        try:
            ast.parse(source)
        except SyntaxError as exc:
            errors.append(
                (
                    rel,
                    f"SYNTAX_ERROR line={exc.lineno}: {exc.msg}",
                )
            )

        for number, line in enumerate(
            source.splitlines(),
            start=1,
        ):

            for category, pattern in PATTERNS.items():

                if pattern.search(line):
                    counts[category] += 1
                    files[rel] += 1
                    findings.append(
                        (
                            category,
                            rel,
                            number,
                            line.strip()[:600],
                        )
                    )


FOCUSED = (
    SERVER / "runtime/universal_orchestration/suspension_resume_eligibility.py",
    SERVER / "runtime/universal_orchestration/recovery.py",
    SERVER / "runtime/universal_orchestration/persistence_interface.py",
    SERVER / "runtime/universal_orchestration/completion_resolution.py",
    SERVER / "runtime/universal_orchestration/cancellation_termination.py",
    SERVER / "runtime/runtime_state_store.py",
    SERVER / "runtime/runtime_persistence.py",
)


focused = []


for path in FOCUSED:

    rel = str(path.relative_to(ROOT))

    if not path.exists():
        focused.append((rel, "MISSING", []))
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    matches = []

    for number, line in enumerate(
        source.splitlines(),
        start=1,
    ):

        if any(
            pattern.search(line)
            for pattern in PATTERNS.values()
        ):
            matches.append(
                (
                    number,
                    line.strip()[:700],
                )
            )

    focused.append(
        (
            rel,
            "FOUND",
            matches,
        )
    )


out = [
    "PHASE 5.1.17 — UNIVERSAL ORCHESTRATION EVIDENCE & DECISION RECORDS READ-ONLY DISCOVERY",
    "=" * 118,
    "",
    "PRODUCTION CODE MODIFIED: NO",
    "",
    "SECTION 1 — FROZEN AUTHORITY PROTECTION",
    "-" * 118,
    "",
]


for name, status, expected, actual in protected:
    out.extend(
        [
            f"{name}: {status}",
            f"  EXPECTED: {expected}",
            f"  ACTUAL:   {actual}",
            "",
        ]
    )


out.extend(
    [
        "",
        "SECTION 2 — REPOSITORY SUMMARY",
        "-" * 118,
        "",
        f"Python files scanned: {scanned}",
        f"Files with findings: {len(files)}",
        f"Total findings: {len(findings)}",
        f"Errors / parse issues: {len(errors)}",
        "",
    ]
)


for name in PATTERNS:
    out.append(
        f"{name}: {counts[name]}"
    )


out.extend(
    [
        "",
        "SECTION 3 — HIGHEST-HIT FILES",
        "-" * 118,
        "",
    ]
)


for index, (filename, count) in enumerate(
    files.most_common(120),
    start=1,
):
    out.append(
        f"{index:03d}. hits={count} {filename}"
    )


out.extend(
    [
        "",
        "SECTION 4 — FOCUSED AUTHORITIES",
        "-" * 118,
        "",
    ]
)


for rel, status, matches in focused:

    out.append(
        f"[{status}] {rel}"
    )

    for line_number, text in matches[:500]:
        out.append(
            f"  L{line_number}: {text}"
        )

    out.append("")


out.extend(
    [
        "",
        "SECTION 5 — FINDINGS",
        "-" * 118,
    ]
)


for category in PATTERNS:

    out.extend(
        [
            "",
            f"[{category.upper()}]",
            "~" * 118,
        ]
    )

    category_items = [
        item
        for item in findings
        if item[0] == category
    ]

    if not category_items:
        out.append("NONE")
        continue

    for _, rel, line, text in category_items[:700]:
        out.append(
            f"{rel}:{line} | {text}"
        )


out.extend(
    [
        "",
        "SECTION 6 — ERRORS",
        "-" * 118,
        "",
    ]
)


if errors:
    for rel, error in errors:
        out.append(
            f"{rel} | {error}"
        )
else:
    out.append("NONE")


out.extend(
    [
        "",
        "SECTION 7 — ARCHITECTURE QUESTIONS",
        "-" * 118,
        "",

        "1. Does a canonical Phase-5 evidence-record authority already exist?",
        "2. Are any legacy audit/event systems suitable only as infrastructure rather than 5.1.17 authority?",
        "3. Should 5.1.17 remain storage-backend agnostic?",

        "4. Which decisions require permanent records?",
        "5. 5.1.12 suspension/resume eligibility?",
        "6. 5.1.13 recovery?",
        "7. 5.1.15 completion?",
        "8. 5.1.16 cancellation/termination?",

        "9. Should 5.1.17 store entire decision objects?",
        "10. Or a canonical evidence envelope referring to decision IDs and evidence snapshots?",
        "11. Should it duplicate state/progress snapshots already persistable through 5.1.14?",
        "12. Or refer to their canonical IDs/fingerprints?",

        "13. Should evidence records be append-only and immutable?",
        "14. Should they have predecessor linkage?",
        "15. Should lineage be per orchestration run?",
        "16. Should evidence ordering rely on explicit predecessor linkage rather than wall clock?",

        "17. Should evidence_record_id be deterministic SHA256?",
        "18. Should same decision evidence generate same record ID?",
        "19. Should record ID include decision type?",
        "20. decision_id?",
        "21. orchestration identity?",
        "22. previous_record_id?",

        "23. Should timestamps be excluded because Phase 5 avoids wall-clock ownership?",
        "24. If timestamps are needed operationally, should concrete persistence infrastructure add them outside canonical semantic identity?",

        "25. Should 5.1.17 expose a Protocol/port?",
        "26. Or should it only create immutable evidence records and let 5.1.14/persistence infrastructure store them later?",
        "27. Would another port duplicate 5.1.14 improperly?",

        "28. Should 5.1.17 import 5.1.12/13/15/16 concrete classes?",
        "29. Or accept a generic decision-kind + canonical decision ID to reduce coupling?",
        "30. How do we validate that a claimed decision ID belongs to a known frozen decision type?",

        "31. Exact decision kinds?",
        "32. SUSPENSION_RESUME?",
        "33. RECOVERY?",
        "34. COMPLETION?",
        "35. CANCELLATION_TERMINATION?",

        "36. Should persistence-record IDs from 5.1.14 be optional provenance?",
        "37. Should evidence records point at pre-decision or post-decision persisted state?",
        "38. Or should 5.1.17 remain independent of concrete state persistence sequencing?",

        "39. Should 5.1.17 ever recompute any decision? Expected NO.",
        "40. Should it transition state? NO.",
        "41. Should it execute recovery? NO.",
        "42. Should it perform cancellation? NO.",
        "43. Should it invoke queues/workers? NO.",
        "44. Should it invoke Runtime State Store? NO.",

        "45. Should record creation be pure/deterministic?",
        "46. Should evidence metadata be immutable MappingProxyType?",
        "47. Should records support successor validation?",
        "48. Should cross-run lineage be rejected?",
        "49. Should skipped predecessor lineage be rejected?",

        "50. What exact boundary distinguishes:",
        "    5.1.14 state/progress persistence",
        "    from",
        "    5.1.17 permanent decision evidence?",

        "",
        "NEXT: analyze discovery, freeze the 5.1.17 boundary, then implement.",
    ]
)


REPORT_PATH.write_text(
    "\n".join(out),
    encoding="utf-8",
)


print("=" * 100)
print(
    "PHASE 5.1.17 ORCHESTRATION EVIDENCE & DECISION RECORDS DISCOVERY COMPLETE"
)
print("=" * 100)

print("Python files scanned:", scanned)
print("Files with findings:", len(files))
print("Total findings:", len(findings))
print("Errors / parse issues:", len(errors))

print(
    "Frozen authority failures:",
    sum(
        1
        for _, status, _, _
        in protected
        if status != "PASS"
    ),
)

print()
print(
    "STATUS: DISCOVERY ONLY — NO PRODUCTION CODE MODIFIED"
)
print(
    "REPORT:",
    REPORT_PATH,
)
