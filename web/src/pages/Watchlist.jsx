import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import { useAuth } from "../context/AuthContext";

function Watchlist() {
  const { user, checking } = useAuth();
  const [tickers, setTickers] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadWatchlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const listRes = await api.get("/watchlist");
      const list = listRes.data.tickers;
      setTickers(list);

      const results = await Promise.all(
        list.map((t) => api.get(`/predict/${t}`).then((res) => [t, res.data]))
      );
      const map = {};
      results.forEach(([t, data]) => { map[t] = data; });
      setPredictions(map);
    } catch {
      setError("Could not load your watchlist.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) loadWatchlist();
    else setLoading(false);
  }, [user, loadWatchlist]);

  const handleRemove = async (ticker) => {
    await api.delete(`/watchlist/${ticker}`);
    loadWatchlist();
  };

  if (checking) return <div className="app"><p style={{ textAlign: "center" }}>Loading...</p></div>;

  if (!user) {
    return (
      <div className="app">
        <h1>⭐ Your Watchlist</h1>
        <p style={{ color: "#9a9ca8" }}>
          <Link to="/login" style={{ color: "#4ade80" }}>Log in</Link> or{" "}
          <Link to="/signup" style={{ color: "#4ade80" }}>create an account</Link> to save stocks to a watchlist that follows you across devices.
        </p>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>⭐ Your Watchlist</h1>

      {error && <p className="error">{error}</p>}
      {loading && <p style={{ textAlign: "center" }}>Loading watchlist...</p>}

      {tickers.length === 0 && !loading && !error && (
        <p style={{ color: "#9a9ca8" }}>
          No stocks starred yet. Go to the <Link to="/" style={{ color: "#4ade80" }}>Dashboard</Link> and click the star icon next to a stock to add it here.
        </p>
      )}

      <div className="watchlist-grid">
        {tickers.map((ticker) => {
          const pred = predictions[ticker];
          if (!pred) return null;
          const isPositive = pred.predicted_change_pct >= 0;

          return (
            <div key={ticker} className="watchlist-card">
              <div className="watchlist-card-header">
                <Link to={`/stock/${ticker}`} className="watchlist-ticker-link">
                  {ticker.replace(".NS", "")}
                </Link>
                <button className="remove-btn" onClick={() => handleRemove(ticker)} title="Remove">✕</button>
              </div>

              <p className="value">₹{pred.current_close}</p>

              <div className="price-row" style={{ marginTop: 8 }}>
                <span className={`value ${isPositive ? "change-positive" : "change-negative"}`} style={{ fontSize: "1rem" }}>
                  ₹{pred.predicted_next_close} ({isPositive ? "+" : ""}{pred.predicted_change_pct}%)
                </span>
              </div>

              <span className={`trend-badge ${pred.trend === "Bullish" ? "trend-bullish" : "trend-bearish"}`} style={{ marginTop: 10, display: "inline-block" }}>
                {pred.trend === "Bullish" ? "🟢" : "🔴"} {pred.trend}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Watchlist;
