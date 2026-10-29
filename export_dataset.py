import csv
import hashlib
import json
import sqlite3
from datetime import datetime, date
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_ROOT / "learning_full.db"
EXPORT_DIR = PROJECT_ROOT / "exports"

TABLES = [
    "learners",
    "courses",
    "skills",
    "skill_prerequisites",
    "content_items",
    "content_skills",
    "attempts",
    "assessment_results",
    "learning_paths",
    "recommendations",
]


def sha256_file(file_path):
    """Calculate the SHA-256 checksum of a file."""
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def json_default(value):
    """Convert SQLite values that JSON cannot serialize directly."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return str(value)


def export_table(connection, table_name):
    """Export one database table to CSV and JSON."""
    cursor = connection.execute(
        f'SELECT * FROM "{table_name}"'
    )

    columns = [column[0] for column in cursor.description]

    csv_path = EXPORT_DIR / f"{table_name}.csv"
    json_path = EXPORT_DIR / f"{table_name}.json"

    row_count = 0

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)

        with open(json_path, "w", encoding="utf-8") as json_file:
            json_file.write("[\n")
            first_row = True

            for row in cursor:
                row_dict = dict(zip(columns, row))

                writer.writerow(row)

                if not first_row:
                    json_file.write(",\n")

                json_file.write(
                    json.dumps(
                        row_dict,
                        default=json_default,
                        ensure_ascii=False,
                    )
                )

                first_row = False
                row_count += 1

            json_file.write("\n]\n")

    print(
        f"PASS: {table_name}: {row_count:,} rows exported"
    )

    return {
        "table": table_name,
        "row_count": row_count,
        "csv_file": csv_path.name,
        "csv_sha256": sha256_file(csv_path),
        "json_file": json_path.name,
        "json_sha256": sha256_file(json_path),
    }


def main():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        f"file:{DATABASE_PATH.as_posix()}?mode=ro",
        uri=True,
    )

    try:
        existing_tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

        selected_tables = [
            table for table in TABLES
            if table in existing_tables
        ]

        if not selected_tables:
            raise RuntimeError(
                "No expected tables were found in the database."
            )

        print("=" * 60)
        print("DATASET EXPORT")
        print("=" * 60)
        print(f"Source: {DATABASE_PATH.name}")
        print(f"Output: {EXPORT_DIR}")
        print()

        manifest = {
            "source_database": DATABASE_PATH.name,
            "random_seed": 20261022,
            "exported_at_utc": datetime.utcnow().isoformat() + "Z",
            "tables": [],
        }

        for table_name in selected_tables:
            manifest["tables"].append(
                export_table(connection, table_name)
            )

        # Export the complete SQLite schema and data as SQL.
        sql_path = EXPORT_DIR / "learning_full.sql"

        with open(sql_path, "w", encoding="utf-8") as sql_file:
            for statement in connection.iterdump():
                sql_file.write(statement + "\n")

        manifest["sql_file"] = sql_path.name
        manifest["sql_sha256"] = sha256_file(sql_path)

        manifest_path = EXPORT_DIR / "manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as manifest_file:
            json.dump(manifest, manifest_file, indent=2)

        print()
        print(f"PASS: SQL export: {sql_path.name}")
        print(f"PASS: Manifest: {manifest_path.name}")
        print()
        print("EXPORT COMPLETED")
        print(f"Tables exported: {len(manifest['tables'])}")
        print(f"Export folder: {EXPORT_DIR}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()

