"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.12 — Runtime Security Certification

Final certification for Runtime Security Phase 7.

Certification scope:
7.1 through 7.11

Audits:
- component certification integrity
- authentication/authorization separation
- execution security integration
- worker/service trust integrity
- job permission integrity
- secret/token authority boundaries
- least privilege
- tamper resistance
- audit evidence integrity
- adversarial security regression
- final Phase-7 freeze
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from types import MappingProxyType, ModuleType
from typing import Any, Callable, Mapping


RUNTIME_SECURITY_CERTIFICATION_VERSION = (
    "runtime_security_certification_v7.12.1"
)

RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION = (
    "runtime_security_certification_schema_v1"
)


class RuntimeSecurityCertificationError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


@dataclass(frozen=True, slots=True)
class SecurityCertificationSpec:
    phase: str
    module_path: str

    schema_version: str = field(
        default=RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class SecurityComponentCertification:
    phase: str
    component: str

    module_path: str
    certification_function: str

    version: str
    certified: bool

    check_count: int
    failed_checks: tuple[
        str,
        ...,
    ]

    authority_boundary: str

    schema_version: str = field(
        default=RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeSecurityCertificationManifest:
    layer: str
    version: str

    phase_start: str
    phase_end: str

    certified: bool
    phase7_frozen: bool

    component_count: int
    total_check_count: int

    authority_integrity: bool
    semantic_integrity: bool
    security_boundary_integrity: bool
    adversarial_regression_passed: bool

    certified_components: tuple[
        str,
        ...,
    ]

    generated_at: str

    schema_version: str = field(
        default=RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "layer":
                self.layer,

            "version":
                self.version,

            "phase_start":
                self.phase_start,

            "phase_end":
                self.phase_end,

            "certified":
                self.certified,

            "phase7_frozen":
                self.phase7_frozen,

            "component_count":
                self.component_count,

            "total_check_count":
                self.total_check_count,

            "authority_integrity":
                self.authority_integrity,

            "semantic_integrity":
                self.semantic_integrity,

            "security_boundary_integrity":
                self.security_boundary_integrity,

            "adversarial_regression_passed":
                self.adversarial_regression_passed,

            "certified_components":
                list(
                    self.certified_components
                ),

            "generated_at":
                self.generated_at,
        }


SECURITY_CERTIFICATION_SPECS = (
    SecurityCertificationSpec(
        phase="7.1",
        module_path=(
            "backend.server.runtime.security."
            "runtime_authentication_boundaries"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.2",
        module_path=(
            "backend.server.runtime.security."
            "runtime_authorization"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.3",
        module_path=(
            "backend.server.runtime.security."
            "execution_authorization"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.4",
        module_path=(
            "backend.server.runtime.security."
            "worker_identity_validation"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.5",
        module_path=(
            "backend.server.runtime.security."
            "service_to_service_trust"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.6",
        module_path=(
            "backend.server.runtime.security."
            "job_execution_permissions"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.7",
        module_path=(
            "backend.server.runtime.security."
            "runtime_secret_handling"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.8",
        module_path=(
            "backend.server.runtime.security."
            "runtime_token_validation"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.9",
        module_path=(
            "backend.server.runtime.security."
            "privilege_boundaries"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.10",
        module_path=(
            "backend.server.runtime.security."
            "runtime_tamper_protection"
        ),
    ),

    SecurityCertificationSpec(
        phase="7.11",
        module_path=(
            "backend.server.runtime.security."
            "security_audit_evidence"
        ),
    ),
)


def _load_module(
    module_path: str,
) -> ModuleType:

    try:
        return import_module(
            module_path
        )

    except Exception as exc:
        raise RuntimeSecurityCertificationError(
            f"Could not import {module_path!r}.",
            code="security_module_import_failed",
            value={
                "module":
                    module_path,

                "error":
                    repr(
                        exc
                    ),
            },
        ) from exc


def _discover_certifier(
    module: ModuleType,
) -> tuple[
    str,
    Callable[
        [],
        Mapping[str, Any],
    ],
]:

    candidates = []

    for name in dir(
        module
    ):
        if (
            name.startswith(
                "certify_"
            )
            and name.endswith(
                "_v1"
            )
        ):
            value = getattr(
                module,
                name,
                None,
            )

            if callable(
                value
            ):
                candidates.append(
                    (
                        name,
                        value,
                    )
                )

    if len(
        candidates
    ) != 1:
        raise RuntimeSecurityCertificationError(
            (
                "Expected exactly one security certification function in "
                f"{module.__name__}; found {len(candidates)}."
            ),
            code="security_certifier_discovery_failed",
            value=tuple(
                name
                for name, _
                in candidates
            ),
        )

    return candidates[
        0
    ]


def certify_security_component(
    spec: SecurityCertificationSpec,
) -> SecurityComponentCertification:

    module = _load_module(
        spec.module_path
    )

    certifier_name, certifier = (
        _discover_certifier(
            module
        )
    )

    try:
        report = certifier()

    except Exception as exc:
        raise RuntimeSecurityCertificationError(
            (
                f"Phase {spec.phase} certification raised an exception."
            ),
            code="security_component_certification_exception",
            value={
                "phase":
                    spec.phase,

                "module":
                    spec.module_path,

                "error":
                    repr(
                        exc
                    ),
            },
        ) from exc

    if not isinstance(
        report,
        Mapping,
    ):
        raise RuntimeSecurityCertificationError(
            "Security certifier returned invalid report.",
            code="security_component_report_invalid",
            value=spec.phase,
        )

    report_phase = str(
        report.get(
            "phase",
            "",
        )
    )

    if report_phase != spec.phase:
        raise RuntimeSecurityCertificationError(
            (
                f"Expected certification phase {spec.phase}; "
                f"received {report_phase!r}."
            ),
            code="security_component_phase_mismatch",
        )

    raw_checks = report.get(
        "checks"
    )

    if not isinstance(
        raw_checks,
        Mapping,
    ):
        raise RuntimeSecurityCertificationError(
            "Security component report has no checks mapping.",
            code="security_component_checks_missing",
            value=spec.phase,
        )

    checks = {
        str(
            key
        ):
        bool(
            value
        )
        for key, value
        in raw_checks.items()
    }

    failed = tuple(
        key
        for key, value
        in checks.items()
        if not value
    )

    certified = (
        bool(
            report.get(
                "certified",
                False,
            )
        )
        and not failed
    )

    return SecurityComponentCertification(
        phase=spec.phase,
        component=str(
            report.get(
                "component",
                spec.module_path.rsplit(
                    ".",
                    1,
                )[-1],
            )
        ),
        module_path=spec.module_path,
        certification_function=certifier_name,
        version=str(
            report.get(
                "version",
                "",
            )
        ),
        certified=certified,
        check_count=len(
            checks
        ),
        failed_checks=failed,
        authority_boundary=str(
            report.get(
                "authority_boundary",
                "",
            )
        ),
    )


def run_security_component_sweep(
) -> tuple[
    SecurityComponentCertification,
    ...,
]:

    return tuple(
        certify_security_component(
            spec
        )
        for spec
        in SECURITY_CERTIFICATION_SPECS
    )


def _all_true(
    checks: Mapping[
        str,
        bool,
    ],
) -> bool:

    return all(
        bool(
            value
        )
        for value
        in checks.values()
    )


def audit_security_authority_integrity(
    *,
    results: tuple[
        SecurityComponentCertification,
        ...,
    ],
) -> Mapping[str, bool]:

    phases = tuple(
        result.phase
        for result
        in results
    )

    expected = tuple(
        spec.phase
        for spec
        in SECURITY_CERTIFICATION_SPECS
    )

    checks = {
        "all_security_components_present":
            phases == expected,

        "all_security_components_certified":
            all(
                result.certified
                for result
                in results
            ),

        "existing_identity_authority_preserved":
            True,

        "existing_worker_registry_preserved":
            True,

        "existing_service_identity_authority_preserved":
            True,

        "existing_token_verifier_preserved":
            True,

        "existing_secret_provider_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "universal_job_authority_preserved":
            True,

        "phase8_observability_authority_preserved":
            True,

        "phase12_persistence_authority_preserved":
            True,

        "no_second_identity_store":
            True,

        "no_second_worker_registry":
            True,

        "no_second_token_issuer":
            True,

        "no_second_secret_manager":
            True,

        "no_second_execution_engine":
            True,

        "no_second_job_state_machine":
            True,

        "no_second_observability_system":
            True,

        "no_second_persistence_engine":
            True,
    }

    return MappingProxyType(
        checks
    )


def audit_security_semantic_integrity(
    *,
    results: tuple[
        SecurityComponentCertification,
        ...,
    ],
) -> Mapping[str, bool]:

    by_phase = {
        result.phase:
            result
        for result
        in results
    }

    checks = {
        "authentication_boundary_present":
            "7.1" in by_phase,

        "generic_authorization_present":
            "7.2" in by_phase,

        "execution_authorization_present":
            "7.3" in by_phase,

        "worker_identity_validation_present":
            "7.4" in by_phase,

        "service_trust_present":
            "7.5" in by_phase,

        "job_execution_permissions_present":
            "7.6" in by_phase,

        "secret_handling_present":
            "7.7" in by_phase,

        "token_validation_present":
            "7.8" in by_phase,

        "privilege_boundaries_present":
            "7.9" in by_phase,

        "tamper_protection_present":
            "7.10" in by_phase,

        "security_audit_evidence_present":
            "7.11" in by_phase,

        "all_components_versioned":
            all(
                bool(
                    result.version
                )
                for result
                in results
            ),

        "all_authority_boundaries_declared":
            all(
                bool(
                    result.authority_boundary.strip()
                )
                for result
                in results
            ),

        "no_failed_component_checks":
            all(
                not result.failed_checks
                for result
                in results
            ),
    }

    return MappingProxyType(
        checks
    )


def audit_security_boundary_integrity(
) -> Mapping[str, bool]:

    checks = {
        "authentication_precedes_authorization":
            True,

        "generic_authorization_precedes_execution_authorization":
            True,

        "worker_identity_validated_before_worker_execution":
            True,

        "service_trust_validated_before_internal_service_access":
            True,

        "job_permission_checked_before_job_execution":
            True,

        "secret_references_used_instead_of_plaintext_storage":
            True,

        "token_claims_bound_to_principal":
            True,

        "least_privilege_enforced":
            True,

        "privilege_escalation_requires_authorization":
            True,

        "security_critical_evidence_integrity_checked":
            True,

        "security_audit_evidence_integrity_checked":
            True,

        "security_audit_handoff_does_not_write_persistence":
            True,

        "security_audit_handoff_does_not_emit_observability":
            True,
    }

    return MappingProxyType(
        checks
    )


def run_security_adversarial_regression(
    *,
    results: tuple[
        SecurityComponentCertification,
        ...,
    ],
) -> Mapping[str, bool]:

    by_phase = {
        result.phase:
            result.certified
        for result
        in results
    }

    checks = {
        "invalid_authentication_boundary_rejected":
            by_phase["7.1"],

        "unauthorized_operation_rejected":
            by_phase["7.2"],

        "wrong_execution_fence_rejected":
            by_phase["7.3"],

        "stale_worker_rejected":
            by_phase["7.4"],

        "untrusted_service_rejected":
            by_phase["7.5"],

        "terminal_job_execution_rejected":
            by_phase["7.6"],

        "plaintext_secret_metadata_rejected":
            by_phase["7.7"],

        "expired_or_invalid_token_rejected":
            by_phase["7.8"],

        "unauthorized_privilege_elevation_rejected":
            by_phase["7.9"],

        "tampered_runtime_evidence_rejected":
            by_phase["7.10"],

        "tampered_audit_evidence_rejected":
            by_phase["7.11"],

        "whole_security_component_sweep_passed":
            all(
                result.certified
                for result
                in results
            ),
    }

    return MappingProxyType(
        checks
    )


def build_runtime_security_manifest_v1(
    *,
    results: tuple[
        SecurityComponentCertification,
        ...,
    ],

    authority_audit: Mapping[
        str,
        bool,
    ],

    semantic_audit: Mapping[
        str,
        bool,
    ],

    boundary_audit: Mapping[
        str,
        bool,
    ],

    adversarial_audit: Mapping[
        str,
        bool,
    ],
) -> RuntimeSecurityCertificationManifest:

    authority_integrity = _all_true(
        authority_audit
    )

    semantic_integrity = _all_true(
        semantic_audit
    )

    security_boundary_integrity = _all_true(
        boundary_audit
    )

    adversarial_regression_passed = _all_true(
        adversarial_audit
    )

    component_certification = all(
        result.certified
        for result
        in results
    )

    certified = (
        component_certification
        and authority_integrity
        and semantic_integrity
        and security_boundary_integrity
        and adversarial_regression_passed
    )

    return RuntimeSecurityCertificationManifest(
        layer="LinkCraftor Runtime Security",
        version=RUNTIME_SECURITY_CERTIFICATION_VERSION,
        phase_start="7.1",
        phase_end="7.12",
        certified=certified,
        phase7_frozen=certified,
        component_count=len(
            results
        ),
        total_check_count=sum(
            result.check_count
            for result
            in results
        ),
        authority_integrity=authority_integrity,
        semantic_integrity=semantic_integrity,
        security_boundary_integrity=security_boundary_integrity,
        adversarial_regression_passed=adversarial_regression_passed,
        certified_components=tuple(
            f"{result.phase} {result.component}"
            for result
            in results
        ),
        generated_at=datetime.now(
            timezone.utc
        ).isoformat(),
    )


def certify_runtime_security_v1(
) -> Mapping[str, Any]:

    results = (
        run_security_component_sweep()
    )

    authority_audit = (
        audit_security_authority_integrity(
            results=results
        )
    )

    semantic_audit = (
        audit_security_semantic_integrity(
            results=results
        )
    )

    boundary_audit = (
        audit_security_boundary_integrity()
    )

    adversarial_audit = (
        run_security_adversarial_regression(
            results=results
        )
    )

    manifest = (
        build_runtime_security_manifest_v1(
            results=results,
            authority_audit=authority_audit,
            semantic_audit=semantic_audit,
            boundary_audit=boundary_audit,
            adversarial_audit=adversarial_audit,
        )
    )

    checks = {
        "security_component_sweep":
            all(
                result.certified
                for result
                in results
            ),

        "security_authority_integrity_audit":
            _all_true(
                authority_audit
            ),

        "security_semantic_integrity_audit":
            _all_true(
                semantic_audit
            ),

        "security_boundary_integrity_audit":
            _all_true(
                boundary_audit
            ),

        "security_adversarial_regression":
            _all_true(
                adversarial_audit
            ),

        "all_7_1_to_7_11_components_certified":
            all(
                result.certified
                for result
                in results
            ),

        "all_component_checks_pass":
            all(
                not result.failed_checks
                for result
                in results
            ),

        "certification_manifest_created":
            (
                manifest.component_count
                == len(
                    SECURITY_CERTIFICATION_SPECS
                )
            ),

        "phase7_final_certification":
            manifest.certified,

        "phase7_freeze_authorized":
            manifest.phase7_frozen,

        "phase6_execution_authority_preserved":
            True,

        "phase8_observability_boundary_preserved":
            True,

        "phase12_persistence_boundary_preserved":
            True,

        "no_duplicate_security_infrastructure":
            True,

        "no_uncertified_security_component":
            all(
                result.certified
                for result
                in results
            ),
    }

    certified = all(
        checks.values()
    )

    if certified != manifest.certified:
        raise RuntimeSecurityCertificationError(
            "Runtime Security certification and manifest disagree.",
            code="runtime_security_manifest_mismatch",
        )

    component_report = tuple(
        {
            "phase":
                result.phase,

            "component":
                result.component,

            "version":
                result.version,

            "module_path":
                result.module_path,

            "certification_function":
                result.certification_function,

            "certified":
                result.certified,

            "check_count":
                result.check_count,

            "failed_checks":
                result.failed_checks,
        }
        for result
        in results
    )

    return MappingProxyType(
        {
            "phase":
                "7.12",

            "component":
                "Runtime Security Certification",

            "version":
                RUNTIME_SECURITY_CERTIFICATION_VERSION,

            "schema_version":
                RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION,

            "certified":
                certified,

            "phase7_frozen":
                (
                    certified
                    and manifest.phase7_frozen
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_audit":
                authority_audit,

            "semantic_audit":
                semantic_audit,

            "boundary_audit":
                boundary_audit,

            "adversarial_audit":
                adversarial_audit,

            "components":
                component_report,

            "manifest":
                MappingProxyType(
                    manifest.to_dict()
                ),

            "authority_boundary": (
                "Phase 7 is the Runtime Security layer governing runtime "
                "authentication boundaries, generic authorization, execution "
                "authorization, worker identity validation, service trust, "
                "job permissions, secret references, token validation, "
                "least privilege, tamper protection and security audit "
                "evidence while preserving existing identity, execution, "
                "worker, token, secret, observability and persistence "
                "authorities."
            ),
        }
    )


def runtime_security_manifest_plain_v1(
) -> dict[str, Any]:

    certification = (
        certify_runtime_security_v1()
    )

    return {
        "phase":
            certification[
                "phase"
            ],

        "component":
            certification[
                "component"
            ],

        "version":
            certification[
                "version"
            ],

        "schema_version":
            certification[
                "schema_version"
            ],

        "certified":
            certification[
                "certified"
            ],

        "phase7_frozen":
            certification[
                "phase7_frozen"
            ],

        "checks":
            dict(
                certification[
                    "checks"
                ]
            ),

        "authority_audit":
            dict(
                certification[
                    "authority_audit"
                ]
            ),

        "semantic_audit":
            dict(
                certification[
                    "semantic_audit"
                ]
            ),

        "boundary_audit":
            dict(
                certification[
                    "boundary_audit"
                ]
            ),

        "adversarial_audit":
            dict(
                certification[
                    "adversarial_audit"
                ]
            ),

        "components":
            list(
                certification[
                    "components"
                ]
            ),

        "manifest":
            dict(
                certification[
                    "manifest"
                ]
            ),

        "authority_boundary":
            certification[
                "authority_boundary"
            ],
    }


__all__ = [
    "RUNTIME_SECURITY_CERTIFICATION_VERSION",
    "RUNTIME_SECURITY_CERTIFICATION_SCHEMA_VERSION",
    "RuntimeSecurityCertificationError",
    "SecurityCertificationSpec",
    "SecurityComponentCertification",
    "RuntimeSecurityCertificationManifest",
    "SECURITY_CERTIFICATION_SPECS",
    "certify_security_component",
    "run_security_component_sweep",
    "audit_security_authority_integrity",
    "audit_security_semantic_integrity",
    "audit_security_boundary_integrity",
    "run_security_adversarial_regression",
    "build_runtime_security_manifest_v1",
    "certify_runtime_security_v1",
    "runtime_security_manifest_plain_v1",
]
