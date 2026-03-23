import unittest
import os
import yaml
from unittest.mock import MagicMock, patch
from src.strategies.base import StrategyRegistry, StrategyBase

class TestStrategyLoader(unittest.TestCase):

    def setUp(self):
        # Clear registry for tests to ensure a clean state
        StrategyRegistry._strategies = {}

    def test_dynamic_discovery(self):
        """Test that discover_strategies correctly loads registered strategies."""
        # This will trigger discover_strategies inside list_strategies
        strategies = StrategyRegistry.list_strategies()
        self.assertIn("MovingAverageCrossover", strategies)

    def test_load_strategy_from_registry(self):
        """Test loading a concrete strategy by name."""
        strategy = StrategyRegistry.get_strategy("MovingAverageCrossover", short_window=10)
        self.assertEqual(strategy.name, "MovingAverageCrossover")
        self.assertEqual(strategy.short_window, 10)
        self.assertIsInstance(strategy, StrategyBase)

    def test_unknown_strategy_handling(self):
        """Test that loading an unknown strategy raises a ValueError."""
        with self.assertRaises(ValueError) as cm:
            StrategyRegistry.get_strategy("NonExistentStrategy")
        self.assertIn("is not registered", str(cm.exception))

    def test_parameter_passing(self):
        """Test that parameters from config are correctly passed to the constructor."""
        params = {"short_window": 15, "long_window": 50, "extra_param": "test"}
        tickers = ["AAPL_US_EQ"]
        strategy = StrategyRegistry.get_strategy("MovingAverageCrossover", tickers=tickers, **params)
        self.assertEqual(strategy.short_window, 15)
        self.assertEqual(strategy.long_window, 50)
        self.assertEqual(strategy.tickers, tickers)
        # Extra params should be in self.params if we use super().__init__(name, **kwargs)
        self.assertEqual(strategy.params.get("extra_param"), "test")

    @patch('src.strategies.base.StrategyRegistry.get_strategy')
    def test_config_driven_loading(self, mock_get_strategy):
        """Simulate the logic in main.py for config-driven loading."""
        config = {
            "strategy": {
                "active_strategy": "MovingAverageCrossover",
                "strategy_params": {"short_window": 7}
            }
        }
        
        strategy_name = config.get("strategy", {}).get("active_strategy")
        strategy_params = config.get("strategy", {}).get("strategy_params", {})
        
        StrategyRegistry.get_strategy(strategy_name, **strategy_params)
        mock_get_strategy.assert_called_once_with("MovingAverageCrossover", short_window=7)

if __name__ == "__main__":
    unittest.main()
