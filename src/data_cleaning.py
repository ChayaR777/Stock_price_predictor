import pandas as pd
import os
from src.config import TICKERS, RAW_DATA_DIR, PROCESSED_DATA_DIR

def load_raw(ticker: str) -> pd.DataFrame:
    clean_name = ticker.replace(".NS", "")
    path = f"{RAW_DATA_DIR}/{clean_name}_raw.csv"
    df = pd.read_csv(path, parse_dates=["Date"])
    return df

def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Sorts by date
    - Drops duplicate dates
    - Forward-fills any missing values (holidays, gaps)
    - Computes daily return %
    """
    df = df.sort_values("Date").drop_duplicates(subset="Date")
    df = df.set_index("Date")

    # Forward-fill missing values (rare, but guards against gaps)
    df = df.ffill()

    # Drop any remaining rows with nulls (e.g. at the very start)
    df = df.dropna()

    # Daily return: % change in closing price
    df["Daily_Return"] = df["Close"].pct_change() * 100

    df = df.reset_index()
    return df

def process_all():
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    for ticker in TICKERS:
        clean_name = ticker.replace(".NS", "")
        print(f"Cleaning {ticker}...")
        raw = load_raw(ticker)
        cleaned = clean_stock_data(raw)
        cleaned.to_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_clean.csv", index=False)
        print(f"  → {len(cleaned)} rows saved")

if __name__ == "__main__":
    process_all()
