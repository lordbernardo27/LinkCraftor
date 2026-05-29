
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class StaffRoleDefinition:
    key: str
    label: str
    description: str
    level: int
    department: str
    can_manage_staff: bool
    can_view_sensitive_context: bool


STAFF_ROLE_DEFINITIONS: Dict[str, StaffRoleDefinition] = {
    "support_agent": StaffRoleDefinition(
        key="support_agent",
        label="Support Agent",
        description="Handles normal customer tickets, replies, and basic status updates.",
        level=1,
        department="support",
        can_manage_staff=False,
        can_view_sensitive_context=False,
    ),
    "senior_agent": StaffRoleDefinition(
        key="senior_agent",
        label="Senior Agent",
        description="Handles advanced support cases, assignment, priority, severity, resolve, and close flows.",
        level=2,
        department="support",
        can_manage_staff=False,
        can_view_sensitive_context=True,
    ),
    "billing_agent": StaffRoleDefinition(
        key="billing_agent",
        label="Billing Agent",
        description="Handles billing-related support, payment issues, invoices, and subscription context.",
        level=2,
        department="billing",
        can_manage_staff=False,
        can_view_sensitive_context=True,
    ),
    "engineering": StaffRoleDefinition(
        key="engineering",
        label="Engineering",
        description="Handles technical escalations, engine failures, worker issues, and system investigations.",
        level=3,
        department="engineering",
        can_manage_staff=False,
        can_view_sensitive_context=True,
    ),
    "manager_admin": StaffRoleDefinition(
        key="manager_admin",
        label="Manager/Admin",
        description="Manages support operations, staff oversight, escalation governance, and administrative workflows.",
        level=4,
        department="management",
        can_manage_staff=True,
        can_view_sensitive_context=True,
    ),
    "owner": StaffRoleDefinition(
        key="owner",
        label="Owner",
        description="Founder-level role with full access to support operations, audit, intelligence, and governance.",
        level=5,
        department="owner",
        can_manage_staff=True,
        can_view_sensitive_context=True,
    ),
}


def get_staff_role_definition(role_key: str) -> StaffRoleDefinition:
    if role_key not in STAFF_ROLE_DEFINITIONS:
        raise ValueError(f"Unknown staff role: {role_key}")

    return STAFF_ROLE_DEFINITIONS[role_key]


def list_staff_role_definitions() -> List[dict]:
    return [
        {
            "key": role.key,
            "label": role.label,
            "description": role.description,
            "level": role.level,
            "department": role.department,
            "can_manage_staff": role.can_manage_staff,
            "can_view_sensitive_context": role.can_view_sensitive_context,
        }
        for role in STAFF_ROLE_DEFINITIONS.values()
    ]
