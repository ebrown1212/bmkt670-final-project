
import os

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv
import joblib

load_dotenv()

st.title("Seattle Mariners Advertising Sales Intelligence")

page = st.sidebar.radio(
    "Dashboard Pages",
    [
        "1. What Happened?",
        "2. How Good Are the Predictions?",
        "3. What Should We Do?"
    ]
)

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
    
    baseline_query = """
    SELECT AVG(ABS(attendance - (
        SELECT AVG(attendance)
        FROM ml_features_attendance
        WHERE data_split = 'train'
    )))
    FROM ml_features_attendance
    WHERE data_split = 'validation'
    """

    cur.execute(baseline_query)
    baseline_mae = float(cur.fetchone()[0])

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


# ============================================================
# PAGE 1: WHAT HAPPENED?
# ============================================================

if page == "1. What Happened?":

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

    st.bar_chart(opponent_attendance)

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


# ============================================================
# PAGE 2: HOW GOOD ARE THE PREDICTIONS?
# ============================================================

elif page == "2. How Good Are the Predictions?":

    st.header("How Good Are the Predictions?")

    predictions_df = pd.DataFrame(
        prediction_rows,
        columns=prediction_columns
    )

    predictions_df["predicted"] = pd.to_numeric(
        predictions_df["predicted"]
    )

    predictions_df["actual"] = pd.to_numeric(
        predictions_df["actual"]
    )

    predictions_df["error"] = pd.to_numeric(
        predictions_df["error"]
    )

    st.dataframe(predictions_df)

    st.write(
        "Validation and test predictions:",
        len(predictions_df)
    )

    predictions_df["absolute_error"] = (
        predictions_df["error"].abs()
    )

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

    largest_errors["mae_for_split"] = (
        largest_errors["split"].map(mae_by_split)
    )

    largest_errors["error_multiple"] = (
        largest_errors["absolute_error"] /
        largest_errors["mae_for_split"]
    )

    largest_errors["unusual"] = (
        largest_errors["error_multiple"] > 2
    )

    largest_errors["error_multiple"] = (
        largest_errors["error_multiple"].round(1)
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
    st.write(
        "The largest miss was game 745238: attendance was 44,924, "
        "compared with a prediction of approximately 25,789, an "
        "underprediction of 19,135 fans, or 3.3 times the validation MAE. "
        "Promotions, special events, or advance ticket sales could help "
        "explain the difference, but these factors were not included "
        "in the model and have not been verified for this game."
    )


# ============================================================
# PAGE 3: WHAT SHOULD WE DO?
# ============================================================

elif page == "3. What Should We Do?":

    st.header("What Should We Do?")
    st.subheader("Predict Attendance for an Upcoming Home Game")

    model_bundle = joblib.load("model/attendance_model.joblib")
    
    st.subheader("Business Recommendations")

    opponent_history = (
        df.groupby("opponent")["attendance"]
        .agg(["count", "mean"])
        .sort_values("mean", ascending=False)
    )

    top_opponent = opponent_history.index[0]
    top_average = opponent_history.iloc[0]["mean"]
    top_count = int(opponent_history.iloc[0]["count"])

    st.write(
        f"1. Prioritize reviewing advertising opportunities for "
        f"games against the {top_opponent}. These games averaged "
        f"{top_average:,.0f} attendees across {top_count} historical "
        f"games. Check the game dates and sample size before "
        f"assuming this pattern will continue."
    )

    st.write(
        f"2. Present advertisers with an attendance estimate and "
        f"an uncertainty range rather than promising an exact crowd. "
        f"The model's test MAE was "
        f"{model_bundle['test_mae']:,.0f} fans, so use the prediction "
        f"tool's range when discussing potential audience exposure."
    )

    st.write(
        "Limitation: Attendance estimates potential in-stadium "
        "audience size, not verified advertising impressions or "
        "sales. The model also excludes promotions, ticket prices, "
        "and advance ticket sales."
    )

    st.write(
        "Enter information available seven days before the game. "
        "Historical attendance and winning percentage must use "
        "only games completed before that cutoff."
    )

    game_date = st.date_input("Upcoming home-game date")

    opponent = st.selectbox(
        "Opponent",
        options=sorted(
            column.removeprefix("team_name_")
            for column in model_bundle["feature_columns"]
            if column.startswith("team_name_")
        )
    )

    day_night = st.selectbox(
        "Day or night game",
        options=["day", "night"]
    )

    is_holiday = st.checkbox("Game falls on a U.S. holiday")

    recent_attendance = st.number_input(
        "Average attendance at up to five eligible previous home games",
        min_value=0.0,
        value=float(
            model_bundle["training_means"]["rolling_avg_attendance_5"]
        ),
        step=100.0
    )

    winning_percentage = st.number_input(
        "Mariners winning percentage before the prediction cutoff",
        min_value=0.0,
        max_value=1.0,
        value=float(
            model_bundle["training_means"][
                "mariners_win_pct_at_prediction"
            ]
        ),
        step=0.01,
        format="%.3f"
    )

    st.caption(
        "The initial attendance and winning-percentage values are "
        "training-data averages, not current team information. "
        "For early-season games without eligible history, "
        "use those defaults."
    )

    if st.button("Predict Attendance"):

        new_game = pd.DataFrame([{
            "is_weekend": game_date.weekday() >= 5,
            "is_holiday": is_holiday,
            "month": game_date.month,
            "day_night": day_night,
            "team_name": opponent,
            "rolling_avg_attendance_5": recent_attendance,
            "mariners_win_pct_at_prediction": winning_percentage
        }])

        new_game = new_game[model_bundle["features"]]

        encoded_game = pd.get_dummies(new_game, dtype=int)

        encoded_game = encoded_game.reindex(
            columns=model_bundle["feature_columns"],
            fill_value=0
        )

        prediction = float(
            model_bundle["model"].predict(encoded_game)[0]
        )

        test_mae = model_bundle["test_mae"]

        st.metric(
            "Predicted Attendance",
            f"{prediction:,.0f} fans"
        )

        st.write(
            f"Prediction ± test MAE: "
            f"{prediction - test_mae:,.0f} to "
            f"{prediction + test_mae:,.0f} fans."
        )

        st.caption(
            f"The test MAE was {test_mae:,.0f} fans. "
            "This range is a typical-error guide, not a "
            "statistical prediction interval or guarantee."
        )
