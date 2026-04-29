from __future__ import annotations

from backend.server.stores.upload_phrase_selector import select_upload_phrases


ARTICLES = {
    "education": """
How to Build an Effective Study Plan for Exam Preparation Without Burning Out

Many students start exam preparation with motivation, but motivation alone rarely lasts. What usually creates strong results is a clear system. A well-designed study plan helps students use time wisely, remember information better, reduce stress, and stay consistent until exam day.

The first step in building an effective study plan is understanding the exam itself. Students should know the exam format, number of subjects, topic weight, deadlines, and scoring method.

Time blocking is one of the most useful techniques in exam preparation. Students should also use active learning methods rather than passive reading. Spaced repetition is another important strategy. A strong study plan should include past questions and mock exams.
""",

    "finance": """
Small Business Cash Flow Management Beyond Monthly Revenue

Many small businesses look profitable on paper but still struggle to pay bills on time. This happens because revenue and cash flow are not the same thing. Revenue shows what the business earned through sales, while cash flow shows how money actually moves in and out of the business bank account.

Cash flow management begins with visibility. Business owners need to know how much cash is available today, what payments are expected this week, and which expenses are due soon.

One of the most important areas to monitor is accounts receivable. Faster invoicing, clear payment terms, automated reminders, and consistent follow-up can improve collections significantly.

Working capital is another key concept. Positive working capital often means the company can handle day-to-day operations more comfortably.

Inventory can quietly damage cash flow. Better inventory management uses sales history, reorder planning, and demand forecasting to keep stock levels healthier.
""",
}


def run_article_test(niche: str, article: str) -> None:
    out = select_upload_phrases(
        workspace_id="ws_demo",
        doc_id=f"{niche}_test_001",
        original_name=f"{niche.title()} Test Article",
        html="",
        text=article,
    )

    print("\n" + "=" * 80)
    print("NICHE:", niche)
    print("=" * 80)
    print("ok:", out.get("ok"))
    print("candidate_count:", out.get("candidate_count"))
    print("selected_count:", out.get("selected_count"))
    print("top_phrases:")

    for row in out.get("phrases", [])[:15]:
        print(
            f"- {row.get('phrase')} "
            f"| score={row.get('score')} "
            f"| quality={row.get('quality_score')} "
            f"| reason={row.get('quality_reason')}"
        )


def main() -> None:
    print("===== BATCH 1 CROSS-NICHE PRECISION TEST (REAL ARTICLES) =====")

    for niche, article in ARTICLES.items():
        run_article_test(niche, article)


if __name__ == "__main__":
    main()