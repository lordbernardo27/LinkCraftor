from pathlib import Path
import ast


targets = [
    Path(
        "backend/server/pipelines/upload_document/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/coordinator.py"
    ),
    Path(
        "backend/server/pipelines/upload_document/"
        "uploaded_document_to_uduc_pipeline/upload_intake.py"
    ),
    Path(
        "backend/server/stores/uploaded_document_unified_content.py"
    ),
    Path(
        "backend/server/stores/upload_document_normalizer.py"
    ),
]


print(
    "=== U8.3 CANONICAL UDUC INPUT CONTRACT CALL-SITE INSPECTION ==="
)


for path in targets:
    print()
    print(
        "============================================================"
    )
    print(
        f"FILE={path}"
    )
    print(
        "============================================================"
    )

    if not path.exists():
        print("FILE_NOT_FOUND")
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tree = ast.parse(source)

    print()
    print("=== IMPORTS ===")

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            code = ast.get_source_segment(
                source,
                node,
            )

            if any(
                term in (
                    code or ""
                )
                for term in (
                    "uploaded_document_unified_content",
                    "upload_document_normalizer",
                    "upload_document_extractor",
                )
            ):
                print(code)

    print()
    print("=== RELEVANT FUNCTION DEFINITIONS ===")

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        fn_source = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        if any(
            term in fn_source
            for term in (
                "build_and_write_uduc_from_extraction_result",
                "build_uduc_from_upload_extraction_result",
                "write_uduc",
                "normalize_uploaded_document_v1",
                "run_uploaded_document_to_uduc_pipeline",
                "run_upload_document",
                "run_upload_intake",
            )
        ):
            print()
            print(
                f"--- {node.name} ---"
            )
            print(fn_source)

    print()
    print("=== RELEVANT CALLS ===")

    hits = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        call = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        if any(
            term in call
            for term in (
                "build_and_write_uduc_from_extraction_result",
                "build_uduc_from_upload_extraction_result",
                "write_uduc",
                "normalize_uploaded_document_v1",
                "run_uploaded_document_to_uduc_pipeline",
                "run_upload_intake",
            )
        ):
            hits.append(
                (
                    getattr(
                        node,
                        "lineno",
                        None,
                    ),
                    call,
                )
            )

    for line, call in hits:
        print()
        print(
            f"LINE {line}"
        )
        print(call)

    print(
        "RELEVANT_CALL_COUNT=",
        len(hits),
    )


print()
print("=== U8.3 CURRENT CONTRACT SUMMARY ===")

coordinator_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_path = Path(
    "backend/server/stores/uploaded_document_unified_content.py"
)

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

print(
    "COORDINATOR_CALLS_EXTRACTION_RESULT_BUILDER:",
    "YES"
    if "build_and_write_uduc_from_extraction_result"
    in coordinator_source
    else "NO",
)

print(
    "COORDINATOR_CALLS_U7_NORMALIZER:",
    "YES"
    if "normalize_uploaded_document_v1"
    in coordinator_source
    else "NO",
)

print(
    "UDUC_CANONICAL_NORMALIZED_INPUT_PRESENT:",
    "YES"
    if "NormalizedUploadedDocumentContent"
    in uduc_source
    else "NO",
)

print(
    "UDUC_DIRECT_EXTRACTION_INPUT_PRESENT:",
    "YES"
    if "build_uduc_from_upload_extraction_result"
    in uduc_source
    else "NO",
)

print(
    "U8.3_EXPECTED_MIGRATION:",
    "UploadExtractionResult -> U7 normalize -> NormalizedUploadedDocumentContent -> UDUC",
)