function About() {
  return (
    <div className="app">
      <h1>ℹ️ About This Project</h1>

      <div className="about-section">
        <h3>What this is</h3>
        <p>
          This is an educational stock price prediction tool for NSE-listed Indian equities.
          It uses historical price data and technical indicators to generate next-day price
          and trend estimates. It was built as a learning project covering the full pipeline —
          data collection, cleaning, feature engineering, model training, evaluation, and deployment.
        </p>
      </div>

      <div className="about-section">
        <h3>How the predictions are made</h3>
        <p>
          Two separate machine learning models (Random Forests) are trained per stock:
        </p>
        <ul>
          <li>A <strong>regression model</strong> predicts the next day's percentage price change, which is used to reconstruct a predicted closing price.</li>
          <li>A <strong>classification model</strong> predicts the probability of the price moving up (Bullish) or down (Bearish), which becomes the trend call and confidence score.</li>
        </ul>
        <p>
          Both models are trained on technical indicators — RSI, MACD, moving averages, and recent
          price momentum — computed from 10 years of historical daily data. Models are evaluated on
          a held-out, chronologically later test period they never saw during training, to simulate
          real-world use.
        </p>
      </div>

      <div className="about-section">
        <h3>Known limitations</h3>
        <p>
          Daily stock price movement is heavily influenced by unpredictable, external factors —
          news, earnings, macroeconomic events, market sentiment — that aren't captured by
          historical price patterns alone. Our own evaluation (see the <a href="/performance" style={{ color: "#4ade80" }}>Model Performance</a> page)
          shows trend prediction accuracy close to a coin flip on most days, which is consistent
          with well-documented research on the difficulty of short-term price forecasting.
          Price predictions track closely to "no significant change," which is usually the correct call,
          since large daily moves are relatively rare.
        </p>
      </div>

      <div className="about-section">
        <h3>Tech stack</h3>
        <ul>
          <li><strong>Data:</strong> Yahoo Finance via yfinance</li>
          <li><strong>ML:</strong> scikit-learn (Random Forest Regressor + Classifier)</li>
          <li><strong>Backend:</strong> FastAPI</li>
          <li><strong>Frontend:</strong> React + Vite, charts via Plotly.js</li>
        </ul>
      </div>

      <p className="disclaimer">
        ⚠️ This tool provides statistical estimates based on historical patterns. It is not financial
        advice, and should not be used as the sole basis for any investment decision. Please consult
        a licensed financial advisor before trading or investing.
      </p>
    </div>
  );
}

export default About;
