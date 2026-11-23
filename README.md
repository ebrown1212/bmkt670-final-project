# Seattle Mariners Attendance Prediction and Advertising Sales Intelligence

## Business Question

How many fans will attend an upcoming Seattle Mariners home game at T-Mobile Park, using information available seven days before the game?

The dashboard is designed for a Mariners advertising sales manager reviewing historical attendance, assessing potential in-stadium audience size, and identifying games that warrant closer review for advertising opportunities.

Attendance is not a measure of verified advertising impressions, advertising revenue, or sales. This academic project has not demonstrated a realized business return.

## Project Overview

Python scripts collect historical data, transform it into analytical tables, load PostgreSQL, run data-quality checks, train attendance models, and generate AI summaries of test-game predictions.

A three-page Streamlit dashboard provides:

1. Historical attendance analysis with a season filter.
2. Model evaluation, baseline comparison, and largest prediction errors.
3. Business recommendations, a future-game prediction tool, and stored AI summaries.

## Data Sources

| Source | Information Used | Access |
|---|---|---|
| Baseball-Reference | Historical home-game attendance, dates, opponents, results, and scores | Schedule tables read with pandas |
| MLB Stats API | Game IDs, schedule information, opponents, venues, day/night designation, and historical team records | Python HTTP requests; original JSON responses retained locally |
| Meteostat | Historical daily Seattle weather observations | Meteostat Python package |

The project covers the 2022–2025 seasons.

Sources:

- Baseball-Reference: https://www.baseball-reference.com/teams/SEA/2025-schedule-scores.shtml
- MLB Stats API: https://statsapi.mlb.com/api/v1/schedule
- Meteostat: https://dev.meteostat.net/python/

Extracted data is saved in `data/raw/`. Transformed data is saved in `data/clean/`. Both folders are excluded from GitHub and created by the pipeline.

Historical observed weather is retained for analysis but is not used by the attendance model. Actual game-day weather would not be known seven days before a game.

## Database Design

The PostgreSQL star schema centers on `fact_game`, with one row per Mariners home game.

| Table | Purpose |
|---|---|
| dim_date | Calendar dates, seasons, months, weekends, and holidays |
| dim_team | Opponent identifiers and names |
| dim_venue | Stadium information |
| fact_game | Game-level attendance, schedule information, results, and scores |
| fact_weather | Daily Seattle weather observations |
| ml_features_attendance | Game-level features and chronological dataset assignments |
| model_predictions | Actual attendance, predictions, signed errors, model name, and split |
| ai_summaries | One stored summary per test game, with its generation timestamp |

The previously verified dataset contains 324 home games. One game has missing attendance and remains in `fact_game` but is excluded from the modeling table, leaving 323 modeling observations.

See `sql/schema.sql` and `docs/field_sources.md` for table definitions and field documentation.

## Features and Prediction Timing

The selected model uses:

- Weekend and U.S. holiday indicators.
- Month.
- Day/night designation.
- Opponent.
- Average attendance at up to five eligible previous home games.
- Mariners overall winning percentage before the prediction cutoff.

Historical attendance and winning-percentage features reset each season and use records dated strictly before the seven-day prediction cutoff.

The feature table also contains scheduling and availability fields that are not all used by the selected model, including days since the previous scheduled home game and an attendance-history indicator.

Missing numerical model inputs are filled using means calculated from training rows only. These means and the encoded feature-column order are saved with the model. Categorical inputs are encoded in Python.

Calendar-date filtering does not independently establish the exact historical availability of every source field or account for every schedule revision.

## Model Evaluation

The datasets are divided chronologically:

| Dataset | Seasons | Games |
|---|---|---:|
| Training | 2022–2023 | 161 |
| Validation | 2024 | 81 |
| Test | 2025 | 81 |
| Total | | 323 |

Mean Absolute Error (MAE) measures the average absolute difference between predicted and actual attendance, in fans.

| Model | Validation MAE, Fans |
|---|---:|
| Baseline: training attendance mean | 6,725 |
| Linear Regression | 6,812 |
| Decision Tree | 6,318 |
| Random Forest | 5,790 |

Random Forest was selected because it had the lowest validation MAE, approximately 13.9% below the baseline. Its separate 2025 test MAE was approximately 6,166 fans.

These are rounded results from the verified project run. The modeling script prints results for each new run.

The model and preprocessing information are saved to `model/attendance_model.joblib`. The pipeline rebuilds this file; it is not committed to GitHub.

See `docs/model_report.md` for exploration, model comparisons, interpretation, and limitations.

## Data Quality

The pipeline checks:

1. Duplicate game IDs.
2. Attendance values outside the defined valid range.
3. Missing attendance targets in the modeling table.
4. Invalid game foreign keys.
5. Games without matching weather dates.
6. Differences between source and loaded game counts.
7. Duplicate weather dates.

A failed check stops subsequent pipeline stages.

Missing attendance targets are excluded from modeling. Missing precipitation remains unknown rather than being replaced with zero. See `docs/missing_data.md`.

## Setup on Windows PowerShell

The project has been developed using Python 3.14, PostgreSQL 18, Git, and Windows PowerShell 5.1.

You need:

- Python 3.14.
- Git.
- A running PostgreSQL server reachable on the default port, 5432.
- A PostgreSQL account allowed to create and load tables in the project database.
- An Anthropic API key with access to the model used by the summary script and sufficient API credit.
- Internet access to the data sources and Anthropic API.

### 1. Clone the Repository

From the folder where you want to keep the project:

```powershell
git clone https://github.com/ebrown1212/bmkt670-final-project.git
Set-Location .\bmkt670-final-project
```

Run all remaining project commands from this repository root.

### 2. Create a Fresh Virtual Environment

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If `py` is unavailable, use your Python 3.14 executable in its place.

### 3. Start PostgreSQL and Create a Database

PostgreSQL must be running before the pipeline connects.

For a standard Windows service installation, start PostgreSQL through Windows Services. On a machine configured for direct startup, run the following in a separate, non-administrator PowerShell window and leave that window open:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\postgres.exe" -D "C:\Program Files\PostgreSQL\18\data"
```

Use the paths appropriate to your installation. Do not attempt direct startup if that PostgreSQL instance is already running.

In your project terminal, check connectivity:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_isready.exe" -h localhost -p 5432
```

The expected result is `accepting connections`.

Create a new, dedicated database:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -h localhost -p 5432 -U postgres mariners_analytics
```

Enter your PostgreSQL password when prompted. Replace `postgres` with your PostgreSQL username if different.

Database creation is a one-time step. The Python loader creates tables inside the existing database; it does not create the database itself.

For a fresh-clone verification alongside an existing project, use a separate database name such as `mariners_analytics_verify` in both the creation command and `.env`.

### 4. Configure Environment Variables

Copy the blank template:

```powershell
Copy-Item .\.env.example .\.env
notepad .\.env
```

Fill in your local values:

```text
DB_HOST=localhost
DB_NAME=mariners_analytics
DB_USER=your_postgresql_username
DB_PASSWORD=your_postgresql_password
ANTHROPIC_API_KEY=your_anthropic_api_key
```

If you created a verification database, use its name for `DB_NAME`.

Save the file. Never commit `.env`, display it in a recording, or share its contents. `.env.example` contains variable names with blank values and is safe to commit.

## Run the Complete Pipeline

With the virtual environment activated and PostgreSQL running:

```powershell
python .\run_pipeline.py
```

The pipeline:

1. Creates the required output folders.
2. Extracts Baseball-Reference data.
3. Extracts MLB Stats API data.
4. Extracts Meteostat weather data.
5. Transforms data and constructs historical features.
6. Rebuilds and loads PostgreSQL tables.
7. Runs seven data-quality checks.
8. Trains models, saves predictions, and saves the selected model bundle.
9. Generates and stores AI summaries for all test games.

A successful run ends with:

```text
Pipeline completed successfully!
```

The pipeline rebuilds project tables in the database named in `.env`, replacing existing project data, predictions, and summaries. Use a dedicated database.

Each full run makes new Anthropic API calls. The previously measured 81-game summary run had an estimated token cost of approximately $0.046 at the rates documented in `docs/dashboard_notes.md`. Actual usage and pricing can differ.

If a stage fails, the pipeline stops. It does not undo earlier completed stages. Review the reported error before rerunning.

Public source availability and website changes can affect extraction.

## Run the Dashboard

Run the pipeline first so the database tables and saved model exist.

```powershell
python -m streamlit run .\dashboard\app.py
```

Open the local URL printed in the terminal, normally:

```text
http://localhost:8501
```

Keep PostgreSQL and Streamlit running while using the dashboard.

Charts and tables read PostgreSQL data. The future-game tool loads the saved model and applies the saved feature encoding. AI summaries are read from PostgreSQL; opening the dashboard does not make Anthropic API calls.

Interact with the dashboard or refresh it after a pipeline rerun to load updated results.

## Using the Prediction Tool

Enter a future-game scenario using information available seven days before the game.

The attendance-history and winning-percentage defaults are training-data means, not current team information. Replace them with eligible historical values when available.

The displayed range is prediction plus or minus test MAE. It is a typical-error guide, not a statistical prediction interval or guarantee.

## AI Summaries

`ai/generate_summaries.py` sends one request per test game to Claude Haiku 4.5 using game facts, predicted attendance, actual attendance, and Python-calculated error direction and size.

Summaries are saved in `ai_summaries`. Rerunning the summary script updates existing game IDs rather than adding duplicate summaries, but makes new API calls.

Three saved summaries were checked against source facts. An earlier prompt produced an incorrect percentage; the revised prompt prohibits added statistics and uses Python-calculated errors.

Checking three examples does not establish that all summaries are correct. Summaries describe historical prediction results and do not establish causes of attendance or explain model behavior.

## Repository Guide

| Location | Contents |
|---|---|
| README.md | Project overview and setup/run instructions |
| requirements.txt | Python dependencies |
| .env.example | Blank environment-variable template |
| run_pipeline.py | Sequential pipeline runner |
| db_check.py | Database connectivity and table-list check |
| etl/ | Extraction, transformation, loading, and quality checks |
| sql/schema.sql | PostgreSQL table definitions |
| model/ | Training script and locally generated model bundle |
| ai/ | API-based summary generation |
| dashboard/ | Streamlit application |
| docs/data_flow.png | Data-flow diagram |
| docs/field_sources.md | Field definitions and sources |
| docs/missing_data.md | Missing-data findings and handling |
| docs/model_report.md | Modeling results and interpretation |
| docs/dashboard_notes.md | Dashboard purpose, AI prompt, validation, and cost |
| docs/figures/ | Exploratory charts |
| data/raw/ | Generated source extracts; ignored by Git |
| data/clean/ | Generated transformed tables; ignored by Git |

## Limitations and Next Improvement

The model uses a small historical dataset and excludes promotions, ticket prices, and advance ticket sales. Historical opponent averages are descriptive associations and may involve small sample sizes.

Predicted attendance estimates potential audience size. It does not directly measure advertising exposure, conversions, or revenue.

A useful next improvement would be adding verified promotional schedules, investigating large misses, and evaluating whether the additional information improves future predictions.