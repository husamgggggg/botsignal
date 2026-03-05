"""Price Action patterns detection."""
from typing import List, Optional, Tuple
from enum import Enum


class CandlePattern(Enum):
    """Price action candle patterns."""
    BULLISH_ENGULFING = "BULLISH_ENGULFING"
    BEARISH_ENGULFING = "BEARISH_ENGULFING"
    PIN_BAR_BULLISH = "PIN_BAR_BULLISH"
    PIN_BAR_BEARISH = "PIN_BAR_BEARISH"
    HAMMER = "HAMMER"
    SHOOTING_STAR = "SHOOTING_STAR"
    DOJI = "DOJI"
    NONE = "NONE"


def detect_candle_pattern(
    open_price: float,
    high: float,
    low: float,
    close: float,
    prev_open: Optional[float] = None,
    prev_high: Optional[float] = None,
    prev_low: Optional[float] = None,
    prev_close: Optional[float] = None
) -> CandlePattern:
    """Detect price action pattern in a candle.
    
    Args:
        open_price: Current candle open
        high: Current candle high
        low: Current candle low
        close: Current candle close
        prev_open: Previous candle open (optional)
        prev_high: Previous candle high (optional)
        prev_low: Previous candle low (optional)
        prev_close: Previous candle close (optional)
        
    Returns:
        Detected candle pattern
    """
    body = abs(close - open_price)
    upper_wick = high - max(close, open_price)
    lower_wick = min(close, open_price) - low
    total_range = high - low
    
    if total_range == 0:
        return CandlePattern.NONE
    
    body_ratio = body / total_range
    upper_wick_ratio = upper_wick / total_range
    lower_wick_ratio = lower_wick / total_range
    
    is_bullish = close > open_price
    is_bearish = close < open_price
    
    # Pin Bar (Bullish) - شمعة دبوس صاعدة
    # جسم صغير، ذيل سفلي طويل، ذيل علوي صغير
    if body_ratio < 0.3 and lower_wick_ratio > 0.6 and upper_wick_ratio < 0.2:
        if is_bullish or abs(close - open_price) < body * 0.3:
            return CandlePattern.PIN_BAR_BULLISH
    
    # Pin Bar (Bearish) - شمعة دبوس هابطة
    # جسم صغير، ذيل علوي طويل، ذيل سفلي صغير
    if body_ratio < 0.3 and upper_wick_ratio > 0.6 and lower_wick_ratio < 0.2:
        if is_bearish or abs(close - open_price) < body * 0.3:
            return CandlePattern.PIN_BAR_BEARISH
    
    # Hammer - مطرقة (إشارة صاعدة)
    # جسم صغير في الأعلى، ذيل سفلي طويل
    if body_ratio < 0.3 and lower_wick_ratio > 0.6 and upper_wick_ratio < 0.3:
        if low < (high + low) / 2:  # الجسم في النصف العلوي
            return CandlePattern.HAMMER
    
    # Shooting Star - نجمة ساقطة (إشارة هابطة)
    # جسم صغير في الأسفل، ذيل علوي طويل
    if body_ratio < 0.3 and upper_wick_ratio > 0.6 and lower_wick_ratio < 0.3:
        if high > (high + low) / 2:  # الجسم في النصف السفلي
            return CandlePattern.SHOOTING_STAR
    
    # Doji - دوجي (عدم قرار)
    # جسم صغير جداً
    if body_ratio < 0.1:
        return CandlePattern.DOJI
    
        # Engulfing patterns (تحتاج شمعة سابقة)
        if prev_open is not None and prev_close is not None:
            prev_body = abs(prev_close - prev_open)
            prev_is_bullish = prev_close > prev_open
            prev_is_bearish = prev_close < prev_open
            
            # Bullish Engulfing - ابتلاع صاعد
            # شمعة حمراء صغيرة يليها شمعة خضراء كبيرة تبتلعها
            if (prev_is_bearish and is_bullish and
                body > prev_body * 1.5 and
                open_price < prev_close and close > prev_open):
                return CandlePattern.BULLISH_ENGULFING
            
            # Bearish Engulfing - ابتلاع هابط
            # شمعة خضراء صغيرة يليها شمعة حمراء كبيرة تبتلعها
            if (prev_is_bullish and is_bearish and
                body > prev_body * 1.5 and
                open_price > prev_close and close < prev_open):
                return CandlePattern.BEARISH_ENGULFING
    
    return CandlePattern.NONE


def is_bullish_pattern(pattern: CandlePattern) -> bool:
    """Check if pattern is bullish.
    
    Args:
        pattern: Candle pattern
        
    Returns:
        True if pattern is bullish
    """
    return pattern in [
        CandlePattern.BULLISH_ENGULFING,
        CandlePattern.PIN_BAR_BULLISH,
        CandlePattern.HAMMER
    ]


def is_bearish_pattern(pattern: CandlePattern) -> bool:
    """Check if pattern is bearish.
    
    Args:
        pattern: Candle pattern
        
    Returns:
        True if pattern is bearish
    """
    return pattern in [
        CandlePattern.BEARISH_ENGULFING,
        CandlePattern.PIN_BAR_BEARISH,
        CandlePattern.SHOOTING_STAR
    ]

