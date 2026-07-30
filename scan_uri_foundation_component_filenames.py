from __future__ import annotations

import ast
import hashlib
import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

EVIDENCE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_15_runtime_foundation_certification"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

REPORT_JSON = (
    EVIDENCE_DIR
    / f"foundation_missing_filename_discovery_{TIMESTAMP}.json"
)

REPORT_TEXT = (
    EVIDENCE_DIR
    / f"foundation_missing_filename_discovery_{TIMESTAMP}.txt"
)


SEARCH_COMPONENTS = {
    "1.1.1 Universal Runtime Kernel": {
        "filename_terms": (
            "kernel",
            "runtime_core",
            "runtime_foundation",
        ),
        "symbol_terms": (
            "RuntimeKernel",
            "UniversalRuntimeKernel",
            "KernelState",
            "KernelSnapshot",
        ),
    },
    "1.1.5 Runtime Lifecycle Manager": {
        "filename_terms": (
            "lifecycle",
            "life_cycle",
        ),
        "symbol_terms": (
            "RuntimeLifecycle",
            "RuntimeLifecycleManager",
            "LifecycleState",
            "LifecycleSnapshot",
        ),
    },
    "1.1.6 Runtime Boot Process": {
        "filename_terms": (
            "boot",
            "startup",
            "start_up",
        ),
        "symbol_terms": (
            "RuntimeBoot",
            "RuntimeBootProcess",
            "BootPlan",
            "BootReport",
            "boot_runtime",
        ),
    },
    "1.1.7 Runtime Shutdown Process": {
        "filename_terms": (
            "shutdown",
            "shut_down",
            "termination",
        ),
        "symbol_terms": (
            "RuntimeShutdown",
            "RuntimeShutdownProcess",
            "ShutdownPlan",
            "ShutdownReport",
            "shutdown_runtime",
        ),
    },
}


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def scan_python_file(
    path: Path,
) -> dict:
    relative = path.relative_to(
        RUNTIME_DIR
    ).as_posix()

    result = {
        "relative_path": relative,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "compile": "NOT_RUN",
        "ast_parse": "NOT_RUN",
        "classes": [],
        "functions": [],
        "constants": [],
        "imports": [],
        "error": None,
    }

    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )

        result["compile"] = "PASS"

    except Exception as exc:
        result["compile"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        return result

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )

        tree = ast.parse(
            source
        )

        result["ast_parse"] = "PASS"

    except Exception as exc:
        result["ast_parse"] = "FAIL"
        result["error"] = (
            f"{type(exc).__name__}: {exc}"
        )

        return result

    result["classes"] = sorted(
        node.name
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
    )

    result["functions"] = sorted(
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    )

    constants = []

    for node in tree.body:
        if isinstance(
            node,
            ast.Assign,
        ):
            for target in node.targets:
                if (
                    isinstance(
                        target,
                        ast.Name,
                    )
                    and target.id.isupper()
                ):
                    constants.append(
                        target.id
                    )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if (
                isinstance(
                    node.target,
                    ast.Name,
                )
                and node.target.id.isupper()
            ):
                constants.append(
                    node.target.id
                )

    result["constants"] = sorted(
        constants
    )

    imports = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.append(
                    node.module
                )

    result["imports"] = sorted(
        set(imports)
    )

    return result


def score_candidate(
    file_result: dict,
    filename_terms: tuple[str, ...],
    symbol_terms: tuple[str, ...],
) -> dict:
    relative_lower = (
        file_result[
            "relative_path"
        ].lower()
    )

    filename_hits = [
        term
        for term in filename_terms
        if term in relative_lower
    ]

    symbols = (
        file_result["classes"]
        + file_result["functions"]
        + file_result["constants"]
    )

    symbol_hits = [
        symbol
        for symbol in symbols
        if any(
            term.lower()
            in symbol.lower()
            for term
            in symbol_terms
        )
    ]

    score = (
        len(filename_hits) * 10
        + len(symbol_hits) * 5
    )

    return {
        **file_result,
        "filename_hits": filename_hits,
        "symbol_hits": symbol_hits,
        "score": score,
    }


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("FOUNDATION COMPONENT FILENAME AND SYMBOL DISCOVERY")
    print("=" * 78)
    print(f"Runtime directory: {RUNTIME_DIR}")
    print()

    if not RUNTIME_DIR.exists():
        raise FileNotFoundError(
            f"Runtime directory does not exist: {RUNTIME_DIR}"
        )

    python_files = sorted(
        path
        for path in RUNTIME_DIR.rglob(
            "*.py"
        )
        if "__pycache__"
        not in path.parts
    )

    scanned_files = [
        scan_python_file(
            path
        )
        for path in python_files
    ]

    component_results = {}

    for component_name, rules in SEARCH_COMPONENTS.items():
        candidates = [
            score_candidate(
                file_result,
                rules[
                    "filename_terms"
                ],
                rules[
                    "symbol_terms"
                ],
            )
            for file_result
            in scanned_files
        ]

        candidates = sorted(
            (
                candidate
                for candidate in candidates
                if candidate[
                    "score"
                ] > 0
            ),
            key=lambda candidate: (
                -candidate[
                    "score"
                ],
                candidate[
                    "relative_path"
                ],
            ),
        )

        component_results[
            component_name
        ] = candidates

    report = {
        "scan": (
            "URI Phase 1 Foundation "
            "Filename and Symbol Discovery"
        ),
        "generated_at": TIMESTAMP,
        "runtime_directory": str(
            RUNTIME_DIR
        ),
        "python_file_count": len(
            python_files
        ),
        "components": (
            component_results
        ),
    }

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    lines = [
        "=" * 78,
        "URI FOUNDATION COMPONENT FILENAME AND SYMBOL DISCOVERY",
        "=" * 78,
        "",
        f"Runtime Python files scanned: {len(python_files)}",
        "",
    ]

    for component_name, candidates in component_results.items():
        print(component_name)
        print("-" * 78)

        lines.append(
            component_name
        )

        if not candidates:
            print("NO CANDIDATES FOUND")
            lines.append(
                "  NO CANDIDATES FOUND"
            )

        else:
            for candidate in candidates[
                :10
            ]:
                print(
                    f"Score {candidate['score']:>3} | "
                    f"{candidate['relative_path']}"
                )

                print(
                    "      filename hits: "
                    + (
                        ", ".join(
                            candidate[
                                "filename_hits"
                            ]
                        )
                        or "none"
                    )
                )

                print(
                    "      symbol hits:   "
                    + (
                        ", ".join(
                            candidate[
                                "symbol_hits"
                            ]
                        )
                        or "none"
                    )
                )

                print(
                    "      compile:       "
                    + candidate[
                        "compile"
                    ]
                )

                lines.extend(
                    [
                        (
                            f"  Score {candidate['score']:>3} | "
                            f"{candidate['relative_path']}"
                        ),
                        (
                            "      filename hits: "
                            + (
                                ", ".join(
                                    candidate[
                                        "filename_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      symbol hits: "
                            + (
                                ", ".join(
                                    candidate[
                                        "symbol_hits"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      classes: "
                            + (
                                ", ".join(
                                    candidate[
                                        "classes"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      functions: "
                            + (
                                ", ".join(
                                    candidate[
                                        "functions"
                                    ]
                                )
                                or "none"
                            )
                        ),
                        (
                            "      compile: "
                            + candidate[
                                "compile"
                            ]
                        ),
                    ]
                )

        print()
        lines.append("")

    REPORT_TEXT.write_text(
        "\n".join(
            lines
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Evidence JSON: {REPORT_JSON}")
    print(f"Evidence text: {REPORT_TEXT}")
    print()
    print(
        "FOUNDATION FILENAME DISCOVERY: PASS"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
