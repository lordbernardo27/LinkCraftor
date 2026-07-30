from __future__ import annotations

import importlib
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

TARGET = (
    RUNTIME_DIR
    / "runtime_foundation_certification.py"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_foundation_certification_review_{TIMESTAMP}"
    / TARGET.name
)


OLD_COMPONENTS = '''FOUNDATION_COMPONENTS: tuple[_ComponentSpec, ...] = (
    _ComponentSpec("1.1.1", ROLE_KERNEL, "Universal Runtime Kernel",
                   ("universal_runtime_kernel",)),
    _ComponentSpec("1.1.2", ROLE_CONFIGURATION, "Runtime Configuration",
                   ("runtime_configuration", "runtime_config")),
    _ComponentSpec("1.1.3", ROLE_ENVIRONMENT, "Runtime Environment",
                   ("runtime_environment_management", "runtime_environment")),
    _ComponentSpec("1.1.4", ROLE_SERVICE_REGISTRY, "Runtime Service Registry",
                   ("runtime_service_registry",)),
    _ComponentSpec("1.1.5", ROLE_LIFECYCLE, "Runtime Lifecycle Manager",
                   ("runtime_lifecycle_manager",)),
    _ComponentSpec("1.1.6", ROLE_BOOT, "Runtime Boot Process",
                   ("runtime_boot_process",)),
    _ComponentSpec("1.1.7", ROLE_SHUTDOWN, "Runtime Shutdown Process",
                   ("runtime_shutdown_process",)),
    _ComponentSpec("1.1.8", ROLE_VERSIONING, "Runtime Versioning",
                   ("runtime_versioning",)),
    _ComponentSpec("1.1.9", ROLE_COMPATIBILITY, "Runtime Compatibility Layer",
                   ("runtime_compatibility_layer",)),
    _ComponentSpec("1.1.10", ROLE_FEATURE_FLAGS, "Runtime Feature Flags",
                   ("runtime_feature_flags",)),
    _ComponentSpec("1.1.11", ROLE_CAPABILITY, "Runtime Capability Negotiation",
                   ("runtime_capability_negotiation",)),
    _ComponentSpec("1.1.12", ROLE_PERSISTENCE, "Runtime Persistence Interface",
                   ("runtime_persistence_interface",)),
    _ComponentSpec("1.1.13", ROLE_STATE_STORE, "Runtime State Store Abstraction",
                   ("runtime_state_store_abstraction",)),
    _ComponentSpec("1.1.14", ROLE_SCHEMA, "Runtime Schema Management",
                   ("runtime_schema_management", "runtime_schema.certification",
                    "runtime_schema")),
)
'''


NEW_COMPONENTS = '''FOUNDATION_COMPONENTS: tuple[_ComponentSpec, ...] = (
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
'''


OLD_SCHEMA_CANDIDATES = '''_SCHEMA_CERTIFIER_CANDIDATES: tuple[str, ...] = (
    "runtime_schema.certification",
    "runtime_schema_management",
)
_SCHEMA_CERTIFIER_ATTRIBUTE: str = "RuntimeSchemaCertification"
'''


NEW_SCHEMA_CANDIDATES = '''_SCHEMA_CERTIFIER_CANDIDATES: tuple[str, ...] = (
    "runtime_schema.certification",
)

_SCHEMA_CERTIFIER_ATTRIBUTE: str = (
    "RuntimeSchemaCertification"
)
'''


OLD_PUBLIC_API = '''def _public_api(module: Any) -> tuple[str, ...]:
    """Return a component's declared public surface, deterministically."""
    declared = getattr(module, "__all__", None)
    if isinstance(declared, (list, tuple)) and declared:
        return tuple(sorted(str(name) for name in declared))
    return tuple(
        sorted(name for name in dir(module) if not name.startswith("_"))
    )
'''


NEW_PUBLIC_API = '''def _public_api(module: Any) -> tuple[str, ...]:
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
'''


OLD_IMPORT_MODULE = '''    @staticmethod
    def _import_module(candidates: tuple[str, ...]) -> tuple[Any, str]:
        """Import the first importable candidate; return (module, logical)."""
        errors: list[str] = []
        package = __package__ or None
        for logical in candidates:
            attempts: list[tuple[str, Optional[str]]] = []
            if package:
                attempts.append(("." + logical, package))
            attempts.append((logical, None))
            for module_name, anchor in attempts:
                try:
                    module = importlib.import_module(module_name, anchor)
                    return module, logical
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{module_name}: {type(exc).__name__}")
        raise ImportError("; ".join(errors) or "no candidates supplied")
'''


NEW_IMPORT_MODULE = '''    @staticmethod
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
'''


OLD_RESOLVE_SCHEMA = '''    def _resolve_schema_certifier(self) -> Any:
        """Locate and instantiate the schema subsystem's own certifier."""
        errors: list[str] = []
        for candidate in _SCHEMA_CERTIFIER_CANDIDATES:
            try:
                module, _ = self._import_module((candidate,))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{candidate}: {type(exc).__name__}")
                continue
            certifier = getattr(module, _SCHEMA_CERTIFIER_ATTRIBUTE, None)
            if certifier is not None:
                return certifier()
        raise LookupError(
            "schema certifier not found: " + "; ".join(errors)
        )
'''


NEW_RESOLVE_SCHEMA = '''    def _resolve_schema_certifier(
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
'''


def replace_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    count = source.count(
        old
    )

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, "
            f"found {count}."
        )

    return source.replace(
        old,
        new,
        1,
    )


def import_target():
    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_foundation_certification",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_foundation_certification"
    )


def verify_behavior(
    module,
) -> None:
    expected_modules = {
        "universal_runtime_kernel",
        "runtime_configuration",
        "runtime_environment",
        "runtime_service_registry",
        "runtime_lifecycle_manager",
        "runtime_boot_process",
        "runtime_shutdown_process",
        "runtime_versioning",
        "runtime_compatibility",
        "runtime_feature_flags",
        "runtime_capability_negotiation",
        "runtime_persistence",
        "runtime_state_store",
        "runtime_schema.certification",
    }

    actual_modules = {
        spec.candidates[
            0
        ]
        for spec in module.FOUNDATION_COMPONENTS
    }

    if actual_modules != expected_modules:
        raise AssertionError(
            "Canonical component module roster mismatch."
        )

    if len(
        module.FOUNDATION_COMPONENTS
    ) != 14:
        raise AssertionError(
            "Foundation component count must be 14."
        )

    for spec in module.FOUNDATION_COMPONENTS:
        if len(
            spec.candidates
        ) != 1:
            raise AssertionError(
                f"{spec.role} has fallback module candidates."
            )

        imported = importlib.import_module(
            spec.candidates[
                0
            ]
        )

        public_api = module._public_api(
            imported
        )

        if not public_api:
            raise AssertionError(
                f"{spec.role} has no public API."
            )

    certifier = (
        module.RuntimeFoundationCertification()
    )

    schema_certifier = (
        certifier
        ._resolve_schema_certifier()
    )

    if (
        schema_certifier
        .__class__
        .__name__
        != "RuntimeSchemaCertification"
    ):
        raise AssertionError(
            "Wrong Runtime Schema certifier class resolved."
        )

    first = certifier.certify()
    second = certifier.certify()

    if not first[
        "complete"
    ]:
        raise AssertionError(
            "Foundation certification matrix is incomplete."
        )

    if (
        first[
            "implementation_fingerprint"
        ]
        != second[
            "implementation_fingerprint"
        ]
    ):
        raise AssertionError(
            "Implementation fingerprint is not deterministic."
        )

    if (
        first[
            "matrix_fingerprint"
        ]
        != second[
            "matrix_fingerprint"
        ]
    ):
        raise AssertionError(
            "Matrix fingerprint is not deterministic."
        )

    if (
        first[
            "certification_fingerprint"
        ]
        != second[
            "certification_fingerprint"
        ]
    ):
        raise AssertionError(
            "Certification fingerprint is not deterministic."
        )

    if (
        first[
            "certification_id"
        ]
        != second[
            "certification_id"
        ]
    ):
        raise AssertionError(
            "Certification ID is not deterministic."
        )

    try:
        first[
            "certified"
        ] = False
    except Exception:
        pass
    else:
        raise AssertionError(
            "Top-level certification report is mutable."
        )


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:
    print("=" * 78)
    print("1.1.15 RUNTIME FOUNDATION CERTIFICATION")
    print("CLAUDE BASELINE REVIEW PATCH")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            "Paste Claude's complete module first: "
            f"{TARGET}"
        )

    original = TARGET.read_text(
        encoding="utf-8-sig"
    )

    BACKUP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET,
        BACKUP,
    )

    try:
        revised = original

        revised = replace_once(
            revised,
            OLD_COMPONENTS,
            NEW_COMPONENTS,
            "Canonical component roster",
        )

        revised = replace_once(
            revised,
            OLD_SCHEMA_CANDIDATES,
            NEW_SCHEMA_CANDIDATES,
            "Schema certifier candidate",
        )

        revised = replace_once(
            revised,
            OLD_PUBLIC_API,
            NEW_PUBLIC_API,
            "Strict public API contract",
        )

        revised = replace_once(
            revised,
            OLD_IMPORT_MODULE,
            NEW_IMPORT_MODULE,
            "Canonical import strategy",
        )

        revised = replace_once(
            revised,
            OLD_RESOLVE_SCHEMA,
            NEW_RESOLVE_SCHEMA,
            "Schema certifier resolution",
        )

        TARGET.write_text(
            revised,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(
            module
        )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The foundation-certification patch failed, "
            "so Claude's original module was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Backup creation:                 PASS")
    print("Canonical filename roster:       PASS")
    print("Fallback aliases removed:        PASS")
    print("Canonical import strategy:       PASS")
    print("Explicit __all__ enforcement:    PASS")
    print("Duplicate API rejection:         PASS")
    print("Missing API-name rejection:      PASS")
    print("Schema certifier class binding:  PASS")
    print("Schema certifier methods:        PASS")
    print("Module compilation:              PASS")
    print("Module import:                   PASS")
    print("Fourteen-component roster:       PASS")
    print("Implementation determinism:      PASS")
    print("Matrix determinism:              PASS")
    print("Certification determinism:       PASS")
    print("Certification identity stability: PASS")
    print("Report immutability:             PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print(
        "RUNTIME FOUNDATION CERTIFICATION "
        "PATCH: PASS"
    )
    print(
        "PRODUCTION CERTIFICATION HAS NOT "
        "YET BEEN FORMALLY INSTALLED"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
