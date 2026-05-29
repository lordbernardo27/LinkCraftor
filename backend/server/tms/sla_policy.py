
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class SLAPolicy:
    key: str
    label: str
    first_response_minutes: int
    resolution_minutes: int
    escalation_minutes: int
    applies_to_priority: str
    workspace_tier: str = "default"


DEFAULT_PRIORITY_SLA_POLICIES: Dict[str, SLAPolicy] = {
    "Low": SLAPolicy(
        key="default_low",
        label="Default Low Priority SLA",
        first_response_minutes=1440,
        resolution_minutes=10080,
        escalation_minutes=2880,
        applies_to_priority="Low",
    ),
    "Medium": SLAPolicy(
        key="default_medium",
        label="Default Medium Priority SLA",
        first_response_minutes=720,
        resolution_minutes=4320,
        escalation_minutes=1440,
        applies_to_priority="Medium",
    ),
    "High": SLAPolicy(
        key="default_high",
        label="Default High Priority SLA",
        first_response_minutes=240,
        resolution_minutes=1440,
        escalation_minutes=480,
        applies_to_priority="High",
    ),
    "Urgent": SLAPolicy(
        key="default_urgent",
        label="Default Urgent Priority SLA",
        first_response_minutes=60,
        resolution_minutes=480,
        escalation_minutes=120,
        applies_to_priority="Urgent",
    ),
}


ENTERPRISE_PRIORITY_SLA_POLICIES: Dict[str, SLAPolicy] = {
    "Low": SLAPolicy(
        key="enterprise_low",
        label="Enterprise Low Priority SLA",
        first_response_minutes=720,
        resolution_minutes=4320,
        escalation_minutes=1440,
        applies_to_priority="Low",
        workspace_tier="enterprise",
    ),
    "Medium": SLAPolicy(
        key="enterprise_medium",
        label="Enterprise Medium Priority SLA",
        first_response_minutes=240,
        resolution_minutes=1440,
        escalation_minutes=480,
        applies_to_priority="Medium",
        workspace_tier="enterprise",
    ),
    "High": SLAPolicy(
        key="enterprise_high",
        label="Enterprise High Priority SLA",
        first_response_minutes=120,
        resolution_minutes=720,
        escalation_minutes=240,
        applies_to_priority="High",
        workspace_tier="enterprise",
    ),
    "Urgent": SLAPolicy(
        key="enterprise_urgent",
        label="Enterprise Urgent Priority SLA",
        first_response_minutes=30,
        resolution_minutes=240,
        escalation_minutes=60,
        applies_to_priority="Urgent",
        workspace_tier="enterprise",
    ),
}


WORKSPACE_SLA_OVERRIDES: Dict[str, Dict[str, SLAPolicy]] = {}


def validate_sla_policy(policy: SLAPolicy) -> bool:
    if not policy.key.strip():
        raise ValueError("SLA policy key is required.")

    if not policy.label.strip():
        raise ValueError("SLA policy label is required.")

    if policy.first_response_minutes <= 0:
        raise ValueError("First response minutes must be greater than zero.")

    if policy.resolution_minutes <= 0:
        raise ValueError("Resolution minutes must be greater than zero.")

    if policy.escalation_minutes <= 0:
        raise ValueError("Escalation minutes must be greater than zero.")

    if policy.first_response_minutes > policy.resolution_minutes:
        raise ValueError("First response SLA cannot exceed resolution SLA.")

    if policy.escalation_minutes > policy.resolution_minutes:
        raise ValueError("Escalation SLA cannot exceed resolution SLA.")

    return True


def get_sla_policy_for_ticket(
    priority: str,
    workspace_tier: str = "default",
    workspace_id: Optional[str] = None,
) -> SLAPolicy:
    if workspace_id and workspace_id in WORKSPACE_SLA_OVERRIDES:
        override = WORKSPACE_SLA_OVERRIDES[workspace_id].get(priority)
        if override:
            validate_sla_policy(override)
            return override

    if workspace_tier == "enterprise":
        policy = ENTERPRISE_PRIORITY_SLA_POLICIES.get(priority)
    else:
        policy = DEFAULT_PRIORITY_SLA_POLICIES.get(priority)

    if not policy:
        raise ValueError(f"No SLA policy found for priority: {priority}")

    validate_sla_policy(policy)
    return policy


def register_workspace_sla_override(
    workspace_id: str,
    priority: str,
    policy: SLAPolicy,
) -> None:
    validate_sla_policy(policy)

    if workspace_id not in WORKSPACE_SLA_OVERRIDES:
        WORKSPACE_SLA_OVERRIDES[workspace_id] = {}

    WORKSPACE_SLA_OVERRIDES[workspace_id][priority] = policy


def list_sla_policies(workspace_tier: str = "default") -> list[dict]:
    policies = (
        ENTERPRISE_PRIORITY_SLA_POLICIES
        if workspace_tier == "enterprise"
        else DEFAULT_PRIORITY_SLA_POLICIES
    )

    return [asdict(policy) for policy in policies.values()]
