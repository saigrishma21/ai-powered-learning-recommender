import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
EXPORT_DIR = PROJECT_ROOT / "exports"

SQL_FILE = EXPORT_DIR / "learning_full.sql"
RESTORE_DB = EXPORT_DIR / "sql_restore_test.db"

EXPECTED_COUNTS = {
    "learners": 10_000,
    "courses": 100,
    "skills": 500,
    "content_items": 2_000,
    "attempts": 500_000,
    "assessment_results": 500_000,
}

def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(SQL_FILE)

    # Never overwrite an existing verification database.
    if RESTORE_DB.exists():
        raise FileExistsError(
            f"{RESTORE_DB} already exists. "
            "Rename or remove it after confirming it is safe to do so."
        )

    print("=" * 60)
    print("SQL EXPORT RESTORE TEST")
    print("=" * 60)

    connection = sqlite3.connect(RESTORE_DB)

    try:
        with open(SQL_FILE, "r", encoding="utf-8") as sql_file:
            connection.executescript(sql_file.read())

        connection.execute("PRAGMA foreign_keys = ON")

        all_passed = True

        for table, expected in EXPECTED_COUNTS.items():
            actual = connection.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            passed = actual == expected

            print(
                f'{"PASS" if passed else "FAIL"}: '
                f"{table}: {actual:,} "
                f"(expected {expected:,})"
            )

            if not passed:
                all_passed = False

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if foreign_key_errors:
            print(
                f"FAIL: Foreign-key violations: "
                f"{len(foreign_key_errors)}"
            )
            all_passed = False
        else:
            print("PASS: No foreign-key violations")

        print("-" * 60)

        if all_passed:
            print("RESULT: SQL EXPORT RESTORED SUCCESSFULLY")
        else:
            print("RESULT: SQL RESTORE NEEDS ATTENTION")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
