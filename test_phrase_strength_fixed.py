from backend.server.stores.phrase_strength_scorer import score_phrase_strength

phrases = [
    "calculate ovulation",
    "fertile window",
    "survive up to five days",
    "high blood pressure",
    "blood pressure",
    "blood pressure medication guide",
    "quickly cash",
    "the day",
    "payroll rent supplier invoices loan",
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
