"""Relative Strength Index (RSI) indicator implementation."""
from typing import List, Optional


def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    """Calculate Relative Strength Index (RSI).
    
    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over the period
        
    Uses Wilder's smoothing method:
        Avg Gain = (Prev Avg Gain * (period - 1) + Current Gain) / period
        Avg Loss = (Prev Avg Loss * (period - 1) + Current Loss) / period
    
    Args:
        prices: List of price values (typically close prices)
        period: RSI period (default 14)
        
    Returns:
        List of RSI values. Values are None until enough data points are available.
        First 'period' values will be None, then RSI values.
        
    Raises:
        ValueError: If period is less than 1 or greater than len(prices)
    """
    if period < 1:
        raise ValueError(f"RSI period must be >= 1, got {period}")
    
    if len(prices) == 0:
        return []
    
    if len(prices) == 1:
        return [None]
    
    # Need at least (period + 1) prices to calculate RSI
    if period + 1 > len(prices):
        raise ValueError(
            f"RSI requires at least {period + 1} prices, got {len(prices)}"
        )
    
    # Initialize result with None values for first 'period' elements
    rsi_values: List[Optional[float]] = [None] * period
    
    # Calculate initial average gain and loss
    # Use first (period + 1) prices to get period price changes
    changes = [prices[i + 1] - prices[i] for i in range(period)]
    
    avg_gain = sum(max(change, 0) for change in changes) / period
    avg_loss = sum(abs(min(change, 0)) for change in changes) / period
    
    # Calculate first RSI value
    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
    
    rsi_values.append(rsi)
    
    # Calculate RSI for remaining prices using Wilder's smoothing
    for i in range(period + 1, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(change, 0)
        loss = abs(min(change, 0))
        
        # Wilder's smoothing
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))
        
        rsi_values.append(rsi)
    
    return rsi_values


def calculate_rsi_at_index(
    prices: List[float],
    period: int,
    index: int
) -> Optional[float]:
    """Calculate RSI at a specific index.
    
    This is a convenience function that calculates RSI up to a specific index.
    
    Args:
        prices: List of price values
        period: RSI period (default 14)
        index: Index to calculate RSI at (0-based)
        
    Returns:
        RSI value at the given index, or None if not enough data
        
    Raises:
        IndexError: If index is out of range
    """
    if index < 0 or index >= len(prices):
        raise IndexError(f"Index {index} out of range for prices list of length {len(prices)}")
    
    # Need at least (period + 1) prices ending at index
    if index < period:
        return None
    
    prices_up_to_index = prices[:index + 1]
    rsi_values = calculate_rsi(prices_up_to_index, period)
    return rsi_values[-1] if rsi_values else None

