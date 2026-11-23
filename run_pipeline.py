import os
import subprocess
import sys

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/clean", exist_ok=True)
os.makedirs("docs/figures", exist_ok=True)

steps = [
    ("Extract Baseball-Reference data", "etl/mariners-data.py"),
    ("Extract MLB API data", "etl/mlb-api.py"),
    ("Extract weather data", "etl/weather-data.py"),
    ("Transform data", "etl/transform.py"),
    ("Load PostgreSQL", "etl/load.py"),
    ("Run quality checks", "etl/quality_checks.py"),
    ("Train attendance models", "model/train_model.py"),
    ("Generate AI summaries", "ai/generate_summaries.py")
]

for name, script in steps:
    print(f"\nRunning: {name}", flush=True)

    subprocess.run(
        [sys.executable, script],
        check=True
    )

print("\nPipeline completed successfully!")