import sqlite3

connection = sqlite3.connect("learning.db")
cursor = connection.cursor()

query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"

cursor.execute(query)

tables = cursor.fetchall()

print("\nDatabase Tables:")

for table in tables:
    print(table[0])

print(f"\nTotal tables found: {len(tables)}")

connection.close()