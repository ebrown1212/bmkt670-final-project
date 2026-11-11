
import os

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("Seattle Mariners Advertising Sales Intelligence")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

query = """
SELECT
    d.season,
    d.full_date,
    t.team_name AS opponent,
    g.attendance
FROM fact_game g
JOIN dim_date d
    ON g.date_key = d.date_key
JOIN dim_team t
    ON g.opponent_key = t.team_key
WHERE g.attendance IS NOT NULL
ORDER BY d.full_date
"""

with conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]

conn.close()

df = pd.DataFrame(rows, columns=columns)

selected_seasons = st.multiselect(
    "Select seasons:",
    options=sorted(df["season"].unique()),
    default=sorted(df["season"].unique())
)

filtered_df = df[df["season"].isin(selected_seasons)]

st.write("Historical Mariners home-game attendance")
st.dataframe(filtered_df)
st.write("Total games:", len(df))


st.subheader("Average Attendance by Season")

season_attendance = (
    filtered_df.groupby("season")["attendance"]
    .mean()
    .round(0)
)

st.bar_chart(season_attendance)

st.write(
    "This chart compares average home-game attendance "
    "across the four seasons."
)

st.subheader("Average Attendance by Opponent")

opponent_attendance = (
    filtered_df.groupby("opponent")["attendance"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .round(0)
)

st.bar_chart(
    opponent_attendance,
    sort="-attendance"
)

st.write(
    "This chart shows the 10 opponents associated with "
    "the highest average Mariners home-game attendance "
    "for the selected seasons."
)

opponent_summary = (
    filtered_df.groupby("opponent")["attendance"]
    .agg(["count", "mean"])
    .sort_values("mean", ascending=False)
    .head(10)
    .round(0)
)

st.write("Top 10 opponents: Attendance and Game Counts")
st.dataframe(opponent_summary)