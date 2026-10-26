import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.config import PROCESSED_DATA_DIR

def load_clean(ticker: str) -> pd.DataFrame:
    clean_name = ticker.replace(".NS", "")
    return pd.read_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_clean.csv", parse_dates=["Date"])

def plot_price_history(ticker: str):
    df = load_clean(ticker)
    clean_name = ticker.replace(".NS", "")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=clean_name
    ))
    fig.update_layout(
        title=f"{clean_name} — Historical Price",
        xaxis_title="Date", yaxis_title="Price (INR)",
        xaxis_rangeslider_visible=True, template="plotly_dark"
    )
    fig.show()

def plot_volume(ticker: str):
    df = load_clean(ticker)
    clean_name = ticker.replace(".NS", "")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume"))
    fig.update_layout(
        title=f"{clean_name} — Trading Volume",
        xaxis_title="Date", yaxis_title="Volume",
        template="plotly_dark"
    )
    fig.show()

def plot_returns_distribution(ticker: str):
    df = load_clean(ticker)
    clean_name = ticker.replace(".NS", "")

    fig = px.histogram(
        df, x="Daily_Return", nbins=100,
        title=f"{clean_name} — Daily Return Distribution (%)",
        template="plotly_white",
        color_discrete_sequence=["#636EFA"]  # solid visible blue bars
    )
    fig.update_layout(
        bargap=0.05,
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency"
    )
    fig.show()

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    plot_price_history(ticker)
    plot_volume(ticker)
    plot_returns_distribution(ticker)
