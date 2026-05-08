import json, shutil
from pathlib import Path

ws = "ws_betterhealthcheck_com"
base = Path("backend/server/data/phrase_pools")
active = base / "active" / f"active_phrase_pool_{ws}.json"
backup = active.with_suffix(".backup_before_recovery.json")

if active.exists():
    shutil.copyfile(active, backup)

paths = {
    "upload": base / "upload" / f"upload_phrase_pool_{ws}.json",
    "draft": base / "draft" / f"draft_phrase_pool_{ws}.json",
    "imported": base / "imported" / f"imported_phrase_pool_{ws}.json",
    "live_domain": base / "live_domain" / f"live_domain_phrase_pool_{ws}.json",
}

merged = {}
counts = {}

for source, path in paths.items():
    obj = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    phrases = obj.get("phrases", {}) if isinstance(obj.get("phrases", {}), dict) else {}
    counts[source] = len(phrases)

    for phrase, rec in phrases.items():
        if isinstance(rec, dict) and str(phrase).strip():
            new_rec = dict(rec)
            new_rec.setdefault("pool_sources", [])
            if source not in new_rec["pool_sources"]:
                new_rec["pool_sources"].append(source)
            merged[str(phrase).strip()] = new_rec

out = {
    "workspace_id": ws,
    "type": "active_phrase_pool",
    "build": "RECOVERY_LIGHT_MERGE",
    "counts_by_source": counts,
    "phrase_count": len(merged),
    "phrases": merged,
}

active.parent.mkdir(parents=True, exist_ok=True)
active.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

print("RECOVERED_ACTIVE_PHRASE_COUNT=", len(merged))
print("BACKUP=", backup)
