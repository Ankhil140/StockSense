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

app = FastAPI(title="StockSense - DevOps Predictor")

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
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "cap": "Large"},
    {"symbol": "INFY.NS", "name": "Infosys", "cap": "Large"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "cap": "Large"},
    {"symbol": "ITC.NS", "name": "ITC Ltd", "cap": "Large"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "cap": "Large"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "cap": "Large"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "cap": "Large"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "cap": "Large"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "cap": "Large"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "cap": "Large"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "cap": "Large"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "cap": "Large"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "cap": "Large"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "cap": "Large"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "cap": "Large"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "cap": "Large"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "cap": "Large"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "cap": "Large"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "cap": "Large"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports", "cap": "Large"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "cap": "Large"},
    {"symbol": "NTPC.NS", "name": "NTPC Ltd", "cap": "Large"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "cap": "Large"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid", "cap": "Large"},
    {"symbol": "ONGC.NS", "name": "ONGC", "cap": "Large"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "cap": "Large"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "cap": "Large"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life", "cap": "Large"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life", "cap": "Large"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "cap": "Large"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "cap": "Large"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "cap": "Large"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer", "cap": "Large"},
    {"symbol": "DRREDDY.NS", "name": "Dr Reddy's", "cap": "Large"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "cap": "Large"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "cap": "Large"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "cap": "Large"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "cap": "Large"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Lab", "cap": "Large"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco", "cap": "Large"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "cap": "Large"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "cap": "Large"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "cap": "Large"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "cap": "Large"},
    {"symbol": "UPL.NS", "name": "UPL", "cap": "Large"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "cap": "Large"},
    # Mid & Small Cap Leaders
    {"symbol": "ZOMATO.NS", "name": "Zomato", "cap": "Large"},
    {"symbol": "PAYTM.NS", "name": "Paytm (One97)", "cap": "Mid"},
    {"symbol": "POLICYBZR.NS", "name": "PB Fintech", "cap": "Mid"},
    {"symbol": "YESBANK.NS", "name": "Yes Bank", "cap": "Mid"},
    {"symbol": "IDFCFIRSTB.NS", "name": "IDFC First Bank", "cap": "Mid"},
    {"symbol": "VEDL.NS", "name": "Vedanta Ltd", "cap": "Large"},
    {"symbol": "IRCTC.NS", "name": "IRCTC", "cap": "Mid"},
    {"symbol": "RVNL.NS", "name": "Rail Vikas Nigam", "cap": "Small"},
    {"symbol": "IRFC.NS", "name": "Ind. Rail Finance", "cap": "Mid"},
    {"symbol": "SUZLON.NS", "name": "Suzlon Energy", "cap": "Small"},
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
