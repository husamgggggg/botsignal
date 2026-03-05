"""Moving Average Convergence Divergence (MACD) indicator implementation."""
from typing import List, Tuple, Optional
from src.indicators.ema import calculate_ema


def calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """Calculate MACD indicator.
    
    MACD consists of:
    - MACD Line: EMA(fast_period) - EMA(slow_period)
    - Signal Line: EMA of MACD Line (signal_period)
    - Histogram: MACD Line - Signal Line
    
    Args:
        prices: List of price values (typically close prices)
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)
        
    Returns:
        Tuple of (macd_line, signal_line, histogram)
        Each is a list of values. Values are None until enough data points are available.
        
    Raises:
        ValueError: If periods are invalid or insufficient data
    """
    if fast_period < 1 or slow_period < 1 or signal_period < 1:
        raise ValueError("MACD periods must be >= 1")
    
    if fast_period >= slow_period:
        raise ValueError(f"Fast period ({fast_period}) must be less than slow period ({slow_period})")
    
    if len(prices) == 0:
        return ([], [], [])
    
    # Need at least slow_period + signal_period prices
    min_required = slow_period + signal_period
    if len(prices) < min_required:
        return (
            [None] * len(prices),
            [None] * len(prices),
            [None] * len(prices)
        )
    
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(prices, fast_period)
    slow_ema = calculate_ema(prices, slow_period)
    
    # Calculate MACD line (difference between fast and slow EMA)
    macd_line: List[Optional[float]] = []
    
    # MACD line starts after slow EMA is available
    # First (slow_period - 1) values are None
    for i in range(slow_period - 1):
        macd_line.append(None)
    
    # Calculate MACD line where both EMAs are available
    for i in range(slow_period - 1, len(prices)):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            macd_line.append(fast_ema[i] - slow_ema[i])
        else:
            macd_line.append(None)
    
    # Calculate Signal line (EMA of MACD line)
    # Extract non-None MACD values for signal calculation
    macd_values = [v for v in macd_line if v is not None]
    
    if len(macd_values) < signal_period:
        signal_line = [None] * len(macd_line)
        histogram = [None] * len(macd_line)
        return (macd_line, signal_line, histogram)
    
    # Calculate signal line EMA
    signal_ema = calculate_ema(macd_values, signal_period)
    
    # Map signal line back to original length
    signal_line: List[Optional[float]] = []
    signal_idx = 0
    
    for i in range(len(macd_line)):
        if macd_line[i] is None:
            signal_line.append(None)
        else:
            if signal_idx < len(signal_ema):
                signal_line.append(signal_ema[signal_idx])
                signal_idx += 1
            else:
                signal_line.append(None)
    
    # Calculate Histogram (MACD Line - Signal Line)
    histogram: List[Optional[float]] = []
    for i in range(len(macd_line)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(None)
    
    return (macd_line, signal_line, histogram)


def calculate_macd_at_index(
    prices: List[float],
    fast_period: int,
    slow_period: int,
    signal_period: int,
    index: int
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Calculate MACD at a specific index.
    
    Args:
        prices: List of price values
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line EMA period
        index: Index to calculate MACD at (0-based)
        
    Returns:
        Tuple of (macd_line, signal_line, histogram) at the given index
        
    Raises:
        IndexError: If index is out of range
    """
    if index < 0 or index >= len(prices):
        raise IndexError(f"Index {index} out of range for prices list of length {len(prices)}")
    
    prices_up_to_index = prices[:index + 1]
    macd_line, signal_line, histogram = calculate_macd(
        prices_up_to_index, fast_period, slow_period, signal_period
    )
    
    return (
        macd_line[-1] if macd_line else None,
        signal_line[-1] if signal_line else None,
        histogram[-1] if histogram else None
    )

