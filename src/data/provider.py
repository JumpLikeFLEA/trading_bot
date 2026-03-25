import logging
import pandas as pd
import yfinance as yf
from typing import List, Optional, Dict, Any
import datetime

# --- Logging Setup ---
logger = logging.getLogger("trading_bot.data")
logger.setLevel(logging.INFO)

class DataProvider:
    """
    Module for data ingestion and management.
    Handles candle fetching and price retrieval from both internal and external sources.
    """
    
    def __init__(self, external_api_key: Optional[str] = None):
        """
        Initialize the DataProvider.
        
        Args:
            external_api_key: Optional API key for external data sources (e.g., Alpha Vantage).
        """
        self.external_api_key = external_api_key

    def fetch_historical_candles(self, ticker: str, interval: str = "1h", limit: int = 100) -> pd.DataFrame:
        """
        Fetch historical candle data for a ticker using yfinance.
        
        Args:
            ticker: Ticker symbol (e.g., "AAPL").
            interval: Time interval between candles (e.g., "1m", "5m", "1h", "1d").
            limit: Number of candles to fetch.
            
        Returns:
            pd.DataFrame: Candle data (timestamp, open, high, low, close, volume).
        """
        logger.info(f"Fetching historical candles for {ticker} at {interval} interval.")
        
        # Map T212 ticker format if necessary (e.g., AAPL_US_EQ -> AAPL)
        clean_ticker = ticker.split('_')[0]
        
        # Calculate period based on limit and interval to ensure we get enough data
        # This is a simplification; yfinance uses 'period' or 'start'/'end'
        period_map = {"1m": "1d", "5m": "5d", "1h": "1mo", "1d": "1y"}
        period = period_map.get(interval, "1mo")

        try:
            df = yf.download(clean_ticker, interval=interval, period=period, progress=False)
            if df.empty:
                logger.warning(f"No data found for {clean_ticker}")
                return pd.DataFrame()
            
            # Clean up column names (yfinance returns MultiIndex if multiple tickers)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df.columns = [col.lower() for col in df.columns]
            
            # Limit to the requested number of rows
            return df.tail(limit)
        except Exception as e:
            logger.error(f"Failed to fetch data from yfinance for {clean_ticker}: {e}")
            return pd.DataFrame()

    def get_fundamentals(self, tickers: List[str]) -> pd.DataFrame:
        """
        Retrieve fundamental data for a list of tickers.
        Required for Value Alpha strategy.
        
        Args:
            tickers: List of ticker symbols.
            
        Returns:
            pd.DataFrame: Fundamental metrics indexed by ticker.
        """
        logger.info(f"Fetching fundamental data for {len(tickers)} tickers.")
        fundamentals_data = []

        for ticker in tickers:
            clean_ticker = ticker.split('_')[0]
            try:
                stock = yf.Ticker(clean_ticker)
                info = stock.info
                
                fundamentals_data.append({
                    "ticker": ticker,
                    "marketCap": info.get("marketCap"),
                    "operatingCashflow": info.get("operatingCashflow"),
                    "enterpriseValue": info.get("enterpriseValue"),
                    "ebitda": info.get("ebitda")
                })
            except Exception as e:
                logger.error(f"Failed to fetch fundamentals for {clean_ticker}: {e}")
                fundamentals_data.append({
                    "ticker": ticker,
                    "marketCap": None,
                    "operatingCashflow": None,
                    "enterpriseValue": None,
                    "ebitda": None
                })

        df = pd.DataFrame(fundamentals_data)
        df.set_index("ticker", inplace=True)
        return df

    def get_realtime_price(self, ticker: str) -> float:
        """
        Fetch the current real-time price for a ticker.
        
        Args:
            ticker: Ticker symbol.
            
        Returns:
            float: Current price.
        """
        logger.info(f"Retrieving real-time price for {ticker}")
        
        # --- PLACEHOLDER: Integration with T212 or External API ---
        # Real logic would fetch from a WebSocket or REST endpoint
        return 152.50 # Mock price

    def ingest_external_dataset(self, source_name: str, config: Dict[str, Any]):
        """
        Placeholder method for ingesting larger datasets for offline analysis or training.
        
        Args:
            source_name: Name of the external data source (e.g., "YahooFinance").
            config: Configuration parameters for the ingestion process.
        """
        logger.info(f"Starting data ingestion from {source_name} with config: {config}")
        # Implementation for bulk data sync goes here
        pass
