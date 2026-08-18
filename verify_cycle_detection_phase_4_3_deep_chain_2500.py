from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from backend.server.coordination.dependency_planning.dependency_graph import (
    create_dependency_graph,
)

from backend.server.coordination.dependency_planning.cycle_detection import (
    detect_dependency_cycles,
    require_acyclic_dependency_graph,
)


ROOT = Path.cwd()

PHASE_43 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/cycle_detection.py"
)

EXPECTED_43_SHA = (
    "E77BF605724F991E85C7FE2E5329051E"
    "16ECB2F30ACDAEA8AA40A2FD47487CEA"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 108)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.3 — 2500-STAGE DEEP-CHAIN FOCUSED VERIFICATION")
print("=" * 108)

print(
    "Python recursion limit:",
    sys.getrecursionlimit(),
)

before_sha = sha256(
    PHASE_43
)

print(
    "Phase 4.3 SHA before:",
    before_sha,
)

print(
    "Frozen SHA exact:",
    before_sha == EXPECTED_43_SHA,
)


# =============================================================================
# Build 2,500-node acyclic chain
# =============================================================================

NODE_COUNT = 2500

edges = tuple(
    (
        f"stage-{i:04d}",
        f"stage-{i + 1:04d}",
    )
    for i in range(
        NODE_COUNT - 1
    )
)

graph = create_dependency_graph(
    workflow_id="phase-4-3-deep-chain-2500",
    edges=edges,
)

print()
print(
    "Graph nodes:",
    len(
        graph.node_ids
    ),
)

print(
    "Graph edges:",
    len(
        graph.edges
    ),
)


# =============================================================================
# Direct cycle detection
# =============================================================================

direct_status = "NOT RUN"
direct_detail = ""

try:
    result = detect_dependency_cycles(
        graph
    )

    if (
        result.is_acyclic
        and not result.has_cycle
        and result.cycle_witness_count == 0
        and result.node_count == NODE_COUNT
        and result.edge_count == NODE_COUNT - 1
    ):
        direct_status = "PASS"

    else:
        direct_status = "FAIL"
        direct_detail = repr(
            result
        )

except RecursionError as exc:
    direct_status = "RECURSION_ERROR"
    direct_detail = repr(
        exc
    )

except Exception as exc:
    direct_status = "ERROR"
    direct_detail = (
        f"{type(exc).__name__}: {exc}"
    )


print()
print(
    "Direct detect_dependency_cycles:",
    direct_status,
)

if direct_detail:
    print(
        "Detail:",
        direct_detail,
    )


# =============================================================================
# Acyclic guard
# =============================================================================

guard_status = "NOT RUN"
guard_detail = ""

try:
    guarded = require_acyclic_dependency_graph(
        graph
    )

    if (
        guarded.is_acyclic
        and not guarded.has_cycle
        and guarded.cycle_witness_count == 0
        and guarded.node_count == NODE_COUNT
        and guarded.edge_count == NODE_COUNT - 1
    ):
        guard_status = "PASS"

    else:
        guard_status = "FAIL"
        guard_detail = repr(
            guarded
        )

except RecursionError as exc:
    guard_status = "RECURSION_ERROR"
    guard_detail = repr(
        exc
    )

except Exception as exc:
    guard_status = "ERROR"
    guard_detail = (
        f"{type(exc).__name__}: {exc}"
    )


print()
print(
    "require_acyclic_dependency_graph:",
    guard_status,
)

if guard_detail:
    print(
        "Detail:",
        guard_detail,
    )


# =============================================================================
# Frozen-file integrity
# =============================================================================

after_sha = sha256(
    PHASE_43
)

print()
print(
    "Phase 4.3 SHA after:",
    after_sha,
)

print(
    "Frozen file unchanged:",
    after_sha == before_sha,
)

print(
    "Frozen SHA still exact:",
    after_sha == EXPECTED_43_SHA,
)


# =============================================================================
# Final result
# =============================================================================

passed = (
    direct_status == "PASS"
    and guard_status == "PASS"
    and before_sha == EXPECTED_43_SHA
    and after_sha == EXPECTED_43_SHA
)

print()
print("=" * 108)

if passed:
    print(
        "RESULT: PASS — 2500-STAGE DEEP CHAIN SUPPORTED"
    )

else:
    print(
        "RESULT: FAIL — PHASE 4.3 DEEP-CHAIN DEFECT PROVEN"
    )

print("=" * 108)


raise SystemExit(
    0
    if passed
    else 1
)
