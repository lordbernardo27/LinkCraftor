from __future__ import annotations

import io
import json
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_upload(name: str, data: bytes) -> UploadFile:
    return UploadFile(
        filename=name,
        file=io.BytesIO(data),
    )


def store(
    workspace_id: str,
    filename: str,
    payload: bytes,
):
    return files_route._store_and_index(
        workspace_id,
        make_upload(filename, payload),
        payload,
        preview_html="",
        preview_text=payload.decode(
            "utf-8",
            errors="ignore",
        ),
    )


def read_index(workspace_id: str):
    path = files_route._index_path(workspace_id)

    if not path.exists():
        return []

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def main() -> None:
    root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_9_"
        )
    )

    original_data_dir = files_route.DATA_DIR

    try:
        files_route.DATA_DIR = root

        # ----------------------------------------------------
        # TEST 1
        # 20 simultaneous uploads to the SAME workspace,
        # all using the SAME original filename.
        # ----------------------------------------------------

        workspace = "ws_u3_9_same"

        def same_workspace_job(i: int):
            return store(
                workspace,
                "same-name.txt",
                f"payload-{i}".encode("utf-8"),
            )

        with ThreadPoolExecutor(
            max_workers=10
        ) as executor:
            metas = list(
                executor.map(
                    same_workspace_job,
                    range(20),
                )
            )

        records = read_index(workspace)

        doc_ids = [
            str(m.get("doc_id") or "")
            for m in metas
        ]

        stored_names = [
            str(m.get("stored_name") or "")
            for m in metas
        ]

        registry_ids = [
            str(r.get("doc_id") or "")
            for r in records
        ]

        check(
            "SAME_WORKSPACE_20_UPLOADS_20_RESULTS",
            len(metas) == 20,
        )

        check(
            "SAME_WORKSPACE_20_UNIQUE_DOCUMENT_IDS",
            len(set(doc_ids)) == 20
            and all(doc_ids),
        )

        check(
            "SAME_WORKSPACE_20_UNIQUE_STORED_NAMES",
            len(set(stored_names)) == 20
            and all(stored_names),
        )

        check(
            "SAME_WORKSPACE_REGISTRY_HAS_20_RECORDS",
            len(records) == 20,
        )

        check(
            "SAME_WORKSPACE_EACH_DOCUMENT_ONCE",
            all(
                registry_ids.count(doc_id) == 1
                for doc_id in doc_ids
            ),
        )

        ws_dir = files_route._ws_dir(workspace)

        check(
            "SAME_WORKSPACE_ALL_20_SOURCES_EXIST",
            all(
                (ws_dir / stored_name).is_file()
                for stored_name in stored_names
            ),
        )

        # ----------------------------------------------------
        # TEST 2
        # Concurrent rollback of one committed upload while
        # another upload is being added to the same workspace.
        # ----------------------------------------------------

        target = metas[0]

        target_id = str(
            target.get("doc_id") or ""
        )
        target_name = str(
            target.get("stored_name") or ""
        )

        def rollback_target():
            files_route._rollback_committed_upload(
                workspace,
                target_id,
                expected_stored_name=target_name,
            )
            return "rolled_back"

        def add_neighbor():
            return store(
                workspace,
                "neighbor.txt",
                b"neighbor-concurrent-payload",
            )

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:
            rollback_future = executor.submit(
                rollback_target
            )
            neighbor_future = executor.submit(
                add_neighbor
            )

            rollback_result = (
                rollback_future.result()
            )
            neighbor = neighbor_future.result()

        after_race = read_index(workspace)

        after_ids = [
            str(r.get("doc_id") or "")
            for r in after_race
        ]

        neighbor_id = str(
            neighbor.get("doc_id") or ""
        )
        neighbor_name = str(
            neighbor.get("stored_name") or ""
        )

        check(
            "CONCURRENT_ROLLBACK_COMPLETED",
            rollback_result == "rolled_back",
        )

        check(
            "CONCURRENT_ROLLBACK_TARGET_REMOVED",
            target_id not in after_ids
            and not (
                ws_dir / target_name
            ).exists(),
        )

        check(
            "CONCURRENT_NEIGHBOR_REGISTRY_PRESERVED",
            after_ids.count(neighbor_id) == 1,
        )

        check(
            "CONCURRENT_NEIGHBOR_SOURCE_PRESERVED",
            (
                ws_dir / neighbor_name
            ).is_file(),
        )

        check(
            "CONCURRENT_ROLLBACK_ONLY_REMOVED_ONE_RECORD",
            len(after_race) == 20,
        )

        # Explanation:
        # started with 20
        # rollback removes 1
        # concurrent neighbor adds 1
        # final total must still be 20.

        # ----------------------------------------------------
        # TEST 3
        # Different workspaces concurrently.
        # ----------------------------------------------------

        workspace_a = "ws_u3_9_a"
        workspace_b = "ws_u3_9_b"

        jobs = []

        with ThreadPoolExecutor(
            max_workers=12
        ) as executor:
            for i in range(12):
                jobs.append(
                    executor.submit(
                        store,
                        workspace_a,
                        "cross.txt",
                        f"A-{i}".encode(),
                    )
                )

                jobs.append(
                    executor.submit(
                        store,
                        workspace_b,
                        "cross.txt",
                        f"B-{i}".encode(),
                    )
                )

            cross_results = [
                job.result()
                for job in jobs
            ]

        records_a = read_index(workspace_a)
        records_b = read_index(workspace_b)

        check(
            "WORKSPACE_A_HAS_12_RECORDS",
            len(records_a) == 12,
        )

        check(
            "WORKSPACE_B_HAS_12_RECORDS",
            len(records_b) == 12,
        )

        ids_a = {
            str(r.get("doc_id") or "")
            for r in records_a
        }

        ids_b = {
            str(r.get("doc_id") or "")
            for r in records_b
        }

        check(
            "WORKSPACES_HAVE_DISJOINT_DOCUMENT_IDS",
            ids_a.isdisjoint(ids_b),
        )

        check(
            "WORKSPACE_PATHS_ARE_DISTINCT",
            files_route._index_path(workspace_a)
            != files_route._index_path(workspace_b),
        )

        check(
            "WORKSPACE_LOCK_OBJECTS_ARE_DISTINCT",
            files_route._index_lock(
                files_route._index_path(
                    workspace_a
                )
            )
            is not
            files_route._index_lock(
                files_route._index_path(
                    workspace_b
                )
            ),
        )

        # ----------------------------------------------------
        # TEST 4
        # Same registry path always gets exact same RLock.
        # ----------------------------------------------------

        index_path = files_route._index_path(
            workspace
        )

        lock_1 = files_route._index_lock(
            index_path
        )

        lock_2 = files_route._index_lock(
            Path(str(index_path))
        )

        check(
            "SAME_INDEX_PATH_RETURNS_SAME_LOCK",
            lock_1 is lock_2,
        )

        # ----------------------------------------------------
        # TEST 5
        # Registry remains parseable and source/record
        # correspondence remains exact.
        # ----------------------------------------------------

        final_records = read_index(workspace)

        final_names = {
            str(r.get("stored_name") or "")
            for r in final_records
        }

        actual_sources = {
            p.name
            for p in ws_dir.iterdir()
            if p.is_file()
            and p.name != "index.json"
        }

        check(
            "FINAL_REGISTRY_JSON_VALID_LIST",
            isinstance(final_records, list)
            and all(
                isinstance(r, dict)
                for r in final_records
            ),
        )

        check(
            "FINAL_SOURCE_SET_MATCHES_REGISTRY",
            actual_sources == final_names,
        )

    finally:
        files_route.DATA_DIR = original_data_dir
        shutil.rmtree(
            root,
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
            "U3.9_SAME_PROCESS_CONCURRENCY_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise SystemExit(1)

    print(
        "U3.9_SAME_PROCESS_CONCURRENCY_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    main()