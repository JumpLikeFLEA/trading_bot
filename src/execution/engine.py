import logging
from typing import Dict, Any, List, Optional
from src.api.t212_client import T212Client, OrderType
from src.signals.models import Signal, SignalSide

# --- Logging Setup ---
logger = logging.getLogger("trading_bot.execution.engine")

class ExecutionEngine:
    """
    Core execution logic that transforms signals into Trading 212 API orders.
    """
    def __init__(self, client: T212Client, risk_limits: Optional[Dict[str, Any]] = None):
        """
        Initialize the ExecutionEngine.
        
        Args:
            client: Instance of T212Client.
            risk_limits: Portfolio risk configuration.
        """
        self.client = client
        self.risk_limits = risk_limits or {"max_position_size": 1000.0}
        self._instrument_cache = {}

    def _refresh_instruments(self):
        """Cache instrument details for ticker validation and ID lookup."""
        if not self._instrument_cache:
            try:
                instruments = self.client.get_instruments()
                self._instrument_cache = {i.ticker: i for i in instruments}
                logger.info(f"Instrument cache refreshed: {len(self._instrument_cache)} symbols.")
            except Exception as e:
                logger.error(f"Failed to refresh instruments: {e}")

    def calculate_quantity(self, signal: Signal) -> float:
        """
        Determine the order quantity based on signal strength and account limits.
        
        Args:
            signal: The validated Signal object.
            
        Returns:
            float: Order quantity (positive for BUY, negative for SELL).
        """
        # --- PLACEHOLDER logic for quantity sizing ---
        # A more advanced version would use current account equity, 
        # position sizes, and risk-per-trade parameters.
        
        try:
            account = self.client.get_account_cash()
            # Simple rule: use 10% of total equity as the base per trade
            base_value = account.total * 0.1
            target_value = base_value * signal.strength
            
            # Dummy price for calculation (should be fetched from DataProvider)
            price = 100.0
            quantity = target_value / price
            
            # Cap by risk limits
            max_size = self.risk_limits.get("max_position_size", 1000.0)
            if abs(quantity * price) > max_size:
                quantity = (max_size / price)
                
            return quantity if signal.side == SignalSide.BUY else -quantity
        except Exception as e:
            logger.error(f"Quantity calculation failed for {signal.symbol}: {e}")
            return 0.0

    def process_signals(self, signals: List[Signal]):
        """
        Convert signals into orders and execute them on T212.
        
        Args:
            signals: A list of validated signals.
        """
        self._refresh_instruments()
        
        for signal in signals:
            if signal.side == SignalSide.HOLD:
                continue

            if signal.symbol not in self._instrument_cache:
                logger.warning(f"Symbol {signal.symbol} not available on T212. Skipping.")
                continue

            quantity = self.calculate_quantity(signal)
            if quantity == 0:
                continue

            try:
                logger.info(f"Placing order: {signal.symbol} | {signal.side} | Qty={quantity}")
                self.client.place_order(signal.symbol, quantity)
            except Exception as e:
                logger.error(f"Order placement failed for {signal.symbol}: {e}")
