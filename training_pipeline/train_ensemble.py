import pandas as pd
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, classification_report
import xgboost as xgb
import lightgbm as lgb
try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("Note: CatBoost not available. Install with: pip install catboost")

print("="*60)
print("Training Ensemble of ML Models for Stock Prediction")
print("="*60)

# Load training data
df = pd.read_csv("feature_store.csv", index_col=0)

# Create targets: direction (binary) and exact price (next day's close)
df["target_direction"] = (df["close"].shift(-1) > df["close"]).astype(int)
df["target_price"] = df["close"].shift(-1)
df["target_return"] = (df["close"].shift(-1) - df["close"]) / df["close"]
df.dropna(inplace=True)

X = df[["return", "ma5", "ma10", "volatility"]]
y_direction = df["target_direction"]
y_price = df["target_price"]
y_return = df["target_return"]

# Train-test split
split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_direction_train, y_direction_test = y_direction.iloc[:split], y_direction.iloc[split:]
y_price_train, y_price_test = y_price.iloc[:split], y_price.iloc[split:]
y_return_train, y_return_test = y_return.iloc[:split], y_return.iloc[split:]

print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)} samples")

models = {}
results = {}

# ============================================================================
# 1. LINEAR REGRESSION - Next-day price prediction & Feature impact
# ============================================================================
print("\n[1/8] Training Linear Regression for Price Prediction...")
lr_price = LinearRegression()
lr_price.fit(X_train, y_price_train)
lr_price_pred = lr_price.predict(X_test)
lr_rmse = np.sqrt(mean_squared_error(y_price_test, lr_price_pred))
lr_mae = mean_absolute_error(y_price_test, lr_price_pred)
print(f"   RMSE: ${lr_rmse:.2f}, MAE: ${lr_mae:.2f}")

# Feature importance (coefficients)
feature_importance_lr = pd.DataFrame({
    'feature': X.columns,
    'coefficient': lr_price.coef_,
    'abs_coefficient': np.abs(lr_price.coef_)
}).sort_values('abs_coefficient', ascending=False)
print(f"   Feature Impact: {dict(zip(feature_importance_lr['feature'], feature_importance_lr['coefficient']))}")

models['linear_regression_price'] = lr_price
results['linear_regression'] = {
    'rmse': lr_rmse,
    'mae': lr_mae,
    'feature_importance': feature_importance_lr.to_dict('records')
}

# ============================================================================
# 2. LOGISTIC REGRESSION - Direction prediction (Up/Down)
# ============================================================================
print("\n[2/8] Training Logistic Regression for Direction Prediction...")
logistic = LogisticRegression(random_state=42, max_iter=1000)
logistic.fit(X_train, y_direction_train)
logistic_pred = logistic.predict(X_test)
logistic_acc = accuracy_score(y_direction_test, logistic_pred)
print(f"   Accuracy: {logistic_acc:.4f}")

models['logistic_regression_direction'] = logistic
results['logistic_regression'] = {'accuracy': logistic_acc}

# ============================================================================
# 3. DECISION TREE - Rule-based behavior & Feature interaction
# ============================================================================
print("\n[3/8] Training Decision Tree Classifier...")
dt_classifier = DecisionTreeClassifier(random_state=42, max_depth=10, min_samples_split=5)
dt_classifier.fit(X_train, y_direction_train)
dt_classifier_pred = dt_classifier.predict(X_test)
dt_classifier_acc = accuracy_score(y_direction_test, dt_classifier_pred)
print(f"   Accuracy: {dt_classifier_acc:.4f}")

print("\n[4/8] Training Decision Tree Regressor...")
dt_regressor = DecisionTreeRegressor(random_state=42, max_depth=10, min_samples_split=5)
dt_regressor.fit(X_train, y_price_train)
dt_regressor_pred = dt_regressor.predict(X_test)
dt_regressor_rmse = np.sqrt(mean_squared_error(y_price_test, dt_regressor_pred))
print(f"   RMSE: ${dt_regressor_rmse:.2f}")

models['decision_tree_classifier'] = dt_classifier
models['decision_tree_regressor'] = dt_regressor
results['decision_tree'] = {
    'classifier_accuracy': dt_classifier_acc,
    'regressor_rmse': dt_regressor_rmse
}

# ============================================================================
# 4. RANDOM FOREST - Price direction & Volatility prediction
# ============================================================================
print("\n[5/8] Training Random Forest Classifier...")
rf_classifier = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
rf_classifier.fit(X_train, y_direction_train)
rf_classifier_pred = rf_classifier.predict(X_test)
rf_classifier_acc = accuracy_score(y_direction_test, rf_classifier_pred)
print(f"   Accuracy: {rf_classifier_acc:.4f}")

print("   Training Random Forest Regressor for Price...")
rf_regressor = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
rf_regressor.fit(X_train, y_price_train)
rf_regressor_pred = rf_regressor.predict(X_test)
rf_regressor_rmse = np.sqrt(mean_squared_error(y_price_test, rf_regressor_pred))
print(f"   RMSE: ${rf_regressor_rmse:.2f}")

models['random_forest_classifier'] = rf_classifier
models['random_forest_regressor'] = rf_regressor
results['random_forest'] = {
    'classifier_accuracy': rf_classifier_acc,
    'regressor_rmse': rf_regressor_rmse
}

# ============================================================================
# 5. GRADIENT BOOSTING (sklearn) - General purpose
# ============================================================================
print("\n[6/8] Training Gradient Boosting Classifier...")
gb_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5)
gb_classifier.fit(X_train, y_direction_train)
gb_classifier_pred = gb_classifier.predict(X_test)
gb_classifier_acc = accuracy_score(y_direction_test, gb_classifier_pred)
print(f"   Accuracy: {gb_classifier_acc:.4f}")

models['gradient_boosting_classifier'] = gb_classifier
results['gradient_boosting'] = {'classifier_accuracy': gb_classifier_acc}

# ============================================================================
# 6. XGBOOST - Direction classification, Return regression, Alpha generation
# ============================================================================
print("\n[7/8] Training XGBoost Classifier...")
xgb_classifier = xgb.XGBClassifier(n_estimators=100, random_state=42, max_depth=5, eval_metric='logloss')
xgb_classifier.fit(X_train, y_direction_train)
xgb_classifier_pred = xgb_classifier.predict(X_test)
xgb_classifier_acc = accuracy_score(y_direction_test, xgb_classifier_pred)
print(f"   Direction Accuracy: {xgb_classifier_acc:.4f}")

print("   Training XGBoost Regressor for Returns...")
xgb_return = xgb.XGBRegressor(n_estimators=100, random_state=42, max_depth=5)
xgb_return.fit(X_train, y_return_train)
xgb_return_pred = xgb_return.predict(X_test)
xgb_return_rmse = np.sqrt(mean_squared_error(y_return_test, xgb_return_pred))
print(f"   Return RMSE: {xgb_return_rmse:.4f}")

models['xgboost_classifier'] = xgb_classifier
models['xgboost_return'] = xgb_return
results['xgboost'] = {
    'classifier_accuracy': xgb_classifier_acc,
    'return_rmse': xgb_return_rmse
}

# ============================================================================
# 7. LIGHTGBM - Direction classification, Return regression
# ============================================================================
print("\n[8/8] Training LightGBM Classifier...")
lgb_classifier = lgb.LGBMClassifier(n_estimators=100, random_state=42, max_depth=5, verbose=-1)
lgb_classifier.fit(X_train, y_direction_train)
lgb_classifier_pred = lgb_classifier.predict(X_test)
lgb_classifier_acc = accuracy_score(y_direction_test, lgb_classifier_pred)
print(f"   Direction Accuracy: {lgb_classifier_acc:.4f}")

print("   Training LightGBM Regressor for Returns...")
lgb_return = lgb.LGBMRegressor(n_estimators=100, random_state=42, max_depth=5, verbose=-1)
lgb_return.fit(X_train, y_return_train)
lgb_return_pred = lgb_return.predict(X_test)
lgb_return_rmse = np.sqrt(mean_squared_error(y_return_test, lgb_return_pred))
print(f"   Return RMSE: {lgb_return_rmse:.4f}")

models['lightgbm_classifier'] = lgb_classifier
models['lightgbm_return'] = lgb_return
results['lightgbm'] = {
    'classifier_accuracy': lgb_classifier_acc,
    'return_rmse': lgb_return_rmse
}

# ============================================================================
# 8. CATBOOST - If available
# ============================================================================
if CATBOOST_AVAILABLE:
    print("\n[9/9] Training CatBoost Classifier...")
    cat_classifier = cb.CatBoostClassifier(iterations=100, random_state=42, depth=5, verbose=False)
    cat_classifier.fit(X_train, y_direction_train)
    cat_classifier_pred = cat_classifier.predict(X_test)
    cat_classifier_acc = accuracy_score(y_direction_test, cat_classifier_pred)
    print(f"   Direction Accuracy: {cat_classifier_acc:.4f}")
    
    models['catboost_classifier'] = cat_classifier
    results['catboost'] = {'classifier_accuracy': cat_classifier_acc}
else:
    print("\n[Note] CatBoost skipped (not installed)")

# ============================================================================
# Save all models and training data statistics for drift detection
# ============================================================================
print("\n" + "="*60)
print("Saving Models...")

for model_name, model in models.items():
    joblib.dump(model, f"model_registry/{model_name}_v1.joblib")
    print(f"   Saved: {model_name}_v1.joblib")

# Save training data statistics for drift detection
training_stats = {
    'mean': X_train.mean().to_dict(),
    'std': X_train.std().to_dict(),
    'min': X_train.min().to_dict(),
    'max': X_train.max().to_dict(),
    'percentiles': {
        '25': X_train.quantile(0.25).to_dict(),
        '50': X_train.quantile(0.50).to_dict(),
        '75': X_train.quantile(0.75).to_dict()
    }
}

joblib.dump(training_stats, "model_registry/training_stats.joblib")
print("   Saved: training_stats.joblib")

# Save results summary
results_df = pd.DataFrame(results).T
results_df.to_csv("model_registry/model_results.csv")
print("   Saved: model_results.csv")

print("\n" + "="*60)
print("Training Complete!")
print("="*60)
print("\nModel Performance Summary:")
print(results_df.to_string())

