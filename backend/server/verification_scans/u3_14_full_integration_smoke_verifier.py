from __future__ import annotations

import asyncio
import copy
import io
import json
import shutil
import tempfile
import traceback
import uuid
from pathlib import Path

from starlette.datastructures import Headers, UploadFile

import backend.server.routes.files as files_route
import backend.server.stores.uploaded_document_unified_content as uduc_store
import backend.server.stores.dis_rejection_pattern_store as rejection_store


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


repo_root = Path.cwd().resolve()

token = uuid.uuid4().hex[:12]

raw_workspace = f"u3_14_smoke_{token}"
workspace_id = files_route._ws(raw_workspace)

filename = f"u3_14_smoke_{token}.txt"

marker = f"U3_14_FULL_INTEGRATION_MARKER_{token}"

raw = (
    f"{marker}\n\n"
    "LinkCraftor integration verification document.\n"
    "Internal linking improves website navigation and "
    "helps readers discover related information.\n"
    "Semantic analysis can identify useful phrases "
    "while preserving the original document content.\n"
).encode("utf-8")


# ------------------------------------------------------------
# Snapshot live production roots and module state.
# ------------------------------------------------------------

old_files_data_dir = files_route.DATA_DIR
old_files_docs_dir = files_route.DOCS_DIR

old_uduc_output_dir = uduc_store.UDUC_OUTPUT_DIR

old_rejection_data_dir = rejection_store.DATA_DIR

old_rejection_cache = copy.deepcopy(
    rejection_store._REJECTION_CACHE
)

old_batch_buffers = copy.deepcopy(
    rejection_store._BATCH_BUFFERS
)

with files_route._INDEX_LOCKS_GUARD:
    old_index_locks = dict(files_route._INDEX_LOCKS)


live_docs_workspace = (
    old_files_docs_dir / workspace_id
)

live_uduc_workspace = (
    old_uduc_output_dir / workspace_id
)

live_rejection_file = (
    old_rejection_data_dir
    / f"{workspace_id}.json"
)


check(
    "SYNTHETIC_WORKSPACE_NOT_PREEXISTING_IN_LIVE_DOCS",
    not live_docs_workspace.exists(),
)

check(
    "SYNTHETIC_WORKSPACE_NOT_PREEXISTING_IN_LIVE_UDUC",
    not live_uduc_workspace.exists(),
)

check(
    "SYNTHETIC_WORKSPACE_NOT_PREEXISTING_IN_LIVE_REJECTION_STORE",
    not live_rejection_file.exists(),
)


temp_root = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_u3_14_smoke_"
    )
).resolve()

check(
    "TEMP_ROOT_OUTSIDE_REPOSITORY",
    temp_root != repo_root
    and repo_root not in temp_root.parents,
)


temp_data_dir = temp_root / "data"
temp_docs_dir = temp_data_dir / "docs"

temp_uduc_dir = (
    temp_root
    / "uploaded_document_unified_content"
)

temp_rejection_dir = (
    temp_root
    / "dis"
    / "rejection_patterns"
)


response = None
route_error = None
stored_path = None
uduc_path = None
index_path = None


try:
    # --------------------------------------------------------
    # Redirect every identified U3 filesystem mutation root.
    # --------------------------------------------------------

    files_route.DATA_DIR = temp_data_dir
    files_route.DOCS_DIR = temp_docs_dir

    uduc_store.UDUC_OUTPUT_DIR = temp_uduc_dir

    rejection_store.DATA_DIR = temp_rejection_dir


    check(
        "FILES_DATA_DIR_REDIRECTED",
        files_route.DATA_DIR == temp_data_dir,
    )

    check(
        "FILES_DOCS_DIR_REDIRECTED",
        files_route.DOCS_DIR == temp_docs_dir,
    )

    check(
        "UDUC_OUTPUT_DIR_REDIRECTED",
        uduc_store.UDUC_OUTPUT_DIR
        == temp_uduc_dir,
    )

    check(
        "REJECTION_STORE_DATA_DIR_REDIRECTED",
        rejection_store.DATA_DIR
        == temp_rejection_dir,
    )


    # --------------------------------------------------------
    # Construct a real Starlette UploadFile and invoke the
    # canonical FastAPI endpoint function.
    # --------------------------------------------------------

    upload = UploadFile(
        file=io.BytesIO(raw),
        filename=filename,
        size=len(raw),
        headers=Headers(
            {
                "content-type": "text/plain",
            }
        ),
    )


    async def execute_upload():
        return await files_route.upload_file(
            workspace_id=raw_workspace,
            file=upload,
        )


    try:
        response = asyncio.run(
            execute_upload()
        )

    except Exception as exc:
        route_error = exc

        print()
        print("ROUTE_EXECUTION_ERROR:")
        print(
            f"{type(exc).__name__}: {exc}"
        )

        traceback.print_exc()


    check(
        "CANONICAL_ROUTE_EXECUTED_WITHOUT_EXCEPTION",
        route_error is None,
    )

    check(
        "PUBLIC_RESPONSE_IS_DICT",
        isinstance(response, dict),
    )


    if isinstance(response, dict):
        # ----------------------------------------------------
        # Public HTTP compatibility contract.
        # ----------------------------------------------------

        check(
            "PUBLIC_RESPONSE_OK_TRUE",
            response.get("ok") is True,
        )

        check(
            "PUBLIC_WORKSPACE_IS_CANONICAL",
            response.get("workspace_id")
            == workspace_id,
        )

        check(
            "PUBLIC_FILENAME_PRESERVED",
            response.get("filename")
            == filename,
        )

        check(
            "PUBLIC_EXTENSION_TXT",
            response.get("ext") == ".txt",
        )

        document_id = str(
            response.get("document_id") or ""
        ).strip()

        check(
            "PUBLIC_DOCUMENT_ID_PRESENT",
            bool(document_id),
        )

        check(
            "PUBLIC_PIPELINE_UPLOAD_DOCUMENT",
            response.get("pipeline")
            == "upload_document",
        )

        check(
            "PUBLIC_JOB_ID_NONE",
            response.get("job_id") is None,
        )

        check(
            "PUBLIC_PROCESSING_STATUS_NOT_APPLICABLE",
            response.get("processing_status")
            == "not_applicable",
        )

        check(
            "PUBLIC_EXECUTION_STARTED_TRUE",
            response.get("execution_started")
            is True,
        )

        check(
            "PUBLIC_EXECUTION_COMPLETED_TRUE",
            response.get("execution_completed")
            is True,
        )

        check(
            "PUBLIC_PREVIEW_CONTAINS_MARKER",
            marker
            in str(response.get("text") or ""),
        )

        check(
            "INTERNAL_EXTRACTION_NOT_EXPOSED_PUBLICLY",
            "extraction" not in response,
        )

        check(
            "INTERNAL_UDUC_NOT_EXPOSED_PUBLICLY",
            "uduc" not in response,
        )


        # ----------------------------------------------------
        # Verify committed source/index in TEMP storage.
        # ----------------------------------------------------

        public_doc = response.get("doc")

        check(
            "PUBLIC_DOC_IS_DICT",
            isinstance(public_doc, dict),
        )

        if isinstance(public_doc, dict):
            check(
                "PUBLIC_DOC_ID_MATCHES_DOCUMENT_ID",
                str(
                    public_doc.get("doc_id") or ""
                ).strip()
                == document_id,
            )

            stored_name = str(
                public_doc.get("stored_name") or ""
            ).strip()

            check(
                "PUBLIC_STORED_NAME_PRESENT",
                bool(stored_name),
            )

            stored_path = (
                temp_docs_dir
                / workspace_id
                / stored_name
            )

            check(
                "TEMP_SOURCE_FILE_EXISTS",
                stored_path.is_file(),
            )

            if stored_path.is_file():
                persisted_raw = (
                    stored_path.read_bytes()
                )

                check(
                    "TEMP_SOURCE_BYTES_EXACT",
                    persisted_raw == raw,
                )


        index_path = (
            temp_docs_dir
            / workspace_id
            / "index.json"
        )

        check(
            "TEMP_INDEX_EXISTS",
            index_path.is_file(),
        )

        if index_path.is_file():
            index_rows = json.loads(
                index_path.read_text(
                    encoding="utf-8"
                )
            )

            check(
                "TEMP_INDEX_IS_LIST",
                isinstance(index_rows, list),
            )

            matching_rows = [
                row
                for row in index_rows
                if isinstance(row, dict)
                and str(
                    row.get("doc_id") or ""
                ).strip()
                == document_id
            ]

            check(
                "TEMP_INDEX_HAS_EXACTLY_ONE_DOCUMENT_ROW",
                len(matching_rows) == 1,
            )


        # ----------------------------------------------------
        # Verify real UDUC construction/persistence.
        # ----------------------------------------------------

        uduc_path = (
            temp_uduc_dir
            / workspace_id
            / f"{document_id}.json"
        )

        check(
            "TEMP_UDUC_FILE_EXISTS",
            uduc_path.is_file(),
        )

        if uduc_path.is_file():
            uduc_payload = json.loads(
                uduc_path.read_text(
                    encoding="utf-8"
                )
            )

            check(
                "TEMP_UDUC_IS_DICT",
                isinstance(
                    uduc_payload,
                    dict,
                ),
            )

            check(
                "TEMP_UDUC_WORKSPACE_MATCH",
                str(
                    uduc_payload.get(
                        "workspace_id"
                    )
                    or ""
                ).strip()
                == workspace_id,
            )

            check(
                "TEMP_UDUC_DOCUMENT_ID_MATCH",
                str(
                    uduc_payload.get(
                        "document_id"
                    )
                    or ""
                ).strip()
                == document_id,
            )

            uduc_text = json.dumps(
                uduc_payload,
                ensure_ascii=False,
            )

            check(
                "TEMP_UDUC_CONTAINS_CANONICAL_MARKER",
                marker in uduc_text,
            )


        # ----------------------------------------------------
        # Rejection-learning state may or may not receive
        # events depending on phrase decisions. Either way,
        # any synthetic state must be keyed only by this
        # isolated workspace and will be restored below.
        # ----------------------------------------------------

        synthetic_buffer = (
            rejection_store
            ._BATCH_BUFFERS
            .get(workspace_id)
        )

        synthetic_cache = (
            rejection_store
            ._REJECTION_CACHE
            .get(workspace_id)
        )

        check(
            "REJECTION_LEARNING_STATE_ISOLATED",
            (
                synthetic_buffer is None
                or isinstance(
                    synthetic_buffer,
                    list,
                )
            )
            and (
                synthetic_cache is None
                or isinstance(
                    synthetic_cache,
                    list,
                )
            ),
        )


    # --------------------------------------------------------
    # Ensure all known generated files are under temp_root.
    # --------------------------------------------------------

    generated_files = [
        path
        for path in temp_root.rglob("*")
        if path.is_file()
    ]

    check(
        "SMOKE_TEST_GENERATED_TEMP_ARTIFACTS",
        len(generated_files) >= 2,
    )

    all_generated_inside_temp = all(
        temp_root in path.resolve().parents
        for path in generated_files
    )

    check(
        "ALL_DISCOVERED_TEST_ARTIFACTS_INSIDE_TEMP_ROOT",
        all_generated_inside_temp,
    )


finally:
    # --------------------------------------------------------
    # Restore production module globals.
    # --------------------------------------------------------

    files_route.DATA_DIR = old_files_data_dir
    files_route.DOCS_DIR = old_files_docs_dir

    uduc_store.UDUC_OUTPUT_DIR = (
        old_uduc_output_dir
    )

    rejection_store.DATA_DIR = (
        old_rejection_data_dir
    )


    # --------------------------------------------------------
    # Restore in-memory rejection-learning state exactly.
    # --------------------------------------------------------

    rejection_store._REJECTION_CACHE.clear()
    rejection_store._REJECTION_CACHE.update(
        old_rejection_cache
    )

    rejection_store._BATCH_BUFFERS.clear()
    rejection_store._BATCH_BUFFERS.update(
        old_batch_buffers
    )


    # --------------------------------------------------------
    # Restore the upload index-lock table exactly.
    # --------------------------------------------------------

    with files_route._INDEX_LOCKS_GUARD:
        files_route._INDEX_LOCKS.clear()
        files_route._INDEX_LOCKS.update(
            old_index_locks
        )


    # --------------------------------------------------------
    # Remove isolated test filesystem.
    # --------------------------------------------------------

    shutil.rmtree(
        temp_root,
        ignore_errors=True,
    )


print()
print("=== POST-TEST RESTORATION ===")

check(
    "FILES_DATA_DIR_RESTORED",
    files_route.DATA_DIR
    == old_files_data_dir,
)

check(
    "FILES_DOCS_DIR_RESTORED",
    files_route.DOCS_DIR
    == old_files_docs_dir,
)

check(
    "UDUC_OUTPUT_DIR_RESTORED",
    uduc_store.UDUC_OUTPUT_DIR
    == old_uduc_output_dir,
)

check(
    "REJECTION_STORE_DATA_DIR_RESTORED",
    rejection_store.DATA_DIR
    == old_rejection_data_dir,
)

check(
    "REJECTION_CACHE_RESTORED",
    rejection_store._REJECTION_CACHE
    == old_rejection_cache,
)

check(
    "BATCH_BUFFERS_RESTORED",
    rejection_store._BATCH_BUFFERS
    == old_batch_buffers,
)

with files_route._INDEX_LOCKS_GUARD:
    current_index_locks = dict(
        files_route._INDEX_LOCKS
    )

check(
    "INDEX_LOCK_STATE_RESTORED",
    current_index_locks
    == old_index_locks,
)

check(
    "TEMP_ROOT_REMOVED",
    not temp_root.exists(),
)


print()
print("=== LIVE PRODUCTION LEAK CHECK ===")

check(
    "NO_LIVE_DOCS_WORKSPACE_ARTIFACT",
    not live_docs_workspace.exists(),
)

check(
    "NO_LIVE_UDUC_WORKSPACE_ARTIFACT",
    not live_uduc_workspace.exists(),
)

check(
    "NO_LIVE_REJECTION_PATTERN_ARTIFACT",
    not live_rejection_file.exists(),
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
        "U3.14_FULL_INTEGRATION_SMOKE_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U3.14 full integration smoke verification failed."
    )

print(
    "U3.14_FULL_INTEGRATION_SMOKE_VERIFICATION: PASS"
)