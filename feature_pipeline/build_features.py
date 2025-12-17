import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"
SYMBOL = "MSFT"

url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": SYMBOL,
    "apikey": API_KEY
}

data = requests.get(url, params=params).json()

df = pd.DataFrame.from_dict(
    data["Time Series (Daily)"], orient="index"
)

df.columns = ["open", "high", "low", "close", "volume"]
df = df.astype(float)
df.index = pd.to_datetime(df.index)
df.sort_index(inplace=True)

df["return"] = df["close"].pct_change()
df["ma5"] = df["close"].rolling(5).mean()
df["ma10"] = df["close"].rolling(10).mean()
df["volatility"] = df["return"].rolling(5).std()

df.dropna(inplace=True)

# FEATURE STORE (CSV = acceptable for course)
df.to_csv("feature_store.csv")

print("Features stored successfully")
