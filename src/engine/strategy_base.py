from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class StrategyBase(ABC):
    """
    Abstract Base Class (ABC) for 'Alphas'.
    Defines the standard interface for strategy implementation.
    """
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on provided historical data.
        Should return a DataFrame with signals (e.g., 'buy', 'sell', 'hold' or quantity weights).
        
        Args:
            data: DataFrame containing historical price/candle data.
            
        Returns:
            pd.DataFrame: DataFrame containing generated signals.
        """
        pass

    @abstractmethod
    def get_tickers(self) -> List[str]:
        """
        Return a list of tickers this strategy is interested in.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
