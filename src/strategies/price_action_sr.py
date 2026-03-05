"""Price Action + Support/Resistance Strategy.

الاستراتيجية:
- تحديد مستويات الدعم والمقاومة تلقائياً
- استخدام Price Action patterns (أنماط الشموع)
- إشارة شراء عند الارتداد من الدعم مع نمط صاعد
- إشارة بيع عند الارتداد من المقاومة مع نمط هابط
- تنبيه "احتمال صفقة" عند اقتراب المستوى
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from src.indicators.support_resistance import (
    find_support_resistance_levels,
    get_nearest_support,
    get_nearest_resistance
)
from src.indicators.price_action import (
    detect_candle_pattern,
    is_bullish_pattern,
    is_bearish_pattern,
    CandlePattern
)


class Signal(Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"
    POTENTIAL_BUY = "POTENTIAL_BUY"
    POTENTIAL_SELL = "POTENTIAL_SELL"


@dataclass
class StrategyResult:
    """Result of strategy analysis."""
    signal: Signal
    confidence: int  # 0-100
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    current_price: float
    candle_pattern: CandlePattern
    rationale: str


class PriceActionSRStrategy:
    """استراتيجية Price Action + Support/Resistance.
    
    القواعد:
        1. شراء (BUY):
           - السعر قريب من مستوى دعم
           - نمط شمعة صاعد (Bullish Engulfing, Pin Bar Bullish, Hammer)
           - السعر يرتد من الدعم
        
        2. بيع (SELL):
           - السعر قريب من مستوى مقاومة
           - نمط شمعة هابط (Bearish Engulfing, Pin Bar Bearish, Shooting Star)
           - السعر يرتد من المقاومة
        
        3. احتمال صفقة (POTENTIAL):
           - السعر قريب من مستوى لكن لم يظهر نمط بعد
    """
    
    def __init__(
        self,
        lookback: int = 20,
        min_touches: int = 2,
        tolerance_pct: float = 0.1,
        proximity_pct: float = 0.15
    ):
        """Initialize strategy.
        
        Args:
            lookback: عدد الشموع للبحث عن مستويات الدعم/المقاومة (default 20)
            min_touches: الحد الأدنى لعدد اللمسات للمستوى (default 2)
            tolerance_pct: نسبة التسامح لتجميع المستويات (default 0.1%)
            proximity_pct: نسبة القرب من المستوى لإعطاء إشارة (default 0.15%)
        """
        self.lookback = lookback
        self.min_touches = min_touches
        self.tolerance_pct = tolerance_pct
        self.proximity_pct = proximity_pct
    
    def analyze(self, candles: List[dict]) -> StrategyResult:
        """Analyze candles and generate trading signal.
        
        Args:
            candles: List of candle dictionaries with 'open', 'high', 'low', 'close' keys
                    Candles should be ordered chronologically (oldest first)
        
        Returns:
            StrategyResult with signal, confidence, levels, and rationale
            
        Raises:
            ValueError: If insufficient candles or missing data
        """
        if len(candles) == 0:
            raise ValueError("Cannot analyze empty candles list")
        
        min_candles = max(self.lookback + 1, 5)  # على الأقل lookback + 1
        if len(candles) < min_candles:
            raise ValueError(
                f"Need at least {min_candles} candles, got {len(candles)}"
            )
        
        # استخراج البيانات
        highs = [float(candle["high"]) for candle in candles]
        lows = [float(candle["low"]) for candle in candles]
        opens = [float(candle["open"]) for candle in candles]
        closes = [float(candle["close"]) for candle in candles]
        
        # السعر الحالي
        current_price = closes[-1]
        current_open = opens[-1]
        current_high = highs[-1]
        current_low = lows[-1]
        current_close = closes[-1]
        
        # إيجاد مستويات الدعم والمقاومة
        support_levels, resistance_levels = find_support_resistance_levels(
            highs=highs,
            lows=lows,
            closes=closes,
            lookback=self.lookback,
            min_touches=self.min_touches,
            tolerance_pct=self.tolerance_pct
        )
        
        # إيجاد أقرب دعم ومقاومة
        nearest_support = get_nearest_support(current_price, support_levels)
        nearest_resistance = get_nearest_resistance(current_price, resistance_levels)
        
        # اكتشاف نمط الشمعة الحالية
        prev_open = opens[-2] if len(opens) > 1 else None
        prev_high = highs[-2] if len(highs) > 1 else None
        prev_low = lows[-2] if len(lows) > 1 else None
        prev_close = closes[-2] if len(closes) > 1 else None
        
        current_pattern = detect_candle_pattern(
            open_price=current_open,
            high=current_high,
            low=current_low,
            close=current_close,
            prev_open=prev_open,
            prev_high=prev_high,
            prev_low=prev_low,
            prev_close=prev_close
        )
        
        # فحص شروط الشراء (ارتداد من الدعم)
        if nearest_support is not None:
            distance_to_support = abs(current_price - nearest_support) / nearest_support * 100
            
            # إذا كان السعر قريب من الدعم (ضمن proximity_pct)
            if distance_to_support <= self.proximity_pct:
                # فحص نمط الشمعة
                if is_bullish_pattern(current_pattern):
                    # إشارة شراء!
                    confidence = self._calculate_confidence(
                        distance_pct=distance_to_support,
                        pattern=current_pattern,
                        signal_type="buy"
                    )
                    
                    return StrategyResult(
                        signal=Signal.BUY,
                        confidence=confidence,
                        nearest_support=nearest_support,
                        nearest_resistance=nearest_resistance,
                        current_price=current_price,
                        candle_pattern=current_pattern,
                        rationale=(
                            f"✅ إشارة شراء: السعر ({current_price:.5f}) قريب من الدعم "
                            f"({nearest_support:.5f}), نمط صاعد ({current_pattern.value})"
                        )
                    )
                else:
                    # السعر قريب من الدعم لكن لم يظهر نمط بعد
                    # نعتبره إشارة شراء ضعيفة إذا كان السعر قريب جداً
                    if distance_to_support <= self.proximity_pct * 0.5:  # قريب جداً (نصف المسافة)
                        confidence = self._calculate_confidence(
                            distance_pct=distance_to_support,
                            pattern=current_pattern,
                            signal_type="buy"
                        )
                        # تقليل الثقة لأن النمط لم يظهر بعد
                        confidence = max(50, int(confidence * 0.7))
                        
                        return StrategyResult(
                            signal=Signal.BUY,
                            confidence=confidence,
                            nearest_support=nearest_support,
                            nearest_resistance=nearest_resistance,
                            current_price=current_price,
                            candle_pattern=current_pattern,
                            rationale=(
                                f"✅ إشارة شراء (ضعيفة): السعر ({current_price:.5f}) قريب جداً من الدعم "
                                f"({nearest_support:.5f}), لكن لم يظهر نمط صاعد بعد"
                            )
                        )
                    else:
                        # بعيد قليلاً، نعتبره POTENTIAL
                        return StrategyResult(
                            signal=Signal.POTENTIAL_BUY,
                            confidence=40,
                            nearest_support=nearest_support,
                            nearest_resistance=nearest_resistance,
                            current_price=current_price,
                            candle_pattern=current_pattern,
                            rationale=(
                                f"⚠️ احتمال شراء: السعر ({current_price:.5f}) قريب من الدعم "
                                f"({nearest_support:.5f}), في انتظار نمط صاعد"
                            )
                        )
        
        # فحص شروط البيع (ارتداد من المقاومة)
        if nearest_resistance is not None:
            distance_to_resistance = abs(current_price - nearest_resistance) / nearest_resistance * 100
            
            # إذا كان السعر قريب من المقاومة
            if distance_to_resistance <= self.proximity_pct:
                # فحص نمط الشمعة
                if is_bearish_pattern(current_pattern):
                    # إشارة بيع!
                    confidence = self._calculate_confidence(
                        distance_pct=distance_to_resistance,
                        pattern=current_pattern,
                        signal_type="sell"
                    )
                    
                    return StrategyResult(
                        signal=Signal.SELL,
                        confidence=confidence,
                        nearest_support=nearest_support,
                        nearest_resistance=nearest_resistance,
                        current_price=current_price,
                        candle_pattern=current_pattern,
                        rationale=(
                            f"✅ إشارة بيع: السعر ({current_price:.5f}) قريب من المقاومة "
                            f"({nearest_resistance:.5f}), نمط هابط ({current_pattern.value})"
                        )
                    )
                else:
                    # السعر قريب من المقاومة لكن لم يظهر نمط بعد
                    # نعتبره إشارة بيع ضعيفة إذا كان السعر قريب جداً
                    if distance_to_resistance <= self.proximity_pct * 0.5:  # قريب جداً (نصف المسافة)
                        confidence = self._calculate_confidence(
                            distance_pct=distance_to_resistance,
                            pattern=current_pattern,
                            signal_type="sell"
                        )
                        # تقليل الثقة لأن النمط لم يظهر بعد
                        confidence = max(50, int(confidence * 0.7))
                        
                        return StrategyResult(
                            signal=Signal.SELL,
                            confidence=confidence,
                            nearest_support=nearest_support,
                            nearest_resistance=nearest_resistance,
                            current_price=current_price,
                            candle_pattern=current_pattern,
                            rationale=(
                                f"✅ إشارة بيع (ضعيفة): السعر ({current_price:.5f}) قريب جداً من المقاومة "
                                f"({nearest_resistance:.5f}), لكن لم يظهر نمط هابط بعد"
                            )
                        )
                    else:
                        # بعيد قليلاً، نعتبره POTENTIAL
                        return StrategyResult(
                            signal=Signal.POTENTIAL_SELL,
                            confidence=40,
                            nearest_support=nearest_support,
                            nearest_resistance=nearest_resistance,
                            current_price=current_price,
                            candle_pattern=current_pattern,
                            rationale=(
                                f"⚠️ احتمال بيع: السعر ({current_price:.5f}) قريب من المقاومة "
                                f"({nearest_resistance:.5f}), في انتظار نمط هابط"
                            )
                        )
        
        # لا توجد إشارة
        support_str = f"{nearest_support:.5f}" if nearest_support is not None else "N/A"
        resistance_str = f"{nearest_resistance:.5f}" if nearest_resistance is not None else "N/A"
        return StrategyResult(
            signal=Signal.NO_TRADE,
            confidence=0,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            current_price=current_price,
            candle_pattern=current_pattern,
            rationale=(
                f"لا توجد إشارة: السعر ({current_price:.5f}), "
                f"دعم: {support_str}, "
                f"مقاومة: {resistance_str}"
            )
        )
    
    def _calculate_confidence(
        self,
        distance_pct: float,
        pattern: CandlePattern,
        signal_type: str
    ) -> int:
        """Calculate confidence score (0-100).
        
        Args:
            distance_pct: Distance to support/resistance as percentage
            pattern: Detected candle pattern
            signal_type: "buy" or "sell"
            
        Returns:
            Confidence score 0-100
        """
        # الثقة تعتمد على:
        # 1. القرب من المستوى (كلما كان أقرب = ثقة أعلى)
        # 2. قوة النمط
        
        # القرب من المستوى: 0-50 نقطة
        # كلما كان أقرب (distance_pct أصغر) = ثقة أعلى
        proximity_score = max(0, 50 - (distance_pct * 10))
        
        # قوة النمط: 0-50 نقطة
        pattern_strength = {
            CandlePattern.BULLISH_ENGULFING: 50,
            CandlePattern.BEARISH_ENGULFING: 50,
            CandlePattern.PIN_BAR_BULLISH: 45,
            CandlePattern.PIN_BAR_BEARISH: 45,
            CandlePattern.HAMMER: 40,
            CandlePattern.SHOOTING_STAR: 40,
        }.get(pattern, 30)
        
        total_confidence = proximity_score + pattern_strength
        
        # ضمان حد أدنى من الثقة
        return max(60, min(100, int(total_confidence)))

