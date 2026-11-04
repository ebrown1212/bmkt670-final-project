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
- **model_predictions:** Stores actual attendance, Random Forest predictions, prediction errors, and dataset assignments for all 323 modeling observations.

The database contains 324 home games from the 2022–2025 seasons. One game has missing attendance, leaving 323 observations in the ML feature table.

### Feature Engineering

The initial ML feature table includes two derived features:

- **Five-game rolling attendance average:** Average attendance from up to five previous home games within the same season, using only attendance available before the seven-day prediction cutoff.
- **Days since previous home game:** Number of calendar days since the previous scheduled home game, resetting at the beginning of each season.
- **Mariners winning percentage:** Overall team winning percentage, including home and away games, calculated from completed MLB games before the seven-day prediction cutoff.

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


## Attendance Prediction Models

The project uses 323 Mariners home games with recorded attendance. The models are trained on 2022–2023 games, compared using 2024 validation games, and evaluated on 2025 test games.

Three regression models were compared using Mean Absolute Error (MAE):

| Model | Validation MAE (Fans) |
|---|---:|
| Baseline (Training Average) | 6,725 |
| Linear Regression | 6,812 |
| Decision Tree | 6,318 |
| **Random Forest** | **5,790** |

Random Forest was selected because it produced the lowest validation error. Its final 2025 test MAE was 6,166 fans.

The selected model uses scheduling, opponent, recent attendance, and historical team-performance features. Missing numerical values are filled using averages calculated from the training data only.

The model saves 323 predictions to the PostgreSQL `model_predictions` table, including actual attendance, predicted attendance, error, and dataset assignment.

The exploratory charts and detailed modeling results are documented in `docs/model_report.md`.

## Running the Complete Pipeline

Activate the project's Python virtual environment and ensure PostgreSQL is running.

From the project root directory, run:

```powershell
python .\run_pipeline.py
```

The pipeline executes the following steps in order:

1. Extract Baseball-Reference game data.
2. Extract MLB Stats API schedule data.
3. Extract Meteostat weather data.
4. Transform the data and generate ML features.
5. Rebuild and load the PostgreSQL tables.
6. Run seven automated data-quality checks.
7. Train the attendance models and save predictions to PostgreSQL.

A successful run ends with:

```text
Predictions prepared: 323
Predictions saved to PostgreSQL: 323

Pipeline completed successfully!
```

The pipeline rebuilds the database tables and replaces existing predictions, allowing the workflow to be rerun without creating duplicate records.
