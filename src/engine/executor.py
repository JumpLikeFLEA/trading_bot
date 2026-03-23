import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from src.api.t212_client import T212Client, OrderType

# --- Logging Setup ---
logger = logging.getLogger("trading_bot.engine")
logger.setLevel(logging.INFO)

class Executor:
    """
    The logic that bridges Alpha signals to the Trading 212 API.
    Handles order sizing and conversion from ticker to T212 internal representation.
    """
    
    def __init__(self, client: T212Client, risk_limits: Optional[Dict[str, Any]] = None):
        """
        Initialize the executor.
        
        Args:
            client: An instance of T212Client.
            risk_limits: Dictionary containing risk parameters (e.g., max position size).
        """
        self.client = client
        self.risk_limits = risk_limits or {"max_position_size": 1000.0}
        self._instrument_map = {} # Internal cache for instrument data

    def refresh_instrument_cache(self):
        """
        Fetches all instruments from T212 and populates the internal cache.
        This is crucial for ticker-to-ISIN mapping or validating ticker existence.
        """
        try:
            instruments = self.client.get_instruments()
            self._instrument_map = {i.ticker: i for i in instruments}
            logger.info(f"Successfully refreshed instrument cache. Total instruments: {len(self._instrument_map)}")
        except Exception as e:
            logger.error(f"Failed to refresh instrument cache: {e}")

    def calculate_order_quantity(self, ticker: str, signal_weight: float) -> float:
        """
        Calculate the quantity to order based on signal weight and account cash.
        
        Args:
            ticker: The ticker symbol.
            signal_weight: The target weight (e.g., 0.1 for 10% of portfolio).
            
        Returns:
            float: The calculated quantity (positive for buy, negative for sell).
        """
        # Placeholder for more complex sizing logic.
        # In a production environment, this would involve fetching current price,
        # checking existing position, and applying risk limits.
        
        try:
            account = self.client.get_account_cash()
            target_value = account.total * signal_weight
            
            # Mock pricing for this shell - in reality, fetch current price from data provider
            # For now, we'll assume a dummy price of 100.0
            current_price = 100.0 
            
            quantity = target_value / current_price
            
            # Apply risk limits
            max_size = self.risk_limits.get("max_position_size", 1000.0)
            if abs(quantity * current_price) > max_size:
                logger.warning(f"Order size for {ticker} exceeds risk limit. Capping.")
                quantity = (max_size / current_price) * (1 if quantity > 0 else -1)
                
            return quantity
        except Exception as e:
            logger.error(f"Error calculating quantity for {ticker}: {e}")
            return 0.0

    def execute_signals(self, signals_df: pd.DataFrame):
        """
        Process a DataFrame of signals and execute trades.
        
        Args:
            signals_df: DataFrame with at least 'ticker' and 'signal_weight' columns.
        """
        if not self._instrument_map:
            self.refresh_instrument_cache()

        for _, row in signals_df.iterrows():
            ticker = row['ticker']
            weight = row['signal_weight']
            
            if ticker not in self._instrument_map:
                logger.error(f"Ticker {ticker} not found in T212 instrument list. Skipping.")
                continue

            quantity = self.calculate_order_quantity(ticker, weight)
            
            if quantity != 0:
                try:
                    logger.info(f"Executing trade for {ticker}: Weight={weight}, Calculated Quantity={quantity}")
                    self.client.place_order(ticker, quantity)
                except Exception as e:
                    logger.error(f"Execution failed for {ticker}: {e}")

    def get_t212_id(self, ticker: str) -> Optional[str]:
        """
        Convert a ticker symbol to its T212 ISIN or internal ID.
        """
        instrument = self._instrument_map.get(ticker)
        return instrument.isin if instrument else None
