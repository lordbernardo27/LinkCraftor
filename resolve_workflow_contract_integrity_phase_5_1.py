from __future__ import annotations

import hashlib
import importlib
import re
import subprocess
from pathlib import Path


ROOT = Path.cwd()

RELATIVE = (
    "backend/server/coordination/"
    "universal_workflows/contract.py"
)

WORKFLOW = ROOT / RELATIVE

REPORT = (
    ROOT
    / "phase_5_1_workflow_contract_integrity_resolution.txt"
)

KNOWN_COMMIT = "91a1c96e"

STALE_EXPECTED_VALUE = (
    "9094A98D2B9DBD9CCED73514648BF5D"
    "5092E547D19446AB0FE18FBE7089"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(
        data
    ).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(
        path.read_bytes()
    )


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — WORKFLOW CONTRACT INTEGRITY RESOLUTION",
    "=" * 112,
]


# =========================================================================
# 1. Current production source
# =========================================================================

lines.extend(
    (
        "",
        "1. CURRENT PRODUCTION SOURCE",
        "=" * 112,
    )
)

exists = WORKFLOW.exists()

lines.append(
    f"Canonical file exists: {exists}"
)

lines.append(
    f"Canonical path: {RELATIVE}"
)

if not exists:
    raise SystemExit(
        "Canonical workflow contract is missing."
    )


current_bytes = (
    WORKFLOW.read_bytes()
)

current_sha = sha256_bytes(
    current_bytes
)

lines.append(
    f"Current SHA256: {current_sha}"
)

lines.append(
    f"Current SHA length: {len(current_sha)}"
)

lines.append(
    "Current SHA structurally valid: "
    + str(
        bool(
            re.fullmatch(
                r"[0-9A-F]{64}",
                current_sha,
            )
        )
    )
)


# =========================================================================
# 2. Previously supplied expected value
# =========================================================================

lines.extend(
    (
        "",
        "2. PREVIOUS PHASE 5.1 EXPECTED VALUE",
        "=" * 112,
    )
)

lines.append(
    "Previous expected value: "
    + STALE_EXPECTED_VALUE
)

lines.append(
    "Previous expected length: "
    + str(
        len(
            STALE_EXPECTED_VALUE
        )
    )
)

stale_is_valid_sha256 = bool(
    re.fullmatch(
        r"[0-9A-F]{64}",
        STALE_EXPECTED_VALUE,
    )
)

lines.append(
    "Previous expected value is valid SHA256: "
    + str(
        stale_is_valid_sha256
    )
)

lines.append(
    "Previous expected value usable as freeze authority: "
    + str(
        stale_is_valid_sha256
    )
)


# =========================================================================
# 3. Git working-tree status
# =========================================================================

lines.extend(
    (
        "",
        "3. GIT WORKING-TREE EVIDENCE",
        "=" * 112,
    )
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

lines.append(
    "Git status: "
    + (
        status
        if status
        else "CLEAN"
    )
)

lines.append(
    "Working-tree file modified: "
    + str(
        bool(
            status
        )
    )
)


# =========================================================================
# 4. Commit history
# =========================================================================

lines.extend(
    (
        "",
        "4. GIT HISTORY",
        "=" * 112,
    )
)

history = subprocess.run(
    [
        "git",
        "log",
        "--oneline",
        "--follow",
        "--",
        RELATIVE,
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()

lines.append(
    history
    if history
    else "NO HISTORY FOUND"
)


# =========================================================================
# 5. Exact committed bytes
# =========================================================================

lines.extend(
    (
        "",
        "5. COMMITTED SOURCE BYTE INTEGRITY",
        "=" * 112,
    )
)

git_show = subprocess.run(
    [
        "git",
        "show",
        f"{KNOWN_COMMIT}:{RELATIVE}",
    ],
    cwd=ROOT,
    capture_output=True,
    check=True,
)

committed_bytes = (
    git_show.stdout
)

committed_sha = sha256_bytes(
    committed_bytes
)

lines.append(
    f"Commit inspected: {KNOWN_COMMIT}"
)

lines.append(
    f"Committed SHA256: {committed_sha}"
)

lines.append(
    f"Committed SHA length: {len(committed_sha)}"
)

lines.append(
    "Current SHA equals committed SHA: "
    + str(
        current_sha
        == committed_sha
    )
)

lines.append(
    "Current bytes equal committed bytes: "
    + str(
        current_bytes
        == committed_bytes
    )
)


# =========================================================================
# 6. Normal package import
# =========================================================================

lines.extend(
    (
        "",
        "6. LIVE CONTRACT IDENTITY",
        "=" * 112,
    )
)

module = importlib.import_module(
    "backend.server.coordination."
    "universal_workflows.contract"
)

identity_names = (
    "UNIVERSAL_WORKFLOW_CONTRACT_ID",
    "UNIVERSAL_WORKFLOW_CONTRACT_VERSION",
    "UNIVERSAL_WORKFLOW_SCHEMA_VERSION",
    "UNIVERSAL_WORKFLOW_CONTRACT_FIELD_COUNT",
)

for name in identity_names:

    if hasattr(
        module,
        name,
    ):
        lines.append(
            f"{name}: "
            f"{getattr(module, name)!r}"
        )
    else:
        lines.append(
            f"{name}: <NOT EXPOSED>"
        )


# =========================================================================
# 7. Search existing canonical evidence
# =========================================================================

lines.extend(
    (
        "",
        "7. PRIOR SHA REFERENCES",
        "=" * 112,
    )
)

reference_hits = []

search_roots = (
    ROOT,
)

candidate_patterns = (
    "verify_*.py",
    "*verification*.txt",
    "*certification*.txt",
)

seen = set()

for pattern in candidate_patterns:

    for path in ROOT.glob(
        pattern
    ):

        if path in seen:
            continue

        seen.add(
            path
        )

        if not path.is_file():
            continue

        try:
            text = path.read_text(
                encoding="utf-8-sig"
            )

        except Exception:
            continue

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            if (
                current_sha in line
                or "9094A98D" in line
            ):
                reference_hits.append(
                    (
                        path.name,
                        line_number,
                        line.strip(),
                    )
                )


if reference_hits:

    for filename, line_number, line in reference_hits:

        lines.append(
            f"{filename}:{line_number}: {line}"
        )

else:
    lines.append(
        "No prior root-level SHA references found."
    )


# =========================================================================
# 8. Resolution
# =========================================================================

lines.extend(
    (
        "",
        "8. INTEGRITY RESOLUTION",
        "=" * 112,
    )
)


current_matches_commit = (
    current_bytes
    == committed_bytes
)

git_clean = (
    status
    == ""
)

stale_authority_invalid = (
    not stale_is_valid_sha256
)


if (
    current_matches_commit
    and git_clean
    and stale_authority_invalid
):

    resolution = (
        "PASS — production workflow contract is unchanged; "
        "the previous Phase 5.1 expected SHA was malformed/stale."
    )

    canonical_candidate = (
        current_sha
    )

else:

    resolution = (
        "REVIEW REQUIRED — evidence does not yet establish "
        "that the mismatch was only a stale scan authority."
    )

    canonical_candidate = (
        "<NOT RESOLVED>"
    )


lines.append(
    resolution
)

lines.append(
    "Resolved canonical SHA candidate: "
    + canonical_candidate
)

lines.append(
    "Production source modification required: False"
)

lines.append(
    "Production source modified by this resolver: False"
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print("PHASE 5.1 — WORKFLOW CONTRACT INTEGRITY RESOLUTION")
print("=" * 112)
print("Current SHA256:")
print(current_sha)
print()
print("Committed SHA256:")
print(committed_sha)
print()
print(
    "Current bytes equal committed bytes:",
    current_bytes
    == committed_bytes,
)
print(
    "Git working tree clean:",
    git_clean,
)
print(
    "Previous expected SHA length:",
    len(
        STALE_EXPECTED_VALUE
    ),
)
print(
    "Previous expected SHA valid:",
    stale_is_valid_sha256,
)
print()
print("RESOLUTION:")
print(resolution)
print()
print(
    "CANONICAL SHA CANDIDATE:",
    canonical_candidate,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 112)
