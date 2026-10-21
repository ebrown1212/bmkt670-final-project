# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Clean and combine Mariners game, MLB API, and weather data
# into PostgreSQL-ready tables and attendance prediction features.

import json

import holidays
import pandas as pd

baseball_reference = pd.read_csv("data/raw/mariners_home_games_2022_2025.csv")
mlb_api = pd.read_csv("data/raw/mlb_schedule_2022_2025.csv")
weather = pd.read_csv("data/raw/seattle_weather_2022_2025.csv")

baseball_reference["clean_date"] = baseball_reference["Date"].str.replace(
    r" \(\d\)", "", regex=True
)

baseball_reference["game_date"] = pd.to_datetime(
    baseball_reference["clean_date"] + ", " + baseball_reference["Season"].astype(str)
)

mlb_api["game_date"] = pd.to_datetime(mlb_api["date"])

baseball_reference["date_game_number"] = (
    baseball_reference.groupby("game_date").cumcount() + 1
)

mlb_api["date_game_number"] = (
    mlb_api.groupby("game_date").cumcount() + 1
)

games = baseball_reference.merge(
    mlb_api,
    on=["game_date", "date_game_number"],
    how="inner",
    validate="one_to_one"
)

print("Matched games:", len(games))
print("Unique MLB game IDs:", games["game_id"].nunique())
print("Missing attendance:", games["Attendance"].isna().sum())


weather["date"] = pd.to_datetime(weather["date"])

all_dates = pd.concat([
    games["game_date"],
    weather["date"]
]).drop_duplicates().sort_values()

dim_date = pd.DataFrame({
    "full_date": all_dates
})

dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["season"] = dim_date["full_date"].dt.year
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["day_of_week"] = dim_date["full_date"].dt.day_name()
dim_date["is_weekend"] = dim_date["full_date"].dt.dayofweek >= 5
us_holidays = holidays.US(years=range(2022, 2026))

dim_date["is_holiday"] = dim_date["full_date"].dt.date.isin(us_holidays)

dim_date = dim_date[[
    "date_key",
    "full_date",
    "season",
    "month",
    "day_of_week",
    "is_weekend",
    "is_holiday"
]]

dim_date.to_csv("data/clean/dim_date.csv", index=False)

print("\ndim_date rows:", len(dim_date))
print(dim_date.head())


team_names = games[["opponent", "Opp"]].drop_duplicates().copy()

team_names["opponent"] = team_names["opponent"].replace({
    "Oakland Athletics": "Athletics"
})

dim_team = team_names.drop_duplicates(subset=["opponent"]).reset_index(drop=True)

dim_team["team_key"] = dim_team.index + 1
team_ids = {}

for year in range(2022, 2026):
    with open(f"data/raw/mlb_schedule_{year}_raw.json", encoding="utf-8") as file:
        data = json.load(file)

    for day in data["dates"]:
        for game in day["games"]:
            if game["teams"]["home"]["team"]["id"] == 136:
                team = game["teams"]["away"]["team"]
                team_name = team["name"]

                if team_name == "Oakland Athletics":
                    team_name = "Athletics"

                team_ids[team_name] = team["id"]

dim_team["team_id"] = dim_team["opponent"].map(team_ids)

print("Missing MLB team IDs:", dim_team["team_id"].isna().sum())
print("Duplicate MLB team IDs:", dim_team["team_id"].duplicated().sum())

dim_team = dim_team.rename(columns={
    "opponent": "team_name",
    "Opp": "team_abbreviation"
})

dim_team = dim_team[[
    "team_key",
    "team_id",
    "team_name",
    "team_abbreviation"
]]

dim_team.to_csv("data/clean/dim_team.csv", index=False)

print("\ndim_team rows:", len(dim_team))
print(dim_team.head())



dim_venue = games[["venue"]].drop_duplicates().reset_index(drop=True)

dim_venue["venue_key"] = dim_venue.index + 1
dim_venue["city"] = "Seattle"
dim_venue["state"] = "Washington"

dim_venue = dim_venue.rename(columns={
    "venue": "venue_name"
})

dim_venue = dim_venue[[
    "venue_key",
    "venue_name",
    "city",
    "state"
]]

dim_venue.to_csv("data/clean/dim_venue.csv", index=False)

print("\ndim_venue rows:", len(dim_venue))
print(dim_venue)


games["opponent"] = games["opponent"].replace({
    "Oakland Athletics": "Athletics"
})

fact_game = games.merge(
    dim_team[["team_key", "team_name"]],
    left_on="opponent",
    right_on="team_name",
    how="left",
    validate="many_to_one"
)

fact_game = fact_game.merge(
    dim_venue[["venue_key", "venue_name"]],
    left_on="venue",
    right_on="venue_name",
    how="left",
    validate="many_to_one"
)

fact_game["date_key"] = fact_game["game_date"].dt.strftime("%Y%m%d").astype(int)

fact_game = fact_game.rename(columns={
    "Attendance": "attendance",
    "W/L": "mariners_result",
    "R": "mariners_score",
    "RA": "opponent_score"
})

fact_game["mariners_result"] = fact_game["mariners_result"].str[0]

fact_game = fact_game[[
    "game_id",
    "date_key",
    "team_key",
    "venue_key",
    "attendance",
    "game_datetime",
    "day_night",
    "doubleheader",
    "series_game_number",
    "mariners_result",
    "mariners_score",
    "opponent_score"
]]

fact_game = fact_game.rename(columns={
    "team_key": "opponent_key"
})

fact_game["attendance"] = fact_game["attendance"].astype("Int64")

fact_game.to_csv("data/clean/fact_game.csv", index=False)

print("\nfact_game rows:", len(fact_game))
print("Missing opponent keys:", fact_game["opponent_key"].isna().sum())
print("Missing venue keys:", fact_game["venue_key"].isna().sum())
print("Missing attendance:", fact_game["attendance"].isna().sum())
print(fact_game.head())


fact_weather = weather.copy()

fact_weather["date_key"] = fact_weather["date"].dt.strftime("%Y%m%d").astype(int)

fact_weather = fact_weather[[
    "date_key",
    "avg_temp_f",
    "min_temp_f",
    "max_temp_f",
    "humidity",
    "precipitation_in",
    "wind_speed_mph"
]]

fact_weather.to_csv("data/clean/fact_weather.csv", index=False)

print("\nfact_weather rows:", len(fact_weather))
print("Unique weather dates:", fact_weather["date_key"].nunique())
print("\nMissing weather values:")
print(fact_weather.isna().sum())


# Calculate historical attendance available seven days before each game.
ml_features = fact_game.copy()

ml_features["game_date"] = pd.to_datetime(
    ml_features["date_key"].astype(str), format="%Y%m%d"
)

ml_features["season"] = ml_features["game_date"].dt.year
ml_features["prediction_date"] = ml_features["game_date"] - pd.Timedelta(days=7)

ml_features = ml_features.sort_values(
    ["game_date", "game_datetime", "game_id"]
).reset_index(drop=True)

rolling_averages = []

for _, game in ml_features.iterrows():
    previous_games = ml_features[
        (ml_features["season"] == game["season"]) &
        (ml_features["game_date"] < game["prediction_date"]) &
        (ml_features["attendance"].notna())
    ]

    previous_five = previous_games.tail(5)

    rolling_averages.append(
        previous_five["attendance"].mean()
    )

ml_features["rolling_avg_attendance_5"] = rolling_averages

print("\nRolling attendance feature:")
print(ml_features[[
    "game_id",
    "game_date",
    "prediction_date",
    "attendance",
    "rolling_avg_attendance_5"
]].head(15))

print(
    "\nMissing rolling averages:",
    ml_features["rolling_avg_attendance_5"].isna().sum()
)


# Calculate days since the previous scheduled home game.
ml_features["previous_home_game"] = (
    ml_features.groupby("season")["game_date"].shift(1)
)

ml_features["days_since_previous_home_game"] = (
    ml_features["game_date"] - ml_features["previous_home_game"]
).dt.days

print("\nDays since previous home game:")
print(ml_features[[
    "game_id",
    "game_date",
    "previous_home_game",
    "days_since_previous_home_game"
]].head(15))

print(
    "\nMissing previous-game gaps:",
    ml_features["days_since_previous_home_game"].isna().sum()
)


# Identify games with available historical attendance.
ml_features["has_attendance_history"] = (
    ml_features["rolling_avg_attendance_5"].notna()
)

# Use zero to identify the first home game of each season.
ml_features["days_since_previous_home_game"] = (
    ml_features["days_since_previous_home_game"].fillna(0).astype(int)
)

# Add calendar and opponent information.
ml_features = ml_features.merge(
    dim_date[["date_key", "month", "day_of_week", "is_weekend", "is_holiday"]],
    on="date_key",
    how="left",
    validate="many_to_one"
)

ml_features = ml_features.merge(
    dim_team[["team_key", "team_name"]],
    left_on="opponent_key",
    right_on="team_key",
    how="left",
    validate="many_to_one"
)

# Assign chronological training, validation, and testing groups.
ml_features["data_split"] = ml_features["season"].map({
    2022: "train",
    2023: "train",
    2024: "validation",
    2025: "test"
})

# Remove the game without a known attendance target.
ml_features = ml_features.dropna(subset=["attendance"]).copy()

# Remove fields that are not needed in the ML dataset.
ml_features = ml_features.drop(columns=[
    "previous_home_game",
    "team_key",
    "mariners_result",
    "mariners_score",
    "opponent_score"
])

ml_features.to_csv(
    "data/clean/ml_features_attendance.csv",
    index=False
)

print("\nML feature table rows:", len(ml_features))
print("\nData split counts:")
print(ml_features["data_split"].value_counts())

print("\nMissing ML feature values:")
print(ml_features.isna().sum()[ml_features.isna().sum() > 0])
