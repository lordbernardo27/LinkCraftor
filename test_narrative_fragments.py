from backend.server.stores.phrase_strength_scorer import score_phrase_strength

phrases = [
    "beds kitchen",
    "clinic gave",
    "central role",
    "due date feels like",
    "explore further",
    "feel like solving small mystery",
    "fertile window",
    "basal body temperature",
    "high blood pressure",
    "cash flow management",
    "calculate ovulation",
    "direct nephrotoxicity",
    "excessive consumption",
]

for phrase in phrases:
    r = score_phrase_strength(
        phrase,
        source_type="noun_phrase",
        workspace_id="ws_betterhealthcheck_com",
        document_id="debug_doc",
        vertical="general",
    )
    print(phrase, "=>", "keep=", r.get("keep"), "score=", r.get("score"), "reason=", r.get("reason"), "phrase=", r.get("phrase"))
