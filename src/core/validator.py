import logging
from typing import List, Optional
from src.signals.models import Signal, SignalSide

# --- Logging Setup ---
logger = logging.getLogger("trading_bot.core.validator")

class SignalValidator:
    """
    Validation layer to check signals before they are sent to execution.
    """
    def __init__(self, min_confidence: float = 0.5, min_strength: float = 0.5):
        self.min_confidence = min_confidence
        self.min_strength = min_strength

    def validate_signal(self, signal: Signal) -> bool:
        """
        Perform a set of checks to ensure the signal is well-formed and meets quality thresholds.
        
        Args:
            signal: The Signal object to validate.
            
        Returns:
            bool: True if the signal is valid, False otherwise.
        """
        # 1. Basic confidence and strength checks
        if signal.confidence < self.min_confidence:
            logger.warning(f"Signal rejected: Confidence {signal.confidence} is below threshold {self.min_confidence}")
            return False
        
        if signal.strength < self.min_strength:
            logger.warning(f"Signal rejected: Strength {signal.strength} is below threshold {self.min_strength}")
            return False

        # 2. Check for missing symbols
        if not signal.symbol:
            logger.error("Signal rejected: Missing symbol.")
            return False

        # 3. Check for valid side
        if signal.side not in SignalSide.__members__.values():
            logger.error(f"Signal rejected: Invalid side '{signal.side}'.")
            return False

        # 4. Check for timestamp sanity (e.g., not too old)
        # (Placeholder for more complex logic if needed)

        logger.info(f"Signal validated for {signal.symbol}: {signal.side}")
        return True

    def validate_signals(self, signals: List[Signal]) -> List[Signal]:
        """
        Validate a list of signals and return only the valid ones.
        """
        return [s for s in signals if self.validate_signal(s)]
