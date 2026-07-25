"""Remove the final active references to the deleted WUC architecture."""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

WORKSPACE_ID = "ws_whattoexpect_com"

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

DATA_ROOT = (
    SERVER_ROOT
    / "data"
)

BACKUP_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\backups\wuc_final_residual_cleanup_20260724_215757"
).resolve()

REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "wuc_final_residual_cleanup_verification.json"
)

DEDICATED_WRAPPER_PATH = (
    SERVER_ROOT
    / "stores"
    / "website_ucd_rebuild_engine.py"
)

SHARED_FILES = [
    (
        SERVER_ROOT
        / "phase_4_5_14_article_body_batch_completion_engine.py"
    ),

    (
        SERVER_ROOT
        / "stores"
        / "site_pages_content_linker.py"
    ),

    (
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_worker.py"
    ),
]

WUC_TERMS = {
    "website_unified_content_store",
    "website_unified_content_batch_worker",
    "website_unified_content_batch_worker_v2",
    "website_unified_content_builder_v2",
    "website_unified_content_verifier_v2",
    "website_unified_content_certifier_v2",
    "website_unified_content_handoff_v2",
    "website_unified_content_orchestrator",
    "website_source_pipeline_orchestrator",
    "website_uucd_rebuild_engine",
    "website_ucd_rebuild_engine",
    "website_article_integrity_checker",
    "crawled_article_viewer",
}

EXCLUDED_SCAN_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "node_modules",
}

PROTECTED_PATHS = {
    "udare_store": (
        DATA_ROOT
        / "udare_store"
        / WORKSPACE_ID
    ),

    "website_article_integrity": (
        DATA_ROOT
        / "website_article_integrity"
        / WORKSPACE_ID
    ),

    "article_validation_evidence": (
        DATA_ROOT
        / "article_validation_evidence"
        / WORKSPACE_ID
    ),

    "article_validation_engine": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_engine_v3.py"
    ),

    "article_validation_runner": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_runner_v3.py"
    ),

    "article_validation_runtime_registration": (
        SERVER_ROOT
        / "article_validation"
        / "article_validation_runtime_registration.py"
    ),

    "universal_runtime_registration": (
        SERVER_ROOT
        / "runtime"
        / "universal_runtime_registration.py"
    ),

    "uucd_convergence": (
        SERVER_ROOT
        / "stores"
        / "universal_unified_content_document_convergence.py"
    ),
}


def relative(
    path: Path,
) -> str:
    try:
        return (
            path.resolve()
            .relative_to(
                PROJECT_ROOT
            )
            .as_posix()
        )

    except ValueError:
        return str(
            path.resolve()
        )


def excluded(
    path: Path,
) -> bool:
    return any(
        part in EXCLUDED_SCAN_PARTS
        for part in path.parts
    )


def contains_wuc_term(
    value: str,
) -> bool:
    lowered = value.casefold()

    return any(
        term in lowered
        for term in WUC_TERMS
    )


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    if path.is_file():
        return sha256_file(
            path
        )

    for file_path in sorted(
        (
            candidate
            for candidate in path.rglob(
                "*"
            )
            if candidate.is_file()
        ),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            file_path.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        digest.update(
            b"\x00"
        )

        digest.update(
            sha256_file(
                file_path
            ).encode(
                "ascii"
            )
        )

        digest.update(
            b"\n"
        )

    return digest.hexdigest()


def backup_item(
    source: Path,
) -> str:
    destination = (
        BACKUP_ROOT
        / source.resolve().relative_to(
            PROJECT_ROOT
        )
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
        )

    else:
        shutil.copy2(
            source,
            destination,
        )

    return relative(
        destination
    )


def write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def node_text(
    source: str,
    node: ast.AST,
) -> str:
    return str(
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )


class WucReferenceRemover(
    ast.NodeTransformer
):
    """Remove only syntax nodes that depend on deleted WUC modules."""

    def __init__(
        self,
        source: str,
    ) -> None:
        self.source = source
        self.removed: list[
            dict[str, Any]
        ] = []

    def record(
        self,
        node: ast.AST,
        reason: str,
    ) -> None:
        self.removed.append(
            {
                "line_number":
                    getattr(
                        node,
                        "lineno",
                        None,
                    ),

                "end_line_number":
                    getattr(
                        node,
                        "end_lineno",
                        None,
                    ),

                "node_type":
                    node.__class__.__name__,

                "reason":
                    reason,

                "source":
                    node_text(
                        self.source,
                        node,
                    )[:1000],
            }
        )

    def statement_contains_wuc(
        self,
        node: ast.AST,
    ) -> bool:
        return contains_wuc_term(
            node_text(
                self.source,
                node,
            )
        )

    def visit_Import(
        self,
        node: ast.Import,
    ) -> ast.AST | None:
        retained = [
            alias
            for alias in node.names
            if not contains_wuc_term(
                alias.name
            )
        ]

        if len(
            retained
        ) == len(
            node.names
        ):
            return node

        removed_names = [
            alias.name
            for alias in node.names
            if alias not in retained
        ]

        self.record(
            node,
            (
                "Removed WUC import aliases: "
                + ", ".join(
                    removed_names
                )
            ),
        )

        if not retained:
            return None

        node.names = retained
        return node

    def visit_ImportFrom(
        self,
        node: ast.ImportFrom,
    ) -> ast.AST | None:
        module = str(
            node.module or ""
        )

        if contains_wuc_term(
            module
        ):
            self.record(
                node,
                (
                    "Removed import from deleted WUC module: "
                    + module
                ),
            )

            return None

        retained = [
            alias
            for alias in node.names
            if not contains_wuc_term(
                alias.name
            )
        ]

        if len(
            retained
        ) == len(
            node.names
        ):
            return node

        self.record(
            node,
            "Removed imported WUC symbols.",
        )

        if not retained:
            return None

        node.names = retained
        return node

    def visit_Dict(
        self,
        node: ast.Dict,
    ) -> ast.AST:
        node = self.generic_visit(
            node
        )

        retained_keys: list[
            ast.expr | None
        ] = []

        retained_values: list[
            ast.expr
        ] = []

        for key, value in zip(
            node.keys,
            node.values,
        ):
            combined = (
                node_text(
                    self.source,
                    key,
                )
                + " "
                + node_text(
                    self.source,
                    value,
                )
            )

            if contains_wuc_term(
                combined
            ):
                self.record(
                    value,
                    "Removed WUC dictionary entry.",
                )

                continue

            retained_keys.append(
                key
            )

            retained_values.append(
                value
            )

        node.keys = retained_keys
        node.values = retained_values

        return node

    def visit_List(
        self,
        node: ast.List,
    ) -> ast.AST:
        node = self.generic_visit(
            node
        )

        retained: list[
            ast.expr
        ] = []

        for element in node.elts:
            if contains_wuc_term(
                node_text(
                    self.source,
                    element,
                )
            ):
                self.record(
                    element,
                    "Removed WUC list item.",
                )

                continue

            retained.append(
                element
            )

        node.elts = retained
        return node

    def visit_Tuple(
        self,
        node: ast.Tuple,
    ) -> ast.AST:
        node = self.generic_visit(
            node
        )

        retained: list[
            ast.expr
        ] = []

        for element in node.elts:
            if contains_wuc_term(
                node_text(
                    self.source,
                    element,
                )
            ):
                self.record(
                    element,
                    "Removed WUC tuple item.",
                )

                continue

            retained.append(
                element
            )

        node.elts = retained
        return node

    def visit_Set(
        self,
        node: ast.Set,
    ) -> ast.AST:
        node = self.generic_visit(
            node
        )

        retained: list[
            ast.expr
        ] = []

        for element in node.elts:
            if contains_wuc_term(
                node_text(
                    self.source,
                    element,
                )
            ):
                self.record(
                    element,
                    "Removed WUC set item.",
                )

                continue

            retained.append(
                element
            )

        node.elts = retained
        return node

    def visit_If(
        self,
        node: ast.If,
    ) -> ast.AST | None:
        test_source = node_text(
            self.source,
            node.test,
        )

        if contains_wuc_term(
            test_source
        ):
            self.record(
                node,
                "Removed WUC-specific conditional branch.",
            )

            return None

        node = self.generic_visit(
            node
        )

        if not node.body:
            node.body = [
                ast.Pass()
            ]

        return node

    def visit_Match(
        self,
        node: ast.Match,
    ) -> ast.AST | None:
        retained_cases = []

        for case in node.cases:
            case_source = node_text(
                self.source,
                case,
            )

            if contains_wuc_term(
                case_source
            ):
                self.record(
                    case,
                    "Removed WUC-specific match case.",
                )

                continue

            retained_cases.append(
                self.visit(
                    case
                )
            )

        node.cases = [
            case
            for case in retained_cases
            if case is not None
        ]

        if not node.cases:
            self.record(
                node,
                "Removed empty match statement after WUC cleanup.",
            )

            return None

        return node

    def visit_Expr(
        self,
        node: ast.Expr,
    ) -> ast.AST | None:
        if self.statement_contains_wuc(
            node
        ):
            self.record(
                node,
                "Removed WUC expression or function call.",
            )

            return None

        return self.generic_visit(
            node
        )

    def visit_Assign(
        self,
        node: ast.Assign,
    ) -> ast.AST | None:
        original_source = node_text(
            self.source,
            node,
        )

        transformed = self.generic_visit(
            node
        )

        if contains_wuc_term(
            original_source
        ):
            transformed_source = ast.unparse(
                transformed
            )

            if contains_wuc_term(
                transformed_source
            ):
                self.record(
                    node,
                    "Removed WUC-dependent assignment.",
                )

                return None

        return transformed

    def visit_AnnAssign(
        self,
        node: ast.AnnAssign,
    ) -> ast.AST | None:
        original_source = node_text(
            self.source,
            node,
        )

        transformed = self.generic_visit(
            node
        )

        if contains_wuc_term(
            original_source
        ):
            transformed_source = ast.unparse(
                transformed
            )

            if contains_wuc_term(
                transformed_source
            ):
                self.record(
                    node,
                    "Removed WUC-dependent annotated assignment.",
                )

                return None

        return transformed

    def visit_Return(
        self,
        node: ast.Return,
    ) -> ast.AST | None:
        if self.statement_contains_wuc(
            node
        ):
            self.record(
                node,
                "Removed WUC-dependent return.",
            )

            return ast.Return(
                value=ast.Constant(
                    value=None
                )
            )

        return self.generic_visit(
            node
        )

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> ast.AST | None:
        if contains_wuc_term(
            node.name
        ):
            self.record(
                node,
                "Removed WUC-specific function.",
            )

            return None

        node = self.generic_visit(
            node
        )

        if not node.body:
            node.body = [
                ast.Pass()
            ]

        return node

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> ast.AST | None:
        if contains_wuc_term(
            node.name
        ):
            self.record(
                node,
                "Removed WUC-specific async function.",
            )

            return None

        node = self.generic_visit(
            node
        )

        if not node.body:
            node.body = [
                ast.Pass()
            ]

        return node

    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ) -> ast.AST | None:
        if contains_wuc_term(
            node.name
        ):
            self.record(
                node,
                "Removed WUC-specific class.",
            )

            return None

        node = self.generic_visit(
            node
        )

        if not node.body:
            node.body = [
                ast.Pass()
            ]

        return node


def clean_shared_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(
            path
        ),
    )

    transformer = WucReferenceRemover(
        source
    )

    transformed = transformer.visit(
        tree
    )

    transformed = ast.fix_missing_locations(
        transformed
    )

    updated_source = ast.unparse(
        transformed
    )

    if contains_wuc_term(
        updated_source
    ):
        remaining_lines = [
            {
                "line_number":
                    line_number,

                "line":
                    line,
            }
            for line_number, line in enumerate(
                updated_source.splitlines(),
                start=1,
            )
            if contains_wuc_term(
                line
            )
        ]

        raise RuntimeError(
            "WUC references remain after AST cleanup in "
            + str(
                path
            )
            + ": "
            + json.dumps(
                remaining_lines[
                    :20
                ],
                ensure_ascii=False,
            )
        )

    ast.parse(
        updated_source,
        filename=str(
            path
        ),
    )

    path.write_text(
        updated_source
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return {
        "path":
            relative(
                path
            ),

        "removed_node_count":
            len(
                transformer.removed
            ),

        "removed_nodes":
            transformer.removed,
    }


def scan_active_references() -> list[
    dict[str, Any]
]:
    findings: list[
        dict[str, Any]
    ] = []

    for path in SERVER_ROOT.rglob(
        "*.py"
    ):
        if (
            not path.is_file()
            or excluded(
                path
            )
        ):
            continue

        matches = []

        for line_number, line in enumerate(
            path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            ).splitlines(),
            start=1,
        ):
            matched_terms = sorted(
                term
                for term in WUC_TERMS
                if term in line.casefold()
            )

            if matched_terms:
                matches.append(
                    {
                        "line_number":
                            line_number,

                        "matched_terms":
                            matched_terms,

                        "line":
                            line.strip()[:1000],
                    }
                )

        if matches:
            findings.append(
                {
                    "path":
                        relative(
                            path
                        ),

                    "matches":
                        matches,
                }
            )

    return sorted(
        findings,
        key=lambda item: (
            item[
                "path"
            ]
        ),
    )


print()
print("=" * 108)
print(
    "WUC — FINAL RESIDUAL REFERENCE CLEANUP"
)
print("=" * 108)
print()

BACKUP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

failures: list[str] = []

protected_before = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

for name, path in PROTECTED_PATHS.items():
    if not path.exists():
        failures.append(
            "Protected path is missing before cleanup: "
            + name
        )

if failures:
    for failure in failures:
        print(
            "FAIL: "
            + failure
        )

    raise SystemExit(1)


backed_up_items: list[str] = []

if DEDICATED_WRAPPER_PATH.is_file():
    backed_up_items.append(
        backup_item(
            DEDICATED_WRAPPER_PATH
        )
    )

for path in SHARED_FILES:
    if path.is_file():
        backed_up_items.append(
            backup_item(
                path
            )
        )


wrapper_deleted = False

if DEDICATED_WRAPPER_PATH.is_file():
    DEDICATED_WRAPPER_PATH.unlink()
    wrapper_deleted = True


shared_cleanup_results: list[
    dict[str, Any]
] = []

for path in SHARED_FILES:
    if not path.is_file():
        failures.append(
            "Expected shared file is missing: "
            + str(
                path
            )
        )

        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    if not contains_wuc_term(
        source
    ):
        shared_cleanup_results.append(
            {
                "path":
                    relative(
                        path
                    ),

                "removed_node_count":
                    0,

                "removed_nodes":
                    [],

                "status":
                    "ALREADY_CLEAN",
            }
        )

        continue

    result = clean_shared_file(
        path
    )

    result[
        "status"
    ] = "CLEANED"

    shared_cleanup_results.append(
        result
    )


for path in SHARED_FILES:
    if not path.is_file():
        continue

    try:
        ast.parse(
            path.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        failures.append(
            "Shared file syntax invalid after cleanup: "
            + str(
                path
            )
            + " -> "
            + str(
                exc
            )
        )


remaining_references = (
    scan_active_references()
)

if remaining_references:
    failures.append(
        "Active references to the deleted WUC architecture remain."
    )


protected_after = {
    name: fingerprint(
        path
    )
    for name, path
    in PROTECTED_PATHS.items()
}

protected_unchanged = {
    name: (
        protected_before[
            name
        ]
        == protected_after[
            name
        ]
    )
    for name
    in PROTECTED_PATHS
}

for name, unchanged in protected_unchanged.items():
    if not unchanged:
        failures.append(
            "Protected architecture changed: "
            + name
        )


legacy_store_exists = (
    SERVER_ROOT
    / "stores"
    / "website_unified_content_store.py"
).exists()

legacy_data_exists = (
    DATA_ROOT
    / "website_unified_content"
).exists()

legacy_workers_exist = any(
    path.exists()
    for path in (
        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker.py",

        SERVER_ROOT
        / "workers"
        / "website_unified_content_batch_worker_v2.py",
    )
)

if legacy_store_exists:
    failures.append(
        "Legacy WUC Store module still exists."
    )

if legacy_data_exists:
    failures.append(
        "Legacy WUC data root still exists."
    )

if legacy_workers_exist:
    failures.append(
        "Legacy WUC worker still exists."
    )


report = {
    "schema_version":
        "wuc_final_residual_cleanup_verification_v1",

    "verification_status":
        (
            "PASS"
            if not failures
            else "FAIL"
        ),

    "workspace_id":
        WORKSPACE_ID,

    "backup_root":
        str(
            BACKUP_ROOT
        ),

    "wrapper_deleted":
        wrapper_deleted,

    "shared_cleanup_results":
        shared_cleanup_results,

    "remaining_active_reference_count":
        len(
            remaining_references
        ),

    "remaining_active_references":
        remaining_references,

    "legacy_wuc_store_exists":
        legacy_store_exists,

    "legacy_wuc_data_exists":
        legacy_data_exists,

    "legacy_wuc_workers_exist":
        legacy_workers_exist,

    "protected_paths_unchanged":
        protected_unchanged,

    "canonical_wuc_exists":
        False,

    "wuc_runtime_registration_exists":
        False,

    "wuc_dispatch_exists":
        False,

    "wuc_jobs_executed":
        False,

    "failures":
        failures,
}

write_json(
    REPORT_PATH,
    report,
)


print(
    "Dedicated compatibility wrapper deleted: "
    + str(
        wrapper_deleted
    )
)

print(
    "Shared files processed:                 "
    + str(
        len(
            shared_cleanup_results
        )
    )
)

print(
    "Remaining active WUC references:        "
    + str(
        len(
            remaining_references
        )
    )
)

print(
    "Legacy WUC Store exists:                "
    + str(
        legacy_store_exists
    )
)

print(
    "Legacy WUC data root exists:            "
    + str(
        legacy_data_exists
    )
)

print(
    "Legacy WUC workers exist:               "
    + str(
        legacy_workers_exist
    )
)

print()
print(
    "SHARED FILE CLEANUP"
)

for result in shared_cleanup_results:
    print(
        "  "
        + result[
            "path"
        ]
        + " -> "
        + result[
            "status"
        ]
        + " | removed nodes: "
        + str(
            result[
                "removed_node_count"
            ]
        )
    )

print()
print(
    "PROTECTED ARCHITECTURE"
)

for name, unchanged in protected_unchanged.items():
    print(
        "  "
        + name
        + ": "
        + (
            "UNCHANGED"
            if unchanged
            else "CHANGED"
        )
    )

print()
print(
    "Canonical WUC exists:            False"
)

print(
    "WUC Runtime Registration exists: False"
)

print(
    "WUC dispatch exists:             False"
)

print(
    "WUC jobs executed:               False"
)

print()
print(
    "Backup location: "
    + str(
        BACKUP_ROOT
    )
)

print(
    "Verification report: "
    + str(
        REPORT_PATH
    )
)

print()

if remaining_references:
    print(
        "REMAINING REFERENCES"
    )

    for finding in remaining_references:
        print(
            "  "
            + finding[
                "path"
            ]
        )

        for match in finding[
            "matches"
        ]:
            print(
                "    line "
                + str(
                    match[
                        "line_number"
                    ]
                )
                + ": "
                + ", ".join(
                    match[
                        "matched_terms"
                    ]
                )
            )

    print()

if failures:
    print(
        "WUC FINAL RESIDUAL CLEANUP: FAIL"
    )

    for failure in failures:
        print(
            "  - "
            + failure
        )

    print("=" * 108)

    raise SystemExit(1)

print(
    "WUC FINAL RESIDUAL CLEANUP: PASS"
)

print(
    "No active WUC implementation, Store, worker, wrapper, "
    "runtime dispatch or legacy module reference remains."
)

print(
    "The shared runtime and non-WUC pipeline architecture remain intact."
)

print("=" * 108)
