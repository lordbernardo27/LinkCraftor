from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path("backend/server/data")

GENERATED_TARGETS = [
    ROOT / "uploaded_document_unified_content",
    ROOT / "universal_unified_content_documents",
    ROOT / "universal_article_body_store",
    ROOT / "uucd_body_store_certifications",
    ROOT / "runtime" / "automatic_rebuild_reports",
]

PRESERVED_TARGETS = [
    ROOT / "docs",
    ROOT / "workspaces",
    ROOT / "raw_website_html",
    ROOT / "website_unified_content",
    ROOT / "site_pages_ws_whattoexpect_com.json",
    ROOT / "site_sources_ws_whattoexpect_com.json",
    ROOT / "source_lifecycle_controls",
    ROOT / "source_asset_versions",
]


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def clear_generated_environment() -> Dict[str, Any]:
    cleared = []
    missing = []

    for target in GENERATED_TARGETS:
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.unlink()
            cleared.append(str(target))
        else:
            target.mkdir(parents=True, exist_ok=True)
            missing.append(str(target))

    preserved = [str(p) for p in PRESERVED_TARGETS if p.exists()]

    return {
        "cleared_generated_targets": cleared,
        "created_missing_generated_targets": missing,
        "preserved_authoritative_targets": preserved,
    }


def run_canonical_environment_rebuild(workspace_id: str) -> Dict[str, Any]:
    raise RuntimeError(
        "Canonical environment rebuild execution is retired pending the fresh runtime implementation."
    )


if __name__ == "__main__":
    workspace_id = "ws_whattoexpect_com"
    result = run_canonical_environment_rebuild(workspace_id)
    rebuild = result["rebuild"]

    print("CANONICAL ENVIRONMENT REBUILD COMPLETE")
    print("Workspace:", result["workspace_id"])
    print("Generated targets cleared:", len(result["reset"]["cleared_generated_targets"]))
    print("Authoritative targets preserved:", len(result["reset"]["preserved_authoritative_targets"]))
    print("Website documents found:", rebuild.get("website_documents_found"))
    print("Uploaded documents found:", rebuild.get("uploaded_documents_found"))
    print("Total UUCD documents:", rebuild.get("total_uucd_documents"))
    print("Bodies written:", rebuild.get("bodies_written"))
    print("Duplicate hashes:", rebuild.get("duplicate_hashes"))
    print("Certified:", rebuild.get("certified"))
    print("Semantic ready:", rebuild.get("semantic_ready"))
    print("Certification level:", rebuild.get("certification_level"))
    print("Problems:", rebuild.get("certification_problems", [])[:10])
    print("Next stage:", result["next_stage"])
    print("Report:", result["report_path"])
