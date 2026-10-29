from src.database import SessionLocal
from src.models import Learner, Course, LearningPath
from src.learning_paths import create_learning_path


def main():
    db = SessionLocal()

    try:
        # Find an active learner.
        learner = (
            db.query(Learner)
            .filter(Learner.status == "ACTIVE")
            .order_by(Learner.learner_id)
            .first()
        )

        if learner is None:
            print("FAIL: No active learner found.")
            return

        # Find a published course.
        course = (
            db.query(Course)
            .filter(Course.status == "PUBLISHED")
            .order_by(Course.course_id)
            .first()
        )

        if course is None:
            print("FAIL: No published course found.")
            return

        print("=" * 60)
        print("LEARNING-PATH CREATION TEST")
        print("=" * 60)

        print(f"Learner: {learner.learner_id}")
        print(f"Course: {course.course_id}")

        # Record the count before testing.
        before_count = (
            db.query(LearningPath)
            .filter(
                LearningPath.learner_id == learner.learner_id,
                LearningPath.course_id == course.course_id,
                LearningPath.status == "ACTIVE",
            )
            .count()
        )

        # First call: create or reuse a path.
        first_path = create_learning_path(
            db,
            learner.learner_id,
            course.course_id,
        )

        print(f"\nFirst call returned: {first_path.learning_path_id}")

        # Second call: should reuse the same active path.
        second_path = create_learning_path(
            db,
            learner.learner_id,
            course.course_id,
        )

        print(f"Second call returned: {second_path.learning_path_id}")

        after_count = (
            db.query(LearningPath)
            .filter(
                LearningPath.learner_id == learner.learner_id,
                LearningPath.course_id == course.course_id,
                LearningPath.status == "ACTIVE",
            )
            .count()
        )

        print(f"Active paths before: {before_count}")
        print(f"Active paths after: {after_count}")

        if (
            first_path.learning_path_id == second_path.learning_path_id
            and after_count == max(before_count, 1)
        ):
            print("\nRESULT: LEARNING-PATH CREATION PASSED")
        else:
            print("\nRESULT: CHECK LEARNING-PATH DUPLICATE HANDLING")

    finally:
        db.close()


if __name__ == "__main__":
    main()

