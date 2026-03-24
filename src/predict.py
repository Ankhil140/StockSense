import numpy as np
import os
import joblib
import pandas as pd

# Try to use tflite-runtime (smaller) first, then fall back to full tensorflow for local dev
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        from tensorflow import lite as tflite
    except ImportError:
        tflite = None

def get_prediction(ticker="AAPL"):
    """
    Get the next predicted closing price for a given ticker using TFLite.
    """
    tflite_path = f"models/{ticker}_model.tflite"
    h5_path = f"models/{ticker}_model.h5"
    scaler_path = f"models/{ticker}_scaler.pkl"
    
    # Priority: TFLite (for Vercel), then H5 (legacy)
    if not os.path.exists(tflite_path) and not os.path.exists(h5_path):
        from src.train import train_model
        train_model(ticker)
        # Check again - train_model should now ideally produce both, or we convert on the fly
        # For simplicity, we assume models exist or are trained.
        
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

    if os.path.exists(tflite_path) and tflite:
        # TFLite Inference
        interpreter = tflite.Interpreter(model_path=tflite_path)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        prediction = interpreter.get_tensor(output_details[0]['index'])
    else:
        # Fallback to Keras if TFLite not found or runtime missing
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
