"""EMA Support Bounce Strategy.

الاستراتيجية:
- استخدام EMA(10) كخط دعم
- عندما يكون الترند صاعد (السعر فوق EMA)
- ثم يحدث تصحيح (شمعة هابطة)
- الشمعة الهابطة تغلق على EMA أو أعلى منه قليلاً (دعم)
- عند الارتداد الصعودي (برجكشن) ترسل إشارة شراء
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from src.indicators.ema import calculate_ema
from src.indicators.rsi import calculate_rsi


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
    ema_10: Optional[float]
    ema_50: Optional[float]
    rsi: Optional[float]
    last_close: float
    last_open: float
    last_high: float
    last_low: float
    rationale: str


class EMASupportBounceStrategy:
    """استراتيجية الارتداد من دعم EMA.
    
    القواعد:
        1. الترند صاعد: السعر فوق EMA(10) في الشموع السابقة
        2. التصحيح: ظهور شمعة هابطة (close < open)
        3. الدعم: الشمعة الهابطة تغلق على EMA أو أعلى منه قليلاً (هامش 0.1%)
        4. البرجكشن (الإشارة): الشمعة التالية تغلق أعلى من فتحها وتغلق أعلى من EMA
        
    إشارة الشراء (BUY):
        - الترند كان صاعداً (السعر فوق EMA في الشموع السابقة)
        - ظهرت شمعة هابطة (bearish candle)
        - الشمعة الهابطة أغلقت على EMA أو أعلى منه (دعم)
        - الشمعة الحالية (أو السابقة) صاعدة وتغلق أعلى من EMA
    """
    
    def __init__(
        self,
        ema_period: int = 10,
        ema_long_period: int = 50,
        support_tolerance_pct: float = 0.1,
        trend_lookback: int = 5,
        rsi_period: int = 14,
        min_rsi_buy: float = 45.0,
        max_rsi_sell: float = 55.0
    ):
        """Initialize strategy.
        
        Args:
            ema_period: فترة EMA القصيرة (default 10)
            ema_long_period: فترة EMA الطويلة للترند العام (default 50)
            support_tolerance_pct: نسبة التسامح للدعم كنسبة مئوية (default 0.1%)
            trend_lookback: عدد الشموع للتحقق من الترند الصاعد (default 5)
            rsi_period: فترة RSI (default 14)
            min_rsi_buy: الحد الأدنى لـ RSI لإشارة الشراء (default 45)
            max_rsi_sell: الحد الأقصى لـ RSI لإشارة البيع (default 55)
        """
        self.ema_period = ema_period
        self.ema_long_period = ema_long_period
        self.support_tolerance_pct = support_tolerance_pct
        self.trend_lookback = trend_lookback
        self.rsi_period = rsi_period
        self.min_rsi_buy = min_rsi_buy
        self.max_rsi_sell = max_rsi_sell
    
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
        
        # نحتاج على الأقل ema_long_period + trend_lookback + 2 شموع
        min_candles = max(self.ema_long_period, self.ema_period + self.trend_lookback + 2, self.rsi_period + 1)
        if len(candles) < min_candles:
            raise ValueError(
                f"Need at least {min_candles} candles, got {len(candles)}"
            )
        
        # استخراج الأسعار
        close_prices = [float(candle["close"]) for candle in candles]
        open_prices = [float(candle["open"]) for candle in candles]
        high_prices = [float(candle["high"]) for candle in candles]
        low_prices = [float(candle["low"]) for candle in candles]
        
        # حساب EMA(10) و EMA(50)
        ema_values = calculate_ema(close_prices, self.ema_period)
        ema_long_values = calculate_ema(close_prices, self.ema_long_period)
        
        # حساب RSI
        rsi_values = calculate_rsi(close_prices, self.rsi_period)
        
        # الحصول على القيم الأخيرة
        last_close = close_prices[-1]
        last_open = open_prices[-1]
        last_high = high_prices[-1]
        last_low = low_prices[-1]
        last_ema = ema_values[-1] if ema_values[-1] is not None else None
        last_ema_long = ema_long_values[-1] if ema_long_values[-1] is not None else None
        last_rsi = rsi_values[-1] if rsi_values[-1] is not None else None
        
        if last_ema is None or last_ema_long is None:
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                ema_10=None,
                ema_50=None,
                rsi=last_rsi,
                last_close=last_close,
                last_open=last_open,
                last_high=last_high,
                last_low=last_low,
                rationale="لا توجد بيانات كافية لحساب EMA"
            )
        
        # التحقق من الترند الصاعد في الشموع السابقة (أكثر مرونة)
        # نفحص الشموع قبل الأخيرة للتأكد من الترند الصاعد
        trend_start_idx = len(candles) - self.trend_lookback - 1
        trend_end_idx = len(candles) - 2  # قبل الشمعة الأخيرة
        
        uptrend_count = 0
        total_checked = 0
        if trend_start_idx >= 0:
            for i in range(trend_start_idx, trend_end_idx):
                if i < len(ema_values) and ema_values[i] is not None:
                    total_checked += 1
                    if close_prices[i] >= ema_values[i]:
                        uptrend_count += 1
        
        # نعتبر الترند صاعداً إذا كان 60% أو أكثر من الشموع فوق EMA (أكثر مرونة)
        uptrend_confirmed = total_checked > 0 and (uptrend_count / total_checked) >= 0.6
        
        # التحقق من الترند العام باستخدام EMA50
        # الترند العام صاعد إذا كان السعر فوق EMA50
        general_uptrend = last_close > last_ema_long if last_ema_long is not None else False
        general_downtrend = last_close < last_ema_long if last_ema_long is not None else False
        
        # التحقق من الترند الهابط (للبيع)
        downtrend_count = 0
        for i in range(trend_start_idx, trend_end_idx):
            if i < len(ema_values) and ema_values[i] is not None:
                if close_prices[i] <= ema_values[i]:
                    downtrend_count += 1
        
        downtrend_confirmed = total_checked > 0 and (downtrend_count / total_checked) >= 0.6
        
        # فلتر RSI: للشراء يجب أن يكون RSI > min_rsi_buy، للبيع يجب أن يكون RSI < max_rsi_sell
        rsi_filter_buy = last_rsi is None or last_rsi >= self.min_rsi_buy
        rsi_filter_sell = last_rsi is None or last_rsi <= self.max_rsi_sell
        
        # معالجة إشارات البيع أولاً (إذا كان الترند هابطاً)
        if downtrend_confirmed and not uptrend_confirmed:
            # البحث عن شمعة صاعدة أغلقت على المقاومة (EMA) - للبيع
            correction_candle_idx = None
            for i in range(len(candles) - 1, max(0, len(candles) - 10), -1):
                if i < len(ema_values) and ema_values[i] is not None:
                    candle = candles[i]
                    candle_open = float(candle["open"])
                    candle_close = float(candle["close"])
                    ema_at_candle = ema_values[i]
                    
                    # شمعة صاعدة (bullish) قريبة من EMA كمقاومة
                    is_bullish = candle_close > candle_open
                    
                    # حساب نسبة القرب من EMA (مقاومة)
                    tolerance_pct = max(self.support_tolerance_pct, 0.3)
                    tolerance = ema_at_candle * (tolerance_pct / 100.0)
                    resistance_zone_high = ema_at_candle + tolerance
                    resistance_zone_low = ema_at_candle - tolerance
                    
                    # الشمعة أغلقت قريباً من EMA (مقاومة)
                    if (candle_close >= resistance_zone_low and candle_close <= resistance_zone_high) or \
                       (is_bullish and candle_close >= ema_at_candle * 0.995):  # هامش إضافي 0.5%
                        correction_candle_idx = i
                        break
            
            # التحقق من البرجكشن الهابط (للبيع)
            current_is_bearish = last_close < last_open
            current_closes_below_ema = last_close < last_ema
            
            if correction_candle_idx is not None:
                if current_is_bearish and current_closes_below_ema and rsi_filter_sell:
                    # إشارة بيع! (مع فلتر RSI)
                    correction_candle = candles[correction_candle_idx]
                    correction_close = float(correction_candle["close"])
                    
                    confidence = self._calculate_confidence(
                        last_close=last_close,
                        ema_value=last_ema,
                        ema_long_value=last_ema_long,
                        rsi_value=last_rsi,
                        correction_close=correction_close,
                        current_is_bullish=False,  # للبيع
                        general_trend_ok=general_downtrend
                    )
                    
                    ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
                    rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
                    return StrategyResult(
                        signal=Signal.SELL,
                        confidence=confidence,
                        ema_10=last_ema,
                        ema_50=last_ema_long,
                        rsi=last_rsi,
                        last_close=last_close,
                        last_open=last_open,
                        last_high=last_high,
                        last_low=last_low,
                        rationale=(
                            f"✅ إشارة بيع: الترند هابط → تصحيح على المقاومة EMA({last_ema:.5f}) "
                            f"→ برجكشن هابط (إغلاق: {last_close:.5f} < EMA), "
                            f"EMA50: {ema50_str}, RSI: {rsi_str}"
                        )
                    )
            
            # إذا لم نجد شمعة تصحيح، لكن السعر تحت EMA والشمعة هابطة، قد تكون إشارة بيع
            if current_is_bearish and last_close < last_ema and rsi_filter_sell:
                confidence = self._calculate_simple_confidence(
                    last_close, last_ema, last_ema_long, last_rsi, general_downtrend
                )
                ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
                rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
                return StrategyResult(
                    signal=Signal.SELL,
                    confidence=confidence,
                    ema_10=last_ema,
                    ema_50=last_ema_long,
                    rsi=last_rsi,
                    last_close=last_close,
                    last_open=last_open,
                    last_high=last_high,
                    last_low=last_low,
                    rationale=f"إشارة بيع: السعر ({last_close:.5f}) تحت EMA({last_ema:.5f}) وشمعة هابطة, "
                              f"EMA50: {ema50_str}, RSI: {rsi_str}"
                )
        
        if not uptrend_confirmed:
            # إذا لم يكن الترند صاعداً، نتحقق من إمكانية إشارة بناءً على السعر الحالي فقط
            # إذا كان السعر الحالي فوق EMA وشمعة صاعدة، قد تكون إشارة شراء
            # لكن يجب أن يكون الترند العام صاعد (فوق EMA50) و RSI مناسب
            if last_close > last_ema and last_close > last_open and general_uptrend and rsi_filter_buy:
                # إشارة شراء بثقة أقل
                confidence = self._calculate_simple_confidence(
                    last_close, last_ema, last_ema_long, last_rsi, general_uptrend
                )
                ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
                rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
                return StrategyResult(
                    signal=Signal.BUY,
                    confidence=confidence,
                    ema_10=last_ema,
                    ema_50=last_ema_long,
                    rsi=last_rsi,
                    last_close=last_close,
                    last_open=last_open,
                    last_high=last_high,
                    last_low=last_low,
                    rationale=f"إشارة شراء: السعر ({last_close:.5f}) فوق EMA({last_ema:.5f}) وشمعة صاعدة, "
                              f"EMA50: {ema50_str}, RSI: {rsi_str}"
                )
            
            ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
            rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                ema_10=last_ema,
                ema_50=last_ema_long,
                rsi=last_rsi,
                last_close=last_close,
                last_open=last_open,
                last_high=last_high,
                last_low=last_low,
                rationale=f"الترند ليس صاعداً بشكل كافٍ ({uptrend_count}/{total_checked} شموع فوق EMA) "
                          f"أو الترند العام هابط (EMA50: {ema50_str}) "
                          f"أو RSI غير مناسب ({rsi_str})"
            )
        
        # البحث عن شمعة هابطة أغلقت على الدعم (EMA) - أكثر مرونة
        # نبحث في الشموع السابقة عن شمعة هابطة أغلقت على EMA
        correction_candle_idx = None
        # زيادة نطاق البحث إلى آخر 10 شموع
        for i in range(len(candles) - 1, max(0, len(candles) - 10), -1):  # نبحث في آخر 9 شموع
            if i < len(ema_values) and ema_values[i] is not None:
                candle = candles[i]
                candle_open = float(candle["open"])
                candle_close = float(candle["close"])
                ema_at_candle = ema_values[i]
                
                # شمعة هابطة (bearish) أو حتى شمعة صاعدة قريبة من EMA
                is_bearish = candle_close < candle_open
                
                # حساب نسبة القرب من EMA (زيادة التسامح إلى 0.3%)
                tolerance_pct = max(self.support_tolerance_pct, 0.3)
                tolerance = ema_at_candle * (tolerance_pct / 100.0)
                support_zone_high = ema_at_candle + tolerance
                support_zone_low = ema_at_candle - tolerance
                
                # الشمعة أغلقت قريباً من EMA (أعلى أو أسفل)
                if (candle_close >= support_zone_low and candle_close <= support_zone_high) or \
                   (is_bearish and candle_close <= ema_at_candle * 1.005):  # هامش إضافي 0.5%
                    correction_candle_idx = i
                    break
        
        if correction_candle_idx is None:
            # ربما الشمعة الحالية هي شمعة التصحيح
            # أو نحاول البحث عن إشارة ارتداد من الشمعة الحالية
            current_is_bearish = last_close < last_open
            current_is_bullish = last_close > last_open
            
            if current_is_bearish:
                # الشمعة الحالية هابطة - نتحقق من إغلاقها على الدعم
                tolerance = last_ema * (self.support_tolerance_pct / 100.0)
                support_zone_high = last_ema + tolerance
                
                if last_close >= last_ema and last_close <= support_zone_high:
                    # الشمعة الحالية هابطة وأغلقت على الدعم
                    # ننتظر الشمعة التالية للبرجكشن
                    return StrategyResult(
                        signal=Signal.NO_TRADE,
                        confidence=0,
                        ema_10=last_ema,
                        ema_50=last_ema_long,
                        rsi=last_rsi,
                        last_close=last_close,
                        last_open=last_open,
                        last_high=last_high,
                        last_low=last_low,
                        rationale=f"شمعة تصحيح هابطة أغلقت على الدعم EMA ({last_ema:.5f}). في انتظار البرجكشن (الارتداد الصعودي)"
                    )
            
            # إذا لم نجد شمعة تصحيح، لكن السعر فوق EMA والشمعة صاعدة، قد تكون إشارة شراء
            # لكن يجب أن يكون الترند العام صاعد (فوق EMA50) و RSI مناسب
            if current_is_bullish and last_close > last_ema and general_uptrend and rsi_filter_buy:
                # إشارة شراء بثقة متوسطة (بدون شمعة تصحيح)
                confidence = self._calculate_simple_confidence(
                    last_close, last_ema, last_ema_long, last_rsi, general_uptrend
                )
                ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
                rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
                return StrategyResult(
                    signal=Signal.BUY,
                    confidence=confidence,
                    ema_10=last_ema,
                    ema_50=last_ema_long,
                    rsi=last_rsi,
                    last_close=last_close,
                    last_open=last_open,
                    last_high=last_high,
                    last_low=last_low,
                    rationale=f"إشارة شراء: السعر ({last_close:.5f}) فوق EMA({last_ema:.5f}) وشمعة صاعدة (بدون شمعة تصحيح واضحة), "
                              f"EMA50: {ema50_str}, RSI: {rsi_str}"
                )
            
            return StrategyResult(
                signal=Signal.NO_TRADE,
                confidence=0,
                ema_10=last_ema,
                ema_50=last_ema_long,
                rsi=last_rsi,
                last_close=last_close,
                last_open=last_open,
                last_high=last_high,
                last_low=last_low,
                rationale=f"لم يتم العثور على شمعة تصحيح هابطة أغلقت على الدعم EMA أو الترند العام هابط أو RSI غير مناسب"
            )
        
        # وجدنا شمعة تصحيح - الآن نتحقق من البرجكشن (الارتداد)
        # البرجكشن: الشمعة الحالية (أو التالية) يجب أن تكون صاعدة وتغلق أعلى من EMA
        
        # الشمعة الحالية
        current_is_bullish = last_close > last_open
        current_closes_above_ema = last_close > last_ema
        
        if current_is_bullish and current_closes_above_ema and general_uptrend and rsi_filter_buy:
            # إشارة شراء! (مع فلاتر EMA50 و RSI)
            correction_candle = candles[correction_candle_idx]
            correction_close = float(correction_candle["close"])
            
            # حساب درجة الثقة
            confidence = self._calculate_confidence(
                last_close=last_close,
                ema_value=last_ema,
                ema_long_value=last_ema_long,
                rsi_value=last_rsi,
                correction_close=correction_close,
                current_is_bullish=current_is_bullish,
                general_trend_ok=general_uptrend
            )
            
            ema50_str = f"{last_ema_long:.5f}" if last_ema_long is not None else "N/A"
            rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
            return StrategyResult(
                signal=Signal.BUY,
                confidence=confidence,
                ema_10=last_ema,
                ema_50=last_ema_long,
                rsi=last_rsi,
                last_close=last_close,
                last_open=last_open,
                last_high=last_high,
                last_low=last_low,
                rationale=(
                    f"✅ إشارة شراء: الترند صاعد → تصحيح على الدعم EMA({last_ema:.5f}) "
                    f"→ برجكشن صعودي (إغلاق: {last_close:.5f} > EMA), "
                    f"EMA50: {ema50_str}, RSI: {rsi_str}"
                )
            )
        
        # لم يحدث برجكشن بعد أو الفلاتر لم تتحقق
        rsi_str = f"{last_rsi:.2f}" if last_rsi is not None else "N/A"
        return StrategyResult(
            signal=Signal.NO_TRADE,
            confidence=0,
            ema_10=last_ema,
            ema_50=last_ema_long,
            rsi=last_rsi,
            last_close=last_close,
            last_open=last_open,
            last_high=last_high,
            last_low=last_low,
            rationale=(
                f"وجدت شمعة تصحيح على الدعم، لكن البرجكشن لم يحدث بعد أو الفلاتر لم تتحقق "
                f"(الحالية: {'صاعدة' if current_is_bullish else 'هابطة'}, "
                f"إغلاق: {last_close:.5f} {'فوق' if current_closes_above_ema else 'تحت'} EMA, "
                f"الترند العام: {'صاعد' if general_uptrend else 'هابط'}, "
                f"RSI: {rsi_str})"
            )
        )
    
    def _calculate_confidence(
        self,
        last_close: float,
        ema_value: float,
        ema_long_value: Optional[float],
        rsi_value: Optional[float],
        correction_close: float,
        current_is_bullish: bool,
        general_trend_ok: bool
    ) -> int:
        """Calculate confidence score (0-100).
        
        الثقة تعتمد على:
        - قوة الارتداد (المسافة من EMA)
        - حجم الشمعة (صاعدة للشراء، هابطة للبيع)
        - الترند العام (EMA50)
        - RSI
        
        Args:
            last_close: آخر سعر إغلاق
            ema_value: قيمة EMA
            ema_long_value: قيمة EMA50
            rsi_value: قيمة RSI
            correction_close: سعر إغلاق شمعة التصحيح
            current_is_bullish: هل الشمعة الحالية صاعدة (True للشراء، False للبيع)
            general_trend_ok: هل الترند العام مناسب
            
        Returns:
            Confidence score 0-100
        """
        if current_is_bullish:
            # للشراء: المسافة فوق EMA
            distance_from_ema = ((last_close - ema_value) / ema_value) * 100
            # قوة الارتداد الصعودي
            bounce_strength = ((last_close - correction_close) / correction_close) * 100
        else:
            # للبيع: المسافة تحت EMA (قيمة سالبة، نأخذ القيمة المطلقة)
            distance_from_ema = abs(((last_close - ema_value) / ema_value) * 100)
            # قوة الارتداد الهابط (الفرق سالب، نأخذ القيمة المطلقة)
            bounce_strength = abs(((last_close - correction_close) / correction_close) * 100)
        
        # حساب الثقة (0-100)
        # المسافة من EMA: 0-30 نقطة
        distance_confidence = min(30.0, max(10.0, distance_from_ema * 150))
        
        # قوة الارتداد: 0-30 نقطة
        bounce_confidence = min(30.0, max(10.0, bounce_strength * 80))
        
        # ثقة الترند العام (EMA50): 0-20 نقطة
        trend_confidence = 20.0 if general_trend_ok else 0.0
        
        # ثقة RSI: 0-20 نقطة
        rsi_confidence = 0.0
        if rsi_value is not None:
            if current_is_bullish:
                # للشراء: RSI يجب أن يكون بين 45-70 (مثالي)
                if 45 <= rsi_value <= 70:
                    rsi_confidence = 20.0
                elif 40 <= rsi_value < 45 or 70 < rsi_value <= 75:
                    rsi_confidence = 15.0
                elif 35 <= rsi_value < 40 or 75 < rsi_value <= 80:
                    rsi_confidence = 10.0
            else:
                # للبيع: RSI يجب أن يكون بين 30-55 (مثالي)
                if 30 <= rsi_value <= 55:
                    rsi_confidence = 20.0
                elif 25 <= rsi_value < 30 or 55 < rsi_value <= 60:
                    rsi_confidence = 15.0
                elif 20 <= rsi_value < 25 or 60 < rsi_value <= 65:
                    rsi_confidence = 10.0
        
        total_confidence = distance_confidence + bounce_confidence + trend_confidence + rsi_confidence
        
        # ضمان حد أدنى من الثقة عند وجود إشارة (70% كحد أدنى - محسّن)
        # والحد الأقصى 100%
        final_confidence = max(70, min(100, int(total_confidence)))
        
        return final_confidence
    
    def _calculate_simple_confidence(
        self,
        last_close: float,
        ema_value: float,
        ema_long_value: Optional[float],
        rsi_value: Optional[float],
        general_trend_ok: bool
    ) -> int:
        """Calculate simple confidence based on price position relative to EMA.
        
        Args:
            last_close: آخر سعر إغلاق
            ema_value: قيمة EMA
            ema_long_value: قيمة EMA50
            rsi_value: قيمة RSI
            general_trend_ok: هل الترند العام مناسب
            
        Returns:
            Confidence score 0-100
        """
        # المسافة من EMA كنسبة مئوية (موجبة دائماً)
        distance_pct = abs(((last_close - ema_value) / ema_value) * 100)
        
        # ثقة أساسية 50% + مسافة من EMA (حتى 20% إضافية)
        base_confidence = 50
        distance_bonus = min(20, max(0, distance_pct * 10))
        
        # ثقة الترند العام (EMA50): 0-15 نقطة
        trend_confidence = 15.0 if general_trend_ok else 0.0
        
        # ثقة RSI: 0-15 نقطة
        rsi_confidence = 0.0
        if rsi_value is not None:
            # للشراء: RSI يجب أن يكون بين 45-70
            if 45 <= rsi_value <= 70:
                rsi_confidence = 15.0
            elif 40 <= rsi_value < 45 or 70 < rsi_value <= 75:
                rsi_confidence = 10.0
            elif 35 <= rsi_value < 40 or 75 < rsi_value <= 80:
                rsi_confidence = 5.0
        
        total_confidence = base_confidence + distance_bonus + trend_confidence + rsi_confidence
        
        # ضمان حد أدنى من الثقة (70% كحد أدنى - محسّن)
        final_confidence = max(70, min(100, int(total_confidence)))
        
        return final_confidence

