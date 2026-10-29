from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///./learning_full.db"

engine = create_engine(DATABASE_URL)

EXPECTED_COUNTS = {
    "learners": 10_000,
    "courses": 100,
    "skills": 500,
    "content_items": 2_000,
    "attempts": 500_000,
    "assessment_results": 500_000,
}


def main():
    print("=" * 60)
    print("FULL DATASET VERIFICATION")
    print("=" * 60)

    all_passed = True

    with engine.connect() as connection:
        for table, expected in EXPECTED_COUNTS.items():
            actual = connection.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar_one()

            passed = actual == expected
            status = "PASS" if passed else "FAIL"

            print(
                f"{status}: {table}: "
                f"{actual:,} records "
                f"(expected {expected:,})"
            )

            if not passed:
                all_passed = False

    print("-" * 60)

    if all_passed:
        print("RESULT: FULL DATASET VERIFIED SUCCESSFULLY")
    else:
        print("RESULT: DATASET NEEDS ATTENTION")

    engine.dispose()


if __name__ == "__main__":
    main()

