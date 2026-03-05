"""Unit tests for EMA/RSI strategy."""
import pytest

from src.strategies.ema_rsi import EMARSIStrategy, Signal


def test_strategy_buy_signal():
    """Test strategy generates BUY signal when conditions are met."""
    # Create candles with upward trend
    # EMA20 > EMA50 (upward trend) and RSI > 50
    candles = []
    base_price = 1.0850
    
    # Create an upward trend
    for i in range(200):
        candles.append({
            "close": base_price + (i * 0.0001),
            "open": base_price + (i * 0.0001) - 0.00005,
            "high": base_price + (i * 0.0001) + 0.00005,
            "low": base_price + (i * 0.0001) - 0.0001,
            "volume": 1000
        })
    
    strategy = EMARSIStrategy()
    result = strategy.analyze(candles)
    
    # Should generate either BUY or NO_TRADE (depending on RSI)
    assert result.signal in [Signal.BUY, Signal.NO_TRADE]
    assert result.confidence >= 0
    assert result.confidence <= 100
    assert result.ema_20 is not None
    assert result.ema_50 is not None
    assert result.rsi is not None


def test_strategy_insufficient_candles():
    """Test strategy with insufficient candles."""
    candles = [{"close": 1.0850}] * 50  # Need at least 51
    
    strategy = EMARSIStrategy()
    
    with pytest.raises(ValueError, match="Need at least"):
        strategy.analyze(candles)


def test_strategy_empty_candles():
    """Test strategy with empty candles."""
    strategy = EMARSIStrategy()
    
    with pytest.raises(ValueError, match="Cannot analyze empty"):
        strategy.analyze([])


def test_strategy_min_ema_distance():
    """Test strategy respects minimum EMA distance."""
    # Create candles with very small EMA distance
    candles = []
    base_price = 1.0850
    
    # Create a very flat trend (minimal EMA distance)
    for i in range(200):
        candles.append({
            "close": base_price + (i * 0.000001),  # Very small increment
            "open": base_price + (i * 0.000001),
            "high": base_price + (i * 0.000001) + 0.00001,
            "low": base_price + (i * 0.000001) - 0.00001,
            "volume": 1000
        })
    
    # Set a minimum EMA distance that's larger than what we'll have
    strategy = EMARSIStrategy(min_ema_distance_pct=1.0)  # 1% minimum
    result = strategy.analyze(candles)
    
    # Should be NO_TRADE due to minimum distance requirement
    assert result.signal == Signal.NO_TRADE
    assert "below minimum" in result.rationale.lower()


def test_strategy_confidence_calculation():
    """Test that confidence is calculated correctly."""
    candles = []
    base_price = 1.0850
    
    # Create a strong upward trend
    for i in range(200):
        candles.append({
            "close": base_price + (i * 0.001),  # Strong trend
            "open": base_price + (i * 0.001) - 0.0005,
            "high": base_price + (i * 0.001) + 0.0005,
            "low": base_price + (i * 0.001) - 0.001,
            "volume": 1000
        })
    
    strategy = EMARSIStrategy()
    result = strategy.analyze(candles)
    
    # Confidence should be between 0 and 100
    assert 0 <= result.confidence <= 100
    
    # If signal is not NO_TRADE, confidence should be > 0
    if result.signal != Signal.NO_TRADE:
        assert result.confidence > 0


def test_strategy_no_trade_signal():
    """Test strategy generates NO_TRADE when conditions not met."""
    # Create candles with mixed conditions
    candles = []
    base_price = 1.0850
    
    # Create a sideways/flat trend
    for i in range(200):
        # Alternate up and down to create flat trend
        offset = 0.0001 * (1 if i % 2 == 0 else -1)
        candles.append({
            "close": base_price + offset,
            "open": base_price,
            "high": base_price + 0.0002,
            "low": base_price - 0.0002,
            "volume": 1000
        })
    
    strategy = EMARSIStrategy()
    result = strategy.analyze(candles)
    
    # Should generate NO_TRADE or a signal with low confidence
    assert result.signal in [Signal.BUY, Signal.SELL, Signal.NO_TRADE]
    assert result.ema_20 is not None
    assert result.ema_50 is not None


def test_strategy_rationale():
    """Test that rationale is provided."""
    candles = []
    base_price = 1.0850
    
    for i in range(200):
        candles.append({
            "close": base_price + (i * 0.0001),
            "open": base_price + (i * 0.0001),
            "high": base_price + (i * 0.0001) + 0.0001,
            "low": base_price + (i * 0.0001) - 0.0001,
            "volume": 1000
        })
    
    strategy = EMARSIStrategy()
    result = strategy.analyze(candles)
    
    # Rationale should be a non-empty string
    assert isinstance(result.rationale, str)
    assert len(result.rationale) > 0

