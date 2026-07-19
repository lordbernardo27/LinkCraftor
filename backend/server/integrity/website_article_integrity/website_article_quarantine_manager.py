"""Website Article Integrity quarantine execution.

Phase 4.4.5 moves failed article documents and their metadata records from
the active UDARE Store into a reversible quarantine store.

The operation is transactional. If the move or manifest update fails, files
moved during the current execution are restored to their original paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Iterable


QUARANTINE_VERSION = "website_article_quarantine_v1"
PHASE = "4.4.5"
PHASE_NAME = "Quarantine Failed Articles"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .strftime("%Y%m%dT%H%M%S%fZ")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(
            descriptor,
            "wb",
        ) as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(
            temporary_path,
            path,
        )
    finally:
        temporary_path.unlink(
            missing_ok=True,
        )


def atomic_write_text(path: Path, value: str) -> None:
    atomic_write_bytes(
        path,
        value.encode("utf-8"),
    )


def atomic_write_json(
    path: Path,
    value: dict[str, Any],
) -> None:
    atomic_write_text(
        path,
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
    )


def write_jsonl(
    path: Path,
    records: Iterable[dict[str, Any]],
) -> None:
    lines = [
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
        )
        for record in records
    ]

    atomic_write_text(
        path,
        "\n".join(lines) + ("\n" if lines else ""),
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL in {path} at line "
                    f"{line_number}: {exc}"
                ) from exc

            if not isinstance(record, dict):
                raise RuntimeError(
                    f"Expected JSON object in {path} at line "
                    f"{line_number}."
                )

            records.append(record)

    return records


def safe_relative_path(
    *,
    root: Path,
    relative_value: str,
    required_prefix: str,
) -> Path:
    normalized = relative_value.replace("\\", "/")

    if not normalized.startswith(required_prefix):
        raise RuntimeError(
            f"Path does not begin with {required_prefix}: "
            f"{relative_value}"
        )

    relative_path = Path(normalized)

    if relative_path.is_absolute():
        raise RuntimeError(
            f"Absolute path is not allowed: {relative_value}"
        )

    resolved_root = root.resolve()
    resolved_path = (
        root
        / relative_path
    ).resolve()

    if (
        resolved_path != resolved_root
        and resolved_root not in resolved_path.parents
    ):
        raise RuntimeError(
            f"Path escapes the permitted root: {relative_value}"
        )

    return resolved_path


def extract_html_title(path: Path) -> str:
    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return path.stem

    match = re.search(
        r"<title\b[^>]*>(.*?)</title\s*>",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if match is None:
        return path.stem

    title = re.sub(
        r"<[^>]+>",
        " ",
        match.group(1),
    )

    title = " ".join(title.split())

    return title or path.stem


def render_active_index(
    *,
    workspace_id: str,
    article_paths: list[Path],
    udare_root: Path,
    quarantined_count: int,
) -> str:
    rows: list[str] = []

    for index, article_path in enumerate(
        article_paths,
        start=1,
    ):
        relative_path = article_path.relative_to(
            udare_root
        ).as_posix()

        title = extract_html_title(
            article_path
        )

        rows.append(
            "<tr>"
            f"<td>{index}</td>"
            f"<td>{escape(title)}</td>"
            f"<td><code>{escape(article_path.stem)}</code></td>"
            f"<td><a href=\"{escape(relative_path)}\" "
            "target=\"_blank\">Open article</a></td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UDARE Store — {escape(workspace_id)}</title>
  <style>
    body {{
      margin: 0;
      padding: 32px;
      font-family: Arial, Helvetica, sans-serif;
      background: #f5f7fa;
      color: #17202a;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    .summary {{
      background: white;
      border: 1px solid #dfe6e9;
      border-radius: 10px;
      padding: 18px;
      margin-bottom: 24px;
    }}

    .panel {{
      background: white;
      border: 1px solid #dfe6e9;
      border-radius: 10px;
      padding: 20px;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    th, td {{
      padding: 10px;
      border-bottom: 1px solid #e9ecef;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #f8f9fa;
      position: sticky;
      top: 0;
    }}

    input {{
      width: 100%;
      max-width: 500px;
      padding: 10px;
      margin-bottom: 16px;
      border: 1px solid #ccd1d1;
      border-radius: 7px;
    }}

    a {{
      color: #21618c;
    }}
  </style>
</head>
<body>
<div class="container">
  <h1>UDARE Store</h1>

  <div class="summary">
    <strong>Workspace:</strong> {escape(workspace_id)}<br>
    <strong>Active articles:</strong> {len(article_paths)}<br>
    <strong>Quarantined articles:</strong> {quarantined_count}
  </div>

  <div class="panel">
    <input
      id="search"
      type="search"
      placeholder="Search title or identity"
      oninput="filterRows()"
    >

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Article</th>
          <th>Identity</th>
          <th>Document</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</div>

<script>
function filterRows() {{
  const query = document
    .getElementById("search")
    .value
    .trim()
    .toLowerCase();

  for (const row of document.querySelectorAll("tbody tr")) {{
    row.style.display = row.innerText
      .toLowerCase()
      .includes(query)
      ? ""
      : "none";
  }}
}}
</script>
</body>
</html>
"""


def render_quarantine_index(
    *,
    workspace_id: str,
    records: list[dict[str, Any]],
) -> str:
    rows: list[str] = []

    for index, record in enumerate(
        records,
        start=1,
    ):
        quarantine_article_path = Path(
            record["quarantine_article_path"]
        )

        article_link = (
            quarantine_article_path
            .relative_to(
                quarantine_article_path.parents[1]
            )
            .as_posix()
        )

        reasons = "<br>".join(
            escape(reason)
            for reason in record[
                "consolidated_failure_reasons"
            ]
        )

        rows.append(
            "<tr>"
            f"<td>{index}</td>"
            f"<td><code>{escape(record['source_record_id'])}</code></td>"
            f"<td>{escape(record['display_title'])}</td>"
            f"<td>{reasons}</td>"
            f"<td><a href=\"{escape(article_link)}\" "
            "target=\"_blank\">Open quarantined article</a></td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Website Article Quarantine — {escape(workspace_id)}</title>
  <style>
    body {{
      margin: 0;
      padding: 32px;
      font-family: Arial, Helvetica, sans-serif;
      background: #f5f7fa;
      color: #17202a;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    .notice {{
      background: #fef9e7;
      border-left: 4px solid #f5b041;
      padding: 16px;
      margin-bottom: 24px;
    }}

    .panel {{
      background: white;
      border: 1px solid #dfe6e9;
      border-radius: 10px;
      padding: 20px;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    th, td {{
      padding: 10px;
      border-bottom: 1px solid #e9ecef;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #f8f9fa;
    }}

    a {{
      color: #21618c;
    }}
  </style>
</head>
<body>
<div class="container">
  <h1>Website Article Quarantine</h1>

  <div class="notice">
    These records failed Website Article Integrity validation and are
    excluded from the active UDARE Store. They remain preserved for
    inspection, repair or later restoration.
  </div>

  <div class="panel">
    <p>
      <strong>Workspace:</strong> {escape(workspace_id)}<br>
      <strong>Quarantined records:</strong> {len(records)}
    </p>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Source identity</th>
          <th>Article</th>
          <th>Reasons</th>
          <th>Document</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""


def move_to_quarantine(
    *,
    source: Path,
    destination: Path,
    expected_sha256: str | None,
    moved_pairs: list[tuple[Path, Path]],
) -> str:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if source.is_file():
        source_hash = sha256_file(
            source
        )

        if (
            expected_sha256 is not None
            and source_hash != expected_sha256
        ):
            raise RuntimeError(
                "Source file hash does not match the integrity "
                f"report: {source}"
            )

        if destination.exists():
            destination_hash = sha256_file(
                destination
            )

            if destination_hash != source_hash:
                raise RuntimeError(
                    "Conflicting quarantine destination exists: "
                    f"{destination}"
                )

            source.unlink()

            return source_hash

        os.replace(
            source,
            destination,
        )

        moved_pairs.append(
            (
                source,
                destination,
            )
        )

        destination_hash = sha256_file(
            destination
        )

        if destination_hash != source_hash:
            raise RuntimeError(
                "File hash changed during quarantine move: "
                f"{destination}"
            )

        return destination_hash

    if destination.is_file():
        destination_hash = sha256_file(
            destination
        )

        if (
            expected_sha256 is not None
            and destination_hash != expected_sha256
        ):
            raise RuntimeError(
                "Existing quarantine file hash does not match "
                f"the report: {destination}"
            )

        return destination_hash

    raise FileNotFoundError(
        f"Neither active nor quarantined file exists: {source}"
    )


def execute_quarantine(
    *,
    project_root: Path,
    workspace_id: str,
    expected_store_count_before: int,
    expected_active_count_after: int,
    expected_quarantine_count: int,
    deferred_upstream_count: int,
) -> dict[str, Any]:
    data_root = (
        project_root
        / "backend"
        / "server"
        / "data"
    )

    udare_root = (
        data_root
        / "udare_store"
        / workspace_id
    )

    active_articles_root = (
        udare_root
        / "articles"
    )

    active_metadata_root = (
        udare_root
        / "metadata"
    )

    udare_manifest_path = (
        udare_root
        / "manifests"
        / "udare_store_manifest.json"
    )

    udare_index_path = (
        udare_root
        / "index.html"
    )

    integrity_root = (
        data_root
        / "website_article_integrity"
        / workspace_id
    )

    report_root = (
        integrity_root
        / "report"
    )

    failures_path = (
        report_root
        / "website_integrity_failures.jsonl"
    )

    report_json_path = (
        report_root
        / "website_integrity_report.json"
    )

    quarantine_root = (
        integrity_root
        / "quarantine"
    )

    quarantine_articles_root = (
        quarantine_root
        / "articles"
    )

    quarantine_metadata_root = (
        quarantine_root
        / "metadata"
    )

    quarantine_manifest_path = (
        quarantine_root
        / "manifests"
        / "quarantine_manifest.json"
    )

    quarantine_records_path = (
        quarantine_root
        / "quarantine_records.jsonl"
    )

    quarantine_execution_path = (
        quarantine_root
        / "quarantine_execution.json"
    )

    quarantine_index_path = (
        quarantine_root
        / "index.html"
    )

    if not failures_path.is_file():
        raise FileNotFoundError(
            f"Integrity failure report missing: {failures_path}"
        )

    if not report_json_path.is_file():
        raise FileNotFoundError(
            f"Integrity JSON report missing: {report_json_path}"
        )

    if not udare_manifest_path.is_file():
        raise FileNotFoundError(
            f"UDARE manifest missing: {udare_manifest_path}"
        )

    failures = load_jsonl(
        failures_path
    )

    if len(failures) != expected_quarantine_count:
        raise RuntimeError(
            "Unexpected quarantine candidate count. "
            f"Expected {expected_quarantine_count}, "
            f"found {len(failures)}."
        )

    source_ids = [
        record.get("source_record_id")
        for record in failures
    ]

    if len(set(source_ids)) != len(source_ids):
        raise RuntimeError(
            "Duplicate source identities exist in the "
            "quarantine candidate list."
        )

    for record in failures:
        if record.get("overall_status") != "FAIL":
            raise RuntimeError(
                "A quarantine candidate is not marked FAIL."
            )

        if record.get("quarantine_candidate") is not True:
            raise RuntimeError(
                "A failed article is not marked as a "
                "quarantine candidate."
            )

    active_article_count_before = len(
        list(
            active_articles_root.rglob("*.html")
        )
    )

    active_metadata_count_before = len(
        list(
            active_metadata_root.glob("*.json")
        )
    )

    valid_before_counts = {
        expected_store_count_before,
        expected_active_count_after,
    }

    if active_article_count_before not in valid_before_counts:
        raise RuntimeError(
            "Unexpected active article count before quarantine: "
            f"{active_article_count_before}"
        )

    if active_metadata_count_before not in valid_before_counts:
        raise RuntimeError(
            "Unexpected active metadata count before quarantine: "
            f"{active_metadata_count_before}"
        )

    transaction_id = (
        "website_article_quarantine_"
        + compact_utc_timestamp()
    )

    transaction_backup_root = (
        quarantine_root
        / "backups"
        / transaction_id
    )

    transaction_backup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_manifest_bytes = (
        udare_manifest_path.read_bytes()
    )

    original_index_bytes = (
        udare_index_path.read_bytes()
        if udare_index_path.is_file()
        else None
    )

    atomic_write_bytes(
        transaction_backup_root
        / "udare_store_manifest_before_quarantine.json",
        original_manifest_bytes,
    )

    if original_index_bytes is not None:
        atomic_write_bytes(
            transaction_backup_root
            / "udare_index_before_quarantine.html",
            original_index_bytes,
        )

    moved_pairs: list[tuple[Path, Path]] = []
    quarantine_records: list[dict[str, Any]] = []

    try:
        quarantined_at = utc_now()

        for failure_record in failures:
            article_relative_value = failure_record.get(
                "article_path"
            )

            metadata_relative_value = failure_record.get(
                "metadata_path"
            )

            if not isinstance(
                article_relative_value,
                str,
            ):
                raise RuntimeError(
                    "Quarantine record has no article_path."
                )

            if not isinstance(
                metadata_relative_value,
                str,
            ):
                raise RuntimeError(
                    "Quarantine record has no metadata_path."
                )

            source_article_path = safe_relative_path(
                root=udare_root,
                relative_value=article_relative_value,
                required_prefix="articles/",
            )

            source_metadata_path = safe_relative_path(
                root=udare_root,
                relative_value=metadata_relative_value,
                required_prefix="metadata/",
            )

            destination_article_path = safe_relative_path(
                root=quarantine_root,
                relative_value=article_relative_value,
                required_prefix="articles/",
            )

            destination_metadata_path = safe_relative_path(
                root=quarantine_root,
                relative_value=metadata_relative_value,
                required_prefix="metadata/",
            )

            article_sha256 = move_to_quarantine(
                source=source_article_path,
                destination=destination_article_path,
                expected_sha256=failure_record.get(
                    "article_sha256"
                ),
                moved_pairs=moved_pairs,
            )

            metadata_sha256 = move_to_quarantine(
                source=source_metadata_path,
                destination=destination_metadata_path,
                expected_sha256=None,
                moved_pairs=moved_pairs,
            )

            quarantine_record_seed = (
                f"{workspace_id}|"
                f"{failure_record['source_record_id']}|"
                f"{article_sha256}|"
                f"{metadata_sha256}"
            )

            quarantine_record_id = (
                "wai_quarantine_"
                + hashlib.sha256(
                    quarantine_record_seed.encode(
                        "utf-8"
                    )
                ).hexdigest()[:24]
            )

            quarantine_records.append(
                {
                    "quarantine_record_id": (
                        quarantine_record_id
                    ),
                    "quarantine_version": (
                        QUARANTINE_VERSION
                    ),
                    "phase": PHASE,
                    "workspace_id": workspace_id,
                    "source_record_id": failure_record[
                        "source_record_id"
                    ],
                    "source_url": failure_record.get(
                        "source_url"
                    ),
                    "display_title": failure_record.get(
                        "display_title"
                    )
                    or Path(
                        article_relative_value
                    ).stem,
                    "quarantined_at": quarantined_at,
                    "quarantine_status": "QUARANTINED",
                    "original_article_path": str(
                        source_article_path
                    ),
                    "original_metadata_path": str(
                        source_metadata_path
                    ),
                    "quarantine_article_path": str(
                        destination_article_path
                    ),
                    "quarantine_metadata_path": str(
                        destination_metadata_path
                    ),
                    "article_sha256": article_sha256,
                    "metadata_sha256": metadata_sha256,
                    "stage_statuses": failure_record.get(
                        "stage_statuses",
                        {},
                    ),
                    "failure_reasons": failure_record.get(
                        "failure_reasons",
                        {},
                    ),
                    "consolidated_failure_reasons": (
                        failure_record.get(
                            "consolidated_failure_reasons",
                            [],
                        )
                    ),
                    "source_report_record_id": (
                        failure_record.get(
                            "report_record_id"
                        )
                    ),
                    "restorable": True,
                }
            )

        active_article_paths = sorted(
            path
            for path in active_articles_root.rglob(
                "*.html"
            )
            if path.is_file()
        )

        active_metadata_paths = sorted(
            path
            for path in active_metadata_root.glob(
                "*.json"
            )
            if path.is_file()
        )

        if (
            len(active_article_paths)
            != expected_active_count_after
        ):
            raise RuntimeError(
                "Active article count after quarantine is "
                f"{len(active_article_paths)}, expected "
                f"{expected_active_count_after}."
            )

        if (
            len(active_metadata_paths)
            != expected_active_count_after
        ):
            raise RuntimeError(
                "Active metadata count after quarantine is "
                f"{len(active_metadata_paths)}, expected "
                f"{expected_active_count_after}."
            )

        udare_manifest = json.loads(
            original_manifest_bytes.decode(
                "utf-8-sig"
            )
        )

        if not isinstance(udare_manifest, dict):
            raise RuntimeError(
                "UDARE manifest root is not a JSON object."
            )

        udare_manifest["record_count"] = (
            expected_active_count_after
        )

        udare_manifest["article_document_count"] = (
            expected_active_count_after
        )

        udare_manifest["metadata_record_count"] = (
            expected_active_count_after
        )

        udare_manifest[
            "website_article_integrity_quarantine"
        ] = {
            "status": "EXECUTED",
            "phase": PHASE,
            "quarantine_version": QUARANTINE_VERSION,
            "transaction_id": transaction_id,
            "executed_at": quarantined_at,
            "active_record_count": (
                expected_active_count_after
            ),
            "quarantined_record_count": (
                expected_quarantine_count
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "quarantine_manifest_path": str(
                quarantine_manifest_path
            ),
            "integrity_report_path": str(
                report_json_path
            ),
        }

        active_index_html = render_active_index(
            workspace_id=workspace_id,
            article_paths=active_article_paths,
            udare_root=udare_root,
            quarantined_count=expected_quarantine_count,
        )

        quarantine_index_html = (
            render_quarantine_index(
                workspace_id=workspace_id,
                records=quarantine_records,
            )
        )

        quarantine_manifest: dict[str, Any] = {
            "schema_version": "1.0",
            "quarantine_version": (
                QUARANTINE_VERSION
            ),
            "phase": PHASE,
            "phase_name": PHASE_NAME,
            "transaction_id": transaction_id,
            "workspace_id": workspace_id,
            "executed_at": quarantined_at,
            "execution_status": "COMPLETE",
            "source_store": "UDARE Store",
            "source_integrity_report": str(
                report_json_path
            ),
            "source_failure_ledger": str(
                failures_path
            ),
            "active_record_count_before": (
                active_article_count_before
            ),
            "active_record_count_after": (
                expected_active_count_after
            ),
            "quarantined_record_count": (
                len(quarantine_records)
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "active_articles_directory": str(
                active_articles_root
            ),
            "active_metadata_directory": str(
                active_metadata_root
            ),
            "quarantine_articles_directory": str(
                quarantine_articles_root
            ),
            "quarantine_metadata_directory": str(
                quarantine_metadata_root
            ),
            "quarantine_records_path": str(
                quarantine_records_path
            ),
            "quarantine_index_path": str(
                quarantine_index_path
            ),
            "udare_manifest_path": str(
                udare_manifest_path
            ),
            "udare_index_path": str(
                udare_index_path
            ),
            "transaction_backup_root": str(
                transaction_backup_root
            ),
            "quarantined_source_ids": [
                record["source_record_id"]
                for record in quarantine_records
            ],
            "restorable": True,
        }

        execution_record: dict[str, Any] = {
            "schema_version": "1.0",
            "transaction_id": transaction_id,
            "phase": PHASE,
            "workspace_id": workspace_id,
            "execution_status": "COMPLETE",
            "executed_at": quarantined_at,
            "active_record_count": (
                expected_active_count_after
            ),
            "quarantined_record_count": (
                len(quarantine_records)
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "quarantine_manifest_path": str(
                quarantine_manifest_path
            ),
            "source_report_sha256": sha256_file(
                report_json_path
            ),
            "source_failures_sha256": sha256_file(
                failures_path
            ),
        }

        write_jsonl(
            quarantine_records_path,
            quarantine_records,
        )

        atomic_write_json(
            quarantine_manifest_path,
            quarantine_manifest,
        )

        atomic_write_json(
            quarantine_execution_path,
            execution_record,
        )

        atomic_write_text(
            quarantine_index_path,
            quarantine_index_html,
        )

        atomic_write_json(
            udare_manifest_path,
            udare_manifest,
        )

        atomic_write_text(
            udare_index_path,
            active_index_html,
        )

        return quarantine_manifest

    except Exception:
        for source, destination in reversed(
            moved_pairs
        ):
            if destination.exists():
                source.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                os.replace(
                    destination,
                    source,
                )

        atomic_write_bytes(
            udare_manifest_path,
            original_manifest_bytes,
        )

        if original_index_bytes is not None:
            atomic_write_bytes(
                udare_index_path,
                original_index_bytes,
            )

        raise
