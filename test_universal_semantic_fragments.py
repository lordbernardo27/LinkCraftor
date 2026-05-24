from backend.server.stores.phrase_strength_scorer import score_phrase_strength

phrases = [
    "more stretchy",
    "slippery stretchy",
    "temperature each",
    "opks to predict",
    "pinpoint the surge",
    "fastest way to convert rough",
    "calendar into personalized ovulation",
    "egg white cervical",
    "fertile window",
    "typical cycle length",
    "high blood pressure",
    "blood pressure medication guide",
    "cash flow management",
    "rental agreement",
    "content optimization",
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
