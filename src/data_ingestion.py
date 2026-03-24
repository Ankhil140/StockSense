import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker, period="2y", interval="1d"):
    """
    Fetch historical stock data from Yahoo Finance.
    Interval can be '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
    """
    print(f"Fetching data for {ticker} (Period: {period}, Interval: {interval})...")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    
    if df.empty:
        # Fallback for intraday if requested period is too long
        if interval in ['1m', '5m', '15m']:
             print(f"Warning: Intraday data for {ticker} might not be available for period {period}. Retrying with period '7d'...")
             df = stock.history(period="7d", interval=interval)
             
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    
    # Save to data directory
    os.makedirs("data", exist_ok=True)
    filename = f"data/{ticker}_{interval}.csv"
    df.to_csv(filename)
    print(f"Data saved to {filename}")
    return df

if __name__ == "__main__":
    fetch_stock_data("AAPL")
