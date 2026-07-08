from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path("backend/server")
DATA = ROOT / "data"

RESET_TARGETS = [
    DATA / "uploaded_document_unified_content",
    DATA / "universal_unified_content_documents",
    DATA / "universal_article_body_store",
    DATA / "uucd_body_store_certifications",
]

PRESERVE_TARGETS = [
    DATA / "docs",
    DATA / "uploads",
    DATA / "raw_website_html",
    DATA / "clean_website_html",
    DATA / "website_unified_content",
    DATA / "source_lifecycle_controls",
    DATA / "source_purge_ledgers",
    DATA / "source_lifecycle_registry",
    DATA / "source_asset_versions",
]


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    stamp = timestamp()
    archive_root = DATA / "_canonical_reset_archives" / f"canonical_reset_{stamp}"
    archive_root.mkdir(parents=True, exist_ok=True)

    report = {
        "reset_name": f"canonical_reset_{stamp}",
        "mode": "archive_then_clear_generated_canonical_outputs",
        "archived": [],
        "cleared": [],
        "preserved": [],
        "missing_reset_targets": [],
        "missing_preserve_targets": [],
        "rules": {
            "delete_original_uploads": False,
            "delete_raw_html": False,
            "delete_clean_html": False,
            "delete_website_unified_content": False,
            "delete_lifecycle_records": False,
            "delete_generated_uduc": True,
            "delete_generated_uucd": True,
            "delete_generated_body_store": True,
            "delete_generated_certifications": True,
        },
    }

    for p in PRESERVE_TARGETS:
        if p.exists():
            report["preserved"].append(str(p))
        else:
            report["missing_preserve_targets"].append(str(p))

    for p in RESET_TARGETS:
        if not p.exists():
            report["missing_reset_targets"].append(str(p))
            continue

        archive_dest = archive_root / p.name
        shutil.copytree(p, archive_dest, dirs_exist_ok=True)
        report["archived"].append({
            "source": str(p),
            "archive": str(archive_dest),
        })

        shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)
        report["cleared"].append(str(p))

    report_path = archive_root / "canonical_reset_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("6J SAFE CANONICAL RESET COMPLETE")
    print("Archive:", archive_root)
    print("Report:", report_path)
    print("Cleared generated stores:")
    for item in report["cleared"]:
        print("-", item)
    print("Original source stores preserved.")


if __name__ == "__main__":
    main()
