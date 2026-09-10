from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

from .security_risk_registry import (
    SecurityRiskRegistry,
    get_security_risk_registry,
)


@dataclass(frozen=True)
class SecurityRiskScore:
    likelihood: int
    impact: int
    inherent_score: int
    inherent_severity: str
    control_effectiveness: int
    residual_score: int
    residual_severity: str


class SecurityRiskScoringEngine:
    def __init__(
        self,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        self.risk_registry = (
            risk_registry
            if risk_registry is not None
            else get_security_risk_registry()
        )

    @staticmethod
    def severity(score: int) -> str:
        if score < 1 or score > 25:
            raise ValueError("risk score must be between 1 and 25")

        if score <= 4:
            return "low"

        if score <= 9:
            return "medium"

        if score <= 16:
            return "high"

        return "critical"

    def calculate(
        self,
        likelihood: int,
        impact: int,
        *,
        control_effectiveness: int = 0,
    ) -> SecurityRiskScore:

        if likelihood < 1 or likelihood > 5:
            raise ValueError("likelihood must be between 1 and 5")

        if impact < 1 or impact > 5:
            raise ValueError("impact must be between 1 and 5")

        if (
            control_effectiveness < 0
            or control_effectiveness > 100
        ):
            raise ValueError(
                "control_effectiveness must be between 0 and 100"
            )

        inherent_score = likelihood * impact

        remaining_fraction = (
            100 - control_effectiveness
        ) / 100.0

        residual_score = max(
            1,
            math.ceil(
                inherent_score * remaining_fraction
            ),
        )

        return SecurityRiskScore(
            likelihood=likelihood,
            impact=impact,
            inherent_score=inherent_score,
            inherent_severity=self.severity(inherent_score),
            control_effectiveness=control_effectiveness,
            residual_score=residual_score,
            residual_severity=self.severity(residual_score),
        )

    def score_risk(
        self,
        risk_id: str,
        likelihood: int,
        impact: int,
        *,
        control_effectiveness: int = 0,
    ) -> Dict:

        result = self.calculate(
            likelihood,
            impact,
            control_effectiveness=control_effectiveness,
        )

        return self.risk_registry.update(
            risk_id,
            {
                "likelihood": result.likelihood,
                "impact": result.impact,
                "inherent_score": result.inherent_score,
                "inherent_severity": result.inherent_severity,
                "control_effectiveness": result.control_effectiveness,
                "residual_score": result.residual_score,
                "residual_severity": result.residual_severity,
                "severity": result.residual_severity,
            },
        )


_default_engine = None


def get_security_risk_scoring_engine():
    global _default_engine

    if _default_engine is None:
        _default_engine = SecurityRiskScoringEngine()

    return _default_engine
