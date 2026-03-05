"""Support and Resistance levels calculation."""
from typing import List, Tuple, Optional


def find_support_resistance_levels(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    lookback: int = 20,
    min_touches: int = 2,
    tolerance_pct: float = 0.1
) -> Tuple[List[float], List[float]]:
    """Find support and resistance levels.
    
    Support: مستويات السعر التي يجد فيها السعر صعوبة في الهبوط
    Resistance: مستويات السعر التي يجد فيها السعر صعوبة في الصعود
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        lookback: Number of candles to look back for levels
        min_touches: Minimum number of touches to consider a level valid
        tolerance_pct: Percentage tolerance for level matching (0.1 = 0.1%)
        
    Returns:
        Tuple of (support_levels, resistance_levels)
        Each is a list of price levels sorted by strength (most recent first)
    """
    if len(highs) < lookback:
        return ([], [])
    
    # استخدام آخر lookback شموع
    recent_highs = highs[-lookback:]
    recent_lows = lows[-lookback:]
    recent_closes = closes[-lookback:]
    
    # إيجاد القمم (peaks) للمقاومة
    resistance_levels = []
    for i in range(1, len(recent_highs) - 1):
        if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i+1]:
            # قمة محتملة
            resistance_levels.append(recent_highs[i])
    
    # إيجاد القيعان (troughs) للدعم
    support_levels = []
    for i in range(1, len(recent_lows) - 1):
        if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
            # قاع محتمل
            support_levels.append(recent_lows[i])
    
    # تجميع المستويات المتقاربة
    def group_levels(levels: List[float], tolerance: float) -> List[float]:
        """Group nearby levels together."""
        if not levels:
            return []
        
        levels = sorted(levels, reverse=True)
        grouped = []
        
        for level in levels:
            if not grouped:
                grouped.append(level)
            else:
                # Check if this level is close to any existing group
                found_group = False
                for i, grouped_level in enumerate(grouped):
                    if abs(level - grouped_level) / grouped_level <= tolerance / 100.0:
                        # Average the levels
                        grouped[i] = (grouped_level + level) / 2.0
                        found_group = True
                        break
                
                if not found_group:
                    grouped.append(level)
        
        return grouped
    
    # تجميع المستويات
    resistance_grouped = group_levels(resistance_levels, tolerance_pct)
    support_grouped = group_levels(support_levels, tolerance_pct)
    
    # حساب قوة المستوى (عدد اللمسات)
    def count_touches(level: float, prices: List[float], tolerance: float) -> int:
        """Count how many times price touched the level."""
        touches = 0
        for price in prices:
            if abs(price - level) / level <= tolerance / 100.0:
                touches += 1
        return touches
    
    # تصفية المستويات حسب عدد اللمسات
    resistance_filtered = [
        level for level in resistance_grouped
        if count_touches(level, recent_highs, tolerance_pct) >= min_touches
    ]
    support_filtered = [
        level for level in support_grouped
        if count_touches(level, recent_lows, tolerance_pct) >= min_touches
    ]
    
    # ترتيب حسب القرب من السعر الحالي
    current_price = closes[-1] if closes else (highs[-1] + lows[-1]) / 2.0
    
    resistance_sorted = sorted(
        resistance_filtered,
        key=lambda x: abs(x - current_price)
    )
    support_sorted = sorted(
        support_filtered,
        key=lambda x: abs(x - current_price)
    )
    
    return (support_sorted, resistance_sorted)


def get_nearest_support(
    price: float,
    support_levels: List[float]
) -> Optional[float]:
    """Get nearest support level below current price.
    
    Args:
        price: Current price
        support_levels: List of support levels
        
    Returns:
        Nearest support level below price, or None
    """
    below_price = [s for s in support_levels if s < price]
    if not below_price:
        return None
    return max(below_price)


def get_nearest_resistance(
    price: float,
    resistance_levels: List[float]
) -> Optional[float]:
    """Get nearest resistance level above current price.
    
    Args:
        price: Current price
        resistance_levels: List of resistance levels
        
    Returns:
        Nearest resistance level above price, or None
    """
    above_price = [r for r in resistance_levels if r > price]
    if not above_price:
        return None
    return min(above_price)

