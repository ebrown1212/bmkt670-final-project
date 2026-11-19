# Missing Data Decisions

## Seattle Mariners Attendance Prediction (2022–2025)

This document records the missing-data findings and handling decisions for the transformed datasets.

## Missing-Data Summary

| Table | Column | Missing Records | Missing Percentage | Handling Decision |
|---|---|---:|---:|---|
| fact_game | attendance | 1 of 324 | 0.31% | Preserve as NULL in PostgreSQL; exclude from ML feature table |
| fact_weather | precipitation_in | 546 of 1,461 | 37.37% | Preserve as NULL; do not impute |
| ml_features_attendance | rolling_avg_attendance_5 | 28 of 323 | 8.67% | Preserve as NULL and retain a historical-attendance availability indicator |

## Attendance

One attendance value is missing for the October 4, 2022, first game against the Detroit Tigers.

The game remains in `fact_game` because its date, opponent, result, and other information are available.

The missing attendance was not replaced with an estimate because attendance is the target variable. Inventing a target value could introduce errors into model training and evaluation.

The ML feature table excludes this observation, leaving 323 games with recorded attendance.

## Precipitation

The Meteostat dataset contains 546 missing precipitation measurements across 1,461 daily observations.

Of the 324 Mariners home games, 94 occurred on dates with missing precipitation observations.

Missing precipitation is not equivalent to zero rainfall. Replacing missing observations with zero would incorrectly classify unknown conditions as dry weather.

These values remain NULL in PostgreSQL.

Because the project predicts attendance seven days before each game, actual game-day precipitation is not included in the initial predictive features. Historical observed weather remains available for descriptive analysis.

## Rolling Attendance Average

The ML feature table contains 28 missing values for `rolling_avg_attendance_5`.

This feature uses up to five previous Mariners home games with attendance information available before the seven-day prediction cutoff. The calculation resets at the beginning of each season.

Missing values occur when there is insufficient eligible attendance history to calculate the feature.

Rather than filling these values with zero or an estimated attendance figure, they remain NULL in PostgreSQL.

The feature table also includes `has_attendance_history`, which identifies whether a rolling attendance average is available.

During modeling, missing rolling-attendance and winning-percentage values are filled using their respective training-set means. Those same means are applied to validation and test rows and saved with the model for dashboard predictions. The PostgreSQL values remain NULL.

## Days Since Previous Home Game

The `days_since_previous_home_game` feature calculates the number of calendar days between scheduled Mariners home games.

The calculation resets at the beginning of each season.
