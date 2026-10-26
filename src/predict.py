import pandas as pd
import numpy as np
import joblib
from src.config import MODELS_DIR, PROCESSED_DATA_DIR
from src.train import FEATURE_COLUMNS

def load_models(ticker: str):
    clean_name = ticker.replace(".NS", "")
    ticker_dir = f"{MODELS_DIR}/{clean_name}"
    return_model = joblib.load(f"{ticker_dir}/return_model.pkl")
    trend_model = joblib.load(f"{ticker_dir}/trend_model.pkl")
    return return_model, trend_model

def get_latest_features(ticker: str) -> pd.DataFrame:
    """
    Loads the most recently engineered feature row for a ticker —
    this represents 'today', which we use to predict 'tomorrow'.
    """
    clean_name = ticker.replace(".NS", "")
    df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_features.csv", parse_dates=["Date"])
    latest = df.iloc[[-1]]  # keep as DataFrame, not Series
    return latest

def predict_next_day(ticker: str) -> dict:
    return_model, trend_model = load_models(ticker)
    latest = get_latest_features(ticker)

    X_latest = latest[FEATURE_COLUMNS]
    today_close = latest["Close"].values[0]
    today_date = latest["Date"].values[0]

    # --- Price prediction ---
    predicted_return_pct = return_model.predict(X_latest)[0]
    predicted_price = today_close * (1 + predicted_return_pct / 100)

    # --- Trend + confidence ---
    trend_pred = trend_model.predict(X_latest)[0]
    trend_proba = trend_model.predict_proba(X_latest)[0]  # [P(Bearish), P(Bullish)]
    confidence = float(np.max(trend_proba)) * 100
    trend_label = "Bullish" if trend_pred == 1 else "Bearish"

    # --- Technical indicators (latest values, for display) ---
    indicators = {
        "RSI_14": round(float(latest["RSI_14"].values[0]), 2),
        "MACD": round(float(latest["MACD"].values[0]), 2),
        "MACD_Signal": round(float(latest["MACD_Signal"].values[0]), 2),
        "SMA_20": round(float(latest["SMA_20"].values[0]), 2),
        "SMA_50": round(float(latest["SMA_50"].values[0]), 2),
        "SMA_200": round(float(latest["SMA_200"].values[0]), 2),
    }

    return {
        "ticker": ticker,
        "as_of_date": str(today_date)[:10],
        "current_close": round(float(today_close), 2),
        "predicted_next_close": round(float(predicted_price), 2),
        "predicted_change_pct": round(float(predicted_return_pct), 2),
        "trend": trend_label,
        "confidence_pct": round(confidence, 2),
        "technical_indicators": indicators,
        "disclaimer": "This prediction is a statistical estimate based on historical patterns, not financial advice. Markets are inherently unpredictable — please consult a licensed financial advisor before making investment decisions."
    }

if __name__ == "__main__":
    import json
    result = predict_next_day("RELIANCE.NS")
    print(json.dumps(result, indent=2))
