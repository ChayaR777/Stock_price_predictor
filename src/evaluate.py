import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, confusion_matrix
)
from src.config import TICKERS, MODELS_DIR

def load_test_artifacts(ticker: str):
    clean_name = ticker.replace(".NS", "")
    ticker_dir = f"{MODELS_DIR}/{clean_name}"

    return_model = joblib.load(f"{ticker_dir}/return_model.pkl")
    trend_model = joblib.load(f"{ticker_dir}/trend_model.pkl")

    X_test = pd.read_csv(f"{ticker_dir}/X_test.csv")
    y_return_test = pd.read_csv(f"{ticker_dir}/y_return_test.csv").iloc[:, 0]
    y_trend_test = pd.read_csv(f"{ticker_dir}/y_trend_test.csv").iloc[:, 0]
    close_test = pd.read_csv(f"{ticker_dir}/close_test.csv").iloc[:, 0]

    return return_model, trend_model, X_test, y_return_test, y_trend_test, close_test

def evaluate_price_model(return_model, X_test, y_return_test, close_test):
    """
    Predict % return, then reconstruct actual price:
    predicted_price = today's close * (1 + predicted_return / 100)
    """
    return_preds = return_model.predict(X_test)

    predicted_price = close_test.values * (1 + return_preds / 100)
    actual_price = close_test.values * (1 + y_return_test.values / 100)

    rmse = np.sqrt(mean_squared_error(actual_price, predicted_price))
    mae = mean_absolute_error(actual_price, predicted_price)
    r2 = r2_score(actual_price, predicted_price)
    mape = np.mean(np.abs((actual_price - predicted_price) / actual_price)) * 100

    print(f"    Price Model  -> RMSE: {rmse:.2f} | MAE: {mae:.2f} | MAPE: {mape:.2f}% | R2: {r2:.4f}")
    return predicted_price, actual_price, {"rmse": rmse, "mae": mae, "mape": mape, "r2": r2}

def evaluate_trend_model(trend_model, X_test, y_trend_test):
    preds = trend_model.predict(X_test)

    acc = accuracy_score(y_trend_test, preds)
    prec = precision_score(y_trend_test, preds)
    rec = recall_score(y_trend_test, preds)
    cm = confusion_matrix(y_trend_test, preds)

    print(f"    Trend Model  -> Accuracy: {acc:.2%} | Precision: {prec:.2%} | Recall: {rec:.2%}")
    print(f"    Confusion Matrix (rows=actual, cols=predicted):\n{cm}")
    return preds, {"accuracy": acc, "precision": prec, "recall": rec}

def naive_baseline_mape(close_test, y_return_test):
    """Naive baseline: predict tomorrow's close = today's close (0% return)."""
    actual_price = close_test.values * (1 + y_return_test.values / 100)
    naive_price = close_test.values
    mape = np.mean(np.abs((actual_price - naive_price) / actual_price)) * 100
    return mape

def plot_predicted_vs_actual(ticker: str, actual_price, predicted_price):
    clean_name = ticker.replace(".NS", "")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=actual_price, mode="lines", name="Actual"))
    fig.add_trace(go.Scatter(y=predicted_price, mode="lines", name="Predicted"))
    fig.update_layout(
        title=f"{clean_name} — Predicted vs Actual Close Price (Test Set)",
        xaxis_title="Test Sample (chronological)",
        yaxis_title="Price (INR)",
        template="plotly_white"
    )
    fig.show()

def evaluate_all():
    results = {}
    for ticker in TICKERS:
        print(f"\nEvaluating {ticker}...")
        return_model, trend_model, X_test, y_return_test, y_trend_test, close_test = load_test_artifacts(ticker)

        predicted_price, actual_price, price_metrics = evaluate_price_model(
            return_model, X_test, y_return_test, close_test
        )
        trend_preds, trend_metrics = evaluate_trend_model(trend_model, X_test, y_trend_test)

        naive_mape = naive_baseline_mape(close_test, y_return_test)
        print(f"    Naive Baseline (predict no change) -> MAPE: {naive_mape:.2f}%")
        if naive_mape < price_metrics["mape"]:
            print(f"    ⚠️  Model is still worse than naive baseline for {ticker}")
        else:
            print(f"    ✅ Model BEATS naive baseline for {ticker}")

        results[ticker] = {"price": price_metrics, "trend": trend_metrics, "naive_mape": naive_mape}

    return results

if __name__ == "__main__":
    results = evaluate_all()
    return_model, trend_model, X_test, y_return_test, y_trend_test, close_test = load_test_artifacts("RELIANCE.NS")
    predicted_price, actual_price, _ = evaluate_price_model(return_model, X_test, y_return_test, close_test)
    plot_predicted_vs_actual("RELIANCE.NS", actual_price, predicted_price)

def show_feature_importance(ticker: str = "RELIANCE.NS"):
    from src.train import FEATURE_COLUMNS
    return_model, trend_model, X_test, y_return_test, y_trend_test, close_test = load_test_artifacts(ticker)

    importances = pd.Series(trend_model.feature_importances_, index=FEATURE_COLUMNS)
    importances = importances.sort_values(ascending=False)
    print(f"\nTop features driving trend prediction for {ticker}:")
    print(importances.head(8))
