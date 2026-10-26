from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Allow importing from src/ when running from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.predict import predict_next_day
from src.config import TICKERS

app = FastAPI(
    title="Indian Stock Price Predictor API",
    description="Predicts next-day closing price and trend for NSE stocks. Not financial advice.",
    version="1.0.0"
)

# Allow the frontend (Sprint 7) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Stock Predictor API is running", "available_tickers": TICKERS}

@app.get("/tickers")
def get_tickers():
    return {"tickers": TICKERS}

@app.get("/predict/{ticker}")
def predict(ticker: str):
    ticker = ticker.upper()
    if not ticker.endswith(".NS"):
        ticker = ticker + ".NS"

    if ticker not in TICKERS:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' not supported. Available: {TICKERS}"
        )

    try:
        result = predict_next_day(ticker)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/history/{ticker}")
def get_history(ticker: str, days: int = 180):
    import pandas as pd
    from src.config import PROCESSED_DATA_DIR

    ticker = ticker.upper()
    if not ticker.endswith(".NS"):
        ticker = ticker + ".NS"

    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not supported.")

    clean_name = ticker.replace(".NS", "")
    df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{clean_name}_features.csv", parse_dates=["Date"])
    df = df.tail(days)  # most recent N trading days

    return {
        "ticker": ticker,
        "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "open": df["Open"].tolist(),
        "high": df["High"].tolist(),
        "low": df["Low"].tolist(),
        "close": df["Close"].tolist(),
        "volume": df["Volume"].tolist(),
    }
@app.get("/model-performance")
def get_model_performance():
    import pandas as pd
    import numpy as np
    import joblib
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, precision_score, recall_score
    from src.config import MODELS_DIR

    results = []
    for ticker in TICKERS:
        clean_name = ticker.replace(".NS", "")
        ticker_dir = f"{MODELS_DIR}/{clean_name}"

        return_model = joblib.load(f"{ticker_dir}/return_model.pkl")
        trend_model = joblib.load(f"{ticker_dir}/trend_model.pkl")

        X_test = pd.read_csv(f"{ticker_dir}/X_test.csv")
        y_return_test = pd.read_csv(f"{ticker_dir}/y_return_test.csv").iloc[:, 0]
        y_trend_test = pd.read_csv(f"{ticker_dir}/y_trend_test.csv").iloc[:, 0]
        close_test = pd.read_csv(f"{ticker_dir}/close_test.csv").iloc[:, 0]

        return_preds = return_model.predict(X_test)
        predicted_price = close_test.values * (1 + return_preds / 100)
        actual_price = close_test.values * (1 + y_return_test.values / 100)

        mape = float(np.mean(np.abs((actual_price - predicted_price) / actual_price)) * 100)
        r2 = float(r2_score(actual_price, predicted_price))
        rmse = float(np.sqrt(mean_squared_error(actual_price, predicted_price)))

        naive_price = close_test.values
        naive_mape = float(np.mean(np.abs((actual_price - naive_price) / actual_price)) * 100)

        trend_preds = trend_model.predict(X_test)
        acc = float(accuracy_score(y_trend_test, trend_preds))
        prec = float(precision_score(y_trend_test, trend_preds))
        rec = float(recall_score(y_trend_test, trend_preds))

        results.append({
            "ticker": ticker,
            "price_mape": round(mape, 2),
            "price_rmse": round(rmse, 2),
            "price_r2": round(r2, 4),
            "naive_baseline_mape": round(naive_mape, 2),
            "beats_naive": mape < naive_mape,
            "trend_accuracy": round(acc * 100, 2),
            "trend_precision": round(prec * 100, 2),
            "trend_recall": round(rec * 100, 2),
        })

    return {"results": results}

# ============ AUTH & WATCHLIST (database-backed) ============

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.database import init_db, get_db, User, WatchlistItem
from src.auth import hash_password, verify_password, create_access_token, decode_access_token

init_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class WatchlistAddRequest(BaseModel):
    ticker: str

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(email=req.email, hashed_password=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "email": user.email}

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "email": user.email}

@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email}

@app.get("/watchlist")
def get_user_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    return {"tickers": [item.ticker for item in items]}

@app.post("/watchlist")
def add_to_user_watchlist(req: WatchlistAddRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticker = req.ticker.upper()
    if not ticker.endswith(".NS"):
        ticker = ticker + ".NS"
    if ticker not in TICKERS:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not supported.")

    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id, WatchlistItem.ticker == ticker
    ).first()
    if existing:
        return {"message": "Already in watchlist"}

    item = WatchlistItem(ticker=ticker, user_id=current_user.id)
    db.add(item)
    db.commit()
    return {"message": "Added to watchlist"}

@app.delete("/watchlist/{ticker}")
def remove_from_user_watchlist(ticker: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticker = ticker.upper()
    item = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id, WatchlistItem.ticker == ticker
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return {"message": "Removed from watchlist"}
