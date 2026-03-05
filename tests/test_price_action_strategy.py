"""Unit tests for Price Action + Support/Resistance Strategy."""
import pytest

from src.strategies.price_action_sr import PriceActionSRStrategy, Signal


def test_strategy_insufficient_candles():
    """Test strategy with insufficient candles."""
    candles = [{"open": 1.0850, "close": 1.0855, "high": 1.0860, "low": 1.0845}] * 10
    
    strategy = PriceActionSRStrategy(lookback=20)
    
    with pytest.raises(ValueError, match="Need at least"):
        strategy.analyze(candles)


def test_strategy_empty_candles():
    """Test strategy with empty candles."""
    strategy = PriceActionSRStrategy()
    
    with pytest.raises(ValueError, match="Cannot analyze empty"):
        strategy.analyze([])


def test_strategy_basic():
    """Test strategy basic functionality."""
    strategy = PriceActionSRStrategy(lookback=20)
    
    candles = []
    base_price = 1.0850
    
    # Create enough candles with some structure
    for i in range(30):
        # Create some support/resistance levels
        if i % 10 == 0:
            price = base_price - 0.001  # Support level
        elif i % 10 == 5:
            price = base_price + 0.001  # Resistance level
        else:
            price = base_price
        
        candles.append({
            "open": price,
            "close": price + 0.0001,
            "high": price + 0.0002,
            "low": price - 0.0001,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    # Should return a result
    assert result is not None
    assert result.signal in [Signal.BUY, Signal.SELL, Signal.NO_TRADE, Signal.POTENTIAL_BUY, Signal.POTENTIAL_SELL]
    assert 0 <= result.confidence <= 100


def test_strategy_rationale():
    """Test that rationale is provided."""
    strategy = PriceActionSRStrategy()
    
    candles = []
    base_price = 1.0850
    
    for i in range(30):
        candles.append({
            "open": base_price,
            "close": base_price + 0.0001,
            "high": base_price + 0.0002,
            "low": base_price - 0.0001,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    assert isinstance(result.rationale, str)
    assert len(result.rationale) > 0

