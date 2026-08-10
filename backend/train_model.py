# ============================================================
# AI BASED REAL-TIME TRAFFIC VOLUME PREDICTION SYSTEM
# Model Training using UCI Metro Interstate Traffic Dataset
# ============================================================

import os
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split


warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = os.path.join(
    "dataset",
    "Metro_Interstate_Traffic_Volume.csv"
)

MODEL_PATH = "model.pkl"

FEATURE_PATH = "model_features.pkl"

RANDOM_STATE = 42


# ============================================================
# START
# ============================================================

print()
print("=" * 65)
print("       AI TRAFFIC VOLUME PREDICTION SYSTEM")
print("=" * 65)
print()


# ============================================================
# CHECK DATASET
# ============================================================

if not os.path.exists(DATASET_PATH):

    print("ERROR: Dataset not found!")
    print()
    print("Expected location:")
    print(
        DATASET_PATH
    )
    print()

    print(
        "Make sure the CSV file is inside:"
    )

    print(
        "backend/dataset/"
    )

    print()

    raise SystemExit(1)


# ============================================================
# LOAD DATASET
# ============================================================

print("Loading dataset...")

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Dataset loaded successfully."
)

print(
    f"Total rows: {len(df)}"
)

print(
    f"Total columns: {len(df.columns)}"
)

print()


# ============================================================
# DISPLAY ORIGINAL COLUMNS
# ============================================================

print("Original columns:")

for column in df.columns:

    print(
        " -",
        column
    )

print()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(
        " ",
        "_"
    )
)


print("Cleaned columns:")

print(
    list(df.columns)
)

print()


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [

    "date_time",

    "temp",

    "rain_1h",

    "snow_1h",

    "clouds_all",

    "weather_main",

    "holiday",

    "traffic_volume"

]


missing_columns = [

    column

    for column in required_columns

    if column not in df.columns

]


if missing_columns:

    print(
        "ERROR: Required columns are missing:"
    )

    for column in missing_columns:

        print(
            " -",
            column
        )

    print()

    raise SystemExit(1)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

before_duplicates = len(df)


df = df.drop_duplicates()


after_duplicates = len(df)


print(
    f"Removed duplicates: "
    f"{before_duplicates - after_duplicates}"
)

print()


# ============================================================
# DATE/TIME CONVERSION
# ============================================================

print("Processing date and time...")


df["date_time"] = pd.to_datetime(
    df["date_time"],
    errors="coerce"
)


# Remove invalid dates

df = df.dropna(
    subset=["date_time"]
)


# ============================================================
# EXTRACT TIME FEATURES
# ============================================================

df["hour"] = (
    df["date_time"].dt.hour
)

df["day"] = (
    df["date_time"].dt.day
)

df["month"] = (
    df["date_time"].dt.month
)

df["weekday"] = (
    df["date_time"].dt.weekday
)


# Monday = 0
# Sunday = 6

df["is_weekend"] = (
    df["weekday"] >= 5
).astype(int)


# ============================================================
# PEAK HOUR FEATURE
# ============================================================

df["is_peak_hour"] = (

    (
        (df["hour"] >= 7) &
        (df["hour"] <= 9)
    )

    |

    (
        (df["hour"] >= 16) &
        (df["hour"] <= 19)
    )

).astype(int)


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "temp",

    "rain_1h",

    "snow_1h",

    "clouds_all",

    "traffic_volume"

]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# MISSING VALUE HANDLING
# ============================================================

print("Handling missing values...")


for column in numeric_columns:

    if df[column].isna().sum() > 0:

        median_value = (
            df[column].median()
        )

        df[column] = (
            df[column]
            .fillna(median_value)
        )


# Weather missing values

df["weather_main"] = (
    df["weather_main"]
    .fillna("Unknown")
)


df["holiday"] = (
    df["holiday"]
    .fillna("None")
)


# ============================================================
# WEATHER ENCODING
# ============================================================

print("Encoding weather...")


weather_mapping = {

    "Clear": 0,

    "Clouds": 1,

    "Rain": 2,

    "Drizzle": 3,

    "Mist": 4,

    "Fog": 5,

    "Haze": 6,

    "Thunderstorm": 7,

    "Snow": 8,

    "Smoke": 9,

    "Squall": 10,

    "Unknown": 11

}


df["weather_encoded"] = (

    df["weather_main"]
    .map(weather_mapping)
    .fillna(11)
    .astype(int)

)


# ============================================================
# HOLIDAY ENCODING
# ============================================================

df["holiday_encoded"] = (

    df["holiday"]
    .apply(
        lambda x:
        0 if str(x).lower()
        in ["none", "nan"]
        else 1
    )

)


# ============================================================
# ADD TRAFFIC LAG FEATURES
# ============================================================

print(
    "Creating traffic history features..."
)


# IMPORTANT:
# Sort by date before creating lag values.

df = df.sort_values(
    "date_time"
).reset_index(
    drop=True
)


# Previous observation traffic

df["previous_traffic"] = (
    df["traffic_volume"]
    .shift(1)
)


# Traffic approximately one day earlier
# Dataset contains traffic measurements
# at regular intervals.

df["traffic_lag_24"] = (
    df["traffic_volume"]
    .shift(24)
)


# Traffic approximately one week earlier

df["traffic_lag_168"] = (
    df["traffic_volume"]
    .shift(168)
)


# ============================================================
# REMOVE ROWS WITH MISSING LAG VALUES
# ============================================================

df = df.dropna(
    subset=[
        "previous_traffic",
        "traffic_lag_24",
        "traffic_lag_168"
    ]
)


# ============================================================
# FEATURE LIST
# ============================================================

features = [

    "hour",

    "day",

    "month",

    "weekday",

    "is_weekend",

    "is_peak_hour",

    "temp",

    "rain_1h",

    "snow_1h",

    "clouds_all",

    "weather_encoded",

    "holiday_encoded",

    "previous_traffic",

    "traffic_lag_24",

    "traffic_lag_168"

]


target = "traffic_volume"


# ============================================================
# CHECK FEATURES
# ============================================================

print()
print("Features used by model:")

for feature in features:

    print(
        " -",
        feature
    )

print()


# ============================================================
# CREATE X AND Y
# ============================================================

X = df[
    features
]

y = df[
    target
]


# ============================================================
# FINAL NAN CHECK
# ============================================================

if X.isnull().sum().sum() > 0:

    print(
        "Removing remaining missing values..."
    )

    valid_rows = (
        X.notnull().all(axis=1)
        &
        y.notnull()
    )

    X = X[
        valid_rows
    ]

    y = y[
        valid_rows
    ]


# ============================================================
# TRAIN TEST SPLIT
# ============================================================

print(
    f"Final training records: {len(X)}"
)

print()

print(
    "Splitting dataset..."
)


X_train, X_test, y_train, y_test = (

    train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=RANDOM_STATE

    )

)


print(
    f"Training records: {len(X_train)}"
)

print(
    f"Testing records:  {len(X_test)}"
)

print()


# ============================================================
# CREATE RANDOM FOREST MODEL
# ============================================================

print(
    "Training Random Forest model..."
)

print(
    "Please wait..."
)

print()


model = RandomForestRegressor(

    n_estimators=200,

    max_depth=25,

    min_samples_split=4,

    min_samples_leaf=2,

    max_features="sqrt",

    random_state=RANDOM_STATE,

    n_jobs=-1

)


# ============================================================
# TRAIN
# ============================================================

model.fit(
    X_train,
    y_train
)


print(
    "Model training completed!"
)

print()


# ============================================================
# PREDICTION
# ============================================================

print(
    "Evaluating model..."
)

y_pred = model.predict(
    X_test
)


# ============================================================
# METRICS
# ============================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)


rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)


r2 = r2_score(
    y_test,
    y_pred
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 65)
print("                 MODEL PERFORMANCE")
print("=" * 65)

print()

print(
    f"MAE  : {mae:.2f} vehicles/hour"
)

print(
    f"RMSE : {rmse:.2f} vehicles/hour"
)

print(
    f"R²   : {r2:.4f}"
)

print(
    f"R² % : {r2 * 100:.2f}%"
)

print()


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print(
    "=" * 65
)

print(
    "              FEATURE IMPORTANCE"
)

print(
    "=" * 65
)

print()


importance = pd.DataFrame({

    "feature":
        features,

    "importance":
        model.feature_importances_

})


importance = (
    importance
    .sort_values(
        "importance",
        ascending=False
    )
)


for _, row in importance.iterrows():

    print(
        f"{row['feature']:25s}"
        f" : "
        f"{row['importance']:.4f}"
    )


print()


# ============================================================
# SAVE MODEL
# ============================================================

print(
    "Saving model..."
)


joblib.dump(
    model,
    MODEL_PATH
)


print(
    f"Model saved: {MODEL_PATH}"
)


# ============================================================
# SAVE FEATURE CONFIGURATION
# ============================================================

feature_config = {

    "features": features,

    "weather_mapping":
        weather_mapping,

    "target":
        target,

    "model":
        "RandomForestRegressor"

}


joblib.dump(
    feature_config,
    FEATURE_PATH
)


print(
    f"Feature configuration saved: "
    f"{FEATURE_PATH}"
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

print()
print(
    "=" * 65
)

print(
    "                SAMPLE PREDICTIONS"
)

print(
    "=" * 65
)

print()


sample_results = pd.DataFrame({

    "Actual":
        y_test.iloc[:10].values,

    "Predicted":
        np.round(
            y_pred[:10]
        ).astype(int)

})


print(
    sample_results.to_string(
        index=False
    )
)


# ============================================================
# COMPLETE
# ============================================================

print()
print(
    "=" * 65
)

print(
    "             TRAINING COMPLETED"
)

print(
    "=" * 65
)

print()

print(
    "Generated files:"
)

print(
    f"1. {MODEL_PATH}"
)

print(
    f"2. {FEATURE_PATH}"
)

print()

print(
    "Your AI traffic prediction model is ready."
)

print()