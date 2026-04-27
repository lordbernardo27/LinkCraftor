from backend.server.stores.upload_phrase_selector import select_upload_phrases

fp = "article_quality_test.txt"

with open(fp, "r", encoding="utf-8") as f:
    text = f.read()

out = select_upload_phrases(
    workspace_id="ws_betterhealthcheck_com",
    doc_id="test_doc",
    original_name="How to Calculate Ovulation",
    html="",
    text=text,
)

phrases = out.get("phrases", [])

print("\n===== UPLOAD SELECTOR ARTICLE TEST =====")
print("ok=", out.get("ok"))
print("vertical=", out.get("vertical"))
print("paragraph_count=", out.get("paragraph_count"))
print("candidate_count=", out.get("candidate_count"))
print("selected_count=", out.get("selected_count"))

print("\n===== SELECTED PHRASES FIRST 150 =====")
for item in phrases[:150]:
    print(
        f"{item.get('phrase',''):55} "
        f"source={item.get('source_type',''):18} "
        f"score={item.get('score')} "
        f"q={item.get('quality_score')} "
        f"reason={item.get('quality_reason')}"
    )

with open("upload_selector_article_phrases.txt", "w", encoding="utf-8") as f:
    for item in phrases:
        f.write(
            f"{item.get('phrase','')}\t"
            f"source={item.get('source_type','')}\t"
            f"score={item.get('score')}\t"
            f"q={item.get('quality_score')}\t"
            f"reason={item.get('quality_reason')}\n"
        )

print("\nSaved: upload_selector_article_phrases.txt")
