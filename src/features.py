import pandas as pd
import numpy as np
import os
from src.config import TICKERS, PROCESSED_DATA_DIR

def load_clean(ticker: str) -> pd.DataFrame:
    clean_name = ticker.replace(".NS", "")
    return pd.read_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_clean.csv", parse_dates=["Date"])

def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    return df

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    df["RSI_14"] = 100 - (100 / (1 + rs))
    return df

def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def add_lagged_features(df: pd.DataFrame, lags=[1, 2, 3, 5]) -> pd.DataFrame:
    """
    Lagged RETURNS (not raw prices) — stationary features that describe
    recent momentum without carrying the stock's absolute price level.
    """
    daily_return_frac = df["Close"].pct_change()
    for lag in lags:
        df[f"Return_Lag_{lag}"] = daily_return_frac.shift(lag - 1)  # lag-1 since already shifted once by pct_change
    return df

def add_normalized_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price-level indicators (SMA, EMA) into RATIOS relative to Close.
    E.g. Close_to_SMA20 = Close / SMA_20 tells us "how stretched is price
    from its 20-day average" — this is stationary, unlike raw SMA values
    which drift upward alongside the stock price over the years.
    """
    df["Close_to_SMA20"] = df["Close"] / df["SMA_20"]
    df["Close_to_SMA50"] = df["Close"] / df["SMA_50"]
    df["Close_to_SMA200"] = df["Close"] / df["SMA_200"]
    df["Close_to_EMA20"] = df["Close"] / df["EMA_20"]
    return df

def add_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Target variable: NEXT day's % price change (regression target).
    We predict the return, not the absolute price — this keeps the
    target stationary so the model isn't forced to extrapolate into
    price ranges it has never seen during training.
    Target_Close is kept only for reference/reconstruction, not as a
    model input.
    """
    df["Target_Close"] = df["Close"].shift(-1)
    df["Target_Return"] = (df["Target_Close"] - df["Close"]) / df["Close"] * 100
    df["Target_Trend"] = (df["Target_Close"] > df["Close"]).astype(int)
    return df

def build_features(ticker: str) -> pd.DataFrame:
    df = load_clean(ticker)
    df = add_moving_averages(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_lagged_features(df)
    df = add_normalized_indicators(df)
    df = add_target(df)
    df = df.dropna().reset_index(drop=True)
    return df

def process_all_features():
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    for ticker in TICKERS:
        clean_name = ticker.replace(".NS", "")
        print(f"Engineering features for {ticker}...")
        df = build_features(ticker)
        df.to_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_features.csv", index=False)
        print(f"  → {len(df)} rows, {df.shape[1]} columns saved")

if __name__ == "__main__":
    process_all_features()
