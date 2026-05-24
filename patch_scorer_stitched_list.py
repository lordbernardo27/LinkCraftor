from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

target = """    if _has_reversed_ordered_pair(tokens):
        return _reject_score_phrase(
            p,
            "reversed_ordered_pair",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

"""

patch = """    if _has_reversed_ordered_pair(tokens):
        return _reject_score_phrase(
            p,
            "reversed_ordered_pair",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

    original_list_hits = sum(
        1 for t in tokens
        if t in LIST_CHAIN_WORDS or t in LIST_CONTEXT_WORDS
    )
    if len(tokens) >= 5 and original_list_hits >= 4 and not _has_valid_ordered_pair(tokens):
        return _reject_score_phrase(
            p,
            "stitched_list_chain_phrase",
            score=0.0,
            workspace_id=workspace_id,
            document_id=document_id,
            vertical=vertical,
        )

"""

if "stitched_list_chain_phrase" not in s:
    if target not in s:
        raise SystemExit("target block not found")
    s = s.replace(target, patch, 1)

p.write_text(s, encoding="utf-8")
print("patched scorer stitched_list_chain_phrase")
