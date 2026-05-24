from backend.server.stores.phrase_strength_scorer import score_phrase_strength

phrases = [
    "calendar method says fertility",
    "hit single exact day",
    "know the average length",
    "mark the five days",
    "period tools",
    "real time ovulation",
    "wet phase ovulation",
    "calculate ovulation",
    "fertile window",
    "basal body temperature",
    "high blood pressure",
    "cash flow management",
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
