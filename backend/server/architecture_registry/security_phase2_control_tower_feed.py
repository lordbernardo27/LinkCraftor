from __future__ import annotations

from typing import Any, Dict

from .security_risk_registry import get_security_risk_registry
from .security_threat_model_registry import (
    get_security_threat_model_registry,
)
from .security_risk_acceptance import (
    get_security_risk_acceptance_workflow,
)
from .security_risk_treatment import (
    get_security_risk_treatment_registry,
)
from .security_residual_risk_tracker import (
    get_security_residual_risk_tracker,
)
from .security_continuous_threat_review import (
    get_security_continuous_threat_review,
)


class SecurityPhase2ControlTowerFeed:
    def snapshot(self) -> Dict[str, Any]:
        risks = get_security_risk_registry()
        threats = get_security_threat_model_registry()
        acceptances = get_security_risk_acceptance_workflow()
        treatments = get_security_risk_treatment_registry()
        residual = get_security_residual_risk_tracker()
        reviews = get_security_continuous_threat_review()

        all_risks = risks.list()

        return {
            "phase": "PSA Phase 2",
            "risk": {
                "total": len(all_risks),
                "open": len(risks.open_risks()),
                "critical": len(risks.critical_risks()),
                "high": len([
                    risk
                    for risk in risks.open_risks()
                    if risk.get("severity") == "high"
                ]),
                "unscored": len([
                    risk
                    for risk in risks.open_risks()
                    if risk.get("severity") == "unscored"
                ]),
            },
            "threat_models": {
                "total": len(threats.list()),
            },
            "governance": {
                "risk_acceptances": len(acceptances.list()),
                "expired_acceptances": len(acceptances.expired()),
                "risk_treatments": len(treatments.list()),
                "residual_assessments": len(residual.list()),
                "threat_reviews": len(reviews.list()),
                "due_threat_reviews": len(reviews.due()),
            },
            "mode": "read-only-psa-phase2-control-tower-feed",
        }


_default_feed = None


def get_security_phase2_control_tower_feed():
    global _default_feed

    if _default_feed is None:
        _default_feed = SecurityPhase2ControlTowerFeed()

    return _default_feed
