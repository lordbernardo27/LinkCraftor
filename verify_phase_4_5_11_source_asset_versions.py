import json
from pathlib import Path
from collections import Counter


WORKSPACE_ID = "ws_whattoexpect_com"

UUCD_PATH = Path(
    "backend/server/data/universal_unified_content_documents/"
    f"universal_unified_content_documents_{WORKSPACE_ID}.json"
)

ASSET_PATH = Path(
    "backend/server/data/source_asset_versions/"
    f"source_asset_versions_{WORKSPACE_ID}.json"
)


def fail(msg):
    raise AssertionError(msg)


def main():
    if not UUCD_PATH.exists():
        fail(f"Missing UUCD store: {UUCD_PATH}")

    if not ASSET_PATH.exists():
        fail(f"Missing source asset version registry: {ASSET_PATH}")

    uucd = json.loads(UUCD_PATH.read_text(encoding="utf-8"))
    registry = json.loads(ASSET_PATH.read_text(encoding="utf-8"))

    docs = uucd.get("documents", [])
    assets = registry.get("assets", [])

    if not docs:
        fail("UUCD has zero documents")

    if not assets:
        fail("Asset registry has zero assets")

    required_asset_fields = [
        "asset_id",
        "source_id",
        "workspace_id",
        "source_type",
        "connection_status",
        "uucd_status",
        "learning_status",
        "current_version",
        "current_snapshot_id",
        "current_snapshot_hash",
        "snapshots",
        "version_policy",
        "events",
    ]

    missing = []
    for asset in assets:
        for field in required_asset_fields:
            if field not in asset or asset.get(field) in ("", None, []):
                missing.append((asset.get("asset_id"), field))

    if missing:
        fail(f"Assets missing required fields: {missing[:20]}")

    asset_ids = [a.get("asset_id") for a in assets]
    duplicate_asset_ids = [
        aid for aid, count in Counter(asset_ids).items()
        if count > 1
    ]
    if duplicate_asset_ids:
        fail(f"Duplicate asset_id values: {duplicate_asset_ids[:20]}")

    tracked_doc_ids = set()

    for asset in assets:
        if asset.get("workspace_id") != WORKSPACE_ID:
            fail(f"Wrong workspace_id in asset: {asset.get('asset_id')}")

        snapshots = asset.get("snapshots", [])
        current = [
            s for s in snapshots
            if s.get("snapshot_id") == asset.get("current_snapshot_id")
            and s.get("status") == "current"
        ]

        if len(current) != 1:
            fail(f"Asset must have exactly one current snapshot: {asset.get('asset_id')}")

        current_snapshot = current[0]

        if current_snapshot.get("version") != asset.get("current_version"):
            fail(f"Current version mismatch: {asset.get('asset_id')}")

        fingerprints = current_snapshot.get("document_fingerprints", [])
        if current_snapshot.get("document_count") != len(fingerprints):
            fail(f"Snapshot document_count mismatch: {asset.get('asset_id')}")

        for fp in fingerprints:
            doc_id = fp.get("document_id")
            if not doc_id:
                fail(f"Fingerprint missing document_id: {asset.get('asset_id')}")
            tracked_doc_ids.add(doc_id)

    uucd_doc_ids = {d.get("document_id") for d in docs if d.get("document_id")}

    missing_from_assets = uucd_doc_ids - tracked_doc_ids
    if missing_from_assets:
        fail(f"UUCD documents not tracked in asset registry: {list(missing_from_assets)[:20]}")

    rules = registry.get("rules", {})
    required_rules = [
        "sources_are_versioned_assets",
        "snapshots_are_immutable",
        "current_snapshot_is_explicit",
        "changed_documents_are_detected_by_hash",
        "semantic_pipeline_should_process_only_current_usable_snapshots",
    ]

    bad_rules = [rule for rule in required_rules if rules.get(rule) is not True]
    if bad_rules:
        fail(f"Missing or false registry rules: {bad_rules}")

    print("PHASE 4.5.11 SOURCE ASSET VERSION VERIFICATION PASSED")
    print("asset_registry_path =", ASSET_PATH)
    print("assets =", len(assets))
    print("uucd_documents =", len(uucd_doc_ids))
    print("documents_tracked =", len(tracked_doc_ids))
    print("registry_counts =", registry.get("counts", {}))
    print("rules =", registry.get("rules", {}))


if __name__ == "__main__":
    main()
