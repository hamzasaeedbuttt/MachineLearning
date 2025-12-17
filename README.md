# Stock Market Predictor ML Project

A machine learning project that predicts stock market price direction and exact prices using Random Forest models.

## Project Structure

```
ML_Proj/
├── api/                    # FastAPI backend
│   └── main.py            # API endpoints
├── feature_pipeline/      # Feature engineering
│   └── build_features.py  # Build features from stock data
├── training_pipeline/     # Model training
│   └── train_model.py     # Train classifier and regressor
├── frontend/              # Streamlit frontend
│   └── app.py            # Web interface
├── model_registry/        # Saved models
└── requirements.txt       # Dependencies
```

## Setup

1. Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Running the Project

### Option 1: Run services separately (Recommended)

**Terminal 1 - Start API Server:**
```powershell
.\start_api.ps1
```
Or manually:
```powershell
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```powershell
.\start_frontend.ps1
```
Or manually:
```powershell
.\venv\Scripts\python.exe -m streamlit run frontend/app.py
```

### Option 2: Quick Start

1. **Train models** (if needed):
```powershell
.\venv\Scripts\python.exe feature_pipeline\build_features.py
.\venv\Scripts\python.exe training_pipeline\train_model.py
```

2. **Start API** (in one terminal):
```powershell
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Start Frontend** (in another terminal):
```powershell
.\venv\Scripts\python.exe -m streamlit run frontend/app.py
```

## Access URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501
- **Network API**: http://192.168.0.202:8000
- **Network Frontend**: http://192.168.0.202:8501

## API Endpoints

### POST /predict
Predict stock price direction and exact price.

**Request:**
```json
{
  "return": 0.01,
  "ma5": 320.5,
  "ma10": 318.2,
  "volatility": 0.02,
  "current_price": 320.0
}
```

**Response:**
```json
{
  "direction": {
    "prediction": 1,
    "meaning": "Price Up"
  },
  "predicted_price": 325.50,
  "current_price": 320.0,
  "predicted_change": 5.50,
  "predicted_change_percent": 1.72
}
```

## Features

- **Direction Prediction**: Predicts if stock price will go up or down
- **Price Prediction**: Predicts exact next day's closing price
- **Interactive Web Interface**: User-friendly Streamlit frontend
- **RESTful API**: FastAPI backend for predictions


