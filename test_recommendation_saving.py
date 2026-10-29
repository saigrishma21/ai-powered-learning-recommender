from src.database import SessionLocal
from src.models import Learner, Recommendation
from src.recommender import (
    generate_recommendations,
    save_recommendations,
)


def main():
    db = SessionLocal()

    try:
        learner = (
            db.query(Learner)
            .filter(Learner.status == "ACTIVE")
            .order_by(Learner.learner_id)
            .first()
        )

        if learner is None:
            print("FAIL: No active learner found.")
            return

        print("=" * 60)
        print("RECOMMENDATION GENERATION TEST")
        print("=" * 60)
        print(f"Learner ID: {learner.learner_id}")

        # Step 1: Generate recommendations.
        recommendations = generate_recommendations(
            db,
            learner.learner_id,
            limit=5,
        )

        print(f"\nGenerated recommendations: {len(recommendations)}")

        for item in recommendations:
            print(
                f"- {item['content_id']} | "
                f"{item['title']} | "
                f"Score: {item['recommendation_score']} | "
                f"Reasons: {item['reason_codes']}"
            )

        if not recommendations:
            print(
                "\nFAIL: No recommendations were generated. "
                "Inspect the learner's skills, prerequisites, "
                "and content mappings before proceeding."
            )
            return

        # Step 2: Save the recommendations.
        saved_count = save_recommendations(
            db,
            learner.learner_id,
            recommendations,
        )

        print(f"\nNew recommendation records saved: {saved_count}")

        # Step 3: Confirm that the records exist.
        total_saved = (
            db.query(Recommendation)
            .filter(
                Recommendation.learner_id == learner.learner_id
            )
            .count()
        )

        print(f"Saved records for this learner: {total_saved}")

        if saved_count > 0 and total_saved >= saved_count:
            print("\nRESULT: RECOMMENDATION SAVING PASSED")
        else:
            print("\nRESULT: CHECK RECOMMENDATION SAVING")

    finally:
        db.close()


if __name__ == "__main__":
    main()

