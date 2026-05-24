
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


DEFAULT_ENABLED_MODULES = [
    "internal_linking",
    "external_linking",
    "semantic_linking",
    "batch_processing",
    "upload_phrase_pool",
    "active_phrase_pool",
    "live_domain_sync",
    "draft_pool",
    "imported_pool",
    "tms",
]


DEFAULT_FEATURE_FLAGS = {
    "async_orchestration": True,
    "batch_processing": True,
    "workspace_context": True,
    "context_snapshot": True,
    "live_domain_sync": True,
    "tms_events": True,
    "owner_monitoring": False,
}


DEFAULT_LIMITS_BY_PLAN = {
    "starter": {
        "billing_limits": {"monthly_usd": 79},
        "document_limits": {"monthly_documents": 100},
        "au_limits": {"monthly_aus": 1000},
    },
    "pro": {
        "billing_limits": {"monthly_usd": 299},
        "document_limits": {"monthly_documents": 1000},
        "au_limits": {"monthly_aus": 10000},
    },
    "business": {
        "billing_limits": {"monthly_usd": 999},
        "document_limits": {"monthly_documents": 10000},
        "au_limits": {"monthly_aus": 100000},
    },
    "enterprise": {
        "billing_limits": {"monthly_usd": 4999},
        "document_limits": {"monthly_documents": 100000},
        "au_limits": {"monthly_aus": 1000000},
    },
}


@dataclass(frozen=True)
class WorkspaceContext:
    workspace_id: str
    domain: str
    plan: str
    enabled_modules: List[str]
    feature_flags: Dict[str, bool]
    billing_limits: Dict[str, Any]
    document_limits: Dict[str, Any]
    au_limits: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _domain_from_workspace_id(workspace_id: str) -> str:
    cleaned = (workspace_id or "").strip()
    if cleaned.startswith("ws_"):
        cleaned = cleaned[3:]
    return cleaned.replace("_", ".") or "unknown.local"


def load_workspace_context(workspace_id: str, plan: str = "business") -> WorkspaceContext:
    workspace_id = (workspace_id or "").strip()

    if not workspace_id:
        raise ValueError("workspace_id is required to load workspace context")

    plan = (plan or "business").strip().lower()
    if plan not in DEFAULT_LIMITS_BY_PLAN:
        plan = "business"

    limits = DEFAULT_LIMITS_BY_PLAN[plan]

    return WorkspaceContext(
        workspace_id=workspace_id,
        domain=_domain_from_workspace_id(workspace_id),
        plan=plan,
        enabled_modules=list(DEFAULT_ENABLED_MODULES),
        feature_flags=dict(DEFAULT_FEATURE_FLAGS),
        billing_limits=dict(limits["billing_limits"]),
        document_limits=dict(limits["document_limits"]),
        au_limits=dict(limits["au_limits"]),
    )
