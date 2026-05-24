from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

old = '''UNIVERSAL_VERB_LIKE: Set[str] = ACTION_STARTS.union({
    "convert", "predict", "detect", "pinpoint", "refine", "survive",
    "change", "move", "make", "take", "get", "give", "use", "find",
    "show", "see", "know", "start", "stop", "open", "close",
})
'''

new = '''UNIVERSAL_VERB_LIKE: Set[str] = ACTION_STARTS.union({
    "convert", "predict", "detect", "pinpoint", "refine", "survive",
    "change", "move", "make", "take", "get", "give", "use", "find",
    "show", "see", "know", "start", "stop", "open", "close",
    "hit", "mark", "say", "says", "said", "tell", "tells", "told",
    "mean", "means", "depend", "depends", "happen", "happens",
})
'''

if old in s:
    s = s.replace(old, new, 1)

helper_old = '''    # Pattern 7: incomplete four-token semantic window ending in adjective-like token.
    # Examples: "egg white cervical" type partial modifier stack.
    if n == 3 and tokens[-1] in UNIVERSAL_ADJECTIVE_LIKE and not _has_valid_ordered_pair(tokens):
        return True

    return False
'''

helper_new = '''    # Pattern 7: incomplete semantic window ending in adjective-like token.
    if n == 3 and tokens[-1] in UNIVERSAL_ADJECTIVE_LIKE and not _has_valid_ordered_pair(tokens):
        return True

    # Pattern 8: subject/object + verb leakage.
    # Examples: "calendar method says fertility", "know the average length".
    if any(t in UNIVERSAL_VERB_LIKE for t in tokens):
        verb_positions = [i for i, t in enumerate(tokens) if t in UNIVERSAL_VERB_LIKE]
        for idx in verb_positions:
            if idx > 0 and idx < n - 1:
                return True
            if idx == 0 and n >= 3 and tokens[1] in {"the", "a", "an", "single", "average"}:
                return True

    # Pattern 9: action + weak quantity/object window.
    # Examples: "mark the five days", "hit single exact day".
    if n >= 3 and tokens[0] in UNIVERSAL_VERB_LIKE:
        if any(t in {"day", "days", "length", "time", "date"} for t in tokens[1:]):
            return True

    return False
'''

if helper_old not in s:
    raise SystemExit("helper target block not found")

s = s.replace(helper_old, helper_new, 1)

p.write_text(s, encoding="utf-8")
print("patched universal verb-leak fragment guards")
