from flask import Flask, request, jsonify, render_template
import psycopg2
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
load_dotenv()


def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )


@app.route("/")
def home():
    """Root endpoint showing available routes"""
    return jsonify(
        {
            "available_endpoints": {
                "/api/episodes": "Get all episodes with optional filters",
                "/api/episodes?subject=TREE": "Get episodes with trees",
                "/api/episodes?color=Bright Red": "Get episodes using Bright Red",
                "/api/episodes?month=1": "Get episodes from January",
                "/api/filters": "Get all available filter options",
            }
        }
    )


@app.route("/ui")
def ui():
    return render_template("index.html")


@app.route("/api/episodes", methods=["GET"])
def get_episodes():
    months = request.args.getlist("month")
    months = [int(m) for m in months if m.isdigit()]
    subjects = [s.upper().strip() for s in request.args.getlist("subject")]
    colors = [c.strip() for c in request.args.getlist("color")]
    filter_type = request.args.get("filter_type", "AND").strip()

    print(
        f"Received filters - Colors: {colors}, Subjects: {subjects}, Months: {months}"
    )

    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT DISTINCT e.episode_id, e.title, e.season, e.episode, 
                e.air_date, e.youtube_src,
                array_agg(DISTINCT s.name) FILTER (WHERE s.name IS NOT NULL) as subjects,
                array_agg(DISTINCT c.name) FILTER (WHERE c.name IS NOT NULL) as colors
            FROM Episodes e
            LEFT JOIN EpisodeSubjects es ON e.episode_id = es.episode_id
            LEFT JOIN Subjects s ON es.subject_id = s.subject_id
            LEFT JOIN EpisodeColors ec ON e.episode_id = ec.episode_id
            LEFT JOIN Colors c ON ec.color_id = c.color_id
        """

        conditions = []
        params = []

        if months:
            month_condition = (
                "EXTRACT(MONTH FROM e.air_date)::integer = ANY(%s::integer[])"
            )
            conditions.append(month_condition)
            params.append(months)

        if subjects:
            if filter_type == "AND":
                for subject in subjects:
                    subject_condition = """
                        EXISTS (
                            SELECT 1 FROM EpisodeSubjects es2
                            JOIN Subjects s2 ON es2.subject_id = s2.subject_id
                            WHERE es2.episode_id = e.episode_id AND UPPER(s2.name) = %s
                        )
                    """
                    conditions.append(subject_condition)
                    params.append(subject)
            else:
                subject_condition = "UPPER(s.name) = ANY(%s)"
                conditions.append(subject_condition)
                params.append(subjects)

        if colors:
            if filter_type == "AND":
                for color in colors:
                    color_condition = """
                        EXISTS (
                            SELECT 1 FROM EpisodeColors ec2
                            JOIN Colors c2 ON ec2.color_id = c2.color_id
                            WHERE ec2.episode_id = e.episode_id AND c2.name = %s
                        )
                    """
                    conditions.append(color_condition)
                    params.append(color)
            else:
                color_condition = """
                    EXISTS (
                        SELECT 1 FROM EpisodeColors ec2
                        JOIN Colors c2 ON ec2.color_id = c2.color_id
                        WHERE ec2.episode_id = e.episode_id AND c2.name = ANY(%s)
                    )
                """
                conditions.append(color_condition)
                params.append(colors)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            GROUP BY e.episode_id, e.title, e.season, e.episode, e.air_date, e.youtube_src
            ORDER BY e.air_date
        """

        print("Query:", query)
        print("Params:", params)

        cur.execute(query, params)
        results = cur.fetchall()
        print(f"Found {len(results)} results")

        for result in results:
            if result["air_date"]:
                result["air_date"] = result["air_date"].strftime("%Y-%m-%d")
            if result["subjects"] is None:
                result["subjects"] = []
            if result["colors"] is None:
                result["colors"] = []

        return jsonify(
            {
                "total_episodes": len(results),
                "episodes": results,
                "debug": {
                    "filters_received": {
                        "colors": colors,
                        "subjects": subjects,
                        "months": months,
                        "filter_type": filter_type,
                    }
                },
            }
        )

    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/filters", methods=["GET"])
def get_filters():
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT name, category 
            FROM Subjects 
            ORDER BY name
            """
        )
        subjects = cur.fetchall()

        cur.execute(
            """
            SELECT name, hex_code 
            FROM Colors 
            ORDER BY name
            """
        )
        colors = cur.fetchall()

        cur.execute(
            """
            SELECT DISTINCT 
                EXTRACT(MONTH FROM air_date)::integer as month_num,
                to_char(air_date, 'Month') as month_name
            FROM Episodes
            ORDER BY month_num
            """
        )
        months = cur.fetchall()

        return jsonify(
            {
                "subjects": subjects,
                "colors": colors,
                "months": months,
                "example_usage": {
                    "filter_by_subject": "/api/episodes?subject=TREE",
                    "filter_by_color": "/api/episodes?color=Bright Red",
                    "filter_by_month": "/api/episodes?month=1",
                    "filter_type_and": "/api/episodes?subject=TREE&subject=MOUNTAIN&filter_type=AND",
                    "filter_type_or": "/api/episodes?subject=TREE&subject=MOUNTAIN&filter_type=OR",
                },
            }
        )

    except Exception as e:
        print(f"Error getting filters: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
