# Seattle Mariners Home Game Attendance Prediction

## Business Question

How many fans will attend an upcoming Seattle Mariners home game at T-Mobile Park?

## Target Variable

Game attendance, measured as the number of fans attending each home game.

## Prediction Unit

One row in my ML feature table = one Seattle Mariners home game.

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

All three datasets are collected using Python and saved as CSV files in `data/raw/`.

## Database Design

The project uses a PostgreSQL star schema centered around `fact_game`, with one row representing each Seattle Mariners home game.

The planned database includes:

- **dim_date:** Game dates and calendar information.
- **dim_team:** Team and opponent information.
- **dim_venue:** Stadium information.
- **fact_game:** Game-level information, including attendance, results, and pregame performance.
- **fact_weather:** Daily weather observations associated with game dates.

A separate `ml_features_attendance` table will combine relevant game, calendar, opponent, historical attendance, pregame performance, and weather variables for predictive modeling. This table will be developed in a later stage.

## How to Run

1. Create a Python virtual environment using `python -m venv .venv`.
2. Activate the environment in PowerShell using `.\.venv\Scripts\Activate.ps1`.
3. Install the required packages using `pip install -r requirements.txt`.
4. Create a `.env` file containing the required database credentials. Do not commit this file to GitHub.
5. Run the extraction scripts in the `etl/` folder to retrieve the raw datasets.
6. Run `sql/schema.sql` in pgAdmin or psql to create the PostgreSQL database tables.
7. Run `python db_check.py` to verify the database connection and display the created tables.

The extraction scripts, database schema, and database verification script will be finalized during project development.

## AI Usage

ChatGPT was used to assist with project planning, repository setup, Python development, debugging, and code review. AI-generated code will be reviewed, tested, and validated before being incorporated into the project. Business questions, database design, feature selection, and interpretation of results remain my responsibility.