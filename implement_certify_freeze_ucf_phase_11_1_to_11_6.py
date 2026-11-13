from __future__ import annotations

import ast
import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

GOV_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_governance"
)

GOV_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

INIT = GOV_ROOT / "__init__.py"

P111 = GOV_ROOT / "workspace_isolation.py"
P112 = GOV_ROOT / "workflow_idempotency.py"
P113 = GOV_ROOT / "duplicate_protection.py"
P114 = GOV_ROOT / "version_governance.py"
P115 = GOV_ROOT / "coordinator_lifecycle.py"
P116 = GOV_ROOT / "security_boundaries.py"

F111 = GOV_ROOT / "workspace_isolation.phase_11_1.freeze.json"
F112 = GOV_ROOT / "workflow_idempotency.phase_11_2.freeze.json"
F113 = GOV_ROOT / "duplicate_protection.phase_11_3.freeze.json"
F114 = GOV_ROOT / "version_governance.phase_11_4.freeze.json"
F115 = GOV_ROOT / "coordinator_lifecycle.phase_11_5.freeze.json"
F116 = GOV_ROOT / "security_boundaries.phase_11_6.freeze.json"

BATCH_FREEZE = (
    GOV_ROOT
    / "coordination_governance.phase_11_1_to_11_6.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_11_1_to_11_6_certification_report.txt"
)

WORKFLOW_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_workflows/contract.py"
)

WORKFLOW_REGISTRY = (
    ROOT
    / "backend/server/coordination/workflow_registry/registry.py"
)

COORDINATOR_REGISTRY = (
    ROOT
    / "backend/server/coordination/coordinator_registry/registry.py"
)

REGISTRATION_VALIDATION = (
    ROOT
    / "backend/server/coordination/registration_validation/validator.py"
)

VERSION_MANAGEMENT = (
    ROOT
    / "backend/server/coordination/version_management/manager.py"
)

PIPELINE_COORDINATOR_CONTRACT = (
    ROOT
    / "backend/server/coordination/pipeline_coordinators/contract.py"
)

PHASE10_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_observability/"
    "phase_10_observability.freeze.json"
)

RUNTIME_IDEMPOTENCY = (
    ROOT
    / "backend/server/runtime/universal_jobs/idempotency_key.py"
)

RUNTIME_DUPLICATE = (
    ROOT
    / "backend/server/runtime/universal_jobs/duplicate_detection.py"
)

RUNTIME_AUTHORIZATION = (
    ROOT
    / "backend/server/runtime/security/runtime_authorization.py"
)


EXPECTED = {
    WORKFLOW_CONTRACT:
        "9094A98D2B9DBD9CCED73514648BF5D4115C5092E547D19446AB0FE18FBE7089",

    WORKFLOW_REGISTRY:
        "34786F74443BAC9049F3CD805CBF8BDB6275C6EF05B94C9BF42579E114CA4564",

    COORDINATOR_REGISTRY:
        "C9E324DF0C4D5AEA8D1D0C91D8FB3A3B479BB9A0830B0C4494186C01C298F071",

    REGISTRATION_VALIDATION:
        "30853E34C6F09B89A2C67D50D91C06EB4B2436A12918DC4E26197EB6159E8453",

    VERSION_MANAGEMENT:
        "118B628ABFCA7CF74B218520D6CF6E0AD4AF2CD6FFE9FB7FE711927A68412E25",

    PIPELINE_COORDINATOR_CONTRACT:
        "90E36C7DFC9B819EA3DCCDAB31E44CB5EA04F3A3ABEBF504C85AF83821944331",

    PHASE10_MASTER:
        "FF400A783DB08834E769370E47FCA8A731E0757FCA75643CE5DA2691A10869CF",

    RUNTIME_IDEMPOTENCY:
        "60D430AB3FACDD1BDA2441701196AC0FFAD60EE99CA4880F23FC4B54DC5D96E5",

    RUNTIME_DUPLICATE:
        "3B46EAB6276E2108F8BC796E087EB70C19C4EACBA5D34A948C69F73B7BD2446E",

    RUNTIME_AUTHORIZATION:
        "DC22A41B49F1233D6EAF6621587CE69E0BF5A34A8BDCECE9B24A4B7522BD0BC1",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def purge() -> None:
    prefix = (
        "backend.server.coordination.coordination_governance"
    )

    for name in tuple(sys.modules):
        if name.startswith(prefix):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 11.1–11.6 GOVERNANCE BATCH"
)


# ==================================================================
# 0 — FROZEN AUTHORITY GUARD
# ==================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


for path, expected in EXPECTED.items():

    check(
        f"exact authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


for path in (
    P111,
    P112,
    P113,
    P114,
    P115,
    P116,
    F111,
    F112,
    F113,
    F114,
    F115,
    F116,
    BATCH_FREEZE,
):

    check(
        f"not already installed: {path.name}",
        not path.exists(),
    )


coord_root = (
    ROOT
    / "backend/server/coordination"
)

runtime_root = (
    ROOT
    / "backend/server/runtime"
)


coord_before = {}

for path in coord_root.rglob("*"):

    if (
        path.is_file()
        and GOV_ROOT
        not in path.parents
    ):
        coord_before[
            path.resolve()
        ] = sha256(
            path
        )


runtime_before = {}

for path in runtime_root.rglob("*"):

    if path.is_file():
        runtime_before[
            path.resolve()
        ] = sha256(
            path
        )


init_created = False

if not INIT.exists():
    INIT.write_text(
        "",
        encoding="utf-8",
    )
    init_created = True


created = [
    P111,
    P112,
    P113,
    P114,
    P115,
    P116,
    F111,
    F112,
    F113,
    F114,
    F115,
    F116,
    BATCH_FREEZE,
    REPORT,
]


try:

    # ==============================================================
    # 1 — 11.1 WORKSPACE ISOLATION
    # ==============================================================

    section(
        "1 — INSTALL 11.1 WORKSPACE ISOLATION"
    )


    P111.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.1 — Workspace Isolation.

Pure coordination-level workspace boundary validation.

This module does not authenticate users, provision memberships, mutate
workflows, or duplicate Runtime workspace-resource governance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


WORKSPACE_ISOLATION_VERSION = (
    "workspace_isolation_v11.1.0"
)

WORKSPACE_ISOLATION_SCHEMA_VERSION = (
    "workspace_isolation_schema_v1"
)


class WorkspaceIsolationDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkspaceIsolationDecision:

    disposition: WorkspaceIsolationDisposition

    workflow_id: str
    expected_workspace_id: str

    observed_workspace_ids: Tuple[
        str,
        ...
    ]

    violations: Tuple[
        str,
        ...
    ]

    isolation_version: str = (
        WORKSPACE_ISOLATION_VERSION
    )

    schema_version: str = (
        WORKSPACE_ISOLATION_SCHEMA_VERSION
    )


def evaluate_workspace_isolation(
    workflow: UniversalWorkflow,
    *,
    observed_workspace_ids: Iterable[str] = (),
) -> WorkspaceIsolationDecision:

    if not isinstance(
        workflow,
        UniversalWorkflow,
    ):
        raise TypeError(
            "workflow must be UniversalWorkflow"
        )

    validation = workflow.validate()

    if not validation.is_valid:
        return WorkspaceIsolationDecision(
            disposition=
                WorkspaceIsolationDisposition.DENY,

            workflow_id=
                workflow.workflow_id,

            expected_workspace_id=
                workflow.workspace_id,

            observed_workspace_ids=(),

            violations=(
                "invalid_workflow",
            ),
        )

    observed = tuple(
        str(item).strip()
        for item in observed_workspace_ids
    )

    violations = []

    if not workflow.workspace_id:
        violations.append(
            "workflow_workspace_missing"
        )

    for value in observed:

        if not value:
            violations.append(
                "observed_workspace_missing"
            )

        elif (
            value
            != workflow.workspace_id
        ):
            violations.append(
                "cross_workspace_reference"
            )

    canonical = tuple(
        dict.fromkeys(
            violations
        )
    )

    return WorkspaceIsolationDecision(
        disposition=(
            WorkspaceIsolationDisposition.DENY
            if canonical
            else WorkspaceIsolationDisposition.ALLOW
        ),

        workflow_id=
            workflow.workflow_id,

        expected_workspace_id=
            workflow.workspace_id,

        observed_workspace_ids=
            observed,

        violations=
            canonical,
    )


__all__ = [
    "WORKSPACE_ISOLATION_VERSION",
    "WORKSPACE_ISOLATION_SCHEMA_VERSION",
    "WorkspaceIsolationDisposition",
    "WorkspaceIsolationDecision",
    "evaluate_workspace_isolation",
]
''',
        encoding="utf-8",
    )


    SHA111 = sha256(
        P111
    )


    # ==============================================================
    # 2 — 11.2 IDEMPOTENCY
    # ==============================================================

    section(
        "2 — INSTALL 11.2 IDEMPOTENCY"
    )


    P112.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.2 — Workflow Idempotency.

Workflow-level idempotency governance only.

Runtime Universal Job idempotency remains owned by the Universal Runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


WORKFLOW_IDEMPOTENCY_VERSION = (
    "workflow_idempotency_v11.2.0"
)

WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION = (
    "workflow_idempotency_schema_v1"
)


class WorkflowIdempotencyDisposition(
    str,
    Enum,
):
    ALLOW_NEW = "ALLOW_NEW"
    REUSE_EXISTING = "REUSE_EXISTING"
    DENY_CONFLICT = "DENY_CONFLICT"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowIdempotencyDecision:

    disposition: WorkflowIdempotencyDisposition

    workflow_id: str
    idempotency_key: str | None

    matching_workflow_ids: Tuple[
        str,
        ...
    ]

    reason_codes: Tuple[
        str,
        ...
    ]

    idempotency_version: str = (
        WORKFLOW_IDEMPOTENCY_VERSION
    )

    schema_version: str = (
        WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION
    )


def evaluate_workflow_idempotency(
    candidate: UniversalWorkflow,
    *,
    existing_workflows: Iterable[
        UniversalWorkflow
    ] = (),
) -> WorkflowIdempotencyDecision:

    if not isinstance(
        candidate,
        UniversalWorkflow,
    ):
        raise TypeError(
            "candidate must be UniversalWorkflow"
        )

    existing = tuple(
        existing_workflows
    )

    for item in existing:

        if not isinstance(
            item,
            UniversalWorkflow,
        ):
            raise TypeError(
                "existing_workflows must contain UniversalWorkflow"
            )

    key = candidate.idempotency_key

    if not key:
        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.ALLOW_NEW,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                None,

            matching_workflow_ids=(),

            reason_codes=(
                "no_workflow_idempotency_key",
            ),
        )

    matches = tuple(
        item
        for item in existing
        if item.idempotency_key
        == key
    )

    if not matches:
        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.ALLOW_NEW,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                key,

            matching_workflow_ids=(),

            reason_codes=(
                "idempotency_key_unused",
            ),
        )

    compatible = tuple(
        item
        for item in matches
        if (
            item.workflow_type
            == candidate.workflow_type
            and item.workflow_version
            == candidate.workflow_version
            and item.workspace_id
            == candidate.workspace_id
        )
    )

    if len(compatible) == len(matches):

        return WorkflowIdempotencyDecision(
            disposition=
                WorkflowIdempotencyDisposition.REUSE_EXISTING,

            workflow_id=
                candidate.workflow_id,

            idempotency_key=
                key,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in compatible
                ),

            reason_codes=(
                "matching_workflow_idempotency_identity",
            ),
        )

    return WorkflowIdempotencyDecision(
        disposition=
            WorkflowIdempotencyDisposition.DENY_CONFLICT,

        workflow_id=
            candidate.workflow_id,

        idempotency_key=
            key,

        matching_workflow_ids=
            tuple(
                item.workflow_id
                for item
                in matches
            ),

        reason_codes=(
            "idempotency_key_reused_with_conflicting_identity",
        ),
    )


__all__ = [
    "WORKFLOW_IDEMPOTENCY_VERSION",
    "WORKFLOW_IDEMPOTENCY_SCHEMA_VERSION",
    "WorkflowIdempotencyDisposition",
    "WorkflowIdempotencyDecision",
    "evaluate_workflow_idempotency",
]
''',
        encoding="utf-8",
    )


    SHA112 = sha256(
        P112
    )


    # ==============================================================
    # 3 — 11.3 DUPLICATE PROTECTION
    # ==============================================================

    section(
        "3 — INSTALL 11.3 DUPLICATE PROTECTION"
    )


    P113.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.3 — Duplicate Protection.

Protects workflow-instance identity at Coordination scope.

Workflow-definition duplicate rejection remains Phase 2.1 authority.
Coordinator-registration duplicate rejection remains Phase 2.2 authority.
Runtime job/queue deduplication remains Runtime-owned.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


DUPLICATE_PROTECTION_VERSION = (
    "duplicate_protection_v11.3.0"
)

DUPLICATE_PROTECTION_SCHEMA_VERSION = (
    "duplicate_protection_schema_v1"
)


class DuplicateDisposition(
    str,
    Enum,
):
    UNIQUE = "UNIQUE"
    DUPLICATE = "DUPLICATE"
    CONFLICT = "CONFLICT"


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateProtectionDecision:

    disposition: DuplicateDisposition

    workflow_id: str

    matching_workflow_ids: Tuple[
        str,
        ...
    ]

    reason_codes: Tuple[
        str,
        ...
    ]

    protection_version: str = (
        DUPLICATE_PROTECTION_VERSION
    )

    schema_version: str = (
        DUPLICATE_PROTECTION_SCHEMA_VERSION
    )


def evaluate_duplicate_workflow(
    candidate: UniversalWorkflow,
    *,
    existing_workflows: Iterable[
        UniversalWorkflow
    ] = (),
) -> DuplicateProtectionDecision:

    existing = tuple(
        existing_workflows
    )

    same_id = tuple(
        item
        for item in existing
        if item.workflow_id
        == candidate.workflow_id
    )

    if same_id:

        equivalent = all(
            (
                item.workflow_type
                == candidate.workflow_type
                and item.workflow_version
                == candidate.workflow_version
                and item.workspace_id
                == candidate.workspace_id
                and item.correlation_id
                == candidate.correlation_id
            )
            for item
            in same_id
        )

        return DuplicateProtectionDecision(
            disposition=(
                DuplicateDisposition.DUPLICATE
                if equivalent
                else DuplicateDisposition.CONFLICT
            ),

            workflow_id=
                candidate.workflow_id,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in same_id
                ),

            reason_codes=(
                (
                    "existing_equivalent_workflow_id"
                    if equivalent
                    else "workflow_id_identity_conflict"
                ),
            ),
        )

    same_correlation = tuple(
        item
        for item in existing
        if (
            item.workspace_id
            == candidate.workspace_id
            and item.workflow_type
            == candidate.workflow_type
            and item.workflow_version
            == candidate.workflow_version
            and item.correlation_id
            == candidate.correlation_id
        )
    )

    if same_correlation:

        return DuplicateProtectionDecision(
            disposition=
                DuplicateDisposition.DUPLICATE,

            workflow_id=
                candidate.workflow_id,

            matching_workflow_ids=
                tuple(
                    item.workflow_id
                    for item
                    in same_correlation
                ),

            reason_codes=(
                "equivalent_workflow_correlation_exists",
            ),
        )

    return DuplicateProtectionDecision(
        disposition=
            DuplicateDisposition.UNIQUE,

        workflow_id=
            candidate.workflow_id,

        matching_workflow_ids=(),

        reason_codes=(
            "workflow_identity_unique",
        ),
    )


__all__ = [
    "DUPLICATE_PROTECTION_VERSION",
    "DUPLICATE_PROTECTION_SCHEMA_VERSION",
    "DuplicateDisposition",
    "DuplicateProtectionDecision",
    "evaluate_duplicate_workflow",
]
''',
        encoding="utf-8",
    )


    SHA113 = sha256(
        P113
    )


    # ==============================================================
    # 4 — 11.4 VERSION GOVERNANCE
    # ==============================================================

    section(
        "4 — INSTALL 11.4 VERSION GOVERNANCE"
    )


    P114.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.4 — Version Governance.

Read-only governance over frozen Phase-2 workflow/coordinator registration
and explicit version-preference authorities.

This module does not modify either registry or version preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple

from backend.server.coordination.workflow_registry.registry import (
    WorkflowRegistryEntry,
)

from backend.server.coordination.registration_validation.validator import (
    RegistrationValidationResult,
)


VERSION_GOVERNANCE_VERSION = (
    "version_governance_v11.4.0"
)

VERSION_GOVERNANCE_SCHEMA_VERSION = (
    "version_governance_schema_v1"
)


class VersionGovernanceDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class VersionGovernanceDecision:

    disposition: VersionGovernanceDisposition

    workflow_type: str
    workflow_version: str

    coordinator_id: str
    coordinator_version: str

    preferred_workflow_version: str | None
    preferred_coordinator_version: str | None

    violations: Tuple[
        str,
        ...
    ]

    governance_version: str = (
        VERSION_GOVERNANCE_VERSION
    )

    schema_version: str = (
        VERSION_GOVERNANCE_SCHEMA_VERSION
    )


def evaluate_version_governance(
    *,
    workflow_entry: WorkflowRegistryEntry,
    coordinator: Any,
    registration_validation: RegistrationValidationResult,
    preferred_workflow_version: str | None = None,
    preferred_coordinator_version: str | None = None,
) -> VersionGovernanceDecision:

    violations = []

    coordinator_id = str(
        getattr(
            coordinator,
            "coordinator_id",
            "",
        )
    )

    coordinator_version = str(
        getattr(
            coordinator,
            "coordinator_version",
            "",
        )
    )

    coordinator_workflow_type = str(
        getattr(
            coordinator,
            "workflow_type",
            "",
        )
    )

    coordinator_workflow_version = str(
        getattr(
            coordinator,
            "workflow_version",
            "",
        )
    )

    if not registration_validation.is_valid:
        violations.append(
            "registration_validation_failed"
        )

    if (
        coordinator_workflow_type
        != workflow_entry.workflow_type
    ):
        violations.append(
            "workflow_type_mismatch"
        )

    if (
        coordinator_workflow_version
        != workflow_entry.workflow_version
    ):
        violations.append(
            "workflow_version_mismatch"
        )

    if (
        preferred_workflow_version
        is not None
        and preferred_workflow_version
        != workflow_entry.workflow_version
    ):
        violations.append(
            "non_preferred_workflow_version"
        )

    if (
        preferred_coordinator_version
        is not None
        and preferred_coordinator_version
        != coordinator_version
    ):
        violations.append(
            "non_preferred_coordinator_version"
        )

    canonical = tuple(
        dict.fromkeys(
            violations
        )
    )

    return VersionGovernanceDecision(
        disposition=(
            VersionGovernanceDisposition.DENY
            if canonical
            else VersionGovernanceDisposition.ALLOW
        ),

        workflow_type=
            workflow_entry.workflow_type,

        workflow_version=
            workflow_entry.workflow_version,

        coordinator_id=
            coordinator_id,

        coordinator_version=
            coordinator_version,

        preferred_workflow_version=
            preferred_workflow_version,

        preferred_coordinator_version=
            preferred_coordinator_version,

        violations=
            canonical,
    )


__all__ = [
    "VERSION_GOVERNANCE_VERSION",
    "VERSION_GOVERNANCE_SCHEMA_VERSION",
    "VersionGovernanceDisposition",
    "VersionGovernanceDecision",
    "evaluate_version_governance",
]
''',
        encoding="utf-8",
    )


    SHA114 = sha256(
        P114
    )


    # ==============================================================
    # 5 — 11.5 COORDINATOR LIFECYCLE
    # ==============================================================

    section(
        "5 — INSTALL 11.5 COORDINATOR LIFECYCLE"
    )


    P115.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.5 — Coordinator Lifecycle.

Governance lifecycle for already-registered coordinator identities.

This does not execute coordinators, mutate the Coordinator Registry,
or choose versions. Phase 2 retains registration/version authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


COORDINATOR_LIFECYCLE_VERSION = (
    "coordinator_lifecycle_v11.5.0"
)

COORDINATOR_LIFECYCLE_SCHEMA_VERSION = (
    "coordinator_lifecycle_schema_v1"
)


class CoordinatorLifecycleState(
    str,
    Enum,
):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


_ALLOWED = {
    CoordinatorLifecycleState.REGISTERED: (
        CoordinatorLifecycleState.ACTIVE,
        CoordinatorLifecycleState.DEPRECATED,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.ACTIVE: (
        CoordinatorLifecycleState.DEPRECATED,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.DEPRECATED: (
        CoordinatorLifecycleState.ACTIVE,
        CoordinatorLifecycleState.RETIRED,
    ),

    CoordinatorLifecycleState.RETIRED:
        (),
}


@dataclass(
    frozen=True,
    slots=True,
)
class CoordinatorLifecycleDecision:

    coordinator_id: str
    coordinator_version: str

    current_state: CoordinatorLifecycleState
    requested_state: CoordinatorLifecycleState

    allowed: bool

    reason_codes: Tuple[
        str,
        ...
    ]

    lifecycle_version: str = (
        COORDINATOR_LIFECYCLE_VERSION
    )

    schema_version: str = (
        COORDINATOR_LIFECYCLE_SCHEMA_VERSION
    )


def evaluate_coordinator_lifecycle_transition(
    *,
    coordinator_id: str,
    coordinator_version: str,
    current_state: CoordinatorLifecycleState,
    requested_state: CoordinatorLifecycleState,
    registration_valid: bool,
) -> CoordinatorLifecycleDecision:

    reasons = []

    if not coordinator_id.strip():
        reasons.append(
            "coordinator_id_missing"
        )

    if not coordinator_version.strip():
        reasons.append(
            "coordinator_version_missing"
        )

    if not registration_valid:
        reasons.append(
            "registration_not_valid"
        )

    if (
        requested_state
        not in _ALLOWED[
            current_state
        ]
    ):
        reasons.append(
            "lifecycle_transition_not_allowed"
        )

    canonical = tuple(
        dict.fromkeys(
            reasons
        )
    )

    return CoordinatorLifecycleDecision(
        coordinator_id=
            coordinator_id,

        coordinator_version=
            coordinator_version,

        current_state=
            current_state,

        requested_state=
            requested_state,

        allowed=
            not canonical,

        reason_codes=
            canonical,
    )


__all__ = [
    "COORDINATOR_LIFECYCLE_VERSION",
    "COORDINATOR_LIFECYCLE_SCHEMA_VERSION",
    "CoordinatorLifecycleState",
    "CoordinatorLifecycleDecision",
    "evaluate_coordinator_lifecycle_transition",
]
''',
        encoding="utf-8",
    )


    SHA115 = sha256(
        P115
    )


    # ==============================================================
    # 6 — 11.6 SECURITY BOUNDARIES
    # ==============================================================

    section(
        "6 — INSTALL 11.6 SECURITY BOUNDARIES"
    )


    P116.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 11.6 — Security Boundaries.

Fail-closed Coordination authorization boundary.

Authentication and generic Runtime authorization remain Runtime-owned.
This component consumes already-established authorization posture and
workspace scope; it does not issue credentials or authenticate principals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from backend.server.coordination.coordination_governance.workspace_isolation import (
    WorkspaceIsolationDecision,
    WorkspaceIsolationDisposition,
)


SECURITY_BOUNDARIES_VERSION = (
    "security_boundaries_v11.6.0"
)

SECURITY_BOUNDARIES_SCHEMA_VERSION = (
    "security_boundaries_schema_v1"
)


class CoordinationSecurityDisposition(
    str,
    Enum,
):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class CoordinationSecurityDecision:

    disposition: CoordinationSecurityDisposition

    principal_id: str
    action: str

    workflow_id: str
    workspace_id: str

    reason_codes: Tuple[
        str,
        ...
    ]

    security_version: str = (
        SECURITY_BOUNDARIES_VERSION
    )

    schema_version: str = (
        SECURITY_BOUNDARIES_SCHEMA_VERSION
    )


def evaluate_coordination_security_boundary(
    *,
    principal_id: str,
    action: str,
    workflow_id: str,
    workspace_id: str,
    authorization_granted: bool,
    workspace_isolation: WorkspaceIsolationDecision,
) -> CoordinationSecurityDecision:

    reasons = []

    if not principal_id.strip():
        reasons.append(
            "principal_missing"
        )

    if not action.strip():
        reasons.append(
            "action_missing"
        )

    if not workflow_id.strip():
        reasons.append(
            "workflow_id_missing"
        )

    if not workspace_id.strip():
        reasons.append(
            "workspace_id_missing"
        )

    if not authorization_granted:
        reasons.append(
            "authorization_not_granted"
        )

    if (
        workspace_isolation.disposition
        is not WorkspaceIsolationDisposition.ALLOW
    ):
        reasons.append(
            "workspace_isolation_denied"
        )

    if (
        workspace_isolation.workflow_id
        != workflow_id
    ):
        reasons.append(
            "workflow_scope_mismatch"
        )

    if (
        workspace_isolation.expected_workspace_id
        != workspace_id
    ):
        reasons.append(
            "workspace_scope_mismatch"
        )

    canonical = tuple(
        dict.fromkeys(
            reasons
        )
    )

    return CoordinationSecurityDecision(
        disposition=(
            CoordinationSecurityDisposition.DENY
            if canonical
            else CoordinationSecurityDisposition.ALLOW
        ),

        principal_id=
            principal_id,

        action=
            action,

        workflow_id=
            workflow_id,

        workspace_id=
            workspace_id,

        reason_codes=
            canonical,
    )


__all__ = [
    "SECURITY_BOUNDARIES_VERSION",
    "SECURITY_BOUNDARIES_SCHEMA_VERSION",
    "CoordinationSecurityDisposition",
    "CoordinationSecurityDecision",
    "evaluate_coordination_security_boundary",
]
''',
        encoding="utf-8",
    )


    SHA116 = sha256(
        P116
    )


    # ==============================================================
    # 7 — STATIC AUTHORITY BOUNDARY
    # ==============================================================

    section(
        "7 — STATIC GOVERNANCE BOUNDARY VERIFICATION"
    )


    forbidden = (
        "register_workflow",
        "register_coordinator",
        "set_preferred_workflow_version",
        "set_preferred_coordinator_version",
        "submit_universal_job",
        "enqueue",
        "requeue",
        "claim_job",
        "run_one_universal_runtime_job_v1",
        "save_workflow",
        "authenticate",
        "issue_token",
        "issue_grant",
    )


    for phase, path in (
        ("11.1", P111),
        ("11.2", P112),
        ("11.3", P113),
        ("11.4", P114),
        ("11.5", P115),
        ("11.6", P116),
    ):

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        calls = set()

        for node in ast.walk(tree):

            if isinstance(
                node,
                ast.Call,
            ):

                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        for symbol in forbidden:

            check(
                f"{phase} forbidden mutation/issuer authority absent: {symbol}",
                symbol
                not in calls,
            )


    # ==============================================================
    # 8 — IMPORT / CONTRACT VERIFICATION
    # ==============================================================

    section(
        "8 — IMPORT / CONTRACT VERIFICATION"
    )


    purge()


    m111 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "workspace_isolation"
    )

    m112 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "workflow_idempotency"
    )

    m113 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "duplicate_protection"
    )

    m114 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "version_governance"
    )

    m115 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "coordinator_lifecycle"
    )

    m116 = importlib.import_module(
        "backend.server.coordination.coordination_governance."
        "security_boundaries"
    )


    check(
        "11.1 version exact",
        m111.WORKSPACE_ISOLATION_VERSION
        == "workspace_isolation_v11.1.0",
    )

    check(
        "11.2 version exact",
        m112.WORKFLOW_IDEMPOTENCY_VERSION
        == "workflow_idempotency_v11.2.0",
    )

    check(
        "11.3 version exact",
        m113.DUPLICATE_PROTECTION_VERSION
        == "duplicate_protection_v11.3.0",
    )

    check(
        "11.4 version exact",
        m114.VERSION_GOVERNANCE_VERSION
        == "version_governance_v11.4.0",
    )

    check(
        "11.5 version exact",
        m115.COORDINATOR_LIFECYCLE_VERSION
        == "coordinator_lifecycle_v11.5.0",
    )

    check(
        "11.6 version exact",
        m116.SECURITY_BOUNDARIES_VERSION
        == "security_boundaries_v11.6.0",
    )


    # ==============================================================
    # 9 — FUNCTIONAL GOVERNANCE VERIFICATION
    # ==============================================================

    section(
        "9 — FUNCTIONAL GOVERNANCE VERIFICATION"
    )


    from types import SimpleNamespace

    from backend.server.coordination.universal_workflows.contract import (
        UniversalWorkflow,
        UniversalWorkflowStatus,
    )

    from backend.server.coordination.workflow_registry.registry import (
        WorkflowRegistryEntry,
    )

    from backend.server.coordination.registration_validation.validator import (
        RegistrationValidationResult,
    )


    def workflow(
        workflow_id,
        *,
        workspace_id="workspace-A",
        correlation_id="corr-A",
        idempotency_key="idem-A",
        workflow_type="governance-test",
        workflow_version="1.0.0",
    ):

        return UniversalWorkflow(
            workflow_id=
                workflow_id,

            workflow_type=
                workflow_type,

            workflow_version=
                workflow_version,

            workspace_id=
                workspace_id,

            coordinator_id=
                "coordinator-A",

            coordinator_version=
                "1.0.0",

            correlation_id=
                correlation_id,

            parent_workflow_id=
                None,

            root_workflow_id=
                workflow_id,

            status=
                UniversalWorkflowStatus.CREATED,

            input_reference=
                None,

            context={},

            metadata={},

            current_stage=
                None,

            completed_stages=(),

            pending_stages=(),

            failed_stages=(),

            skipped_stages=(),

            result_reference=
                None,

            artifact_references=(),

            idempotency_key=
                idempotency_key,

            created_at=
                "2026-11-08T00:00:00+00:00",

            started_at=
                None,

            updated_at=
                "2026-11-08T00:00:00+00:00",

            completed_at=
                None,

            failed_at=
                None,

            cancelled_at=
                None,

            failure_code=
                None,

            failure_message=
                None,

            failure_details={},
        )


    candidate = workflow(
        "workflow-A"
    )


    isolation_ok = (
        m111.evaluate_workspace_isolation(
            candidate,
            observed_workspace_ids=(
                "workspace-A",
                "workspace-A",
            ),
        )
    )


    check(
        "11.1 allows same-workspace evidence",
        isolation_ok.disposition.value
        == "ALLOW",
    )


    isolation_bad = (
        m111.evaluate_workspace_isolation(
            candidate,
            observed_workspace_ids=(
                "workspace-B",
            ),
        )
    )


    check(
        "11.1 denies cross-workspace evidence",
        isolation_bad.disposition.value
        == "DENY",
    )


    existing_same = workflow(
        "workflow-old",
        correlation_id=
            "corr-old",
    )


    idem = (
        m112.evaluate_workflow_idempotency(
            candidate,
            existing_workflows=(
                existing_same,
            ),
        )
    )


    check(
        "11.2 reuses compatible workflow idempotency identity",
        idem.disposition.value
        == "REUSE_EXISTING",
    )


    existing_conflict = workflow(
        "workflow-conflict",
        workspace_id=
            "workspace-B",
    )


    idem_conflict = (
        m112.evaluate_workflow_idempotency(
            candidate,
            existing_workflows=(
                existing_conflict,
            ),
        )
    )


    check(
        "11.2 denies conflicting idempotency reuse",
        idem_conflict.disposition.value
        == "DENY_CONFLICT",
    )


    duplicate = (
        m113.evaluate_duplicate_workflow(
            candidate,
            existing_workflows=(
                candidate,
            ),
        )
    )


    check(
        "11.3 detects equivalent workflow duplicate",
        duplicate.disposition.value
        == "DUPLICATE",
    )


    unique_candidate = workflow(
        "workflow-unique",
        correlation_id=
            "corr-unique",
        idempotency_key=
            "idem-unique",
    )


    unique = (
        m113.evaluate_duplicate_workflow(
            unique_candidate,
            existing_workflows=(
                candidate,
            ),
        )
    )


    check(
        "11.3 permits unique workflow instance",
        unique.disposition.value
        == "UNIQUE",
    )


    entry = WorkflowRegistryEntry(
        workflow_type=
            "governance-test",

        workflow_version=
            "1.0.0",

        workflow_contract_version=
            "universal_workflow_contract_v1.1.0",

        description=
            "test",

        metadata={},
    )


    coordinator = SimpleNamespace(
        coordinator_id=
            "coordinator-A",

        coordinator_version=
            "1.0.0",

        workflow_type=
            "governance-test",

        workflow_version=
            "1.0.0",
    )


    registration = RegistrationValidationResult(
        coordinator_id=
            "coordinator-A",

        coordinator_version=
            "1.0.0",

        workflow_type=
            "governance-test",

        workflow_version=
            "1.0.0",

        is_valid=
            True,

        violations=(),

        checked_rule_count=
            6,
    )


    version_ok = (
        m114.evaluate_version_governance(
            workflow_entry=
                entry,

            coordinator=
                coordinator,

            registration_validation=
                registration,

            preferred_workflow_version=
                "1.0.0",

            preferred_coordinator_version=
                "1.0.0",
        )
    )


    check(
        "11.4 allows registered preferred versions",
        version_ok.disposition.value
        == "ALLOW",
    )


    version_bad = (
        m114.evaluate_version_governance(
            workflow_entry=
                entry,

            coordinator=
                coordinator,

            registration_validation=
                registration,

            preferred_workflow_version=
                "2.0.0",

            preferred_coordinator_version=
                "1.0.0",
        )
    )


    check(
        "11.4 denies non-preferred workflow version",
        version_bad.disposition.value
        == "DENY",
    )


    lifecycle_ok = (
        m115.evaluate_coordinator_lifecycle_transition(
            coordinator_id=
                "coordinator-A",

            coordinator_version=
                "1.0.0",

            current_state=
                m115.CoordinatorLifecycleState.REGISTERED,

            requested_state=
                m115.CoordinatorLifecycleState.ACTIVE,

            registration_valid=
                True,
        )
    )


    check(
        "11.5 allows REGISTERED -> ACTIVE",
        lifecycle_ok.allowed,
    )


    lifecycle_bad = (
        m115.evaluate_coordinator_lifecycle_transition(
            coordinator_id=
                "coordinator-A",

            coordinator_version=
                "1.0.0",

            current_state=
                m115.CoordinatorLifecycleState.RETIRED,

            requested_state=
                m115.CoordinatorLifecycleState.ACTIVE,

            registration_valid=
                True,
        )
    )


    check(
        "11.5 blocks RETIRED -> ACTIVE",
        not lifecycle_bad.allowed,
    )


    security_ok = (
        m116.evaluate_coordination_security_boundary(
            principal_id=
                "principal-A",

            action=
                "inspect_workflow",

            workflow_id=
                candidate.workflow_id,

            workspace_id=
                candidate.workspace_id,

            authorization_granted=
                True,

            workspace_isolation=
                isolation_ok,
        )
    )


    check(
        "11.6 allows authorized same-workspace action",
        security_ok.disposition.value
        == "ALLOW",
    )


    security_bad = (
        m116.evaluate_coordination_security_boundary(
            principal_id=
                "principal-A",

            action=
                "inspect_workflow",

            workflow_id=
                candidate.workflow_id,

            workspace_id=
                candidate.workspace_id,

            authorization_granted=
                False,

            workspace_isolation=
                isolation_ok,
        )
    )


    check(
        "11.6 denies without authorization posture",
        security_bad.disposition.value
        == "DENY",
    )


    # ==============================================================
    # 10 — FREEZE 11.1–11.6
    # ==============================================================

    section(
        "10 — FREEZE PHASE 11.1–11.6"
    )


    source_hashes = {
        "11.1":
            SHA111,

        "11.2":
            SHA112,

        "11.3":
            SHA113,

        "11.4":
            SHA114,

        "11.5":
            SHA115,

        "11.6":
            SHA116,
    }


    specs = (
        (
            F111,
            "11.1",
            "Workspace Isolation",
            P111,
            "workspace_isolation_v11.1.0",
            "workspace_isolation_schema_v1",
        ),
        (
            F112,
            "11.2",
            "Idempotency",
            P112,
            "workflow_idempotency_v11.2.0",
            "workflow_idempotency_schema_v1",
        ),
        (
            F113,
            "11.3",
            "Duplicate Protection",
            P113,
            "duplicate_protection_v11.3.0",
            "duplicate_protection_schema_v1",
        ),
        (
            F114,
            "11.4",
            "Version Governance",
            P114,
            "version_governance_v11.4.0",
            "version_governance_schema_v1",
        ),
        (
            F115,
            "11.5",
            "Coordinator Lifecycle",
            P115,
            "coordinator_lifecycle_v11.5.0",
            "coordinator_lifecycle_schema_v1",
        ),
        (
            F116,
            "11.6",
            "Security Boundaries",
            P116,
            "security_boundaries_v11.6.0",
            "security_boundaries_schema_v1",
        ),
    )


    freeze_hashes = {}


    for (
        freeze_path,
        phase,
        component,
        source_path,
        version,
        schema,
    ) in specs:

        write_json(
            freeze_path,
            {
                "framework":
                    "Universal Coordination Framework",

                "phase":
                    phase,

                "component":
                    component,

                "certified":
                    True,

                "frozen":
                    True,

                "production": {
                    "path":
                        str(
                            source_path.relative_to(
                                ROOT
                            )
                        ).replace(
                            "\\",
                            "/",
                        ),

                    "version":
                        version,

                    "schema_version":
                        schema,

                    "sha256":
                        sha256(
                            source_path
                        ),
                },

                "governance_authorities": {
                    "workflow_contract":
                        sha256(
                            WORKFLOW_CONTRACT
                        ),

                    "workflow_registry":
                        sha256(
                            WORKFLOW_REGISTRY
                        ),

                    "coordinator_registry":
                        sha256(
                            COORDINATOR_REGISTRY
                        ),

                    "registration_validation":
                        sha256(
                            REGISTRATION_VALIDATION
                        ),

                    "version_management":
                        sha256(
                            VERSION_MANAGEMENT
                        ),

                    "phase_10_master":
                        sha256(
                            PHASE10_MASTER
                        ),
                },

                "runtime_boundaries": {
                    "runtime_idempotency_duplicated":
                        False,

                    "runtime_duplicate_detection_duplicated":
                        False,

                    "runtime_authentication_owned":
                        False,

                    "runtime_authorization_owned":
                        False,

                    "runtime_mutation":
                        False,
                },

                "freeze_created_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            },
        )


        freeze_hashes[
            phase
        ] = sha256(
            freeze_path
        )


    # ==============================================================
    # 11 — BATCH CERTIFICATION
    # ==============================================================

    section(
        "11 — BATCH CERTIFICATION"
    )


    canonical = "\n".join(
        f"{phase}:{source_hashes[phase]}"
        for phase
        in (
            "11.1",
            "11.2",
            "11.3",
            "11.4",
            "11.5",
            "11.6",
        )
    )


    COMPOSITE = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


    passed_before_final = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    REPORT.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 11.1–11.6 GOVERNANCE CERTIFICATION",
                "",
                "11.1 Workspace Isolation: CERTIFIED + FROZEN",
                "11.2 Idempotency: CERTIFIED + FROZEN",
                "11.3 Duplicate Protection: CERTIFIED + FROZEN",
                "11.4 Version Governance: CERTIFIED + FROZEN",
                "11.5 Coordinator Lifecycle: CERTIFIED + FROZEN",
                "11.6 Security Boundaries: CERTIFIED + FROZEN",
                "",
                f"11.1 SHA256: {SHA111}",
                f"11.2 SHA256: {SHA112}",
                f"11.3 SHA256: {SHA113}",
                f"11.4 SHA256: {SHA114}",
                f"11.5 SHA256: {SHA115}",
                f"11.6 SHA256: {SHA116}",
                "",
                f"11.1–11.6 COMPOSITE SHA256: {COMPOSITE}",
                "",
                "Governance boundaries:",
                "- Phase 2 remains workflow/coordinator registration authority",
                "- Phase 2.4 remains explicit version-preference authority",
                "- Runtime remains Universal Job idempotency authority",
                "- Runtime remains job/queue deduplication authority",
                "- Runtime authentication and generic authorization remain Runtime-owned",
                "- Phase 11 adds workflow-level coordination governance only",
                "",
                f"Formal checks passed before final immutability: {passed_before_final}",
                "Formal failures: 0",
                "",
                "STATUS: CERTIFIED + FROZEN",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    REPORT_SHA = sha256(
        REPORT
    )


    write_json(
        BATCH_FREEZE,
        {
            "framework":
                "Universal Coordination Framework",

            "scope":
                "11.1 through 11.6",

            "certified":
                True,

            "frozen":
                True,

            "source_sha256":
                source_hashes,

            "freeze_sha256":
                freeze_hashes,

            "composite_sha256":
                COMPOSITE,

            "phase_10_master_sha256":
                sha256(
                    PHASE10_MASTER
                ),

            "report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "next":
                "11.7 Governance Certification",

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        },
    )


    BATCH_FREEZE_SHA = sha256(
        BATCH_FREEZE
    )


    # ==============================================================
    # 12 — FINAL IMMUTABILITY
    # ==============================================================

    section(
        "12 — FINAL IMMUTABILITY VERIFICATION"
    )


    for path, expected in EXPECTED.items():

        check(
            f"frozen authority unchanged: {path.name}",
            sha256(path)
            == expected,
        )


    coord_after = {}

    for path in coord_root.rglob("*"):

        if (
            path.is_file()
            and GOV_ROOT
            not in path.parents
        ):
            coord_after[
                path.resolve()
            ] = sha256(
                path
            )


    check(
        "existing Coordination inventory unchanged",
        set(
            coord_after
        )
        == set(
            coord_before
        ),
    )


    check(
        "existing Coordination hashes unchanged",
        coord_after
        == coord_before,
    )


    runtime_after = {}

    for path in runtime_root.rglob("*"):

        if path.is_file():
            runtime_after[
                path.resolve()
            ] = sha256(
                path
            )


    check(
        "Runtime inventory unchanged",
        set(
            runtime_after
        )
        == set(
            runtime_before
        ),
    )


    check(
        "Runtime hashes unchanged",
        runtime_after
        == runtime_before,
    )


    purge()


    for module_name, version_name, expected_version in (
        (
            "backend.server.coordination.coordination_governance.workspace_isolation",
            "WORKSPACE_ISOLATION_VERSION",
            "workspace_isolation_v11.1.0",
        ),
        (
            "backend.server.coordination.coordination_governance.workflow_idempotency",
            "WORKFLOW_IDEMPOTENCY_VERSION",
            "workflow_idempotency_v11.2.0",
        ),
        (
            "backend.server.coordination.coordination_governance.duplicate_protection",
            "DUPLICATE_PROTECTION_VERSION",
            "duplicate_protection_v11.3.0",
        ),
        (
            "backend.server.coordination.coordination_governance.version_governance",
            "VERSION_GOVERNANCE_VERSION",
            "version_governance_v11.4.0",
        ),
        (
            "backend.server.coordination.coordination_governance.coordinator_lifecycle",
            "COORDINATOR_LIFECYCLE_VERSION",
            "coordinator_lifecycle_v11.5.0",
        ),
        (
            "backend.server.coordination.coordination_governance.security_boundaries",
            "SECURITY_BOUNDARIES_VERSION",
            "security_boundaries_v11.6.0",
        ),
    ):

        module = importlib.import_module(
            module_name
        )

        check(
            f"final import/version exact: {expected_version}",
            getattr(
                module,
                version_name,
            )
            == expected_version,
        )


    # ==============================================================
    # 13 — FINAL STATUS
    # ==============================================================

    section(
        "13 — PHASE 11.1–11.6 FINAL STATUS"
    )


    total = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    print(
        "TOTAL FORMAL CHECKS:",
        total,
        "PASS",
    )

    print()

    print(
        "PHASE 11.1 WORKSPACE ISOLATION: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 11.2 IDEMPOTENCY: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 11.3 DUPLICATE PROTECTION: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 11.4 VERSION GOVERNANCE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 11.5 COORDINATOR LIFECYCLE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 11.6 SECURITY BOUNDARIES: CERTIFIED + FROZEN"
    )

    print()

    print(
        "11.1 SOURCE SHA256:",
        SHA111,
    )

    print(
        "11.1 FREEZE SHA256:",
        freeze_hashes["11.1"],
    )

    print(
        "11.2 SOURCE SHA256:",
        SHA112,
    )

    print(
        "11.2 FREEZE SHA256:",
        freeze_hashes["11.2"],
    )

    print(
        "11.3 SOURCE SHA256:",
        SHA113,
    )

    print(
        "11.3 FREEZE SHA256:",
        freeze_hashes["11.3"],
    )

    print(
        "11.4 SOURCE SHA256:",
        SHA114,
    )

    print(
        "11.4 FREEZE SHA256:",
        freeze_hashes["11.4"],
    )

    print(
        "11.5 SOURCE SHA256:",
        SHA115,
    )

    print(
        "11.5 FREEZE SHA256:",
        freeze_hashes["11.5"],
    )

    print(
        "11.6 SOURCE SHA256:",
        SHA116,
    )

    print(
        "11.6 FREEZE SHA256:",
        freeze_hashes["11.6"],
    )

    print()

    print(
        "PHASE 11.1–11.6 COMPOSITE SHA256:",
        COMPOSITE,
    )

    print(
        "11.1–11.6 BATCH FREEZE SHA256:",
        BATCH_FREEZE_SHA,
    )

    print(
        "CERTIFICATION REPORT SHA256:",
        REPORT_SHA,
    )

    print()

    print(
        "PHASE 10 MODIFIED: FALSE"
    )

    print(
        "EXISTING COORDINATION COMPONENTS MODIFIED: FALSE"
    )

    print(
        "UNIVERSAL RUNTIME MODIFIED: FALSE"
    )

    print()

    print(
        "NEXT: PHASE 11.7 — GOVERNANCE CERTIFICATION"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("PHASE 11.1–11.6 BATCH FAILED — ROLLING BACK NEW FILES")
    print("=" * 120)

    for path in created:

        if path.exists():
            path.unlink()

    if (
        init_created
        and INIT.exists()
    ):
        INIT.unlink()

    try:
        if (
            GOV_ROOT.exists()
            and not any(
                GOV_ROOT.iterdir()
            )
        ):
            GOV_ROOT.rmdir()
    except Exception:
        pass

    print(
        "ROLLBACK COMPLETE."
    )

    raise
