import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from src.preprocessing import preprocess_data
import os

def train_model(ticker="AAPL"):
    """
    Train an LSTM model for stock price prediction.
    """
    file_path = f"data/{ticker}_1d.csv"
    from src.data_ingestion import fetch_stock_data
    
    # Always ensure we have enough data for training (2 years)
    if os.path.exists(file_path):
        # Check if file has enough lines (approx)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if len(lines) < 100:
                print(f"Existing data for {ticker} is too short ({len(lines)} lines). Refetching...")
                fetch_stock_data(ticker, period="2y", interval="1d")
    else:
        fetch_stock_data(ticker, period="2y", interval="1d")
        
    x_train, y_train, scaler = preprocess_data(file_path, ticker)
    
    print(f"Training LSTM model for {ticker}...")
    model = Sequential()
    
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    # Train the model
    # Note: For production use more epochs, this is for demonstration
    model.fit(x_train, y_train, batch_size=32, epochs=5)
    
    # Save the model
    os.makedirs("models", exist_ok=True)
    model.save(f"models/{ticker}_model.h5")
    print(f"Model saved to models/{ticker}_model.h5")
    
    return model

if __name__ == "__main__":
    train_model("AAPL")
