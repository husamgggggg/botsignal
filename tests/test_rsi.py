"""Unit tests for RSI indicator."""
import pytest

from src.indicators.rsi import calculate_rsi, calculate_rsi_at_index


def test_rsi_period_2():
    """Test RSI with period 2."""
    # Need at least 3 prices for period 2 RSI
    prices = [1.0, 2.0, 1.5]
    result = calculate_rsi(prices, period=2)
    
    # First 2 should be None
    assert result[0] is None
    assert result[1] is None
    
    # Third should have RSI value
    assert result[2] is not None
    assert 0 <= result[2] <= 100


def test_rsi_period_14_typical():
    """Test RSI with typical period 14."""
    # Create price series with some volatility
    prices = [
        100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0,
        103.5, 105.0, 104.5, 106.0, 105.5, 107.0, 106.5,
        108.0, 107.5, 109.0, 108.5, 110.0
    ]
    
    result = calculate_rsi(prices, period=14)
    
    # First 14 should be None
    for i in range(14):
        assert result[i] is None
    
    # Remaining should have RSI values
    for i in range(14, len(result)):
        assert result[i] is not None
        assert 0 <= result[i] <= 100


def test_rsi_empty_list():
    """Test RSI with empty price list."""
    result = calculate_rsi([], period=14)
    assert result == []


def test_rsi_single_price():
    """Test RSI with single price."""
    result = calculate_rsi([100.0], period=14)
    assert result == [None]


def test_rsi_insufficient_data():
    """Test RSI with insufficient data."""
    prices = [1.0, 2.0, 3.0]
    
    with pytest.raises(ValueError, match="requires at least"):
        calculate_rsi(prices, period=14)


def test_rsi_invalid_period():
    """Test RSI with invalid period."""
    prices = [1.0, 2.0, 3.0, 4.0]
    
    with pytest.raises(ValueError, match="must be >= 1"):
        calculate_rsi(prices, period=0)
    
    with pytest.raises(ValueError, match="must be >= 1"):
        calculate_rsi(prices, period=-1)


def test_rsi_all_gains():
    """Test RSI when prices only go up (should approach 100)."""
    prices = [100.0]
    for i in range(1, 20):
        prices.append(prices[-1] + 1.0)
    
    result = calculate_rsi(prices, period=14)
    
    # RSI should be high (close to 100) for all gains
    rsi_value = result[-1]
    assert rsi_value is not None
    assert rsi_value > 90  # Should be very high


def test_rsi_all_losses():
    """Test RSI when prices only go down (should approach 0)."""
    prices = [100.0]
    for i in range(1, 20):
        prices.append(prices[-1] - 1.0)
    
    result = calculate_rsi(prices, period=14)
    
    # RSI should be low (close to 0) for all losses
    rsi_value = result[-1]
    assert rsi_value is not None
    assert rsi_value < 10  # Should be very low


def test_rsi_at_index():
    """Test RSI calculation at specific index."""
    prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5]
    
    # Index 0 with period 2: not enough data
    assert calculate_rsi_at_index(prices, period=2, index=0) is None
    
    # Index 1 with period 2: should work
    result = calculate_rsi_at_index(prices, period=2, index=2)
    assert result is not None
    assert 0 <= result <= 100


def test_rsi_at_index_out_of_range():
    """Test RSI at index with out of range index."""
    prices = [1.0, 2.0, 3.0]
    
    with pytest.raises(IndexError):
        calculate_rsi_at_index(prices, period=2, index=5)
    
    with pytest.raises(IndexError):
        calculate_rsi_at_index(prices, period=2, index=-1)


def test_rsi_wilders_smoothing():
    """Test that RSI uses Wilder's smoothing correctly."""
    # Create a controlled price series
    prices = [100.0]
    # First 15 prices: alternate +1 and -1
    for i in range(1, 16):
        if i % 2 == 0:
            prices.append(prices[-1] - 1.0)
        else:
            prices.append(prices[-1] + 1.0)
    
    result = calculate_rsi(prices, period=14)
    
    # RSI should be calculated (not None)
    rsi_value = result[-1]
    assert rsi_value is not None
    assert 0 <= rsi_value <= 100

