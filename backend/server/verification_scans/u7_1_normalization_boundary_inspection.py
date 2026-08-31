from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

FILES = [
    ROOT / "backend/server/pipelines/upload_document/coordinator.py",
    ROOT / "backend/server/pipelines/upload_document/uploaded_document_to_uduc_pipeline/upload_intake.py",
    ROOT / "backend/server/stores/uploaded_document_unified_content.py",
    ROOT / "backend/server/utils/text_normalization.py",
]


def read(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )


print("=== U7.1 NORMALIZATION BOUNDARY INSPECTION ===")

for path in FILES:
    print()
    print(f"=== {path.relative_to(ROOT)} ===")

    if not path.exists():
        print("STATUS: MISSING")
        continue

    source = read(path)

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )
    except SyntaxError as exc:
        print(
            "PARSE_ERROR:",
            f"{type(exc).__name__}: {exc}",
        )
        continue

    print("TOP_LEVEL_FUNCTIONS:")

    functions = [
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    if functions:
        for name in functions:
            print(f"  {name}")
    else:
        print("  NONE")

    print("NORMALIZATION_RELATED_LINES:")

    hits = []

    for lineno, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        lower = line.lower()

        if any(
            token in lower
            for token in (
                "normalize",
                "normalise",
                "strip(",
                ".strip()",
                "replace(",
                "splitlines",
                "join(",
                "extraction_result.text",
                "extraction_result.title",
                "extraction_result.headings",
                'getattr(extraction_result, "text"',
                'getattr(extraction_result, "title"',
                'getattr(extraction_result, "headings"',
            )
        ):
            hits.append(
                (
                    lineno,
                    line.rstrip(),
                )
            )

    if hits:
        for lineno, line in hits:
            print(
                f"  L{lineno}: {line}"
            )
    else:
        print("  NONE")

    print("IMPORTS:")

    imports = [
        ast.unparse(node)
        for node in tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    for statement in imports:
        if (
            "normal" in statement.lower()
            or "clean" in statement.lower()
            or "upload" in statement.lower()
            or "uduc" in statement.lower()
        ):
            print(f"  {statement}")


print()
print(
    "U7.1_NORMALIZATION_BOUNDARY_INSPECTION_COMPLETE: YES"
)
print("NO_PRODUCTION_FILES_MODIFIED: YES")