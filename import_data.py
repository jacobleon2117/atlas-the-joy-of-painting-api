import psycopg2
import re
from datetime import datetime
import csv


def connect_db():
    return psycopg2.connect(
        dbname="joy_of_painting",
        user="jacobleon",
        password="",
        host="localhost",
    )


def parse_episode_data(line):
    pattern = r'"([^"]+)"\s*\((\w+\s+\d+,\s+\d+)\)'
    match = re.match(pattern, line)
    if match:
        title = match.group(1)
        date_str = match.group(2)
        date = datetime.strptime(date_str, "%B %d, %Y")
        return title, date
    return None, None


def import_episodes(cursor, episode_data, color_data):
    youtube_urls = {}
    reader = csv.DictReader(color_data.strip().split("\n"))
    for row in reader:
        season = f"S{str(int(row['season'])).zfill(2)}"
        episode = f"E{str(int(row['episode'])).zfill(2)}"
        youtube_urls[f"{season}{episode}"] = row["youtube_src"]

    lines = episode_data.split("\n")
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        title, air_date = parse_episode_data(line)
        if not title:
            continue

        season = f"S{str(((i-1) // 13) + 1).zfill(2)}"
        episode = f"E{str(((i-1) % 13) + 1).zfill(2)}"

        youtube_url = youtube_urls.get(f"{season}{episode}")

        cursor.execute(
            """
            INSERT INTO Episodes (season, episode, title, air_date, youtube_src)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (season, episode, title, air_date, youtube_url),
        )


def import_subjects(cursor, subject_data):
    subjects = set()
    lines = subject_data.strip().split("\n")[1:]
    for line in lines:
        cols = line.split(",")
        for i, val in enumerate(cols[3:], 3):
            if val == "1":
                subject = cols[i].strip('"')
                if subject:
                    subjects.add(subject)

    for subject in subjects:
        category = categorize_subject(subject)
        cursor.execute(
            """
            INSERT INTO Subjects (name, category)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING
        """,
            (subject, category),
        )


def categorize_subject(subject):
    nature = {"TREE", "BUSH", "FLOWERS", "GRASS"}
    water = {"LAKE", "OCEAN", "RIVER", "WATERFALL", "WAVES"}
    structure = {"CABIN", "BARN", "MILL", "LIGHTHOUSE", "BRIDGE"}
    landscape = {"MOUNTAIN", "CLIFF", "BEACH", "HILLS"}
    weather = {"SNOW", "FOG", "CLOUDS"}

    if subject in nature:
        return "NATURE"
    elif subject in water:
        return "WATER"
    elif subject in structure:
        return "STRUCTURE"
    elif subject in landscape:
        return "LANDSCAPE"
    elif subject in weather:
        return "WEATHER"
    return "OTHER"


def link_episode_subjects(cursor, subject_data):
    cursor.execute("SELECT subject_id, name FROM Subjects")
    subject_ids = {name: id for id, name in cursor.fetchall()}

    cursor.execute("SELECT episode_id, season, episode FROM Episodes")
    episode_ids = {(season, episode): id for id, season, episode in cursor.fetchall()}

    lines = subject_data.strip().split("\n")[1:]
    for line in lines:
        cols = line.split(",")
        season_ep = cols[0].strip('"')
        season = f"S{season_ep[1:3]}"
        episode = f"E{season_ep[4:6]}"

        episode_id = episode_ids.get((season, episode))
        if not episode_id:
            continue

        for i, val in enumerate(cols[3:], 3):
            if val == "1":
                subject = cols[i].strip('"')
                subject_id = subject_ids.get(subject)
                if subject_id:
                    cursor.execute(
                        """
                        INSERT INTO EpisodeSubjects (episode_id, subject_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """,
                        (episode_id, subject_id),
                    )


def import_colors(cursor, color_data):
    lines = color_data.strip().split("\n")[1:]
    for line in lines:
        if not line.strip():
            continue

        cols = line.split(",")

        try:
            season = f"S{str(int(cols[4])).zfill(2)}"
            episode = f"E{str(int(cols[5])).zfill(2)}"
        except (IndexError, ValueError):
            print(f"Skipping line due to invalid season/episode format")
            continue

        cursor.execute(
            """
            SELECT episode_id FROM Episodes 
            WHERE season = %s AND episode = %s
        """,
            (season, episode),
        )
        result = cursor.fetchone()
        if not result:
            print(f"No episode found for {season} {episode}")
            continue

        episode_id = result[0]

        color_columns = [
            "Black_Gesso",
            "Bright_Red",
            "Burnt_Umber",
            "Cadmium_Yellow",
            "Dark_Sienna",
            "Indian_Red",
            "Indian_Yellow",
            "Liquid_Black",
            "Liquid_Clear",
            "Midnight_Black",
            "Phthalo_Blue",
            "Phthalo_Green",
            "Prussian_Blue",
            "Sap_Green",
            "Titanium_White",
            "Van_Dyke_Brown",
            "Yellow_Ochre",
            "Alizarin_Crimson",
        ]

        color_mapping = {
            "Black_Gesso": "Black Gesso",
            "Bright_Red": "Bright Red",
            "Burnt_Umber": "Burnt Umber",
            "Cadmium_Yellow": "Cadmium Yellow",
            "Dark_Sienna": "Dark Sienna",
            "Indian_Yellow": "Indian Yellow",
            "Phthalo_Blue": "Phthalo Blue",
            "Prussian_Blue": "Prussian Blue",
            "Sap_Green": "Sap Green",
            "Titanium_White": "Titanium White",
            "Van_Dyke_Brown": "Van Dyke Brown",
            "Alizarin_Crimson": "Alizarin Crimson",
        }

        for i, color_col in enumerate(color_columns, 10):
            try:
                if i < len(cols) and cols[i] == "1" and color_col in color_mapping:
                    cursor.execute(
                        """
                        SELECT color_id FROM Colors 
                        WHERE name = %s
                    """,
                        (color_mapping[color_col],),
                    )
                    color_result = cursor.fetchone()
                    if color_result:
                        cursor.execute(
                            """
                            INSERT INTO EpisodeColors (episode_id, color_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """,
                            (episode_id, color_result[0]),
                        )
            except Exception as e:
                print(f"Error processing color {color_col}: {e}")
                continue


def main():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        with open("episode_data.txt", "r") as f:
            episode_data = f.read()

        with open("subject_data.csv", "r") as f:
            subject_data = f.read()

        with open("color_data.csv", "r") as f:
            color_data = f.read()

        import_episodes(cursor, episode_data, color_data)
        import_subjects(cursor, subject_data)
        link_episode_subjects(cursor, subject_data)
        import_colors(cursor, color_data)

        conn.commit()

    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
