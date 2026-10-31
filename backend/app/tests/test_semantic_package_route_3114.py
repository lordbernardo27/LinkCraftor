
"""Phase 3.11.4 ? Production package wiring guard tests."""

import ast
from pathlib import Path

from backend.app.tests.test_semantic_intelligence_package_39 import (
    build,
    provenance_fixture,
)


ROUTE = Path("backend/server/routes/engine_run.py")


def route_source():
    source = ROUTE.read_text(encoding="utf-8-sig")
    ast.parse(source)
    return source


def test_3114_route_contains_canonical_package_call():
    tree = ast.parse(route_source())
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "build_semantic_intelligence_package"
    ]
    assert len(calls) == 1


def test_3114_package_remains_advisory():
    result = build(provenance_fixture())
    assert result["status"] == "package_envelope_created"
    assert result["scorer_invoked"] is False
    assert result["semantic_certification_performed"] is False
    assert result["automatic_linking_authorized"] is False


def test_3114_package_validation_precedes_prepared_status():
    source = route_source()
    start = source.index("canonical_semantic_package_3114")
    validation = source.index(
        'canonical_semantic_package.get("status")',
        start,
    )
    prepared = source.index(
        '"canonical_package_status": canonical_semantic_package',
        start,
    )
    assert start < validation < prepared


def test_3114_legacy_density_path_retained():
    source = route_source()
    assert "apply_highlight_density(" in source
    assert "Legacy Density modified the canonical Pipeline 2 handoff" in source


def test_3114_failure_does_not_claim_readiness():
    source = route_source()
    assert "Canonical Phase 3.9 package validation failed:" in source
    assert '"handoff_prepared": False' in source
    assert '"status": "unavailable"' in source
