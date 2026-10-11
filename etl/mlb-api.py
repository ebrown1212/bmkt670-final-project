import requests
import pandas as pd
import json

years = [2022, 2023, 2024, 2025]

home_games = []

for year in years:
    url = "https://statsapi.mlb.com/api/v1/schedule"

    params = {
        "sportId": 1,
        "teamId": 136,
        "season": year
    }

    response = requests.get(url, params=params)

    data = response.json()
    
    with open(f"data/raw/mlb_schedule_{year}_raw.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    for date in data["dates"]:
        for game in date["games"]:
            if game["gameType"] == "R" and game["teams"]["home"]["team"]["id"] == 136:
                home_games.append({
                    "game_id": game["gamePk"],
                    "season": year,
                    "date": game["officialDate"],
                    "game_datetime": game["gameDate"],
                    "opponent": game["teams"]["away"]["team"]["name"],
                    "venue": game["venue"]["name"],
                    "day_night": game["dayNight"],
                    "doubleheader": game["doubleHeader"],
                    "series_game_number": game["seriesGameNumber"]
                })

mlb_games = pd.DataFrame(home_games)

print(mlb_games)

print("\nNumber of regular season home games:", len(mlb_games))

print("\nHome games by season:")
print(mlb_games.groupby("season").size())

mlb_games.to_csv("data/raw/mlb_schedule_2022_2025.csv", index=False)