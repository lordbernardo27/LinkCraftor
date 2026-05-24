from pathlib import Path

p = Path("backend/server/stores/phrase_strength_scorer.py")
s = p.read_text(encoding="utf-8")

marker = "return False\n\n\ndef score_phrase_strength("

insert = '''    # Pattern 8: subject/object + verb leakage.
    # Examples: "calendar method says fertility", "know the average length".
    if any(t in UNIVERSAL_VERB_LIKE for t in tokens):
        verb_positions = [i for i, t in enumerate(tokens) if t in UNIVERSAL_VERB_LIKE]

        for idx in verb_positions:
            # Verb inside phrase body.
            if idx > 0 and idx < n - 1:
                return True

            # Verb-led sentence fragment.
            if (
                idx == 0
                and n >= 3
                and (
                    tokens[1] in {"the", "a", "an", "single", "average"}
                    or tokens[-1] in {"day", "days", "length", "time", "date"}
                )
            ):
                return True

    # Pattern 9: weak temporal/object fragment.
    # Examples: "mark the five days", "hit single exact day".
    if (
        n >= 3
        and tokens[0] in UNIVERSAL_VERB_LIKE
        and any(t in {"day", "days", "length", "time", "date"} for t in tokens[1:])
    ):
        return True

    return False


def score_phrase_strength(
'''

if "subject/object + verb leakage" not in s:
    if marker not in s:
        raise SystemExit("marker not found")

    s = s.replace(marker, insert, 1)

p.write_text(s, encoding="utf-8")
print("verb leak guards inserted safely")
