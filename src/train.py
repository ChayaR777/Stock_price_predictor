import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from src.config import TICKERS, PROCESSED_DATA_DIR, MODELS_DIR

# All stationary — ratios, oscillators, and returns. No raw price levels,
# so the model isn't thrown off by prices being higher in the test period.
FEATURE_COLUMNS = [
    "RSI_14", "MACD", "MACD_Signal", "MACD_Hist",
    "Close_to_SMA20", "Close_to_SMA50", "Close_to_SMA200", "Close_to_EMA20",
    "Return_Lag_1", "Return_Lag_2", "Return_Lag_3", "Return_Lag_5",
    "Daily_Return"
]

def load_features(ticker: str) -> pd.DataFrame:
    clean_name = ticker.replace(".NS", "")
    return pd.read_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_features.csv", parse_dates=["Date"])

def train_ticker_models(ticker: str):
    df = load_features(ticker)

    X = df[FEATURE_COLUMNS]
    y_return = df["Target_Return"]   # % change target, not raw price
    y_trend = df["Target_Trend"]

    # Keep Close alongside test data so we can reconstruct predicted price later
    close_prices = df["Close"]

    split_idx = int(len(df) * 0.8)

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_return_train, y_return_test = y_return.iloc[:split_idx], y_return.iloc[split_idx:]
    y_trend_train, y_trend_test = y_trend.iloc[:split_idx], y_trend.iloc[split_idx:]
    close_test = close_prices.iloc[split_idx:]

    # --- Regression model: predicts next-day % RETURN ---
    return_model = RandomForestRegressor(
        n_estimators=300, max_depth=8, min_samples_leaf=5, random_state=42, n_jobs=-1
    )
    return_model.fit(X_train, y_return_train)

    # --- Classification model: predicts Bullish(1)/Bearish(0) ---
    trend_model = RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1
    )
    trend_model.fit(X_train, y_trend_train)

    clean_name = ticker.replace(".NS", "")
    ticker_dir = f"{MODELS_DIR}/{clean_name}"
    os.makedirs(ticker_dir, exist_ok=True)

    joblib.dump(return_model, f"{ticker_dir}/return_model.pkl")
    joblib.dump(trend_model, f"{ticker_dir}/trend_model.pkl")

    X_test.to_csv(f"{ticker_dir}/X_test.csv", index=False)
    y_return_test.to_csv(f"{ticker_dir}/y_return_test.csv", index=False)
    y_trend_test.to_csv(f"{ticker_dir}/y_trend_test.csv", index=False)
    close_test.to_csv(f"{ticker_dir}/close_test.csv", index=False)

    print(f"  {ticker}: trained on {len(X_train)} rows, held out {len(X_test)} rows for testing")

def train_all():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for ticker in TICKERS:
        print(f"Training models for {ticker}...")
        train_ticker_models(ticker)
    print("All models trained and saved to models/")

if __name__ == "__main__":
    train_all()
