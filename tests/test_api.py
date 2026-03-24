from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Stock Prediction API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_endpoint_error():
    # Test with invalid ticker to check error handling
    response = client.post("/predict", json={"ticker": "INVALID_TICKER_123"})
    assert response.status_code == 500
