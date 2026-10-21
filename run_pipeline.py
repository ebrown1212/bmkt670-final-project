# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Run data extraction, transformation, PostgreSQL loading,
# and automated quality checks in sequence with one command.

import subprocess
import sys

steps = [
    ("Extract Baseball-Reference data", "etl/mariners-data.py"),
    ("Extract MLB API data", "etl/mlb-api.py"),
    ("Extract weather data", "etl/weather-data.py"),
    ("Transform data", "etl/transform.py"),
    ("Load PostgreSQL", "etl/load.py"),
    ("Run quality checks", "etl/quality_checks.py")
]

for name, script in steps:
    print(f"\nRunning: {name}", flush=True)

    subprocess.run(
        [sys.executable, script],
        check=True
    )

print("\nPipeline completed successfully!")
