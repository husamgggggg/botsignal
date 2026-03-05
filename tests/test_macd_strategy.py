"""Unit tests for MACD Crossover Strategy."""
import pytest

from src.strategies.macd_crossover import MACDCrossoverStrategy, Signal


def test_strategy_insufficient_candles():
    """Test strategy with insufficient candles."""
    candles = [{"open": 1.0850, "close": 1.0855, "high": 1.0860, "low": 1.0845}] * 30
    
    strategy = MACDCrossoverStrategy()
    
    with pytest.raises(ValueError, match="Need at least"):
        strategy.analyze(candles)


def test_strategy_empty_candles():
    """Test strategy with empty candles."""
    strategy = MACDCrossoverStrategy()
    
    with pytest.raises(ValueError, match="Cannot analyze empty"):
        strategy.analyze([])


def test_strategy_no_trade():
    """Test strategy when no signal conditions are met."""
    strategy = MACDCrossoverStrategy()
    
    candles = []
    base_price = 1.0850
    
    # Create enough candles
    for i in range(50):
        candles.append({
            "open": base_price,
            "close": base_price,  # Flat candles (no direction)
            "high": base_price + 0.0001,
            "low": base_price - 0.0001,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    # Should be NO_TRADE
    assert result.signal == Signal.NO_TRADE
    assert result.confidence >= 0
    assert result.confidence <= 100


def test_strategy_rationale():
    """Test that rationale is provided."""
    strategy = MACDCrossoverStrategy()
    
    candles = []
    base_price = 1.0850
    
    for i in range(50):
        candles.append({
            "open": base_price,
            "close": base_price,
            "high": base_price + 0.0001,
            "low": base_price - 0.0001,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    assert isinstance(result.rationale, str)
    assert len(result.rationale) > 0


def test_strategy_confidence_range():
    """Test that confidence is within valid range."""
    strategy = MACDCrossoverStrategy()
    
    candles = []
    base_price = 1.0850
    
    for i in range(50):
        candles.append({
            "open": base_price + (i * 0.0001),
            "close": base_price + (i * 0.0001) + 0.00005,
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.00005,
            "volume": 1000
        })
    
    result = strategy.analyze(candles)
    
    # Confidence should be between 0 and 100
    assert 0 <= result.confidence <= 100

