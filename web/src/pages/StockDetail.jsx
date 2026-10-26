import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import Plot from "react-plotly.js";

const API_BASE = "http://127.0.0.1:8000";

function getConfidenceClass(confidence) {
  if (confidence < 55) return "confidence-low";
  if (confidence < 65) return "confidence-medium";
  return "confidence-high";
}

function StockDetail() {
  const { ticker } = useParams();
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    Promise.all([
      axios.get(`${API_BASE}/predict/${ticker}`),
      axios.get(`${API_BASE}/history/${ticker}?days=365`)
    ])
      .then(([predRes, histRes]) => {
        setPrediction(predRes.data);
        setHistory(histRes.data);
      })
      .catch(() => setError("Failed to load data for this stock."))
      .finally(() => setLoading(false));
  }, [ticker]);

  if (loading) return <div className="app"><p style={{ textAlign: "center" }}>Loading...</p></div>;
  if (error) return <div className="app"><p className="error">{error}</p></div>;
  if (!prediction || !history) return null;

  const isPositive = prediction.predicted_change_pct >= 0;
  const rsi = prediction.technical_indicators.RSI_14;

  let rsiSignal = "Neutral";
  if (rsi > 70) rsiSignal = "Overbought";
  if (rsi < 30) rsiSignal = "Oversold";

  const macdSignal = prediction.technical_indicators.MACD > prediction.technical_indicators.MACD_Signal
    ? "Bullish crossover"
    : "Bearish crossover";

  return (
    <div className="app">
      <Link to="/" className="back-link">← Back to Dashboard</Link>

      <h1>{ticker.replace(".NS", "")} — Full Analysis</h1>
      <p style={{ color: "#9a9ca8" }}>As of {prediction.as_of_date}</p>

      <div className="chart-container">
        <Plot
          data={[
            {
              x: history.dates,
              open: history.open,
              high: history.high,
              low: history.low,
              close: history.close,
              type: "candlestick",
              name: ticker,
              increasing: { line: { color: "#4ade80" } },
              decreasing: { line: { color: "#f87171" } },
            },
          ]}
          layout={{
            title: { text: `${ticker.replace(".NS", "")} — 1 Year History`, font: { color: "#e6e6e6" } },
            paper_bgcolor: "#1a1d29",
            plot_bgcolor: "#1a1d29",
            font: { color: "#e6e6e6" },
            xaxis: { rangeslider: { visible: true }, gridcolor: "#2c2f3d" },
            yaxis: { gridcolor: "#2c2f3d" },
            margin: { t: 40, b: 40, l: 50, r: 20 },
            autosize: true,
          }}
          style={{ width: "100%", height: "450px" }}
          useResizeHandler={true}
          config={{ displayModeBar: false }}
        />
      </div>

      <div className="detail-grid">
        <div className="prediction-card">
          <h3>Prediction</h3>
          <div className="price-row">
            <span>
              <span className="label">Current Close</span><br />
              <span className="value">₹{prediction.current_close}</span>
            </span>
            <span>
              <span className="label">Predicted Next Close</span><br />
              <span className={`value ${isPositive ? "change-positive" : "change-negative"}`}>
                ₹{prediction.predicted_next_close} ({isPositive ? "+" : ""}{prediction.predicted_change_pct}%)
              </span>
            </span>
          </div>

          <div style={{ marginTop: 16 }}>
            <span className={`trend-badge ${prediction.trend === "Bullish" ? "trend-bullish" : "trend-bearish"}`}>
              {prediction.trend === "Bullish" ? "🟢" : "🔴"} {prediction.trend}
            </span>
          </div>

          <div style={{ marginTop: 16 }}>
            <span className="label">Confidence: {prediction.confidence_pct}%</span>
            <div className="confidence-bar-container">
              <div
                className={`confidence-bar-fill ${getConfidenceClass(prediction.confidence_pct)}`}
                style={{ width: `${prediction.confidence_pct}%` }}
              />
            </div>
          </div>
        </div>

        <div className="prediction-card">
          <h3>Technical Signal Breakdown</h3>
          <div className="signal-row">
            <span className="label">RSI (14)</span>
            <span className="value">{rsi} — <span className="signal-tag">{rsiSignal}</span></span>
          </div>
          <div className="signal-row">
            <span className="label">MACD vs Signal</span>
            <span className="value"><span className="signal-tag">{macdSignal}</span></span>
          </div>
          <div className="signal-row">
            <span className="label">Price vs SMA 20</span>
            <span className="value">{prediction.current_close > prediction.technical_indicators.SMA_20 ? "Above" : "Below"} (₹{prediction.technical_indicators.SMA_20})</span>
          </div>
          <div className="signal-row">
            <span className="label">Price vs SMA 50</span>
            <span className="value">{prediction.current_close > prediction.technical_indicators.SMA_50 ? "Above" : "Below"} (₹{prediction.technical_indicators.SMA_50})</span>
          </div>
          <div className="signal-row">
            <span className="label">Price vs SMA 200</span>
            <span className="value">{prediction.current_close > prediction.technical_indicators.SMA_200 ? "Above" : "Below"} (₹{prediction.technical_indicators.SMA_200})</span>
          </div>
        </div>
      </div>

      <p className="disclaimer">⚠️ {prediction.disclaimer}</p>
    </div>
  );
}

export default StockDetail;
