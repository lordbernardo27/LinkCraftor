from pathlib import Path
from datetime import datetime

fp = Path("backend/server/data/target_pools/live_domain/live_domain_target_pool_ws_whattoexpect_com.json")

if not fp.exists():
    print("No target pool file found.")
else:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = fp.with_suffix(f".stale_before_rebuild_{stamp}.json")
    fp.rename(backup)
    print("✅ Stale target pool quarantined.")
    print("Backup:", backup)
