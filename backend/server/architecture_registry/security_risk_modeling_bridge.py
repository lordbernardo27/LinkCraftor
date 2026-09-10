from __future__ import annotations

from typing import Any, Dict, Optional

from .security_risk_registry import (
    SecurityRiskRegistry,
    get_security_risk_registry,
)


class SecurityRiskModelingBridge:
    """
    Converts modeled security findings into formal Security Risk Registry
    records while preserving their source provenance.
    """

    def __init__(
        self,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        self.risk_registry = (
            risk_registry
            if risk_registry is not None
            else get_security_risk_registry()
        )

    def create_from_model(
        self,
        *,
        risk_id: str,
        title: str,
        risk_statement: str,
        category: str,
        risk_owner: str,
        source_type: str,
        source_id: str,
        source_component_id: str,
    ) -> Dict[str, Any]:

        allowed_sources = {
            "trust-boundary",
            "attack-path",
            "abuse-case",
            "misuse-case",
        }

        if source_type not in allowed_sources:
            raise ValueError("invalid modeled risk source")

        return self.risk_registry.register({
            "risk_id": risk_id,
            "title": title,
            "architecture_id": "platform-security-architecture",
            "risk_statement": risk_statement,
            "category": category,
            "risk_owner": risk_owner,
            "status": "identified",
            "severity": "unscored",
            "source": source_type,
            "source_id": source_id,
            "source_component_id": source_component_id,
        })


_default_bridge = None


def get_security_risk_modeling_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = SecurityRiskModelingBridge()

    return _default_bridge
