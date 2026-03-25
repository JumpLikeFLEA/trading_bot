import os
import importlib
import pkgutil
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Any
import pandas as pd
from src.signals.models import Signal

class StrategyBase(ABC):
    """
    Abstract Base Class for Alphas (Trading Strategies).
    Alphas should NOT call the Trading 212 API directly.
    """
    def __init__(self, name: str, tickers: List[str] = None, **kwargs):
        self.name = name
        self.tickers = tickers or []
        self.params = kwargs

    @abstractmethod
    def generate_signals(self, market_data: Dict[str, pd.DataFrame], fundamental_data: pd.DataFrame = None) -> List[Signal]:
        """
        Produce a list of standardized signals based on market data and optional fundamentals.
        
        Args:
            market_data: Dictionary mapping ticker symbols to their historical/real-time DataFrames.
            fundamental_data: Optional DataFrame with fundamental metrics for the tickers.
            
        Returns:
            List[Signal]: A list of validated signal objects.
        """
        pass

    def get_tickers(self) -> List[str]:
        """
        Returns the list of tickers this strategy is interested in.
        """
        return self.tickers

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
        # Ensure strategies are discovered/loaded if not already
        if not cls._strategies:
            cls.discover_strategies()

        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' is not registered. Available: {cls.list_strategies()}")
        
        return cls._strategies[name](name=name, **kwargs)

    @classmethod
    def list_strategies(cls) -> List[str]:
        """Return the names of all registered strategies."""
        if not cls._strategies:
            cls.discover_strategies()
        return list(cls._strategies.keys())

    @classmethod
    def discover_strategies(cls):
        """
        Dynamically discover and import all modules in the strategies package
        to trigger registration.
        """
        import sys
        package_dir = os.path.dirname(__file__)
        for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
            if module_name != "base" and not is_pkg:
                full_module_name = f"src.strategies.{module_name}"
                if full_module_name in sys.modules:
                    importlib.reload(sys.modules[full_module_name])
                else:
                    importlib.import_module(full_module_name)
