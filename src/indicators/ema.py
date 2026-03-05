"""Exponential Moving Average (EMA) indicator implementation."""
from typing import List, Optional


def calculate_ema(prices: List[float], period: int) -> List[Optional[float]]:
    """Calculate Exponential Moving Average (EMA).
    
    Formula:
        EMA = Price(t) * k + EMA(y) * (1 - k)
        where k = 2 / (N + 1), N = period
    
    For the first value, use SMA as the initial EMA value.
    
    Args:
        prices: List of price values (typically close prices)
        period: EMA period (e.g., 20, 50)
        
    Returns:
        List of EMA values. Values are None until enough data points are available.
        First (period - 1) values will be None, then EMA values.
        
    Raises:
        ValueError: If period is less than 1 or greater than len(prices)
    """
    if period < 1:
        raise ValueError(f"EMA period must be >= 1, got {period}")
    
    if len(prices) == 0:
        return []
    
    if period > len(prices):
        raise ValueError(
            f"EMA period ({period}) cannot be greater than number of prices ({len(prices)})"
        )
    
    # Multiplier for EMA calculation
    multiplier = 2.0 / (period + 1.0)
    
    # Initialize result with None values for first (period - 1) elements
    ema_values: List[Optional[float]] = [None] * (period - 1)
    
    # Calculate initial EMA using SMA of first 'period' prices
    initial_sma = sum(prices[:period]) / period
    ema_values.append(initial_sma)
    
    # Calculate EMA for remaining prices
    current_ema = initial_sma
    for price in prices[period:]:
        current_ema = (price * multiplier) + (current_ema * (1 - multiplier))
        ema_values.append(current_ema)
    
    return ema_values


def calculate_ema_at_index(
    prices: List[float],
    period: int,
    index: int
) -> Optional[float]:
    """Calculate EMA at a specific index.
    
    This is a convenience function that calculates EMA up to a specific index.
    
    Args:
        prices: List of price values
        period: EMA period
        index: Index to calculate EMA at (0-based)
        
    Returns:
        EMA value at the given index, or None if not enough data
        
    Raises:
        IndexError: If index is out of range
    """
    if index < 0 or index >= len(prices):
        raise IndexError(f"Index {index} out of range for prices list of length {len(prices)}")
    
    # Need at least 'period' prices ending at index
    if index < period - 1:
        return None
    
    prices_up_to_index = prices[:index + 1]
    ema_values = calculate_ema(prices_up_to_index, period)
    return ema_values[-1] if ema_values else None

