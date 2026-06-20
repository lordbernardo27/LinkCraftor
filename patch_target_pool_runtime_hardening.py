from pathlib import Path

# ============================================================
# PATCH A/B/D: live_domain_target_pool contamination hardening
# ============================================================
p = Path("backend/server/pools/target_pools/live_domain_target_pool.py")
s = p.read_text(encoding="utf-8")

backup = p.with_suffix(".py.bak_target_pool_hardening")
backup.write_text(s, encoding="utf-8")

old1 = '''        # Do not store very weak accidental matches.
        if phrase_score < 0.45:
            continue
'''

new1 = '''        # Do not store weak accidental matches.
        # Target-pool phrase memory must require strong, multi-token evidence.
        if phrase_score < 0.75:
            continue

        if len(overlap) < 2:
            continue
'''

if old1 not in s:
    raise SystemExit("Patch A marker not found")
s = s.replace(old1, new1, 1)


old2 = '''        "aliases": [x["phrase"] for x in top],'''
new2 = '''        # Do not manufacture aliases from historical phrase matches.
        "aliases": [],'''

if old2 not in s:
    raise SystemExit("Patch B marker not found")
s = s.replace(old2, new2, 1)


old3 = '''            if priority_match_count > 0:
                priority_scored_urls.append((priority_score, priority_match_count, u))
                continue
'''

new3 = '''            if priority_match_count >= 2:
                priority_scored_urls.append((priority_score, priority_match_count, u))
                continue
'''

if old3 not in s:
    raise SystemExit("Patch D1 marker not found")
s = s.replace(old3, new3, 1)


old4 = '''            if secondary_match_count > 0:
                secondary_scored_urls.append((secondary_score, secondary_match_count, u))
            elif u in active_live_domain_url_set:
                filler_urls.append(u)
'''

new4 = '''            if secondary_match_count >= 2:
                secondary_scored_urls.append((secondary_score, secondary_match_count, u))
            elif u in active_live_domain_url_set:
                filler_urls.append(u)
'''

if old4 not in s:
    raise SystemExit("Patch D2 marker not found")
s = s.replace(old4, new4, 1)

p.write_text(s, encoding="utf-8")

print("✅ live_domain_target_pool hardening applied.")
print(f"Backup created: {backup}")


# ============================================================
# PATCH C: engine_run runtime bypass hardening
# ============================================================
p2 = Path("backend/server/routes/engine_run.py")
s2 = p2.read_text(encoding="utf-8")

backup2 = p2.with_suffix(".py.bak_runtime_filter_hardening")
backup2.write_text(s2, encoding="utf-8")

old5 = '''    if source_type == "live_domain" and (
        bool(target.get("target_pool_phrase_exact_match"))
        or bool(target.get("target_pool_phrase_contains_match"))
        or int(target.get("target_pool_active_phrase_matches") or 0) >= 2
        or str(target.get("resolver_reason") or "") == "phrase_aware_target_pool_match"
    ):
        return True
'''

new5 = '''    if source_type == "live_domain" and (
        bool(target.get("target_pool_phrase_exact_match"))
        or bool(target.get("target_pool_phrase_contains_match"))
    ):
        return True
'''

if old5 not in s2:
    raise SystemExit("Patch C marker not found")
s2 = s2.replace(old5, new5, 1)

p2.write_text(s2, encoding="utf-8")

print("✅ engine_run runtime filter hardening applied.")
print(f"Backup created: {backup2}")
