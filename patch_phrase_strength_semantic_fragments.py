from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

insert_after = '''def score_phrase_strength(
    phrase: str,
    *,
    source_type: str = "",
    allow_trim: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    workspace_id = str(kwargs.get("workspace_id", "default") or "default")
    document_id = str(kwargs.get("document_id", "") or "")
    vertical = str(kwargs.get("vertical", "general") or "general")

    p = canonical_phrase(phrase)
    tokens = tokenize(p)
'''

replacement = '''def score_phrase_strength(
    phrase: str,
    *,
    source_type: str = "",
    allow_trim: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    workspace_id = str(kwargs.get("workspace_id", "default") or "default")
    document_id = str(kwargs.get("document_id", "") or "")
    vertical = str(kwargs.get("vertical", "general") or "general")

    p = canonical_phrase(phrase)
    tokens = tokenize(p)

    def hard_reject(reason: str) -> Dict[str, Any]:
        return _reject_score_phrase(
            p,
            reason,
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

    # Universal semantic-fragment suppressors.
    weak_exact = {
        "more stretchy",
        "slippery stretchy",
        "temperature each",
        "opks to predict",
        "pinpoint the surge",
        "fastest way to convert rough",
        "calendar into personalized ovulation",
        "period up to ovulation",
    }
    if p in weak_exact:
        return hard_reject("semantic_fragment_suppression")

    # Reject adjective-only collisions unless they form a known complete anchor.
    adjective_collision_terms = {
        "stretchy", "slippery", "rough", "wet", "dry", "more", "less",
        "fastest", "personalized", "typical", "shortest", "longest",
    }
    if len(tokens) == 2 and all(t in adjective_collision_terms for t in tokens):
        return hard_reject("adjective_collision_fragment")

    # Reject incomplete medical/fertility anchor fragments.
    broken_medical_windows = {
        ("egg", "white", "cervical"),
        ("basal", "body"),
        ("luteinizing", "hormone"),
    }
    if tuple(tokens) in broken_medical_windows:
        return hard_reject("incomplete_medical_anchor")

    if len(tokens) >= 2 and tokens[-1] in {"each", "rough", "predict", "surge"}:
        return hard_reject("dangling_tail_fragment")

    if "into" in tokens and len(tokens) <= 4:
        return hard_reject("broken_prepositional_window")
'''

if insert_after not in s:
    raise SystemExit("target score_phrase_strength block not found")

s = s.replace(insert_after, replacement, 1)
p.write_text(s, encoding="utf-8")
print("patched phrase_strength_scorer semantic fragment suppression")
