from __future__ import annotations

from typing import Any, Dict

from .registry import get_architecture_registry
from .security_adr_registry import get_security_adr_registry
from .security_control_ownership_registry import (
    get_security_control_ownership_registry,
)
from .security_exception_registry import get_security_exception_registry
from .security_technical_debt_registry import (
    get_security_technical_debt_registry,
)
from .security_sarb_workflow import get_security_sarb_workflow
from .security_foundation_certification_registry import (
    get_security_foundation_certification_registry,
)
from .security_evidence_telemetry import (
    get_security_evidence_telemetry,
)


class SecurityControlTowerFeed:
    """
    Read-only aggregation layer for Owner Security Control Tower.

    This service does not change governance state.
    """

    def snapshot(self) -> Dict[str, Any]:
        architecture_registry = get_architecture_registry()
        adr_registry = get_security_adr_registry()
        ownership_registry = get_security_control_ownership_registry()
        exception_registry = get_security_exception_registry()
        debt_registry = get_security_technical_debt_registry()
        sarb_workflow = get_security_sarb_workflow()
        certification_registry = (
            get_security_foundation_certification_registry()
        )
        evidence_service = get_security_evidence_telemetry()

        psa = architecture_registry.get(
            "platform-security-architecture"
        )

        adrs = adr_registry.list()
        controls = ownership_registry.list()
        exceptions = exception_registry.list()
        debts = debt_registry.list()
        sarb_reviews = sarb_workflow.list()
        certifications = certification_registry.list()
        evidence = evidence_service.list_evidence()

        return {
            "architecture": {
                "architecture_id": psa["architecture_id"],
                "name": psa["architecture_name"],
                "version": psa["version"],
                "status": psa["status"],
                "integration_state": psa.get("integration_state"),
                "certification_state": psa.get("certification_state"),
                "registered_components": len(
                    psa.get("components", [])
                ),
            },
            "governance": {
                "adr_count": len(adrs),
                "control_ownership_count": len(controls),
                "security_exception_count": len(exceptions),
                "technical_debt_count": len(debts),
                "sarb_review_count": len(sarb_reviews),
                "certification_count": len(certifications),
                "evidence_count": len(evidence),
            },
            "attention": {
                "unowned_controls": len(
                    ownership_registry.unowned_controls()
                ),
                "expired_exceptions": len(
                    exception_registry.expired()
                ),
                "pending_sarb_reviews": len(
                    sarb_workflow.pending()
                ),
                "open_technical_debt": len(
                    [
                        item
                        for item in debts
                        if item.get("status")
                        not in {"resolved", "closed"}
                    ]
                ),
            },
            "mode": "read-only-owner-security-control-tower-feed",
        }


_default_feed = None


def get_security_control_tower_feed():
    global _default_feed

    if _default_feed is None:
        _default_feed = SecurityControlTowerFeed()

    return _default_feed
