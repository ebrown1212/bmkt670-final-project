# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Run seven automated PostgreSQL data-quality checks
# and report PASS or FAIL for data integrity and completeness.

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()
failures = 0

# Check 1: No duplicate game IDs.
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT game_id)
    FROM fact_game
""")

duplicates = cur.fetchone()[0]

if duplicates == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Duplicate game IDs: {duplicates}")


# Check 2: Attendance must be within a valid range.
cur.execute("""
    SELECT COUNT(*)
    FROM fact_game
    WHERE attendance <= 0
       OR attendance > 47929
""")

invalid_attendance = cur.fetchone()[0]

if invalid_attendance == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Invalid attendance values: {invalid_attendance}")


# Check 3: ML attendance targets must not be missing.
cur.execute("""
    SELECT COUNT(*)
    FROM ml_features_attendance
    WHERE attendance IS NULL
""")

missing_targets = cur.fetchone()[0]

if missing_targets == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Missing ML attendance targets: {missing_targets}")


# Check 4: Every game must have valid dimension keys.
cur.execute("""
    SELECT COUNT(*)
    FROM fact_game g
    LEFT JOIN dim_date d ON g.date_key = d.date_key
    LEFT JOIN dim_team t ON g.opponent_key = t.team_key
    LEFT JOIN dim_venue v ON g.venue_key = v.venue_key
    WHERE d.date_key IS NULL
       OR t.team_key IS NULL
       OR v.venue_key IS NULL
""")

invalid_keys = cur.fetchone()[0]

if invalid_keys == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Invalid game foreign keys: {invalid_keys}")


# Check 5: Every home game must have a matching weather date.
cur.execute("""
    SELECT COUNT(*)
    FROM fact_game g
    LEFT JOIN fact_weather w ON g.date_key = w.date_key
    WHERE w.date_key IS NULL
""")

missing_weather_dates = cur.fetchone()[0]

if missing_weather_dates == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Games without matching weather dates: {missing_weather_dates}")


# Check 6: Loaded game count must match the source data.
import pandas as pd

source_games = pd.read_csv("data/raw/mariners_home_games_2022_2025.csv")

cur.execute("SELECT COUNT(*) FROM fact_game")
loaded_games = cur.fetchone()[0]

count_difference = abs(len(source_games) - loaded_games)

if count_difference == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Source vs loaded game count difference: {count_difference}")

# Check 7: No duplicate weather dates.
cur.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT date_key)
    FROM fact_weather
""")

duplicate_weather_dates = cur.fetchone()[0]

if duplicate_weather_dates == 0:
    status = "PASS"
else:
    status = "FAIL"
    failures += 1

print(f"[{status}] Duplicate weather dates: {duplicate_weather_dates}")

cur.close()
conn.close()

print(f"\nQuality checks: {7 - failures}/7 passed")

if failures > 0:
    raise SystemExit(1)