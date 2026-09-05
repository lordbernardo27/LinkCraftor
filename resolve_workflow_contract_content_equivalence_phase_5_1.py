from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


ROOT = Path.cwd()

RELATIVE = (
    "backend/server/coordination/"
    "universal_workflows/contract.py"
)

WORKFLOW = ROOT / RELATIVE

COMMIT = "91a1c96e"

REPORT = ROOT / (
    "phase_5_1_workflow_contract_content_equivalence.txt"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(
        data
    ).hexdigest().upper()


def newline_counts(data: bytes) -> dict[str, int]:
    crlf = data.count(b"\r\n")

    # LF not already participating in CRLF
    lf_total = data.count(b"\n")
    lone_lf = lf_total - crlf

    # CR not participating in CRLF
    cr_total = data.count(b"\r")
    lone_cr = cr_total - crlf

    return {
        "CRLF": crlf,
        "LF_ONLY": lone_lf,
        "CR_ONLY": lone_cr,
    }


def normalize_lf(data: bytes) -> bytes:
    return (
        data
        .replace(b"\r\n", b"\n")
        .replace(b"\r", b"\n")
    )


print()
print("=" * 112)
print("PHASE 5.1 — WORKFLOW CONTRACT CONTENT-EQUIVALENCE RESOLUTION")
print("=" * 112)


current = WORKFLOW.read_bytes()

committed = subprocess.run(
    [
        "git",
        "show",
        f"{COMMIT}:{RELATIVE}",
    ],
    cwd=ROOT,
    capture_output=True,
    check=True,
).stdout


current_sha = sha256_bytes(
    current
)

committed_sha = sha256_bytes(
    committed
)


current_normalized = normalize_lf(
    current
)

committed_normalized = normalize_lf(
    committed
)


current_normalized_sha = sha256_bytes(
    current_normalized
)

committed_normalized_sha = sha256_bytes(
    committed_normalized
)


raw_equal = (
    current
    == committed
)

normalized_equal = (
    current_normalized
    == committed_normalized
)


status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        RELATIVE,
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


diff = subprocess.run(
    [
        "git",
        "diff",
        "--",
        RELATIVE,
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout


word_diff = subprocess.run(
    [
        "git",
        "diff",
        "--ignore-space-at-eol",
        "--",
        RELATIVE,
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout


attr = subprocess.run(
    [
        "git",
        "check-attr",
        "-a",
        "--",
        RELATIVE,
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — WORKFLOW CONTRACT CONTENT-EQUIVALENCE RESOLUTION",
    "=" * 112,
    "",
    "1. RAW BYTE EVIDENCE",
    "=" * 112,
    f"Current SHA256:   {current_sha}",
    f"Committed SHA256: {committed_sha}",
    f"Raw bytes equal: {raw_equal}",
    "",
    "Current newline counts:",
    repr(
        newline_counts(
            current
        )
    ),
    "Committed newline counts:",
    repr(
        newline_counts(
            committed
        )
    ),
    "",
    "2. NORMALIZED SOURCE EVIDENCE",
    "=" * 112,
    f"Current normalized SHA256:   {current_normalized_sha}",
    f"Committed normalized SHA256: {committed_normalized_sha}",
    f"Normalized source equal: {normalized_equal}",
    "",
    "3. GIT EVIDENCE",
    "=" * 112,
    "Git status: "
    + (
        status
        if status
        else "CLEAN"
    ),
    "",
    "Git attributes:",
    (
        attr
        if attr
        else "<NONE>"
    ),
    "",
    "git diff empty: "
    + str(
        diff == ""
    ),
    "git diff --ignore-space-at-eol empty: "
    + str(
        word_diff == ""
    ),
    "",
    "4. RESOLUTION",
    "=" * 112,
]


if (
    normalized_equal
    and status == ""
    and diff == ""
):
    resolution = (
        "PASS — current working-tree source is logically identical "
        "to the committed workflow contract. Raw SHA mismatch is "
        "caused by byte-level representation such as line endings."
    )

elif normalized_equal:
    resolution = (
        "PASS WITH REVIEW — normalized source is identical, but Git "
        "working-tree evidence is not fully clean."
    )

else:
    resolution = (
        "CONTENT DIFFERENCE DETECTED — current source is not equivalent "
        "to the committed workflow contract after newline normalization."
    )


lines.append(
    resolution
)

lines.append(
    ""
)

lines.append(
    "Production modification performed: False"
)

lines.append(
    "Canonical SHA authority changed: False"
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print("Current raw SHA256:")
print(current_sha)

print()
print("Committed raw SHA256:")
print(committed_sha)

print()
print("Current newline counts:")
print(
    newline_counts(
        current
    )
)

print("Committed newline counts:")
print(
    newline_counts(
        committed
    )
)

print()
print("Current normalized SHA256:")
print(current_normalized_sha)

print("Committed normalized SHA256:")
print(committed_normalized_sha)

print()
print(
    "NORMALIZED SOURCE EQUAL:",
    normalized_equal,
)

print(
    "GIT STATUS CLEAN:",
    status == "",
)

print(
    "GIT DIFF EMPTY:",
    diff == "",
)

print()
print("RESOLUTION:")
print(resolution)

print()
print(
    "REPORT:",
    REPORT.name,
)

print("=" * 112)
