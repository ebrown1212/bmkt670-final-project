# Seattle Mariners Attendance Prediction
# BMKT 670 Final Project
# Purpose: Train and evaluate attendance prediction models.

import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

query = "SELECT * FROM public.ml_features_attendance"

df = pd.read_sql_query(query, conn)

conn.close()

print("Total ML observations:", len(df))
print("\nData split counts:")
print(df["data_split"].value_counts())

train = df[df["data_split"] == "train"]
validate = df[df["data_split"] == "validation"]
test = df[df["data_split"] == "test"]

print("\nTraining rows:", len(train))
print("Validation rows:", len(validate))
print("Testing rows:", len(test))

plt.figure(figsize=(10, 6))
plt.hist(train["attendance"], bins=10, edgecolor="black")

plt.title("Seattle Mariners Home Game Attendance (2022–2023)")
plt.xlabel("Attendance")
plt.ylabel("Number of Games")

plt.tight_layout()
plt.savefig("docs/figures/attendance_distribution.png")
plt.close()

print("\nAttendance histogram saved.")

weekend_attendance = train.groupby("is_weekend")["attendance"].mean()

plt.figure(figsize=(8, 6))
plt.bar(
    ["Weekday", "Weekend"],
    [
        weekend_attendance[False],
        weekend_attendance[True]
    ]
)

plt.title("Mariners Average Attendance: Weekday vs Weekend (2022–2023)")
plt.xlabel("Game Type")
plt.ylabel("Average Attendance")

plt.tight_layout()
plt.savefig("docs/figures/weekend_attendance.png")
plt.close()

print("Weekend attendance chart saved.")

win_pct_data = train.dropna(subset=["mariners_win_pct_at_prediction"])

plt.figure(figsize=(10, 6))
plt.scatter(
    win_pct_data["mariners_win_pct_at_prediction"],
    win_pct_data["attendance"],
    alpha=0.6
)

plt.title("Mariners Winning Percentage vs Attendance (2022–2023)")
plt.xlabel("Mariners Winning Percentage at Prediction Date")
plt.ylabel("Attendance")

plt.tight_layout()
plt.savefig("docs/figures/winning_pct_attendance.png")
plt.close()

print("Winning percentage chart saved.")

baseline_prediction = train["attendance"].mean()

baseline_mae = (
    validate["attendance"] - baseline_prediction
).abs().mean()

print("\nBaseline prediction:", round(baseline_prediction, 0))
print("Baseline validation MAE:", round(baseline_mae, 0))

numeric_features = [
    "rolling_avg_attendance_5",
    "mariners_win_pct_at_prediction"
]

train = train.copy()
validate = validate.copy()
test = test.copy()

for feature in numeric_features:
    training_mean = train[feature].mean()

    train[feature] = train[feature].fillna(training_mean)
    validate[feature] = validate[feature].fillna(training_mean)
    test[feature] = test[feature].fillna(training_mean)

    print(f"\n{feature} training mean: {training_mean:.3f}")

print("\nMissing values after imputation:")
print(train[numeric_features].isna().sum())
print(validate[numeric_features].isna().sum())
print(test[numeric_features].isna().sum())

print("\nTraining data types:")
print(train.dtypes)

features = [
    "is_weekend",
    "is_holiday",
    "month",
    "day_night",
    "team_name",
    "rolling_avg_attendance_5",
    "mariners_win_pct_at_prediction"
]

X_train = pd.get_dummies(train[features], dtype=int)
X_validate = pd.get_dummies(validate[features], dtype=int)

X_validate = X_validate.reindex(
    columns=X_train.columns,
    fill_value=0
)

y_train = train["attendance"]
y_validate = validate["attendance"]

print("\nTraining features:", X_train.shape)
print("Validation features:", X_validate.shape)
print("Training target:", y_train.shape)
print("Validation target:", y_validate.shape)


linear_model = LinearRegression()

linear_model.fit(X_train, y_train)

linear_predictions = linear_model.predict(X_validate)

linear_mae = mean_absolute_error(y_validate, linear_predictions)

print("\nLinear Regression Validation MAE:", round(linear_mae, 0))


tree_model = DecisionTreeRegressor(
    max_depth=5,
    random_state=42
)

tree_model.fit(X_train, y_train)

tree_predictions = tree_model.predict(X_validate)

tree_mae = mean_absolute_error(y_validate, tree_predictions)

print("\nDecision Tree Validation MAE:", round(tree_mae, 0))

forest_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=5,
    random_state=42
)

forest_model.fit(X_train, y_train)

forest_predictions = forest_model.predict(X_validate)

forest_mae = mean_absolute_error(y_validate, forest_predictions)

print("\nRandom Forest Validation MAE:", round(forest_mae, 0))

print("\nTraining vs Validation MAE:")

for name, model in [
    ("Linear Regression", linear_model),
    ("Decision Tree", tree_model),
    ("Random Forest", forest_model)
]:
    training_predictions = model.predict(X_train)
    training_mae = mean_absolute_error(y_train, training_predictions)

    validation_predictions = model.predict(X_validate)
    validation_mae = mean_absolute_error(y_validate, validation_predictions)

    print(
        f"{name}: Training MAE = {training_mae:.0f}, "
        f"Validation MAE = {validation_mae:.0f}"
    )
    
    X_test = pd.get_dummies(test[features], dtype=int)

X_test = X_test.reindex(
    columns=X_train.columns,
    fill_value=0
)

y_test = test["attendance"]

test_predictions = forest_model.predict(X_test)

test_mae = mean_absolute_error(y_test, test_predictions)

print("\nRandom Forest Test MAE:", round(test_mae, 0))

feature_importance = pd.Series(
    forest_model.feature_importances_,
    index=X_train.columns
).sort_values(ascending=False)

print("\nTop 10 Random Forest Features:")
print(feature_importance.head(10))