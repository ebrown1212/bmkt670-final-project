# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Rebuild the PostgreSQL database and load six cleaned
# tables, including the attendance prediction feature table.

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

tables = [
    "dim_date",
    "dim_team",
    "dim_venue",
    "fact_game",
    "fact_weather",
    "ml_features_attendance"
]

try:
    with conn.cursor() as cur:
        with open("sql/schema.sql", "r", encoding="utf-8") as file:
            cur.execute(file.read())

        print("Database schema created.")

        for table in tables:
            file_path = f"data/clean/{table}.csv"

            with open(file_path, "r", encoding="utf-8") as file:
                if table == "fact_weather":
                    columns = "(date_key, avg_temp_f, min_temp_f, max_temp_f, humidity, precipitation_in, wind_speed_mph)"
                else:
                    columns = ""

                cur.copy_expert(
                    f"COPY {table} {columns} FROM STDIN WITH CSV HEADER",
                    file
                )

            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"{table}: {cur.fetchone()[0]} rows loaded")

    conn.commit()
    print("\nAll tables loaded successfully.")

except Exception as error:
    conn.rollback()
    print("Database loading failed:", error)
    raise

finally:
    conn.close()
