from backend.server.stores.smart_phrase_extractor import extract_smart_phrases
from backend.server.stores.phrase_quality_gate import classify_phrase_strength

fp = "article_quality_test.txt"

with open(fp, "r", encoding="utf-8") as f:
    text = f.read()

candidates = extract_smart_phrases(
    text=text,
    html="",
    title="How to Calculate Ovulation",
    doc_id="test_doc",
    max_candidates=500,
)

strong = []
weak = []

for item in candidates:
    phrase = item.get("phrase", "")
    source_type = item.get("source_type", "")
    snippet = item.get("snippet", "")

    r = classify_phrase_strength(
        phrase,
        source_type=source_type,
        vertical="health",
        context=snippet or text,
    )

    row = (phrase, source_type, r["keep"], r["score"], r["reason"])

    if r["keep"]:
        strong.append(row)
    else:
        weak.append(row)

strong = sorted(strong, key=lambda x: (-x[3], x[0]))
weak = sorted(weak, key=lambda x: (x[3], x[0]))

print("\n===== SMART EXTRACTOR + QUALITY GATE TEST =====")
print("Raw smart candidates:", len(candidates))
print("Strong kept:", len(strong))
print("Weak rejected:", len(weak))

print("\n===== STRONG PHRASES FIRST 120 =====")
for phrase, source_type, keep, score, reason in strong[:120]:
    print(f"{phrase:55} source={source_type:18} score={score} reason={reason}")

print("\n===== WEAK PHRASES FIRST 80 =====")
for phrase, source_type, keep, score, reason in weak[:80]:
    print(f"{phrase:55} source={source_type:18} score={score} reason={reason}")

with open("smart_article_strong.txt", "w", encoding="utf-8") as f:
    for phrase, source_type, keep, score, reason in strong:
        f.write(f"{phrase}\tsource={source_type}\tscore={score}\treason={reason}\n")

with open("smart_article_weak.txt", "w", encoding="utf-8") as f:
    for phrase, source_type, keep, score, reason in weak:
        f.write(f"{phrase}\tsource={source_type}\tscore={score}\treason={reason}\n")

print("\nSaved:")
print("smart_article_strong.txt")
print("smart_article_weak.txt")
