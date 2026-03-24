# Stock Prediction with DevOps

Automated stock price prediction system using LSTM and DevOps best practices.

## Features
- **Data Ingestion**: Historical data from Yahoo Finance.
- **ML Model**: LSTM (Long Short-Term Memory) network for time-series prediction.
- **REST API**: FastAPI for serving predictions.
- **Containerization**: Docker and Docker Compose support.
- **CI/CD**: GitHub Actions for testing and building.

## Setup

### Local Development (Python)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   python src/app.py
   ```

### Using Docker
1. Build and run:
   ```bash
   docker-compose up --build
   ```

## Usage
Send a POST request to `/predict`:
```bash
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"ticker": "AAPL"}'
```

## DevOps
The project includes:
- `Dockerfile`: Multi-stage build for production.
- `ci.yml`: Automated testing and image build on push to main.
- `tests/`: Unit tests for API endpoints.
