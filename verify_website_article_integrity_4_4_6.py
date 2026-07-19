"""Verification for Phase 4.4.6 Website Article Integrity certification."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_ROOT = PROJECT_ROOT / "backend" / "server"

if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(SERVER_ROOT),
    )

from integrity.website_article_integrity.website_article_integrity_certifier import (  # noqa: E402
    certify_website_article_integrity,
)


WORKSPACE_ID = "ws_whattoexpect_com"

EXPECTED_UPSTREAM_COUNT = 2225
EXPECTED_ASSESSED_COUNT = 2222
EXPECTED_ACTIVE_COUNT = 2219
EXPECTED_QUARANTINE_COUNT = 3
DEFERRED_UPSTREAM_COUNT = 3

EXPECTED_QUARANTINED_SOURCE_IDS = {
    "raw_html_fc8c43c9937f0809",
    "raw_html_14533594924ea9c1",
    "raw_html_98f22e0c526ac925",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def directory_fingerprint(
    root: Path,
    patterns: tuple[str, ...],
) -> str:
    digest = hashlib.sha256()

    paths: list[Path] = []

    for pattern in patterns:
        paths.extend(
            path
            for path in root.rglob(pattern)
            if path.is_file()
        )

    for path in sorted(
        set(paths),
        key=lambda item: item.as_posix(),
    ):
        relative_path = path.relative_to(
            root
        ).as_posix()

        digest.update(
            relative_path.encode("utf-8")
        )
        digest.update(b"\x00")
        digest.update(
            sha256_file(path).encode("ascii")
        )
        digest.update(b"\n")

    return digest.hexdigest()


def load_json(path: Path) -> dict:
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


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []

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
                    f"Invalid JSONL line {line_number}: {exc}"
                ) from exc

            if not isinstance(value, dict):
                raise RuntimeError(
                    f"Expected object at line {line_number}."
                )

            records.append(value)

    return records


def calculate_evidence_root(
    artifacts: dict[str, dict[str, str]],
) -> str:
    digest = hashlib.sha256()

    for name in sorted(artifacts):
        digest.update(
            name.encode("utf-8")
        )
        digest.update(b"\x00")
        digest.update(
            artifacts[name]["sha256"].encode("ascii")
        )
        digest.update(b"\n")

    return digest.hexdigest()


def main() -> int:
    print()
    print("=" * 78)
    print(
        "PHASE 4.4.6 — WEBSITE ARTICLE INTEGRITY CERTIFICATION"
    )
    print("=" * 78)

    data_root = (
        PROJECT_ROOT
        / "backend"
        / "server"
        / "data"
    )

    udare_root = (
        data_root
        / "udare_store"
        / WORKSPACE_ID
    )

    integrity_root = (
        data_root
        / "website_article_integrity"
        / WORKSPACE_ID
    )

    quarantine_root = (
        integrity_root
        / "quarantine"
    )

    report_root = (
        integrity_root
        / "report"
    )

    certification_root = (
        integrity_root
        / "certification"
    )

    active_fingerprint_before = directory_fingerprint(
        udare_root,
        (
            "articles/*.html",
            "metadata/*.json",
        ),
    )

    quarantine_fingerprint_before = directory_fingerprint(
        quarantine_root,
        (
            "articles/*.html",
            "metadata/*.json",
        ),
    )

    protected_evidence_paths = {
        "report_json": (
            report_root
            / "website_integrity_report.json"
        ),
        "report_html": (
            report_root
            / "website_integrity_report.html"
        ),
        "report_ledger": (
            report_root
            / "website_integrity_ledger.jsonl"
        ),
        "report_failures": (
            report_root
            / "website_integrity_failures.jsonl"
        ),
        "quarantine_manifest": (
            quarantine_root
            / "manifests"
            / "quarantine_manifest.json"
        ),
        "quarantine_records": (
            quarantine_root
            / "quarantine_records.jsonl"
        ),
        "quarantine_execution": (
            quarantine_root
            / "quarantine_execution.json"
        ),
    }

    protected_hashes_before = {
        name: sha256_file(path)
        for name, path in protected_evidence_paths.items()
    }

    certificate = certify_website_article_integrity(
        project_root=PROJECT_ROOT,
        workspace_id=WORKSPACE_ID,
        expected_upstream_count=EXPECTED_UPSTREAM_COUNT,
        expected_assessed_count=EXPECTED_ASSESSED_COUNT,
        expected_active_count=EXPECTED_ACTIVE_COUNT,
        expected_quarantine_count=EXPECTED_QUARANTINE_COUNT,
        deferred_upstream_count=DEFERRED_UPSTREAM_COUNT,
    )

    active_fingerprint_after = directory_fingerprint(
        udare_root,
        (
            "articles/*.html",
            "metadata/*.json",
        ),
    )

    quarantine_fingerprint_after = directory_fingerprint(
        quarantine_root,
        (
            "articles/*.html",
            "metadata/*.json",
        ),
    )

    protected_hashes_after = {
        name: sha256_file(path)
        for name, path in protected_evidence_paths.items()
    }

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

    evidence_manifest_path = (
        certification_root
        / "certification_evidence_manifest.json"
    )

    active_ledger_path = (
        certification_root
        / "certified_active_articles.jsonl"
    )

    quarantine_ledger_path = (
        certification_root
        / "certified_quarantine_records.jsonl"
    )

    udare_manifest_path = (
        udare_root
        / "manifests"
        / "udare_store_manifest.json"
    )

    failures: list[str] = []

    required_outputs = (
        certificate_json_path,
        certificate_html_path,
        certification_index_path,
        evidence_manifest_path,
        active_ledger_path,
        quarantine_ledger_path,
    )

    for path in required_outputs:
        if not path.is_file():
            failures.append(
                f"Required certification artifact missing: {path}"
            )

    if active_fingerprint_before != active_fingerprint_after:
        failures.append(
            "One or more active UDARE article or metadata files "
            "changed during certification."
        )

    if (
        quarantine_fingerprint_before
        != quarantine_fingerprint_after
    ):
        failures.append(
            "One or more quarantine article or metadata files "
            "changed during certification."
        )

    if protected_hashes_before != protected_hashes_after:
        failures.append(
            "A protected report or quarantine evidence artifact "
            "changed during certification."
        )

    stored_certificate = (
        load_json(
            certificate_json_path
        )
        if certificate_json_path.is_file()
        else {}
    )

    evidence_manifest = (
        load_json(
            evidence_manifest_path
        )
        if evidence_manifest_path.is_file()
        else {}
    )

    active_records = (
        load_jsonl(
            active_ledger_path
        )
        if active_ledger_path.is_file()
        else []
    )

    quarantine_records = (
        load_jsonl(
            quarantine_ledger_path
        )
        if quarantine_ledger_path.is_file()
        else []
    )

    if (
        stored_certificate.get(
            "certification_status"
        )
        != "CERTIFIED"
    ):
        failures.append(
            "Certification status is not CERTIFIED."
        )

    if (
        stored_certificate.get(
            "certification_scope"
        )
        != "ACTIVE_UDARE_STORE"
    ):
        failures.append(
            "Certification scope is incorrect."
        )

    if (
        stored_certificate.get(
            "qualification"
        )
        != "WITH_DEFERRED_UPSTREAM_RECORDS"
    ):
        failures.append(
            "Certification qualification is incorrect."
        )

    coverage = stored_certificate.get(
        "coverage",
        {},
    )

    expected_coverage = {
        "expected_upstream_count": 2225,
        "articles_assessed": 2222,
        "active_certified_count": 2219,
        "quarantined_count": 3,
        "deferred_upstream_count": 3,
        "coverage_reconciliation": 2225,
    }

    for field, expected_value in expected_coverage.items():
        if coverage.get(field) != expected_value:
            failures.append(
                f"Certificate coverage field {field} is "
                f"not {expected_value}."
            )

    if len(active_records) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Certified active ledger does not contain 2,219 records."
        )

    if len(quarantine_records) != EXPECTED_QUARANTINE_COUNT:
        failures.append(
            "Certified quarantine ledger does not contain "
            "three records."
        )

    active_source_ids = {
        record.get("source_record_id")
        for record in active_records
    }

    quarantine_source_ids = {
        record.get("source_record_id")
        for record in quarantine_records
    }

    if len(active_source_ids) != EXPECTED_ACTIVE_COUNT:
        failures.append(
            "Certified active source identities are not unique."
        )

    if (
        quarantine_source_ids
        != EXPECTED_QUARANTINED_SOURCE_IDS
    ):
        failures.append(
            "Certified quarantine source set is incorrect."
        )

    if active_source_ids & quarantine_source_ids:
        failures.append(
            "Active and quarantine certification scopes overlap."
        )

    evidence_artifacts = evidence_manifest.get(
        "artifacts",
        {},
    )

    if not isinstance(evidence_artifacts, dict):
        failures.append(
            "Evidence artifact manifest is invalid."
        )
    else:
        for name, artifact in evidence_artifacts.items():
            path_value = artifact.get("path")
            expected_hash = artifact.get("sha256")

            if not isinstance(path_value, str):
                failures.append(
                    f"Evidence path is invalid for {name}."
                )
                continue

            evidence_path = Path(path_value)

            if not evidence_path.is_file():
                failures.append(
                    f"Evidence artifact is missing: {evidence_path}"
                )
                continue

            actual_hash = sha256_file(
                evidence_path
            )

            if actual_hash != expected_hash:
                failures.append(
                    f"Evidence hash mismatch for {name}."
                )

        recalculated_root = calculate_evidence_root(
            evidence_artifacts
        )

        if (
            recalculated_root
            != evidence_manifest.get(
                "evidence_root_sha256"
            )
        ):
            failures.append(
                "Evidence root hash is invalid."
            )

        if (
            recalculated_root
            != stored_certificate.get(
                "evidence_root_sha256"
            )
        ):
            failures.append(
                "Certificate evidence seal does not match "
                "the evidence manifest."
            )

    if udare_manifest_path.is_file():
        udare_manifest = load_json(
            udare_manifest_path
        )

        certification_state = udare_manifest.get(
            "website_article_integrity_certification",
            {},
        )

        if (
            certification_state.get("status")
            != "CERTIFIED"
        ):
            failures.append(
                "UDARE manifest certification status is not "
                "CERTIFIED."
            )

        if (
            certification_state.get("certificate_id")
            != stored_certificate.get("certificate_id")
        ):
            failures.append(
                "UDARE manifest certificate ID does not match "
                "the certificate."
            )

        if (
            certification_state.get(
                "active_certified_count"
            )
            != 2219
        ):
            failures.append(
                "UDARE manifest certified active count is "
                "not 2,219."
            )

        if (
            certification_state.get(
                "quarantined_count"
            )
            != 3
        ):
            failures.append(
                "UDARE manifest quarantined count is not three."
            )

        if (
            certification_state.get(
                "deferred_upstream_count"
            )
            != 3
        ):
            failures.append(
                "UDARE manifest deferred count is not three."
            )

    if certificate_html_path.is_file():
        certificate_html = certificate_html_path.read_text(
            encoding="utf-8",
        )

        if "CERTIFIED" not in certificate_html:
            failures.append(
                "HTML certificate does not display CERTIFIED."
            )

        for source_id in EXPECTED_QUARANTINED_SOURCE_IDS:
            if source_id not in certificate_html:
                failures.append(
                    "HTML certificate does not contain quarantine "
                    f"identity: {source_id}"
                )

    if (
        certificate_json_path.is_file()
        and certification_index_path.is_file()
        and certificate_html_path.is_file()
    ):
        if (
            sha256_file(certificate_html_path)
            != sha256_file(certification_index_path)
        ):
            failures.append(
                "Certification browser index does not match "
                "the HTML certificate."
            )

    print()
    print(
        f"Certificate status:             "
        f"{stored_certificate.get('certification_status')}"
    )
    print(
        f"Certificate ID:                 "
        f"{stored_certificate.get('certificate_id')}"
    )
    print(
        f"Articles assessed:              "
        f"{coverage.get('articles_assessed')}"
    )
    print(
        f"Active articles certified:      "
        f"{coverage.get('active_certified_count')}"
    )
    print(
        f"Quarantined records preserved:  "
        f"{coverage.get('quarantined_count')}"
    )
    print(
        f"Deferred upstream pages:        "
        f"{coverage.get('deferred_upstream_count')}"
    )
    print(
        f"Evidence seal:                  "
        f"{stored_certificate.get('evidence_root_sha256')}"
    )

    print()
    print(
        f"Certificate JSON: {certificate_json_path}"
    )
    print(
        f"Certificate HTML: {certificate_html_path}"
    )
    print(
        f"Browser index:    {certification_index_path}"
    )
    print(
        f"Evidence manifest: {evidence_manifest_path}"
    )
    print()

    if failures:
        print("PHASE 4.4.6 VERIFICATION: FAIL")

        for failure in failures:
            print(f"  - {failure}")

        print("=" * 78)
        return 1

    print("PHASE 4.4.6 VERIFICATION: PASS")
    print(
        "Website Article Integrity is certified for the "
        "2,219 active PASS articles."
    )
    print(
        "All three failed article and metadata pairs remain "
        "preserved in reversible quarantine."
    )
    print(
        "The three deferred upstream pages are explicitly "
        "outside the certification scope."
    )
    print(
        "No active or quarantined article or metadata file "
        "was modified during certification."
    )
    print("=" * 78)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
