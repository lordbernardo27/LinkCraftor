from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.server.crawler import (
    explain_universal_web_seed_controls_v1,
)

ROOT = PROJECT_ROOT

CONTROLS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "seed_controls.py"
)

INIT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "crawler"
    / "__init__.py"
)

checks = 0
passed = 0

def ok(message: str):
    global checks, passed
    checks += 1
    passed += 1
    print(f"[PASS] {message}")


assert CONTROLS_PATH.exists()
ok("seed_controls.py exists")
print(CONTROLS_PATH)

assert INIT_PATH.exists()
ok("__init__.py exists")
print(INIT_PATH)

py_compile.compile(
    str(CONTROLS_PATH),
    doraise=True,
)
ok("seed_controls.py compiles")

py_compile.compile(
    str(INIT_PATH),
    doraise=True,
)
ok("__init__.py compiles")

contract = explain_universal_web_seed_controls_v1()

assert contract["ok"]
ok("explanation contract")

assert (
    contract["component"]
    == "universal_web_seed_controls"
)
ok("component")

assert (
    contract["schema_version"]
    == "universal_web_seed_controls.v1"
)
ok("schema version")

expected = {
    "enable_seed",
    "disable_seed",
    "archive_seed",
    "restore_seed",
    "update_priority",
    "update_metadata",
}

assert expected == set(
    contract["public_operations"]
)
ok("public operations")

allowed = contract["allowed_transitions"]

assert set(
    allowed["registered"]
) == {
    "disabled",
    "archived",
}

assert set(
    allowed["disabled"]
) == {
    "registered",
    "archived",
}

assert set(
    allowed["archived"]
) == {
    "disabled",
}

ok("allowed lifecycle transitions")

assert (
    contract["transition_validator"]
    == "validate_seed_transition"
)

ok("transition validator")

assert (
    contract["next_pipeline_stage"]
    == "Seed Eligibility Validation"
)

ok("next pipeline stage")

assert (
    "crawl scheduling"
    in contract["excluded_responsibilities"]
)

assert (
    "seed registration"
    in contract["excluded_responsibilities"]
)

ok("excluded responsibilities")

print()

print(
    json.dumps(
        contract,
        indent=2,
    )
)

print()

print(f"Checks executed: {checks}")
print(f"Checks passed:   {passed}")
print(f"Checks failed:   {checks-passed}")

print()

print(
    "UNIVERSAL WEB SEED CONTROLS VERIFICATION: PASS"
)