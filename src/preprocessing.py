import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

def preprocess_data(file_path, ticker, window_size=60):
    """
    Scale data and create windows for LSTM.
    """
    print(f"Preprocessing data for {ticker}...")
    df = pd.read_csv(file_path)
    
    # Use 'Close' price
    data = df['Close'].values.reshape(-1, 1)
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Save the scaler
    os.makedirs("models", exist_ok=True)
    import joblib
    joblib.dump(scaler, f"models/{ticker}_scaler.pkl")
    
    if len(scaled_data) <= window_size:
        print(f"Warning: Not enough data for window {window_size}. Using smaller window.")
        window_size = len(scaled_data) // 2
        if window_size < 1:
            raise ValueError(f"Insufficient data for ticker {ticker}. Need more than 1 point.")

    x_train = []
    y_train = []
    
    for i in range(window_size, len(scaled_data)):
        x_train.append(scaled_data[i-window_size:i, 0])
        y_train.append(scaled_data[i, 0])
        
    x_train, y_train = np.array(x_train), np.array(y_train)
    
    # Reshape for LSTM [samples, time steps, features]
    if len(x_train) > 0:
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    else:
        raise ValueError(f"Failed to create training sequences for {ticker}. Data too short.")
        
    return x_train, y_train, scaler

if __name__ == "__main__":
    # Test preprocessing
    from src.data_ingestion import fetch_stock_data
    fetch_stock_data("AAPL")
    preprocess_data("data/AAPL.csv", "AAPL")
