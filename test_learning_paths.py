from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.learning_paths import (
    create_learning_path,
    get_learning_path_content,
)


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
        course_id = "CRS-000001"

        # Create or retrieve an active learning path.
        path = create_learning_path(
            db=db,
            learner_id=learner_id,
            course_id=course_id,
        )

        print("=" * 60)
        print("LEARNING PATH")
        print("=" * 60)
        print("Path ID:", path.learning_path_id)
        print("Learner ID:", path.learner_id)
        print("Course ID:", path.course_id)
        print("Status:", path.status)
        print("Version:", path.version)

        # Retrieve eligible content in learning order.
        items = get_learning_path_content(
            db=db,
            learner_id=learner_id,
            course_id=course_id,
        )

        print("\nLEARNING CONTENT")

        if not items:
            print("No eligible content found.")

        for index, item in enumerate(items, start=1):
            print(
                f"{index}. {item['title']} "
                f"({item['difficulty']}) - "
                f"{item['estimated_minutes']} minutes"
            )

        print("\nTotal eligible items:", len(items))

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
