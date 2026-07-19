"""Final Website Article Integrity certification.

Phase 4.4.6 certifies the active UDARE Store after validation,
reporting and quarantine have completed.

The certificate covers the active PASS articles. Quarantined records
remain preserved but excluded. Deferred upstream pages are explicitly
recorded as outside the certification scope.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Iterable


CERTIFIER_VERSION = "website_article_integrity_certifier_v1"
CERTIFICATE_SCHEMA_VERSION = "1.0"
PHASE = "4.4.6"
PHASE_NAME = "Certify Website Article Integrity"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


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
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSONL in {path} at line "
                    f"{line_number}: {exc}"
                ) from exc

            if not isinstance(value, dict):
                raise RuntimeError(
                    f"Expected JSON object in {path} at line "
                    f"{line_number}."
                )

            records.append(value)

    return records


def resolve_store_path(
    *,
    root: Path,
    relative_value: str,
    required_prefix: str,
) -> Path:
    normalized = relative_value.replace("\\", "/")

    if not normalized.startswith(required_prefix):
        raise RuntimeError(
            f"Invalid store path prefix: {relative_value}"
        )

    relative_path = Path(normalized)

    if relative_path.is_absolute():
        raise RuntimeError(
            f"Absolute store path is not permitted: "
            f"{relative_value}"
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
            f"Store path escapes permitted root: "
            f"{relative_value}"
        )

    return resolved_path


def evidence_root_hash(
    artifacts: dict[str, dict[str, str]],
) -> str:
    digest = hashlib.sha256()

    for name in sorted(artifacts):
        artifact = artifacts[name]

        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(
            artifact["sha256"].encode("ascii")
        )
        digest.update(b"\n")

    return digest.hexdigest()


def render_certificate_html(
    certificate: dict[str, Any],
) -> str:
    coverage = certificate["coverage"]

    quarantine_rows: list[str] = []

    for record in certificate["quarantined_records"]:
        reasons = "<br>".join(
            escape(reason)
            for reason in record[
                "consolidated_failure_reasons"
            ]
        )

        quarantine_rows.append(
            "<tr>"
            f"<td><code>{escape(record['source_record_id'])}</code></td>"
            f"<td>{escape(record['display_title'])}</td>"
            f"<td>{reasons}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Website Article Integrity Certificate</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Arial, Helvetica, sans-serif;
      background: #f4f6f7;
      color: #17202a;
    }}

    body {{
      margin: 0;
      padding: 34px;
    }}

    .container {{
      max-width: 1250px;
      margin: 0 auto;
    }}

    .certificate {{
      background: white;
      border: 2px solid #1e8449;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
    }}

    .status {{
      display: inline-block;
      padding: 7px 13px;
      border-radius: 999px;
      background: #d5f5e3;
      color: #196f3d;
      font-weight: 700;
    }}

    .qualification {{
      margin: 18px 0;
      padding: 14px;
      border-left: 4px solid #f5b041;
      background: #fef9e7;
    }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 14px;
      margin: 24px 0;
    }}

    .card {{
      border: 1px solid #dfe6e9;
      border-radius: 9px;
      padding: 16px;
    }}

    .label {{
      color: #566573;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .value {{
      margin-top: 6px;
      font-size: 27px;
      font-weight: 700;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
    }}

    th, td {{
      padding: 10px;
      border-bottom: 1px solid #e5e7e9;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #f8f9fa;
    }}

    code {{
      overflow-wrap: anywhere;
    }}

    .seal {{
      margin-top: 24px;
      padding: 16px;
      background: #f8f9fa;
      border: 1px solid #dfe6e9;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="certificate">
    <span class="status">CERTIFIED</span>

    <h1>Website Article Integrity Certificate</h1>

    <p>
      <strong>Workspace:</strong>
      {escape(certificate['workspace_id'])}<br>
      <strong>Certificate ID:</strong>
      <code>{escape(certificate['certificate_id'])}</code><br>
      <strong>Certified:</strong>
      {escape(certificate['certified_at'])}
    </p>

    <div class="qualification">
      The active UDARE Store is certified. Three upstream pages
      remain explicitly deferred and are outside the certification
      scope.
    </div>

    <div class="cards">
      <div class="card">
        <div class="label">Expected upstream</div>
        <div class="value">{coverage['expected_upstream_count']}</div>
      </div>

      <div class="card">
        <div class="label">Articles assessed</div>
        <div class="value">{coverage['articles_assessed']}</div>
      </div>

      <div class="card">
        <div class="label">Active certified</div>
        <div class="value">{coverage['active_certified_count']}</div>
      </div>

      <div class="card">
        <div class="label">Quarantined</div>
        <div class="value">{coverage['quarantined_count']}</div>
      </div>

      <div class="card">
        <div class="label">Deferred upstream</div>
        <div class="value">{coverage['deferred_upstream_count']}</div>
      </div>
    </div>

    <h2>Quarantined Records</h2>

    <table>
      <thead>
        <tr>
          <th>Source identity</th>
          <th>Article</th>
          <th>Integrity findings</th>
        </tr>
      </thead>
      <tbody>
        {''.join(quarantine_rows)}
      </tbody>
    </table>

    <div class="seal">
      <strong>SHA-256 evidence seal</strong><br>
      <code>{escape(certificate['evidence_root_sha256'])}</code>
    </div>
  </div>
</div>
</body>
</html>
"""


def certify_website_article_integrity(
    *,
    project_root: Path,
    workspace_id: str,
    expected_upstream_count: int,
    expected_assessed_count: int,
    expected_active_count: int,
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

    structure_summary_path = (
        integrity_root
        / "structure"
        / "structure_summary.json"
    )

    component_summary_path = (
        integrity_root
        / "components"
        / "component_summary.json"
    )

    corruption_summary_path = (
        integrity_root
        / "corruption_truncation"
        / "corruption_truncation_summary.json"
    )

    report_root = (
        integrity_root
        / "report"
    )

    report_json_path = (
        report_root
        / "website_integrity_report.json"
    )

    report_html_path = (
        report_root
        / "website_integrity_report.html"
    )

    report_ledger_path = (
        report_root
        / "website_integrity_ledger.jsonl"
    )

    report_failures_path = (
        report_root
        / "website_integrity_failures.jsonl"
    )

    quarantine_root = (
        integrity_root
        / "quarantine"
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

    certification_root = (
        integrity_root
        / "certification"
    )

    active_ledger_path = (
        certification_root
        / "certified_active_articles.jsonl"
    )

    quarantine_ledger_path = (
        certification_root
        / "certified_quarantine_records.jsonl"
    )

    evidence_manifest_path = (
        certification_root
        / "certification_evidence_manifest.json"
    )

    certificate_json_path = (
        certification_root
        / "website_article_integrity_certificate.json"
    )

    certificate_html_path = (
        certification_root
        / "website_article_integrity_certificate.html"
    )

    certification_index_path = (
        certification_root
        / "index.html"
    )

    required_paths = (
        active_articles_root,
        active_metadata_root,
        udare_manifest_path,
        udare_index_path,
        structure_summary_path,
        component_summary_path,
        corruption_summary_path,
        report_json_path,
        report_html_path,
        report_ledger_path,
        report_failures_path,
        quarantine_manifest_path,
        quarantine_records_path,
        quarantine_execution_path,
        quarantine_index_path,
    )

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required certification evidence missing: {path}"
            )

    report = load_json(
        report_json_path
    )

    report_ledger = load_jsonl(
        report_ledger_path
    )

    report_failures = load_jsonl(
        report_failures_path
    )

    quarantine_manifest = load_json(
        quarantine_manifest_path
    )

    quarantine_records = load_jsonl(
        quarantine_records_path
    )

    udare_manifest = load_json(
        udare_manifest_path
    )

    pass_records = [
        record
        for record in report_ledger
        if record.get("overall_status") == "PASS"
    ]

    failed_records = [
        record
        for record in report_ledger
        if record.get("overall_status") == "FAIL"
    ]

    if len(report_ledger) != expected_assessed_count:
        raise RuntimeError(
            "Integrity ledger does not contain the expected "
            f"{expected_assessed_count} assessed records."
        )

    if len(pass_records) != expected_active_count:
        raise RuntimeError(
            "Integrity ledger PASS count does not equal "
            f"{expected_active_count}."
        )

    if len(failed_records) != expected_quarantine_count:
        raise RuntimeError(
            "Integrity ledger FAIL count does not equal "
            f"{expected_quarantine_count}."
        )

    if len(report_failures) != expected_quarantine_count:
        raise RuntimeError(
            "Failure ledger count is incorrect."
        )

    if len(quarantine_records) != expected_quarantine_count:
        raise RuntimeError(
            "Quarantine ledger count is incorrect."
        )

    if (
        expected_active_count
        + expected_quarantine_count
        != expected_assessed_count
    ):
        raise RuntimeError(
            "Active and quarantine counts do not equal "
            "the assessed article count."
        )

    if (
        expected_assessed_count
        + deferred_upstream_count
        != expected_upstream_count
    ):
        raise RuntimeError(
            "Assessed and deferred counts do not equal "
            "the expected upstream count."
        )

    if report.get("report_status") != "COMPLETE":
        raise RuntimeError(
            "Website Integrity Report is not COMPLETE."
        )

    if (
        report.get("integrity_outcome")
        != "COMPLETE_WITH_FAILURES"
    ):
        raise RuntimeError(
            "Website Integrity Report outcome is invalid."
        )

    if (
        quarantine_manifest.get("execution_status")
        != "COMPLETE"
    ):
        raise RuntimeError(
            "Quarantine execution is not COMPLETE."
        )

    if (
        quarantine_manifest.get(
            "quarantined_record_count"
        )
        != expected_quarantine_count
    ):
        raise RuntimeError(
            "Quarantine manifest count is incorrect."
        )

    if (
        quarantine_manifest.get(
            "deferred_upstream_count"
        )
        != deferred_upstream_count
    ):
        raise RuntimeError(
            "Quarantine manifest deferred count is incorrect."
        )

    if udare_manifest.get("record_count") != expected_active_count:
        raise RuntimeError(
            "UDARE manifest active record count is incorrect."
        )

    if (
        udare_manifest.get("article_document_count")
        != expected_active_count
    ):
        raise RuntimeError(
            "UDARE manifest article document count is incorrect."
        )

    if (
        udare_manifest.get("metadata_record_count")
        != expected_active_count
    ):
        raise RuntimeError(
            "UDARE manifest metadata record count is incorrect."
        )

    quarantine_state = udare_manifest.get(
        "website_article_integrity_quarantine",
        {},
    )

    if quarantine_state.get("status") != "EXECUTED":
        raise RuntimeError(
            "UDARE manifest quarantine state is not EXECUTED."
        )

    active_certification_records: list[
        dict[str, Any]
    ] = []

    expected_active_article_paths: set[str] = set()
    expected_active_metadata_paths: set[str] = set()

    for record in pass_records:
        article_relative_path = record.get(
            "article_path"
        )

        metadata_relative_path = record.get(
            "metadata_path"
        )

        source_record_id = record.get(
            "source_record_id"
        )

        if not isinstance(article_relative_path, str):
            raise RuntimeError(
                "PASS record has no valid article path."
            )

        if not isinstance(metadata_relative_path, str):
            raise RuntimeError(
                "PASS record has no valid metadata path."
            )

        if not isinstance(source_record_id, str):
            raise RuntimeError(
                "PASS record has no source identity."
            )

        article_path = resolve_store_path(
            root=udare_root,
            relative_value=article_relative_path,
            required_prefix="articles/",
        )

        metadata_path = resolve_store_path(
            root=udare_root,
            relative_value=metadata_relative_path,
            required_prefix="metadata/",
        )

        if not article_path.is_file():
            raise FileNotFoundError(
                f"Certified PASS article missing: {article_path}"
            )

        if not metadata_path.is_file():
            raise FileNotFoundError(
                f"Certified PASS metadata missing: {metadata_path}"
            )

        article_sha256 = sha256_file(
            article_path
        )

        expected_report_hash = record.get(
            "article_sha256"
        )

        if (
            isinstance(expected_report_hash, str)
            and article_sha256 != expected_report_hash
        ):
            raise RuntimeError(
                "PASS article hash differs from the integrity "
                f"report: {article_path}"
            )

        metadata_sha256 = sha256_file(
            metadata_path
        )

        expected_active_article_paths.add(
            article_relative_path.replace("\\", "/")
        )

        expected_active_metadata_paths.add(
            metadata_relative_path.replace("\\", "/")
        )

        active_certification_records.append(
            {
                "certificate_scope": "ACTIVE_PASS_ARTICLE",
                "workspace_id": workspace_id,
                "source_record_id": source_record_id,
                "source_url": record.get("source_url"),
                "display_title": record.get("display_title"),
                "article_path": article_relative_path,
                "metadata_path": metadata_relative_path,
                "article_sha256": article_sha256,
                "metadata_sha256": metadata_sha256,
                "overall_integrity_status": "PASS",
                "stage_statuses": record.get(
                    "stage_statuses",
                    {},
                ),
            }
        )

    actual_active_article_paths = {
        path.relative_to(
            udare_root
        ).as_posix()
        for path in active_articles_root.rglob("*.html")
        if path.is_file()
    }

    actual_active_metadata_paths = {
        path.relative_to(
            udare_root
        ).as_posix()
        for path in active_metadata_root.glob("*.json")
        if path.is_file()
    }

    if (
        actual_active_article_paths
        != expected_active_article_paths
    ):
        raise RuntimeError(
            "Active article files do not exactly match "
            "the PASS integrity ledger."
        )

    if (
        actual_active_metadata_paths
        != expected_active_metadata_paths
    ):
        raise RuntimeError(
            "Active metadata files do not exactly match "
            "the PASS integrity ledger."
        )

    failed_source_ids = {
        record.get("source_record_id")
        for record in failed_records
    }

    quarantine_source_ids = {
        record.get("source_record_id")
        for record in quarantine_records
    }

    if failed_source_ids != quarantine_source_ids:
        raise RuntimeError(
            "Quarantine source identities do not match "
            "the failed integrity set."
        )

    certified_quarantine_records: list[
        dict[str, Any]
    ] = []

    expected_quarantine_article_paths: set[str] = set()
    expected_quarantine_metadata_paths: set[str] = set()

    quarantine_root_resolved = quarantine_root.resolve()

    for record in quarantine_records:
        article_path = Path(
            record["quarantine_article_path"]
        ).resolve()

        metadata_path = Path(
            record["quarantine_metadata_path"]
        ).resolve()

        if quarantine_root_resolved not in article_path.parents:
            raise RuntimeError(
                "Quarantine article path escapes quarantine root."
            )

        if quarantine_root_resolved not in metadata_path.parents:
            raise RuntimeError(
                "Quarantine metadata path escapes quarantine root."
            )

        if not article_path.is_file():
            raise FileNotFoundError(
                f"Quarantined article missing: {article_path}"
            )

        if not metadata_path.is_file():
            raise FileNotFoundError(
                f"Quarantined metadata missing: {metadata_path}"
            )

        article_sha256 = sha256_file(
            article_path
        )

        metadata_sha256 = sha256_file(
            metadata_path
        )

        if article_sha256 != record.get("article_sha256"):
            raise RuntimeError(
                "Quarantined article hash mismatch: "
                f"{article_path}"
            )

        if metadata_sha256 != record.get("metadata_sha256"):
            raise RuntimeError(
                "Quarantined metadata hash mismatch: "
                f"{metadata_path}"
            )

        expected_quarantine_article_paths.add(
            article_path.relative_to(
                quarantine_root
            ).as_posix()
        )

        expected_quarantine_metadata_paths.add(
            metadata_path.relative_to(
                quarantine_root
            ).as_posix()
        )

        certified_quarantine_records.append(
            {
                "certificate_scope": "QUARANTINED_EXCLUDED",
                "workspace_id": workspace_id,
                "source_record_id": record[
                    "source_record_id"
                ],
                "source_url": record.get("source_url"),
                "display_title": record.get("display_title"),
                "quarantine_article_path": str(article_path),
                "quarantine_metadata_path": str(metadata_path),
                "article_sha256": article_sha256,
                "metadata_sha256": metadata_sha256,
                "consolidated_failure_reasons": record.get(
                    "consolidated_failure_reasons",
                    [],
                ),
                "restorable": record.get(
                    "restorable",
                    False,
                ),
            }
        )

    actual_quarantine_article_paths = {
        path.relative_to(
            quarantine_root
        ).as_posix()
        for path in (
            quarantine_root
            / "articles"
        ).rglob("*.html")
        if path.is_file()
    }

    actual_quarantine_metadata_paths = {
        path.relative_to(
            quarantine_root
        ).as_posix()
        for path in (
            quarantine_root
            / "metadata"
        ).glob("*.json")
        if path.is_file()
    }

    if (
        actual_quarantine_article_paths
        != expected_quarantine_article_paths
    ):
        raise RuntimeError(
            "Quarantine article files do not exactly match "
            "the quarantine ledger."
        )

    if (
        actual_quarantine_metadata_paths
        != expected_quarantine_metadata_paths
    ):
        raise RuntimeError(
            "Quarantine metadata files do not exactly match "
            "the quarantine ledger."
        )

    active_source_ids = {
        record["source_record_id"]
        for record in active_certification_records
    }

    if active_source_ids & quarantine_source_ids:
        raise RuntimeError(
            "A source identity exists in both active and "
            "quarantine certification scopes."
        )

    certified_at = utc_now()

    certificate_seed = (
        f"{workspace_id}|"
        f"{report.get('report_id')}|"
        f"{quarantine_manifest.get('transaction_id')}|"
        f"{expected_active_count}|"
        f"{expected_quarantine_count}|"
        f"{certified_at}"
    )

    certificate_id = (
        "website_article_integrity_certificate_"
        + hashlib.sha256(
            certificate_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    certification_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_paths = (
        active_ledger_path,
        quarantine_ledger_path,
        evidence_manifest_path,
        certificate_json_path,
        certificate_html_path,
        certification_index_path,
    )

    original_udare_manifest_bytes = (
        udare_manifest_path.read_bytes()
    )

    try:
        write_jsonl(
            active_ledger_path,
            active_certification_records,
        )

        write_jsonl(
            quarantine_ledger_path,
            certified_quarantine_records,
        )

        udare_manifest[
            "website_article_integrity_certification"
        ] = {
            "status": "CERTIFIED",
            "phase": PHASE,
            "certifier_version": CERTIFIER_VERSION,
            "certificate_id": certificate_id,
            "certified_at": certified_at,
            "certification_scope": "ACTIVE_UDARE_STORE",
            "qualification": (
                "WITH_DEFERRED_UPSTREAM_RECORDS"
            ),
            "active_certified_count": (
                expected_active_count
            ),
            "quarantined_count": (
                expected_quarantine_count
            ),
            "deferred_upstream_count": (
                deferred_upstream_count
            ),
            "certificate_path": str(
                certificate_json_path
            ),
            "certificate_index_path": str(
                certification_index_path
            ),
            "evidence_manifest_path": str(
                evidence_manifest_path
            ),
        }

        atomic_write_json(
            udare_manifest_path,
            udare_manifest,
        )

        source_artifact_paths = {
            "structure_summary": structure_summary_path,
            "component_summary": component_summary_path,
            "corruption_truncation_summary": (
                corruption_summary_path
            ),
            "website_integrity_report_json": (
                report_json_path
            ),
            "website_integrity_report_html": (
                report_html_path
            ),
            "website_integrity_ledger": (
                report_ledger_path
            ),
            "website_integrity_failures": (
                report_failures_path
            ),
            "quarantine_manifest": (
                quarantine_manifest_path
            ),
            "quarantine_records": (
                quarantine_records_path
            ),
            "quarantine_execution": (
                quarantine_execution_path
            ),
            "quarantine_index": (
                quarantine_index_path
            ),
            "udare_manifest": (
                udare_manifest_path
            ),
            "udare_index": (
                udare_index_path
            ),
            "certified_active_ledger": (
                active_ledger_path
            ),
            "certified_quarantine_ledger": (
                quarantine_ledger_path
            ),
        }

        evidence_artifacts = {
            name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for name, path in source_artifact_paths.items()
        }

        evidence_root_sha256 = evidence_root_hash(
            evidence_artifacts
        )

        evidence_manifest: dict[str, Any] = {
            "schema_version": "1.0",
            "certificate_id": certificate_id,
            "certifier_version": CERTIFIER_VERSION,
            "workspace_id": workspace_id,
            "generated_at": certified_at,
            "hash_algorithm": "SHA-256",
            "evidence_root_sha256": (
                evidence_root_sha256
            ),
            "artifacts": evidence_artifacts,
        }

        atomic_write_json(
            evidence_manifest_path,
            evidence_manifest,
        )

        certificate: dict[str, Any] = {
            "schema_version": (
                CERTIFICATE_SCHEMA_VERSION
            ),
            "certificate_id": certificate_id,
            "certifier_version": CERTIFIER_VERSION,
            "phase": PHASE,
            "phase_name": PHASE_NAME,
            "workspace_id": workspace_id,
            "certified_at": certified_at,
            "certification_status": "CERTIFIED",
            "certification_scope": "ACTIVE_UDARE_STORE",
            "certification_outcome": (
                "CERTIFIED_ACTIVE_STORE_WITH_"
                "DEFERRED_UPSTREAM_RECORDS"
            ),
            "qualification": (
                "WITH_DEFERRED_UPSTREAM_RECORDS"
            ),
            "source_store": "UDARE Store",
            "coverage": {
                "expected_upstream_count": (
                    expected_upstream_count
                ),
                "articles_assessed": (
                    expected_assessed_count
                ),
                "active_certified_count": (
                    expected_active_count
                ),
                "quarantined_count": (
                    expected_quarantine_count
                ),
                "deferred_upstream_count": (
                    deferred_upstream_count
                ),
                "coverage_reconciliation": (
                    expected_active_count
                    + expected_quarantine_count
                    + deferred_upstream_count
                ),
            },
            "integrity_assertions": {
                "all_active_articles_have_pass_status": True,
                "all_active_articles_have_metadata": True,
                "active_article_and_metadata_counts_match": True,
                "failed_records_are_excluded_from_active_store": True,
                "failed_records_are_preserved_in_quarantine": True,
                "active_and_quarantine_scopes_do_not_overlap": True,
                "article_hashes_match_integrity_evidence": True,
                "quarantine_hashes_match_quarantine_evidence": True,
                "quarantine_is_reversible": True,
                "deferred_upstream_records_are_explicit": True,
            },
            "quarantined_records": (
                certified_quarantine_records
            ),
            "evidence_root_sha256": (
                evidence_root_sha256
            ),
            "evidence_manifest_path": str(
                evidence_manifest_path
            ),
            "certified_active_ledger_path": str(
                active_ledger_path
            ),
            "certified_quarantine_ledger_path": str(
                quarantine_ledger_path
            ),
            "certificate_html_path": str(
                certificate_html_path
            ),
            "important_notes": [
                (
                    "Certification applies to the 2,219 active "
                    "UDARE articles that passed all Website "
                    "Article Integrity checks."
                ),
                (
                    "Three failed article and metadata pairs are "
                    "preserved in the reversible quarantine store "
                    "and are excluded from active certification."
                ),
                (
                    "Three upstream pages absent from the UDARE "
                    "Store remain deferred and are outside the "
                    "certification scope."
                ),
                (
                    "The evidence seal is an internal SHA-256 "
                    "integrity seal, not an external authority "
                    "digital signature."
                ),
            ],
        }

        atomic_write_json(
            certificate_json_path,
            certificate,
        )

        certificate_html = render_certificate_html(
            certificate
        )

        atomic_write_text(
            certificate_html_path,
            certificate_html,
        )

        atomic_write_text(
            certification_index_path,
            certificate_html,
        )

        return certificate

    except Exception:
        atomic_write_bytes(
            udare_manifest_path,
            original_udare_manifest_bytes,
        )

        for path in generated_paths:
            path.unlink(
                missing_ok=True,
            )

        raise
