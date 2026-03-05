"""Unit tests for EMA indicator."""
import pytest

from src.indicators.ema import calculate_ema, calculate_ema_at_index


def test_ema_period_1():
    """Test EMA with period 1."""
    prices = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = calculate_ema(prices, period=1)
    
    # EMA with period 1 should equal the prices
    assert len(result) == len(prices)
    assert result[0] == 1.0
    assert result[-1] == 5.0


def test_ema_period_2():
    """Test EMA with period 2."""
    prices = [1.0, 2.0]
    result = calculate_ema(prices, period=2)
    
    # First value should be None, second should be SMA of first 2
    assert result[0] is None
    assert result[1] == 1.5  # (1.0 + 2.0) / 2


def test_ema_period_3():
    """Test EMA with period 3."""
    prices = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = calculate_ema(prices, period=3)
    
    # First 2 should be None
    assert result[0] is None
    assert result[1] is None
    
    # Third should be SMA of first 3
    assert result[2] == 2.0  # (1.0 + 2.0 + 3.0) / 3
    
    # Fourth: EMA = price * k + prev_ema * (1-k), k = 2/(3+1) = 0.5
    # EMA(4) = 4.0 * 0.5 + 2.0 * 0.5 = 3.0
    assert abs(result[3] - 3.0) < 0.0001
    
    # Fifth: EMA(5) = 5.0 * 0.5 + 3.0 * 0.5 = 4.0
    assert abs(result[4] - 4.0) < 0.0001


def test_ema_empty_list():
    """Test EMA with empty price list."""
    result = calculate_ema([], period=5)
    assert result == []


def test_ema_insufficient_data():
    """Test EMA with insufficient data."""
    prices = [1.0, 2.0, 3.0]
    
    with pytest.raises(ValueError, match="cannot be greater than"):
        calculate_ema(prices, period=5)


def test_ema_invalid_period():
    """Test EMA with invalid period."""
    prices = [1.0, 2.0, 3.0]
    
    with pytest.raises(ValueError, match="must be >= 1"):
        calculate_ema(prices, period=0)
    
    with pytest.raises(ValueError, match="must be >= 1"):
        calculate_ema(prices, period=-1)


def test_ema_realistic_data():
    """Test EMA with realistic price data."""
    prices = [
        1.0850, 1.0855, 1.0860, 1.0858, 1.0862,
        1.0865, 1.0870, 1.0868, 1.0872, 1.0875,
        1.0880, 1.0885, 1.0890, 1.0888, 1.0892,
        1.0895, 1.0900, 1.0905, 1.0910, 1.0915,
        1.0920, 1.0925, 1.0930, 1.0935, 1.0940
    ]
    
    result = calculate_ema(prices, period=20)
    
    # Should have 19 None values, then EMA values
    assert result[18] is None
    assert result[19] is not None
    assert result[24] is not None
    
    # EMA should be increasing for this upward trend
    assert result[19] < result[24]


def test_ema_at_index():
    """Test EMA calculation at specific index."""
    prices = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Index 0 with period 3: not enough data
    assert calculate_ema_at_index(prices, period=3, index=0) is None
    
    # Index 2 with period 3: should work
    result = calculate_ema_at_index(prices, period=3, index=2)
    assert result == 2.0  # SMA of first 3
    
    # Index 3 with period 3: should work
    result = calculate_ema_at_index(prices, period=3, index=3)
    assert abs(result - 3.0) < 0.0001


def test_ema_at_index_out_of_range():
    """Test EMA at index with out of range index."""
    prices = [1.0, 2.0, 3.0]
    
    with pytest.raises(IndexError):
        calculate_ema_at_index(prices, period=2, index=5)
    
    with pytest.raises(IndexError):
        calculate_ema_at_index(prices, period=2, index=-1)

