from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from src.predict import get_prediction
import uvicorn
import os
import sys
import uuid

# Ensure project root is in path
sys.path.append(os.path.dirname(__file__))

app = FastAPI(title="StockAI - DevOps Predictor")

import base64

class LoginRequest(BaseModel):
    username: str
    password: str

def get_current_user(session_id: str = Cookie(None)):
    if session_id:
        try:
            # Simple stateless session: base64 encoded username
            # In production, use JWT with a secret key
            return base64.b64decode(session_id).decode('utf-8')
        except:
            return None
    return None

class PredictionRequest(BaseModel):
    ticker: str

class PredictionResponse(BaseModel):
    ticker: str
    predicted_price: float

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def read_root(user=Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/login")
def login_get():
    return FileResponse(os.path.join(static_path, "login.html"))

@app.post("/login")
def login_post(request: LoginRequest, response: Response):
    if request.username == "admin" and request.password == "password123":
        # Stateless session: base64 encoded username
        session_id = base64.b64encode(request.username.encode('utf-8')).decode('utf-8')
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return {"status": "success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="session_id")
    return RedirectResponse(url="/login")

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        prediction = get_prediction(request.ticker)
        return PredictionResponse(ticker=request.ticker, predicted_price=prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

POPULAR_STOCKS = [
    {"symbol": "^NSEI", "name": "Nifty 50", "cap": "Index"},
    {"symbol": "^BSESN", "name": "SENSEX", "cap": "Index"},
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "cap": "Large"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "cap": "Large"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "cap": "Large"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "cap": "Large"},
    {"symbol": "TRENT.NS", "name": "Trent Ltd", "cap": "Mid"},
    {"symbol": "CUMMINSIND.NS", "name": "Cummins India", "cap": "Mid"},
    {"symbol": "FEDERALBNK.NS", "name": "Federal Bank", "cap": "Mid"},
    {"symbol": "SUZLON.NS", "name": "Suzlon Energy", "cap": "Small"},
    {"symbol": "WIPRO.NS", "name": "Wipro Ltd", "cap": "Large"},
    {"symbol": "YESBANK.NS", "name": "Yes Bank", "cap": "Small"},
]

@app.get("/stocks")
def get_stocks(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return POPULAR_STOCKS

@app.get("/history/{ticker}")
def get_history(ticker: str, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        from src.data_ingestion import fetch_stock_data
        # Try daily first as it's more stable
        df = fetch_stock_data(ticker, period="60d", interval="1d")
        history = []
        for index, row in df.iterrows():
            history.append({
                "date": str(index.date()),
                "price": float(row['Close'])
            })
        return history
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=f"Stock '{ticker}' data is temporarily unavailable on Yahoo Finance.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intraday/{ticker}")
def get_intraday(ticker: str, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        from src.data_ingestion import fetch_stock_data
        # Try 1m for 1d first
        try:
            df = fetch_stock_data(ticker, period="1d", interval="1m")
        except ValueError:
            # Fallback to last available intraday sessions
            df = fetch_stock_data(ticker, period="5d", interval="5m")
            
        history = []
        for index, row in df.iterrows():
            history.append({
                "time": index.strftime("%H:%M") if hasattr(index, 'strftime') else str(index),
                "price": float(row['Close'])
            })
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
