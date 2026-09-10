from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .registry import get_architecture_registry
from .security_risk_registry import get_security_risk_registry
from .security_threat_model_registry import (
    get_security_threat_model_registry,
)
from .security_trust_boundary_registry import (
    get_security_trust_boundary_registry,
)
from .security_attack_path_registry import (
    get_security_attack_path_registry,
)
from .security_abuse_case_registry import (
    get_security_abuse_case_registry,
)
from .security_misuse_case_registry import (
    get_security_misuse_case_registry,
)
from .security_risk_scoring import (
    get_security_risk_scoring_engine,
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
from .security_phase2_control_tower_feed import (
    get_security_phase2_control_tower_feed,
)


class SecurityPhase2Certification:
    def evaluate(self) -> Dict[str, Any]:
        architecture_registry = get_architecture_registry()

        psa = architecture_registry.get(
            "platform-security-architecture"
        )

        component_ids = {
            component["component_id"]
            for component in psa.get("components", [])
        }

        required = {
            f"2.1.{number}"
            for number in range(1, 21)
        }

        checks = {
            "all_phase2_components_registered":
                required.issubset(component_ids),

            "risk_registry":
                get_security_risk_registry() is not None,

            "threat_model_registry":
                get_security_threat_model_registry() is not None,

            "trust_boundary_registry":
                get_security_trust_boundary_registry() is not None,

            "attack_path_registry":
                get_security_attack_path_registry() is not None,

            "abuse_case_registry":
                get_security_abuse_case_registry() is not None,

            "misuse_case_registry":
                get_security_misuse_case_registry() is not None,

            "risk_scoring_engine":
                get_security_risk_scoring_engine() is not None,

            "risk_acceptance_workflow":
                get_security_risk_acceptance_workflow() is not None,

            "risk_treatment_registry":
                get_security_risk_treatment_registry() is not None,

            "residual_risk_tracker":
                get_security_residual_risk_tracker() is not None,

            "continuous_threat_review":
                get_security_continuous_threat_review() is not None,
        }

        tower = get_security_phase2_control_tower_feed().snapshot()

        checks["control_tower_feed"] = (
            tower.get("mode")
            == "read-only-psa-phase2-control-tower-feed"
        )

        passed = all(checks.values())

        return {
            "certification_id":
                "SEC-CERT-RISK-THREAT-0001",

            "architecture_id":
                "platform-security-architecture",

            "scope":
                "PSA Phase 2 Security Risk Threat and Trust Architecture",

            "status":
                "certified" if passed else "failed",

            "passed":
                passed,

            "checks":
                checks,

            "generated_at":
                datetime.now(timezone.utc).isoformat(),

            "production_security_certification":
                False,

            "statement":
                (
                    "PSA Phase 2 Risk, Threat and Trust Architecture "
                    "is structurally and operationally integrated."
                    if passed
                    else
                    "PSA Phase 2 certification failed."
                ),
        }

    def write(
        self,
        path: Optional[Path] = None,
    ) -> Dict[str, Any]:

        result = self.evaluate()

        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "phase2_risk_threat_certification.json"
            )

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        temp = path.with_suffix(path.suffix + ".tmp")

        with temp.open("w", encoding="utf-8") as handle:
            json.dump(
                result,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temp.replace(path)

        return result


_default_certifier = None


def get_security_phase2_certification():
    global _default_certifier

    if _default_certifier is None:
        _default_certifier = SecurityPhase2Certification()

    return _default_certifier
