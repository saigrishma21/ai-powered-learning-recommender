from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.recommender import generate_recommendations


DATABASE_URL = "sqlite:///./learning_dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


def main():
    db = SessionLocal()

    try:
        learner_id = "LRN-000001"

        recommendations = generate_recommendations(
            db=db,
            learner_id=learner_id,
            limit=10,
        )

        print("=" * 60)
        print(f"RECOMMENDATIONS FOR {learner_id}")
        print("=" * 60)

        if not recommendations:
            print("No eligible recommendations found.")

        for index, item in enumerate(recommendations, start=1):
            print(f"\n{index}. {item['title']}")
            print(f"   Content ID: {item['content_id']}")
            print(f"   Difficulty: {item['difficulty']}")
            print(f"   Score: {item['recommendation_score']}")
            print(f"   Reasons: {item['reason_codes']}")

        print("\nTotal recommendations:", len(recommendations))

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()

