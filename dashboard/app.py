
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

    prediction_query = """
    SELECT
        game_id,
        split,
        actual,
        predicted,
        error,
        model_name
    FROM model_predictions
    WHERE split IN ('validation', 'test')
    ORDER BY game_id
    """

    cur.execute(prediction_query)
    prediction_rows = cur.fetchall()
    prediction_columns = [column[0] for column in cur.description]

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

st.header("How Good Are the Predictions?")

predictions_df = pd.DataFrame(
    prediction_rows,
    columns=prediction_columns
)

predictions_df["predicted"] = pd.to_numeric(predictions_df["predicted"])
predictions_df["actual"] = pd.to_numeric(predictions_df["actual"])

predictions_df["error"] = pd.to_numeric(predictions_df["error"])

st.dataframe(predictions_df)

st.write("Validation and test predictions:", len(predictions_df))


predictions_df["absolute_error"] = predictions_df["error"].abs()

mae_by_split = (
    predictions_df.groupby("split")["absolute_error"]
    .mean()
    .round(0)
)

st.subheader("Model Prediction Accuracy")

st.write("Mean Absolute Error by Dataset:")
st.dataframe(mae_by_split)


st.subheader("Predicted vs. Actual Attendance")

st.scatter_chart(
    predictions_df,
    x="predicted",
    y="actual",
    color="split"
)

st.write(
    "Each point represents one home game. Predictions closer "
    "to actual attendance indicate better forecasting accuracy."
)


st.subheader("Model vs. Baseline")

baseline_mae = 6725
model_mae = mae_by_split["validation"]

improvement = (
    (baseline_mae - model_mae) / baseline_mae
) * 100

st.metric(
    "Baseline Validation MAE",
    f"{baseline_mae:,.0f} fans"
)

st.metric(
    "Random Forest Validation MAE",
    f"{model_mae:,.0f} fans",
    delta=f"{improvement:.1f}% improvement"
)


st.subheader("Largest Prediction Errors")

largest_errors = predictions_df.copy()

largest_errors["mae_for_split"] = largest_errors["split"].map(
    mae_by_split
)

largest_errors["error_multiple"] = (
    largest_errors["absolute_error"] /
    largest_errors["mae_for_split"]
).round(1)

largest_errors["unusual"] = (
    largest_errors["error_multiple"] > 2
)

largest_errors = largest_errors.sort_values(
    "absolute_error",
    ascending=False
).head(10)

st.dataframe(
    largest_errors[
        [
            "game_id",
            "split",
            "actual",
            "predicted",
            "absolute_error",
            "error_multiple",
            "unusual"
        ]
    ]
)
