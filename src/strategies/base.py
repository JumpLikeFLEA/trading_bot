from abc import ABC, abstractmethod
from typing import List, Dict, Type
import pandas as pd
from src.signals.models import Signal

class StrategyBase(ABC):
    """
    Abstract Base Class for Alphas (Trading Strategies).
    Alphas should NOT call the Trading 212 API directly.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, market_data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Produce a list of standardized signals based on market data.
        
        Args:
            market_data: Dictionary mapping ticker symbols to their historical/real-time DataFrames.
            
        Returns:
            List[Signal]: A list of validated signal objects.
        """
        pass

    @abstractmethod
    def get_tickers(self) -> List[str]:
        """
        Returns the list of tickers this strategy is interested in.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"

class StrategyRegistry:
    """
    A simple registry to manage and load strategies by name.
    """
    _strategies: Dict[str, Type[StrategyBase]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a strategy class."""
        def decorator(strategy_cls: Type[StrategyBase]):
            cls._strategies[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> StrategyBase:
        """Instantiate and return a registered strategy."""
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' is not registered.")
        return cls._strategies[name](name=name, **kwargs)

    @classmethod
    def list_strategies(cls) -> List[str]:
        """Return the names of all registered strategies."""
        return list(cls._strategies.keys())
