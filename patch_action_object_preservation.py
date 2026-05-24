from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

old = '''    # Pattern 10: short narrative verb fragment.
    # Examples: "clinic gave", "explore further".
    if n <= 3 and any(t in UNIVERSAL_VERB_LIKE for t in tokens):
        if not _has_valid_ordered_pair(tokens):
            return True
'''

new = '''    # Pattern 10: short narrative verb fragment.
    # Examples: "clinic gave", "explore further".
    if n <= 3 and any(t in UNIVERSAL_VERB_LIKE for t in tokens):

        # Preserve clean action-object anchors.
        # Examples:
        # "calculate ovulation"
        # "measure bmi"
        # "track fertility"
        if (
            n == 2
            and tokens[0] in ACTION_STARTS
            and tokens[1] not in UNIVERSAL_DANGLING_TAILS
            and tokens[1] not in {"further", "more", "again", "later"}
        ):
            pass
        else:
            if not _has_valid_ordered_pair(tokens):
                return True
'''

if old not in s:
    raise SystemExit("old Pattern 10 block not found")

s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("patched action-object preservation")
