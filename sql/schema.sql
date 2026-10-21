-- Seattle Mariners Attendance Prediction
-- BMKT 670 Final Project
-- Purpose: Define and rebuild the PostgreSQL database schema
-- for historical game data, weather observations, and ML features.

-- Drop existing tables so the schema can be rebuilt.
DROP TABLE IF EXISTS ml_features_attendance CASCADE;
DROP TABLE IF EXISTS fact_weather CASCADE;
DROP TABLE IF EXISTS fact_game CASCADE;
DROP TABLE IF EXISTS dim_venue CASCADE;
DROP TABLE IF EXISTS dim_team CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;


-- One row represents one calendar date.
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    season INTEGER,
    month INTEGER,
    day_of_week TEXT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);


-- One row represents one MLB team.
CREATE TABLE dim_team (
    team_key INTEGER PRIMARY KEY,
    team_id INTEGER UNIQUE,
    team_name TEXT NOT NULL,
    team_abbreviation TEXT
);


-- One row represents one stadium.
CREATE TABLE dim_venue (
    venue_key INTEGER PRIMARY KEY,
    venue_name TEXT NOT NULL,
    city TEXT,
    state TEXT
);


-- One row represents one Seattle Mariners home game.
CREATE TABLE fact_game (
    game_id INTEGER PRIMARY KEY,
    date_key INTEGER REFERENCES dim_date(date_key),
    opponent_key INTEGER REFERENCES dim_team(team_key),
    venue_key INTEGER REFERENCES dim_venue(venue_key),
    attendance INTEGER,
    game_datetime TIMESTAMPTZ,
    day_night TEXT,
    doubleheader TEXT,
    series_game_number INTEGER,
    mariners_result TEXT,
    mariners_score INTEGER,
    opponent_score INTEGER
);


-- One row represents one daily weather observation.
CREATE TABLE fact_weather (
    weather_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_key INTEGER NOT NULL UNIQUE REFERENCES dim_date(date_key),
    avg_temp_f NUMERIC,
    min_temp_f NUMERIC,
    max_temp_f NUMERIC,
    humidity INTEGER,
    precipitation_in NUMERIC,
    wind_speed_mph NUMERIC
);


-- One row per Mariners home game with recorded attendance.
CREATE TABLE ml_features_attendance (
    game_id INTEGER PRIMARY KEY REFERENCES fact_game(game_id),
    date_key INTEGER REFERENCES dim_date(date_key),
    opponent_key INTEGER REFERENCES dim_team(team_key),
    venue_key INTEGER REFERENCES dim_venue(venue_key),
    attendance INTEGER,
    game_datetime TIMESTAMPTZ,
    day_night TEXT,
    doubleheader TEXT,
    series_game_number INTEGER,
    game_date DATE,
    season INTEGER,
    prediction_date DATE,
    rolling_avg_attendance_5 NUMERIC,
    days_since_previous_home_game INTEGER,
    has_attendance_history BOOLEAN,
    month INTEGER,
    day_of_week TEXT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    team_name TEXT,
    data_split TEXT
);
