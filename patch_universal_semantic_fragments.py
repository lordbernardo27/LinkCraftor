from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

insert_after = '''ACTION_STARTS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check",
    "measure", "estimate", "build", "create", "fix", "improve",
    "optimize", "reduce", "increase", "manage", "review", "audit",
    "forecast", "plan", "analyze", "monitor", "test", "rank",
    "score", "calculate", "publish", "import", "export", "sync", "validate",
    "prevent", "protect", "design", "write", "stopping",
}
'''

new_block = '''ACTION_STARTS: Set[str] = {
    "calculate", "track", "confirm", "compare", "choose", "check",
    "measure", "estimate", "build", "create", "fix", "improve",
    "optimize", "reduce", "increase", "manage", "review", "audit",
    "forecast", "plan", "analyze", "monitor", "test", "rank",
    "score", "calculate", "publish", "import", "export", "sync", "validate",
    "prevent", "protect", "design", "write", "stopping",
}

UNIVERSAL_DANGLING_TAILS: Set[str] = {
    "each", "rough", "general", "basic", "simple", "specific", "certain",
    "particular", "same", "different", "various", "more", "less", "better",
    "best", "good", "bad", "clear", "important", "useful", "helpful",
}

UNIVERSAL_VAGUE_OBJECTS: Set[str] = {
    "surge", "thing", "things", "way", "ways", "part", "parts", "area",
    "areas", "point", "points", "one", "ones", "case", "cases",
}

UNIVERSAL_ADJECTIVE_LIKE: Set[str] = {
    "more", "less", "most", "least", "slippery", "stretchy", "rough",
    "fastest", "quickest", "slowest", "better", "best", "good", "bad",
    "clear", "simple", "basic", "general", "specific", "useful",
    "helpful", "important", "personalized", "customized", "traditional",
    "healthy", "safe", "unsafe", "strong", "weak", "early", "late",
}

UNIVERSAL_PREPOSITION_TOKENS: Set[str] = {
    "to", "into", "from", "with", "without", "during", "before", "after",
    "over", "under", "through", "around", "between", "among",
}

UNIVERSAL_VERB_LIKE: Set[str] = ACTION_STARTS.union({
    "convert", "predict", "detect", "pinpoint", "refine", "survive",
    "change", "move", "make", "take", "get", "give", "use", "find",
    "show", "see", "know", "start", "stop", "open", "close",
})
'''

if "UNIVERSAL_DANGLING_TAILS" not in s:
    if insert_after not in s:
        raise SystemExit("ACTION_STARTS block not found")
    s = s.replace(insert_after, new_block, 1)

helper_marker = "\ndef score_phrase_strength("
helper_block = '''

def _is_universal_semantic_fragment_pattern(tokens: List[str]) -> bool:
    if not tokens:
        return True

    n = len(tokens)

    # Pattern 1: adjective/adverb collision with no real head.
    # Examples: "more stretchy", "slippery stretchy".
    if n == 2 and all(t in UNIVERSAL_ADJECTIVE_LIKE for t in tokens):
        return True

    # Pattern 2: dangling determiner/quantifier/tail.
    # Examples: "temperature each", "rough each".
    if tokens[-1] in UNIVERSAL_DANGLING_TAILS and tokens[-1] not in STRONG_CONCEPT_HEADS:
        return True

    # Pattern 3: noun/acronym + to + verb/object fragment.
    # Examples: "opks to predict", "tools to convert".
    if n <= 4 and "to" in tokens[1:-1]:
        idx = tokens.index("to")
        if idx + 1 < n and tokens[idx + 1] in UNIVERSAL_VERB_LIKE:
            return True

    # Pattern 4: verb + determiner + vague object.
    # Examples: "pinpoint the surge", "find the thing".
    if n == 3 and tokens[0] in UNIVERSAL_VERB_LIKE and tokens[1] in {"the", "a", "an"} and tokens[2] in UNIVERSAL_VAGUE_OBJECTS:
        return True

    # Pattern 5: superlative + way + to + verb + dangling adjective.
    # Examples: "fastest way to convert rough".
    if (
        n >= 5
        and tokens[0] in {"fastest", "quickest", "best", "easiest", "simplest"}
        and tokens[1] in {"way", "method"}
        and "to" in tokens
        and tokens[-1] in UNIVERSAL_DANGLING_TAILS
    ):
        return True

    # Pattern 6: noun + preposition + adjective + noun without stable ordered pair.
    # Examples: "calendar into personalized ovulation".
    if n == 4 and tokens[1] in UNIVERSAL_PREPOSITION_TOKENS and tokens[2] in UNIVERSAL_ADJECTIVE_LIKE:
        if not _has_valid_ordered_pair(tokens):
            return True

    # Pattern 7: incomplete four-token semantic window ending in adjective-like token.
    # Examples: "egg white cervical" type partial modifier stack.
    if n == 3 and tokens[-1] in UNIVERSAL_ADJECTIVE_LIKE and not _has_valid_ordered_pair(tokens):
        return True

    return False

'''

if "_is_universal_semantic_fragment_pattern" not in s:
    if helper_marker not in s:
        raise SystemExit("score_phrase_strength marker not found")
    s = s.replace(helper_marker, helper_block + helper_marker, 1)

needle = '''    if _fails_malformed_wrapper_validation(tokens):
        return _reject_score_phrase(
            p,
            "malformed_wrapper_validation_failed",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

'''

insert = '''    if _fails_malformed_wrapper_validation(tokens):
        return _reject_score_phrase(
            p,
            "malformed_wrapper_validation_failed",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

    if _is_universal_semantic_fragment_pattern(tokens):
        return _reject_score_phrase(
            p,
            "universal_semantic_fragment_pattern",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

'''

if "universal_semantic_fragment_pattern" not in s:
    if needle not in s:
        raise SystemExit("malformed wrapper block not found")
    s = s.replace(needle, insert, 1)

p.write_text(s, encoding="utf-8")
print("patched universal semantic fragment guards")
