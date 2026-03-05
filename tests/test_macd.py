"""Unit tests for MACD indicator."""
import pytest

from src.indicators.macd import calculate_macd, calculate_macd_at_index


def test_macd_basic():
    """Test basic MACD calculation."""
    prices = [1.0850 + (i * 0.0001) for i in range(50)]
    
    macd_line, signal_line, histogram = calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9)
    
    assert len(macd_line) == len(prices)
    assert len(signal_line) == len(prices)
    assert len(histogram) == len(prices)
    
    # Last values should not be None (we have enough data)
    assert macd_line[-1] is not None
    assert signal_line[-1] is not None
    assert histogram[-1] is not None


def test_macd_insufficient_data():
    """Test MACD with insufficient data."""
    prices = [1.0850] * 10
    
    macd_line, signal_line, histogram = calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9)
    
    # Should return None values for insufficient data
    assert all(v is None for v in macd_line)
    assert all(v is None for v in signal_line)
    assert all(v is None for v in histogram)


def test_macd_empty_list():
    """Test MACD with empty price list."""
    macd_line, signal_line, histogram = calculate_macd([])
    
    assert macd_line == []
    assert signal_line == []
    assert histogram == []


def test_macd_invalid_periods():
    """Test MACD with invalid periods."""
    prices = [1.0850] * 50
    
    with pytest.raises(ValueError, match="must be less than"):
        calculate_macd(prices, fast_period=26, slow_period=12)
    
    with pytest.raises(ValueError, match="must be >= 1"):
        calculate_macd(prices, fast_period=0)


def test_macd_at_index():
    """Test MACD calculation at specific index."""
    prices = [1.0850 + (i * 0.0001) for i in range(50)]
    
    # Index with enough data
    macd, signal, hist = calculate_macd_at_index(prices, 12, 26, 9, 40)
    
    assert macd is not None
    assert signal is not None
    assert hist is not None
    
    # Index with insufficient data
    macd2, signal2, hist2 = calculate_macd_at_index(prices, 12, 26, 9, 10)
    assert macd2 is None or signal2 is None or hist2 is None


def test_macd_at_index_out_of_range():
    """Test MACD at index with out of range index."""
    prices = [1.0850] * 50
    
    with pytest.raises(IndexError):
        calculate_macd_at_index(prices, 12, 26, 9, 100)
    
    with pytest.raises(IndexError):
        calculate_macd_at_index(prices, 12, 26, 9, -1)

