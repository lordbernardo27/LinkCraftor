from pathlib import Path

p = Path("backend/server/engine/intelligence_target_resolver.py")
s = p.read_text(encoding="utf-8")

backup = p.with_suffix(".py.bak_resolver_contamination_fix")
backup.write_text(s, encoding="utf-8")

old1 = '''            phrase_evidence = _phrase_evidence_score(
                anchor_phrase,
                target_text_for_concepts,
                universal_aliases + resolver_aliases,
            )
'''

new1 = '''            # IMPORTANT:
            # Phrase evidence must be computed from real target surface text only.
            # Do NOT include target matched_phrases, aliases, or resolver-generated aliases here.
            # Those can contaminate evidence and make unrelated URLs look like exact matches.
            phrase_evidence = _phrase_evidence_score(
                anchor_phrase,
                target_text_for_concepts,
                [],
            )
'''

if old1 not in s:
    raise SystemExit("Patch 1 marker not found: phrase_evidence block")
s = s.replace(old1, new1, 1)


old2 = '''        phrase_aware_guard_pass = bool(
            str(item.get("source_type") or "") == "live_domain"
            and (
                bool(item.get("target_pool_phrase_exact_match"))
                or bool(item.get("target_pool_phrase_contains_match"))
                or int(item.get("target_pool_active_phrase_matches") or 0) >= 2
            )
        )
'''

new2 = '''        phrase_aware_guard_pass = bool(
            str(item.get("source_type") or "") == "live_domain"
            and (
                bool(item.get("target_pool_phrase_exact_match"))
                or bool(item.get("target_pool_phrase_contains_match"))
            )
        )
'''

if old2 not in s:
    raise SystemExit("Patch 2 marker not found: phrase_aware_guard_pass block")
s = s.replace(old2, new2, 1)


old3 = '''            phrase_aware_count = int(target.get("active_phrase_matches") or 0)

            anchor_norm = _norm_text(anchor_phrase)
'''

new3 = '''            phrase_aware_count = int(target.get("active_phrase_matches") or 0)

            if phrase_aware_count:
                try:
                    print(
                        "[RESOLVER_TARGET_POOL_DEBUG]",
                        "phrase=", str(anchor_phrase or "")[:90],
                        "title=", str(title or "")[:90],
                        "active_phrase_matches=", phrase_aware_count,
                        "matched_sample=", phrase_aware_matches[:5],
                    )
                except Exception:
                    pass

            anchor_norm = _norm_text(anchor_phrase)
'''

if old3 not in s:
    raise SystemExit("Patch 3 marker not found: phrase_aware_count block")
s = s.replace(old3, new3, 1)


p.write_text(s, encoding="utf-8")

print("✅ Resolver contamination patch applied.")
print(f"Backup created: {backup}")
