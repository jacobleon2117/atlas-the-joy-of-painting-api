import psycopg2
import csv
import re
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def connect_db():
    return psycopg2.connect(
        dbname="joy_of_painting",
        user="jacobleon",
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
    )


def parse_episode_line(line):
    match = re.match(r'"([^"]+)" \(([^)]+)\)', line.strip())
    if match:
        title, date_str = match.groups()
        date = datetime.strptime(date_str, "%B %d, %Y").date()
        return title, date
    return None, None


def import_episodes(cur):
    with open("episode_data.txt", "r") as f:
        episode_number = 1
        season = 1
        for line in f:
            title, air_date = parse_episode_line(line)
            if title and air_date:
                cur.execute(
                    """
                    INSERT INTO Episodes (season, episode, title, air_date)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (season, episode) DO UPDATE 
                    SET title = EXCLUDED.title,
                        air_date = EXCLUDED.air_date
                    RETURNING episode_id
                """,
                    (f"S{season:02d}", f"E{episode_number:02d}", title, air_date),
                )

                if episode_number % 13 == 0:
                    season += 1
                episode_number += 1


def import_subjects(cur):
    with open("subject_data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            episode_code = row["EPISODE"]
            season, episode = episode_code.split("E")

            cur.execute(
                """
                SELECT episode_id FROM Episodes 
                WHERE season = %s AND episode = %s
            """,
                (season, f"E{int(episode):02d}"),
            )

            episode_result = cur.fetchone()
            if not episode_result:
                continue

            episode_id = episode_result[0]

            subject_columns = [
                "MOUNTAIN",
                "TREE",
                "LAKE",
                "CABIN",
                "SNOW",
                "CLOUDS",
                "WATERFALL",
            ]
            for subject in subject_columns:
                if subject in row and row[subject] == "1":
                    cur.execute(
                        "SELECT subject_id FROM Subjects WHERE name = %s", (subject,)
                    )
                    subject_result = cur.fetchone()
                    if subject_result:
                        subject_id = subject_result[0]
                        cur.execute(
                            """
                            INSERT INTO EpisodeSubjects (episode_id, subject_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """,
                            (episode_id, subject_id),
                        )


def import_colors(cur):
    with open("color_data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("colors"):
                continue

            season = int(row["season"])
            episode = int(row["episode"])

            cur.execute(
                """
                SELECT episode_id FROM Episodes 
                WHERE season = %s AND episode = %s
            """,
                (f"S{season:02d}", f"E{episode:02d}"),
            )

            episode_result = cur.fetchone()
            if not episode_result:
                continue

            episode_id = episode_result[0]

            try:
                colors = eval(row["colors"])
                for color_name in colors:
                    color_name = color_name.strip()
                    cur.execute(
                        "SELECT color_id FROM Colors WHERE name = %s", (color_name,)
                    )
                    color_result = cur.fetchone()
                    if color_result:
                        color_id = color_result[0]
                        cur.execute(
                            """
                            INSERT INTO EpisodeColors (episode_id, color_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """,
                            (episode_id, color_id),
                        )
            except:
                print(
                    f"Error processing colors for episode S{season:02d}E{episode:02d}"
                )


def main():
    conn = connect_db()
    cur = conn.cursor()

    try:
        print("Importing episodes...")
        import_episodes(cur)

        print("Importing subject relationships...")
        import_subjects(cur)

        print("Importing color relationships...")
        import_colors(cur)

        conn.commit()
        print("Import completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error during import: {str(e)}")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
