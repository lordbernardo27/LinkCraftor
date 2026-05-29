
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set


class StaffRole(str, Enum):
    SUPPORT_AGENT = "support_agent"
    SENIOR_AGENT = "senior_agent"
    BILLING_AGENT = "billing_agent"
    ENGINEERING = "engineering"
    MANAGER_ADMIN = "manager_admin"
    OWNER = "owner"


class Permission(str, Enum):
    VIEW_TICKETS = "view_tickets"
    REPLY_TO_TICKET = "reply_to_ticket"
    ADD_INTERNAL_NOTE = "add_internal_note"
    ASSIGN_TICKET = "assign_ticket"
    UPDATE_PRIORITY = "update_priority"
    UPDATE_SEVERITY = "update_severity"
    UPDATE_STATUS = "update_status"
    RESOLVE_TICKET = "resolve_ticket"
    CLOSE_TICKET = "close_ticket"
    VIEW_BILLING_CONTEXT = "view_billing_context"
    VIEW_ENGINEERING_CONTEXT = "view_engineering_context"
    MANAGE_STAFF = "manage_staff"
    VIEW_AUDIT_LOGS = "view_audit_logs"


ROLE_PERMISSION_REGISTRY: Dict[StaffRole, Set[Permission]] = {
    StaffRole.SUPPORT_AGENT: {
        Permission.VIEW_TICKETS,
        Permission.REPLY_TO_TICKET,
        Permission.ADD_INTERNAL_NOTE,
        Permission.UPDATE_STATUS,
    },
    StaffRole.SENIOR_AGENT: {
        Permission.VIEW_TICKETS,
        Permission.REPLY_TO_TICKET,
        Permission.ADD_INTERNAL_NOTE,
        Permission.ASSIGN_TICKET,
        Permission.UPDATE_PRIORITY,
        Permission.UPDATE_SEVERITY,
        Permission.UPDATE_STATUS,
        Permission.RESOLVE_TICKET,
        Permission.CLOSE_TICKET,
    },
    StaffRole.BILLING_AGENT: {
        Permission.VIEW_TICKETS,
        Permission.REPLY_TO_TICKET,
        Permission.ADD_INTERNAL_NOTE,
        Permission.UPDATE_STATUS,
        Permission.RESOLVE_TICKET,
        Permission.VIEW_BILLING_CONTEXT,
    },
    StaffRole.ENGINEERING: {
        Permission.VIEW_TICKETS,
        Permission.ADD_INTERNAL_NOTE,
        Permission.UPDATE_SEVERITY,
        Permission.UPDATE_STATUS,
        Permission.VIEW_ENGINEERING_CONTEXT,
    },
    StaffRole.MANAGER_ADMIN: set(Permission),
    StaffRole.OWNER: set(Permission),
}


@dataclass(frozen=True)
class StaffContext:
    staff_id: str
    email: str
    role: StaffRole
    workspace_id: str | None = None


def get_permissions_for_role(role: StaffRole | str) -> List[str]:
    normalized_role = StaffRole(role)
    return sorted(permission.value for permission in ROLE_PERMISSION_REGISTRY[normalized_role])


def staff_has_permission(role: StaffRole | str, permission: Permission | str) -> bool:
    normalized_role = StaffRole(role)
    normalized_permission = Permission(permission)
    return normalized_permission in ROLE_PERMISSION_REGISTRY[normalized_role]


def require_staff_permission(role: StaffRole | str, permission: Permission | str) -> bool:
    if not staff_has_permission(role, permission):
        raise PermissionError(f"Staff role '{role}' does not have permission '{permission}'.")
    return True


def validate_staff_role(role: str) -> bool:
    return role in {item.value for item in StaffRole}
