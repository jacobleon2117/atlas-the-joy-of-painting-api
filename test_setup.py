import os
from import_data import connect_db


def test_file_structure():
    required_files = ["episode_data.txt", "subject_data.csv", "color_data.csv"]

    print("Checking required files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} found")
            with open(file, "r") as f:
                first_lines = [next(f) for _ in range(3)]
                print(f"Preview of {file}:")
                print("".join(first_lines))
                print("-" * 50)
        else:
            print(f"✗ {file} missing!")


def test_database():
    try:
        conn = connect_db()
        cur = conn.cursor()

        tables = ["Episodes", "Subjects", "Colors", "EpisodeSubjects", "EpisodeColors"]
        print("\nChecking database tables:")

        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"✓ {table}: {count} records")

            cur.execute(f"SELECT * FROM {table} LIMIT 3")
            preview = cur.fetchall()
            print(f"Preview of {table}:")
            print(preview)
            print("-" * 50)

        cur.close()
        conn.close()
        print("\nDatabase connection test successful!")

    except Exception as e:
        print(f"Database test failed: {e}")


if __name__ == "__main__":
    print("=== Testing Setup ===\n")
    test_file_structure()
    test_database()
