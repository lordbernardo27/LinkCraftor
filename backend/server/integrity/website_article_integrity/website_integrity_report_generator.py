"""Consolidated Website Article Integrity Report generator.

Phase 4.4.4 combines the results of:

- Phase 4.4.1 reconstructed article structure validation
- Phase 4.4.2 required article component validation
- Phase 4.4.3 corruption and truncation detection

The generator does not modify or quarantine UDARE Store assets.
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
from urllib.parse import quote


REPORT_VERSION = "website_integrity_report_v1"
PHASE = "4.4.4"
PHASE_NAME = "Generate Website Integrity Report"


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


def atomic_write_text(path: Path, value: str) -> None:
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
            "w",
            encoding="utf-8",
            newline="\n",
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


def index_by_article_path(
    records: list[dict[str, Any]],
    *,
    source_name: str,
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}

    for record in records:
        article_path = record.get("article_path")

        if not isinstance(article_path, str) or not article_path:
            raise RuntimeError(
                f"{source_name} contains a record without "
                "article_path."
            )

        if article_path in index:
            raise RuntimeError(
                f"{source_name} contains duplicate article path: "
                f"{article_path}"
            )

        index[article_path] = record

    return index


def normalize_reason_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [
        str(item)
        for item in value
        if isinstance(item, str) and item
    ]


def choose_display_title(
    component_record: dict[str, Any],
    article_path: str,
) -> str:
    observations = component_record.get("observations")

    if isinstance(observations, dict):
        for field in (
            "document_title",
            "metadata_title",
        ):
            value = observations.get(field)

            if isinstance(value, str) and value.strip():
                return value.strip()

    return Path(article_path).stem


def choose_source_record_id(
    structure_record: dict[str, Any],
    component_record: dict[str, Any],
    corruption_record: dict[str, Any],
) -> str:
    for record in (
        component_record,
        corruption_record,
        structure_record,
    ):
        value = record.get("source_record_id")

        if isinstance(value, str) and value:
            return value

    raise RuntimeError(
        "Unable to resolve source_record_id."
    )


def build_consolidated_record(
    *,
    workspace_id: str,
    article_path: str,
    structure_record: dict[str, Any],
    component_record: dict[str, Any],
    corruption_record: dict[str, Any],
) -> dict[str, Any]:
    source_record_id = choose_source_record_id(
        structure_record,
        component_record,
        corruption_record,
    )

    structure_status = structure_record.get("status")
    component_status = component_record.get("status")
    corruption_status = corruption_record.get("status")

    valid_statuses = {"PASS", "FAIL"}

    for stage_name, status in (
        ("structure", structure_status),
        ("components", component_status),
        ("corruption_truncation", corruption_status),
    ):
        if status not in valid_statuses:
            raise RuntimeError(
                f"Invalid {stage_name} status for "
                f"{article_path}: {status}"
            )

    structure_reasons = normalize_reason_list(
        structure_record.get("failure_reasons")
    )

    component_reasons = normalize_reason_list(
        component_record.get("failure_reasons")
    )

    corruption_reasons = normalize_reason_list(
        corruption_record.get("corruption_reasons")
    )

    truncation_reasons = normalize_reason_list(
        corruption_record.get("truncation_reasons")
    )

    warning_reasons = normalize_reason_list(
        corruption_record.get("warning_reasons")
    )

    overall_status = (
        "PASS"
        if (
            structure_status == "PASS"
            and component_status == "PASS"
            and corruption_status == "PASS"
        )
        else "FAIL"
    )

    consolidated_reasons = [
        *[
            f"structure:{reason}"
            for reason in structure_reasons
        ],
        *[
            f"components:{reason}"
            for reason in component_reasons
        ],
        *[
            f"corruption:{reason}"
            for reason in corruption_reasons
        ],
        *[
            f"truncation:{reason}"
            for reason in truncation_reasons
        ],
    ]

    component_observations = component_record.get(
        "observations",
        {},
    )

    if not isinstance(component_observations, dict):
        component_observations = {}

    source_url = component_observations.get(
        "source_url"
    )

    metadata_path = component_record.get(
        "metadata_path"
    )

    article_sha256 = (
        component_record.get("article_sha256")
        or corruption_record.get("article_sha256")
        or structure_record.get("file_sha256")
    )

    record_seed = (
        f"{workspace_id}|"
        f"{source_record_id}|"
        f"{article_path}|"
        f"{article_sha256}|"
        f"{overall_status}"
    )

    report_record_id = (
        "wai_report_record_"
        + hashlib.sha256(
            record_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    return {
        "report_record_id": report_record_id,
        "report_version": REPORT_VERSION,
        "phase": PHASE,
        "workspace_id": workspace_id,
        "source_record_id": source_record_id,
        "source_url": source_url,
        "display_title": choose_display_title(
            component_record,
            article_path,
        ),
        "article_path": article_path,
        "metadata_path": metadata_path,
        "article_sha256": article_sha256,
        "overall_status": overall_status,
        "quarantine_candidate": overall_status == "FAIL",
        "stage_statuses": {
            "structure": structure_status,
            "components": component_status,
            "corruption_truncation": corruption_status,
        },
        "failure_reasons": {
            "structure": structure_reasons,
            "components": component_reasons,
            "corruption": corruption_reasons,
            "truncation": truncation_reasons,
        },
        "consolidated_failure_reasons": (
            consolidated_reasons
        ),
        "warning_reasons": warning_reasons,
        "source_result_ids": {
            "structure": structure_record.get(
                "result_id"
            ),
            "components": component_record.get(
                "result_id"
            ),
            "corruption_truncation": (
                corruption_record.get("result_id")
            ),
        },
    }


def article_link(
    *,
    workspace_id: str,
    article_path: str,
) -> str:
    relative_path = (
        f"../../../udare_store/"
        f"{quote(workspace_id)}/"
        f"{quote(article_path, safe='/')}"
    )

    return relative_path


def render_failure_reasons(
    record: dict[str, Any],
) -> str:
    reasons = record.get(
        "consolidated_failure_reasons",
        [],
    )

    if not isinstance(reasons, list) or not reasons:
        return "None"

    return "<br>".join(
        escape(str(reason))
        for reason in reasons
    )


def render_html_report(
    *,
    report: dict[str, Any],
    records: list[dict[str, Any]],
) -> str:
    summary = report["summary"]

    failed_records = [
        record
        for record in records
        if record["overall_status"] == "FAIL"
    ]

    failure_rows: list[str] = []

    for record in failed_records:
        link = article_link(
            workspace_id=report["workspace_id"],
            article_path=record["article_path"],
        )

        failure_rows.append(
            "<tr>"
            f"<td><span class='status fail'>FAIL</span></td>"
            f"<td><code>{escape(record['source_record_id'])}</code></td>"
            f"<td>{escape(record['display_title'])}</td>"
            f"<td>{render_failure_reasons(record)}</td>"
            f"<td><a href='{escape(link)}' target='_blank'>"
            "Open article</a></td>"
            "</tr>"
        )

    ledger_rows: list[str] = []

    for record in records:
        status = record["overall_status"]
        css_class = "pass" if status == "PASS" else "fail"

        link = article_link(
            workspace_id=report["workspace_id"],
            article_path=record["article_path"],
        )

        ledger_rows.append(
            "<tr class='ledger-row'"
            f" data-search='{escape((record['source_record_id'] + ' ' + record['display_title']).lower())}'>"
            f"<td><span class='status {css_class}'>{status}</span></td>"
            f"<td><code>{escape(record['source_record_id'])}</code></td>"
            f"<td>{escape(record['display_title'])}</td>"
            f"<td>{escape(record['stage_statuses']['structure'])}</td>"
            f"<td>{escape(record['stage_statuses']['components'])}</td>"
            f"<td>{escape(record['stage_statuses']['corruption_truncation'])}</td>"
            f"<td><a href='{escape(link)}' target='_blank'>Open</a></td>"
            "</tr>"
        )

    if not failure_rows:
        failure_rows.append(
            "<tr><td colspan='5'>No failed articles.</td></tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Website Article Integrity Report — {escape(report['workspace_id'])}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Arial, Helvetica, sans-serif;
      background: #f5f7fa;
      color: #17202a;
    }}

    body {{
      margin: 0;
      padding: 32px;
    }}

    .container {{
      max-width: 1500px;
      margin: 0 auto;
    }}

    h1, h2 {{
      margin-top: 0;
    }}

    .subtitle {{
      color: #566573;
      margin-bottom: 28px;
    }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 28px;
    }}

    .card {{
      background: white;
      border: 1px solid #dfe6e9;
      border-radius: 10px;
      padding: 18px;
    }}

    .card .label {{
      color: #566573;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .card .value {{
      font-size: 28px;
      font-weight: 700;
      margin-top: 6px;
    }}

    .panel {{
      background: white;
      border: 1px solid #dfe6e9;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 24px;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}

    th, td {{
      border-bottom: 1px solid #e9ecef;
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: #f8f9fa;
      position: sticky;
      top: 0;
    }}

    .status {{
      display: inline-block;
      min-width: 48px;
      text-align: center;
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 12px;
      font-weight: 700;
    }}

    .status.pass {{
      background: #d5f5e3;
      color: #196f3d;
    }}

    .status.fail {{
      background: #fadbd8;
      color: #922b21;
    }}

    .notice {{
      border-left: 4px solid #f5b041;
      background: #fef9e7;
      padding: 14px 16px;
      margin-bottom: 24px;
    }}

    input[type="search"] {{
      width: 100%;
      max-width: 520px;
      padding: 11px;
      border: 1px solid #ccd1d1;
      border-radius: 7px;
      margin-bottom: 16px;
    }}

    code {{
      white-space: nowrap;
    }}

    a {{
      color: #21618c;
    }}
  </style>
</head>
<body>
<div class="container">
  <h1>Website Article Integrity Report</h1>
  <div class="subtitle">
    Workspace: <strong>{escape(report['workspace_id'])}</strong><br>
    Generated: {escape(report['generated_at'])}<br>
    Report version: {escape(report['report_version'])}
  </div>

  <div class="cards">
    <div class="card">
      <div class="label">Stored articles</div>
      <div class="value">{summary['stored_article_count']}</div>
    </div>
    <div class="card">
      <div class="label">Overall PASS</div>
      <div class="value">{summary['overall_pass_count']}</div>
    </div>
    <div class="card">
      <div class="label">Overall FAIL</div>
      <div class="value">{summary['overall_fail_count']}</div>
    </div>
    <div class="card">
      <div class="label">Deferred upstream</div>
      <div class="value">{summary['deferred_upstream_count']}</div>
    </div>
    <div class="card">
      <div class="label">Quarantine candidates</div>
      <div class="value">{summary['quarantine_candidate_count']}</div>
    </div>
  </div>

  <div class="notice">
    Three upstream pages absent from the UDARE Store remain deferred.
    Quarantine has not yet been executed. Failed articles remain in the
    UDARE Store until Phase 4.4.5.
  </div>

  <div class="panel">
    <h2>Failed Articles</h2>
    <table>
      <thead>
        <tr>
          <th>Status</th>
          <th>Source identity</th>
          <th>Article</th>
          <th>Findings</th>
          <th>Document</th>
        </tr>
      </thead>
      <tbody>
        {''.join(failure_rows)}
      </tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Complete Integrity Ledger</h2>
    <input
      id="ledger-search"
      type="search"
      placeholder="Search source identity or article title"
      oninput="filterLedger()"
    >
    <table>
      <thead>
        <tr>
          <th>Overall</th>
          <th>Source identity</th>
          <th>Article</th>
          <th>Structure</th>
          <th>Components</th>
          <th>Corruption / truncation</th>
          <th>Document</th>
        </tr>
      </thead>
      <tbody>
        {''.join(ledger_rows)}
      </tbody>
    </table>
  </div>
</div>

<script>
function filterLedger() {{
  const query = document
    .getElementById("ledger-search")
    .value
    .trim()
    .toLowerCase();

  for (const row of document.querySelectorAll(".ledger-row")) {{
    const value = row.dataset.search || "";
    row.style.display = value.includes(query) ? "" : "none";
  }}
}}
</script>
</body>
</html>
"""


def generate_website_integrity_report(
    *,
    project_root: Path,
    workspace_id: str,
    expected_store_count: int,
    expected_upstream_count: int,
    deferred_upstream_count: int,
) -> dict[str, Any]:
    data_root = (
        project_root
        / "backend"
        / "server"
        / "data"
    )

    integrity_root = (
        data_root
        / "website_article_integrity"
        / workspace_id
    )

    structure_results_path = (
        integrity_root
        / "structure"
        / "structure_results.jsonl"
    )

    component_results_path = (
        integrity_root
        / "components"
        / "component_results.jsonl"
    )

    corruption_results_path = (
        integrity_root
        / "corruption_truncation"
        / "corruption_truncation_results.jsonl"
    )

    required_sources = {
        "structure": structure_results_path,
        "components": component_results_path,
        "corruption_truncation": corruption_results_path,
    }

    for source_name, source_path in required_sources.items():
        if not source_path.is_file():
            raise FileNotFoundError(
                f"Missing {source_name} result file: "
                f"{source_path}"
            )

    structure_records = load_jsonl(
        structure_results_path
    )

    component_records = load_jsonl(
        component_results_path
    )

    corruption_records = load_jsonl(
        corruption_results_path
    )

    if len(structure_records) != expected_store_count:
        raise RuntimeError(
            "Unexpected structure-result count: "
            f"{len(structure_records)}"
        )

    if len(component_records) != expected_store_count:
        raise RuntimeError(
            "Unexpected component-result count: "
            f"{len(component_records)}"
        )

    if len(corruption_records) != expected_store_count:
        raise RuntimeError(
            "Unexpected corruption-result count: "
            f"{len(corruption_records)}"
        )

    structure_index = index_by_article_path(
        structure_records,
        source_name="structure results",
    )

    component_index = index_by_article_path(
        component_records,
        source_name="component results",
    )

    corruption_index = index_by_article_path(
        corruption_records,
        source_name="corruption results",
    )

    structure_paths = set(structure_index)
    component_paths = set(component_index)
    corruption_paths = set(corruption_index)

    if not (
        structure_paths
        == component_paths
        == corruption_paths
    ):
        raise RuntimeError(
            "Article path coverage differs between integrity stages."
        )

    consolidated_records: list[dict[str, Any]] = []

    for article_path in sorted(structure_paths):
        consolidated_records.append(
            build_consolidated_record(
                workspace_id=workspace_id,
                article_path=article_path,
                structure_record=structure_index[
                    article_path
                ],
                component_record=component_index[
                    article_path
                ],
                corruption_record=corruption_index[
                    article_path
                ],
            )
        )

    pass_records = [
        record
        for record in consolidated_records
        if record["overall_status"] == "PASS"
    ]

    failed_records = [
        record
        for record in consolidated_records
        if record["overall_status"] == "FAIL"
    ]

    source_record_ids = [
        record["source_record_id"]
        for record in consolidated_records
    ]

    if len(set(source_record_ids)) != len(
        source_record_ids
    ):
        raise RuntimeError(
            "Duplicate source identities exist in the "
            "consolidated integrity ledger."
        )

    structure_fail_count = sum(
        record["stage_statuses"]["structure"] == "FAIL"
        for record in consolidated_records
    )

    component_fail_count = sum(
        record["stage_statuses"]["components"] == "FAIL"
        for record in consolidated_records
    )

    corruption_fail_count = sum(
        record["stage_statuses"][
            "corruption_truncation"
        ]
        == "FAIL"
        for record in consolidated_records
    )

    output_root = (
        integrity_root
        / "report"
    )

    ledger_path = (
        output_root
        / "website_integrity_ledger.jsonl"
    )

    failures_path = (
        output_root
        / "website_integrity_failures.jsonl"
    )

    report_json_path = (
        output_root
        / "website_integrity_report.json"
    )

    report_html_path = (
        output_root
        / "website_integrity_report.html"
    )

    index_html_path = (
        output_root
        / "index.html"
    )

    source_artifacts = {
        source_name: {
            "path": str(source_path),
            "sha256": sha256_file(source_path),
        }
        for source_name, source_path in required_sources.items()
    }

    generated_at = utc_now()

    report_seed = (
        workspace_id
        + "|"
        + "|".join(
            artifact["sha256"]
            for artifact in source_artifacts.values()
        )
    )

    report_id = (
        "website_integrity_report_"
        + hashlib.sha256(
            report_seed.encode("utf-8")
        ).hexdigest()[:24]
    )

    report: dict[str, Any] = {
        "schema_version": "1.0",
        "report_id": report_id,
        "report_version": REPORT_VERSION,
        "phase": PHASE,
        "phase_name": PHASE_NAME,
        "workspace_id": workspace_id,
        "generated_at": generated_at,
        "report_status": "COMPLETE",
        "integrity_outcome": (
            "COMPLETE_WITH_FAILURES"
            if failed_records
            else "COMPLETE_NO_FAILURES"
        ),
        "certification_status": "NOT_YET_CERTIFIED",
        "quarantine_status": "NOT_YET_EXECUTED",
        "source_store": "UDARE Store",
        "source_artifacts": source_artifacts,
        "summary": {
            "expected_upstream_count": expected_upstream_count,
            "deferred_upstream_count": deferred_upstream_count,
            "stored_article_count": expected_store_count,
            "articles_assessed": len(
                consolidated_records
            ),
            "overall_pass_count": len(pass_records),
            "overall_fail_count": len(failed_records),
            "structure_fail_count": structure_fail_count,
            "component_fail_count": component_fail_count,
            "corruption_truncation_fail_count": (
                corruption_fail_count
            ),
            "distinct_failed_article_count": len(
                failed_records
            ),
            "quarantine_candidate_count": len(
                failed_records
            ),
            "quarantine_executed": False,
        },
        "failed_articles": failed_records,
        "output_artifacts": {
            "ledger": str(ledger_path),
            "failures": str(failures_path),
            "json_report": str(report_json_path),
            "html_report": str(report_html_path),
            "browser_index": str(index_html_path),
        },
        "important_notes": [
            (
                "Three upstream pages absent from the UDARE Store "
                "remain deferred and are not counted as integrity "
                "failures."
            ),
            (
                "No article has been quarantined during this report "
                "generation phase."
            ),
            (
                "The same article may fail more than one validation "
                "stage but is counted once in the overall failed "
                "article total."
            ),
        ],
    }

    write_jsonl(
        ledger_path,
        consolidated_records,
    )

    write_jsonl(
        failures_path,
        failed_records,
    )

    atomic_write_json(
        report_json_path,
        report,
    )

    html_report = render_html_report(
        report=report,
        records=consolidated_records,
    )

    atomic_write_text(
        report_html_path,
        html_report,
    )

    atomic_write_text(
        index_html_path,
        html_report,
    )

    return report
