from backend.server.stores.candidate_window_guard import candidate_window_guard

ws = "ws_betterhealthcheck_com"
doc_id = "debug_doc"

phrases = [
    "calculate ovulation",
    "several days before ovulation",
    "fertile window",
    "survive up to five days",
    "the day",
    "quickly cash",
    "payroll rent supplier invoices loan",
    "high blood pressure",
    "blood pressure medication guide",
]

for phrase in phrases:
    r = candidate_window_guard(
        phrase,
        source_type="noun_phrase",
        workspace_id=ws,
        document_id=doc_id,
        vertical="general",
    )
    print(phrase, "=>", "keep=", r.get("keep"), "reason=", r.get("reason"), "phrase=", r.get("phrase"))
