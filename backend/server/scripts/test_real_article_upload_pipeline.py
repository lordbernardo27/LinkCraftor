from __future__ import annotations

import json
from pathlib import Path

from backend.server.stores.upload_phrase_selector import select_upload_phrases
from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "test_articles" / "cross_niche" / "education_1500.txt"
DATA_DIR = ROOT / "data"

WORKSPACE_ID = "ws_cross_niche_education"
DOC_ID = "education_1500_001"


def main() -> None:
    article = ARTICLE_PATH.read_text(encoding="utf-8")

    selected = select_upload_phrases(
        workspace_id=WORKSPACE_ID,
        doc_id=DOC_ID,
        original_name="education_1500.txt",
        html="",
        text=article,
    )

    print("===== SELECTOR RESULT =====")
    print("article:", ARTICLE_PATH)
    print("candidate_count:", selected.get("candidate_count"))
    print("selected_count:", selected.get("selected_count"))
    print()

    for row in selected.get("phrases", [])[:50]:
        print(
            "-",
            row.get("phrase"),
            "| score:",
            row.get("score"),
            "| quality:",
            row.get("quality_score"),
            "| reason:",
            row.get("quality_reason"),
        )

    index_path = DATA_DIR / f"upload_phrase_index_{WORKSPACE_ID}.json"

    phrases = {}

    for row in selected.get("phrases", []):
        phrase = str(row.get("phrase") or "").strip()
        if not phrase:
            continue

        phrases[phrase] = {
            "phrase": phrase,
            "canonical": row.get("canonical") or phrase,
            "source_type": row.get("source_type") or "noun_phrase",
            "count_total": 1,
            "docs": {DOC_ID: 1},
            "sections": [row.get("section_id") or ""],
            "examples": [
                {
                    "doc_id": DOC_ID,
                    "section_id": row.get("section_id") or "",
                    "snippet": row.get("snippet") or "",
                }
            ],
            "aliases": [],
        }

    index_obj = {
        "workspace_id": WORKSPACE_ID,
        "doc_id": DOC_ID,
        "source": str(ARTICLE_PATH),
        "phrases": phrases,
    }

    index_path.write_text(
        json.dumps(index_obj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    built = build_upload_phrase_pool(WORKSPACE_ID)

    print()
    print("===== QUALITY GATE / BUILDER RESULT =====")
    print("source_phrase_count:", built.get("source_phrase_count"))
    print("quality_filtered_source_count:", built.get("quality_filtered_source_count"))
    print("phrase_count:", built.get("phrase_count"))
    print()

    for phrase in sorted(built.get("phrases", {}).keys()):
        print("-", phrase)

    false_positive_terms = {
        "one topic",
        "same topic",
        "each review",
        "light review",
        "lighter review",
        "extreme schedule",
        "study science",
        "average topics",
        "explaining topics",
        "influence learning performance",
        "another essential learning strategy",
    }

    saved_phrases = set(built.get("phrases", {}).keys())
    false_positives = sorted(saved_phrases & false_positive_terms)

    expected_good = {
        "study plan",
        "effective study plan",
        "active learning methods",
        "mock exams",
        "past questions",
        "study environment",
        "practice questions",
        "academic assessment",
    }

    good_found = sorted(saved_phrases & expected_good)
    good_missing = sorted(expected_good - saved_phrases)

    score = 10.0
    score -= len(false_positives) * 0.35
    score -= len(good_missing) * 0.60
    score = max(0.0, round(score, 1))

    production_ready = score >= 9.0 and not false_positives and not good_missing

    print()
    print("===== RATING / PRODUCTION READINESS =====")
    print("rating:", f"{score}/10")
    print("production_ready:", production_ready)
    print("good_found:", good_found)
    print("good_missing:", good_missing)
    print("false_positives:", false_positives)

    if not production_ready:
        print()
        print("WHAT TO FIX:")
        print("- Downgrade generic education fragments like one topic, same topic, light review.")
        print("- Penalize vague modifier + generic head pairs unless they are whitelisted.")
        print("- Add education-specific bad fragments to guard and scorer.")


if __name__ == "__main__":
    main()