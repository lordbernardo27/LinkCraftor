from pathlib import Path

s = Path("backend/server/pools/target_pools/live_domain_target_pool.py").read_text(encoding="utf-8")

checks = {
    "phrase_score < 0.75": "phrase_score < 0.75" in s,
    "len(overlap) < 2": "len(overlap) < 2" in s,
    "aliases empty": '"aliases": []' in s,
    "priority_match_count >= 2": "priority_match_count >= 2" in s,
    "secondary_match_count >= 2": "secondary_match_count >= 2" in s,
}

for k, v in checks.items():
    print(k, "=", v)
