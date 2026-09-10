from __future__ import annotations

from typing import Any, Dict, Optional

from .security_risk_registry import (
    SecurityRiskRegistry,
    get_security_risk_registry,
)
from .security_threat_model_registry import (
    SecurityThreatModelRegistry,
    get_security_threat_model_registry,
)


class SecurityThreatRiskBridge:
    """
    Connects registered threat models to the Security Risk Registry.

    The bridge does not score or accept risk. Those responsibilities belong
    to PSA 2.1.15 and 2.1.16.
    """

    def __init__(
        self,
        threat_registry: Optional[SecurityThreatModelRegistry] = None,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        self.threat_registry = (
            threat_registry
            if threat_registry is not None
            else get_security_threat_model_registry()
        )

        self.risk_registry = (
            risk_registry
            if risk_registry is not None
            else get_security_risk_registry()
        )

    def create_risk_from_threat(
        self,
        *,
        risk_id: str,
        threat_model_id: str,
        title: str,
        risk_statement: str,
        category: str,
        risk_owner: str,
        threat_scenario: str,
        severity: str = "unscored",
    ) -> Dict[str, Any]:

        model = self.threat_registry.get(threat_model_id)

        return self.risk_registry.register({
            "risk_id": risk_id,
            "title": title,
            "architecture_id": model["architecture_id"],
            "risk_statement": risk_statement,
            "category": category,
            "risk_owner": risk_owner,
            "status": "identified",
            "severity": severity,
            "source": "threat-model",
            "source_threat_model_id": model["threat_model_id"],
            "source_component_id": model["component_id"],
            "threat_scenario": threat_scenario,
        })


_default_bridge = None


def get_security_threat_risk_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = SecurityThreatRiskBridge()

    return _default_bridge
