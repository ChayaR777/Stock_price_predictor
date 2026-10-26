import yfinance as yf
import pandas as pd
import os
from src.config import TICKERS, START_DATE, END_DATE, RAW_DATA_DIR

def fetch_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        print(f"⚠️ No data returned for {ticker}")
        return pd.DataFrame()

    # yfinance sometimes returns MultiIndex columns like ('Close', 'RELIANCE.NS')
    # Flatten them down to just 'Close', 'High', etc.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.reset_index(inplace=True)
    data["Ticker"] = ticker
    return data

def fetch_all(tickers: list, start: str, end: str) -> pd.DataFrame:
    frames = []
    for t in tickers:
        print(f"Fetching {t}...")
        df = fetch_stock_data(t, start, end)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True)

def save_raw(all_data: pd.DataFrame, tickers: list):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    for ticker in tickers:
        subset = all_data[all_data["Ticker"] == ticker]
        clean_name = ticker.replace(".NS", "")
        subset.to_csv(f"{RAW_DATA_DIR}/{clean_name}_raw.csv", index=False)
    print(f"Saved raw files to {RAW_DATA_DIR}/")

if __name__ == "__main__":
    all_data = fetch_all(TICKERS, START_DATE, END_DATE)
    save_raw(all_data, TICKERS)