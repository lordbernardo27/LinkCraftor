from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.server.crawler.seed_eligibility import (
    SEED_ELIGIBILITY_SCHEMA_VERSION,
    SeedEligibilityDecision,
    SeedEligibilityEvidence,
    SeedEligibilityReasonCode,
    SeedEligibilityResult,
    explain_seed_eligibility_validation_v1,
    normalize_eligibility_decision,
    normalize_eligibility_reason_code,
)


checks = 0
passed = 0


def check(
    condition: bool,
    name: str,
) -> None:
    global checks
    global passed

    checks += 1

    if condition:
        passed += 1
        print(f"[PASS] {name}")
        return

    print(f"[FAIL] {name}")
    raise AssertionError(name)


check(
    SEED_ELIGIBILITY_SCHEMA_VERSION
    == "seed_eligibility_validation.v1",
    "schema version",
)

check(
    normalize_eligibility_decision(
        "eligible"
    )
    == SeedEligibilityDecision.ELIGIBLE,
    "decision normalization",
)

check(
    normalize_eligibility_reason_code(
        "invalid_scheme"
    )
    == SeedEligibilityReasonCode.INVALID_SCHEME,
    "reason-code normalization",
)

evidence = SeedEligibilityEvidence(
    check="scheme_validation",
    passed=True,
    reason_code=(
        SeedEligibilityReasonCode.ELIGIBLE
    ),
    details={
        "scheme": "https",
    },
)

check(
    evidence.check == "scheme_validation",
    "evidence check",
)

check(
    evidence.passed is True,
    "evidence boolean",
)

check(
    evidence.to_dict()["scheme"] 
    if "scheme" in evidence.to_dict()
    else evidence.to_dict()["details"]["scheme"]
    == "https",
    "evidence serialization",
)

result = SeedEligibilityResult(
    seed_id="seed_test_001",
    workspace_id="ws_test",
    seed_type="url",
    decision="eligible",
    reason_code="eligible",
    normalized_target=(
        "https://example.com/"
    ),
    evidence=(
        evidence,
    ),
)

check(
    result.seed_id == "seed_test_001",
    "result seed identity",
)

check(
    result.workspace_id == "ws_test",
    "result workspace identity",
)

check(
    result.decision
    == SeedEligibilityDecision.ELIGIBLE,
    "result decision",
)

check(
    result.is_eligible is True,
    "is_eligible property",
)

serialized = result.to_dict()

check(
    serialized["schema_version"]
    == SEED_ELIGIBILITY_SCHEMA_VERSION,
    "result schema serialization",
)

check(
    serialized["decision"] == "eligible",
    "result decision serialization",
)

check(
    serialized["is_eligible"] is True,
    "result eligibility serialization",
)

check(
    len(serialized["evidence"]) == 1,
    "result evidence serialization",
)

explanation = (
    explain_seed_eligibility_validation_v1()
)

check(
    explanation["ok"] is True,
    "explanation contract",
)

check(
    explanation["pipeline_stage"]
    == "Seed Eligibility Validation",
    "pipeline stage",
)

check(
    explanation["previous_pipeline_stage"]
    == "Universal Web Seed Registry",
    "previous pipeline stage",
)

check(
    explanation["next_pipeline_stage"]
    == "Crawl Frontier",
    "next pipeline stage",
)

check(
    explanation["frontier_authority"] is False,
    "Crawl Frontier boundary",
)

check(
    "Crawl Frontier insertion"
    in explanation["excluded_responsibilities"],
    "frontier insertion excluded",
)

invalid_decision_rejected = False

try:
    normalize_eligibility_decision(
        "send_to_frontier"
    )
except ValueError:
    invalid_decision_rejected = True

check(
    invalid_decision_rejected,
    "invalid decision rejected",
)

invalid_reason_rejected = False

try:
    normalize_eligibility_reason_code(
        "made_up_reason"
    )
except ValueError:
    invalid_reason_rejected = True

check(
    invalid_reason_rejected,
    "invalid reason code rejected",
)

invalid_evidence_rejected = False

try:
    SeedEligibilityEvidence(
        check="test",
        passed="yes",
        reason_code="eligible",
    )
except ValueError:
    invalid_evidence_rejected = True

check(
    invalid_evidence_rejected,
    "non-boolean evidence rejected",
)

wrong_schema_rejected = False

try:
    SeedEligibilityResult(
        seed_id="seed_test_002",
        workspace_id="ws_test",
        seed_type="url",
        decision="eligible",
        reason_code="eligible",
        schema_version="wrong.v1",
    )
except ValueError:
    wrong_schema_rejected = True

check(
    wrong_schema_rejected,
    "wrong schema version rejected",
)

print("")
print("============================================================")
print("SEED ELIGIBILITY CONTRACT VERIFICATION")
print("============================================================")
print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks - passed}")

if checks != passed:
    raise SystemExit(1)

print("")
print("SEED ELIGIBILITY CONTRACT VERIFICATION: PASS")
print("")
print(
    json.dumps(
        explanation,
        indent=2,
        ensure_ascii=False,
    )
)
