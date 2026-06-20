from pathlib import Path

p = Path("backend/server/engine/intelligence_target_resolver.py")
s = p.read_text(encoding="utf-8")

backup = p.with_suffix(".py.bak_literal_phrase_evidence")
backup.write_text(s, encoding="utf-8")

old = '''    anchor_tokens = _expanded_meaningful_tokens(anchor_norm)
    target_tokens = _expanded_meaningful_tokens(" ".join([target_norm] + alias_texts))
'''

new = '''    # Phrase evidence must be literal, not semantic.
    # Semantic expansion belongs in concept alignment / alias / intent layers.
    # This prevents "begins" matching unrelated "starting preschool" pages.
    anchor_tokens = _meaningful_tokens(anchor_norm)
    target_tokens = _meaningful_tokens(target_norm)
'''

if old not in s:
    raise SystemExit("Literal phrase evidence marker not found")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")

print("✅ Literal phrase evidence patch applied.")
print(f"Backup created: {backup}")
