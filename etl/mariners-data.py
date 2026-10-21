# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Extract Seattle Mariners home-game results and attendance
# from Baseball-Reference for the 2022–2025 seasons.

import pandas as pd

years = [2022, 2023, 2024, 2025]

all_games = []

for year in years:
    url = f"https://www.baseball-reference.com/teams/SEA/{year}-schedule-scores.shtml"

    tables = pd.read_html(url)
    games = tables[0]

    games["Season"] = year

    all_games.append(games)

mariners_games = pd.concat(all_games, ignore_index=True)
mariners_games.to_csv("data/raw/mariners_schedule_raw_2022_2025.csv", index=False)

mariners_games["Gm#"] = pd.to_numeric(mariners_games["Gm#"], errors="coerce")

mariners_games = mariners_games.dropna(subset=["Gm#"])

home_games = mariners_games[mariners_games["Unnamed: 4"].isna()]

print(home_games)

print("\nNumber of home games:", len(home_games))

print("\nHome games by season:")
print(home_games.groupby("Season").size())

home_games.to_csv("data/raw/mariners_home_games_2022_2025.csv", index=False)