import os
from import_data import connect_db
from psycopg2.extras import RealDictCursor


def test_file_structure():
    required_files = ["episode_data.txt", "subject_data.csv", "color_data.csv"]

    print("Checking required files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} found")
            try:
                with open(file, "r") as f:
                    first_lines = [next(f) for _ in range(3)]
                    print(f"Preview of {file}:")
                    print("".join(first_lines))
            except StopIteration:
                print("File is empty or has fewer than 3 lines")
            except Exception as e:
                print(f"Error reading file: {e}")
            print("-" * 50)
        else:
            print(f"✗ {file} missing!")


def test_database():
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """
        )
        existing_tables = [row["table_name"].lower() for row in cur.fetchall()]

        tables = ["Episodes", "Subjects", "Colors", "EpisodeSubjects", "EpisodeColors"]
        print("\nChecking database tables:")

        for table in tables:
            if table.lower() not in existing_tables:
                print(f"✗ {table} table missing!")
                continue

            cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cur.fetchone()["count"]
            print(f"✓ {table}: {count} records")

            cur.execute(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table.lower()}'
                ORDER BY ordinal_position
            """
            )
            columns = [row["column_name"] for row in cur.fetchall()]

            cur.execute(f"SELECT * FROM {table} LIMIT 3")
            preview = cur.fetchall()
            print(f"Preview of {table}:")
            print("Columns:", columns)
            for row in preview:
                print({col: row[col] for col in row.keys()})
            print("-" * 50)

        print("\nTesting relationships:")

        cur.execute(
            """
            SELECT e.title, array_agg(s.name) as subjects
            FROM Episodes e
            JOIN EpisodeSubjects es ON e.episode_id = es.episode_id
            JOIN Subjects s ON es.subject_id = s.subject_id
            GROUP BY e.episode_id, e.title
            LIMIT 3
        """
        )
        print("\nEpisodes with subjects:")
        for row in cur.fetchall():
            print(row)

        cur.execute(
            """
            SELECT e.title, array_agg(c.name) as colors
            FROM Episodes e
            JOIN EpisodeColors ec ON e.episode_id = ec.episode_id
            JOIN Colors c ON ec.color_id = c.color_id
            GROUP BY e.episode_id, e.title
            LIMIT 3
        """
        )
        print("\nEpisodes with colors:")
        for row in cur.fetchall():
            print(row)

        cur.close()
        conn.close()
        print("\nDatabase connection test successful!")

    except Exception as e:
        print(f"Database test failed: {e}")
        if "cur" in locals() and cur is not None:
            cur.close()
        if "conn" in locals() and conn is not None:
            conn.close()


def test_queries():
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        print("\nTesting common queries:")

        cur.execute(
            """
            SELECT e.title
            FROM Episodes e
            JOIN EpisodeSubjects es ON e.episode_id = es.episode_id
            JOIN Subjects s ON es.subject_id = s.subject_id
            WHERE s.name = 'TREE'
            LIMIT 3
        """
        )
        print("\nEpisodes with trees:")
        print(cur.fetchall())

        cur.execute(
            """
            SELECT e.title
            FROM Episodes e
            JOIN EpisodeColors ec ON e.episode_id = ec.episode_id
            JOIN Colors c ON ec.color_id = c.color_id
            WHERE c.name = 'Bright Red'
            LIMIT 3
        """
        )
        print("\nEpisodes using Bright Red:")
        print(cur.fetchall())

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Query tests failed: {e}")
        if "cur" in locals() and cur is not None:
            cur.close()
        if "conn" in locals() and conn is not None:
            conn.close()


if __name__ == "__main__":
    print("=== Testing Setup ===\n")
    test_file_structure()
    test_database()
    test_queries()
