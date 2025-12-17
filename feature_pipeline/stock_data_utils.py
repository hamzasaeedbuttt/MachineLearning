import requests
import pandas as pd
import time
from typing import Dict, List, Optional

API_KEY = "4WJ1XNU3HTMJPN11"
BASE_URL = "https://www.alphavantage.co/query"

# Popular stock symbols to analyze
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM",
    "V", "JNJ", "WMT", "MA", "PG", "UNH", "DIS", "HD", "BAC", "PYPL",
    "NFLX", "ADBE", "CMCSA", "XOM", "CSCO", "PFE", "VZ", "INTC", "T",
    "ABBV", "PEP", "COST", "CVX", "MRK", "TMO", "ACN", "ABT", "WFC"
]

def fetch_stock_data(symbol: str, api_key: str = API_KEY) -> Optional[pd.DataFrame]:
    """
    Fetch stock data from Alpha Vantage API for a given symbol.
    
    Args:
        symbol: Stock ticker symbol
        api_key: Alpha Vantage API key
    
    Returns:
        DataFrame with stock data or None if error
    """
    url = BASE_URL
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Error Message" in data:
            print(f"    API Error for {symbol}: {data['Error Message']}")
            return None
        if "Note" in data:
            print(f"    API Note for {symbol}: {data['Note'][:100]}...")  # Rate limit or key issue
            return None
        if "Information" in data:
            print(f"    API Information for {symbol}: {data['Information'][:100]}...")  # Rate limit
            return None
        
        if "Time Series (Daily)" not in data:
            print(f"    No time series data for {symbol}")
            return None
        
        df = pd.DataFrame.from_dict(
            data["Time Series (Daily)"], orient="index"
        )
        
        df.columns = ["open", "high", "low", "close", "volume"]
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return None

def calculate_features(df: pd.DataFrame) -> Optional[Dict]:
    """
    Calculate features from stock data for prediction.
    
    Args:
        df: DataFrame with stock price data
    
    Returns:
        Dictionary with features or None if insufficient data
    """
    if df is None or len(df) < 10:
        return None
    
    try:
        df = df.copy()
        df["return"] = df["close"].pct_change()
        df["ma5"] = df["close"].rolling(5).mean()
        df["ma10"] = df["close"].rolling(10).mean()
        df["volatility"] = df["return"].rolling(5).std()
        
        df.dropna(inplace=True)
        
        if len(df) == 0:
            return None
        
        # Get the latest row (most recent data)
        latest = df.iloc[-1]
        current_price = latest["close"]
        
        features = {
            "return": float(latest["return"]),
            "ma5": float(latest["ma5"]),
            "ma10": float(latest["ma10"]),
            "volatility": float(latest["volatility"]),
            "current_price": float(current_price)
        }
        
        return features
        
    except Exception as e:
        print(f"Error calculating features: {str(e)}")
        return None

def get_stock_features(symbol: str, api_key: str = API_KEY) -> Optional[Dict]:
    """
    Fetch stock data and calculate features for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        api_key: Alpha Vantage API key
    
    Returns:
        Dictionary with symbol and features, or None if error
    """
    df = fetch_stock_data(symbol, api_key)
    if df is None:
        return None
    
    features = calculate_features(df)
    if features is None:
        return None
    
    features["symbol"] = symbol
    return features

def get_multiple_stocks_features(symbols: List[str], api_key: str = API_KEY, delay: float = 12.0) -> List[Dict]:
    """
    Fetch features for multiple stocks with rate limiting.
    
    Args:
        symbols: List of stock ticker symbols
        api_key: Alpha Vantage API key
        delay: Delay between API calls (seconds) to avoid rate limits.
               Default 12 seconds for free tier (5 calls/minute limit)
    
    Returns:
        List of dictionaries with stock features
    """
    results = []
    failed = []
    
    total = len(symbols)
    for idx, symbol in enumerate(symbols, 1):
        print(f"[{idx}/{total}] Fetching {symbol}...")
        stock_data = get_stock_features(symbol, api_key)
        if stock_data:
            results.append(stock_data)
            print(f"  [OK] Successfully fetched {symbol}")
        else:
            failed.append(symbol)
            print(f"  [FAIL] Failed to fetch {symbol}")
        
        # Rate limiting to avoid API throttling (12 seconds = 5 calls/minute for free tier)
        # Only sleep if not the last item
        if idx < total:
            print(f"  Waiting {delay} seconds before next request (API rate limit)...")
            time.sleep(delay)
    
    print(f"\nSummary: {len(results)}/{total} stocks successfully fetched")
    if failed:
        print(f"Failed stocks: {', '.join(failed)}")
    
    return results

