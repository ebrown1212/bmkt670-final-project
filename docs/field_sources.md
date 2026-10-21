# Seattle Mariners Attendance Prediction
## Field Sources and Data Dictionary

This document identifies the source, population method, and purpose of every field in the PostgreSQL database. The project uses Seattle Mariners home-game data from 2022 through 2025.

## dim_date

One row represents one calendar date.

| Field | Source | How It Is Populated | Purpose |
|---|---|---|---|
| date_key | Calculated in Python | Date formatted as YYYYMMDD | Primary key; connects games and weather |
| full_date | MLB Stats API / Meteostat | Calendar date from the project date range | Matches records by calendar date |
| season | Calculated in Python | Extract year from full_date | Historical season comparisons |
| month | Calculated in Python | Extract month from full_date | Seasonal attendance patterns |
| day_of_week | Calculated in Python | Determine weekday from full_date | Weekday attendance patterns |
| is_weekend | Calculated in Python | TRUE for Saturday or Sunday | Weekend attendance patterns |
| is_holiday | Calculated in Python | Compare dates against U.S. holidays | Holiday attendance patterns |

## dim_team

One row represents one MLB opponent team appearing in the Mariners home-game data.

| Field | Source | How It Is Populated | Purpose |
|---|---|---|---|
| team_key | Calculated in Python | Unique identifier assigned to each team | Primary key |
| team_id | MLB Stats API | Official MLB team identifier | Identifies teams across API records |
| team_name | MLB Stats API | Opponent name from schedule data | Identifies the opponent |
| team_abbreviation | Baseball-Reference | Opponent abbreviation | Matches teams across sources |

## dim_venue

One row represents one stadium.

| Field | Source | How It Is Populated | Purpose |
|---|---|---|---|
| venue_key | Created in Python | Unique identifier assigned to each stadium | Primary key |
| venue_name | MLB Stats API | Venue name from schedule data | Identifies the stadium |
| city | Venue information | Seattle | Stadium location |
| state | Venue information | Washington | Stadium location |

## fact_game

One row represents one Seattle Mariners home game.

| Field | Source | How It Is Populated | Purpose |
|---|---|---|---|
| game_id | MLB Stats API | Official MLB game ID | Primary key |
| date_key | Joined | Match MLB game date to dim_date | Foreign key |
| opponent_key | Joined | Match opponent to dim_team | Foreign key |
| venue_key | Joined | Match game venue to dim_venue | Foreign key |
| attendance | Baseball-Reference | Attendance associated with each home game | Prediction target |
| game_datetime | MLB Stats API | Game datetime in UTC | Scheduled game time |
| day_night | MLB Stats API | Day/night designation | Potential prediction feature |
| doubleheader | MLB Stats API | Doubleheader designation | Potential prediction feature |
| series_game_number | MLB Stats API | Game number within a series | Potential prediction feature |
| mariners_result | Baseball-Reference | Historical win/loss result | Historical team performance |
| mariners_score | Baseball-Reference | Mariners runs scored | Historical performance calculations |
| opponent_score | Baseball-Reference | Opponent runs scored | Historical performance calculations |

## fact_weather

One row represents one daily weather observation.

| Field | Source | How It Is Populated | Purpose |
|---|---|---|---|
| weather_id | PostgreSQL | Automatically generated identity value | Primary key |
| date_key | Joined | Match weather date to dim_date | Foreign key; unique daily observation |
| avg_temp_f | Meteostat | Convert Celsius to Fahrenheit | Historical weather analysis |
| min_temp_f | Meteostat | Convert Celsius to Fahrenheit | Historical weather analysis |
| max_temp_f | Meteostat | Convert Celsius to Fahrenheit | Historical weather analysis |
| humidity | Meteostat | Relative humidity percentage | Historical weather analysis |
| precipitation_in | Meteostat | Convert millimeters to inches | Historical weather analysis |
| wind_speed_mph | Meteostat | Convert km/h to mph | Historical weather analysis |

## ml_features_attendance

One row represents one Seattle Mariners home game with a recorded attendance target.

This table combines game information