from __future__ import annotations

import asyncio
import io
import shutil
import tempfile
import zipfile

from dataclasses import replace
from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def upload_file(name: str, raw: bytes) -> UploadFile:
    return UploadFile(
        filename=name,
        file=io.BytesIO(raw),
    )


def build_docx_bytes() -> bytes:
    output = io.BytesIO()

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

    root_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship
    Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="word/document.xml"/>
</Relationships>
"""

    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>U3.10 DOCX Title</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Canonical DOCX body content.</w:t></w:r>
    </w:p>
    <w:sectPr/>
  </w:body>
</w:document>
"""

    document_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""

    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("word/document.xml", document)
        zf.writestr(
            "word/_rels/document.xml.rels",
            document_rels,
        )

    return output.getvalue()


def dependencies() -> UploadIntakeDependencies:
    return UploadIntakeDependencies(
        guess_extension=files_route._guess_ext,
        normalize_workspace_id=files_route._ws,
        extract_preview=files_route._extract_preview_from_bytes,
        store_and_index=files_route._store_and_index,
        rollback_committed_upload=files_route._rollback_committed_upload,
        workspace_directory=files_route._ws_dir,
        allowed_extensions=files_route.ALLOWED_EXT,
    )


async def intake(
    workspace: str,
    filename: str,
    raw: bytes,
    deps: UploadIntakeDependencies,
):
    return await run_upload_intake(
        workspace_id=workspace,
        file=upload_file(filename, raw),
        dependencies=deps,
    )


async def main() -> None:
    temp_root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_10_"
        )
    )

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR

    try:
        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = temp_root / "docs"

        deps = dependencies()

        fixtures = {
            "sample.txt": (
                b"TXT canonical content.",
                "txt",
            ),
            "sample.md": (
                b"# Markdown Title\n\nMarkdown canonical body.",
                "markdown",
            ),
            "sample.markdown": (
                b"# Markdown Title\n\nMarkdown canonical body.",
                "markdown",
            ),
            "sample.html": (
                b"<html><body><h1>HTML Title</h1>"
                b"<p>HTML canonical body.</p></body></html>",
                "html",
            ),
            "sample.htm": (
                b"<html><body><h1>HTML Title</h1>"
                b"<p>HTML canonical body.</p></body></html>",
                "html",
            ),
            "sample.docx": (
                build_docx_bytes(),
                "docx",
            ),
        }

        # ----------------------------------------------------
        # TEST 1
        # All six accepted extensions complete intake using
        # canonical persisted-source extraction.
        # ----------------------------------------------------

        for filename, (
            payload,
            expected_source_type,
        ) in fixtures.items():

            workspace = (
                "ws_u3_10_"
                + filename.replace(".", "_")
            )

            result = await intake(
                workspace,
                filename,
                payload,
                deps,
            )

            extraction = result.get("extraction") or {}
            metadata = result.get("doc") or {}

            stored_name = str(
                metadata.get("stored_name") or ""
            )

            stored_path = (
                files_route._ws_dir(workspace)
                / stored_name
            )

            label = filename.upper().replace(".", "_")

            check(
                f"{label}_INTAKE_OK",
                result.get("ok") is True,
            )

            check(
                f"{label}_EXTRACTION_SUCCESS",
                extraction.get("extraction_status")
                == "success",
            )

            check(
                f"{label}_SOURCE_TYPE",
                extraction.get("source_type")
                == expected_source_type,
            )

            check(
                f"{label}_SOURCE_BYTES_EXACT",
                stored_path.is_file()
                and stored_path.read_bytes() == payload,
            )

            check(
                f"{label}_EXTRACTOR_USED_STORED_SOURCE",
                Path(
                    str(extraction.get("source_path") or "")
                ).resolve()
                == stored_path.resolve(),
            )

        # ----------------------------------------------------
        # TEST 2
        # Extension aliases must produce equivalent preview
        # behavior.
        # ----------------------------------------------------

        markdown_payload = (
            b"# Alias Title\n\nAlias markdown body."
        )

        md_preview = (
            files_route._extract_preview_from_bytes(
                "alias.md",
                ".md",
                markdown_payload,
            )
        )

        markdown_preview = (
            files_route._extract_preview_from_bytes(
                "alias.markdown",
                ".markdown",
                markdown_payload,
            )
        )

        check(
            "MARKDOWN_ALIAS_PREVIEW_TEXT_EQUIVALENT",
            md_preview.get("text")
            == markdown_preview.get("text"),
        )

        check(
            "MARKDOWN_ALIAS_PREVIEW_HTML_EQUIVALENT",
            md_preview.get("html")
            == markdown_preview.get("html"),
        )

        check(
            "MARKDOWN_ALIAS_PREVIEW_MODE_EQUIVALENT",
            md_preview.get("is_html")
            == markdown_preview.get("is_html"),
        )

        html_payload = (
            b"<h1>Alias HTML</h1><p>Body</p>"
        )

        html_preview = (
            files_route._extract_preview_from_bytes(
                "alias.html",
                ".html",
                html_payload,
            )
        )

        htm_preview = (
            files_route._extract_preview_from_bytes(
                "alias.htm",
                ".htm",
                html_payload,
            )
        )

        check(
            "HTML_ALIAS_PREVIEW_EQUIVALENT",
            html_preview.get("text")
            == htm_preview.get("text")
            and html_preview.get("html")
            == htm_preview.get("html"),
        )

        # ----------------------------------------------------
        # TEST 3
        # Preview truncation must not truncate canonical
        # extraction.
        # ----------------------------------------------------

        tail_marker = "U3_10_CANONICAL_TAIL_MARKER"

        large_text = (
            "A" * (files_route.TEXT_LIMIT + 500)
            + tail_marker
        )

        large_raw = large_text.encode("utf-8")

        truncation_result = await intake(
            "ws_u3_10_truncation",
            "large.txt",
            large_raw,
            deps,
        )

        preview_text = str(
            truncation_result.get("text") or ""
        )

        canonical_text = str(
            (
                truncation_result.get("extraction")
                or {}
            ).get("text")
            or ""
        )

        check(
            "PREVIEW_REPORTS_TRUNCATED",
            truncation_result.get("truncated") is True,
        )

        check(
            "PREVIEW_LENGTH_CAPPED",
            len(preview_text)
            == files_route.TEXT_LIMIT,
        )

        check(
            "TAIL_MARKER_ABSENT_FROM_PREVIEW",
            tail_marker not in preview_text,
        )

        check(
            "TAIL_MARKER_PRESENT_IN_CANONICAL_EXTRACTION",
            tail_marker in canonical_text,
        )

        check(
            "CANONICAL_EXTRACTION_LONGER_THAN_PREVIEW",
            len(canonical_text) > len(preview_text),
        )

        trunc_meta = (
            truncation_result.get("doc")
            or {}
        )

        trunc_source = (
            files_route._ws_dir(
                "ws_u3_10_truncation"
            )
            / str(
                trunc_meta.get("stored_name")
                or ""
            )
        )

        check(
            "TRUNCATION_SOURCE_BYTES_UNCHANGED",
            trunc_source.read_bytes() == large_raw,
        )

        # ----------------------------------------------------
        # TEST 4
        # Preview failure occurs before persistence.
        # ----------------------------------------------------

        def failing_preview(
            filename: str,
            ext: str,
            raw: bytes,
        ):
            raise RuntimeError(
                "synthetic preview failure"
            )

        failing_deps = replace(
            deps,
            extract_preview=failing_preview,
        )

        preview_failure_raised = False

        try:
            await intake(
                "ws_u3_10_preview_failure",
                "failure.txt",
                b"must never be persisted",
                failing_deps,
            )
        except RuntimeError as exc:
            preview_failure_raised = (
                "synthetic preview failure"
                in str(exc)
            )

        failure_workspace = files_route._ws_dir(
            "ws_u3_10_preview_failure"
        )

        check(
            "PREVIEW_FAILURE_PROPAGATES",
            preview_failure_raised,
        )

        check(
            "PREVIEW_FAILURE_BEFORE_PERSISTENCE",
            not failure_workspace.exists(),
        )

    finally:
        files_route.DATA_DIR = original_data_dir
        files_route.DOCS_DIR = original_docs_dir

        # Remove only temporary lock-registry entries created
        # for this verifier.
        temp_prefix = str(temp_root.resolve())

        with files_route._INDEX_LOCKS_GUARD:
            stale_keys = [
                key
                for key in files_route._INDEX_LOCKS
                if key.startswith(temp_prefix)
            ]

            for key in stale_keys:
                files_route._INDEX_LOCKS.pop(
                    key,
                    None,
                )

        shutil.rmtree(
            temp_root,
            ignore_errors=True,
        )

    failures = [
        name
        for name, status in results
        if status != "PASS"
    ]

    print()
    print("========================================")

    if failures:
        print(
            "U3.10_PREVIEW_CANONICAL_BEHAVIORAL_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.10 behavioral verification failed."
        )

    print(
        "U3.10_PREVIEW_CANONICAL_BEHAVIORAL_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())