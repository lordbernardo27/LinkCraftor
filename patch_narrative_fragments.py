from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

old = '''UNIVERSAL_VERB_LIKE: Set[str] = ACTION_STARTS.union({
    "convert", "predict", "detect", "pinpoint", "refine", "survive",
    "change", "move", "make", "take", "get", "give", "use", "find",
    "show", "see", "know", "start", "stop", "open", "close",
    "hit", "mark", "say", "says", "said", "tell", "tells", "told",
    "mean", "means", "depend", "depends", "happen", "happens",
})
'''

new = '''UNIVERSAL_VERB_LIKE: Set[str] = ACTION_STARTS.union({
    "convert", "predict", "detect", "pinpoint", "refine", "survive",
    "change", "move", "make", "take", "get", "give", "use", "find",
    "show", "see", "know", "start", "stop", "open", "close",
    "hit", "mark", "say", "says", "said", "tell", "tells", "told",
    "mean", "means", "depend", "depends", "happen", "happens",
    "feel", "feels", "gave", "give", "gives", "explore", "explores",
    "solve", "solves", "solving", "reveal", "reveals", "develop",
    "develops", "developing",
})
'''

if old in s:
    s = s.replace(old, new, 1)

target = '''    # Pattern 9: action + weak quantity/object window.
    # Examples: "mark the five days", "hit single exact day".
    if n >= 3 and tokens[0] in UNIVERSAL_VERB_LIKE:
        if any(t in {"day", "days", "length", "time", "date"} for t in tokens[1:]):
            return True

    return False
'''

replacement = '''    # Pattern 9: action + weak quantity/object window.
    # Examples: "mark the five days", "hit single exact day".
    if n >= 3 and tokens[0] in UNIVERSAL_VERB_LIKE:
        if any(t in {"day", "days", "length", "time", "date"} for t in tokens[1:]):
            return True

    # Pattern 10: short narrative verb fragment.
    # Examples: "clinic gave", "explore further".
    if n <= 3 and any(t in UNIVERSAL_VERB_LIKE for t in tokens):
        if not _has_valid_ordered_pair(tokens):
            return True

    # Pattern 11: "feel/feels like" narrative residue.
    # Examples: "due date feels like", "feel like solving small mystery".
    if "like" in tokens and any(t in {"feel", "feels"} for t in tokens):
        return True

    # Pattern 12: weak narrative ending.
    # Examples: "explore further", "continue further", "read more".
    if tokens[-1] in {"further", "more", "again", "later"} and n <= 4:
        return True

    return False
'''

if target not in s:
    raise SystemExit("target narrative block not found")

s = s.replace(target, replacement, 1)

p.write_text(s, encoding="utf-8")
print("patched universal narrative-fragment guards")
