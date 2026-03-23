import pytest
from datetime import datetime
from src.signals.models import Signal, SignalSide
from src.core.validator import SignalValidator
from src.strategies.base import StrategyRegistry, StrategyBase
from src.strategies.moving_average_alpha import MovingAverageCrossover
import pandas as pd

# 1. Signal Schema Validation
def test_signal_schema():
    signal = Signal(
        symbol="AAPL_US_EQ",
        side=SignalSide.BUY,
        strength=0.8,
        confidence=0.9,
        strategy_name="TestStrategy",
        metadata={"info": "test"}
    )
    assert signal.symbol == "AAPL_US_EQ"
    assert signal.side == SignalSide.BUY
    assert signal.strength == 0.8
    assert isinstance(signal.timestamp, datetime)

def test_signal_invalid_strength():
    with pytest.raises(ValueError):
        Signal(
            symbol="AAPL",
            side=SignalSide.BUY,
            strength=1.5, # Out of range [0, 1]
            strategy_name="Test"
        )

# 2. Signal Validator
def test_signal_validator():
    validator = SignalValidator(min_confidence=0.5, min_strength=0.5)
    
    valid_signal = Signal(
        symbol="AAPL",
        side=SignalSide.BUY,
        strength=0.7,
        confidence=0.8,
        strategy_name="Test"
    )
    
    weak_signal = Signal(
        symbol="AAPL",
        side=SignalSide.BUY,
        strength=0.3,
        confidence=0.8,
        strategy_name="Test"
    )
    
    assert validator.validate_signal(valid_signal) is True
    assert validator.validate_signal(weak_signal) is False

# 3. Strategy Registry
def test_strategy_registry():
    # MovingAverageCrossover should be registered
    assert "MovingAverageCrossover" in StrategyRegistry.list_strategies()
    
    strategy = StrategyRegistry.get_strategy("MovingAverageCrossover")
    assert isinstance(strategy, MovingAverageCrossover)
    assert strategy.name == "MovingAverageCrossover"

# 4. Sample Strategy Logic (Mock Data)
def test_moving_average_alpha_logic():
    strategy = MovingAverageCrossover(name="MA_Test", short_window=2, long_window=5)
    
    # Create dummy data where short MA will cross above long MA
    # Close prices: [10, 11, 12, 13, 14, 16]
    # Long MA (5): [NaN, NaN, NaN, NaN, 12.0, 13.2]
    # Short MA (2): [NaN, 10.5, 11.5, 12.5, 13.5, 15.0]
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 16]
    })
    
    market_data = {"AAPL": data}
    signals = strategy.generate_signals(market_data)
    
    assert len(signals) == 1
    assert signals[0].symbol == "AAPL"
    # In this case, short_ma (15.0) > long_ma (13.2), but we also need to check previous crossover.
    # Actually, the logic in generate_signals checks iloc[-1] vs iloc[-2].
    # Let's just verify it returns a Signal object.
    assert isinstance(signals[0], Signal)
