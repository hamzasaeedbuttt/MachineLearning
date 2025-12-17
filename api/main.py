from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from feature_pipeline.stock_data_utils import get_multiple_stocks_features, POPULAR_STOCKS
from monitoring.data_drift import detect_data_drift, get_drift_summary

app = FastAPI(title="Quant Vista API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load all models
print("Loading ML models...")
models = {}

# Core models
try:
    models['linear_regression'] = joblib.load("model_registry/linear_regression_price_v1.joblib")
    models['logistic_regression'] = joblib.load("model_registry/logistic_regression_direction_v1.joblib")
    models['decision_tree_classifier'] = joblib.load("model_registry/decision_tree_classifier_v1.joblib")
    models['decision_tree_regressor'] = joblib.load("model_registry/decision_tree_regressor_v1.joblib")
    models['random_forest_classifier'] = joblib.load("model_registry/random_forest_classifier_v1.joblib")
    models['random_forest_regressor'] = joblib.load("model_registry/random_forest_regressor_v1.joblib")
    models['gradient_boosting'] = joblib.load("model_registry/gradient_boosting_classifier_v1.joblib")
    models['xgboost_classifier'] = joblib.load("model_registry/xgboost_classifier_v1.joblib")
    models['xgboost_return'] = joblib.load("model_registry/xgboost_return_v1.joblib")
    models['lightgbm_classifier'] = joblib.load("model_registry/lightgbm_classifier_v1.joblib")
    models['lightgbm_return'] = joblib.load("model_registry/lightgbm_return_v1.joblib")
    
    try:
        models['catboost_classifier'] = joblib.load("model_registry/catboost_classifier_v1.joblib")
    except:
        print("Note: CatBoost model not found (optional)")
    
    print("All models loaded successfully!")
except Exception as e:
    print(f"Warning: Some models not found. Please run train_ensemble.py first. Error: {e}")
    # Fallback to old models if available
    try:
        models['random_forest_classifier'] = joblib.load("model_registry/random_forest_classifier_v1.joblib")
        models['random_forest_regressor'] = joblib.load("model_registry/random_forest_regressor_v1.joblib")
        print("Using fallback models (Random Forest only)")
    except:
        raise Exception("No models found. Please train models first.")

@app.get("/")
def home():
    return {"message": "Quant Vista API is running", "models_loaded": list(models.keys())}

@app.post("/predict")
def predict_single(features: dict):
    """
    Predict for a single stock using ensemble of models.
    """
    try:
        features_df = pd.DataFrame([{
            "return": features["return"],
            "ma5": features["ma5"],
            "ma10": features["ma10"],
            "volatility": features["volatility"]
        }])
        
        current_price = features.get("current_price", 0)
        
        # Ensemble predictions
        predictions = {}
        
        # Direction predictions (ensemble)
        direction_predictions = []
        if 'logistic_regression' in models:
            direction_predictions.append(('logistic', models['logistic_regression'].predict(features_df)[0]))
        if 'decision_tree_classifier' in models:
            direction_predictions.append(('decision_tree', models['decision_tree_classifier'].predict(features_df)[0]))
        if 'random_forest_classifier' in models:
            direction_predictions.append(('random_forest', models['random_forest_classifier'].predict(features_df)[0]))
        if 'gradient_boosting' in models:
            direction_predictions.append(('gradient_boosting', models['gradient_boosting'].predict(features_df)[0]))
        if 'xgboost_classifier' in models:
            direction_predictions.append(('xgboost', models['xgboost_classifier'].predict(features_df)[0]))
        if 'lightgbm_classifier' in models:
            direction_predictions.append(('lightgbm', models['lightgbm_classifier'].predict(features_df)[0]))
        if 'catboost_classifier' in models:
            direction_predictions.append(('catboost', models['catboost_classifier'].predict(features_df)[0]))
        
        # Majority vote for direction
        if direction_predictions:
            direction_votes = [pred[1] for pred in direction_predictions]
            ensemble_direction = 1 if sum(direction_votes) > len(direction_votes) / 2 else 0
            predictions['direction'] = {
                'prediction': int(ensemble_direction),
                'meaning': 'Price Up' if ensemble_direction == 1 else 'Price Down',
                'model_agreement': f"{sum(direction_votes)}/{len(direction_votes)} models predict {'Up' if ensemble_direction == 1 else 'Down'}",
                'individual_predictions': {name: int(pred) for name, pred in direction_predictions}
            }
        
        # Price predictions (ensemble average)
        price_predictions = []
        if 'linear_regression' in models:
            price_predictions.append(('linear_regression', float(models['linear_regression'].predict(features_df)[0])))
        if 'decision_tree_regressor' in models:
            price_predictions.append(('decision_tree', float(models['decision_tree_regressor'].predict(features_df)[0])))
        if 'random_forest_regressor' in models:
            price_predictions.append(('random_forest', float(models['random_forest_regressor'].predict(features_df)[0])))
        
        if price_predictions:
            ensemble_price = np.mean([pred[1] for pred in price_predictions])
            predictions['price'] = {
                'predicted_price': round(ensemble_price, 2),
                'model_predictions': {name: round(pred, 2) for name, pred in price_predictions},
                'price_range': {
                    'min': round(min([pred[1] for pred in price_predictions]), 2),
                    'max': round(max([pred[1] for pred in price_predictions]), 2)
                }
            }
        
        # Return predictions (for alpha generation)
        return_predictions = []
        if 'xgboost_return' in models:
            return_predictions.append(('xgboost', float(models['xgboost_return'].predict(features_df)[0])))
        if 'lightgbm_return' in models:
            return_predictions.append(('lightgbm', float(models['lightgbm_return'].predict(features_df)[0])))
        
        if return_predictions:
            ensemble_return = np.mean([pred[1] for pred in return_predictions])
            predictions['expected_return'] = {
                'predicted_return_pct': round(ensemble_return * 100, 2),
                'model_predictions': {name: round(pred * 100, 2) for name, pred in return_predictions}
            }
            
            # Alpha generation (expected return adjusted)
            if current_price > 0:
                alpha = ensemble_return * current_price
                predictions['alpha'] = round(alpha, 2)
        
        # Feature impact analysis (from Linear Regression)
        if 'linear_regression' in models:
            lr_model = models['linear_regression']
            feature_impact = {
                'return': round(float(lr_model.coef_[0]), 4),
                'ma5': round(float(lr_model.coef_[1]), 4),
                'ma10': round(float(lr_model.coef_[2]), 4),
                'volatility': round(float(lr_model.coef_[3]), 4)
            }
            predictions['feature_impact'] = feature_impact
        
        # Data drift detection
        drift_results = detect_data_drift({
            'return': features['return'],
            'ma5': features['ma5'],
            'ma10': features['ma10'],
            'volatility': features['volatility']
        })
        predictions['data_drift'] = {
            'has_drift': drift_results.get('has_drift', False),
            'drift_severity': drift_results.get('drift_severity', 'none'),
            'summary': get_drift_summary(drift_results),
            'feature_analysis': drift_results.get('features_analyzed', [])
        }
        
        result = predictions.copy()
        if current_price > 0 and 'price' in predictions:
            result['current_price'] = current_price
            price_change = predictions['price']['predicted_price'] - current_price
            result['predicted_change'] = round(price_change, 2)
            result['predicted_change_percent'] = round((price_change / current_price) * 100, 2)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/recommendations")
def get_stock_recommendations(limit: int = 10, symbols: str = None):
    """
    Get stock recommendations using ensemble ML models, ranked by predicted increase.
    Includes data drift analysis for each stock.
    """
    try:
        # Determine which stocks to analyze
        if symbols:
            stock_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            stock_list = POPULAR_STOCKS[:limit]
        
        # Fetch features for all stocks
        print(f"Fetching data for {len(stock_list)} stocks...")
        stocks_data = get_multiple_stocks_features(stock_list)
        
        if not stocks_data:
            raise HTTPException(status_code=500, detail="Failed to fetch stock data")
        
        # Make predictions for all stocks
        recommendations = []
        for stock in stocks_data:
            try:
                # Prepare features
                features_df = pd.DataFrame([{
                    "return": stock["return"],
                    "ma5": stock["ma5"],
                    "ma10": stock["ma10"],
                    "volatility": stock["volatility"]
                }])
                
                # Ensemble direction prediction
                direction_predictions = []
                if 'logistic_regression' in models:
                    direction_predictions.append(models['logistic_regression'].predict(features_df)[0])
                if 'random_forest_classifier' in models:
                    direction_predictions.append(models['random_forest_classifier'].predict(features_df)[0])
                if 'xgboost_classifier' in models:
                    direction_predictions.append(models['xgboost_classifier'].predict(features_df)[0])
                if 'lightgbm_classifier' in models:
                    direction_predictions.append(models['lightgbm_classifier'].predict(features_df)[0])
                
                direction_pred = 1 if sum(direction_predictions) > len(direction_predictions) / 2 else 0
                
                # Ensemble price prediction
                price_predictions = []
                if 'linear_regression' in models:
                    price_predictions.append(models['linear_regression'].predict(features_df)[0])
                if 'random_forest_regressor' in models:
                    price_predictions.append(models['random_forest_regressor'].predict(features_df)[0])
                
                predicted_price = float(np.mean(price_predictions)) if price_predictions else 0
                current_price = stock["current_price"]
                
                # Return prediction (alpha)
                return_pred = 0
                if 'xgboost_return' in models:
                    return_pred = float(models['xgboost_return'].predict(features_df)[0])
                
                # Calculate metrics
                price_change = predicted_price - current_price
                price_change_percent = (price_change / current_price) * 100
                
                # Data drift detection
                drift_results = detect_data_drift({
                    'return': stock['return'],
                    'ma5': stock['ma5'],
                    'ma10': stock['ma10'],
                    'volatility': stock['volatility']
                })
                
                recommendations.append({
                    "symbol": stock["symbol"],
                    "current_price": round(current_price, 2),
                    "predicted_price": round(predicted_price, 2),
                    "predicted_change": round(price_change, 2),
                    "predicted_change_percent": round(price_change_percent, 2),
                    "expected_return_pct": round(return_pred * 100, 2),
                    "direction": "Price Up" if direction_pred == 1 else "Price Down",
                    "direction_confidence": f"{sum(direction_predictions)}/{len(direction_predictions)}",
                    "data_drift": {
                        "has_drift": drift_results.get('has_drift', False),
                        "severity": drift_results.get('drift_severity', 'none'),
                        "summary": get_drift_summary(drift_results)
                    }
                })
            except Exception as e:
                print(f"Error predicting for {stock.get('symbol', 'unknown')}: {str(e)}")
                continue
        
        # Sort by predicted change percent
        recommendations.sort(key=lambda x: x["predicted_change_percent"], reverse=True)
        
        # Filter positive predictions and limit
        positive_recommendations = [r for r in recommendations if r["predicted_change_percent"] > 0]
        top_recommendations = positive_recommendations[:limit] if positive_recommendations else recommendations[:limit]
        
        return {
            "total_analyzed": len(stocks_data),
            "recommendations": top_recommendations,
            "models_used": list(models.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

