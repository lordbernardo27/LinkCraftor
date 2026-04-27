from backend.server.stores.phrase_quality_gate import classify_phrase_strength, canonical_phrase, tokenize

fp = "article_quality_test.txt"

with open(fp, "r", encoding="utf-8") as f:
    text = f.read()

tokens = tokenize(text)

candidates = set()
for n in (2, 3, 4, 5):
    for i in range(0, len(tokens) - n + 1):
        phrase = canonical_phrase(" ".join(tokens[i:i+n]))
        if phrase:
            candidates.add(phrase)

strong = []
weak = []

for phrase in sorted(candidates):
    r = classify_phrase_strength(
        phrase,
        source_type="noun_phrase",
        vertical="health",
        context=text,
    )

    row = (phrase, r["score"], r["reason"])

    if r["keep"]:
        strong.append(row)
    else:
        weak.append(row)

strong = sorted(strong, key=lambda x: (-x[1], x[0]))
weak = sorted(weak, key=lambda x: (x[1], x[0]))

print("\n===== ARTICLE QUALITY GATE TEST =====")
print("Total candidates:", len(candidates))
print("Strong kept:", len(strong))
print("Weak rejected:", len(weak))

print("\n===== STRONG PHRASES FIRST 120 =====")
for phrase, score, reason in strong[:120]:
    print(f"{phrase:55} score={score} reason={reason}")

print("\n===== WEAK PHRASES FIRST 120 =====")
for phrase, score, reason in weak[:120]:
    print(f"{phrase:55} score={score} reason={reason}")

with open("article_quality_strong.txt", "w", encoding="utf-8") as f:
    for phrase, score, reason in strong:
        f.write(f"{phrase}\tscore={score}\treason={reason}\n")

with open("article_quality_weak.txt", "w", encoding="utf-8") as f:
    for phrase, score, reason in weak:
        f.write(f"{phrase}\tscore={score}\treason={reason}\n")

print("\nSaved:")
print("article_quality_strong.txt")
print("article_quality_weak.txt")
