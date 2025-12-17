import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
import numpy as np

df = pd.read_csv("feature_store.csv", index_col=0)

# Create targets: direction (binary) and exact price (next day's close)
df["target_direction"] = (df["close"].shift(-1) > df["close"]).astype(int)
df["target_price"] = df["close"].shift(-1)
df.dropna(inplace=True)

X = df[["return", "ma5", "ma10", "volatility"]]
y_direction = df["target_direction"]
y_price = df["target_price"]

split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_direction_train, y_direction_test = y_direction.iloc[:split], y_direction.iloc[split:]
y_price_train, y_price_test = y_price.iloc[:split], y_price.iloc[split:]

# Train classifier for direction prediction
print("Training direction classifier...")
classifier = RandomForestClassifier(n_estimators=200, random_state=42)
classifier.fit(X_train, y_direction_train)

acc = accuracy_score(y_direction_test, classifier.predict(X_test))
print(f"Direction Accuracy: {acc:.4f}")

# Train regressor for exact price prediction
print("Training price regressor...")
regressor = RandomForestRegressor(n_estimators=200, random_state=42)
regressor.fit(X_train, y_price_train)

price_predictions = regressor.predict(X_test)
mse = mean_squared_error(y_price_test, price_predictions)
mae = mean_absolute_error(y_price_test, price_predictions)
rmse = np.sqrt(mse)
print(f"Price RMSE: ${rmse:.2f}")
print(f"Price MAE: ${mae:.2f}")

# Save both models
joblib.dump(classifier, "model_registry/random_forest_classifier_v1.joblib")
joblib.dump(regressor, "model_registry/random_forest_regressor_v1.joblib")
print("Models saved to registry")
