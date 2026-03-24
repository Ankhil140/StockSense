import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import pandas as pd
import os

def get_prediction(ticker="AAPL"):
    """
    Get the next predicted closing price for a given ticker.
    """
    model_path = f"models/{ticker}_model.h5"
    scaler_path = f"models/{ticker}_scaler.pkl"
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        from src.train import train_model
        train_model(ticker)
        
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    
    # Get recent data (Real-time attempt with 1m interval for the last day)
    from src.data_ingestion import fetch_stock_data
    try:
        # Try to get enough minutes for the window
        df = fetch_stock_data(ticker, period="1d", interval="1m")
        if len(df) < 60:
            print("Not enough 1m data, falling back to 1h...")
            df = fetch_stock_data(ticker, period="7d", interval="1h")
    except Exception as e:
        print(f"Intraday fetch failed: {e}. Falling back to daily.")
        df = fetch_stock_data(ticker, period="60d", interval="1d")
    
    # Take the last 60 steps
    df = df.tail(60)
    
    # Preprocess
    data = df['Close'].values.reshape(-1, 1)
    scaled_data = scaler.transform(data)
    
    # Shape for model [1, window_size, 1]
    input_data = np.reshape(scaled_data, (1, scaled_data.shape[0], 1))
    
    prediction = model.predict(input_data)
    prediction = scaler.inverse_transform(prediction)
    
    return float(prediction[0][0])

if __name__ == "__main__":
    try:
        p = get_prediction("RELIANCE.NS")
        print(f"Predicted price for RELIANCE.NS: {p}")
    except Exception as e:
        import traceback
        traceback.print_exc()
