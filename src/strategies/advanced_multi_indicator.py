"""Advanced Multi-Indicator Strategy - استراتيجية متقدمة متعددة المؤشرات.

هذه الاستراتيجية تجمع بين أقوى المؤشرات الفنية لزيادة نسبة النجاح:
- MACD: لتحديد الاتجاه والقوة
- RSI: لتجنب الذروات (تجنب الشراء في ذروة الشراء والبيع في ذروة البيع)
- EMA (10, 20, 50): للاتجاهات متعددة الأطر الزمنية
- Support/Resistance: للمستويات المهمة
- Price Action: للتحقق من أنماط الشموع

الاستراتيجية تتطلب تأكيد من 4-5 مؤشرات على الأقل قبل إعطاء إشارة.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum

from src.indicators.ema import calculate_ema
from src.indicators.rsi import calculate_rsi
from src.indicators.macd import calculate_macd
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


@dataclass
class StrategyResult:
    """Result of strategy analysis."""
    signal: Signal
    confidence: int  # 0-100
    macd_line: Optional[float]
    macd_signal: Optional[float]
    macd_histogram: Optional[float]
    rsi: Optional[float]
    ema_10: Optional[float]
    ema_20: Optional[float]
    ema_50: Optional[float]
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    candle_pattern: CandlePattern
    last_close: float
    rationale: str
    confirmation_count: int  # عدد المؤشرات المؤكدة (0-5)


class AdvancedMultiIndicatorStrategy:
    """استراتيجية متقدمة متعددة المؤشرات.
    
    القواعد:
        1. شراء (BUY) - يتطلب تأكيد من 4 مؤشرات على الأقل:
           - MACD: MACD Line > Signal Line AND MACD Line > 0 AND Histogram > 0
           - RSI: بين 45-70 (تجنب الذروة)
           - EMA: السعر > EMA10 > EMA20 > EMA50 (ترند صاعد قوي)
           - Support/Resistance: السعر قريب من دعم أو ارتداد من دعم
           - Price Action: نمط شمعة صاعد (Bullish Engulfing, Hammer, etc.)
        
        2. بيع (SELL) - يتطلب تأكيد من 4 مؤشرات على الأقل:
           - MACD: MACD Line < Signal Line AND MACD Line < 0 AND Histogram < 0
           - RSI: بين 30-55 (تجنب الذروة)
           - EMA: السعر < EMA10 < EMA20 < EMA50 (ترند هابط قوي)
           - Support/Resistance: السعر قريب من مقاومة أو ارتداد من مقاومة
           - Price Action: نمط شمعة هابط (Bearish Engulfing, Shooting Star, etc.)
        
        3. لا تداول (NO_TRADE): إذا لم يتم تأكيد 4 مؤشرات على الأقل
    """
    
    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        rsi_buy_min: float = 45.0,
        rsi_buy_max: float = 70.0,
        rsi_sell_min: float = 30.0,
        rsi_sell_max: float = 55.0,
        ema_short: int = 10,
        ema_medium: int = 20,
        ema_long: int = 50,
        sr_lookback: int = 50,
        sr_min_touches: int = 2,
        sr_tolerance_pct: float = 0.15,
        sr_proximity_pct: float = 0.2,
        min_confirmations: int = 4  # الحد الأدنى للمؤشرات المؤكدة
    ):
        """Initialize strategy.
        
        Args:
            macd_fast: فترة MACD السريعة (default 12)
            macd_slow: فترة MACD البطيئة (default 26)
            macd_signal: فترة خط الإشارة (default 9)
            rsi_period: فترة RSI (default 14)
            rsi_buy_min: الحد الأدنى لـ RSI للشراء (default 45)
            rsi_buy_max: الحد الأقصى لـ RSI للشراء (default 70)
            rsi_sell_min: الحد الأدنى لـ RSI للبيع (default 30)
            rsi_sell_max: الحد الأقصى لـ RSI للبيع (default 55)
            ema_short: فترة EMA القصيرة (default 10)
            ema_medium: فترة EMA المتوسطة (default 20)
            ema_long: فترة EMA الطويلة (default 50)
            sr_lookback: عدد الشموع للبحث عن مستويات الدعم/المقاومة (default 50)
            sr_min_touches: الحد الأدنى لعدد اللمسات للمستوى (default 2)
            sr_tolerance_pct: نسبة التسامح لتجميع المستويات (default 0.15%)
            sr_proximity_pct: نسبة القرب من المستوى (default 0.2%)
            min_confirmations: الحد الأدنى للمؤشرات المؤكدة (default 4)
        """
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.rsi_period = rsi_period
        self.rsi_buy_min = rsi_buy_min
        self.rsi_buy_max = rsi_buy_max
        self.rsi_sell_min = rsi_sell_min
        self.rsi_sell_max = rsi_sell_max
        self.ema_short = ema_short
        self.ema_medium = ema_medium
        self.ema_long = ema_long
        self.sr_lookback = sr_lookback
        self.sr_min_touches = sr_min_touches
        self.sr_tolerance_pct = sr_tolerance_pct
        self.sr_proximity_pct = sr_proximity_pct
        self.min_confirmations = min_confirmations
    
    def analyze(self, candles: List[dict]) -> StrategyResult:
        """Analyze candles and generate trading signal.
        
        Args:
            candles: List of candle dictionaries with 'open', 'high', 'low', 'close' keys
                    Candles should be ordered chronologically (oldest first)
        
        Returns:
            StrategyResult with signal, confidence, indicators, and rationale
            
        Raises:
            ValueError: If insufficient candles or missing data
        """
        if len(candles) == 0:
            raise ValueError("Cannot analyze empty candles list")
        
        # نحتاج على الأقل ema_long + macd_slow + macd_signal شموع
        min_candles = max(self.ema_long, self.macd_slow + self.macd_signal, self.rsi_period + 1)
        # نقبل أقل قليلاً للتعامل مع الشموع غير المكتملة من OANDA
        min_candles_flexible = max(min_candles - 1, self.ema_long - 1)
        if len(candles) < min_candles_flexible:
            raise ValueError(
                f"Need at least {min_candles_flexible} candles, got {len(candles)}"
            )
        
        # استخراج البيانات
        close_prices = [float(candle["close"]) for candle in candles]
        open_prices = [float(candle["open"]) for candle in candles]
        high_prices = [float(candle["high"]) for candle in candles]
        low_prices = [float(candle["low"]) for candle in candles]
        
        # السعر الحالي
        current_price = close_prices[-1]
        current_open = open_prices[-1]
        current_high = high_prices[-1]
        current_low = low_prices[-1]
        current_close = close_prices[-1]
        
        # حساب جميع المؤشرات
        macd_line, signal_line, histogram = calculate_macd(
            close_prices,
            fast_period=self.macd_fast,
            slow_period=self.macd_slow,
            signal_period=self.macd_signal
        )
        
        rsi_values = calculate_rsi(close_prices, self.rsi_period)
        
        ema_10_values = calculate_ema(close_prices, self.ema_short)
        ema_20_values = calculate_ema(close_prices, self.ema_medium)
        ema_50_values = calculate_ema(close_prices, self.ema_long)
        
        # الحصول على القيم الأخيرة
        last_macd = macd_line[-1] if macd_line and macd_line[-1] is not None else None
        last_signal = signal_line[-1] if signal_line and signal_line[-1] is not None else None
        last_histogram = histogram[-1] if histogram and histogram[-1] is not None else None
        last_rsi = rsi_values[-1] if rsi_values and rsi_values[-1] is not None else None
        last_ema_10 = ema_10_values[-1] if ema_10_values and ema_10_values[-1] is not None else None
        last_ema_20 = ema_20_values[-1] if ema_20_values and ema_20_values[-1] is not None else None
        last_ema_50 = ema_50_values[-1] if ema_50_values and ema_50_values[-1] is not None else None
        
        # التحقق من وجود جميع المؤشرات
        if any(x is None for x in [last_macd, last_signal, last_histogram, last_rsi, 
                                    last_ema_10, last_ema_20, last_ema_50]):
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                macd_line=last_macd,
                macd_signal=last_signal,
                macd_histogram=last_histogram,
                rsi=last_rsi,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=None,
                nearest_resistance=None,
                candle_pattern=CandlePattern.NONE,
                last_close=current_price,
                rationale="لا توجد بيانات كافية لحساب جميع المؤشرات",
                confirmation_count=0
            )
        
        # إيجاد مستويات الدعم والمقاومة
        support_levels, resistance_levels = find_support_resistance_levels(
            highs=high_prices,
            lows=low_prices,
            closes=close_prices,
            lookback=self.sr_lookback,
            min_touches=self.sr_min_touches,
            tolerance_pct=self.sr_tolerance_pct
        )
        
        nearest_support = get_nearest_support(current_price, support_levels)
        nearest_resistance = get_nearest_resistance(current_price, resistance_levels)
        
        # اكتشاف نمط الشمعة
        prev_open = open_prices[-2] if len(open_prices) > 1 else None
        prev_high = high_prices[-2] if len(high_prices) > 1 else None
        prev_low = low_prices[-2] if len(low_prices) > 1 else None
        prev_close = close_prices[-2] if len(close_prices) > 1 else None
        
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
        
        # فحص شروط الشراء
        buy_confirmations = self._check_buy_conditions(
            macd=last_macd,
            signal=last_signal,
            histogram=last_histogram,
            rsi=last_rsi,
            price=current_price,
            ema_10=last_ema_10,
            ema_20=last_ema_20,
            ema_50=last_ema_50,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            pattern=current_pattern
        )
        
        # فحص شروط البيع
        sell_confirmations = self._check_sell_conditions(
            macd=last_macd,
            signal=last_signal,
            histogram=last_histogram,
            rsi=last_rsi,
            price=current_price,
            ema_10=last_ema_10,
            ema_20=last_ema_20,
            ema_50=last_ema_50,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            pattern=current_pattern
        )
        
        # تحديد الإشارة بناءً على عدد التأكيدات
        buy_count = sum(buy_confirmations.values())
        sell_count = sum(sell_confirmations.values())
        
        if buy_count >= self.min_confirmations and buy_count > sell_count:
            # إشارة شراء قوية
            confidence = self._calculate_confidence(
                confirmations=buy_confirmations,
                macd=last_macd,
                signal=last_signal,
                histogram=last_histogram,
                rsi=last_rsi,
                price=current_price,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=nearest_support,
                signal_type="buy"
            )
            
            rationale = self._build_rationale(
                confirmations=buy_confirmations,
                macd=last_macd,
                signal=last_signal,
                histogram=last_histogram,
                rsi=last_rsi,
                price=current_price,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=nearest_support,
                pattern=current_pattern,
                signal_type="buy"
            )
            
            return StrategyResult(
                signal=Signal.BUY,
                confidence=confidence,
                macd_line=last_macd,
                macd_signal=last_signal,
                macd_histogram=last_histogram,
                rsi=last_rsi,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=nearest_support,
                nearest_resistance=nearest_resistance,
                candle_pattern=current_pattern,
                last_close=current_price,
                rationale=rationale,
                confirmation_count=buy_count
            )
        
        elif sell_count >= self.min_confirmations and sell_count > buy_count:
            # إشارة بيع قوية
            confidence = self._calculate_confidence(
                confirmations=sell_confirmations,
                macd=last_macd,
                signal=last_signal,
                histogram=last_histogram,
                rsi=last_rsi,
                price=current_price,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_resistance=nearest_resistance,
                signal_type="sell"
            )
            
            rationale = self._build_rationale(
                confirmations=sell_confirmations,
                macd=last_macd,
                signal=last_signal,
                histogram=last_histogram,
                rsi=last_rsi,
                price=current_price,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_resistance=nearest_resistance,
                pattern=current_pattern,
                signal_type="sell"
            )
            
            return StrategyResult(
                signal=Signal.SELL,
                confidence=confidence,
                macd_line=last_macd,
                macd_signal=last_signal,
                macd_histogram=last_histogram,
                rsi=last_rsi,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=nearest_support,
                nearest_resistance=nearest_resistance,
                candle_pattern=current_pattern,
                last_close=current_price,
                rationale=rationale,
                confirmation_count=sell_count
            )
        
        else:
            # لا توجد إشارة (عدد التأكيدات غير كافٍ)
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                macd_line=last_macd,
                macd_signal=last_signal,
                macd_histogram=last_histogram,
                rsi=last_rsi,
                ema_10=last_ema_10,
                ema_20=last_ema_20,
                ema_50=last_ema_50,
                nearest_support=nearest_support,
                nearest_resistance=nearest_resistance,
                candle_pattern=current_pattern,
                last_close=current_price,
                rationale=(
                    f"لا توجد إشارة: تأكيدات الشراء: {buy_count}/{self.min_confirmations}, "
                    f"تأكيدات البيع: {sell_count}/{self.min_confirmations}"
                ),
                confirmation_count=max(buy_count, sell_count)
            )
    
    def _check_buy_conditions(
        self,
        macd: float,
        signal: float,
        histogram: float,
        rsi: float,
        price: float,
        ema_10: float,
        ema_20: float,
        ema_50: float,
        nearest_support: Optional[float],
        nearest_resistance: Optional[float],
        pattern: CandlePattern
    ) -> dict:
        """Check buy conditions and return confirmation dict.
        
        Returns:
            Dict with confirmation status for each indicator
        """
        confirmations = {}
        
        # 1. MACD confirmation
        macd_bullish = (macd > signal) and (macd > 0) and (histogram > 0)
        confirmations["macd"] = macd_bullish
        
        # 2. RSI confirmation (تجنب الذروة)
        rsi_ok = self.rsi_buy_min <= rsi <= self.rsi_buy_max
        confirmations["rsi"] = rsi_ok
        
        # 3. EMA confirmation (ترند صاعد قوي)
        ema_bullish = (price > ema_10) and (ema_10 > ema_20) and (ema_20 > ema_50)
        confirmations["ema"] = ema_bullish
        
        # 4. Support/Resistance confirmation
        sr_ok = False
        if nearest_support is not None:
            distance_pct = abs(price - nearest_support) / nearest_support * 100
            if distance_pct <= self.sr_proximity_pct:
                sr_ok = True
        confirmations["support_resistance"] = sr_ok
        
        # 5. Price Action confirmation
        price_action_ok = is_bullish_pattern(pattern)
        confirmations["price_action"] = price_action_ok
        
        return confirmations
    
    def _check_sell_conditions(
        self,
        macd: float,
        signal: float,
        histogram: float,
        rsi: float,
        price: float,
        ema_10: float,
        ema_20: float,
        ema_50: float,
        nearest_support: Optional[float],
        nearest_resistance: Optional[float],
        pattern: CandlePattern
    ) -> dict:
        """Check sell conditions and return confirmation dict.
        
        Returns:
            Dict with confirmation status for each indicator
        """
        confirmations = {}
        
        # 1. MACD confirmation
        macd_bearish = (macd < signal) and (macd < 0) and (histogram < 0)
        confirmations["macd"] = macd_bearish
        
        # 2. RSI confirmation (تجنب الذروة)
        rsi_ok = self.rsi_sell_min <= rsi <= self.rsi_sell_max
        confirmations["rsi"] = rsi_ok
        
        # 3. EMA confirmation (ترند هابط قوي)
        ema_bearish = (price < ema_10) and (ema_10 < ema_20) and (ema_20 < ema_50)
        confirmations["ema"] = ema_bearish
        
        # 4. Support/Resistance confirmation
        sr_ok = False
        if nearest_resistance is not None:
            distance_pct = abs(price - nearest_resistance) / nearest_resistance * 100
            if distance_pct <= self.sr_proximity_pct:
                sr_ok = True
        confirmations["support_resistance"] = sr_ok
        
        # 5. Price Action confirmation
        price_action_ok = is_bearish_pattern(pattern)
        confirmations["price_action"] = price_action_ok
        
        return confirmations
    
    def _calculate_confidence(
        self,
        confirmations: dict,
        macd: float,
        signal: float,
        histogram: float,
        rsi: float,
        price: float,
        ema_10: float,
        ema_20: float,
        ema_50: float,
        nearest_support: Optional[float] = None,
        nearest_resistance: Optional[float] = None,
        signal_type: str = "buy"
    ) -> int:
        """Calculate confidence score (0-100) based on confirmations and indicator strength.
        
        Args:
            confirmations: Dict with confirmation status for each indicator
            macd: MACD line value
            signal: Signal line value
            histogram: Histogram value
            rsi: RSI value
            price: Current price
            ema_10: EMA10 value
            ema_20: EMA20 value
            ema_50: EMA50 value
            nearest_support: Nearest support level (for buy)
            nearest_resistance: Nearest resistance level (for sell)
            signal_type: "buy" or "sell"
            
        Returns:
            Confidence score 0-100
        """
        # الثقة الأساسية: عدد التأكيدات (20 نقطة لكل تأكيد)
        base_confidence = sum(confirmations.values()) * 20
        
        # قوة MACD (0-15 نقطة)
        macd_strength = 0
        if confirmations.get("macd", False):
            if signal_type == "buy":
                macd_strength = min(15, abs(macd) * 10000)  # تحويل إلى مقياس مناسب
            else:
                macd_strength = min(15, abs(macd) * 10000)
        
        # قوة RSI (0-10 نقطة) - كلما كان أقرب للمنطقة المثالية
        rsi_strength = 0
        if confirmations.get("rsi", False):
            if signal_type == "buy":
                ideal_rsi = (self.rsi_buy_min + self.rsi_buy_max) / 2  # 57.5
                rsi_distance = abs(rsi - ideal_rsi)
                rsi_strength = max(0, 10 - (rsi_distance * 0.4))
            else:
                ideal_rsi = (self.rsi_sell_min + self.rsi_sell_max) / 2  # 42.5
                rsi_distance = abs(rsi - ideal_rsi)
                rsi_strength = max(0, 10 - (rsi_distance * 0.4))
        
        # قوة EMA (0-10 نقطة) - المسافة من المتوسطات
        ema_strength = 0
        if confirmations.get("ema", False):
            if signal_type == "buy":
                # المسافة فوق EMA10 كنسبة مئوية
                distance_pct = ((price - ema_10) / ema_10) * 100
                ema_strength = min(10, max(5, distance_pct * 2))
            else:
                # المسافة تحت EMA10
                distance_pct = ((ema_10 - price) / ema_10) * 100
                ema_strength = min(10, max(5, distance_pct * 2))
        
        # قوة Support/Resistance (0-10 نقطة) - القرب من المستوى
        sr_strength = 0
        if confirmations.get("support_resistance", False):
            if signal_type == "buy" and nearest_support is not None:
                distance_pct = abs(price - nearest_support) / nearest_support * 100
                sr_strength = max(0, 10 - (distance_pct * 50))
            elif signal_type == "sell" and nearest_resistance is not None:
                distance_pct = abs(price - nearest_resistance) / nearest_resistance * 100
                sr_strength = max(0, 10 - (distance_pct * 50))
        
        # قوة Price Action (0-5 نقطة)
        price_action_strength = 5 if confirmations.get("price_action", False) else 0
        
        total_confidence = (
            base_confidence +
            macd_strength +
            rsi_strength +
            ema_strength +
            sr_strength +
            price_action_strength
        )
        
        # ضمان حد أدنى من الثقة (75% كحد أدنى) والحد الأقصى 100%
        return max(75, min(100, int(total_confidence)))
    
    def _build_rationale(
        self,
        confirmations: dict,
        macd: float,
        signal: float,
        histogram: float,
        rsi: float,
        price: float,
        ema_10: float,
        ema_20: float,
        ema_50: float,
        nearest_support: Optional[float] = None,
        nearest_resistance: Optional[float] = None,
        pattern: CandlePattern = CandlePattern.NONE,
        signal_type: str = "buy"
    ) -> str:
        """Build rationale string explaining the signal.
        
        Args:
            confirmations: Dict with confirmation status
            macd: MACD line value
            signal: Signal line value
            histogram: Histogram value
            rsi: RSI value
            price: Current price
            ema_10: EMA10 value
            ema_20: EMA20 value
            ema_50: EMA50 value
            nearest_support: Nearest support level
            nearest_resistance: Nearest resistance level
            pattern: Candle pattern
            signal_type: "buy" or "sell"
            
        Returns:
            Rationale string
        """
        confirmed = [k for k, v in confirmations.items() if v]
        not_confirmed = [k for k, v in confirmations.items() if not v]
        
        parts = []
        
        if signal_type == "buy":
            parts.append(f"✅ إشارة شراء قوية ({sum(confirmations.values())}/5 تأكيدات)")
        else:
            parts.append(f"✅ إشارة بيع قوية ({sum(confirmations.values())}/5 تأكيدات)")
        
        parts.append("\n📊 المؤشرات المؤكدة:")
        for indicator in confirmed:
            if indicator == "macd":
                parts.append(f"  • MACD: {macd:.5f} > Signal: {signal:.5f}, Histogram: {histogram:.5f} > 0")
            elif indicator == "rsi":
                parts.append(f"  • RSI: {rsi:.2f} (في النطاق المثالي)")
            elif indicator == "ema":
                parts.append(f"  • EMA: السعر ({price:.5f}) > EMA10 ({ema_10:.5f}) > EMA20 ({ema_20:.5f}) > EMA50 ({ema_50:.5f})")
            elif indicator == "support_resistance":
                if signal_type == "buy" and nearest_support:
                    parts.append(f"  • الدعم: السعر قريب من مستوى الدعم ({nearest_support:.5f})")
                elif signal_type == "sell" and nearest_resistance:
                    parts.append(f"  • المقاومة: السعر قريب من مستوى المقاومة ({nearest_resistance:.5f})")
            elif indicator == "price_action":
                parts.append(f"  • Price Action: نمط صاعد ({pattern.value})")
        
        if not_confirmed:
            parts.append(f"\n⚠️ مؤشرات غير مؤكدة: {', '.join(not_confirmed)}")
        
        return "\n".join(parts)
