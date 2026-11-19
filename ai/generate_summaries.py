import os

import anthropic
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

prompt_template = """
Write exactly two short, plain-language sentences for a Mariners
advertising sales manager reviewing a historical attendance prediction.
Return only the two sentences, without a heading, bullets, or Markdown.

Sentence 1: Identify the game date and opponent, then report predicted
and actual attendance.
Sentence 2: State whether the model overpredicted, underpredicted, or
matched attendance, using the supplied size of the miss.

Use the supplied rounded numbers exactly.
Do not calculate or add percentages, ratios, or other statistics.
Do not invent promotions, special events, causes, advertising impressions,
or revenue. Missing values mean unknown. Feature values alone do not
establish why the model made its prediction.

Game ID: {game_id}
Game date: {game_date}
Opponent: {team_name}
Day/night: {day_night}
Month: {month}
Weekend: {is_weekend}
U.S. holiday: {is_holiday}
Historical attendance average before cutoff: {rolling_avg_attendance_5}
Mariners winning percentage before cutoff: {mariners_win_pct_at_prediction}
Predicted attendance, rounded: {predicted_rounded}
Actual attendance: {actual}
Error direction: {direction}
Size of miss, rounded: {absolute_error_rounded} fans
"""

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

total_input_tokens = 0
total_output_tokens = 0
saved_count = 0

try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_summaries (
                game_id INTEGER PRIMARY KEY
                    REFERENCES fact_game(game_id),
                summary TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            SELECT
                m.game_id,
                m.game_date,
                m.team_name,
                m.day_night,
                m.month,
                m.is_weekend,
                m.is_holiday,
                m.rolling_avg_attendance_5,
                m.mariners_win_pct_at_prediction,
                p.predicted,
                p.actual
            FROM model_predictions p
            JOIN ml_features_attendance m
                ON p.game_id = m.game_id
            WHERE p.split = 'test'
            ORDER BY m.game_date, m.game_id
        """)

        games = cur.fetchall()

    conn.commit()

    if not games:
        raise ValueError("No test-game predictions found.")

    print("Test games to summarize:", len(games))

    for game in games:
        predicted = float(game["predicted"])
        actual = int(game["actual"])

        game["predicted_rounded"] = round(predicted)
        game["absolute_error_rounded"] = round(
            abs(actual - predicted)
        )

        if predicted < actual:
            game["direction"] = "underpredicted"
        elif predicted > actual:
            game["direction"] = "overpredicted"
        else:
            game["direction"] = "matched actual attendance"

        prompt = prompt_template.format(**game)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=250,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        if response.stop_reason != "end_turn":
            raise ValueError(
                f"Summary did not finish normally for "
                f"game {game['game_id']}: {response.stop_reason}"
            )

        summary = "\n".join(
            block.text
            for block in response.content
            if block.type == "text"
        ).strip()

        if not summary:
            raise ValueError(
                f"Empty summary for game {game['game_id']}"
            )

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ai_summaries
                    (game_id, summary, created_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (game_id)
                DO UPDATE SET
                    summary = EXCLUDED.summary,
                    created_at = EXCLUDED.created_at
            """, (int(game["game_id"]), summary))

        conn.commit()
        saved_count += 1

        print(
            f"Saved {saved_count}/{len(games)}: "
            f"game {game['game_id']}",
            flush=True
        )

        if saved_count <= 3:
            print("\nFACTS SENT:")
            print(prompt)
            print("\nSAVED SUMMARY:")
            print(summary)
            print()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM ai_summaries a
            JOIN model_predictions p
                ON a.game_id = p.game_id
            WHERE p.split = 'test'
        """)

        stored_count = cur.fetchone()[0]

    if stored_count != len(games):
        raise ValueError(
            f"Expected {len(games)} stored test summaries, "
            f"but found {stored_count}."
        )

    print("\nSummaries saved this run:", saved_count)
    print("Test summaries in PostgreSQL:", stored_count)
    print("Total input tokens:", total_input_tokens)
    print("Total output tokens:", total_output_tokens)

except Exception:
    conn.rollback()
    print(
        f"\nRun stopped. {saved_count} summaries were "
        "successfully committed before the error."
    )
    raise

finally:
    conn.close()