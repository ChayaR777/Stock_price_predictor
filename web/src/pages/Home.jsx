import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Plot from "react-plotly.js";
import { useAuth } from "../context/AuthContext";
import api from "../api";

const API_BASE = "http://127.0.0.1:8000";

const RANGE_OPTIONS = [
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
  { label: "All", days: 3000 },
];

function getConfidenceClass(confidence) {
  if (confidence < 55) return "confidence-low";
  if (confidence < 65) return "confidence-medium";
  return "confidence-high";
}

function Home() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tickers, setTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState(null);
  const [rangeDays, setRangeDays] = useState(180);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [starred, setStarred] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE}/tickers`)
      .then((res) => {
        setTickers(res.data.tickers);
        setSelectedTicker(res.data.tickers[0]);
      })
      .catch(() => {
        setError("Could not reach the prediction API. Is the FastAPI server running?");
      });
  }, []);

  useEffect(() => {
    if (!selectedTicker) return;
    setLoading(true);
    setError(null);

    axios.get(`${API_BASE}/predict/${selectedTicker}`)
      .then((res) => setPrediction(res.data))
      .catch(() => setError("Failed to fetch prediction."))
      .finally(() => setLoading(false));
  }, [selectedTicker]);

  useEffect(() => {
    if (!selectedTicker) return;

    axios.get(`${API_BASE}/history/${selectedTicker}?days=${rangeDays}`)
      .then((res) => setHistory(res.data))
      .catch(() => setError("Failed to fetch chart history."));
  }, [selectedTicker, rangeDays]);

  // Check whether the selected stock is in this user's watchlist
  useEffect(() => {
    if (!selectedTicker || !user) {
      setStarred(false);
      return;
    }
    api.get("/watchlist")
      .then((res) => setStarred(res.data.tickers.includes(selectedTicker)))
      .catch(() => setStarred(false));
  }, [selectedTicker, user]);

  const toggleStar = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    try {
      if (starred) {
        await api.delete(`/watchlist/${selectedTicker}`);
        setStarred(false);
      } else {
        await api.post("/watchlist", { ticker: selectedTicker });
        setStarred(true);
      }
    } catch {
      setError("Could not update your watchlist.");
    }
  };

  const isPositive = prediction?.predicted_change_pct >= 0;

  return (
    <div className="app">
      <h1>📈 Indian Stock Price Predictor</h1>

      <div className="ticker-selector">
        <label htmlFor="ticker">Select Stock: </label>
        <select
          id="ticker"
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
        >
          {tickers.map((t) => (
            <option key={t} value={t}>{t.replace(".NS", "")}</option>
          ))}
        </select>
        <button className="star-btn" onClick={toggleStar} title={starred ? "Remove from watchlist" : "Add to watchlist"}>
          {starred ? "⭐" : "☆"}
        </button>
        {selectedTicker && (
          <button className="detail-link-btn" onClick={() => navigate(`/stock/${selectedTicker}`)}>
            View Full Detail →
          </button>
        )}
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p style={{ textAlign: "center" }}>Loading prediction...</p>}

      {history && !loading && (
        <div className="chart-container">
          <div className="range-selector">
            {RANGE_OPTIONS.map((opt) => (
              <button
                key={opt.label}
                className={`range-btn ${rangeDays === opt.days ? "range-btn-active" : ""}`}
                onClick={() => setRangeDays(opt.days)}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <Plot
            data={[
              {
                x: history.dates,
                open: history.open,
                high: history.high,
                low: history.low,
                close: history.close,
                type: "candlestick",
                name: history.ticker,
                increasing: { line: { color: "#4ade80" } },
                decreasing: { line: { color: "#f87171" } },
              },
            ]}
            layout={{
              title: { text: `${history.ticker.replace(".NS", "")} Price History`, font: { color: "#e6e6e6" } },
              paper_bgcolor: "#1a1d29",
              plot_bgcolor: "#1a1d29",
              font: { color: "#e6e6e6" },
              xaxis: { rangeslider: { visible: false }, gridcolor: "#2c2f3d" },
              yaxis: { gridcolor: "#2c2f3d" },
              margin: { t: 40, b: 40, l: 50, r: 20 },
              autosize: true,
            }}
            style={{ width: "100%", height: "400px" }}
            useResizeHandler={true}
            config={{ displayModeBar: false }}
          />
        </div>
      )}

      {prediction && !loading && (
        <>
          <div className="prediction-card">
            <h2>{prediction.ticker.replace(".NS", "")}</h2>
            <p style={{ color: "#9a9ca8", marginTop: -8 }}>As of {prediction.as_of_date}</p>

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

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 20 }}>
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

            <div className="indicators-grid">
              <div className="indicator-box">
                <span className="label">RSI (14)</span>
                <span className="value">{prediction.technical_indicators.RSI_14}</span>
              </div>
              <div className="indicator-box">
                <span className="label">MACD</span>
                <span className="value">{prediction.technical_indicators.MACD}</span>
              </div>
              <div className="indicator-box">
                <span className="label">MACD Signal</span>
                <span className="value">{prediction.technical_indicators.MACD_Signal}</span>
              </div>
              <div className="indicator-box">
                <span className="label">SMA 20</span>
                <span className="value">₹{prediction.technical_indicators.SMA_20}</span>
              </div>
              <div className="indicator-box">
                <span className="label">SMA 50</span>
                <span className="value">₹{prediction.technical_indicators.SMA_50}</span>
              </div>
              <div className="indicator-box">
                <span className="label">SMA 200</span>
                <span className="value">₹{prediction.technical_indicators.SMA_200}</span>
              </div>
            </div>
          </div>

          <p className="disclaimer">⚠️ {prediction.disclaimer}</p>
        </>
      )}
    </div>
  );
}

export default Home;
