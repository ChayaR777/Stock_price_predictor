import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

function ModelPerformance() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/model-performance`)
      .then((res) => setResults(res.data.results))
      .catch(() => setError("Failed to load model performance data."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app">
      <h1>📊 Model Performance</h1>
      <p style={{ color: "#9a9ca8" }}>
        Metrics computed on a held-out test set (most recent ~20% of trading days, never seen during training).
        We compare against a naive baseline ("tomorrow's price = today's price") to check whether the model
        adds real predictive value beyond the fact that daily price moves are naturally small.
      </p>

      {loading && <p style={{ textAlign: "center" }}>Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && results.length > 0 && (
        <div className="perf-table-wrapper">
          <table className="perf-table">
            <thead>
              <tr>
                <th>Stock</th>
                <th>Price MAPE</th>
                <th>Naive MAPE</th>
                <th>Price R²</th>
                <th>Trend Accuracy</th>
                <th>Trend Precision</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr key={r.ticker}>
                  <td>{r.ticker.replace(".NS", "")}</td>
                  <td>{r.price_mape}%</td>
                  <td>{r.naive_baseline_mape}%</td>
                  <td>{r.price_r2}</td>
                  <td>{r.trend_accuracy}%</td>
                  <td>{r.trend_precision}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="perf-note">
        <h3>How to read these numbers</h3>
        <ul>
          <li><strong>Price MAPE</strong> — average % error in next-day price prediction. Lower is better.</li>
          <li><strong>Naive MAPE</strong> — error if you simply guessed "no change" from today. Our model's MAPE closely tracks this because daily stock moves are naturally small — this is expected, not a flaw.</li>
          <li><strong>Trend Accuracy</strong> — how often the Bullish/Bearish call was correct. Values near 50% reflect the well-documented difficulty of predicting daily direction from technical indicators alone; short-term stock movement is close to a random walk.</li>
        </ul>
      </div>

      <p className="disclaimer">
        ⚠️ These figures describe historical backtest performance only and are not a guarantee of future accuracy.
        This tool is for educational purposes and is not financial advice.
      </p>
    </div>
  );
}

export default ModelPerformance;
