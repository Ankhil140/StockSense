import numpy as np
import os
import joblib
import pandas as pd

# Use onnxruntime for lightweight inference
try:
    import onnxruntime as ort
except ImportError:
    ort = None

def get_prediction(ticker="AAPL"):
    """
    Get the next predicted closing price for a given ticker using ONNX.
    """
    # Use absolute paths relative to this file's directory
    # src/predict.py -> models/..
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    onnx_path = os.path.join(base_dir, "models", f"{ticker}_model.onnx")
    h5_path = os.path.join(base_dir, "models", f"{ticker}_model.h5")
    scaler_path = os.path.join(base_dir, "models", f"{ticker}_scaler.pkl")
    
    # Priority: ONNX (for Vercel), then H5 (local fallback)
    if not os.path.exists(onnx_path) and not os.path.exists(h5_path):
        from src.train import train_model
        train_model(ticker)
        
    scaler = joblib.load(scaler_path)
    
    # Get recent data
    from src.data_ingestion import fetch_stock_data
    try:
        df = fetch_stock_data(ticker, period="1d", interval="1m")
        if len(df) < 60:
            df = fetch_stock_data(ticker, period="7d", interval="1h")
    except Exception:
        df = fetch_stock_data(ticker, period="60d", interval="1d")
    
    df = df.tail(60)
    data = df['Close'].values.reshape(-1, 1)
    scaled_data = scaler.transform(data)
    input_data = np.reshape(scaled_data, (1, 60, 1)).astype(np.float32)

    if os.path.exists(onnx_path) and ort:
        # ONNX Inference
        session = ort.InferenceSession(onnx_path)
        input_name = session.get_inputs()[0].name
        prediction = session.run(None, {input_name: input_data})[0]
    else:
        # Fallback to Keras if ONNX not found or runtime missing
        from tensorflow.keras.models import load_model
        model = load_model(h5_path)
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
