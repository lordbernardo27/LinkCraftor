from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

needle = '''    p = canonical_phrase(phrase)
    tokens = tokenize(p)

    def hard_reject(reason: str) -> Dict[str, Any]:
'''

insert = '''    p = canonical_phrase(phrase)
    tokens = tokenize(p)

    def hard_reject(reason: str) -> Dict[str, Any]:
'''

# Add after hard_reject function block, because hard_reject must exist before use.
target = '''        )

    if not p or len(tokens) < 2:
'''

replacement = '''        )

    if _is_universal_semantic_fragment_pattern(tokens):
        return hard_reject("universal_semantic_fragment_pattern")

    if not p or len(tokens) < 2:
'''

if "_is_universal_semantic_fragment_pattern(tokens)" not in s[s.find("def score_phrase_strength("):]:
    if target not in s:
        raise SystemExit("target after hard_reject not found")
    s = s.replace(target, replacement, 1)

p.write_text(s, encoding="utf-8")
print("wired universal semantic fragment helper into score_phrase_strength")
