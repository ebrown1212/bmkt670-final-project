# Missing Data Decisions

## Seattle Mariners Attendance Prediction (2022–2025)

This document records the missing-data findings and handling decisions for the transformed datasets.

### Missing-Data Summary

| Table | Column | Missing Records | Missing Percentage | Handling Decision |
|---|---|---:|---:|---|
| fact_game | attendance | 1 of 324 | 0.31% | Preserve as NULL in PostgreSQL; exclude from model training and evaluation |
| fact_weather | precipitation_in | 546 of 1,461 | 37.37% | Preserve as NULL; do not impute |

### Attendance

One attendance value is missing for the October 4, 2022, first game against the Detroit Tigers.

The game will remain in `fact_game` because its date, opponent, result, and other information are available.

The missing attendance will not be replaced with an estimate because attendance is the target variable. Inventing a target value could introduce errors into model training and evaluation.

The ML feature table will exclude this observation, leaving 323 games with recorded attendance.

### Precipitation

The Meteostat dataset contains 546 missing precipitation measurements across 1,461 daily observations.

Of the 324 Mariners home games, 94 occurred on dates with missing precipitation observations.

Missing precipitation is not equivalent to zero rainfall. Replacing missing observations with zero would incorrectly classify unknown conditions as dry weather.

These values will remain NULL in PostgreSQL.

Because the project predicts attendance seven days before each game, actual game-day precipitation will not be used as an initial predictive feature. Historical observed weather will remain available for descriptive analysis.

### Prediction Timing and Data Leakage

The model will predict attendance seven days before each scheduled Mariners home game.

Only information available by that prediction date will be eligible for model features.

Historical game results may be used to calculate team performance and attendance trends, but games occurring after the prediction cutoff will be excluded from those calculations.

Actual game-day weather observations will not be used as predictive features.

### Validation

The transformation and data-quality pipeline will verify that:

- All 324 historical home games are retained in `fact_game`.
- The ML feature table contains only records with known attendance.
- Missing precipitation values remain NULL.
- All game and weather date keys match valid records in `dim_date`.
- No duplicate game IDs are introduced during transformation.