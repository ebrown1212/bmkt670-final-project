# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Extract daily Seattle weather observations from Meteostat
# for 2022–2025 and standardize measurements to U.S. units.

from datetime import date
import meteostat as ms

t_mobile_park = ms.Point(47.5914, -122.3325)

stations = ms.stations.nearby(t_mobile_park, limit=5)

print(stations)

weather = ms.daily(
    "KBFI0",
    start=date(2022, 1, 1),
    end=date(2025, 12, 31)
)

weather_df = weather.fetch()

weather_df.to_csv("data/raw/seattle_weather_raw_2022_2025.csv")


weather_df["temp"] = (weather_df["temp"] * 9 / 5) + 32
weather_df["tmin"] = (weather_df["tmin"] * 9 / 5) + 32
weather_df["tmax"] = (weather_df["tmax"] * 9 / 5) + 32
weather_df["prcp"] = weather_df["prcp"] / 25.4
weather_df["wspd"] = weather_df["wspd"] / 1.609

weather_df = weather_df.rename(columns={
    "temp": "avg_temp_f",
    "tmin": "min_temp_f",
    "tmax": "max_temp_f",
    "rhum": "humidity",
    "prcp": "precipitation_in",
    "wspd": "wind_speed_mph"
})

weather_df = weather_df.reset_index()

weather_df = weather_df[[
    "time",
    "avg_temp_f",
    "min_temp_f",
    "max_temp_f",
    "humidity",
    "precipitation_in",
    "wind_speed_mph"
]]

weather_df = weather_df.rename(columns={
    "time": "date"
})

weather_df.to_csv("data/raw/seattle_weather_2022_2025.csv", index=False)

print("\nFinal weather data:")
print(weather_df)

print("\nNumber of rows:", len(weather_df))