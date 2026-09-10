from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .registry import get_architecture_registry
from .change_classification import get_change_classification_engine
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
from .security_control_tower_feed import (
    get_security_control_tower_feed,
)


class SecurityPhase1IntegrationCertification:
    """
    Certifies structural and operational wiring of PSA Phase 1 integration.

    This is not a full production security certification.
    """

    def evaluate(self) -> Dict[str, Any]:
        checks: Dict[str, bool] = {}

        architecture_registry = get_architecture_registry()

        checks["architecture_registry"] = architecture_registry.exists(
            "platform-security-architecture"
        )

        psa = architecture_registry.get(
            "platform-security-architecture"
        )

        checks["phase1_components_registered"] = (
            len(psa.get("components", [])) == 20
        )

        checks["change_classifier"] = (
            get_change_classification_engine() is not None
        )
        checks["adr_registry"] = (
            get_security_adr_registry() is not None
        )
        checks["control_ownership_registry"] = (
            get_security_control_ownership_registry() is not None
        )
        checks["exception_registry"] = (
            get_security_exception_registry() is not None
        )
        checks["technical_debt_registry"] = (
            get_security_technical_debt_registry() is not None
        )
        checks["sarb_workflow"] = (
            get_security_sarb_workflow() is not None
        )
        checks["foundation_certification_registry"] = (
            get_security_foundation_certification_registry()
            is not None
        )
        checks["evidence_telemetry"] = (
            get_security_evidence_telemetry() is not None
        )

        tower = get_security_control_tower_feed().snapshot()

        checks["control_tower_feed"] = (
            tower.get("mode")
            == "read-only-owner-security-control-tower-feed"
        )

        passed = all(checks.values())

        return {
            "certification_id": "SEC-CERT-PHASE1-INTEGRATION-0001",
            "architecture_id": "platform-security-architecture",
            "scope": "PSA Phase 1 Security Foundation Integration",
            "status": "certified" if passed else "failed",
            "checks": checks,
            "passed": passed,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "statement": (
                "PSA Phase 1 governance integration is structurally "
                "and operationally wired."
                if passed
                else "PSA Phase 1 integration certification failed."
            ),
            "production_security_certification": False,
        }

    def write(
        self,
        path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        result = self.evaluate()

        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "phase1_integration_certification.json"
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


def get_security_phase1_integration_certification():
    global _default_certifier

    if _default_certifier is None:
        _default_certifier = SecurityPhase1IntegrationCertification()

    return _default_certifier
