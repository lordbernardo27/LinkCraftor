# -*- coding: utf-8 -*-
"""Phase 1.1.15 - Runtime Foundation Certification.

This module certifies the Runtime Foundation as a whole (phases 1.1.1
through 1.1.14) rather than any single component. It resolves each
foundation component by module name, binds the public contract of every
component into a deterministic implementation fingerprint, and evaluates
foundation-level guarantees: component presence, interface integrity,
dependency consistency, runtime boundaries, lifecycle integrity,
boot/shutdown composition, cross-component contracts, deterministic
behaviour and overall Phase 1 completeness.

The certification is honest and fail-closed: a check that fails or raises
yields a failed report, never a false pass. It performs no filesystem
writes, no network access, no database access, starts no application, and
mutates no production state. Components are verified by contract
introspection and are never booted or executed; the only behaviour
exercised at runtime is the schema subsystem's own isolated
self-certification, which itself runs solely against in-memory fixtures.

Determinism is layered so timestamps cannot corrupt evidence: the
implementation fingerprint binds only component public contracts, the
certification fingerprint binds the implementation together with the
check matrix and its results, and only the report fingerprint
incorporates the generation timestamp.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

# ---------------------------------------------------------------------------
# Contract constants
# ---------------------------------------------------------------------------

#: Version of the foundation certification contract implemented here.
FOUNDATION_CERTIFICATION_CONTRACT_VERSION: str = "1.0.0"

#: Phase identifier for the certified foundation.
FOUNDATION_PHASE: str = "1.1"

#: Human-readable subsystem label for the report.
FOUNDATION_SUBSYSTEM: str = "1.1.15 Runtime Foundation Certification"

#: Structure tag mixed into every foundation certification fingerprint.
FOUNDATION_STRUCTURE_KIND: str = "runtime.foundation.certification"

# Component role identifiers, in dependency order.
ROLE_KERNEL: str = "universal_runtime_kernel"
ROLE_CONFIGURATION: str = "runtime_configuration"
ROLE_ENVIRONMENT: str = "runtime_environment"
ROLE_SERVICE_REGISTRY: str = "runtime_service_registry"
ROLE_LIFECYCLE: str = "runtime_lifecycle_manager"
ROLE_BOOT: str = "runtime_boot_process"
ROLE_SHUTDOWN: str = "runtime_shutdown_process"
ROLE_VERSIONING: str = "runtime_versioning"
ROLE_COMPATIBILITY: str = "runtime_compatibility_layer"
ROLE_FEATURE_FLAGS: str = "runtime_feature_flags"
ROLE_CAPABILITY: str = "runtime_capability_negotiation"
ROLE_PERSISTENCE: str = "runtime_persistence_interface"
ROLE_STATE_STORE: str = "runtime_state_store_abstraction"
ROLE_SCHEMA: str = "runtime_schema_management"


@dataclass(frozen=True, slots=True)
class _ComponentSpec:
    """Static description of one foundation component to certify."""

    index_label: str
    role: str
    name: str
    candidates: tuple[str, ...]


#: The 14 foundation components, in phase order. Each carries an ordered
#: tuple of candidate module names so certification is resilient to local
#: naming variance; the first importable candidate is used.
FOUNDATION_COMPONENTS: tuple[_ComponentSpec, ...] = (
    _ComponentSpec(
        "1.1.1",
        ROLE_KERNEL,
        "Universal Runtime Kernel",
        ("universal_runtime_kernel",),
    ),
    _ComponentSpec(
        "1.1.2",
        ROLE_CONFIGURATION,
        "Runtime Configuration",
        ("runtime_configuration",),
    ),
    _ComponentSpec(
        "1.1.3",
        ROLE_ENVIRONMENT,
        "Runtime Environment",
        ("runtime_environment",),
    ),
    _ComponentSpec(
        "1.1.4",
        ROLE_SERVICE_REGISTRY,
        "Runtime Service Registry",
        ("runtime_service_registry",),
    ),
    _ComponentSpec(
        "1.1.5",
        ROLE_LIFECYCLE,
        "Runtime Lifecycle Manager",
        ("runtime_lifecycle_manager",),
    ),
    _ComponentSpec(
        "1.1.6",
        ROLE_BOOT,
        "Runtime Boot Process",
        ("runtime_boot_process",),
    ),
    _ComponentSpec(
        "1.1.7",
        ROLE_SHUTDOWN,
        "Runtime Shutdown Process",
        ("runtime_shutdown_process",),
    ),
    _ComponentSpec(
        "1.1.8",
        ROLE_VERSIONING,
        "Runtime Versioning",
        ("runtime_versioning",),
    ),
    _ComponentSpec(
        "1.1.9",
        ROLE_COMPATIBILITY,
        "Runtime Compatibility Layer",
        ("runtime_compatibility",),
    ),
    _ComponentSpec(
        "1.1.10",
        ROLE_FEATURE_FLAGS,
        "Runtime Feature Flags",
        ("runtime_feature_flags",),
    ),
    _ComponentSpec(
        "1.1.11",
        ROLE_CAPABILITY,
        "Runtime Capability Negotiation",
        ("runtime_capability_negotiation",),
    ),
    _ComponentSpec(
        "1.1.12",
        ROLE_PERSISTENCE,
        "Runtime Persistence Interface",
        ("runtime_persistence",),
    ),
    _ComponentSpec(
        "1.1.13",
        ROLE_STATE_STORE,
        "Runtime State Store Abstraction",
        ("runtime_state_store",),
    ),
    _ComponentSpec(
        "1.1.14",
        ROLE_SCHEMA,
        "Runtime Schema Management",
        ("runtime_schema.certification",),
    ),
)

#: Candidate locations for the schema subsystem's own certifier class.
_SCHEMA_CERTIFIER_CANDIDATES: tuple[str, ...] = (
    "runtime_schema.certification",
)

_SCHEMA_CERTIFIER_ATTRIBUTE: str = (
    "RuntimeSchemaCertification"
)

#: Network-client libraries a pure foundation abstraction must not bind.
#:
#: Low-level standard-library primitives such as ``socket``, ``ssl``,
#: ``http`` and ``asyncio`` are intentionally not rejected merely because
#: a foundation component imports them. Runtime certification separately
#: verifies that certification execution performs no actual network access.
_FORBIDDEN_NETWORK_MODULES: frozenset[str] = frozenset(
    {
        "urllib",
        "urllib3",
        "ftplib",
        "requests",
        "aiohttp",
        "httpx",
        "websocket",
        "websockets",
    }
)
_FORBIDDEN_DATABASE_MODULES: frozenset[str] = frozenset(
    {"sqlite3", "psycopg2", "pymysql", "mysql", "sqlalchemy", "pymongo",
     "redis"}
)
_FORBIDDEN_PROCESS_MODULES: frozenset[str] = frozenset(
    {"subprocess", "multiprocessing"}
)

#: Sentinels that would indicate an application was booted at import time.
_BOOT_SENTINELS: frozenset[str] = frozenset(
    {"__runtime_booted__", "_BOOTED", "_RUNNING", "_APPLICATION_STARTED"}
)


# ---------------------------------------------------------------------------
# Deterministic, dependency-free canonicalisation
# ---------------------------------------------------------------------------


def _canonical_json(payload: Any) -> str:
    """Serialise *payload* to a canonical, deterministic JSON string."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def _fingerprint(payload: Any) -> str:
    """Return the SHA-256 hex digest of *payload*'s canonical form."""
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    """Current UTC time as a canonical microsecond timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _public_api(module: Any) -> tuple[str, ...]:
    """Return a component's explicit declared public surface."""
    declared = getattr(
        module,
        "__all__",
        None,
    )

    if (
        not isinstance(
            declared,
            (
                list,
                tuple,
            ),
        )
        or not declared
    ):
        raise RuntimeError(
            f"{module.__name__} must declare a non-empty __all__"
        )

    normalized = tuple(
        sorted(
            str(name)
            for name in declared
        )
    )

    if len(
        normalized
    ) != len(
        set(
            normalized
        )
    ):
        raise RuntimeError(
            f"{module.__name__} contains duplicate __all__ entries"
        )

    for name in normalized:
        if (
            not name
            or name.startswith(
                "_"
            )
        ):
            raise RuntimeError(
                f"{module.__name__} exports invalid public name {name!r}"
            )

        if not hasattr(
            module,
            name,
        ):
            raise RuntimeError(
                f"{module.__name__} declares missing public name {name!r}"
            )

    return normalized


# ---------------------------------------------------------------------------
# Immutable certification value objects
# ---------------------------------------------------------------------------


class CertificationStatus(str, Enum):
    """Outcome of a single check or of the overall certification."""

    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class CertificationCheck:
    """Immutable record of one executed foundation check."""

    check_id: str
    section: str
    name: str
    requirement: str
    status: CertificationStatus
    detail: str

    @property
    def passed(self) -> bool:
        return self.status is CertificationStatus.PASS

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "section": self.section,
            "name": self.name,
            "requirement": self.requirement,
            "status": self.status.value,
            "detail": self.detail,
        }

    def identity_dict(self) -> dict[str, Any]:
        """Timestamp-independent identity bound by the matrix fingerprint."""
        return {
            "check_id": self.check_id,
            "section": self.section,
            "name": self.name,
            "requirement": self.requirement,
            "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class CertificationSection:
    """Immutable summary of one matrix section."""

    name: str
    checks: tuple[CertificationCheck, ...]
    passed_count: int
    failed_count: int
    status: CertificationStatus

    @classmethod
    def build(
        cls, name: str, checks: tuple[CertificationCheck, ...]
    ) -> "CertificationSection":
        passed = sum(1 for check in checks if check.passed)
        failed = len(checks) - passed
        status = (
            CertificationStatus.PASS
            if failed == 0 and checks
            else CertificationStatus.FAIL
        )
        return cls(name, checks, passed, failed, status)

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "status": self.status.value,
            "checks": [check.to_canonical_dict() for check in self.checks],
        }

    def summary_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "status": self.status.value,
            "total_checks": len(self.checks),
        }


@dataclass(frozen=True, slots=True)
class RuntimeFoundationCertificationReport:
    """Immutable, canonical foundation certification report."""

    certification_id: str
    phase: str
    subsystem: str
    certification_contract_version: str
    implementation_fingerprint: str
    certification_fingerprint: str
    matrix_fingerprint: str
    certified: bool
    complete: bool
    status: CertificationStatus
    passed_checks: int
    failed_checks: int
    total_checks: int
    section_summaries: tuple[dict[str, Any], ...]
    sections: tuple[CertificationSection, ...]
    failure_codes: tuple[str, ...]
    generated_at: str
    report_fingerprint: str

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "phase": self.phase,
            "subsystem": self.subsystem,
            "certification_contract_version": (
                self.certification_contract_version
            ),
            "implementation_fingerprint": self.implementation_fingerprint,
            "certification_fingerprint": self.certification_fingerprint,
            "matrix_fingerprint": self.matrix_fingerprint,
            "certified": self.certified,
            "complete": self.complete,
            "status": self.status.value,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "total_checks": self.total_checks,
            "section_summaries": [dict(s) for s in self.section_summaries],
            "sections": [s.to_canonical_dict() for s in self.sections],
            "failure_codes": list(self.failure_codes),
            "generated_at": self.generated_at,
            "report_fingerprint": self.report_fingerprint,
        }


# ---------------------------------------------------------------------------
# Assertion helper
# ---------------------------------------------------------------------------


def _expect(condition: bool, message: str) -> None:
    """Raise :class:`AssertionError` when *condition* is false."""
    if not condition:
        raise AssertionError(message)


# ---------------------------------------------------------------------------
# The foundation certification implementation
# ---------------------------------------------------------------------------


class RuntimeFoundationCertification:
    """Deterministic, thread-safe certifier for the whole Runtime Foundation.

    Implements the canonical certification interface: :meth:`certify`,
    :meth:`last_report` and :meth:`certification_fingerprint`. A single
    instance may be certified repeatedly and shared across threads; each
    :meth:`certify` call resolves the foundation afresh, runs the full
    matrix and atomically publishes an immutable report.
    """

    __slots__ = ("_lock", "_report_json", "_report_fingerprint")

    def __init__(self) -> None:
        object.__setattr__(self, "_lock", threading.RLock())
        object.__setattr__(self, "_report_json", None)
        object.__setattr__(self, "_report_fingerprint", None)

    # -- canonical certification interface ----------------------------------

    def certify(self) -> Mapping[str, Any]:
        """Run the full matrix and publish an immutable canonical report."""
        resolutions = self._resolve_components()
        sections = self._run_matrix(resolutions)
        report = self._assemble_report(resolutions, sections)
        text = _canonical_json(report.to_canonical_dict())
        with self._lock:
            object.__setattr__(self, "_report_json", text)
            object.__setattr__(
                self, "_report_fingerprint", report.report_fingerprint
            )
        return MappingProxyType(json.loads(text))

    def last_report(self) -> Optional[Mapping[str, Any]]:
        """Return the most recent report as an immutable mapping, or None."""
        with self._lock:
            text = self._report_json
        if text is None:
            return None
        return MappingProxyType(json.loads(text))

    def certification_fingerprint(self) -> Optional[str]:
        """Return the most recent report fingerprint, or None."""
        with self._lock:
            return self._report_fingerprint

    # -- component resolution ----------------------------------------------

    @staticmethod
    def _import_module(
        candidates: tuple[str, ...],
    ) -> tuple[Any, str]:
        """Import the single canonical module candidate."""
        if len(
            candidates
        ) != 1:
            raise ImportError(
                "foundation components must declare exactly "
                "one canonical module name"
            )

        logical = candidates[
            0
        ]

        try:
            module = importlib.import_module(
                logical
            )
        except Exception as exc:
            raise ImportError(
                f"{logical}: {type(exc).__name__}: {exc}"
            ) from exc

        return module, logical

    def _resolve_components(self) -> dict[str, dict[str, Any]]:
        """Resolve every foundation component, capturing failures."""
        resolutions: dict[str, dict[str, Any]] = {}
        for spec in FOUNDATION_COMPONENTS:
            entry: dict[str, Any] = {
                "spec": spec,
                "module": None,
                "logical": None,
                "public_api": (),
                "error": None,
            }
            try:
                module, logical = self._import_module(spec.candidates)
                entry["module"] = module
                entry["logical"] = logical
                entry["public_api"] = _public_api(module)
            except Exception as exc:  # noqa: BLE001
                entry["error"] = f"{type(exc).__name__}: {exc}"
            resolutions[spec.role] = entry
        return resolutions

    def _resolve_schema_certifier(
        self,
    ) -> Any:
        """Instantiate the canonical Runtime Schema certifier."""
        module, _ = self._import_module(
            _SCHEMA_CERTIFIER_CANDIDATES
        )

        certifier_class = getattr(
            module,
            _SCHEMA_CERTIFIER_ATTRIBUTE,
            None,
        )

        if certifier_class is None:
            raise LookupError(
                "runtime_schema.certification does not expose "
                "RuntimeSchemaCertification"
            )

        if not inspect.isclass(
            certifier_class
        ):
            raise TypeError(
                "RuntimeSchemaCertification must be a class"
            )

        certifier = certifier_class()

        for method_name in (
            "certify",
            "last_report",
            "certification_fingerprint",
        ):
            if not callable(
                getattr(
                    certifier,
                    method_name,
                    None,
                )
            ):
                raise TypeError(
                    "RuntimeSchemaCertification is missing "
                    f"{method_name}()"
                )

        return certifier

    # -- fingerprints -------------------------------------------------------

    @staticmethod
    def _implementation_payload(
        resolutions: Mapping[str, dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "kind": FOUNDATION_STRUCTURE_KIND,
            "phase": FOUNDATION_PHASE,
            "contract": FOUNDATION_CERTIFICATION_CONTRACT_VERSION,
            "components": {
                spec.role: {
                    "index": spec.index_label,
                    "name": spec.name,
                    "resolved": resolutions[spec.role]["module"] is not None,
                    "public_api": list(resolutions[spec.role]["public_api"]),
                }
                for spec in FOUNDATION_COMPONENTS
            },
        }

    def _implementation_fingerprint(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> str:
        return _fingerprint(self._implementation_payload(resolutions))

    @staticmethod
    def _matrix_fingerprint(
        sections: tuple[CertificationSection, ...]
    ) -> str:
        payload = {
            "kind": FOUNDATION_STRUCTURE_KIND + ".matrix",
            "sections": [
                {
                    "name": section.name,
                    "checks": [
                        check.identity_dict() for check in section.checks
                    ],
                }
                for section in sections
            ],
        }
        return _fingerprint(payload)

    # -- report assembly ----------------------------------------------------

    def _assemble_report(
        self,
        resolutions: Mapping[str, dict[str, Any]],
        sections: tuple[CertificationSection, ...],
    ) -> RuntimeFoundationCertificationReport:
        total = sum(len(section.checks) for section in sections)
        passed = sum(section.passed_count for section in sections)
        failed = sum(section.failed_count for section in sections)
        failure_codes = tuple(
            check.check_id
            for section in sections
            for check in section.checks
            if not check.passed
        )
        complete = bool(sections) and all(
            section.checks for section in sections
        )
        implementation_fp = self._implementation_fingerprint(resolutions)
        matrix_fp = self._matrix_fingerprint(sections)
        certification_fp = _fingerprint(
            {
                "kind": FOUNDATION_STRUCTURE_KIND + ".evidence",
                "phase": FOUNDATION_PHASE,
                "contract": FOUNDATION_CERTIFICATION_CONTRACT_VERSION,
                "implementation": implementation_fp,
                "matrix": matrix_fp,
            }
        )
        certified = complete and failed == 0
        status = (
            CertificationStatus.PASS
            if certified
            else CertificationStatus.FAIL
        )
        certification_id = "rfc-cert-" + _fingerprint(
            {
                "phase": FOUNDATION_PHASE,
                "contract": FOUNDATION_CERTIFICATION_CONTRACT_VERSION,
                "certification": certification_fp,
            }
        )[:24]
        section_summaries = tuple(
            section.summary_dict() for section in sections
        )
        generated_at = _utc_now()

        core = {
            "certification_id": certification_id,
            "phase": FOUNDATION_PHASE,
            "subsystem": FOUNDATION_SUBSYSTEM,
            "certification_contract_version": (
                FOUNDATION_CERTIFICATION_CONTRACT_VERSION
            ),
            "implementation_fingerprint": implementation_fp,
            "certification_fingerprint": certification_fp,
            "matrix_fingerprint": matrix_fp,
            "certified": certified,
            "complete": complete,
            "status": status.value,
            "passed_checks": passed,
            "failed_checks": failed,
            "total_checks": total,
            "section_summaries": [dict(s) for s in section_summaries],
            "sections": [s.to_canonical_dict() for s in sections],
            "failure_codes": list(failure_codes),
            "generated_at": generated_at,
        }
        report_fp = _fingerprint(core)

        return RuntimeFoundationCertificationReport(
            certification_id=certification_id,
            phase=FOUNDATION_PHASE,
            subsystem=FOUNDATION_SUBSYSTEM,
            certification_contract_version=(
                FOUNDATION_CERTIFICATION_CONTRACT_VERSION
            ),
            implementation_fingerprint=implementation_fp,
            certification_fingerprint=certification_fp,
            matrix_fingerprint=matrix_fp,
            certified=certified,
            complete=complete,
            status=status,
            passed_checks=passed,
            failed_checks=failed,
            total_checks=total,
            section_summaries=section_summaries,
            sections=sections,
            failure_codes=failure_codes,
            generated_at=generated_at,
            report_fingerprint=report_fp,
        )

    # -- matrix runner ------------------------------------------------------

    @staticmethod
    def _check(
        section: str,
        check_id: str,
        name: str,
        requirement: str,
        thunk: Callable[[], Any],
    ) -> CertificationCheck:
        """Execute *thunk* fail-closed and record the outcome."""
        try:
            detail = thunk()
            status = CertificationStatus.PASS
            detail_text = str(detail) if detail else "ok"
        except Exception as exc:  # fail-closed: any raise is a failure
            status = CertificationStatus.FAIL
            detail_text = f"{type(exc).__name__}: {exc}"
        return CertificationCheck(
            check_id, section, name, requirement, status, detail_text
        )

    def _run_matrix(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> tuple[CertificationSection, ...]:
        builders = (
            ("COMPONENT_PRESENCE", self._component_presence_checks),
            ("INTERFACE_INTEGRITY", self._interface_integrity_checks),
            ("DEPENDENCY_CONSISTENCY", self._dependency_consistency_checks),
            ("RUNTIME_BOUNDARIES", self._runtime_boundary_checks),
            ("LIFECYCLE_INTEGRITY", self._lifecycle_checks),
            ("BOOT_SHUTDOWN_COMPOSITION", self._boot_shutdown_checks),
            ("CROSS_COMPONENT_CONTRACTS", self._cross_component_checks),
            ("DETERMINISM", self._determinism_checks),
            ("FOUNDATION_COMPLETENESS", self._completeness_checks),
        )
        sections: list[CertificationSection] = []
        for name, builder in builders:
            try:
                checks = tuple(builder(resolutions))
            except Exception as exc:  # noqa: BLE001
                checks = (
                    CertificationCheck(
                        name.lower() + ".builder", name, "section builder",
                        "section must assemble", CertificationStatus.FAIL,
                        f"{type(exc).__name__}: {exc}",
                    ),
                )
            sections.append(CertificationSection.build(name, checks))
        return tuple(sections)

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _module_of(
        resolutions: Mapping[str, dict[str, Any]], role: str
    ) -> Any:
        entry = resolutions[role]
        if entry["module"] is None:
            raise AssertionError(
                f"component {role} unresolved: {entry['error']}"
            )
        return entry["module"]

    @staticmethod
    def _exports_class_or_callable(module: Any, api: tuple[str, ...]) -> bool:
        for attr_name in api:
            attr = getattr(module, attr_name, None)
            if inspect.isclass(attr) or callable(attr):
                return True
        return False

    @staticmethod
    def _forbidden_bindings(
        module: Any, categories: frozenset[str]
    ) -> list[str]:
        hits: list[str] = []
        for attr_name, attr in vars(module).items():
            if inspect.ismodule(attr):
                root = getattr(attr, "__name__", "").split(".")[0]
                if root in categories:
                    hits.append(f"{attr_name}->{root}")
        return hits

    # -- COMPONENT PRESENCE -------------------------------------------------

    def _component_presence_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "COMPONENT_PRESENCE"
        out: list[CertificationCheck] = []
        for spec in FOUNDATION_COMPONENTS:
            role = spec.role

            def thunk(role: str = role, spec: _ComponentSpec = spec) -> str:
                self._module_of(resolutions, role)
                api = resolutions[role]["public_api"]
                _expect(bool(api), f"{role} exposes no public API")
                return (
                    f"{spec.index_label} {spec.name} resolved "
                    f"({len(api)} public names)"
                )

            out.append(
                self._check(
                    s, f"presence.{role}", spec.name,
                    f"{spec.index_label} present and importable", thunk
                )
            )
        return out

    # -- INTERFACE INTEGRITY ------------------------------------------------

    def _interface_integrity_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "INTERFACE_INTEGRITY"
        out: list[CertificationCheck] = []

        def resolve_names() -> str:
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                for attr_name in resolutions[spec.role]["public_api"]:
                    _expect(
                        hasattr(module, attr_name),
                        f"{spec.role}.{attr_name} declared but missing",
                    )
            return "all declared public names resolve as attributes"

        out.append(self._check(s, "interface.resolve",
                               "public names resolve",
                               "declared API resolves", resolve_names))

        def exports_surface() -> str:
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                api = resolutions[spec.role]["public_api"]
                _expect(
                    self._exports_class_or_callable(module, api),
                    f"{spec.role} exports no class or callable",
                )
            return "every component exports a class or callable"

        out.append(self._check(s, "interface.surface",
                               "callable/class surface",
                               "components expose usable interface",
                               exports_surface))

        def no_private() -> str:
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                declared = getattr(module, "__all__", None)
                if isinstance(declared, (list, tuple)):
                    for attr_name in declared:
                        _expect(
                            isinstance(attr_name, str)
                            and not attr_name.startswith("_"),
                            f"{spec.role} leaks private name {attr_name!r}",
                        )
            return "no private or dunder names in declared public API"

        out.append(self._check(s, "interface.no_private",
                               "public API hygiene",
                               "no private names exported", no_private))
        return out

    # -- DEPENDENCY CONSISTENCY ---------------------------------------------

    def _dependency_consistency_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "DEPENDENCY_CONSISTENCY"
        out: list[CertificationCheck] = []

        def all_resolved() -> str:
            unresolved = [
                spec.role
                for spec in FOUNDATION_COMPONENTS
                if resolutions[spec.role]["module"] is None
            ]
            _expect(not unresolved, f"unresolved: {', '.join(unresolved)}")
            return "every declared dependency resolves"

        out.append(self._check(s, "dependency.resolved",
                               "dependency graph resolves",
                               "all components import", all_resolved))

        def idempotent() -> str:
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                reimported, _ = self._import_module(spec.candidates)
                _expect(
                    reimported is module,
                    f"{spec.role} re-import is not idempotent",
                )
            return "re-import is idempotent for every component"

        out.append(self._check(s, "dependency.idempotent",
                               "idempotent imports",
                               "imports are idempotent", idempotent))

        def unique_modules() -> str:
            identities = {
                id(self._module_of(resolutions, spec.role))
                for spec in FOUNDATION_COMPONENTS
            }
            _expect(
                len(identities) == len(FOUNDATION_COMPONENTS),
                "distinct components collapsed to the same module",
            )
            return "each component is a distinct module"

        out.append(self._check(s, "dependency.unique",
                               "distinct component modules",
                               "components are distinct", unique_modules))
        return out

    # -- RUNTIME BOUNDARIES -------------------------------------------------

    def _runtime_boundary_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "RUNTIME_BOUNDARIES"
        out: list[CertificationCheck] = []

        def _scan(categories: frozenset[str]) -> list[str]:
            offenders: list[str] = []
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                for hit in self._forbidden_bindings(module, categories):
                    offenders.append(f"{spec.role}.{hit}")
            return offenders

        def no_network() -> str:
            offenders = _scan(_FORBIDDEN_NETWORK_MODULES)
            _expect(not offenders, "; ".join(offenders))
            return "no component binds a networking module"

        out.append(self._check(s, "boundary.network", "no networking",
                               "no network bindings", no_network))

        def no_database() -> str:
            offenders = _scan(_FORBIDDEN_DATABASE_MODULES)
            _expect(not offenders, "; ".join(offenders))
            return "no component binds a database driver"

        out.append(self._check(s, "boundary.database", "no database",
                               "no database bindings", no_database))

        def no_process() -> str:
            offenders = _scan(_FORBIDDEN_PROCESS_MODULES)
            _expect(not offenders, "; ".join(offenders))
            return "no component spawns external processes"

        out.append(self._check(s, "boundary.process",
                               "no external processes",
                               "no process bindings", no_process))

        def no_boot_sentinel() -> str:
            for spec in FOUNDATION_COMPONENTS:
                module = self._module_of(resolutions, spec.role)
                for sentinel in _BOOT_SENTINELS:
                    _expect(
                        not bool(getattr(module, sentinel, False)),
                        f"{spec.role} set boot sentinel {sentinel}",
                    )
            return "no application boot occurred at import time"

        out.append(self._check(s, "boundary.no_boot",
                               "no application boot",
                               "no import-time boot", no_boot_sentinel))

        def certifier_pure() -> str:
            forbidden = (
                _FORBIDDEN_NETWORK_MODULES
                | _FORBIDDEN_DATABASE_MODULES
                | _FORBIDDEN_PROCESS_MODULES
                | frozenset({"shutil", "tempfile"})
            )
            this_module = sys.modules[__name__]
            hits = self._forbidden_bindings(this_module, forbidden)
            _expect(not hits, "; ".join(hits))
            return "certification module binds no I/O, DB or process modules"

        out.append(self._check(s, "boundary.certifier_pure",
                               "certifier purity",
                               "certifier performs no I/O", certifier_pure))
        return out

    # -- LIFECYCLE INTEGRITY ------------------------------------------------

    def _lifecycle_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "LIFECYCLE_INTEGRITY"
        out: list[CertificationCheck] = []

        def lifecycle_surface() -> str:
            module = self._module_of(resolutions, ROLE_LIFECYCLE)
            api = resolutions[ROLE_LIFECYCLE]["public_api"]
            classes = [
                name for name in api
                if inspect.isclass(getattr(module, name, None))
            ]
            _expect(classes, "lifecycle manager exposes no class")
            return f"lifecycle manager exposes {len(classes)} class(es)"

        out.append(self._check(s, "lifecycle.surface",
                               "lifecycle manager interface",
                               "lifecycle manager is a class contract",
                               lifecycle_surface))

        def supporting_present() -> str:
            for role in (ROLE_CONFIGURATION, ROLE_ENVIRONMENT,
                         ROLE_SERVICE_REGISTRY):
                self._module_of(resolutions, role)
            return "configuration, environment and service registry present"

        out.append(self._check(s, "lifecycle.support",
                               "lifecycle dependencies present",
                               "lifecycle supporting components present",
                               supporting_present))

        def versioning_contract() -> str:
            module = self._module_of(resolutions, ROLE_VERSIONING)
            api = resolutions[ROLE_VERSIONING]["public_api"]
            _expect(
                self._exports_class_or_callable(module, api),
                "versioning exposes no usable contract",
            )
            self._module_of(resolutions, ROLE_COMPATIBILITY)
            return "versioning and compatibility contracts present"

        out.append(self._check(s, "lifecycle.versioning",
                               "version and compatibility contracts",
                               "version/compatibility present",
                               versioning_contract))
        return out

    # -- BOOT / SHUTDOWN COMPOSITION ----------------------------------------

    def _boot_shutdown_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "BOOT_SHUTDOWN_COMPOSITION"
        out: list[CertificationCheck] = []

        def boot_surface() -> str:
            module = self._module_of(resolutions, ROLE_BOOT)
            api = resolutions[ROLE_BOOT]["public_api"]
            _expect(
                self._exports_class_or_callable(module, api),
                "boot process exposes no coordinator",
            )
            return "boot process exposes a coordinator contract"

        out.append(self._check(s, "composition.boot", "boot coordinator",
                               "boot process interface present", boot_surface))

        def shutdown_surface() -> str:
            module = self._module_of(resolutions, ROLE_SHUTDOWN)
            api = resolutions[ROLE_SHUTDOWN]["public_api"]
            _expect(
                self._exports_class_or_callable(module, api),
                "shutdown process exposes no coordinator",
            )
            return "shutdown process exposes a coordinator contract"

        out.append(self._check(s, "composition.shutdown",
                               "shutdown coordinator",
                               "shutdown process interface present",
                               shutdown_surface))

        def inverse_pair() -> str:
            boot = self._module_of(resolutions, ROLE_BOOT)
            shutdown = self._module_of(resolutions, ROLE_SHUTDOWN)
            _expect(boot is not shutdown, "boot and shutdown are one module")
            self._module_of(resolutions, ROLE_KERNEL)
            return "boot and shutdown compose around the kernel root"

        out.append(self._check(s, "composition.inverse",
                               "boot/shutdown pairing",
                               "boot and shutdown are distinct phases",
                               inverse_pair))
        return out

    # -- CROSS-COMPONENT CONTRACTS ------------------------------------------

    def _cross_component_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "CROSS_COMPONENT_CONTRACTS"
        out: list[CertificationCheck] = []

        def negotiation_stack() -> str:
            for role in (ROLE_FEATURE_FLAGS, ROLE_CAPABILITY,
                         ROLE_COMPATIBILITY):
                module = self._module_of(resolutions, role)
                api = resolutions[role]["public_api"]
                _expect(
                    self._exports_class_or_callable(module, api),
                    f"{role} exposes no contract",
                )
            return "feature-flag, capability and compatibility stack present"

        out.append(self._check(s, "cross.negotiation",
                               "negotiation stack",
                               "negotiation contracts present",
                               negotiation_stack))

        def persistence_stack() -> str:
            for role in (ROLE_PERSISTENCE, ROLE_STATE_STORE):
                module = self._module_of(resolutions, role)
                api = resolutions[role]["public_api"]
                _expect(
                    self._exports_class_or_callable(module, api),
                    f"{role} exposes no contract",
                )
            return "persistence and state-store abstractions present"

        out.append(self._check(s, "cross.persistence",
                               "persistence stack",
                               "persistence contracts present",
                               persistence_stack))

        def schema_self_certifies() -> str:
            certifier = self._resolve_schema_certifier()
            report = certifier.certify()
            _expect(
                bool(report.get("certified")),
                "schema subsystem failed its own certification: "
                + ",".join(report.get("failure_codes", []) or ["unknown"]),
            )
            fingerprint = certifier.certification_fingerprint()
            _expect(
                isinstance(fingerprint, str) and len(fingerprint) == 64,
                "schema certification fingerprint invalid",
            )
            return "schema subsystem self-certifies in isolation"

        out.append(self._check(s, "cross.schema_certifies",
                               "schema subsystem self-certification",
                               "schema subsystem certifies",
                               schema_self_certifies))
        return out

    # -- DETERMINISM --------------------------------------------------------

    def _determinism_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "DETERMINISM"
        out: list[CertificationCheck] = []

        def canonical_order() -> str:
            a = {"b": 2, "a": [3, {"y": 1, "x": 0}], "c": True}
            b = {"c": True, "a": [3, {"x": 0, "y": 1}], "b": 2}
            _expect(_canonical_json(a) == _canonical_json(b), "order-sensitive")
            return "canonical serialisation is order-independent"

        out.append(self._check(s, "determinism.canonical",
                               "canonical determinism",
                               "serialisation deterministic",
                               canonical_order))

        def implementation_stable() -> str:
            first = self._implementation_fingerprint(resolutions)
            second = self._implementation_fingerprint(resolutions)
            _expect(first == second, "implementation fingerprint drifted")
            _expect(len(first) == 64, "fingerprint length")
            return "implementation fingerprint is deterministic"

        out.append(self._check(s, "determinism.implementation",
                               "implementation fingerprint stability",
                               "implementation evidence stable",
                               implementation_stable))

        def timestamp_independence() -> str:
            payload = self._implementation_payload(resolutions)
            _expect(
                "generated_at" not in _canonical_json(payload),
                "implementation evidence bound a timestamp",
            )
            return "implementation evidence carries no timestamp"

        out.append(self._check(s, "determinism.timestamp",
                               "timestamp independence",
                               "evidence excludes timestamps",
                               timestamp_independence))
        return out

    # -- FOUNDATION COMPLETENESS --------------------------------------------

    def _completeness_checks(
        self, resolutions: Mapping[str, dict[str, Any]]
    ) -> list[CertificationCheck]:
        s = "FOUNDATION_COMPLETENESS"
        out: list[CertificationCheck] = []

        def count() -> str:
            _expect(
                len(FOUNDATION_COMPONENTS) == 14,
                "component roster is not 14 entries",
            )
            resolved = sum(
                1
                for spec in FOUNDATION_COMPONENTS
                if resolutions[spec.role]["module"] is not None
            )
            _expect(resolved == 14, f"only {resolved}/14 components resolved")
            return "all 14 foundation components resolved"

        out.append(self._check(s, "completeness.count",
                               "component count",
                               "all 14 components present", count))

        def numbering() -> str:
            labels = [spec.index_label for spec in FOUNDATION_COMPONENTS]
            expected = [f"1.1.{n}" for n in range(1, 15)]
            _expect(labels == expected, "phase numbering has gaps")
            return "phase numbering 1.1.1-1.1.14 is contiguous"

        out.append(self._check(s, "completeness.numbering",
                               "contiguous numbering",
                               "no numbering gaps", numbering))

        def phase_label() -> str:
            _expect(FOUNDATION_PHASE == "1.1", "unexpected phase")
            _expect(
                FOUNDATION_CERTIFICATION_CONTRACT_VERSION == "1.0.0",
                "unexpected contract version",
            )
            return "phase and contract labels correct"

        out.append(self._check(s, "completeness.phase",
                               "phase identity",
                               "phase identity correct", phase_label))
        return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "FOUNDATION_CERTIFICATION_CONTRACT_VERSION",
    "FOUNDATION_PHASE",
    "FOUNDATION_SUBSYSTEM",
    "FOUNDATION_STRUCTURE_KIND",
    "FOUNDATION_COMPONENTS",
    "CertificationStatus",
    "CertificationCheck",
    "CertificationSection",
    "RuntimeFoundationCertificationReport",
    "RuntimeFoundationCertification",
]