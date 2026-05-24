from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

needle = '''        )

    # Universal semantic-fragment suppressors.
'''

replacement = '''        )

    if _is_universal_semantic_fragment_pattern(tokens):
        return hard_reject("universal_semantic_fragment_pattern")

    # Universal semantic-fragment suppressors.
'''

if "_is_universal_semantic_fragment_pattern(tokens)" not in s[s.find("def score_phrase_strength("):]:
    if needle not in s:
        raise SystemExit("insertion point not found")
    s = s.replace(needle, replacement, 1)

p.write_text(s, encoding="utf-8")
print("wired universal semantic helper before weak_exact")
