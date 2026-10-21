# Seattle Mariners Home Game Attendance Prediction

## Business Question

How many fans will attend an upcoming Seattle Mariners home game at T-Mobile Park?

## Target Variable

Game attendance, measured as the number of fans attending each home game.

## Prediction Unit

One row in my ML feature table = one Seattle Mariners home game.

The model is intended to predict attendance seven days before each game.

## Business Decisions Supported

- Estimate potential in-stadium advertising exposure to support advertising sales negotiations.
- Improve revenue forecasting based on expected game attendance.
- Support demand for future capital investments based on expected and historical attendance patterns.

## Data Sources

### 1. Baseball-Reference

Historical Seattle Mariners game data from the 2022–2025 seasons.

**Data collected:** Game dates, opponents, attendance, results, team records, standings, and streaks.

**Access:** Python extraction from publicly available schedule and results tables.

**Source:** https://www.baseball-reference.com/teams/SEA/2025-schedule-scores.shtml

### 2. MLB Stats API

Historical MLB schedule data for Seattle Mariners home games from 2022–2025.

**Data collected:** Game IDs, dates, scheduled start times, opponents, venues, day/night designation, doubleheader status, and series game numbers.

**Access:** Python requests to the MLB Stats API.

**Source:** https://statsapi.mlb.com/api/v1/schedule

### 3. Meteostat

Historical daily weather observations for Seattle from 2022–2025.

**Data collected:** Temperature, humidity, precipitation, and wind speed.

**Access:** Meteostat Python package.

**Source:** https://dev.meteostat.net/python/

All three datasets are collected using Python and saved in `data/raw/`. The MLB API extraction also saves the original JSON responses.

## Database Design

The project uses a PostgreSQL star schema centered around `fact_game`, with one row representing each Seattle Mariners home game.

The database includes:

- **dim_date:** Game dates and calendar information.
- **dim_team:** Team and opponent information.
- **dim_venue:** Stadium information.
- **fact_game:** Game-level information, including attendance, results, and scores.
- **fact_weather:** Daily weather observations for Seattle.
- **ml_features_attendance:** Game-level features used to predict attendance, including opponent, calendar information, historical attendance, and scheduling variables.

The database contains 324 home games from the 2022–2025 seasons. One game has missing attendance, leaving 323 observations in the ML feature table.

### Feature Engineering

The initial ML feature table includes two derived features:

- **Five-game rolling attendance average:** Average attendance from up to five previous home games within the same season, using only attendance available before the seven-day prediction cutoff.
- **Days since previous home game:** Number of calendar days since the previous scheduled home game, resetting at the beginning of each season.

The rolling attendance average is missing for 28 games without eligible historical attendance. These values are preserved as NULL, with a separate indicator identifying whether attendance history is available.

Opponent and day-of-week categories are stored as text in PostgreSQL. Categorical encoding will be performed in Python during the modeling stage.

Actual game-day precipitation is excluded from the initial seven-day-ahead prediction features because it would not be known when the prediction is made.

### Training, Validation, and Testing

The data is divided chronologically to evaluate predictions on later seasons:

| Dataset | Seasons | Games |
|---|---|---|
| Training | 2022–2023 | 161 |
| Validation | 2024 | 81 |
| Testing | 2025 | 81 |
| **Total** | | **323** |

## Data Quality

The project includes seven automated data-quality checks:

1. No duplicate game IDs.
2. Attendance values within the defined